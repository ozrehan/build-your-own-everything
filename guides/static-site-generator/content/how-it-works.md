---
title: How This Generator Works
---

# How This Generator Works

Building a static site generator teaches you three real skills at once:
**parsing**, *templating*, and file management.

## The pipeline

1. Read every `.md` file in `content/`
2. Strip the `---` front matter for the page title
3. Convert Markdown blocks to HTML fragments
4. Wrap each fragment in the layout template
5. Write the pages to `site/` and copy `static/` assets

## Parsing order matters

Inline formatting is applied *after* HTML-escaping, and `code` spans are
handled before **bold** and *italic* -- otherwise the asterisks inside
code would get eaten.

> Parse defensively: unknown input should become a boring paragraph,
> never a crash.

Check the [cheatsheet](cheatsheet.html) for the full syntax list.
