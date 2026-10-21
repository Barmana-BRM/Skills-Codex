# Python Review Heuristics

Load this reference when the change touches Python services, scripts, jobs, test harnesses, or shared Python runtime contracts.

## Correctness

Check:

- implicit `None` paths and missing return branches
- mutable default arguments
- timezone-aware versus naive datetime usage
- broad exception handling that hides behavior-critical failures
- mismatch between type hints and runtime values
- partial parsing that trusts inbound dicts too early

## Reliability

Check:

- cleanup for files, temporary paths, subprocesses, and network clients
- retry loops without timeout, jitter, or idempotency boundaries
- background work started without ownership, join, or failure visibility
- module-level state that leaks across requests, jobs, or tests

## Testing

Check:

- whether the exact failure path is asserted, not just the happy path
- whether mocks are hiding integration risk at IO boundaries
- whether time, randomness, and environment access are made deterministic
- whether `pytest` or `unittest` coverage would fail for the bug you suspect

## Review Prompts

Ask:

- where can `None`, empty data, or missing keys still reach business logic?
- if this datetime crosses timezones or daylight-saving boundaries, what breaks first?
- if an exception is raised here, does the caller see the failure or does the code silently continue?
