# Setup Guide Template

Use this reference when generating an instructor setup guide from a course title,
syllabus idea, module description, lab sequence, or rollout goal.

## Context Mapping

Choose the best-fit context from the input.

**Introductory MATLAB programming**

- Triggers: intro, first programming course, arrays, indexing, scripts,
  functions, plotting, loops.
- MATLAB emphasis: guided scripts, functions, and MATLAB Exercise practice.
- Simulink emphasis: optional demos only unless modeling is an explicit goal.
- Review emphasis: learner setup, naming consistency, clear templates, small
  assessments.

**Engineering computation with MATLAB and Simulink**

- Triggers: engineering, numerical methods, dynamics, controls, ODEs,
  simulation, modeling, design.
- MATLAB emphasis: reusable calculations, data analysis, plotting.
- Simulink emphasis: simulation experiments, model completion, control design.
- Review emphasis: starter `.slx`, solution `.slx`, units, assumptions,
  tolerances, model behavior, rubrics.

**Data analysis or AI course**

- Triggers: data, statistics, machine learning, AI, visualization, tables,
  apps, workflows.
- MATLAB emphasis: data import, cleaning, models, visualization, apps.
- Simulink emphasis: include only when model-based systems are part of the
  course.
- Review emphasis: datasets, reproducibility, compute requirements, privacy.

**Model-based design course**

- Triggers: Simulink, model-based design, control systems, physical modeling,
  verification, code generation.
- MATLAB emphasis: parameter scripts, analysis, post-processing.
- Simulink emphasis: model construction, simulation, requirements, tests.
- Review emphasis: starter models, solution models, expected signals, model
  validation, product requirements.

**MATLAB Exercise assessment course**

- Triggers: auto-graded MATLAB Exercises, homework-style practice, code tests.
- MATLAB emphasis: use `matlab-create-course-activity` to wrap `matlab-generate-grader-assessments`, create
  Script, Function, Class, or Object usage component parts, and validate `.m`
  files for MATLAB Exercises.
- Simulink emphasis: use Simulink Exercises for model-based work.
- Review emphasis: generated `description.txt`, `solution.m`, `template.m`,
  and `tests.m` from the `matlab-generate-grader-assessments` skill, MATLAB MCP validation results, and
  Course Designer copy/paste fields `background.m` and `task.m`.

**Common Cartridge or downstream LMS migration**

- Triggers: Canvas, Blackboard, Moodle, D2L, Brightspace, LMS, Common Cartridge,
  `.imscc`, import, export.
- Export emphasis: IDStack `course-export` with IMS Common Cartridge selected.
- Review emphasis: sandbox import, module order, links, rubrics, product
  requirements, and placeholder dates.

**MATLAB Course Designer structure**

- Triggers: Course Designer, modules, learning activities, course instance,
  web application, API creation.
- Structure emphasis: course metadata, ordered modules, and ordered learning
  activities.
- Activity emphasis: only native Course Designer activity types: Reading,
  Video, MATLAB Exercise, and Simulink Exercise.
- Review emphasis: `course-designer-structure.md` matches the course -> modules
  -> learning activities hierarchy.

## Output Format

```markdown
# MATLAB and Simulink Course Setup Guide: [Course or Goal]

## Best Fit
- Context:
- Why this fit:
- Secondary considerations:

## Prerequisites
- Agent skills:
- MathWorks access: [always include the MATLAB MCP Server connected to a
  licensed MATLAB session; it is what runs all `.m` file and model validation]
- Course Designer access:
- Downstream LMS access, if relevant:

## Starter Prompt for `matlab-generate-course`
[Instructor-ready prompt text.]

## MATLAB and Simulink Planning Notes
- MATLAB activities:
- Simulink activities:
- Required products:

## Course Designer Structure
- Course:
- Modules:
- Learning activity types:

## Simulink Exercise Model Plan
- Activities needing starter and solution models:
- Required products:
- Validation approach:
- Starter prompt for `simulink-create-course-activity`:

## MATLAB Exercise Plan
- Recommended use of `matlab-create-course-activity`:
- Underlying `matlab-generate-grader-assessments` assessment type:
- MATLAB MCP validation checks:
- Starter prompt for `matlab-create-course-activity`:
- Description split into `background.m` context/objective notes and `task.m`
  concrete learner instructions:
- Course Designer fields to add after validation:
- Review notes:

## Common Cartridge and Course Persistence
- Export target:
- Structure checks:
- Limitations:

## First Pilot
1. Generate:
2. Review:
3. Validate persisted structure:
4. Revise:

## Instructor Checklist
- [ ] Confirm course title, audience, duration, and persistence target.
- [ ] Confirm MATLAB, Simulink, and toolbox access.
- [ ] Run `matlab-generate-course` with the starter prompt.
- [ ] Review MATLAB and Simulink activity briefs.
- [ ] Generate MATLAB Exercise component parts through `matlab-create-course-activity`.
- [ ] Review MATLAB MCP validation for `solution.m`, `template.m`, and `tests.m`.
- [ ] Confirm `description.txt` has been split into copy/paste-ready
      `background.m` and `task.m` files.
- [ ] Confirm assessment work is represented as native MATLAB Exercises or
      Simulink Exercises.
- [ ] Generate Simulink Exercise starter and solution `.slx` files through
      `simulink-create-course-activity`.
- [ ] Review Simulink validation reports and Course Designer activity metadata.
- [ ] Confirm the course -> modules -> learning activities structure.
- [ ] Export IMS Common Cartridge as the persisted course representation.
- [ ] Revise before publishing to students.
```

