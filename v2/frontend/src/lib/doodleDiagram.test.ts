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
});
