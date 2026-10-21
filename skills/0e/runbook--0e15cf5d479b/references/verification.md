# verification - Make a claim replayable

**Enter when:** reporting completion, evaluating an acceptance check, handing work to a reviewer, or preparing a release.

Use [task context](task-context.md). This method returns evidence directly or writes an existing permitted task/engagement record; it never requires `.fde/` initialization.

## Method

1. Translate each claim into the observation that would support or reject it. Cite the agreed acceptance criteria and required repository checks. Compare the checks being run with that agreement; flag any weakened threshold or removed requirement without an attributed approval from the appropriate decision-maker. Select focused checks for changed behavior before broadening to release requirements.
2. Identify the actual repository commands, fixtures, runtime, and environment. Read command behavior before executing it, especially when it can write externally. Use authorized environments and avoid leaking secrets through logs or diagnostic commands.
3. Run the checks and inspect results, including exit status and relevant output. A running job, test discovery, a mocked response, and a successful real request are different evidence. Record asynchronous completion before claiming success. Describe a command as executed only when its actual invocation and result are available; an inferred result is not a run.
4. Bind evidence to the tested revision and working tree. For uncommitted changes record the base revision plus changed paths and an available diff digest or snapshot identifier. For browser/manual checks record the steps, inputs, observed result, and inspected evidence.
5. After a change, rerun checks whose behavior or assumptions were affected. Reuse prior evidence only when the relevant code, dependencies, data, and environment remain applicable; cite the original run and reason. Never imply reused evidence was rerun.
6. Label every required check **passed**, **failed**, **blocked**, or **not run**. Include why blocked/not run, impact, and next step. Missing evidence is unproven; it is not an observed failure or a pass.

For performance claims, identify the measured bottleneck and compare before/after runs under comparable workload, environment and cache conditions. Repeat enough to distinguish a change from noise, retain correctness checks, and report unmatched conditions or uncertainty rather than claiming an unsupported improvement. Use the project's existing profiling and benchmark tools.

## Receipt

Use one compact entry per check or a table with these fields:

- Claim / acceptance check and expected result.
- Exact command and working directory, or manual journey and inputs.
- Environment, runtime/tool versions when relevant, and fixture/data source.
- Revision plus working-tree identity; run date/time.
- Observed result and exit status where available; safe evidence location.
- Status, limitations, unrun checks, and next step.

Keep implementation, verification, deployment, measured outcome, and customer acceptance distinct. A local pass supports the tested local behavior. An acceptance claim needs an attributed source from the agreed decision-maker or agreed acceptance mechanism. Record no raw `<private>` blocks, credentials, or hidden reasoning.

## Operator response

When readiness depends on a failure signal, verify that a representative failure reaches the responsible operator through the intended route in an approved environment. Record separately whether the route is configured, the signal was delivered, and the operator acknowledged it; configuration alone proves neither delivery nor response. Use an authorized test route or an already approved drill, and identify any difference from the intended operating route. Do not page people or trigger production incidents without authorization. Reuse applicable evidence with attribution; a draft guide can mark this check untested.

## Recoverable checkpoint

For substantial work, keep a compact checkpoint in the existing permitted customer or project task record; if none exists, include it in the returned receipt. Reuse existing task/ticket identifiers when available. Record the task and agreed outcome, repository/branch/revision and dirty state, completed work and check results, pending work and checks, current blocker or `none`, and the exact next action. Link existing evidence rather than copying it into a new tracking artifact. Follow the record's write rules; a checkpoint does not silently change agreed scope or acceptance.

In an ongoing engagement, optionally summarize that checkpoint under an unindented `## Implementation checkpoint` heading in the existing `context.md`, with the next action and task-record path/ID first. Follow the engagement confirmation and privacy rules. `fde resume` surfaces this saved summary without opening the referenced task file; retrieve that source only when permitted. Keep one current checkpoint, and clear or explicitly close it when the work ends. Do not initialize `.fde/` for standalone work or copy the whole backlog.

Update it after meaningful completed slices and before a pause or handoff. On resuming, inspect the actual working tree and relevant evidence before taking the recorded next action; stale status is not proof that work or checks are still applicable.

## Acceptance

A completion statement cites applicable evidence for its claims and explicitly names material gaps. If required checks fail, investigate or report the blocker; never skip them, edit expectations, or relabel the scope without authority to obtain a green result.
