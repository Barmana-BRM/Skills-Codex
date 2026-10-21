# Paragraph Job Archetypes

## Purpose

This file defines the semantic job of each H3 paragraph family.
Use it to decide which move the writer should perform.
Do not treat the matching asset templates as reader-facing copy to preserve verbatim.

## Setup

Intent:
- establish the subsection's comparison frame
- make the thesis legible early
- state why the evidence is unstable or contested

Required slots:
- one opener mode tied to the pack's actual pressure
- thesis
- optional tension follow-up
- optional seed record only when it sharpens the frame

Avoid:
- narrating the subsection itself
- opening with a method list
- using the same opener cadence across many H3s

## Mechanism Contrast

Intent:
- show what each route changes in the system
- connect that design choice to a concrete consequence

Required slots:
- one cluster-specific lead
- evidence-bearing support
- one closing only if it sharpens the contrast

Avoid:
- using the cluster label as a bare grammatical subject everywhere
- repeating `what matters is ...` as the default closer

## Implementation

Intent:
- expose where similar-looking systems actually diverge
- tie architecture labels to concrete training, control, or data choices

Required slots:
- implementation split lead
- concrete system evidence
- close on what remains structurally comparable

Avoid:
- generic `implementation layer matters because ...` reuse
- fixed closers such as `At implementation level, the decisive issue is ...`
- fixed closers such as `The implementation contrast matters because ...`
- implementation paragraphs that just restate the mechanism paragraph

## Evaluation

Intent:
- keep task, metric, and constraint near the claim
- show when a reported gain is trustworthy

Required slots:
- evaluation lead
- at least one benchmark / protocol-bearing fact when available
- caveat or protocol boundary

Avoid:
- count-based limitation stems
- repeated caveat shells such as `Interpretation becomes harder once ...`
- repeated caveat shells such as `This comparison weakens if ...`
- clause-fragile wrappers that force a full proposition into `if/when/once/while ...`
- evaluation paragraphs that float without protocol context

## Synthesis

Intent:
- compare clusters at subsection level, not per-paper level
- identify the axis that really separates the evidence

Required slots:
- synthesis lead
- one or two explicit cross-cluster comparisons
- fallback only when the cards are thin

Avoid:
- replaying the same axis-cloned sentence across multiple H3s
- turning synthesis into another local summary

## Decision

Intent:
- translate the subsection contrast into a setting-dependent choice
- explain what assumption the user / reader must fix first

Required slots:
- decision lead
- optional paired contrast sentence
- protocol close when the claim depends on aligned evaluation

Avoid:
- pretending there is one winner independent of setting
- using the same operational advice sentence in every H3

## Limitation

Intent:
- end on the uncertainty that materially changes interpretation
- push the paper toward bounded claims instead of soft filler

Required slots:
- limitation lead
- one or two evidence-backed caveats
- protocol or RQ fallback only if it adds information

Avoid:
- generic future-work endings
- limitation paragraphs that merely apologize for sparse evidence
