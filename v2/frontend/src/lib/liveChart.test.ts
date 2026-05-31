import { describe, expect, it } from "vitest";
import {
  hasLiveDirective,
  liveSourceIds,
  resolveLiveDoodleSource,
  stdoutOf,
} from "./liveChart";
import type { CellRuntime } from "../types";

describe("liveChart (iter 174)", () => {
  it("stdoutOf joins only stdout outputs", () => {
    const rt: CellRuntime = {
      running: false,
      result: {
        status: "ok",
        elapsed_ms: 1,
        outputs: [
          { type: "stdout", text: "chart: X\n" },
          { type: "stderr", text: "warn\n" },
          { type: "stdout", text: "A: 1" },
        ],
      },
    };
    expect(stdoutOf(rt)).toBe("chart: X\nA: 1");
  });

  it("stdoutOf is empty for an unrun cell", () => {
    expect(stdoutOf(undefined)).toBe("");
    expect(stdoutOf({ running: true })).toBe("");
  });

  it("detects + lists live directives", () => {
    const src = "live: c1\nA: 1\nlive: c2";
    expect(hasLiveDirective(src)).toBe(true);
    expect(liveSourceIds(src)).toEqual(["c1", "c2"]);
    expect(hasLiveDirective("A: 1\nB: 2")).toBe(false);
  });

  it("replaces live lines with the referenced stdout", () => {
    const out = resolveLiveDoodleSource("live: c1\nfooter: 1", (id) =>
      id === "c1" ? "chart: Live\nA: 5\nB: 9" : "",
    );
    expect(out).toBe("chart: Live\nA: 5\nB: 9\nfooter: 1");
  });

  it("leaves non-live lines untouched and blanks unknown cells", () => {
    const out = resolveLiveDoodleSource("flow\nA --> B\nlive: missing", () => "");
    expect(out).toBe("flow\nA --> B\n");
  });

  it("is case-insensitive on the directive keyword", () => {
    expect(liveSourceIds("LIVE: c9")).toEqual(["c9"]);
  });
});
