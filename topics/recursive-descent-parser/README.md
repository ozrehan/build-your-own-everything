---
title: "Build Your Own Recursive-Descent Parser"
category: "programming-languages"
difficulty: "beginner"
tags: [parsing, grammars, compilers]
related: [parser-combinators, formal-grammars-ebnf, tree-walking-interpreter]
---

# Build Your Own Recursive-Descent Parser

A recursive-descent parser turns a stream of tokens into a syntax tree using one function per grammar rule — `parseExpression()` calls `parseTerm()` which calls `parseFactor()`, mirroring the grammar itself. It is the parser architecture behind GCC, V8, and countless hand-written language front ends, because the code reads like the grammar and debugging means reading a stack trace. If you can write a grammar in EBNF, you can write a recursive-descent parser for it in an afternoon.

## Core concepts

- **One function per nonterminal** — each grammar rule becomes a function; recursion in the grammar becomes recursion in the code, so the parser's shape mirrors the language's shape.
- **Lookahead and predictive parsing** — peeking at the next token (LL(1)/LL(k)) decides which production to take without backtracking; most hand-written parsers are predictive.
- **Left recursion is forbidden** — a rule like `expr → expr "+" term` would recurse forever; rewrite it as iteration, or handle operators with precedence climbing.
- **Precedence climbing / Pratt parsing** — binary operators at different precedence levels fold into layered functions (or a precedence table) instead of one grammar rule per level.
- **Error recovery** — on an unexpected token, synchronize: skip to a known boundary (a semicolon, a closing brace) and keep parsing, so one typo doesn't hide the next error.
- **The AST is the output** — parsing functions return node objects, not just accept/reject verdicts; the tree they build is the parser's real product.

## How it works

A lexer first converts characters to tokens. The parser holds the token stream with a one-token lookahead: helper functions like `match()` consume an expected token or raise a parse error, and each `parseX()` function implements one grammar rule by calling the functions for the rules it references. Expressions are the interesting case — instead of a rule per precedence level, precedence climbing loops: parse a primary, then while the next token is a binary operator at sufficient precedence, consume it and parse the right-hand side. When an error occurs, the parser reports line and column, then skips tokens until a synchronization point so a single file can yield multiple diagnostics.

## Build milestones

1. Write a lexer for a tiny expression language (numbers, operators, parentheses) and a parser that produces a tree you can pretty-print.
2. Implement a full expression grammar with precedence (`+`, `-`, `*`, `/`, unary minus, parentheses) via layered functions or Pratt parsing.
3. Add statements — assignment, `if`/`while`, blocks — with AST nodes for each.
4. Produce error messages with line and column info, plus synchronization that reports multiple errors per file instead of bailing on the first.
5. Parse a real subset (JSON, or the Lox grammar) and feed the resulting tree into an evaluator.

## Best resources

- [Recursive descent parser (Wikipedia)](https://en.wikipedia.org/wiki/Recursive_descent_parser) — the canonical overview: predictive parsing, LL(k), left recursion, and backtracking variants.
- [Parsing Expressions — Crafting Interpreters](http://craftinginterpreters.com/parsing-expressions.html) — recursive descent with precedence for expressions, building the AST chapter by chapter.
- [The Super Tiny Compiler](https://github.com/vagacoder/super-tiny-compiler) — a heavily commented tiny compiler walkthrough: tokenizer, parser, transformer, code generator.
- [Babel Plugin Handbook](https://github.com/jamiebuilds/babel-handbook/blob/HEAD/README.md) — parsing into ASTs and manipulating them with visitors; the parse side of the transpile pipeline.
- [Recursive descent parsing homework walkthrough](https://github.com/purdue-wl-ece264-spring2025/hw08-recursive-descent-parser) — a university assignment explaining the peek/next tokenizer design and the matching algorithm step by step.

## Stretch ideas

- Implement Pratt parsing alongside layered functions and compare the two on code size and extensibility.
- Write error recovery good enough to parse a file with ten seeded syntax errors and report all of them sensibly.
- Generate the parser mechanically from your EBNF grammar (a tiny parser generator) and diff its output against your hand-written one.
