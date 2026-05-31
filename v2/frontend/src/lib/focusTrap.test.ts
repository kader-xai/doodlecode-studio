import { describe, expect, it } from "vitest";
import { nextTrapTarget } from "./focusTrap";

describe("nextTrapTarget (iter 176)", () => {
  it("Tab off the last element wraps to first", () => {
    expect(nextTrapTarget(3, 2, false)).toBe(0);
  });

  it("Tab in the middle needs no intervention", () => {
    expect(nextTrapTarget(3, 0, false)).toBe(-1);
    expect(nextTrapTarget(3, 1, false)).toBe(-1);
  });

  it("Shift+Tab off the first element wraps to last", () => {
    expect(nextTrapTarget(3, 0, true)).toBe(2);
  });

  it("Shift+Tab in the middle needs no intervention", () => {
    expect(nextTrapTarget(3, 1, true)).toBe(-1);
    expect(nextTrapTarget(3, 2, true)).toBe(-1);
  });

  it("focus outside the dialog snaps back inside", () => {
    expect(nextTrapTarget(3, -1, false)).toBe(0); // Tab → first
    expect(nextTrapTarget(3, -1, true)).toBe(2); // Shift+Tab → last
  });

  it("no focusable elements is a no-op", () => {
    expect(nextTrapTarget(0, -1, false)).toBe(-1);
    expect(nextTrapTarget(0, -1, true)).toBe(-1);
  });

  it("a single focusable element keeps focus on itself", () => {
    expect(nextTrapTarget(1, 0, false)).toBe(0);
    expect(nextTrapTarget(1, 0, true)).toBe(0);
  });
});
