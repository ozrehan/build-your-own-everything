---
title: "Data Lake Layout"
category: "distributed-data"
difficulty: "intermediate"
tags: [data-lake, storage, parquet]
related: [etl-pipeline, columnar-storage-format, olap-cube]
---

# Data Lake Layout

Dump raw files into cloud storage and you have a data swamp; organize them with partitions, formats, and table metadata and you have a data lake that thousands of queries can share. Building the layout layer teaches you why "just files" isn't enough — and how modern table formats bring database guarantees to cheap object storage.

## Core concepts

- **Zones: bronze / silver / gold** — The medallion architecture: bronze holds raw ingested data (immutable, as-arrived), silver holds cleaned and validated tables, gold holds business-ready aggregates. Each zone has different consumers, SLAs, and retention.
- **Partitioning** — Organizing files by column values in the path (`year=2025/month=09/day=24/`): queries reading one day skip all other files (partition pruning). The most impactful physical-design decision in a lake; choose low-cardinality columns or you get a million tiny files.
- **File formats: Parquet / ORC** — Columnar formats with compression, encoding, and per-column statistics (min/max). A query reading 2 of 50 columns touches a fraction of the bytes — the reason lakes are queryable at all.
- **Small-files problem** — Thousands of tiny files murder query performance (each needs listing, opening, metadata). Compaction jobs merge them; good ingestion writes reasonably sized files (128MB–1GB) in the first place.
- **Table formats: Delta / Iceberg / Hudi** — A metadata layer over the files providing ACID transactions, schema evolution, time travel, and partition evolution on object storage. This is what turns "files in S3" into an actual table.
- **Manifest-based reads** — Instead of listing directories (slow, inconsistent), the table format keeps a manifest of exactly which files belong to the current snapshot. Readers get a consistent view; writers commit by swapping manifests atomically.
- **Schema evolution** — Real schemas change: add columns, widen types, rename. Table formats record the evolution so old files (without the new column) and new files coexist, and readers see one coherent schema.

## How it works

Ingestion lands raw files in the bronze zone, partitioned by arrival time. A processing job validates and converts them to Parquet in the silver zone, partitioned by business-meaningful columns (date, region), compacting small files as it goes. A table format (say Delta Lake) tracks each table as a transaction log: every write appends a JSON log entry listing added/removed files, so a "table version" is just a log position. Readers resolve the latest (or any historical) version, prune partitions using the log's statistics, and read only the needed Parquet files and columns. Schema changes are recorded in the log; time travel is reading an older log position. Compaction, vacuuming old files, and partition management run as maintenance jobs — the lake stays fast because something actively tends it.

## Build milestones

1. Build the zone layout: a script that ingests messy CSV/JSON into `bronze/` (raw, immutable), cleans it into `silver/` Parquet partitioned by date, and publishes aggregates to `gold/` — with a README describing the contract of each zone.
2. Add partition pruning: write a reader that, given a date-range predicate, lists only the relevant partition directories and measures the I/O saved vs a full scan.
3. Implement a mini table format: a JSON transaction log per table recording (added files, removed files, schema version) per commit; readers resolve a snapshot from the log instead of directory listing.
4. Add time travel and schema evolution: query the table "as of last Tuesday," add a column mid-stream, and show old and new files reading through one schema.
5. Impressive end state: a lake with 3 zones, 10M+ rows, partitioned Parquet, your table-format transaction log, a SQL-ish query CLI with partition pruning and time travel, and a maintenance job (compaction + vacuum) — benchmarked against naive "pile of CSVs" on the same queries.

## Best resources

- [Data lakehouse — Databricks glossary](https://www.databricks.com/glossary/data-lakehouse) — The clearest explanation of why lakes grew table formats and became "lakehouses."
- [Delta Lake](https://delta.io/) — The transaction-log-over-Parquet design your mini table format imitates; its docs explain the log protocol concretely.
- [Apache Iceberg](https://iceberg.apache.org/) — The other major table format; its spec docs are excellent on manifest-based reads, partition evolution, and hidden partitioning.
- [Data lake — Wikipedia](https://en.wikipedia.org/wiki/Data_lake) — The concept's history, the "data swamp" failure mode, and how lakes relate to warehouses.

## Stretch ideas

- Implement hidden partitioning (Iceberg-style): let users query `WHERE event_date = ...` while the engine transparently maps it to the physical partition layout, so layouts can evolve without rewriting queries.
- Add a data-quality layer: Great-Expectations-style checks that quarantine bad batches to a `_quarantine` zone before they reach silver.
