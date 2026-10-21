# Improvement log

Append one entry per skill improvement (rule V2S-093). Newest last.

| Date | Reason (observed friction) | Change |
|---|---|---|
| 2026-10-13 | Restructure into rule.md / references / scripts | Moved mandatory requirements from `SKILL.md` to `rule.md` with IDs; `VLSIT_RTL_Design_Rule.md` kept in `references/` and made normative by V2S-010 |
| 2026-10-16 | User asked for the standard structure (SKILL.md workflow, rule.md with non-duplicating IDs, references, Python scripts with a minimal library set, installation proposal when Python is missing) | The rule file was audited for duplicate IDs and undefined references (0 found); added the Python prerequisite rule (V2S-096) and the stdlib-only script convention; Python installed with the user approval (3.12.10) and every script tested on real input; status columns updated |
