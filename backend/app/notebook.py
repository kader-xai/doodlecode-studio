"""Parse uploaded files into a Notebook of cells.

Supported `.py` cell-marker formats:

  # %% [markdown]
  # text content of a markdown cell

  # %% kind=function color=mint title="Defining the area function"
  # @explain: First callout body.
  # @image: data:image/png;base64,...     (optional)
  # @tags: function, math
  # @callout title="Second bubble" color=peach
  # @explain: A second callout next to the same cell.
  import math
  def area_of_circle(r):
      return math.pi * r * r

Backward-compatible: files with only the v1 fields (single callout, no
images) still parse into the same `Notebook` shape — v2 just adds the
`callouts` list and the `image` field.
"""
from __future__ import annotations

import json
import re
import uuid
from typing import Optional

from .models import FILE_FORMAT_VERSION, CalloutBlock, Cell, CellMeta, Notebook

_HEADER_RE = re.compile(r"(?m)^[ \t]*#[ \t]*%%[ \t]*(.*)$")
_KV_RE = re.compile(r'(\w+)\s*=\s*("(?:[^"\\]|\\.)*"|\S+)')
_AT_RE = re.compile(r"^[ \t]*#[ \t]*@(\w+)\b[ \t]*(?::[ \t]*(.*)|\s*(.*))$")


# ---------- public ----------

def from_ipynb(name: str, raw: bytes) -> Notebook:
    nb = json.loads(raw.decode("utf-8"))
    cells: list[Cell] = []
    for c in nb.get("cells", []):
        kind = "code" if c.get("cell_type") == "code" else "markdown"
        src = c.get("source", "")
        if isinstance(src, list):
            src = "".join(src)
        cells.append(Cell(id=str(uuid.uuid4()), kind=kind, source=src))
    return Notebook(name=name, cells=cells)


def from_py(name: str, raw: bytes) -> Notebook:
    text = raw.decode("utf-8")
    if "# %%" not in text and "#%%" not in text:
        return Notebook(
            name=name,
            cells=[Cell(id=str(uuid.uuid4()), kind="code", source=text.strip("\n"))],
        )
    return _split_with_markers(name, text)


def from_markdown(name: str, raw: bytes) -> Notebook:
    text = raw.decode("utf-8")
    cells: list[Cell] = []
    pattern = re.compile(r"```python\n(.*?)```", re.DOTALL)
    last = 0
    for m in pattern.finditer(text):
        if m.start() > last:
            md = text[last:m.start()].strip()
            if md:
                cells.append(Cell(id=str(uuid.uuid4()), kind="markdown", source=md))
        cells.append(Cell(id=str(uuid.uuid4()), kind="code", source=m.group(1).rstrip()))
        last = m.end()
    if last < len(text):
        tail = text[last:].strip()
        if tail:
            cells.append(Cell(id=str(uuid.uuid4()), kind="markdown", source=tail))
    return Notebook(name=name, cells=cells)


# ---------- internals ----------

def _parse_kv(header: str) -> dict[str, str]:
    out: dict[str, str] = {}
    for m in _KV_RE.finditer(header):
        k, v = m.group(1), m.group(2)
        if len(v) >= 2 and v[0] == '"' and v[-1] == '"':
            # Unescape `\"` and `\\` without round-tripping through bytes
            # (that destroys multi-byte UTF-8 characters like em-dash, π).
            inner = v[1:-1]
            out_chars: list[str] = []
            i = 0
            while i < len(inner):
                if inner[i] == "\\" and i + 1 < len(inner):
                    nxt = inner[i + 1]
                    out_chars.append({"n": "\n", "t": "\t", '"': '"', "\\": "\\"}.get(nxt, nxt))
                    i += 2
                else:
                    out_chars.append(inner[i])
                    i += 1
            v = "".join(out_chars)
        out[k] = v
    return out


_MARKDOWN_FLAG_RE = re.compile(r"^\s*\[?markdown\]?\s*", re.IGNORECASE)


def _parse_header(header: str) -> tuple[bool, dict[str, str]]:
    h = header.strip()
    is_markdown = bool(_MARKDOWN_FLAG_RE.match(h))
    if is_markdown:
        # Strip the leading `[markdown]` (or `markdown`) marker so the
        # rest of the header parses as plain key=value pairs.
        h = _MARKDOWN_FLAG_RE.sub("", h)
    return is_markdown, _parse_kv(h)


def _block_from_dict(d: dict) -> CalloutBlock:
    tags = []
    raw_tags = d.get("tags", "")
    if isinstance(raw_tags, str) and raw_tags:
        tags = [t.strip() for t in raw_tags.split(",") if t.strip()]
    elif isinstance(raw_tags, list):
        tags = list(raw_tags)
    return CalloutBlock(
        title=d.get("title"),
        explain=d.get("explain"),
        color=d.get("color"),
        kind=d.get("kind"),
        image=d.get("image"),
        tags=tags,
    )


def _drain_directives(lines: list[str], i: int) -> tuple[dict, int]:
    """Read one block of `# @key: ...` lines starting at index i.
    Returns (dict-with-multiline-explain-joined, next-index)."""
    acc: dict[str, list[str]] = {}
    while i < len(lines):
        line = lines[i]
        if line.strip() == "" and acc:
            i += 1
            continue
        m = _AT_RE.match(line)
        if not m:
            break
        key = m.group(1)
        if key == "callout":
            break  # caller handles the new-callout marker
        val = (m.group(2) if m.group(2) is not None else m.group(3) or "").strip()
        acc.setdefault(key, []).append(val)
        i += 1
    out: dict[str, str] = {}
    for k, vs in acc.items():
        if k == "explain":
            out[k] = " ".join(v for v in vs if v)
        else:
            out[k] = vs[-1]  # last wins for single-value keys
    return out, i


