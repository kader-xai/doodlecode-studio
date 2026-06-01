"""Serialize / parse the `.py` notebook format.

Format (v4, additive over v1's v2.x):

    # doodlecode format-version: 4
    # notebook: Untitled

    # %% kind=code id=c0 x=80 y=80
    # @title: Hello, Python
    print("hi")

    # %% kind=code id=cabc x=80 y=200
    # @title: Cell 2
    print(2 + 2)

Rules:
  - First non-blank line MAY be `# doodlecode format-version: N`. If
    missing we default to 1 and try our best (v1 didn't write the
    header until v2).
  - `# %%` opens a new cell. The rest of the line is `key=value`
    pairs (whitespace-separated). Unknown keys are ignored.
  - Directive lines (`# @key: value`) consumed until the first
    non-directive line. After that, every line is part of the cell
    source.
  - v4: a source line that itself looks like a `# %%` marker is escaped
    (`# %\\%`) on write and un-escaped on read, so a cell body can safely
    contain Jupyter-style markers or explain this format. Single-line
    directive values (`@reveal`/`@note`/`@explain`) escape backslashes
    before newlines so a literal `\\n` survives the round-trip.

Backward-compat: a plain `.py` with just `# %%` separators (no
key=value, no directives) still loads — every cell becomes a code
cell at (0,0) with no title.
"""
from __future__ import annotations

import re
from typing import Iterable

from .models import FILE_FORMAT_VERSION, CalloutPayload, CellPayload, NotebookPayload

_HEADER_RE = re.compile(r"^\s*#\s*doodlecode\s+format-version:\s*(\d+)\s*$")
_NB_NAME_RE = re.compile(r"^\s*#\s*notebook:\s*(.+?)\s*$")
_CELL_RE = re.compile(r"^\s*#\s*%%\s*(.*)$")
_DIRECTIVE_RE = re.compile(r"^\s*#\s*@(\w+)\s*:\s*(.*)$")
_KV_RE = re.compile(r"(\w+)=(?:\"([^\"]*)\"|(\S+))")


def _escape_inline(s: str) -> str:
    """v4: escape backslashes *before* newlines so a literal ``\\n`` in the
    value survives the round-trip. Without the backslash escape, a reveal
    of ``print("a\\nb")`` (two chars: backslash, n) decoded back to a real
    newline and split the string — see iter 198."""
    return s.replace("\\", "\\\\").replace("\n", "\\n")


def _unescape_inline(s: str) -> str:
    """v4 inverse of :func:`_escape_inline`. A single left-to-right pass so
    ``\\\\n`` (escaped backslash + literal ``n``) is NOT read as a newline."""
    out: list[str] = []
    k = 0
    while k < len(s):
        if s[k] == "\\" and k + 1 < len(s):
            nxt = s[k + 1]
            if nxt == "n":
                out.append("\n")
                k += 2
                continue
            if nxt == "\\":
                out.append("\\")
                k += 2
                continue
        out.append(s[k])
        k += 1
    return "".join(out)


_BODY_MARKER_RE = re.compile(r"^(\s*#\s*%)(\\*)(%)")


def _escape_body_line(line: str) -> str:
    """v4: a body line that would be re-read as a cell marker (``# %%``)
    gets a backslash inserted before the closing ``%`` so it no longer
    matches ``_CELL_RE``. Stacks on already-escaped lines so the transform
    stays reversible (``# %%`` → ``# %\\%`` → ``# %\\\\%`` …). Without this a
    code cell whose body contains ``# %%`` — e.g. a Jupyter cell marker or
    a tutorial about this very format — split into two cells on load."""
    m = _BODY_MARKER_RE.match(line)
    if m:
        return line[: m.start(3)] + "\\" + line[m.start(3) :]
    return line


def _unescape_body_line(line: str) -> str:
    """v4 inverse of :func:`_escape_body_line` — removes one backslash from
    an escaped marker line. No-op for ordinary lines."""
    m = _BODY_MARKER_RE.match(line)
    if m and m.group(2):
        return line[: m.start(2)] + m.group(2)[:-1] + line[m.start(3) :]
    return line


