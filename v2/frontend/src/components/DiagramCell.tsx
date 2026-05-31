import { useEffect, useMemo, useRef, useState } from "react";
import { Handle, NodeProps, Position } from "reactflow";

import { renderDoodleDiagram } from "../lib/doodleDiagram";
import { resolveLiveDoodleSource, stdoutOf } from "../lib/liveChart";
import { DoodleBorder } from "./DoodleBorder";
import { EditableTitle } from "./EditableTitle";
import { ResizeHandle } from "./ResizeHandle";
import { useStore } from "../store";

const DEFAULT_W = 560;
const DEFAULT_H = 360;

/**
 * Iter 167: one-click doodle-chart snippets. Inserting a preset is
 * the discoverability path so users never memorize the mini-syntax —
 * each appends a working block they can then tweak. Charts coexist, so
 * appending is non-destructive.
 */
const DOODLE_PRESETS: { key: string; label: string; snippet: string }[] = [
  { key: "flow", label: "→ Flow", snippet: "Idea --> Draft\nDraft --> Ship" },
  { key: "bar", label: "▭ Bar", snippet: "chart: Scores\nAlpha: 8\nBeta: 5\nGamma: 10" },
  { key: "stack", label: "▥ Stacked", snippet: "stack: Spend by quarter\nseries: Eng, Sales, Ops\nstack Q1: 5, 3, 2\nstack Q2: 6, 4, 3\nstack Q3: 7, 5, 4" },
  { key: "line", label: "📈 Line", snippet: "xlabel: Epoch\nylabel: Loss\nhline Target: 0.3\nline Loss: 0.9, 0.6, 0.4, 0.25" },
  { key: "area", label: "▰ Area", snippet: "xlabel: Week\nylabel: Users\narea Active: 2, 5, 9, 14, 20" },
  { key: "pie", label: "◔ Pie", snippet: "pie: Share\npie Python: 60\npie Rust: 40" },
  { key: "scatter", label: "⠿ Scatter", snippet: "scatter: Cloud\nxlabel: Width\nylabel: Height\npoint: 1, 2\npoint: 3, 4\npoint: 5, 3" },
  // Iter 174: live data — replace the id with a code cell that prints
  // doodle-chart syntax (e.g. `print(doodle.bar({...}))`).
  { key: "live", label: "🔌 Live", snippet: "live: CODE_CELL_ID" },
];

function escapeHtml(s: string): string {
  return s.replace(/[&<>"']/g, (c) => ({
    "&": "&amp;", "<": "&lt;", ">": "&gt;", "\"": "&quot;", "'": "&#039;",
  }[c]!));
}

// Iter 181: Mermaid (~0.5 MB) and KaTeX (~0.3 MB) are heavy and only
// needed by the Mermaid / Math diagram kinds, so they're code-split via
// dynamic import — the main chunk no longer carries them. Each loader
// memoizes the module promise so the chunk loads at most once.
type MermaidModule = typeof import("mermaid")["default"];
let _mermaidPromise: Promise<MermaidModule> | null = null;
let mermaidInitialized = false;
async function getMermaid(): Promise<MermaidModule> {
  if (!_mermaidPromise) {
    _mermaidPromise = import("mermaid").then((m) => m.default);
  }
  const mermaid = await _mermaidPromise;
  if (!mermaidInitialized) {
    mermaid.initialize({
      startOnLoad: false,
      securityLevel: "loose",
      theme: "default",
      fontFamily: "JetBrains Mono, ui-monospace, monospace",
    });
    mermaidInitialized = true;
  }
  return mermaid;
}

