# Scripts index

Python 3, standard library only (rule RHD-090). Check `python --version` first; if Python is missing, propose the installation to the user and wait for approval (RHD-103). Register every script here (RHD-091); scripts obey `rule.md` (RHD-092).

| Script | Purpose | Status |
|---|---|---|
| `rtl_hier.py` | Module inventory, instance tree to a depth, port tables (`--ports`), Markdown output (`--md`) for analysis stage 1 (RHD-030..033). Read only (RHD-002). `python scripts/rtl_hier.py <RTL_DIR> [--top M] [--depth N] [--ports M] [--md]` | Tested on the CAN RTL (3 level-1 instances, 15 `can_ibo`, unreferenced `can_register_syn`, line numbers match the files) |
| `drawio_frame_diagram.py` | Generates `rtl_hierarchy.drawio` (page 00_TOP and the frame page) from a JSON spec: grid layout, A* router with bend and crossing limits, straight boundary stubs, IO pads, clock tree, labels, native tables, legend. `python scripts/drawio_frame_diagram.py SPEC.json OUT_DIR`; schema in `references/diagram_spec.md` | Tested on `references/examples/can_level1_spec.json`: 4 physical crossings, 17 bends, frame 860 x 290; passes `library_symbols.py validate` |
| `layout_search.py` | Runs the generator over parameter sets and ranks by crossings, bends, area (RHD-097). `python scripts/layout_search.py SPEC.json PARAMS.txt WORK_DIR [--top N]` | Tested with 4 parameter sets |
| `drawio_geometry_check.py` | Geometry review of a `.drawio`: connector through shapes, label overlaps, collinear overlaps, physical crossings, bends (RHD-079), text fill (RHD-052), frame ratio (RHD-087), page bounds. `--allow-shared-start` accepts one distribution tree (RHD-102). | Tested: 0 findings on the generated diagram, findings on a damaged copy |
| `library_symbols.py` | Library catalog, template clone, and `validate --diagram FILE` for provenance, protected styles, groups, 18 pt black and white (RHD-061). Accepts `jumpStyle`/`jumpSize` (RHD-057) and skips native table cells tagged `vlsit_native_table="1"` (RHD-023). | Tested: PASS on the generated diagram (83 library cells, 2 pages) |

## Adding a script

Create it when a deterministic step recurs (RHD-090). Python standard library only, header docstring, English messages, no RTL edits, no writes outside approved paths. Test on a real input, then add a row above. Open candidates: generation of deeper-level pages (level 2 and more) from the same spec, and a spec builder that reads `rtl_analysis.md` tables.
