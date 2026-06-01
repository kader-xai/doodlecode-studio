"""Round-trip tests for the .py notebook format."""
from pathlib import Path

from app import notebook_io
from app.models import CalloutPayload, CellPayload, NotebookPayload

_EXAMPLES = Path(__file__).resolve().parents[2] / "examples"


def _roundtrip(nb: NotebookPayload) -> NotebookPayload:
    text = notebook_io.serialize(nb)
    parsed, _ = notebook_io.parse(text)
    return parsed


def test_empty_notebook():
    nb = NotebookPayload(name="Empty", cells=[])
    out = _roundtrip(nb)
    assert out.name == "Empty"
    assert out.cells == []


def test_literal_backslash_n_round_trips_in_reveal_note_callout():
    """Iter 198: a literal ``\\n`` (backslash + n) in a reveal / note /
    callout must survive — reveals are code that often contains it."""
    nb = NotebookPayload(cells=[CellPayload(
        id="c0", kind="code", x=0, y=0, source="print()",
        reveals=['print("a\\nb")', "x = 1\ny = 2"],   # literal \n, then real newline
        note='use \\n for a newline\nsecond line',
        callouts=[CalloutPayload(text='regex: \\n \\\\ \\t')],
    )])
    out = _roundtrip(nb)
    assert out.cells[0].reveals == nb.cells[0].reveals
    assert out.cells[0].note == nb.cells[0].note
    assert out.cells[0].callouts[0].text == nb.cells[0].callouts[0].text


def test_body_with_cell_marker_does_not_split(  ):
    """Iter 199: a code body containing `# %%` (a Jupyter marker, or a
    deck explaining this very format) must stay one cell, not split."""
    body = 'x = 1\n# %% not a real marker\nprint("# %% nor this")\ny = 2'
    nb = NotebookPayload(cells=[CellPayload(id="c0", kind="code", x=0, y=0, source=body)])
    out = _roundtrip(nb)
    assert len(out.cells) == 1
    assert out.cells[0].source == body


def test_body_marker_escape_is_reversible_for_literal_escaped_form():
    """A body line already shaped like the escape (`# %\\%`) round-trips
    byte-for-byte — escaping stacks and un-escaping peels one level."""
    for body in ["# %\\%", "# %\\\\%", "  # %% indented"]:
        nb = NotebookPayload(cells=[CellPayload(id="c0", kind="code", x=0, y=0, source=body)])
        out = _roundtrip(nb)
        assert len(out.cells) == 1
        assert out.cells[0].source == body


def test_serialize_stamps_format_version_4():
    nb = NotebookPayload(cells=[CellPayload(id="c0", kind="code", x=0, y=0, source="x=1")])
    assert "# doodlecode format-version: 4" in notebook_io.serialize(nb)


def test_legacy_v3_note_decodes_with_old_scheme():
    """A v3 file's ``\\n`` is a newline under the legacy decoder — old
    files must parse exactly as they did when written."""
    legacy = (
        "# doodlecode format-version: 3\n# notebook: Old\n\n"
        "# %% kind=code id=c0 x=0.0 y=0.0\n# @note: line1\\nline2\n\nprint(1)\n"
    )
    nb, ver = notebook_io.parse(legacy)
    assert ver == 3
    assert nb.cells[0].note == "line1\nline2"


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


def test_collapsed_round_trips():
    """Iter 54: cell.collapsed=True emits `# @collapsed: true` and
    parses back. Default False stays default (no directive)."""
    nb = NotebookPayload(name="C", cells=[
        CellPayload(id="a", kind="code", source="x = 1", collapsed=True),
        CellPayload(id="b", kind="code", source="y = 2"),  # default = False
    ])
    text = notebook_io.serialize(nb)
    assert "# @collapsed: true" in text
    # Only one occurrence — the default-False cell stays clean.
    assert text.count("# @collapsed") == 1

    out = _roundtrip(nb)
    assert out.cells[0].collapsed is True
    assert out.cells[1].collapsed is False


def test_old_files_without_collapsed_default_false():
    text = (
        "# doodlecode format-version: 3\n"
        "# notebook: Old\n"
        "\n"
        "# %% kind=code id=c0 x=0 y=0\n"
        "\n"
        "x = 1\n"
    )
    nb, _ = notebook_io.parse(text)
    assert nb.cells[0].collapsed is False


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


def test_reveals_round_trip():
    """Iter 157: reveal steps survive serialize → parse, in order,
    with newlines preserved."""
    nb = NotebookPayload(name="R", cells=[
        CellPayload(
            id="c0", kind="code", source="import math",
            x=0, y=0,
            reveals=[
                "def sigmoid(x):\n    return 1 / (1 + math.exp(-x))",
                "print(sigmoid(0))",
            ],
        ),
    ])
    out = _roundtrip(nb)
    assert out.cells[0].reveals == [
        "def sigmoid(x):\n    return 1 / (1 + math.exp(-x))",
        "print(sigmoid(0))",
    ]
    # Base source is untouched by the reveal round-trip.
    assert out.cells[0].source == "import math"


def test_old_files_without_reveal_default_empty():
    text = (
        "# doodlecode format-version: 3\n"
        "# notebook: T\n"
        "\n"
        "# %% kind=code id=c0 x=0 y=0\n"
        "\n"
        "x = 1\n"
    )
    nb, _ = notebook_io.parse(text)
    assert nb.cells[0].reveals == []


