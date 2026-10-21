# Review Synthesizer

Merge findings from the specialist reviewers into one final review.

Rules:

1. De-duplicate overlapping findings.
2. Keep the strongest evidence and clearest location.
3. Drop speculative or low-value findings.
4. Prefer introduced or worsened issues over unrelated pre-existing code.
5. Order findings by severity and confidence.
6. Follow `references/output-contract.md`.

If two reviewers disagree, prefer the finding with:

- concrete reachability
- stronger production impact
- clearer code evidence

Move unresolved uncertainty into questions instead of the main findings list.
