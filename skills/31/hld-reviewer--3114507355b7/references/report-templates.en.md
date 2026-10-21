# HLD Review Report and Approval Certificate Templates

Follow `../../../references/review-boundaries.md`. Full reports/certificates apply only to `formal_design`; use the final template for a bounded change, inline or in the existing request. Do not prefill success, 100% coverage, or reviewer independence. Technical judgment, scope authorization, and execution permission are separate.

## Formal Review Report Template

```markdown
# HLD Review Report

## Basic Information

| Item | Content |
|------|---------|
| HLD / reviewed version | [Path and actual version] |
| PRD / API / Guardrails / ADR | [Relevant valid baselines and versions] |
| Original authorization | [Who had authority and approved what; original record, not a prior reviewer comment] |
| Mode and scope | formal_design; [Whole object / remediation IDs and unchanged boundaries] |
| Time / round | [Actual time and round N] |
| Risks / perspectives | [Evidence-based risks, selected roles and trigger evidence] |
| technical_verdict | APPROVED / CHANGES_REQUIRED / EVIDENCE_BLOCKED |
| scope_status | WITHIN_APPROVED_SCOPE / DECISION_REQUIRED |

## Gate 1: Approved Scope and Drift

### Requirement Coverage

| Baseline item | Acceptance / boundary | HLD location | Status | Missing evidence / clarification |
|---------------|-----------------------|--------------|--------|----------------------------------|
| REQ-* / approved decision | [Requirement] | [Section/line] | Covered / Partial / Missing / Unknown | [— when covered; specific reason otherwise] |

- [Actual x/y coverage and denominator; distinguish 1:N allocation from completed design]
- [Actual metadata / lint / RTM results and impact; existing equivalent mapping when no block exists]
- [Results and evidence for omissions, semantic drift, and unauthorized responsibility/dependency changes]
- [Conclusions depending on unresolved items, and independent review that can continue]

## Findings

### P0 / P1 Defects

| Stable ID / severity | Failure and impact | Valid baseline / evidence | Minimum fix and boundary change |
|----------------------|--------------------|---------------------------|---------------------------------|
| [Original ID / P0 or P1] | [Concrete failure and impact] | [Original authority + HLD location] | [Smallest in-scope fix; new authority belongs in Decision Gates] |

## Missing Info / Questions

- [Necessary fact/feasibility gap, minimum evidence and affected conclusion; otherwise None]
- [Prior reviewer omission/error and affected conclusion; do not label your old error a new Dev defect]

## Decision Gates

- [Old → proposed behavior, product/architecture impact, in-scope option, recommendation, authorized owner, exact missing permission; otherwise None]
- [If author notes/prior comments were recycled as approval, identify the original source and retract the specific false claim without rewriting unrelated baselines]

## Optional Improvements

- [Optional P2; count never blocks or automatically carries into the next round; otherwise None]

## Technical and Evidence Coverage

| Dimension | Evidence / actual result / N/A reason |
|-----------|--------------------------------------|
| Responsibilities, architecture decisions and alternatives | [Result] |
| Stack, reuse and maintenance cost | [Result] |
| Interfaces, data and lifecycle | [Result] |
| Compatibility, rollout and recovery | [Result] |
| Observability, risks and testability | [Result] |
| Specialist perspectives | [Triggers and results] |
| Actual management entry and evaluator | [Real parser/client/configuration capability evidence; limits of mocks/self-written compilers] |

## Design Review Decision

| Threshold | Actual result |
|-----------|---------------|
| P0 / P1 are zero | [Counts and closure evidence] |
| Necessary evidence gaps closed | [Actual] |
| Scope has valid original authorization | [Actual] |
| Formal scope fully reviewed | [Actual; disclose unreviewed areas] |

technical_verdict: [APPROVED / CHANGES_REQUIRED / EVIDENCE_BLOCKED]
scope_status: [WITHIN_APPROVED_SCOPE / DECISION_REQUIRED]
Execution permission: [Explicitly granted actions; technical approval does not authorize implementation, push, CI, policy publication, or deployment]

## History and Next Steps

| Round | Original ID | Change / evidence / conclusion |
|-------|-------------|--------------------------------|
| [N] | [Original finding] | [Actual remediation and closure evidence] |

- [Minimum fix, evidence, or owner decision; stop when in-scope blockers close rather than adding deliverables]
```

## Formal Approval Certificate Template

Generate only after formal coverage is complete, P0/P1 are zero, and necessary evidence/authorization gaps are closed. Fields must be filled from facts, not assumed success. Never issue a full certificate for a bounded repair.

```markdown
# HLD Approval Certificate

## Basic Information and Reviewed Object

- HLD: [Path and actual reviewed version/commit]
- Authorized baselines: [PRD/API/Guardrails/ADR versions, original owner decisions and scope]
- Time / rounds: [Actual]
- technical_verdict / scope_status: [Verified conclusions]

## Alignment and Threshold Confirmation

- [In-scope coverage and evidence; results for omissions, distortion, and unauthorized expansion]
- [Actual P0/P1 zero counts and original-finding closure evidence]
- [Closure sources for necessary evidence gaps / scope decisions]
- P2 is optional and is not an approval threshold.

## Review History and Coverage

- [Actual conclusions by round, all three gates, selected perspectives and N/A reasons]
- [Do not generate this certificate with incomplete formal coverage or mark unreviewed work as passed]

## Reviewer and Permission Boundary

- Reviewer: [Actual reviewer and verified independence; never claim independent review when none occurred]
- This certificate records only the design-review conclusion for the stated formal HLD scope. Implementation, push, CI, policy publication, shared-data writes, and deployment require their own explicit authorization.
- A filename hash or invented PASSED stamp is not approval or reviewer provenance.
```

## Bounded Change / Remediation Delta Template

```markdown
Mode: bounded_change
Object / scope: [Request, relevant approved baselines, original finding IDs, explicitly unchanged boundaries]
Original authority: [Who approved what within which scope, with original record]
Findings: [Original-ID closure evidence; separate defects, minimum evidence gaps and scope decisions; state None where applicable]
technical_verdict: [APPROVED / CHANGES_REQUIRED / EVIDENCE_BLOCKED]
scope_status: [WITHIN_APPROVED_SCOPE / DECISION_REQUIRED]
Execution permission: [Explicit authority, not inferred from technical approval]
Next step: [Minimum action; explain old/new behavior and recommendation to the authorized owner when needed]
Optional items: [P2 never blocks or automatically continues the review loop]
```
