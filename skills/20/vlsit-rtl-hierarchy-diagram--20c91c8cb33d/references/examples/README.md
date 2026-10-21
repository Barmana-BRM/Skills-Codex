# Worked examples (reference only; `rule.md` takes precedence)

| File | What it is |
|---|---|
| `can_level1_spec.json` | Spec of the CAN controller (8051 host configuration), level 1: blocks, connectors, boundary pins, clock tree, tables. Input of `scripts/drawio_frame_diagram.py`; schema in `references/diagram_spec.md`. |
| `can_level1_params.txt` | Parameter sets for `scripts/layout_search.py` (gaps, seeds, side variants). |
| `rtl_analysis.md`, `rtl_hierarchy.drawio` | Final report and diagram of the same CAN level-1 run (output of the spec above with the current skill: frame style, one page `01_LEVEL_1`). Format example only. |

Run from the skill folder:

    python scripts/drawio_frame_diagram.py references/examples/can_level1_spec.json <OUTPUT_DIR>
    python scripts/layout_search.py references/examples/can_level1_spec.json references/examples/can_level1_params.txt <WORK_DIR> --top 3
