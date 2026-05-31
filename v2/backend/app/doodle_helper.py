"""`doodle` — turn Python data into doodle-chart (and markdown-table) source.

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


def _category_bars(
    keyword: str,
    rows: Union[Mapping[str, Sequence[Number]], Sequence[tuple[str, Sequence[Number]]]],
    series: Sequence[str] | None,
    title: str | None,
) -> str:
    lines: list[str] = []
    if title:
        lines.append(f"{keyword}: {title}")
    if series:
        lines.append("series: " + ", ".join(str(s) for s in series))
    for label, values in _pairs(rows):  # type: ignore[arg-type]
        lines.append(f"{keyword} {label}: {_nums(values)}")
    return "\n".join(lines)


def stack(
    rows: Union[Mapping[str, Sequence[Number]], Sequence[tuple[str, Sequence[Number]]]],
    series: Sequence[str] | None = None,
    title: str | None = None,
) -> str:
    """Stacked bar — `stack: title` + `series: …` legend + one
    `stack Category: a, b, c` row each (segments = series)."""
    return _category_bars("stack", rows, series, title)


def group(
    rows: Union[Mapping[str, Sequence[Number]], Sequence[tuple[str, Sequence[Number]]]],
    series: Sequence[str] | None = None,
    title: str | None = None,
) -> str:
    """Grouped bar — `group: title` + `series: …` legend + one
    `group Category: a, b, c` row each (side-by-side columns = series)."""
    return _category_bars("group", rows, series, title)


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


def _cell(v: object) -> str:
    """One markdown table cell — pipes escaped, newlines flattened."""
    return str(v).replace("|", "\\|").replace("\n", " ").strip()


def table(
    rows: object,
    headers: Sequence[str] | None = None,
) -> str:
    """Markdown table — turn data into `| a | b |` source to paste into a
    **Text** cell (which renders it as a doodle table). Accepts:

      - a mapping → two columns (`headers` defaults to ``Key``/``Value``)
      - a sequence of mappings → columns from the first row's keys
      - a sequence of row sequences → pass ``headers=[...]``

        print(doodle.table({"Python": 8, "Rust": 4}, headers=["Lang", "LOC"]))
    """
    if isinstance(rows, Mapping):
        cols = list(headers) if headers else ["Key", "Value"]
        body = [[_cell(k), _cell(v)] for k, v in rows.items()]
    else:
        seq = list(rows)  # type: ignore[call-overload]
        if seq and isinstance(seq[0], Mapping):
            cols = list(headers) if headers else [str(k) for k in seq[0].keys()]
            body = [[_cell(r.get(c, "")) for c in cols] for r in seq]
        else:
            body = [[_cell(v) for v in r] for r in seq]
            cols = (
                list(headers)
                if headers
                else [f"Col {i + 1}" for i in range(len(body[0]))]
                if body
                else []
            )
    head = "| " + " | ".join(_cell(c) for c in cols) + " |"
    sep = "| " + " | ".join("---" for _ in cols) + " |"
    return "\n".join([head, sep] + ["| " + " | ".join(r) + " |" for r in body])
