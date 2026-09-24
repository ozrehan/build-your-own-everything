# Example: Programming Languages — TinyLang Playground

**[▶ Try it live](https://byoe-tiny-lang.netlify.app)**

A complete interpreter for a tiny Lisp-like language in one HTML file:
**tokenize → parse → evaluate**, with every stage shown on screen.

Example project for the [programming-languages learning path](../../topics/tree-walking-interpreter/).
Type code, hit run, and see the tokens, the AST, and the output side by side.

## The language

```lisp
(def fact (n)
  (if (<= n 1) 1 (* n (fact (- n 1)))))
(print (fact 6))            ; 720
(print (map (fn (x) (* x x)) (list 1 2 3 4)))
```

Functions, lambdas, closures, `let`, `if`, `map`, recursion — in ~150 lines of JS.

## What it teaches

| Stage | Code | Concept |
|---|---|---|
| Lexer | `tokenize()` | regex-driven tokenizer, comments, parens |
| Parser | `parse()` | recursive descent → AST |
| Evaluator | `ev()` | tree-walking interpreter, lexical scope, closures |
| Special forms | `def`/`fn`/`if`/`let` | how syntax becomes semantics |

## Exercises

1. Add `while` loops or string literals.
2. Show evaluation *steps* (one AST node at a time) instead of just the result.
3. Compile to a bytecode VM instead of tree-walking (see the `bytecode-virtual-machine` topic).
