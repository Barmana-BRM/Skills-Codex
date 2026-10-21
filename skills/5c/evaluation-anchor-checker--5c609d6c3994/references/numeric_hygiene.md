# Numeric Hygiene

`evaluation-anchor-checker` is the explicit cleanup pass for numeric claims that survive subsection writing.

Principles:

- keep a number only when the sentence carries enough protocol context to interpret it
- if that context is missing, weaken the sentence instead of guessing missing details
- benchmark inventories and token lists are metadata, not reader-facing evidence
- preserve citation keys exactly; rewrite the claim, not the citation contract

Operational rule:

- count task / metric / constraint context in the same sentence
- if fewer than two categories are explicit, downgrade the sentence to a qualitative statement
- when downgrading, prefer subsection-level `evaluation_anchor_minimal` hints from `writer_context_packs.jsonl`

Use this skill pre-merge on `sections/*.md` when possible.
