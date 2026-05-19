import { useEffect, useState } from "react";
import { useStore } from "../store";

type Kind = "mermaid" | "math" | "chart";

const SAMPLES: Record<Kind, string> = {
  mermaid:
    "graph TB\n  A[Input] --> B{Decision}\n  B -->|yes| C[Train]\n  B -->|no|  D[Skip]",
  math:
    "AB = \\begin{bmatrix} 1 & 2 \\\\ 3 & 4 \\end{bmatrix} \\begin{bmatrix} 5 \\\\ 6 \\end{bmatrix} = \\begin{bmatrix} 17 \\\\ 39 \\end{bmatrix}",
  chart:
    '{\n  "type": "bar",\n  "title": "Stars (k)",\n  "data": [\n    ["Python", 82],\n    ["Rust", 38],\n    ["Go", 41]\n  ]\n}',
};

export function DiagramEditor({ cellId, onClose }: { cellId: string; onClose: () => void }) {
  const cell = useStore((s) => s.notebook.cells.find((c) => c.id === cellId));
  const updateSource = useStore((s) => s.updateCellSource);
  const updateMeta = useStore((s) => s.updateCellMeta);
  const resetStep = useStore((s) => s.resetDiagramStep);

  const [kind, setKind] = useState<Kind>(
    (cell?.meta?.diagram_kind as Kind | undefined) ?? "mermaid"
  );
  const [title, setTitle] = useState<string>(cell?.meta?.title ?? "");
  const [source, setSource] = useState<string>(cell?.source ?? "");
  const [fontScale, setFontScale] = useState<number>(
    cell?.meta?.diagram_font_scale ?? 1
  );

  useEffect(() => {
    setKind((cell?.meta?.diagram_kind as Kind | undefined) ?? "mermaid");
    setTitle(cell?.meta?.title ?? "");
    setSource(cell?.source ?? "");
    setFontScale(cell?.meta?.diagram_font_scale ?? 1);
  }, [cell?.meta?.diagram_kind, cell?.meta?.title, cell?.source, cell?.meta?.diagram_font_scale]);

  // Live-sync the font scale to the cell on every bump so the user
  // can SEE the diagram resize behind the editor in real time.
  const bumpScale = (delta: number) => {
    const next = Math.max(0.6, Math.min(2.4, Math.round((fontScale + delta) * 10) / 10));
    setFontScale(next);
    if (!cell) return;
    updateMeta(cellId, {
      ...(cell.meta ?? {}),
      cell_type: "diagram",
      diagram_font_scale: next,
    });
  };

  useEffect(() => {
    const onKey = (e: KeyboardEvent) => { if (e.key === "Escape") onClose(); };
    window.addEventListener("keydown", onKey);
    return () => window.removeEventListener("keydown", onKey);
  }, [onClose]);

  if (!cell) return null;

  const onSave = () => {
    updateMeta(cellId, {
      ...(cell.meta ?? {}),
      cell_type: "diagram",
      diagram_kind: kind,
      title: title.trim() || undefined,
      diagram_font_scale: fontScale !== 1 ? fontScale : undefined,
    });
    updateSource(cellId, source);
    resetStep(cellId);
    onClose();
  };

  const onLoadSample = () => setSource(SAMPLES[kind]);

  return (
    <div
      className="fixed inset-0 z-50 flex items-center justify-center bg-black/60"
      onClick={onClose}
    >
      <div
        className="relative w-[820px] max-w-[94vw] max-h-[92vh] overflow-hidden bg-white dark:bg-[#1f2228] border-2 border-ink dark:border-white rounded-3xl shadow-sketch p-5 font-hand text-ink dark:text-white flex flex-col"
        onClick={(e) => e.stopPropagation()}
      >
        <div className="flex items-center justify-between mb-3 gap-3 flex-wrap">
          <div className="text-2xl">🧭 Diagram source</div>
          <div className="flex items-center gap-2">
            {/* Font-size control — applies to the rendered diagram
             *  text. Live-syncs to the cell, so the diagram behind
             *  the editor resizes as you click. */}
            <div
              className="flex items-center gap-1 border-2 border-ink/40 dark:border-white/40 rounded-xl px-1 py-0.5 bg-white/40 dark:bg-black/30"
              title={`Diagram font scale ${Math.round(fontScale * 100)}%`}
            >
              <button
                type="button"
                className="w-7 h-7 rounded-md font-hand text-lg text-ink dark:text-white hover:bg-marker-yellow dark:hover:bg-amber-700 disabled:opacity-40"
                onClick={() => bumpScale(-0.1)}
                disabled={fontScale <= 0.6 + 1e-3}
                title="Smaller diagram text (A−)"
              >
                A−
              </button>
              <span className="font-mono text-xs px-1 text-ink/70 dark:text-white/70 select-none w-10 text-center">
                {Math.round(fontScale * 100)}%
              </span>
              <button
                type="button"
                className="w-7 h-7 rounded-md font-hand text-xl text-ink dark:text-white hover:bg-marker-yellow dark:hover:bg-amber-700 disabled:opacity-40"
                onClick={() => bumpScale(0.1)}
                disabled={fontScale >= 2.4 - 1e-3}
                title="Larger diagram text (A+)"
              >
                A+
              </button>
            </div>
            <button
              type="button"
              onClick={onClose}
              className="w-9 h-9 rounded-full border-2 border-ink dark:border-white bg-white dark:bg-[#0f1115] text-xl"
            >
              ✕
            </button>
          </div>
        </div>

        <div className="flex items-center gap-3 mb-3 flex-wrap">
          <label className="flex items-center gap-2">
            <span className="text-base text-ink/70 dark:text-white/70">Renderer</span>
            <select
              value={kind}
              onChange={(e) => setKind(e.target.value as Kind)}
              className="font-mono text-sm px-2 py-1 rounded border-2 border-ink dark:border-white bg-white dark:bg-[#0f1115] text-ink dark:text-white"
            >
              <option value="mermaid">Mermaid (graphs / trees / flowcharts)</option>
              <option value="math">Math (LaTeX via KaTeX)</option>
              <option value="chart">Chart (JSON — bar / line / pie)</option>
            </select>
          </label>
          <label className="flex items-center gap-2 flex-1">
            <span className="text-base text-ink/70 dark:text-white/70">Title</span>
            <input
              type="text"
              value={title}
              onChange={(e) => setTitle(e.target.value)}
              placeholder="optional"
              className="flex-1 font-hand text-lg px-2 py-1 rounded border-2 border-ink dark:border-white bg-white dark:bg-[#0f1115] text-ink dark:text-white"
            />
          </label>
          <button
            onClick={onLoadSample}
            className="font-hand text-sm px-3 py-1 rounded-lg border-2 border-ink dark:border-white bg-marker-yellow text-ink"
            title={`Replace the source with a working ${kind} example`}
          >
            🧪 Load sample
          </button>
        </div>

        <div className="text-sm text-ink/70 dark:text-white/70 mb-1">
          Source — use <code className="font-mono">{`# @step 1`}</code>,{" "}
          <code className="font-mono">{`# @step 2`}</code>, … to split into layered reveals
          (right-arrow during presentation advances each step).
        </div>
        <textarea
          value={source}
          onChange={(e) => setSource(e.target.value)}
          className="flex-1 min-h-[280px] font-mono text-sm p-3 rounded-xl border-2 border-ink dark:border-white bg-white dark:bg-[#0f1115] text-ink dark:text-white"
          spellCheck={false}
        />

        <div className="mt-3 flex items-center justify-end gap-2">
          <button className="btn-sketch" onClick={onClose}>Cancel</button>
          <button className="btn-sketch mint" onClick={onSave}>💾 Save</button>
        </div>
      </div>
    </div>
  );
}
