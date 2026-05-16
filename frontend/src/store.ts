import { create } from "zustand";
import type { Cell, CellMeta, ExecuteResponse, ExplainResponse, Notebook } from "./types";
import { autosaveNotebook } from "./api";

type CellState = {
  outputs?: ExecuteResponse;
  explain?: ExplainResponse;
  running?: boolean;
};

type Store = {
  notebook: Notebook;
  cellState: Record<string, CellState>;
  presenting: boolean;
  focusedCellId: string | null;
  savedAt: number | null;
  theme: "light" | "dark";
  aboutOpen: boolean;
  installing: { packages: string; log: string } | null;
  /**
   * Cursor — click selects, double-click edits, no drag.
   * Hand   — drag pans the canvas, no node move.
   * Move   — drag moves cells, no canvas pan.
   * Three explicit modes prevent the click/drag/double-click confusion
   * Figma-style auto-mode had in v0.5.
   */
  interactionMode: "cursor" | "hand" | "move";
  /** The currently-open inline editor, if any. A singleton so two
   *  popovers can't fight for the screen. */
  openEditor: { kind: "callout" | "text"; cellId: string } | null;
  /** Active presenter overlay tool. `none` = nothing extra. `pen` =
   *  Excalidraw-style red ink that fades in ~1.4 s. `highlighter` =
   *  thick yellow ink that lingers ~4 s. */
  presenterTool: "none" | "pen" | "highlighter";
  /** Browser-level fullscreen state (mirror of document.fullscreenElement).
   *  When true + presenting, the toolbar hides and the presenter bar
   *  auto-fades after a few seconds of mouse-idle. */
  fullscreen: boolean;
  /** Active design / font theme. `doodle` is the golden default
   *  (handwriting). Other options swap the heading + body fonts
   *  app-wide via the `--font-display` CSS custom property. */
  design: "doodle" | "professional" | "serif" | "mono";
  /** Global font scale (1.0 = default). Applied to <html>'s font-size so
   *  every rem-based Tailwind utility scales together. Clamped 0.8–1.6. */
  fontScale: number;
  /** Singleton state for the install modal. Lifted out of the Toolbar
   *  so it isn't trapped inside the `pointer-events: none` wrapper. */
  installOpen: boolean;
  /** Actual rendered height per cell (px), populated by ResizeObserver.
   *  Canvas layout uses this when present so a tall output pushes the
   *  next cell down instead of overlapping it. */
  cellHeight: Record<string, number>;
  /** When set, the canvas layout uses these absolute positions instead
   *  of stacking. Toggled by the Auto-Space ↔ Together buttons. */
  cellPositionOverrides: Record<string, { x: number; y: number }> | null;
  /** Per-cell custom box dimensions set by the user via the corner
   *  resize handle. Width-only by default; height optional. Local to
   *  this session — NOT serialized to the .py file. */
  cellSize: Record<string, { width?: number; height?: number }>;
  setNotebook: (n: Notebook) => void;
  updateCellSource: (id: string, source: string) => void;
  updateCellMeta: (id: string, meta: CellMeta | null) => void;
  addCell: (after?: string, kind?: "code" | "markdown") => void;
  deleteCell: (id: string) => void;
  setExecResult: (id: string, r: ExecuteResponse | undefined, running?: boolean) => void;
  setExplain: (id: string, e: ExplainResponse | undefined) => void;
  setPresenting: (v: boolean) => void;
  focus: (id: string | null) => void;
  markSaved: (t: number) => void;
  toggleTheme: () => void;
  setAboutOpen: (v: boolean) => void;
  newNotebook: (name: string) => void;
  setInstalling: (s: { packages: string; log: string } | null) => void;
  reportCellHeight: (id: string, h: number) => void;
  autoSpaceForPresentation: (slideHeight: number) => void;
  rollbackLayout: () => void;
  setCellSize: (id: string, size: { width?: number; height?: number }) => void;
  setInteractionMode: (m: "cursor" | "hand" | "move") => void;
  setOpenEditor: (v: { kind: "callout" | "text"; cellId: string } | null) => void;
  setPresenterTool: (t: "none" | "pen" | "highlighter") => void;
  setInstallOpen: (v: boolean) => void;
  setFullscreen: (v: boolean) => void;
  setDesign: (d: "doodle" | "professional" | "serif" | "mono") => void;
  setFontScale: (n: number) => void;
};

const LS_KEY = "doodlecode.notebook.v2";

