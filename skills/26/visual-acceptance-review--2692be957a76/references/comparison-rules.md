# Comparison Rules

## Overall Match

Check:

- does the rendered page look like reference.png?
- is UI type preserved?
- is layout paradigm preserved?
- is visual hierarchy preserved?
- is the main visual layer present?

## Region Layout

Compare:

- position
- size
- margin
- padding
- z-index
- overlay placement
- panel placement
- thumbnails
- controls

## Components

Compare against `component-tree.md`.

Check:

- required visible components present
- prohibited components absent
- no hallucinated components reintroduced
- expected labels/icons/controls appear

## Colors

Compare against `tokens.json`.

If no exact color script exists:

- describe qualitative difference
- include confidence
- do not claim exact delta-E

## Typography

Check:

- font size
- weight
- hierarchy
- readability
- label alignment

## Spacing

Check:

- panel padding
- control spacing
- scene-to-overlay balance
- density

## Responsive

Compare tablet/mobile against responsive-spec.md.

Fail if responsive behavior changes UI Type or hides required primary visual.

## Browser Health

Fail if console/network errors break main visual or required controls.
