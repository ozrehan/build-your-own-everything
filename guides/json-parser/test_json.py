#!/usr/bin/env python3
"""Tests for json.py -- run with: python3 test_json.py"""
from json import parse, stringify, JsonError

passed = failed = 0


def check(name, got, want):
    global passed, failed
    if got == want and type(got) == type(want):
        passed += 1
        print("ok   " + name)
    else:
        failed += 1
        print("FAIL %s: got %r (%s), want %r (%s)"
              % (name, got, type(got).__name__, want, type(want).__name__))


def check_raises(name, func, *args):
    global passed, failed
    try:
        func(*args)
    except JsonError:
        passed += 1
        print("ok   " + name)
    except Exception as e:
        failed += 1
        print("FAIL %s: wrong exception %r" % (name, e))
    else:
        failed += 1
        print("FAIL %s: no JsonError raised" % name)


# --- literals ------------------------------------------------------------------
check("null", parse("null"), None)
check("true", parse("true"), True)
check("false", parse("false"), False)
check("int", parse("123"), 123)
check("negative int", parse("-45"), -45)
check("zero", parse("0"), 0)
check("float", parse("3.14"), 3.14)
check("negative float", parse("-2.5"), -2.5)
check("exponent", parse("1e3"), 1000.0)
check("exponent neg", parse("-2.5E-2"), -0.025)
check("exponent plus", parse("1E+2"), 100.0)

# --- strings ---------------------------------------------------------------------
check("simple string", parse('"hello"'), "hello")
check("escapes", parse(r'"a\nb\t\"\\\/"'), 'a\nb\t"\\/')
check("unicode escape", parse(r'"\u0041"'), "A")
check("surrogate pair", parse(r'"\ud83d\ude00"'), "\U0001F600")
check("empty string", parse('""'), "")
check("string with spaces", parse('"  x  "'), "  x  ")

# --- arrays & objects ---------------------------------------------------------------
check("empty array", parse("[]"), [])
check("empty object", parse("{}"), {})
check("array", parse("[1, 2, 3]"), [1, 2, 3])
check("nested", parse('[1, [2, [3]], {"a": null}]'), [1, [2, [3]], {"a": None}])
check("object", parse('{"a": 1, "b": true}'), {"a": 1, "b": True})
check("deep nesting", parse('{"a":{"b":{"c":[1,{"d":2}]}}}'),
      {"a": {"b": {"c": [1, {"d": 2}]}}})
check("whitespace everywhere", parse('  { "a" : [1 , 2 ] }  '), {"a": [1, 2]})
check("mixed array", parse('[null, true, "x", 1.5]'), [None, True, "x", 1.5])

# --- stringify -------------------------------------------------------------------------
check("stringify null", stringify(None), "null")
check("stringify true", stringify(True), "true")
check("stringify false", stringify(False), "false")
check("stringify int", stringify(42), "42")
check("stringify float", stringify(2.5), "2.5")
check("stringify string", stringify("hi"), '"hi"')
check("stringify escapes", stringify('a\nb\t"q"\\'), '"a\\nb\\t\\"q\\"\\\\"')
check("stringify control char", stringify("\x01"), '"\\u0001"')
check("stringify array", stringify([1, None, "x"]), '[1,null,"x"]')
check("stringify object", stringify({"b": 2, "a": 1}), '{"b":2,"a":1}')
check("stringify nested", stringify({"a": [1, {"b": False}]}),
      '{"a":[1,{"b":false}]}')

# --- round trips --------------------------------------------------------------------------
for value in [None, True, False, 0, -17, 3.14, "", "a\nb\t\"q\"\\",
              [], [1, [2.5, "x"]], {}, {"a": 1, "b": [None, {"c": "d"}]},
              "\U0001F600"]:
    check("round-trip %r" % (value,), parse(stringify(value)), value)
check("round-trip keeps key order",
      stringify(parse('{"b":2,"a":1}')), '{"b":2,"a":1}')

# --- invalid JSON must raise -----------------------------------------------------------------
check_raises("trailing comma in array", parse, "[1,]")
check_raises("trailing comma in object", parse, '{"a":1,}')
check_raises("unquoted key", parse, "{a:1}")
check_raises("single quotes", parse, "'hi'")
check_raises("leading zero", parse, "[01]")
check_raises("bare leading zero", parse, "01")
check_raises("missing comma", parse, "[1 2]")
check_raises("missing colon", parse, '{"a" 1}')
check_raises("truncated object", parse, '{"a":1')
check_raises("truncated array", parse, "[1,2")
check_raises("empty input", parse, "")
check_raises("whitespace only", parse, "   ")
check_raises("bad literal", parse, "nul")
check_raises("capitalized True", parse, "True")
check_raises("dangling minus", parse, "-")
check_raises("plus sign", parse, "+1")
check_raises("double minus", parse, "--1")
check_raises("trailing dot", parse, "1.")
check_raises("leading dot", parse, ".5")
check_raises("bad exponent", parse, "1e")
check_raises("unterminated string", parse, '"abc')
check_raises("bad escape", parse, r'"\q"')
check_raises("unescaped control char", parse, '"\x01"')
check_raises("lone high surrogate", parse, r'"\ud83d"')
check_raises("trailing data", parse, '{} {}')
check_raises("trailing comma text", parse, '{"a":1} x')
check_raises("non-string input", parse, 123)
check_raises("stringify inf", stringify, float("inf"))
check_raises("stringify nan", stringify, float("nan"))
check_raises("stringify non-string key", stringify, {1: "a"})
check_raises("stringify set", stringify, {1, 2})

print("\n%d passed, %d failed" % (passed, failed))
raise SystemExit(1 if failed else 0)
