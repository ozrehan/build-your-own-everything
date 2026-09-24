---
title: "Dev Server with HMR"
category: "web-development"
difficulty: "advanced"
tags: [dev-server, hmr, tooling]
related: [js-bundler, test-runner-framework, spa-router, websocket-chat]
---

# Dev Server with HMR

A dev server serves your app unbundled with Hot Module Replacement: when you save a file, only the changed module is swapped into the running page without losing state. Building one teaches file watching, module graphs, WebSocket push, and the accept/dispose protocol that makes state-preserving updates possible.

## Core concepts

- **No-bundle dev serving** — Modern dev servers skip bundling and serve native ES modules directly to the browser, transforming each file on request — which is why Vite starts instantly on huge apps.
- **File watching** — OS-level watchers (inotify/FSEvents via chokidar or Node's `fs.watch`) detect saves and trigger re-transforms; debouncing avoids rebuilding mid-save.
- **HMR boundary** — A module that calls `import.meta.hot.accept()` declares it can handle its own updates; without a boundary, the update bubbles up the import chain until one is found or the page reloads.
- **The HMR protocol** — Over a WebSocket the server sends `{ type: 'update', updates: [...] }`; the client fetches the new module (cache-busted URL), runs accept callbacks, and swaps the module in the registry.
- **Dispose/prune callbacks** — `import.meta.hot.dispose()` lets a module clean up (remove listeners, timers) before it's replaced; without cleanup, HMR leaks handlers on every save.
- **Dependency invalidation** — When module A changes, the server walks the import graph to find all modules that import A, so the client knows which boundaries must re-run.
- **Transform pipeline** — Each request runs the file through transforms (TypeScript strip, JSX, CSS injection, import rewriting for bare specifiers like `import 'vue'`).
- **Error overlay** — Compile errors are pushed over the socket and rendered as a full-page overlay that clears on the next successful update — the DX detail that makes HMR feel magical.

## How it works

1. The dev server serves HTML with a client HMR runtime injected; app modules load as native ESM with rewritten imports.
2. A file watcher detects a save; the server re-transforms the file and computes affected modules via the import graph.
3. The server pushes an update message over WebSocket; the client fetches the new module code and finds the nearest HMR boundary.
4. Boundary accept callbacks run with the new module, dispose callbacks clean up the old one, and the page updates without reload — state intact.

## Build milestones

1. A static file server with a file watcher that injects a WebSocket client and does full-page reload on save — live reload in an evening.
2. Add on-demand per-file transforms (strip types via a simple transform, rewrite bare imports to `/@modules/` URLs) and serve native ESM.
3. Implement the HMR protocol: `import.meta.hot.accept()` runtime, server-sent update messages, module re-fetch with cache busting.
4. Add the import graph, boundary bubbling (walk up importers to find acceptors), and dispose callbacks for cleanup.
5. Add the error overlay, CSS hot-swap without JS reload, and dependency pre-bundling for `node_modules`.

## Best resources

- [Vite — HMR API](https://vite.dev/guide/api-hmr) — the canonical `import.meta.hot` API: accept, dispose, prune, invalidate.
- [webpack — Hot Module Replacement](https://webpack.js.org/concepts/hot-module-replacement/) — the original HMR design doc: the runtime/compiler contract explained from both sides.
- [esbuild — Watch mode](https://esbuild.github.io/api/#watch) — how the fastest bundler does incremental rebuilds.
- [Node.js — `--watch` mode](https://nodejs.org/docs/latest/api/cli.html#--watch) — Node's built-in file watching, useful for the server side of your dev loop.

## Stretch ideas

- Implement React Fast Refresh-style function-component state preservation on top of your HMR runtime.
- Add time-travel debugging: keep old module versions and let the developer step back through HMR updates.
