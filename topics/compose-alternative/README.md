---
title: "Compose Alternative"
category: "devops-infra"
difficulty: "intermediate"
tags: [containers, orchestration, docker]
related: [container-runtime-basics, config-management, iac-mini-terraform]
---

# Compose Alternative

`docker compose up` turns a YAML file into a running multi-container application: networks created, volumes mounted, containers started in dependency order, logs interleaved. Building your own Compose teaches you the surprisingly deep problems hiding behind that one command — service dependency graphs, network isolation per project, variable interpolation, and the reconciliation loop that makes `up` idempotent.

## Core concepts

- **The Compose file as a service graph** — services, networks, and volumes declared together; `depends_on` plus healthchecks define startup order. The file is a small declarative orchestration language, and parsing/interpolating it correctly (variables, extends, multiple files) is real work.
- **Project isolation** — every resource gets a project prefix (`myapp_web_1`, network `myapp_default`) so two projects never collide. Naming, labeling everything, and filtering by label is the mechanism behind `compose down` knowing exactly what to remove.
- **Networks per project** — Compose creates a dedicated bridge network per project with an embedded DNS server, so `web` resolves to the `web` container's IP. Service discovery falls out of DNS naming — no config needed for containers to find each other.
- **Dependency ordering vs readiness** — `depends_on` controls start order, but order isn't health. `depends_on: { condition: service_healthy }` waits for healthchecks, closing the race where the app starts before its database accepts connections.
- **Reconciliation on `up`** — Compose compares the desired state (file) with actual state (running containers, labeled): create missing, recreate changed (image or config hash differs), leave the rest. Idempotent `up` is a mini control loop.
- **Build + run unification** — Compose orchestrates image builds (`build:` context) before container creation, wiring build args and caching into the same workflow as runtime config. It's the bridge between your image builder and your running system.
- **One-shot commands and exec** — `compose run` starts a one-off container attached to the project's network (migrations, shells); `compose exec` runs a process in an existing container. These need the same networking/volume context as the long-running services.

## How it works

The tool parses the Compose file (YAML with variable interpolation from the environment and `.env` files, merging multiple `-f` files), validates it against the Compose spec schema, and builds the service dependency graph. It ensures the project's network and volumes exist (creating them with project-prefixed names and labels if missing), then topologically sorts services.

For each service in order: resolve the image (build it first if a `build` section exists, or pull if missing), compare the desired container config hash against any existing project container — if identical and running, skip; otherwise stop/remove and create fresh. Container creation maps Compose concepts to runtime calls: port mappings, volume mounts, environment, `depends_on` health-gating (poll the dependency's healthcheck before starting), and DNS aliases on the project network. `logs` multiplexes the containers' log streams with service-name prefixes and color; `down` finds everything by project label and removes it in reverse dependency order.

## Build milestones

1. Parse a minimal Compose file (services with image, ports, environment), create containers via the Docker/Podman API in dependency order on a shared network, and implement `up`/`down`/`ps`.
2. Add variable interpolation (`.env` + shell env), named volumes, project-name prefixing with labels, and `logs -f` with multiplexed, prefixed output.
3. Implement healthcheck-gated `depends_on`, config-hash-based recreation (only recreate what changed), and `run`/`exec` one-shot commands.
4. Add `build` support wired to your image builder, multi-file merging (`-f base.yml -f override.yml`), and watch mode that rebuilds/restarts on file changes.

## Best resources

- [Compose Specification](https://github.com/compose-spec/compose-spec) — the vendor-neutral spec: file format, interpolation, dependencies, deploy semantics. Your implementation contract.
- [Docker Compose documentation](https://docs.docker.com/compose/) — the reference implementation's docs; best for understanding `up` behavior, networking, and the CLI surface.
- [podman-compose](https://github.com/containers/podman-compose) — a from-scratch Python reimplementation of Compose against Podman; the closest existing analog to this project and highly readable.
- [Podman systemd integration (Quadlet)](https://docs.podman.io/en/latest/markdown/podman-systemd.unit.5.html) — the alternative end-state: generating systemd units from container definitions instead of a long-running daemon; shows where Compose-like ideas lead.

## Stretch ideas

- Add `compose watch`-style sync: copy changed files into running containers without rebuilding, for fast dev loops.
- Implement profiles and conditional services: subsets of the stack (e.g. `--profile debug`) for different workflows from one file.
- Build a TUI dashboard: live container states, resource usage, and log tailing in a single terminal UI, like lazydocker for your Compose.
