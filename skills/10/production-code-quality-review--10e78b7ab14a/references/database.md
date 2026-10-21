# Database And Migration Review Heuristics

Load this reference when the change touches schema, migrations, queries, indexes, transactions, or persistence logic.

## Migrations

Check:

- backward compatibility during rolling deploys
- lock duration and blast radius
- rollback path
- default value behavior on large tables
- data backfill safety

## Queries And Transactions

Check:

- transaction boundaries and isolation assumptions
- tenant or workspace scoping
- pagination and cardinality
- index coverage for new predicates
- N+1 or fan-out behavior

## Correctness

Check:

- uniqueness assumptions
- stale read vs write ordering
- nullable columns and application expectations
- serialization compatibility for stored payloads
