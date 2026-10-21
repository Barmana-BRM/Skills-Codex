# rtl_analysis.md template

Reference only. `rule.md` (RHD-070..077) takes precedence. A complete worked example is [examples/rtl_analysis.md](examples/rtl_analysis.md); it was produced by this skill version. Follow this template for all sections.

```markdown
# <Design> RTL Analysis

## 1. Scope and evidence
RTL root, selected diagram level N (and effective level if clamped), files inspected, selected top and why, configuration assumptions (defines, parameters), evidence level (static analysis only unless stated).

## 2. Hierarchy
Tree (depth, instance, module, file:line, parent, parameters, generate scope).
| Depth | Instance | Module | File:line | Parent | Notes |

## 3. Module functions
| Module | Main function (from RTL) | Key state / datapath / control | Instances | Instance-specific role |

### 3a. Functional groups (modules with own logic, RHD-080..085)
| Module | Group | Function | Constructs and line ranges | State elements | Signals driven | Inputs | Outputs | Merge note (if more than 10 candidates) |

## 4. Signal analysis (per inter-block connection)
| Signal (src) | Signal (dst) | Src inst | Dst inst | Dir | Width | Type (level/pulse/data/addr/ctrl/status/irq/clk/rst) | Evidence for type | Meaning | Group |

## 5. Interface classification
| Interface | Category (standard / handshake / custom) | Protocol and version or "none" | Active side (initiator) -> passive side, with evidence (RHD-049) | Mandatory signals present | Missing signals | Evidence |

## 6. Signal groups (with mnemonics, RHD-059)
| Mnemonic | Interface name | Catalog match or `(proposed group)` | Endpoints (blocks, parent, external) | Signals | Active -> passive |
Ungrouped signals listed explicitly.

## 7. Conditional and unresolved items
Generate or define branches, unresolved/external modules, unclear signal types.

## 8. Diagram mapping
Page -> blocks drawn; connector -> group name. Updated whenever analysis changes (RHD-077).
```

## Level vs pulse hints (evidence, not name-based)

- Pulse: assigned for one cycle then cleared, or generated from an edge detector; consumers use edge or event semantics.
- Level: held until explicitly cleared or changed; consumers sample the value.
- Document the file:line that shows the behavior.
