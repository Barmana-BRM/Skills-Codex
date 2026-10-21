// Generic comparison-hook pack for CTF flag checkers.
//
// Logs every libc string/memory comparison: arguments, result, and (optionally)
// a backtrace. The "expected" side of the comparison is frequently the
// transformed flag — this dump often solves the challenge outright.
//
// Usage:
//   frida -f ./target -l frida_hooks.js --no-pause   # spawn (hooks pre-main)
//   frida -p <PID> -l frida_hooks.js                 # attach
//   frida -f ./app.apk -l frida_hooks.js -U          # Android (frida-server)
//
// Windows targets: add module names like 'msvcrt.dll'/'ntdll.dll' to
// MODULES and wcscmp/lstrcmpA variants to FUNCS.

const MODULES = [null]; // null = any module (POSIX)
const FUNCS = ["strcmp", "strncmp", "memcmp", "strcasecmp", "strncasecmp",
               "bcmp", "strstr", "wcscmp", "memeq"];
const BACKTRACE = false; // true = print call stack per hit (noisy)

function safeStr(p, max) {
  try { return Memory.readUtf8String(p, max); } catch (e) { return "<unreadable>"; }
}
function safeHex(p, n) {
  try { return Memory.readByteArray(p, n); } catch (e) { return null; }
}

MODULES.forEach(function (mod) {
  FUNCS.forEach(function (name) {
    var addr = Module.findExportByName(mod, name);
    if (addr === null) return;
    Interceptor.attach(addr, {
      onEnter: function (args) {
        this.name = name;
        this.a0 = args[0]; this.a1 = args[1];
        this.n = (name.indexOf("ncmp") > 0 || name.indexOf("memcmp") === 0 ||
                  name === "bcmp" || name === "memeq") ? args[2].toInt32() : -1;
      },
      onLeave: function (rv) {
        var line = "[" + this.name + "] ret=" + rv.toInt32();
        if (this.n >= 0) {
          line += " a0=" + hexdump(safeHex(this.a0, this.n), { length: this.n }) +
                  " a1=" + hexdump(safeHex(this.a1, this.n), { length: this.n });
        } else {
          line += " a0=\"" + safeStr(this.a0, 128) + "\" a1=\"" +
                  safeStr(this.a1, 128) + "\"";
        }
        console.log(line);
        if (BACKTRACE) {
          Thread.backtrace(this.context, Backtracer.ACCURATE)
            .slice(0, 6)
            .forEach(function (x) { console.log("    " + DebugSymbol.fromAddress(x)); });
        }
      }
    });
  });
});

console.log("[*] hook pack installed: " + FUNCS.join(", "));
