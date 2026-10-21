# Review Framework

Use this reference for substantial reviews, cross-cutting changes, risky diffs, or architecture-sensitive work.

## Phase 0: Review Setup

Before reading code in detail:

1. Collect structured review context from the helper scripts.
2. Identify the review scope:
   - base branch or fallback scope
   - staged, unstaged, and untracked files
   - changed file list
   - changed line ranges
3. Read only the references relevant to the detected stack and risk flags.
4. Decide whether the review should stay single-agent or use specialist prompts.

Do not start reporting findings before this setup is complete unless the user has given only a pasted snippet with no repo access.

## Phase 1: Scope And Intent

Identify:

- what changed
- intended behavior
- affected modules and ownership boundaries
- external systems, APIs, databases, queues, caches, files, or users affected
- whether the change is local, cross-cutting, or architectural
- risk level: low, medium, high, or critical

Keep this mostly internal unless it materially affects the final recommendation.

## Phase 2: Correctness

Review:

- control flow and branch behavior
- data flow and state transitions
- input and output behavior
- null, undefined, empty, zero, and missing-value handling
- type assumptions and runtime validation
- API contracts and backward compatibility
- database query correctness
- serialization and deserialization
- time, date, timezone, and ordering logic
- race conditions in shared state or async code

Ask:

- can valid input produce wrong output?
- can invalid input break the code?
- are errors swallowed?
- are assumptions enforced?
- does this break existing callers?
- does similar functionality already exist and should it be reused?

## Phase 3: Robustness

Review behavior under failure, load, bad input, and real production conditions:

- error handling and propagation
- retry, timeout, and cancellation behavior
- idempotency and duplicate requests
- partial failure and transaction boundaries
- resource cleanup for files, sockets, handles, and memory
- concurrency safety and backpressure
- rate limiting and fallback behavior
- logging, metrics, traces, and alertability
- sensitive information in logs

Ask:

- what happens when dependencies are slow or unavailable?
- what happens on duplicate requests?
- can this create inconsistent state?
- can this fail silently?
- can operators debug the failure from logs or metrics?

## Phase 4: Architecture

Review:

- module boundaries
- dependency direction
- coupling and cohesion
- abstraction level
- separation of concerns
- ownership of business logic
- framework leakage
- domain model consistency
- API boundaries and data ownership
- configuration strategy
- reuse versus duplication
- simplicity versus over-engineering

Report architecture issues only when they create real future cost, not because another design is possible.

## Phase 5: Evolution

Review:

- extensibility and deleteability
- migration and rollback path
- feature toggle needs
- backward compatibility
- test and observability safety nets
- documentation of non-obvious decisions
- upgrade, downgrade, and vendor risks
- schema evolution and API versioning

Ask:

- what happens when this feature grows by 2x?
- what happens when another team integrates with it?
- what will be hard to change six months from now?
- is this shortcut becoming structural debt?

## Phase 6: Tests

Review tests as production code:

- are tests added or updated for changed behavior?
- would tests fail if the implementation is broken?
- are edge cases and failure paths covered?
- are integration points covered?
- are concurrency or time-sensitive paths tested when relevant?
- are mocks hiding real integration risk?
- are snapshots too broad or too weak?
- are tests deterministic and readable?

Do not simply say "add tests." Name the exact missing test scenario.

For test quality and production observability details, load `references/verification-and-operations.md`.

## Phase 7: Verification Pass

Before final output, classify every candidate finding:

- Confirmed: directly supported by code or deterministic evidence
- Likely: strongly implied but not fully proven
- Needs confirmation: possible issue requiring runtime or project context
- Removed: speculative, duplicate, or too minor

Only include confirmed and important likely findings in the main list. Move uncertain material to questions. Remove style-only opinions unless they affect maintainability or safety.

## Changed-Line Guidance

Use changed-line ranges to determine whether a finding is:

- directly introduced by the current change
- pre-existing but worsened by the current change
- pre-existing and unrelated

Prefer reporting introduced or worsened issues. Mention pre-existing issues only when they materially block the reviewed change.

## Smaller-Stack Guidance

When Python-specific issues appear, check:

- implicit `None` paths
- mutable defaults
- timezone-aware versus naive datetime handling
- broad exception handling in behavior-critical paths

When Docker or deployment packaging changes appear, check:

- pinned base image strategy
- root versus non-root execution
- healthcheck and shutdown behavior
- runtime config or secret expectations

## Final Recommendation Labels

Use one of:

- Safe to merge
- Safe to merge with follow-ups
- Fix P1 or P0 issues before merge
- Do not merge yet

State the minimal required fixes.
