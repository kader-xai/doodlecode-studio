import { describe, expect, it } from "vitest";
import { parseDoodleDiagram, renderDoodleDiagram } from "./doodleDiagram";

describe("parseDoodleDiagram", () => {
  it("parses flow edges with --> ", () => {
    const p = parseDoodleDiagram("A --> B\nB --> C");
    expect(p.flow).toEqual([
      { from: "A", to: "B" },
      { from: "B", to: "C" },
    ]);
  });

  it("parses chart bars (label: number)", () => {
    const p = parseDoodleDiagram("Markdown: 8\nWhiteboard: 9");
    expect(p.charts).toEqual([
      { label: "Markdown", value: 8 },
      { label: "Whiteboard", value: 9 },
    ]);
  });

  it("captures chart title", () => {
    const p = parseDoodleDiagram("chart: My title\nA: 1");
    expect(p.chartTitle).toBe("My title");
  });

  it("ignores the friendly 'flowchart' header", () => {
    const p = parseDoodleDiagram("flowchart\nA --> B");
    expect(p.flow.length).toBe(1);
  });

  it("supports mixed flow + chart in one source", () => {
    const p = parseDoodleDiagram(
      "flowchart\nA --> B\n\nchart: Demo\nA: 1\nB: 2",
    );
    expect(p.flow.length).toBe(1);
    expect(p.charts.length).toBe(2);
    expect(p.chartTitle).toBe("Demo");
  });

  it("parses a labelled line series (iter 160)", () => {
    const p = parseDoodleDiagram("line Loss: 0.9, 0.6, 0.4, 0.25");
    expect(p.lines).toEqual([{ label: "Loss", points: [0.9, 0.6, 0.4, 0.25] }]);
    // A line series must NOT also be captured as a bar.
    expect(p.charts).toEqual([]);
  });

  it("parses multiple line series + default labels (iter 160)", () => {
    const p = parseDoodleDiagram("line: 1 2 3\nline Val: 4, 5, 6");
    expect(p.lines).toEqual([
      { label: "Series 1", points: [1, 2, 3] },
      { label: "Val", points: [4, 5, 6] },
    ]);
  });

  it("keeps bars and line series separate (iter 160)", () => {
    const p = parseDoodleDiagram("Bars: 5\nline Trend: 1, 2, 3");
    expect(p.charts).toEqual([{ label: "Bars", value: 5 }]);
    expect(p.lines.length).toBe(1);
  });

  it("parses pie slices and an optional pie title (iter 164)", () => {
    const p = parseDoodleDiagram("pie: Languages\npie Python: 60\npie Rust: 40");
    expect(p.pieTitle).toBe("Languages");
    expect(p.pies).toEqual([
      { label: "Python", value: 60 },
      { label: "Rust", value: 40 },
    ]);
    // Pie slices must not leak into the bar list.
    expect(p.charts).toEqual([]);
  });

  it("ignores non-positive pie slices (iter 164)", () => {
    const p = parseDoodleDiagram("pie A: 10\npie B: 0\npie C: -3");
    expect(p.pies).toEqual([{ label: "A", value: 10 }]);
  });

  it("keeps bars, lines, and pies independent (iter 164)", () => {
    const p = parseDoodleDiagram("Bar: 5\nline L: 1, 2\npie Slice: 7");
    expect(p.charts.length).toBe(1);
    expect(p.lines.length).toBe(1);
    expect(p.pies.length).toBe(1);
  });
});

