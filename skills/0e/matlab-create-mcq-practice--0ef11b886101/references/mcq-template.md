# MATLAB MCQ Template

Use this structure when creating question banks or quiz artifacts.
In a live quiz session, the `Correct answer:`, `Feedback:`, and `Follow-up:`
fields are artifact-only: present the question through the choices, wait for
the learner's answer, and deliver those fields in the feedback turn.

For instructors, the best MCQs are diagnostic. Each wrong answer should reveal a
plausible MATLAB misconception, such as confusing matrix and element-wise
operators, expecting zero-based indexing, or misreading table extraction.

```markdown
### Question [N]: [Short Title]

Learning objective: [Observable skill]
Difficulty: [Novice | Developing | Proficient]
Topic: [MATLAB topic]

Prompt:
[Question text]

```matlab
[Optional code snippet]
```

A. [Choice]
B. [Choice]
C. [Choice]
D. [Choice]

Correct answer: [Letter]

Feedback:
- A: [Why a learner might choose it; why right/wrong]
- B: [Why a learner might choose it; why right/wrong]
- C: [Why a learner might choose it; why right/wrong]
- D: [Why a learner might choose it; why right/wrong]

Follow-up:
[One next question or small coding task]
```

## Quality Checklist

- The code snippet is short and deterministic.
- The snippet and correct answer were verified by execution when a MATLAB
  session was available.
- The question tests MATLAB behavior, not trivia.
- Distractors are plausible and diagnostic.
- The correct answer is not made obvious by wording length.
- Feedback teaches the underlying rule.
- The follow-up requires transfer, not repetition.

Instructor check: Before using a question, ask what you would do instructionally
if students choose each distractor. If a distractor does not point to a teaching
response, replace it.

## Common MCQ Formats

### Predict the Output

Ask what MATLAB displays or stores after a snippet.

### Find the Error

Ask which line fails and why.

### Choose the Idiom

Ask which MATLAB expression is most appropriate.

### Interpret the Data Operation

Use `table`, logical indexing, or grouped operations and ask what rows/values result.

### Test the Function

Show a function and ask which test case best catches a bug.

## Example Feedback Style

```text
Not quite. Choice B is tempting because it treats x as a scalar, but x is a
1-by-3 vector. MATLAB applies .^ element-by-element, so the result keeps the
same size as x. Try the same prediction when x is a column vector.
```
