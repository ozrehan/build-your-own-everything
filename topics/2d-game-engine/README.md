---
title: "2D Game Engine"
category: "games-graphics"
difficulty: "intermediate"
tags: ["game-engine", "2d-graphics", "architecture"]
related: [sprite-animation, particle-system, physics-engine, tilemap-editor]
---

# 2D Game Engine
A 2D game engine is the reusable core that sits under a game: a main loop, rendering, input, audio, and scene management. Building your own teaches you how engines organize thousands of moving parts into something predictable and fast. Start tiny and grow it feature by feature.

## Core concepts

- **Game loop**: The heartbeat of the engine — process input, update the simulation, render the frame, repeat. A fixed timestep keeps physics deterministic while rendering runs as fast as it can.
- **Entity management**: Game objects (players, enemies, projectiles) need creation, update, and destruction. Many engines use an Entity-Component-System (ECS) design where entities are IDs and behavior lives in data components processed by systems.
- **Rendering pipeline**: Sprites and shapes are batched into draw calls and pushed to the GPU each frame. Sorting by texture and depth minimizes expensive state changes.
- **Input handling**: Raw keyboard, mouse, and controller events are translated into game actions. Good engines abstract this so gameplay code asks "is jump pressed?" instead of reading hardware directly.
- **Scene management**: Levels, menus, and cutscenes are scenes with their own object sets and logic. A scene stack or switcher controls which one is live.
- **Delta time**: The elapsed time between frames scales movement so the game runs at the same speed on any hardware.
- **Resource management**: Textures, sounds, and fonts are loaded once, cached, and shared instead of being reloaded per use.

## How it works

The engine boots, loads assets, and enters the main loop. Each iteration polls input events, advances the simulation by a fixed or variable timestep, then renders every visible object to the screen. When the frame is done, the loop repeats — typically 60 times per second. Subsystems like physics, animation, and audio hook into this loop, each reading and writing shared game state in a defined order so nothing races.

## Build milestones

1. Open a window and clear it to a color, running a basic main loop that exits cleanly.
2. Draw a sprite that moves with keyboard input using delta-time-based movement.
3. Add an entity list with spawn/destroy so you can manage many objects at once.
4. Implement scenes and switching — for example, a title screen that leads into gameplay.
5. Add audio playback, a camera that follows the player, and sprite batching for performance.
6. Polish into a tiny playable game (like Breakout) built entirely on your engine, with hot-reloadable assets.

## Best resources

- [ECS FAQ](https://github.com/SanderMertens/ecs-faq) — answers to common questions about entity-component-system design used by modern engines.
- [Lazy Foo's Particle Engines tutorial](https://www.lazyfoo.net/tutorials/SDL/38_particle_engines/index.php) — part of a complete from-scratch 2D engine tutorial series in C++ and SDL.
- [Graphics Developer Roadmap](https://github.com/landonwengang/graphics-developer-roadmap) — what sits under a 2D renderer, from the pipeline to shaders.
- [renderer by zauonlok](https://github.com/zauonlok/renderer) — a tiny from-scratch renderer project, a good study of how a real-time loop is organized.

## Stretch ideas

- Add a scripting layer so game logic can be written without recompiling the engine.
- Implement an in-engine debug console with frame stats and entity inspection.
