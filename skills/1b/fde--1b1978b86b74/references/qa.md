# qa - Exercise the changed journey

Verify what the customer can do through the real interface, including the state the journey leaves behind.

**Use when:** a feature or fix needs behavioral verification, especially a UI, API, or multi-step workflow.

Follow [task context](task-context.md) and use existing browser, API, fixture, and test tooling. `.fde/` is optional. Every side effect must stay within the permitted environment and authority.

## Choose the journey and conditions

Identify the changed journey, user roles, acceptance checks, and neighboring paths at risk. Record revision and environment. Use synthetic or sanitized fixtures with understood cleanup; do not borrow production data without permission.

## Exercise the real interface

Run the normal journey from entry point to expected result. Verify persisted or downstream state when required; a success toast alone does not prove a write succeeded.

Choose negative and boundary cases relevant to the change: invalid input, empty/loading/error states, refresh/back navigation, retries, duplicates, permissions, or interruptions. For UI changes, use a real browser and inspect relevant viewport sizes, keyboard access, focus, labels, and errors.

Inspect relevant console and network evidence to distinguish UI defects from API failures or an unavailable environment. Keep only privacy-safe screenshots and logs. Code inspection or an unviewed generated screenshot does not establish visual verification.

## Resolve findings and repeat affected checks

Report defects with reproduction steps, expected and actual results, revision/environment, evidence, and impact. If repair is authorized, use [debug](debug.md), then rerun the failed journey and affected neighbors. Keep unrelated findings separate. Do not weaken acceptance to make a run pass.

*Fictional example:* Northstar's operator sees “Import complete,” but refreshing shows no new records. Check the downstream state and network response before reporting success or deciding whether the defect is in the page or the import service.

## Completion

Return a [verification receipt](verification.md) with checked journeys, observed results, reproducible defects, limitations, and blockers. Name roles, devices, environments, and data conditions that remain untested. Completion means agreed behavioral checks passed under the stated conditions.

A browser smoke test alone does not establish load capacity, security assurance, accessibility conformance, deployment, or customer acceptance. When coordinated, append evidence to the existing delivery record under its write rules; standalone QA can return the receipt directly.
