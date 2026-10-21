# Output Contract

Use this output shape unless the host or user explicitly asks for a different one.

For machine-readable automation, use:

- `review-context.schema.json` for `review-entrypoint.py --format json`
- `finding.schema.json` for individual finding records

## Scope

- Base:
- Scope mode:
- Changed files:
- Changed line map used:
- Risk level:
- Assumptions:

## Findings

For each finding:

### P1: Short title

- Location:
- Problem:
- Impact:
- Evidence:
- Suggested fix:
- Confidence:
- New or pre-existing:

Rules:

- Order findings by severity, then by confidence.
- Include file and line references when available.
- Use `High`, `Medium`, or `Low` confidence.
- Low-confidence items belong in questions unless the impact is severe and the evidence is still concrete.
- Do not emit empty sections if there is nothing to report.

## Questions Or Needs Confirmation

Use for:

- uncertain reachability
- missing runtime context
- ambiguous product intent
- possible pre-existing issues not clearly caused by this diff

## Architecture Assessment

Answer briefly:

- does behavior live in the right layer?
- did coupling get worse?
- did the change create future migration cost?

## Robustness Assessment

Answer briefly:

- what happens on failure?
- can operators debug it?
- is retry, timeout, idempotency, or cleanup behavior acceptable?

## Test Assessment

Name:

- the strongest coverage present
- the missing scenario that matters most
- whether current tests would fail for the bug you are reporting

## Meaningful Strengths

Mention only if there is real positive signal such as:

- a good rollback strategy
- a strong migration safety pattern
- tests that cover the important failure path
- clear layering or contract preservation

## Final Recommendation

Use one:

- Safe to merge
- Safe to merge with follow-ups
- Fix P1 or P0 issues before merge
- Do not merge yet

Name the minimum fixes required.
