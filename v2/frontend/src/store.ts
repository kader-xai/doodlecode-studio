import { create } from "zustand";
import { executeCode, openNotebook, saveNotebook } from "./api";
import type { Callout, Cell, CellRuntime } from "./types";

/**
 * Global app state. ONE source of truth — components subscribe with
 * selectors and never duplicate state in local hooks.
 *
 * Iter 4 additions:
 *   - `notebookName`                — display + filename
 *   - `savedAt`                     — last successful save / autosave
 *   - `newNotebook`                 — wipe to one seed cell
 *   - `loadNotebookFromText`        — calls /api/open
 *   - `downloadNotebook`            — calls /api/save and triggers download
 *
 * Autosave: any change to `cells` or `notebookName` schedules a
 * 300ms-debounced localStorage write. On boot we restore from
 * localStorage if present; otherwise we seed.
 */
export type Theme = "light" | "dark";

export interface AppState {
  // ── theme ───────────────────────────────────────────────────────
  theme: Theme;
  setTheme: (t: Theme) => void;
  toggleTheme: () => void;
  /** Ambient background style. Persists across sessions. */
  ambient: "off" | "geometry" | "nature" | "science";
  setAmbient: (a: "off" | "geometry" | "nature" | "science") => void;

  // ── notebook ────────────────────────────────────────────────────
  notebookName: string;
  setNotebookName: (n: string) => void;
  savedAt: number | null;

  // ── cells & runtime ─────────────────────────────────────────────
  cells: Cell[];
  runtimes: Record<string, CellRuntime>;
  /** Iter 37: monotonic global counter incremented per runCell call.
   *  Stamps `execCount` on the per-cell runtime so the UI can show
   *  Jupyter-style `[n]` badges. Reset on ↻ Kernel + New notebook. */
  execCounter: number;
  selectedId: string | null;
  /** Iter 33: full selection set. `selectedId` is the "primary"
   *  (last-clicked) cell — toolbar / callout / focus continue to act
   *  on it. `selectedIds` is the marquee/shift-click superset and
   *  drives group-move and group-delete. When length === 1 the two
   *  agree; when empty, no cell is selected. */
  selectedIds: string[];
  setSelectedIds: (ids: string[]) => void;
  /** Per-cell "force rename" tick. Bumping this triggers an
   *  EditableTitle to enter edit mode (used by F2 keyboard handler). */
  renameTick: Record<string, number>;
  requestRename: (id: string) => void;

  /** Tool mode. "select" = drag selects/moves cells (default).
   *  "hand" = drag pans the canvas, cells locked. */
  interactionMode: "select" | "hand";
  setInteractionMode: (m: "select" | "hand") => void;

  setSource: (id: string, source: string) => void;
  setTitle: (id: string, title: string) => void;
  setDiagramKind: (id: string, kind: string) => void;
  /** null clears the first callout (or removes it entirely). Empty string is treated the same. */
  setExplain: (id: string, text: string | null) => void;
  setCallouts: (id: string, callouts: Callout[]) => void;
  /** Which cell, if any, is currently in the callout-editor modal. */
  calloutEditorCellId: string | null;
  openCalloutEditor: (id: string | null) => void;
  /** Whether the pip-install modal is open. */
  installOpen: boolean;
  setInstallOpen: (on: boolean) => void;

  /** ── Presentation mode ─────────────────────────────────────── */
  presenting: boolean;
  /** Which cell is currently centered on screen (presentation focus). */
  focusedCellId: string | null;
  setPresenting: (on: boolean) => void;
  focusCell: (id: string | null) => void;
  /** Reading order: top-to-bottom, then left-to-right. */
  cellsInOrder: () => Cell[];
  nextCell: () => void;
  prevCell: () => void;

  /** Active presenter ink tool. */
  presenterTool: "none" | "pen" | "highlighter" | "fixedPen";
  setPresenterTool: (t: "none" | "pen" | "highlighter" | "fixedPen") => void;
  /** Mirror of `document.fullscreenElement != null`. Updated by the
   *  app shell listening to the native `fullscreenchange` event so
   *  state stays in sync when the user exits via Esc. */
  fullscreen: boolean;
  setFullscreen: (on: boolean) => void;
  /** Bumped to wipe all presenter ink (Esc / E / exit). */
  presenterClearCounter: number;
  clearPresenterInk: () => void;

