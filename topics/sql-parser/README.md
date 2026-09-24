---
title: "SQL Parser"
category: "databases"
difficulty: "intermediate"
tags: [sql, parsing, compilers]
related: [recursive-descent-parser, query-planner-optimizer, formal-grammars-ebnf, repl-design]
---

# SQL Parser

A SQL parser turns the text `SELECT a FROM t WHERE x > 1` into a structured query tree the database can plan and execute. Building one teaches the front half of every database engine — and, since SQL's grammar is far more irregular than it looks, it teaches why real parsers are hand-written more often than generated.

## Core concepts

- **Lexer (tokenizer)** — The first pass that turns raw text into tokens: keywords, identifiers, string/number literals, operators, punctuation. SQL lexing has quirks like quoted identifiers (`"my col"`), escaped quotes in strings (`'it''s'`), and comments.
- **Grammar vs. reality** — SQL looks context-free, but details like the order of clauses, ambiguous `JOIN ... ON` vs. `WHERE`, and vendor dialects mean production parsers are usually hand-rolled recursive descent rather than generated from a clean grammar.
- **Abstract syntax tree (AST)** — The parser's output: nodes like `SelectStmt { columns, from, where, groupBy, orderBy, limit }` with expression trees for predicates. Everything downstream (planning, optimization) consumes this tree.
- **Expression parsing with precedence** — `a + b * c`, `NOT x AND y`, `BETWEEN`, `LIKE`, and function calls need a precedence-climbing or Pratt parser so operators bind correctly without grammar hacks.
- **Name resolution** — After parsing, bare identifiers like `a` must be bound to `t.a`: checking tables exist, resolving aliases, and rejecting ambiguous columns. This is the semantic pass that turns a parse tree into something executable.
- **Prepared statements and parameters** — Placeholders (`$1`, `?`) parsed once and executed many times with different values. This is what makes parsing cost amortizable and is the basis of the client/server protocol.
- **Error reporting** — A good parser reports `syntax error at or near "FROM", line 2` with position info instead of dying silently. Tracking line/column through the lexer is a small feature with outsized UX value.

## How it works

The lexer scans the query string left to right, emitting tokens and skipping whitespace and comments. The parser consumes tokens with a set of mutually recursive functions — one per grammar rule (`parseSelect`, `parseExpression`, `parseFromClause`) — each building AST nodes and expecting specific tokens next. Expressions are parsed with a precedence-climbing loop so `*` binds tighter than `+` and `AND` tighter than `OR`. A second pass walks the AST resolving names against the schema (tables, columns, aliases) and validating types of literals. The final AST — or a lowered, normalized form of it — is handed to the planner.

## Build milestones

1. Write a lexer for a SQL subset: keywords, identifiers, integers, strings with `''` escapes, operators, and `--`/`/* */` comments, tracking line and column.
2. Build a recursive-descent parser for `SELECT <cols> FROM <table> [WHERE <expr>] [ORDER BY ...] [LIMIT n]` with a precedence-climbing expression parser (`AND`/`OR`/`NOT`, comparisons, `+ - * /`, function calls).
3. Add `JOIN` (inner/left), `GROUP BY` with aggregates (`COUNT`, `SUM`, `AVG`), subqueries in `FROM`, and aliases — plus clear syntax error messages with positions.
4. Implement name resolution against a small in-memory catalog: qualify columns, detect ambiguous references and unknown tables, and type-check literals.
5. Add prepared statements (`PREPARE`/`EXECUTE` or `$1` parameters), parse once and bind values per execution, and fuzz the parser with random/adversarial inputs to harden it.

## Best resources

- [PostgreSQL: SQL Commands](https://www.postgresql.org/docs/current/sql-commands.html) — the reference grammar of real SQL; every clause's syntax is specified here.
- [The Internals of PostgreSQL — Hironobu Suzuki](https://www.interdb.jp/pg/index.html) — free, deep walkthrough of Postgres's parser, analyzer, and rewriter stages.
- [Apache Calcite](https://calcite.apache.org/) — a production SQL parser/planner framework in Java; its `SqlNode` AST and validator are the reference design for a serious parser.
- [SQLite documentation](https://sqlite.org/docs.html) — SQLite's docs include its grammar diagrams and the famously readable Lemon parser generator it uses.
- [CMU 15-445/645 Intro to Database Systems](https://15445.courses.cs.cmu.edu/) — covers SQL processing from parsing through planning with lecture slides.
- [SQL (Wikipedia)](https://en.wikipedia.org/wiki/SQL) — history and scope of the language; useful context for why dialects diverge.

## Stretch ideas

- Add a `EXPLAIN` mode that pretty-prints the AST, so you can see exactly what the parser understood.
- Implement a second dialect (e.g., MySQL backticks vs. Postgres double quotes) behind a dialect flag and diff the grammars.
- Write a SQL formatter/linter on top of the AST that normalizes capitalization and indentation.
