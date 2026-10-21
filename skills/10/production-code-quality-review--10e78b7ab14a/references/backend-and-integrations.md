# Backend And Integration Review Heuristics

Load this reference when the change touches Node services, API routes, webhooks, queues, schedulers, external SDK clients, or cross-service contracts.

## Request And Response Boundaries

Check:

- runtime validation before business logic
- request-scoped context leakage
- status code and error contract consistency
- backward compatibility for callers
- idempotency for create, webhook, or retry-prone endpoints
- auth and permission checks before loading privileged data
- partial parsing that lets invalid payloads reach side effects

## Reliability

Check:

- timeout and cancellation behavior
- upstream retries and retry storms
- resource cleanup for streams, files, sockets, and clients
- partial failure when local and external writes both happen
- connection pool or client reuse assumptions
- background work kicked off without ownership or retry policy
- duplicate delivery handling for webhooks and queues

## Integrations

Check:

- request and response versioning assumptions
- partial or missing field behavior
- schema validation before side effects
- enum expansion and unknown status handling
- ordering assumptions between local and remote writes
- fallback behavior when upstream is degraded

## Observability

Check:

- request IDs or correlation IDs
- logs that explain upstream failure without leaking sensitive data
- metrics around retries, failures, and latency
- enough logging to map a failure back to the input contract

## Common Bugs

- async errors not awaited
- broad catch blocks that swallow response semantics
- response sent twice
- mutable shared state across requests
- webhook verification missing or happening too late
- retries wrapped around non-idempotent writes
- success responses emitted before downstream side effects commit

## Review Prompts

Ask:

- does this change preserve response shape for existing callers?
- if an upstream dependency is slower or stricter, how does this handler degrade?
- where does local state become inconsistent if the external call fails?
- if the callback is delivered twice, does local state stay correct?
