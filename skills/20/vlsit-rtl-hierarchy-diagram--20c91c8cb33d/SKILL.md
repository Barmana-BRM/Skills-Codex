---
name: vlsit-rtl-hierarchy-diagram
description: Analyze existing Verilog or SystemVerilog RTL to trace module hierarchy, functional relationships, and protocol interfaces, then create a source-grounded multi-page draw.io diagram using only the bundled VLSIT symbol library. Use when asked to inspect or map a design from its top module to its submodules.
---

# VLSIT RTL Hierarchy Analysis and draw.io Diagram

## Operating contract

1. Read [rule.md](rule.md) completely before doing anything. Its numbered rules (RHD-xxx) are mandatory and rank above everything else; this file only orders the work.
2. References ([references/](references/)) explain terms, templates, and examples. Follow them for detail, but when a reference differs from a rule, follow the rule and report the difference.
3. Scripts ([scripts/README.md](scripts/README.md)) do the repeatable work so that tokens are spent on analysis, not on drawing or counting. Python 3 with the standard library only.
4. Prerequisite (RHD-103): run `python --version`. If Python is missing, propose installing it (Windows: `winget install Python.Python.3.12`) and wait for approval.
5. At the end of every run apply the self-improvement rules RHD-090..096.

## Workflow (strictly in this order, RHD-070)

| Step | Do | Rules | Tool or reference |
|---|---|---|---|
| 1 | Obtain the RTL directory and the diagram level N (1 = TOP frame with its children, 2 = one more level, ...; no separate TOP-only page); ask for both in one message if absent. | RHD-010..013 | |
| 2 | Hierarchy analysis down to level N: files, top, instances, parameters, generate scope. | RHD-030..033, 036, 037 | `python scripts/rtl_hier.py <RTL_DIR> --depth N`, `--ports MODULE` |
| 3 | Module functions; split modules with own logic into at most 10 functional groups. | RHD-034, 071, 080..083 | |
| 4 | Signals and interfaces: meaning, direction, width, level or pulse, standard, handshake or custom. | RHD-035, 072, 073 | `references/interface_groups.md` |
| 5 | Group signals into interfaces (one per functionally related set, dedicated pad lines separate), assign mnemonics, find the active side. | RHD-074, 049, 059, 078, 100 | |
| 6 | Write everything in one `rtl_analysis.md`. | RHD-075..077 | `references/analysis_template.md` |
| 7 | Build the spec and generate the diagram; optionally search layouts. | RHD-020..025, 040..059, 079, 084..089, 097..102 | `references/diagram_spec.md`, `scripts/drawio_frame_diagram.py`, `scripts/layout_search.py`, `references/sizing_guide.md`, `references/library_usage.md` |
| 8 | Validate and report: library validator, geometry check, preview when possible. | RHD-060..063 | `python scripts/library_symbols.py validate --diagram FILE`, `python scripts/drawio_geometry_check.py FILE --allow-shared-start` |
| 9 | Improve: add scripts, refine references, log in `references/improvement_log.md`, ask the user about proposed interface groups and rule changes. | RHD-078, 090..096 | |

## Folder map

| Path | Role | Priority |
|---|---|---|
| `rule.md` | Numbered mandatory rules | 1 (highest) |
| `SKILL.md` | Workflow and routing | 2 |
| `references/` | Guides, templates, catalog, worked examples, improvement log | 3 |
| `assets/` | Bundled symbol library (immutable) | data |
| `scripts/` | Python tools | tool |
