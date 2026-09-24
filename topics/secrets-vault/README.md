---
title: "Secrets Vault"
category: "devops-infra"
difficulty: "intermediate"
tags: [security, secrets, encryption]
related: [certificate-authority, password-hashing, audit-logger]
---

# Secrets Vault

API keys, database passwords, and TLS private keys can't live in Git and shouldn't live in env files scattered across laptops. A secrets vault is a hardened service that stores secrets encrypted, hands them out only to authenticated clients with the right policy, rotates them, and audits every access. Building one teaches you the real security primitives — envelope encryption, Shamir sealing, short-lived credentials — that make HashiCorp Vault and AWS Secrets Manager trustworthy.

## Core concepts

- **Envelope encryption** — secrets are encrypted with a data-encryption key (DEK), and the DEK itself is encrypted with a key-encryption key (KEK) held in a KMS/HSM. You can rotate the KEK by re-wrapping DEKs without re-encrypting every secret, which makes rotation cheap and safe.
- **Seal/unseal and Shamir's Secret Sharing** — at rest, the vault's master key is split into N shares requiring M-of-N to reconstruct (Shamir's scheme). No single operator can decrypt the vault alone; unsealing is a deliberate multi-person ceremony.
- **Authentication vs authorization** — clients authenticate via tokens, TLS certs, cloud IAM, or Kubernetes service accounts; policies then authorize *which paths* each identity can read/write. AuthN proves who you are, AuthZ decides what you get.
- **Dynamic secrets** — instead of storing a long-lived database password, the vault mints short-lived credentials on demand (e.g. a Postgres role valid for 1 hour) and revokes them at lease expiry. Stolen credentials expire before they can be abused.
- **Leases and renewal** — every secret access grants a lease with a TTL; clients must renew, and the vault revokes on expiry. Leases turn "who has my password?" from an unanswerable question into a queryable list.
- **Audit logging** — every request and response (with secrets redacted) is written to an append-only audit log. The audit log is the vault's own immune system: it proves who accessed what, when, and is itself tamper-evident.
- **Response wrapping** — for bootstrapping trust, the vault can return a single-use wrapping token instead of the secret itself; the intended recipient unwraps it once. This solves "how do I safely hand a secret to a brand-new machine?"

## How it works

At rest, all secrets live in a storage backend (files, Consul, a database) encrypted with AES-GCM under DEKs, which are wrapped by the master key. On startup the vault is *sealed*: it holds only the encrypted master key. Operators submit Shamir shares until the threshold is met, the master key is reconstructed in memory, DEKs are unwrapped, and the vault opens — the master key never touches disk.

Clients authenticate (say, with a Kubernetes service account token the vault validates against the K8s API) and receive a short-lived token bound to policies. A read request checks the policy, decrypts the secret from storage, writes a redacted audit entry, and returns the value with a lease. A background reaper revokes expired leases — for dynamic secrets this means calling the database to drop the temporary user. Rotation is a first-class operation: generate a new value, store it, and (for dynamic secrets) let old leases die naturally.

## Build milestones

1. Build an encrypted KV store: AES-GCM encryption of secrets at rest, a master key held only in memory, and a token-authenticated HTTP API with per-path policies.
2. Add Shamir seal/unseal: split the master key into 5 shares (3 to unseal), persist the sealed state, and require the unseal ceremony after every restart.
3. Implement leases with TTL + renewal, an append-only audit log with hash chaining, and response wrapping for single-use secret delivery.
4. Add dynamic secrets for one backend (e.g. mint ephemeral Postgres users), automatic rotation, and at least two auth methods (token + TLS client certs).

## Best resources

- [HashiCorp Vault documentation](https://developer.hashicorp.com/vault/docs) — the definitive reference: seal/unseal, auth methods, policies, dynamic secrets, and audit devices. Your architecture spec.
- [SOPS (Secrets OPerationS)](https://github.com/getsops/sops) — encrypts secrets in Git with envelope encryption via KMS/PGP; the best small-scale example of the DEK/KEK pattern done right.
- [age encryption tool](https://github.com/FiloSottile/age) — a modern, minimal file encryption tool by Filippo Valsorda; excellent for understanding simple, auditable crypto design.
- [Sealed Secrets](https://github.com/bitnami-labs/sealed-secrets) — encrypts Kubernetes secrets so only the in-cluster controller can decrypt; a great study in asymmetric sealed-box patterns.
- [AWS KMS concepts — envelope encryption](https://docs.aws.amazon.com/kms/latest/developerguide/concepts.html) — the clearest explanation of data keys, key hierarchy, and why envelope encryption exists.

## Stretch ideas

- Implement automatic credential rotation for a real database, with dual-password overlap so rotation never causes an outage.
- Add a transit encryption-as-a-service endpoint: clients send plaintext and get ciphertext without ever seeing the key, like Vault's transit engine.
- Build break-glass access: emergency unseal with mandatory MFA, time-boxed, and every action during the window highlighted in the audit log.
