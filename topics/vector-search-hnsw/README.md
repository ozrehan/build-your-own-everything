---
title: "HNSW Vector Search"
category: "ai-ml"
difficulty: "advanced"
tags: [vector-search, hnsw, ann]
related: [rag-pipeline, embeddings-visualizer, vector-database]
---

# HNSW Vector Search

Exact nearest-neighbor search over millions of high-dimensional vectors is too slow for production, so systems use approximate search — and HNSW (Hierarchical Navigable Small World) is the algorithm that won. Implementing it yourself teaches the graph-navigation trick that powers FAISS, Pinecone, and every vector database.

## Core concepts

- **The curse of dimensionality** — In high dimensions, distances concentrate and tree-based indexes (kd-trees) degrade to linear scan. ANN algorithms accept slightly-wrong answers to buy back logarithmic-ish query time.
- **Navigable small world graphs** — HNSW builds a graph where each vector links to nearby neighbors plus a few long-range links. Greedy routing ("move to the neighbor closest to the query") then converges in few hops, like navigating a social network by degrees of separation.
- **Hierarchy of layers** — Vectors are inserted into multiple layers: sparse upper layers with long jumps for coarse navigation, a dense bottom layer for fine search. Queries descend from the top, zooming in at each level — the same idea as zooming into a map.
- **efConstruction / efSearch** — The two master knobs. `efConstruction` is the candidate-list size during index building (quality of the graph); `efSearch` is the candidate-list size at query time (recall vs latency). Tuning them is the whole performance game.
- **Recall vs QPS tradeoff** — ANN is never free: you trade a few percent of recall for 10–100× the queries per second. Benchmarking your index means plotting this curve, not quoting a single number.
- **Distance metrics** — Cosine, Euclidean, and inner product behave differently under normalization. Most embedding pipelines L2-normalize vectors so cosine becomes a dot product — one less thing to get wrong.

## How it works

Insertion: for a new vector, start at the top layer's entry point and greedily walk to the nearest node, then descend a layer and repeat, refining the candidate set at each level. At the bottom layer, connect the vector bidirectionally to its M nearest neighbors (pruning with a diversity heuristic so links spread in different directions rather than clustering). Search: same top-down descent, but at the bottom layer run a best-first beam search with a candidate list of size `efSearch`, returning the closest k. Deletion and updates are the hard parts production systems wrestle with — your build can start append-only.

## Build milestones

1. Implement brute-force k-NN with cosine similarity; benchmark it on 100k vectors to feel why ANN is necessary.
2. Build a single-layer NSW graph: greedy insertion, greedy search; measure recall@k against brute force.
3. Add the hierarchy (layer assignment, top-down descent) to complete HNSW; verify recall ≥ 95% with sub-millisecond queries.
4. Expose `efConstruction`/`efSearch`/`M` as parameters; plot the recall-vs-QPS frontier by sweeping them.
5. Benchmark against FAISS or hnswlib on the same dataset; then add batched queries and a simple persistence format.

## Best resources

- [Efficient and robust approximate nearest neighbor search using HNSW graphs](https://arxiv.org/abs/1603.09320) — The Malkov & Yashunin paper; the algorithm description is complete enough to implement from.
- [hnswlib](https://github.com/nmslib/hnswlib) — The reference C++/Python implementation; compare your graph structure and recall curves against it.
- [FAISS](https://github.com/facebookresearch/faiss) — Meta's vector search library; the production-grade alternative with GPU support and many index types.
- [ANN-Benchmarks](https://github.com/erikbern/ann-benchmarks) — The standard benchmarking harness; run it to see where your implementation lands on real datasets.
- [Nearest neighbor search (Wikipedia)](https://en.wikipedia.org/wiki/Nearest_neighbor_search) — Solid background on exact methods and why they break in high dimensions.

## Stretch ideas

- Implement product quantization (PQ) for compressed storage and compare memory-vs-recall against your pure HNSW.
- Add filtered search (metadata predicates combined with vector search), the feature that separates toy indexes from real ones.
