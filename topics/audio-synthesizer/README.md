---
title: "Audio Synthesizer"
category: "games-graphics"
difficulty: "intermediate"
tags: ["audio", "synthesis", "dsp"]
related: [chip8-emulator, particle-system, tween-animation-system]
---

# Audio Synthesizer
An audio synthesizer generates sound from math: oscillators, filters, and envelopes combine to make everything from chiptune bleeps to lush pads. Games use synthesis for adaptive music and procedural sound effects that samples can't provide. Building one teaches you digital signal processing hands-on.

## Core concepts

- **Oscillators**: Sine, square, sawtooth, and triangle waves are the raw ingredients; their harmonic content determines the basic timbre.
- **Sampling**: Audio is a stream of amplitude values (typically 44,100 per second); the synthesizer computes each sample in real time.
- **ADSR envelopes**: Attack, Decay, Sustain, Release shape a note's volume over time — a piano pluck and a string pad differ mostly in envelope.
- **Filters**: Low-pass, high-pass, and band-pass filters sculpt harmonics; sweeping a filter cutoff over time is the classic synth move.
- **LFOs and modulation**: Low-frequency oscillators modulate pitch (vibrato), amplitude (tremolo), or filter cutoff for movement and richness.
- **Polyphony**: Multiple voices play simultaneously, each with its own oscillator and envelope state, mixed down to one output stream.
- **Effects**: Delay, reverb, chorus, and distortion are DSP blocks chained after the voices to add space and character.

## How it works

A MIDI note (or game event) triggers a voice: one or more oscillators generate raw waveforms at the note's frequency, an ADSR envelope scales their amplitude over the note's life, and the result passes through filters modulated by LFOs. All active voices are summed, run through effects, and written into the audio callback buffer sample by sample. The game drives the synth by sending note-on/note-off and parameter changes, so music and SFX react to gameplay in real time.

## Build milestones

1. Generate a sine wave at a fixed pitch and play it through the audio output.
2. Add square/saw/triangle oscillators, an ADSR envelope, and note on/off control.
3. Implement a low-pass filter with an adjustable cutoff and an LFO for vibrato.
4. Build polyphony: a voice allocator that handles chords and note stealing.
5. Add delay and a simple reverb effect, plus a piano-roll or keyboard UI to play it.
6. Create game-ready features: procedural footstep/explosion SFX and an adaptive music layer driven by game state.

## Best resources

- [Synth Secrets — Sound on Sound](https://www.soundonsound.com/series/synth-secrets-sound-sound) — the legendary series explaining every classic synthesis technique.
- [Stanford audio DSP intro](https://ccrma.stanford.edu/~jos/intro320/intro320.pdf) — Julius Smith's introduction to digital audio signal processing.
- [Julius Smith's internet resources](http://ccrma.stanford.edu/~jos/pasp/Resources_Internet.html) — a curated index of online DSP and audio programming resources.
- [awesome-audio-dsp textbooks](https://github.com/BillyDM/awesome-audio-dsp/blob/main/sections/PAID_TEXTBOOKS.md) — recommended books for going deeper into audio DSP.

## Stretch ideas

- Implement wavetable or FM synthesis for richer, more complex timbres.
- Build a step sequencer that composes chiptune loops from your synth voices.
