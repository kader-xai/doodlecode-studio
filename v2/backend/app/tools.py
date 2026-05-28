"""PPT → PNG conversion.

Two-step pipeline:
  1. `soffice --headless --convert-to pdf` (LibreOffice) turns the
     uploaded .pptx into a temporary .pdf.
  2. `pdftoppm -png -r 110` (poppler) writes one PNG per page into
     a temp directory.

Both tools are checked at request time; missing binaries return a
friendly 503 with install hints rather than a stack trace.

We do this inside a `TemporaryDirectory` so the host filesystem
never accumulates artifacts even if a conversion fails partway.
"""
from __future__ import annotations

import base64
import shutil
import subprocess
import tempfile
from pathlib import Path
from typing import List

from fastapi import HTTPException, UploadFile
from pydantic import BaseModel


_ALLOWED_EXT = {".ppt", ".pptx", ".odp", ".key"}
_MAX_BYTES = 50 * 1024 * 1024  # 50 MB cap


def _which(*names: str) -> str | None:
    for n in names:
        p = shutil.which(n)
        if p:
            return p
    return None


class PptToPngResponse(BaseModel):
    ok: bool
    pages: int
    images_b64: List[str]
    note: str = ""


async def ppt_to_png(file: UploadFile) -> PptToPngResponse:
    name = file.filename or "upload"
    ext = Path(name).suffix.lower()
    if ext not in _ALLOWED_EXT:
        raise HTTPException(
            400,
            f"Unsupported file type {ext}. Upload .ppt / .pptx / .odp / .key.",
        )

    soffice = _which("soffice", "libreoffice")
    pdftoppm = _which("pdftoppm")
    missing = []
    if not soffice:   missing.append("LibreOffice (soffice)")
    if not pdftoppm:  missing.append("pdftoppm (poppler-utils)")
    if missing:
        raise HTTPException(
            503,
            "Server missing required binaries: "
            + ", ".join(missing)
            + ". On macOS: `brew install libreoffice poppler`. "
            + "On Ubuntu: `sudo apt install libreoffice poppler-utils`.",
        )

    data = await file.read()
    if len(data) > _MAX_BYTES:
        raise HTTPException(413, f"File too large ({len(data) // 1024} KB > {_MAX_BYTES // 1024} KB)")
    if not data:
        raise HTTPException(400, "Empty file")

    with tempfile.TemporaryDirectory() as tmp_s:
        tmp = Path(tmp_s)
        src = tmp / f"in{ext}"
        src.write_bytes(data)

        # Step 1: LibreOffice → PDF.
        try:
            r = subprocess.run(
                [soffice, "--headless", "--convert-to", "pdf",
                 "--outdir", str(tmp), str(src)],
                capture_output=True, text=True, timeout=180,
            )
        except subprocess.TimeoutExpired:
            raise HTTPException(504, "LibreOffice timed out converting to PDF.")
        if r.returncode != 0:
            raise HTTPException(
                500,
                f"LibreOffice conversion failed:\n{(r.stderr or r.stdout or '').strip()[:1000]}",
            )

        pdf = next(tmp.glob("*.pdf"), None)
        if pdf is None:
            raise HTTPException(500, "LibreOffice produced no PDF.")

        # Step 2: pdftoppm → one PNG per page.
        out_prefix = tmp / "slide"
        try:
            r2 = subprocess.run(
                [pdftoppm, "-png", "-r", "110", str(pdf), str(out_prefix)],
                capture_output=True, text=True, timeout=120,
            )
        except subprocess.TimeoutExpired:
            raise HTTPException(504, "pdftoppm timed out.")
        if r2.returncode != 0:
            raise HTTPException(
                500,
                f"pdftoppm failed:\n{(r2.stderr or r2.stdout or '').strip()[:1000]}",
            )

        pngs = sorted(tmp.glob("slide-*.png"))
        images = [base64.b64encode(p.read_bytes()).decode("ascii") for p in pngs]

    return PptToPngResponse(
        ok=True,
        pages=len(images),
        images_b64=images,
        note=f"Converted {len(images)} slide(s) from {name}.",
    )
