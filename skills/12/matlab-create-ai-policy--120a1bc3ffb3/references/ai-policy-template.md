# AI-POLICY.md Template

Use this template to write the final `AI-POLICY.md` file. The file should be
learner-facing and suitable for LMS upload.

~~~markdown
# AI Use Policy for [Course Title]

**Term:** [term]
**Instructor:** [name or role]
**Contact:** [contact or support path]
**Effective date:** [date]
**Policy version:** [version]
**Review cadence:** [when this policy is reviewed]

## Purpose

This policy explains when and how you may use AI tools, including the MATLAB AI
Tutor, in this course. The goal is to support learning while preserving the
meaning of your submitted work.

## Course-Wide AI Use Stance

[Encouraged | Allowed with limits | Restricted | Prohibited except when
explicitly authorized]

[Plain-language explanation.]

## Rules by Activity Type

| Activity | AI tutor use | What this means |
| --- | --- | --- |
| Homework | [Open/Coached/Review-only/No AI] | [rule] |
| Labs | [Open/Coached/Review-only/No AI] | [rule] |
| Projects | [Open/Coached/Review-only/No AI] | [rule] |
| Quizzes | [Open/Coached/Review-only/No AI] | [rule] |
| Exams | [Open/Coached/Review-only/No AI] | [rule] |
| Take-home assessments | [Open/Coached/Review-only/No AI] | [rule] |
| Instructor-facing materials | Instructor-only | [rule] |

For an activity type the course does not have, write "Not offered" in the table
and set the matching `activity_rules` key to `not_applicable`; do not invent a
rule.

## Allowed Uses

- [allowed use]
- [allowed use]
- [allowed use]

## Restricted Uses

- [restricted use]
- [restricted use]
- [restricted use]

## Disclosure and Submission Requirements

[State whether students must disclose AI use, include a session report,
transcript, prompt log, or reflection.]

Suggested disclosure statement:

> I used the MATLAB AI Tutor for [concept help/debugging/review/etc.]. I used
> the assistance to [brief description]. The submitted work reflects my own
> understanding and final decisions.

## Privacy and Data Boundaries

Do not share private personal information, other students' work, confidential
data, access tokens, passwords, unpublished research data, or restricted course
materials unless the instructor explicitly authorizes it.
[Add any course-specific items the instructor named during the interview.]

## Local MATLAB AI Tutor Enforcement

[Describe local enforcement level in learner-facing language.]

## If You Are Unsure

Ask the instructor before using AI assistance on graded or assessment-like work.
When in doubt, use the tutor for concepts, debugging your own attempt, tests, or
smaller analogous examples rather than final answers.

## Open Items for Instructor Review

[Optional section. List unresolved placeholders and conservative defaults the
instructor should confirm, then delete this section before releasing the policy
to students. This is the sanctioned place for placeholders; the rest of the
file stays learner-facing.]

## Policy Summary for Tutor Guardrails

```yaml
policy_file: AI-POLICY.md
course: [course title]
term: [term]
overall_stance: [encouraged|allowed_with_limits|restricted|prohibited_unless_authorized]
local_enforcement: [advisory|standard|strict|assessment_lockout]
activity_rules:
  homework: [open|coached|review_only|no_ai]
  labs: [open|coached|review_only|no_ai]
  projects: [open|coached|review_only|no_ai]
  quizzes: [open|coached|review_only|no_ai]
  exams: [open|coached|review_only|no_ai]
  take_home_assessments: [open|coached|review_only|no_ai]
  instructor_facing_materials: instructor_only
allowed_help:
  - [allowed help]
restricted_help:
  - [restricted help]
disclosure_required: [true|false|conditional]
session_report_required: [true|false|conditional]
transcript_required: [true|false|conditional]
```
~~~

## Guardrail Interpretation

When applying the policy:

- `open`: provide normal tutoring support, but keep the learner active.
- `coached`: require attempts for assignment-specific help; use hints,
  diagnostics, analogous examples, tests, and limited next-step edits.
- `review_only`: review learner work after a meaningful attempt; do not write or
  rewrite the submission.
- `no_ai`: refuse task help and redirect to policy clarification or instructor
  contact.
- `instructor_only`: complete instructor-facing materials only when the user is
  clearly acting as instructor or content author.
- `not_applicable`: the course has no such activity; if a request still arrives
  for one, fall back to the course-wide stance and conservative defaults.

`local_enforcement` is a single value.
When different activities need different enforcement, set it to the strictest
level any activity requires and describe the per-activity behavior in the
"Local MATLAB AI Tutor Enforcement" section.
