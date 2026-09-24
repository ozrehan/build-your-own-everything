---
title: "SSR and Hydration"
category: "web-development"
difficulty: "intermediate"
tags: [ssr, hydration, rendering]
related: [spa-router, js-bundler, headless-cms, cdn-edge-cache]
---

# SSR and Hydration

Server-Side Rendering (SSR) means a Node/Deno server runs your UI code and sends fully-formed HTML to the browser, so the page is readable before any JavaScript downloads. Hydration is the client-side step where the framework "takes over" that static HTML, attaching event listeners and state without re-rendering it. Building a tiny SSR + hydration pipeline yourself teaches exactly where the server's job ends, what the client must reconstruct, and why hydration mismatches happen.

## Core concepts

- **Server render** — The server executes your components to an HTML string on each request (or at build time), inlining fetched data so the browser paints content on first load without waiting for JS.
- **Hydration** — The client framework walks the server-rendered DOM, matches it against its virtual tree, and attaches listeners and state — it does not rebuild the DOM from scratch.
- **Hydration mismatch** — When server and client render different markup (e.g. `Date.now()` or random IDs rendered on both sides), the framework warns and patches, which can be slow and buggy; deterministic rendering avoids it.
- **Rehydration / resumability** — Rehydration re-runs components on the client to rebuild state; resumability (Qwik-style) skips that work by serializing component state and listeners into the HTML itself.
- **Streaming SSR** — The server flushes HTML chunks progressively (via Node streams / `renderToPipeableStream`) so the browser can paint early content while slow components still render, instead of waiting for one giant HTML string.
- **Islands architecture** — Static page shells with isolated interactive "islands" that hydrate independently and lazily (on visibility, idle, or media query), shipping far less JS than full-app hydration.
- **Data serialization** — Server-fetched data is embedded in the HTML (e.g. `window.__DATA__` or `<script type="application/json">`) so the client can hydrate with the same data without refetching.
- **Client-only escape hatches** — Components that depend on browser APIs (`window`, `localStorage`) must be marked client-only so the server skips them, leaving a placeholder in the server HTML.

## How it works

1. A request hits your server, which runs the router, fetches the route's data, and calls the framework's render-to-string function to produce HTML.
2. The server embeds that HTML plus the serialized props/data into a full HTML document and streams it to the browser, which paints it immediately.
3. The browser downloads the client bundle; the framework calls `hydrateRoot(domNode, <App/>)`, walking the existing DOM and attaching event listeners and reactive state without recreating nodes.
4. From then on, navigation can either be client-side (SPA behavior) or fall back to full server renders per request.

## Build milestones

1. A Node HTTP server that renders a plain template function to an HTML string per request — the core "SSR" primitive in an evening.
2. Add a `data-*` contract: server inlines JSON data in a script tag, client script reads it and attaches interactivity to the existing DOM (manual hydration).
3. Build a minimal component model (nested render functions returning HTML) with a `hydrate()` that walks server DOM and binds `onClick`-style handlers by matching attributes.
4. Add streaming: pipe HTML chunks with `ReadableStream` so content paints before slow sections finish.
5. Graduate to islands: mark some components `data-island`, hydrate each lazily on `IntersectionObserver`, and measure the JS savings.

## Best resources

- [Rendering on the Web](https://web.dev/articles/rendering-on-the-web) — the classic Google write-up comparing CSR, SSR, SSG, and streaming, with the trade-off table everyone cites.
- [hydrateRoot – React](https://react.dev/reference/react-dom/client/hydrateRoot) — the canonical hydration API docs, including mismatch caveats and options.
- [Astro — Concepts: Astro Islands](https://docs.astro.build/en/concepts/islands/) — the best explanation of partial hydration and the `client:*` directive model.
- [React — renderToPipeableStream](https://react.dev/reference/react-dom/server/renderToPipeableStream) — the official docs for streaming SSR with Suspense on the server.
- [Vue — SSR Guide](https://vuejs.org/guide/scaling-up/ssr) — Vue's guide to universal rendering, hydration, and the caveats of a framework-agnostic SSR setup.

## Stretch ideas

- Implement resumability: serialize listener references so the client never re-runs component code.
- Add per-request caching with stale-while-revalidate semantics on the server render.
