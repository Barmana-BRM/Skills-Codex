---
name: vlsit-vhdl-to-systemverilog
description: Convert complete VHDL RTL designs into readable, synthesizable SystemVerilog under the bundled VLSIT coding rules. Analyze semantics and rule conflicts, obtain plan sign-off, preserve cycle behavior, and deliver source mappings, rule evidence, and actual validation results.
---

# VHDL to SystemVerilog

## Operating contract

1. Read [rule.md](rule.md) completely before doing anything. Its numbered rules (V2S-xxx) are mandatory and rank above everything else. V2S-010 makes [references/VLSIT_RTL_Design_Rule.md](references/VLSIT_RTL_Design_Rule.md) normative; read it in full too.
2. Follow the workflow below. It orders the work; it never relaxes a rule.
3. Consult the other `references/` files as needed: they rank below `rule.md`.
4. Prerequisite (V2S-096): run `python --version`; if Python is missing, propose installing it (Windows: `winget install Python.Python.3.12`) and wait for approval.
5. Run helpers from `scripts/` (index: [scripts/README.md](scripts/README.md)) instead of repeating manual steps.
6. Apply the self-improvement rules V2S-090..096 at the end of every run.

## Workflow

1. **Inputs (V2S-020..024).** VHDL directory required; discover tops, bindings, standard, generics; confirm output and tool choices.
2. **Baseline and plan (V2S-030..033).** Read [references/vhdl_semantics.md](references/vhdl_semantics.md); inventory units; write `conversion_plan.md`; run `python scripts/create_rule_matrix.py` for the initial matrix, then expand subchecks.
3. **Gate 1 (V2S-034).** Present the plan; wait for approve, revise, or stop.
4. **Convert (V2S-040..044).** Behavior-preserving translation under the coding rule.
5. **Validate (V2S-050..052).** Follow [references/validation_and_reports.md](references/validation_and_reports.md).
6. **Deliver (V2S-053, 054).** Required deliverable set with separated evidence categories.
7. **Gate 2 (V2S-055).** Present evidence and limits.
8. **Improve (V2S-090..096).** Add or fix scripts and references, log in `references/improvement_log.md`, and propose rule changes to the user.

## Folder map

| Path | Role | Priority |
|---|---|---|
| `rule.md` | Numbered mandatory rules | 1 (highest) |
| `references/VLSIT_RTL_Design_Rule.md` | RTL coding rule, normative via V2S-010 | 1 (incorporated) |
| `SKILL.md` | Workflow and routing | 2 |
| `references/` (others) | VHDL semantics, validation contract, improvement log | 3 |
| `scripts/` | `create_rule_matrix.py` and model-added helpers | tool |
