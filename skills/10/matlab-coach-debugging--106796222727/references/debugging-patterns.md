# Debugging Patterns

Use these patterns when a MATLAB tutoring session is centered on a bug, failing
test, or unexpected output.

For instructors, the goal is to make debugging visible. Students should learn to
name the expectation, collect evidence, isolate the smallest failing case, and
then repair the code. The tutor should model that process every time.

## Diagnostic Prompts

- "What did you expect this line to produce?"
- "What did MATLAB produce instead?"
- "Which line first makes the value wrong?"
- "What are `size(x)`, `class(x)`, and the first few values?"
- "Can you make a three-line version that still fails?"
- "What test would pass if your hypothesis is correct?"

## Minimal Reproduction Template

```matlab
% Goal:
% Expected:
% Actual:

input = ...;
result = ...;

disp(result)
disp(size(result))
disp(class(result))
```

Ask the learner to remove unrelated loading, plotting, formatting, and long data
until the failure is isolated.

Instructor note: Minimal reproductions are especially useful in large lab files.
They reduce frustration and make it easier to identify whether the problem is
array shape, indexing, type, function scope, or data import.

## Teach-the-Agent Drill Template

```text
Here is a flawed AI explanation:
[short flawed explanation]

1. Which claim is wrong?
2. What MATLAB evidence would prove it?
3. What is the smallest corrected code or explanation?
4. What test distinguishes the flawed and corrected versions?
```

## Repair Feedback Template

```text
Partly correct.
Why: [tie the issue to MATLAB behavior].
Evidence: [size/class/value/error text].
Bug pattern: [name the pattern].
Next step: [one inspection, edit, or test].
```

## Common MATLAB Debugging Checks

- Shape: `size(x)`, `height(T)`, `width(T)`, `numel(x)`.
- Type: `class(x)`, `istable(x)`, `iscell(x)`, `isstring(x)`.
- Workspace: `whos`, function inputs, local variables, path conflicts.
- Numeric tolerance: `abs(actual - expected) < tol`.
- Table indexing: compare `T.Var`, `T(:, "Var")`, and `T{:, "Var"}`.
- Plot checks: axis labels, units, vector lengths, and missing values.

## Reflection Prompt

After the repair, ask:

```text
What evidence showed the bug, what MATLAB rule explained it, and how would you
recognize the same pattern next time?
```
