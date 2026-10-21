# Elastic Docs Links

The local version range is Elasticsearch `9.5.4` and later. Use official Elastic docs applicable to the actual deployment version or a matching local Elasticsearch branch for exact syntax and behavior checks. Treat `9.5.4` as the minimum baseline, not an exact version pin.

## Starting Points

- ES|QL reference: https://www.elastic.co/docs/reference/query-languages/esql
- Commands: https://www.elastic.co/docs/reference/query-languages/esql/commands
- Functions and operators: https://www.elastic.co/docs/reference/query-languages/esql/functions-operators
- Release notes: https://www.elastic.co/docs/release-notes/elasticsearch

## High-Value Pages for Reviews

- `STATS`: https://www.elastic.co/docs/reference/query-languages/esql/commands/stats-by
- `LIMIT`: https://www.elastic.co/docs/reference/query-languages/esql/commands/limit
- `SORT`: https://www.elastic.co/docs/reference/query-languages/esql/commands/sort
- `TS`: https://www.elastic.co/docs/reference/query-languages/esql/commands/ts
- `RATE`: https://www.elastic.co/docs/reference/query-languages/esql/functions-operators/time-series-aggregation-functions/rate
- Metric temporality: https://www.elastic.co/docs/manage-data/data-store/data-streams/metric-temporality
- Time series index settings: https://www.elastic.co/docs/reference/elasticsearch/index-settings/time-series
- `TBUCKET`: https://www.elastic.co/docs/reference/query-languages/esql/functions-operators/grouping-functions/tbucket
- Operators: https://www.elastic.co/docs/reference/query-languages/esql/functions-operators/operators
- Time-series aggregation functions: https://www.elastic.co/docs/reference/query-languages/esql/functions-operators/time-series-aggregation-functions

## Facts Worth Rechecking

- `STATS` supports per-aggregation `WHERE`; this is not equivalent to filtering rows before `STATS`.
- `LIMIT N BY group` keeps up to N rows per group; use a preceding `SORT` when order matters.
- ES|QL result limits cap output rows, not the number of source documents scanned. `TS` and `FROM` use separate default and maximum limit settings; preserve output coverage when switching sources.
- `RATE`, `INCREASE`, and `IRATE` can respect both delta and cumulative temporality. The local delta contract does not establish whether index metadata enables that behavior. Check the target version, mapping, temporality setting, and document values; see [ts-vs-from.md](ts-vs-from.md#rate-and-temporality). The short `RATE` reference alone does not describe all temporality behavior.
- Integer division truncates when both operands are integer types; use a double operand or cast for fractional division.
- Many scalar operators return null on multivalued inputs.
