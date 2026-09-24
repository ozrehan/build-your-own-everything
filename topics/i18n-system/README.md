---
title: "i18n System"
category: "web-development"
difficulty: "intermediate"
tags: [i18n, localization, intl]
related: [form-validation-library, headless-cms, markdown-renderer, spa-router]
---

# i18n System

An internationalization system separates every user-facing string from code, then renders the right language, plural form, date, and number format per user. Building one teaches ICU MessageFormat, plural rules (Arabic has six!), locale negotiation, and the build tooling that extracts strings for translators.

## Core concepts

- **Message catalogs** — Keyed dictionaries (`"cart.items": "You have {count} items"`) per locale, usually JSON; keys stay stable while translators work on values independently of code releases.
- **ICU MessageFormat** — The standard message syntax supporting placeholders, plurals (`{count, plural, one {...} other {...}}`), selects (gender), and nesting — far beyond naive string interpolation.
- **Plural rules (CLDR)** — Different languages have different plural categories: English has two (one/other), Russian three, Arabic six; the `Intl.PluralRules` API encodes the CLDR data.
- **`Intl` APIs** — The built-in `Intl.NumberFormat`, `Intl.DateTimeFormat`, `Intl.RelativeTimeFormat`, and `Intl.ListFormat` handle locale-correct formatting without any library.
- **Locale negotiation** — Picking the best locale from the user's `Accept-Language` header or preferences, with fallback chains (`fr-CA` → `fr` → `en`) when a translation is missing.
- **String extraction** — Build tooling (Babel plugins, CLI scanners) that pulls message keys and default text out of source code into files translators can edit.
- **RTL support** — Right-to-left languages (Arabic, Hebrew) need `dir="rtl"`, mirrored layouts (CSS logical properties like `margin-inline-start`), and flipped icons.
- **Pseudo-localization** — Testing with fake translations (`[!! Şťŕíńĝ !!]` plus 40% longer text) that exposes hardcoded strings and layout breakage before real translations arrive.

## How it works

1. Developers write `t("cart.items", { count })` with ICU messages; extraction tooling collects keys into per-locale catalog files.
2. At runtime (or build time), the system negotiates the user's locale, loads the matching catalog, and falls back through the chain for missing keys.
3. Messages are formatted with `Intl` formatters: plurals via CLDR rules, dates/numbers/currencies per locale conventions.
4. The UI sets `lang`/`dir` attributes and uses logical CSS properties so RTL layouts mirror correctly.

## Build milestones

1. A `t(key, vars)` function with `{placeholder}` interpolation, JSON catalogs per locale, and fallback chains — working in an evening.
2. Add ICU-style plural and select support backed by `Intl.PluralRules` for real CLDR categories.
3. Add `Intl`-based date/number/currency/relative-time formatters and an `Accept-Language` negotiator for the server.
4. Build an extraction CLI that scans source files for `t()` calls and generates/updates catalog JSON for translators.
5. Add pseudo-localization testing, RTL layout support with logical properties, and lazy-loading of locale chunks.

## Best resources

- [Intl — MDN](https://developer.mozilla.org/en-US/docs/Web/JavaScript/Reference/Global_Objects/Intl) — the reference for every built-in internationalization API.
- [ECMA-402 spec](https://tc39.es/ecma402/) — the actual standard behind `Intl`; the locale negotiation algorithm is specified here.
- [ICU Message Format guide](https://unicode-org.github.io/icu/userguide/format_parse/messages/) — the definitive guide to plural/select message syntax.
- [FormatJS docs](https://formatjs.io/) — the production i18n toolchain (extraction, ICU, React bindings) to study and compare against.
- [W3C — Declaring language in HTML](https://www.w3.org/International/questions/qa-html-language-declarations) — `lang`/`dir` attributes and why they matter for accessibility and SEO.

## Stretch ideas

- Build a translator-facing web UI with side-by-side editing and missing-key detection.
- Implement locale-aware routing (`/fr/produits`) with SEO-friendly hreflang tags.
