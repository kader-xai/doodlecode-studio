import { describe, it, expect, beforeEach, vi } from "vitest";

// Mock the autosave API so the store doesn't try to POST during tests.
vi.mock("../src/api", () => ({
  autosaveNotebook: vi.fn(async () => ({ path: "" })),
}));

import { useStore } from "../src/store";

function reset() {
  try {
    if (typeof localStorage !== "undefined" && typeof localStorage.clear === "function") {
      localStorage.clear();
    }
  } catch {
    // jsdom may not expose full Storage in every environment; ignore.
  }
  useStore.setState({
    notebook: {
      name: "test.py",
      cells: [
        {
          id: "c1",
          kind: "code",
          source: "print(1)\n",
          meta: { kind: "intro", color: "sky", title: "First", explain: "body", tags: [] },
        },
      ],
    },
    cellState: {},
    focusedCellId: "c1",
    savedAt: null,
    cellHeight: {},
    installing: null,
    interactionMode: "cursor",
    openEditor: null,
    presenterTool: "none",
    installOpen: false,
    cellPositionOverrides: null,
    cellSize: {},
  });
}

beforeEach(reset);

describe("store: updateCellSource", () => {
  it("replaces the source and clears explain", () => {
    useStore.setState({
      cellState: { c1: { explain: { blocks: [], explanations: [] } } },
    });
    useStore.getState().updateCellSource("c1", "x = 99\n");
    const cell = useStore.getState().notebook.cells.find((c) => c.id === "c1");
    expect(cell!.source).toBe("x = 99\n");
    expect(useStore.getState().cellState.c1.explain).toBeUndefined();
  });

  it("preserves other cells' references (no global rebuild)", () => {
    const id2 = "c2";
    useStore.setState({
      notebook: {
        name: "n.py",
        cells: [
          ...useStore.getState().notebook.cells,
          { id: id2, kind: "code", source: "y = 2\n" },
        ],
      },
    });
    const before = useStore.getState().notebook.cells.find((c) => c.id === id2);
    useStore.getState().updateCellSource("c1", "z = 3\n");
    const after = useStore.getState().notebook.cells.find((c) => c.id === id2);
    expect(after).toBe(before);
  });
});

describe("store: updateCellMeta", () => {
  it("replaces the cell's meta", () => {
    useStore.getState().updateCellMeta("c1", {
      title: "Renamed",
      color: "peach",
      explain: "new body",
      tags: ["t"],
    });
    const cell = useStore.getState().notebook.cells.find((c) => c.id === "c1");
    expect(cell!.meta?.title).toBe("Renamed");
    expect(cell!.meta?.color).toBe("peach");
  });

  it("can clear meta entirely (passing null)", () => {
    useStore.getState().updateCellMeta("c1", null);
    const cell = useStore.getState().notebook.cells.find((c) => c.id === "c1");
    expect(cell!.meta).toBeNull();
  });
});

describe("store: newNotebook", () => {
  it("creates a single-cell notebook and focuses it", () => {
    useStore.getState().newNotebook("intro.py");
    const nb = useStore.getState().notebook;
    expect(nb.name).toBe("intro.py");
    expect(nb.cells).toHaveLength(1);
    expect(useStore.getState().focusedCellId).toBe(nb.cells[0].id);
  });

  it("appends .py if missing", () => {
    useStore.getState().newNotebook("foo");
    expect(useStore.getState().notebook.name).toBe("foo.py");
  });

  it("replaces an existing extension", () => {
    useStore.getState().newNotebook("foo.ipynb");
    expect(useStore.getState().notebook.name).toBe("foo.py");
  });
});

describe("store: addCell / deleteCell", () => {
  it("addCell appends an empty code cell by default", () => {
    const before = useStore.getState().notebook.cells.length;
    useStore.getState().addCell();
    const cells = useStore.getState().notebook.cells;
    expect(cells.length).toBe(before + 1);
    expect(cells[cells.length - 1].kind).toBe("code");
  });

  it("addCell with kind=markdown adds a slide-style text cell", () => {
    useStore.getState().addCell(undefined, "markdown");
    const cells = useStore.getState().notebook.cells;
    const added = cells[cells.length - 1];
    expect(added.kind).toBe("markdown");
    expect(added.source).toContain("New slide");
    expect(added.meta?.title).toBe("New slide");
  });

  it("addCell focuses the newly added cell", () => {
    useStore.getState().addCell(undefined, "markdown");
    const cells = useStore.getState().notebook.cells;
    expect(useStore.getState().focusedCellId).toBe(cells[cells.length - 1].id);
  });

  it("deleteCell removes by id", () => {
    useStore.getState().addCell();
    const cells = useStore.getState().notebook.cells;
    const id = cells[cells.length - 1].id;
    useStore.getState().deleteCell(id);
    expect(useStore.getState().notebook.cells.find((c) => c.id === id)).toBeUndefined();
  });
});

describe("store: reportCellHeight hysteresis", () => {
  it("ignores changes under 6px (prevents layout feedback loops)", () => {
    useStore.getState().reportCellHeight("c1", 400);
    useStore.getState().reportCellHeight("c1", 403);
    expect(useStore.getState().cellHeight.c1).toBe(400);
  });

  it("records changes >= 6px", () => {
    useStore.getState().reportCellHeight("c1", 400);
    useStore.getState().reportCellHeight("c1", 410);
    expect(useStore.getState().cellHeight.c1).toBe(410);
  });
});

