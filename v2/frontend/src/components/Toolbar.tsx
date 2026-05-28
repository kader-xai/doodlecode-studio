import { useEffect, useState } from "react";
import { useStore } from "../store";
import { resetKernel } from "../api";
import { AmbientPicker } from "./AmbientPicker";
import { FileMenu } from "./FileMenu";
import { ThemeToggle } from "./ThemeToggle";

/**
 * Top toolbar.
 *
 * Hard rule (learned from v1): action buttons live in ONE place —
 * here — and read the current selection from the store. No per-card
 * Edit/Delete/Callout buttons anywhere.
 */
export function Toolbar({ version, onHelp }: { version: string | null; onHelp: () => void }) {
  const presenting = useStore((s) => s.presenting);
  const setPresenting = useStore((s) => s.setPresenting);
  const spaced = useStore((s) => s.originalPositions !== null);
  const spaceForPresentation = useStore((s) => s.spaceForPresentation);
  const rollbackLayout = useStore((s) => s.rollbackLayout);
  const mode = useStore((s) => s.interactionMode);
  const setMode = useStore((s) => s.setInteractionMode);
  const addCell = useStore((s) => s.addCell);
  const addMarkdownCell = useStore((s) => s.addMarkdownCell);
  const addMediaCell = useStore((s) => s.addMediaCell);
  const addBrowserCell = useStore((s) => s.addBrowserCell);
  const addWhiteboardCell = useStore((s) => s.addWhiteboardCell);
  const addDiagramCell = useStore((s) => s.addDiagramCell);
  const deleteCell = useStore((s) => s.deleteCell);
  const openCalloutEditor = useStore((s) => s.openCalloutEditor);
  const resizeCell = useStore((s) => s.resizeCell);
  const selectedId = useStore((s) => s.selectedId);
  const selectedIds = useStore((s) => s.selectedIds);
  const alignSelected = useStore((s) => s.alignSelected);
  const setAllCollapsed = useStore((s) => s.setAllCollapsed);
  const allCollapsed = useStore(
    (s) => s.cells.length > 0 && s.cells.every((c) => c.collapsed),
  );
  const toggleLinkSelected = useStore((s) => s.toggleLinkSelected);
  const selectedPairLinked = useStore((s) => {
    if (s.selectedIds.length !== 2) return false;
    const [a, b] = s.selectedIds;
    const ca = s.cells.find((c) => c.id === a);
    return !!ca?.links?.includes(b);
  });
  const selectedTitle = useStore((s) =>
    s.cells.find((c) => c.id === s.selectedId)?.title ?? null,
  );
  const selectedHasCallouts = useStore((s) => {
    const cell = s.cells.find((c) => c.id === s.selectedId);
    return !!(cell?.callouts && cell.callouts.length > 0);
  });
  const notebookName = useStore((s) => s.notebookName);
  const savedAt = useStore((s) => s.savedAt);

  // Refresh the "saved Xs ago" label every second.
  const [, tick] = useState(0);
  useEffect(() => {
    const t = setInterval(() => tick((n) => n + 1), 1000);
    return () => clearInterval(t);
  }, []);

  const onDelete = () => {
    if (!selectedId) return;
    const ok = window.confirm(`Delete "${selectedTitle ?? selectedId}"?`);
    if (ok) deleteCell(selectedId);
  };

  const onCallout = () => {
    if (!selectedId) return;
    openCalloutEditor(selectedId);
  };

  const savedLabel = savedAt
    ? `saved ${Math.max(1, Math.round((Date.now() - savedAt) / 1000))}s ago`
    : "not saved yet";

  // Hide the whole top toolbar during presentation — PresenterBar
  // takes over and the audience shouldn't see editing chrome.
  if (presenting) return null;

  return (
    <header className="absolute top-3 left-3 right-3 z-30 flex items-start justify-between pointer-events-none">
      <div className="flex flex-col gap-1 pointer-events-auto">
        <div className="flex items-center gap-2 bg-white/70 dark:bg-[#262a31]/70 backdrop-blur px-3 py-1.5 rounded-xl border-2 border-ink/40 dark:border-white/30 shadow-sketch">
          <span className="font-hand text-3xl select-none leading-none">📓 DoodleCode</span>
          <span className="font-hand text-3xl text-[#c2255c] dark:text-[#fcc2d7] leading-none">Studio</span>
          <span className="font-mono text-xs ml-1 px-1.5 py-0.5 rounded-md border-2 border-ink/40 dark:border-white/40 bg-white/80 dark:bg-black/40">
            v{version ?? "…"}
          </span>

          <span className="mx-1 h-6 w-px bg-ink/30 dark:bg-white/30" />

          {/* Two tool modes: drag cells (default) or pan the canvas. */}
          <div className="flex gap-0.5 rounded-lg border-2 border-ink/40 dark:border-white/40 p-0.5 bg-white/40 dark:bg-black/30">
            {([
              { id: "select", label: "➤", title: "Select (V) — drag cells to move, click selects" },
              { id: "hand",   label: "✋", title: "Hand (H) — drag empty space to pan the canvas" },
            ] as const).map((t) => (
              <button
                key={t.id}
                title={t.title}
                onClick={() => setMode(t.id)}
                className={`w-7 h-7 rounded-md border-2 text-base font-hand transition ${
                  mode === t.id
                    ? "bg-marker-yellow border-ink dark:bg-amber-700 dark:border-white text-ink dark:text-white shadow-sketch"
                    : "bg-white/70 dark:bg-[#1f2228] border-ink/30 dark:border-white/30 text-ink/70 dark:text-white/70 hover:translate-y-[1px]"
                }`}
              >
                {t.label}
              </button>
            ))}
          </div>

          <FileMenu />

          <button
            onClick={() => (spaced ? rollbackLayout() : spaceForPresentation())}
            className={`font-hand text-xl px-3 py-0.5 rounded-lg border-2 border-ink dark:border-white/70 ${
              spaced
                ? "bg-marker-mint dark:bg-[#2b8a3e]"
                : "bg-marker-violet dark:bg-[#5f3dc4]"
            } text-ink dark:text-white shadow-sketch hover:translate-y-[1px] transition`}
            title={spaced ? "Pack cells together (S)" : "Spread cells one-per-slide for presenting (S)"}
          >
            {spaced ? "🔗 Together" : "📐 Space"}
          </button>
          <button
            onClick={() => setPresenting(true)}
            className="font-hand text-xl px-3 py-0.5 rounded-lg border-2 border-ink dark:border-white/70 bg-marker-pink dark:bg-[#a61e4d] text-ink dark:text-white shadow-sketch hover:translate-y-[1px] transition"
            title="Enter presentation mode (F5 / Shift+P)"
          >
            🎬 Present
          </button>

          <button
            onClick={() => addCell()}
            className="font-hand text-xl px-3 py-0.5 rounded-lg border-2 border-ink dark:border-white/70 bg-marker-sky dark:bg-[#1864ab] text-ink dark:text-white shadow-sketch hover:translate-y-[1px] transition"
            title="Add a new code cell (N)"
          >
            ＋ Code
          </button>
          <button
            onClick={() => addMarkdownCell()}
            className="font-hand text-xl px-3 py-0.5 rounded-lg border-2 border-ink dark:border-white/70 bg-marker-yellow dark:bg-amber-700 text-ink dark:text-white shadow-sketch hover:translate-y-[1px] transition"
            title="Add a new text / markdown cell (T)"
          >
            ＋ Text
          </button>
          <button
            onClick={() => {
              const url = window.prompt(
                "Image or video URL\n(.png, .jpg, .gif, .mp4, .webm, .mov, YouTube, Vimeo…)",
                "",
              );
              if (url != null && url.trim()) addMediaCell(url);
            }}
            className="font-hand text-xl px-3 py-0.5 rounded-lg border-2 border-ink dark:border-white/70 bg-marker-violet dark:bg-[#5f3dc4] text-ink dark:text-white shadow-sketch hover:translate-y-[1px] transition"
            title="Add an image or video cell from a URL (M)"
          >
            ＋ Media
          </button>
          <button
            onClick={() => {
              const url = window.prompt("Website URL", "https://example.com");
              if (url != null && url.trim()) addBrowserCell(url);
            }}
            className="font-hand text-xl px-3 py-0.5 rounded-lg border-2 border-ink dark:border-white/70 bg-marker-peach dark:bg-[#9a4f10] text-ink dark:text-white shadow-sketch hover:translate-y-[1px] transition"
            title="Add a browser cell (live website) (W)"
          >
            ＋ Browser
          </button>
          <button
            onClick={() => addWhiteboardCell()}
            className="font-hand text-xl px-3 py-0.5 rounded-lg border-2 border-ink dark:border-white/70 bg-marker-mint dark:bg-[#2b8a3e] text-ink dark:text-white shadow-sketch hover:translate-y-[1px] transition"
            title="Add a whiteboard cell (draw + highlight) (D)"
          >
            ＋ Draw
          </button>
          <button
            onClick={() => addDiagramCell()}
            className="font-hand text-xl px-3 py-0.5 rounded-lg border-2 border-ink dark:border-white/70 bg-marker-pink dark:bg-[#a61e4d] text-ink dark:text-white shadow-sketch hover:translate-y-[1px] transition"
            title="Add a Mermaid diagram cell (G)"
          >
            ＋ Diagram
          </button>

          <span className="mx-1 h-6 w-px bg-ink/30 dark:bg-white/30" />

          {/* Iter 36: Run All Cells — sequential execution against the
           *  persistent kernel. Same as clicking ▶ on every code cell
           *  in reading order. */}
          <button
            onClick={async () => {
              const failed = await useStore.getState().runAllCells();
              if (failed) {
                const t =
                  useStore.getState().cells.find((c) => c.id === failed)?.title ??
                  failed;
                window.alert(`Run All stopped at "${t}" — see its output for the error.`);
              }
            }}
            className="font-hand text-xl px-3 py-0.5 rounded-lg border-2 border-ink dark:border-white/70 bg-marker-green dark:bg-emerald-700 text-ink dark:text-white shadow-sketch hover:translate-y-[1px] transition"
            title="Run every code cell top-to-bottom (Cmd/Ctrl+Shift+Enter)"
          >
            ▶▶ Run All
          </button>
          {/* Iter 38: Clear Outputs — drops every output panel + [n]
           *  badge in one shot. Kernel state untouched. */}
          <button
            onClick={() => {
              if (window.confirm("Clear every cell's output? (Variables in the kernel survive.)")) {
                useStore.getState().clearAllOutputs();
              }
            }}
            className="font-hand text-xl px-3 py-0.5 rounded-lg border-2 border-ink dark:border-white/70 bg-marker-peach/70 dark:bg-amber-800 text-ink dark:text-white shadow-sketch hover:translate-y-[1px] transition"
            title="Clear all outputs (Cmd/Ctrl+Shift+L). Kernel variables stay alive."
          >
            🧹 Clear
          </button>
          {/* Iter 75: Collapse-all / Expand-all toggle. Label flips
           *  based on the current state so a single button covers
           *  both Cmd/Ctrl+Shift+[ and ]. */}
          <button
            onClick={() => setAllCollapsed(!allCollapsed)}
            className="font-hand text-xl px-3 py-0.5 rounded-lg border-2 border-ink dark:border-white/70 bg-white/80 dark:bg-[#1f2228] text-ink dark:text-white shadow-sketch hover:translate-y-[1px] transition"
            title={allCollapsed ? "Expand every cell (Cmd/Ctrl+Shift+])" : "Collapse every cell (Cmd/Ctrl+Shift+[)"}
          >
            {allCollapsed ? "▸ All" : "▾ All"}
          </button>
          <button
            onClick={() => useStore.getState().setInstallOpen(true)}
            className="font-hand text-xl px-3 py-0.5 rounded-lg border-2 border-ink dark:border-white/70 bg-marker-violet dark:bg-[#5f3dc4] text-ink dark:text-white shadow-sketch hover:translate-y-[1px] transition"
            title="pip install Python packages into the kernel"
          >
            📦 Install
          </button>
          <button
            onClick={async () => {
              if (!window.confirm("Restart the Python kernel? All variables and imports will be wiped.")) return;
              try {
                await resetKernel();
                // Iter 37: also reset the in-memory execution counter
                // + per-cell badges so [n] starts back at [1].
                useStore.setState((s) => {
                  const cleared: typeof s.runtimes = {};
                  for (const k of Object.keys(s.runtimes)) {
                    const r = s.runtimes[k];
                    cleared[k] = { ...r, execCount: undefined };
                  }
                  return { execCounter: 0, runtimes: cleared };
                });
              } catch (err) {
                window.alert(`Could not reset kernel: ${err}`);
              }
            }}
            className="font-hand text-xl px-3 py-0.5 rounded-lg border-2 border-ink dark:border-white/70 bg-marker-peach dark:bg-[#9a4f10] text-ink dark:text-white shadow-sketch hover:translate-y-[1px] transition"
            title="Restart the Python kernel — wipes variables, imports, and any leftover state"
          >
            ↻ Kernel
          </button>
          <button
            onClick={onCallout}
            disabled={!selectedId}
            className="font-hand text-xl px-3 py-0.5 rounded-lg border-2 border-ink dark:border-white/70 bg-marker-yellow dark:bg-amber-700 text-ink dark:text-white shadow-sketch hover:translate-y-[1px] transition disabled:opacity-40 disabled:cursor-not-allowed"
            title={selectedId ? (selectedHasCallouts ? "Edit callouts (C)" : "Add callouts (C)") : "Click a cell to select it first"}
          >
            💬 {selectedHasCallouts ? "Edit Callouts" : "Callouts"}
          </button>
          <button
            onClick={onDelete}
            disabled={!selectedId}
            className="font-hand text-xl px-3 py-0.5 rounded-lg border-2 border-ink dark:border-white/70 bg-marker-pink dark:bg-[#a61e4d] text-ink dark:text-white shadow-sketch hover:translate-y-[1px] transition disabled:opacity-40 disabled:cursor-not-allowed"
            title={selectedId ? "Delete selected cell (Backspace / Delete)" : "Click a cell to select it first"}
          >
            🗑 Delete
          </button>

          {/* Iter 35: Align + distribute bar — only when 2+ cells are
           *  multi-selected. Hidden in single-selection so it doesn't
           *  clutter the toolbar. */}
          {selectedIds.length >= 2 && (
            <div
              className="ml-1 flex items-center gap-0.5 rounded-md border-2 border-ink/30 dark:border-white/30 p-0.5 bg-white/60 dark:bg-black/30"
              title={`Align ${selectedIds.length} cells`}
            >
              <span className="font-hand text-xs px-1 text-ink/60 dark:text-white/60">
                Align
              </span>
              {([
                { k: "left", icon: "⇤", t: "Align left edges" },
                { k: "centerX", icon: "↔", t: "Center horizontally" },
                { k: "right", icon: "⇥", t: "Align right edges" },
                { k: "top", icon: "⇡", t: "Align top edges" },
                { k: "middleY", icon: "↕", t: "Center vertically" },
                { k: "bottom", icon: "⇣", t: "Align bottom edges" },
                { k: "distH", icon: "⇿", t: "Distribute horizontally (≥3)" },
                { k: "distV", icon: "⇕", t: "Distribute vertically (≥3)" },
              ] as const).map((b) => (
                <button
                  key={b.k}
                  type="button"
                  onClick={() => alignSelected(b.k)}
                  disabled={
                    (b.k === "distH" || b.k === "distV") && selectedIds.length < 3
                  }
                  title={b.t}
                  className="font-hand text-base leading-none px-1.5 py-0.5 rounded border-2 border-ink/30 dark:border-white/30 bg-white/80 dark:bg-[#1f2228] text-ink dark:text-white hover:bg-marker-yellow/60 dark:hover:bg-amber-700/40 transition disabled:opacity-30 disabled:cursor-not-allowed"
                >
                  {b.icon}
                </button>
              ))}
            </div>
          )}

          {/* Iter 67: multi-select count chip so the user can see at
           *  a glance how many cells are about to be hit by a bulk
           *  action (Delete, Cmd+D duplicate, Align, …). */}
          {selectedIds.length >= 2 && (
            <span
              className="font-hand text-sm px-2 py-0.5 rounded-md border-2 border-ink/40 dark:border-white/30 bg-marker-yellow/40 dark:bg-amber-700/40 text-ink dark:text-white shrink-0"
              title="Selected — Delete / Cmd+D / Align act on the whole group"
            >
              ▣ {selectedIds.length} cells selected
            </span>
          )}

          {/* Iter 45: Link / Unlink — only when exactly two cells are
           *  selected. Single click toggles a sketchy connector
           *  between them; ConnectionsLayer draws the line. */}
          {selectedIds.length === 2 && (
            <button
              type="button"
              onClick={() => toggleLinkSelected()}
              title={selectedPairLinked ? "Unlink these two cells" : "Link these two cells"}
              className="font-hand text-xl px-3 py-0.5 rounded-lg border-2 border-ink dark:border-white/70 bg-marker-violet/80 dark:bg-[#5f3dc4] text-ink dark:text-white shadow-sketch hover:translate-y-[1px] transition"
            >
              {selectedPairLinked ? "⛓‍💥 Unlink" : "🔗 Link"}
            </button>
          )}

          {selectedId && (
            <>
              <span
                className="ml-2 font-hand text-sm px-2 py-0.5 rounded-md border-2 border-ink/30 dark:border-white/30 bg-white/80 dark:bg-black/40 max-w-[180px] truncate"
                title={`Selected: ${selectedTitle ?? selectedId}`}
              >
                ▸ {selectedTitle ?? selectedId.slice(0, 6)}
              </span>
              {/* Size presets — quick alternative to dragging the
               *  corner. Useful for setting cells to slide-friendly
               *  proportions. */}
              <div className="ml-1 flex gap-0.5 rounded-md border-2 border-ink/30 dark:border-white/30 p-0.5 bg-white/50 dark:bg-black/30">
                {([
                  { label: "S",   w: 480,  h: 320, title: "Small (480×320)" },
                  { label: "M",   w: 640,  h: 420, title: "Medium (640×420)" },
                  { label: "L",   w: 800,  h: 520, title: "Large (800×520)" },
                  { label: "XL",  w: 1024, h: 680, title: "X-Large (1024×680)" },
                  { label: "Fit", w: 1600, h: 900, title: "Fit slide (1600×900)" },
                ] as const).map((p) => (
                  <button
                    key={p.label}
                    onClick={() => resizeCell(selectedId, p.w, p.h)}
                    title={p.title}
                    className="font-hand text-xs px-1.5 py-0.5 rounded border-2 border-ink/30 dark:border-white/30 bg-white/80 dark:bg-[#1f2228] text-ink dark:text-white hover:bg-marker-yellow/60 dark:hover:bg-amber-700/40 transition"
                  >
                    {p.label}
                  </button>
                ))}
              </div>
            </>
          )}
        </div>
        <div className="font-hand text-lg ml-1 text-ink/70 dark:text-white/70 select-none flex items-center gap-2 flex-wrap">
          <span>{notebookName}</span>
          <span className="text-ink/40 dark:text-white/40">·</span>
          <span>{savedLabel}</span>
        </div>
      </div>

      <div className="pointer-events-auto flex items-center gap-2">
        <a
          href="/tools"
          title="Tools (PPT → PNG converter, etc.)"
          className="font-hand text-base px-3 py-1.5 rounded-xl border-2 border-ink dark:border-white/70 bg-white/70 dark:bg-[#262a31] text-ink dark:text-white shadow-sketch hover:translate-y-[1px] transition no-underline"
        >
          🛠 Tools
        </a>
        <AmbientPicker />
        <button
          onClick={onHelp}
          title="Keyboard shortcuts (?)"
          className="font-hand text-2xl px-3 py-1.5 rounded-xl border-2 border-ink dark:border-white/70 bg-white/70 dark:bg-[#262a31] text-ink dark:text-white shadow-sketch hover:translate-y-[1px] transition"
        >
          ⌨️ ?
        </button>
        <ThemeToggle />
      </div>
    </header>
  );
}
