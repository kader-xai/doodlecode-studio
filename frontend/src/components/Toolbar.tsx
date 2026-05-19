import { resetKernel } from "../api";
import { useStore } from "../store";
import { DesignPicker } from "./DesignPicker";
import { AmbientPicker } from "./AmbientPicker";
import { BackgroundPicker } from "./BackgroundPicker";
import { FileMenu } from "./FileMenu";
import { AddMenu } from "./AddMenu";
import { isMediaOnlySource } from "./MarkdownNode";

export function Toolbar() {
  const presenting = useStore((s) => s.presenting);
  const setPresenting = useStore((s) => s.setPresenting);
  const notebook = useStore((s) => s.notebook);
  const savedAt = useStore((s) => s.savedAt);
  const setAboutOpen = useStore((s) => s.setAboutOpen);
  const installing = useStore((s) => s.installing);
  const setInstallOpen = useStore((s) => s.setInstallOpen);
  const branding = useStore((s) => s.branding);
  const fullscreen = useStore((s) => s.fullscreen);
  const positionOverrides = useStore((s) => s.cellPositionOverrides);
  const autoSpace = useStore((s) => s.autoSpaceForPresentation);
  const rollback = useStore((s) => s.rollbackLayout);
  const mode = useStore((s) => s.interactionMode);
  const setMode = useStore((s) => s.setInteractionMode);
  const selection = useStore((s) => s.selection);
  const setSelection = useStore((s) => s.setSelection);
  const setOpenEditor = useStore((s) => s.setOpenEditor);
  const deleteCell = useStore((s) => s.deleteCell);
  const deleteCallout = useStore((s) => s.deleteCallout);
  const setCellSize = useStore((s) => s.setCellSize);
  const notebookCells = useStore((s) => s.notebook.cells);

  // Resolve the selected entity for the action bar.
  const selCell = selection
    ? notebookCells.find((c) => c.id === selection.cellId) ?? null
    : null;
  const selIsMediaOnly =
    !!selCell && selCell.kind === "markdown" && isMediaOnlySource(selCell.source);
  // Every cell type is resizable now — code + markdown both honor
  // `cellSize` (code cards stretch the Monaco editor; markdown cards
  // grow to fit). Outputs in code cells render BELOW the card, so
  // they're never clipped by the chosen preset, and the presenter
  // focus region uses `estimateCellHeight` which already includes
  // output height.
  const selIsResizableVariant = !!selCell;

  // Preset sizes for media-only cells. (w, h) in canvas pixels.
  const MEDIA_PRESETS: { label: string; w: number; h: number; tip: string }[] = [
    { label: "S",  w: 480,  h: 320, tip: "Small  (480 × 320)" },
    { label: "M",  w: 720,  h: 480, tip: "Medium (720 × 480)" },
    { label: "L",  w: 960,  h: 640, tip: "Large  (960 × 640)" },
    { label: "XL", w: 1280, h: 800, tip: "X-Large (1280 × 800)" },
    { label: "Fit", w: 1600, h: 900, tip: "Fit slide (1600 × 900)" },
  ];
  const selLabel = (() => {
    if (!selection || !selCell) return "";
    if (selection.type === "callout") {
      return `Callout ${selection.index + 1} of "${selCell.meta?.title || selCell.id.slice(0, 6)}"`;
    }
    return selCell.meta?.title || (selCell.kind === "code" ? "Code cell" : "Text cell");
  })();

  const onEditSelection = () => {
    if (!selection || !selCell) return;
    if (selection.type === "callout") {
      setOpenEditor({ kind: "callout", cellId: selection.cellId });
    } else if (selCell.meta?.cell_type === "diagram") {
      // Diagram cells: edit the source notation (Mermaid / Math / Chart).
      setOpenEditor({ kind: "diagram", cellId: selection.cellId });
    } else if (selCell.kind === "markdown") {
      setOpenEditor({ kind: "text", cellId: selection.cellId });
    } else {
      setOpenEditor({ kind: "callout", cellId: selection.cellId });
    }
  };
  const onDeleteSelection = () => {
    if (!selection || !selCell) return;
    if (selection.type === "callout") {
      if (window.confirm(`Delete callout "${selLabel}"?`)) {
        deleteCallout(selection.cellId, selection.index);
        setSelection(null);
      }
    } else {
      if (window.confirm(`Delete "${selLabel}"? The rest of the deck reorders automatically.`)) {
        deleteCell(selection.cellId);
        setSelection(null);
      }
    }
  };

  // In fullscreen presentation mode the toolbar would be a distraction
  // (and would steal click events). Hide it completely — but AFTER all
  // hooks have run so React's hook count stays stable.
  if (fullscreen && presenting) return null;

  const savedLabel = savedAt
    ? `saved ${Math.max(1, Math.round((Date.now() - savedAt) / 1000))}s ago`
    : "unsaved";

  return (
    <div className="absolute top-3 left-3 right-3 z-30 flex items-start justify-between pointer-events-none">
      <div className="flex flex-col gap-1 pointer-events-auto">
        <div className="flex gap-2 items-center flex-wrap">
          <div className="font-hand text-3xl mr-1 select-none leading-none text-ink dark:text-white">
            {branding.logo} DoodleCode <span className="text-[#c2255c] dark:text-[#fcc2d7]">Studio</span>
          </div>

          {/* Three tools: cursor / hand / move (V / H / M). Like Figma. */}
          <div className="flex gap-1 border-2 border-ink/40 dark:border-white/40 rounded-xl p-0.5 bg-white/40 dark:bg-black/30">
            {[
              { id: "cursor", icon: "➤", label: "Cursor — click selects, double-click edits (V)" },
              { id: "hand", icon: "✋", label: "Hand — drag to pan the canvas (H)" },
              { id: "move", icon: "✥", label: "Move — drag to reposition boxes (M)" },
            ].map((t) => (
              <button
                key={t.id}
                title={t.label}
                onClick={() => setMode(t.id as "cursor" | "hand" | "move")}
                className={`w-8 h-8 rounded-md border-2 text-lg font-hand transition ${
                  mode === t.id
                    ? "bg-marker-yellow border-ink dark:bg-amber-700 dark:border-white text-ink dark:text-white shadow-sketch"
                    : "bg-white/70 dark:bg-[#1f2228] border-ink/30 dark:border-white/30 text-ink/70 dark:text-white/70"
                }`}
              >
                {t.icon}
              </button>
            ))}
          </div>

          <FileMenu />
          <AddMenu />
          <button
            className="btn-sketch violet"
            onClick={() => setInstallOpen(true)}
            title="Pip-install packages into the kernel"
          >
            📦 Install
          </button>
          <button className="btn-sketch peach" onClick={() => resetKernel()}>
            ↻ Kernel
          </button>
          {positionOverrides ? (
            <button
              className="btn-sketch"
              onClick={() => rollback()}
              title="Bring cells back close together for editing"
            >
              🔗 Together
            </button>
          ) : (
            <button
              className="btn-sketch violet"
              onClick={() => autoSpace(window.innerHeight)}
              title="Spread cells one-per-slide for presenting"
            >
              📐 Space
            </button>
          )}
          <button className="btn-sketch pink" onClick={() => setPresenting(!presenting)}>
            {presenting ? "✕ Exit" : "🎬 Present"}
          </button>

          {/* Selection action bar — INLINE with the top row.
           *  Appears only when a cell / callout is selected, so cards
           *  stay clean and the top row stays compact otherwise. */}
          {selection && selCell && (
            <div className="flex items-center gap-1.5 ml-2 pl-2 border-l-2 border-ink/30 dark:border-white/30 font-hand">
              <span
                className="text-sm px-2 py-0.5 rounded-md border-2 border-ink/40 dark:border-white/40 bg-white/80 dark:bg-black/40 text-ink dark:text-white max-w-[180px] truncate"
                title={selLabel}
              >
                {selLabel}
              </span>
              <button
                className="btn-sketch sky text-sm !py-0.5 !px-2"
                onClick={onEditSelection}
                title="Open the editor for this item"
              >
                ✏️ Edit
              </button>
              {selection?.type === "cell" && (
                <button
                  className="btn-sketch mint text-sm !py-0.5 !px-2"
                  onClick={() => setOpenEditor({ kind: "callout", cellId: selection.cellId })}
                  title="Add or edit the side callout bubble(s) for this cell"
                >
                  💬 Callout
                </button>
              )}
              <button
                className="btn-sketch pink text-sm !py-0.5 !px-2"
                onClick={onDeleteSelection}
                title="Delete this item"
              >
                🗑 Delete
              </button>
              {selIsResizableVariant && selection?.type === "cell" && (
                <div className="flex items-center gap-0.5 ml-1 pl-1 border-l-2 border-ink/20 dark:border-white/20">
                  {MEDIA_PRESETS.map((p) => (
                    <button
                      key={p.label}
                      className="text-xs font-hand px-1.5 py-0.5 rounded-md border-2 border-ink/40 dark:border-white/40 bg-white/80 dark:bg-black/40 text-ink dark:text-white hover:bg-marker-yellow dark:hover:bg-amber-700"
                      onClick={() => setCellSize(selection.cellId, { width: p.w, height: p.h })}
                      title={p.tip}
                    >
                      {p.label}
                    </button>
                  ))}
                </div>
              )}
              <button
                className="text-xs text-ink/60 dark:text-white/60 underline underline-offset-2 hover:opacity-80 ml-1"
                onClick={() => setSelection(null)}
                title="Clear selection"
              >
                clear
              </button>
            </div>
          )}
        </div>
        <div className="font-hand text-lg ml-1 text-ink/70 dark:text-white/70 select-none flex items-center gap-3 flex-wrap">
          <button
            onClick={() => setAboutOpen(true)}
            className="text-[#c2255c] dark:text-[#fcc2d7] underline decoration-wavy underline-offset-2 hover:opacity-80 text-left"
          >
            {branding.byline}
          </button>
          <span className="text-ink/40 dark:text-white/40">·</span>
          <span>{notebook.name}</span>
          <span className="text-ink/40 dark:text-white/40">·</span>
          <span>{savedLabel}</span>
        </div>
      </div>
      <div className="flex gap-2 pointer-events-auto">
        <DesignPicker />
        <AmbientPicker />
        <BackgroundPicker />
        <a
          className="btn-sketch peach inline-block text-base"
          href="/tools"
          title="Open the /tools page (PPT → Images, etc.)"
        >
          🛠 Tools
        </a>
        <button className="btn-sketch sky" onClick={() => setAboutOpen(true)}>
          ⓘ About
        </button>
      </div>
      {installing && (
        <div className="fixed bottom-4 left-4 z-40 pointer-events-auto bg-white dark:bg-[#1f2228] border-2 border-ink dark:border-white/70 rounded-xl px-3 py-2 font-hand text-lg shadow-sketch">
          📦 installing {installing.packages}…
        </div>
      )}
    </div>
  );
}
