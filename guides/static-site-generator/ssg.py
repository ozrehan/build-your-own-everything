#!/usr/bin/env python3
"""ssg.py -- a tiny static site generator.

Reads Markdown files from ./content/, converts a Markdown subset to HTML,
wraps each page in an HTML layout, and writes the result to ./site/.
Also generates an index page and copies ./static/ assets if present.

Usage:
    python3 ssg.py                        # build sample content into ./site/
    python3 ssg.py <content> <output>     # build custom dirs
    python3 ssg.py <content> <output> <static>

Markdown subset supported:
    # H1, ## H2, ### H3
    **bold**, *italic*, `inline code`, [links](url)
    - unordered lists, 1. ordered lists
    > blockquotes
    ``` fenced code blocks ```
    paragraphs

Simple front matter is supported for page titles:

    ---
    title: My Post
    ---
"""

import html
import os
import re
import shutil
import sys

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DEFAULT_CONTENT = os.path.join(BASE_DIR, "content")
DEFAULT_OUTPUT = os.path.join(BASE_DIR, "site")
DEFAULT_STATIC = os.path.join(BASE_DIR, "static")

# ---------------------------------------------------------------------------
# Front matter
# ---------------------------------------------------------------------------

def parse_front_matter(text):
    """Split off a leading `--- ... ---` block into a dict of metadata.

    Returns (metadata_dict, remaining_text). If no front matter is present,
    returns ({}, text) unchanged.
    """
    if not text.startswith("---"):
        return {}, text
    # Look for the closing fence on its own line.
    end = text.find("\n---", 3)
    if end == -1:
        return {}, text
    meta = {}
    for line in text[3:end].strip().split("\n"):
        if ":" in line:
            key, value = line.split(":", 1)
            meta[key.strip()] = value.strip()
    return meta, text[end + 4:].lstrip("\n")


# ---------------------------------------------------------------------------
# Inline formatting (bold, italic, code, links)
# ---------------------------------------------------------------------------

def inline(text):
    """Apply inline Markdown formatting to a single line of text.

    HTML is escaped FIRST so that raw `<` / `&` in the source can never
    break the output page. Code spans are then wrapped (their content is
    already escaped, which is exactly what we want inside <code>).
    """
    text = html.escape(text)
    # `code` spans first so formatting chars inside code are not processed.
    text = re.sub(r"`([^`]+)`", lambda m: "<code>%s</code>" % m.group(1), text)
    # [text](url) links before bold/italic so markers inside link text work.
    text = re.sub(r"\[([^\]]+)\]\(([^)]+)\)", r'<a href="\2">\1</a>', text)
    text = re.sub(r"\*\*([^*]+)\*\*", r"<strong>\1</strong>", text)
    text = re.sub(r"\*([^*]+)\*", r"<em>\1</em>", text)
    return text


# ---------------------------------------------------------------------------
# Block parsing (headings, lists, quotes, code fences, paragraphs)
# ---------------------------------------------------------------------------

def is_block_start(line):
    """True if this line starts a new block element (not a paragraph)."""
    return (
        line.startswith("```")
        or re.match(r"^#{1,3}\s", line) is not None
        or re.match(r"^[-*]\s", line) is not None
        or re.match(r"^\d+\.\s", line) is not None
        or line.startswith(">")
    )


