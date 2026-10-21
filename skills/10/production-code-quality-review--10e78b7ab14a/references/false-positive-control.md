# False-Positive Control

The value of this skill depends on keeping trust high. False positives are worse than silence.

## Hard Rules

- No location, no finding.
- No evidence, no finding.
- No realistic failure mode, no finding.
- No material impact, no finding.
- No confidence label, no finding.

## Confidence Rules

- `High`: directly supported by code path, changed line range, or deterministic behavior
- `Medium`: strongly implied by code, but one detail still depends on surrounding runtime context
- `Low`: plausible concern but not yet proven

Low-confidence items do not belong in the main findings list unless the impact is severe and the evidence is still concrete. Prefer moving them to questions.

## Reachability Checks

Before reporting:

1. Can this path execute?
2. Is the input or state realistic?
3. Is there already a guard, validation step, or fallback?
4. Is the issue introduced or worsened by this review scope?
5. Would a maintainer likely agree this is worth fixing now?

## Severity Control

- Prefer P0, P1, and strong P2 findings.
- Do not flood the review with speculative P2s.
- Skip `Nit` and P3 unless the user explicitly asks for style or polish review.

## Duplicate Control

When multiple reviewer lenses find the same issue:

- merge them into one finding
- keep the strongest evidence
- keep the clearest location
- avoid repeating the same impact in different words

## Pre-Existing Code

If the issue is clearly pre-existing:

- do not treat it as a normal finding unless the current change worsens it
- otherwise move it to questions, follow-ups, or architecture notes

## Bad Findings To Avoid

Avoid findings like:

- "this might be insecure" without an attack path
- "add more tests" without a named missing scenario
- "consider refactoring" without a concrete maintenance or correctness problem
- "this could be slow" without a realistic scale trigger
