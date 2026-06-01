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
        return f"```python\n{src}\n```" if src else ""
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


def to_markdown(nb: NotebookPayload) -> str:
    """Render the whole notebook as a single Markdown document. Cells are
    emitted in their stored order (which is reading order after a Save)."""
    out: list[str] = [f"# {nb.name}".rstrip(), ""]
    for c in nb.cells:
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
    return "\n".join(out).rstrip() + "\n"
