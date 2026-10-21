# who-decides - Map decision rights

**Enter when:** a consequential decision has unclear authority, ownership is disputed, stakeholders change, or observed communication changes affect the next action.

**Read first:** apply [task context](task-context.md), then permitted `stakeholders.md` and `context.md` evidence. Retrieve relevant trust constraints only when access or disclosure is involved.

Titles, influence and responsiveness can help you find the right conversation. They do not establish approval authority or explain someone's motives.

## Method (you do this work)

**1. Resolve the decisions in front of you.** Reuse the customer's existing agreement, delegation or decision process. For each relevant decision, identify who or what can decide, the scope of that right, its source, and whether it is confirmed, proposed, disputed or unknown. Distinguish budget/scope approval, data/AI-policy approval, release authority, customer acceptance, and operating/recovery responsibility when they differ. Do not require separate people or a full matrix for a routine decision already covered by confirmed authority.

A sponsor naming an operating team is a proposal until that team accepts responsibility. If accounts conflict, record both attributed positions and the unresolved decision; ask the applicable authority to resolve it. Do not choose an owner from seniority, authorship, repository access or silence. Continue authorized work that does not depend on the disputed right.

**2. Understand participation.** Identify the sponsor, people helping the work, access/process owners, people raising concerns, and required participants not yet consulted. One person may fill several roles; none must exist merely to complete a taxonomy. Capture their stated concerns and useful knowledge. Opposition may identify a real defect or unaccepted obligation. Being absent does not prove hidden authority or disengagement.

**3. Track observable changes.** Compare communication and decisions with the agreed cadence and the person's usual pattern. A delayed reply, shortened meeting or new participant may merit a check; holidays, workload, delegation and scheduling are alternative explanations to escalation. Record the observation separately from any hypothesis. Use green/amber/red only when supported by attributed evidence and its effect on the work; do not derive motives or authority from a color.

Choose follow-up timing from the decision deadline and potential impact. An imminent release with a missing owner warrants prompt resolution; an ordinary delayed reply does not have an automatic 48-hour escalation clock. Offer a neutral question such as “Has anything changed in the decision or timing we should account for?” Messages and outreach still require authorization.

**4. Learn from the existing team.** Ask what they tried, what constraints remain and what they expect to own. Use established terminology and credit actual contributions. Do not assume the team was passed over, resents outside help, or knows every cause. Verify consequential technical claims through the relevant evidence.

**5. Prepare the decision conversation.** For a decision involving several parties, identify unresolved questions, relevant decision rights and needed evidence. Address dependencies in a useful order through existing channels. Record stated objections faithfully; label any possible motivation as an unverified hypothesis only when it matters to the next action. A short pre-mortem can ask “What missing evidence or unresolved responsibility could prevent this decision?” It must not invent an opponent or predict agreement.

**6. Keep identities consistent.** Use one confirmed spelling per person across the table and contact records. `fde doctor` can flag possible identity clusters; verify that they are the same person before consolidating. Do not erase historical evidence to tidy the display.

## Artifact

Return the relevant decision rights directly, or update the existing `stakeholders.md` under the confirmed record rules. Link an existing authoritative record instead of duplicating its full contents.

```markdown
| Decision / responsibility | Person or mechanism | Scope | Source | Status / next action |
|---------------------------|---------------------|-------|--------|----------------------|
| <relevant decision> | <confirmed person/mechanism or unknown> | <system, environment, limit> | <actual agreement/policy/reference> | <confirmed / proposed / disputed / unknown; next step> |
```

Keep a compact participation/signal table where it helps:

```markdown
| Who | Role | Signal | Last evidence | Notes |
|-----|------|--------|---------------|-------|
| <name> | <observed role> | <supported signal or unknown> | <source and date> | <stated concern / unresolved question> |
```

Preserve the existing `## Signal history` section and its dated `[signal:...]` entries. CLI status, receipts and dashboard read that history; changing the display table alone does not update those signals. Use the existing confirmed contact/debrief workflow for signal changes. Never delete or overwrite history while refreshing the tables.

## Checkpoint

State the decision that can proceed under confirmed authority and any dependent action still blocked by an unknown or disputed right. Include material observed changes and the next evidence or conversation needed. If nothing relevant changed, reuse the map; no calendar interval alone requires a new review.

## Worked example

A sponsor requests release on Thursday and names Platform as operator. The Platform lead says the team has not accepted on-call responsibility. The sponsor's slower replies and a new finance participant are observed, but their cause is unknown.

Return the map as a draft; when bound and confirmed, save it in `stakeholders.md` and the next action in `context.md`. Record the sponsor's request and Platform's objection with their sources. Existing policy confirms who approves production releases; it does not establish that Platform accepted recovery duties. The release authority row cites that policy; the operating responsibility row remains disputed. Acceptance and data-policy rights are checked only to the extent required by this change, reusing existing evidence. Prepare verification and the release receipt while the responsible parties resolve coverage. Do not infer escalation, assign Platform by title, or turn the sponsor's deadline into deployment permission.

## Principles

- Resolve scoped authority from evidence; influence is not delegation.
- Separate observed behavior, stated concerns and possible explanations.
- Ownership requires applicable agreement, not an unchallenged name in a table.
- Reuse confirmed decisions and scale follow-up to impact.
- Preserve attributed history and unknowns; never fabricate agreement.
