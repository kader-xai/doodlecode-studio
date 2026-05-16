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
  /** Actual rendered height per cell (px), populated by ResizeObserver.
   *  Canvas layout uses this when present so a tall output pushes the
   *  next cell down instead of overlapping it. */
  cellHeight: Record<string, number>;
  setNotebook: (n: Notebook) => void;
  updateCellSource: (id: string, source: string) => void;
  updateCellMeta: (id: string, meta: CellMeta | null) => void;
  addCell: (after?: string) => void;
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
  cellHeight: {},

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

  addCell: (after) => {
    const nb = get().notebook;
    const cell: Cell = { id: crypto.randomUUID(), kind: "code", source: "" };
    const cells = [...nb.cells];
    const idx = after ? cells.findIndex((c) => c.id === after) : cells.length - 1;
    cells.splice(idx + 1, 0, cell);
    const next: Notebook = { ...nb, cells };
    set({ notebook: next });
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
