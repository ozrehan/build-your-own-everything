---
title: "Service Discovery"
category: "networking"
difficulty: "intermediate"
tags: [discovery, dns, consensus]
related: [tcp-load-balancer, layer7-routing, dns-resolver, status-page]
---

# Service Discovery

In a world of containers and autoscaling, "where is the payments service?" changes every minute — hardcoded IPs don't survive. Service discovery (DNS-SRV, Consul, etcd) is how services find each other dynamically, and building a registry plus health-checked lookups teaches the consistency and failure-detection tradeoffs behind every orchestrator.

## Core concepts

- **Service registry** — A central store mapping service names to live instance addresses. Instances register on startup and deregister on shutdown; clients query the registry instead of config files.
- **Health checking** — Registrations expire unless the instance keeps proving it's alive (heartbeats/TTLs) or the registry actively probes it. Without this, discovery hands out addresses of dead servers.
- **DNS-based discovery** — SRV records (`_http._tcp.payments.example.com`) encode host, port, priority, and weight in plain DNS — zero client libraries needed, but TTLs make updates sluggish.
- **Client-side vs server-side discovery** — Either clients query the registry and load-balance themselves, or they call a router that does it for them. Client-side is more resilient; server-side keeps clients dumb.
- **Consistency tradeoffs** — Strongly consistent registries (Raft-backed, like etcd/Consul) give every client the same answer but can stall during partitions; gossip-based AP systems (like Serf) stay available with possibly-stale answers.
- **Watch/long-poll** — Instead of polling for changes, clients subscribe and get pushed updates when instances change — the mechanism behind instant failover without thundering polling herds.
- **Sidecar pattern** — A local agent per host handles registration, health checks, and DNS so application code stays oblivious — the architecture Consul and the service mesh world converged on.

## How it works

Instances POST their service name, address, port, and metadata to the registry with a TTL, then renew with heartbeats; missed heartbeats mark them unhealthy and expire them. Clients resolve a name via DNS SRV or an HTTP API and get the healthy instance list, caching it and refreshing on watch notifications. An optional sidecar agent runs per host, proxying local DNS queries and performing the health probes, so services themselves need no discovery code at all.

## Build milestones

1. Build a registry HTTP API: register, deregister, and list instances for a named service.
2. Add TTL heartbeats: instances must renew or get expired; verify dead instances disappear from query results.
3. Serve DNS SRV records for registered services so plain `dig` or any DNS client can discover them.
4. Implement watch/long-poll so clients learn about changes instantly instead of polling.
5. Add active health checks (TCP/HTTP probes from the registry) and a sidecar agent that auto-registers local services.

## Best resources

- [Consul documentation](https://developer.hashicorp.com/consul/docs) — service discovery, health checking, and DNS interface; the best production reference for the whole feature set.
- [etcd](https://etcd.io/) — the Raft-backed key-value store under Kubernetes' discovery; study its leases for the TTL/heartbeat model.
- [DNS SRV records (RFC 2782)](https://www.rfc-editor.org/rfc/rfc2782) — the 25-year-old standard for encoding service location in DNS.
- [Serf](https://www.serf.io/) — HashiCorp's gossip-based membership; the AP-side contrast to Raft-backed registries.

## Stretch ideas

- Back your registry with a Raft implementation and demonstrate consistent reads surviving a leader election.
- Build client-side load balancing on top of discovery with automatic retry on a different instance when one fails.
