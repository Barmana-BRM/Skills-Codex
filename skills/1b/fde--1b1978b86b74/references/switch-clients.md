# switch-clients - Switch engagements

Switch customers without losing the next action or carrying one customer's information into another's work.

**Use when:** moving between existing engagements, reviewing competing customer needs, or recovering from confused customer context.

Apply [task context](task-context.md). This task needs existing records; do not invent or initialise a customer merely to complete a portfolio view. Check `fde privacy` before record access, then use `fde status --all` for the permitted portfolio summary. Do not read raw `.fde/` files.

## Decide what needs attention

Use the available evidence to compare customer impact, safety or security incidents, contractual deadlines, blocked work and agreed commitments. A trust signal is a prompt to examine its source, not a fixed countdown or an automatic priority over an incident. A delayed reply does not establish lost trust.

Keep portfolio summaries brief and authorised. Inspect deeper context only for the customer being worked on, through a sanitized `fde resume` packet and targeted `fde recall`. If there is not enough capacity for the competing commitments, name the conflict and the decision-maker who can change priorities. Do not silently deprioritise another customer.

## Leave the current engagement recoverable

Identify what changed, what remains uncertain and the next action. For unfinished implementation, use the existing [recoverable checkpoint](verification.md#recoverable-checkpoint), with its task ID, working-tree state and applicable evidence.

Follow the record's confirmation and CLI write rules. An unconfirmed checkpoint stays a draft; switching customers does not approve it. Keep every update in the current customer's record. Do not automatically commit, stash, discard or move working-tree changes. Preserve them under the repository's policy and the user's existing authority.

## Select the next customer explicitly

1. Identify the requested customer and the intended workspace. If either is ambiguous, resolve that before record access or changes.
2. Inspect the binding with `fde resume --bind`. Merely opening another editor tab or running bare `fde resume` does not select a different customer.
3. Confirm the target exists using permitted metadata. Prefer its already-bound workspace. For read-only work, a command-scoped `FDEOPS_ENGAGEMENT=<known-record-path>` selects that existing record without changing the workspace binding; use the same scope for each record command and report that the persistent binding is unchanged. `fde resume --init <existing-client>` can fill missing templates and initialise memory Git as well as bind the workspace. Use it only when those record changes are also authorised; a request to switch alone is not enough. Never guess a missing customer or silently change unrelated host settings.
4. Get a fresh sanitized `fde resume` packet and verify its visible `ENGAGEMENT:` identity matches the intended customer. Stop on a mismatch; do not continue from the previous customer's packet.
5. Resume the selected task from current evidence. Check actual repository state before relying on a saved implementation checkpoint. Keep the other customer's files and output out of subsequent tool reads and messages.

Changing the binding does not erase earlier conversation context. Use a fresh agent session when the customer's isolation policy requires it or prior sensitive context should not remain available. Do not claim that closing tabs removes information already supplied to a model.

## Communicate within the agreed boundaries

Use each customer's agreed audience, channel and cadence. Prepare an update when a commitment changes or a material risk needs a decision; send it only within existing communication authority. Explain the effect on that customer's work without disclosing another customer's identity, incident or confidential priorities.

Reusing a field lesson across customers requires permission as well as removal of identifying and confidential information. Masking alone does not authorise reuse.

## Worked example

The FDE is leaving Garvey with an unfinished retry fix and switching to Kesterman. Garvey's `context.md` has a confirmed checkpoint pointing to the existing task and its unrun staging check. The FDE preserves the dirty working tree rather than committing or stashing it automatically. `fde resume --bind` still identifies Garvey, so bare resume would reopen the wrong record. After verifying that Kesterman already exists, the FDE selects its bound workspace or uses a command-scoped selection when record writes are prohibited, then obtains a fresh sanitized packet and checks `ENGAGEMENT:` before continuing. A temporary selection is reported as temporary, not as a changed workspace binding. Kesterman's sponsor has not replied, but the notes show planned leave; that alone does not justify an amber signal. An unconfirmed Garvey update stays a draft for Garvey and is never written into Kesterman's record.

## Completion

Return the selected customer, whether selection is temporary or persistent, binding evidence, next action, and any unsaved update or unresolved priority. A switch is complete only when the fresh packet identifies the intended customer and the previous work remains recoverable. Standalone portfolio review can return its summary without rebinding or saving anything.

For an authorised portfolio view, `fde dashboard --all` regenerates `fieldbook.html`; it does not change customer records. Neither the dashboard nor the agent's summary grants approval for a release or customer communication.

## Principles

- One customer's writes belong in that customer's record.
- Use sanitized CLI packets; never substitute raw record reads.
- Verify identity after a switch and preserve unfinished work without inventing authority.
- Prioritise from impact and commitments, not unsupported trust timelines.
- A fresh binding is not a fresh model context.
