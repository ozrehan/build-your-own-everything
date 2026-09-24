---
title: "Mini Terraform (IaC)"
category: "devops-infra"
difficulty: "intermediate"
tags: [iac, terraform, cloud]
related: [config-management, service-discovery, compose-alternative]
---

# Mini Terraform (IaC)

Infrastructure as Code tools let you declare "I want 3 VMs and a load balancer" in a file and have software make reality match. Terraform's core trick is a three-way comparison: your config (desired), the state file (what it last created), and the real cloud (actual) — reconciled into a plan of creates, updates, and deletes. Building a mini-Terraform against a fake cloud provider teaches you the entire IaC mental model, including why state files are the source of so much drama.

## Core concepts

- **Declarative desired state** — you describe *what* you want (resources and their attributes), not the API calls to create it. The tool derives the steps, which is what makes configs reviewable and repeatable.
- **State as a mapping table** — the state file records resource address → real-world ID (e.g. `vm.web` → `i-0abc123`). Without it, the tool can't tell "update this VM" from "create a duplicate", and renames become destroy+create.
- **Plan/apply two-phase workflow** — `plan` computes the diff (create/update/delete/no-op per resource) and shows it for review; `apply` executes it. This separation is the safety rail that lets teams approve infrastructure changes like code.
- **Dependency graph and ordering** — resources reference each other (`subnet.vpc_id = vpc.main.id`), forming a DAG. Terraform topologically sorts it so the VPC is created before the subnet, and destroys in reverse.
- **Providers as plugins** — the core engine is cloud-agnostic; providers translate resource schemas into real API calls (AWS, Docker, a fake local provider). Your engine speaks to providers over a stable interface, so new clouds need no core changes.
- **Drift detection** — reality changes outside the tool (someone clicks in the console). Refreshing state from the provider API before planning reveals drift, and `apply` can bring things back — the "configuration drift" loop.
- **Idempotency of apply** — running apply twice with no config change must produce zero API calls. Every resource's "does it already match?" check (read → compare → skip) is what makes this true.

## How it works

The engine parses HCL-like config files into resource blocks with attributes and references. It builds a dependency graph from the references and loads the state file (JSON) from the previous run. In the refresh phase it calls each provider's `Read` for every tracked resource, updating state to reflect reality and flagging drift.

Planning walks the graph: for each resource it compares desired config, refreshed state, and (for computed attributes) provider defaults, producing an action per resource — create, update-in-place, replace (delete+create when an immutable attribute changed), or no-op. The plan is serialized and shown to the user. Apply executes the graph in topological order with bounded parallelism, calling `Create`/`Update`/`Delete`, and writes a new state file after each successful operation so an interrupted apply can resume without duplicating resources.

## Build milestones

1. Build an engine with a fake provider (in-memory or local files as "resources"): parse simple config, keep state in JSON, and implement create/delete with address→ID mapping.
2. Add plan/apply separation with a human-readable diff output, plus update-in-place for mutable attributes and replace semantics for immutable ones.
3. Implement the dependency graph with topological ordering, parallel apply with a worker pool, and state locking (refuse concurrent applies).
4. Add drift detection via a refresh phase, remote state backends (S3-like), and a second provider (e.g. a Docker provider that manages containers), proving the provider abstraction works.

## Best resources

- [Terraform documentation](https://developer.hashicorp.com/terraform/docs) — the canonical reference for configuration language, state, plan/apply, and the resource lifecycle; read it as the spec you're reimplementing.
- [OpenTofu documentation](https://opentofu.org/docs/) — the open-source Terraform fork; its internals docs and state format are freely inspectable and community-maintained.
- [Pulumi documentation](https://www.pulumi.com/docs/) — the imperative/general-purpose-language alternative; comparing its engine to Terraform's clarifies what the graph-based model buys you.
- [Kubernetes Controllers documentation](https://kubernetes.io/docs/concepts/architecture/controller/) — the control-loop/reconciliation pattern is the same idea as IaC applied to a running cluster; essential context for drift correction.

## Stretch ideas

- Implement `import` (adopt existing real resources into state) and `moved` blocks (rename without destroy), the two features that make state surgery survivable.
- Add a policy engine: evaluate plans against rules ("no public S3 buckets", "all resources tagged") before apply, like Sentinel/OPA.
- Build a plan visualizer: render the dependency graph and per-resource actions as an interactive DAG in the browser.
