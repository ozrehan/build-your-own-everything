#!/usr/bin/env python3
"""
regex.py -- a tiny regular expression engine, built from scratch.

A regex engine works in two phases (just like real ones):

    1. PARSE the pattern string into an AST (abstract syntax tree).
    2. MATCH the AST against text with a backtracking matcher.

Public API:
    match(pattern, text) -> bool   # True if the WHOLE text matches
    search(pattern, text) -> bool  # True if the pattern matches ANYWHERE

Supported syntax:
    abc          literal characters
    .            any single character
    a*  a+  a?   zero-or-more / one-or-more / optional
    a|b          alternation ("a or b")
    (ab)+        groups
    ^abc  xyz$   anchors: start-of-text / end-of-text
    [abc]        character class (one of a, b, c)
    [a-z]        character range
    [^abc]       negated class (anything EXCEPT a, b, c)
    \\d \\w \\s   digit / word-character / whitespace classes
    \\. \\* ...  backslash turns a metacharacter into a literal

Stdlib only. No dependencies.
"""


class RegexError(Exception):
    """Raised when a pattern is invalid."""


# ---------------------------------------------------------------------------
# 1. AST nodes -- one tiny class per pattern construct.
#    The parser builds these; the matcher interprets them.
# ---------------------------------------------------------------------------

class Lit:
    """A literal character, e.g. the `a` in `abc`."""
    def __init__(self, char):
        self.char = char
    def __repr__(self):
        return "Lit(%r)" % self.char


class Dot:
    """`.` -- matches any single character."""
    def __repr__(self):
        return "Dot()"


class Empty:
    """Matches the empty string (the empty side of `a|`, or `()`)."""
    def __repr__(self):
        return "Empty()"


class Seq:
    """Concatenation: match each node in order, e.g. `abc`."""
    def __init__(self, nodes):
        self.nodes = nodes
    def __repr__(self):
        return "Seq(%r)" % (self.nodes,)


class Alt:
    """Alternation: match left OR right, e.g. `a|b`."""
    def __init__(self, left, right):
        self.left = left
        self.right = right
    def __repr__(self):
        return "Alt(%r, %r)" % (self.left, self.right)


class Star:
    """`x*` -- zero or more repetitions of x."""
    def __init__(self, node):
        self.node = node
    def __repr__(self):
        return "Star(%r)" % (self.node,)


class Plus:
    """`x+` -- one or more repetitions of x."""
    def __init__(self, node):
        self.node = node
    def __repr__(self):
        return "Plus(%r)" % (self.node,)


class Question:
    """`x?` -- zero or one occurrence of x."""
    def __init__(self, node):
        self.node = node
    def __repr__(self):
        return "Question(%r)" % (self.node,)


class AnchorStart:
    """`^` -- matches only at the very start of the text."""
    def __repr__(self):
        return "AnchorStart()"


class AnchorEnd:
    """`$` -- matches only at the very end of the text."""
    def __repr__(self):
        return "AnchorEnd()"


class CharClass:
    """`[abc]`, `[a-z]`, `[^0-9]` -- matches one char from (or not from) a set."""
    def __init__(self, chars, negated=False):
        self.chars = frozenset(chars)
        self.negated = negated
    def matches(self, char):
        hit = char in self.chars
        return (not hit) if self.negated else hit
    def __repr__(self):
        return "CharClass(negated=%r, %r)" % (self.negated, set(self.chars))


class Group:
    """`(...)` -- groups its inner node (no capture groups in this engine)."""
    def __init__(self, node):
        self.node = node
    def __repr__(self):
        return "Group(%r)" % (self.node,)


# Prebuilt character sets for \d \w \s (also usable inside [...])
_DIGITS = frozenset("0123456789")
_WORD = frozenset(
    "abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789_")
_WHITESPACE = frozenset(" \t\n\r\f\v")

# Backslash escapes that produce a single literal character.
_SIMPLE_ESCAPES = {"n": "\n", "t": "\t", "r": "\r",
                   "\\": "\\", "'": "'", '"': '"'}


