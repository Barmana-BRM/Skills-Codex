# rescue - Resolve the incident

**Enter when:** production is down, something's bleeding - OR a stakeholder went quiet, confidence is slipping, or three weeks into the build the brief turned out to be wrong. Choose urgency from actual impact and the pending decision; a delayed reply alone is not an outage.

**Read first:** apply [task context](task-context.md), then permitted `context.md` and `risks.md` evidence. Pull specific module context only once you know what you're looking at.

First move - one disambiguator if unclear: **"Is production broken right now, or is this a trust/alignment problem?"**

## A. Technical fire (you do this work)

Open by narrowing time, like a human: "Walk me through the last couple hours - deploys, config, anything that moved." Check recent changes, but keep external dependencies, traffic, expired credentials and latent faults in view; no known deploy does not prove nothing relevant changed:
```bash
git log --since="6 hours ago" --format="%ad %an %s" --date=relative
```

**The sequence:** separate authorized containment from a root-cause fix. Do not wait for a complete diagnosis to reduce ongoing harm safely, and do not claim the cause is established merely because containment worked.

1. **Stabilise first.** Use the applicable incident authority and established containment/recovery procedures. Consider rollback, disabling a path or routing around it against actual side effects and recovery limits; do not invent production permission.
2. **Name the unknowns.** "We don't know if the queue is corrupted / if this hits all users / if the cache is stale." Written down. Named unknowns are safer than assumed knowns.
3. **Bound the blast radius.** State observed affected paths and plausible exposure separately. An unfamiliar integration warrants investigation; it does not prove every user is affected.
4. **Minimum safe change.** Often a read-only query first - observe before acting. Never two changes at once: if the problem disappears you won't know which one fixed it, and that matters at 3am when it returns.
5. **One hypothesis at a time.** "If X, then Y should produce Z." Test, document, next.
6. **Instrument before touching.** A change without observability is a change without evidence.

**Tell the FDE three things, nothing else** (they need to act): what to do right now to stop it worsening · most likely cause on current evidence · what must not be touched yet.

## B. Trust fire (you coach - calm, no panic coding)

**Signals:** a stakeholder stops responding or routes around the FDE · meetings shorten, decisions defer · "is the timeline still realistic?" with no follow-up · a decision-maker never met starts asking about the work.

**The read:** compare the observation with the agreed cadence and upcoming decisions. Workload, absence, changed expectations and escalation are possible explanations, not established causes. Clarify the effect on the work without guessing intent; urgency follows the decision deadline and impact.

**The move:** offer a neutral alignment check through the agreed channel: ask whether expectations or the decision timing changed. Continue useful authorized delivery; additional commits alone do not resolve an ownership or acceptance dispute. When a concern is confirmed, propose a dated next step with the responsible person. Record only what was said and agreed, with its source, under the normal confirmation rules. Do not send outreach without authority.

## C. Wrong brief, mid-build

The most politically dangerous moment in FDE work: visible progress toward the wrong thing. Never absorb it silently.

1. **Pause the affected work.** Identify which assumptions the evidence invalidates; continue independent authorized work that remains applicable.
2. **Write the evidence, not the interpretation.** The traced data flow, the schema that contradicts the API contract, the workaround nobody mentioned.
3. **Raise the decision promptly.** Use the agreed channel and urgency appropriate to the impact; a call helps when written context is insufficient. Do not infer concealment from communication timing.
4. **Evidence before recommendations.** A customer who reaches the conclusion themselves owns the reset.
5. **Offer viable paths:** narrow the outcome, revise scope/timing, or pause the affected work to investigate. Include only options supported by the situation; distinguish proposals from authorized changes.
6. **Confirm the reset** - obtain the applicable scope/acceptance decision before dependent building resumes, then update relevant records under the normal confirmation rules.

Customers remember who told them the truth before it cost them money.

## D. Pivot - the whole direction changed

Not hold-scope (that's someone adding). This is: budget cut, new CTO arrives, strategic priority shift, acquisition changes everything, "we've decided to go a different direction." The engagement's foundation moved.

**Signals:** new leadership asks "why are we doing this?", the sponsor's boss questions ROI, a competing initiative gets the resources, the quarterly priorities deck doesn't mention your project, the team you're embedded in gets reorganized.

**The pivot protocol:**
1. **Acknowledge immediately.** Don't pretend the old brief still applies. "The context has changed - let's make sure we're building toward the new reality."
2. **Protect what's already delivered.** Identify what remains live and useful with evidence. A pivot may change the value of a feature; keep deployed behavior, measured benefit and accepted outcomes distinct.
3. **Assess salvageability.** What from the current work applies to the new direction? What's dead? What can be repurposed? Present this honestly - don't stretch to make everything fit.
4. **Consider applicable paths (same pattern as wrong-brief):**
   - **Redirect** - current work pivots to serve the new priority (minimal waste).
   - **Pause** - freeze current scope, start fresh discovery on new direction.
   - **Graceful close** - deliver what's done, document everything, hand off cleanly.
5. **Reset the artifacts.** Update `success.md` (new definition of success), `reality.md` (new context), `brief.md` (new direction). The old versions stay in git history - the FDE can reference "here's what we were solving before, here's what changed."
6. **Agree the next checkpoint.** Show what can be reused, what needs verification and what authority the new direction requires. Do not promise a first-week win or infer trust from agreement with the pivot.

**Commercial awareness:** A pivot may change the SOW. Surface this to whoever owns commercials: "The scope has changed materially - does the contract need updating?" Don't assume; don't ignore.

## Artifact

**`chaos-log.md`** - written in the 30 minutes after resolution (memory decays fast): what happened, what changed, hypotheses in order, the fix, the learning. **`risks.md`** - new risks the crisis revealed. **`decisions.md`** - trust-fire conversations, agreements, and pivot decisions. Update `reality.md`/`terrain.md` if the crisis or pivot disproved them.

## Checkpoint

Stable + log written + one question answered with the FDE: does this change what we thought we knew? If yes, the relevant artifact gets updated now, not "later."

## Principles

- Stabilise before diagnosing.
- Named unknowns beat assumed knowns. Minimum safe change, one hypothesis.
- Use applicable incident authority and recovery evidence; account for effects a code revert cannot undo.
- Clarify relationship concerns from evidence; urgency follows impact, not a fixed escalation clock.
- The chaos log is written before the day ends.
- Confirm changed scope and authority before acting on a proposed pivot.
