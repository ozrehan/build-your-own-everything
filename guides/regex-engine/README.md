# Build Your Own Regex Engine

A tiny but real regular expression engine in ~350 lines of Python, stdlib only.
It supports literals, `.`, `*` `+` `?`, `|` alternation, `(...)` groups,
`^`/`$` anchors, `[abc]` / `[a-z]` / `[^abc]` character classes, and escapes
like `\d` `\w` `\s` `\.`.

```python
from regex import match, search

match(r"a*b", "aaab")        # True  -- full match, like re.fullmatch
match(r"(a|b)*c", "ababc")   # True
search(r"\d+", "abc123")     # True  -- found anywhere, like re.search
match(r"^a*$", "aaab")       # False
```

## What you'll build

Two clean phases, exactly like production regex engines:

1. **Parser** — turns a pattern string into an AST (abstract syntax tree).
   `a(b|c)*` becomes `Seq(Lit('a'), Star(Group(Alt(Lit('b'), Lit('c')))))`.
2. **Matcher** — walks the AST against the text and answers True/False.

## How it works, in plain steps

**Step 1 — Decide what a pattern *means*.** Every regex construct becomes a
node type: `Lit` (one exact char), `Dot` (any char), `Seq` (things in order),
`Alt` (this or that), `Star`/`Plus`/`Question` (repetition), `AnchorStart`/
`AnchorEnd` (`^`/`$`), `CharClass` (`[...]`), `Group` (`(...)`). Writing these
as tiny classes first forces you to pin down the semantics before any parsing.

**Step 2 — Write the parser as a recursive descent parser.** The grammar is:

```
regex      := alt
alt        := concat ('|' concat)*
concat     := quantified*
quantified := atom ('*' | '+' | '?')?
atom       := '(' regex ')' | '[' class ']' | '.' | '^' | '$'
              | '\' escape | literal-char
```

Each rule becomes one method (`parse_alt`, `parse_concat`, …) that reads from
a cursor (`self.pos`) and returns AST nodes. Notice how precedence falls out
for free: `*` binds tightest (it's deepest, in `parse_quantified`), then
concatenation, then `|` — exactly like real regex. Character classes get their
own little sub-parser handling ranges (`a-z`), negation (`[^...]`), and the
`\]` / `\-` edge cases.

**Step 3 — Write the matcher.** The key insight:

```python
_match(node, text, pos) -> set of end positions
```

Instead of returning one position, return the **set of all positions** the
match could end at. Backtracking becomes set union: `Alt` tries both sides and
unions the results; `Seq` threads the position set through each child; `Star`
flood-fills — repeatedly match the inner node from every reached position
until no new positions appear. Because positions are bounded by `len(text)`,
this always terminates (even `(a?)*` can't loop forever) and `a*a*a*` stays
polynomial instead of blowing up exponentially.

**Step 4 — Add the API.** `match()` compiles the pattern, runs the matcher at
position 0, and checks whether `len(text)` is among the end positions.
`search()` tries every start position from 0 to `len(text)`.

## How to run

```bash
cd guides/regex-engine
python3 -c "
from regex import match, search
print(match(r'(a|b)*c', 'ababc'))  # True
print(search(r'\d+', 'abc123'))    # True
"
```

## How to test

```bash
python3 test_regex.py
```

72 checks: every feature, tricky backtracking cases (`a*b` vs `aaab`,
`(a|b)*c`, `(a|ab)*` vs `ab`), anchors, classes, escapes, and 8 invalid
patterns that must raise `RegexError` (unbalanced parens, dangling `*`,
bad escapes…).

## Stretch exercises

1. **Capture groups.** Make `Group` record the text it matched and return a
   dict of group spans, so `match` can behave like `re.Match` with `.group(1)`.
2. **`{m,n}` repetition.** Parse `a{2,4}` into a new AST node and implement it
   in the matcher (hint: it's just `Seq` of the right pieces plus `Question`s).
3. **Character class subtraction / POSIX classes.** Add `[[:alpha:]]`, or make
   `\d` inside `[^...]` behave correctly and add tests proving it.

## Further reading

- Russ Cox, "Regular Expression Matching Can Be Simple And Fast" —
  https://swtch.com/~rsc/regexp/ (how real engines avoid backtracking blowup)
- Python `re` docs — https://docs.python.org/3/library/re.html (the
  full feature set to aspire to)
- "Regular Expressions Tutorial" — https://www.regular-expressions.info/tutorial.html