def test_note_round_trips():
    """Iter 165: presenter speaker note survives serialize → parse
    with newlines preserved, and is omitted when empty."""
    nb = NotebookPayload(name="N", cells=[
        CellPayload(id="c0", kind="markdown", source="# Slide", x=0, y=0,
                    note="Mention the benchmark here.\nThen pause."),
        CellPayload(id="c1", kind="code", source="x=1", x=0, y=200),
    ])
    out = _roundtrip(nb)
    assert out.cells[0].note == "Mention the benchmark here.\nThen pause."
    assert out.cells[1].note is None  # omitted, not empty string


def test_animation_cell_round_trips():
    """Iter 224: animation cell kind + transition style + frames (in
    source, one per line) survive serialize → parse."""
    nb = NotebookPayload(name="N", cells=[
        CellPayload(
            id="a0", kind="animation", x=0, y=0,
            title="How a request flows",
            transition="fade",
            source="Client sends request\nServer validates\nDB returns rows",
        ),
    ])
    out = _roundtrip(nb)
    cell = out.cells[0]
    assert cell.kind == "animation"
    assert cell.transition == "fade"
    assert cell.source.split("\n") == [
        "Client sends request", "Server validates", "DB returns rows",
    ]


def test_transition_omitted_when_unset():
    nb = NotebookPayload(name="N", cells=[
        CellPayload(id="c0", kind="code", source="x=1", x=0, y=0),
    ])
    text = notebook_io.serialize(nb)
    assert "@transition" not in text
    assert _roundtrip(nb).cells[0].transition is None


def test_old_files_without_note_default_none():
    text = (
        "# doodlecode format-version: 3\n"
        "# notebook: T\n"
        "\n"
        "# %% kind=code id=c0 x=0 y=0\n"
        "\n"
        "x = 1\n"
    )
    nb, _ = notebook_io.parse(text)
    assert nb.cells[0].note is None


# ── Example decks double as regression fixtures ─────────────────────


def test_data_viz_demo_parses_and_round_trips():
    """The shipped data-viz demo must keep parsing and round-tripping —
    it's the canonical fixture for the v2.6.0 chart + notes suite."""
    src = (_EXAMPLES / "data_viz_demo.py").read_text()
    nb, ver = notebook_io.parse(src)
    assert ver == 3
    assert len(nb.cells) == 9

    # Every diagram cell carries a speaker note; the code cell has reveals.
    diagrams = [c for c in nb.cells if c.kind == "diagram"]
    assert len(diagrams) == 6
    assert all(c.note for c in diagrams)
    code = [c for c in nb.cells if c.kind == "code"]
    assert len(code) == 1 and len(code[0].reveals) == 2

    # Coverage: bar, line (+ axis titles + target line), area, pie, scatter,
    # stacked bar.
    blob = "\n".join(c.source for c in diagrams)
    assert "chart:" in blob          # bar / line / area titles
    assert "line " in blob           # line series
    assert "area " in blob           # area series
    assert "hline " in blob          # reference / target line
    assert "xlabel:" in blob and "ylabel:" in blob  # axis titles
    assert "pie " in blob            # pie slices
    assert "point:" in blob          # scatter points
    assert "stack " in blob and "series:" in blob  # stacked bar + legend

    # Exact round-trip of the format-stable fields.
    nb2, _ = notebook_io.parse(notebook_io.serialize(nb))
    for a, b in zip(nb.cells, nb2.cells):
        assert (a.id, a.kind, a.title, a.note, a.reveals, a.source) == (
            b.id, b.kind, b.title, b.note, b.reveals, b.source
        )


def test_markdown_showcase_parses_and_round_trips():
    """Iter 217: the markdown showcase deck is living documentation for the
    text-cell dialect — it must keep parsing (as format v4) and exercise
    every block construct, with an exact round-trip including the fenced
    code body (which contains `# `-comment lines and `**` markup)."""
    src = (_EXAMPLES / "markdown_showcase.py").read_text()
    nb, ver = notebook_io.parse(src)
    assert ver == 4
    assert len(nb.cells) == 5
    assert all(c.kind == "markdown" for c in nb.cells)
    assert all(c.title for c in nb.cells)

    blob = "\n".join(c.source for c in nb.cells)
    assert "~~struck-through~~" in blob          # strikethrough
    assert "https://github.com" in blob          # bare-URL autolink
    assert "- [x]" in blob and "- [ ]" in blob    # task list
    assert "| Feature" in blob and ":------:" in blob  # table + alignment
    assert "```python" in blob                    # fenced code block

    # Exact round-trip — the fenced `def greet` body and `# @`-looking
    # comment lines must survive byte-for-byte (format-v4 escaping).
    nb2, _ = notebook_io.parse(notebook_io.serialize(nb))
    for a, b in zip(nb.cells, nb2.cells):
        assert (a.id, a.kind, a.title, a.note, a.source) == (
            b.id, b.kind, b.title, b.note, b.source
        )


def test_animation_showcase_parses_and_round_trips():
    """Iter 228: the animation showcase deck is living documentation for the
    `kind=animation` cell — it must parse (format v4), carry frames in the
    body and the transition style as `# @transition:`, and round-trip the
    format-stable fields exactly."""
    src = (_EXAMPLES / "animation_showcase.py").read_text()
    nb, ver = notebook_io.parse(src)
    assert ver == 4

    anims = [c for c in nb.cells if c.kind == "animation"]
    assert len(anims) == 3
    # Every transition style the showcase advertises is present.
    assert {c.transition for c in anims} == {"fade", "draw-on", "pop"}
    # Frames live in the body, one per line — the first cell has 5.
    first = next(c for c in anims if c.transition == "fade")
    assert len(first.source.split("\n")) == 5

    nb2, _ = notebook_io.parse(notebook_io.serialize(nb))
    for a, b in zip(nb.cells, nb2.cells):
        assert (a.id, a.kind, a.title, a.transition, a.source) == (
            b.id, b.kind, b.title, b.transition, b.source
        )
