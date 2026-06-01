"""Export a notebook to a plain-Markdown document (iter 219).

Turns a deck into a readable, shareable `.md` handout — titles become
headings, code becomes fenced ```python blocks, diagram/chart sources
become fenced ```text blocks, media/browser become links or images, and
audience-facing callouts become blockquotes. Speaker notes are presenter-
private (product principle) and are intentionally omitted.

Pure + dependency-free so it unit-tests without the kernel or a browser.
"""
from __future__ import annotations

from .models import CellPayload, NotebookPayload

_IMG_EXT = (".png", ".jpg", ".jpeg", ".gif", ".webp", ".svg", ".bmp", ".avif")


def _is_image_url(src: str) -> bool:
    s = src.split("?")[0].split("#")[0].strip().lower()
    return s.startswith("data:image/") or s.endswith(_IMG_EXT)


def _blockquote(text: str) -> str:
    return "\n".join("> " + line if line else ">" for line in text.split("\n"))


def _cell_body(c: CellPayload) -> str:
    src = (c.source or "").strip()
    if c.kind == "markdown":
        return src
    if c.kind == "code":
        blocks = [f"```python\n{src}\n```"] if src else []
        # Reveals are the live build-up steps of a code walkthrough — the
        # teaching content. Emit each as its own labeled fenced block so a
        # handout captures the full progression, not just the base.
        for i, rev in enumerate(c.reveals or [], 1):
            step = (rev or "").rstrip("\n")
            if step.strip():  # skip blank reveals; keep indentation otherwise
                blocks.append(f"*Step {i}:*\n\n```python\n{step}\n```")
        return "\n\n".join(blocks)
    if c.kind == "diagram":
        # The doodle/mermaid source is human-readable; fence it as text so
        # a reader sees the chart's data definition even without a render.
        return f"```text\n{src}\n```" if src else ""
    if c.kind == "media":
        if not src:
            return ""
        label = c.title or "media"
        return f"![{label}]({src})" if _is_image_url(src) else f"[▶ Video]({src})"
    if c.kind == "browser":
        return f"[🔗 Live demo]({src})" if src else ""
    if c.kind == "whiteboard":
        return "_[Whiteboard sketch]_"
    return src


def _reading_order(cells: list[CellPayload]) -> list[CellPayload]:
    """Top-to-bottom, left-to-right — the same spatial order the canvas uses
    to navigate slides (store.cellsInOrder: y bucketed at 40px, then x).
    Python's sort is stable, so cells in the same cell tie-break on input
    order, matching the frontend."""
    return sorted(cells, key=lambda c: (round((c.y or 0) / 40), c.x or 0))


def to_markdown(nb: NotebookPayload) -> str:
    """Render the whole notebook as a single Markdown document. Cells are
    emitted in canvas reading order so the handout matches the slide flow."""
    out: list[str] = [f"# {nb.name}".rstrip(), ""]
    for c in _reading_order(nb.cells):
        if c.title:
            out.append(f"## {c.title}")
            out.append("")
        body = _cell_body(c)
        if body:
            out.append(body)
            out.append("")
        for co in c.callouts or []:
            if co.text and co.text.strip():
                out.append(_blockquote(co.text.strip()))
                out.append("")
            if co.image and co.image.strip():
                # Keep the annotation image in the handout (callouts can be
                # text, image, or both). Alt text reuses the callout text.
                alt = (co.text or "callout").strip().split("\n")[0] or "callout"
                out.append(f"![{alt}]({co.image.strip()})")
                out.append("")
    return "\n".join(out).rstrip() + "\n"
