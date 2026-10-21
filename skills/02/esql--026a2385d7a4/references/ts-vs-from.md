# Choosing TS or FROM for metrics

Ask: can samples from all matching series be combined before calculating the requested statistic? If yes, prefer a direct `FROM` aggregation. If each series must contribute a separately calculated value, use `TS` with an explicit inner function. A TSDS source, an `_OVER_TIME` function name, or a field ending in `_count` alone does not settle the choice.

## Local counter contract

All counters stored in our metrics environment are interval deltas, including counters originating from Prometheus. This establishes what the samples mean; it does not establish the Elasticsearch mapping or temporality configuration. For direct totals over complete intervals, sum the counts and divide by the covered duration in seconds for throughput. Do not ask the user to choose delta versus cumulative semantics again for our sources.

For explicitly external sources outside this contract, establish the stored temporality separately.

## RATE and temporality

Our minimum Elasticsearch version, `9.5.4`, supports `RATE`, `INCREASE`, and `IRATE` for delta counters; later versions are also in scope. Elastic documents this in [metric temporality](https://www.elastic.co/docs/manage-data/data-store/data-streams/metric-temporality): under `TS`, delta readings contribute their values directly, while cumulative readings require differences. `RATE` returns a per-second result; do not divide it by 60 again.

Check how Elasticsearch interprets the field:

- The source must support `TS`, and the metric mapping must support the counter function. Delta values stored in an ordinary gauge field do not automatically become a supported counter input.
- For native temporality handling, `index.time_series.temporality_field` names a `keyword` dimension (`time_series_dimension: true`). Its document value must be `delta` for our counters. Missing or invalid values default counter fields to cumulative semantics. See [time series index settings](https://www.elastic.co/docs/reference/elasticsearch/index-settings/time-series).
- Supported native OTLP ingestion preserves temporality automatically; custom ingestion must configure and populate it. The local fact that samples are deltas is not evidence that this metadata is present.
- Native temporality support is documented in the [9.5.0 release notes](https://www.elastic.co/docs/release-notes/elasticsearch) and [Elastic's explanation](https://www.elastic.co/search-labs/blog/otel-metrics-cumulative-delta-elasticsearch). This capability is available at our `9.5.4` baseline; verify any version-sensitive changes against the actual deployment version.

When those conditions hold, `TS ... | STATS SUM(RATE(x)) BY TBUCKET(1 minute)` is valid for delta counters. If metadata is unknown, state that gap; do not label `RATE` wrong merely because the data is delta. `FROM` does not interpret temporality metadata. Its direct sum/division remains a candidate for ordinary numeric deltas when the requested window and bucket semantics match; do not assume it is equivalent to a `RATE` query's lookback or boundary handling.

## Decision table

| Intended quantity | Query shape | Reason |
| --- | --- | --- |
| Requests from per-interval counts | `FROM ... \| STATS SUM(x)` | Add the disjoint interval counts. |
| Throughput from per-interval counts | `FROM ... \| STATS total = SUM(x) \| EVAL rate = total / 60.0` | For one complete minute, divide the interval-count total by 60 seconds; use the actual covered duration for other windows. |
| Counter rate with configured temporality | `TS ... \| STATS SUM(RATE(x))` | Supports delta or cumulative counters when the version, mapping, and temporality conditions above hold. |
| Sum of latest gauge values | `TS ... \| STATS SUM(LAST_OVER_TIME(x))` | Each series contributes its latest value in the selected window. |
| Highest/lowest recorded sample | `FROM ... \| STATS MAX(x)` / `MIN(x)` | Series identity does not affect the extremum. |
| Sum of each series' peak | `TS ... \| STATS SUM(MAX_OVER_TIME(x))` | Each peak must be calculated separately. |
| Average with equal weight per sample | `FROM ... \| STATS AVG(x)` | Every non-null sample contributes equally. |
| Average with equal weight per series | `TS ... \| STATS AVG(AVG_OVER_TIME(x))` | Each contributing series supplies one average. |

Equal weight per series is not necessarily equal weight per host: a host may have several series. Establish the intended dimensions first. A latest value within a window also needs a freshness policy before it can be described as current.

The [TS reference](https://www.elastic.co/docs/reference/query-languages/esql/commands/ts) documents per-series processing and implicit inner functions. For numeric fields, omitting the inner function can imply `LAST_OVER_TIME`; do not assume `TS ... | STATS SUM(x)` sums all stored samples. Verify behavior and function/type support for the target version.

## Collapsing redundant per-series reductions

These mathematical reductions do not require series identity:

| Original TS expression | Direct FROM expression |
| --- | --- |
| `SUM(SUM_OVER_TIME(x))` | `SUM(x)` |
| `MAX(MAX_OVER_TIME(x))` | `MAX(x)` |
| `MIN(MIN_OVER_TIME(x))` | `MIN(x)` |

Before proposing a rewrite, establish all of the following:

- The input is ordinary numeric samples. Downsampled `aggregate_metric_double`, histogram/distribution fields, and mixed mappings require separate semantic verification.
- Both queries select the same documents and preserve filters, non-time grouping keys, null handling, and field expressions. Check multivalue behavior if present.
- Time buckets have identical boundaries and membership. The inner function has no distinct lookback, sliding/overlapping window, or other behavior that changes which samples enter each output bucket.
- No other aggregate in the same `STATS` still needs series identity. Check the whole aggregation before changing its source command.
- Final output row coverage is preserved. Check the effective default and maximum result limits and any explicit `LIMIT`; see [Result limits](#result-limits).

Use `BUCKET(@timestamp, 1 minute)` for an explicit one-minute grouping in the `FROM` rewrite. `TBUCKET` is timestamp-based shorthand, not itself a reason to choose `TS`; check exact syntax against the target version.

The sum rewrite preserves the mathematical total, but a different floating-point reduction order can change low-order bits. Check output types, null/empty behavior, and threshold results when validating equivalence.

Do not apply these substitutions to `SUM(LAST_OVER_TIME(x))`, `SUM(MAX_OVER_TIME(x))`, or `AVG(AVG_OVER_TIME(x))`. For example, series with samples `[0, 100]` and `[100]` have a sample average of `200 / 3`, but an equal-series average of `(50 + 100) / 2 = 75`. Evaluate a `RATE` or `INCREASE` rewrite separately against its temporality, time window, and boundary behavior; replacing it on delta data is not automatically a correctness fix or an equivalent simplification.

## Result limits

The [LIMIT documentation](https://www.elastic.co/docs/reference/query-languages/esql/commands/limit) lists default output limits of 10,000 rows for `TS` and 1,000 for `FROM`. Verify the target version and effective cluster settings: ordinary queries use `esql.query.result_truncation_default_size` and `esql.query.result_truncation_max_size`; time-series queries use `esql.query.timeseries_result_truncation_default_size` and `esql.query.timeseries_result_truncation_max_size`.

For a query returning 1,464 minute buckets, switching to `FROM` without a sufficient final `LIMIT` can truncate the result to 1,000 rows under those defaults. When returning buckets, preserve the required coverage with an explicit final `LIMIT` within the effective maximum, and use a deterministic `SORT` when order or row selection matters. If the maximum is insufficient, report that limitation rather than claim equivalence.

These limits apply to final output, not intermediate buckets consumed by a later `STATS`. Do not insert a `LIMIT` before the downstream alert aggregation; doing so would change its counts or totals.

## Request throughput example

The local `requests_count` field follows the interval-delta contract. The investigation's sum-of-sums can become:

```esql
FROM metrics_*:.ds-metrics-otelcol*vegas*
  | WHERE service.environment == "production"
    AND service.name == "aggregator"
    AND metrics.http.server.requests_count IS NOT NULL
    AND attributes.integration == "softswiss"
    AND attributes.status == "200"
    AND attributes.uri NOT LIKE "*actuator*"
  | STATS rpm = SUM(metrics.http.server.requests_count)
      BY bucket = BUCKET(@timestamp, 1 minute)
  | EVAL rps = rpm / 60.0
```

This fragment assumes the runner supplies a range of complete minutes and that collection intervals align with the intended accounting buckets. Preserve the existing downstream threshold, grouping, and alert output when making this substitution. Review missing and partial buckets separately using [review-checklist.md](review-checklist.md).

## Performance evidence

When a profile retains an unnecessary intermediate grouping by `(_tsid, time bucket)`, high series cardinality can produce many intermediate rows even if the final result has few buckets. Inspect the physical plan, intermediate row counts, and coordinator aggregation cost; a small final result or fast shard phase does not prove the whole query is cheap.

In the [linked investigation](https://chatgpt.com/g/g-p-69b7b5eedbe08191be7240aa95d03360-es-plugin/c/6ac4f6ab-afe0-83eb-8c4b-dae4ba9da91a), the discussion described about 36.85 million intermediate rows for 1,464 output buckets and 19.2 seconds spent hashing at the coordinator. The user subsequently reported that the `FROM` version was about 100 times faster. These are case-specific reports; the retrieved discussion did not include a replacement profile establishing its exact row counts or execution mechanism.

Treat this as motivation to test an equivalent rewrite, not a universal claim that `TS` is slow or `FROM` is 100 times faster. When execution is available and authorized, compare results and timings over the same fixed range, source, filters, and cluster conditions; use profiles to establish the mechanism. Otherwise distinguish mathematical equivalence, a suspected plan cost, and an unmeasured speedup. Retain `TS` when its per-series semantics are necessary.