def parse_blocks(text):
    """Convert the Markdown body (no front matter) into an HTML fragment."""
    lines = text.split("\n")
    parts = []
    i = 0
    while i < len(lines):
        line = lines[i]
        stripped = line.strip()

        # Skip blank lines -- they just separate blocks.
        if not stripped:
            i += 1
            continue

        # ``` fenced code block (content is escaped, never inline-formatted)
        if stripped.startswith("```"):
            lang = stripped[3:].strip()
            code_lines = []
            i += 1
            while i < len(lines) and not lines[i].strip().startswith("```"):
                code_lines.append(lines[i])
                i += 1
            i += 1  # skip the closing fence
            code = html.escape("\n".join(code_lines))
            cls = ' class="language-%s"' % html.escape(lang) if lang else ""
            parts.append("<pre><code%s>%s</code></pre>" % (cls, code))
            continue

        # # Headings (levels 1-3)
        m = re.match(r"^(#{1,3})\s+(.*)$", stripped)
        if m:
            level = len(m.group(1))
            parts.append("<h%d>%s</h%d>" % (level, inline(m.group(2)), level))
            i += 1
            continue

        # - Unordered lists
        if re.match(r"^[-*]\s+", stripped):
            items = []
            while i < len(lines) and re.match(r"^[-*]\s+", lines[i].strip()):
                item = re.sub(r"^[-*]\s+", "", lines[i].strip())
                items.append("<li>%s</li>" % inline(item))
                i += 1
            parts.append("<ul>\n%s\n</ul>" % "\n".join(items))
            continue

        # 1. Ordered lists
        if re.match(r"^\d+\.\s+", stripped):
            items = []
            while i < len(lines) and re.match(r"^\d+\.\s+", lines[i].strip()):
                item = re.sub(r"^\d+\.\s+", "", lines[i].strip())
                items.append("<li>%s</li>" % inline(item))
                i += 1
            parts.append("<ol>\n%s\n</ol>" % "\n".join(items))
            continue

        # > Blockquotes (consecutive > lines become one quote)
        if stripped.startswith(">"):
            quotes = []
            while i < len(lines) and lines[i].strip().startswith(">"):
                quotes.append(re.sub(r"^>\s?", "", lines[i].strip()))
                i += 1
            inner = "\n".join("<p>%s</p>" % inline(q) for q in quotes)
            parts.append("<blockquote>\n%s\n</blockquote>" % inner)
            continue

        # Plain paragraph: gather lines until a blank line or new block.
        para = [stripped]
        i += 1
        while i < len(lines) and lines[i].strip() and not is_block_start(lines[i].strip()):
            para.append(lines[i].strip())
            i += 1
        parts.append("<p>%s</p>" % inline(" ".join(para)))

    return "\n".join(parts)


# ---------------------------------------------------------------------------
# Page template and build
# ---------------------------------------------------------------------------

LAYOUT = """<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <title>{title}</title>
  <link rel="stylesheet" href="style.css">
</head>
<body>
  <nav><a href="index.html">&larr; Home</a></nav>
  <main>
{content}
  </main>
</body>
</html>
"""

INDEX_LAYOUT = """<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <title>{title}</title>
  <link rel="stylesheet" href="style.css">
</head>
<body>
  <main>
    <h1>{title}</h1>
    <ul>
{items}
    </ul>
  </main>
</body>
</html>
"""


def render_page(title, body_html):
    """Wrap a body fragment in the site layout."""
    return LAYOUT.format(title=html.escape(title), content=body_html)


def build(content_dir, output_dir, static_dir=None):
    """Build every .md file in content_dir into output_dir."""
    os.makedirs(output_dir, exist_ok=True)
    pages = []

    for name in sorted(os.listdir(content_dir)):
        if not name.endswith(".md"):
            continue
        src = os.path.join(content_dir, name)
        with open(src, "r", encoding="utf-8") as f:
            raw = f.read()

        meta, body = parse_front_matter(raw)
        title = meta.get("title", os.path.splitext(name)[0].replace("-", " ").title())
        body_html = parse_blocks(body)
        page_html = render_page(title, body_html)

        out_name = os.path.splitext(name)[0] + ".html"
        with open(os.path.join(output_dir, out_name), "w", encoding="utf-8") as f:
            f.write(page_html)
        pages.append((out_name, title))
        print("built %s -> %s" % (name, out_name))

    # Index page linking to every post.
    items = "\n".join(
        '      <li><a href="%s">%s</a></li>' % (fname, html.escape(title))
        for fname, title in pages
    )
    index = INDEX_LAYOUT.format(title="My Tiny Blog", items=items)
    with open(os.path.join(output_dir, "index.html"), "w", encoding="utf-8") as f:
        f.write(index)
    print("built index.html (%d pages)" % len(pages))

    # Copy static assets (css, images, ...) if the folder exists.
    if static_dir and os.path.isdir(static_dir):
        for name in os.listdir(static_dir):
            src = os.path.join(static_dir, name)
            dst = os.path.join(output_dir, name)
            if os.path.isfile(src):
                shutil.copy2(src, dst)
                print("copied static/%s" % name)

    return pages


def main(argv):
    content_dir = argv[1] if len(argv) > 1 else DEFAULT_CONTENT
    output_dir = argv[2] if len(argv) > 2 else DEFAULT_OUTPUT
    static_dir = argv[3] if len(argv) > 3 else DEFAULT_STATIC
    if not os.path.isdir(content_dir):
        sys.exit("content dir not found: %s" % content_dir)
    build(content_dir, output_dir, static_dir)
    print("done -> %s" % output_dir)


if __name__ == "__main__":
    main(sys.argv)
