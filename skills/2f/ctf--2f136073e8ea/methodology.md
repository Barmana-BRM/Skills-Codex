# RE Methodology: Triage Decision Tree & Escalation Ladder

Systematic playbook for reverse challenges. Use this file when you don't know
where to start, or when you are stuck and need the next move. All supporting
scripts live in [scripts/](scripts/).

## Stage 0 — Triage (first 5 minutes)

Always run these before opening any decompiler:

```bash
file binary
strings -n 6 binary | head -50        # language/runtime fingerprints
rabin2 -I binary                       # arch, bits, endian, canary, nx, pie
rabin2 -i binary 2>/dev/null | head    # imports (syscall-only = handcrafted)
r2 -q -c 'i~entropy' binary            # section entropy
```

| Observation | Likely conclusion | Next move |
|---|---|---|
| Entropy > 7.2 in a section, few imports | Packed / encrypted payload | UPX -d; if custom packer, break at OEP and dump (see L4) |
| `Go build` / `go1.` strings | Go binary | [languages-compiled.md](languages-compiled.md) + GoReSym |
| Rust panic strings, `.rustc` section hints | Rust binary | [languages-compiled.md](languages-compiled.md) |
| `NimMain` / `__zig_probe_stack` symbols | Nim / Zig binary | [languages-compiled.md](languages-compiled.md#nim--zig) |
| `pyc` magic / `Py_` strings | Python bytecode | [languages.md](languages.md), pycdc |
| `.jar`, `classes.dex`, `META-INF` | JVM / Android | jadx / apktool; [platforms.md](platforms.md) |
| `WebAssembly` magic `\0asm` | WASM | wasm2c / wabt; [tools.md](tools.md) |
| Mach-O | macOS/iOS binary | [platforms.md](platforms.md) + [anti-analysis-macos.md](anti-analysis-macos.md) |
| No `.dynsym`, `int 0x80`/`syscall` inline | Static handcrafted asm | Read asm directly; check for self-modifying code |
| ARM/MIPS/RISC-V ELF | Foreign arch | Cross-compile toolchain or emulate (L4) |
| Trailing data after ELF sections | Appended blob (VM bytecode, encrypted flag) | `binwalk`, carve at `readelf -h` segment end |

## Stage 1 — Symptom → route

```
Run binary, observe behavior
├─ Asks for input, prints "wrong"        → flag-checker → ladder below
├─ Crashes immediately without debugger  → anti-debug present → anti-analysis.md
├─ Runs under lldb/frida but exits       → macOS PT_DENY_ATTACH → anti-analysis-macos.md
├─ No output at all                      → check argv / env / files it stats (strace)
├─ GUI / audio / serial                  → platforms.md, platforms-hardware.md
├─ Custom bytecode interpreter loop      → VM pattern → patterns.md + devirtualize
└─ "License expired" / HWID              → keygenme → decompile validation routine
```

## The Escalation Ladder

Climb one level only when the previous level's exit condition is NOT met
(flag found). Each level lists symptoms that let you skip straight to it.

### L0 — Quick wins (minutes)

- `strings | grep -E "flag|CTF|key|pass"`, `rabin2 -z`
- Run it: `./binary AAAA`; feed files: `echo test | ./binary`
- `ltrace ./binary` / `strace -f -s 500` — look for `strcmp`/`memcmp` with the
  expected value already in the trace, `open()` of hidden files
- Exit: flag in output. Stay here if the binary is trivial.

### L1 — Static decompile

- Open in Ghidra (headless bulk export: [scripts/ghidra_export.py](scripts/ghidra_export.py)),
  rename globals from strings, follow from `main` / entry
- Identify: input read → transform loop → comparison against target blob
- Determine **comparison direction** (see SKILL.md): reversing
  `transform(flag) == stored` vs applying `transform(stored) == flag`
- Exit: transform is invertible on paper → invert it (Python/Z3), done.
- Symptom shortcut: stripless binary with symbols → start here.
- Anti-shortcut: decompilation garbage → anti-disassembly / mid-function
  entries → see Stuck Recovery below.

### L2 — Dynamic hooking / oracles

- Frida hook pack ([scripts/frida_hooks.js](scripts/frida_hooks.js)): log every
  `strcmp/memcmp` argument and return value — often the expected buffer IS the
  transformed flag
- Break at the FINAL comparison, enter any correct-length input, dump the
  computed buffer (`x/32xb $rsi`) — let the program do the math for you
- `strlen`/`read` hook to recover expected input length first
- Exit: flag recovered from dump. Best when transform is runtime-computed.

### L3 — Symbolic execution

- [scripts/angr_solve.py](scripts/angr_solve.py) with the success address
  (`v` in Ghidra) or success string
- Works when: input → long linear/branchy arithmetic → single compare
- Control explosion: constrain stdin length, hook `rand`/`time`
  (`state.libc`... or simprocedure them to constants), start at the check
  function instead of `main`
- Z3 alternative: transcribe the decompiled check into a Z3 expression when
  angr chokes on exotic syscalls — often faster and fully deterministic
- Exit: solver returns printable input.

### L4 — Emulation

- When the binary won't run natively: foreign arch (qemu-user / Unicorn
  harness [scripts/unicorn_harness.py](scripts/unicorn_harness.py)),
  anti-debug too dense (Qiling patches the environment), macOS-only checks on
  Linux (Qiling rootfs), kernel modules
