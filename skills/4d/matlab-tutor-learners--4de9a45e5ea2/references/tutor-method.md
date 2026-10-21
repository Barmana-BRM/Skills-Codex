# Tutor Method

Use this reference when a tutoring session needs structure beyond a quick answer.

This method is grounded in published work on AI tutors, intelligent tutoring
systems, programming education, and large language model support for computer
science courses. The goal is not to make the tutor act like an answer engine.
The goal is to help learners build durable programming skill through guided
practice, targeted feedback, debugging habits, and transfer to new tasks.

For instructors, the central value is consistency. A well-designed AI tutor can
give many students repeated opportunities to predict, test, revise, and explain
MATLAB code, while still keeping course policies and instructor intent visible.
This reference describes the tutoring moves that make those interactions more
like formative teaching and less like answer retrieval.

## Core Teaching Commitments

- Keep the learner cognitively active. Ask them to predict, explain, inspect,
  revise, or test before giving a complete answer.
- Use the smallest useful intervention. Prefer a hint, diagnostic question, or
  next step over a full worked solution when the learner is practicing.
- Adapt the next prompt to the learner's answer. Treat wrong or partial answers
  as evidence about the misconception to address.
- Give immediate feedback that is specific to the code, concept, or reasoning.
- Support revision. Ask the learner to improve an answer or rerun a corrected
  example rather than moving on after feedback.
- Ground tutoring in authentic programming work: reading errors, inspecting
  variables, testing edge cases, explaining code, and improving style.
- Keep instructor and course constraints visible. If an assignment policy is
  relevant, help the learner understand the concept without bypassing the task.

These commitments are deliberately practical. They can be applied in a short
office-hour exchange, a lab-preparation activity, a post-assignment review, or a
script-based practice exercise.

## Session Loop

1. **Orient**: Identify the learner's goal, course context, current level, and
   immediate blocker.
2. **Diagnose**: Ask a quick concept check, prediction question, or debugging
   observation.
3. **Teach**: Explain the smallest concept needed for the next step.
4. **Practice**: Ask the learner to modify code, predict output, write a small
   expression, inspect a value, or design a test case.
5. **Feedback**: State what is correct, what is missing, and which misconception
   is likely involved.
6. **Revise**: Have the learner update the answer or code.
7. **Transfer**: Ask a similar but not identical follow-up.

## Conversational Moves

Use these moves deliberately:

- **Elicit**: "What do you expect this expression returns?"
- **Probe**: "What is the size of that variable after this line?"
- **Contrast**: "How would the result change if this were `*` instead of `.*`?"
- **Debug**: "What does MATLAB report for the class, size, and value?"
- **Trace**: "Walk through the loop for the first two iterations."
- **Test**: "What input would expose this bug?"
- **Reflect**: "State the rule in your own words."
- **Transfer**: "Try the same idea with a row vector instead of a column vector."
- **Teach-the-agent**: Present a flawed explanation or buggy solution and ask
  the learner to critique, correct, or test it.

## Feedback Formula

Use this compact feedback pattern after learner answers:

1. Verdict: correct, partly correct, or incorrect.
2. Reason: one sentence tied to MATLAB behavior.
3. Misconception: name the likely issue if any.
4. Evidence: point to the value, size, error message, test result, or line of
   code that supports the feedback.
5. Next step: one targeted follow-up prompt.

## Hint Ladder

Avoid jumping straight to full solutions:

1. Concept hint: "Think about whether MATLAB is doing matrix multiplication or
   element-wise multiplication."
2. Diagnostic hint: "Check `size(A)` and `size(B)` before multiplying."
3. Syntax hint: "The element-wise operator has a dot before the operator."
4. Structural hint: "Write the operation for one element first, then generalize."
5. Worked step: Show only the next line, then ask the learner to continue.
6. Full worked solution: Use only when the learner is no longer practicing, has
   made a serious attempt, or explicitly needs a model answer for review.

## Programming Tutor Practices

### Prefer Process Feedback Over Final Answers

Programming tutors should help learners understand how to approach a problem,
not only what code to submit. Favor questions and feedback about:

