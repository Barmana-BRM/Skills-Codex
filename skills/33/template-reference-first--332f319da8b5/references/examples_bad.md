# Bad Examples

## Bad `SKILL.md`: overloaded entrypoint

```markdown
# Skill

This file contains the complete domain background, the evaluation rubric, the writing voice, the sentence bank, and the implementation notes for the script.
```

Why it fails:
- the entrypoint becomes too large to skim
- another agent must read everything before it can act
- routing and reference loading are unclear

## Bad script boundary: hidden method in Python

```python
INTRO_OPENERS = [
    "This section provides an overview of the topic.",
    "The next section walks through the main design space."
]

DEFAULT_DOMAIN = "some favored domain"
```

Why it fails:
- the method is hidden in implementation details
- the skill quietly bakes in a domain default
- the script now owns reader-facing voice

## Bad reader-facing output

```text
This workspace artifact summarizes the current pipeline stage and organizes the next section of the document.
```

Why it fails:
- it leaks internal process terms
- it describes the writing process instead of delivering content

## Bad example quality

```text
The deliverable should become stronger later after remaining gaps are filled.
```

Why it fails:
- it is vague and not actionable
- it normalizes unfinished language instead of modeling a complete artifact

## Bad reference design

```markdown
See another file for details.
```

Why it fails:
- it does not say which file to read or when
- it creates unnecessary search work for the next agent
