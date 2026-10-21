---
name: nature-paper-polishing
description: Use when Codex needs to polish, translate, restructure, or critique academic manuscript text for scientific-paper style, especially Chinese-to-English drafts, abstracts, introductions, results, discussion, methods, titles, citation wording, claim calibration, overclaim detection, and Nature-aware British English conventions.
---

# Nature Paper Polishing

## Overview

Use this skill to improve manuscript language while preserving the author's scientific meaning. Treat it as an academic editing workflow, not a generator of new data, citations, or arguments.

The style target is Nature-aware scientific prose: concise sentences, high information density, calibrated claims, transparent methods, and British English spelling. Always defer to the target journal's current author guidelines when the user names a specific journal.

## Boundaries

- Preserve the user's findings, scope, variables, numerical values, and cited claims.
- Do not invent references, data, statistical results, methods, limitations, author contributions, or ethics approvals.
- Mark uncertain content instead of resolving it silently.
- If a claim needs evidence and no citation is supplied, flag it as "citation needed".
- If a manuscript is unpublished or sensitive, avoid suggesting upload to public services.
- Do not promise that text meets Nature acceptance standards. Only improve style and editorial quality.

## Quick Workflow

1. Identify the manuscript section: title, abstract, introduction, results, discussion, conclusion, methods, figure legend, cover letter, or response to reviewers.
2. Preserve content first. Extract factual claims, measurements, comparisons, section purpose, and implied causal language.
3. Apply section rules below.
4. Split overloaded sentences. Aim for one core subject and one main verb per sentence.
5. Calibrate hedging to evidence strength.
6. Replace filler and weak verbs with precise scientific language.
7. Apply British English, article use, abbreviation, number, and unit conventions.
8. Check citations, attribution, and intellectual debt.
9. Flag overclaims, missing methods details, unsupported causality, and unverified "first" or "best" claims.
10. Output the polished text first, followed by a short edit note.

## Output Format

When polishing text, provide:

1. Polished text as normal prose, not in a code block.
2. "Key edits" with 3-5 bullets.
3. "Flags" only when needed, listing unresolved citation, evidence, terminology, or scientific-accuracy issues.

If the user asks only for the final wording, omit the edit notes.

## Sentence Rules

- Keep most sentences under 25 words. No sentence should exceed 30 words unless a technical name or citation makes this unavoidable.
- Split Chinese sentences longer than about 40 characters, or English sentences with several clauses, into multiple English sentences.
- Do not compress several propositions into one sentence to appear concise.
- Vary cohesion between sentences. Use subject restatement, adverbial connectives, definite nouns, pronouns with clear antecedents, or zero-connective flow.
- Avoid starting many consecutive sentences with "This", "These", or "Such". If using a demonstrative, attach a meaningful noun.
- Remove filler: "It is well known that", "As a matter of fact", "It is worth noting that", "in recent years" when generic, and similar phrases.

## Section Rules

### Title

- Keep the title searchable, specific, and defensible.
- Prefer concrete nouns and findings over vague claims.
- Avoid inflated words such as "novel", "unprecedented", "revolutionary", and "first" unless evidence is explicit.
- For Nature-style titles, aim for 75 characters or fewer when possible, but do not remove necessary keywords.

### Abstract

Build a mini-paper:

1. Field context or problem.
2. Gap or unresolved limitation.
3. Approach.
4. Key quantitative result or central finding.
5. Implication with appropriate boundary.

Do not introduce methods, claims, or numbers that are absent from the manuscript.

### Introduction

Use an hourglass structure:

1. Broad context.
2. Specific unresolved gap.
3. Why the gap matters.
4. What this study asks or tests.
5. "Here we..." contribution statement.

Do not summarize all results or conclusions in the introduction. State enough to orient the reader.

### Results

