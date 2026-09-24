# Example: 2D Game Engine — "Neon Drift"

**[▶ Play it live](https://byoe-2d-game-engine.netlify.app)**

A complete tiny 2D game engine in **one HTML file, zero dependencies, zero assets**.
Dodge asteroids, shoot them apart, chase your high score — on desktop or mobile.

This is an *example project* for the [games-graphics learning path](../../topics/2d-game-engine/):
it shows what "build your own game engine" actually produces. Read the topic guide
first for the theory, then read this code to see every concept running.

## Run it

Just open `index.html` in a browser — no build step, no server. Or play the hosted
version above.

**Controls**

| Desktop | Mobile |
|---|---|
| ← → / A D — rotate | Touch & hold — steer toward finger + thrust |
| ↑ / W — thrust | FIRE button — shoot |
| Space — shoot / start | Tap — start / restart |

## Engine systems (where to look in `index.html`)

| System | Concept it teaches | Code |
|---|---|---|
| Fixed-timestep game loop | Simulation decoupled from rendering; accumulator pattern; spiral-of-death guard | `frame()`, `STEP = 1/120` |
| Entity system | Game objects as plain data + functions, no inheritance | `ship`, `bullets`, `asteroids`, `particles` arrays |
| Input | Keyboard state map, pointer events, touch steering | `keys`, `touchSteer` |
| Collision | Circle-vs-circle tests | the two collision loops in `update()` |
| Particles | Pooled short-lived entities, capped for performance | `burst()` |
| Parallax starfield | Layered scrolling at different speeds = cheap depth | `initStars()` |
| Synth audio | WebAudio oscillators instead of asset files | `beep()`, `sfx` |
| Game states | Menu → playing → game-over state machine | `state`, `startGame()`, `gameOver()` |
| Juice | Screen shake, invulnerability blink, thruster flame | `shake`, `invuln` |

## Exercises

1. **Spatial hash** — the bullet/asteroid collision is O(n·m). Add a uniform grid
   broadphase and watch it scale to 500 asteroids.
2. **Power-ups** — triple-shot, shield, slow-mo. Each is a 10-line entity.
3. **Enemy AI** — make some asteroids home toward the player (steering behaviors).
4. **Fixed timestep rendering** — add interpolation between steps for buttery motion
   on 120 Hz+ displays.

## Files

- `index.html` — the whole engine + game (~470 lines, commented)
- `README.md` — this file
