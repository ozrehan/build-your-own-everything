---
title: "CDN Edge Cache"
category: "networking"
difficulty: "intermediate"
tags: [cdn, caching, http]
related: [http-protocol-deep-dive, redis-like-cache, status-page, rate-limiter]
---

# CDN Edge Cache

A CDN puts cached copies of content on servers near users so most requests never reach the origin. Building an edge cache yourself — cache keys, TTLs, validation, purging — teaches the HTTP caching model deeply enough to debug the "why am I seeing stale content?" incidents that plague every web team.

## Core concepts

- **Edge vs origin** — The origin holds the truth; edge nodes hold copies. A cache HIT serves locally in milliseconds, a MISS fetches from origin and stores the result. The hit ratio is the whole business.
- **Cache keys** — Usually the URL plus selected request headers (`Vary: Accept-Encoding`). Key it wrong and mobile users get desktop pages, or every user gets their own copy and your hit ratio collapses.
- **TTL and freshness** — `Cache-Control: max-age` and `s-maxage` say how long a response is fresh; `Expires` is the legacy equivalent. Fresh responses serve without contacting origin at all.
- **Stale-while-revalidate** — Serve the slightly-stale copy *immediately* while refreshing in the background. Users never wait on origin latency, and this one directive fixes most "cache makes us slow" complaints.
- **Validation (conditional requests)** — `ETag`/`Last-Modified` let the edge ask "changed since X?" and get a tiny `304 Not Modified` instead of the full body — bandwidth savings without staleness risk.
- **Purging/invalidation** — When content changes now, waiting out the TTL isn't acceptable: purge APIs (by URL, tag, or wildcard) actively evict. "There are only two hard things" applies directly.
- **Tiered caching and consistent hashing** — Edges share a parent tier so one MISS populates many edges; consistent hashing spreads keys across cache nodes with minimal reshuffling when nodes change.

## How it works

Your cache sits as a reverse proxy in front of an origin. On each request it computes the cache key and looks it up: fresh HIT → serve immediately with an `Age` header; stale-but-revalidatable → send a conditional request upstream and serve 304-refreshed content; MISS → fetch from origin, store the body plus headers and computed expiry on disk, then serve. A purge endpoint deletes by key/tag, background revalidation keeps hot entries warm, and hit/miss/revalidation counters expose the cache's effectiveness.

## Build milestones

1. Build a caching reverse proxy: fetch from origin once, store response body + headers on disk keyed by URL, serve repeats from cache.
2. Honor `Cache-Control` (`max-age`, `no-store`, `no-cache`) and `Vary`; add `Age` and `X-Cache: HIT/MISS` headers.
3. Implement conditional revalidation: store ETags, send `If-None-Match`, and handle `304` without rewriting the body.
4. Add `stale-while-revalidate` (serve stale instantly, refresh in background) and a purge API by URL and by tag.
5. Track hit ratio, byte savings, and revalidation counts on a stats endpoint; tune TTLs against a simulated workload.

## Best resources

- [RFC 9111 — HTTP Caching](https://www.rfc-editor.org/rfc/rfc9111) — the authoritative spec: freshness, validation, and what caches are allowed to do.
- [Varnish Cache](https://github.com/varnishcache/varnish-cache) — the classic open-source HTTP cache; its VCL model is the clearest expression of cache policy as code.
- [What is a CDN? (Cloudflare)](https://www.cloudflare.com/learning/cdn/what-is-a-cdn/) — how edge networks, anycast, and tiered caching fit together in production.
- [MDN: HTTP caching](https://developer.mozilla.org/en-US/docs/Web/HTTP/Guides/Caching) — freshness lifetimes, validation, and cache-busting from the web developer's side.

## Stretch ideas

- Shard the cache across multiple nodes with consistent hashing and measure hit-ratio changes as nodes join and leave.
- Add range-request caching (partial content) so video seeking works through your edge without refetching whole files.