- For packers: emulate until OEP (entropy drops / section perms flip), dump
- Exit: emulated run reaches the comparison with controlled input.

### L5 — Side channels

- Byte-at-a-time brute via comparison timing or instruction counting
  (Intel Pin / Qiling instruction counter — see [tools-emulation.md](tools-emulation.md))
- When the check is a sequential loop over input bytes with an early exit
- Exit: each byte position leaks → recover string position by position.

### L6 — Manual deobfuscation

- Custom VM: identify dispatch loop → opcode semantics table → lift to
  Python/LLVM (see tools-advanced.md "custom VM bytecode lifting")
- MBA / flattening: D-810, Triton simplification, or hand-lift to Z3
- Devirtualize only the check function; don't boil the ocean

## Agent-assisted triage (batch decompile → reason → transcribe → solve)

You are an LLM agent with filesystem access — leverage that instead of
clicking around a GUI:

1. **Bulk decompile**: [scripts/ghidra_export.py](scripts/ghidra_export.py)
   turns the binary into one `.c` file per function.
2. **Locate the check by text search**, not reading:
   `grep -l -E 'memcmp|strcmp|== *[0-9A-Fa-f]{6,}' binary_fns/*.c`, then
   grep for input-entry points (`read|scanf|fgets|argv`) and follow the call
   chain between them.
3. **Read the candidate functions completely** — the check and everything it
   calls on the path. Paste them into your working context rather than
   paraphrasing from memory; transcribe from the actual decompiled text.
4. **Transcribe to Z3** ([z3-cookbook.md](z3-cookbook.md)) or invert in
   Python. Solve.
5. **Verify against the untouched binary** — rerun with the candidate input.
   A solution that only works on your model of the check is a hallucination,
   not a flag.

Discipline rules that keep this reliable:
- Derive constraints from the decompiled code in view, never from "what such
  challenges usually do".
- When decompiler output is ambiguous (signedness, widths), resolve it by
  checking the disasm or dynamic behavior — then record the resolved fact.
- Constants/tables used in constraints must come from the binary (dump), not
  from standard reference values.

## Stuck Recovery Table

| Symptom | Move |
|---|---|
| Ghidra shows garbage at function start | Entry into middle of instruction stream: `U`ndefine, re-disassemble from the real entry; try `pd` from `main`'s first call target |
| Decompiler output differs per run / self-modifying | Dump memory after unpack, analyze the dump instead of the file |
| angr path explosion | Constrain length; `entry_state` → `call_state` at check function; stub `rand`, `time`, `read` with returns |
| memcmp target is runtime-computed | Don't reverse the transform — break AFTER it, dump the computed buffer (L2) |
| Correct-length input unknown | Hook `strlen`/`scanf` return; or watch `read(fd, buf, n)`'s n; check `cmp len, 0x24` style constants |
| Works standalone, dies under debugger | ptrace self-attach / timing checks → [anti-analysis.md](anti-analysis.md) |
| Won't attach on macOS | PT_DENY_ATTACH → [anti-analysis-macos.md](anti-analysis-macos.md) |
| Import hash-resolved / no IAT | Static hash resolution — build hash DB of common API names (tools-advanced) |
| Flag-checker with NO compare anywhere | Result conveyed via exit code / timing / file write / signal count — check `patterns-ctf-3.md` instruction-counter pattern |
| Everything decoded but flag looks wrong | Decoy flags — recheck which comparison gates the REAL success path (SKILL.md Decoy section) |
| Deobfuscated check too slow to invert | Satisfiability beats inversion: model it in Z3 instead of unrolling |

## Convergence & Verification

1. Rerun the original (unpatched) binary with the recovered flag — must print
   success. A flag validated only against a patched binary is not a flag.
2. Sanity-check format against the scoreboard's regex (`flag{...}`, hex32...).
3. Write a 5-line transform summary (input → steps → target). Needed for the
   writeup and re-solves when the flag is per-team.

## Time-boxing (competition mode)

- L0–L1: 15 min. L2: 10 min. L3–L4: 20 min each. If a level exceeds its box,
  write down what you know and climb — do not sink 2 hours into one decompile.
- Hints exist for a reason; taking one at minute 45 beats a blank at minute 90.