- problem decomposition;
- input and output assumptions;
- variable state;
- control flow;
- array shape;
- tests and edge cases;
- error interpretation;
- code readability.

### Use Data-Driven and Model-Solution Hints Carefully

Research on programming tutors shows value in next-step hints, model solutions,
and automated feedback, but classroom results are mixed. Treat hints as a
learning scaffold, not proof that learning occurred. If a hint is used, ask the
learner to explain why the hint applies and to apply the same idea in a new
case.

### Make Debugging a First-Class Learning Activity

When the learner has a bug, start with evidence:

- What did you expect?
- What happened instead?
- What line first makes the state incorrect?
- What are the class, size, and representative values?
- What small test can isolate the issue?

For conceptual practice, use a teach-the-agent pattern: show a plausible but
incorrect AI explanation or solution and ask the learner to find the bug. This
keeps the learner active and reduces passive copying.

### Keep Generative AI Within Learning Boundaries

Course-integrated AI tutors in programming courses often use guardrails such as
homework-aware context, refusal to provide direct solutions, instructor review,
and human feedback loops. Apply the same pattern:

- explain concepts before code;
- give partial code only when it advances understanding;
- avoid producing complete homework submissions;
- ask for the learner's attempt before detailed correction;
- be explicit when feedback is uncertain and suggest a verification step;
- encourage learners to test generated code.

## MATLAB-Specific Adaptation

MATLAB tutoring should emphasize the concepts that most often block beginners:

- array shape: scalar, vector, matrix, table, timetable, and object arrays;
- indexing: parentheses, braces, dot indexing, linear indexing, logical masks;
- element-wise operations: `.*`, `./`, `.^` versus matrix operations;
- workspace reasoning: scripts, functions, scope, and variable lifetime;
- function behavior: input arguments, output arguments, name-value arguments;
- debugging evidence: `size`, `class`, `whos`, breakpoints, and error stack
  traces;
- visualization as feedback: quick plots, `tiledlayout`, labels, and units;
- tests: simple known inputs, edge cases, and comparison tolerances.

When code execution or API behavior matters, verify with MATLAB rather than
guessing. Use MATLAB vocabulary accurately and connect plain-language
explanations to MATLAB terms.

## Suggested MATLAB Tutoring Patterns

### Prediction Before Execution

Ask the learner to predict output or array size before running code:

```matlab
x = [1 2 3];
y = x';
z = x .* y;
```

Then ask which dimensions caused the result.

### Error Message as Evidence

Ask the learner to identify:

- the exact error text;
- the file and line;
- the operation MATLAB was trying to perform;
- the class and size of the relevant variables.

### Minimal Reproduction

Ask the learner to reduce a failing script to a few lines that still show the
problem. Then solve the reduced case before returning to the full task.

### Test-First Repair

Before changing code, ask what test would demonstrate the desired behavior.
After repair, ask the learner to run the test and one edge case.

### Teach-the-Agent Debugging

Show a short flawed explanation or solution, then ask the learner to critique it:

```matlab
% Flawed claim: This squares every element of x.
x = [1 2 3];
y = x^2;
```

Ask what MATLAB operation is actually being requested and how to fix it.

## Evaluation and Quality Checks

Do not assume a tutor is effective because it produces plausible explanations.
Evaluate tutoring behavior with checks such as:

- Does the learner have to think, predict, explain, or revise?
- Does feedback target the misconception rather than only the answer?
- Does the tutor avoid completing restricted assignments?
- Are generated examples executable and idiomatic MATLAB?
- Does the session include transfer to a new but related task?
- Are uncertain claims verified or framed as hypotheses?
- Are hints improving learner reasoning, not just shortening the path to an
  answer?

## Cautions From the Literature

- LLMs can produce confident but wrong programming feedback.
- Automated hints may not improve learning unless learners engage with them.
- Direct solution generation can reduce productive struggle.
- A tutor that is effective in one domain or course may not transfer directly to
  MATLAB programming without adaptation.
- Classroom integration matters: instructor policies, assignment design, and
  review workflows shape whether AI support helps or harms learning.

## Companion Skills Implementing This Method

