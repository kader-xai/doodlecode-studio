"""Notebook -> .py text with `# %%` markers + `# @explain:` directives.
Round-trips with notebook.from_py().

Format level is recorded in the very first line so future readers can
detect and adapt. Readers without version awareness simply ignore it."""
from __future__ import annotations

import re

from .models import FILE_FORMAT_VERSION, CalloutBlock, Cell, CellMeta, Notebook

_NEEDS_QUOTE = re.compile(r"[\s\"]")


def _kv(k: str, v: str) -> str:
    v = v.replace("\\", "\\\\").replace("\"", "\\\"")
    if _NEEDS_QUOTE.search(v) or not v:
        return f'{k}="{v}"'
    return f"{k}={v}"


def _split_lines(text: str) -> list[str]:
    """One @explain: line per logical line. Preserves internal spacing
    so the parser can reconstruct the original `explain` string exactly
    (parser joins lines with single ' ', so we keep no leading/trailing
    spaces per line, but we DO preserve runs of inner whitespace)."""
    text = (text or "").rstrip()
    if not text:
        return []
    return [line for line in text.split("\n") if line.strip() or True]


def _serialize_callout_directives(c: CalloutBlock, *, header_already: bool) -> list[str]:
    """Emit `# @key: value` lines for one callout. When `header_already`
    is True (i.e. this is the primary callout and the parent header line
    already carries kind/color/title), skip those keys here."""
    lines: list[str] = []
    if not header_already:
        if c.title:
            lines.append(f"# @title: {c.title}")
        if c.kind:
            lines.append(f"# @kind: {c.kind}")
        if c.color:
            lines.append(f"# @color: {c.color}")
    if c.explain:
        for chunk in _split_lines(c.explain):
            lines.append(f"# @explain: {chunk}")
    if c.image:
        lines.append(f"# @image: {c.image}")
    if c.tags:
        lines.append(f"# @tags: {', '.join(c.tags)}")
    return lines


def _serialize_cell(cell: Cell) -> str:
    if cell.kind == "markdown":
        body = "\n".join(
            ("# " + line) if line.strip() else "#" for line in cell.source.split("\n")
        )
        meta = cell.meta
        if not meta:
            return f"# %% [markdown]\n{body}"

        # Build a `# %% [markdown] kind=... color=... title=...` header
        # plus directive lines for image + extra callouts. Mirrors how
        # code cells emit their meta.
        primary = CalloutBlock(
            title=meta.title,
            explain=meta.explain,
            color=meta.color,
            kind=meta.kind,
            image=meta.image,
            tags=list(meta.tags),
        )
        extras = list(meta.callouts or [])
        parts: list[str] = ["[markdown]"]
        if primary.kind:
            parts.append(_kv("kind", primary.kind))
        if primary.color:
            parts.append(_kv("color", primary.color))
        if primary.title:
            parts.append(_kv("title", primary.title))
        header = "# %% " + " ".join(parts)

        lines: list[str] = [header]
        if meta.box_image:
            lines.append(f"# @box_image: {meta.box_image}")
        if meta.cell_type:
            lines.append(f"# @cell_type: {meta.cell_type}")
        if meta.browser_url:
            lines.append(f"# @browser_url: {meta.browser_url}")
        if meta.whiteboard_bg:
            lines.append(f"# @whiteboard_bg: {meta.whiteboard_bg}")
        if meta.strokes:
            lines.append(f"# @strokes: {meta.strokes}")
        if meta.stickers:
            lines.append(f"# @stickers: {meta.stickers}")
        if meta.cell_width is not None:
            lines.append(f"# @cell_width: {int(meta.cell_width)}")
        if meta.cell_height is not None:
            lines.append(f"# @cell_height: {int(meta.cell_height)}")
        if meta.diagram_kind:
            lines.append(f"# @diagram_kind: {meta.diagram_kind}")
        if meta.diagram_font_scale is not None:
            lines.append(f"# @diagram_font_scale: {float(meta.diagram_font_scale):.2f}")
        if meta.text_font_scale is not None:
            lines.append(f"# @text_font_scale: {float(meta.text_font_scale):.2f}")
        lines.extend(_serialize_callout_directives(primary, header_already=True))
        for extra in extras:
            inline_parts: list[str] = []
            if extra.kind:
                inline_parts.append(_kv("kind", extra.kind))
            if extra.color:
                inline_parts.append(_kv("color", extra.color))
            if extra.title:
                inline_parts.append(_kv("title", extra.title))
            marker = "# @callout" + ((" " + " ".join(inline_parts)) if inline_parts else "")
            lines.append(marker)
            lines.extend(_serialize_callout_directives(extra, header_already=True))
        if body.strip("#\n "):
            lines.append("")
            lines.append(body)
        return "\n".join(lines)

    meta = cell.meta or CellMeta()
    primary = CalloutBlock(
        title=meta.title,
        explain=meta.explain,
        color=meta.color,
        kind=meta.kind,
        image=meta.image,
        tags=list(meta.tags),
    )
    extras = list(meta.callouts or [])

    # Header line carries the primary callout's kind/color/title for v1
    # readers — those fields stay where they've always been.
    parts: list[str] = []
    if primary.kind:
        parts.append(_kv("kind", primary.kind))
    if primary.color:
        parts.append(_kv("color", primary.color))
    if primary.title:
        parts.append(_kv("title", primary.title))
    header = "# %%" + (" " + " ".join(parts) if parts else "")

    lines: list[str] = [header]
    if meta.box_image:
        lines.append(f"# @box_image: {meta.box_image}")
    if meta.cell_width is not None:
        lines.append(f"# @cell_width: {int(meta.cell_width)}")
    if meta.cell_height is not None:
        lines.append(f"# @cell_height: {int(meta.cell_height)}")
    lines.extend(_serialize_callout_directives(primary, header_already=True))
    for extra in extras:
        # Inline kind/color/title on the `# @callout` line for compactness.
        inline_parts: list[str] = []
        if extra.kind:
            inline_parts.append(_kv("kind", extra.kind))
        if extra.color:
            inline_parts.append(_kv("color", extra.color))
        if extra.title:
            inline_parts.append(_kv("title", extra.title))
        marker = "# @callout" + ((" " + " ".join(inline_parts)) if inline_parts else "")
        lines.append(marker)
        lines.extend(_serialize_callout_directives(extra, header_already=True))

    if cell.source.strip():
        lines.append("")
        lines.append(cell.source.rstrip())
    return "\n".join(lines)


def serialize_notebook(nb: Notebook) -> str:
    preamble = (
        f"# doodlecode format-version: {FILE_FORMAT_VERSION}\n"
        f"# Generated by DoodleCode Studio. Safe to edit; see docs/FILE_FORMAT.md.\n\n"
    )
    cells_text = [_serialize_cell(c) for c in nb.cells]
    body = ("\n\n\n".join(cells_text)).rstrip() + "\n"
    return preamble + body
