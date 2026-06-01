# DoodleCode — Remotion feature tour 🎬

A **60-second, silent** montage of every DoodleCode feature, in the app's
doodle aesthetic. Record your voiceover over it — see [`SCRIPT.md`](SCRIPT.md)
for a timed script.

It renders with **no external assets** (every scene is code-drawn), so you
can `npm i && npm start` and immediately see it. Swap in real footage where
you want extra punch (below).

## Run it

```bash
cd remotion-demo
npm install
npm start          # opens Remotion Studio — scrub the timeline live
```

## Render

```bash
npm run build       # → out/doodlecode-tour.mp4   (1920×1080, 30 fps, 60 s)
npm run build:webm  # → out/doodlecode-tour.webm  (transparent-friendly)
npm run build:gif   # → out/doodlecode-tour.gif   (960px, every 2nd frame)
```

(First render downloads a headless Chromium via Remotion — that's normal.)

## The timeline (30 fps · 1800 frames)

| Scene | Time | What it shows |
|-------|------|----------------|
| Intro | 0:00–0:04 | Logo + tagline |
| One canvas, any cell | 0:04–0:11 | Cell types, ➕ Add menu, one `.py`, callouts |
| Run real Python | 0:11–0:18 | Code cell types in, Run, matplotlib plot draws on |
| Mermaid + flowcharts | 0:18–0:24 | Flowchart builds, sequence diagram, KaTeX math |
| Data, hand-drawn | 0:24–0:31 | Bar + line + pie charts animate in |
| Build it up live | 0:31–0:37 | Animation cell steps through frames |
| Embed live media | 0:37–0:44 | YouTube player, AI GIF (neural net), Wikipedia browser |
| Presentation mode | 0:44–0:51 | Centered slide, progress bar, timer, pen + highlighter ink |
| Install anything | 0:51–0:56 | `pip install` modal, progress, models |
| Outro | 0:56–1:00 | Wrap-up + repo link |

Edit timings in `src/DemoTour.tsx` (the `SCENES` array: `from` / `dur`).

## Use REAL footage (optional)

The media scene uses mockups so it renders dependency-free. To use real
captures, drop files in `public/assets/` and swap the mock blocks in
`src/scenes/MediaScene.tsx`:

```tsx
import { Img, OffthreadVideo, staticFile } from "remotion";

<OffthreadVideo src={staticFile("assets/clip.mp4")} />     {/* real video */}
<Img src={staticFile("assets/wikipedia.png")} />           {/* screenshot */}
<Img src={staticFile("assets/ai.gif")} />                  {/* GIFs animate */}
```

Great real assets to capture from the running app (`http://localhost:8001`):
a real matplotlib output, a real Mermaid render, a real presentation with
your own ink, and a screen-grab of the `pip install` modal.

## Brand

Colors + fonts live in `src/theme.ts`, mirrored from the app
(`tailwind.config.js` marker-\* palette). Want a crisper marker font?
`npm i @remotion/google-fonts` and load e.g. *Caveat* or *Patrick Hand*
in `theme.ts`.