def _legacy_unescape(s: str) -> str:
    """Pre-v4 decoder: turns every ``\\n`` into a newline. Lossy for values
    that contained a literal backslash-n, but kept verbatim so files
    written by older versions parse exactly as they did then."""
    return s.replace("\\n", "\n")


def serialize(nb: NotebookPayload) -> str:
    out: list[str] = [
        f"# doodlecode format-version: {FILE_FORMAT_VERSION}",
        f"# notebook: {nb.name}",
        "",
    ]
    for c in nb.cells:
        parts = [f"kind={c.kind}", f"id={c.id}", f"x={c.x:.1f}", f"y={c.y:.1f}"]
        if c.w is not None:
            parts.append(f"w={c.w:.1f}")
        if c.h is not None:
            parts.append(f"h={c.h:.1f}")
        out.append(f"# %% {' '.join(parts)}")
        if c.title:
            out.append(f"# @title: {c.title}")
        if c.diagram_kind:
            out.append(f"# @diagram_kind: {c.diagram_kind}")
        # Iter 224: Animation cell transition style. Single token, no
        # escaping needed; emitted only when set.
        if c.transition:
            out.append(f"# @transition: {c.transition}")
        # Iter 45: cell→cell links emit one directive per target.
        for target in c.links:
            out.append(f"# @link_to: {target}")
        # Iter 54: collapsed-to-title UI state. Emit only when True so
        # newly-created files don't grow a noisy `# @collapsed: false`.
        if c.collapsed:
            out.append("# @collapsed: true")
        # Iter 157: reveal steps — one directive per fragment, newlines
        # escaped so each step stays on one line (same scheme as
        # `# @explain:`). Order is preserved on parse.
        for step in c.reveals:
            out.append(f"# @reveal: {_escape_inline(step)}")
        # Iter 165: presenter speaker note (newlines escaped). Emitted
        # only when present so clean files don't grow an empty note.
        if c.note:
            out.append(f"# @note: {_escape_inline(c.note)}")
        # Callouts. The first one needs no marker (writes
        # `# @explain:` / `# @image:` straight into the directive
        # block). Subsequent ones are introduced by `# @callout`.
        for idx, co in enumerate(c.callouts):
            if idx > 0:
                out.append("# @callout")
            if co.text:
                out.append(f"# @explain: {_escape_inline(co.text)}")
            if co.image:
                out.append(f"# @image: {co.image}")
        # Blank line after directives, before body, so manual readers
        # can tell where the source starts.
        if c.source:
            out.append("")
            # Escape any body line that would be re-read as a `# %%` cell
            # marker so the source can't be split across cells on load.
            body = "\n".join(_escape_body_line(ln) for ln in c.source.rstrip("\n").split("\n"))
            out.append(body)
        out.append("")  # gap between cells
    return "\n".join(out).rstrip() + "\n"


def _parse_kv(s: str) -> dict[str, str]:
    out: dict[str, str] = {}
    for m in _KV_RE.finditer(s):
        out[m.group(1)] = m.group(2) if m.group(2) is not None else m.group(3)
    return out


