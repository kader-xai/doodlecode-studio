import { describe, it, expect } from "vitest";
import { colorFor, PALETTE, PALETTE_DARK } from "../src/lib/rough";

describe("colorFor", () => {
  it("returns the named color from the light palette", () => {
    expect(colorFor({ color: "mint" })).toBe(PALETTE.mint);
  });

  it("returns the dark variant when dark=true", () => {
    expect(colorFor({ color: "mint", dark: true })).toBe(PALETTE_DARK.mint);
  });

  it("falls back to the kind→color map when no color given", () => {
    expect(colorFor({ kind: "function" })).toBe(PALETTE.mint);
    expect(colorFor({ kind: "import" })).toBe(PALETTE.sky);
  });

  it("returns a neutral default when neither color nor kind is provided", () => {
    expect(colorFor({})).toMatch(/^#/);
  });

  it("passes through raw hex codes unchanged", () => {
    expect(colorFor({ color: "#abc123" })).toBe("#abc123");
  });

  it("dark palette has an entry for every light palette name", () => {
    for (const k of Object.keys(PALETTE)) {
      expect(PALETTE_DARK[k], `dark variant missing for ${k}`).toBeDefined();
    }
  });
});
