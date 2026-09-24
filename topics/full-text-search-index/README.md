---
title: "Full-Text Search Index"
category: "databases"
difficulty: "intermediate"
tags: [search, indexing, text-processing]
related: [search-ranking-tfidf, b-tree-index, secondary-indexing, mapreduce-mini]
---

# Full-Text Search Index

A full-text index is what turns "find documents containing *these words*" from a hopeless table scan into a millisecond query — it's the core of every search box, from Postgres `tsvector` to Elasticsearch. Building one teaches inverted indexes, the data structure that made web search possible.

## Core concepts

- **Inverted index** — Instead of mapping documents to their words, map each word to the list of documents containing it (the *postings list*). A query becomes: look up each term, intersect the lists.
- **Tokenization and normalization** — Splitting text into terms is half the battle: case folding, punctuation, stemming ("running" → "run"), stop-word removal ("the", "and"). The analyzer you choose determines what queries can match.
- **Postings lists with positions** — Storing not just document ids but term positions enables phrase queries ("quick brown fox" as consecutive words) and proximity ranking.
- **Document frequency and IDF** — A term appearing in 3 of 1M documents is far more discriminating than one in 900k. Inverse document frequency turns that intuition into a ranking weight.
- **TF-IDF / BM25 ranking** — Term frequency (how often in this doc) × IDF (how rare overall), with BM25 adding length normalization and saturation. BM25 is still the default ranker nearly everywhere.
- **Segment-based indexing** — Like an LSM-tree, real search engines buffer documents in memory, flush immutable segments to disk, and merge them in the background. Lucene's segments are the direct ancestor of this design.
- **Deletes and updates** — Segments are immutable, so deletes are just tombstone markers checked at query time; the document physically disappears during a segment merge.

## How it works

At index time, each document passes through an analyzer (tokenizer → lowercase → stemmer → stop-word filter) producing a stream of terms with positions. The engine appends the document id to each term's postings list in an in-memory buffer; when the buffer fills, it is flushed as an immutable sorted segment containing a term dictionary (itself often an FST or B-tree for prefix lookup) plus postings. At query time, the query is analyzed the same way, each term's postings list is fetched, the lists are intersected (for AND) or unioned (for OR) with a merge join, and surviving documents are scored with BM25 using term frequencies and precomputed document statistics. Background merges keep the segment count — and thus the number of lists to merge per query — bounded.

## Build milestones

1. Build the core: an analyzer (tokenize, lowercase, simple stemmer) and an in-memory inverted index mapping term → sorted doc-id list; support AND/OR queries via list merge.
2. Add phrase queries and proximity search by storing term positions in postings; add a tiny query parser for `"quoted phrases"` and `field:term` syntax.
3. Implement BM25 ranking with document-length normalization, and evaluate result quality on a small corpus (e.g., a few thousand Wikipedia articles) with hand-judged queries.
4. Make it persistent and segment-based: flush immutable segments to disk, merge them in the background, support deletes via tombstones.
5. Add faceted filtering (filter by metadata before ranking), prefix/autocomplete queries via the term dictionary, and benchmark index size and query latency vs. a Postgres `tsvector` GIN index.

## Best resources

- [Inverted index (Wikipedia)](https://en.wikipedia.org/wiki/Inverted_index) — the data structure itself: postings, compression, and query processing.
- [Apache Lucene documentation](https://lucene.apache.org/core/documentation.html) — the engine under Elasticsearch/Solr; the docs explain segments, postings formats, and scoring.
- [Tantivy](https://github.com/quickwit-oss/tantivy) — a full search engine in Rust modeled on Lucene; small enough to read and learn the segment architecture from.
- [PostgreSQL: Full Text Search](https://www.postgresql.org/docs/current/textsearch-intro.html) — `tsvector`, `tsquery`, and GIN indexes: how a relational database does text search natively.
- [Database Internals — Alex Petrov](https://www.databass.dev/) — covers index structures including the LSM/inverted-index family with implementation detail.
- [Elastic (Elasticsearch docs)](https://www.elastic.co/) — the production reference for analyzers, mappings, and distributed search behavior.

## Stretch ideas

- Implement index-time synonyms and query-time spell correction (edit-distance over the term dictionary).
- Add distributed search: shard the index, scatter queries, gather and merge top-k results across shards.
- Build hybrid search: combine BM25 scores with vector similarity (see vector-database) via reciprocal rank fusion.
