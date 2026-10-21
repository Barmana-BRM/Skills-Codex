# Course AI Policy Examples

Use these examples to calibrate `AI-POLICY.md` generation. Adapt them to the
instructor's stated rules rather than copying them blindly.

## Example 1: Homework Help

Policy intent: Students may use the MATLAB AI Tutor for learning support, but
submitted homework should reflect their own reasoning.

Recommended settings:

```yaml
overall_stance: allowed_with_limits
local_enforcement: standard
activity_rules:
  homework: coached
allowed_help:
  - Concept explanations
  - Smaller analogous examples
  - Debugging learner attempts
  - Tests and sanity checks
  - Review after a meaningful attempt
restricted_help:
  - Complete final homework solutions
  - Filling every blank in starter code
  - Polishing code before the learner has a meaningful attempt
disclosure_required: conditional
session_report_required: conditional
transcript_required: false
```

Learner-facing wording:

```text
You may use the MATLAB AI Tutor for homework concept help, debugging your own
attempt, smaller analogous examples, and tests. Do not ask the tutor to produce
a complete final answer or fill in all required code. If AI help materially
affected your submitted work, include the required disclosure statement.
```

## Example 2: Lab Submissions

Policy intent: Students may use the tutor during labs, but the tutor should keep
the learner active and preserve lab learning objectives.

Recommended settings:

```yaml
overall_stance: encouraged
local_enforcement: standard
activity_rules:
  labs: coached
allowed_help:
  - Interpreting lab instructions
  - Debugging using error text, size, class, and output checks
  - Explaining MATLAB syntax and functions
  - Reviewing learner-generated code
  - Creating session reports for reflection
restricted_help:
  - Completing the lab before the learner has made an attempt
  - Bypassing required lab steps or hidden checks
  - Fabricating results or analysis
disclosure_required: conditional
session_report_required: conditional
transcript_required: false
```

Learner-facing wording:

```text
You may use the tutor during labs to understand MATLAB behavior, debug your
attempt, and check whether your results are reasonable. You are responsible for
the final code, analysis, and interpretation you submit.
```

## Example 3: Projects

Policy intent: Projects require more student independence, especially for design
decisions and final implementation.

Recommended settings:

```yaml
overall_stance: restricted
local_enforcement: strict
activity_rules:
  projects: review_only
allowed_help:
  - Planning and concept clarification
  - Reviewing learner-written code
  - Identifying bugs or test gaps
  - Suggesting next diagnostic steps
restricted_help:
  - Writing major project functions or full scripts
  - Rewriting the project into submission-ready form
  - Making design decisions the assignment asks the learner to make
disclosure_required: true
session_report_required: conditional
transcript_required: conditional
```

Learner-facing wording:

```text
For projects, use the tutor for planning, concept clarification, debugging your
own draft, and review. Do not use the tutor to write substantial project code or
make core design decisions for you. Disclose AI assistance as required.
```

## Example 4: Quizzes and Exams

Policy intent: AI help is not allowed on quizzes, exams, or restricted
take-home assessments unless the instructor explicitly authorizes it.

Recommended settings:

```yaml
overall_stance: restricted
local_enforcement: assessment_lockout
activity_rules:
  quizzes: no_ai
  exams: no_ai
  take_home_assessments: no_ai
allowed_help:
  - Policy clarification
  - Instructor-authorized accommodations only
restricted_help:
  - Answering quiz or exam questions
  - Generating code, explanations, or reasoning for active assessments
  - Checking answers during a restricted assessment
disclosure_required: true
session_report_required: false
transcript_required: false
```

Learner-facing wording:

```text
Do not use the MATLAB AI Tutor or other AI tools on quizzes, exams, or
restricted take-home assessments unless the instructor explicitly authorizes it.
The tutor may clarify this policy but should not help solve assessment items.
```

## Example 5: Instructor-Facing Solution Generation

Policy intent: Instructors may use the tutor to create solutions, rubrics, test
cases, and teaching materials, but those materials should be labeled
instructor-facing and not exposed as learner support.

Recommended settings:

```yaml
overall_stance: allowed_with_limits
local_enforcement: standard
activity_rules:
  instructor_facing_materials: instructor_only
allowed_help:
  - Drafting instructor solutions
  - Creating rubrics and feedback notes
  - Generating tests and expected outputs
  - Creating analogous examples for students
restricted_help:
  - Presenting answer keys as student tutoring help
  - Mixing instructor-only solutions into learner sessions
  - Claiming generated materials are official without instructor review
disclosure_required: false
session_report_required: false
transcript_required: false
```

Instructor-facing wording:

```text
Instructor-facing materials may include complete solutions, rubrics, test cases,
and feedback examples. Label these materials clearly and keep them separate from
student tutoring interactions.
```

## Choosing Between Examples

- Use **homework help** when assignments are graded but formative and learners
  are expected to practice independently.
- Use **lab submissions** when students work through structured MATLAB tasks and
  can benefit from debugging support during the activity.
- Use **projects** when design, implementation, and interpretation are central
  learning outcomes.
- Use **quizzes and exams** for high-stakes or restricted assessments.
- Use **instructor-facing solution generation** when the user is clearly an
  instructor or content author.
