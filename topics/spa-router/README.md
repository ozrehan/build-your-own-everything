---
title: "SPA Router"
category: "web-development"
difficulty: "beginner"
tags: [routing, spa, history-api]
related: [ssr-hydration, web-components-library, rest-api-client, i18n-system]
---

# SPA Router

A single-page-app router swaps views in the browser without full page reloads, keeping the address bar and back button working like a multi-page site. Building one from scratch — route matching, history integration, lazy views — teaches how frameworks turn URLs into components and why client-side routing needs server fallback rules.

## Core concepts

- **History API** — `pushState`/`replaceState` change the URL without a reload, and the `popstate` event fires on back/forward; this is the entire foundation of client-side routing.
- **Route matching** — URL paths are compared against patterns like `/users/:id` (params) and `/files/*` (wildcards); matching is usually first-match-wins in declaration order.
- **Hash routing** — An older fallback using `#/path` fragments, which never reach the server, so no server config is needed — useful for static file hosts without rewrites.
- **Route params vs query strings** — `/users/42` params identify resources and are part of the pattern; `?tab=settings` queries are ad-hoc state parsed with `URLSearchParams`.
- **Guards and redirects** — Hooks that run before a route renders (e.g. "is the user logged in?"), able to cancel or redirect navigation — how auth-protected pages work.
- **Lazy route loading** — Splitting each route's code and loading it on first visit via dynamic `import()`, so the initial bundle stays small.
- **Scroll and state restoration** — A real router restores scroll position and can pass state between navigations (via `history.state`) so back-button feels native.
- **Server fallback** — Since no files exist at `/users/42`, the server must serve `index.html` for unknown paths, or direct loads/deep links 404.

## How it works

1. On startup, the router reads `location.pathname` (or the hash), finds the first matching route pattern, and renders its view into a root element.
2. Clicking an internal link is intercepted (`preventDefault`), `history.pushState` updates the URL, and the router renders the new view — no network request happens.
3. Browser back/forward fires `popstate`, which the router listens to, re-matching the URL and re-rendering.
4. Guards run before each render, lazy routes `import()` their modules on demand, and unmatched URLs render a 404 view.

## Build milestones

1. A router that matches exact paths, listens to `popstate`, intercepts link clicks, and swaps `innerHTML` between two views — a working evening project.
2. Add parameterized routes (`/users/:id`) with a pattern-to-regex compiler and a 404 catch-all.
3. Add guards (`beforeEach`) for auth-style redirects and scroll restoration on back/forward.
4. Add lazy loading: routes defined as `() => import('./pages/home.js')` with a loading placeholder.
5. Add nested routes with outlets (a parent layout rendering child routes in a slot), mirroring real frameworks.

## Best resources

- [History API — MDN](https://developer.mozilla.org/en-US/docs/Web/API/History_API) — the definitive reference for `pushState`, `replaceState`, and `popstate`.
- [React Router docs](https://reactrouter.com/) — the reference implementation of nested routes, loaders, and actions in a real library.
- [Vue Router guide](https://router.vuejs.org/) — clean explanations of route matching, navigation guards, and lazy loading.
- [Navigo source code](https://github.com/krasimir/navigo) — a tiny (~10KB) router whose readable source is a great study model.

## Stretch ideas

- Implement transition hooks (loading indicators, animated page transitions between routes).
- Add a data-loading convention: routes declare `loader()` functions whose data resolves before render.
