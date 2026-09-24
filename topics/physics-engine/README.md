---
title: "Physics Engine"
category: "games-graphics"
difficulty: "intermediate"
tags: ["physics", "collision", "simulation"]
related: [2d-game-engine, particle-system, voxel-engine-basics]
---

# Physics Engine
A physics engine simulates how bodies move and collide: gravity pulls, objects bounce, and stacks settle. Games fake it convincingly with rigid-body dynamics solved in small time steps. Building one teaches you the vector math and iterative solvers behind every platformer and puzzle game.

## Core concepts

- **Rigid bodies**: Objects have position, velocity, mass, and rotation. Forces change velocity; velocity changes position — integrated once per step.
- **Integration**: Numerical integrators like semi-implicit Euler advance the simulation. Smaller, fixed timesteps keep fast objects from tunneling through walls.
- **Collision detection**: A broad phase (spatial partitioning, bounding boxes) finds candidate pairs cheaply; a narrow phase computes exact contact points, normals, and penetration depth.
- **GJK algorithm**: The Gilbert–Johnson–Keerthi algorithm tests whether two convex shapes overlap using only their support functions, without explicit mesh math.
- **Contact resolution**: Contacts are solved as constraints with sequential impulses — push colliding bodies apart along the contact normal and apply friction tangentially.
- **Restitution and friction**: Restitution controls bounciness, friction controls sliding. Both are applied as impulses at contact points.
- **Sleeping**: Bodies that stop moving are put to sleep so the solver skips them, saving a large amount of CPU in quiet scenes.

## How it works

Each fixed timestep, the engine applies forces (like gravity) to every dynamic body, integrates their positions, then detects collisions. For each contact, it computes a normal and penetration depth, then runs several solver iterations that apply corrective impulses so bodies separate and stack stably. Rendering then draws the bodies at their new transforms. Repeating this 60+ times per second produces believable motion.

## Build milestones

1. Simulate a single bouncing ball with gravity and ground collision using semi-implicit Euler.
2. Add circle-vs-circle collision with positional correction and restitution.
3. Implement AABB and polygon bodies with the GJK algorithm for narrow-phase detection.
4. Add sequential-impulse contact solving so boxes stack without jitter.
5. Introduce friction, angular velocity, and a broad phase (uniform grid or sweep-and-prune).
6. Build a small demo scene — a collapsing tower or a marble run — with sleeping bodies and debug-drawn contacts.

## Best resources

- [Game Physics: Introduction](http://allenchou.net/2013/12/game-physics-introduction/) — Allen Chou's gentle introduction to the concepts behind game physics.
- [ImpulseEngine](https://github.com/dreucifer/impulseengine) — a small educational 2D rigid-body engine implementing sequential impulses.
- [Game Physics: Collision Detection with GJK](https://allenchou.net/2013/12/game-physics-collision-detection-gjk/) — clear explanation of the GJK narrow-phase algorithm.
- [Game Physics: Constraints and Sequential Impulses](https://allenchou.net/2013/12/game-physics-constraints-sequential-impulse/) — how contacts are resolved as constraints.

## Stretch ideas

- Add soft bodies or rope/bridge constraints using verlet integration.
- Implement continuous collision detection to stop very fast projectiles tunneling.