const fallback: Notebook = {
  name: "untitled.py",
  cells: [
    {
      id: "demo-1",
      kind: "code",
      source:
        "# Welcome to DoodleCode Studio.\n# Edit me, then press ▶ Run.\n\nprint(\"hello\")\n",
      meta: {
        kind: "intro",
        color: "sky",
        title: "Welcome",
        explain:
          "This is a callout — the right-side bubble you can edit by clicking ✎ on the code cell. Callouts are saved into the file when you export.",
      },
    },
  ],
};

function loadInitial(): Notebook {
  try {
    const raw = localStorage.getItem(LS_KEY);
    if (raw) {
      const parsed = JSON.parse(raw) as Notebook;
      if (parsed?.cells?.length) return parsed;
    }
  } catch {
    // ignore
  }
  return fallback;
}

let autosaveTimer: number | undefined;
function scheduleAutosave(nb: Notebook) {
  try {
    localStorage.setItem(LS_KEY, JSON.stringify(nb));
  } catch {
    // ignore quota errors
  }
  if (autosaveTimer) window.clearTimeout(autosaveTimer);
  autosaveTimer = window.setTimeout(() => {
    autosaveNotebook(nb)
      .then((r) => useStore.getState().markSaved(Date.now()))
      .catch(() => {});
  }, 1200);
}

const LS_THEME = "doodlecode.theme";

function loadTheme(): "light" | "dark" {
  try {
    const v = localStorage.getItem(LS_THEME);
    if (v === "dark" || v === "light") return v;
  } catch {}
  return window.matchMedia?.("(prefers-color-scheme: dark)").matches ? "dark" : "light";
}

