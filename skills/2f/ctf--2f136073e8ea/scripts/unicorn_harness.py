#!/usr/bin/env python3
"""Unicorn emulation harness for ELF x86-64 / AArch64 functions.

Maps a binary's segments, sets up a stack + input/output buffers, calls one
function, and dumps the output buffer. Use it when the binary refuses to run
natively (wrong arch, hostile environment, anti-debug you don't want to fight).

  python3 unicorn_harness.py ./crackme --symbol check --input AAAA... --outlen 64
  python3 unicorn_harness.py ./crackme --addr 0x401680 --input "$(python3 -c 'print("A"*32)')" --trace

Adaptation points are marked with `# ADAPT`.
Requires: pip install unicorn lief
"""
import argparse
import string
import sys

import lief
from unicorn import (Uc, UC_ARCH_ARM64, UC_ARCH_X86, UC_HOOK_BLOCK,
                     UC_HOOK_CODE, UC_HOOK_MEM_INVALID, UC_MODE_64, UC_MODE_ARM)
from unicorn.arm64_const import UC_ARM64_REG_LR, UC_ARM64_REG_SP, UC_ARM64_REG_X0, UC_ARM64_REG_X1, UC_ARM64_REG_X2
from unicorn.x86_const import (UC_X86_REG_RSP, UC_X86_REG_RDI, UC_X86_REG_RSI,
                               UC_X86_REG_RDX)

PAGE = 0x1000
def align_up(x): return (x + PAGE - 1) & ~(PAGE - 1)

STACK = 0x7fff0000
INPUT = 0x60000000
OUTPUT = 0x60001000
RETADDR = 0x60002000          # sentinel return address; code hook stops here


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("binary")
    g = ap.add_mutually_exclusive_group(required=True)
    g.add_argument("--symbol", help="function symbol name")
    g.add_argument("--addr", type=lambda s: int(s, 0), help="function address")
    ap.add_argument("--input", default="A" * 32, help="input bytes for the buffer")
    ap.add_argument("--outlen", type=int, default=64, help="bytes to dump from OUTPUT after run")
    ap.add_argument("--trace", action="store_true", help="log each instruction")
    args = ap.parse_args()

    binary = lief.parse(args.binary)
    if binary is None:
        sys.exit("[-] not an ELF (or lief failed to parse)")
    is_arm = binary.header.machine_type == lief.ELF.ARCH.AARCH64
    uc = Uc(UC_ARCH_ARM64 if is_arm else UC_ARCH_X86,
            UC_MODE_ARM if is_arm else UC_MODE_64)

    # --- map PT_LOAD segments (base 0x400000; PIE segments keep file layout)
    BASE = 0x400000
    lo, hi = None, None
    for seg in binary.segments:
        if seg.type != lief.ELF.Segment.TYPE.LOAD:
            continue
        va = BASE + seg.virtual_address
        size = max(align_up(seg.virtual_size), align_up(len(seg.content)))
        uc.mem_map(va & ~(PAGE - 1) if va & (PAGE - 1) else va, size)  # ADAPT odd alignments
        uc.mem_write(va, bytes(seg.content))
        lo = va if lo is None else min(lo, va)
        hi = va + size if hi is None else max(hi, va + size)
    uc.mem_map(STACK, 0x20000)
    uc.mem_map(INPUT, PAGE)
    uc.mem_map(OUTPUT, PAGE)
    uc.mem_map(RETADDR, PAGE)   # sentinel page (mapped so RET doesn't fault)

    if args.symbol:
        cand = [s for s in binary.symbols if s.name == args.symbol]
        if not cand:
            sys.exit("[-] symbol not found; use --addr (stripped binary?)")
        fn = BASE + cand[0].value
    else:
        fn = BASE + args.addr

    data = args.input.encode()
    uc.mem_write(INPUT, data)

    # --- calling convention setup: f(input, len, output)
    uc.mem_write(OUTPUT, b"\x00" * args.outlen)
    if is_arm:
        uc.reg_write(UC_ARM64_REG_X0, INPUT)
        uc.reg_write(UC_ARM64_REG_X1, len(data))
        uc.reg_write(UC_ARM64_REG_X2, OUTPUT)
        uc.reg_write(UC_ARM64_REG_SP, STACK + 0x10000)
        uc.reg_write(UC_ARM64_REG_LR, RETADDR)
    else:
        uc.reg_write(UC_X86_REG_RDI, INPUT)
        uc.reg_write(UC_X86_REG_RSI, len(data))
        uc.reg_write(UC_X86_REG_RDX, OUTPUT)
        uc.reg_write(UC_X86_REG_RSP, STACK + 0xfff8)
        uc.mem_write(STACK + 0xfff8, RETADDR.to_bytes(8, "little"))

    from unicorn.arm64_const import UC_ARM64_REG_PC
    from unicorn.x86_const import UC_X86_REG_RIP
    PC_REG = UC_ARM64_REG_PC if is_arm else UC_X86_REG_RIP

    def hook_mem(uc_, access, address, size, value, user):
        print("[-] invalid memory access at 0x%x (pc=0x%x) — check BASE/segments"
              % (address, uc_.reg_read(PC_REG)))
        return False
    uc.hook_add(UC_HOOK_MEM_INVALID, hook_mem)

    if args.trace:
        def hook_code(uc_, address, size, user):
            if address == RETADDR:
                uc_.emu_stop()
                return
            print("  0x%x" % address)
        uc.hook_add(UC_HOOK_CODE, hook_code)

    def hook_ret(uc_, address, size, user):
        if address == RETADDR:
            uc_.emu_stop()
    if not args.trace:
        uc.hook_add(UC_HOOK_CODE, hook_ret)

    # ADAPT: if the function reads globals/env/heap, map and prefill them here.
    # ADAPT: loop here over candidate inputs to brute force byte-by-byte.
    print("[*] calling 0x%x with %d input bytes" % (fn, len(data)))
    try:
        uc.emu_start(fn, RETADDR, timeout=0, count=100_000_000)
    finally:
        out = uc.mem_read(OUTPUT, args.outlen)
        printable = sum(c in string.printable.encode() for c in out)
        print("[*] output (%d/%d printable):" % (printable, args.outlen))
        print(bytes(out))


if __name__ == "__main__":
    main()
