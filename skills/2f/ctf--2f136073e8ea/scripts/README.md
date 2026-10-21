# Ready-to-run templates

Copy, adapt the marked spots, run. Each script stays deliberately small so it
is cheap to read in full before modifying.

| Script | When | Typical invocation |
|---|---|---|
| [angr_solve.py](angr_solve.py) | stdin flag-checker, linear-ish check | `python3 angr_solve.py ./crackme --len 24` |
| [frida_hooks.js](frida_hooks.js) | capture runtime comparisons | `frida -f ./crackme -l frida_hooks.js --no-pause` |
| [ghidra_export.py](ghidra_export.py) | bulk decompile to .c, grep/LLM later | `analyzeHeadless /tmp/g p -import ./b -postScript ghidra_export.py -deleteProject` |
| [unicorn_harness.py](unicorn_harness.py) | binary won't run natively / hostile env | `python3 unicorn_harness.py ./b --symbol check --input AAAA --trace` |
| [xor_solve.py](xor_solve.py) | decode XORed blobs | `python3 xor_solve.py blob.bin --pt 'flag{' --repeat` |
| [const_scan.py](const_scan.py) | identify crypto from magic constants | `python3 const_scan.py ./binary -C` |

Dependencies: `pip install angr frida-tools unicorn lief` (or see SKILL.md
prerequisites). Usage context and escalation strategy: [methodology.md](../methodology.md).
