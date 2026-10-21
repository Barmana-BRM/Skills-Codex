# LLD review report and Approval Certificate Template

Use these templates with `../../../references/review-boundaries.md`. Select the mode first; keep useful coverage without creating extra documents or findings for the template. Every mandatory comment needs the effective baseline, actual failure, impact, smallest fix, and whether it changes a boundary. Separate defects, Evidence gaps, Scope decisions, and optional P2 suggestions. Fill applicability, counts, and pass states from actual evidence; example tables are not default-green results.

## Bounded repair / remediation delta

A direct response or an update to the existing review note is sufficient. Do not require a new file, full Manifest, or certificate.

```markdown
mode: bounded_change
technical_verdict: APPROVED / CHANGES_REQUIRED / EVIDENCE_BLOCKED
scope_status: WITHIN_APPROVED_SCOPE / DECISION_REQUIRED

Scope: {proposal/delta, original finding IDs, acceptance semantics, direct effects; unreviewed parts}
Effective basis: {approved requirements/Contract/HLD/ADR/user decision; original approver and scope for disputed boundaries}
Results: {closure evidence; for defects, actual failure and smallest in-scope fix}
Necessary Evidence gaps: {minimum missing facts or NONE; affected conclusions and independent work that can continue}
Scope decisions: {old/new behavior, engineering/product impact, authorized Owner, in-scope alternatives and recommendation; or NONE}
Optional P2: {never blocking and not automatically carried into remediation}
Stop / next step: {only agreed P0/P1 and necessary gaps; stop when closed, without restarting historical scope}
Authority: This conclusion covers only the stated delta; it does not authorize push, CI, policy/configuration publication, shared-data writes, or deployment.
```

Technical feasibility with an unresolved Scope decision is not design exit approval. A prior reviewer comment or its copied APPROVED note is not an original source of scope authority. Withdraw only the affected approval claim when a baseline is contaminated; preserve unrelated valid approvals.

---

## Review Report Template

### Full Report (`formal_design` only)

