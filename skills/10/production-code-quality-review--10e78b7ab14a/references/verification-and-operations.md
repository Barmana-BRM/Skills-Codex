# Verification And Operations Review Guide

Load this reference when the change includes tests, failure handling, background work, or production-operability concerns.

## Test Quality

Check:

- tests fail for the bug or regression you are worried about
- tests cover changed behavior, not just happy-path snapshots
- failure paths are explicit
- integration boundaries are exercised where unit mocks would hide risk
- time, retries, and concurrency are made deterministic

## High-Value Missing Scenarios

- invalid input at the boundary
- upstream failure or timeout
- duplicate request or replay
- migration rollback or backward compatibility
- authorization denied path
- empty result, partial result, or stale data path

## Observability

Check:

- logs that identify the failing request, job, or record
- correlation IDs where the stack already uses them
- redaction of secrets, tokens, and PII
- metrics for success, failure, retries, latency, queue depth, or saturation
- traces or spans for high-value cross-service flows when applicable
- alertable failure signals instead of silent drops

## Review Prompts

Ask:

- what exact test would fail if this implementation is wrong?
- if this fails in production, how will the on-call engineer notice?
- how will they identify affected users or jobs?
- can they tell whether the failure is local, upstream, or data dependent?

## Weak Signals

- snapshots that cover too much surface area
- tests that only assert mocks were called
- broad fixtures that hide the edge case
- warnings for hard failures
- noisy logs that still fail to explain impact
