---
title: "Ray Tracer"
category: "games-graphics"
difficulty: "intermediate"
tags: ["ray-tracing", "rendering", "graphics"]
related: [software-rasterizer, glsl-shaders-playground, voxel-engine-basics]
---

# Ray Tracer
A ray tracer renders images by simulating light: for every pixel, it shoots a ray into the scene and sees what it hits. It is the simplest way to produce photorealistic images — reflections, shadows, and refraction fall out naturally. Writing one is the classic first deep dive into computer graphics.

## Core concepts

- **Ray casting**: Each pixel maps to a ray from the camera through the scene. The closest intersection determines the pixel's color.
- **Ray-sphere and ray-triangle intersection**: Closed-form math tests whether and where a ray hits geometry; triangles are the workhorse primitive of real scenes.
- **Shading**: The material at the hit point is shaded using the light direction, surface normal, and viewer position — diffuse, specular, and ambient terms.
- **Shadows**: A shadow ray from the hit point toward each light reveals occluders; if blocked, the point is in shadow.
- **Reflection and refraction**: Recursive rays bounce off reflective surfaces or bend through transparent ones following the law of reflection and Snell's law.
- **Acceleration structures**: Bounding volume hierarchies (BVHs) group geometry so rays skip most of the scene, turning hours of rendering into minutes.
- **Path tracing**: Instead of one recursive ray, many random rays are sampled per pixel and averaged, producing soft shadows and global illumination at the cost of noise.

## How it works

For each pixel, compute a ray from the camera through the pixel's position on the image plane. Test it against every object (or traverse a BVH) to find the nearest hit. Shade that point: add direct lighting, cast shadow rays, and spawn reflected or refracted rays up to a recursion depth. The returned color becomes the pixel. Loop over all pixels — and for path tracing, repeat with jittered rays and average.

## Build milestones

1. Render a single shaded sphere on a background gradient by casting one ray per pixel.
2. Add multiple spheres, planes, and a point light with diffuse shading.
3. Implement shadow rays and mirror reflections via recursion.
4. Support triangle meshes loaded from a simple model file, plus refraction for glass.
5. Add a BVH so scenes with thousands of triangles still render quickly.
6. Extend to a Monte Carlo path tracer with soft shadows, depth of field, and multi-threading.

## Best resources

- [Tiny Ray Tracer walkthrough](https://github.com/benatfroemming/explicode/blob/HEAD/examples/tinyraytracer.cpp.md) — an annotated explanation of a minimal ray tracer in a few hundred lines.
- [tinygfx-rs](https://github.com/gabrielmajeri/tinygfx-rs) — tiny graphics projects in Rust, including ray tracing fundamentals.
- [Graphics Developer Roadmap](https://github.com/landonwengang/graphics-developer-roadmap) — the bigger picture of rendering techniques around ray tracing.
- [Tiny Renderer learning notes](https://github.com/ventixz/daily-projects/blob/HEAD/2026-08-25-cpp-tiny-renderer/LEARNING.md) — notes from building a tiny renderer from scratch.
- [zauonlok's renderer site](https://zauonlok.github.io/renderer/) — writeup of a from-scratch renderer, useful for comparing ray tracing with rasterization.

## Stretch ideas

- Render a scene description format of your own design with materials and instancing.
- Add denoising or adaptive sampling to clean up path-traced noise faster.
