---
title: "Search Ranking (TF-IDF)"
category: "distributed-data"
difficulty: "beginner"
tags: [search, ranking, information-retrieval]
related: [full-text-search-index, mapreduce-mini, vector-database]
---

# Search Ranking (TF-IDF)

Type "jaguar" into a search box and the car should beat the animal — if that's what the corpus suggests. TF-IDF is the classic ranking formula behind that judgment: words that appear often in a document but rarely in the collection are the most discriminating. Building it teaches you the foundation every modern ranker (including BM25 and neural search) is built on.

## Core concepts

- **Term frequency (TF)** — How often a term appears in a document. More mentions suggest more relevance — but with diminishing returns, which is why raw counts are usually log-scaled (10 mentions isn't 10× more relevant than 1).
- **Document frequency (DF)** — In how many documents the term appears. "The" appears everywhere and tells you nothing; "arachnocentric" appears in one document and tells you everything.
- **Inverse document frequency (IDF)** — `log(N / DF)`: the rarity weight. Terms in every document get IDF near zero (stop words, effectively); terms in few documents get high weight. The log dampens the effect so one rare term doesn't dominate absolutely.
- **TF-IDF weight** — `TF × IDF` per term per document: high when the term is frequent in this document but rare overall. Each document becomes a vector of these weights, one dimension per vocabulary term.
- **Vector space model** — Documents and queries are both vectors in term space; relevance is the cosine of the angle between them. Cosine normalizes for document length, so long documents don't win just by containing more words.
- **Inverted index** — The data structure that makes it fast: term → list of (document, TF) postings. At query time you only score documents containing query terms instead of scanning the corpus.
- **BM25** — TF-IDF's successor and the default in Lucene/Elasticsearch: adds saturation on term frequency and explicit document-length normalization with tunable parameters. Learn TF-IDF first and BM25 is a small, well-motivated step.

## How it works

At index time, tokenize every document (lowercase, split on non-letters, drop stop words, optionally stem), count term frequencies per document, and build the inverted index plus document frequencies. At query time, tokenize the query the same way, compute IDF for each query term from the collection stats, and for each document containing any query term compute the score: the sum over query terms of `TF-IDF(term, doc)`, often as a cosine similarity against the query vector. Sort documents by score descending and return the top K. The whole thing is a few dozen lines once the inverted index exists — the insight is entirely in the weighting.

## Build milestones

1. Build the indexer: tokenize a folder of text documents, compute term frequencies, and store an inverted index (term → list of doc IDs with counts).
2. Add IDF and scoring: implement `TF × log(N/DF)`, score every document for a query, and return ranked results — test with an obvious query ("which document is about X?").
3. Add cosine normalization: divide by document vector length and watch long documents stop dominating the rankings unfairly.
4. Add log-scaled TF and stop-word removal; compare rankings before/after on a set of test queries to see the quality difference.
5. Impressive end state: index a real corpus (e.g. a few thousand Wikipedia articles or Project Gutenberg books), build a tiny web UI with highlighted matching terms, and evaluate with a handful of hand-judged queries — then implement BM25 and A/B the two rankers.

## Best resources

- [Tf-idf weighting — Stanford IR Book](http://nlp.stanford.edu/IR-book/html/htmledition/tf-idf-weighting-1.html) — The textbook derivation: why TF is log-scaled, why IDF is logarithmic, and how they combine, with worked examples.
- [Introduction to Information Retrieval — Stanford](https://nlp.stanford.edu/IR-book/) — The full free textbook; chapters 6–7 take you from TF-IDF through the vector space model to evaluation.
- [Apache Lucene](https://lucene.apache.org/) — The library behind Elasticsearch/Solr; its similarity classes show how TF-IDF evolved into BM25 in production code.
- [Elastic](https://www.elastic.co/) — Elasticsearch's relevance documentation explains how these formulas behave at scale, with practical tuning guidance.

## Stretch ideas

- Implement BM25 with tunable k1 and b parameters, and grid-search them against your judged queries.
- Add phrase queries and proximity scoring ("terms near each other rank higher") using positional postings in your index.
