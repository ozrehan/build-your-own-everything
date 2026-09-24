---
title: "Build Your Own Lexical Scoping and Closures"
category: "programming-languages"
difficulty: "beginner"
tags: [language-design, semantics, interpreters]
related: [tree-walking-interpreter, repl-design, dsl-design]
---

# Build Your Own Lexical Scoping and Closures

Lexical scoping means a name refers to whatever was visible where the code was *written*, not where it happens to run — and a closure is a function that carries its birthplace scope along with it. This one idea explains JavaScript callbacks, Python decorators, and why loop variables famously misbehave inside closures. Building environments and closures yourself turns a confusing interview topic into machinery you can watch working.

## Core concepts

- **Environments as chained maps** — each scope is a dictionary with a pointer to its enclosing scope; name lookup walks outward until it finds the binding.
- **Lexical vs. dynamic scope** — lexical scope resolves names by source nesting; dynamic scope resolves them by the call stack. Nearly every modern language chose lexical because it's predictable.
- **Closures capture environments, not values** — the function object holds a reference to the environment where it was defined, so later mutations of captured variables remain visible.
- **The loop-variable gotcha** — one shared environment per loop means every closure sees the variable's final value; per-iteration environments fix it (the subject of a famous *Crafting Interpreters* design note).
- **Upvalues in bytecode VMs** — when compiling, a captured local becomes an *upvalue*: heap-allocated once its frame dies, so the closure outlives the call that created it.
- **The resolver pass** — a pre-pass binding each variable use to its declaration catches errors (undefined variables, self-reference in initializers) before the program runs.

## How it works

The interpreter represents each scope as an environment object with a `values` map and an `enclosing` pointer. Evaluating a block creates a child environment; variable lookup recurses outward through the chain. A function literal evaluates to a closure object bundling its parameters, body AST, and the *current* environment — the defining one. Calling it creates a fresh environment enclosed by that captured environment, binds the arguments, and evaluates the body. Because the captured environment is shared by reference, two closures over the same scope observe each other's mutations, which is exactly how counters and private state work.

## Build milestones

1. Build an interpreter with global and block scopes via chained environments; demonstrate variable shadowing working correctly.
2. Add first-class functions: declaration, calls, `return`, and recursion (the function's own name must resolve in its defining environment).
3. Implement closures: counter/adder examples where the inner function outlives the outer call, showing shared mutable capture.
4. Add the resolver pass: statically report "can't read local variable in its own initializer" and undefined-variable errors before execution.

## Best resources

- [Crafting Interpreters](https://craftinginterpreters.com/) — Chapters 11 (resolving and binding) and 25 (closures) implement lexical scope twice: once in the tree-walker, once compiled to upvalues.
- [Crafting Interpreters — Table of Contents](https://craftinginterpreters.com/contents.html) — navigate to the scoping, function, and closure chapters, including the "Closing Over the Loop Variable" design note.
- [Closures — MDN Web Docs](https://lia.disi.unibo.it/materiale/JS/developer.mozilla.org/en-US/docs/Web/JavaScript/Closures.html) — MDN's reference on how closures capture their lexical environment in JavaScript (via a university mirror).
- [SICP full text](https://github.com/jayfid/sicp-textbook) — *Structure and Interpretation of Computer Programs*; Chapter 3's environment model of evaluation is the deepest treatment of scoping ever written.

## Stretch ideas

- Reproduce the classic loop-closure bug, then fix it two ways (per-iteration scope vs. capture-by-value) with tests for both.
- Compile closures to a bytecode VM with upvalues instead of interpreting the tree.
- Implement `nonlocal`/`global`-style declarations and observe what they do to your resolver.
