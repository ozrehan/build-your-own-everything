---
title: "Graph Database"
category: "databases"
difficulty: "intermediate"
tags: [graph, query-language, traversals]
related: [document-store, secondary-indexing, query-planner-optimizer, vector-database]
---

# Graph Database

A graph database stores entities as nodes and their relationships as first-class edges, so "friends of friends who bought X" is a traversal instead of a pile of joins. Building one teaches index-free adjacency — the physical layout trick that makes multi-hop queries fast.

## Core concepts

- **Property graph model** — Nodes and edges both carry labels and key/value properties (e.g., `(:Person {name: "Asha"})-[:KNOWS {since: 2020}]->(:Person)`). This is the model behind Neo4j/Cypher and the practical standard.
- **Index-free adjacency** — Each node physically stores direct pointers to its incident edges, so traversing a relationship is a pointer hop, not an index lookup. Multi-hop queries cost proportional to the traversed subgraph, not the database size.
- **Adjacency lists vs. matrices** — Sparse real-world graphs use adjacency lists (per-node edge lists); the layout choice determines cache behavior during traversals and is the first physical-design decision.
- **Traversal algorithms** — Breadth-first and depth-first search over the stored graph, with cycle detection via visited sets. Every graph query language compiles down to traversals with filters.
- **Cypher / pattern matching** — Declarative patterns like `(a:Person)-[:KNOWS*1..3]->(b)` describe the shape to find; the engine plans join order over pattern parts just like a relational optimizer plans table joins.
- **Supernodes** — A celebrity node with millions of edges breaks traversal assumptions and statistics. Real systems need degree-aware planning (expand from the low-degree side first) or special handling.
- **Graph vs. relational vs. document** — Graphs win on deep, relationship-heavy queries; they lose on bulk aggregations over whole datasets, where columnar/relational engines dominate. Knowing which workload you have is the design decision.

## How it works

Nodes and edges are stored as fixed-size records; each node record holds a pointer to the head of its edge list, and each edge record points to its start/end nodes plus next-edge pointers in both nodes' lists — a doubly-linked structure on disk. A query like "friends of friends" parses a pattern, plans an expansion order (usually starting from the most selective node label/property, using an index), then walks adjacency pointers hop by hop, filtering on properties and tracking visited nodes to avoid cycles. Aggregations and ordering happen after the traversal materializes the matched subgraph. Writes append node/edge records and splice them into the adjacency lists inside a transaction.

## Build milestones

1. Build the storage: node/edge records with properties in files, adjacency via edge lists per node; support create node, create edge, and 1-hop neighbor listing.
2. Implement BFS/DFS traversals with depth limits, cycle detection, and property filters; benchmark "friends of friends" vs. the equivalent SQL joins on generated data.
3. Add a tiny Cypher subset parser (`MATCH (a:Label)-[:REL]->(b) WHERE ... RETURN ...`) that compiles patterns to traversal plans.
4. Add label/property indexes for selective starting points and a cost-based choice of which pattern node to expand first (degree statistics).
5. Add variable-length paths (`*1..3`), shortest-path queries (BFS/Dijkstra), and ACID transactions over graph mutations.

## Best resources

- [Graph database (Wikipedia)](https://en.wikipedia.org/wiki/Graph_database) — models, history, and how graph stores differ from relational/document systems.
- [Neo4j documentation](https://neo4j.com/docs/) — Cypher manual, internals on native graph storage, and index-free adjacency explained by the reference implementation.
- [Apache TinkerPop](https://tinkerpop.apache.org/) — the Gremlin traversal language and the graph-computing framework; great for understanding traversals as composable steps.
- [Graph Databases (book) — Robinson, Webber, Eifrem](https://neo4j.com/graph-databases-book/) — the free O'Reilly book: modeling, Cypher, and internals chapters.
- [Database Internals — Alex Petrov](https://www.databass.dev/) — storage and indexing fundamentals that transfer to graph record layouts.
- [CMU 15-445/645 Intro to Database Systems](https://15445.courses.cs.cmu.edu/) — query planning concepts that apply directly to pattern-match planning.

## Stretch ideas

- Implement a Pregel-style bulk-synchronous-parallel engine (PageRank, connected components) over your graph files.
- Add full-text indexes on node properties and hybrid queries ("people named *ash* within 2 hops of X").
- Build a visual graph explorer: render query results as an interactive node-link diagram in the browser.
