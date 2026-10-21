# Preflight Gates

## visual-spec-review Gate

If `ui/04_visual_spec_review/spec-review-report.md` says Fail:

- stop
- write blocked-report.md
- do not generate normal fix-tasks

## spec-compliance-review Gate

If `ui/06_spec_review/compliance-report.md` exists and says Fail:

- stop by default
- write blocked-report.md

Exception:

If user explicitly requests diagnostic-only visual review:

- continue
- mark `acceptanceMode: diagnostic-only`
- all findings are non-final until spec-compliance errors are fixed

## Screenshot Capability Gate

At least one must be available:

- Playwright project script
- Playwright config
- Codex browser screenshot capability
- user-provided actual screenshots

If none exists:

- stop
- write blocked-report.md

## Required Assets

`reference.png` must be available.

If missing:

- stop
- write blocked-report.md
