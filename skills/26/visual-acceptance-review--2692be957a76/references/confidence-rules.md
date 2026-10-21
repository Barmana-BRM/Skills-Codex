# Confidence Rules

## confidenceTier

Use:

- tier-1: script-backed or objective browser fact
- tier-2: LLM visual comparison with strong evidence
- tier-3: subjective or uncertain judgment requiring human review

## confidence Score

Use 0-1.

Examples:

- 0.95: obvious missing component
- 0.85: clear layout mismatch
- 0.70: likely spacing mismatch
- 0.50: subjective shadow/blur difference

## Script-backed Findings

Use tier-1 when:

- pixel diff script reports mismatch
- color extraction script reports mismatch
- Playwright detects missing asset
- console/network error is captured

## LLM-estimated Findings

Use tier-2 or tier-3.

Do not claim exact pixel distance unless script-backed.

## Human Review

Mark as review-required when:

- shadow depth differs subjectively
- blur/glassmorphism differs subjectively
- image crop interpretation is unclear
- responsive expectation is ambiguous
- automated and visual judgments conflict
