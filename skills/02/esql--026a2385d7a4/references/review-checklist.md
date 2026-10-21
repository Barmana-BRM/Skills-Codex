# ES|QL Review Checklist

Use this checklist to review Elastic ES|QL queries. Keep the final answer focused on issues that can change correctness, cost, or alert behavior.

## Input Shape

- Treat a standalone `.esql` file as one query unless the user explicitly identifies multiple queries.
- A supplied query may be complete or a fragment.
- For fragments, review only the visible behavior and state missing assumptions.

## YAML Alert Definitions

- Alert queries may be embedded in `.yaml` or `.yml` files as block scalars, commonly `query: |`. Parse the YAML structure instead of extracting the query with ad hoc line matching.
- Review every alert object independently when a file contains a list or multiple YAML documents.
- Use surrounding fields and comments to infer intent and execution semantics. Important fields include `name`, `description`, `severity`, `interval_sec`, and `time_window`.
- Treat a valid `time_window` as the externally injected query time bound. Do not report a missing `@timestamp` predicate when the alert runner applies this window.
- Check agreement between metadata and query text: hard-coded periods in comments or `details` must match `time_window`, and sustained-event logic must be possible at the configured `interval_sec` and metric publication cadence.
- Keep YAML findings separate from ES|QL findings. Flag malformed YAML, a missing/empty `query`, invalid duration values, or contradictory scheduling metadata only when they affect alert execution or meaning.

## Source Scope and Filtering

- Flag very broad `FROM` patterns when a narrower data stream, namespace, cluster, service, or metric family is available.
- Check for a time filter when the query is meant to run over a bounded window. If the user says the query is executed as an alert and the alert runner injects the time range outside the ES|QL text, treat the time bound as satisfied and do not report "missing time bound" as a finding. You may mention the external time-window assumption if it matters.
- A final `LIMIT` does not reduce scanned documents.
- Prefer filters before `STATS` when they are row predicates such as environment, service, metric name, cluster, namespace, or timestamp.
- Keep aggregate predicates after `STATS`, for example `WHERE c > 100`.
- Do not recommend moving a per-aggregation `WHERE` out of `STATS` when the query intentionally computes several conditional aggregates from the same input.

## Syntax and Version

- Verify SQL habits: ES|QL uses `WHERE` after `STATS` for aggregate filters, not SQL-style `HAVING`.
- `LIMIT N BY group` is valid ES|QL, but it should be preceded by a deterministic `SORT` when the query needs the top or latest row per group.
- Conditional aggregations use `STATS value = AGG(field) WHERE condition`.
- `TS` enables time-series aggregation functions inside `STATS`; `FROM` does not have the same time-series semantics.
- Target Elasticsearch `9.5.4` and later. Verify version-sensitive command or function behavior against official docs for the actual deployment version.

## Aggregation Grain

- Identify the intended grain before judging `BY`: service, host, shard, namespace, cluster, time bucket, or full alert.
- Flag `STATS ... BY high-cardinality fields` such as trace IDs, user IDs, raw `@timestamp`, request IDs, or concatenated identifiers unless the user is intentionally listing individual events.
- For metrics, raw `@timestamp` often creates one group per sample. It may be valid for exact pivoting, but it is fragile when publishers have jitter.
- If pivoting metrics with conditional `STATS`, check whether all metrics are guaranteed to share the exact same timestamp and grouping dimensions. If not, recommend a time bucket or `TS` query.
- Question `MAX`, `MIN`, or `AVG` used as a duplicate resolver. `MAX` is only safe when the input contract guarantees one value per metric per group, or when the maximum is actually the intended statistic.

## Time-Series Metrics

