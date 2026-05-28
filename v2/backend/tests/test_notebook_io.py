"""Round-trip tests for the .py notebook format."""
from app import notebook_io
from app.models import CalloutPayload, CellPayload, NotebookPayload


def _roundtrip(nb: NotebookPayload) -> NotebookPayload:
    text = notebook_io.serialize(nb)
    parsed, _ = notebook_io.parse(text)
    return parsed


def test_empty_notebook():
    nb = NotebookPayload(name="Empty", cells=[])
    out = _roundtrip(nb)
    assert out.name == "Empty"
    assert out.cells == []


def test_code_cell_roundtrip():
    nb = NotebookPayload(name="X", cells=[
        CellPayload(id="c0", kind="code", source="print(1)\nprint(2)",
                    title="Hello", x=100, y=200, w=580, h=300),
    ])
    out = _roundtrip(nb)
    assert len(out.cells) == 1
    c = out.cells[0]
    assert c.id == "c0"
    assert c.kind == "code"
    assert c.source == "print(1)\nprint(2)"
    assert c.title == "Hello"
    assert c.x == 100 and c.y == 200
    assert c.w == 580 and c.h == 300


def test_diagram_kind_persists():
    nb = NotebookPayload(name="D", cells=[
        CellPayload(id="d0", kind="diagram", source="A --> B",
                    diagram_kind="doodle", x=0, y=0),
    ])
    out = _roundtrip(nb)
    assert out.cells[0].diagram_kind == "doodle"


def test_single_callout_roundtrips():
    nb = NotebookPayload(name="C", cells=[
        CellPayload(id="c0", kind="code", source="x = 1",
                    callouts=[CalloutPayload(text="explain me")]),
    ])
    out = _roundtrip(nb)
    assert len(out.cells[0].callouts) == 1
    assert out.cells[0].callouts[0].text == "explain me"


def test_multiple_callouts_roundtrip():
    nb = NotebookPayload(name="M", cells=[
        CellPayload(id="c0", kind="markdown", source="# Hi",
                    callouts=[
                        CalloutPayload(text="first"),
                        CalloutPayload(text="second", image="data:image/png;base64,iVBOR"),
                    ]),
    ])
    out = _roundtrip(nb)
    cos = out.cells[0].callouts
    assert len(cos) == 2
    assert cos[0].text == "first"
    assert cos[1].text == "second"
    assert cos[1].image == "data:image/png;base64,iVBOR"


def test_unknown_kind_falls_back_to_code():
    text = "# %% kind=quantum id=q0 x=0 y=0\nprint('hi')\n"
    nb, _ = notebook_io.parse(text)
    assert nb.cells[0].kind == "code"
    assert nb.cells[0].source.strip() == "print('hi')"


def test_legacy_explain_loads_as_callout():
    text = (
        "# %% kind=code id=c0 x=0 y=0\n"
        "# @title: T\n"
        "# @explain: legacy single callout\n"
        "\n"
        "print(1)\n"
    )
    nb, _ = notebook_io.parse(text)
    assert nb.cells[0].callouts == [CalloutPayload(text="legacy single callout")]


def test_newline_in_explain_round_trips():
    nb = NotebookPayload(name="NL", cells=[
        CellPayload(id="c0", kind="code", source="",
                    callouts=[CalloutPayload(text="line one\nline two")]),
    ])
    out = _roundtrip(nb)
    assert out.cells[0].callouts[0].text == "line one\nline two"


# ── Iter 49: cell↔cell link round-trip ─────────────────────────────


def test_links_round_trip():
    """A cell with outgoing links emits `# @link_to:` directives and
    parses back with the same list."""
    nb = NotebookPayload(name="L", cells=[
        CellPayload(id="a", kind="code",     source="x = 1", x=0,   y=0,   links=["b", "c"]),
        CellPayload(id="b", kind="markdown", source="# B",   x=200, y=0,   links=["a"]),
        CellPayload(id="c", kind="browser",  source="https://example.com", x=400, y=0),
    ])
    text = notebook_io.serialize(nb)
    # Directives appear in the serialized text.
    assert "# @link_to: b" in text
    assert "# @link_to: c" in text
    assert "# @link_to: a" in text

    out = _roundtrip(nb)
    assert out.cells[0].links == ["b", "c"]
    assert out.cells[1].links == ["a"]
    assert out.cells[2].links == []


def test_old_files_without_link_to_still_parse():
    """Iter 45 added @link_to; v3 files written before that have no
    such directive. Parser should treat missing links as empty."""
    text = (
        "# doodlecode format-version: 3\n"
        "# notebook: Legacy\n"
        "\n"
        "# %% kind=code id=c0 x=0.0 y=0.0\n"
        "# @title: Hello\n"
        "\n"
        "print('hi')\n"
    )
    nb, _ = notebook_io.parse(text)
    assert len(nb.cells) == 1
    assert nb.cells[0].id == "c0"
    assert nb.cells[0].links == []
    assert nb.cells[0].title == "Hello"


def test_empty_link_target_is_ignored():
    """A `# @link_to:` directive with no value should not add an
    empty-string entry — keeps the array clean."""
    text = (
        "# doodlecode format-version: 3\n"
        "# notebook: T\n"
        "\n"
        "# %% kind=code id=c0 x=0 y=0\n"
        "# @link_to: \n"
        "# @link_to: b\n"
        "\n"
        "x = 1\n"
    )
    nb, _ = notebook_io.parse(text)
    assert nb.cells[0].links == ["b"]
