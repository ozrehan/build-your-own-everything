---
title: "Service Worker Offline"
category: "web-development"
difficulty: "intermediate"
tags: [service-worker, offline, caching]
related: [pwa-installable, spa-router, cdn-edge-cache, websocket-chat]
---

# Service Worker Offline

A service worker is a script the browser runs in the background, able to intercept every network request from your site and serve cached responses when the network is gone. Building an offline-first app with one teaches the service worker lifecycle, caching strategies, and the update pitfalls that make or break real-world deployments.

## Core concepts

- **Lifecycle: install → activate** — A new service worker installs, waits (while the old one still controls open pages), then activates; `skipWaiting()` and `clients.claim()` let it take over immediately — a common source of "why isn't my update live?" confusion.
- **Fetch interception** — The `fetch` event lets the worker respond with anything: cache, network, or a synthetic response; `event.respondWith()` is the hook that makes offline possible.
- **Cache-first** — Serve from cache, fall back to network; ideal for versioned static assets (JS/CSS with hashed filenames) where the bytes never change.
- **Network-first** — Try network, fall back to cache on failure; right for API data and HTML where freshness matters but offline should still show something.
- **Stale-while-revalidate** — Serve the cached copy instantly while fetching a fresh one in the background for next time; the sweet spot for avatars, feeds, and config.
- **Precaching the app shell** — Caching the core HTML/CSS/JS during `install` so the app boots with zero network — the foundation of the "app shell" offline pattern.
- **Background sync** — `sync` events let the worker retry failed mutations (queued while offline) when connectivity returns, enabling offline writes.
- **Update hazards** — A stale worker can serve stale JS against a new API; versioning caches and prompting users to reload are production necessities, not polish.

## How it works

1. The page registers the worker (`navigator.serviceWorker.register('/sw.js')`); the browser installs it on a secure context and it begins controlling the scope.
2. During `install`, the worker precaches the app shell; on `activate`, it deletes old caches.
3. Every request from the page fires a `fetch` event in the worker, which applies the chosen caching strategy per resource type and returns the response.
4. Queued mutations are stored in IndexedDB while offline and replayed via background sync when the network returns.

## Build milestones

1. Register a service worker that precaches an app shell and serves a custom offline page when the network fails — working in an evening.
2. Implement the three caching strategies with per-route configuration (cache-first for hashed assets, network-first for API, SWR for images).
3. Add cache versioning and an "update available — reload" prompt using the lifecycle events.
4. Add offline writes: queue form submissions in IndexedDB and replay them with background sync.
5. Graduate to Workbox-style: build a tiny routing/strategy library, or adopt Workbox itself and compare.

## Best resources

- [The Offline Cookbook — web.dev](https://web.dev/articles/offline-cookbook) — Jake Archibald's legendary guide to caching strategies; the single best resource on the topic.
- [Service Worker API — MDN](https://developer.mozilla.org/en-US/docs/Web/API/Service_Worker_API) — the full reference, including the Using Service Workers guide.
- [Workbox docs](https://developer.chrome.com/docs/workbox) — Google's production library for precaching, routing, and strategies; study its recipes.
- [Service Workers spec — W3C](https://www.w3.org/TR/service-workers/) — the normative lifecycle and fetch-event semantics when MDN isn't enough.

## Stretch ideas

- Implement periodic background sync for a news-reader that pre-fetches content overnight.
- Build an offline-first collaborative notes app with CRDT sync on reconnect.
