#!/usr/bin/env python3
# Ghidra headless post-script: decompile every function to .c files.
#
# Run:
#   analyzeHeadless /tmp/gproj p1 -import ./binary \
#       -postScript ghidra_export.py -deleteProject
# Output:
#   <binary>_fns/<entry-addr>_<name>.c   (created next to analyzeHeadless cwd)
#
# Feed the .c files to grep or an LLM to locate the check function fast:
#   grep -l "memcmp\|strcmp" ./binary_fns/*.c

import os

from ghidra.app.decompiler import DecompInterface
from ghidra.util.task import ConsoleTaskMonitor

OUT = os.path.join(os.getcwd(), currentProgram.getName() + "_fns")


def main():
    os.makedirs(OUT, exist_ok=True)
    ifc = DecompInterface()
    ifc.openProgram(currentProgram)
    monitor = ConsoleTaskMonitor()
    ok = fail = 0
    for func in currentProgram.getFunctionManager().getFunctions(True):
        try:
            res = ifc.decompileFunction(func, 30, monitor)
            if not res.decompileCompleted():
                fail += 1
                continue
            name = "%x_%s.c" % (func.getEntryPoint().getOffset(), func.getName())
            with open(os.path.join(OUT, name), "w") as fh:
                fh.write(res.getDecompiledFunction().getC())
            ok += 1
        except Exception as exc:  # keep going on individual failures
            print("[-] %s: %s" % (func.getName(), exc))
    print("[+] wrote %d functions (%d failed) to %s" % (ok, fail, OUT))


main()
