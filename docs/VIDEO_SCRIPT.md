# Recording script — "Python as a doodle presentation"

A complete shot list for a **~3-minute screencast** of DoodleCode Studio
turning a Python file into a colorful, hand-drawn presentation. Record
in one take with QuickTime / OBS / Loom / ScreenStudio.

**Total runtime:** 2:50 – 3:30 minutes.
**On-screen file:** [`examples/video_demo_python_in_presentation.py`](../examples/video_demo_python_in_presentation.py).
**Audio:** narrate as you go, or record screen-only and add a voiceover
afterward.

---

## Before you hit record

```bash
# 1. Make sure the app is running
./start.sh

# 2. In the browser at http://localhost:5173, force a clean slate:
#    - DevTools → Application → Local Storage → clear
#    - Refresh the page

# 3. Set theme to Light (cleaner on camera), zoom your browser to
#    100% (Cmd+0), full-screen the window (Cmd+Shift+F on Chrome).

# 4. Open QuickTime Player → File → New Screen Recording → choose the
#    browser window only. Aim for 1080p / 60 fps if you can.
```

A 16:9 ratio with the browser at ~1600 × 900 reads well on YouTube.

---

## Shot list

| # | Time     | What's on screen                                          | What you do                                                                                                                          | Narration (read aloud or post-dub)                                                                                                                                                                                  |
|---|----------|-----------------------------------------------------------|--------------------------------------------------------------------------------------------------------------------------------------|---------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------|
| 1 | 0:00–0:08 | Empty DoodleCode Studio, light theme.                     | Hover the toolbar. Show **📂 Open**, **💾 Save**, **🎬 Present**, **📦 Install**.                                                     | "This is DoodleCode Studio — a Python notebook that turns your code into a hand-drawn whiteboard. Everything's local. Let me show you what it can do."                                                              |
| 2 | 0:08–0:18 | Toolbar with **📂 Open** highlighted.                     | Click **📂 Open** → pick `video_demo_python_in_presentation.py`.                                                                     | "I'll open a small Python lesson — a real `.py` file with twelve cells covering the basics."                                                                                                                        |
| 3 | 0:18–0:30 | Canvas showing colored cells on the left, bubbles on right. | Pan with two-finger trackpad scroll. Pinch out a bit, then back.                                                                     | "Every code block is a colored card. Every card has a callout on the right that I wrote myself — those are real comments in the file, not AI-generated noise. Drag to pan, pinch to zoom."                          |
| 4 | 0:30–0:42 | The "Variables hold values" cell focused.                 | Click ✎ on the cell. Show the editor popover. Change the title to "**Naming things in Python**", change color to **mint**, hit **Save**. | "I can edit any callout in-place. Title, body, kind, color. The bubble and the card's color stripe both update instantly — and the change goes straight into the `.py` file when I save."                            |
| 5 | 0:42–0:55 | Same cell, but now with **▶ Run** button highlighted.     | Click **▶ Run**. Output panel appears below.                                                                                          | "Hit Run and it executes on a real Jupyter kernel. The output box drops in below the editor — colorful, scrollable, never overlapping anything else."                                                               |
| 6 | 0:55–1:08 | Cell with `import torch` somewhere (use the AI demo if you prefer). | Type `import torch` in any cell, hit Run. **📦 Install torch** chip appears in the output box. Click it. Wait or fast-forward.       | "If I import something that's not installed, the kernel returns a normal error — but a one-click install button appears right there. Behind the scenes that runs `pip install` into the kernel's environment."     |
| 7 | 1:08–1:30 | Toolbar with **🎬 Present** highlighted.                  | Click **🎬 Present**. The view animates and fits the first cell to the screen with the Prev/Next bar appearing at the bottom.        | "Now the fun part. Hit Present and the canvas auto-fits each slide to the viewport — bigger cards get a bit of zoom-out, small ones zoom in. The callout sits next to the code so the audience reads both at once." |
| 8 | 1:30–2:00 | First cell, then `→` arrow → second cell, etc.            | Tap **→** four or five times slowly. After each, pause one beat, then click ▶ Run on one cell so the output appears mid-talk.        | "Right arrow advances. Up and down don't scroll the canvas — only the buttons or the arrows move slides. Watch what happens when I run a cell mid-presentation: the box shifts up so the output is fully visible."  |
| 9 | 2:00–2:15 | Cell with a long output growing under it.                 | Press `→` past the output cell. See how the next cell is positioned BELOW the long output, no overlap.                              | "The canvas measures every cell and pushes the next one down automatically — long stdout never collides with the next slide."                                                                                       |
| 10| 2:15–2:30 | Press **Esc** to exit presentation.                       | Cmd+Shift to toggle dark mode (the **🌙 Dark** button).                                                                              | "Esc exits. There's a light and a dark theme — Excalidraw-inspired palette, tuned for legibility on both."                                                                                                          |
| 11| 2:30–2:45 | Toolbar with **💾 Save** highlighted.                     | Click **💾 Save** → file downloads. Open it in your text editor (TextEdit / VS Code) side-by-side.                                   | "Save downloads a plain `.py`. The callouts are encoded as `# @explain:` comments — readable, diffable, commit it to git. Reopen it tomorrow and your callouts come back exactly as you left them."                |
| 12| 2:45–3:00 | About modal.                                              | Click **ⓘ About** → show LinkedIn / GitHub / website links. Close.                                                                  | "It's open source, MIT-licensed, all local. Repo's in the description. Thanks for watching."                                                                                                                        |

---

## Tips while recording

- **Cursor**: turn on cursor highlight in your screen recorder. macOS QuickTime → Show Mouse Clicks; Loom has its own highlight.
- **Click cadence**: pause one full beat after every click so the viewer sees the effect.
- **Keyboard**: when you press **→**, **Esc**, etc, say the key name out loud — even better, enable a key-overlay tool like [KeyCastr](https://github.com/keycastr/keycastr).
- **Zoom in for editor moments**: at scene 4 (editing a callout), nudge browser zoom to 110% so the popover is legible at 1080p.
- **Don't move the mouse during a card-zoom**: the auto-fit animation is the wow factor. Let it finish before clicking again.
- **One take, edit later**: keep recording even if you flub a line. Trim in iMovie / DaVinci Resolve. Pauses are cheaper than retakes.

---

## Cover frame / thumbnail

A good thumbnail is the canvas at presentation time on the "Functions
package up reusable logic" cell — bright **mint** title strip, dark
Monaco editor, mint callout bubble on the right with the **`def`** key
word visible. Add big handwriting-font text **"Python, presented."** in
the upper-left corner of the frame.

---

## Publish

- **YouTube**: title `Doodling Python — a 3-minute tour of DoodleCode Studio`, description points at the repo + the example file. Tag it `python`, `jupyter`, `notebook`, `presentation`, `excalidraw`, `open source`.
- **Twitter / X**: trim to 60 seconds — scenes 3 → 7 → 11 cover the wow moments. Caption: *"I built an open-source Python notebook where every cell is a doodle with its own callout. One file, your handwriting in code form. → [link]"*
- **Repo README**: at the top of `README.md`, insert a link to the video and an animated GIF of scenes 7–9 (the presentation auto-fit). Use [Gifski](https://gif.ski/) for a small, sharp GIF from your recording.
