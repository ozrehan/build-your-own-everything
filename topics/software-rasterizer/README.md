---
title: "Software Rasterizer"
category: "games-graphics"
difficulty: "advanced"
tags: ["rasterization", "rendering", "graphics"]
related: [ray-tracer, 2d-game-engine, glsl-shaders-playground]
---

# Software Rasterizer
A software rasterizer draws 3D graphics entirely on the CPU, pixel by pixel, with no GPU help. Every game console before the 3D-accelerator era did exactly this. Building one teaches you the graphics pipeline from the inside: how triangles become pixels and how depth, texture, and light combine.

## Core concepts

- **The graphics pipeline**: Model space → world space → view space → clip space → screen space, each a matrix transform. The rasterizer implements every stage by hand.
- **Triangle rasterization**: Triangles are scan-converted into fragments by testing which pixels fall inside their edges; barycentric coordinates interpolate depth, UVs, and colors across the surface.
- **Depth buffering**: A z-buffer stores the closest depth per pixel so nearer triangles correctly occlude farther ones.
- **Perspective-correct interpolation**: Attributes must be interpolated with 1/w weighting, or textures will visibly warp on angled surfaces.
- **Texture mapping**: UV coordinates sample a texture image per fragment, with filtering (nearest, bilinear) to avoid blockiness.
- **Backface culling**: Triangles facing away from the camera are discarded before rasterization, roughly halving the work.
- **Shading**: Per-fragment lighting (Gouraud or Phong-style) is computed on the CPU from normals, lights, and material parameters.

## How it works

Load a mesh, transform its vertices through the model-view-projection matrices, and clip to the screen. For each triangle, compute its screen-space bounding box and test every pixel inside against the three edge functions. Pixels that pass get their depth compared against the z-buffer; survivors sample textures and lighting to produce a final color. Repeat for every triangle, then present the framebuffer.

## Build milestones

1. Draw a single wireframe triangle by projecting 3D vertices to 2D screen coordinates.
2. Fill triangles with solid colors using edge-function rasterization and a z-buffer.
3. Add perspective-correct texture mapping with bilinear filtering.
4. Implement backface culling, per-vertex lighting, and loading a real model file.
5. Add a programmable-ish fragment stage: multiple lights, specular highlights, and fog.
6. Optimize with scanline spans or SIMD and render a spinning textured scene at interactive frame rates.

## Best resources

- [renderer by zauonlok](https://github.com/zauonlok/renderer) — a software renderer built from scratch, excellent reference architecture.
- [zauonlok's renderer writeup](https://zauonlok.github.io/renderer/) — accompanying explanations of the rasterization pipeline.
- [tinygfx-rs](https://github.com/gabrielmajeri/tinygfx-rs) — tiny graphics projects in Rust covering software rendering techniques.
- [Tiny Renderer learning notes](https://github.com/ventixz/daily-projects/blob/HEAD/2026-08-25-cpp-tiny-renderer/LEARNING.md) — notes from writing a tiny C++ renderer.

## Stretch ideas

- Add shadow mapping or screen-space ambient occlusion on the CPU.
- Port the rasterizer to a shader-based GPU version and benchmark the difference.
