"""Tests for the notebook → Markdown export (iter 219)."""
from app.export_md import to_markdown
from app.models import CalloutPayload, CellPayload, NotebookPayload


def _nb(*cells: CellPayload, name: str = "Deck") -> NotebookPayload:
    return NotebookPayload(name=name, cells=list(cells))


def test_title_and_markdown_passthrough():
    nb = _nb(
        CellPayload(id="m", kind="markdown", title="Intro", source="Hello **world**"),
    )
    md = to_markdown(nb)
    assert md.startswith("# Deck\n")
    assert "## Intro" in md
    assert "Hello **world**" in md


def test_code_cell_becomes_a_python_fence():
    nb = _nb(CellPayload(id="c", kind="code", source="print('hi')"))
    md = to_markdown(nb)
    assert "```python\nprint('hi')\n```" in md


def test_diagram_source_fenced_as_text():
    nb = _nb(CellPayload(id="d", kind="diagram", source="chart: X\nA: 1"))
    md = to_markdown(nb)
    assert "```text\nchart: X\nA: 1\n```" in md


def test_media_image_vs_video():
    img = _nb(CellPayload(id="i", kind="media", title="Pic", source="https://x.io/a.png"))
    vid = _nb(CellPayload(id="v", kind="media", source="https://x.io/clip.mp4?controls=1"))
    assert "![Pic](https://x.io/a.png)" in to_markdown(img)
    assert "[▶ Video](https://x.io/clip.mp4?controls=1)" in to_markdown(vid)


def test_browser_and_whiteboard():
    nb = _nb(
        CellPayload(id="b", kind="browser", source="https://example.com"),
        CellPayload(id="w", kind="whiteboard", source='{"strokes":[]}'),
    )
    md = to_markdown(nb)
    assert "[🔗 Live demo](https://example.com)" in md
    assert "_[Whiteboard sketch]_" in md


def test_callouts_become_blockquotes_notes_omitted():
    nb = _nb(
        CellPayload(
            id="c",
            kind="code",
            source="x = 1",
            callouts=[CalloutPayload(text="This assigns x.\nSecond line.")],
            note="Presenter only — should NOT appear.",
        ),
    )
    md = to_markdown(nb)
    assert "> This assigns x.\n> Second line." in md
    assert "Presenter only" not in md  # speaker notes stay private


def test_code_reveals_become_labeled_step_blocks():
    nb = _nb(
        CellPayload(
            id="c",
            kind="code",
            source="def f():",
            reveals=["    return 1", "    return 2"],
        ),
    )
    md = to_markdown(nb)
    assert "```python\ndef f():\n```" in md
    assert "*Step 1:*\n\n```python\n    return 1\n```" in md
    assert "*Step 2:*\n\n```python\n    return 2\n```" in md


def test_blank_reveals_skipped():
    nb = _nb(CellPayload(id="c", kind="code", source="x = 1", reveals=["", "   "]))
    md = to_markdown(nb)
    assert "Step" not in md


def test_callout_image_exported_with_text_alt():
    nb = _nb(
        CellPayload(
            id="c",
            kind="markdown",
            source="Body",
            callouts=[CalloutPayload(text="See the chart", image="data:image/png;base64,XYZ")],
        ),
    )
    md = to_markdown(nb)
    assert "> See the chart" in md
    assert "![See the chart](data:image/png;base64,XYZ)" in md


def test_image_only_callout_still_exports():
    nb = _nb(
        CellPayload(
            id="c",
            kind="markdown",
            source="Body",
            callouts=[CalloutPayload(text="", image="https://x.io/a.png")],
        ),
    )
    md = to_markdown(nb)
    assert "![callout](https://x.io/a.png)" in md


def test_data_url_image_detected():
    nb = _nb(CellPayload(id="i", kind="media", source="data:image/png;base64,AAAA"))
    assert "![media](data:image/png;base64,AAAA)" in to_markdown(nb)


def test_empty_notebook_just_the_title():
    assert to_markdown(NotebookPayload(name="Empty", cells=[])) == "# Empty\n"
