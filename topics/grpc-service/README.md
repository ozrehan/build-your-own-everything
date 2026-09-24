---
title: "gRPC Service"
category: "networking"
difficulty: "beginner"
tags: [grpc, rpc, protobuf]
related: [http2-framing, rest-api-client, graphql-server, service-discovery]
---

# gRPC Service

gRPC lets you define an API once in a `.proto` file and get type-safe clients and servers in a dozen languages, with binary serialization and HTTP/2 streaming underneath. Building a real service with it teaches contract-first API design — and shows exactly what you're trading away versus REST.

## Core concepts

- **IDL-first contracts** — You write the API as a `.proto` file: services, methods, and message types. The schema is the documentation, the validation, and the source of generated code — versioning it carefully is the central discipline.
- **Code generation** — `protoc` plus language plugins generate client stubs and server skeletons from the `.proto`. You fill in business logic; marshaling, framing, and transport are handled for you.
- **Four call types** — Unary (one request, one response), server-streaming, client-streaming, and bidirectional streaming. Streaming turns gRPC into a realtime substrate, not just RPC.
- **HTTP/2 transport** — Under the hood every call is an HTTP/2 stream with protobuf payloads and trailers carrying the status code. Understanding this explains gRPC's multiplexing and why browsers need grpc-web.
- **Status codes and error model** — A fixed set of codes (`NOT_FOUND`, `INVALID_ARGUMENT`, …) plus rich error details. Mapping domain errors to codes consistently is what makes clients able to react programmatically.
- **Deadlines and cancellation** — Every call carries a deadline propagated across the call chain; servers must respect context cancellation or they'll do work nobody waits for.
- **Interceptors** — Middleware for RPCs: logging, auth, metrics, and retries compose as client/server interceptors, the same idea as HTTP middleware one layer down.

## How it works

You define messages and a service in `service.proto`, run the protobuf compiler to generate Go/Python/Java stubs, and implement the server methods against your business logic. The client stub marshals a request message to protobuf bytes, opens an HTTP/2 stream to the server with the method encoded in the `:path` header, and streams back length-prefixed response messages; the final HTTP/2 trailers carry the gRPC status code. Interceptors on both sides add auth headers, enforce deadlines, and translate errors — while protobuf's field numbering keeps old clients working as you evolve the schema.

## Build milestones

1. Write a `.proto` file, generate code, and get a unary `SayHello` round trip working between client and server.
2. Add server-streaming (e.g., a live event feed) and client-streaming (e.g., a metrics aggregator) methods.
3. Build a bidirectional chat: both sides stream concurrently and handle graceful shutdown.
4. Add interceptors for request logging and token auth; map domain errors to proper gRPC status codes with details.
5. Enforce deadlines end to end and verify cancellation propagates: a slow server method must abort when the client gives up.

## Best resources

- [gRPC FAQ](https://grpc.io/docs/what-is-grpc/faq/) — what gRPC is, when to use it, and how it compares to alternatives, from the official docs.
- [gRPC documentation](https://grpc.io/docs/) — core concepts, quickstarts per language, and guides for streaming, errors, and deadlines.
- [Protocol Buffers documentation](https://protobuf.dev/) — the serialization layer: proto3 syntax, field numbering, and schema evolution rules.
- [grpc/grpc](https://github.com/grpc/grpc) — the reference C-core implementation; reading its HTTP/2 transport code shows what's under the stubs.

## Stretch ideas

- Expose your service to browsers via grpc-web (through an Envoy proxy) and compare the ergonomics with a REST/JSON version of the same API.
- Add gRPC health checking and server reflection, then explore your live service with `grpcurl`.
