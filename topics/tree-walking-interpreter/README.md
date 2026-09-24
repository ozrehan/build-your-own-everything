---
title: "Build Your Own Tree-Walking Interpreter"
category: "programming-languages"
difficulty: "intermediate"
tags: [interpreters, language-design, compilers]
related: [bytecode-virtual-machine, recursive-descent-parser, lexical-scoping-closures]
---

# Build Your Own Tree-Walking Interpreter

A tree-walking interpreter is the most direct way to make a programming language run: it parses source code into an abstract syntax tree, then executes the program by recursively evaluating each node. Every language feature becomes one more node type with one more evaluation rule, which makes this the ideal architecture for your first complete interpreter. Bob Nystrom's *Crafting Interpreters* and Thorsten Ball's *Writing an Interpreter in Go* both teach interpreters this way before moving on to bytecode.

## Core concepts

- **The AST is the program** — parsing produces a tree of node objects (binary expressions, literals, statements); after that the interpreter never touches raw text again, only this structured representation.
- **Evaluate by dispatch** — each node type has an evaluation routine that recursively evaluates its children first, then combines the results; adding a language feature usually means adding one node type and one evaluate case.
- **Environments for variables** — a chain of scopes maps names to values; looking up a variable walks outward through enclosing scopes, which is how nested blocks resolve names.
- **Closures capture environments** — a function value bundles its parameter list, body AST, and the environment where it was defined, so it remembers its birthplace scope when called later.
- **Runtime values vs. syntax** — the tree is syntax; evaluation produces values (numbers, strings, booleans, functions). Type errors surface at evaluation time, when an operator meets values it cannot handle.
- **Control flow as interpretation** — loops and conditionals are nodes whose evaluation conditionally re-evaluates child nodes; `return` and `break` are typically implemented by unwinding with an exception or a sentinel value.

## How it works

Source code goes through a lexer (characters to tokens) and a parser (tokens to AST). The interpreter then walks the tree: evaluating a binary expression evaluates the left and right subtrees and applies the operator; evaluating a block executes each statement in a fresh child environment; evaluating a variable declaration binds a value in the current environment. Function calls create a new environment enclosed by the function's captured environment, bind arguments to parameters, and evaluate the body — recursion falls out naturally because the function's own name resolves in its defining scope.

Because everything is late-bound at evaluation time, a tree-walker is slow but wonderfully simple to extend: new syntax is a new node class, new semantics is a new branch in the evaluator. The main engineering work is error reporting with line numbers, since a crash deep in a recursive evaluation needs to tell the user where in *their* program things went wrong.

## Build milestones

1. Write a lexer producing tokens, AST node classes, and an evaluator for arithmetic literals and binary operators behind a tiny REPL.
2. Add statements: expression statements, `print`, variable declaration and assignment, with block scoping via chained environments.
3. Add control flow: `if`/`else`, `while`/`for` loops, comparison and logical operators.
4. Add functions: declaration, calls with arity checking, `return`, recursion, plus a couple of native functions like a clock.
5. Implement a resolver pass that binds each variable use to its declaration lexically, then add closures and classes with methods and inheritance as the capstone.

## Best resources

- [Crafting Interpreters](https://craftinginterpreters.com/) — Bob Nystrom's free book; Part II builds jlox, a complete tree-walk interpreter in Java, from scanning to inheritance.
- [A Tree-Walk Interpreter](https://craftinginterpreters.com/a-tree-walk-interpreter.html) — the Part II overview chapter: why walking the tree directly is a legitimate execution strategy.
- [The Lox Language](https://craftinginterpreters.com/the-lox-language.html) — the small language the book implements; a great example of designing a language before implementing it.
- [Writing An Interpreter in Go](https://interpreterbook.com) — Thorsten Ball's book building the Monkey language interpreter: lexer, parser (Pratt), and tree-walking evaluator.
- [Writing A Compiler in Go](https://compilerbook.com) — Ball's follow-up, showing where the tree-walker ends and a bytecode compiler begins.
- [Lisp interpreter in C](https://github.com/mudphone/lisp-in-c) — a compact real-world example of a tree-walking evaluator for a Lisp dialect, in C.

## Stretch ideas

- Add a static resolver that reports errors before running: variables used in their own initializer, unused locals, undefined names.
- Implement a module system or standard library (string manipulation, file I/O) on top of your native-function mechanism.
- Add proper tail calls or a step-limited debugger with breakpoints, and watch your recursion depth stop mattering.
