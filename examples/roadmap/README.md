# Data Science Roadmap — DoodleCode decks

Ninety presentation-ready `.py` files, one per module of the
**Data Science Roadmap**, converted into the DoodleCode Studio
slide format so they can be opened with 📂 Open and presented live
with 🎬 Present.

## Source

All content is derived from the original Jupyter notebooks in:

> **kader-xai / data-science-roadmap**
> https://github.com/kader-xai/data-science-roadmap

The roadmap is authored and maintained by **Kader Mohideen**. The
notebooks in this directory are an adapted, slide-friendly
presentation layer over the same source material — same code, same
ideas, just sliced into one-concept-per-card with short markdown
intros and 1–5 callout bullets per code slide.

## How they were created

- The 90 `module_*.ipynb` notebooks were cloned from the source repo.
- Each was sliced into a DoodleCode `.py` deck where:
  - Code blocks are kept **verbatim** — what runs in the original
    notebook also runs here.
  - Markdown is trimmed to **short, presentation-friendly slides**
    (≤ 8 lines per card, headings preserved).
  - Each code slide carries **1–5 `# @explain:` callouts** that
    appear as the right-side hand-drawn bubble in the canvas.
  - Boilerplate (Colab badges, "part of data-science-roadmap"
    banner) is stripped.
- Color palette rotates through the 8-color doodle theme
  (sky / mint / peach / violet / amber / rose / lime / teal).

The auto-conversion is a starting point. **Module 1
(`module_01_python_basics.py`) is hand-tuned** as the reference
style — tighter slide count, callouts that teach instead of echo
the inline comment. Other modules can be tightened the same way
on demand.

## How to use

1. From the repo root, start the app:
   ```bash
   ./start.sh
   ```
2. Open http://localhost:8000.
3. Click **📂 Open**, navigate to `examples/roadmap/`, pick any
   `module_XX_*.py`.
4. Click **🎬 Present** and use **→** / **←** (or Space / Shift+Space)
   to step through.

## Files

`module_01_python_basics.py` through `module_90_edge_on_device_ai.py`
— **90 decks total**, ~27 slides each (~2,400 slides across the
whole roadmap).

## Attribution & license

- Original notebook content © Kader Mohideen, used under the source
  repo's license. See
  https://github.com/kader-xai/data-science-roadmap/blob/main/LICENSE
  for terms.
- DoodleCode Studio itself is MIT-licensed; see the repo root
  `LICENSE`.
- These adapted decks are shipped as **examples** for presenters
  using DoodleCode Studio. Always cite the source repo when
  presenting derivative material.
