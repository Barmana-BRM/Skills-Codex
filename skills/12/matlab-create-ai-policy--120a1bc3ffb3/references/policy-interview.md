# Course AI Policy Interview

Use this sequence to interview instructors. Ask at most three questions per
round. Fill in defaults only when the instructor explicitly accepts them or when
the skill marks them as conservative defaults.

## Round 1: Course Context

Ask:

1. What is the course title, term, audience, and instructor name (or role), and
   how should students reach you or course support?
2. What kinds of MATLAB work will students do: homework, labs, projects,
   quizzes, exams, or something else?
3. Should the overall AI-use stance be encouraged, allowed with limits,
   restricted, or prohibited except when explicitly authorized?

## Round 2: Activity Rules

For each activity type, capture one policy level:

- **Open**: AI tutor use is allowed for explanations, debugging, examples, and
  substantial code help.
- **Coached**: AI tutor use is allowed for concepts, hints, debugging, tests,
  analogous examples, and review after a meaningful attempt.
- **Review-only**: AI tutor use is allowed only after the learner has a draft,
  and the tutor may identify issues but not write or rewrite the submission.
- **No AI**: AI tutor use is not allowed except for policy clarification or
  instructor-authorized accommodations.
- **Instructor-only**: Solutions, answer keys, rubrics, and grading artifacts
  may be generated only for instructor-facing use.

Recommended defaults:

- Homework: Coached.
- Labs: Coached.
- Projects: Review-only or Coached, depending on course goals.
- Quizzes and exams: No AI unless explicitly authorized.
- Take-home assessments: No AI or Review-only, depending on policy.
- Instructor-facing materials: Instructor-only.

## Round 3: Allowed and Restricted Help

Capture allowed help:

- concept explanations;
- MATLAB syntax examples;
- smaller analogous examples;
- debugging using error text, `size`, `class`, values, and tests;
- reviewing learner attempts;
- writing tests or sanity checks;
- session reports and transcript logs;
- study planning and reflection.

Capture restricted help:

- complete final answers or full programs for restricted work;
- filling every blank in starter code;
- generating quiz, exam, or take-home answers;
- bypassing hidden tests or assignment constraints;
- polishing or optimizing work before a meaningful learner attempt;
- submitting AI-generated work without required disclosure.

## Round 4: Disclosure and Evidence

Ask:

1. Must students disclose AI tutor use?
2. Should they submit a transcript, session report, prompt log, or short
   reflection?
3. What information should students avoid sharing with the tutor?

Common disclosure options:

- No disclosure needed for unrestricted practice.
- Short disclosure statement required for graded assignments.
- Session report or transcript required for all graded work.
- Session report or transcript required for selected assignments.
- Prompt and output excerpts required when AI materially affected the work.

## Round 5: Local Enforcement

Choose one enforcement level for MATLAB AI Tutor guardrails:

- **Advisory**: Tutor reminds students of policy and encourages disclosure.
- **Standard**: Tutor asks for learner attempts on graded work and refuses final
  restricted submissions.
- **Strict**: Tutor provides only concepts, diagnostics, analogous examples, and
  review after attempts for graded work.
- **Assessment lockout**: Tutor refuses help on quizzes, exams, and restricted
  take-home assessments except policy clarification.

Recommended default: Standard for courses with homework/labs; Strict or
Assessment lockout for high-stakes assessments.

The policy records one enforcement level.
When different activities need different enforcement, choose the strictest level
any activity requires and describe the per-activity behavior in the policy's
enforcement section.

## Round 6: Housekeeping

Ask:

1. What effective date and policy version should the file carry?
2. How often will you review this policy (each term, each year, or as needed)?

Accept "start of term, version 1.0, reviewed each term" as the default when the
instructor has no preference.

## Confirmation Prompt

Before writing `AI-POLICY.md`, summarize:

- course, term, and contact path;
- overall stance;
- activity-level rules;
- disclosure requirement;
- local enforcement level;
- effective date, version, and review cadence;
- unresolved placeholders.

Ask the instructor to confirm or revise any high-stakes item.
