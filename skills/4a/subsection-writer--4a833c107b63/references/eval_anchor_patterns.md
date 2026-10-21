# Evaluation Anchor Patterns

## Purpose

Evaluation anchors make comparisons interpretable.
A claim is better anchored when the reader can tell what was evaluated, how, and under which constraint.

## Minimal anchor fields

When possible, keep these in the same paragraph:
- task or benchmark family
- metric or success criterion
- relevant constraint (budget, tool access, latency, environment, threat model)

## Good use cases

Use an anchor when:
- a paragraph compares performance or robustness
- a paragraph implies transferability or reproducibility
- a number appears

## If evidence is thin

If the pack does not support a full anchor:
- weaken the claim
- state the comparison boundary explicitly
- prefer `under the reported setting` over a stronger generalization

## Avoid

Avoid:
- raw benchmark-name drops without saying why they matter
- protocol metadata such as `Evaluation mentions include ...` copied directly into prose
- free-floating numbers with no metric or constraint
- claiming broad superiority when the protocol context is missing
