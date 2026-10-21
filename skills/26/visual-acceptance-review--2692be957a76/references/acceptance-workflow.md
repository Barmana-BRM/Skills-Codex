# Acceptance Workflow

## Purpose

Compare actual browser rendering against the approved reference design and visual contract.

## Workflow

### Step 1 — Preflight

Check:

- visual-spec-review status
- spec-compliance-review status
- screenshot capability
- reference.png availability
- dev server URL or actual screenshot availability

### Step 2 — Capture Screenshots

Capture:

- desktop HD
- desktop
- tablet
- mobile

Also capture:

- console errors
- network errors

### Step 3 — Overall Comparison

Compare actual desktop screenshot with reference.png.

Check:

- visual identity
- UI type
- layout paradigm
- visual hierarchy
- main visual / overlay relationship

### Step 4 — Contract-Based Comparison

Use:

- layout-spec.md
- component-tree.md
- tokens.json
- implementation-risks.md
- responsive-spec.md

### Step 5 — Region Diffs

Write region-level reports under:

```text
region-diffs/
```

### Step 6 — Generate Fix Tasks

Write `fix-tasks.json` for visual-diff-fix.

### Step 7 — Final Decision

Output:

- Pass
- Conditional Pass
- Fail
- Blocked
