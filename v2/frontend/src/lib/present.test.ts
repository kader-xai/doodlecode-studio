import { describe, expect, it } from "vitest";
import {
  slideCenter,
  slideCenterY,
  topFractionOf,
  progressFraction,
} from "./present";

describe("slideCenter (iter 206 — dead-center both axes)", () => {
  it("centers on the cell midpoint with no callouts", () => {
    expect(slideCenter(120, 100, 560, 360)).toEqual({ cx: 400, cy: 280 });
  });

  it("shifts the horizontal center right to balance a callout column", () => {
    const plain = slideCenter(0, 0, 600, 400);
    const withCallout = slideCenter(0, 0, 600, 400, 300);
    expect(withCallout.cx).toBe(plain.cx + 150); // half the extra width
    expect(withCallout.cy).toBe(plain.cy); // vertical unchanged
  });

  it("is independent of zoom (pure geometry)", () => {
    expect(slideCenter(50, 50, 200, 100)).toEqual({ cx: 150, cy: 100 });
  });
});

describe("progressFraction (iter 163 — deck progress bar)", () => {
  it("fills to (index+1)/total so the last slide is 100%", () => {
    expect(progressFraction(0, 4)).toBe(0.25);
    expect(progressFraction(1, 4)).toBe(0.5);
    expect(progressFraction(3, 4)).toBe(1);
  });

  it("returns 0 for an empty / unknown deck", () => {
    expect(progressFraction(0, 0)).toBe(0);
    expect(progressFraction(2, 0)).toBe(0);
  });

  it("clamps an out-of-range index", () => {
    expect(progressFraction(99, 3)).toBe(1); // past the end → full
    expect(progressFraction(-5, 3)).toBeCloseTo(1 / 3, 5); // before start → first
  });
});

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
