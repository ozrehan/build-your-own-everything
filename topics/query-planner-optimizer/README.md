---
title: "Query Planner and Optimizer"
category: "databases"
difficulty: "advanced"
tags: [sql, query-optimization, cost-model]
related: [sql-parser, columnar-storage-format, b-tree-index, olap-cube]
---

# Query Planner and Optimizer

The planner is what makes declarative SQL fast: it turns "give me these rows" into a concrete execution plan — which indexes to use, which join order, which algorithm — chosen by cost, not by the user. Building one teaches why the same query can run in 1 ms or 10 s, and how statistics drive that decision.

## Core concepts

- **Logical vs. physical plans** — The logical plan says *what* (join A and B, filter, aggregate); the physical plan says *how* (hash join vs. nested loop, index scan vs. seq scan). Optimization is the search over physical plans for one logical query.
- **Cost model** — Every plan gets an estimated cost from statistics: table row counts, page counts, index selectivity, CPU vs. I/O weights. The optimizer picks the cheapest estimate — which is only as good as the statistics.
- **Table statistics and histograms** — The planner keeps per-column stats (distinct counts, most-common values, histograms of value distribution) built by `ANALYZE`. Stale stats are the #1 cause of bad plans in production.
- **Join ordering** — With n tables there are n! join orders. System R's dynamic programming (build optimal plans for 1 table, then 2, then 3...) finds the optimum without enumerating everything; greedy heuristics handle the rest.
- **Join algorithms** — Nested loop (good for tiny inner tables), hash join (good for large equijoins), merge join (good when inputs are already sorted). The planner picks per join based on sizes and available orderings.
- **Predicate pushdown and other rewrites** — Logical rewrites applied before costing: push filters below joins, eliminate redundant subqueries, flatten views. These are "always win" transformations.
- **EXPLAIN and plan inspection** — `EXPLAIN` shows the chosen plan with cost estimates; `EXPLAIN ANALYZE` shows actual vs. estimated rows. Learning to read these is how you debug the optimizer rather than fight it.

## How it works

Parsing produces a logical plan tree of relational operators. The optimizer first applies heuristic rewrites (predicate pushdown, constant folding, subquery flattening). Then, using table statistics, it enumerates candidate physical plans: for each table, possible access paths (sequential scan, index scan, bitmap scan); for each join, possible algorithms and orders, explored with dynamic programming over subsets of tables. Each candidate gets a cost from the cost model (estimated rows × per-row CPU + page I/O), the cheapest overall plan wins, and it is compiled into an executable operator pipeline. When estimates are wrong — stale stats, correlated columns — the "optimal" plan can be badly wrong, which is why `ANALYZE` and plan inspection matter.

## Build milestones

1. Build a tiny executor first: table scan, filter, and nested-loop join operators over in-memory tables, driven by a hand-built plan tree.
2. Add a rule-based planner: parse simple `SELECT ... WHERE ...` (reuse the sql-parser topic), always push filters to the scan, and choose index scan when a usable B-tree index exists.
3. Implement table statistics (row counts, per-column histograms, most-common values) and a cost model; add `EXPLAIN` output showing estimated rows and costs.
4. Implement join ordering with System R-style dynamic programming over table subsets, plus hash join and merge join operators, and compare plans on 3–4 table joins.
5. Add `EXPLAIN ANALYZE` (actual vs. estimated rows), detect the worst misestimates, and implement one adaptive fix (e.g., re-plan a join when a build side is 10x larger than estimated).

## Best resources

- [SQLite Query Planner](https://sqlite.org/queryplanner.html) — SQLite's own documentation of its planner: join ordering, automatic indexes, and the "query planner stability guarantee". Short and excellent.
- [Architecture of a Database System — Hellerstein, Stonebraker, Hamilton](https://dsf.berkeley.edu/papers/fntdb07-architecture.pdf) — the classic survey; its query processing section is the standard mental model.
- [Apache Calcite](https://calcite.apache.org/) — the open-source, rules-based query planner (Volcano/Cascades style); reading its planner package teaches real optimizer architecture.
- [PostgreSQL: Planner Statistics](https://www.postgresql.org/docs/current/planner-stats.html) — how Postgres collects and uses statistics; pairs with `EXPLAIN` for hands-on learning.
- [The Internals of PostgreSQL — Hironobu Suzuki](https://www.interdb.jp/pg/index.html) — chapters on the planner/optimizer walk through paths, costs, and GEQO with internals-level detail.
- [Use The Index, Luke!](https://use-the-index-luke.com/) — the practitioner side: what the optimizer needs from you (sargable predicates, good stats) to pick good plans.

## Stretch ideas

- Implement genetic query optimization (like Postgres's GEQO) for 10+ table joins where dynamic programming explodes.
- Add column correlation statistics (multivariate stats) and show a query where they fix a catastrophic misestimate.
- Build a plan cache keyed by parameterized query shape and measure parse/plan vs. execution time.
