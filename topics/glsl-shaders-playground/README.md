---
title: "GLSL Shaders Playground"
category: "games-graphics"
difficulty: "beginner"
tags: ["shaders", "glsl", "graphics"]
related: [ray-tracer, particle-system, software-rasterizer]
---

# GLSL Shaders Playground
A GLSL shaders playground is a live editor where you write fragment shaders and instantly see pixels respond. Shaders are tiny programs that run on the GPU — one copy per pixel, all in parallel — and they power water, fire, and stylized looks in modern games. A playground is the fastest way to build shader intuition.

## Core concepts

- **Fragment shaders**: A program that computes the color of one pixel (fragment). It runs millions of times per frame, so it must be fast and stateless.
- **Uniforms**: Values like time, mouse position, and resolution passed from the CPU into the shader, letting animations react to input.
- **Vector math**: Colors and positions are vec2/vec3/vec4; dot products, mixing, and smoothstep are the vocabulary of shader art.
- **Signed distance functions (SDFs)**: Shapes defined by distance-to-edge math, combined with min/max operations to build scenes without any geometry.
- **Noise**: Value noise, gradient noise, and fractal Brownian motion (fbm) create clouds, marble, fire, and terrain from pure math.
- **The graphics pipeline in miniature**: Vertex shader positions a fullscreen quad; the fragment shader does all the creative work per pixel.

## How it works

The playground compiles your GLSL source on every keystroke and links it into a program that draws a fullscreen quad. Each frame it sets uniforms (time, resolution, mouse), then the GPU runs your main function once per pixel, writing colors into the framebuffer. Compile errors are caught and shown inline so you can fix syntax without leaving the editor. Saved shaders get shareable URLs so others can fork and remix them.

## Build milestones

1. Render a fullscreen quad with a hardcoded fragment shader that outputs a gradient.
2. Add a text editor pane with live recompile and inline error messages.
3. Expose uniforms: time, resolution, and mouse position for interactive effects.
4. Implement a gallery of starter shaders (plasma, SDF circle, fbm clouds) users can load.
5. Add shader saving with shareable links and a thumbnail preview per shader.
6. Support multi-pass shaders (render to texture, then post-process) and audio-reactive uniforms.

## Best resources

- [The Book of Shaders](https://thebookofshaders.com/) — a gentle step-by-step guide through fragment shaders by Patricio Gonzalez Vivo and Jen Lowe.
- [thebookofshaders source](https://github.com/patriciogonzalezvivo/thebookofshaders) — the book's code and examples to study and remix.
- [awesome-glsl](https://github.com/vanrez-nez/awesome-glsl) — a curated compilation of resources for learning OpenGL shaders.
- [ShaderToy](https://www.shadertoy.com/) — the canonical live shader playground and community gallery.
- [30 Days of Shade](https://willstall.github.io/30-days-of-shade/) — a month of bite-sized shader exercises.

## Stretch ideas

- Add a node-based editor that generates GLSL from connected blocks.
- Implement raymarching in the fragment shader to render 3D SDF scenes.
