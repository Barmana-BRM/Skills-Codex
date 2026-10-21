---
name: esql
description: "Review Elastic ES|QL queries for Elasticsearch 9.5.4 and later, covering compatibility, correctness, Prometheus and 01.metrics operational-metric semantics, alert reliability, and query performance. Use when Codex is asked to inspect, critique, fix, or rewrite ES|QL pipelines, especially Elastic/Kibana alert queries embedded in .yaml/.yml files or standalone .esql queries."
---

# ES|QL Query Review

## Workflow

1. Target Elasticsearch `9.5.4` and later; `9.5.4` is the minimum local version, not an exact version pin. Use the actual deployment version when known, and verify version-sensitive syntax and behavior against applicable official Elastic docs or matching-version material already supplied inside this project.
2. Detect the input format before extracting queries:
   - For `.yaml`/`.yml`, parse the YAML and review each ES|QL block scalar such as `query: |`. Read the surrounding alert metadata and comments before reviewing the query.
   - For `.esql`, treat the file as one query unless the user explicitly identifies multiple queries.
3. Infer the query intent, source grain, time range, whether the alert runner injects the time window, metric format and type, grouping grain, and alert condition before judging the query. Distinguish traditional Prometheus metrics from the `01.metrics` operational format before reviewing aggregation semantics. In YAML alerts, use fields such as `name`, `description`, `severity`, `interval_sec`, and `time_window` as part of that contract.
4. Read `references/review-checklist.md` for any non-trivial review. Read `references/01-metrics.md` when the query uses operational fields such as `metrics.calls`, `metrics.failures`, or `metrics.duration_*`, or when the metric format is ambiguous. Read `good-examples.esql` and `bad-examples.esql` when matching this repository's preferred review style or adding new examples. In `bad-examples.esql`, text after `PROBLEM:` or `Problem:` is annotation, not ES|QL.
5. Review in passes: syntax/version, source scope, filter placement, aggregation grain, metrics semantics, null and multivalue behavior, arithmetic, alert determinism, result limits, and output shape.
6. Prefer findings over generic advice. Every finding should name the risky fragment, explain why it matters, and propose a concrete fix or safer rewrite.

## Choosing `TS` or `FROM`

In our metrics environment, all stored counters are interval deltas, including counters originating from Prometheus. Treat this as the established local data contract. For a direct total over complete intervals, sum the counts; for throughput, divide by the covered duration. Elasticsearch `9.5.4` also supports `RATE` and `INCREASE` on delta counters using the metric mapping and configured temporality metadata. Check that field configuration when judging a query; do not reject these functions merely because the samples are deltas. See [references/ts-vs-from.md](references/ts-vs-from.md#rate-and-temporality).

Choose from the required calculation, not from the fact that the source is a time series data stream (TSDS). Use `FROM` when matching samples can be combined directly; use `TS` when each series needs a separate calculation before combining results. For metric aggregations or a proposed `TS`/`FROM` rewrite, read [references/ts-vs-from.md](references/ts-vs-from.md) for the decision table, equivalence conditions, and examples.

## Review Scope

- Keep filesystem inspection inside the current ES|QL project and files explicitly supplied by the user.
- Do not search sibling repositories, parent workspaces, application code, deployment code, or metric producers to infer undocumented behavior unless the user explicitly asks for that investigation.
- Use the query, YAML metadata and comments, bundled references, examples, and official Elastic documentation. If these do not establish a data contract, state the assumption or uncertainty in the review instead of searching external code.

## Review Stance

- Be strict about correctness, false negatives, false positives, arbitrary alert rows, and obviously excessive shard scans.
- Be careful with inferred data contracts. If a problem depends on undocumented assumptions such as "one document per metric per timestamp", say that explicitly.
- Do not claim that a final `KEEP` or `DROP` improves aggregation cost. It mostly reduces response payload after upstream work has already happened.
- Do not rewrite the whole query unless the user asks. For review, preserve the original intent and give minimal corrected fragments.
- Treat `good-examples.esql` as style calibration: narrow sources where possible, filter early, name intermediate fields, use conditional `STATS`, use deterministic `SORT` before top-N `LIMIT`, and produce alert-friendly `details`.
- Apply the local interval-delta contract and the `TS`/`FROM` decision rule when reusing examples. Existing `SUM(SUM_OVER_TIME(...))` examples do not prove that `TS` is needed.

## Output Format

Start with findings, ordered by severity. Use this shape:

```text
[severity] Short title
Fragment: `...`
Why: ...
Fix: ...
```

Use severities:

- `blocker`: invalid ES|QL, wrong version, or query cannot return intended result.
- `high`: likely false alert, missed alert, or severe avoidable cluster cost.
- `medium`: fragile metric semantics, cardinality risk, nondeterministic output, or maintainability issue that can affect operations.
- `low`: readability, naming, comments, magic constants, or minor style.

After findings, include a corrected fragment or full corrected query only when it materially helps. If there are no material issues, say so and list residual assumptions that could not be verified from the query alone.

## Version Notes

The local version range is Elasticsearch `9.5.4` and later. Prefer official Elastic documentation applicable to the actual deployment version or a checked-out matching Elastic branch over memory. Useful starting points are in `references/elastic-docs.md`.
