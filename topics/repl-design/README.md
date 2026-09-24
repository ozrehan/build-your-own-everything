---
title: "Build Your Own REPL"
category: "programming-languages"
difficulty: "beginner"
tags: [developer-tools, interpreters, language-design]
related: [tree-walking-interpreter, lexical-scoping-closures, bytecode-virtual-machine]
---

# Build Your Own REPL

A REPL — read, eval, print, loop — is the fastest feedback loop in programming: type an expression, see the result, keep the state. Every language worth learning has one, from Python's `>>>` to Node's `>`, and building your own teaches you interactive line editing, incremental parsing, and how to keep interpreter state alive across inputs. Python's own `code` module and prompt_toolkit show how the pros structure it.

## Core concepts

- **The four phases** — read a line (with editing), eval it against persistent state, print the result readably, loop. Each phase is independently interesting.
- **Persistent environments** — definitions survive between inputs; the REPL's top-level scope is just an environment that never gets discarded.
- **Incremental / partial input** — an unfinished construct (`def f():`) needs a continuation prompt; detect incomplete parses and keep reading instead of erroring.
- **Readable printing** — results need a `repr`: truncated collections, quoted strings, cycle detection. Printing *is* a feature, not an afterthought.
- **Line editing and history** — readline-style editing, history search, and completion turn a toy into a tool; libraries like prompt_toolkit do the heavy lifting.
- **Error isolation** — a runtime error must print a traceback and return to the prompt, never kill the session; each input runs inside its own exception boundary.

## How it works

The loop is simple: display a prompt, read a line with editing support, and try to parse it. If parsing fails with an "incomplete input" signal — unbalanced parentheses, an expected indented block — switch to a continuation prompt and accumulate lines until the input parses. Then evaluate the AST against the persistent top-level environment inside a try/except boundary: on success, print the value's readable representation (skipping it for statements with no value); on failure, print a traceback with source lines and resume. History, completion, and highlighting plug in at the "read" phase without touching evaluation.

## Build milestones

1. Wrap your tree-walking interpreter in a bare loop: read a line, eval, print — with definitions persisting across lines.
2. Add continuation prompts: detect incomplete input (unbalanced delimiters, expected blocks) and keep reading with a `...` prompt.
3. Make errors friendly: tracebacks with source lines that return to the prompt, plus a `repr` that truncates long outputs.
4. Upgrade input with prompt_toolkit — history, completion drawn from your environment's names, syntax highlighting — or readline bindings.

## Best resources

- [Python `code` module](https://docs.Python.org/3.9/library/code.html) — the stdlib building blocks for interpreters and interactive consoles: `InteractiveConsole` and friends.
- [Node.js REPL documentation](https://nodejs.org/download/release/v13.10.1/docs/api/repl.html) — the REPL API: custom eval functions, writer customization, and persistent history.
- [prompt_toolkit documentation](https://python-prompt-toolkit.readthedocs.io/en/stable/) — the library behind ptpython and many CLIs: editing, completion, highlighting.
- [prompt_toolkit: asking for input](https://python-prompt-toolkit.readthedocs.io/en/stable/pages/asking_for_input.html) — prompts, validation, and multiline input handling in detail.
- [Crafting Interpreters](https://craftinginterpreters.com/) — Lox runs an interactive prompt from chapter one; the book's error-reporting design carries over directly to REPL work.

## Stretch ideas

- Add multi-line editing and a paste mode that handles indented blocks correctly.
- Implement `%timeit`-style magic commands or shell escapes (`!ls`) à la IPython.
- Persist session history to a file with reverse-i-search, then dogfood it while building your next interpreter.
