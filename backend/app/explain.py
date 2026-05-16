"""Cell-level callout generator.

Right-side bubbles are exclusively user-authored callouts — they come
from the file as `# @explain:` / `# @title:` / `# @callout` directives.
No AST-derived blocks are returned; the canvas right column is the user.
"""
from __future__ import annotations

from typing import Optional

from .models import CellMeta, ExplainResponse, Explanation

KIND_COLOR = {
    "import": "sky",
    "function": "mint",
    "class": "pink",
    "loop": "yellow",
    "conditional": "yellow",
    "assign": "peach",
    "return": "lavender",
    "try": "rose",
    "expr": "paper",
    "context": "sky",
    "intro": "sky",
    "install": "rose",
}


def explain_code(
    code: str,
    mode: str = "beginner",
    cell_id: str = "cell",
    meta: Optional[CellMeta] = None,
) -> ExplainResponse:
    explanations: list[Explanation] = []
    if not meta:
        return ExplainResponse(blocks=[], explanations=[])

    # Primary (legacy) callout
    if meta.title or meta.explain or meta.image:
        explanations.append(Explanation(
            block_id=f"{cell_id}-callout-0",
            title=meta.title or (meta.kind.title() if meta.kind else "Note"),
            body=meta.explain or "",
            tags=meta.tags or ([meta.kind] if meta.kind else []),
            color=meta.color or KIND_COLOR.get(meta.kind or "", None),
            image=meta.image,
        ))

    # Extra callouts (v2)
    for i, c in enumerate(meta.callouts or [], start=1):
        if not (c.title or c.explain or c.image):
            continue
        explanations.append(Explanation(
            block_id=f"{cell_id}-callout-{i}",
            title=c.title or (c.kind.title() if c.kind else "Note"),
            body=c.explain or "",
            tags=c.tags or ([c.kind] if c.kind else []),
            color=c.color or KIND_COLOR.get(c.kind or "", None),
            image=c.image,
        ))

    return ExplainResponse(blocks=[], explanations=explanations)
