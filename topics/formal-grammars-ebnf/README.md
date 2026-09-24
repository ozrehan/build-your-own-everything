---
title: "Build Your Own Formal Grammar (EBNF)"
category: "programming-languages"
difficulty: "beginner"
tags: [grammars, parsing, theory]
related: [recursive-descent-parser, parser-combinators, assembler]
---

# Build Your Own Formal Grammar (EBNF)

A formal grammar is a precise, checkable definition of what counts as a valid program — every language specification, from XML to Rust, is ultimately a grammar plus prose. EBNF (Extended Backus–Naur Form) is the standard notation for writing grammars down: terminals in quotes, nonterminals by name, and a small set of operators for sequence, choice, and repetition. Writing the grammar *first* is the cheapest way to design a language, because ambiguities show up on paper before they become parser bugs.

## Core concepts

- **Terminals vs. nonterminals** — terminals are the tokens (`"if"`, numbers); nonterminals are named rules built from them. A grammar is a system of equations over these two kinds.
- **Productions** — a line like `expr = term { ("+" | "-") term }` defines a nonterminal; the `=` (or `::=`) separates the name from its alternatives.
- **EBNF operators** — `{ x }` means repetition, `[ x ]` means optional, `( x | y )` groups and chooses. They all desugar to plain BNF with helper rules.
- **Recursion for nesting** — nested structures (parentheses, blocks) need recursive rules; iteration alone cannot express "arbitrarily deep".
- **Ambiguity** — when one input has two valid parse trees (the classic dangling-else), the grammar is ambiguous; fix it by restructuring rules, not with parser hacks.
- **Grammars as contracts** — a published grammar lets independent implementations agree; the XML spec's EBNF is why every XML parser accepts the same documents.

## How it works

You write the grammar as a set of productions, starting from the start symbol (usually `program`) down to tokens. Each new construct gets a rule; each rule uses sequence (juxtaposition), choice (`|`), option (`[ ]`), and repetition (`{ }`). Then you validate it: derive a few sample programs by hand to confirm they're accepted, and try to derive invalid ones to confirm they're rejected. Ambiguity hunting is the real skill — for expressions you layer rules by precedence; for `if/else` you bind `else` to the nearest `if`. A finished grammar maps almost mechanically onto a recursive-descent parser: one function per rule.

## Build milestones

1. Write EBNF for JSON from memory, then diff it against the real spec and fix every discrepancy.
2. Write a grammar for arithmetic with correct precedence using layered rules; identify exactly where the naive grammar is ambiguous.
3. Specify a tiny statement language (assignment, `if`, `while`, blocks) in EBNF, solving the dangling-else explicitly in the rules.
4. Turn your grammar into a working recursive-descent parser mechanically — one function per rule — with a test suite of valid and invalid programs.

## Best resources

- [Extended Backus–Naur form (Wikipedia)](https://en.wikipedia.org/wiki/Extended_Backus–Naur_form) — the notation's definition, operators, and history, with examples.
- [XML spec (proposed recommendation) — EBNF notation](https://www.w3.org/TR/PR-xml-971208) — a real specification written in EBNF; see how the W3C defines the notation and uses it.
- [BNF, EBNF, ABNF reference](http://www.xahlee.info/parser/bnf_ebnf_abnf.html) — Xah Lee's side-by-side comparison of the three notations with examples.
- [EBNF resources](https://github.com/tabnas/ebnf) — a collection of EBNF grammars and tooling references.
- [Syntax Specification — Wikibooks](https://en.wikibooks.org/wiki/Programming_Languages/Syntax_Specification) — a textbook chapter on specifying language syntax with grammars.

## Stretch ideas

- Convert your EBNF to ABNF (RFC 5234) and render it as railroad diagrams; compare the readability of all three.
- Prove a property of your grammar on paper — e.g. that every derivable program has balanced braces — by induction on the rules.
- Write a grammar fuzzer that generates random valid programs from your EBNF, and use it to stress-test your parser.
