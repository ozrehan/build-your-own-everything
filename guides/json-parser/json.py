#!/usr/bin/env python3
"""
json.py -- a JSON parser from scratch (recursive descent), plus a serializer.

JSON's grammar maps beautifully onto recursive functions: an object
contains values, a value can be an object, an array contains values...
Each grammar rule becomes one parse_* method, and nesting takes care
of itself through recursion.

Public API:
    parse(text)    -> Python objects (null->None, true->True, false->False)
    stringify(obj) -> JSON text

    parse('{"a": [1, 2.5, "x\\n"]}')  ->  {'a': [1, 2.5, 'x\n']}
    stringify({'a': [1, None]})       ->  '{"a":[1,null]}'

Invalid input raises JsonError with a message saying where and why.

Stdlib only. No dependencies.
"""


class JsonError(Exception):
    """Raised for any invalid JSON input (or unserializable object)."""


# ---------------------------------------------------------------------------
# Parser -- a recursive descent parser. One method per grammar rule:
#
#   value   := object | array | string | number | "true" | "false" | "null"
#   object  := '{' (string ':' value (',' string ':' value)*)? '}'
#   array   := '[' (value (',' value)*)? ']'
# ---------------------------------------------------------------------------

class _Parser:
    def __init__(self, text):
        self.text = text
        self.pos = 0

    # -- cursor helpers --------------------------------------------------
    def peek(self):
        if self.pos < len(self.text):
            return self.text[self.pos]
        return None

    def error(self, msg):
        raise JsonError("%s (at index %d)" % (msg, self.pos))

    def expect(self, ch):
        if self.peek() != ch:
            self.error("expected %r, found %r" % (ch, self.peek()))
        self.pos += 1

    def skip_ws(self):
        while self.peek() in (" ", "\t", "\n", "\r"):
            self.pos += 1

    # -- entry point ------------------------------------------------------
    def parse(self):
        self.skip_ws()
        value = self.parse_value()
        self.skip_ws()
        if self.pos != len(self.text):
            self.error("unexpected trailing data %r"
                       % self.text[self.pos:self.pos + 10])
        return value

    # -- grammar rules -----------------------------------------------------
    def parse_value(self):
        c = self.peek()
        if c == "{":
            return self.parse_object()
        if c == "[":
            return self.parse_array()
        if c == '"':
            return self.parse_string()
        if c == "t":
            return self.parse_literal("true", True)
        if c == "f":
            return self.parse_literal("false", False)
        if c == "n":
            return self.parse_literal("null", None)
        if c == "-" or (c is not None and "0" <= c <= "9"):
            return self.parse_number()
        self.error("unexpected character %r" % c)

    def parse_literal(self, word, value):
        if self.text[self.pos:self.pos + len(word)] != word:
            self.error("invalid literal, expected %r" % word)
        self.pos += len(word)
        return value

    def parse_string(self):
        self.expect('"')
        out = []
        while True:
            if self.pos >= len(self.text):
                self.error("unterminated string")
            c = self.text[self.pos]
            if c == '"':
                self.pos += 1
                return "".join(out)
            if c == "\\":
                out.append(self.parse_escape())
            elif ord(c) < 0x20:
                self.error("unescaped control character in string")
            else:
                out.append(c)
                self.pos += 1

    def parse_escape(self):
        """Cursor is ON the backslash; returns the decoded character."""
        self.pos += 1  # consume backslash
        if self.pos >= len(self.text):
            self.error("unterminated escape sequence")
        e = self.text[self.pos]
        self.pos += 1
        simple = {'"': '"', "\\": "\\", "/": "/",
                  "b": "\b", "f": "\f", "n": "\n",
                  "r": "\r", "t": "\t"}
        if e in simple:
            return simple[e]
        if e == "u":
            return self.parse_unicode_escape()
        self.error("bad escape '\\%s'" % e)

    def parse_unicode_escape(self):
        """Cursor is just AFTER the 'u' in \\uXXXX; handles surrogate pairs."""
        code = self.parse_hex4("bad \\u escape")
        # A high surrogate must be followed by \uDC00-\uDFFF (one character).
        if 0xD800 <= code <= 0xDBFF:
            if self.text[self.pos:self.pos + 2] == "\\u":
                self.pos += 2
                low = self.parse_hex4("bad low surrogate in \\u escape")
                if 0xDC00 <= low <= 0xDFFF:
                    code = 0x10000 + (code - 0xD800) * 0x400 + (low - 0xDC00)
                else:
                    self.error("lone high surrogate in \\u escape")
            else:
                self.error("lone high surrogate in \\u escape")
        elif 0xDC00 <= code <= 0xDFFF:
            self.error("lone low surrogate in \\u escape")
        try:
            return chr(code)
        except ValueError:
            self.error("invalid code point in \\u escape")

    def parse_hex4(self, what):
        digits = self.text[self.pos:self.pos + 4]
        if len(digits) < 4 or any(d not in "0123456789abcdefABCDEF"
                                  for d in digits):
            self.error(what)
        self.pos += 4
        return int(digits, 16)

    def parse_number(self):
        # -?(0|[1-9][0-9]*)(\.[0-9]+)?([eE][+-]?[0-9]+)?
        # Built by hand, char by char, so bad numbers fail loudly.
        start = self.pos
        if self.peek() == "-":
            self.pos += 1
        c = self.peek()
        if c == "0":
            self.pos += 1
        elif c is not None and "1" <= c <= "9":
            while self.peek() is not None and "0" <= self.peek() <= "9":
                self.pos += 1
        else:
            self.error("bad number")
        is_float = False
        if self.peek() == ".":
            is_float = True
            self.pos += 1
            if not (self.peek() is not None and "0" <= self.peek() <= "9"):
                self.error("bad number: '.' must be followed by a digit")
            while self.peek() is not None and "0" <= self.peek() <= "9":
                self.pos += 1
        if self.peek() in ("e", "E"):
            is_float = True
            self.pos += 1
            if self.peek() in ("+", "-"):
                self.pos += 1
            if not (self.peek() is not None and "0" <= self.peek() <= "9"):
                self.error("bad number: exponent needs a digit")
            while self.peek() is not None and "0" <= self.peek() <= "9":
                self.pos += 1
        raw = self.text[start:self.pos]
        return float(raw) if is_float else int(raw)

    def parse_array(self):
        self.expect("[")
        self.skip_ws()
        items = []
        if self.peek() == "]":
            self.pos += 1
            return items
        while True:
            self.skip_ws()
            items.append(self.parse_value())
            self.skip_ws()
            c = self.peek()
            if c == ",":
                self.pos += 1
                continue
            if c == "]":
                self.pos += 1
                return items
            self.error("expected ',' or ']' in array")

    def parse_object(self):
        self.expect("{")
        self.skip_ws()
        obj = {}
        if self.peek() == "}":
            self.pos += 1
            return obj
        while True:
            self.skip_ws()
            if self.peek() != '"':
                self.error("expected string key in object")
            key = self.parse_string()
            self.skip_ws()
            self.expect(":")
            self.skip_ws()
            obj[key] = self.parse_value()  # later duplicate keys win
            self.skip_ws()
            c = self.peek()
            if c == ",":
                self.pos += 1
                continue
            if c == "}":
                self.pos += 1
                return obj
            self.error("expected ',' or '}' in object")


