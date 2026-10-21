# The Same Page Meeting (Fable ↔ Codex, IDS protocol)

The adversarial planning loop. Fable submits the plan, Codex attacks it as the Integrator, the two iterate until the verdict line says so or the round cap hits. Cross-model review kills the echo chamber: Codex advises, Fable decides, the user breaks deadlocks.

## Inputs

- The canonical plan file: `PLAN.md` for pipeline runs, or the file the user pointed at (copied into the repo as `RF-PLAN.md` if it lives outside). One file for the whole meeting; every revision lands in it. Call it `PLAN_FILE` below.
- The Core Focus: one sentence from `VTO.md`, or from the user's request if there is no VTO
- `MAX_ROUNDS` = 5 by default; whatever the user set is a hard cap, not a suggestion

## Round 1: fresh Codex session (read-only)

Write the review prompt to a temp file first (never inline-quote a long prompt), then launch per the invocation contract in [CODEX-INTEGRATOR.md](CODEX-INTEGRATOR.md), capturing the thread id.

The review prompt template:

```
You are the INTEGRATOR reviewing your Visionary co-founder's plan. Your job is the
filter: protect the company from ideas that do not serve the Core Focus, and find
what breaks. Be skeptical and specific; you are not here to be agreeable.

CORE FOCUS: <one sentence>

Read the plan at <PLAN_FILE substituted here> and any repo files you need (you are read-only).

For every issue you find, output one line in this exact shape:
- [KILL|DEFER|FIX|CLARIFY] <root cause in one sentence> -> <one-line fix or question>

  KILL    = does not serve the Core Focus, cut it entirely
  DEFER   = real but not this cycle, move to the Issues List
  FIX     = stays, but broken as written (security, race, edge case, wrong
            assumption, missing migration, observability gap)
  CLARIFY = cannot judge without an answer

Also flag: anything with a materially simpler alternative, and any rock whose
"proof" would pass while the feature is actually broken.

Do NOT modify any files. End your reply with EXACTLY one line:
VERDICT: SAME PAGE
or
VERDICT: NOT YET
```

## Rounds 2..N: resume the SAME session

Codex remembers its own critiques; the follow-up only asks it to verify they were addressed and flag anything new:

```
I revised the plan. Re-read <PLAN_FILE>. Check whether each of your prior findings
is addressed, flag any new issues in the same [KILL|DEFER|FIX|CLARIFY] shape, and
end with exactly one line: VERDICT: SAME PAGE or VERDICT: NOT YET.
```

## Between rounds: IDS every finding

For each finding, run Identify / Discuss / Solve:

1. **Identify.** Restate the real issue in one sentence. The stated problem is rarely the root; if Codex flagged a symptom, name the root yourself.
2. **Discuss once.** Decide your position. You are the Visionary and the final arbiter of the plan: accept findings that are right, reject findings that miss the Core Focus or the user's stated constraints. Say it once; re-arguing a settled point in a later round is politicking.
3. **Solve.** Apply accepted findings to `PLAN_FILE` immediately. DEFER items go to `ISSUES.md` (or `RF-ISSUES.md` under the collision rule). Rejected findings stay rejected with a reason in the log.

## The log (`SAME-PAGE-LOG.md`)

Append per round, verbatim findings first, your response second:

```markdown
## Round N
### Integrator findings (Codex, verbatim)
<paste the -o file content>
### Visionary response (Fable)
- ACCEPTED: <finding> -> <what changed in PLAN.md>
- REJECTED: <finding> -> <why, in one sentence>
- DEFERRED: <finding> -> ISSUES.md
```

## Exit conditions

- `VERDICT: SAME PAGE` greppable in the last Codex reply: meeting over, proceed.
- Round cap hit with `VERDICT: NOT YET`: STOP. Present the unresolved findings to the user in plain language with your recommendation. The user is the Owner's Box; they decide. Record the decision in the log as `USER OVERRIDE: <decision>`. A flagged deadlock beats a fake approval.
- Codex call fails twice in a row: follow the invocation contract's failure ladder (retry, then a LOUDLY-announced degraded fresh session carrying the meeting summary, then stop and surface). Log `DEGRADED: fresh session from round N` in the meeting log if the fallback fires. Never silently continue without the review.

## Hygiene

- One finding, one line, one disposition. No finding disappears without a logged reason.
- Never let Codex edit files during this meeting. The invocation contract snapshots status + diff before every call; if a read-only round changes files anyway, revert only previously-clean paths, STOP on mutated previously-dirty paths (surface, never auto-revert user work), then restart the round with the sandbox forced per the contract.
