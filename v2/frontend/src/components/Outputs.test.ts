import { describe, expect, it } from "vitest";
import { clampText, PER_ITEM_CHAR_CAP } from "./Outputs";

describe("clampText (iter 161 — big-output guard)", () => {
  it("leaves short text untouched", () => {
    const r = clampText("hello", 100);
    expect(r.shown).toBe("hello");
    expect(r.truncated).toBe(0);
  });

  it("clamps text over the cap and reports the remainder", () => {
    const r = clampText("x".repeat(250), 100);
    expect(r.shown.length).toBe(100);
    expect(r.truncated).toBe(150);
  });

  it("treats text exactly at the cap as not truncated", () => {
    const r = clampText("a".repeat(100), 100);
    expect(r.shown.length).toBe(100);
    expect(r.truncated).toBe(0);
  });

  it("defaults to the 100k character cap", () => {
    const big = "y".repeat(PER_ITEM_CHAR_CAP + 500);
    const r = clampText(big);
    expect(r.shown.length).toBe(PER_ITEM_CHAR_CAP);
    expect(r.truncated).toBe(500);
  });
});
