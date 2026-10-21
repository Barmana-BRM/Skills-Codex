# Z3 Cookbook: Transcribing Decompiled Checks

Use Z3 when the check is readable as decompiled C but inverting it by hand is
error-prone. angr explores *execution*; Z3 answers *algebra*. Rule of thumb:
if you can paste the check into a C compiler and compile it, you can
transcribe it into Z3.

## Boilerplate

```python
from z3 import *

N = 32                                    # flag length
flag = [BitVec("c%d" % i, 8) for i in range(N)]
s = Solver()
for c in flag:                            # printable constraint FIRST
    s.add(c >= 0x20, c <= 0x7e)
# ... transcribed constraints ...
s.add(check(flag))
if s.check() == sat:
    print("".join(chr(s.model()[c].as_long()) for c in flag))
```

## Translation dictionary (C → Z3)

| Decompiled C | Z3 | Note |
|---|---|---|
| `a + b` (uint32) | `a + b` | BitVec arithmetic wraps mod 2^N — matches CPU exactly |
| `a ^ b`, `a & b`, `a \| b` | same | direct |
| `~a` | `~a` | direct |
| `a << n` | `a << n` | BitVec shift (logical for BV) |
| `(uint32)a >> n` | `LShR(a, n)` | **logical** right shift — plain `>>` on BitVec is arithmetic (SAR); wrong choice silently flips high bits |
| `(int32)a >> n` | `a >> n` | arithmetic shift |
| `a * b` | `a * b` | wraps; imitate the C type width |
| `a / b` (unsigned) | `UDiv(a, b)` | `/` on BitVecs is signed division |
| `a % b` (unsigned) | `URem(a, b)` | Python `%` on BitVec is signed SRem |
| `(uint8)x` cast | `Extract(7, 0, x)` | truncation; upcast = `ZeroExt(24, x)` or `SignExt` |
| `ROTATE_LEFT32(x, n)` | `RotateLeft(x, n)` | `RotateRight` for the other direction |
| `arr[i]` symbolic index | `Array` or If-chain | see below |
| `x == 0x1234` | `x == 0x1234` | comparisons: unsigned `ULT/UGT/ULE/UGE`, signed `slt`... on Python operators |

## Recipes

### Per-byte chained transform

```python
# out[i] = (in[i] ^ 0x37) + i
out = [BitVec("o%d" % i, 32) for i in range(N)]
for i in range(N):
    x = ZeroExt(24, flag[i])
    s.add(out[i] == (x ^ 0x37) + i)
```

### Checksum equality against a dumped target

Dump the target blob first (memory dump at the final compare — SKILL.md
"Memory Dumping Strategy"), then:

```python
target = bytes.fromhex("deadbeef...")
for i, t in enumerate(target):
    s.add(out[i] == t)
```

### Lookup table

Small fixed table, index from input:

```python
tbl = [BitVecVal(v, 32) for v in DUMPED_TABLE]   # extract from the binary!
def lookup(idx):
    return reduce(lambda a, b: If(idx == b, tbl[b], a), ... )
```
Cleaner for ≤ 256 entries:

```python
def lookup(idx):                            # idx: 8-bit BitVec
    res = tbl[0]
    for j, v in enumerate(tbl):
        res = If(idx == j, v, res)
    return res
```

### Loop over the flag (unroll in Python)

```python
# v = 0; for c in flag: v = v*31 + c   (Java-style hash)
v = BitVecVal(0, 32)
for c in flag:
    v = v * 31 + ZeroExt(24, c)
s.add(v == 0xCAFEBABE)
```

### Mixing widths

Work at one width: widen 8-bit chars with `ZeroExt(24, c)` at the boundary,
`Extract(7,0, ...)` at the store. Mixed widths are the #1 source of "solver
returns junk".

## Gotchas (each of these has cost someone a flag)

1. **`>>` vs `LShR`** — see table above. Symptom: solution fails rerun, high
   bytes wrong.
2. **Signed vs unsigned compare** — `a < b` in Z3 on BitVec is *signed*;
   unsigned is `ULT(a, b)`. Decompiled `(unsigned)a < b` must use ULT.
3. **Under-constrained solutions** — solver returns `!!!!!!...` because
   nothing forces printability. Always add the printable range first.
4. **Python int creep** — `c + 1` where 1 is a Python int is fine (coerced),
   but `chr()` on a BitVec crashes; use `s.model()[c].as_long()`.
5. **`s.check()` unknown** — usually too many constraints or deep If-chains:
   split the flag into halves with shared boundary constraints, or replace
   the table lookup with a precomputed relation.
6. **Multiple solutions** — after solving, add
   `s.add(Or([c != s.model()[c] for c in flag]))` and re-check to see if the
   solution is unique (challenge may accept any preimage; writeups need THE
   flag — uniqueness matters).
7. **Wrong transcription beats wrong solver** — validate by feeding the
   solver's answer back through your Python transcription of the check
   before blaming Z3.

## When NOT to use Z3

- The check has a `rand()`/`time()` dependency — pin those first, else
  constraints are unsat for the wrong reason.
- The transform is runtime-generated (self-modifying) — transcribe from the
  *dumped* code, not the file.
- The check is sequential byte-comparison with early exit — side-channel
  brute (L5) is faster than modeling the loop.
- Inputs shorter than ~20 chars, trivial invertible transform — just invert
  in Python; don't reach for the solver for what a `for` loop does.
