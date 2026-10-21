# Security, Privacy, Performance, And Scalability Gates

Load this reference when code touches authentication, authorization, user input, files, databases, secrets, tokens, payments, PII, network calls, admin features, serialization, template rendering, shell commands, dependencies, hot paths, batch jobs, queues, caches, or rendering.

## Security Gate

Check for concrete misuse paths:

- authentication bypass
- broken authorization or access control
- insecure direct object reference
- injection: SQL, command, template, LDAP, NoSQL, prompt, or header injection
- XSS, CSRF, SSRF, and open redirect risks
- path traversal and unsafe file upload or download
- secret, token, or PII leakage
- sensitive information in logs, metrics, errors, traces, or analytics
- unsafe deserialization
- insecure defaults or missing deny-by-default behavior
- missing audit trail for admin or security-sensitive actions
- dependency or supply-chain risk introduced by the change

Security findings must include an attack or misuse path. Do not report broad security anxiety without a reachable path.

## Privacy Gate

Check:

- data minimization
- user consent and purpose limitation when visible in product code
- retention and deletion behavior
- PII propagation across logs, queues, caches, analytics, or third-party APIs
- redaction in errors and support tooling
- tenant or workspace isolation

## Performance And Scalability Gate

Run when code touches hot paths, loops over large data, database access, network calls, rendering, serialization, background jobs, queues, caches, batch processing, or startup.

Check:

- N+1 queries
- unbounded loops or memory growth
- missing pagination or streaming
- missing indexes or inefficient query predicates
- blocking operations in async paths
- excessive retries or retry storms
- cache correctness and invalidation
- thundering herd risks
- lock contention and shared mutable state
- work done per request that should be amortized or precomputed
- startup path regressions

Report performance issues only when plausible at realistic scale. Include the scale trigger and affected path.

## Operational Readiness Gate

Check:

- can operators detect the failure?
- can operators identify affected users, jobs, records, or requests?
- is there enough context in logs without leaking sensitive data?
- are metrics and alerts aligned with the failure mode?
- is rollback or mitigation clear for risky changes?

## Merge Gate Questions

Before signing off a risky change, ask:

- what is the worst realistic misuse path?
- would an operator detect it quickly?
- would the blast radius stay local?
- can the team roll back safely?
