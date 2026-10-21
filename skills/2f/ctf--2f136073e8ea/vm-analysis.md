# Custom VM Analysis Playbook

Bytecode-VM challenges dominate hard RE. The winning move is systematic: don't
reverse 60 handlers by hand — build a disassembler, trace the real execution,
and only lift the opcodes that touch the check.

## Recognize the shape

Symptoms: a huge `while (1)` with a computed jump; a 20+ case switch on a
byte; an `ldr x8, [table, idx, lsl 3]; br x8` (arm64) / `jmp rax` after a
table lookup (x86-64); a blob of high-entropy-ish bytes that nothing else
references; a `pc`-like counter incremented by odd amounts (2/3/4).

## The six steps

### 1. Find the dispatch loop

In Ghidra: the biggest function containing a jump table, or follow xrefs of
the bytecode blob — the reader of the blob is the interpreter. In r2:
`axt` on the blob address; `pf`... use `pdf` on the reader.

### 2. Identify the VM state (context struct)

One register (usually) holds a pointer to a struct containing: register file
(array of N words), `pc`, `sp` + stack array, flags. Find it by looking at
what *every* handler reads first. Name it, create the struct in Ghidra
(`vm_ctx { regs[16]; pc; sp; stack[64]; }`), and the whole binary suddenly
reads like an emulator.

### 3. Decode the instruction format

Watch how bytes are consumed per iteration:
- `opcode = code[pc]; pc++` → 1-byte opcodes, operands follow (look at which
  handlers read `code[pc+1]`, `code[pc+2]`).
- 16-bit packed: `op = w >> 12; reg = (w >> 8) & 0xF; imm = w & 0xFF`.
- Variable-length: pc increments differ per handler — tally them.
The `pc += K` at the end of each handler tells you that handler's
instruction length. Record it per handler.

### 4. Build the semantics table (one line per handler)

For each handler write one pseudocode line: `0x0A: R[a] = R[b] + R[c]`.
Speed tricks:
- Rename each handler function to its semantics (`vm_add`,
  `vm_loadimm`...). Renamed functions make the *next* decompile read free.
- Many "handlers" are junk/decoys or debug prints — mark and skip.
- If handlers are tiny, dump them all at once with
  [scripts/ghidra_export.py](scripts/ghidra_export.py) and process as text.

### 5. Write the disassembler (30 lines of Python)

```python
CODE = open("blob.bin", "rb").read()
pc = 0
while pc < len(CODE):
    op, a, b = CODE[pc], CODE[pc+1], CODE[pc+2]
    name = OPS.get(op, "??? %02x" % op)
    print("%04x: %-12s a=%d b=%d" % (pc, name, a, b))
    pc += LEN.get(op, 3)
```

Run it over the blob, read the program. The check usually becomes a visible
algorithm (keygenme → invert or Z3).

### 6. Trace-first shortcut (do this BEFORE step 4 if possible)

Instrument the dispatch instead of understanding all handlers:
- Frida: breakpoint on the dispatch address, log `(pc, opcode, regs[0..3])`
  each step — the executed path is often 5–10 distinct opcodes out of 60.
- Unicorn/Qiling: run the VM, hook the dispatch, same log.
- Compare traces of a WRONG input vs a RIGHT-prefix input: the first
  divergence point is the comparison. That's all you need to invert.

## VM archetypes you'll meet

| Archetype | Tell | Approach |
|---|---|---|
| Stack VM | handlers are push/pop/peek; sp prominent | transcribe to RPN, then to Python |
| Register VM | 3-operand ops on `regs[N]` | read disasm directly |
| Accumulator | single implicit register | trivial to hand-trace |
| Encrypted opcodes | `op = blob[i] ^ i` or rolling key at dispatch | decode blob first, then standard flow |
| Self-modifying bytecode | store into the code region | trace dynamic; static disasm lies |
| One-opcode VM | everything is a single XOR/move composition | treat as expression tree |
| VM-in-VM | nested dispatch loops | solve the inner one first, it's usually the real one |

## Solve strategies after lifting

1. **Invert** the lifted program if operations are bijective (classic
   keygenme).
2. **Z3**: transcribe the lifted check to constraints — see
   [z3-cookbook.md](z3-cookbook.md). VM checkers are usually linear enough.
3. **Symbolic bytecode**: if angr exists for the *host* binary, running angr
   over the interpreter rarely works (state explosion at the dispatch loop) —
   lifting beats symbolic execution here.
4. **Hybrid**: use the trace (step 6) to learn the executed subset, lift only
   those handlers, constrain, solve.

## Pitfalls

- Handlers with side effects on `pc` (computed jumps) break the static
  disassembler — handle them as control flow, not data.
- Two handlers with identical semantics but different opcodes = anti-trace
  decoys. Deduplicate by semantics, not opcode.
- Watch for the flag being checked byte-by-byte with early exit — that's a
  side-channel opportunity (L5), no lifting needed.