def _extract_callouts(
    body: str, header_meta: dict[str, str]
) -> tuple[list[CalloutBlock], str, Optional[str]]:
    """Split leading `# @...` directives into one or more CalloutBlocks.
    Returns (callouts, remaining source, box_image).

    `box_image` is the cell-body image (`# @box_image:`) — it belongs to
    the cell itself, NOT to any callout, so we yank it out before
    building the primary callout dict."""
    lines = body.split("\n")
    callouts: list[CalloutBlock] = []

    # First callout = header kv + leading @-directives.
    first_attrs, i = _drain_directives(lines, 0)
    primary = {**header_meta, **first_attrs}
    primary.pop("version", None)  # version is a file-level concept, not callout
    box_image = primary.pop("box_image", None)
    if any(primary.get(k) for k in ("title", "explain", "color", "kind", "image", "tags")):
        callouts.append(_block_from_dict(primary))

    # Subsequent callouts opened by `# @callout ...` lines.
    while i < len(lines):
        line = lines[i]
        m = _AT_RE.match(line)
        if m and m.group(1) == "callout":
            inline = _parse_kv(m.group(2) or m.group(3) or "")
            i += 1
            attrs, i = _drain_directives(lines, i)
            merged = {**inline, **attrs}
            callouts.append(_block_from_dict(merged))
            continue
        if line.strip() == "":
            i += 1
            continue
        break

    rest = "\n".join(lines[i:]).strip("\n")
    return callouts, rest, box_image


def _meta_from_callouts(
    callouts: list[CalloutBlock], box_image: Optional[str] = None
) -> Optional[CellMeta]:
    if not callouts and not box_image:
        return None
    if callouts:
        primary = callouts[0]
        extras = callouts[1:]
        return CellMeta(
            kind=primary.kind,
            color=primary.color,
            title=primary.title,
            explain=primary.explain,
            tags=list(primary.tags),
            image=primary.image,
            callouts=extras,
            box_image=box_image,
        )
    # No callouts but a box_image is set — still need a meta to carry it.
    return CellMeta(box_image=box_image)


def _markdown_strip(body: str) -> str:
    out = []
    for line in body.split("\n"):
        out.append(re.sub(r"^[ \t]*#[ \t]?", "", line))
    return "\n".join(out).strip("\n")


def _extract_markdown_directives(
    body: str, header_meta: dict[str, str]
) -> tuple[list[CalloutBlock], str, Optional[str]]:
    """Markdown cells can carry the same `# @title:` / `# @image:` /
    `# @callout` directives as code cells. Strip them first; the rest of
    the body is markdown text (still with leading `# ` per line)."""
    lines = body.split("\n")
    callouts, _rest_drop, box_image = _extract_callouts("\n".join(lines), header_meta)

    # Reconstruct the markdown body by skipping the directive lines that
    # `_extract_callouts` would have consumed.
    rest_lines: list[str] = []
    consumed_directive_block = False
    i = 0
    while i < len(lines):
        line = lines[i]
        if not consumed_directive_block:
            if _AT_RE.match(line) or line.strip() == "":
                i += 1
                continue
            consumed_directive_block = True
        rest_lines.append(line)
        i += 1

    return callouts, _markdown_strip("\n".join(rest_lines)), box_image


def _split_with_markers(name: str, text: str) -> Notebook:
    headers = list(_HEADER_RE.finditer(text))
    cells: list[Cell] = []
    format_version = FILE_FORMAT_VERSION

    if headers and headers[0].start() > 0:
        pre = text[: headers[0].start()]
        # Pick up a "format-version: N" line if present.
        m = re.search(r"(?im)^[ \t]*#[ \t]*doodlecode[^\n]*format-version[: \t]+(\d+)", pre)
        if m:
            try:
                format_version = int(m.group(1))
            except ValueError:
                pass
        pre_stripped = pre.strip("\n")
        # Drop a preamble that is only comments / blank lines — that's
        # the auto-generated header. Real code at the top is preserved.
        only_comments = all(
            (not ln.strip()) or ln.lstrip().startswith("#")
            for ln in pre_stripped.split("\n")
        )
        if pre_stripped.strip() and not only_comments:
            cells.append(Cell(id=str(uuid.uuid4()), kind="code", source=pre_stripped))

    for idx, h in enumerate(headers):
        body_start = h.end()
        body_end = headers[idx + 1].start() if idx + 1 < len(headers) else len(text)
        body = text[body_start:body_end].lstrip("\n").rstrip()
        is_md, header_attrs = _parse_header(h.group(1))
        if "version" in header_attrs:
            try:
                format_version = int(header_attrs["version"])
            except ValueError:
                pass
        if is_md:
            callouts, md_source, box_image = _extract_markdown_directives(body, header_attrs)
            cells.append(Cell(
                id=str(uuid.uuid4()),
                kind="markdown",
                source=md_source,
                meta=_meta_from_callouts(callouts, box_image=box_image)
                    if (callouts or box_image)
                    else None,
            ))
        else:
            callouts, source, box_image = _extract_callouts(body, header_attrs)
            cells.append(Cell(
                id=str(uuid.uuid4()),
                kind="code",
                source=source,
                meta=_meta_from_callouts(callouts, box_image=box_image),
            ))
    return Notebook(name=name, cells=cells, format_version=format_version)
