---
title: "Config Management"
category: "devops-infra"
difficulty: "intermediate"
tags: [configuration, automation, ansible]
related: [iac-mini-terraform, compose-alternative, secrets-vault]
---

# Config Management

Installing nginx on one server is a command; installing it identically on two hundred, keeping it that way, and knowing when someone changed one by hand — that's configuration management. Tools like Ansible and Puppet converge machines to a declared state using idempotent operations. Building a mini-Ansible (inventory, playbooks, SSH execution, idempotent modules) teaches you why "run this command everywhere" fails and what replaces it.

## Core concepts

- **Idempotency** — running the same playbook twice must produce the same result with no changes the second time. Every module checks current state first ("is the package already installed?") and only acts on drift. Without idempotency, automation is just a faster way to break things twice.
- **Declarative state vs imperative steps** — you declare `package: nginx, state: present` rather than `apt-get install nginx`. The tool figures out the steps, which makes playbooks readable as documentation and safe to re-run.
- **Inventory and grouping** — hosts organized into groups (`webservers`, `db`, `prod`) with group variables and per-host overrides. Targeting is a first-class concept: the same playbook behaves differently per group by design.
- **Agentless push over SSH** — Ansible's signature move: no agent installed on targets; it SSHes in, copies a small Python script, runs it, and deletes it. This trades per-run connection overhead for zero fleet-wide agent maintenance.
- **Facts gathering** — before doing anything, the tool collects facts about each host (OS, IPs, memory, disks). Playbooks branch on facts (`when: ansible_os_family == "Debian"`), making one playbook portable across distros.
- **Handlers and change notification** — a task that changes something notifies a handler (e.g. "restart nginx"), which runs once at the end. This batches restarts and avoids restarting a service five times when five config files changed.
- **Secrets in config** — configs contain passwords and keys, so real systems encrypt values at rest (Ansible Vault, SOPS) and decrypt only in memory on the control machine. Plaintext secrets in playbooks are the classic config-management sin.

## How it works

The engine reads an inventory (hosts, groups, variables) and a playbook (ordered plays, each with tasks targeting a host group). For each play it opens SSH connections to the target hosts — with connection multiplexing and a fork pool for parallelism. It first runs the setup module on each host, collecting facts into per-host variable scopes.

Then it executes tasks in order: each task names a module (`apt`, `copy`, `template`, `service`) with arguments. The engine ships the module code to the host, runs it with the arguments, and parses the JSON result, which reports `changed: true/false`. Templating (Jinja2-style) renders config files from variables and facts before comparison — a template that renders identically to the file on disk reports no change. Tasks that report changes trigger their notified handlers, which run once after all tasks. A final recap shows per-host changed/failed counts.

## Build milestones

1. Build an SSH runner: read an inventory file, connect to each host in parallel, run a shell command, and report per-host output. This alone is genuinely useful.
2. Add idempotent modules: `copy` (only write when content differs), `package` (check installed first), `service` (ensure running/enabled) — each returning changed/failed as structured data.
3. Add a playbook format (YAML: plays → tasks → modules), variable precedence (host > group > defaults), facts gathering, and Jinja-style templating for config files.
4. Implement handlers with change-triggered notification, `--check` dry-run mode showing what *would* change, and encrypted secret values decrypted only in memory.

## Best resources

- [Ansible documentation](https://docs.ansible.com/ansible/latest/index.html) — the canonical reference for playbooks, inventory, modules, and vault; the design you're reimplementing.
- [The Twelve-Factor App — Config](https://12factor.net/config) — the philosophy of strict separation between code and config via environment; essential context for *what* you're managing.
- [NixOS manual](https://nixos.org/manual/nixos/stable/) — the purely functional extreme: the entire system as a pure function of a config file; shows where declarative config management logically ends.
- [etcd documentation](https://etcd.io/docs/) — the distributed KV store behind dynamic config; understand it and you understand how config propagates to running services, not just files on disk.

## Stretch ideas

- Add pull mode: agents on hosts periodically fetch desired config and converge locally, for hosts behind NAT or with flaky SSH.
- Implement config drift detection as a scheduled audit: report (don't fix) hosts that diverged from the playbook since last run.
- Build a module SDK so users can write custom idempotent modules in any language with a simple JSON protocol.
