---
title: "Web Components Library"
category: "web-development"
difficulty: "beginner"
tags: [web-components, custom-elements, library]
related: [spa-router, form-validation-library, css-layout-engine, i18n-system]
---

# Web Components Library

Web Components are the browser's native component model: custom elements, shadow DOM, and templates, working in any framework or none. Building a small component library on them teaches encapsulation without a build step, the custom-element lifecycle, and how to design an API (attributes, properties, events, slots) that feels native.

## Core concepts

- **Custom elements** — `customElements.define('my-button', class extends HTMLElement)` registers a new tag; the browser upgrades existing markup automatically, even before your script loads.
- **Lifecycle callbacks** — `connectedCallback` (added to DOM), `disconnectedCallback` (removed), `attributeChangedCallback` (observed attributes change) — the hooks your components live in.
- **Shadow DOM** — An encapsulated DOM subtree per element: styles and markup inside don't leak out or get styled accidentally from outside — true style scoping built into the platform.
- **Slots and composition** — `<slot>` elements let users project their own markup into your component's shadow tree (named slots for header/footer patterns), the native equivalent of framework children.
- **Attributes vs properties** — Attributes are strings in HTML (`<my-el count="3">`); properties are JS values (`el.count = 3`); a good library reflects important properties to attributes and parses types.
- **Templates** — `<template>` holds inert, cloneable markup so each instance stamps out its shadow DOM cheaply without re-parsing HTML strings.
- **CSS custom properties as API** — Since shadow styles are sealed, theming flows through CSS variables (`--my-btn-bg`) and `::part()` selectors that pierce the shadow boundary deliberately.
- **Form-associated custom elements** — `ElementInternals` + `static formAssociated = true` lets custom elements participate in `<form>` submission and native validation like real inputs.

## How it works

1. You define element classes with shadow DOM templates, observed attributes, and public properties/methods.
2. Users drop `<my-card>` tags in plain HTML; the browser upgrades them when your script registers the definitions.
3. Attribute changes flow through `attributeChangedCallback` into re-renders; internal state changes reflect back to attributes when they matter for styling or semantics.
4. Components communicate outward via `CustomEvent`s (with `bubbles: true, composed: true` to cross shadow boundaries) and accept content through slots.

## Build milestones

1. Three components (`<my-button>`, `<my-card>`, `<my-badge>`) with shadow DOM, attributes, and slots — a working library in an evening.
2. Add a base class handling attribute↔property reflection, typed parsing, and efficient re-rendering.
3. Add theming via CSS custom properties and `::part()`, plus a dark-mode toggle demo.
4. Build form-associated inputs (`<my-input>`, `<my-checkbox>`) that work inside native `<form>` with validation.
5. Add SSR-friendly patterns (declarative shadow DOM) and a docs page with live examples.

## Best resources

- [Web Components — MDN](https://developer.mozilla.org/en-US/docs/Web/API/Web_components) — the complete guide: custom elements, shadow DOM, templates.
- [Custom Elements spec — WHATWG](https://html.spec.whatwg.org/multipage/custom-elements.html) — the normative lifecycle and upgrade semantics.
- [Shadow DOM spec — WHATWG DOM](https://dom.spec.whatwg.org/#shadow-trees) — slots, composition, and event retargeting, precisely defined.
- [Lit docs](https://lit.dev/) — the minimal layer on top of web components (reactive properties, templating); the natural next step after hand-rolling.
- [Open WC](https://open-wc.org/) — recommendations and tooling for building and testing web component libraries.

## Stretch ideas

- Build a data-grid component with virtualized scrolling for 100k rows.
- Implement a router and state store as framework-agnostic custom elements.
