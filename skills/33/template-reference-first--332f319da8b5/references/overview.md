# Overview

## Purpose

This file carries the reusable method behind a reference-first skill.

Read it before editing the template or turning it into a concrete skill.

## Role split

### `SKILL.md`

Use `SKILL.md` as the entrypoint and router.

Keep only:
- trigger conditions
- problem statement
- inputs and outputs
- step-by-step workflow
- block conditions
- which reference files to load and when
- which assets and scripts exist

Keep out of `SKILL.md`:
- long domain summaries
- large example catalogs
- detailed rubrics that belong in references
- prose banks that another agent might copy verbatim

### `references/`

Use `references/` for the parts that help the model think correctly:
- domain summaries
- decision rubrics
- evidence policies
- good and bad examples
- persona-specific framing guidance
- variant- or domain-pack notes

References should be written for selective reading. Each file should have a clear purpose and a visible scope.

### `assets/`

Use `assets/` for things the script or deliverable consumes directly:
- JSON or YAML schema
- static templates
- machine-readable configuration packs
- palettes or style resources

Assets should not be the main place where judgment rules are hidden.

### `scripts/`

Use scripts for deterministic tasks only:
- discovering files
- reading and writing structured data
- normalizing fields
- validating outputs
- producing manifests and reports
- calling external tools

Do not use scripts for:
- hard-coded domain defaults
- paragraph templates
- reader-facing sentence libraries
- filler text for missing evidence
- final judgment that should live in references or explicit instructions

## Progressive disclosure

Design the package so another agent can work in this order:
1. read `SKILL.md`
2. load only the relevant reference files
3. use assets and scripts as needed

If a skill supports multiple domains or variants, make the selection rule explicit in `SKILL.md` and keep the variant-specific details in references or domain packs.

## Reader-facing hygiene

When the skill emits text for a human reader:
- prefer concrete, bounded language
- keep internal pipeline terms out of the final artifact unless the artifact itself is internal
- avoid unresolved placeholders, truncation markers, and scaffold text
- do not rely on meta narration such as section signposting when a content-bearing sentence can do the job

Good hygiene questions:
- Would a reader understand the artifact without knowing the pipeline?
- Does every example sound like a finished sentence rather than a slot pattern?
- Are the risks and decision criteria concrete enough to act on?

## Domain-pack rule

Keep generic skills generic.

If a domain needs special treatment, externalize it as a named domain pack and mention the selection rule in `SKILL.md`. Do not bury domain-specific rules in Python constants.

## Customization checklist

Before copying this template into a real skill, confirm:
- the skill name describes a reusable action
- the trigger description matches how users will ask for the capability
- the references reflect the actual judgments the agent must make
- the schema matches the structured artifact the skill cares about
- the script can stay small after customization
