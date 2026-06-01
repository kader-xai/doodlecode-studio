import { describe, expect, it } from "vitest";
import {
  DEFAULT_TRANSITION,
  frameAt,
  frameCount,
  normalizeTransition,
  parseFrames,
} from "./animation";

describe("parseFrames", () => {
  it("splits non-blank trimmed lines into frames", () => {
    expect(parseFrames("  A \n\nB\n  \nC")).toEqual(["A", "B", "C"]);
  });
  it("empty source → no frames", () => {
    expect(parseFrames("")).toEqual([]);
    expect(parseFrames("   \n  ")).toEqual([]);
  });
});

describe("frameCount", () => {
  it("counts frames", () => {
    expect(frameCount("A\nB\nC")).toBe(3);
    expect(frameCount("")).toBe(0);
  });
});

describe("frameAt", () => {
  const f = ["one", "two", "three"];
  it("returns the frame at a step", () => {
    expect(frameAt(f, 0)).toBe("one");
    expect(frameAt(f, 2)).toBe("three");
  });
  it("clamps out-of-range steps", () => {
    expect(frameAt(f, -5)).toBe("one");
    expect(frameAt(f, 99)).toBe("three");
  });
  it("no frames → empty string, never throws", () => {
    expect(frameAt([], 0)).toBe("");
  });
});

describe("normalizeTransition", () => {
  it("passes through known styles", () => {
    expect(normalizeTransition("slide")).toBe("slide");
    expect(normalizeTransition("draw-on")).toBe("draw-on");
  });
  it("falls back for unknown/undefined", () => {
    expect(normalizeTransition(undefined)).toBe(DEFAULT_TRANSITION);
    expect(normalizeTransition("sparkle")).toBe(DEFAULT_TRANSITION);
  });
});
