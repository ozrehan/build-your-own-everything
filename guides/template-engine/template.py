#!/usr/bin/env python3
"""Build your own template engine.

A mini Jinja-style template engine with one public function:

    render(template_str, context) -> str

Supported syntax:
    {{ var }}               variable interpolation (dotted paths: {{ user.name }})
    {% if flag %}...{% endif %}   include the block if `flag` is truthy
    {% for x in xs %}...{% endfor %}   loop over a list
    {# comment #}           stripped from the output

How it works: the template is tokenized with a regex, parsed into a small
tree of nodes (text / var / if / for), and the tree is rendered against the
context dict. Missing variables render as an empty string.
"""

import re

# Split the template into literal text and {{ }}, {% %}, {# #} tags.
TOKEN_RE = re.compile(r"({{.*?}}|{%.*?%}|{#.*?#})", re.DOTALL)


def _resolve(expr, context):
    """Look up a dotted name like 'user.name' in the context dict.
    Returns "" when any part is missing."""
    value = context
    for part in expr.strip().split("."):
        if isinstance(value, dict):
            value = value.get(part)
        elif isinstance(value, (list, tuple)):
            try:
                value = value[int(part)]
            except (ValueError, IndexError):
                return ""
        else:
            value = getattr(value, part, None)
        if value is None:
            return ""
    return value


def _parse(tokens, pos, end_tags):
    """Parse tokens into a node list. Stops when a tag in `end_tags` is hit,
    returning (nodes, new_pos). Nested blocks recurse naturally."""
    nodes = []
    while pos < len(tokens):
        tok = tokens[pos]
        if tok.startswith("{#"):
            pos += 1  # comments are stripped
        elif tok.startswith("{{"):
            nodes.append(("var", tok[2:-2].strip()))
            pos += 1
        elif tok.startswith("{%"):
            tag = tok[2:-2].strip()
            if tag in end_tags:
                return nodes, pos + 1
            parts = tag.split()
            if parts and parts[0] == "if" and len(parts) == 2:
                body, pos = _parse(tokens, pos + 1, {"endif"})
                nodes.append(("if", parts[1], body))
            elif parts and parts[0] == "for" and len(parts) == 4 and parts[2] == "in":
                body, pos = _parse(tokens, pos + 1, {"endfor"})
                nodes.append(("for", parts[1], parts[3], body))
            else:
                pos += 1  # unknown tag: skip it
        else:
            nodes.append(("text", tok))
            pos += 1
    return nodes, pos


def _render_nodes(nodes, context):
    out = []
    for node in nodes:
        kind = node[0]
        if kind == "text":
            out.append(node[1])
        elif kind == "var":
            value = _resolve(node[1], context)
            out.append("" if value is None else str(value))
        elif kind == "if":
            if _resolve(node[1], context):  # truthiness check
                out.append(_render_nodes(node[2], context))
        elif kind == "for":
            items = _resolve(node[2], context)
            if not isinstance(items, (list, tuple)):
                items = []
            for item in items:
                # The loop variable shadows anything in the outer context,
                # but only inside the loop body.
                child = dict(context)
                child[node[1]] = item
                out.append(_render_nodes(node[3], child))
    return "".join(out)


def render(template_str, context):
    """Render `template_str` against the `context` dict and return a string."""
    tokens = TOKEN_RE.split(template_str)
    nodes, _ = _parse(tokens, 0, set())
    return _render_nodes(nodes, context)


if __name__ == "__main__":
    template = """Hello {{ user.name }}!
{# this comment disappears #}
{% if user.admin %}You have admin powers.{% endif %}
Your tasks:
{% for task in tasks %}- {{ task.title }} (done: {{ task.done }})
{% endfor %}"""
    context = {
        "user": {"name": "Ada", "admin": True},
        "tasks": [
            {"title": "Write code", "done": True},
            {"title": "Ship it", "done": False},
        ],
    }
    print(render(template, context))
