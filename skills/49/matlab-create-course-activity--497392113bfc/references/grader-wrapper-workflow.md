# Grader Wrapper Workflow

Use this workflow to create MATLAB Exercise component parts through the existing
`matlab-generate-grader-assessments` skill.

## Build Order

1. Convert the module objective into one measurable MATLAB learning objective.
2. Choose the `matlab-generate-grader-assessments` assessment type:
   - Script
   - Function
   - Class
   - Object usage
3. Choose assessment purpose:
   - Formative
   - Summative
   - Both
4. Invoke or prompt `matlab-generate-grader-assessments`.
5. Review that `matlab-generate-grader-assessments` created:
   - `description.txt`
   - `template.m`
   - `solution.m`
   - `tests.m`
6. Keep the `matlab-generate-grader-assessments` folder as the source for shared MATLAB Exercise component
   parts.

## Output Folder

Use:

```text
grader-items/module-NN-activity-MM-[slug]/
```

## Mapping to MATLAB Exercise

Map `matlab-generate-grader-assessments` output to Course Designer as follows:

| Grader artifact | MATLAB Exercise use |
| --- | --- |
| `description.txt` | Source text split into `background.m` and `task.m` |
| `template.m` | Starter code |
| `solution.m` | Instructor solution/reference |
| `tests.m` | Validation and assessment logic |

After `matlab-generate-grader-assessments` finishes, split `description.txt` into Course Designer
copy/paste fields:

- `background.m`: task context, learning objective, and high-level information
  learners need before starting.
- `task.m`: instructions learners follow, including deliverables, required
  names, constraints, expected outputs, and self-check prompts.

Course Designer-only fields such as estimated time, prerequisite context,
product requirements, and module placement are added after the split.
