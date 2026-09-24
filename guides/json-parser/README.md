# Build Your Own JSON Parser

A complete JSON parser **and** serializer in ~330 lines of Python, stdlib
only. Parses to native Python objects (`null`→`None`, `true`→`True`,
`false`→`False`) and serializes back, with strict error messages.

```python
from json import parse, stringify

parse('{"name": "ada", "scores": [10, 2.5, null], "ok": true}')
# {'name': 'ada', 'scores': [10, 2.5, None], 'ok': True}

stringify({"a": [1, "x\ny"]})   # '{"a":[1,"x\\ny"]}'
parse('[1,]')                   # raises JsonError: ... (at index 3)
```

## What you'll build

Two mirror-image halves:

1. **Parser** — JSON text → Python objects, via recursive descent.
2. **Serializer** — Python objects → JSON text (`stringify`), the parser's
   inverse. Together they must round-trip: `parse(stringify(x)) == x`.

## How it works, in plain steps

**Step 1 — Learn the grammar.** JSON is tiny; that's the point. From
[json.org](https://www.json.org/json-en.html):

```
value  := object | array | string | number | "true" | "false" | "null"
object := '{' (string ':' value (',' string ':' value)*)? '}'
array  := '[' (value (',' value)*)? ']'
```

Nesting is free: `parse_value` calls `parse_object`, which calls
`parse_value` again. Recursion *is* the nesting.

**Step 2 — Build the cursor.** A `_Parser` holds the text and `self.pos`.
Helpers: `peek()` (look at the current char without consuming), `expect(ch)`
(consume it or raise), `skip_ws()` (eat spaces/tabs/newlines), and `error(msg)`
which raises `JsonError` with the index — good errors are half the project.

**Step 3 — Dispatch on the first character.** `parse_value` looks at one char
and picks the rule: `{`→object, `[`→array, `"`→string, `t/f/n`→literal,
`-`/digit→number, anything else→error. This one-character lookahead is what
makes it "recursive *descent*".

**Step 4 — Parse strings carefully.** Walk char by char until the closing
quote. On `\`, decode the escape (`\n`, `\"`, `\\`, …); on `\u`, read 4 hex
digits — and handle **surrogate pairs** (`\ud83d\ude00` = 😀), raising on lone
surrogates. Reject raw control characters (strict JSON forbids them).

**Step 5 — Parse numbers by hand.** Don't regex-and-`float()` it: consume
`-`, then the int part (rejecting leading zeros like `01`), then optional
`.digits` and `[eE][+-]?digits`. Return `int` when there's no fraction or
exponent, `float` otherwise. Hand-rolling is what lets you *reject* `1.`, `.5`,
`+1`, `1e` with clear errors instead of silently accepting them.

**Step 6 — Arrays and objects.** The classic loop: parse a value, then expect
`,` (keep going) or the closing bracket (done) — anything else is an error.
This shape is also what rejects trailing commas (`[1,]`), the most common
real-world JSON mistake.

**Step 7 — Write `stringify`.** A recursive mirror: `None`→`null`,
`True`→`true`, `str`→quoted+escaped, `int`→digits, `float`→`repr` (rejecting
`inf`/`nan`, which aren't valid JSON), `list`/`tuple`→`[...]`,
`dict`→`{...}` (keys must be strings). Check `bool` *before* `int` — in
Python, `True` is an instance of `int`!

## How to run

```bash
cd guides/json-parser
python3 -c "
from json import parse, stringify
print(parse('{\"a\": [1, 2.5, \"x\"]}'))
print(stringify({'a': [1, None]}))
"
```

## How to test

```bash
python3 test_json.py
```

81 checks: every JSON type, string escapes (`\n`, `\t`, `\"`, `\u0041`,
surrogate pairs), number shapes, nesting, whitespace tolerance, round-trips
(`parse(stringify(x)) == x` for 13 tricky values), and 30 invalid inputs that
must raise `JsonError` — trailing commas, leading zeros, truncated input,
bad escapes, lone surrogates, `stringify(float('inf'))`, non-string keys…

## Stretch exercises

1. **Pretty-printing.** Add `stringify(obj, indent=2)` producing indented,
   human-readable JSON.
2. **Duplicate-key detection.** Real parsers disagree on `{"a":1,"a":2}` —
   add a strict mode that raises `JsonError` on duplicate keys.
3. **Big numbers.** Python ints are arbitrary precision, but JSON
   doubles aren't — add an option to parse floats as `decimal.Decimal`
   for lossless money math.

## Further reading

- The JSON grammar, on one page — https://www.json.org/json-en.html
- RFC 8259, the actual spec — https://www.rfc-editor.org/rfc/rfc8259
- *Crafting Interpreters*, chapters 4–6 — https://craftinginterpreters.com/
  (the same recursive-descent technique, applied to a full language)
