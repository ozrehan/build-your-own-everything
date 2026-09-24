---
title: "Artifact Registry"
category: "devops-infra"
difficulty: "intermediate"
tags: [registry, packages, ci-cd]
related: [ci-runner, container-image-builder, package-manager]
---

# Artifact Registry

Every `docker pull`, `npm install`, and CI build artifact flows through a registry: a service that stores immutable, content-addressed blobs and resolves human-friendly names (`myapp:1.2.3`) to them. Building a mini Docker Hub / npm registry teaches you the OCI distribution protocol, content addressing, and the trust model (signatures, provenance) that keeps software supply chains from collapsing.

## Core concepts

- **Content-addressed storage** — blobs are stored and referenced by their SHA-256 digest, never by name. Identical content is stored once (deduplication), and any corruption is detectable on read — the integrity guarantee everything else rests on.
- **OCI distribution API** — the wire protocol: `POST /v2/<name>/blobs/uploads/` starts an upload, `PATCH` streams chunks, `PUT` finalizes with the digest; `PUT /v2/<name>/manifests/<tag>` publishes. Pulls reverse it, and clients skip blobs they already have.
- **Tags vs digests** — a tag is a mutable pointer (`latest` moves); a digest is immutable. Production systems pin digests because tags can be repointed — the difference between reproducible deploys and mystery breakage.
- **Manifests and media types** — a manifest lists the config blob and layer blobs with their digests and media types; manifest lists (fat manifests) point to per-architecture manifests, which is how one tag serves both amd64 and arm64.
- **Authentication and scoped tokens** — registries issue short-lived bearer tokens scoped to specific repositories and actions (`pull`, `push`), often minted via a token server after the client authenticates. Push and pull have different trust levels.
- **Garbage collection** — deleting a tag doesn't delete blobs (other tags may reference them). A GC pass marks all blobs reachable from existing manifests and sweeps the rest, usually during a maintenance window with the registry in read-only mode.
- **Signatures and provenance** — cosign-style signatures and SLSA attestations bind a digest to "built by CI job X from commit Y". The registry stores these as associated artifacts so clients can verify before pulling.

## How it works

The registry exposes the OCI distribution API over HTTPS. On push, the client starts an upload session, streams blob chunks (resumable via `Range` on failure), and finalizes with the expected digest — the server verifies the hash before accepting. Blobs land in content-addressed storage (a directory tree sharded by digest prefix, or object storage). The client then uploads the manifest JSON referencing those digests and assigns it a tag; the server validates that all referenced blobs exist before recording the tag→digest mapping.

On pull, the client resolves tag→digest, fetches the manifest, then downloads each blob it doesn't already have, verifying hashes as it goes. Authentication is a token exchange: the client presents credentials to the token server, receives a JWT scoped to `repository:myapp:pull,push`, and the registry validates the token's signature and scope on every request. A background GC job periodically computes the reachable blob set from all manifests and deletes orphans.

## Build milestones

1. Build a registry that implements blob upload/download by digest with on-disk content-addressed storage, plus manifest PUT/GET and tag resolution. Verify with `docker push`/`docker pull` against it.
2. Add resumable chunked uploads, manifest lists for multi-arch images, and `crane`-compatible behavior for the core endpoints.
3. Implement token-based auth with scoped JWTs (separate pull/push scopes), per-repository access control, and a garbage collector for unreferenced blobs.
4. Add vulnerability-scan hooks on push, signature storage/verification (cosign-style), retention policies per repository, and replication to a second registry instance.

## Best resources

- [OCI Distribution Specification](https://github.com/opencontainers/distribution-spec) — the exact API contract: uploads, mounts, manifests, tags, and auth challenges. Your implementation spec.
- [Harbor](https://goharbor.io/) — the CNCF open-source registry: replication, vulnerability scanning, RBAC, and retention policies; the feature checklist for a production-grade build.
- [Sonatype Nexus Repository documentation](https://help.sonatype.com/repomanager3) — multi-format registries (npm, PyPI, Maven, Docker) in one service; shows how the content-addressed core generalizes across ecosystems.
- [Debian Repository Format](https://wiki.debian.org/DebianRepository/Format) — the older, simpler package repository design (Packages indices, Release signatures); a great contrast to OCI's blob model.

## Stretch ideas

- Build a pull-through cache: proxy upstream registries, cache blobs locally, and serve air-gapped environments.
- Implement cross-repository blob mounting so CI pipelines can push shared base layers without re-uploading bytes.
- Add SLSA provenance generation: attest every pushed artifact with its build inputs and expose a verification endpoint.
