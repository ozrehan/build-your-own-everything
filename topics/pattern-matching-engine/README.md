---
title: "Build Your Own Pattern-Matching Engine"
category: "programming-languages"
difficulty: "advanced"
tags: [compilers, language-design, algorithms]
related: [type-checker, recursive-descent-parser, tree-walking-interpreter]
---

# Build Your Own Pattern-Matching Engine

Pattern matching lets you destructure data by shape — matching on lists, trees, and variants — and it's the feature that makes ML-family languages feel like they read your mind. Underneath, the compiler turns nested patterns into efficient decision trees, checks that your matches are exhaustive, and warns about redundant cases. Lennart Augustsson's classic paper shows how to compile patterns to optimal decision trees, and it's a wonderful algorithms project.

## Core concepts

- **Patterns as predicates plus bindings** — a pattern is a test (constructor? literal? wildcard?) together with the variables it binds; matching tries cases top to bottom, first match wins.
- **Decision trees** — Augustsson's compilation turns a matrix of patterns into a tree of tests where each value is examined once; no backtracking happens at runtime.
- **Usefulness and exhaustiveness** — a case is *useful* if some value can reach it; a match is exhaustive if no value falls through. Both are decided by the same matrix algorithm (Maranget).
- **Redundancy warnings** — a case subsumed by earlier ones is dead code; detecting it falls out of the usefulness check for free.
- **Compilation to switches** — decision trees lower to nested switches and jumps; constructor tags become integer dispatches that CPUs predict well.
- **Guards and or-patterns** — boolean guards attach to cases and are checked after the pattern matches; or-patterns merge alternatives that share one right-hand side.

## How it works

Parsing produces a match expression: a scrutinee plus a list of (pattern, guard, body) clauses. Arrange the patterns as a matrix — rows are clauses, columns are the scrutinee's sub-values — and compile it with Augustsson's algorithm: pick a column, split rows by the constructor they test, and recurse, building a decision tree of constructor tests, literal comparisons, and bindings. In parallel, run Maranget's usefulness check on the matrix: it tells you which clauses are redundant and synthesizes a counterexample value when the match isn't exhaustive. The decision tree then lowers to nested switch instructions or straight-line conditional code.

## Build milestones

1. Define ASTs for patterns (wildcard, literal, variable, constructor, tuple) and write a naive tree-walking matcher that tries cases in order.
2. Implement pattern-matrix compilation from Augustsson's paper, producing a decision tree; interpret the tree directly.
3. Add Maranget-style exhaustiveness and redundancy checking, with warnings that name the missing case.
4. Lower decision trees to bytecode switch instructions (or generated conditionals); benchmark against the naive matcher.
5. Add or-patterns and guards, and verify the exhaustiveness checker still handles them correctly.

## Best resources

- [Compiling Pattern Matching to Good Decision Trees [pdf]](https://github.com/papers-we-love/papers-we-love/raw/refs/heads/main/pattern_matching/compiling-pattern-matching-to-good-decision-trees.pdf) — Lennart Augustsson's classic paper: the decision-tree compilation algorithm.
- [Warnings for Pattern Matching [pdf]](http://gallium.inria.fr/~maranget/papers/ml05e-maranget.pdf) — Luc Maranget's paper on usefulness, exhaustiveness, and redundancy checking.
- [Pattern compilation — Ori language design docs](https://github.com/upstat-io/ori-lang/blob/HEAD/docs/compiler/design/07-canonicalization/pattern-compilation.md) — a modern design doc applying pattern compilation in a real small compiler.
- [Compiling pattern matching — Regulus book](https://github.com/desertthunder/regulus/blob/HEAD/docs/book/src/chapter_8/compiling_pattern_matching.md) — a textbook chapter walking through compiling matches step by step.
- [Pattern matching theory — Ko language](https://github.com/adjanour/ko-language/blob/HEAD/ko-zig/docs/archived/THEORY.md) — theory notes covering pattern matching as part of a language design.

## Stretch ideas

- Compile matches to native jump tables and measure dispatch cost against chained conditionals.
- Add view patterns or active patterns (F#-style) that run functions during matching.
- Formalize your exhaustiveness checker on paper and prove it sound for the core pattern language.
