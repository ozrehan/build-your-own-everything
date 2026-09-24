---
title: "HTTP Protocol Deep Dive"
category: "networking"
difficulty: "intermediate"
tags: [http, protocol, web]
related: [websocket-server, http2-framing, cdn-edge-cache, rest-api-client]
---

# HTTP Protocol Deep Dive

HTTP looks simple — text requests, text responses — but the details (persistent connections, chunked encoding, caching, content negotiation) are where real-world web behavior lives. Writing your own HTTP/1.1 parser and server from scratch teaches you exactly what frameworks hide and why certain bugs (like truncated responses) happen.

## Core concepts

- **Request/response and statelessness** — Each HTTP exchange is independent: a method, a target, headers, an optional body, then a status line, headers, and body back. All "state" (cookies, sessions) is bolted on top via headers.
- **Methods and status codes** — GET/POST/PUT/DELETE/PATCH carry intent; 2xx/3xx/4xx/5xx classes carry outcome. Idempotency (safe to retry GET, PUT, DELETE but not POST) is a contract clients rely on.
- **Headers as the control plane** — Almost everything interesting in HTTP happens in headers: authentication, caching, compression, content type, connection reuse. Parsing them correctly is most of the work.
- **Persistent connections (keep-alive)** — HTTP/1.1 reuses one TCP connection for many requests by default, which means your parser must know exactly where each message ends — via Content-Length or chunked encoding — or the stream desynchronizes.
- **Chunked transfer encoding** — Lets a server stream a response without knowing its total length upfront: each chunk is prefixed with its size in hex, terminated by a zero-length chunk. Your parser must handle it to talk to real servers.
- **Content negotiation** — `Accept`, `Accept-Encoding`, and `Accept-Language` let client and server agree on representation. This is why the same URL can return JSON, HTML, or gzipped bytes.
- **Caching semantics** — `Cache-Control`, `ETag`, and conditional requests (`If-None-Match` → `304 Not Modified`) are a whole sub-protocol for avoiding redundant transfers; getting them right saves enormous bandwidth.

## How it works

A client opens a TCP connection and sends a request line (`GET /path HTTP/1.1`), followed by headers (`Host:`, `User-Agent:`, …), a blank line, and an optional body. The server parses this, routes on method + path, and responds with a status line (`HTTP/1.1 200 OK`), headers (`Content-Type:`, `Content-Length:` or `Transfer-Encoding: chunked`), a blank line, and the body. Both sides must frame messages precisely so multiple requests can share one connection, and either side can pipeline or close the connection with `Connection: close`.

## Build milestones

1. Write a TCP server that reads a raw GET request, parses the request line and headers, and returns a hardcoded `200 OK` with correct `Content-Length`.
2. Add routing on method + path, query-string parsing, and static file serving with proper `Content-Type` and `Content-Length`.
3. Support persistent connections: loop reading requests on one socket, framing each body via `Content-Length`, and handle `Connection: close`.
4. Implement chunked transfer encoding (both parsing requests and generating responses) plus `ETag`/`If-None-Match` conditional responses.
5. Add gzip content encoding negotiation and write a minimal HTTP client from scratch that can fetch a real website.

## Best resources

- [RFC 9110 — HTTP Semantics](https://www.rfc-editor.org/rfc/rfc9110) — methods, status codes, headers, and caching semantics; the authoritative reference.
- [RFC 9112 — HTTP/1.1](https://www.rfc-editor.org/rfc/rfc9112) — message framing, chunked encoding, and connection management; exactly what your parser implements.
- [MDN Web Docs: HTTP](https://developer.mozilla.org/en-US/docs/Web/HTTP) — the most readable accurate overview of methods, headers, and status codes.
- [High Performance Browser Networking](https://hpbn.co/) — Ilya Grigorik's free online book; the HTTP chapters explain why the protocol looks the way it does.
- [HTTP Working Group specs](https://httpwg.org/specs/) — the living drafts and published RFCs for HTTP/1.1 through HTTP/3 in one place.
- [httpbin](https://httpbin.org/) — a free request/response testing service; perfect for exercising your client against chunked responses, redirects, and auth.

## Stretch ideas

- Build a reverse proxy that forwards to backends and adds `X-Forwarded-For`, then benchmark keep-alive vs connection-per-request.
- Implement HTTP/1.0 vs 1.1 differences and a strict parser fuzzer to find where your framing breaks on malformed input.
