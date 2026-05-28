import { beforeEach, describe, expect, it } from "vitest";
import { useStore } from "./store";

/**
 * Store smoke tests — verify CRUD invariants. We re-seed the cells
 * array in each test so they don't bleed into each other.
 */

function freshNotebook() {
  const s = useStore.getState();
  // Clear everything to a known state.
  useStore.setState({
    cells: [{ id: "c0", kind: "code", source: "print('hi')", title: "First", x: 0, y: 0 }],
    runtimes: {},
    selectedId: null,
    originalPositions: null,
    fileHandle: null,
  });
  return s;
}

describe("store: cell CRUD", () => {
  beforeEach(() => freshNotebook());

  it("adds and deletes a code cell", () => {
    const before = useStore.getState().cells.length;
    const id = useStore.getState().addCell();
    expect(useStore.getState().cells.length).toBe(before + 1);
    useStore.getState().deleteCell(id);
    expect(useStore.getState().cells.length).toBe(before);
  });

  it("moveCell updates x/y", () => {
    useStore.getState().moveCell("c0", 200, 300);
    const c = useStore.getState().cells.find((c) => c.id === "c0")!;
    expect(c.x).toBe(200);
    expect(c.y).toBe(300);
  });

  it("setSource changes the cell body", () => {
    useStore.getState().setSource("c0", "print('updated')");
    expect(useStore.getState().cells.find((c) => c.id === "c0")!.source).toBe("print('updated')");
  });

  it("duplicateCell creates a near-duplicate", () => {
    const dup = useStore.getState().duplicateCell("c0");
    expect(dup).not.toBeNull();
    const all = useStore.getState().cells;
    const original = all.find((c) => c.id === "c0")!;
    const copy = all.find((c) => c.id === dup!)!;
    expect(copy.source).toBe(original.source);
    expect(copy.x).toBe(original.x + 40);
    expect(copy.y).toBe(original.y + 40);
  });

  it("addMarkdownCell creates a markdown cell with seed content", () => {
    const id = useStore.getState().addMarkdownCell();
    const c = useStore.getState().cells.find((c) => c.id === id)!;
    expect(c.kind).toBe("markdown");
    expect(c.source).toMatch(/Heading/);
  });

  it("addMediaCell normalizes empty input to null", () => {
    expect(useStore.getState().addMediaCell("   ")).toBeNull();
  });

  it("setExplain populates callouts[0]", () => {
    useStore.getState().setExplain("c0", "hello bubble");
    const c = useStore.getState().cells.find((c) => c.id === "c0")!;
    expect(c.callouts?.[0].text).toBe("hello bubble");
  });

  it("setExplain(null) clears the callouts", () => {
    useStore.getState().setExplain("c0", "x");
    useStore.getState().setExplain("c0", null);
    expect(useStore.getState().cells.find((c) => c.id === "c0")!.callouts).toEqual([]);
  });

  it("spaceForPresentation snapshots and rollback restores", () => {
    useStore.getState().moveCell("c0", 500, 700);
    useStore.getState().spaceForPresentation(800);
    expect(useStore.getState().originalPositions).not.toBeNull();
    const after = useStore.getState().cells.find((c) => c.id === "c0")!;
    expect(after.y).toBe(0); // first cell goes to row 0
    useStore.getState().rollbackLayout();
    const back = useStore.getState().cells.find((c) => c.id === "c0")!;
    expect(back.x).toBe(500);
    expect(back.y).toBe(700);
    expect(useStore.getState().originalPositions).toBeNull();
  });
});

describe("store: cellsInOrder", () => {
  it("sorts top-to-bottom then left-to-right", () => {
    useStore.setState({
      cells: [
        { id: "a", kind: "code", source: "", x: 100, y: 0 },
        { id: "b", kind: "code", source: "", x: 0, y: 0 },
        { id: "c", kind: "code", source: "", x: 50, y: 200 },
      ],
      runtimes: {},
    });
    const ids = useStore.getState().cellsInOrder().map((c) => c.id);
    expect(ids).toEqual(["b", "a", "c"]);
  });
});
