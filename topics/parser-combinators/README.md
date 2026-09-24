---
title: "Build Your Own Parser Combinators"
category: "programming-languages"
difficulty: "intermediate"
tags: [parsing, functional-programming, compilers]
related: [recursive-descent-parser, formal-grammars-ebnf, dsl-design]
---

# Build Your Own Parser Combinators

Parser combinators build parsers out of parsers: tiny functions like `char('(')` and `many(digit)` snap together with combinators like `sequence`, `choice`, and `map` to describe whole grammars as ordinary code. The technique comes from functional programming — Parsec and Megaparsec made it famous in Haskell — and it turns parsing from a separate toolchain step into a library you just import. Rust's nom and C's mpc prove the idea works far beyond Haskell.

## Core concepts

- **Parsers as values** — a parser is a function from input to a (result, remaining input) pair; because it's just a value, you compose it with ordinary code instead of a generator tool.
- **Primitive parsers** — `char`, `string`, `satisfy`, and `digit` match the smallest units of input; every grammar you write is built from these.
- **Combinators** — `sequence`, `choice`, `many`, `optional`, and `sepBy` combine parsers into bigger ones; `map` transforms parsed results into AST nodes.
- **Sequencing with results** — applicative or monadic binding threads parsed values through a computation (do-notation in Haskell, `and_then` chains elsewhere).
- **Backtracking and committed choice** — `choice` tries alternatives in order; committed choice (`try`/cut) controls exponential blowup and determines error quality.
- **Error reporting** — good libraries track expected-vs-found with source positions; labels name grammar constructs so messages read like "expected expression" instead of "parse error".

## How it works

At the core, a parser is a function `input -> Option<(output, rest)>`. A primitive like `char('x')` checks the first character and returns the remainder; `sequence(p, q)` runs `p`, then `q` on what remains, pairing the results; `choice(p, q)` tries `p` and falls back to `q`. Recursive grammars work because parsers are usually wrapped in functions or lazily evaluated references, so a rule can mention itself. Whitespace is handled once, by a `token` combinator that runs a parser and skips trailing space — apply it everywhere and layout stops mattering. The whole library is often under 200 lines, yet it parses real languages.

## Build milestones

1. In your language of choice, define the parser type and primitives: `char`, `string`, `satisfy`, plus `map` and `choice`.
2. Add `many`, `optional`, `sepBy`, and a `token` wrapper that skips trailing whitespace; parse CSV or S-expressions as a first real grammar.
3. Parse arithmetic with precedence using combinator chaining (or a Pratt-style helper) and build an AST from the results.
4. Add position tracking and labeled errors so a failing parse prints a caret under the offending column.
5. Port a grammar you previously wrote by hand (JSON, or Lox expressions) to combinators, and compare line counts and error-message quality.

## Best resources

- [mpc — Micro Parser Combinators](https://github.com/orangeduck/mpc) — a parser-combinator library for C in a single file; proof the technique needs no fancy type system.
- [nom](https://github.com/rust-bakery/nom) — the industrial-strength Rust parser-combinator framework; its docs are a masterclass in combinator design.
- [Megaparsec documentation](https://hackage.haskell.org/package/megaparsec-4.4.0/docs/Text-Megaparsec.html) — the modern Haskell reference: error messages, backtracking control, and performance.
- [Parsec package](http://hackage.haskell.org/package/parsec-3.1.12.0) — the original Haskell combinator library that started it all.
- [Parser combinators in Haskell](https://DEV.to/serokell/parser-combinators-in-haskell-5c23) — Serokell's gentle tutorial building combinators from scratch before introducing the libraries.

## Stretch ideas

- Implement `try`/cut semantics and benchmark backtracking vs. committed parsing on a pathological input.
- Write a JSON parser with combinators plus a pretty-printer, then round-trip property-test them against each other.
- Build a tiny regex engine out of parser combinators to discover exactly where the technique breaks down (hint: left recursion).
