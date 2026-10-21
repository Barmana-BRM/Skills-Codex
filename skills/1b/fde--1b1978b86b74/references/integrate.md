# integrate - Prove the system boundary

An integration works when an input crosses the real boundary and produces the agreed downstream result.

**Use when:** connecting or changing an API, data source, SDK, event stream, tool, or service contract.

Follow [task context](task-context.md); `.fde/` is optional. Use the customer's existing clients, authentication, fixtures, and diagnostics. One connection does not call for a new integration platform.

## Define the boundary and evidence

Map producer, consumer, owner, direction, and side effects. Inspect the installed version and local implementation; check uncertain behavior against current official documentation. Identify schemas, authentication scopes, network boundaries, and the permitted test environment. Before changing an untested boundary, characterize mappings, ordering, and other behavior its callers depend on.

Write a real input and expected downstream result, plus a rejection or failure example. Keep configuration validity, authentication, connectivity, contract compatibility, and end-to-end behavior separate: evidence for one does not prove the next.

Inspect credentials by presence and scope without printing values; use existing secret storage. Check classification and retention before moving data. Never load raw `<private>` blocks into a model. Prefer sanitized or synthetic cases approved for the target environment.

## Implement the narrow adapter

Use native repository patterns. Validate external inputs and model outputs, bound timeouts and retries, and handle cancellation. Preserve error codes and the failure phase without leaking payloads. Keep explicit authentication or permission rejection distinguishable from transport uncertainty.

For writes, establish idempotency or duplicate detection before retries and apply the uncertain-write rules below. For events, address ordering, replay, and poison messages where relevant.

## Resolve uncertain writes safely

Use existing storage and worker mechanisms for these rules:

- **Identify the attempt before dispatch.** For a replayable write, persist a tenant-scoped operation identity, payload identity, and enough state to recover after restart. Establish ownership of in-flight attempts so workers cannot independently replay them. Verify any upstream deduplication guarantee, including key, payload rules, and retention window; sending a key proves nothing by itself.
- **Preserve ambiguity.** A timeout, cancellation, or lost response after dispatch can hide a completed side effect. Keep that uncertainty across restart. Stopping the caller is not rollback; do not silently create a fresh operation from an uncertain attempt.
- **Reconcile before replay.** Use an authoritative receipt or lookup matching the operation and payload. One verified result can confirm completion; conflicting or multiple matches need resolution. An empty stale, partial, or eventually consistent lookup proves neither absence nor permission to replay. Retry only under the verified deduplication contract or evidence that repeating the write is safe.
- **Keep a resolution owner.** Leave unresolved attempts visible with safe error context, a next action, and a known owner or explicit ownership gap. Manual corrective writes still need authority. Do not invent completion to clear a queue.
- **Exercise the failure boundary.** Test a committed write with a lost response, cancellation or restart before success is recorded, and stale lookup or concurrent replay where applicable. Record what was exercised and what remains unproven.

## Prove the result and recovery

Exercise a permitted success case and relevant failures, such as denied access, malformed data, rate limits, timeout, duplicate delivery, or partial completion. Trace correlation IDs or other safe evidence on both sides. Check cleanup and recovery for test side effects. A mock proves client behavior only; missing live access is a verification gap.

Use [verification](verification.md) for receipts and [review](review.md) for security or data-contract changes. Deploy through [ship](ship.md) only when authorized.

*Fictional example:* Northstar's ERP accepts an order but the response is lost. An empty, delayed search result does not justify resubmission. Keep the attempt unresolved until an authoritative receipt or verified deduplication contract supports the next action.

## Completion

Return the contract, changed paths, environment, evidence at each tested layer, and remaining dependencies with owners when known. Completion requires the agreed end-to-end result or an explicitly agreed narrower scope; never silently replace live acceptance with a stub. In engagement mode, update existing terrain/delivery records with confirmed facts under their write rules; otherwise return the receipt directly.
