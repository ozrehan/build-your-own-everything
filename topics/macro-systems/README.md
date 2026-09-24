---
title: "Build Your Own Macro System"
category: "programming-languages"
difficulty: "advanced"
tags: [metaprogramming, language-design, compilers]
related: [dsl-design, tree-walking-interpreter, esoteric-language]
---

# Build Your Own Macro System

A macro system lets programs write programs: macros transform syntax before (or during) compilation, so you can add language features as libraries instead of waiting for the language designer. From C's preprocessor to Racket's hygienic syntax transformers, macros are the oldest and most powerful form of metaprogramming. Building one teaches you the difference between text substitution, AST transformation, and true syntactic extension — and why hygiene matters.

## Core concepts

- **Expansion time vs. run time** — macros run at compile time on code-as-data; the expanded code then compiles and runs normally. Keeping the phases straight is the whole game.
- **Textual vs. syntactic macros** — the C preprocessor pastes tokens blindly; Lisp and Racket macros transform structured syntax, so they can't produce unbalanced delimiters.
- **Hygiene** — a hygienic macro can't accidentally capture (or be captured by) identifiers at the use site; `syntax-rules` renames introduced bindings automatically.
- **Pattern-based definition** — `syntax-rules` style: match the input shape against patterns and fill in templates. Most macros you'll ever write fit this mold.
- **Procedural macros** — full functions from syntax to syntax (Racket syntax transformers, Rust proc macros) for the cases patterns can't express.
- **Compile-time computation** — macros can run arbitrary code during expansion: reading config files, generating boilerplate, or embedding DSLs that compile to efficient code.

## How it works

The pipeline is parse, then expand, then compile: the expander walks the syntax tree, and wherever it finds a macro call it invokes the macro's transformer on the unevaluated syntax, splices the result back in, and recursively expands again (macro-generating macros must terminate). Hygiene is implemented either by renaming — every binding a macro introduces gets a fresh generated symbol — or by attaching scope information to syntax objects, as Racket does. Once expansion reaches a fixed point with no macro calls left, the resulting core-language tree goes to the evaluator or compiler unchanged.

## Build milestones

1. Write a Lisp-style reader producing S-expressions; implement `defmacro` with quasiquote/unquote doing naive substitution, and demonstrate variable capture breaking.
2. Add hygiene: rename introduced bindings with generated symbols (or track scopes); show the capture example now working.
3. Implement pattern-based macros (`syntax-rules`-like): patterns with ellipses expanding to templates; define `or`, `cond`, and `let` as macros.
4. Add procedural macros — a macro defined by an arbitrary function over syntax objects — and use one to build a tiny DSL (an HTML templating or test-assertion language).
5. Support compile-time side effects: a macro that reads a file at expansion time and embeds its contents as program data.

## Best resources

- [Racket Reference: Macros](https://docs.racket-lang.org/reference/Macros.html) — the definitive reference for `define-syntax`, `syntax-rules`, and `syntax-case` in the world's most macro-centric language.
- [Macros and Syntax Transformers](http://docs.racket-lang.org/mischief/Macros_and_Syntax_Transformers.html) — a tutorial-style guide to writing real syntax transformers, with worked examples.
- [Rhombus expression macros](https://docs.racket-lang.org/rhombus/expr-macro.html) — how Racket's new Rhombus language exposes macro definition with modern syntax.
- [The C Preprocessor — invocation](https://gcc.gnu.org/onlinedocs/cpp/Invocation.html) — GCC's manual for the textual macro system every C programmer uses daily.
- [The C Preprocessor — the preprocessing language](https://gcc.gnu.org/onlinedocs/gcc-9.5.0/cpp/The-preprocessing-language.html) — conditionals, macro expansion rules, and pitfalls of token-based macros.

## Stretch ideas

- Implement `define-syntax-rule` with proper ellipsis (`...`) repetition handling in patterns and templates.
- Add reader macros (like quote and quasiquote) so your surface syntax itself becomes extensible.
- Write a macro stepper that shows each expansion step for a tricky macro, making debugging possible.
