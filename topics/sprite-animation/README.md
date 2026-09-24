---
title: "Sprite Animation System"
category: "games-graphics"
difficulty: "beginner"
tags: ["sprites", "animation", "2d-graphics"]
related: [2d-game-engine, tilemap-editor, particle-system]
---

# Sprite Animation System
Sprite animation is how 2D characters walk, jump, and attack: a series of frames drawn fast enough to look like motion. A sprite animation system manages which frames play, how fast, and when to switch between clips like idle, run, and hurt. It is the first animation system most game developers ever build.

## Core concepts

- **Spritesheets**: Animation frames are packed into one image grid so the GPU loads a single texture; each frame is a rectangle (source rect) within it.
- **Frame timing**: An accumulator advances time each frame, and the current frame index is time divided by seconds-per-frame. Time-based (not frame-based) timing keeps speed consistent across hardware.
- **Animation clips**: Named sequences (idle, walk, jump) each with their own frame list, frame rate, and loop behavior.
- **State machines**: Gameplay state picks the clip — moving plays walk, airborne plays jump, and transitions can blend or snap between clips.
- **Flipping and pivots**: Sprites flip horizontally for left/right movement; a pivot (origin) point anchors rotation and positioning so feet stay planted.
- **Onion skinning and keyframes**: When authoring, artists draw key poses and in-between frames; the system just plays back the result, so clean frame data matters.
- **Atlas packing**: Tools pack many clips into one atlas to cut texture swaps and memory use at runtime.

## How it works

Each animated entity holds a reference to the current clip and a time accumulator. Every update, elapsed time is added; dividing by the clip's frame duration yields the frame index, which wraps if the clip loops or clamps and fires a "finished" event if it doesn't. The renderer draws the sprite using the source rectangle of that frame, applying flip and pivot. When gameplay logic changes state — landing, attacking, dying — it requests a different clip and the accumulator resets.

## Build milestones

1. Load a spritesheet and draw a single frame by slicing a source rectangle out of it.
2. Play a looping clip by advancing frames on a timer.
3. Support multiple named clips with per-clip frame rates and one-shot vs looping playback.
4. Add flip, pivot points, and tint so sprites face the right way and anchor correctly.
5. Build a small state machine that switches clips based on velocity and input (idle/run/jump).
6. Add animation events (footstep sounds, attack hit frames) and a preview tool to scrub clips.

## Best resources

- [Animated Sprite 2D in Godot](https://Dev.to/eduardojuliao/animated-sprite-2d-147a) — walkthrough of importing a spritesheet and playing frames with AnimatedSprite2D.
- [Different Ways of Doing Sprite Sheet Animation in Unity](https://gamedev.net/blogs/entry/2265264-different-ways-of-doing-sprite-sheet-animation-in-unity) — animator-controller vs scripting approaches.
- [Multiple ways of doing sprite sheet animation in Unity3D](https://www.gamedeveloper.com/business/multiple-ways-of-doing-sprite-sheet-animation-in-unity3d) — another take on spritesheet animation techniques.
- [Sprite Animation in JavaScript](https://www.youtube.com/watch?v=CY0HE277IBM) — vanilla JS/canvas sprite animation explaining frame navigation in a sheet.

## Stretch ideas

- Add skeletal-style animation by rotating sprite parts around pivots instead of swapping frames.
- Build a tiny in-browser spritesheet packer and clip editor.
