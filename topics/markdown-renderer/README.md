---
title: "Markdown Renderer"
category: "web-development"
difficulty: "beginner"
tags: [markdown, parsing, rendering]
related: [headless-cms, recursive-descent-parser, parser-combinators, ssr-hydration]
---

# Markdown Renderer

A Markdown renderer parses plain-text markup like `**bold**` and `# Heading` into an AST and then emits HTML. Building one — tokenizer, block/inline parsers, HTML emitter — teaches real parsing concepts (CommonMark's spec is famously tricky) and powers docs sites, CMS previews, and chat apps everywhere.

## Core concepts

- **Block vs inline parsing** — Block structures (headings, lists, code fences, blockquotes) are parsed line-by-line first; inline elements (emphasis, links, code spans) are then parsed within each block's text.
- **CommonMark spec** — The unambiguous specification of Markdown with 650+ examples; real renderers aim for spec compliance because naive regex approaches break on edge cases.
- **Delimiter runs and emphasis** — `*` and `_` handling is a state machine over "delimiter runs" with left/right-flanking rules — the hardest part of inline parsing, and why `_foo_bar_` differs from `*foo*bar*`.
- **Reference links** — `[text][id]` with definitions stored elsewhere in the document, requiring a pre-pass to collect reference definitions before inline parsing.
- **AST as intermediate** — Parsing to a tree (document → blocks → inlines) before emitting HTML lets you render to multiple targets (HTML, plain text, React) and run transforms like syntax highlighting.
- **Sanitization** — Rendered HTML must be sanitized (strip `<script>`, event handlers, `javascript:` URLs) when the Markdown comes from untrusted users — rendering without sanitizing is an XSS hole.
- **Extensions** — Tables, footnotes, task lists, and strikethrough are not in core CommonMark; they're layered as optional syntax plugins, which is how most renderers are architected.
- **Streaming/incremental rendering** — For live previews (editors, chat), re-parsing only changed regions or debouncing full re-parses keeps typing responsive.

## How it works

1. Split input into lines; run the block parser to identify containers (lists, quotes, fences) and leaf blocks (paragraphs, headings, code).
2. Collect reference definitions in a pre-pass, then run the inline parser over each block's text to resolve emphasis, links, and code spans.
3. Walk the resulting AST with an HTML emitter, escaping raw text and sanitizing any embedded raw HTML.
4. Optional: post-process with plugins (syntax highlighting on code blocks, heading anchor links).

## Build milestones

1. A block parser handling headings, paragraphs, fenced code, and horizontal rules, emitting escaped HTML — working in an evening.
2. Add inline parsing: code spans, `**bold**`/`*italic*` with flanking rules, and inline links.
3. Add nested containers: blockquotes and ordered/unordered lists with nesting.
4. Add reference links, autolinks, and hard breaks; test against a subset of the CommonMark spec suite.
5. Add an extension plugin system (tables, task lists) and a sanitizer for untrusted input.

## Best resources

- [CommonMark Spec](https://spec.commonmark.org/) — the specification itself, with hundreds of examples; the ultimate reference and test suite.
- [CommonMark Dingus](https://spec.commonmark.org/dingus/) — live playground showing the AST for any input; invaluable while debugging your parser.
- [marked on GitHub](https://github.com/markedjs/marked) — the most popular JS renderer's readable source for architecture ideas.
- [unified / remark](https://github.com/unifiedjs/unified) — the AST-centric Markdown ecosystem; shows how plugins transform trees before rendering.
- [Markdown Guide — Basic Syntax](https://www.markdownguide.org/basic-syntax/) — the friendly user-facing reference for what syntax your renderer should support.

## Stretch ideas

- Implement the full CommonMark spec suite (all 650+ examples passing) — a real badge of honor.
- Add WYSIWYG-style live preview with synchronized scrolling between editor and preview panes.