  /** Snapshot of cell positions BEFORE Space-mode was triggered.
   *  When non-null, `rollbackLayout` restores them. */
  originalPositions: Record<string, { x: number; y: number }> | null;
  /** Spread cells vertically one-per-slide. `slideHeight` defaults to
   *  the viewport height; pass an explicit value for testing. */
  spaceForPresentation: (slideHeight?: number) => void;
  /** Restore positions saved by `spaceForPresentation`. No-op if not spaced. */
  rollbackLayout: () => void;
  setSelected: (id: string | null) => void;
  moveCell: (id: string, x: number, y: number) => void;
  addCell: (partial?: Partial<Cell>) => string;
  addMarkdownCell: () => string;
  addMediaCell: (url: string) => string | null;
  addBrowserCell: (url: string) => string | null;
  addWhiteboardCell: () => string;
  addDiagramCell: () => string;
  duplicateCell: (id: string) => string | null;
  resizeCell: (id: string, w: number, h: number) => void;

  /** Which browser cell, if any, currently owns pointer events.
   *  Only one can be interactive at a time. */
  interactiveBrowserId: string | null;
  setInteractiveBrowser: (id: string | null) => void;
  deleteCell: (id: string) => void;
  /** Iter 33: delete every cell in the list in one shot. */
  deleteCells: (ids: string[]) => void;
  /** Iter 35: align / distribute the multi-selected cells.
   *  No-op when fewer than 2 cells are selected (distribute needs 3). */
  alignSelected: (
    mode:
      | "left"
      | "centerX"
      | "right"
      | "top"
      | "middleY"
      | "bottom"
      | "distH"
      | "distV",
  ) => void;
  runCell: (id: string) => Promise<void>;
  /** Iter 36: run every code cell in reading order, awaiting each
   *  one so the persistent kernel sees them sequentially. Stops on
   *  the first error so the user can investigate. Returns the id of
   *  the failed cell, or null on success. */
  runAllCells: () => Promise<string | null>;
  /** Iter 38: drop every cell's output panel + [n] badge. Does NOT
   *  reset the Python kernel — variables and imports survive so the
   *  next run can pick up where the last one left off. */
  clearAllOutputs: () => void;
  /** Iter 45: link two cells together. Symmetric — adds `to` into
   *  `from.links` and vice-versa. No-op when the link already exists
   *  or when either id is missing. */
  linkCells: (from: string, to: string) => void;
  /** Iter 45: drop a link between two cells (both directions). */
  unlinkCells: (from: string, to: string) => void;
  /** Iter 45: toolbar shortcut — when exactly 2 cells are selected,
   *  toggle the link between them. Returns true when a link now
   *  exists, false when it was just removed. */
  toggleLinkSelected: () => boolean;
  /** Iter 53: toggle a cell's collapsed-to-title state. */
  toggleCollapse: (id: string) => void;
  /** Iter 57: flip the collapsed flag on every cell at once. */
  setAllCollapsed: (collapsed: boolean) => void;
  /** Iter 62: Cmd+K palette visibility. */
  paletteOpen: boolean;
  setPaletteOpen: (on: boolean) => void;
  /** Iter 62: bumped when the palette picks a cell; Canvas listens
   *  to this counter to pan the viewport to the selected cell. */
  panToTick: number;
  panToCell: (id: string) => void;

  // ── file operations ─────────────────────────────────────────────
  newNotebook: () => void;
  loadNotebookFromText: (text: string) => Promise<void>;
  downloadNotebook: () => Promise<void>;
  /** Iter 84: "Save As" — always prompts for a fresh file location
   *  via showSaveFilePicker (when available), updates `fileHandle`,
   *  and writes the current text there. Falls back to a regular
   *  download when the File System Access API is unavailable. */
  saveNotebookAs: () => Promise<void>;
  /** Where this notebook is currently bound on disk (File System
   *  Access API). Held in memory only; lost on reload — that's OK,
   *  the browser also forgets the permission grant on reload. */
  fileHandle: FileSystemFileHandle | null;
  setFileHandle: (h: FileSystemFileHandle | null) => void;
}

const THEME_KEY = "doodle-v2-theme";
const AMBIENT_KEY = "doodle-v2-ambient";
const NOTEBOOK_KEY = "doodle-v2-notebook";
const AUTOSAVE_DEBOUNCE_MS = 300;

