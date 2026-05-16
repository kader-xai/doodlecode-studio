# Usage guide

## The 60-second workflow

1. **📂 Open** a Python file — `.py`, `.ipynb`, or `.md`. Or start typing
   in the seeded cell.
2. For each section you want to explain, click **✎** in the cell header.
   Write a Title and an Explanation, pick a Color, hit **Save**. The
   bubble appears on the right; the cell's header strip and editor's left
   strip share the color.
3. **▶ Run** each cell. Output appears in the white `↳ output` panel
   below the editor — never on the right.
4. **🎬 Present** to step through cells like slides.
5. **💾 Save** to download the `.py`. (Auto-saved too — see below.)

## Toolbar reference

| Button       | Action |
|--------------|--------|
| **📂 Open**  | Upload `.py` / `.ipynb` / `.md`. Replaces the current notebook. |
| **💾 Save**  | Download the current notebook as a `.py` with `# %%` + `# @explain:` directives. |
| **＋ Cell**  | Append an empty code cell. |
| **↻ Kernel** | Restart the IPython kernel — clears all in-memory state. |
| **🎬 Present** | Toggle presentation mode. |
| **🌙 / ☀**   | Toggle dark / light theme. |
| **ⓘ About**  | Show the developer info + links modal. |

## Canvas controls

Three tools live in the top-left toggle (Figma convention):

| Tool | Shortcut | What drag does | What click does |
|------|----------|----------------|-----------------|
| **➤ Cursor** (default) | **V** | nothing | select / focus |
| **✋ Hand** | **H** | pans the canvas | select / focus |
| **✥ Move** | **M** | moves the cell | select / focus |

Across all three tools:

| Action | How |
|--------|-----|
| Two-finger trackpad scroll | pans the canvas |
| Cmd / Ctrl + scroll | zoom |
| Pinch (trackpad) | zoom |
| Double-click a cell title | rename inline |
| **Double-click anywhere on a code cell** | opens the callout editor |
| **Double-click anywhere on a text cell** | opens the text editor |
| **Double-click a callout bubble** | opens the callout editor for its source cell |
| Click on a callout bubble | pans the view to its source cell |

Monaco editor scrolling and the output panel both keep their own scroll
— they don't pan the canvas.

## The callout editor

Click **✎** in any code cell's header.

- **Title** — short, shown in big handwriting on the bubble. Optional.
- **Explanation** — multi-line body. This is what your audience reads.
- **Section kind** — free-text label (e.g. `data`, `model`, `loop`). Used
  for downstream tooling; can be left blank.
- **Color** — pick from the 8-swatch palette. Repaints the header, left
  strip, and bubble.
- **Remove** — drop the callout entirely. The cell's right-side bubble
  disappears and no metadata is serialized.

Edits live in `localStorage` immediately and hit the disk-autosave
endpoint after 1.2 seconds idle.

## Save vs autosave vs export

| Mechanism | When  | Where | Reversible? |
|-----------|-------|-------|-------------|
| **localStorage**   | Every keystroke (debounced) | Your browser | Lasts until you clear browser data |
| **`POST /autosave`** | Every change (debounced 1.2 s) | `~/.doodlecode/<name>.py` | Last write wins |
| **💾 Save (export)** | Manual | Downloaded to your computer | Always available |

The toolbar shows `saved Ns ago` when autosave succeeds.

## Presentation mode

- Press **🎬 Present**.
- A `◀ Prev · Slide M/N · Next ▶` strip appears at the bottom.
- The canvas pans/auto-fits to each focused cell. Set your starting
  zoom once with Cmd+scroll; arrows then move you slide-by-slide.

### Presenter tools (v0.7)

Two extra buttons sit on the presenter bar:

| Tool | Shortcut | What it does |
|------|----------|--------------|
| **✒️ Pen** (Excalidraw-style) | **P** | Drag to draw red ink. Strokes fade out in ~1.4 s. Perfect for circling something to draw the eye — your circle vanishes by the time the audience looks. |
| **🖍 Highlighter** | **H** | Thick translucent yellow ink that fades in ~4 s. Use for stable annotations on a slide. |

Both toggle off when pressed again, or auto-clear when you exit
presentation mode (Esc).

## Troubleshooting

### Installing libraries (PyTorch, pandas, anything)

The kernel runs in `backend/.venv` and starts with only the basics. To
add any package:

- **Toolbar → 📦 Install** → type the package name(s) (`torch`,
  `pandas matplotlib==3.9.*`, etc.) → hit ▶ Install. Once finished the
  package is importable in the next `import` statement — no kernel
  restart needed.
- **Automatic prompt on `ModuleNotFoundError`** — if a cell errors with
  `No module named 'foo'`, an "📦 Install foo" chip appears above the
  traceback. Click it; we even remap common aliases (`cv2` →
  `opencv-python`, `PIL` → `pillow`, `sklearn` → `scikit-learn`,
  `yaml` → `pyyaml`, `bs4` → `beautifulsoup4`).
- **From a cell** — IPython's `%pip install …` magic also works
  because the kernel is real IPython. Useful for embedding the install
  step inside an example notebook.

Heavy installs like `torch` take 1–2 minutes on the first run; the
toolbar shows an "📦 installing …" pill while it runs.

### "▶ Run" spins forever

The Python kernel may be installing a heavy dependency (e.g. PyTorch in
the demo file). Watch the backend log: `tail -f /tmp/doodle-backend.log`.
If the cell really is hung, click **↻ Kernel** to restart.

### Plot or display output doesn't appear

The kernel emits matplotlib via `image/png` mime bundles, which the
Outputs panel renders. If you're using a third-party library that emits
something exotic (e.g. `image/svg+xml`), open a feature request — we'll
add the mime type.

### Callouts disappeared after upload

Make sure the file you uploaded has the `# %%` markers preserved. Some
editors silently turn cell-marker comments into bare comments — pasting
into a different IDE can lose them. Use **💾 Save** to round-trip
through DoodleCode.

### Mouse wheel doesn't scroll inside Monaco

That should never happen — Monaco is marked `nowheel`. If it does, your
browser may be eating the event; please file a bug with the OS / browser.

## Keyboard shortcuts

Currently very minimal — the canvas focuses on mouse / trackpad. The
Monaco editor has its full standard shortcut set (Cmd-S inside an editor
is intercepted by Monaco — use the toolbar 💾 Save for export).

A future release will add canvas-level shortcuts (`R` to run, `M` to
markdown, etc.). PRs welcome.
