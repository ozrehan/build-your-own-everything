---
title: "JavaScript Bundler"
category: "web-development"
difficulty: "intermediate"
tags: [bundling, esm, build-tools]
related: [dev-server-hmr, transpiler, package-manager, test-runner-framework]
---

# JavaScript Bundler

A bundler resolves your `import` graph starting from entry files, transforms each module, and emits optimized output files the browser can load. Building a minimal bundler — resolution, a module graph, scope hoisting, tree shaking — demystifies what webpack, Rollup, and esbuild do with every build and why "just concatenate files" was never enough.

## Core concepts

- **Entry points and module graph** — Starting from entry files, the bundler follows every `import` to build a graph of modules; cycles are allowed because ESM bindings are live and lazily initialized.
- **Module resolution** — The algorithm that turns `'./util'` or `'lodash'` into a file path: relative paths, `node_modules` lookup, `package.json` `main`/`exports` fields, and extension probing.
- **Loaders / transforms** — A pipeline stage that converts non-JS (CSS, images, TypeScript) into JS modules the graph can consume, or downlevels syntax via a parser like Babel/esbuild.
- **Tree shaking** — Dead-code elimination using static ESM analysis: if an export is never imported anywhere in the graph, it is dropped from the output.
- **Code splitting** — Shared dependencies are hoisted into common chunks, and dynamic `import()` creates async chunks loaded on demand, so routes ship only what they need.
- **Scope hoisting** — Concatenating modules into one scope (renaming colliding identifiers) instead of wrapping each in a function, producing smaller, faster bundles.
- **Source maps** — Mappings from output positions back to original files/line numbers, so devtools show your source instead of minified bundle code.
- **Content hashing** — Emitting `app.a3f9c2.js` with a hash of the file's contents so browsers cache aggressively and only re-download changed files.

## How it works

1. Parse each entry file's imports, resolve them to paths, and recursively build the full module graph.
2. Parse each module into an AST, track which exports are actually used, and mark unused ones for tree shaking.
3. Transform modules (transpile syntax, apply loaders), then hoist or wrap them and concatenate into chunks according to the splitting strategy.
4. Emit final assets with hashed filenames plus a manifest/source maps, ready for `<script>` tags.

## Build milestones

1. A naive concatenator: resolve relative imports with regex-free AST parsing (acorn), wrap each module in a function with a tiny `require` runtime — your own CommonJS bundle.
2. Add ESM support: rewrite `import`/`export` to registry lookups, handle circular imports correctly.
3. Implement tree shaking: mark-and-sweep unused exports via AST analysis across the graph.
4. Add code splitting: dynamic `import()` becomes a separate chunk loaded with a JSONP-style script tag at runtime.
5. Add minification (via an existing parser or simple transforms), content hashing, and source maps.

## Best resources

- [esbuild — Getting started](https://esbuild.github.io/getting-started/) — the fastest modern bundler's docs; the architecture notes explain why bundlers are I/O- and parse-bound.
- [Rollup — Introduction](https://rollupjs.org/introduction/) — the ESM-first bundler that pioneered tree shaking and scope hoisting.
- [webpack — Concepts](https://webpack.js.org/concepts/) — the canonical mental model: entry, loaders, plugins, module graph, chunks.
- [SurviveJS — Webpack: The Core Concepts](https://survivejs.com/webpack/what-is-webpack/) — a free, thorough walkthrough of bundler internals.
- [acorn on GitHub](https://github.com/acornjs/acorn) — the tiny, fast parser you'll reach for when parsing modules in your own bundler.

## Stretch ideas

- Write a dev-server mode with in-memory builds and incremental rebuilds (stepping stone to HMR).
- Implement your own minifier pass (constant folding, dead-branch removal, identifier mangling).
