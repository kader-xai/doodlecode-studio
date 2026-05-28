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
});
