import { describe, expect, it } from "vitest";
import { slideCenterY, topFractionOf } from "./present";

describe("slideCenterY (iter 162 — present in the upper third)", () => {
  it("lands the cell top at the requested fraction (round-trip)", () => {
    const cellTopY = 150;
    const H = 800;
    const zoom = 1;
    const cy = slideCenterY(cellTopY, H, zoom, 0.33);
    // The inverse must report the cell top at ~33% of the viewport.
    expect(topFractionOf(cellTopY, cy, H, zoom)).toBeCloseTo(0.33, 5);
  });

  it("is independent of cell height (anchors the TOP, not the middle)", () => {
    // Same top, two different heights → same centered point.
    const a = slideCenterY(500, 800, 1, 0.33);
    const b = slideCenterY(500, 800, 1, 0.33);
    expect(a).toBe(b);
  });

  it("respects zoom — a zoomed-in slide still tops out at the fraction", () => {
    const cellTopY = 400;
    const H = 900;
    const zoom = 1.5;
    const cy = slideCenterY(cellTopY, H, zoom, 0.35);
    expect(topFractionOf(cellTopY, cy, H, zoom)).toBeCloseTo(0.35, 5);
  });

  it("keeps the top above the old mid-screen centering", () => {
    // Old behavior centered the midpoint (cell.y + h/2). For a 240px
    // cell that put the TOP at 50% - 120px. The new top (33%) is higher.
    const cellTopY = 150;
    const h = 240;
    const H = 800;
    const zoom = 1;
    const newCy = slideCenterY(cellTopY, H, zoom, 0.33);
    const oldCy = cellTopY + h / 2; // legacy
    const newTop = topFractionOf(cellTopY, newCy, H, zoom);
    const oldTop = topFractionOf(cellTopY, oldCy, H, zoom);
    expect(newTop).toBeLessThan(oldTop); // new top sits higher on screen
    expect(newTop).toBeCloseTo(0.33, 5);
  });
});
