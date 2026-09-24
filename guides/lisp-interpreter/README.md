# Build Your Own Lisp Interpreter

A tiny but complete Lisp interpreter in ~400 lines of Python, stdlib only:
tokenizer → parser → tree-walking evaluator, with closures, recursion,
`define`, `lambda`, `if`, `quote`, `begin`, arithmetic, comparisons, list
operations, `display`, and `;` comments. Doubles as a REPL.

```bash
python3 lisp.py                      # REPL
python3 lisp.py program.lisp         # run a file
```

```lisp
; program.lisp
(define (fact n)
  (if (= n 0) 1 (* n (fact (- n 1)))))
(fact 5)   ; -> 120

(define (make-adder x) (lambda (y) (+ x y)))
(define add3 (make-adder 3))
(add3 10)  ; -> 13, the lambda remembered x=3 (a closure!)
```

## What you'll build

Three classic stages, the same architecture as real interpreters:

1. **Tokenizer** — source text → flat token list (`(`, `+`, `42`, …).
2. **Parser** — tokens → AST, where Lisp code is just nested Python lists.
3. **Evaluator** — walks the AST with an **environment** (a chain of scopes).

## How it works, in plain steps

**Step 1 — Tokenize.** Scan the text left to right: skip whitespace, skip `;`
comments to end of line, emit `(` `)` `'` as single tokens, read `"..."`
strings (with `\n` `\"` escapes), and grab everything else as a
number-or-symbol token. One small trick: strings become a `Str` subclass of
Python `str`, so the evaluator can tell `"hello"` (a literal) apart from
`hello` (a variable).

**Step 2 — Parse into S-expressions.** `(` starts a Python list, `)` ends it,
`'x` is sugar for `["quote", x]`, and atoms become ints, floats, `#t`/`#f`
booleans, strings, or symbol names. Lisp's genius: the AST *is* the syntax —
no separate grammar needed beyond "lists and atoms".

**Step 3 — Environments.** An `Env` is a dict plus an `outer` pointer.
`find(var)` walks outward to the nearest binding — that's lexical scoping in
six lines. A `Proc` bundles parameter names + body + the environment where the
`lambda` was *defined*. That captured environment is the entire secret of
closures: `make-adder` returns a `Proc` that still sees `x=3` after
`make-adder` has returned.

**Step 4 — Evaluate.** `evl(node, env)`:

- *Atoms*: strings evaluate to themselves, symbols are looked up
  (`env.find(name)[name]` — undefined names raise `LispError`), numbers and
  booleans are self-evaluating.
- *Special forms* use their arguments **unevaluated**: `if` evaluates only the
  taken branch, `quote` returns its argument raw, `define` binds a name
  (or `(define (f args) body)` shorthand for functions), `lambda` builds a
  `Proc`, `begin` runs a sequence, `set!` mutates an existing binding.
- *Everything else* is a call: evaluate the head to a procedure, evaluate all
  arguments, apply. Calling a non-function, or an undefined variable, is a
  clear `LispError` — never a raw Python traceback.

**Step 5 — Builtins as Python functions.** `+ - * /` (variadic), `= < > <=
>=`, `car`/`cdr`/`cons`/`list`, `null?`, `display`, … live in
`standard_env()`. Note `/`: `(/ 8 2)` → `2` (exact divisions stay ints),
`(/ 7 2)` → `3.5`, and division by zero is a `LispError`.

**Step 6 — Two front ends.** `run_file(path)` evaluates each top-level form
and prints non-`None` results; `repl()` loops `input()` → `eval_str` →
print, catching `LispError`s so one bad expression doesn't kill the session.
Recursion works because `(define (fact n) …)` binds `fact` in the environment
the `Proc` closes over.

## How to run

```bash
cd guides/lisp-interpreter
python3 lisp.py                       # REPL -- try (+ 1 2), (define (sq n) (* n n))
echo '(define (fact n) (if (= n 0) 1 (* n (fact (- n 1))))) (fact 5)' > f.lisp
python3 lisp.py f.lisp                # -> 120
```

## How to test

```bash
python3 test_lisp.py
```

62 checks: tokenizer/parser basics, arithmetic, comparisons, `define`/`if`/
`begin`/`set!`, lambdas, **closures capturing their environment**, **factorial
via recursion** (120 and the base case), quote behavior (`'(1 2 3)`,
`(car '(4 5))`), list ops, strings, comments, pretty-printing, 12 error cases
(undefined variable, calling a non-function, unbalanced parens, …), plus a
real subprocess test proving `python3 lisp.py program.lisp` works end to end.

## Stretch exercises

1. **Multi-line REPL.** Buffer input until the parens balance, so you can
   paste a whole `define` across lines.
2. **`cond` and `let`.** Add them as special forms — or better, as *derived*
   forms rewritten into `if`/`lambda` by the parser.
3. **Tail-call optimization.** `(fact 100000)` currently hits Python's
   recursion limit — convert the evaluator's tail positions into a loop so
   recursion runs in constant stack space.

## Further reading

- Peter Norvig, "(How to Write a (Lisp) Interpreter (in Python))" —
  http://norvig.com/lispy.html (the classic 100-line version of this idea)
- Paul Graham, "The Roots of Lisp" — http://www.paulgraham.com/rootsoflisp.html
  (Lisp from 7 axioms)
- *Structure and Interpretation of Computer Programs*, ch. 4 —
  https://mitpress.mit.edu/sites/default/files/sicp/index.html
  (the metacircular evaluator: Lisp interpreting Lisp)
