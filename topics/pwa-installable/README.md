---
title: "Installable PWA"
category: "web-development"
difficulty: "beginner"
tags: [pwa, installable, manifest]
related: [service-worker-offline, spa-router, web-components-library, jwt-auth]
---

# Installable PWA

A Progressive Web App is a website that can be installed to a home screen like a native app — with an icon, splash screen, and standalone window — while remaining just a website. Building one teaches the web app manifest, installability criteria, and how far web capabilities (push, shortcuts, share targets) now reach.

## Core concepts

- **Web app manifest** — A JSON file (`name`, `icons`, `start_url`, `display`, `theme_color`) that tells the OS how to present your installed app: its icon, title, and window chrome.
- **Installability criteria** — Browsers require a manifest with icons (including a 512px maskable icon), a registered service worker, and HTTPS before offering the install prompt.
- **`beforeinstallprompt`** — The event that lets you defer the browser's install prompt and show your own custom "Install app" button at the right moment.
- **Display modes** — `standalone`, `fullscreen`, and `minimal-ui` control how much browser chrome the installed app shows; `standalone` is the classic app-like look.
- **Maskable icons** — Icons designed with safe-zone padding so Android's adaptive icon masks (circles, squircles) never clip important pixels.
- **App shortcuts** — Manifest `shortcuts` give long-press quick actions (e.g. "New note", "Open inbox") like native app shortcuts.
- **Share target** — Declaring `share_target` lets your PWA appear in the OS share sheet and receive shared files/text from other apps.
- **Push notifications** — Via the Push API + service worker, installed PWAs can receive server-sent notifications even when closed — with explicit user permission.

## How it works

1. You add a manifest linked from your HTML and a service worker with a fetch handler (the offline requirement).
2. On a repeat visit over HTTPS, the browser fires `beforeinstallprompt`; you stash the event and trigger it from your own install UI.
3. The user accepts, the OS installs the icon, and launches open your `start_url` in standalone mode with your theme color as the splash background.
4. Shortcuts, share targets, and push extend the installed app toward native parity.

## Build milestones

1. Add a manifest with icons (generate all sizes + a maskable 512px) and `display: standalone` to any site, and install it from Chrome DevTools — the basics in an evening.
2. Capture `beforeinstallprompt` and build a custom install button with proper UX (only show when eligible).
3. Add app shortcuts and a share target that receives shared text into your app.
4. Add push notifications: generate VAPID keys, subscribe via PushManager, and send a notification from your server.
5. Polish: theme-color meta, splash behavior, iOS-specific tags (`apple-touch-icon`, `apple-mobile-web-app-capable`), and an installability audit in Lighthouse.

## Best resources

- [Progressive Web Apps — MDN](https://developer.mozilla.org/en-US/docs/Web/Progressive_web_apps) — the full MDN guide: manifests, service workers, installability.
- [Web App Manifest spec — W3C](https://www.w3.org/TR/appmanifest/) — the normative definition of every manifest field.
- [web.dev — Learn PWA](https://web.dev/learn/pwa) — Google's course covering installability, capabilities, and patterns.
- [PWABuilder](https://www.pwabuilder.com/) — Microsoft's tool that audits your PWA and packages it for app stores; great for validating your build.

## Stretch ideas

- Package your PWA for the Play Store with a Trusted Web Activity via PWABuilder.
- Implement file handling so your PWA opens associated file types from the OS.
