---
title: "Columnar Storage Format"
category: "databases"
difficulty: "intermediate"
tags: [analytics, compression, file-formats]
related: [olap-cube, query-planner-optimizer, mapreduce-mini, etl-pipeline]
---

# Columnar Storage Format

Columnar formats (Parquet, Arrow) store each column contiguously instead of each row, so an analytical query reading 2 of 50 columns touches a fraction of the data. Building one teaches why analytics engines are 10–100x faster than row stores on scans — and the encoding tricks that make it possible.

## Core concepts

- **Columnar vs. row layout** — OLTP reads whole rows; OLAP reads few columns over many rows. Storing columns contiguously means a `SELECT avg(price)` never touches the other 49 columns — less I/O, better cache use.
- **Run-length encoding (RLE)** — Sorted or low-cardinality columns compress to (value, run length) pairs. A `country` column with 200 distinct values over a billion rows nearly vanishes.
- **Dictionary encoding** — Map each distinct value to a small integer id once, then store ids. Strings become ints; equality and grouping operate on the ids directly.
- **Bit packing and delta encoding** — Store integers in the minimum bits needed (bit packing), or store differences from a base/previous value (delta). Timestamps and ids shrink dramatically.
- **Row groups and statistics** — Files are split into row groups, each with per-column min/max/null counts. Query engines skip entire row groups whose stats can't match the filter — "predicate pushdown" at the file level.
- **Nested data without joins** — Parquet's Dremel-derived repetition/definition levels encode nested/repeated fields (lists, structs) in columns, so JSON-like data stays columnar.
- **Arrow vs. Parquet** — Parquet is the on-disk archival format (compressed, encoded); Arrow is the in-memory interchange format (ready to compute on, zero-copy between processes). Engines convert between them.

## How it works

A writer buffers rows into a row group (e.g., 128 MB), then encodes each column independently: pick dictionary encoding for strings, delta + bit packing for integers/timestamps, RLE where runs exist — recording the chosen encoding per column chunk. It writes per-column statistics (min, max) into the file footer alongside the schema. A reader opens the footer, prunes row groups using min/max stats against the query's filters, then reads only the needed column chunks, decoding them into Arrow-style columnar batches that vectorized execution engines process with SIMD-friendly loops. The whole design is one idea applied everywhere: never read, decompress, or decode data the query doesn't need.

## Build milestones

1. Write a minimal columnar file: schema + one encoding (plain), row groups, and a reader that projects a subset of columns; benchmark a 2-of-20-column scan vs. a CSV row scan.
2. Add dictionary encoding for strings and delta + bit-packed encoding for integers; measure compression ratio and decode speed on realistic data.
3. Add per-row-group min/max statistics and predicate pushdown: skip row groups that can't match `WHERE` filters, and show the I/O savings.
4. Implement nested data with repetition/definition levels (Dremel-style) so a column can hold lists of structs; round-trip JSON documents through it.
5. Add an Arrow-compatible in-memory batch layer and a vectorized `SUM`/`GROUP BY` that operates on encoded batches; compare against your row-based executor from the query-planner-optimizer topic.

## Best resources

- [Apache Parquet](https://parquet.apache.org/) — the format spec, encodings, and the Java/C++ implementations; the reference for on-disk columnar.
- [Apache Arrow](https://arrow.apache.org/) — the in-memory columnar standard: memory layout spec and zero-copy interchange.
- [Dremel: Interactive Analysis of Web-Scale Datasets (Google Research)](https://research.google/pubs/dremel-interactive-analysis-of-web-scale-datasets/) — the paper that introduced columnar nested storage and repetition/definition levels.
- [DuckDB documentation](https://duckdb.org/docs) — DuckDB is the embodiment of vectorized columnar execution; its docs explain the execution side of the format.
- [Column-oriented DBMS (Wikipedia)](https://en.wikipedia.org/wiki/Column-oriented_DBMS) — history from MonetDB and C-Store to the modern lakehouse.
- [CMU 15-445/645 Intro to Database Systems](https://15445.courses.cs.cmu.edu/) — lectures on columnar storage, compression schemes, and vectorized execution.

## Stretch ideas

- Implement late materialization: carry (row-group, position) tuples through filters and only decode full columns for surviving rows.
- Add zone maps / bloom filters per row group and measure selective-query speedup on skewed data.
- Build a Parquet-to-Arrow zero-copy path and benchmark against a naive decode loop.
