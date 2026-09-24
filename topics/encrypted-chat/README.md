---
title: "Encrypted Chat"
category: "security"
difficulty: "intermediate"
tags: [e2ee, messaging, cryptography]
related: [websocket-chat, totp-2fa, tls-handshake]
---

# Encrypted Chat

End-to-end encrypted chat means only the two people talking can read the messages — not the server operator, not anyone tapping the wire. Building your own teaches you the protocols (X3DH, Double Ratchet) that make modern secure messaging work, and why "encrypted in transit" is a much weaker promise.

## Core concepts

- **End-to-end encryption (E2EE)** — Keys live only on the endpoints; the server relays ciphertext it cannot read, which is fundamentally different from TLS where the server sees plaintext.
- **X3DH key agreement** — The initial handshake: combining identity keys, signed prekeys, and one-time prekeys in multiple Diffie-Hellman operations so two strangers can establish a shared secret asynchronously.
- **Double Ratchet** — The ongoing key evolution: a symmetric ratchet derives a fresh message key per message (forward secrecy), and a DH ratchet mixes in new key material on each reply (post-compromise healing).
- **Forward secrecy** — Deleting old message keys after use means a stolen phone can't decrypt last month's messages — only future ones.
- **Post-compromise security** — The DH ratchet's self-healing: after an attacker briefly steals keys, the next honest key exchange locks them out again.
- **Deniability** — Signal-style protocols use symmetric MACs rather than signatures for message authentication, so neither party can cryptographically prove to a third party what the other said.
- **The server-trust problem** — E2EE still trusts the server for identity: if it hands you the wrong public key for your contact, it can man-in-the-middle you — which is why safety numbers / key verification exist.

## How it works

When Alice first messages Bob, her client fetches Bob's prekey bundle from the server (identity key, signed prekey, one-time prekey) and runs X3DH: four Diffie-Hellman operations mixing her ephemeral and identity keys with his, producing a shared secret that seeds the Double Ratchet. She can send immediately — no round trip with Bob needed.

From then on, every message advances the symmetric ratchet: the chain key is HMAC'd forward to derive the message key (used once, then deleted) and the next chain key. Each reply also performs a DH ratchet step with fresh ephemeral keys, mixing new entropy into the root key. Building a two-client demo that does X3DH + Double Ratchet over a dumb relay server shows you exactly which properties come from which ratchet — break one in a test and watch forward secrecy or healing fail independently.

## Build milestones

1. Build a relay server (dumb pipe: stores and forwards ciphertext blobs, never sees keys) plus a CLI client with X25519 identity keys.
2. Implement X3DH session setup: prekey bundles, the four-DH handshake, and first-message encryption.
3. Implement the Double Ratchet: symmetric chain per message, DH ratchet on new keys, out-of-order message handling with skipped-key storage.
4. Add safety-number verification: display a fingerprint of both identity keys for out-of-band comparison.
5. Add group chat via pairwise sessions or study MLS (RFC 9420) and prototype a two-party version of its tree-based key agreement.

## Best resources

- [Signal Protocol Documentation](https://signal.org/docs/) — The official docs hub for the protocol family behind Signal, WhatsApp, and others.
- [The Double Ratchet Algorithm spec](https://signal.org/docs/specifications/doubleratchet/) — The precise spec for the ratchet: read it alongside your implementation.
- [The X3DH Key Agreement Protocol](https://signal.org/docs/specifications/x3dh/) — The async handshake spec; short and implementable.
- [RFC 9420 — Messaging Layer Security (MLS)](https://www.rfc-editor.org/rfc/rfc9420.html) — The IETF standard for efficient group E2EE; the future of group messaging.
- [Off-the-Record (OTR) Messaging](https://otr.cypherpunks.ca/) — The earlier protocol that pioneered deniability and forward secrecy in chat.

## Stretch ideas

- Add sealed-sender-style metadata protection: hide who's talking to whom from the relay server, not just message contents.
- Implement key-change warnings and a re-verification flow when a contact's identity key rotates.