```markdown
# LLD Review Report

## Basic Information

| Project | Content |
|------|------|
| **LLD Documentation** | {file path} |
| **PRD Baseline** | {file path} v{version} |
| **HLD Baseline** | {file path} v{version} |
| **API Contract** | {file path} v{version} |
| **Guardrails** | {file path} / N/A |
| **Review Time** | {YYYY-MM-DD HH:MM} |
| **Review Round** | Round {N} |
| **technical_verdict** | APPROVED / CHANGES_REQUIRED / EVIDENCE_BLOCKED |
| **scope_status** | WITHIN_APPROVED_SCOPE / DECISION_REQUIRED |
| **Scope authority source** | {original authorized Owner record and scope, not this review as its own authority} |

---

## Problem statistics

| Level | Quantity | Threshold | Status |
|------|------|------|------|
| P0 (Block) | {n} | = 0 | ✅ Passed / ❌ Failed |
| P1 (Severe) | {n} | = 0 | ✅ Pass / ❌ Fail |
| P2 (suggestion) | {n} | No count threshold | Optional, non-blocking |

List necessary Evidence gaps and Scope decisions separately. Do not count them as proven P0/P1 defects or omit them to issue a certificate.

---

## Gate 1: Baseline and Manifest Check

### Baseline reference checking

| Check Item | Result | Evidence Location | Question |
|--------|------|----------|------|
| PRD version annotation | ✅/⚠️/❌ | LLD:{Chapter} | {Problem description} |
| HLD version annotation | ✅/⚠️/❌ | LLD:{chapter} | {problem description} |
| Contract version annotation | ✅/⚠️/❌ | LLD:{Chapter} | {Problem description} |

### Manifest integrity check

| Module | Status | N/A Reason | Check Result |
|------|------|----------|----------|
| Core | Included | — | ✅ |
| API Contract | Included | — | ✅ |
| Storage & Migration | Excluded | {Reason} | ✅/⚠️ |
| Async/Event | Excluded | {Reason} | ✅/⚠️ |
| Infra/IaC | Included | — | ✅ |
| Observability | Included | — | ✅/⚠️ |
| Security/Compliance | Excluded | {Reason} | ✅/⚠️ |
| Deployment/Release | Included | — | ✅/⚠️ |
| Frontend UX | Excluded | {Reason} | ✅/⚠️ |
| External Integration | Excluded | {Reason} | ✅/⚠️ |
| SDK/Library | Excluded | {Reason} | ✅/⚠️ |

### Guardrails Coverage Check

| Guardrail Requirements | LLD Coverage Locations | Results |
|----------------|--------------|------|
| {Requirement 1} | LLD:{Chapter} | ✅/❌ |
| {Requirement 2} | LLD:{Chapter} | ✅/❌ |

### New boundary detection

| Test items | Results | Evidence |
|--------|------|------|
| New services/interfaces | None / Authorized / Decision needed | {original approval and scope, or proposed change} |
| Authorization responsibility/principal or trust changes | None / Authorized / Decision needed | {old/new behavior and source} |
| Standing dependency/control-flow/failure-boundary changes | None / Authorized / Decision needed | {include changes without new components} |

**Gate 1 Conclusion**: {Basis confirmed / Necessary evidence missing / Scope decision / Proven defect}; {dependent conclusions and independent work that can continue}.

---

## Gate 2: Consistency and Drift Detection

### HLD→LLD coverage table

| HLD design decisions | LLD coverage locations | Status | Description |
|--------------|-------------|------|------|
| HLD:{Chapter} {Decision Description} | LLD:{Chapter} | ✅ Covered | — |
| HLD:{Chapter} {Decision description} | LLD:{Chapter} | ⚠️ Partial coverage | {Description} |
| HLD:{Chapter} {Decision Description} | — | ❌ Not Covered | {Description} |

**Coverage**: {Number covered}/{Total} = {Percent}%

### List of drift issues

| Stable ID | Type | Effective basis | LLD location | Failure and impact | Classification |
|-----------|------|-----------------|--------------|--------------------|----------------|
| {ID} | {omission/inflation/distortion/degradation} | {original approval/requirement} | {location} | {facts} | {P0/P1 or Evidence gap / Scope decision} |

### Contract consistency check

| Interface | Contract Definition | LLD Definition | Results | Question |
|------|--------------|----------|------|------|
| {Interface name} | Contract:{Location} | LLD:{Location} | ✅/❌ | {Question} |

**Gate 2 Conclusion**: ✅ No drift / ⚠️ Drift present

---

## Gate 3: Module integrity check

| Module | Status | Required | Missing | Severity |
|------|------|--------|--------|--------|
| Core | Included | 5/5 | — | — |
| API Contract | Included | 3/3 | — | — |
| Storage & Migration | Included | 4/4 | — | — |
| Async/Event | Included | 4/4 | — | — |
| Infra/IaC | Included | 3/3 | — | — |
| Observability | Included | 4/4 | — | — |
| Security/Compliance | Included | 3/3 | — | — |
| Deployment/Release | Included | 3/3 | — | — |
| Frontend UX | Included | 4/4 | — | — |
| External Integration | Included | 3/3 | — | — |
| SDK/Library | Included | 3/3 | — | — |

**Gate 3 Conclusion**: ✅ Complete / ⚠️ Missing

---

## Gate 4: Feasibility and Risk Assessment

| Assessment Item | Result | Evidence Location | Question |
|--------|------|----------|------|
| Key process pseudocode | ✅/⚠️/❌ | LLD:{location} | {question} |
| Error handling completeness | ✅/⚠️/❌ | LLD:{location} | {issue} |
| Concurrency / Transactions / Idempotency | ✅/⚠️/❌ | LLD:{Location} | {Question} |
| Test strategy feasibility | ✅/⚠️/❌ | LLD:{location} | {question} |
| Production management entry point / SDK capability | ✅/⚠️/❌ | {evidence for input, management interface, and evaluator} | {a custom compiler or direct evaluator call is not a substitute} |
| Observational Design | ✅/⚠️/❌ | LLD:{Location} | {Question} |
| Publishing Policy | ✅/⚠️/❌ | LLD:{Location} | {Question} |

**Gate 4 Conclusion**: ✅ Achievable / ⚠️ Risky

---

## Question list summary

Each suggested mandatory fix below must be the smallest fix within existing authority and state whether the boundary changes. If that is impossible, move it to Scope decisions instead of hiding a new design in P1. Severity follows actual impact, not missing document formats, checklist items, or lint levels.

### 🔴 P0 blocking problem (must be fixed)

| # | Gate | Problem Description | Evidence Location | Suggested Modifications |
|---|------|----------|----------|----------|
| 1 | Gate 1 | {Description} | LLD:{Location} | {Suggestion} |
| 2 | Gate 2 | {Description} | HLD:{Location} vs LLD:{Location} | {Suggestion} |

### 🟡 P1 serious problem (must be fixed)

| # | Gate | Problem Description | Evidence Location | Suggested Modifications |
|---|------|----------|----------|----------|
| 1 | Gate 2 | {Description} | LLD:{Location} | {Suggestion} |
| 2 | Gate 3 | {Description} | LLD:{Location} | {Suggestion} |

### 🔵 P2 suggested question (optional optimization)

| # | Gate | Problem Description | Evidence Location | Suggested Modifications |
|---|------|----------|----------|----------|
| 1 | Gate 4 | {Description} | LLD:{Location} | {Suggestion} |

### Necessary Evidence gaps

{Minimum missing facts, affected conclusions, and independent work that can continue; or NONE}

### Scope decisions

{Old boundary, new behavior, concrete impact, in-scope alternatives and recommendation, authorized engineering/product Owner; or NONE}

---

## Design review decision

### Exit threshold inspection

| Threshold | Requirement | Actual | Status |
|------|------|------|------|
| P0 | = 0 | {n} | ✅/❌ |
| P1 | = 0 | {n} | ✅/❌ |
| P2 | No count threshold | {n} | Non-blocking |
| Necessary evidence / authority gaps | None unresolved for full design exit | {status} | {status} |

### in conclusion

technical_verdict: {APPROVED / CHANGES_REQUIRED / EVIDENCE_BLOCKED}
scope_status: {WITHIN_APPROVED_SCOPE / DECISION_REQUIRED}

Formal design exit requires full coverage, no P0/P1 defects, and no necessary evidence or authority gaps. A technically sound proposal awaiting scope authority gets a technical opinion, not a conditional approval certificate.

---

## Next step

### If passed
- End this design review; any implementation follows the user's existing authorization
- Keep this report as review evidence, not self-proving original authority for added scope
- P2 remains optional; do not automatically add it to another round or authorize push, CI, policy publication, shared-data writes, or deployment

### If not passed
1. LLD author fixes the following issues:
- {Question 1}
- {Question 2}
2. After the repair is completed, initiate a review (round +1)
3. Retain original IDs, scope, and acceptance semantics. Review only the remediation delta, original blockers, and direct effects; explicitly complete unreviewed/evidence-gap parts without automatically restarting all four gates
```