def parse(text):
    """Parse a JSON document into Python objects."""
    if not isinstance(text, str):
        raise JsonError("parse() needs a string, got %s"
                        % type(text).__name__)
    return _Parser(text).parse()


# ---------------------------------------------------------------------------
# Serializer -- Python objects -> JSON text. The mirror image of the parser.
# ---------------------------------------------------------------------------

# Short escapes used when writing strings (anything else < 0x20 -> \u00XX).
_ENCODE_ESCAPES = {'"': '\\"', "\\": "\\\\", "\b": "\\b", "\f": "\\f",
                   "\n": "\\n", "\r": "\\r", "\t": "\\t"}


def _encode_string(s):
    out = ['"']
    for c in s:
        if c in _ENCODE_ESCAPES:
            out.append(_ENCODE_ESCAPES[c])
        elif ord(c) < 0x20:
            out.append("\\u%04x" % ord(c))
        else:
            out.append(c)
    out.append('"')
    return "".join(out)


def stringify(obj):
    """Serialize Python objects to a JSON document string."""
    if obj is None:
        return "null"
    if obj is True:
        return "true"
    if obj is False:
        return "false"
    if isinstance(obj, str):
        return _encode_string(obj)
    if isinstance(obj, int):  # (bool handled above -- bool is a subclass)
        return str(obj)
    if isinstance(obj, float):
        if obj != obj or obj in (float("inf"), float("-inf")):
            raise JsonError("cannot stringify non-finite float %r" % obj)
        return repr(obj)
    if isinstance(obj, (list, tuple)):
        return "[" + ",".join(stringify(x) for x in obj) + "]"
    if isinstance(obj, dict):
        parts = []
        for key, value in obj.items():
            if not isinstance(key, str):
                raise JsonError("object keys must be strings, got %s"
                                % type(key).__name__)
            parts.append(_encode_string(key) + ":" + stringify(value))
        return "{" + ",".join(parts) + "}"
    raise JsonError("cannot stringify object of type %s"
                    % type(obj).__name__)
