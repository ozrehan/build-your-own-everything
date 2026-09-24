# Build Your Own Static Site Generator

A tiny static site generator in **one Python file** (`ssg.py`, ~250 lines,
stdlib only). It turns a folder of Markdown files into a complete website —
no frameworks, no dependencies, no build step beyond `python3 ssg.py`.

## What you'll build

`ssg.py` reads Markdown posts from `content/`, converts a Markdown subset
to HTML, wraps every page in an HTML layout template, generates an index
page, copies `static/` assets, and writes everything to `site/`. The result
is plain HTML you can host anywhere — GitHub Pages, Netlify, or even the
tiny web server from this series.

## How it works, step by step

1. **Front matter** — `parse_front_matter()` splits an optional leading
   `---` block (`title: My Post`) off the top of each file. The title ends
   up in the page's `<title>` tag.
2. **Block parsing** — `parse_blocks()` walks the file line by line and
   recognizes block elements: `#`/`##`/`###` headings, `-` and `1.`
   lists, `>` blockquotes, ` ``` ` fenced code blocks, and plain
   paragraphs (consecutive non-blank lines joined together).
3. **Inline formatting** — `inline()` handles `**bold**`, `*italic*`,
   `` `code` ``, and `[text](url)`. Crucially, it **HTML-escapes first**,
   so raw `<` and `&` in your writing can never break the page, and code
   spans are processed before bold/italic so markers inside code survive.
4. **Templating** — `render_page()` drops the body fragment into a small
   HTML5 layout with a stylesheet link and a "Home" nav.
5. **Build** — `build()` converts every `.md` file, writes an `index.html`
   linking all pages, and copies `static/` (CSS, images) into the output.

## How to run

```bash
cd guides/static-site-generator
python3 ssg.py                  # builds content/ into site/
python3 -m http.server -d site 8000   # preview at http://localhost:8000
```

Custom folders also work:

```bash
python3 ssg.py <content_dir> <output_dir> [static_dir]
```

## How to test

```bash
python3 test_ssg.py
```

The test builds the real sample posts into a temp directory and asserts
22 things: headings/lists/quotes convert correctly, front-matter titles
land in `<title>`, code blocks are HTML-escaped, the index links every
page, and static assets are copied.

## Stretch exercises

1. **Dates and sorting** — add a `date:` field to front matter, show it on
   each post, and sort the index newest-first.
2. **Nested lists** — support indented sub-lists (`  - nested item`).
3. **RSS feed** — generate a `feed.xml` from the posts so readers can
   subscribe.

## Further reading

- [Markdown original syntax (Daring Fireball)](https://daringfireball.net/projects/markdown/syntax)
- [CommonMark spec — the precise Markdown reference](https://spec.commonmark.org/)
- [Jekyll docs — how a production SSG structures layouts/includes](https://jekyllrb.com/docs/)