export const useStore = create<Store>((set, get) => ({
  notebook: loadInitial(),
  cellState: {},
  presenting: false,
  focusedCellId: null,
  savedAt: null,
  theme: loadTheme(),
  aboutOpen: false,
  installing: null,
  interactionMode: "cursor",
  openEditor: null,
  presenterTool: "none",
  installOpen: false,
  fullscreen: false,
  design: (() => {
    try {
      const v = localStorage.getItem("doodlecode.design");
      if (v === "doodle" || v === "professional" || v === "serif" || v === "mono") return v;
    } catch {}
    return "doodle";
  })(),
  fontScale: (() => {
    try {
      const v = parseFloat(localStorage.getItem("doodlecode.fontScale") ?? "1");
      if (!isNaN(v) && v >= 0.8 && v <= 1.6) return v;
    } catch {}
    return 1;
  })(),
  cellHeight: {},
  cellPositionOverrides: null,
  cellSize: {},

  setNotebook: (notebook) => {
    set({ notebook, cellState: {}, focusedCellId: notebook.cells[0]?.id ?? null });
    scheduleAutosave(notebook);
  },

  updateCellSource: (id, source) => {
    const nb = get().notebook;
    const next: Notebook = {
      ...nb,
      cells: nb.cells.map((c) => (c.id === id ? { ...c, source } : c)),
    };
    set((s) => ({
      notebook: next,
      cellState: { ...s.cellState, [id]: { ...(s.cellState[id] ?? {}), explain: undefined } },
    }));
    scheduleAutosave(next);
  },

  updateCellMeta: (id, meta) => {
    const nb = get().notebook;
    const next: Notebook = {
      ...nb,
      cells: nb.cells.map((c) => (c.id === id ? { ...c, meta } : c)),
    };
    set((s) => ({
      notebook: next,
      cellState: { ...s.cellState, [id]: { ...(s.cellState[id] ?? {}), explain: undefined } },
    }));
    scheduleAutosave(next);
  },

  addCell: (after, kind = "code") => {
    const nb = get().notebook;
    const cell: Cell =
      kind === "markdown"
        ? {
            id: crypto.randomUUID(),
            kind: "markdown",
            source: "# New slide\n\nClick **📝 Edit** in the header to write here.",
            meta: { color: "sky", title: "New slide" },
          }
        : { id: crypto.randomUUID(), kind: "code", source: "" };
    const cells = [...nb.cells];
    const idx = after ? cells.findIndex((c) => c.id === after) : cells.length - 1;
    cells.splice(idx + 1, 0, cell);
    const next: Notebook = { ...nb, cells };
    set({ notebook: next, focusedCellId: cell.id });
    scheduleAutosave(next);
  },

  deleteCell: (id) => {
    const nb = get().notebook;
    const next: Notebook = { ...nb, cells: nb.cells.filter((c) => c.id !== id) };
    set({ notebook: next });
    scheduleAutosave(next);
  },

  setExecResult: (id, r, running) =>
    set((s) => ({
      cellState: { ...s.cellState, [id]: { ...(s.cellState[id] ?? {}), outputs: r, running } },
    })),

  setExplain: (id, e) =>
    set((s) => ({
      cellState: { ...s.cellState, [id]: { ...(s.cellState[id] ?? {}), explain: e } },
    })),

  setPresenting: (v) => {
    set({ presenting: v });
    if (!v) {
      set({ presenterTool: "none" });
      // Drop out of fullscreen too — chrome should be back on the next
      // render so the user can edit immediately.
      try {
        if (typeof document !== "undefined" && document.fullscreenElement) {
          const p = document.exitFullscreen?.();
          if (p && typeof p.catch === "function") p.catch(() => {});
        }
      } catch {
        /* ignore — browser-specific exits sometimes throw synchronously */
      }
    }
    if (v) {
      const s = get();
      // Always jump to a cell when entering present mode — even if a
      // focused cell already exists, we re-set it so the canvas's
      // fitBounds effect fires (it depends on focused id changing).
      const target =
        s.notebook.cells.find((c) => c.id === s.focusedCellId) ?? s.notebook.cells[0];
      if (target) {
        // Clear first, then set, so the effect runs even if it was
        // already pointed at this cell.
        set({ focusedCellId: null });
        // microtask to ensure the dep flip is observed
        queueMicrotask(() => set({ focusedCellId: target.id }));
      }
    }
  },
  focus: (id) => set({ focusedCellId: id }),
  markSaved: (t) => set({ savedAt: t }),
  toggleTheme: () => {
    const next = get().theme === "dark" ? "light" : "dark";
    try { localStorage.setItem(LS_THEME, next); } catch {}
    set({ theme: next });
  },
  setAboutOpen: (v) => set({ aboutOpen: v }),
  setInstalling: (s) => set({ installing: s }),
  reportCellHeight: (id, h) =>
    set((s) => {
      const prev = s.cellHeight[id];
      // Ignore tiny fluctuations (avoids feedback loops with the layout).
      if (prev !== undefined && Math.abs(prev - h) < 6) return s;
      return { cellHeight: { ...s.cellHeight, [id]: h } };
    }),
  autoSpaceForPresentation: (slideHeight) => {
    const cells = get().notebook.cells;
    if (!cells.length) return;
    const heights = get().cellHeight;
    // Each cell occupies at least one slide-height worth of vertical
    // space (so during presentation it fills the viewport without
    // bleeding into the next slide). Cells that measure taller than a
    // slide get rounded up to the next slide-height multiple.
    const overrides: Record<string, { x: number; y: number }> = {};
    let y = 40;
    for (const c of cells) {
      overrides[c.id] = { x: 80, y };
      const h = heights[c.id] ?? slideHeight * 0.7;
      const slots = Math.max(1, Math.ceil((h + 80) / slideHeight));
      y += slots * slideHeight;
    }
    set({ cellPositionOverrides: overrides });
  },
  rollbackLayout: () => set({ cellPositionOverrides: null }),
  setInteractionMode: (m) => set({ interactionMode: m }),
  setOpenEditor: (v) => set({ openEditor: v }),
  setPresenterTool: (t) => set({ presenterTool: t }),
  setInstallOpen: (v) => set({ installOpen: v }),
  setFullscreen: (v) => set({ fullscreen: v }),
  setDesign: (d) => {
    try { localStorage.setItem("doodlecode.design", d); } catch {}
    set({ design: d });
  },
  setFontScale: (n) => {
    const clamped = Math.min(1.6, Math.max(0.8, Math.round(n * 100) / 100));
    try { localStorage.setItem("doodlecode.fontScale", String(clamped)); } catch {}
    set({ fontScale: clamped });
  },
  setCellSize: (id, size) =>
    set((s) => {
      const prev = s.cellSize[id] ?? {};
      const next = { ...prev, ...size };
      // Drop the entry entirely when both dimensions are cleared.
      if (next.width === undefined && next.height === undefined) {
        const { [id]: _drop, ...rest } = s.cellSize;
        return { cellSize: rest };
      }
      return { cellSize: { ...s.cellSize, [id]: next } };
    }),
  newNotebook: (rawName) => {
    const name = (rawName.trim().endsWith(".py")
      ? rawName.trim()
      : `${rawName.trim().replace(/\.[^.]+$/, "")}.py`) || "untitled.py";
    const id = crypto.randomUUID();
    const notebook: Notebook = {
      name,
      cells: [
        {
          id,
          kind: "code",
          source: "print(\"hello from DoodleCode\")\n",
          meta: {
            kind: "intro",
            color: "sky",
            title: "Welcome",
            explain:
              "Edit this callout by clicking ✎ in the cell header. Save with 💾 — everything (text + images + multiple callouts) goes into one .py file.",
            tags: [],
          },
        },
      ],
    };
    set({ notebook, cellState: {}, focusedCellId: id });
    scheduleAutosave(notebook);
  },
}));
