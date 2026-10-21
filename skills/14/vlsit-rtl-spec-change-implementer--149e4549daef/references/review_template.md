# rtl_change_review.md template

Reference only. `rule.md` (RSC-030..037, 051) takes precedence. Write in scientific English.

```markdown
# RTL Change Review — <feature> — plan version N

Status: Awaiting user sign-off | Approved (version N) | Not approved | Implemented

## 1. Design and input summary
RTL root, old spec (path or "not supplied"), new spec source, selected top/modules, analysis limits, pre-existing working-tree changes.

## 2. Requirement comparison
| ID | New requirement | Old requirement | Current RTL behavior (file:line) | Intended behavior |

## 3. Affected modules and files
| Module | File | Code region | Proposed change | Reason |

## 4. Design choices (max three, ranked, one recommended)
| Strategy | Functional coverage | Change size | Compatibility | Complexity | Risk |

## 5. Minimal-change rationale
Why each edit is needed. Related code explicitly excluded.

## 6. Open questions, assumptions, conflicts, risks

## 7. Proposed validation
| Check | Command | Expected evidence | Status (not run) |

## 8. Approval
Do you approve plan version N, including the listed RTL files, proposed behavior, and validation commands? Reply APPROVE, REVISE, or STOP.

## 9. Final implementation report (added after approval)
Traceability (requirement -> file:line), changed files and summaries, executed checks and results, remaining risks, completion status.
Code-change metrics: baseline lines, added, deleted, percentage, changed-file list (from `scripts/rtl_change_metrics.py compare`).
```