function initialTheme(): Theme {
  if (typeof window === "undefined") return "light";
  const saved = window.localStorage.getItem(THEME_KEY);
  if (saved === "light" || saved === "dark") return saved;
  return window.matchMedia?.("(prefers-color-scheme: dark)").matches ? "dark" : "light";
}

function applyTheme(t: Theme) {
  if (typeof document === "undefined") return;
  document.documentElement.classList.toggle("dark", t === "dark");
}

const SEED_CELL: Cell = {
  id: "c0",
  kind: "code",
  title: "Hello, Python",
  source: 'print("Hello from v2! 🎉")\nprint(2 + 2)',
  x: 80,
  y: 80,
};

interface PersistedShape {
  notebookName: string;
  cells: Cell[];
}

function loadPersisted(): PersistedShape | null {
  if (typeof window === "undefined") return null;
  try {
    const raw = localStorage.getItem(NOTEBOOK_KEY);
    if (!raw) return null;
    const obj = JSON.parse(raw) as PersistedShape;
    if (!obj || !Array.isArray(obj.cells)) return null;
    return obj;
  } catch {
    return null;
  }
}

let autosaveTimer: number | undefined;
function scheduleAutosave(shape: PersistedShape, onSaved: (ts: number) => void) {
  if (typeof window === "undefined") return;
  if (autosaveTimer) window.clearTimeout(autosaveTimer);
  autosaveTimer = window.setTimeout(() => {
    try {
      localStorage.setItem(NOTEBOOK_KEY, JSON.stringify(shape));
      onSaved(Date.now());
    } catch { /* quota — ignore */ }
  }, AUTOSAVE_DEBOUNCE_MS);
}

/** Tiny id generator. */
let _idSeq = 0;
function newId(): string {
  _idSeq += 1;
  return `c${Date.now().toString(36)}${_idSeq.toString(36)}`;
}

function spawnPosition(cells: Cell[]): { x: number; y: number } {
  const STEP = 40;
  const occupied = new Set(cells.map((c) => `${Math.round(c.x / STEP)}:${Math.round(c.y / STEP)}`));
  let x = 80, y = 80;
  for (let i = 0; i < 200; i++) {
    if (!occupied.has(`${Math.round(x / STEP)}:${Math.round(y / STEP)}`)) return { x, y };
    x += STEP;
    y += STEP;
  }
  return { x, y };
}

function triggerDownload(filename: string, text: string) {
  const blob = new Blob([text], { type: "text/x-python;charset=utf-8" });
  const url = URL.createObjectURL(blob);
  const a = document.createElement("a");
  a.href = url;
  a.download = filename;
  document.body.appendChild(a);
  a.click();
  document.body.removeChild(a);
  // Give the browser a tick to start the download before revoking.
  setTimeout(() => URL.revokeObjectURL(url), 1000);
}

