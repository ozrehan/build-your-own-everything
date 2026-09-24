---
title: "Container Image Builder"
category: "devops-infra"
difficulty: "advanced"
tags: [containers, oci, images]
related: [artifact-registry, process-orchestrator, chroot-sandbox]
---

# Container Image Builder

`docker build` feels like magic: a Dockerfile becomes a portable image you can run anywhere. Underneath, an image is just a stack of tar archives (layers) plus JSON metadata describing how to stack them and what command to run. Building your own image builder — parsing a Dockerfile, snapshotting filesystem changes per instruction, and pushing to a registry — teaches you that containers are a packaging format first and a runtime second.

## Core concepts

- **OCI image layout** — an image is a manifest (JSON) pointing to a config blob (env vars, entrypoint, layer digests) and a list of layer blobs, each a gzipped tar of filesystem diffs. Every blob is content-addressed by its SHA-256 digest.
- **Layered filesystem and copy-on-write** — layers stack like transparencies: a file added in layer 3 shadows (but does not delete) the same path in layer 1. Deletions are recorded as special "whiteout" files. This is why small changes produce small new layers.
- **Dockerfile instructions as state machine** — each instruction (`RUN`, `COPY`, `ENV`, ...) is a transformation from one filesystem snapshot to the next. `RUN` executes a command in a container and diffs the filesystem before/after; the rest just mutate metadata or copy files in.
- **Build cache and cache invalidation** — each instruction's result is keyed by a hash of its inputs (parent layer digest + instruction text + file contents). If nothing changed, the cached layer is reused; one changed byte early in the file invalidates everything after it.
- **Multi-stage builds** — named build stages let you compile in a fat image (with toolchains) and `COPY --from=builder` only the final binary into a slim runtime image, a pattern that shrinks images from gigabytes to megabytes.
- **Registry push protocol** — pushing means uploading each blob via the OCI distribution API, then PUTing the manifest. Pulls work in reverse and skip blobs already present, which is why layer reuse speeds up both pushes and pulls.
- **Reproducibility and determinism** — real builders normalize timestamps, file order, and ownership so the same inputs produce the same digests; without this, cache hits and security audits break.

## How it works

The builder parses the Dockerfile into an ordered list of instructions. It starts from the base image referenced by `FROM` — either fetched from a registry or an empty scratch root. For each instruction, it creates a working container from the current layer stack: `RUN` executes the command inside a chroot/network namespace with the lower layers mounted read-only via overlayfs, then computes the filesystem diff against the parent snapshot and packs it into a new layer tarball. `COPY`/`ADD` diff the host files being added. `ENV`, `WORKDIR`, `EXPOSE`, `CMD`, `ENTRYPOINT` only update the config JSON.

Each new layer is hashed and stored in a local content-addressed cache. After the final instruction, the builder assembles the image config, computes the manifest, and pushes: blobs first (with resumable chunked uploads), then the manifest tagged with the requested name. Because layers are shared, a rebuild that only changed the last `RUN` uploads exactly one new blob.

## Build milestones

1. Write a tool that takes a directory and produces a single-layer OCI image: tar the directory, compute SHA-256, write the config + manifest JSON in OCI layout, and verify it with `crane` or `skopeo`.
2. Add a minimal Dockerfile parser supporting `FROM` (scratch only), `COPY`, `ENV`, `WORKDIR`, `CMD`: execute against a chroot and snapshot per-instruction layers.
3. Implement `RUN` by executing commands in a container with overlayfs lower dirs, diffing the upper dir afterward; add layer caching keyed by instruction hash and push support to a local registry.
4. Support multi-stage builds with `COPY --from`, `.dockerignore`, build args, and `ARG`; then benchmark your builder's cache behavior against BuildKit on a real project.

## Best resources

- [OCI Image Format Specification](https://github.com/opencontainers/image-spec) — the definitive spec for manifests, configs, layers, and media types; everything a builder emits must conform to it.
- [BuildKit repository](https://github.com/moby/buildkit) — the actual code behind `docker build`; read its Dockerfile frontend and LLB (low-level build) graph to see how instructions become a parallelizable build plan.
- [Kaniko](https://github.com/GoogleContainerTools/kaniko) — builds images inside a container without a Docker daemon by snapshotting the filesystem after each command; the closest real-world analog to a hand-built builder.
- [Dockerfile best practices](https://docs.docker.com/build/building/best-practices/) — ordering instructions for cache efficiency, multi-stage patterns, and minimizing layer count; the practical half of the theory.
- [Buildah](https://buildah.io/) — daemonless image building from scripts instead of Dockerfiles; great for understanding the container-then-commit model your milestone 2 implements.

## Stretch ideas

- Implement remote build cache: store layer cache records in a registry so a fresh machine reuses layers built elsewhere, like BuildKit's `type=registry` cache exporter.
- Add build provenance: emit SLSA-style attestations recording the base image digest, source commit, and builder version for supply-chain verification.
- Support hermetic builds: disable network during `RUN`, pin all external inputs by digest, and verify two builds byte-for-byte identical.