describe("renderDoodleDiagram", () => {
  it("returns SVG markup for both flow and chart", () => {
    const out = renderDoodleDiagram("A --> B\nA: 1\nB: 2");
    expect(out).toContain("<svg");
    expect(out).toMatch(/role="img"/);
  });

  it("returns a placeholder when source is empty", () => {
    const out = renderDoodleDiagram("");
    expect(out).toContain("Empty diagram");
  });

  it("escapes user-provided text in node labels", () => {
    const out = renderDoodleDiagram("'<script>' --> safe");
    expect(out).not.toContain("<script>");
    expect(out).toContain("&lt;script&gt;");
  });

  it("renders a line chart with polyline + dots (iter 160)", () => {
    const out = renderDoodleDiagram("line Loss: 0.9, 0.6, 0.4, 0.25");
    expect(out).toContain("<svg");
    expect(out).toMatch(/aria-label="Line chart"/);
    expect(out).toContain("<circle"); // point markers
    expect(out).toContain("Loss"); // legend label
  });

  it("escapes the line-series label (iter 160)", () => {
    const out = renderDoodleDiagram("line <b>x</b>: 1, 2, 3");
    expect(out).not.toContain("<b>x</b>");
    expect(out).toContain("&lt;b&gt;");
  });

  it("renders a pie chart with wedges + percentage legend (iter 164)", () => {
    const out = renderDoodleDiagram("pie: Share\npie Python: 60\npie Rust: 40");
    expect(out).toContain("<svg");
    expect(out).toMatch(/aria-label="Pie chart"/);
    expect(out).toContain("<path"); // wedge
    expect(out).toContain("60%"); // legend percentage
    expect(out).toContain("Python");
  });

  it("escapes a pie slice label (iter 164)", () => {
    const out = renderDoodleDiagram("pie <i>x</i>: 5\npie y: 5");
    expect(out).not.toContain("<i>x</i>");
    expect(out).toContain("&lt;i&gt;");
  });

  it("parses scatter points (point: x, y) (iter 166)", () => {
    const p = parseDoodleDiagram("scatter: Cloud\npoint: 1, 2\npoint: 3, 4.5");
    expect(p.scatterTitle).toBe("Cloud");
    expect(p.points).toEqual([
      { x: 1, y: 2 },
      { x: 3, y: 4.5 },
    ]);
  });

  it("ignores a point with fewer than two numbers (iter 166)", () => {
    const p = parseDoodleDiagram("point: 5\npoint: 1, 2");
    expect(p.points).toEqual([{ x: 1, y: 2 }]);
  });

  it("does not treat scatter points as bars (iter 166)", () => {
    const p = parseDoodleDiagram("point: 1, 2");
    expect(p.charts).toEqual([]);
  });

  it("renders a scatter plot with dots + axes (iter 166)", () => {
    const out = renderDoodleDiagram("scatter: XY\npoint: 1, 2\npoint: 3, 4\npoint: 5, 1");
    expect(out).toContain("<svg");
    expect(out).toMatch(/aria-label="Scatter plot"/);
    expect(out).toContain("<circle");
    expect(out).toContain("XY");
  });

  it("parses xlabel / ylabel axis titles (iter 168)", () => {
    const p = parseDoodleDiagram("xlabel: Epoch\nylabel: Loss\nline L: 1, 2");
    expect(p.xLabel).toBe("Epoch");
    expect(p.yLabel).toBe("Loss");
  });

  it("does not treat axis-label directives as bars (iter 168)", () => {
    const p = parseDoodleDiagram("xlabel: Epoch\nylabel: Loss\nA: 5");
    expect(p.charts).toEqual([{ label: "A", value: 5 }]);
  });

  it("renders axis titles on a line chart (iter 168)", () => {
    const out = renderDoodleDiagram("xlabel: Epoch\nylabel: Loss\nline Loss: 0.9, 0.5, 0.3");
    expect(out).toContain("Epoch");
    expect(out).toContain("rotate(-90"); // y title rotated
  });

  it("renders axis titles on a scatter plot (iter 168)", () => {
    const out = renderDoodleDiagram("scatter: XY\nxlabel: Width\nylabel: Height\npoint: 1, 2\npoint: 3, 4");
    expect(out).toContain("Width");
    expect(out).toContain("Height");
    expect(out).toContain("rotate(-90");
  });

  it("escapes axis-title text (iter 168)", () => {
    const out = renderDoodleDiagram("xlabel: <b>x</b>\nline L: 1, 2");
    expect(out).not.toContain("<b>x</b>");
    expect(out).toContain("&lt;b&gt;");
  });

  it("parses area series (area Label: ...) (iter 172)", () => {
    const p = parseDoodleDiagram("area Active: 2, 5, 9\narea New: 1, 2, 3");
    expect(p.areas).toEqual([
      { label: "Active", points: [2, 5, 9] },
      { label: "New", points: [1, 2, 3] },
    ]);
  });

  it("does not treat an area series as a bar (iter 172)", () => {
    const p = parseDoodleDiagram("area Active: 2, 5, 9");
    expect(p.charts).toEqual([]);
  });

  it("renders an area chart with a filled polygon (iter 172)", () => {
    const out = renderDoodleDiagram("xlabel: Week\nylabel: Users\narea Active: 2, 5, 9, 14");
    expect(out).toContain("<svg");
    expect(out).toMatch(/aria-label="Area chart"/);
    expect(out).toContain("fill-opacity=\"0.28\""); // the area fill
    expect(out).toContain("Active");
    expect(out).toContain("Week");
  });

  it("escapes an area-series label (iter 172)", () => {
    const out = renderDoodleDiagram("area <b>x</b>: 1, 2, 3");
    expect(out).not.toContain("<b>x</b>");
    expect(out).toContain("&lt;b&gt;");
  });
});
