# macOS Anti-Analysis: Anti-Debug & Hardened Runtime (Mach-O)

macOS anti-debugging uses different primitives than Linux: there is no
`/proc/self/status` `TracerPid`, `ptrace` has a request that *forbids*
debugging, and code-signing enforcement (hardened runtime) can strip your
injection environment variables. This file covers detection, behavior, and
bypasses for each. General (cross-platform) techniques live in
[anti-analysis.md](anti-analysis.md).

## Triage commands

```bash
file binary                      # Mach-O 64-bit ... arm64 / x86_64
otool -hv binary                 # MAGIC, PIE flag
otool -L binary                  # linked frameworks (anti-debug lives in libSystem ptrace)
nm -u binary 2>/dev/null         # undefined syms: look for _ptrace, _sysctl, _csops
codesign -dvv binary 2>&1        # signature, entitlements, runtime enforcement
codesign -d --entitlements :- binary 2>/dev/null
```

If `_ptrace` shows up in `nm -u` on a CTF binary, it is PT_DENY_ATTACH ~90% of
the time. Statically: search for the immediate `31` (`0x1f`) loaded into the
first argument register (`w0`/`edi`) before the call/syscall.

## 1. `ptrace(PT_DENY_ATTACH)` — the macOS classic

**Behavior:** `ptrace(PT_DENY_ATTACH=31, 0, 0, 0)` marks the process
non-debuggable. Effects: attaching fails; if a debugger is *already* attached
when the call executes, the process exits (SIGTRAP/SIGKILL); `proc_pidinfo`
returns sanitized info. lldb symptoms: "error: attach failed", or the process
dies the moment you continue after a breakpoint that sits before/inside the
check.

### Bypass A — patch the call out (always works)

| Arch | Patch |
|---|---|
| arm64 dynamic `bl _ptrace` | replace the `bl` (4 bytes) with `nop` = `1f 20 03 d5` |
| arm64 static syscall | replace `svc #0` of the ptrace syscall with `nop`, or rewrite `mov w0, #0x1f` → `mov w0, #0xfffffff` (invalid, returns ENOTSUP harmlessly... prefer NOP the svc) |
| x86_64 dynamic `call _ptrace` | replace the 5-byte call with `0f 1f 44 00 00` (5-byte nop) |
| x86_64 `syscall` | replace with `90 90` (2× nop) — only when you've confirmed rax=0x1a is ptrace on this path |

Find candidates: `r2 -q -c '/c jmp ptrace' binary` or
`objdump -d binary | grep -B3 'ptrace\|<\$*'` and in Ghidra search for
constants `0x1f`/`31` near `ptrace` xrefs.

### Bypass B — lldb skip (no patching)

```bash
lldb ./binary
(lldb) breakpoint set --name ptrace
(lldb) run
(lldb) thread return          # force ptrace() to return immediately
(lldb) continue
```

Or at the breakpoint `register write x0 0` (arm64) / `register write rdi 0`
(x86_64) — request 0 is PT_TRACE_ME, harmless.

### Bypass C — Frida replace (cleanest, spawn-gated)

Spawn mode hooks before `main`, so the call never lands:

```js
// frida -f ./binary -l no_trace.js --no-pause
const pt = Module.getExportByName(null, 'ptrace');
Interceptor.replace(pt, new NativeCallback(() => 0, 'long', ['int','int','long','long']));
```

### Bypass D — DYLD interposer (for dynamically-linked calls)

```c
// no_trace.c — cc -shared -o no_trace.dylib no_trace.c
#include <errno.h>
long ptrace(int request, pid_t pid, void *addr, void *data) { errno = 0; return 0; }
int sysctl(int *name, u_int n, void *old, size_t *oldlen,
           void *new, size_t newlen) {
  // chain to real sysctl, then clear P_TRACED below
  extern int sysctl$INTERRUPT();  // or dlsym(RTLD_NEXT, "sysctl")
  return 0;
}
```

```bash
DYLD_INSERT_LIBRARIES=./no_trace.dylib ./binary
```

