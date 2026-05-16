"""Serializer + round-trip tests. The format is the project's contract,
so every example file must round-trip byte-stable on meaningful fields."""
from __future__ import annotations

import json
from pathlib import Path

import pytest

from app.models import CalloutBlock, Cell, CellMeta, Notebook
from app.notebook import from_py
from app.serialize import serialize_notebook

EXAMPLES = Path(__file__).resolve().parent.parent.parent / "examples"


def test_preamble_header_emitted():
    nb = Notebook(name="x.py", cells=[Cell(id="1", kind="code", source="x = 1\n")])
    text = serialize_notebook(nb)
    assert text.splitlines()[0].startswith("# doodlecode format-version:")


def test_markdown_round_trip():
    nb = Notebook(
        name="x.py",
        cells=[Cell(id="1", kind="markdown", source="# Heading\n\nBody.")],
    )
    text = serialize_notebook(nb)
    parsed = from_py("x.py", text.encode())
    assert parsed.cells[0].kind == "markdown"
    assert parsed.cells[0].source == "# Heading\n\nBody."


def test_simple_callout_round_trip():
    nb = Notebook(name="x.py", cells=[
        Cell(id="1", kind="code", source="def f(): pass\n",
             meta=CellMeta(kind="function", color="mint", title="Demo",
                            explain="Short body.", tags=["a", "b"])),
    ])
    text = serialize_notebook(nb)
    parsed = from_py("x.py", text.encode())
    m = parsed.cells[0].meta
    assert m.kind == "function"
    assert m.color == "mint"
    assert m.title == "Demo"
    assert m.explain == "Short body."
    assert m.tags == ["a", "b"]


def test_quoted_title_with_spaces_round_trip():
    nb = Notebook(name="x.py", cells=[
        Cell(id="1", kind="code", source="x = 1\n",
             meta=CellMeta(title="A long title with spaces", color="sky")),
    ])
    text = serialize_notebook(nb)
    assert 'title="A long title with spaces"' in text
    parsed = from_py("x.py", text.encode())
    assert parsed.cells[0].meta.title == "A long title with spaces"


def test_multiline_explain_splits_into_multiple_directives():
    """Newlines in explain become separate `# @explain:` lines, which
    the parser rejoins with single spaces (lossy on newlines, exact
    on internal multi-space runs)."""
    nb = Notebook(name="x.py", cells=[
        Cell(id="1", kind="code", source="x = 1\n",
             meta=CellMeta(title="t", explain="first line\nsecond line")),
    ])
    text = serialize_notebook(nb)
    explain_lines = [ln for ln in text.splitlines() if ln.startswith("# @explain:")]
    assert len(explain_lines) == 2


def test_internal_multispace_survives_round_trip():
    """A title body with column-aligned spaces (common in tutorials)
    must survive serialize -> parse byte-stable."""
    explain = "fit(X, y)         -> train\npredict(X)        -> infer"
    nb = Notebook(name="x.py", cells=[
        Cell(id="1", kind="code", source="x = 1\n",
             meta=CellMeta(title="t", explain=explain)),
    ])
    text = serialize_notebook(nb)
    parsed = from_py("x.py", text.encode())
    # parser joins on " " so the only loss is newline -> space
    assert parsed.cells[0].meta.explain == explain.replace("\n", " ")


def test_unicode_title_round_trip():
    """Em-dash and superscript chars must not be mangled by quoting."""
    nb = Notebook(name="x.py", cells=[
        Cell(id="1", kind="code", source="x = 1\n",
             meta=CellMeta(title="Metrics — MSE, MAE, R²", color="mint")),
    ])
    text = serialize_notebook(nb)
    parsed = from_py("x.py", text.encode())
    assert parsed.cells[0].meta.title == "Metrics — MSE, MAE, R²"


def test_extra_callouts_round_trip():
    primary = CellMeta(
        title="Main", color="mint", kind="function", explain="primary",
        callouts=[
            CalloutBlock(title="Aside", color="peach", explain="second"),
            CalloutBlock(title="Note", color="lavender", explain="third"),
        ],
    )
    nb = Notebook(name="x.py", cells=[
        Cell(id="1", kind="code", source="print(1)\n", meta=primary),
    ])
    text = serialize_notebook(nb)
    parsed = from_py("x.py", text.encode())
    m = parsed.cells[0].meta
    assert m.title == "Main" and m.color == "mint"
    assert [c.title for c in m.callouts] == ["Aside", "Note"]
    assert [c.color for c in m.callouts] == ["peach", "lavender"]


def test_image_data_url_round_trip():
    img = "data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAQAAAC1HAwCAAAAC0lEQVR42mNkYAAAAAYAAjCB0C8AAAAASUVORK5CYII="
    nb = Notebook(name="x.py", cells=[
        Cell(id="1", kind="code", source="x = 1\n",
             meta=CellMeta(title="t", explain="body", image=img,
                            callouts=[CalloutBlock(title="b", image=img, explain="x")])),
    ])
    text = serialize_notebook(nb)
    parsed = from_py("x.py", text.encode())
    assert parsed.cells[0].meta.image == img
    assert parsed.cells[0].meta.callouts[0].image == img


@pytest.mark.parametrize("path", sorted(EXAMPLES.glob("*.py")))
def test_every_example_round_trips_stable(path: Path):
    """Source bodies and meta objects survive serialize → parse exactly."""
    nb = from_py(path.name, path.read_bytes())
    text = serialize_notebook(nb)
    again = from_py(path.name, text.encode())
    assert len(nb.cells) == len(again.cells), f"cell count drift in {path.name}"
    for a, b in zip(nb.cells, again.cells):
        assert a.kind == b.kind
        assert a.source.rstrip() == b.source.rstrip()
        assert _meta_eq(a.meta, b.meta), f"meta drift in {path.name}"


def _meta_eq(a, b):
    if a is None and b is None:
        return True
    if a is None or b is None:
        return False
    return json.dumps(a.model_dump(), sort_keys=True) == json.dumps(b.model_dump(), sort_keys=True)
