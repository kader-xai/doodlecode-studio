"""Pydantic models shared across endpoints.

v2 keeps these in one place so the frontend's `types.ts` mirrors the
backend exactly. Round-trip discipline: every field that crosses the
wire shows up here first.
"""
from __future__ import annotations

from typing import Literal, Optional

from pydantic import BaseModel, Field

# Bump whenever a new directive or field is added. Reader stays
# backward-compatible — old files keep parsing as long as the
# directives they use still exist.
FILE_FORMAT_VERSION = 3


class ExecuteRequest(BaseModel):
    source: str = Field(..., description="Python source to execute")
    timeout_s: float = Field(15.0, ge=0.1, le=120.0)


class ExecuteOutput(BaseModel):
    """One output chunk returned by the executor.

    For text streams the payload is in `text`. For `image_png` the
    `text` field holds the base64-encoded PNG bytes (no `data:`
    prefix — the frontend wraps it for the `<img src>`).
    """

    type: Literal["stdout", "stderr", "error", "done", "image_png"]
    text: str = ""


class ExecuteResponse(BaseModel):
    status: Literal["ok", "error", "timeout"]
    elapsed_ms: int
    outputs: list[ExecuteOutput]


# ─── Notebook serialization ────────────────────────────────────────

CellKind = Literal["code", "markdown", "media", "browser", "whiteboard", "diagram"]


class CalloutPayload(BaseModel):
    """One speech-bubble. Image is an optional data URL (under ~1.5 MB)."""
    text: str = ""
    image: Optional[str] = None


class CellPayload(BaseModel):
    """One cell as it crosses the wire. Mirrors `types.ts:Cell`."""
    id: str
    kind: CellKind
    source: str
    title: Optional[str] = None
    x: float = 0
    y: float = 0
    # Optional explicit size. None means "use the cell-type default".
    # Persisted in .py so reload restores user-resized cards.
    w: Optional[float] = None
    h: Optional[float] = None
    # Diagram subtype: "mermaid" today; later "math" / "chart". Kept
    # generic so non-diagram cells leave it as None.
    diagram_kind: Optional[str] = None
    # **Deprecated** single-callout field kept for backward-compat with
    # files saved in iter 13. New code writes `callouts` instead and the
    # parser migrates `explain` into `callouts[0]` automatically.
    explain: Optional[str] = None
    # Zero or more speech-bubbles displayed beside the cell, top-to-
    # bottom. Persisted via `# @callout` separator directives.
    callouts: list[CalloutPayload] = []


class NotebookPayload(BaseModel):
    name: str = "Untitled"
    cells: list[CellPayload] = []


class SaveRequest(BaseModel):
    notebook: NotebookPayload


class SaveResponse(BaseModel):
    text: str
    """Serialized .py text. Frontend triggers the download."""
    format_version: int = FILE_FORMAT_VERSION


class OpenRequest(BaseModel):
    text: str


class OpenResponse(BaseModel):
    notebook: NotebookPayload
    format_version: int
