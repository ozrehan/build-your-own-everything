---
title: "Tween Animation System"
category: "games-graphics"
difficulty: "beginner"
tags: ["tweening", "animation", "easing"]
related: [ui-toolkit, sprite-animation, particle-system]
---

# Tween Animation System
Tweening (in-betweening) animates a value from A to B over time — a menu sliding in, a button popping, a character hopping. Instead of hand-keyframing every frame, you declare start, end, duration, and an easing curve, and the system fills in the rest. It is the secret behind "juicy" game feel.

## Core concepts

- **Tweens**: Objects that interpolate one or more properties (position, scale, alpha, color) from a start value to an end value over a duration.
- **Easing functions**: Curves like ease-out-quad or ease-in-out-back remap linear time into natural motion — fast starts, soft landings, overshoot and bounce.
- **Delta-time updates**: Each frame the tween advances by elapsed time, so animation speed is consistent regardless of frame rate.
- **Chaining and sequences**: Tweens link end-to-start to build multi-step animations; sequences group them with parallel and serial execution.
- **Callbacks**: onStart, onUpdate, and onComplete hooks trigger sounds, spawn effects, or start the next animation when a tween finishes.
- **Loops and yoyo**: Tweens can repeat, ping-pong back and forth (yoyo), or run a fixed number of times for pulsing and idle motion.
- **Tween management**: A central updater ticks all active tweens; killing or pausing by ID or tag prevents stale animations from fighting new ones.

## How it works

You create a tween targeting an object's property with an end value, duration, and easing function. The tween manager stores it and each frame advances its internal clock, computing eased progress = ease(elapsed / duration) and setting the property to lerp(start, end, eased). When the clock passes the duration, the value snaps to the end, the completion callback fires, and the tween is recycled. Chained tweens start automatically, building complex motion from simple declarations.

## Build milestones

1. Tween a single value (like an object's x position) linearly over one second.
2. Add the classic easing set: quad/cubic/sine in, out, and in-out variants.
3. Support tweening colors, scales, and rotations, plus onComplete callbacks.
4. Implement sequences, delays, loops, and yoyo ping-ponging.
5. Add a tween manager with kill-by-tag and safe handling of destroyed targets.
6. Build a demo scene showcasing juice: button presses, menu transitions, and screen shake built from tweens.

## Best resources

- [eases — mattdesl](https://github.com/mattdesl/eases) — a grab-bag of modular Robert Penner easing equations.
- [Robert Penner's easing library](https://github.com/robertpenner/easing/blob/HEAD/README.md) — the canonical easing functions with modern extensions.
- [Tween Animations lesson — LunaEngine](https://github.com/mrjuaumbr/lunaengine/blob/HEAD/lessons/intermediate/10-tween-animations.md) — a practical tween system tutorial with chaining and callbacks.
- [PyTweening tutorial — inventwithpython](https://inventwithpython.com/blog/make-lively-movement-animation-with-pytweenings-tweening-functions.html) — lively movement via tweening functions, great for game feel.
- [Tweening docs — polyphase-engine](https://github.com/polyphase-labs/polyphase-engine/blob/HEAD/Documentation/Development/Tweening.md) — how a game engine documents its tween and easing API.

## Stretch ideas

- Add custom bezier-curve easing and spring-physics-based tweens.
- Build a visual tween curve editor that exports easing presets.