describe("store: installOpen (v0.7.2)", () => {
  it("defaults to false", () => {
    expect(useStore.getState().installOpen).toBe(false);
  });
  it("setInstallOpen toggles", () => {
    useStore.getState().setInstallOpen(true);
    expect(useStore.getState().installOpen).toBe(true);
    useStore.getState().setInstallOpen(false);
    expect(useStore.getState().installOpen).toBe(false);
  });
});

describe("store: presenterTool (v0.7)", () => {
  it("defaults to 'none'", () => {
    expect(useStore.getState().presenterTool).toBe("none");
  });

  it("setPresenterTool switches the active overlay tool", () => {
    useStore.getState().setPresenterTool("pen");
    expect(useStore.getState().presenterTool).toBe("pen");
    useStore.getState().setPresenterTool("highlighter");
    expect(useStore.getState().presenterTool).toBe("highlighter");
  });

  it("leaving presentation resets the tool to 'none'", () => {
    useStore.getState().setPresenting(true);
    useStore.getState().setPresenterTool("pen");
    useStore.getState().setPresenting(false);
    expect(useStore.getState().presenterTool).toBe("none");
  });
});

describe("store: interactionMode + openEditor (v0.6)", () => {
  it("defaults to the cursor tool", () => {
    expect(useStore.getState().interactionMode).toBe("cursor");
  });

  it("setInteractionMode switches the active tool", () => {
    useStore.getState().setInteractionMode("hand");
    expect(useStore.getState().interactionMode).toBe("hand");
    useStore.getState().setInteractionMode("move");
    expect(useStore.getState().interactionMode).toBe("move");
  });

  it("openEditor is a singleton — second open replaces the first", () => {
    useStore.getState().setOpenEditor({ kind: "callout", cellId: "c1" });
    expect(useStore.getState().openEditor).toEqual({ kind: "callout", cellId: "c1" });
    useStore.getState().setOpenEditor({ kind: "text", cellId: "c2" });
    expect(useStore.getState().openEditor).toEqual({ kind: "text", cellId: "c2" });
    useStore.getState().setOpenEditor(null);
    expect(useStore.getState().openEditor).toBeNull();
  });
});

describe("store: setCellSize", () => {
  it("stores width and height", () => {
    useStore.getState().setCellSize("c1", { width: 700, height: 500 });
    expect(useStore.getState().cellSize.c1).toEqual({ width: 700, height: 500 });
  });

  it("merges partial updates", () => {
    useStore.getState().setCellSize("c1", { width: 700 });
    useStore.getState().setCellSize("c1", { height: 400 });
    expect(useStore.getState().cellSize.c1).toEqual({ width: 700, height: 400 });
  });

  it("clears the entry when both dimensions are undefined", () => {
    useStore.getState().setCellSize("c1", { width: 700, height: 500 });
    useStore.getState().setCellSize("c1", { width: undefined, height: undefined });
    expect(useStore.getState().cellSize.c1).toBeUndefined();
  });
});

describe("store: autoSpaceForPresentation / rollbackLayout", () => {
  it("sets one override entry per cell, spaced apart", () => {
    useStore.getState().addCell();
    useStore.getState().addCell();
    const cells = useStore.getState().notebook.cells;
    useStore.getState().autoSpaceForPresentation(800);
    const overrides = useStore.getState().cellPositionOverrides!;
    expect(Object.keys(overrides).length).toBe(cells.length);
    const ys = cells.map((c) => overrides[c.id].y);
    for (let i = 1; i < ys.length; i++) {
      expect(ys[i]).toBeGreaterThan(ys[i - 1]); // strictly increasing
      expect(ys[i] - ys[i - 1]).toBeGreaterThanOrEqual(800); // >= one slide
    }
  });

  it("rollback clears the overrides", () => {
    useStore.getState().autoSpaceForPresentation(800);
    expect(useStore.getState().cellPositionOverrides).not.toBeNull();
    useStore.getState().rollbackLayout();
    expect(useStore.getState().cellPositionOverrides).toBeNull();
  });

  it("tall cells consume multiple slide slots", () => {
    useStore.getState().reportCellHeight("c1", 1800); // ~2.25 × slide of 800
    useStore.getState().addCell(); // adds a normal-sized cell
    const cells = useStore.getState().notebook.cells;
    useStore.getState().autoSpaceForPresentation(800);
    const overrides = useStore.getState().cellPositionOverrides!;
    const firstY = overrides[cells[0].id].y;
    const secondY = overrides[cells[1].id].y;
    expect(secondY - firstY).toBeGreaterThanOrEqual(800 * 3);
  });
});

describe("store: setPresenting auto-focuses first cell", () => {
  it("flips focus from null to first cell on entry", () => {
    useStore.setState({ focusedCellId: null });
    useStore.getState().setPresenting(true);
    // The implementation defers the focus set via queueMicrotask
    return Promise.resolve().then(() => {
      expect(useStore.getState().focusedCellId).toBe("c1");
    });
  });
});
