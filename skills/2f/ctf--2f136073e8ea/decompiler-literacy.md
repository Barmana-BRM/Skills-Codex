# Decompiler Literacy: Reading Hex-Rays & Ghidra Output

Decompilers emit compiler-shaped code, not source-shaped code. This file
teaches the idiom → meaning dictionary and the three moves that turn an
unreadable function into a readable one.

## Type vocabulary

| You see | Meaning |
|---|---|
| `_BYTE` / `_WORD` / `_DWORD` / `_QWORD` | 1/2/4/8-byte int of unknown signedness |
| `LOBYTE(v)`, `HIBYTE(v)`, `BYTE1(v)`, `LOWORD`, `HIWORD` | byte/word extraction from a wider value — the source did a cast or packed fields |
| `*(_DWORD *)(v + 4)` | a struct field at offset 4 → make a struct |
| `v[4]` where `v` is a `char *` | index arithmetic — could be `v->field` or real array |
| `qmemcpy(dst, "literal", n)` | string or struct constant initialization |
| `(unsigned __int8)v` | the author's `char` used as a byte — usually input |
| `unsigned int` / `int` mixes in the same expression | signedness games the author *intended* (or the decompiler guessed wrong) |

## Compiler idioms masquerading as logic

These look meaningful but are just compiled arithmetic:

| Decompiled | Source intent |
|---|---|
| `x % 8` (uint) | often appears as `x & 7` in asm; decompiler may show either — same thing |
| `x * 2 / x * 5 ...` with powers of two | `x << 1`, `x << 2` — scaling |
| `x * 0xAAAAAAAB` then shift | division by 3 (magic-number division) — **not crypto** |
| `(x >> 31) & 1` | sign bit test, i.e. `x < 0` |
| `~x + 1` | `-x` (two's complement) |
| `x ^ (x >> 31)` | conditional negate trick |
| 16-byte `mov`/`xor` with `xmm` in disasm | vectorized string compare — your `strcmp` became SIMD, don't hunt for `strcmp` |
| a long chain of `?? :` | if/else chain — mentally restore the braces |
| `goto LABEL_x` out of a loop | `break`/`continue` in a switch — restructure, don't chase the goto |

## The three readability moves

Apply in order; each one compounds:

1. **Rename** everything you understand: `v3` → `key_stream`, `sub_4017A0` →
   `check_char`. Every name is a note to future-you.
2. **Retype**: fix a function's signature when args look wrong — if a
   function receives garbage arguments, the *decompiler guessed the
   signature*, the code is fine. In Ghidra: edit signature in the decompile
   pane; in IDA: `Y` on the function.
3. **Restructure data**: `*(_DWORD *)(v + 12)` spam → define the struct once
   (Ghidra: Data Type Manager → new struct → apply to `v`) and offsets become
   field names. Also: mark the expected-value blob as an array, define enums
   for opcode dispatch tables.

## Where decompilers lie

- **Mid-function entry**: handwritten asm enters functions at `main+0xca`;
  the decompiler decodes instructions from the *symbol* entry and garbage
  precedes. Fix: disassemble from the true entry, re-create the function.
- **Custom calling conventions**: locally hand-written functions pass
  arguments in odd registers/stack slots; decompiled calls show wrong args.
  Check the disasm at the call site for actual register setup.
- **Self-modifying/unpacked code**: decompiling the file shows the packer.
  Dump memory after unpack, analyze the dump (L2/L4 in
  [methodology.md](methodology.md)).
- **Stack frame size errors**: local arrays overflow into "other variables";
  suspect when many variables alias. Increase the frame / check `sub rsp, N`.
- **Thumb/ARM mode confusion**: 4-vs-2-byte instructions misparse the whole
  function — force the right mode (`asm.arm`/`cpu` toggles in r2; `T` in
  Ghidra disassembly listing).

## Register quick tables (for when you must read asm)

x86-64 SysV: args `rdi rsi rdx rcx r8 r9` (+stack), return `rax`, callee
saved `rbx rbp r12-r15`. Windows x64: args `rcx rdx r8 r9`, return `rax`.
AArch64: args `x0-x7`, return `x0`, `x29` fp / `x30` lr / `sp`. MIPS o32:
args `a0-a3` (`$4-$7`), return `v0`.

## Reading workflow for a check function

1. Find the comparison (target blob / memcmp / arithmetic-eq) — that's the
   output. Work *backwards* through the transform chain.
2. Annotate the direction: `transform(flag) == target` (invert) vs
   `transform(target) == flag` (apply forward) — SKILL.md "Comparison
   Direction".
3. At each step note: width (8/16/32/64), signedness, order (byte order!),
   and table usage.
4. When the chain is fully annotated, either invert it in Python or
   transcribe it to Z3 ([z3-cookbook.md](z3-cookbook.md)).
