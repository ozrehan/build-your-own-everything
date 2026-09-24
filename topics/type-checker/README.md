---
title: "Build Your Own Type Checker"
category: "programming-languages"
difficulty: "advanced"
tags: [type-systems, compilers, language-design]
related: [tree-walking-interpreter, bytecode-virtual-machine, pattern-matching-engine]
---

# Build Your Own Type Checker

A type checker is the part of a compiler that proves your program makes sense before it runs: it walks the syntax tree, assigns a type to every expression, and rejects programs where the types don't line up. Building one teaches you the machinery behind TypeScript's red squiggles and Rust's borrow-checker errors — environments of bindings, unification of type variables, and error messages that point at the real mistake. Stephen Diehl's *Write You a Haskell* implements Hindley-Milner inference from scratch.

## Core concepts

- **Typing environments** — checking is a function from (environment, expression) to type; the environment maps variables to their types, mirroring an interpreter's value environment.
- **Bidirectional checking** — some positions *infer* a type (function bodies) while others *check* against a known type (arguments); splitting the two keeps the algorithm tractable.
- **Unification** — when two types must match, unify them: walk both structures, binding type variables, and fail with a clear error on mismatch. The occurs check prevents infinite types.
- **Let-generalization (Hindley-Milner)** — a let-bound value gets a *type scheme* with quantified variables, which is what makes `let id = \x -> x` usable at many types.
- **Subtyping vs. invariance** — some systems accept a subtype where a supertype is expected (width subtyping on records); getting variance right is half of designing a checker.
- **Error messages as a feature** — the checker's real product is diagnostics: expected vs. actual types with source spans. Good errors are engineered, not accidental.

## How it works

The checker walks the AST carrying a type environment. Literals get base types; variables look up their type in the environment; a lambda introduces fresh type variables for its parameters and infers the body's type. Applications unify the function's domain type with the argument's type. At each `let`, the inferred type is generalized into a scheme by quantifying over variables not free in the environment — this is the heart of Hindley-Milner. Unification failures produce errors naming the expected and actual types with their source locations, and the compiler refuses to run the program until they are fixed.

## Build milestones

1. Define a tiny language AST and implement a checker for monomorphic types (numbers, booleans, annotated functions) — inference only, no polymorphism yet.
2. Add unification with type variables and the occurs check; infer types for unannotated lambdas.
3. Implement let-generalization; write tests showing `let id = fun x -> x` used at two different types in one program.
4. Add records, variants, or a small set of builtins; produce expected-vs-actual error messages with source locations.
5. Type-check a real program end to end: parse, check, and only interpret if checking passes.

## Best resources

- [rustc-dev-guide: type checking summary](https://rustc-dev-guide.Rust-lang.org/hir-typeck/summary.html) — how rustc type-checks HIR: inference, obligations, and trait solving in a production compiler.
- [rustc-dev-guide](https://rustc-dev-guide.Rust-lang.org/print.html) — the full guide to the Rust compiler internals; the surrounding chapters put type checking in context.
- [Interacting with the AST](https://rustc-dev-guide.Rust-lang.org/rustc-driver/interacting-with-the-ast.html) — working with rustc's syntax trees, the input your checker would consume.
- [Hindley-Milner inference — Write You a Haskell](https://github.com/sdiehl/write-you-a-haskell/blob/HEAD/006_hindley_milner.md) — the classic tutorial chapter implementing Algorithm W from scratch.
- [Write You a Haskell — introduction](https://github.com/sdiehl/write-you-a-haskell/blob/HEAD/000_introduction.md) — the series overview; the type-system chapters build on its core language.

## Stretch ideas

- Add row polymorphism or simple subtyping, and feel exactly where inference gets harder.
- Implement exhaustiveness checking for pattern matches over your variant types.
- Write a "type debugger" that shows the inferred type of any subexpression on hover, using your checker's intermediate results.
