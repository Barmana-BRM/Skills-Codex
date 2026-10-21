# MATLAB Validation Rules

Use MATLAB MCP Server tool calls to validate generated MATLAB Exercise files.

## Required Checks

- Product check: MATLAB and required toolboxes are available or missing products
  are reported.
- File check: `description.txt`, `template.m`, `solution.m`, and `tests.m`
  exist, plus `function_call.m` for Function assessment items.
- Static analysis: run `check_matlab_code` on `solution.m`, `template.m`, and
  `tests.m`.
- Solution check: run or call `solution.m` when the generated artifact is
  executable in MATLAB.
- Template check: confirm `template.m` preserves required function names, class
  names, variable names, or scaffold comments.
- Tests check: confirm `tests.m` parses and contains the expected MATLAB
  Exercise checks.
- Discrimination check (summative items): run at least two plausible wrong
  implementations (for example a hardcoded result and an off-by-one variant)
  against `tests.m`; every wrong implementation must fail at least one test.
  A test suite that only passes the reference solution is not validated.
  Record any test rewritten because of this check.

## Execution Guidance

Use the least invasive MCP call that gives useful evidence:

- `check_matlab_code` for `solution.m`, `template.m`, and `tests.m`
  (never `background.m` or `task.m`, which are plain-text fields).
- `evaluate_matlab_code` to add the activity folder to the path, call generated
  functions, instantiate generated classes, or parse files.
- `run_matlab_file` for script-style solution smoke tests and validation
  drivers.

Some `tests.m` files depend on MATLAB assessment functions such as
`assessVariableEqual`. If those functions are unavailable in the current MATLAB
environment, record static validation and mark runtime test execution as
partial instead of pretending the tests passed.

## Validation Report

`validation-report.md` must include:

- Date generated
- MATLAB release/toolbox check status when available
- Files checked
- Static analysis results
- Execution checks attempted
- Test checks attempted
- Deferred checks
- Final status: passed, partial, or failed

Never mark validation as passed when file existence, static analysis, or
required dependency checks failed.
Treat Code Analyzer errors as failures.
Expected warnings are reportable, not blocking: the Grader file-naming warning
on `solution.m` and `template.m`, unset outputs and unused inputs in
`template.m` (they are the blank), and unused-variable warnings on variables
that `assessVariableEqual` consumes by name inside a character vector.
Keep validation scaffolding (drivers, stand-ins, wrong implementations) outside
the activity and grader-source folders; it is working material, not a
deliverable.
