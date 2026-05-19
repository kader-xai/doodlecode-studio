import { Handle, Position, NodeProps } from "reactflow";
import { useEffect, useMemo, useRef } from "react";
import { ResizeHandle } from "./ResizeHandle";
import { useStore } from "../store";
import { MermaidRender } from "./diagramRenderers/MermaidRender";
import { MathRender } from "./diagramRenderers/MathRender";
import { ChartRender } from "./diagramRenderers/ChartRender";

const DEFAULT_W = 1100;
const DEFAULT_H = 640;

/** Split a diagram source by `# @step N` markers.
 *  Returns an array of cumulative sources — element i is everything
 *  through step (i+1). If no markers exist, returns one element. */
export function splitSteps(src: string): string[] {
  const lines = src.split("\n");
  const stepRe = /^\s*#\s*@step\b/;
  if (!lines.some((l) => stepRe.test(l))) return [src];
  const groups: string[][] = [];
  let cur: string[] = [];
  for (const ln of lines) {
    if (stepRe.test(ln)) {
      if (cur.length) groups.push(cur);
      cur = [];
    } else {
      cur.push(ln);
    }
  }
  if (cur.length) groups.push(cur);
  // Cumulative: step N contains step 0..N joined.
  const out: string[] = [];
  for (let i = 0; i < groups.length; i++) {
    out.push(groups.slice(0, i + 1).flat().join("\n"));
  }
  return out;
}

export function DiagramNode({ data }: NodeProps<{ cellId: string }>) {
  const cellId = data.cellId;
  const cell = useStore((s) => s.notebook.cells.find((c) => c.id === cellId));
  const size = useStore((s) => s.cellSize[cellId]);
  const reportCellHeight = useStore((s) => s.reportCellHeight);
  const step = useStore((s) => s.diagramStep[cellId] ?? 1);

  const wrapRef = useRef<HTMLDivElement>(null);

  const source = cell?.source ?? "";
  const kind = (cell?.meta?.diagram_kind ?? "mermaid") as
    | "mermaid" | "math" | "chart";
  const steps = useMemo(() => splitSteps(source), [source]);
  const visible = steps[Math.min(step, steps.length) - 1] ?? "";
  const rawScale = cell?.meta?.diagram_font_scale ?? 1;
  const fontScale = Math.max(0.6, Math.min(2.4, rawScale));

  useEffect(() => {
    const el = wrapRef.current;
    if (!el) return;
    const ro = new ResizeObserver((entries) => {
      for (const e of entries) reportCellHeight(cellId, Math.ceil(e.contentRect.height));
    });
    ro.observe(el);
    return () => ro.disconnect();
  }, [cellId, reportCellHeight]);

  if (!cell) return null;
  const w = size?.width ?? DEFAULT_W;
  const h = size?.height ?? DEFAULT_H;
  const totalSteps = steps.length;

  const Renderer =
    kind === "math" ? MathRender
    : kind === "chart" ? ChartRender
    : MermaidRender;

  const kindLabel =
    kind === "math" ? "📐 Math"
    : kind === "chart" ? "📊 Chart"
    : "🧭 Mermaid";

  return (
    <div ref={wrapRef} data-cell-id={cellId} style={{ width: w, position: "relative" }}>
      <Handle type="target" position={Position.Left} />
      <div className="doodle-card relative p-0 overflow-hidden" style={{ height: h, borderRadius: 18 }}>
        {/* Header strip */}
        <div className="flex items-center justify-between px-3 py-1.5 border-b-2 border-ink/40 dark:border-white/40 nodrag" style={{ background: "rgba(255,255,255,0.6)" }}>
          <div className="flex items-baseline gap-3 min-w-0">
            <span className="font-hand text-2xl text-ink dark:text-white truncate">
              {cell.meta?.title ?? "Diagram"}
            </span>
            <span className="font-mono text-xs text-ink/60 dark:text-white/60 select-none shrink-0">
              {kindLabel}
            </span>
          </div>
          {totalSteps > 1 && (
            <span className="font-mono text-xs text-ink/70 dark:text-white/70 select-none">
              step {Math.min(step, totalSteps)} / {totalSteps}
            </span>
          )}
        </div>
        {/* Body — render area.
         *
         * Font scaling: we apply a CSS `transform: scale()` on a child
         * wrapper rather than passing scale into each renderer.
         * Reason: Mermaid v11 doesn't honor a runtime fontSize change
         * once a diagram has rendered, and KaTeX has explicit
         * `font-size` rules that override inherited values. A wrapper
         * transform sidesteps both — Mermaid SVG, KaTeX HTML, and the
         * Chart SVG all scale together as a single graphic.
         * Origin top-left + overflow-auto means content past the
         * card edge stays scrollable instead of clipping. */}
        <div className="absolute inset-x-0 bottom-0 top-[40px] overflow-auto nowheel">
          <div
            style={{
              transform: fontScale === 1 ? undefined : `scale(${fontScale})`,
              transformOrigin: "top left",
              // When scaled up, give the inner box enough room so the
              // scaled content doesn't end up sitting on a strip the
              // size of the original card.
              width: fontScale > 1 ? `${100 * fontScale}%` : "100%",
              minHeight: fontScale > 1 ? `${100 * fontScale}%` : "100%",
            }}
          >
            <Renderer source={visible} fontScale={fontScale} />
          </div>
        </div>
      </div>
      <ResizeHandle cellId={cellId} baseWidth={w} baseHeight={h} />
      <Handle type="source" position={Position.Right} />
    </div>
  );
}