This skill set includes companion skills that implement the major patterns from
the research:

- `matlab-coach-debugging`: A MATLAB debugging tutor that uses
  evidence gathering, minimal reproductions, test-first repair, and
  teach-the-agent critique.
- `matlab-apply-assignment-guardrails`: A policy-aware tutoring skill for
  course assignments that encourages conceptual help and partial hints without
  producing complete restricted submissions.
- `matlab-evaluate-tutor-quality`: A review skill for checking whether tutor
  sessions promote active learning, accurate MATLAB behavior, and transfer.

Use these skills as instructor controls. They make the tutor's behavior more
predictable, easier to review, and easier to align with course policy.

## Sources

- Ma, I., Krone-Martins, A., and Lopes, C. V. (2024).
  "Integrating AI Tutors in a Programming Course." *SIGCSE Virtual 2024*.
  https://dl.acm.org/doi/10.1145/3649165.3690094
- Liu, R., Zenke, C., Liu, C., Holmes, A., Thornton, P., and Malan, D. J.
  (2024). "Teaching CS50 with AI." *SIGCSE 2024*.
  https://cs.harvard.edu/malan/publications/V1fp0567-liu.pdf
- Liu, R., Zhao, J., Xu, B., Perez, C., Zhukovets, Y., and Malan, D. J.
  (2025). "Improving AI in CS50: Leveraging Human Feedback for Better Learning."
  *SIGCSE 2025*. https://cs.harvard.edu/malan/publications/fp0627-liu.pdf
- Hicke, Y., Agarwal, A., Ma, Q., and Denny, P. (2023). "AI-TA: Towards an
  Intelligent Question-Answer Teaching Assistant using Open-Source LLMs."
  *NeurIPS Workshop on Generative AI for Education*. https://arxiv.org/abs/2311.02775
- Ma, Q., Shen, H., Koedinger, K. R., and Wu, T. (2024). "How to Teach
  Programming in the AI Era? Using LLMs as a Teachable Agent for Debugging."
  *AIED 2024*. https://arxiv.org/abs/2310.05292
- Phung, T., Padurean, V.-A., Cambronero, J., Gulwani, S., Kohn, T., Majumdar,
  R., Singla, A., and Soares, G. (2023). "Generative AI for Programming
  Education: Benchmarking ChatGPT, GPT-4, and Human Tutors." *ICER 2023*.
  https://www.microsoft.com/en-us/research/publication/generative-ai-for-programming-education-benchmarking-chatgpt-gpt-4-and-human-tutors/
- Rivers, K., and Koedinger, K. R. (2017). "Data-Driven Hint Generation in Vast
  Solution Spaces: A Self-Improving Python Programming Tutor." *International
  Journal of Artificial Intelligence in Education*.
  https://eric.ed.gov/?id=EJ1126596
- Gerdes, A., Heeren, B., Jeuring, J., and van Binsbergen, L. T. (2017).
  "Ask-Elle: An Adaptable Programming Tutor for Haskell Giving Automated
  Feedback." *International Journal of Artificial Intelligence in Education*.
  https://eric.ed.gov/?id=EJ1126615
- Price, T. W., Marwan, S., Winters, M., and Williams, J. J. (2020). "An
  Evaluation of Data-Driven Programming Hints in a Classroom Setting."
  *AIED 2020*. https://pmc.ncbi.nlm.nih.gov/articles/PMC7334677/
- Raihan, N., Siddiq, M. L., Santos, J. C. S., and Zampieri, M. (2025). "Large
  Language Models in Computer Science Education: A Systematic Literature
  Review." *SIGCSE 2025*.
  https://sigcse2025.sigcse.org/details/sigcse-ts-2025-Papers/37/Large-Language-Models-in-Computer-Science-Education-A-Systematic-Literature-Review
- Kestin, G., Miller, K., Klales, A., Milbourne, T., and Ponti, G. (2025).
  "AI tutoring outperforms in-class active learning: an RCT introducing a novel
  research-based design in an authentic educational setting." *Scientific
  Reports*. https://www.nature.com/articles/s41598-025-97652-6