- Identify the metric format before reviewing aggregation semantics. This system contains both traditional Prometheus metrics and the `01.metrics` operational format; do not apply one field model to both.
- Prometheus-origin metrics retain their instrument fields and labels, but all counters stored in our environment are interval deltas. Apply this established contract to both Prometheus-origin and `01.metrics` counters; a counter name or upstream instrument type does not imply cumulative stored readings.
- Operational metrics normally use a `scope.name` beginning with `01-metrics/`, `attributes.operation`, and fields such as `metrics.calls`, `metrics.failures`, and `metrics.duration_*`. Consult `references/01-metrics.md` when these fields are present.
- For operational metrics, `metrics.calls` is the number of operations in the client aggregation bucket, `metrics.failures` is the unsuccessful-operation count, `metrics.duration_max` is the maximum duration in the bucket, and `metrics.duration_avg_calls` is total duration in nanoseconds. `metrics.duration_NN_calls` stores the client percentile multiplied by calls.
- Operational metrics are emitted as bucket deltas. `SUM(metrics.calls)` across client buckets counts operations over the query window; `MAX(metrics.calls)` selects the busiest client bucket. Choose between them from the alert intent rather than flagging either mechanically.
- An SDK gauge is encoded specially in the operational format: `metrics.calls` is always `1`, while `metrics.duration_avg_calls`, `metrics.duration_min`, and `metrics.duration_max` carry the actual gauge value. Review gauge queries against the duration field, not `metrics.calls`.
- Still check duplicate ingestion, client-instance grouping, client aggregation resolution, and whether the query intentionally combines all sources.
- Choose `TS` or `FROM` from the required calculation, not the storage mode or metric name. Read [ts-vs-from.md](ts-vs-from.md): interval-delta totals/rates, direct sample extrema, and sample-weighted averages suit `FROM`; latest-per-series values and equal-series weighting need per-series processing.
- Check whether `SUM(SUM_OVER_TIME(x))`, `MAX(MAX_OVER_TIME(x))`, or `MIN(MIN_OVER_TIME(x))` can collapse to a direct `FROM` aggregation under the equivalence conditions in that reference. Do not collapse mixed reductions such as `SUM(MAX_OVER_TIME(x))` or an unweighted average of per-series averages.
- For our counters, direct totals use `SUM` and throughput divides those totals by the covered duration in seconds. Elasticsearch `9.5.4` also supports `RATE` and `INCREASE` on delta counters. Check counter mapping and `index.time_series.temporality_field` with a `delta` dimension value; missing or invalid temporality metadata makes counter fields default to cumulative semantics. Do not flag these functions solely because the input is delta. See [ts-vs-from.md](ts-vs-from.md#rate-and-temporality).
- For gauges, confirm whether `MAX`, `MIN`, `AVG_OVER_TIME`, `LAST_OVER_TIME`, or percentile matches the alert's real intent.
- Check bucket size. Very small buckets can explode result sets; very large buckets can hide spikes or smear incidents.
- Check whether the query mixes metrics with different dimensional cardinality. Missing dimensions can turn calculations into nulls or misleading totals.

## Nulls, Missing Data, and Multivalues

- Treat blanket `COALESCE(metric, 0)` as risky. Missing may mean zero, data loss, failed pivot, or ingestion lag depending on the metric.
- Check denominators before division. Avoid divide-by-zero and low-sample alert noise.
- For percentages, make sure the zero case matches the real semantics. Example: if `good = 0` and `dropped > 0`, drop percentage should not become `0`.
- For string output, guard important fields with `COALESCE(TO_STRING(field), "<missing>")` when nulls would make alert details useless.
- Arithmetic and comparisons over multivalued fields can return null. Use `MV_*` functions, `MV_EXPAND`, or an explicit single-value contract.

## Arithmetic and Types

- Integer division rounds toward zero when both operands are integer types. Use `100.0`, `1048576.0`, `::DOUBLE`, or `TO_DOUBLE` when fractional math matters.
- Avoid awkward mixed types in `COALESCE` and `CASE`, especially when later doing floating-point math.
- Avoid rounding before threshold comparison unless the alert intentionally compares rounded values.
- Prefer named intermediate fields for complex formulas. This makes denominator handling and null behavior reviewable.
- Replace magic constants with named fields when they encode units, thresholds, or policy.

## Alert Determinism

- `LIMIT` without `SORT` returns arbitrary rows from the reviewer perspective. If the query alerts on top offenders, require a meaningful `SORT`.
- If more rows can match than the alert returns, make the selection deterministic and explain what is being sacrificed.
- Low sample sizes can produce noisy rates or percentages. Consider minimum request/event thresholds.
- Average can hide spikes. For incident detection, consider max, percentile, bucket-count, or sustained-threshold logic.
- Counting threshold-breaching buckets establishes how many buckets breached anywhere in the selected range, not consecutive duration. A preceding `SORT` does not make the count consecutive.
- Ordinary bucket aggregation omits minutes with no matching documents. Neither division by the bucket duration nor `COALESCE` on existing rows creates missing buckets; verify no-data behavior separately.
- For interval counts divided by a fixed bucket duration, use complete, aligned buckets and account for ingestion lag. An injected time window may be bounded yet still cut the first or last minute short.
- Build expensive `details` strings after filtering to the rows that will be returned.

## Output and Maintainability

- When replacing `TS` with `FROM`, check the effective default and maximum output limits and any explicit `LIMIT`; the source commands use different settings. Preserve final row coverage as described in [ts-vs-from.md](ts-vs-from.md#result-limits).
- Use `KEEP`/`DROP` for response shape and alert payload clarity, not as a claimed performance fix after aggregation.
- Name repeated complex expressions once with `EVAL`, then reuse the alias.
- Prefer meaningful field names: `request_rate`, `error_pct`, `period`, `cluster`, `namespace`, `host`.
- Comments should explain business meaning or data contracts, not claim false performance benefits.
- Preserve localized alert text from the original query unless the user asks to rewrite copy.
