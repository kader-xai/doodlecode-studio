import { Handle, Position, NodeProps } from "reactflow";
import { useEffect, useMemo, useRef } from "react";
import { colorFor } from "../lib/rough";
import { useStore } from "../store";
import { EditableTitle } from "./EditableTitle";
import { ResizeHandle } from "./ResizeHandle";
import { explainCode } from "../api";

const DEFAULT_W = 560;

function renderInline(s: string) {
  const parts: (string | JSX.Element)[] = [];
  const re = /(\*\*[^*]+\*\*|`[^`]+`)/g;
  let last = 0;
  let m: RegExpExecArray | null;
  let key = 0;
  while ((m = re.exec(s))) {
    if (m.index > last) parts.push(s.slice(last, m.index));
    const tok = m[0];
    if (tok.startsWith("**")) {
      parts.push(<strong key={key++}>{tok.slice(2, -2)}</strong>);
    } else {
      parts.push(
        <code key={key++} className="font-mono text-[0.9em] bg-marker-yellow/40 px-1 rounded">
          {tok.slice(1, -1)}
        </code>
      );
    }
    last = m.index + tok.length;
  }
  if (last < s.length) parts.push(s.slice(last));
  return parts;
}

function renderBody(src: string) {
  const lines = src.split("\n");
  const out: JSX.Element[] = [];
  let i = 0;
  let key = 0;
  while (i < lines.length) {
    const line = lines[i];
    // `break-words` + overflowWrap:anywhere makes long sentences AND
    // long unbroken tokens (URLs, file paths) wrap inside the cell
    // instead of overflowing the right edge.
    const wrap = "break-words [overflow-wrap:anywhere]";
    if (/^###\s+/.test(line)) {
      out.push(<h3 key={key++} className={`font-hand text-2xl mt-1 ${wrap}`}>{renderInline(line.replace(/^###\s+/, ""))}</h3>);
      i++;
    } else if (/^##\s+/.test(line)) {
      out.push(<h2 key={key++} className={`font-hand text-3xl mt-1 ${wrap}`}>{renderInline(line.replace(/^##\s+/, ""))}</h2>);
      i++;
    } else if (/^#\s+/.test(line)) {
      out.push(<h1 key={key++} className={`font-hand text-4xl mt-1 ${wrap}`}>{renderInline(line.replace(/^#\s+/, ""))}</h1>);
      i++;
    } else if (/^[-*]\s+/.test(line)) {
      const items: string[] = [];
      while (i < lines.length && /^[-*]\s+/.test(lines[i])) {
        items.push(lines[i].replace(/^[-*]\s+/, ""));
        i++;
      }
      out.push(
        <ul key={key++} className={`list-disc pl-6 font-hand text-xl leading-snug space-y-0.5 ${wrap}`}>
          {items.map((it, j) => <li key={j}>{renderInline(it)}</li>)}
        </ul>
      );
    } else if (line.trim() === "") {
      out.push(<div key={key++} className="h-2" />);
      i++;
    } else {
      out.push(<p key={key++} className={`font-hand text-xl leading-snug ${wrap}`}>{renderInline(line)}</p>);
      i++;
    }
  }
  return out;
}

export function MarkdownNode({
  data,
}: NodeProps<{ cellId: string; source: string; color?: string; kind?: string; title?: string; image?: string }>) {
  const dark = useStore((s) => s.theme === "dark");
  const cellId = data.cellId;
  const cell = useStore((s) => s.notebook.cells.find((c) => c.id === cellId));
  const setExplain = useStore((s) => s.setExplain);
  const reportCellHeight = useStore((s) => s.reportCellHeight);
  const updateMeta = useStore((s) => s.updateCellMeta);
  const setOpenEditor = useStore((s) => s.setOpenEditor);
  const size = useStore((s) => s.cellSize[cellId]);

  const wrapRef = useRef<HTMLDivElement>(null);

  useEffect(() => {
    if (!cell) return;
    explainCode(cell.source, "beginner", cell.meta ?? undefined)
      .then((r) => setExplain(cellId, r))
      .catch(() => {});
  }, [cell?.meta, cell?.source, cellId, setExplain, cell]);

  useEffect(() => {
    const el = wrapRef.current;
    if (!el) return;
    const ro = new ResizeObserver((entries) => {
      for (const e of entries) reportCellHeight(cellId, Math.ceil(e.contentRect.height));
    });
    ro.observe(el);
    return () => ro.disconnect();
  }, [cellId, reportCellHeight]);

  const rendered = useMemo(() => renderBody(data.source || ""), [data.source]);
  const fill = colorFor({ color: data.color, kind: data.kind ?? "intro", dark });
  const W = size?.width ?? DEFAULT_W;

  // Sizing is now driven entirely by CSS:
  //   - User dragged the corner → `height: size.height` locks the card.
  //   - User hasn't resized      → height is auto and the card grows
  //                                with its content.
  // DoodleBorder measures its own parent (the doodle-card) via
  // ResizeObserver and rebuilds the wavy SVG to match in the same
  // frame, so the outline always wraps the actual painted card.

  return (
    <div ref={wrapRef} data-cell-id={cellId} style={{ width: W, position: "relative" }}>
      <Handle type="target" position={Position.Left} />
      <div
        className="doodle-card relative"
        style={{
          // When the user has dragged the corner, lock the card to that
          // exact height so the box and SVG move together pixel-for-pixel.
          // Otherwise leave height auto so the card grows with content.
          height: size?.height,
          // Paint the card with the section color so content always sits
          // on the right background, even if the SVG doodle border is
          // briefly under-sized during a resize / first render.
          background: fill,
          borderRadius: 18,
          overflow: size?.height ? "hidden" : undefined,
        }}
      >
        <div
          className="relative -mx-3 -mt-3 px-3 py-1.5 mb-2 border-b-2 border-ink/60 dark:border-white/60 flex items-center justify-between rounded-t-lg"
          style={{ background: "rgba(255,255,255,0.45)" }}
        >
          <div className="flex items-baseline gap-2 min-w-0 flex-1">
            <EditableTitle
              value={data.title}
              className="font-hand text-2xl leading-tight"
              onCommit={(next) =>
                updateMeta(cellId, { ...(cell?.meta ?? {}), title: next })
              }
            />
          </div>
          <div className="flex gap-1 nodrag shrink-0">
            <button
              className="font-hand text-lg w-8 h-8 rounded-lg border-2 border-ink dark:border-white/70 bg-white/70 dark:bg-black/40 hover:translate-x-[1px] hover:translate-y-[1px] transition"
              onPointerDown={(e) => e.stopPropagation()}
              onMouseDown={(e) => e.stopPropagation()}
              onClick={(e) => { e.stopPropagation(); setOpenEditor({ kind: "text", cellId }); }}
              title="Edit text box"
            >
              📝
            </button>
            <button
              className="font-hand text-lg w-8 h-8 rounded-lg border-2 border-ink dark:border-white/70 bg-white/70 dark:bg-black/40 hover:translate-x-[1px] hover:translate-y-[1px] transition"
              onPointerDown={(e) => e.stopPropagation()}
              onMouseDown={(e) => e.stopPropagation()}
              onClick={(e) => { e.stopPropagation(); setOpenEditor({ kind: "callout", cellId }); }}
              title="Edit side callout"
            >
              ✎
            </button>
          </div>
        </div>
        <div className="relative">
          {data.image && (
            <img
              src={data.image}
              alt={data.title ?? ""}
              className="mb-2 max-w-full max-h-72 object-contain rounded-lg border-2 border-ink/70 dark:border-white/60"
            />
          )}
          {rendered}
        </div>
        <ResizeHandle cellId={cellId} baseWidth={W} baseHeight={size?.height ?? 200} />
      </div>
      <Handle type="source" position={Position.Right} />
    </div>
  );
}
