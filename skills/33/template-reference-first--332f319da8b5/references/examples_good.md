# Good Examples

## Good `SKILL.md` routing

```markdown
## When to read `references/`

- Always read `references/overview.md` before drafting or validating the deliverable.
- Read `references/examples_good.md` before writing reader-facing sections.
- Read `references/examples_bad.md` when removing generic opener patterns or internal jargon.
```

Why it works:
- the loading rule is explicit
- the entrypoint stays short
- the actual method lives outside `SKILL.md`

## Good reference guidance

```markdown
## Decision rubric

- choose the smallest artifact that proves the claim
- make risks concrete enough to stop the work early if needed
- prefer bounded recommendations over exhaustive option lists
```

Why it works:
- it teaches judgment, not just formatting
- it is reusable across tasks in the same skill

## Good reader-facing example

```text
Recommended path: start with the smallest version that can be evaluated in one week, record one clear success signal, and define in advance what result would make the project not worth extending.
```

Why it works:
- the advice is concrete
- the sentence is complete and copy-safe
- it avoids internal pipeline terms

## Good schema shape

```json
{
  "artifact_name": "decision-memo",
  "required_sections": [
    "recommendation",
    "inputs_used",
    "risks",
    "next_step"
  ],
  "reader_facing": true
}
```

Why it works:
- it captures a contract the script can validate
- it stays machine-readable and domain-neutral

## Good script boundary

```text
The script validates the manifest, checks required files, and writes a small report.
It does not generate the final narrative or supply domain defaults.
```

Why it works:
- deterministic work stays in code
- high-level judgment stays in references and instructions
