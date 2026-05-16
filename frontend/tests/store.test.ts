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
  it("addCell appends an empty code cell", () => {
    const before = useStore.getState().notebook.cells.length;
    useStore.getState().addCell();
    expect(useStore.getState().notebook.cells.length).toBe(before + 1);
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
