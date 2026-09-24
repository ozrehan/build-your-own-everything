# Build Your Own Template Engine

A mini Jinja-style template engine in ~110 lines of Python. One public function — `render(template_str, context)` — and zero dependencies.

## What you'll build

A template engine supporting:

- `{{ var }}` and dotted paths like `{{ user.name }}` — missing variables render as empty string
- `{% if flag %}...{% endif %}` — include a block when a context variable is truthy
- `{% for item in items %}...{% endfor %}` — loop over a list (nesting works)
- `{# comment #}` — stripped from the output

## How it works, in plain steps

1. **Tokenize.** A single regex splits the template into literal text chunks and `{{ }}` / `{% %}` / `{# #}` tags. Everything between tags is just text.
2. **Parse into a node tree.** `_parse()` walks the tokens and builds a list of nodes: `("text", ...)`, `("var", expr)`, `("if", cond, body)`, `("for", var, iterable, body)`. When it meets `{% if %}` or `{% for %}` it recurses to parse the body until the matching `{% endif %}` / `{% endfor %}` — that's what makes nesting free.
3. **Resolve dotted names.** `_resolve("user.name", context)` walks the dict one key at a time. Any missing step returns `""`, which is why undefined variables silently render empty instead of crashing.
4. **Render the tree.** `_render_nodes()` walks the nodes: text is copied verbatim, variables are resolved and stringified, `if` renders its body only when the condition is truthy, and `for` renders its body once per item with the loop variable shadowed in a *copy* of the context (so the outer context is never polluted).

## How to run

```bash
python3 template.py
```

This renders a sample template with a user dict, an `if` block, a `for` loop, and a comment.

Try it yourself in a REPL:

```python
from template import render
render("Hello {{ name }}!", {"name": "Ada"})
# 'Hello Ada!'
```

## How to test

```bash
python3 test_template.py
```

Covers variables, dotted paths, missing variables, if true/false branches, for loops, nested loops, comment stripping, and a mixed template.

## Stretch exercises

1. **`{% else %}` and `{% elif %}`.** Extend the parser so `if` nodes can carry an else-branch (and chained elifs). You'll need to parse the if-body until `else`/`elif`/`endif`.
2. **Filters.** Support `{{ name | upper }}` with a small registry of filter functions (`upper`, `lower`, `length`, ...). Parse the `|` in var tags and apply the filters left to right.
3. **Compile to Python.** Instead of interpreting the node tree, generate a Python source string (a function that appends to a list) and `exec` it. Compare the speed against the tree-walking version with `timeit`.

## Further reading

- Jinja2 documentation — https://jinja.palletsprojects.com/ (the real thing this mimics; great design reference)
- "So you want to write an interpreter?" — http://effbot.org/zone/simple-top-down-parsing.htm (tokenize → parse → evaluate, the same pipeline)
- TinyJinja / mini template engine gists — search GitHub for "template engine in 50 lines" to see how small this idea can get
