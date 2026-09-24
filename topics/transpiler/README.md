---
title: "Build Your Own Transpiler"
category: "programming-languages"
difficulty: "intermediate"
tags: [compilers, language-design, developer-tools]
related: [recursive-descent-parser, bytecode-virtual-machine, macro-systems]
---

# Build Your Own Transpiler

A transpiler is a compiler whose target language is another high-level language: TypeScript becomes JavaScript, early C++ became C, and Babel turns next-year's JavaScript into today's. Because the output is readable source rather than machine code, you can debug, test, and ship it with ordinary tools — which is why transpilation is often the fastest route from a language idea to real users. The Babel handbook teaches the parse → transform → generate pipeline that every transpiler shares.

## Core concepts

- **Parse → transform → generate** — reuse an existing parser for the source language, rewrite the AST with plugins or visitors, then pretty-print the target language.
- **AST visitors** — transforms are expressed as visitors keyed by node type with enter/exit hooks; Babel plugins are the canonical example.
- **Source fidelity** — a transpiler must preserve semantics *and* readability: comments, formatting, and source maps so stack traces point at the original code.
- **Desugaring** — fancy source constructs lower to simpler target constructs (async/await to state machines, classes to prototypes); each desugar is one small, testable pass.
- **Polyfills vs. syntax transforms** — syntax can be rewritten, but new runtime APIs need polyfill libraries shipped alongside the output.
- **Targeting multiple outputs** — one AST can generate several dialects (ES5 vs. ES2017); usually the printer varies, not the transformer.

## How it works

An existing, battle-tested parser turns source into an AST — you don't write this part. Your code is a set of transform passes, each an AST visitor that pattern-matches node types and rewrites them: an arrow function becomes a function expression with a bound `this`, optional chaining becomes explicit nil checks. Passes compose in a pipeline, and a code generator walks the final AST emitting target source plus a source map recording which output line came from which input line. A test suite of before/after program pairs, executed in both languages, proves semantics survived.

## Build milestones

1. Pick a tiny source language (or a subset of JS) and reuse an existing parser; write a pretty-printer that round-trips programs unchanged.
2. Implement one desugaring pass as an AST visitor (e.g. arrow functions to function expressions, or `?.` to explicit checks).
3. Chain three passes — parse, two transforms, generate — and add source-map generation so errors map back to the original.
4. Write a Babel plugin (or TypeScript compiler-API transform) that performs your desugaring on real-world code.
5. Build the full pipeline: a CLI reading source files, applying your plugin set, and writing output plus maps, with before/after test pairs.

## Best resources

- [Babel Plugin Handbook](https://github.com/jamiebuilds/babel-handbook/blob/HEAD/README.md) — the essential guide to Babel's AST, visitors, paths, and writing your first transform.
- [Writing your first Babel plugin](https://github.com/jamiebuilds/babel-docs/blob/HEAD/jamiebuilds-babel-docs-2a74836/en_US/authors/guides/writing-your-first-babel-plugin.md) — the official walkthrough: visitors, scope handling, and plugin structure.
- [Using the TypeScript Compiler API](https://github.com/microsoft/typescript-wiki/blob/HEAD/Using-the-Compiler-API.md) — parse, bind, and transform real TypeScript with the compiler's own API.
- [TypeScript Compiler API wiki](https://github.com/Microsoft/TypeScript/wiki/Using-the-Compiler-API) — the companion wiki page with further compiler-API examples.
- [The Super Tiny Compiler](https://github.com/vagacoder/super-tiny-compiler) — the tokenizer → parser → transformer → generator pipeline in miniature, heavily commented.

## Stretch ideas

- Add watch mode with incremental re-transpilation and caching keyed by file hash.
- Implement scope-aware transforms (hygienic helper injection, like Babel's helpers) without name collisions.
- Transpile one of your earlier interpreter projects to a second language and run its test suite against the output.