# ---------------------------------------------------------------------------
# 2. Parser -- pattern string -> AST. A recursive descent parser:
#
#       regex      := alt
#       alt        := concat ('|' concat)*
#       concat     := quantified*
#       quantified := atom ('*' | '+' | '?')?
#       atom       := '(' regex ')' | '[' class ']' | '.' | '^' | '$'
#                    | '\' escape | literal-char
# ---------------------------------------------------------------------------

class _Parser:
    def __init__(self, pattern):
        self.pattern = pattern
        self.pos = 0

    # -- cursor helpers --------------------------------------------------
    def peek(self):
        if self.pos < len(self.pattern):
            return self.pattern[self.pos]
        return None

    def advance(self):
        ch = self.pattern[self.pos]
        self.pos += 1
        return ch

    def error(self, msg):
        raise RegexError("%s (at index %d of %r)"
                         % (msg, self.pos, self.pattern))

    # -- grammar rules ----------------------------------------------------
    def parse(self):
        node = self.parse_alt()
        if self.pos != len(self.pattern):
            self.error("unexpected %r" % self.peek())
        return node

    def parse_alt(self):
        left = self.parse_concat()
        while self.peek() == "|":
            self.advance()
            left = Alt(left, self.parse_concat())
        return left

    def parse_concat(self):
        nodes = []
        while self.peek() is not None and self.peek() not in "|)":
            nodes.append(self.parse_quantified())
        if not nodes:
            return Empty()
        if len(nodes) == 1:
            return nodes[0]
        return Seq(nodes)

    def parse_quantified(self):
        node = self.parse_atom()
        c = self.peek()
        if c == "*":
            self.advance()
            return Star(node)
        if c == "+":
            self.advance()
            return Plus(node)
        if c == "?":
            self.advance()
            return Question(node)
        return node

    def parse_atom(self):
        c = self.peek()
        if c == "(":
            self.advance()
            node = self.parse_alt()
            if self.peek() != ")":
                self.error("unbalanced '(' -- expected ')'")
            self.advance()
            return Group(node)
        if c == "[":
            return self.parse_class()
        if c == ".":
            self.advance()
            return Dot()
        if c == "^":
            self.advance()
            return AnchorStart()
        if c == "$":
            self.advance()
            return AnchorEnd()
        if c == "\\":
            return self.parse_escape()
        if c in "*+?|)":
            self.error("dangling metacharacter %r" % c)
        self.advance()  # anything else is a literal character
        return Lit(c)

    def parse_escape(self):
        """Parse `\\x` outside a class; cursor is ON the backslash."""
        self.advance()  # consume backslash
        c = self.peek()
        if c is None:
            self.error("pattern ends with a backslash")
        self.advance()
        if c in _SIMPLE_ESCAPES:
            return Lit(_SIMPLE_ESCAPES[c])
        if c == "d":
            return CharClass(_DIGITS)
        if c == "w":
            return CharClass(_WORD)
        if c == "s":
            return CharClass(_WHITESPACE)
        if c in r".*+?|()[]{}^$":
            return Lit(c)  # escaped metacharacter -> literal
        self.error("bad escape '\\%s'" % c)

    # -- character classes -------------------------------------------------
    def class_char(self):
        """Read one class element; cursor is ON the char (or backslash).

        Returns a one-character string, or a frozenset for \d \w \s."""
        c = self.peek()
        if c == "\\":
            self.advance()
            e = self.peek()
            if e is None:
                self.error("pattern ends with a backslash")
            self.advance()
            if e in _SIMPLE_ESCAPES:
                return _SIMPLE_ESCAPES[e]
            if e == "d":
                return _DIGITS
            if e == "w":
                return _WORD
            if e == "s":
                return _WHITESPACE
            if e in r"\]-^":
                return e
            self.error("bad escape '\\%s' in character class" % e)
        self.advance()
        return c

    def parse_class(self):
        self.advance()  # consume '['
        negated = False
        if self.peek() == "^":
            self.advance()
            negated = True
        chars = set()
        first = True  # a ']' or '-' first is a literal, not syntax
        while True:
            c = self.peek()
            if c is None:
                self.error("unterminated '[' -- expected ']'")
            if c == "]" and not first:
                self.advance()
                break
            lo = self.class_char()
            if isinstance(lo, frozenset):
                # \d \w \s inside a class: union the whole set in.
                chars.update(lo)
            elif (self.peek() == "-" and
                    self.pos + 1 < len(self.pattern) and
                    self.pattern[self.pos + 1] != "]"):
                # A range like a-z: '-' counts only if a char follows it.
                self.advance()  # consume '-'
                hi = self.class_char()
                if isinstance(hi, frozenset) or ord(hi) < ord(lo):
                    self.error("bad range %r-%r" % (lo, hi))
                chars.update(chr(i) for i in range(ord(lo), ord(hi) + 1))
            else:
                chars.add(lo)
            first = False
        return CharClass(chars, negated)


