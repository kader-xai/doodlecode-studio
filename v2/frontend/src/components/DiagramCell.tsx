import { useEffect, useMemo, useRef, useState } from "react";
import { Handle, NodeProps, Position } from "reactflow";
import mermaid from "mermaid";
import katex from "katex";
import "katex/dist/katex.min.css";

import { renderDoodleDiagram } from "../lib/doodleDiagram";
import { DoodleBorder } from "./DoodleBorder";
import { EditableTitle } from "./EditableTitle";
import { ResizeHandle } from "./ResizeHandle";
import { useStore } from "../store";

const DEFAULT_W = 560;
const DEFAULT_H = 360;

function escapeHtml(s: string): string {
  return s.replace(/[&<>"']/g, (c) => ({
    "&": "&amp;", "<": "&lt;", ">": "&gt;", "\"": "&quot;", "'": "&#039;",
  }[c]!));
}

// One global init — Mermaid is a singleton. We re-themes on dark
// toggle below by passing { theme } at render time.
let mermaidInitialized = false;
function initMermaid() {
  if (mermaidInitialized) return;
  mermaid.initialize({
    startOnLoad: false,
    securityLevel: "loose",
    theme: "default",
    fontFamily: "JetBrains Mono, ui-monospace, monospace",
  });
  mermaidInitialized = true;
}

let _seq = 0;
function nextSvgId() {
  _seq += 1;
  return `mmd-${Date.now().toString(36)}-${_seq}`;
}

/**
 * Diagram cell — renders Mermaid source.
 *
 * View mode shows the SVG; double-click body to enter edit mode
 * (textarea, local-draft pattern — same one we proved out in
 * MarkdownCell so typing is rock-solid).
 *
 * Iter 11 will branch on `diagram_kind` to add Math (KaTeX) and
 * Chart (roughjs). For now: only "mermaid" is honored; other values
 * fall through to a "Renderer not available yet" placeholder.
 */
