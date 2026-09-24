#!/usr/bin/env python3
"""Tests for ssg.py. Run with: python3 test_ssg.py"""
import os
import shutil
import sys
import tempfile

BASE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, BASE)
import ssg  # noqa: E402

PASS = 0


def check(name, cond):
    global PASS
    assert cond, "FAILED: %s" % name
    PASS += 1
    print("ok - %s" % name)


def main():
    tmp = tempfile.mkdtemp(prefix="ssg_test_")
    try:
        out = os.path.join(tmp, "site")
        # Build the real sample content into a temp dir.
        pages = ssg.build(os.path.join(BASE, "content"), out,
                          os.path.join(BASE, "static"))

        # 1. All three posts + index were generated.
        for fname in ("hello-world.html", "cheatsheet.html",
                      "how-it-works.html", "index.html"):
            check("file exists: %s" % fname,
                  os.path.isfile(os.path.join(out, fname)))

        cheatsheet = open(os.path.join(out, "cheatsheet.html"),
                          encoding="utf-8").read()
        hello = open(os.path.join(out, "hello-world.html"),
                     encoding="utf-8").read()

        # 2. Headings converted.
        check("h1 present", "<h1>Markdown Cheatsheet</h1>" in cheatsheet)
        check("h2 present", "<h2>Text styles</h2>" in cheatsheet)

        # 3. Inline formatting converted.
        check("bold -> strong", "<strong>bold</strong>" in cheatsheet)
        check("italic -> em", "<em>italic</em>" in cheatsheet)
        check("inline code -> code", "<code>monospace</code>" in cheatsheet)
        check("link -> a href",
              '<a href="https://example.com">link to example.com</a>' in cheatsheet)

        # 4. Lists converted.
        check("unordered list", "<ul>" in cheatsheet and
              "<li>apples</li>" in cheatsheet)
        check("ordered list", "<ol>" in hello and
              "<li>Write a Markdown file</li>" in hello)

        # 5. Blockquote converted.
        check("blockquote", "<blockquote>" in cheatsheet)

        # 6. Front-matter title lands in <title>.
        check("title in <title> (cheatsheet)",
              "<title>Markdown Cheatsheet</title>" in cheatsheet)
        check("title in <title> (hello)",
              "<title>Hello, Static World</title>" in hello)

        # 7. Code blocks are HTML-escaped, not rendered as HTML.
        check("code block escaped: <div>",
              "&lt;div&gt;" in cheatsheet)
        check("code block escaped: ampersand",
              "&amp; welcome!" in cheatsheet)
        check("code block has pre/code tags",
              "<pre><code" in cheatsheet)

        # 8. Index page links to all posts.
        index = open(os.path.join(out, "index.html"),
                     encoding="utf-8").read()
        check("index links hello-world",
              '<a href="hello-world.html">Hello, Static World</a>' in index)
        check("index links cheatsheet",
              '<a href="cheatsheet.html">Markdown Cheatsheet</a>' in index)

        # 9. Static assets copied.
        check("static/style.css copied",
              os.path.isfile(os.path.join(out, "style.css")))

        # 10. Paragraphs wrapped.
        check("paragraphs", "<p>Welcome to my tiny blog." in hello)

        print("\n%d tests passed" % PASS)
    finally:
        shutil.rmtree(tmp, ignore_errors=True)


if __name__ == "__main__":
    main()
