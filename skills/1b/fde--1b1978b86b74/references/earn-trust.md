# earn-trust - Earn access

**Enter when:** new engagement where you don't have full access yet, trust is thin, the customer said "let's start small," or you need to navigate "we don't trust AI-generated code."

**Read first:** apply [task context](task-context.md), then retrieve permitted trust constraints, stakeholder evidence and current context. Never read raw private blocks.

Build confidence through useful work, clear evidence and respect for the customer's process. Relationship confidence and access permissions are separate: a strong relationship does not grant production authority.

## Method (you do this work)

**1. Establish the access needed now.** Identify the next task, the minimum relevant access, and its actual policy or authorization source. Read-only access, reviewed PRs, branch writes and deployment rights can be granted independently. Reuse permissions already granted for the same scope; do not impose a ladder or ask the customer to re-earn established access. For missing or disputed access, record the blocked task, status, responsible approver or unknown, next action and any supplied expected wait in the existing plan or context. Mark steps that require the FDE or customer to act, such as VPN enrollment or secret provisioning; never collect secret values. Request only what the next task needs and continue independent work.

**2. Make progress visible.** Choose useful actions for the engagement's stage and agreed cadence:

- Deliver a small verified result within scope, or clarify a consequential unknown when implementation is premature. A quick win does not bypass release gates.
- Ask the existing team about conventions and prior attempts; credit their contributions without assuming they were passed over.
- Prepare a concise status update using the agreed channel and audience. Send only within existing communication authority.
- Flag a supported risk and its consequence without exaggerating urgency.
- Show results the intended users can evaluate, distinguishing demonstrated behavior from reported satisfaction.

**3. Navigate "we don't trust AI-generated code":**

This is increasingly common. The right response is respect, not persuasion:

- **Ask the policy, don't assume.** "Does your organisation have a position on AI-assisted code in production?"
- **If prohibited:** do not load or work on their code with the model. Engagement notes and planning may also contain restricted data; use FDEOps on them only when that use is permitted. Continue with generic or explicitly permitted material, and identify what must be handled outside the AI workflow.
- **If permitted with review:** every AI-touched line goes through their normal review process. Flag it: "AI-assisted, human-reviewed" in commit messages if they want traceability.
- **If grey area:** treat as prohibited until someone with authority says otherwise. Clarify only the policy needed for the next action and continue work on already permitted material.
- **Never hide it.** Disclose AI involvement according to the agreed policy; do not represent prohibited use as ordinary local tooling.

**4. Trust recovery - when you've made a mistake:**

Mistakes happen. What matters is speed and honesty:

- **Report promptly under the incident process.** State the known impact and your confirmed contribution. Do not assign yourself or another person a cause before evidence supports it.
- **Show the fix AND the prevention.** "Here's what happened, here's the fix, here's the test that prevents it next time."
- **Agree a recovery checkpoint.** Use a verified corrective result and a realistic next update; do not promise a win within an arbitrary window.
- **Never minimise.** "It was a small bug" is your assessment, not theirs. Let them size it.

**5. The trust account - deposits and withdrawals:**

| Deposits (slow, steady) | Withdrawals (fast, expensive) |
|-------------------------|-------------------------------|
| On-time status updates | Surprises - especially bad ones they hear from someone else |
| Using their conventions | "I know better" energy - even when you do |
| Flagging risks early | Breaking something in production |
| Crediting the internal team | Taking credit for shared work |
| Asking before touching sensitive code | Assuming access you haven't been given |
| Over-communicating during incidents | Going quiet when things are hard |

## Artifact

**`trust-profile.md`** - updated sections:
```markdown
## Access and working agreement
Current: <permitted task, system/environment and limits>
Source: <actual authorization/policy and date>
Next need: <access gap or none; responsible decision-maker if known>

## AI policy
Status: <prohibited / permitted-with-review / grey-area-treating-as-prohibited>
Source: <who confirmed, when>
```

**`decisions.md`** - record consequential confirmed agreements with their sources. A risk raised is an observed action; increased trust is not established unless supported by the customer's response.

## Checkpoint

Check whether the next task has the required access and agreement. Reuse current evidence; if a material gap remains, name the applicable decision and next action.

## Keep expectations current

At the agreed checkpoints, explain what changed, what has been demonstrated and what remains uncertain. If discovery invalidates the expected scope or timeline, surface the evidence when it affects the next decision. A long discovery phase may be appropriate for the work; week numbers alone do not establish impatience or failure.

## Principles

- Earn confidence through observable work; permissions come from applicable authority.
- Use the customer's conventions and credit actual contributions.
- AI policy applies to the data and use, including engagement memory.
- Report mistakes promptly, distinguish known causes from hypotheses, and verify recovery.
- Choose updates and follow-up timing from impact and the agreed cadence.
