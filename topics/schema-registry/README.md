---
title: "Schema Registry"
category: "distributed-data"
difficulty: "intermediate"
tags: [schemas, kafka, compatibility]
related: [message-queue, etl-pipeline, event-sourcing-bank]
---

# Schema Registry

In a system with fifty services producing events, who stops someone from renaming `user_id` to `userId` and breaking every consumer? A schema registry: a central service where producers register their event schemas, consumers fetch them, and compatibility rules reject breaking changes. Building one teaches you schema evolution — the unglamorous discipline that keeps distributed data flowing.

## Core concepts

- **Schema as contract** — A formal description (Avro, Protobuf, JSON Schema) of what each event looks like. Registering it makes the contract explicit, versioned, and discoverable instead of tribal knowledge.
- **Subjects and versions** — Schemas are registered under a subject (usually `topic-name-value`), and each registration creates a new numbered version. The full history is retained, so you can always see what version 3 of `orders-value` looked like.
- **Schema IDs in the wire format** — Serialized messages carry a tiny schema ID (not the whole schema). Consumers fetch the schema by ID once and cache it — small messages, fast deserialization, no per-message schema overhead.
- **Compatibility modes** — BACKWARD (new consumers read old data: only add optional fields), FORWARD (old consumers read new data: only remove optional fields), FULL (both), NONE. The registry rejects registrations that violate the configured mode.
- **Compatibility checking** — Real logic, not vibes: for Avro, the registry walks both schemas verifying the reader/writer resolution rules (added field must have a default, type changes must be promotable). This is the code that actually prevents outages.
- **Single-primary design** — The registry assigns globally unique, monotonically increasing schema IDs, which requires one writer at a time; reads scale horizontally. The schema log itself is backed by a Kafka topic, so the registry's state is replayable.
- **Normalization** — Before comparing schemas, the registry canonicalizes them (field ordering, whitespace, equivalent type spellings) so two textually different but semantically identical schemas get the same ID instead of two.

## How it works

A producer serializes an event with the Avro/Protobuf serializer, which first registers the schema (or looks up its existing ID) under the topic's subject. The registry checks the new schema against the latest version under the configured compatibility mode and rejects it if it breaks the contract. On success it returns a numeric ID; the serializer writes a magic byte + the ID + the binary payload into the Kafka message. A consumer reads the ID, fetches the schema from the registry (caching it locally), and deserializes — using schema resolution to map the writer's schema to whatever version the consumer was built against. Evolving a schema is thus a safe, reviewed operation: add an optional field, register version 4, deploy consumers and producers in any order.

## Build milestones

1. Build the registry core: a REST service with `POST /subjects/{name}/versions` (register, returns integer ID) and `GET /schemas/ids/{id}`, backed by SQLite.
2. Add Avro compatibility checking: implement BACKWARD checks (new schema must be able to read data written by the previous version — added fields need defaults) and reject a breaking registration with a clear error.
3. Build the serializer pair: a producer-side serializer that registers-on-first-use and prefixes messages with the schema ID, and a consumer-side deserializer with a local schema cache.
4. Add subject strategies and modes: topic-name strategies plus per-subject compatibility configuration (one subject FULL, another NONE).
5. Impressive end state: a multi-producer demo where a "rogue" service tries to deploy a breaking schema change and gets rejected by the registry, while a compatible evolution rolls out with old and new consumers reading each other's messages — plus a schema diff viewer showing version history.

## Best resources

- [Schema Registry — confluentinc (GitHub)](https://github.com/confluentinc/schema-registry/blob/HEAD/README.md) — The reference implementation's README: architecture, the ID-on-the-wire format, and links into the full docs.
- [Schema Registry Installation / Migration — Confluent Docs](https://docs.confluent.io/platform/7.9/schema-registry/installation/migrate.html) — Shows the production concerns: single-primary deployment and how the Kafka-backed schema topic works.
- [Apache Avro](https://avro.apache.org/) — The schema-first serialization format; its specification defines the reader/writer resolution rules your compatibility checker implements.
- [Protocol Buffers](https://protobuf.dev/) — The other major schema language; its field-numbering discipline is the reason Protobuf evolution is so robust.

## Stretch ideas

- Implement schema normalization and fingerprinting so semantically identical schemas deduplicate to one ID.
- Add a "schema lint" CI check: fail the build if a pull request changes a schema incompatibly, before it ever reaches the registry.
