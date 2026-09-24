---
title: "OLAP Cube"
category: "distributed-data"
difficulty: "intermediate"
tags: [olap, analytics, data-warehouse]
related: [columnar-storage-format, etl-pipeline, dashboard-metrics]
---

# OLAP Cube

"Show me revenue by region, by quarter, by product category — and let me drill from year to month to day." Answering that from raw transaction rows takes minutes; an OLAP cube pre-aggregates the answers so slicing and dicing is instant. Building one teaches you the central trick of analytics: trade storage for query speed by precomputing along dimensions.

## Core concepts

- **Dimensions and measures** — Dimensions are the axes you slice by (time, region, product); measures are the numbers you aggregate (revenue, units, profit). Every analytical question is "measures grouped by dimensions."
- **Cube / hypercube** — The N-dimensional array of precomputed aggregates: each cell holds the aggregate for one combination of dimension values. A 3-dimension cube is literally a cube; real ones have dozens of dimensions.
- **Roll-up and drill-down** — Roll-up aggregates to a coarser level (day → month → year); drill-down goes finer. The cube makes both O(1) lookups instead of rescans because every level is precomputed.
- **Slice and dice** — Slice fixes one dimension ("only 2025") to get a sub-cube; dice selects ranges on multiple dimensions. These are the operations behind every pivot-table drag.
- **MOLAP vs ROLAP** — MOLAP precomputes and stores the cube in a specialized multidimensional engine (fast queries, expensive builds, sparse-data problems); ROLAP computes aggregations on the fly from relational tables with heavy indexing (flexible, slower). Modern systems mostly blend both.
- **Sparsity** — Most dimension combinations never occur (nobody bought snow tires in Miami in July). Naive cubes explode combinatorially; real engines store only non-empty cells and compress aggressively.
- **Pre-aggregation tradeoff** — The cube answers known query patterns instantly but must be rebuilt when data or dimensions change. Choosing which aggregations to precompute — and which to compute at query time — is the core design decision.

## How it works

You declare dimensions with hierarchies (time: year → quarter → month → day; geography: country → region → city) and measures with aggregation functions (sum of revenue, count of orders). The build job scans the fact table once and computes aggregates for every combination of dimension levels — the full lattice, or a chosen subset — storing each as (dimension-key tuple → measure values) in a sparse map. A query like "revenue by quarter for electronics in 2025" becomes a direct lookup of precomputed cells plus a sum over the quarter level; drill-down to month just reads the finer-grained cells. Incremental builds append new facts and update affected cells rather than rebuilding the world.

## Build milestones

1. Build the aggregator: read a CSV of sales rows and compute `GROUP BY` aggregates for one dimension set (e.g. revenue by month × region) into a dictionary keyed by tuple.
2. Add hierarchies: support roll-up/drill-down on a time dimension (day → month → quarter → year) by precomputing each level; query any level instantly.
3. Add slice and dice: a tiny query API (`cube.query(dims={year: 2025}, measures=["revenue"])`) that filters precomputed cells instead of scanning rows.
4. Handle sparsity and scale: store only non-empty cells, benchmark build time and size as you add dimensions, and feel the combinatorial explosion firsthand.
5. Impressive end state: a cube over a million-row dataset with 4+ dimensions and hierarchies, an HTTP API for slice/dice/roll-up/drill-down, and a small frontend pivot table — with benchmarks showing sub-100ms queries against the multi-second raw scan.

## Best resources

- [OLAP cube — Wikipedia](https://en.wikipedia.org/wiki/OLAP_cube) — The operations (slice, dice, roll-up, drill-down, pivot) explained precisely, with the MOLAP/ROLAP/HOLAP taxonomy.
- [Online analytical processing — Wikipedia](https://en.wikipedia.org/wiki/Online_analytical_processing) — The broader context: OLAP vs OLTP, and why transactional databases make terrible analytics engines.
- [ClickHouse](https://clickhouse.com/) — A columnar OLAP database whose docs are a masterclass in how pre-aggregation, sorting keys, and compression make analytics fast.
- [DuckDB](https://duckdb.org/) — An embeddable analytical database; perfect for experimenting with cube-style queries locally before building your own engine.

## Stretch ideas

- Implement incremental cube updates: stream new sales rows in and update only the affected cells, measuring how freshness trades against build cost.
- Add approximate aggregates (HyperLogLog for distinct counts, t-digest for percentiles) to cells so the cube stays small on high-cardinality dimensions.