- Use past tense for observations and experiments.
- Include objects, conditions, comparisons, and quantitative values where provided.
- Describe what was observed before interpreting why it happened.
- Do not repeat every visible feature of a figure.
- Keep mechanism and broad implication mostly for Discussion.

### Discussion

- Interpret results, connect to the field, and state boundaries.
- Use calibrated language: "suggests", "is consistent with", "may reflect", "could support", or "indicates" when evidence is partial.
- Identify limitations, conditions where the finding may fail, and work needed for generalization.
- Credit earlier work without creating a straw man.

### Methods

Methods text must be specific enough for replication. Flag vague phrases and ask for missing details:

| Vague phrase | Needed detail |
| --- | --- |
| under standard conditions | temperature, medium, duration, cell line, organism, or environment |
| using routine methods | protocol, reference, instrument, or procedure |
| statistically analysed | test, software, version, correction, threshold |
| significant difference | p-value, effect size, test, sample size |
| randomly assigned | randomization method |
| validated | validation dataset, metric, comparator, or criterion |
| standard software | software name and version |

Do not fabricate missing protocol information.

### Conclusion

Use a compact three-part shape:

1. Main contribution.
2. Evidence or enabling result.
3. Boundary, implication, or next step.

Run overclaim detection before finalizing.

## Claim Calibration

Match verbs to evidence:

| Evidence strength | Preferred language |
| --- | --- |
| Direct experimental evidence | show, demonstrate, establish, reveal, identify |
| Statistical association or convergent evidence | suggest, indicate, support, are consistent with |
| Hypothesis or extrapolation | may reflect, could indicate, might support, appears to |

Soften these patterns:

- "proves" -> "shows" or "supports"
- "X causes Y" from correlation -> "X is associated with Y" or "X may contribute to Y"
- "universal" claims from one system -> specify the studied system
- "the first" -> "to our knowledge" only if the author can verify priority
- "best" or "most effective" -> define the metric and comparison set

## Vocabulary

Prefer precise verbs:

| Weak | Stronger options |
| --- | --- |
| look at | examine, investigate, probe |
| find out | determine, establish |
| make | generate, produce, yield, drive |
| use | employ, use, leverage |
| get | obtain, achieve, attain |
| change | alter, modulate, shift |
| help | enable, facilitate, enhance |
| cause | induce, trigger, drive, underlie |

Use "use" when it is clearer than "utilize". Do not over-polish simple statements.

## Citations and Attribution

- Distinguish support, method borrowing, contrast, and reuse.
- Cite primary sources for specific claims when possible.
- Do not cite a paper for a claim unless the user has verified that the paper contains the claim.
- If reusing datasets, code, images, protocols, or distinctive wording, require attribution.
- Avoid hostile positioning. Prefer "Although prior methods have shown X, Y remains insufficiently validated" over broad dismissal.

## Style Conventions

- Use British English consistently for Nature-aware drafts: analyse, colour, behaviour, modelling, signalling, centre, defence.
- Define abbreviations on first use unless universally known in the field, such as DNA, RNA, ATP, or pH.
- Use numerals for measurements, with a space between number and unit: "25 cm", "1.2 mm".
- Keep figure references consistent with the user's numbering.
- Use articles carefully for Chinese-to-English drafts: "a/an" for first countable singular mention, "the" for established entities, no article for generic plural classes.

## Self-Check Before Responding

- The polished wording preserves the user's scientific content.
- No new data, citations, or claims were invented.
- Sentences are not overloaded.
- Tense matches the section.
- Hedging matches evidence strength.
- Overclaims and missing citations are flagged.
- The output starts with the polished text unless the user requested analysis first.

## Example Prompt Fit

Use this skill for requests such as:

- "Polish this paragraph for a Nature-style introduction."
- "Translate this Chinese results paragraph into academic English."
- "Rewrite this abstract to be concise and less overclaimed."
- "Check this discussion for hedging, citation wording, and unsupported causality."
- "Improve the methods wording without adding details."