Blocked by hardened runtime / library validation → see §3 and re-sign.

## 2. `sysctl` P_TRACED and `proc_pidinfo`

**Detection:** `sysctl(CTL_KERN, KERN_PROC, KERN_PROC_PID, getpid(), ...)`
fills a `struct kinfo_proc`; the check reads
`kp_proc.p_flag & P_TRACED (0x8000)`. Loop-based versions poll it. Also seen:
`proc_pidinfo(pid, PROC_PIDTBSDINFO, ...)` with `t_bsdinfo` flags.

**Bypass:** Frida `onLeave` scrub — clear the flag in the returned struct:

```js
const sysctl = Module.getExportByName(null, 'sysctl');
// offset of p_flag inside kinfo_proc — macOS-version dependent; compute it:
//   printf("%zu\n", offsetof(struct kinfo_proc, kp_proc.p_flag));
Interceptor.attach(sysctl, {
  onEnter(a) { this.oldp = a[2]; },
  onLeave(r) { if (!this.oldp.isNull()) {
      const off = 0x20;  // common on recent x86_64/arm64 SDKs — VERIFY
      const fl = this.oldp.add(off);
      fl.writeU32(fl.readU32() & ~0x8000);
  } }
});
```

Static bypass: patch the `tst`/`tbz` on the returned flag, or NOP the
conditional branch that consumes it.

## 3. Hardened runtime, library validation, DYLD stripping

Symptoms: `DYLD_INSERT_LIBRARIES` silently ignored; Frida injection into the
signed process fails; `codesign -dvv` shows `runtime` flag.

Counter-play:

1. **Work on a copy** (never patch SIP-protected paths like `/usr/bin`).
2. **Drop the signature**: `codesign --remove-signature ./binary` — ad-hoc or
   unsigned local binaries get no library validation.
3. **Re-sign ad-hoc with debug entitlement** (also re-enables attach on
   arm64):

```bash
cat > ent.plist <<'EOF'
<?xml version="1.0" encoding="UTF-8"?>
<!DOCTYPE plist PUBLIC "-//Apple//DTD PLIST 1.0//EN"
 "http://www.apple.com/DTDs/PropertyList-1.0.dtd">
<plist version="1.0"><dict>
  <key>com.apple.security.get-task-allow</key><true/>
</dict></plist>
EOF
codesign -f -s - --entitlements ent.plist ./binary
```

4. Classic CTF relic: a `__RESTRICT,__restrict` segment historically opts a
   binary out of env sanitization — if present, DYLD_ vars just work.

## 4. Platform debugger notes (lldb is the native tool)

```bash
lldb ./binary
(lldb) b main           # or: b *0x100003f40 (arm64 PIE: rebase via image list)
(lldb) run
(lldb) register read
(lldb) memory read --size 4 --format x --count 32 $rsi
(lldb) memory write $pc <addr>   # skip instructions
(lldb) image list                # slide/base for PIE math
```

- PIE: breakpoints on file offsets work via symbols; for raw offsets compute
  `runtime = image_base + file_vaddr`.
- Frida local: `frida -f ./binary -l hooks.js` (spawn). On recent macOS,
  attaching to processes you don't own needs elevated privileges; spawning
  your own copy is unrestricted.
- qemu for foreign Mach-O is not a thing — use a matching-arch VM or Qiling's
  macOS rootfs for edge cases.

## 5. Symptom → cause quick table

| Symptom | Cause | Section |
|---|---|---|
| `lldb` attach refused / process SIGTRAPs on continue | PT_DENY_ATTACH | §1 |
| Dies only when breakpoint hit before a syscall | P_TRACED sysctl poll | §2 |
| DYLD_INSERT_LIBRARIES ignored | hardened runtime | §3 |
| Frida can't inject, codesign shows runtime | library validation | §3 |
| Works when launched by Finder, dies in terminal (or vice versa) | `isatty`/parent-PID checks | anti-analysis.md §timing |
