---
title: "Form Validation Library"
category: "web-development"
difficulty: "beginner"
tags: [forms, validation, schemas]
related: [web-components-library, i18n-system, test-runner-framework, rest-api-client]
---

# Form Validation Library

A form validation library turns declarative rules ("email, required, min 8 chars") into field-level error messages, touched-state tracking, and submit gating. Building one teaches schema design, sync/async validation orchestration, and the UX details — when to show errors, how to localize them — that separate good forms from frustrating ones.

## Core concepts

- **Schema-first validation** — Rules declared as data (objects or a builder API) instead of imperative `if` chains, so the same schema can validate on client and server and generate TypeScript types.
- **Field state machine** — Each field tracks `value`, `touched`, `dirty`, and `errors`; errors typically show only after touch or submit attempt — the core UX rule of form libraries.
- **Sync vs async validators** — Sync rules (required, minLength, regex) run instantly; async rules (username availability) need debouncing, cancellation of stale requests, and pending states.
- **Cross-field validation** — Rules spanning fields ("passwords must match", "end date after start date") need access to the whole form value, not just one field.
- **Error message pipeline** — Validators return error codes, and a separate message layer maps codes to human strings — which is also where i18n plugs in.
- **Nested and array fields** — Real forms have lists (phone numbers) and nested objects (address); paths like `addresses[0].zip` and per-item validation make this work.
- **Submit orchestration** — On submit: touch all fields, run all validators, block submission on errors, focus the first invalid field, and handle async submission states.
- **Native constraint validation** — The browser's built-in `required`, `pattern`, and `setCustomValidity()` API; a good library complements rather than fights it.

## How it works

1. You declare a schema mapping field paths to rule lists; the library compiles it into validator functions.
2. On input/blur, the library updates field state, runs the relevant validators, and stores error codes per field.
3. Error codes are mapped through the message catalog (with i18n) and rendered next to fields, respecting touched/dirty visibility rules.
4. On submit, all fields are validated, async rules resolve with cancellation, and the submit handler only fires when everything passes.

## Build milestones

1. A `validate(values, schema)` function with required/minLength/pattern/email rules returning an errors object — working in an evening.
2. Add a form-state manager: touched/dirty tracking, per-field error visibility, and a vanilla-JS or framework binding.
3. Add async validators with debounce and stale-request cancellation, plus cross-field rules.
4. Add nested objects and field arrays with path-based errors, and a message catalog with pluggable i18n.
5. Add schema-to-TypeScript inference (or JSON Schema export) so the same schema types your form values.

## Best resources

- [Constraint Validation — MDN](https://developer.mozilla.org/en-US/docs/Web/HTML/Guides/Constraint_validation) — the native browser validation API your library builds on.
- [Zod on GitHub](https://github.com/colinhacks/zod) — the schema library that defined the modern API; study its composable design.
- [Vest](https://vestjs.dev/) — a validation framework with a unique "suite" model; great alternative architecture to study.
- [Ajv — JSON Schema validator](https://ajv.js.org/) — the fastest JSON Schema validator; shows how compiled validators outperform interpreted ones.

## Stretch ideas

- Build a visual schema builder UI that exports your schema format.
- Add conditional validation (rules that activate based on other fields' values) with a dependency graph.
