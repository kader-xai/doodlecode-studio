import { describe, expect, it } from "vitest";
import { effectiveSource, revealCount } from "./reveal";
import type { Cell } from "../types";

function codeCell(source: string, reveals?: string[]): Cell {
  return { id: "c", kind: "code", source, x: 0, y: 0, reveals };
}

describe("effectiveSource (iter 154)", () => {
  it("returns base source at step 0", () => {
    const c = codeCell("print(1)", ["print(2)"]);
    expect(effectiveSource(c, 0)).toBe("print(1)");
  });

  it("appends one revealed step below the base", () => {
    const c = codeCell("def base():\n  pass", ["def step1():\n  pass"]);
    expect(effectiveSource(c, 1)).toBe("def base():\n  pass\n\ndef step1():\n  pass");
  });

  it("appends multiple revealed steps in order", () => {
    const c = codeCell("A", ["B", "C", "D"]);
    expect(effectiveSource(c, 2)).toBe("A\n\nB\n\nC");
    expect(effectiveSource(c, 3)).toBe("A\n\nB\n\nC\n\nD");
  });

  it("clamps step above the number of reveals", () => {
    const c = codeCell("A", ["B"]);
    expect(effectiveSource(c, 99)).toBe("A\n\nB");
  });

  it("returns base for non-code kinds even with reveals", () => {
    const c: Cell = { id: "m", kind: "markdown", source: "# hi", x: 0, y: 0, reveals: ["X"] };
    expect(effectiveSource(c, 1)).toBe("# hi");
  });

  it("trims trailing whitespace on the base before joining", () => {
    const c = codeCell("A\n\n  ", ["B"]);
    expect(effectiveSource(c, 1)).toBe("A\n\nB");
  });
});

describe("revealCount (iter 154)", () => {
  it("counts reveals on a code cell", () => {
    expect(revealCount(codeCell("A", ["B", "C"]))).toBe(2);
  });
  it("is 0 with no reveals", () => {
    expect(revealCount(codeCell("A"))).toBe(0);
  });
  it("is 0 for non-code kinds", () => {
    expect(revealCount({ id: "m", kind: "markdown", source: "x", x: 0, y: 0, reveals: ["B"] })).toBe(0);
  });
});