type KatexModule = typeof import("katex")["default"];
let _katexPromise: Promise<KatexModule> | null = null;
async function getKatex(): Promise<KatexModule> {
  if (!_katexPromise) {
    _katexPromise = Promise.all([
      import("katex"),
      import("katex/dist/katex.min.css"),
    ]).then(([m]) => m.default);
  }
  return _katexPromise;
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
  // Iter 174: subscribe to runtimes so `live: <id>` charts re-render
  // when the referenced code cell produces new stdout.
  const runtimes = useStore((s) => s.runtimes);

  const [editing, setEditing] = useState(false);
  const [draft, setDraft] = useState(cell?.source ?? "");
  const [svg, setSvg] = useState<string>("");
  const [renderError, setRenderError] = useState<string | null>(null);
  // Iter 181: KaTeX is loaded lazily, so the rendered math HTML is now
  // async state instead of a synchronous useMemo.
  const [mathHtml, setMathHtml] = useState<string>("");
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
  // Iter 174: `live: <id>` lines are first substituted with that code
  // cell's current stdout, so the chart tracks live data.
  const doodleSvg = useMemo(() => {
    if (!cell || cell.diagram_kind !== "doodle") return "";
    const resolved = resolveLiveDoodleSource(cell.source, (id) => stdoutOf(runtimes[id]));
    return renderDoodleDiagram(resolved, dark);
  }, [cell?.source, cell?.diagram_kind, dark, runtimes, cell]);

  // Iter 181: KaTeX renders after its chunk loads. `throwOnError:false`
  // makes KaTeX emit a red error span instead of crashing on bad LaTeX.
  useEffect(() => {
    if (!cell || cell.diagram_kind !== "math") { setMathHtml(""); return; }
    let cancelled = false;
    (async () => {
      try {
        const katex = await getKatex();
        if (cancelled) return;
        setMathHtml(
          katex.renderToString(cell.source || "", {
            displayMode: true,
            throwOnError: false,
            errorColor: "#c2255c",
            strict: "ignore",
          }),
        );
      } catch (e: any) {
        if (!cancelled) {
          setMathHtml(`<span style="color:#c2255c;font-family:monospace;">${escapeHtml(e?.message ?? String(e))}</span>`);
        }
      }
    })();
    return () => { cancelled = true; };
  }, [cell?.source, cell?.diagram_kind, cell]);

  // Render Mermaid whenever source or theme changes.
  useEffect(() => {
    if (!cell || cell.diagram_kind !== "mermaid") return;
    let cancelled = false;
    const id = nextSvgId();
    (async () => {
      try {
        const mermaid = await getMermaid();
        if (cancelled) return;
        // Theme switch is a re-init in mermaid v11.
        mermaid.initialize({
          startOnLoad: false,
          securityLevel: "loose",
          theme: dark ? "dark" : "default",
          fontFamily: "JetBrains Mono, ui-monospace, monospace",
        });
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

  // Iter 167: append a chart preset to the draft (non-destructive —
  // doodle charts stack). Separate from existing content with a blank
  // line, then refocus the textarea at the end.
  const insertPreset = (snippet: string) => {
    setDraft((prev) => {
      const base = prev.replace(/\s+$/, "");
      return base ? `${base}\n\n${snippet}\n` : `${snippet}\n`;
    });
    requestAnimationFrame(() => {
      const ta = taRef.current;
      if (ta) { ta.focus(); ta.setSelectionRange(ta.value.length, ta.value.length); }
    });
  };

  return (
    <div
      className="relative"
      // Iter 61: when collapsed, shrink the outer height to just the
      // title strip (~44 px) instead of keeping the full 400+ px the
      // cell normally claims. We use a fixed px value rather than
      // "auto" because the inner is absolutely-positioned with
      // `inset-1`, which collapses to 0 when the outer is auto.
      style={{ width: w, height: cell.collapsed ? 44 : h }}
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
            {/* Iter 92: when collapsed, swap the kind selector for a
             *  compact static chip so the title strip stays clean. */}
            {cell.collapsed ? (
              <span
                className="font-hand text-sm px-1.5 py-0.5 rounded-md border-2 border-ink/30 dark:border-white/30 bg-white/60 dark:bg-black/40 text-ink/70 dark:text-white/70 shrink-0"
                title={`Diagram kind — ${cell.diagram_kind ?? "doodle"}`}
              >
                {cell.diagram_kind === "mermaid"
                  ? "🧭 Mermaid"
                  : cell.diagram_kind === "math"
                  ? "📐 Math"
                  : "🖍 Doodle"}
              </span>
            ) : (
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
            )}
            {/* Iter 92: hide Edit when collapsed (the body it'd open is hidden). */}
            {!cell.collapsed && (
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
            )}
          </div>

          {/* Body — hidden when collapsed (iter 56). */}
          {!cell.collapsed && (
          <div className="relative flex-1 overflow-auto nodrag nowheel bg-white dark:bg-[#1a1d23]">
            {editing ? (
              <div className="absolute inset-0 flex flex-col">
                {/* Iter 167: chart preset bar — doodle kind only. Each
                 *  button inserts a working snippet so the mini-syntax
                 *  is discoverable without docs. */}
                {(cell.diagram_kind === "doodle" || !cell.diagram_kind) && (
                  <div className="flex flex-wrap items-center gap-1 px-2 py-1 border-b-2 border-ink/15 dark:border-white/15 bg-marker-yellow/30 dark:bg-amber-900/20 shrink-0">
                    <span className="font-hand text-xs text-ink/60 dark:text-white/60 mr-1">Insert:</span>
                    {DOODLE_PRESETS.map((p) => (
                      <button
                        key={p.key}
                        type="button"
                        // preventDefault on mousedown keeps the textarea
                        // focused so its onBlur doesn't commit+close first.
                        onMouseDown={(e) => { e.preventDefault(); e.stopPropagation(); }}
                        onPointerDown={(e) => e.stopPropagation()}
                        onClick={(e) => { e.stopPropagation(); insertPreset(p.snippet); }}
                        className="nodrag font-hand text-xs px-1.5 py-0.5 rounded-md border-2 border-ink/40 dark:border-white/30 bg-white/90 dark:bg-[#262a31] text-ink dark:text-white hover:translate-y-[1px] transition"
                        title={`Insert a ${p.key} chart sample`}
                      >
                        {p.label}
                      </button>
                    ))}
                  </div>
                )}
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
                  className="flex-1 w-full font-mono text-sm leading-relaxed p-2 bg-white dark:bg-[#1f2228] text-ink dark:text-white outline-none resize-none"
                />
              </div>
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
