"""`doodle` — turn Python data into doodle-chart source.

Exposed inside every code cell's kernel as the `doodle` namespace (no
import needed). Each function returns a string in the exact mini-syntax
the frontend's `renderDoodleDiagram` understands, so a code cell can
compute numbers and `print()` chart source ready to paste into a 🖍
Doodle diagram cell:

    print(doodle.bar({"Python": 8, "Rust": 4}, title="LOC"))
    # chart: LOC
    # Python: 8
    # Rust: 4

Kept dependency-free and pure so it round-trips through the same parser
and is unit-tested on its own.
"""
from __future__ import annotations

from typing import Iterable, Mapping, Sequence, Union

Number = Union[int, float]
# A data table is either a mapping {label: value} or a sequence of
# (label, value) pairs — both preserve caller order in modern Python.
Table = Union[Mapping[str, Number], Sequence[tuple[str, Number]]]


def _num(v: Number) -> str:
    """Compact number — ints stay int, floats drop trailing zeros."""
    f = float(v)
    if f.is_integer():
        return str(int(f))
    return str(round(f, 4))


def _pairs(data: Table) -> list[tuple[str, Number]]:
    if isinstance(data, Mapping):
        return list(data.items())
    return [(str(k), v) for k, v in data]


def _nums(values: Iterable[Number]) -> str:
    return ", ".join(_num(v) for v in values)


def _axes(xlabel: str | None, ylabel: str | None) -> list[str]:
    out: list[str] = []
    if xlabel:
        out.append(f"xlabel: {xlabel}")
    if ylabel:
        out.append(f"ylabel: {ylabel}")
    return out


def bar(data: Table, title: str | None = None) -> str:
    """Bar chart — `chart: title` + one `Label: value` row each."""
    lines: list[str] = []
    if title:
        lines.append(f"chart: {title}")
    lines += [f"{label}: {_num(value)}" for label, value in _pairs(data)]
    return "\n".join(lines)


def _series(
    keyword: str,
    series: Union[Mapping[str, Sequence[Number]], Sequence[Number]],
    title: str | None,
    xlabel: str | None,
    ylabel: str | None,
) -> str:
    lines: list[str] = []
    if title:
        lines.append(f"chart: {title}")
    lines += _axes(xlabel, ylabel)
    if isinstance(series, Mapping):
        for label, values in series.items():
            lines.append(f"{keyword} {label}: {_nums(values)}")
    else:
        lines.append(f"{keyword} Series: {_nums(series)}")
    return "\n".join(lines)


def line(
    series: Union[Mapping[str, Sequence[Number]], Sequence[Number]],
    title: str | None = None,
    xlabel: str | None = None,
    ylabel: str | None = None,
) -> str:
    """Line chart — one `line Label: a, b, c` per series."""
    return _series("line", series, title, xlabel, ylabel)


def area(
    series: Union[Mapping[str, Sequence[Number]], Sequence[Number]],
    title: str | None = None,
    xlabel: str | None = None,
    ylabel: str | None = None,
) -> str:
    """Area chart — one `area Label: a, b, c` per series."""
    return _series("area", series, title, xlabel, ylabel)


def pie(data: Table, title: str | None = None) -> str:
    """Pie / donut — `pie: title` + one `pie Label: value` slice each.
    Non-positive values are dropped (the renderer ignores them too)."""
    lines: list[str] = []
    if title:
        lines.append(f"pie: {title}")
    lines += [
        f"pie {label}: {_num(value)}"
        for label, value in _pairs(data)
        if float(value) > 0
    ]
    return "\n".join(lines)


def scatter(
    points: Sequence[tuple[Number, Number]],
    title: str | None = None,
    xlabel: str | None = None,
    ylabel: str | None = None,
) -> str:
    """Scatter plot — `scatter: title` + one `point: x, y` per pair."""
    lines: list[str] = []
    if title:
        lines.append(f"scatter: {title}")
    lines += _axes(xlabel, ylabel)
    lines += [f"point: {_num(x)}, {_num(y)}" for x, y in points]
    return "\n".join(lines)


def flow(edges: Sequence[tuple[str, str]]) -> str:
    """Flowchart — one `A --> B` per edge."""
    return "\n".join(f"{a} --> {b}" for a, b in edges)
