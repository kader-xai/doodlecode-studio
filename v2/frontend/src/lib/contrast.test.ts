import { describe, expect, it } from "vitest";
import { contrastRatio, hexToRgb, meetsAA, relativeLuminance } from "./contrast";

const INK = "#2a2a2a";
const INK_DARK = "#f0f0f0"; // chart/text foreground in dark theme
const CALLOUT_FILL = "#fff3a3";
const CARD_LIGHT = "#ffffff";
const CARD_DARK_DIAGRAM = "#1a1d23";
const CHART_STROKE_LIGHT = "#202124";

const MARKERS = {
  yellow: "#ffe066",
  pink: "#fcc2d7",
  mint: "#b2f2bb",
  sky: "#a5d8ff",
  peach: "#ffd8a8",
  violet: "#d0bfff",
};

describe("contrast utilities (iter 179)", () => {
  it("parses 3- and 6-digit hex", () => {
    expect(hexToRgb("#fff")).toEqual([255, 255, 255]);
    expect(hexToRgb("#2a2a2a")).toEqual([42, 42, 42]);
  });

  it("rejects bad hex", () => {
    expect(() => hexToRgb("#zzz")).toThrow();
  });

  it("black vs white is the maximum 21:1", () => {
    expect(contrastRatio("#000000", "#ffffff")).toBeCloseTo(21, 1);
  });

  it("same color is 1:1", () => {
    expect(contrastRatio(INK, INK)).toBeCloseTo(1, 5);
  });

  it("luminance is ordered white > mid > black", () => {
    expect(relativeLuminance("#ffffff")).toBeGreaterThan(relativeLuminance("#808080"));
    expect(relativeLuminance("#808080")).toBeGreaterThan(relativeLuminance("#000000"));
  });
});

describe("palette meets WCAG AA (iter 179)", () => {
  it("callout ink text on the yellow fill clears AA (normal text)", () => {
    expect(meetsAA(INK, CALLOUT_FILL)).toBe(true);
  });

  it("chart labels clear AA on the light card", () => {
    expect(meetsAA(CHART_STROKE_LIGHT, CARD_LIGHT)).toBe(true);
  });

  it("dark-theme chart labels clear AA on the dark diagram card", () => {
    expect(meetsAA(INK_DARK, CARD_DARK_DIAGRAM)).toBe(true);
  });

  it("ink text on every toolbar marker fill clears AA", () => {
    for (const [name, fill] of Object.entries(MARKERS)) {
      expect(meetsAA(INK, fill), `marker-${name}`).toBe(true);
    }
  });
});