---

## Approval Certificate Template

### Only for formal design meeting all exit conditions

```markdown
# LLD approval certificate

---

## Basic Information

| Project | Content |
|------|------|
| **LLD Documentation** | {file path} |
| **PRD Baseline** | {file path} v{version} |
| **HLD Baseline** | {file path} v{version} |
| **API Contract** | {file path} v{version} |
| **Exact time** | {YYYY-MM-DD HH:MM} |
| **Review Rounds** | {N} rounds in total |
| **Review Conclusion** | 🟢 **Passed** |
| **technical_verdict** | APPROVED |
| **scope_status** | WITHIN_APPROVED_SCOPE |
| **Scope authority source** | {original approval record, authorized Owner, and scope} |

---

## Review Process

| Round | Date | P0 | P1 | P2 | Conclusion |
|------|------|----|----|----| -----|
| {actual round} | {actual date} | {count} | {count} | {count} | {actual conclusion and record} |

---

## Consistency confirmation

- HLD→LLD coverage: {reviewed/applicable total and evidence; incomplete coverage cannot receive a certificate}
- Omission, unauthorized inflation, semantic drift, and quality degradation: {actual findings and evidence}
- API Contract consistency: {actual coverage and evidence; technical reasons/annotations do not replace approval}

---

## Confirmation of passing the threshold

| Threshold | Requirement | Actual | Status |
|------|------|------|------|
| P0 | = 0 | {actual count} | {conclusion} |
| P1 | = 0 | {actual count} | {conclusion} |
| P2 | No count threshold | {n} | Non-blocking |
| Necessary evidence / authority gaps | None unresolved | {actual state and closure sources} | {conclusion} |

---

## Review coverage

- **Gate 1**: {actual baseline and Manifest result}
- **Gate 2**: {actual consistency and drift result}
- **Gate 3**: {actual module completeness result}
- **Gate 4**: {actual feasibility and risk result}

---

## Legacy Suggestions (P2)

The following suggestions do not block design exit and are not automatically included in implementation or the next remediation round. The author decides whether to adopt them:

| # | Question | Suggestion |
|---|------|------|
| 1 | {P2 problem description} | {Optimization suggestions} |

---

## Confirmation of accurate departure

This LLD has been fully reviewed by **lld-reviewer** and meets the approval standards.

This certificate attests only to completion of this formal LLD review. It does not replace the scope Owner's approval or authorize implementation, push, CI, policy/configuration publication, shared-data writes, or deployment.

---

**Reviewer**: lld-reviewer

**Review record**: {review time, reviewed version, and actual evidence location; do not manufacture an authority seal}
```

---

## Necessary basis / pending boundary decision

When critical basis or authority is unresolved, pause only dependent conclusions and continue independently reviewable work. Missing files are not automatic P0 defects; proven defects are still classified by impact.

```markdown
# LLD Review - Pending evidence / boundary decision

## Basic Information

| Project | Content |
|------|------|
| **LLD Documentation** | {file path} |
| **Review Time** | {YYYY-MM-DD HH:MM} |
| **technical_verdict** | {APPROVED / CHANGES_REQUIRED / EVIDENCE_BLOCKED} |
| **scope_status** | {WITHIN_APPROVED_SCOPE / DECISION_REQUIRED} |

---

## Specific paused conclusions

| ID | Gap / decision | Dependent scope | Minimum evidence or authorized Owner options |
|----|----------------|-----------------|----------------------------------------------|
| {ID} | {Evidence gap / Scope decision} | {specific conclusion} | {details} |

---

## Next step

1. Supply the minimum necessary facts or corresponding boundary decision; do not require a new full set of upstream documents
2. Continue / record independent review work: {results}
3. Review only the affected delta and original gap next, without reopening unrelated valid conclusions

---

**Coverage disclosure**: {what was actually reviewed, what was not, and why}; do not claim full design exit.
```

---

## Instructions for use

1. **Select Template**: Select the corresponding template based on the review results
2. **Fill content**: Replace `{placeholder}` with actual content
3. **Fit the task**: Preserve necessary decisions; bounded reviews may use concise prose rather than tables or a full certificate
4. **Evidence Reference**: All questions must refer to specific locations (e.g. `LLD:3.2`, `HLD:4.1`)