# ---------------------------------------------------------------------------
# 3. Matcher -- AST + text -> set of reachable end positions.
#
#    _match(node, text, pos) returns the SET of positions where matching
#    `node` starting at `pos` can end. Sets (not single positions) are the
#    trick: they express backtracking naturally ("try every possibility"),
#    and they keep patterns like `a*a*a*` polynomial instead of
#    exponential -- positions are bounded by len(text), so the search
#    space can never explode.
# ---------------------------------------------------------------------------

def _match(node, text, pos):
    """Set of end positions after matching `node` at `pos`."""
    if isinstance(node, Empty):
        return {pos}
    if isinstance(node, Lit):
        if pos < len(text) and text[pos] == node.char:
            return {pos + 1}
        return set()
    if isinstance(node, Dot):
        if pos < len(text):
            return {pos + 1}
        return set()
    if isinstance(node, CharClass):
        if pos < len(text) and node.matches(text[pos]):
            return {pos + 1}
        return set()
    if isinstance(node, AnchorStart):
        return {pos} if pos == 0 else set()
    if isinstance(node, AnchorEnd):
        return {pos} if pos == len(text) else set()
    if isinstance(node, Group):
        return _match(node.node, text, pos)
    if isinstance(node, Seq):
        positions = {pos}
        for child in node.nodes:
            nxt = set()
            for p in positions:
                nxt |= _match(child, text, p)
            positions = nxt
            if not positions:
                break
        return positions
    if isinstance(node, Alt):
        return _match(node.left, text, pos) | _match(node.right, text, pos)
    if isinstance(node, Question):
        return {pos} | _match(node.node, text, pos)
    if isinstance(node, Star):
        # Flood-fill: keep matching the inner node from every position
        # reached so far, until no new positions appear. Always terminates:
        # positions are bounded by len(text), and we never revisit one.
        # (This is also why `(a?)*` can't loop forever.)
        seen = {pos}
        stack = [pos]
        while stack:
            p = stack.pop()
            for q in _match(node.node, text, p):
                if q not in seen:
                    seen.add(q)
                    stack.append(q)
        return seen
    if isinstance(node, Plus):
        # One occurrence, then zero or more.
        out = set()
        for p in _match(node.node, text, pos):
            out |= _match(Star(node.node), text, p)
        return out
    raise RegexError("unknown AST node: %r" % (node,))


# ---------------------------------------------------------------------------
# 4. Public API
# ---------------------------------------------------------------------------

def _compile(pattern):
    if not isinstance(pattern, str):
        raise RegexError("pattern must be a string")
    return _Parser(pattern).parse()


def match(pattern, text):
    """True if `pattern` matches the ENTIRE `text` (like re.fullmatch)."""
    return len(text) in _match(_compile(pattern), text, 0)


def search(pattern, text):
    """True if `pattern` matches ANYWHERE inside `text` (like re.search)."""
    ast = _compile(pattern)
    for start in range(len(text) + 1):
        if _match(ast, text, start):
            return True
    return False
