---
title: "WebGL 2D Renderer"
category: "web-development"
difficulty: "advanced"
tags: [webgl, rendering, gpu]
related: [css-layout-engine, 2d-game-engine, particle-system, glsl-shaders-playground]
---

# WebGL 2D Renderer

WebGL gives JavaScript direct access to the GPU: you upload geometry, write shaders, and draw thousands of sprites in a single frame. Building a 2D renderer (sprite batching, textures, transforms) teaches the GPU pipeline — buffers, shaders, draw calls — and why batching is the difference between 60fps and a slideshow.

## Core concepts

- **The pipeline: vertex → rasterizer → fragment** — Your vertex shader positions triangles; the GPU rasterizes them into pixels; your fragment shader colors each pixel — everything in WebGL is this pipeline.
- **Shaders (GLSL)** — Small C-like programs compiled on the GPU: vertex shaders transform coordinates, fragment shaders compute colors; shader compile errors are the classic beginner wall.
- **Buffers and attributes** — Vertex data (positions, UVs, colors) lives in GPU buffers; attributes describe how the vertex shader reads each vertex's slice of that data.
- **Textures and samplers** — Images uploaded to GPU memory, sampled in the fragment shader by UV coordinates; texture atlases pack many sprites into one texture to avoid rebinding.
- **Sprite batching** — The core performance technique: accumulate hundreds of quads into one big buffer and draw them with a single `drawArrays`/`drawElements` call instead of one call per sprite.
- **Orthographic projection** — A matrix mapping pixel coordinates to clip space (-1..1), so you can think in screen pixels while the GPU thinks in clip space.
- **Blend modes** — How overlapping fragments combine (`SRC_ALPHA, ONE_MINUS_SRC_ALPHA` for normal transparency); essential for particles and layered sprites.
- **State changes are expensive** — Every texture bind, shader switch, or blend change costs; renderers sort draw calls by state to minimize switches.

## How it works

1. On init: compile vertex/fragment shaders, link a program, create buffers, and upload a texture atlas.
2. Each frame: the scene submits sprites (position, rotation, UV rect, tint) into a batch keyed by texture.
3. When the batch fills or the texture changes, the renderer uploads the vertex data and issues one draw call per batch.
4. The vertex shader applies the projection matrix; the fragment shader samples the texture and applies tint/alpha.

## Build milestones

1. Clear the canvas and draw a single colored triangle with hand-written shaders — the "hello triangle" in an evening.
2. Add textures: upload an image, draw a textured quad with UVs, and build an orthographic camera so you work in pixels.
3. Implement sprite batching: a dynamic buffer that packs many quads and flushes in one draw call; benchmark 10k sprites.
4. Add a texture atlas with sprite regions, rotation/scale transforms, tint colors, and blend modes.
5. Add text rendering (bitmap font atlas or SDF) and a simple particle system on top of the batcher.

## Best resources

- [WebGL Fundamentals](https://webglfundamentals.org/webgl/lessons/webgl-fundamentals.html) — the legendary tutorial series; start here and work through the 2D lessons.
- [WebGL — How It Works](https://webglfundamentals.org/webgl/lessons/webgl-how-it-works.html) — the single best explainer of the GPU pipeline mental model.
- [WebGL API — MDN](https://developer.mozilla.org/en-US/docs/Web/API/WebGL_API) — the complete API reference with tutorials.
- [WebGL2 Specification — Khronos](https://www.khronos.org/registry/webgl/specs/latest/2.0/) — the normative spec when you need exact behavior.
- [The Book of Shaders](https://thebookofshaders.com/) — a beautiful interactive introduction to fragment shaders and GLSL thinking.

## Stretch ideas

- Implement render-to-texture post-processing (bloom, blur) with framebuffers.
- Port the renderer to WebGL2 with instanced rendering for 100k+ sprites.
