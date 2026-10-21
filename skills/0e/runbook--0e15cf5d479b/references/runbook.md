# runbook - Write an operating guide

**Enter when:** the team needs instructions to operate, diagnose or recover a system, or an engineer is preparing to transfer responsibility.

Apply [task context](task-context.md). Use supplied operational facts, relevant code and verified procedures. For a bound engagement, retrieve relevant sanitized delivery, dependency and ownership evidence; do not load the full customer record or raw private material.

## Match the request

- **Draft a guide:** write what is known, mark unverified procedures and missing evidence, and return the requested document. No customer record, live access, drill or closure ceremony is required.
- **Verify an operating guide:** agree the permitted environment and checks, exercise relevant procedures, and record what happened. Do not run a destructive or production drill from a documentation request alone.
- **Complete a handoff:** use [handoff](close.md) for the wider ownership and acceptance decision. A written guide is one part of that decision, not proof of readiness.

## Build the guide from evidence

Identify the system, the intended reader and the decisions that reader can make. Follow the actual operating path and include only relevant sections:

```markdown
# Operating guide - <system>
Status: Draft / Verified for <environment and scope>
Evidence: <code, observed run, operator statement or existing document>
Operating owner: <confirmed role/person and source, or proposed/unconfirmed>

## Normal operation
What should happen, how often, and how to check it.

## Known failure modes
Symptom: <what the operator sees>
Evidence: <what establishes this behavior>
Cause: <verified cause or explicit unknown>
Action: <supported steps, constraints and stop conditions>
Validation: <tested environment/date/result, or unverified>
Escalation: <confirmed role/channel, or missing>

## Deploy and recover
Procedure: <verified commands or a source link; do not invent commands>
Permissions and prerequisites: <required access and safety conditions>
Check: <expected observable result>
Recovery: <tested procedure or the missing recovery evidence>

## Monitor and escalate
Signal: <existing alert or check>
Meaning: <known interpretation>
Response: <authorized action and when to escalate>

## Open readiness gaps
Missing evidence, owner to confirm, and proposed next check.
```

Do not pad the document with an arbitrary number of failures, contacts or commands. A stated retry problem without a known cause should remain an investigation item, not become a fabricated repair procedure. A suggested owner is not an accepted operating responsibility.

For AI components, include relevant model and configuration versions, evaluation checks, failure limits and the supported way to pause actions. Do not assume retraining or autonomous operation is required.

## Verify when requested

Select checks based on the system's actual consequences. For example, the receiving operator may demonstrate normal operation, diagnose a known failure, or recover a failed release in a permitted test environment.

When readiness depends on a failure signal, follow the [operator-response evidence check](verification.md#operator-response). A draft can mark it untested; configuration alone does not prove delivery or response.

Record each critical capability separately as verified, failed or untested, with evidence. A successful walkthrough cannot compensate for an untested recovery path. Avoid an averaged confidence score that hides a critical gap.

If a procedure fails, correct the guide or system within scope and repeat the affected check. If verification is unavailable, deliver the draft with its limits and propose the next check; do not claim the handoff complete or indefinitely extend the engagement yourself.

## Deliver and retain ownership boundaries

Return the guide, its verification status and any remaining operating decisions. Save it to the requested location. In a bound engagement, propose updates to `handoff.md` and relevant current-state records under their confirmation rules.

Access changes, exports of customer records, sponsor messages and closure decisions require their own authorization. A request for a runbook does not authorize these actions. Transfer only the material the recipient is entitled to receive.

## Principles

- Write for the person handling the actual failure.
- Supported procedures beat plausible commands.
- Draft, tested procedure and accepted ownership remain distinct.
- Verify critical capabilities individually.
- Keep private relationship notes and credentials out of an operating guide.
