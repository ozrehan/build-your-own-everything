---
title: "Headless CMS"
category: "web-development"
difficulty: "intermediate"
tags: [cms, api, content]
related: [markdown-renderer, rest-api-client, graphql-server, oauth2-provider]
---

# Headless CMS

A headless CMS stores content (posts, pages, products) and serves it through an API instead of rendering web pages itself — the "head" (frontend) is separate and can be anything. Building one teaches content modeling, API design, media handling, and the draft/publish workflows that make tools like Strapi and Sanity tick.

## Core concepts

- **Content types and fields** — Schemas like "Blog Post has title (text), body (rich text), cover (media), tags (relation)" defined as structured data, often stored as JSON schema plus migrations.
- **Draft / publish workflow** — Content has lifecycle states; editors preview drafts while the public API serves only published versions — implemented as status flags or separate tables.
- **REST and GraphQL delivery APIs** — The CMS auto-generates typed APIs from content types, with filtering, sorting, pagination, and population of relations.
- **Media library** — Uploaded files are stored (local disk or S3-compatible), with metadata, thumbnails/variants generated on upload, and URLs served through the API.
- **Roles and permissions** — Editors, authors, and admins get scoped capabilities per content type (create/read/update/delete/publish), enforced at the API layer.
- **Webhooks** — On publish/unpublish events the CMS POSTs to configured URLs, so frontends can trigger rebuilds or revalidate caches.
- **Localization** — Fields can be translatable, with one entry holding per-locale values and the API accepting a locale parameter.
- **Preview and live editing** — Draft content served to an authenticated preview URL, or visual editing overlays that map API responses back to on-page elements.

## How it works

1. Admins define content types in an admin UI; the CMS stores these schemas and dynamically builds database tables or document collections for them.
2. Editors create entries through the admin panel; entries move from draft to published via the workflow, with revisions tracked.
3. The delivery API serves published content as JSON (REST or GraphQL) with filtering/pagination; media files are served from storage with generated variants.
4. Webhooks fire on publish events so static sites rebuild or SSR caches invalidate.

## Build milestones

1. A JSON-schema-driven content store: define a "post" type, get CRUD REST endpoints auto-generated, entries persisted to SQLite — the core in an evening.
2. Add draft/publish states with a separate public read API that only returns published entries.
3. Add media uploads with thumbnail generation and a media library API.
4. Add API tokens with per-type permissions, filtering/sorting/pagination, and webhooks on publish.
5. Build a minimal admin UI (list, edit form generated from the schema) and a GraphQL endpoint alongside REST.

## Best resources

- [Strapi docs](https://docs.strapi.io/) — the leading open-source headless CMS; its content-type builder and API docs map directly to what you're building.
- [Sanity docs](https://www.sanity.io/docs) — content modeling as code (schemas in JS) and GROQ queries; the best treatment of structured content.
- [Contentful — Concepts](https://www.contentful.com/developers/docs/concepts/) — clear explanations of content modeling, entries, assets, and delivery APIs.
- [Directus docs](https://docs.directus.io/) — shows the "database-first" approach: wrap any SQL database with an instant API and admin app.
- [Payload CMS docs](https://payloadcms.com/docs) — a TypeScript-native CMS whose architecture (collections, hooks, access control) is a great build reference.

## Stretch ideas

- Implement versioned entries with diff/restore, and scheduled publishing.
- Add live preview: an authenticated token renders draft content in the frontend.
