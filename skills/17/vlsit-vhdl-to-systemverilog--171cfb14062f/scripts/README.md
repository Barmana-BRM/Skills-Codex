# Scripts index

Python 3, standard library only. Check `python --version` first; if Python is missing, propose the installation to the user and wait for approval.

Register every script here (rule V2S-091). Scripts must obey `rule.md` (V2S-092).

| Script | Purpose | Status |
|---|---|---|
| `create_rule_matrix.py` | Create an unassessed evidence matrix (`rule_compliance.json`) from `references/VLSIT_RTL_Design_Rule.md` and record its SHA-256. A document inventory, not a compliance checker. | Tested: 159 NOT_RUN entries created from the bundled rule, SHA-256 recorded |

## Adding a script

Create it when a deterministic step recurs (V2S-090), for example a VHDL design-unit inventory or a source-hash manifest. Include a header docstring, English messages, no overwriting of inputs, and no writes outside approved paths. Test on a real input, then add a row above.
