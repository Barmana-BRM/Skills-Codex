# Deliverable Self-Loop — Quality Checklist

## Trace presence (all must exist and be non-empty)

| Artifact | Path |
|---|---|
| Signal table | `output/trace/IDEA_SIGNAL_TABLE.md` |
| Direction pool | `output/trace/IDEA_DIRECTION_POOL.md` |
| Screening table | `output/trace/IDEA_SCREENING_TABLE.md` |
| Shortlist | `output/trace/IDEA_SHORTLIST.md` |
| Report | `output/REPORT.md` |
| Appendix | `output/APPENDIX.md` |
| Structured report | `output/REPORT.json` |

## Shortlist size

- The shortlist (`IDEA_SHORTLIST.md`) must contain **3–5** directions (headings matching `### Direction N.`).
- Fewer than 3 suggests under-exploration; more than 5 suggests insufficient curation.

## Required REPORT.md sections

The final `REPORT.md` must include these sections:

- `## 1. Big-picture takeaways`
- `## 2. Top directions at a glance`
- `## 3. Direction 1` (expanded memo for each top direction)
- `## 6. Other promising but not prioritized directions`
- `## 7. Cross-cutting discussion questions`
- `## 8. Uncertainty and disagreement`

## APPENDIX.md quality tokens

The appendix should expose paper-specific reading-guide tables. Check for these expected tokens:

- `Anchor paper`
- `Why read now`
- `What to extract`
- `Kill signal`

## Templated language anti-patterns (forbidden)

The following phrases indicate templated/canned language that should be rewritten:

- ❌ `reports a meaningful gain`
- ❌ `Sharper mechanism question;`
- ❌ `read it to extract what it really attributes gains to`

These are generator-voice leakage from earlier pipeline stages and should be replaced with specific, context-aware language.
