import { beforeEach, describe, expect, it, vi } from "vitest";
import { useStore } from "./store";

/**
 * Mock the API layer so runAllCells doesn't actually hit the backend.
 * Each call resolves to a unique stdout payload so we can assert
 * order. setting status="error" lets us prove the loop bails early.
 */
vi.mock("./api", async () => {
  const real = await vi.importActual<typeof import("./api")>("./api");
  return {
    ...real,
    executeCode: vi.fn(async (source: string) => ({
      status: source.includes("BOOM") ? "error" : "ok",
      elapsed_ms: 1,
      outputs: [{ type: "stdout", text: source }],
    })),
  };
});

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

  it("addCell never spawns on top of an existing cell (iter 136)", () => {
    // Seed the canvas with a wall of cells covering the default spawn
    // origin so spawnPosition must step diagonally past them.
    useStore.setState({
      cells: Array.from({ length: 5 }, (_, i) => ({
        id: `seed${i}`,
        kind: "code" as const,
        source: "",
        x: 80 + i * 40,
        y: 80 + i * 40,
      })),
    });
    const id = useStore.getState().addCell();
    const added = useStore.getState().cells.find((c) => c.id === id)!;
    // The new cell must occupy a slot none of the seeds already do.
    const STEP = 40;
    const key = (x: number, y: number) =>
      `${Math.round(x / STEP)}:${Math.round(y / STEP)}`;
    const seeded = new Set(
      useStore.getState().cells.filter((c) => c.id !== id).map((c) => key(c.x, c.y)),
    );
    expect(seeded.has(key(added.x, added.y))).toBe(false);
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

  it("addBrowserCell prepends https:// + derives title from host (iter 139)", () => {
    const id = useStore.getState().addBrowserCell("example.com/about");
    expect(id).not.toBeNull();
    const c = useStore.getState().cells.find((x) => x.id === id)!;
    expect(c.kind).toBe("browser");
    expect(c.source).toBe("https://example.com/about");
    expect(c.title).toBe("example.com");
  });

  it("addBrowserCell keeps an explicit http:// prefix (iter 139)", () => {
    const id = useStore.getState().addBrowserCell("http://localhost:3000");
    const c = useStore.getState().cells.find((x) => x.id === id)!;
    expect(c.source).toBe("http://localhost:3000");
  });

  it("addBrowserCell returns null for whitespace (iter 139)", () => {
    expect(useStore.getState().addBrowserCell("   ")).toBeNull();
  });

  it("addWhiteboardCell + addDiagramCell return well-formed cells (iter 141)", () => {
    const wbId = useStore.getState().addWhiteboardCell();
    const wb = useStore.getState().cells.find((c) => c.id === wbId)!;
    expect(wb.kind).toBe("whiteboard");
    // Whiteboard source must be parseable JSON with a strokes array
    // and a bg field — drawing code relies on both.
    const parsed = JSON.parse(wb.source);
    expect(Array.isArray(parsed.strokes)).toBe(true);
    expect(parsed.strokes.length).toBe(0);
    expect(typeof parsed.bg).toBe("string");

    const dgId = useStore.getState().addDiagramCell();
    const dg = useStore.getState().cells.find((c) => c.id === dgId)!;
    expect(dg.kind).toBe("diagram");
    expect(dg.diagram_kind).toBe("doodle");
  });

  it("addCell partial overrides defaults but auto-fills missing fields (iter 140)", () => {
    // Partial { kind: 'markdown' } should override the default
    // 'code' kind without forcing the caller to repeat the
    // generated id, position, or source.
    const id = useStore.getState().addCell({ kind: "markdown", title: "Doc" });
    const c = useStore.getState().cells.find((x) => x.id === id)!;
    expect(c.kind).toBe("markdown");
    expect(c.title).toBe("Doc");
    // x/y come from spawnPosition, not the partial — assert they
    // were assigned to numbers, not left undefined.
    expect(typeof c.x).toBe("number");
    expect(typeof c.y).toBe("number");
    // Selection mirrors the new id per rule 21e.
    expect(useStore.getState().selectedId).toBe(id);
    expect(useStore.getState().selectedIds).toEqual([id]);
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

  it("setExplain('   ') treats whitespace as a clear (iter 143)", () => {
    useStore.getState().setExplain("c0", "real text");
    useStore.getState().setExplain("c0", "   \t  ");
    // The store treats whitespace-only as a clear, same as null.
    expect(useStore.getState().cells.find((c) => c.id === "c0")!.callouts).toEqual([]);
  });

  it("setCallouts filters out empty entries but keeps image-only ones (iter 144)", () => {
    useStore.getState().setCallouts("c0", [
      { text: "keep me" },
      { text: "  " }, // whitespace-only, no image → dropped
      { text: "", image: "data:image/png;base64,abc" }, // image-only → kept
      { text: "" }, // wholly empty → dropped
    ]);
    const c = useStore.getState().cells.find((x) => x.id === "c0")!;
    expect(c.callouts).toEqual([
      { text: "keep me" },
      { text: "", image: "data:image/png;base64,abc" },
    ]);
  });

  it("setExplain preserves callouts[1+] when replacing callouts[0] (iter 143)", () => {
    // Seed two callouts; setExplain only touches the first.
    useStore.getState().setCallouts("c0", [
      { text: "first" },
      { text: "second" },
    ]);
    useStore.getState().setExplain("c0", "first replaced");
    const c = useStore.getState().cells.find((x) => x.id === "c0")!;
    expect(c.callouts?.[0].text).toBe("first replaced");
    expect(c.callouts?.[1].text).toBe("second");
    expect(c.callouts?.length).toBe(2);
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

describe("store: multi-select + group ops (iter 33-35)", () => {
  beforeEach(() => {
    useStore.setState({
      cells: [
        { id: "a", kind: "code", source: "", x: 0,   y: 0,   w: 100, h: 100 },
        { id: "b", kind: "code", source: "", x: 200, y: 50,  w: 100, h: 100 },
        { id: "c", kind: "code", source: "", x: 400, y: 100, w: 100, h: 100 },
      ],
      runtimes: {},
      selectedId: null,
      selectedIds: [],
    });
  });

  it("deleteCells removes a whole group + focuses survivor (iter 109)", () => {
    useStore.getState().setSelectedIds(["a", "c"]);
    useStore.getState().deleteCells(["a", "c"]);
    const ids = useStore.getState().cells.map((c) => c.id);
    expect(ids).toEqual(["b"]);
    // Survivor "b" becomes the new selection (was null pre-iter-109).
    expect(useStore.getState().selectedId).toBe("b");
    expect(useStore.getState().selectedIds).toEqual(["b"]);
  });

  it("deleteCells on every cell leaves selection empty (iter 109)", () => {
    useStore.getState().setSelectedIds(["a", "b", "c"]);
    useStore.getState().deleteCells(["a", "b", "c"]);
    expect(useStore.getState().cells).toEqual([]);
    expect(useStore.getState().selectedId).toBeNull();
    expect(useStore.getState().selectedIds).toEqual([]);
  });

  it("alignSelected('left') aligns x to the leftmost", () => {
    useStore.getState().setSelectedIds(["a", "b", "c"]);
    useStore.getState().alignSelected("left");
    const xs = useStore.getState().cells.map((c) => c.x);
    expect(xs).toEqual([0, 0, 0]);
  });

  it("alignSelected('top') aligns y to the topmost", () => {
    useStore.getState().setSelectedIds(["a", "b", "c"]);
    useStore.getState().alignSelected("top");
    const ys = useStore.getState().cells.map((c) => c.y);
    expect(ys).toEqual([0, 0, 0]);
  });

  it("alignSelected('distH') spreads ≥3 cells with equal gaps", () => {
    useStore.getState().setSelectedIds(["a", "b", "c"]);
    useStore.getState().alignSelected("distH");
    // Bounding box left=0, right=500. Total w=300, span=500, gap=100.
    // a stays at 0; b at 100+100=200; c at 200+100+100=400.
    const xs = useStore.getState().cells.map((c) => c.x);
    expect(xs).toEqual([0, 200, 400]);
  });

  it("alignSelected no-ops with fewer than 2 selected", () => {
    useStore.getState().setSelectedIds(["a"]);
    useStore.getState().alignSelected("left");
    const a = useStore.getState().cells.find((c) => c.id === "a")!;
    expect(a.x).toBe(0); // unchanged
  });

  it("alignSelected('distH') no-ops with only 2 cells (iter 131)", () => {
    useStore.getState().setSelectedIds(["a", "b"]);
    const before = useStore.getState().cells.map((c) => c.x);
    useStore.getState().alignSelected("distH");
    const after = useStore.getState().cells.map((c) => c.x);
    expect(after).toEqual(before); // distribution needs ≥3 anchors
  });
});

describe("store: runAllCells + clearAllOutputs (iter 36-38)", () => {
  beforeEach(() => {
    useStore.setState({
      cells: [
        { id: "a", kind: "code",     source: "ONE", x: 0, y: 0 },
        { id: "m", kind: "markdown", source: "## skip me", x: 0, y: 100 },
        { id: "b", kind: "code",     source: "TWO", x: 0, y: 200 },
      ],
      runtimes: {},
      execCounter: 0,
      selectedId: null,
      selectedIds: [],
    });
  });

  it("runAllCells runs every code cell, skipping non-code, returns null on success", async () => {
    const failed = await useStore.getState().runAllCells();
    expect(failed).toBeNull();
    const ra = useStore.getState().runtimes["a"];
    const rb = useStore.getState().runtimes["b"];
    expect(ra?.result?.status).toBe("ok");
    expect(rb?.result?.status).toBe("ok");
    expect(useStore.getState().runtimes["m"]).toBeUndefined();
    // execCounter is bumped twice — once per code cell.
    expect(useStore.getState().execCounter).toBe(2);
    expect(ra?.execCount).toBe(1);
    expect(rb?.execCount).toBe(2);
  });

  it("runAllCells halts at the first error and returns the failed id", async () => {
    useStore.setState({
      cells: [
        { id: "a", kind: "code", source: "fine",      x: 0, y: 0 },
        { id: "b", kind: "code", source: "BOOM",      x: 0, y: 100 },
        { id: "c", kind: "code", source: "neverruns", x: 0, y: 200 },
      ],
      runtimes: {},
      execCounter: 0,
    });
    const failed = await useStore.getState().runAllCells();
    expect(failed).toBe("b");
    expect(useStore.getState().runtimes["c"]).toBeUndefined();
    // Iter 114: failed cell becomes the selection so the red iter-40
    // border is in the user's face.
    expect(useStore.getState().selectedId).toBe("b");
    expect(useStore.getState().selectedIds).toEqual(["b"]);
    // Iter 115: panToTick bumps so Canvas centers on the failed cell.
    expect(useStore.getState().panToTick).toBeGreaterThan(0);
  });

  it("runAllCells on an empty notebook returns null (iter 126)", async () => {
    useStore.setState({ cells: [], runtimes: {}, execCounter: 0 });
    const failed = await useStore.getState().runAllCells();
    expect(failed).toBeNull();
    expect(useStore.getState().runtimes).toEqual({});
    expect(useStore.getState().execCounter).toBe(0);
  });

  it("runAllCells on a markdown-only notebook returns null (iter 126)", async () => {
    useStore.setState({
      cells: [
        { id: "m1", kind: "markdown", source: "# hi",  x: 0, y: 0 },
        { id: "m2", kind: "markdown", source: "## hi", x: 0, y: 100 },
      ],
      runtimes: {},
      execCounter: 0,
    });
    const failed = await useStore.getState().runAllCells();
    expect(failed).toBeNull();
    // No markdown cell got a runtime entry.
    expect(useStore.getState().runtimes).toEqual({});
  });

  it("clearAllOutputs wipes runtimes without touching cells", () => {
    useStore.setState({
      runtimes: {
        a: { running: false, result: { status: "ok", elapsed_ms: 1, outputs: [] }, execCount: 7 },
      },
    });
    useStore.getState().clearAllOutputs();
    expect(useStore.getState().runtimes).toEqual({});
    expect(useStore.getState().cells.length).toBe(3); // cells untouched
  });

  it("clearAllOutputs also resets execCounter (iter 103)", () => {
    useStore.setState({ execCounter: 12 });
    useStore.getState().clearAllOutputs();
    expect(useStore.getState().execCounter).toBe(0);
  });

  it("deleteCell focuses the next sibling when the deleted cell was primary (iter 108)", () => {
    useStore.setState({
      cells: [
        { id: "a", kind: "code", source: "", x: 0, y: 0 },
        { id: "b", kind: "code", source: "", x: 0, y: 100 },
        { id: "c", kind: "code", source: "", x: 0, y: 200 },
      ],
      runtimes: {},
      selectedId: "b",
      selectedIds: ["b"],
    });
    useStore.getState().deleteCell("b");
    expect(useStore.getState().selectedId).toBe("c");
    expect(useStore.getState().selectedIds).toEqual(["c"]);
  });

  it("deleteCell focuses the new last cell when deleting from the end (iter 108)", () => {
    useStore.setState({
      cells: [
        { id: "a", kind: "code", source: "", x: 0, y: 0 },
        { id: "b", kind: "code", source: "", x: 0, y: 100 },
      ],
      runtimes: {},
      selectedId: "b",
      selectedIds: ["b"],
    });
    useStore.getState().deleteCell("b");
    expect(useStore.getState().selectedId).toBe("a");
  });

  it("deleteCell on an empty notebook clears selection (iter 108)", () => {
    useStore.setState({
      cells: [{ id: "lonely", kind: "code", source: "", x: 0, y: 0 }],
      runtimes: {},
      selectedId: "lonely",
      selectedIds: ["lonely"],
    });
    useStore.getState().deleteCell("lonely");
    expect(useStore.getState().selectedId).toBeNull();
    expect(useStore.getState().selectedIds).toEqual([]);
  });

  it("resetKernelState drops execCount but keeps result panels (iter 104)", () => {
    useStore.setState({
      execCounter: 7,
      runtimes: {
        a: { running: false, result: { status: "ok", elapsed_ms: 5, outputs: [] }, execCount: 5 },
        b: { running: false, result: { status: "error", elapsed_ms: 1, outputs: [] }, execCount: 7 },
      },
    });
    useStore.getState().resetKernelState();
    const s = useStore.getState();
    expect(s.execCounter).toBe(0);
    // [n] badges gone
    expect(s.runtimes["a"].execCount).toBeUndefined();
    expect(s.runtimes["b"].execCount).toBeUndefined();
    // But the result panels (incl. traceback on b) are still there.
    expect(s.runtimes["a"].result?.status).toBe("ok");
    expect(s.runtimes["b"].result?.status).toBe("error");
  });
});

describe("store: cell↔cell links (iter 45)", () => {
  beforeEach(() => {
    useStore.setState({
      cells: [
        { id: "a", kind: "code",     source: "", x: 0,   y: 0   },
        { id: "b", kind: "markdown", source: "", x: 200, y: 0   },
        { id: "c", kind: "browser",  source: "", x: 400, y: 0   },
      ],
      runtimes: {},
      selectedId: null,
      selectedIds: [],
    });
  });

  it("linkCells writes the link on BOTH endpoints", () => {
    useStore.getState().linkCells("a", "b");
    const cells = useStore.getState().cells;
    expect(cells.find((c) => c.id === "a")!.links).toEqual(["b"]);
    expect(cells.find((c) => c.id === "b")!.links).toEqual(["a"]);
    expect(cells.find((c) => c.id === "c")!.links ?? []).toEqual([]);
  });

  it("linkCells is idempotent — calling twice does not duplicate", () => {
    useStore.getState().linkCells("a", "b");
    useStore.getState().linkCells("a", "b");
    const cellA = useStore.getState().cells.find((c) => c.id === "a")!;
    expect(cellA.links).toEqual(["b"]);
  });

  it("linkCells refuses self-links", () => {
    useStore.getState().linkCells("a", "a");
    expect(useStore.getState().cells.find((c) => c.id === "a")!.links ?? []).toEqual([]);
  });

  it("linkCells refuses dangling endpoints (iter 130)", () => {
    useStore.getState().linkCells("a", "ghost");
    useStore.getState().linkCells("ghost", "b");
    const cells = useStore.getState().cells;
    expect(cells.find((c) => c.id === "a")!.links ?? []).toEqual([]);
    expect(cells.find((c) => c.id === "b")!.links ?? []).toEqual([]);
  });

  it("unlinkCells drops the link from both endpoints", () => {
    useStore.getState().linkCells("a", "b");
    useStore.getState().unlinkCells("a", "b");
    const cells = useStore.getState().cells;
    expect(cells.find((c) => c.id === "a")!.links).toEqual([]);
    expect(cells.find((c) => c.id === "b")!.links).toEqual([]);
  });

  it("unlinkCells refuses self-references (iter 132)", () => {
    useStore.getState().linkCells("a", "b");
    useStore.getState().unlinkCells("a", "a");
    // The legitimate a→b link must survive a self-unlink attempt.
    const cellA = useStore.getState().cells.find((c) => c.id === "a")!;
    expect(cellA.links).toEqual(["b"]);
  });

  it("unlinkCells on a never-linked pair is a no-op (iter 127)", () => {
    useStore.getState().unlinkCells("a", "c");
    const cells = useStore.getState().cells;
    expect(cells.find((c) => c.id === "a")!.links ?? []).toEqual([]);
    expect(cells.find((c) => c.id === "c")!.links ?? []).toEqual([]);
  });

  it("toggleLinkSelected creates then removes a link with exactly 2 selected", () => {
    useStore.getState().setSelectedIds(["a", "c"]);
    expect(useStore.getState().toggleLinkSelected()).toBe(true);
    expect(useStore.getState().cells.find((c) => c.id === "a")!.links).toEqual(["c"]);
    expect(useStore.getState().toggleLinkSelected()).toBe(false);
    expect(useStore.getState().cells.find((c) => c.id === "a")!.links).toEqual([]);
  });

  it("toggleLinkSelected is a no-op with !=2 selected", () => {
    useStore.getState().setSelectedIds(["a"]);
    expect(useStore.getState().toggleLinkSelected()).toBe(false);
    useStore.getState().setSelectedIds(["a", "b", "c"]);
    expect(useStore.getState().toggleLinkSelected()).toBe(false);
    expect(useStore.getState().cells.find((c) => c.id === "a")!.links ?? []).toEqual([]);
  });

  it("deleteCell prunes dangling links from survivors", () => {
    useStore.getState().linkCells("a", "b");
    useStore.getState().linkCells("b", "c");
    useStore.getState().deleteCell("b");
    const cells = useStore.getState().cells;
    expect(cells.map((c) => c.id)).toEqual(["a", "c"]);
    expect(cells.find((c) => c.id === "a")!.links).toEqual([]);
    expect(cells.find((c) => c.id === "c")!.links).toEqual([]);
  });
});

describe("store: duplicate semantics (iter 60)", () => {
  beforeEach(() => {
    useStore.setState({
      cells: [
        { id: "src", kind: "code", source: "x = 1", x: 0, y: 0,
          callouts: [{ text: "hello" }], links: ["other"] },
        { id: "other", kind: "code", source: "", x: 200, y: 0, links: ["src"] },
      ],
      runtimes: {},
      selectedId: null,
      selectedIds: [],
    });
  });

  it("duplicateCell drops outgoing links so the graph stays symmetric", () => {
    const dupId = useStore.getState().duplicateCell("src")!;
    const dup = useStore.getState().cells.find((c) => c.id === dupId)!;
    expect(dup.links).toEqual([]);
  });

  it("duplicateCell deep-clones callouts so editing the copy doesn't mutate the source", () => {
    const dupId = useStore.getState().duplicateCell("src")!;
    const dup = useStore.getState().cells.find((c) => c.id === dupId)!;
    const src = useStore.getState().cells.find((c) => c.id === "src")!;
    expect(dup.callouts).toEqual([{ text: "hello" }]);
    // Different array identity.
    expect(dup.callouts).not.toBe(src.callouts);
    // Different element identity.
    expect(dup.callouts![0]).not.toBe(src.callouts![0]);
  });
});

describe("store: rule 21e selection sync (iter 78)", () => {
  beforeEach(() => {
    useStore.setState({
      cells: [{ id: "c0", kind: "code", source: "", x: 0, y: 0 }],
      runtimes: {},
      selectedId: null,
      selectedIds: [],
    });
  });

  it("addCell sets both selectedId and selectedIds", () => {
    const id = useStore.getState().addCell();
    expect(useStore.getState().selectedId).toBe(id);
    expect(useStore.getState().selectedIds).toEqual([id]);
  });

  it("duplicateCell sets both", () => {
    const dup = useStore.getState().duplicateCell("c0")!;
    expect(useStore.getState().selectedId).toBe(dup);
    expect(useStore.getState().selectedIds).toEqual([dup]);
  });

  it("focusCell sets both (null clears)", () => {
    useStore.getState().focusCell("c0");
    expect(useStore.getState().selectedIds).toEqual(["c0"]);
    useStore.getState().focusCell(null);
    expect(useStore.getState().selectedIds).toEqual([]);
  });
});

describe("store: setSelectedIds keeps primary in sync (iter 76)", () => {
  beforeEach(() => {
    useStore.setState({
      cells: [
        { id: "a", kind: "code", source: "", x: 0, y: 0 },
        { id: "b", kind: "code", source: "", x: 0, y: 100 },
        { id: "c", kind: "code", source: "", x: 0, y: 200 },
      ],
      runtimes: {},
      selectedId: "a",
      selectedIds: ["a"],
    });
  });

  it("preserves primary when it's still in the new set", () => {
    useStore.getState().setSelectedIds(["a", "b"]);
    expect(useStore.getState().selectedId).toBe("a");
  });

  it("picks the first member when previous primary is dropped", () => {
    useStore.getState().setSelectedIds(["b", "c"]);
    expect(useStore.getState().selectedId).toBe("b");
  });

  it("clears primary when the new set is empty", () => {
    useStore.getState().setSelectedIds([]);
    expect(useStore.getState().selectedId).toBeNull();
  });
});

describe("store: collapse (iter 53/57)", () => {
  beforeEach(() => {
    useStore.setState({
      cells: [
        { id: "a", kind: "code",     source: "", x: 0, y: 0 },
        { id: "b", kind: "markdown", source: "", x: 0, y: 100, collapsed: true },
        { id: "c", kind: "browser",  source: "", x: 0, y: 200 },
      ],
      runtimes: {},
      selectedId: null,
      selectedIds: [],
    });
  });

  it("toggleCollapse flips the flag on the target cell only", () => {
    useStore.getState().toggleCollapse("a");
    const cells = useStore.getState().cells;
    expect(cells.find((c) => c.id === "a")!.collapsed).toBe(true);
    expect(cells.find((c) => c.id === "b")!.collapsed).toBe(true); // unchanged
    expect(cells.find((c) => c.id === "c")!.collapsed).toBeFalsy();
  });

  it("setAllCollapsed(true) collapses every cell", () => {
    useStore.getState().setAllCollapsed(true);
    expect(useStore.getState().cells.every((c) => c.collapsed)).toBe(true);
  });

  it("setAllCollapsed(false) expands every cell", () => {
    useStore.getState().setAllCollapsed(false);
    expect(useStore.getState().cells.every((c) => !c.collapsed)).toBe(true);
  });

  it("setAllCollapsed preserves object identity for already-matching cells (iter 142)", () => {
    // Cell 'b' starts collapsed; a + c don't. After setAllCollapsed(true),
    // only a and c should be new object references. 'b' must stay the
    // same reference so React's downstream memo / shallow-compare
    // doesn't repaint cells that didn't actually change.
    const before = useStore.getState().cells;
    const bBefore = before.find((c) => c.id === "b")!;
    useStore.getState().setAllCollapsed(true);
    const bAfter = useStore.getState().cells.find((c) => c.id === "b")!;
    expect(bAfter).toBe(bBefore);
  });
});

describe("store: palette (iter 62/63)", () => {
  beforeEach(() => {
    useStore.setState({
      cells: [
        { id: "a", kind: "code", source: "", x: 0, y: 0 },
        { id: "b", kind: "code", source: "", x: 100, y: 100 },
      ],
      runtimes: {},
      selectedId: null,
      selectedIds: [],
      paletteOpen: false,
      panToTick: 0,
    });
  });

  it("setPaletteOpen toggles visibility", () => {
    useStore.getState().setPaletteOpen(true);
    expect(useStore.getState().paletteOpen).toBe(true);
    useStore.getState().setPaletteOpen(false);
    expect(useStore.getState().paletteOpen).toBe(false);
  });

  it("panToCell selects the target and bumps panToTick", () => {
    const before = useStore.getState().panToTick;
    useStore.getState().panToCell("b");
    const s = useStore.getState();
    expect(s.selectedId).toBe("b");
    expect(s.selectedIds).toEqual(["b"]);
    expect(s.panToTick).toBe(before + 1);
  });

  it("panToCell can be called repeatedly — each bump differs", () => {
    useStore.getState().panToCell("a");
    const after1 = useStore.getState().panToTick;
    useStore.getState().panToCell("a"); // same id, but tick should still bump
    expect(useStore.getState().panToTick).toBe(after1 + 1);
  });

  it("panToCell refuses non-existent ids (iter 133)", () => {
    useStore.getState().panToCell("a");
    const baseline = useStore.getState();
    useStore.getState().panToCell("ghost");
    const after = useStore.getState();
    // selection stays on 'a', tick does NOT bump
    expect(after.selectedId).toBe("a");
    expect(after.selectedIds).toEqual(["a"]);
    expect(after.panToTick).toBe(baseline.panToTick);
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

  it("tolerates small y-jitter within the row bucket (iter 137)", () => {
    // Bucket width is 40, so y=0 and y=19 land in the same row;
    // the secondary sort by x should win. The third cell sits well
    // below in a separate bucket.
    useStore.setState({
      cells: [
        { id: "right", kind: "code", source: "", x: 300, y: 0 },
        { id: "left",  kind: "code", source: "", x: 0,   y: 19 },
        { id: "below", kind: "code", source: "", x: 100, y: 200 },
      ],
      runtimes: {},
    });
    const ids = useStore.getState().cellsInOrder().map((c) => c.id);
    expect(ids).toEqual(["left", "right", "below"]);
  });
});
