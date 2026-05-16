"""explain_code is the contract for the right-side callout column."""
from __future__ import annotations

from app.explain import KIND_COLOR, explain_code
from app.models import CalloutBlock, CellMeta


def test_no_meta_yields_no_explanations():
    """Per CLAUDE.md rule 1: never auto-generate AI commentary."""
    r = explain_code("print('hi')", meta=None)
    assert r.explanations == []


def test_meta_without_title_or_explain_yields_no_explanations():
    r = explain_code("x = 1", meta=CellMeta(kind="assign", color="peach"))
    assert r.explanations == []


def test_primary_callout_emitted():
    r = explain_code(
        "x = 1",
        meta=CellMeta(kind="assign", color="peach", title="Set x", explain="One."),
    )
    assert len(r.explanations) == 1
    e = r.explanations[0]
    assert e.title == "Set x"
    assert e.body == "One."
    assert e.color == "peach"
    assert e.tags == ["assign"]


def test_extra_callouts_emitted():
    r = explain_code(
        "x = 1",
        meta=CellMeta(
            title="Main", color="mint", explain="primary",
            callouts=[
                CalloutBlock(title="Aside", color="rose", explain="aside body"),
                CalloutBlock(title="Note", color="violet", explain="another"),
            ],
        ),
    )
    assert [e.title for e in r.explanations] == ["Main", "Aside", "Note"]
    assert [e.color for e in r.explanations] == ["mint", "rose", "violet"]


def test_color_falls_back_to_kind_default():
    r = explain_code(
        "x = 1",
        meta=CellMeta(title="t", explain="body", kind="function"),  # no color
    )
    assert r.explanations[0].color == KIND_COLOR["function"]


def test_image_passed_through():
    img = "data:image/png;base64,AAAA"
    r = explain_code(
        "x = 1",
        meta=CellMeta(title="t", explain="body", image=img),
    )
    assert r.explanations[0].image == img
