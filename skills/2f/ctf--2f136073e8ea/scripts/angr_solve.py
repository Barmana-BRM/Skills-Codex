#!/usr/bin/env python3
"""Generic angr solver for stdin-driven flag-checker binaries.

Finds an input that reaches the success branch. Two modes:

  1. --str (default auto-list): explore until stdout contains the string,
     auto-avoiding common failure strings. Works without knowing addresses.
  2. --find 0xADDR: explore to a specific success address (from Ghidra).

Examples:
  python3 angr_solve.py ./crackme                        # stdout-string mode
  python3 angr_solve.py ./crackme --len 24
  python3 angr_solve.py ./crackme --find 0x4017c2 --avoid 0x4017d4
  python3 angr_solve.py ./crackme --base 0x100000        # match Ghidra's PIE base

Notes:
  * PIE binaries: angr loads at base 0x400000 by default; pass --base equal to
    your disassembler's image base so --find addresses line up.
  * Path explosion: pass --start ADDR to begin at the check function instead
    of the entry point, and --seed 0 to pin rand()/time() to constants.
"""
import argparse
import angr
import claripy

AUTO_FIND = ["Correct", "correct", "Success", "success", "WIN", "win",
             "Good", "good", "flag{", "Yes", "OK"]
AUTO_AVOID = ["Wrong", "wrong", "Incorrect", "incorrect", "Nope", "Denied",
              "Failed", "failed", "Try again", "Invalid"]


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("binary")
    ap.add_argument("--len", dest="length", type=int, default=32,
                    help="flag length guess (default 32)")
    ap.add_argument("--find", type=lambda s: int(s, 0), default=None,
                    help="success address")
    ap.add_argument("--avoid", type=lambda s: int(s, 0), default=None,
                    help="failure address")
    ap.add_argument("--str", dest="findstr", default=None,
                    help="success string to look for in stdout")
    ap.add_argument("--base", type=lambda s: int(s, 0), default=None,
                    help="load base address (match disassembler for PIE)")
    ap.add_argument("--start", type=lambda s: int(s, 0), default=None,
                    help="start simulation at this address instead of entry")
    ap.add_argument("--seed", type=int, default=None,
                    help="pin rand()/time() to this constant")
    args = ap.parse_args()

    main_opts = {"base_addr": args.base} if args.base else {}
    proj = angr.Project(args.binary, auto_load_libs=False, main_opts=main_opts)

    if args.seed is not None:
        const = angr.SIM_PROCEDURES["stubs"]["ReturnConst"](args.seed)
        for sym in ("rand", "random", "time"):
            try:
                proj.hook_symbol(sym, const)
            except Exception:
                pass

    flag = claripy.BVS("flag", args.length * 8)
    if args.start:
        state = proj.factory.call_state(args.start, flag, proto_args=[claripy.BVV(64, args.length)])
    else:
        state = proj.factory.full_init_state(
            args=[args.binary], stdin=flag, add_options=angr.options.unicorn)
    for byte in flag.chop(8):
        state.solver.add(byte >= 0x20, byte <= 0x7E)

    sm = proj.factory.simgr(state)

    if args.find is not None:
        sm.explore(find=args.find, avoid=args.avoid)
    else:
        finds = [args.findstr.encode()] if args.findstr else \
            [s.encode() for s in AUTO_FIND]
        avoids = [s.encode() for s in AUTO_AVOID]
        sm.explore(
            find=lambda s: any(x in s.posix.dumps(1) for x in finds),
            avoid=lambda s: any(x in s.posix.dumps(1) for x in avoids),
        )

    if not sm.found:
        print("[-] no solution found; try: different --len, --find address, "
              "--start at the check function, or relax printability")
        return
    sol = sm.found[0]
    data = sol.posix.dumps(0)
    print("[+] input:", data[:args.length])


if __name__ == "__main__":
    main()
