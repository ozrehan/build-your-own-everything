#!/usr/bin/env python3
"""Tests for regex.py -- run with: python3 test_regex.py"""
from regex import match, search, RegexError

passed = failed = 0


def check(name, got, want):
    global passed, failed
    if got == want:
        passed += 1
        print("ok   " + name)
    else:
        failed += 1
        print("FAIL %s: got %r, want %r" % (name, got, want))


def check_raises(name, pattern):
    global passed, failed
    try:
        match(pattern, "")
    except RegexError:
        passed += 1
        print("ok   " + name)
    except Exception as e:
        failed += 1
        print("FAIL %s: wrong exception %r" % (name, e))
    else:
        failed += 1
        print("FAIL %s: no RegexError raised" % name)


# --- literals ---------------------------------------------------------------
check("literal full match", match("abc", "abc"), True)
check("literal too short", match("abc", "ab"), False)
check("literal too long", match("abc", "abcd"), False)
check("empty pattern matches empty", match("", ""), True)
check("empty pattern vs text", match("", "a"), False)

# --- dot --------------------------------------------------------------------
check("dot matches one char", match("a.c", "abc"), True)
check("dot needs a char", match("a.c", "ac"), False)
check("dot matches any char", match(".", "z"), True)

# --- star -------------------------------------------------------------------
check("star: zero reps", match("a*b", "b"), True)
check("star: many reps", match("a*b", "aaab"), True)
check("star: wrong tail", match("a*b", "aac"), False)
check("star: empty on empty", match("a*", ""), True)
check("star: backtrack needed", match("a*a", "aaa"), True)

# --- plus / question ---------------------------------------------------------
check("plus: needs one", match("a+", ""), False)
check("plus: many", match("a+", "aaa"), True)
check("question: absent", match("colou?r", "color"), True)
check("question: present", match("colou?r", "colour"), True)
check("question: too many", match("colou?r", "colouur"), False)

# --- alternation & groups ----------------------------------------------------
check("alt: left", match("cat|dog", "cat"), True)
check("alt: right", match("cat|dog", "dog"), True)
check("alt: neither", match("cat|dog", "cow"), False)
check("grouped star", match("(ab)+", "abab"), True)
check("grouped star single", match("(ab)+", "ab"), True)
check("grouped star partial", match("(ab)+", "aba"), False)
check("alt star then c", match("(a|b)*c", "ababc"), True)
check("alt star missing c", match("(a|b)*c", "abab"), False)
check("empty group", match("a()b", "ab"), True)
check("empty alt branch", match("a|", ""), True)

# --- anchors -----------------------------------------------------------------
check("anchor start ok", match("^abc", "abc"), True)
check("search anchored start fails mid", search("^abc", "xabc"), False)
check("search anchored end", search("abc$", "xabc"), True)
check("search anchored end fails", search("abc$", "abcx"), False)
check("both anchors", match("^a*$", "aaa"), True)
check("both anchors fail", match("^a*$", "aaab"), False)
check("anchor is positional", match("a^b", "a^b"), False)

# --- character classes --------------------------------------------------------
check("class: member", match("[abc]", "b"), True)
check("class: non-member", match("[abc]", "d"), False)
check("class: range", match("[a-z]+", "hello"), True)
check("class: range fail", match("[a-z]", "A"), False)
check("class: negated", match("[^0-9]+", "abc"), True)
check("class: negated fail", match("[^0-9]", "5"), False)
check("class: literal dash", match("[-a]", "-"), True)
check("class: literal bracket", match("[]a]", "]"), True)
check("class: digit set", match("[\\d]+", "123"), True)

# --- escapes ------------------------------------------------------------------
check("escape d", match("\\d+", "123"), True)
check("escape d fail", match("\\d", "a"), False)
check("escape w", match("\\w+", "abc_123"), True)
check("escape s", match("\\s", " "), True)
check("escape s fail", match("\\s", "x"), False)
check("escaped dot literal", match("\\.", "."), True)
check("escaped dot not wildcard", match("\\.", "a"), False)
check("escaped star", match("a\\*b", "a*b"), True)
check("escaped backslash", match("\\\\", "\\"), True)
check("newline escape", match("a\\nb", "a\nb"), True)

# --- search vs match ------------------------------------------------------------
check("search finds mid", search("b", "abc"), True)
check("match rejects mid", match("b", "abc"), False)
check("search with dot", search("a.c", "xxabcxx"), True)
check("search no hit", search("z+", "abc"), False)

# --- tricky backtracking --------------------------------------------------------
check("greedy star backtracks", match("a*b", "aaab"), True)
check("alt order backtrack", match("(a|ab)*", "ab"), True)
check("search alt-star", search("(a|b)*c", "zzababc"), True)
check("optional chain", match("a?a?a?b", "aab"), True)
check("nested stars terminate", match("(a*)*", "aaa"), True)
check("star-heavy stays fast", match("a*a*a*b", "aaaa"), False)

# --- invalid patterns --------------------------------------------------------------
check_raises("unbalanced paren", "(ab")
check_raises("stray close paren", "a)b")
check_raises("unterminated class", "[abc")
check_raises("dangling star", "*a")
check_raises("dangling plus", "a**")
check_raises("trailing backslash", "ab\\")
check_raises("bad escape", "\\q")
check_raises("bad range", "[z-a]")

print("\n%d passed, %d failed" % (passed, failed))
raise SystemExit(1 if failed else 0)
