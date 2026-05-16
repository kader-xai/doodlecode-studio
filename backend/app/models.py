from __future__ import annotations

from typing import Any, Literal, Optional

from pydantic import BaseModel, Field

# File-format version. Bump on breaking changes.
# v1: single per-cell callout via `# @explain:` directives.
# v2: multiple callouts via `# @callout` separator + `# @image:`
#     attachment. v2 readers handle v1 files transparently.
FILE_FORMAT_VERSION = 2


class CalloutBlock(BaseModel):
    """One bubble on the right column. A cell may have one or more."""
    title: Optional[str] = None
    explain: Optional[str] = None
    color: Optional[str] = None
    kind: Optional[str] = None
    image: Optional[str] = None  # data URL or path
    tags: list[str] = Field(default_factory=list)


class CellMeta(BaseModel):
    """Cell-level metadata. Backward compatible with v1:
    `kind/color/title/explain/tags` describe the FIRST callout.
    Additional callouts live in `callouts` (without the first one)."""
    # Legacy v1 fields — always populated for the primary callout.
    kind: Optional[str] = None
    color: Optional[str] = None
    title: Optional[str] = None
    explain: Optional[str] = None
    tags: list[str] = Field(default_factory=list)
    # v2 fields:
    image: Optional[str] = None
    callouts: list[CalloutBlock] = Field(default_factory=list)


class Cell(BaseModel):
    id: str
    kind: Literal["code", "markdown"] = "code"
    source: str = ""
    meta: Optional[CellMeta] = None


class Notebook(BaseModel):
    name: str
    cells: list[Cell] = Field(default_factory=list)
    format_version: int = FILE_FORMAT_VERSION


class ExecuteRequest(BaseModel):
    code: str
    session_id: str = "default"


class ExecuteOutput(BaseModel):
    type: Literal["stream", "result", "error", "display"]
    name: Optional[str] = None
    text: Optional[str] = None
    data: Optional[dict[str, Any]] = None
    ename: Optional[str] = None
    evalue: Optional[str] = None
    traceback: Optional[list[str]] = None


class ExecuteResponse(BaseModel):
    outputs: list[ExecuteOutput]
    status: Literal["ok", "error", "aborted"]
    execution_count: Optional[int] = None


class CodeBlock(BaseModel):
    id: str
    start_line: int
    end_line: int
    kind: str
    name: Optional[str] = None
    summary: str = ""


class ExplainRequest(BaseModel):
    code: str
    mode: Literal["child", "beginner", "engineer", "researcher", "presenter"] = "beginner"
    meta: Optional[CellMeta] = None


class Explanation(BaseModel):
    block_id: str
    title: str
    body: str
    tags: list[str] = Field(default_factory=list)
    color: Optional[str] = None
    image: Optional[str] = None


class ExplainResponse(BaseModel):
    blocks: list[CodeBlock]
    explanations: list[Explanation]


class VersionInfo(BaseModel):
    app: str
    format_version: int


class InstallRequest(BaseModel):
    """Pip-install one or more packages into the kernel's environment.

    `packages` is the raw user input — split on whitespace, lightly
    validated. Use the same string you'd type after `pip install`.
    """
    packages: str
    upgrade: bool = False


class InstallResponse(BaseModel):
    ok: bool
    packages: list[str]
    stdout: str
    stderr: str
    returncode: int
