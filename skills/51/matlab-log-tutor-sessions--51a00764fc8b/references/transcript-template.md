# Transcript Template

Use Markdown by default. The transcript is an evidence artifact, not a polished
session report.

## Header

```markdown
# MATLAB AI Tutor Transcript

- Session date:
- Transcript status: Real | Synthetic | Partial | Reconstructed | Mixed
- Learner goal:
- Course or assignment context:
- Assignment policy status: Unrestricted | Possibly graded | Graded | Unknown
- MATLAB topics:
- Tools or MATLAB products used:
- Omitted or unavailable content:
```

## Session Markers

Use short markers only when they help an instructor or evaluator follow the
session.

```markdown
## Session Markers

- [00:00] Session started; learner asked about array indexing.
- [00:04] Assignment guardrail check; learner confirmed this was lab practice.
- [00:08] MATLAB execution evidence added for script output.
- [00:12] Transfer prompt given for a different array shape.
```

If timestamps are unavailable, use turn numbers:

```markdown
- [Turn 3] Learner shared error message.
```

## Turn Format

~~~markdown
## Transcript

### Turn 1 - Learner
Content:

```text
Learner message here.
```

Evidence tags: learner-goal, assignment-context

### Turn 2 - Tutor
Content:

```text
Tutor message here.
```

Tutor moves: active-learning, guardrail
Evidence tags: prompt, question
~~~

Use exact wording when available. If a turn is summarized rather than exact,
prefix it with `Summary:` and mark the transcript as partial or reconstructed.

## MATLAB Evidence Blocks

Attach evidence near the relevant turn.

~~~markdown
MATLAB evidence:

```matlab
% Code shared, generated, or executed
x = [1 2 3];
y = x.^2;
```

```text
Observed output, error message, Code Analyzer warning, or test result.
```

Evidence tags: matlab-code, execution-output, error-text, code-analyzer,
test-result, inspected-size, inspected-class
~~~

## Recommended Tags

Tutor moves:

- `active-learning`
- `direct-explanation`
- `feedback`
- `guardrail`
- `debugging-support`
- `transfer`
- `metacognitive-prompt`

Evidence tags:

- `learner-goal`
- `assignment-context`
- `matlab-code`
- `execution-output`
- `error-text`
- `code-analyzer`
- `test-result`
- `inspected-value`
- `inspected-size`
- `inspected-class`
- `learner-revision`
- `unresolved-issue`

## Export Notes

End every instructor-shareable transcript with:

```markdown
## Export Notes

- Completeness:
- Synthetic or reconstructed content:
- Privacy omissions:
- Known limitations for evaluation:
```

For synthetic transcripts, state the scenario and learning objective. Do not
present synthetic evidence as a real learner record.
