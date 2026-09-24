---
title: "ETL Pipeline"
category: "distributed-data"
difficulty: "beginner"
tags: [etl, data-pipeline, data-engineering]
related: [stream-processor, data-lake-layout, mapreduce-mini]
---

# ETL Pipeline

Raw data is never in the shape you need: APIs return nested JSON, timestamps come in five formats, half the rows are malformed. ETL — Extract, Transform, Load — is the disciplined pipeline that turns messy sources into clean, queryable tables. Building one teaches you the unglamorous core of data engineering: idempotency, schema drift, and making failures cheap.

## Core concepts

- **Extract** — Pulling data out of source systems: API pagination, database snapshots, file drops, log tails. Extraction must be incremental where possible (only new/changed rows) or every run reprocesses the world.
- **Transform** — Cleaning, joining, and reshaping: parsing dates, normalizing currencies, deduplicating, joining user IDs to a dimension table. This is where business logic lives — and where most pipeline bugs hide.
- **Load** — Writing results into the destination (warehouse table, data lake partition) in a way that doesn't corrupt it if the job dies halfway — usually write-to-temp-then-swap, or idempotent upserts.
- **Idempotency** — Running the same pipeline twice must not double-count. Design each step so re-execution is safe: keyed upserts, deterministic output paths, or "delete the day's partition, then rewrite it."
- **Schema drift** — Sources change: a new column appears, a field flips from int to string. A robust pipeline detects unexpected schema changes, quarantines bad rows, and alerts instead of silently loading garbage.
- **Orchestration / DAG** — Pipelines are directed acyclic graphs of tasks with dependencies ("transform can't run until both extracts finish"). The orchestrator schedules, retries, and backfills — Airflow is the canonical example.
- **ELT vs ETL** — Modern warehouses are powerful enough that many teams Load raw data first, then Transform inside the warehouse with SQL (dbt's model). The letters moved, but the problems — idempotency, drift, testing — didn't.

## How it works

A scheduler triggers the pipeline on a cadence (hourly, daily). The extract step pulls each source incrementally — e.g. "orders API, everything since last successful watermark" — and lands raw files in a staging area, untouched. Transform jobs read the staged data, apply cleaning and business rules (each as a testable function), and write validated output to a temporary location; a data-quality gate checks row counts, null rates, and schema conformance, quarantining violations. Only if every check passes does the load step atomically swap the new partition into the production table (or upsert by key), then advance the watermark. If anything fails, the production table is untouched and the next run retries from the last good watermark.

## Build milestones

1. Build a one-shot script: fetch JSON from a public API, flatten/normalize it, and load it into SQLite — the whole ETL in 50 lines.
2. Make it incremental and idempotent: track a watermark (e.g. max timestamp loaded), fetch only newer records, and prove that re-running changes nothing.
3. Add data-quality gates: schema validation on every batch, quarantine bad rows to a separate table with the error reason, and fail loudly (not silently) on unexpected schema changes.
4. Add orchestration: split the pipeline into extract → transform → load tasks with dependencies, retries with backoff, and a daily schedule — first with cron, then with a real DAG runner.
5. Impressive end state: a pipeline over 3+ messy sources (API + CSV dump + database) with incremental loads, quality gates, quarantine, backfill support ("reprocess March"), and a status page showing each run's row counts and duration.

## Best resources

- [Extract, transform, load — Wikipedia](https://en.wikipedia.org/wiki/Extract,_transform,_load) — The concepts, the history, and how ETL relates to ELT and data virtualization.
- [Apache Airflow](https://airflow.apache.org/) — The standard open-source orchestrator; its tutorial teaches DAG thinking, which transfers to every other runner.
- [dbt](https://www.getdbt.com/) — The "T in ELT" done right: SQL-based transforms with testing, documentation, and version control built in.
- [Apache Spark](https://spark.apache.org/) — The engine most heavy transforms run on; its docs show how the transform step scales when the data outgrows one machine.

## Stretch ideas

- Implement slowly-changing dimensions: track how a customer's address history evolves instead of overwriting it (SCD Type 2).
- Add data lineage: record which source rows produced which output rows, so you can answer "why is this number wrong?" by tracing backwards.
