---
title: "CSS Layout Engine"
category: "web-development"
difficulty: "advanced"
tags: [css, layout, rendering]
related: [webgl-2d-renderer, terminal-emulator, ui-toolkit, tween-animation-system]
---

# CSS Layout Engine

A layout engine takes a DOM tree plus CSS rules and computes the exact pixel position and size of every box on the page — the "layout" step between styling and painting in a browser. Building a simplified one (block layout, then flexbox) teaches how CSS actually works under the hood and why some layouts are cheap while others trigger expensive reflows.

## Core concepts

- **Box model** — Every element generates boxes with content, padding, border, and margin areas; `box-sizing: border-box` vs `content-box` changes which area the `width` applies to, a constant source of confusion.
- **Style resolution and cascade** — Matching selectors against elements, sorting by specificity and origin, and inheriting properties (like `color`) down the tree before any geometry is computed.
- **Block layout** — The vertical stacking model: block boxes stack top-to-bottom, widths fill the containing block, and vertical margins collapse between siblings.
- **Flexbox layout** — A two-pass algorithm: first resolve flexible lengths (`flex-grow`/`flex-shrink` against free space), then lay out items along the main axis and align them on the cross axis.
- **Formatting contexts** — Isolated layout regions (block formatting contexts, flex containers) that contain floats and margin collapsing, created by things like `overflow: hidden` or `display: flow-root`.
- **Line layout / inline formatting** — Text and inline elements are broken into line boxes by a line-breaking algorithm, with baseline alignment and `line-height` strut mechanics.
- **Reflow and dirty bits** — When styles or DOM change, the engine marks affected subtrees dirty and re-lays-out only them; deep or repeated reflows are the classic performance pitfall.
- **Stacking contexts and paint order** — Layout computes geometry, but `z-index`, transforms, and opacity create stacking contexts that determine paint order — layout alone doesn't decide what you see.

## How it works

1. Parse HTML into a DOM tree and CSS into rules; resolve the cascade to compute each element's final style.
2. Build a layout tree of boxes (dropping `display: none` elements, generating anonymous boxes where needed).
3. Walk the tree top-down: each box's size and position are computed from its parent's constraints and its own display type (block, flex, inline).
4. The result is a geometry tree (x, y, width, height per box) that a painter can rasterize.

## Build milestones

1. Parse a tiny HTML subset and CSS subset, and implement block layout: vertical stacking with margins and padding — renders simple documents.
2. Add the box model correctly: `border-box` vs `content-box`, margin collapsing, and width resolution against the containing block.
3. Implement a simplified flexbox (single-line, `flex-grow`/`flex-shrink`, `justify-content`, `align-items`) — the most satisfying milestone.
4. Add inline layout: line breaking for text with `line-height` and basic text measurement.
5. Add dirty-bit incremental reflow and a simple paint step (draw boxes to a canvas or SVG) to close the loop.

## Best resources

- [CSS Box Model — MDN](https://developer.mozilla.org/en-US/docs/Web/CSS/CSS_box_model/Introduction_to_the_CSS_box_model) — the authoritative box model reference.
- [CSS Flexible Box Layout spec](https://www.w3.org/TR/css-flexbox-1/) — surprisingly readable; the flexbox algorithm section is the real spec for what you're implementing.
- [How Browsers Work — Tali Garsiel](https://web.dev/articles/howbrowserswork) — the classic end-to-end tour: parsing, render tree, layout, painting.
- [Robinson (mattbaker) — Let's build a browser engine](https://limpet.net/mbrubeck/2014/08/08/toy-layout-engine-1.html) — a 7-part series building a toy HTML/CSS engine in Rust; the best guided build.
- [Yoga layout engine](https://github.com/facebook/yoga) — Meta's real cross-platform flexbox implementation; great reference for edge cases.

## Stretch ideas

- Implement CSS grid (the track-sizing algorithm is the genuinely hard part).
- Add a selector engine with specificity and pseudo-classes, then a real CSS parser.