export function DiagramCell({ data, selected }: NodeProps<{ cellId: string }>) {
  const cellId = data.cellId;
  const cell = useStore((s) => s.cells.find((c) => c.id === cellId));
  const setSource = useStore((s) => s.setSource);
  const setTitle = useStore((s) => s.setTitle);
  const setDiagramKind = useStore((s) => s.setDiagramKind);
  const setSelected = useStore((s) => s.setSelected);
  const toggleCollapse = useStore((s) => s.toggleCollapse);
  const dark = useStore((s) => s.theme === "dark");
  const renameTick = useStore((s) => s.renameTick[cellId] ?? 0);

  const [editing, setEditing] = useState(false);
  const [draft, setDraft] = useState(cell?.source ?? "");
  const [svg, setSvg] = useState<string>("");
  const [renderError, setRenderError] = useState<string | null>(null);
  const taRef = useRef<HTMLTextAreaElement>(null);

  // F2 → rename bridge.
  const [forceEditTitle, setForceEditTitle] = useState(false);
  useEffect(() => {
    if (renameTick > 0) {
      setForceEditTitle(true);
      const t = setTimeout(() => setForceEditTitle(false), 50);
      return () => clearTimeout(t);
    }
  }, [renameTick]);

  // Resync draft from store while NOT editing.
  useEffect(() => {
    if (!editing) setDraft(cell?.source ?? "");
  }, [cell?.source, editing]);

  // Render the doodle SVG synchronously — it's just string templating.
  const doodleSvg = useMemo(() => {
    if (!cell || cell.diagram_kind !== "doodle") return "";
    return renderDoodleDiagram(cell.source, dark);
  }, [cell?.source, cell?.diagram_kind, dark, cell]);

  // KaTeX renders synchronously. We compute the HTML once per source
  // change and dangerouslySet it. `throwOnError: false` makes KaTeX
  // emit a red error span instead of crashing on bad LaTeX.
  const mathHtml = useMemo(() => {
    if (!cell || cell.diagram_kind !== "math") return "";
    try {
      return katex.renderToString(cell.source || "", {
        displayMode: true,
        throwOnError: false,
        errorColor: "#c2255c",
        strict: "ignore",
      });
    } catch (e: any) {
      return `<span style="color:#c2255c;font-family:monospace;">${escapeHtml(e?.message ?? String(e))}</span>`;
    }
  }, [cell?.source, cell?.diagram_kind, cell]);

  // Render Mermaid whenever source or theme changes.
  useEffect(() => {
    if (!cell || cell.diagram_kind !== "mermaid") return;
    let cancelled = false;
    initMermaid();
    // Theme switch is a re-init in mermaid v11.
    mermaid.initialize({
      startOnLoad: false,
      securityLevel: "loose",
      theme: dark ? "dark" : "default",
      fontFamily: "JetBrains Mono, ui-monospace, monospace",
    });
    const id = nextSvgId();
    (async () => {
      try {
        const out = await mermaid.render(id, cell.source);
        if (!cancelled) {
          setSvg(out.svg);
          setRenderError(null);
        }
      } catch (e: any) {
        if (!cancelled) {
          setSvg("");
          setRenderError(e?.message ?? String(e));
        }
      }
    })();
    return () => { cancelled = true; };
  }, [cell?.source, cell?.diagram_kind, dark, cell]);

  useEffect(() => {
    if (editing) {
      taRef.current?.focus();
      const ta = taRef.current;
      if (ta) ta.setSelectionRange(ta.value.length, ta.value.length);
    }
  }, [editing]);

  if (!cell) return null;

  const w = cell.w ?? DEFAULT_W;
  const h = cell.h ?? DEFAULT_H;
  const ringColor = selected ? "#c2255c" : "var(--doodle-stroke, #2a2a2a)";
  const ringWidth = selected ? 3.5 : 2.5;
  const fill = dark ? "#262a31" : "#ffffff";

  const enterEdit = () => { setDraft(cell.source); setEditing(true); };
  const commitAndClose = () => {
    if (draft !== cell.source) setSource(cellId, draft);
    setEditing(false);
  };

  return (
    <div
      className="relative"
      style={{ width: w, height: h }}
      onClickCapture={() => setSelected(cellId)}
    >
      <Handle type="target" position={Position.Left} className="!bg-transparent !border-0" />

      <div className="absolute inset-0">
        <DoodleBorder stroke={ringColor} fill={fill} strokeWidth={ringWidth} radius={14} />

        <div className="absolute inset-1 flex flex-col overflow-hidden rounded-lg">
          {/* Header strip — drag-handle. Title is draggable; the
           *  selector + Edit button below carry `nodrag` so they
           *  still receive clicks. */}
          <div className="flex items-center gap-2 px-2 py-1 border-b-2 border-ink/30 dark:border-white/30 bg-white/80 dark:bg-[#1f2228]">
            {/* Iter 56: collapse chevron. */}
            <button
              type="button"
              onClick={(e) => { e.stopPropagation(); toggleCollapse(cellId); }}
              onPointerDown={(e) => e.stopPropagation()}
              onMouseDown={(e) => e.stopPropagation()}
              className="font-mono text-sm w-5 h-5 leading-none rounded border-2 border-ink/30 dark:border-white/30 bg-white/60 dark:bg-black/40 text-ink/70 dark:text-white/70 hover:bg-marker-yellow/50 dark:hover:bg-amber-700/30 transition nodrag shrink-0"
              title={cell.collapsed ? "Expand cell" : "Collapse cell"}
            >
              {cell.collapsed ? "▸" : "▾"}
            </button>
            <EditableTitle
              value={cell.title}
              onCommit={(t) => setTitle(cellId, t)}
              forceEdit={forceEditTitle}
              className="font-hand text-base truncate text-ink dark:text-white flex-1 min-w-0"
            />
            <select
              value={cell.diagram_kind ?? "doodle"}
              onChange={(e) => { e.stopPropagation(); setDiagramKind(cellId, e.target.value); }}
              onKeyDown={(e) => e.stopPropagation()}
              onPointerDown={(e) => e.stopPropagation()}
              onMouseDown={(e) => e.stopPropagation()}
              onClick={(e) => e.stopPropagation()}
              title="Diagram style"
              className="nodrag font-hand text-sm px-1.5 py-0.5 rounded-md border-2 border-ink/40 dark:border-white/30 bg-white/90 dark:bg-[#262a31] text-ink dark:text-white shrink-0"
            >
              <option value="doodle">🖍 Doodle</option>
              <option value="mermaid">🧭 Mermaid</option>
              <option value="math">📐 Math</option>
            </select>
            <button
              type="button"
              // `preventDefault` on mousedown keeps the textarea focused
              // so its onBlur doesn't fire BEFORE our click handler runs.
              // `nodrag` lets ReactFlow ignore this button's pointerdown.
              onMouseDown={(e) => { e.preventDefault(); e.stopPropagation(); }}
              onPointerDown={(e) => e.stopPropagation()}
              onClick={(e) => {
                e.stopPropagation();
                if (editing) commitAndClose();
                else enterEdit();
              }}
              className="nodrag font-hand text-sm px-2 py-0.5 rounded-md border-2 border-ink dark:border-white/70 bg-white/90 dark:bg-[#262a31] text-ink dark:text-white shadow-sketch hover:translate-y-[1px] transition shrink-0"
              title={editing ? "Stop editing (Esc)" : "Edit diagram source"}
            >
              {editing ? "✓ Done" : "✏️ Edit"}
            </button>
          </div>

          {/* Body — hidden when collapsed (iter 56). */}
          {!cell.collapsed && (
          <div className="relative flex-1 overflow-auto nodrag nowheel bg-white dark:bg-[#1a1d23]">
            {editing ? (
              <textarea
                ref={taRef}
                value={draft}
                onChange={(e) => setDraft(e.target.value)}
                onBlur={commitAndClose}
                onKeyDown={(e) => {
                  e.stopPropagation();
                  if (e.key === "Escape") {
                    e.preventDefault();
                    commitAndClose();
                  }
                }}
                onClick={(e) => e.stopPropagation()}
                onPointerDown={(e) => e.stopPropagation()}
                spellCheck={false}
                className="absolute inset-0 w-full h-full font-mono text-sm leading-relaxed p-2 bg-white dark:bg-[#1f2228] text-ink dark:text-white outline-none resize-none"
              />
            ) : cell.diagram_kind === "doodle" || !cell.diagram_kind ? (
              <div
                className="w-full h-full flex items-start justify-center p-3 overflow-auto"
                onDoubleClick={(e) => { e.stopPropagation(); enterEdit(); }}
                title="Double-click to edit"
              >
                {/* The doodle renderer returns one big HTML blob with
                 *  flow + chart stacked. dangerouslySetInnerHTML is OK
                 *  here — the renderer escapes every user-provided value. */}
                <div
                  className="w-full"
                  // eslint-disable-next-line react/no-danger
                  dangerouslySetInnerHTML={{ __html: doodleSvg }}
                />
              </div>
            ) : cell.diagram_kind === "math" ? (
              <div
                className="w-full h-full flex items-center justify-center p-4 overflow-auto"
                onDoubleClick={(e) => { e.stopPropagation(); enterEdit(); }}
                title="Double-click to edit"
                style={{ fontSize: "1.4em" }}
              >
                {/* KaTeX emits a self-contained HTML blob. `katex.min.css`
                 *  is imported above so the layout works without extra
                 *  setup. */}
                <div
                  className="max-w-full text-ink dark:text-white"
                  // eslint-disable-next-line react/no-danger
                  dangerouslySetInnerHTML={{ __html: mathHtml }}
                />
              </div>
            ) : cell.diagram_kind === "mermaid" ? (
              <div
                className="w-full h-full flex items-center justify-center p-2"
                onDoubleClick={(e) => { e.stopPropagation(); enterEdit(); }}
                title="Double-click to edit"
              >
                {renderError ? (
                  <pre className="font-mono text-xs text-[#c2255c] dark:text-[#fcc2d7] whitespace-pre-wrap p-2 max-w-full">
                    {renderError}
                  </pre>
                ) : svg ? (
                  // mermaid returns a complete <svg> blob.
                  // eslint-disable-next-line react/no-danger
                  <div className="max-w-full max-h-full" dangerouslySetInnerHTML={{ __html: svg }} />
                ) : (
                  <span className="font-hand text-lg text-ink/50 dark:text-white/50">rendering…</span>
                )}
              </div>
            ) : (
              <div className="w-full h-full flex items-center justify-center text-ink/60 dark:text-white/60 font-hand text-lg p-4 text-center">
                Renderer for <code className="font-mono">{cell.diagram_kind}</code> arrives in a later iteration.
              </div>
            )}
          </div>
          )}
        </div>

        <ResizeHandle cellId={cellId} baseWidth={w} baseHeight={h} />
      </div>

      <Handle type="source" position={Position.Right} className="!bg-transparent !border-0" />
    </div>
  );
}
