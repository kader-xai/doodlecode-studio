"""Tests for the `doodle` data→chart-syntax kernel helper (iter 173)."""
from app import doodle_helper as d


def test_bar_from_dict_with_title():
    out = d.bar({"Python": 8, "Rust": 4}, title="LOC")
    assert out == "chart: LOC\nPython: 8\nRust: 4"


def test_bar_without_title_and_from_pairs():
    out = d.bar([("A", 1), ("B", 2)])
    assert out == "A: 1\nB: 2"


def test_num_keeps_ints_and_trims_floats():
    assert d.bar({"x": 3.0}) == "x: 3"
    assert d.bar({"x": 0.5}) == "x: 0.5"


def test_line_multi_series_with_axes():
    out = d.line({"Train": [0.9, 0.6], "Val": [1.0, 0.7]},
                 title="Loss", xlabel="Epoch", ylabel="Loss")
    assert out == (
        "chart: Loss\nxlabel: Epoch\nylabel: Loss\n"
        "line Train: 0.9, 0.6\nline Val: 1, 0.7"
    )


def test_line_single_sequence():
    assert d.line([1, 2, 3]) == "line Series: 1, 2, 3"


def test_area_uses_area_keyword():
    assert d.area({"Users": [2, 5, 9]}) == "area Users: 2, 5, 9"


def test_pie_drops_non_positive():
    out = d.pie({"Yes": 60, "No": 40, "Maybe": 0}, title="Vote")
    assert out == "pie: Vote\npie Yes: 60\npie No: 40"


def test_scatter_emits_points_with_axes():
    out = d.scatter([(1, 2), (3, 4.5)], title="XY", xlabel="w", ylabel="h")
    assert out == "scatter: XY\nxlabel: w\nylabel: h\npoint: 1, 2\npoint: 3, 4.5"


def test_flow_edges():
    assert d.flow([("A", "B"), ("B", "C")]) == "A --> B\nB --> C"


def test_output_round_trips_through_the_chart_parser_shape():
    # The strings must use exactly the tokens the frontend parser keys
    # on; assert the leading keywords are present and well-formed.
    assert d.bar({"a": 1}, "t").startswith("chart: t")
    assert "line " in d.line({"s": [1]})
    assert "area " in d.area({"s": [1]})
    assert d.pie({"a": 1}, "t").startswith("pie: t")
    assert "pie a:" in d.pie({"a": 1})
    assert d.scatter([(1, 2)], "t").startswith("scatter: t")
    assert "point: 1, 2" in d.scatter([(1, 2)])
    assert "-->" in d.flow([("a", "b")])