export const useStore = create<AppState>((set, get) => {
  const theme = initialTheme();
  applyTheme(theme);
  const persisted = loadPersisted();
  // Normalize any legacy `explain` field into `callouts[0]` so the
  // rest of the app sees a single shape.
  const seedCells = (persisted?.cells ?? [SEED_CELL]).map((c) => {
    if (!c.callouts && c.explain) {
      return { ...c, callouts: [{ text: c.explain }], explain: undefined };
    }
    return c;
  });
  const seedName = persisted?.notebookName ?? "Untitled";

  /** Persist current notebook shape to localStorage (debounced). */
  const autosave = () => {
    const s = get();
    scheduleAutosave(
      { notebookName: s.notebookName, cells: s.cells },
      (ts) => set({ savedAt: ts }),
    );
  };

  return {
    theme,
    setTheme: (t) => {
      applyTheme(t);
      try { localStorage.setItem(THEME_KEY, t); } catch { /* private mode */ }
      set({ theme: t });
    },
    toggleTheme: () => get().setTheme(get().theme === "dark" ? "light" : "dark"),

    ambient: ((): AppState["ambient"] => {
      if (typeof window === "undefined") return "geometry";
      const v = window.localStorage.getItem(AMBIENT_KEY);
      if (v === "off" || v === "geometry" || v === "nature" || v === "science") return v;
      return "geometry";
    })(),
    setAmbient: (a) => {
      try { localStorage.setItem(AMBIENT_KEY, a); } catch { /* ignore */ }
      set({ ambient: a });
    },

    notebookName: seedName,
    setNotebookName: (n) => {
      set({ notebookName: n });
      autosave();
    },
    savedAt: persisted ? Date.now() : null,

    interactionMode: "select",
    setInteractionMode: (m) => set({ interactionMode: m }),

    cells: seedCells,
    runtimes: {},
    execCounter: 0,
    selectedId: null,
    selectedIds: [],
    setSelectedIds: (ids) =>
      // Iter 76: keep selectedId in sync with selectedIds. If the
      // previous primary is no longer in the new set, fall back to
      // the first member (or null when empty). Toolbar surfaces
      // bound to selectedId would otherwise still target a cell
      // the user just deselected — misleading state.
      set((s) => ({
        selectedIds: ids,
        selectedId:
          s.selectedId && ids.includes(s.selectedId)
            ? s.selectedId
            : ids[0] ?? null,
      })),
    renameTick: {},
    requestRename: (id) => {
      set((s) => ({ renameTick: { ...s.renameTick, [id]: (s.renameTick[id] ?? 0) + 1 } }));
    },

    setSource: (id, source) => {
      set((s) => ({ cells: s.cells.map((c) => (c.id === id ? { ...c, source } : c)) }));
      autosave();
    },
    setTitle: (id, title) => {
      set((s) => ({ cells: s.cells.map((c) => (c.id === id ? { ...c, title } : c)) }));
      autosave();
    },
    setDiagramKind: (id, kind) => {
      set((s) => ({ cells: s.cells.map((c) => (c.id === id ? { ...c, diagram_kind: kind } : c)) }));
      autosave();
    },
    setExplain: (id, text) => {
      // Backward-compat shim: a single-text "explain" is now stored
      // as the first entry of `callouts`. We don't carry the legacy
      // field forward.
      set((s) => ({
        cells: s.cells.map((c) => {
          if (c.id !== id) return c;
          if (!text || !text.trim()) {
            return { ...c, callouts: [], explain: undefined };
          }
          const existing = c.callouts ?? [];
          const next: Callout[] = existing.length
            ? [{ ...existing[0], text }, ...existing.slice(1)]
            : [{ text }];
          return { ...c, callouts: next, explain: undefined };
        }),
      }));
      autosave();
    },
    setCallouts: (id, callouts) => {
      set((s) => ({
        cells: s.cells.map((c) =>
          c.id === id ? { ...c, callouts: callouts.filter((co) => co.text.trim() || co.image), explain: undefined } : c,
        ),
      }));
      autosave();
    },
    calloutEditorCellId: null,
    openCalloutEditor: (id) => set({ calloutEditorCellId: id }),
    installOpen: false,
    setInstallOpen: (on) => set({ installOpen: on }),

    presenting: false,
    focusedCellId: null,
    setPresenting: (on) => {
      const s = get();
      // Auto-focus the first cell when entering presentation so the
      // canvas pans immediately instead of dropping the user wherever
      // they happened to be panned.
      if (on && !s.focusedCellId) {
        const first = s.cellsInOrder()[0];
        // Iter 78: keep selectedId ⊂ selectedIds (rule 21e).
        if (first) set({ presenting: true, focusedCellId: first.id, selectedId: first.id, selectedIds: [first.id] });
        else set({ presenting: true });
      } else {
        set({ presenting: on });
      }
      // Leaving presentation kills any active ink tool and triggers
      // a global ink wipe.
      if (!on) {
        set((s2) => ({
          presenterTool: "none",
          presenterClearCounter: s2.presenterClearCounter + 1,
        }));
      }
    },
    focusCell: (id) =>
      // Iter 78: rule 21e — primary mirrors into selectedIds.
      set({ focusedCellId: id, selectedId: id, selectedIds: id ? [id] : [] }),
    cellsInOrder: () => {
      // Sort by row (y bucketed) first, then x. Bucket width tolerates
      // small vertical jitter so two cells "on the same row" stay
      // left-to-right even when their y differs by 20px.
      const BUCKET = 40;
      return [...get().cells].sort((a, b) => {
        const ay = Math.round(a.y / BUCKET);
        const by = Math.round(b.y / BUCKET);
        if (ay !== by) return ay - by;
        return a.x - b.x;
      });
    },
    nextCell: () => {
      const ordered = get().cellsInOrder();
      if (!ordered.length) return;
      const idx = ordered.findIndex((c) => c.id === get().focusedCellId);
      const next = idx < 0 ? ordered[0] : ordered[Math.min(ordered.length - 1, idx + 1)];
      // Iter 78: rule 21e.
      set({ focusedCellId: next.id, selectedId: next.id, selectedIds: [next.id] });
    },
    prevCell: () => {
      const ordered = get().cellsInOrder();
      if (!ordered.length) return;
      const idx = ordered.findIndex((c) => c.id === get().focusedCellId);
      const prev = idx <= 0 ? ordered[0] : ordered[idx - 1];
      // Iter 78: rule 21e.
      set({ focusedCellId: prev.id, selectedId: prev.id, selectedIds: [prev.id] });
    },

    presenterTool: "none",
    setPresenterTool: (t) => set({ presenterTool: t }),
    fullscreen: false,
    setFullscreen: (on) => set({ fullscreen: on }),
    presenterClearCounter: 0,
    clearPresenterInk: () =>
      set((s) => ({ presenterClearCounter: s.presenterClearCounter + 1 })),

    originalPositions: null,
    spaceForPresentation: (slideHeight) => {
      const s = get();
      const H = slideHeight ?? (typeof window !== "undefined" ? window.innerHeight : 800);
      const ordered = s.cellsInOrder();
      if (!ordered.length) return;
      // Snapshot current positions exactly once. Re-pressing S
      // re-spreads but doesn't overwrite the original snapshot, so
      // Together always goes back to the user's hand-placed layout.
      const snapshot: Record<string, { x: number; y: number }> =
        s.originalPositions ?? Object.fromEntries(s.cells.map((c) => [c.id, { x: c.x, y: c.y }]));
      // Map each cell to (60, i * slideGap) in reading order.
      const SLIDE_X = 60;
      const newPos = new Map<string, { x: number; y: number }>();
      ordered.forEach((c, i) => {
        newPos.set(c.id, { x: SLIDE_X, y: i * H });
      });
      set({
        originalPositions: snapshot,
        cells: s.cells.map((c) => {
          const p = newPos.get(c.id);
          return p ? { ...c, x: p.x, y: p.y } : c;
        }),
      });
      autosave();
    },
    rollbackLayout: () => {
      const s = get();
      if (!s.originalPositions) return;
      const snap = s.originalPositions;
      set({
        originalPositions: null,
        cells: s.cells.map((c) => {
          const p = snap[c.id];
          return p ? { ...c, x: p.x, y: p.y } : c;
        }),
      });
      autosave();
    },
    setSelected: (id) =>
      set({ selectedId: id, selectedIds: id ? [id] : [] }),
    moveCell: (id, x, y) => {
      set((s) => ({ cells: s.cells.map((c) => (c.id === id ? { ...c, x, y } : c)) }));
      autosave();
    },
    addCell: (partial = {}) => {
      const id = newId();
      const { x, y } = spawnPosition(get().cells);
      const next: Cell = {
        id,
        kind: "code",
        title: "New cell",
        source: 'print("…")',
        x,
        y,
        ...partial,
      };
      // Iter 78: rule 21e — primary mirrors into selectedIds.
      set((s) => ({ cells: [...s.cells, next], selectedId: id, selectedIds: [id] }));
      autosave();
      return id;
    },
    addMarkdownCell: () => {
      return get().addCell({
        kind: "markdown",
        title: "Notes",
        source: "# Heading\n\nWrite **markdown** here. Use `code` and bullets:\n\n- one\n- two\n- three",
      });
    },
    addMediaCell: (url) => {
      const trimmed = url.trim();
      if (!trimmed) return null;
      return get().addCell({
        kind: "media",
        title: undefined,                         // media cells are frameless
        source: trimmed,
        w: 480,
        h: 320,
      });
    },
    addBrowserCell: (url) => {
      const trimmed = url.trim();
      if (!trimmed) return null;
      const normalized = /^https?:\/\//i.test(trimmed) ? trimmed : `https://${trimmed}`;
      return get().addCell({
        kind: "browser",
        title: normalized.replace(/^https?:\/\//, "").split("/")[0],
        source: normalized,
        w: 720,
        h: 480,
      });
    },

    interactiveBrowserId: null,
    setInteractiveBrowser: (id) => set({ interactiveBrowserId: id }),

    addWhiteboardCell: () => {
      return get().addCell({
        kind: "whiteboard",
        title: "Whiteboard",
        // Empty whiteboard — strokes will be a JSON-encoded
        // { bg, strokes: [] } payload once the user draws.
        source: JSON.stringify({ bg: "light", strokes: [] }),
        w: 640,
        h: 420,
      });
    },
    addDiagramCell: () => {
      return get().addCell({
        kind: "diagram",
        title: "Diagram",
        diagram_kind: "doodle",
        // Default to the doodle flow + chart format — that's the
        // visual style the user actually wants. Mermaid stays
        // available via the kind selector in the cell header.
        source:
          "flowchart\n" +
          "Idea --> Sketch\n" +
          "Sketch --> Try it\n" +
          "Try it --> Ship\n" +
          "\n" +
          "chart: Demo energy\n" +
          "Idea: 6\n" +
          "Sketch: 8\n" +
          "Try it: 9\n" +
          "Ship: 10",
        w: 720,
        h: 520,
      });
    },
    resizeCell: (id, w, h) => {
      set((s) => ({
        cells: s.cells.map((c) =>
          c.id === id ? { ...c, w: Math.max(120, w), h: Math.max(80, h) } : c,
        ),
      }));
      autosave();
    },
    duplicateCell: (id) => {
      const src = get().cells.find((c) => c.id === id);
      if (!src) return null;
      const dupId = newId();
      const dup: Cell = {
        ...src,
        id: dupId,
        x: src.x + 40,
        y: src.y + 40,
        title: src.title ? `${src.title} (copy)` : "Copy",
        // Iter 60: drop outgoing links — otherwise the copy would
        // inherit edges asymmetrically (target cells wouldn't know
        // about the duplicate). User can re-link explicitly via 🔗.
        links: [],
        // Iter 60: deep-clone the callouts array so editing a bubble
        // on the duplicate doesn't mutate the source's bubble.
        callouts: src.callouts ? src.callouts.map((co) => ({ ...co })) : undefined,
      };
      // Iter 78: rule 21e.
      set((s) => ({ cells: [...s.cells, dup], selectedId: dupId, selectedIds: [dupId] }));
      autosave();
      return dupId;
    },
    deleteCell: (id) => {
      set((s) => {
        // Iter 45: drop any link referencing the deleted cell so we
        // don't leak dangling endpoints into the saved file.
        const cells = s.cells
          .filter((c) => c.id !== id)
          .map((c) =>
            c.links?.includes(id) ? { ...c, links: c.links.filter((x) => x !== id) } : c,
          );
        const { [id]: _drop, ...runtimes } = s.runtimes;
        const selectedId = s.selectedId === id ? null : s.selectedId;
        const selectedIds = s.selectedIds.filter((sid) => sid !== id);
        return { cells, runtimes, selectedId, selectedIds };
      });
      autosave();
    },
    alignSelected: (mode) => {
      const s = get();
      const ids = s.selectedIds;
      if (ids.length < 2) return;
      const idSet = new Set(ids);
      // Approx dimensions when w/h aren't set yet — matches the
      // CELL_WIDTH_FALLBACK in Canvas.tsx.
      const widthOf = (c: Cell) =>
        c.w ?? (c.kind === "code" ? 580 : c.kind === "markdown" ? 560 : 560);
      const heightOf = (c: Cell) => c.h ?? 360;
      const picked = s.cells.filter((c) => idSet.has(c.id));
      if (picked.length < 2) return;

      const lefts = picked.map((c) => c.x);
      const rights = picked.map((c) => c.x + widthOf(c));
      const tops = picked.map((c) => c.y);
      const bottoms = picked.map((c) => c.y + heightOf(c));
      const L = Math.min(...lefts);
      const R = Math.max(...rights);
      const T = Math.min(...tops);
      const B = Math.max(...bottoms);
      const cx = (L + R) / 2;
      const cy = (T + B) / 2;

      const updates = new Map<string, { x: number; y: number }>();

      if (mode === "left") {
        for (const c of picked) updates.set(c.id, { x: L, y: c.y });
      } else if (mode === "right") {
        for (const c of picked) updates.set(c.id, { x: R - widthOf(c), y: c.y });
      } else if (mode === "centerX") {
        for (const c of picked) updates.set(c.id, { x: cx - widthOf(c) / 2, y: c.y });
      } else if (mode === "top") {
        for (const c of picked) updates.set(c.id, { x: c.x, y: T });
      } else if (mode === "bottom") {
        for (const c of picked) updates.set(c.id, { x: c.x, y: B - heightOf(c) });
      } else if (mode === "middleY") {
        for (const c of picked) updates.set(c.id, { x: c.x, y: cy - heightOf(c) / 2 });
      } else if (mode === "distH" && picked.length >= 3) {
        const sorted = [...picked].sort((a, b) => a.x - b.x);
        const totalW = sorted.reduce((sum, c) => sum + widthOf(c), 0);
        const span = R - L;
        const gap = (span - totalW) / (sorted.length - 1);
        let cursor = L;
        for (const c of sorted) {
          updates.set(c.id, { x: cursor, y: c.y });
          cursor += widthOf(c) + gap;
        }
      } else if (mode === "distV" && picked.length >= 3) {
        const sorted = [...picked].sort((a, b) => a.y - b.y);
        const totalH = sorted.reduce((sum, c) => sum + heightOf(c), 0);
        const span = B - T;
        const gap = (span - totalH) / (sorted.length - 1);
        let cursor = T;
        for (const c of sorted) {
          updates.set(c.id, { x: c.x, y: cursor });
          cursor += heightOf(c) + gap;
        }
      } else {
        return; // distH/distV with <3 cells
      }

      set((st) => ({
        cells: st.cells.map((c) =>
          updates.has(c.id) ? { ...c, ...updates.get(c.id)! } : c,
        ),
      }));
      autosave();
    },
    deleteCells: (ids) => {
      if (!ids.length) return;
      const drop = new Set(ids);
      set((s) => {
        const cells = s.cells.filter((c) => !drop.has(c.id));
        const runtimes = { ...s.runtimes };
        for (const id of ids) delete runtimes[id];
        const selectedId = s.selectedId && drop.has(s.selectedId) ? null : s.selectedId;
        const selectedIds = s.selectedIds.filter((sid) => !drop.has(sid));
        return { cells, runtimes, selectedId, selectedIds };
      });
      autosave();
    },

    runCell: async (id) => {
      const cell = get().cells.find((c) => c.id === id);
      if (!cell) return;
      set((s) => ({
        runtimes: {
          ...s.runtimes,
          [id]: {
            running: true,
            result: s.runtimes[id]?.result,
            execCount: s.runtimes[id]?.execCount,
          },
        },
      }));
      try {
        const result = await executeCode(cell.source);
        // Iter 37: bump the global execution counter and stamp the
        // new number on this cell's runtime.
        const next = (get().execCounter ?? 0) + 1;
        set((s) => ({
          execCounter: next,
          runtimes: { ...s.runtimes, [id]: { running: false, result, execCount: next } },
        }));
      } catch (e) {
        const next = (get().execCounter ?? 0) + 1;
        set((s) => ({
          execCounter: next,
          runtimes: {
            ...s.runtimes,
            [id]: {
              running: false,
              result: { status: "error", elapsed_ms: 0, outputs: [{ type: "error", text: String(e) }] },
              execCount: next,
            },
          },
        }));
      }
    },

    clearAllOutputs: () => {
      set({ runtimes: {} });
    },

    linkCells: (from, to) => {
      if (!from || !to || from === to) return;
      set((s) => {
        const cells = s.cells.map((c) => {
          if (c.id === from) {
            const list = c.links ?? [];
            if (list.includes(to)) return c;
            return { ...c, links: [...list, to] };
          }
          if (c.id === to) {
            // Track the reverse so deletion of one endpoint
            // still cleans up — but the visual is a single line.
            const list = c.links ?? [];
            if (list.includes(from)) return c;
            return { ...c, links: [...list, from] };
          }
          return c;
        });
        return { cells };
      });
      autosave();
    },
    unlinkCells: (from, to) => {
      if (!from || !to) return;
      set((s) => {
        const cells = s.cells.map((c) => {
          if (c.id === from && c.links?.includes(to)) {
            return { ...c, links: c.links.filter((id) => id !== to) };
          }
          if (c.id === to && c.links?.includes(from)) {
            return { ...c, links: c.links.filter((id) => id !== from) };
          }
          return c;
        });
        return { cells };
      });
      autosave();
    },
    toggleLinkSelected: () => {
      const s = get();
      if (s.selectedIds.length !== 2) return false;
      const [a, b] = s.selectedIds;
      const cellA = s.cells.find((c) => c.id === a);
      const linked = !!cellA?.links?.includes(b);
      if (linked) {
        s.unlinkCells(a, b);
        return false;
      }
      s.linkCells(a, b);
      return true;
    },
    toggleCollapse: (id) => {
      set((s) => ({
        cells: s.cells.map((c) =>
          c.id === id ? { ...c, collapsed: !c.collapsed } : c,
        ),
      }));
      autosave();
    },
    setAllCollapsed: (collapsed) => {
      set((s) => ({
        cells: s.cells.map((c) => (c.collapsed === collapsed ? c : { ...c, collapsed })),
      }));
      autosave();
    },
    paletteOpen: false,
    setPaletteOpen: (on) => set({ paletteOpen: on }),
    panToTick: 0,
    panToCell: (id) => {
      set((s) => ({ selectedId: id, selectedIds: [id], panToTick: s.panToTick + 1 }));
    },

    runAllCells: async () => {
      const ordered = get().cellsInOrder().filter((c) => c.kind === "code");
      for (const c of ordered) {
        await get().runCell(c.id);
        const r = get().runtimes[c.id]?.result;
        if (r && r.status === "error") return c.id;
      }
      return null;
    },

    newNotebook: () => {
      set({
        notebookName: "Untitled",
        cells: [{ ...SEED_CELL, id: "c0" }],
        runtimes: {},
        execCounter: 0,
        selectedId: null,
        selectedIds: [],
      });
      autosave();
    },

    loadNotebookFromText: async (text) => {
      const r = await openNotebook(text);
      set({
        notebookName: r.notebook.name || "Untitled",
        cells: r.notebook.cells.map((c) => {
          const co = (c as Cell).callouts ?? [];
          const legacy = (c as Cell).explain;
          const callouts = co.length
            ? co
            : legacy
            ? [{ text: legacy } as Callout]
            : [];
          return {
            id: c.id,
            kind: c.kind ?? "code",
            source: c.source,
            title: c.title,
            x: c.x,
            y: c.y,
            w: c.w,
            h: c.h,
            diagram_kind: (c as Cell).diagram_kind,
            callouts,
            // Iter 45: outgoing cell-to-cell links.
            links: (c as Cell).links ?? [],
            // Iter 54: collapsed UI state from `# @collapsed:`.
            collapsed: (c as Cell).collapsed ?? false,
          };
        }),
        runtimes: {},
        execCounter: 0,
        selectedId: null,
        selectedIds: [],
      });
      autosave();
    },

    downloadNotebook: async () => {
      const s = get();
      const r = await saveNotebook({
        name: s.notebookName,
        cells: s.cells,
      });
      // If we have a live disk handle, write back silently. Otherwise
      // trigger a browser download (legacy / fallback path).
      if (s.fileHandle) {
        try {
          const w = await s.fileHandle.createWritable();
          await w.write(r.text);
          await w.close();
          set({ savedAt: Date.now() });
          return;
        } catch (err) {
          // Permission revoked or other write error — fall back to download.
          console.warn("Disk write failed, falling back to download:", err);
        }
      }
      const safe = (s.notebookName || "Untitled").replace(/[^A-Za-z0-9_-]+/g, "_");
      triggerDownload(`${safe}.py`, r.text);
      set({ savedAt: Date.now() });
    },

    saveNotebookAs: async () => {
      const s = get();
      const r = await saveNotebook({ name: s.notebookName, cells: s.cells });
      const safe = (s.notebookName || "Untitled").replace(/[^A-Za-z0-9_-]+/g, "_");
      // File System Access API is only on Chromium-family browsers.
      const w = (window as unknown as { showSaveFilePicker?: (opts?: unknown) => Promise<FileSystemFileHandle> });
      if (w.showSaveFilePicker) {
        try {
          const handle = await w.showSaveFilePicker({
            suggestedName: `${safe}.py`,
            types: [{ description: "DoodleCode notebook", accept: { "text/x-python": [".py"] } }],
          });
          const writable = await handle.createWritable();
          await writable.write(r.text);
          await writable.close();
          // Iter 87: sync notebookName from the picked file name so
          // the toolbar reflects what's actually on disk. Strip the
          // .py extension; ignore an empty handle.name just in case.
          const picked = handle.name?.replace(/\.py$/, "");
          set({
            fileHandle: handle,
            savedAt: Date.now(),
            ...(picked ? { notebookName: picked } : {}),
          });
          return;
        } catch (err) {
          // AbortError means the user cancelled — silent return.
          if ((err as { name?: string })?.name === "AbortError") return;
          console.warn("Save As failed, falling back to download:", err);
        }
      }
      triggerDownload(`${safe}.py`, r.text);
      set({ savedAt: Date.now() });
    },

    fileHandle: null,
    setFileHandle: (h) => set({ fileHandle: h }),
  };
});
