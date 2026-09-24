---
title: "Build Your Own Esoteric Language"
category: "programming-languages"
difficulty: "beginner"
tags: [language-design, fun, interpreters]
related: [tree-walking-interpreter, macro-systems, bytecode-virtual-machine]
---

# Build Your Own Esoteric Language

Esoteric languages are programming languages designed as art, jokes, or puzzles — Brainfuck has eight commands, Shakespeare programs read like plays, and Befunge executes in two dimensions. Because they're tiny, they're the perfect excuse to build a complete language implementation in a weekend: lexer, parser, and interpreter with almost no edge cases. The esolangs wiki catalogs hundreds of them, and the IOCCC celebrates code that's beautiful *because* it's unreadable.

## Core concepts

- **Minimalism as a design tool** — Brainfuck's eight instructions are Turing-complete; removing features forces you to discover what's truly essential in a language.
- **The tape machine** — many esolangs are just a pointer, an array of cells, and I/O; the entire runtime fits in a paragraph of code.
- **Brackets as control flow** — `[` and `]` are conditional jumps on the current cell; matching them at parse time turns interpretation into simple jumps.
- **Weird topologies** — Befunge's 2D grid, Piet's colors, and Shakespeare's characters prove "source code" doesn't have to be linear text.
- **Self-reference and quines** — esolangs love programs that print themselves; writing a quine tests whether you truly understand your own semantics.
- **The spec as playground** — with no users to disappoint, you can experiment with semantics (nondeterminism, randomness) that "serious" languages forbid.

## How it works

Pick one twist — a 2D grid, a stack-only machine, a single-instruction set — and write the spec on a single page: the state, the commands, and exactly what each command does to the state. Implementation is usually direct execution without even building an AST: Brainfuck precomputes bracket matches, then a program counter walks the commands manipulating the tape. Then comes the fun part: writing example programs from hello-world to fizzbuzz, which always reveals the spec bugs your reading missed. Document it with flair, because for an esolang the documentation *is* half the language.

## Build milestones

1. Implement Brainfuck: an interpreter for the eight commands with precomputed bracket matching; run the classic "Hello World".
2. Design your own esolang: pick one twist (2D grid, stack-only, single instruction) and write its spec on one page.
3. Implement it end to end: reader, interpreter, and five example programs from hello-world to fizzbuzz.
4. Publish it: esolangs-wiki-style documentation, a quine in your language, and one deliberately obfuscated masterpiece.

## Best resources

- [Brainfuck — Esolangs Wiki](https://esolangs.org/wiki/Brainfuck) — the canonical esolang's spec, examples, and commentary; your implementation target for milestone one.
- [IOCCC — winning entries by year](http://www.ioccc.org/years.html) — the International Obfuscated C Code Contest archive; inspiration for beautifully unreadable programs.
- [IOCCC winner repository — news](https://github.com/ioccc-src/winner/blob/HEAD/news.md) — the contest's current home: rules, guidelines, and recent winners.
- [Crafting Interpreters](https://craftinginterpreters.com/) — the serious counterpart: everything about implementing languages properly, once the joke language works.

## Stretch ideas

- Compile your esolang to your bytecode VM (or down to Brainfuck) instead of interpreting it.
- Add a visual debugger showing the tape or grid evolving step by step.
- Enter the IOCCC — or design an esolang specifically engineered to win "most obfuscated".
