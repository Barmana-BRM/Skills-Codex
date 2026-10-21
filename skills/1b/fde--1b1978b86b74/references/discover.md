# discover - Find the problem behind the request

**Enter when:** the customer brief is unclear, the proposed solution may miss the real problem, or a change has exposed an unmapped part of the work.

Apply [task context and evidence](task-context.md) first. Supplied notes are enough to begin. In an existing engagement, use permitted summaries of `context.md`, `brief.md`, `reality.md` and relevant `terrain.md` sections; extend existing findings instead of restarting.

## Choose the depth the task needs

- **Notes or meeting preparation:** return the current steps, observations, hypotheses and a few questions that would change the next decision. No repository scan, workshop or customer-record setup is required.
- **A specific delivery problem:** follow the affected people, systems and data far enough to explain the break and identify what evidence is missing.
- **A wider engagement:** map dependencies and decision owners across the involved teams. Examine each candidate problem before choosing where to invest; do not make a full enterprise inventory a prerequisite for one useful finding.

State what you are investigating and which decision it informs. Reuse the user's stated goal. Ask only when a missing answer changes the next action; otherwise proceed with a clearly labelled provisional interpretation.

## Frame the decision

Write a short frame from the evidence available:

| Part | What to establish |
|---|---|
| Situation | How people complete this task today |
| Complication | The observed delay, failure, cost or constraint |
| Question | The decision that further evidence should help someone make |
| Possible outcomes | Confirm the brief, change its scope, investigate further or pause |

Keep the question specific and neutral. “What causes requests to wait before assignment?” leaves room for different explanations. “How should we automate assignment?” assumes the solution before establishing the cause.

Name the decision owner when known. An unknown owner or unmeasured baseline is a finding, not a reason to keep questioning indefinitely. Return a provisional frame and identify who or what could verify it. Do not present a new interpretation as agreed scope.

## Trace the work

Follow an ordinary case from arrival to completion, then relevant exceptions. Use the customer's terms for the request, system and people involved.

For each step, establish:

- Who performs it and where the input comes from.
- What they do, check or decide, and which system they update.
- Time spent working versus time spent waiting.
- What happens when information is missing or the normal path fails.
- Who notices the failure, how they recover, and which record they trust.

Distinguish measured timings from estimates. A team lead's recollection is useful evidence about their experience; it is not a measured baseline. Do not infer that the slowest visible step causes the whole delay without following its dependencies.

Use concrete questions when the supplied material leaves a gap: “Show me the last request that waited a day. What had to happen before someone could take it?” Ask about spreadsheets, manual transfers or other workarounds when there is evidence of them, without assuming they exist.

When a workaround looks surprising, use the targeted history check in [audit](audit.md#before-changing-an-unfamiliar-workaround). History supplies clues, not proof that an old requirement still applies.

## Inspect systems when relevant and permitted

If the question depends on application behavior and code access is authorized, use `fde scan` and targeted file reads. If the CLI is unavailable, use the repository's existing search, Git and test tools. Do not load the whole repository or unrelated customer data.

Follow the actual path: entry point → validation → processing → storage or downstream action. Inspect the code, configuration and tests that can explain the observed discrepancy.

Check existing capability before proposing new work. A disabled feature, frequent edits or a missing nearby test is a lead to investigate, not proof of a root cause. Record the evidence behind any technical risk. When there is no repository access, state that implementation behavior remains unchecked and finish the work possible from the notes.

## Check the data and dependencies the proposed work needs

For each relevant source, establish where it lives, how fresh it is, who controls access, which fields the task needs, and what happens when it is unavailable. Inspect a permitted sample appropriate to the question; report its size and limitations rather than treating a small sample as representative by default.

| Source or connection | Needed for | Freshness and quality evidence | Access owner | Failure or constraint | Next check |
|---|---|---|---|---|---|
| Fill only relevant sources | | | Unknown if unconfirmed | | |

Check mappings between systems, supported APIs, permissions and retry behavior where they affect feasibility. A promised export or integration is not yet an available dependency. Record its responsible owner, verification date and required evidence when known; propose missing commitments for confirmation.

For AI work, identify which steps can use deterministic logic, which need model judgment, and which require a human decision. Keep that allocation provisional until the affected owners agree. Establish who would operate the resulting change and what access or training they would need.

## Use a workshop only when it resolves a real disagreement

A short meeting with the relevant decision makers may help when teams describe different problems or constraints. Bring the observed cases and the decision to be made. Ask participants to state their constraints before discussing options.

Summarize areas of agreement and disagreement. A vote or an absence of objections does not establish authority or acceptance. Ask the responsible owner to confirm the decision and record any unresolved objection, next action and date. Draft the summary promptly, then follow the record-confirmation rules before saving it.

## Return a useful discovery result

Use the smallest output that answers the user's request:

1. The current task and the decision under investigation.
2. What the evidence establishes, with its source.
3. The working explanation and plausible alternatives.
4. Relevant exceptions, dependencies or technical risks actually observed.
5. Missing evidence and the next check that would change the decision.

Do not fill a quota of risks, exceptions or questions. If no system was inspected, do not invent code findings. If several interpretations have failed, reassess the evidence and investigation method rather than blaming the person who wrote the brief.

For a bound engagement, propose updates to the existing records after the discovery result is reviewed:

- `reality.md`: preserve `Working theory`, `Evidence` and `Differs from brief how`; add the decision frame and validation status.
- `terrain.md`: relevant steps, system behavior, data dependencies and unknowns. Preserve the `## Operating map (exception-led)` section and its columns when recording observed breaks.
- `assumptions.md`: new or changed assumptions, verification owners and checkpoints.

An operating-map row uses: `Exception / break | Who notices first | What they do today | System of record then | Blast | Evidence`. Preserve the existing schema. If no break has been observed, report that gap; do not fabricate a row to satisfy a readiness check.

For standalone work, return the same findings in the conversation or requested document. No `.fde/` write or initialization is needed.

## Worked example

This example is fictional and uses only supplied meeting notes.

The brief asks for an assistant to draft responses. The supplied notes say drafting takes about four minutes, while requests sometimes wait a day for assignment. The timings come from a team lead; no measured baseline is available.

**Working theory:** assignment delay may matter more than drafting time. **Evidence:** the lead's estimates in the supplied notes, still unverified. **Differs from brief how:** the requested assistant addresses drafting, while the reported delay concerns assignment. **Question:** what causes the assignment delay, and which change would reduce it? **Next check:** trace a sample of recent requests using arrival and assignment timestamps, then ask the people handling delayed cases what prevented assignment.

The discovery result does not reject the assistant or declare an ownership problem solved. It gives the FDE a focused way to find out what to build, change or investigate next. Return this as a short draft for notes-only work; in a bound engagement, propose it for `reality.md` with validation still pending.

## Principles

- Investigate the work before choosing a solution.
- Keep observations, estimates and hypotheses distinct.
- Match discovery effort to the decision at hand.
- Unknown ownership and missing evidence remain explicit.
- Confirmation comes from the responsible person, never from silence.