## Prompt Patterns

Use these patterns in the starter prompt section.

- Full course:
  `"Create a [duration] MATLAB and Simulink enabled course titled [title] for [audience]. Interview me for missing constraints, generate the course with IDStack, structure it as Course Designer course -> modules -> learning activities, create MATLAB Exercises with matlab-create-course-activity so grader output is validated with MATLAB MCP calls and description.txt is split into background.m and task.m, create Simulink Exercises with starter and solution .slx files through simulink-create-course-activity, and export an IMS Common Cartridge package for persistence outside MATLAB Course Designer."`
- MATLAB-heavy course:
  `"Create a MATLAB-focused course titled [title] for [audience]. Include Simulink only where it supports the objectives, generate MATLAB Exercises with matlab-create-course-activity, validate solution.m, template.m, and tests.m with MATLAB MCP calls, split description.txt into background.m and task.m, and export a Common Cartridge package."`
- Simulink-heavy course:
  `"Create a Simulink-focused course titled [title] for [audience]. Include MATLAB parameter and analysis scripts, create model-based Simulink Exercise activities with starter and solution .slx files using simulink-create-course-activity, include validation reports, and export a Common Cartridge package."`
- MATLAB Exercise via `matlab-create-course-activity`:
  `"Create a Course Designer MATLAB Exercise for [objective]. Use matlab-create-course-activity to call grader for a [script/function/class/object usage] assessment item, validate solution.m, template.m, and tests.m with MATLAB MCP calls, split description.txt into background.m and task.m for Course Designer copy/paste fields, then add module placement, activity order, estimated time, product requirements, and persistence notes."`
- Simulink Exercise via `simulink-create-course-activity`:
  `"Create a Course Designer Simulink Exercise for [objective]. Build a solution model and a starter model using MATLAB MCP Server tool calls through the Simulink Agentic Toolkit workflow, validate both models, and write the activity folder under simulink-activities/module-[NN]-activity-[MM]-[slug]."`

## Review Gates

- Prerequisites: IDStack, the MATLAB MCP Server, MATLAB Agentic Toolkit,
  Simulink Agentic Toolkit, `matlab-create-course-activity`,
  `simulink-create-course-activity`, and `matlab-generate-grader-assessments`
  skill are available.
- Course source: `.idstack/project.json`, `.idstack/course-content/`, and
  `course-designer-structure.md` exist.
- Structure: course metadata, ordered modules, and ordered learning activities
  are explicit.
- MATLAB Exercise learning activities: `matlab-create-course-activity` created
  `matlab-generate-grader-assessments` component mappings, `background.m`, `task.m`, MATLAB MCP validation
  report, objectives, starter artifacts, validation criteria, and product
  requirements.
- Simulink Exercise learning activities: model task, expected behavior, and
  submission evidence are explicit; starter `.slx`, solution `.slx`,
  validation report, and `course-designer-activity.json` exist.
- Grader-sourced components: generated by `matlab-generate-grader-assessments`, validated by
  `matlab-create-course-activity`, and reviewed before being enriched as MATLAB
  Exercises.
- Common Cartridge: `.imscc` persists the course structure outside MATLAB Course
  Designer.
