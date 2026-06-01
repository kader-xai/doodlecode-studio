import { describe, expect, it } from "vitest";
import { cellDisplayWidth, cellDisplayHeight } from "./cellSize";

describe("cellDisplayWidth (iter 239)", () => {
  it("fixed-width cells ignore cell.w (the connector-gap bug)", () => {
    // A 720 stored width must NOT win over the real 560/580 card width.
    expect(cellDisplayWidth({ kind: "markdown", w: 720 })).toBe(560);
    expect(cellDisplayWidth({ kind: "code", w: 720 })).toBe(580);
    expect(cellDisplayWidth({ kind: "animation", w: 999 })).toBe(560);
  });
  it("resizable cells honor cell.w, with a per-kind default", () => {
    expect(cellDisplayWidth({ kind: "browser", w: 900 })).toBe(900);
    expect(cellDisplayWidth({ kind: "browser" })).toBe(720);
    expect(cellDisplayWidth({ kind: "diagram" })).toBe(560);
    expect(cellDisplayWidth({ kind: "media" })).toBe(480);
  });
});

describe("cellDisplayHeight (iter 239)", () => {
  it("resizable cells honor cell.h", () => {
    expect(cellDisplayHeight({ kind: "browser", h: 333 })).toBe(333);
    expect(cellDisplayHeight({ kind: "diagram" })).toBe(360);
  });
  it("auto-grow cells fall back to an estimate", () => {
    expect(cellDisplayHeight({ kind: "markdown" })).toBe(200);
    expect(cellDisplayHeight({ kind: "code" })).toBe(300);
  });
});
