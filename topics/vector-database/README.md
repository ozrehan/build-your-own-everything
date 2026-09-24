---
title: "Vector Database"
category: "databases"
difficulty: "advanced"
tags: [embeddings, ann-search, rag]
related: [vector-search-hnsw, embeddings-visualizer, rag-pipeline, columnar-storage-format]
---

# Vector Database

A vector database stores ML embeddings and answers "find the 10 most similar items" over millions of high-dimensional vectors in milliseconds — the memory layer behind RAG and semantic search. Building one teaches approximate nearest neighbor (ANN) search, the algorithms that make similarity search possible at scale.

## Core concepts

- **Embeddings as coordinates** — Text, images, and audio become dense vectors (e.g., 768 floats) where distance ≈ semantic similarity. The database doesn't understand meaning; it just does geometry very fast.
- **Distance metrics** — Cosine similarity (angle, for normalized embeddings), Euclidean (L2), dot product. The metric must match what the embedding model was trained with, or results silently degrade.
- **The curse of dimensionality** — In high dimensions, exact nearest-neighbor search degenerates to brute force: tree indexes collapse. This is why *approximate* search (ANN) with tunable recall exists.
- **HNSW graphs** — Hierarchical Navigable Small World: a multi-layer graph where greedy routing zooms from coarse to fine layers. The dominant ANN index — fast queries, high recall, incremental inserts.
- **IVF + Product Quantization** — Inverted File partitions vectors into clusters (search only nearby clusters); Product Quantization compresses each vector to ~tens of bytes. The Faiss recipe for billion-scale search on one machine.
- **Recall vs. latency tradeoff** — ANN parameters (HNSW's `ef_search`, IVF's `nprobe`) trade result quality for speed. Benchmarking recall@k against brute force is how you tune honestly.
- **Hybrid search** — Real systems combine vector similarity with metadata filters and keyword (BM25) scores. Pre-filtering vs. post-filtering changes both index design and result quality.

## How it works

At insert time, each vector is added to the ANN index: in HNSW, the new node is linked into each layer by greedy search for its nearest neighbors, with a cap on connections per node (the `M` parameter) keeping the graph sparse. The raw vectors (or their quantized codes) plus payload metadata are stored alongside. At query time, the query embedding enters the top layer and greedily walks toward the query, descending layer by layer, maintaining a dynamic candidate list of size `ef_search`; the best k are returned with distances. Metadata filters are applied either before the graph walk (pre-filtering, needs filter-aware traversal) or after (post-filtering, risks returning fewer than k). For scale, IVF variants first find the nearest coarse centroids, then scan only those partitions — optionally against product-quantized codes for memory efficiency.

## Build milestones

1. Build brute-force search over normalized embeddings (cosine via dot product) with a NumPy backend; benchmark queries/sec at 100k vectors and establish your recall baseline (100% by definition).
2. Implement HNSW from scratch: layered graph construction, greedy search with candidate lists, `M` and `ef_construction` parameters; verify recall@10 ≥ 0.95 vs. brute force.
3. Add persistence (serialize the graph + vectors), deletes via tombstones, and metadata payloads with pre/post-filtering options.
4. Implement IVF + product quantization as a second index type; benchmark memory (bytes/vector) and recall/latency against HNSW on 1M vectors.
5. Build a RAG demo: chunk documents, embed with a real model, store in your index, and answer questions with retrieved context; add hybrid BM25 + vector ranking.

## Best resources

- [Vector database (Wikipedia)](https://en.wikipedia.org/wiki/Vector_database) — the concept map: ANN techniques (HNSW, LSH, PQ), use cases, and hybrid retrieval.
- [Efficient and robust approximate nearest neighbor search using Hierarchical Navigable Small World graphs (Malkov & Yashunin)](https://arxiv.org/abs/1603.09320) — the HNSW paper; the algorithm spec you'll implement from.
- [Faiss](https://github.com/facebookresearch/faiss) — Meta's ANN library; the reference implementations of IVF, PQ, and HNSW plus honest benchmarks.
- [Annoy](https://github.com/spotify/annoy) — Spotify's small, readable ANN library (random projection trees); the gentlest real codebase to study.
- [Qdrant documentation](https://qdrant.tech/documentation/) — a production vector database's docs: HNSW tuning, quantization, filtering, and distributed mode.
- [Database Internals — Alex Petrov](https://www.databass.dev/) — indexing fundamentals that transfer: the tradeoff thinking behind every ANN structure.

## Stretch ideas

- Implement DISKANN-style graph search over SSD-resident vectors to scale past RAM.
- Add incremental re-embedding: detect stale vectors when the embedding model version changes and reindex in the background.
- Build a benchmark harness (recall@k vs. QPS vs. memory) and publish results comparing your HNSW against Faiss.