def parse(text: str) -> tuple[NotebookPayload, int]:
    """Returns (notebook, detected_format_version)."""
    lines = text.split("\n")
    version = 1
    name = "Untitled"
    cells: list[CellPayload] = []

    i = 0
    # Header block (before first `# %%`).
    while i < len(lines):
        line = lines[i]
        if _CELL_RE.match(line):
            break
        m = _HEADER_RE.match(line)
        if m:
            version = int(m.group(1))
        else:
            n = _NB_NAME_RE.match(line)
            if n:
                name = n.group(1).strip()
        i += 1

    # Iter 198: pick the inline decoder by format version. v4+ files were
    # written with backslash escaping, so a literal `\n` in the value
    # survives; v1–v3 files used the lossy legacy scheme and must decode
    # exactly as they did when written.
    unescape = _unescape_inline if version >= 4 else _legacy_unescape

    # Cells.
    while i < len(lines):
        cm = _CELL_RE.match(lines[i])
        if not cm:
            i += 1
            continue
        attrs = _parse_kv(cm.group(1))
        i += 1
        # Directive block.
        title: str | None = None
        diagram_kind: str | None = None
        links: list[str] = []
        collapsed: bool = False
        reveals: list[str] = []
        note: str | None = None
        transition: str | None = None
        callouts: list[CalloutPayload] = []
        # `current` points at the callout being edited. Starts implicit
        # at index 0 so an `# @explain:` before any `# @callout` marker
        # populates the first bubble (v1 backward-compat).
        def ensure_current() -> CalloutPayload:
            if not callouts:
                callouts.append(CalloutPayload())
            return callouts[-1]

        while i < len(lines):
            line = lines[i]
            if _CELL_RE.match(line):
                break
            # `# @callout` (no value) starts a fresh bubble. Treated as
            # a directive even though it has no body — the directive
            # regex requires `:` so we handle it specially first.
            if re.match(r"^\s*#\s*@callout\s*$", line):
                callouts.append(CalloutPayload())
                i += 1
                continue
            dm = _DIRECTIVE_RE.match(line)
            if not dm:
                break
            key, val = dm.group(1), dm.group(2)
            if key == "title":
                title = val.strip()
            elif key == "diagram_kind":
                diagram_kind = val.strip()
            elif key == "explain":
                ensure_current().text = unescape(val).strip()
            elif key == "image":
                ensure_current().image = val.strip()
            elif key == "link_to":
                t = val.strip()
                if t:
                    links.append(t)
            elif key == "collapsed":
                collapsed = val.strip().lower() in ("true", "1", "yes")
            elif key == "reveal":
                # Iter 157: un-escape newlines; keep order. Don't strip —
                # leading/trailing whitespace inside a fragment matters
                # for indentation. (The directive regex already ate the
                # single space after the colon.)
                reveals.append(unescape(val))
            elif key == "note":
                # Iter 165: presenter speaker note (un-escape newlines).
                note = unescape(val)
            elif key == "transition":
                # Iter 224: Animation cell transition style.
                transition = val.strip() or None
            # Unknown directives silently ignored — keeps forward-compat.
            i += 1

        # Backward-compat: nothing emitted via `@callout` yet — keep
        # the legacy single-string field populated for the frontend
        # migration shim. New files use `callouts` exclusively.
        explain = callouts[0].text if callouts and not callouts[0].image else None

        # Source body until the next `# %%` or EOF. v4+ un-escapes any
        # body line that was escaped to avoid colliding with the marker.
        body_lines: list[str] = []
        while i < len(lines) and not _CELL_RE.match(lines[i]):
            line = lines[i]
            body_lines.append(_unescape_body_line(line) if version >= 4 else line)
            i += 1

        raw_kind = attrs.get("kind") or "code"
        kind = raw_kind if raw_kind in ("code", "markdown", "media", "browser", "whiteboard", "diagram", "animation") else "code"
        w = float(attrs["w"]) if "w" in attrs else None
        h = float(attrs["h"]) if "h" in attrs else None
        cells.append(
            CellPayload(
                id=attrs.get("id") or f"c{len(cells)}",
                kind=kind,  # unknown kinds fall back to "code" for fwd-compat
                source=_dedent_body(body_lines),
                title=title,
                x=float(attrs.get("x") or 0),
                y=float(attrs.get("y") or 0),
                w=w,
                h=h,
                diagram_kind=diagram_kind,
                explain=explain,
                callouts=callouts,
                links=links,
                collapsed=collapsed,
                reveals=reveals,
                note=note,
                transition=transition,
            )
        )

    return NotebookPayload(name=name, cells=cells), version


def _dedent_body(lines: Iterable[str]) -> str:
    """Strip leading/trailing blank lines from the cell body."""
    arr = list(lines)
    while arr and not arr[0].strip():
        arr.pop(0)
    while arr and not arr[-1].strip():
        arr.pop()
    return "\n".join(arr)
