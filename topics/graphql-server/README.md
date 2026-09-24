---
title: "GraphQL Server"
category: "web-development"
difficulty: "intermediate"
tags: [graphql, api, server]
related: [rest-api-client, headless-cms, jwt-auth, query-planner-optimizer]
---

# GraphQL Server

A GraphQL server exposes a typed schema and executes client-specified queries against it, letting frontends ask for exactly the fields they need in one request. Building one — schema definition, query parsing, resolver execution — teaches the execution model (including the N+1 problem and how DataLoader fixes it) that makes GraphQL more than "REST with a query language".

## Core concepts

- **Schema Definition Language (SDL)** — The contract: `type Query { user(id: ID!): User }` declares types, fields, and arguments; it's both documentation and the source of validation.
- **Resolvers** — Functions `(parent, args, context, info) => value` attached to each field; the executor calls them top-down, passing each field's result as the next level's parent.
- **Query parsing and validation** — Incoming queries are parsed into an AST and validated against the schema (fields exist, types match, fragments valid) before any resolver runs.
- **The N+1 problem** — Naive resolvers fire one DB query per parent row (100 users → 100 post queries); the fix is batching all child loads for one level into a single query.
- **DataLoader** — The canonical batching/caching utility: collects all `load(id)` calls in a tick, dispatches one batched fetch, and caches by key for the request lifetime.
- **Mutations and input types** — Writes go through a `Mutation` type with `input` objects; they're executed serially (unlike parallel query fields) to keep writes predictable.
- **Subscriptions** — Real-time fields backed by async iterators, usually over WebSockets; the server pushes events to subscribed clients as they happen.
- **Introspection** — The schema can query itself (`__schema`, `__type`), which powers GraphiQL/Playground explorers and codegen — a free feature of spec compliance.

## How it works

1. The client POSTs `{ query, variables }` to `/graphql`; the server parses the query into an AST.
2. The AST is validated against the schema; invalid queries are rejected before touching data.
3. The executor walks the AST top-down, calling resolvers per field with `(parent, args, context)`, batching child loads through DataLoader.
4. Results assemble into the response JSON shape mirroring the query; errors are collected per-field (partial data + errors array) rather than failing the whole request.

## Build milestones

1. A `/graphql` endpoint that parses a tiny query subset and resolves hardcoded data from a schema object — the execution model in an evening.
2. Add full SDL parsing, query validation against the schema, and variables/arguments.
3. Add a real data source and demonstrate the N+1 problem, then fix it with a hand-rolled DataLoader.
4. Add mutations with input types, custom scalars (Date), and per-request context (auth user).
5. Add subscriptions over WebSocket and introspection support so GraphiQL works against your server.

## Best resources

- [GraphQL Spec](https://spec.graphql.org/) — the language, type system, and execution semantics, precisely defined.
- [Learn GraphQL — Queries](https://graphql.org/learn/queries/) — the official tutorial for the query language your server must implement.
- [graphql-js on GitHub](https://github.com/graphql/graphql-js) — the reference implementation; read its executor to see the algorithm.
- [Apollo Server docs](https://www.apollographql.com/docs/apollo-server/) — the production server's docs: resolvers, context, DataLoader patterns, subscriptions.
- [GraphQL over HTTP spec](https://graphql.github.io/graphql-over-http/) — the transport convention (POST shape, status codes) your endpoint should follow.

## Stretch ideas

- Implement query cost analysis and depth limiting to protect against malicious queries.
- Add persisted queries (query allow-listing by hash) for production hardening.
