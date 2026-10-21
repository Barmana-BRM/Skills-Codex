# MATLAB Course Designer Artifacts

Use these rules for MATLAB Course Designer-ready MATLAB Exercise output.

## Folder Structure

```text
matlab-activities/
└── module-NN-activity-MM-[slug]/
    ├── activity.md
    ├── background.m
    ├── task.m
    ├── instructor-notes.md
    ├── validation-report.md
    ├── course-designer-activity.json
    └── grader-source.md
```

The shared component files remain in the `matlab-generate-grader-assessments` output folder unless the
course packaging workflow needs local copies.

`grader-source.md` records the mapping to that source folder:

- Path to the `grader-items/` folder for this activity
- The component files it contains (including `function_call.m` or
  `supporting_class.m` when the item type produces them)
- Which skill generated them
- Whether `description.txt` was modified after generation (it must not be)
- Any post-generation changes to component files, with the reason

## Activity Markdown

`activity.md` is learner-facing and should include:

- Title
- Background summary
- Learning objective
- Learner task
- Starter code file name or reference
- Expected evidence or submission
- Required products and toolboxes
- Setup steps

## Course Designer Copy/Paste Fields

Create `background.m` and `task.m` as plaintext `.m` files from
`description.txt`. These are copy/paste field transport files, not executable
MATLAB scripts.

Use the MATLAB Course Designer create-MATLAB-Exercise documentation as the
source of truth for the Background and Task field purposes:
https://www.mathworks.com/help/matlab-and-simulink-online-courses/ug/create-matlab-exercise-using-matlab-course-designer.html

`background.m` should contain:

- Context for the exercise task
- The learning objective in learner-facing language
- High-level information learners need before starting
- Prerequisite concepts only when needed to complete the task

`task.m` should contain:

- Instructions learners follow to complete the task
- Ordered steps when sequencing matters
- Required file, variable, function, class, or object names
- Expected outputs or evidence
- Constraints
- Self-check prompts that do not reveal hidden tests

Do not prefix prose with `%` solely to make these files valid MATLAB code; the
text should be ready to paste into MATLAB Course Designer text fields. These
files are not replacements for `template.m`, `solution.m`, or `tests.m`.

Field alignment check:

- `background.m` must not contain detailed step-by-step instructions, required
  variable names, or deliverable lists unless they are unavoidable context.
- `task.m` must not contain broad exposition that belongs in the background.
- `task.m` must be specific enough that a learner knows which MATLAB artifacts
  to create or edit, which names to preserve, and what output or evidence to
  produce.
- Neither file should include hidden tests, reference solution details, or
  grading mechanics unless those details are intentionally learner-facing.

## Instructor Notes

`instructor-notes.md` should include:

- `matlab-generate-grader-assessments` source folder
- `solution.m` path
- `template.m` path
- `tests.m` path
- `background.m` path
- `task.m` path
- Intended learner gaps in the template
- Expected behavior
- Validation method
- Known limitations

## Course Designer Metadata

Write `course-designer-activity.json` with this shape:

```json
{
  "course": {
    "title": "",
    "id": ""
  },
  "module": {
    "title": "",
    "order": 1
  },
  "learningActivity": {
    "title": "",
    "order": 1,
    "type": "MATLAB Exercise",
    "backgroundFile": "background.m",
    "taskFile": "task.m",
    "objective": "",
    "estimatedTimeMinutes": 0,
    "assessmentPurpose": "",
    "assessmentItemType": "",
    "prerequisiteContext": "",
    "learnerSetupNotes": ""
  },
  "graderSource": {
    "folder": "",
    "description": "description.txt",
    "template": "template.m",
    "solution": "solution.m",
    "tests": "tests.m",
    "functionCall": "function_call.m (Function items only)",
    "generatedBy": "matlab-generate-grader-assessments",
    "descriptionModified": false,
    "postGenerationChanges": []
  },
  "products": {
    "required": ["MATLAB"],
    "toolboxes": []
  },
  "validation": {
    "status": "passed|partial|failed",
    "checks": []
  },
  "persistence": {
    "commonCartridgePath": "",
    "courseDesignerApiReady": true
  }
}
```

Keep paths relative to the course output folder when possible. This sidecar is
the future Course Designer API bridge and should be complete even when Common
Cartridge packaging is also used.
