---
title: "Particle System"
category: "games-graphics"
difficulty: "beginner"
tags: ["particles", "effects", "2d-graphics"]
related: [2d-game-engine, glsl-shaders-playground, audio-synthesizer]
---

# Particle System
A particle system creates effects like fire, smoke, sparks, and rain from hundreds of tiny sprites following simple rules. Each particle is dumb — position, velocity, lifetime — but together they look alive. It is the highest visual-payoff-per-line-of-code system in game development.

## Core concepts

- **Particles**: Lightweight structs holding position, velocity, color, size, and remaining lifetime. Thousands can be updated per frame cheaply.
- **Emitters**: Objects that spawn particles with randomized initial conditions — a fountain emitter shoots upward, an explosion emitter bursts outward in all directions.
- **Lifetime and decay**: Particles fade, shrink, or change color as they age, then die and get recycled so no allocation happens during gameplay.
- **Forces**: Gravity, wind, drag, and turbulence modify velocity each frame, turning uniform bursts into believable smoke or drifting snow.
- **Object pooling**: A fixed-size pool of particle slots is reused forever, avoiding garbage collection spikes that would stutter the game.
- **Blending modes**: Additive blending makes fire and magic glow; normal alpha blending suits smoke and dust. The blend mode changes the mood completely.
- **Burst vs continuous emission**: Explosions spawn everything at once; campfires trickle particles out at a steady rate.

## How it works

An emitter holds a pool of particles and a spawn rate. Each frame it activates dead slots with randomized position, velocity, and lifetime around its origin. Every live particle integrates its motion under configured forces, ages, and interpolates color/size over its lifetime curve. Dead particles return to the pool. The renderer draws all live particles as textured quads in one batched draw call, sorted or unsorted depending on the blend mode.

## Build milestones

1. Spawn 100 white dots that drift upward and fade out, recycled from a fixed pool.
2. Add an emitter with configurable spawn rate, spread angle, speed range, and lifetime.
3. Implement color/size-over-lifetime gradients and gravity plus drag forces.
4. Support textured particles, additive vs alpha blending, and one-shot bursts.
5. Build preset effects: campfire, explosion, rain, magic sparkle — each a parameter set.
6. Add a visual editor to tweak parameters live and export effect definitions as data files.

## Best resources

- [Lazy Foo's Particle Engines](https://www.lazyfoo.net/tutorials/SDL/38_particle_engines/index.php) — a from-scratch particle trail effect in SDL/C++.
- [Particle Systems from Scratch](https://hive.blog/hive-196387/@femdev/learn-creative-coding-11-particle-systems-from-scratch) — building emitters with pooling and behavior-by-initial-conditions in JS.
- [OpenGL ES Particle System Tutorial](https://www.kodeco.com/2704-opengl-es-particle-system-tutorial-part-1-3/page/2?page=2) — GPU-oriented particle system implementation walkthrough.
- [b3dframework Particle System docs](https://github.com/gamefoundry/b3dframework/blob/HEAD/Documentation/Manuals/docs/00_User_Manuals/11_Particles/00_particleSystem.md) — how an engine structures emitters, materials, and settings.

## Stretch ideas

- Move simulation to the GPU with transform feedback or compute shaders for 100k+ particles.
- Add particle collision against level geometry so sparks bounce off floors.
