---
title: "UI Toolkit"
category: "games-graphics"
difficulty: "intermediate"
tags: ["ui", "widgets", "tools"]
related: [tilemap-editor, dialogue-system, tween-animation-system]
---

# UI Toolkit
A UI toolkit is the widget set behind every menu, HUD, and settings screen: buttons, sliders, text fields, and panels that handle input and draw themselves. Games need UI that works with mouse, keyboard, and gamepad at any resolution. Building one teaches you layout, event routing, and the retained vs immediate mode divide.

## Core concepts

- **Widgets**: Self-contained controls (button, slider, checkbox, label) that own their state, handle input, and render themselves.
- **Layout**: Containers arrange children with anchors, padding, and flex-like rules so UI adapts to any screen size and aspect ratio.
- **Event routing**: Clicks and key presses travel down the widget tree (hit testing) and back up as handled events; focus determines which widget gets keyboard input.
- **Immediate vs retained mode**: Immediate mode (Dear ImGui) rebuilds the UI from code each frame with no persistent objects; retained mode keeps a widget tree alive between frames.
- **Theming**: Colors, fonts, spacing, and corner radii defined in one place so the whole UI can be reskinned without touching widget code.
- **Draw batching**: Widgets emit rectangles and text into vertex buffers rendered in a few draw calls, keeping UI cheap even with hundreds of controls.
- **Navigation**: Gamepad/keyboard focus movement between widgets (up/down/left/right) is essential for console-style menus.

## How it works

Each frame, input events are fed into the toolkit, which hit-tests the widget tree to find the hovered and focused controls. Widgets update their state (a button tracks hover → pressed → clicked) and then emit draw commands — textured quads for backgrounds, glyph quads for text — into batched buffers. Layout runs before drawing so every widget knows its rectangle. The game reads widget events (button clicked, slider changed) to drive menus and settings, and the whole UI redraws fresh each frame.

## Build milestones

1. Draw a clickable button that changes color on hover and fires a callback on click.
2. Add labels, toggles, and sliders with mouse drag interaction.
3. Implement a layout container (vertical/horizontal box) with padding and automatic sizing.
4. Add keyboard/gamepad focus navigation and a text input field with caret.
5. Build a theming system and a settings screen (volume, resolution, key bindings) using only your widgets.
6. Implement either an immediate-mode API or a retained widget tree with event bubbling — then compare with the other approach.

## Best resources

- [Dear ImGui docs](https://github.com/ocornut/imgui/blob/HEAD/docs/README.md) — the definitive guide to the immediate-mode GUI paradigm.
- [Nuklear](https://github.com/immediate-mode-ui/nuklear/blob/HEAD/README.md) — a single-header ANSI C immediate-mode GUI toolkit, great for studying minimal design.
- [Game UI/UX skill](https://github.com/gamedev-skills/awesome-gamedev-agent-skills/blob/HEAD/skills/disciplines/game-ui-ux/SKILL.md) — engine-neutral UI architecture: layout, scaling, focus navigation, screen flow.
- [ImPlot](https://github.com/ocornut/implot) — immediate-mode plotting for Dear ImGui, showing how the paradigm extends to complex widgets.

## Stretch ideas

- Add a UI layout editor where designers drag widgets and export the hierarchy.
- Implement resolution-independent scaling with safe-area support for phones and TVs.
