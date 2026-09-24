#!/usr/bin/env python3
"""Tests for the mini template engine. Run with: python3 test_template.py"""
import sys
sys.path.insert(0, ".")
from template import render


def test_variables():
    assert render("Hello {{ name }}!", {"name": "Ada"}) == "Hello Ada!"
    print("PASS: variable interpolation")


def test_dotted_variables():
    out = render("{{ user.name }} is {{ user.role }}", {"user": {"name": "Bob", "role": "admin"}})
    assert out == "Bob is admin", repr(out)
    print("PASS: dotted variable paths")


def test_missing_var_renders_empty():
    assert render("[{{ nope }}]", {}) == "[]"
    assert render("[{{ user.name }}]", {"user": {}}) == "[]"
    print("PASS: missing variables render as empty string")


def test_if_true_and_false():
    assert render("{% if show %}yes{% endif %}", {"show": True}) == "yes"
    assert render("{% if show %}yes{% endif %}", {"show": False}) == ""
    assert render("{% if show %}yes{% endif %}", {}) == ""
    print("PASS: if true/false branches")


def test_for_loop():
    out = render("{% for x in xs %}{{ x }},{% endfor %}", {"xs": [1, 2, 3]})
    assert out == "1,2,3,", repr(out)
    print("PASS: for loops")


def test_nested_loop():
    tpl = "{% for row in rows %}{% for c in row %}{{ c }}{% endfor %};{% endfor %}"
    out = render(tpl, {"rows": [[1, 2], [3]]})
    assert out == "12;3;", repr(out)
    print("PASS: nested loops")


def test_comments_removed():
    out = render("a{# hidden #}b", {})
    assert out == "ab", repr(out)
    out = render("{# {{ not_a_var }} #}x", {})
    assert out == "x", repr(out)
    print("PASS: comments stripped")


def test_mixed_template():
    tpl = "Hi {{ name }}!{% if admin %} (admin){% endif %}{% for t in todos %} [{{ t }}]{% endfor %}"
    out = render(tpl, {"name": "Zed", "admin": True, "todos": ["a", "b"]})
    assert out == "Hi Zed! (admin) [a] [b]", repr(out)
    print("PASS: mixed template")


if __name__ == "__main__":
    test_variables()
    test_dotted_variables()
    test_missing_var_renders_empty()
    test_if_true_and_false()
    test_for_loop()
    test_nested_loop()
    test_comments_removed()
    test_mixed_template()
    print("\nAll template engine tests passed.")
