---
title: "Notification Fanout"
category: "distributed-data"
difficulty: "intermediate"
tags: [notifications, fanout, scalability]
related: [pubsub-broker, message-queue, websocket-server]
---

# Notification Fanout

When a celebrity with 10 million followers posts, the system must create 10 million inbox entries in seconds — without making normal users wait behind the celebrity. Notification fanout is the write-vs-read tradeoff at the heart of every feed, inbox, and push system. Building it teaches you push vs pull, hot keys, and graceful degradation under celebrity load.

## Core concepts

- **Fan-out on write (push)** — When user X posts, immediately write the post ID into every follower's inbox/timeline. Reads are then a single fast lookup — but a celebrity post is a 10-million-write thundering herd.
- **Fan-out on read (pull)** — Don't precompute; at read time, gather the recent posts of everyone the user follows and merge them. Writes stay cheap, but reads do the expensive merge — and caching gets complicated.
- **Hybrid fanout** — The production answer: push for normal users, pull for celebrities. Followers of a celebrity read that celebrity's posts on demand (merged at read time), while everyone else's posts are pushed. The threshold (e.g. 10k followers) is the tuning knob.
- **Hot keys / celebrity problem** — A tiny fraction of users generate most of the fanout work. Any design that treats all users identically will collapse the first time a mega-account posts; sharding and special-casing hot keys is mandatory.
- **Delivery vs notification** — Storing "this belongs in your feed" (delivery) is separate from "ping their phone" (notification). Push notifications add device targeting, batching ("3 new posts"), and per-user preferences on top of the fanout.
- **Inbox vs outbox storage** — Inbox: per-user list of received item IDs (fast reads, expensive writes). Outbox: per-author list of posts (cheap writes, merge at read). The choice is literally the push/pull decision expressed as schema.
- **Graceful degradation** — Under extreme load, it's acceptable for a celebrity's post to appear in followers' feeds over minutes rather than seconds. Prioritizing normal users' latency while letting celebrity fanout lag is a deliberate, correct tradeoff.

## How it works

Each user has an inbox (a sorted set or list, newest first, capped at some N). On post: look up the author's follower count. If below the celebrity threshold, iterate followers and push the post ID into each inbox (batched, in the background via a queue — the HTTP request returns immediately). If above the threshold, write only to the author's outbox and mark followers' timelines as needing a merge. On timeline read: fetch the user's inbox, fetch recent outbox posts from each followed celebrity, merge-sort by timestamp, and return the top page. A background worker drains the fanout queue, and per-user rate limits plus inbox caps bound the worst case. Push notifications are a second pipeline: the fanout worker checks each recipient's notification preferences and batches device pushes.

## Build milestones

1. Build naive push fanout: on post, synchronously write to every follower's inbox in Redis/SQLite; measure how latency explodes as follower count grows.
2. Add async fanout: put fanout jobs on a queue, return from the POST immediately, and have workers drain the queue — then add the celebrity threshold with pull-on-read merging.
3. Add the read path properly: merged timelines (inbox + celebrity outboxes), pagination with cursors, and inbox caps so storage stays bounded.
4. Add push notifications: per-user preferences (mute, batching window), device tokens, and a digest mode ("5 new posts in the last hour" as one push).
5. Impressive end state: simulate 100k users including 10 "celebrities" with 50k followers each; post as a celebrity and show p99 post latency unaffected, timelines correct, and a load graph proving the hot key is contained — then demo the degradation dial (fanout lag vs freshness).

## Best resources

- [Fan-out — Wikipedia](https://en.wikipedia.org/wiki/Fan-out) — The general pattern across electronics, messaging, and software; good for the vocabulary.
- [Apache Kafka](https://kafka.apache.org/) — The durable queue your async fanout workers will drain; understanding consumer groups is prerequisite to scaling the write path.
- [Firebase Cloud Messaging](https://firebase.google.com/docs/cloud-messaging) — The docs for the last-mile device push side: topics, batching, and delivery semantics.
- [PubNub](https://www.pubnub.com/) — A realtime pub/sub platform whose docs and architecture explain the push-notification and presence side of fanout at scale.

## Stretch ideas

- Implement "stories"-style ephemeral fanout with TTLs, where inbox entries expire and storage reclaims itself.
- Add smart batching: learn per-user activity patterns and send one digest push at the time they're most likely to open the app.
