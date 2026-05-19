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

// Matches `![alt](url)` (the whole line is one image/video).
const MEDIA_RE = /^\s*!\[([^\]]*)\]\(([^)]+)\)\s*$/;
const VIDEO_EXT = /\.(mp4|webm|mov|m4v)(\?|#|$)/i;

/** True if the cell's source is JUST one `![](...)` line (media-only). */
export function isMediaOnlySource(src: string | undefined | null): boolean {
  if (!src) return false;
  const lines = src.trim().split("\n").map((l) => l.trim()).filter(Boolean);
  if (lines.length !== 1) return false;
  return /^!\[[^\]]*\]\([^)]+\)$/.test(lines[0]);
}

/** True if the cell's markdown body contains any media tag. */
export function cellHasMedia(src: string | undefined | null): boolean {
  if (!src) return false;
  for (const ln of src.split("\n")) {
    const m = ln.match(MEDIA_RE);
    if (!m) continue;
    return true;
  }
  return false;
}

function MediaBlock({ url, alt }: { url: string; alt: string }) {
  const isVideo = VIDEO_EXT.test(url);
  // Wrapper has `resize: both` so the user can drag the bottom-right
  // corner to resize. `overflow: hidden` clips the resize-handle visual.
  // The media element fills the wrapper (width 100%, auto-height).
  if (isVideo) {
    return (
      <span
        className="block my-2 mx-auto rounded-lg border-2 border-ink/70 dark:border-white/60 nowheel"
        style={{ resize: "both", overflow: "hidden", maxWidth: "100%" }}
      >
        <video
          src={url}
          autoPlay
          loop
          muted
          playsInline
          preload="auto"
          style={{ display: "block", width: "100%", height: "auto" }}
        />
      </span>
    );
  }
  return (
    <span
      className="block my-2 rounded-lg border-2 border-ink/70 dark:border-white/60"
      style={{
        resize: "both",
        overflow: "hidden",
        // Show the image at its NATURAL size by default. `max-width:100%`
        // keeps wide screenshots inside the card. Height adjusts via
        // the resize handle in the bottom-right corner.
        display: "inline-block",
        maxWidth: "100%",
      }}
    >
      <img
        src={url}
        alt={alt}
        style={{ display: "block", width: "100%", height: "auto" }}
      />
    </span>
  );
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
    const media = line.match(MEDIA_RE);
    if (media) {
      out.push(<MediaBlock key={key++} url={media[2]} alt={media[1]} />);
      i++;
      continue;
    }
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
  // Per-cell text font scale. Applied as a CSS transform on the
  // rendered body so headings + paragraphs + bullets all scale
  // together (Tailwind utility classes set explicit sizes, so a
  // wrapper font-size wouldn't propagate). 0.7–2.4 clamp.
  const rawTextScale = cell?.meta?.text_font_scale ?? 1;
  const textScale = Math.max(0.7, Math.min(2.4, rawTextScale));

  // Sizing is now driven entirely by CSS:
  //   - User dragged the corner → `height: size.height` locks the card.
  //   - User hasn't resized      → height is auto and the card grows
  //                                with its content.
  // DoodleBorder measures its own parent (the doodle-card) via
  // ResizeObserver and rebuilds the wavy SVG to match in the same
  // frame, so the outline always wraps the actual painted card.

  // A "media-only" cell has just a single `![](...)` in its body and
  // no other prose. Rendered frameless and full-bleed — the image /
  // video fills the card on BOTH width and height (via object-fit),
  // and the existing corner ResizeHandle drives both dims.
  const mediaOnly = (() => {
    const src = (data.source || "").trim();
    if (!src) return null;
    const lines = src.split("\n").map((l) => l.trim()).filter(Boolean);
    if (lines.length !== 1) return null;
    const m = lines[0].match(/^!\[([^\]]*)\]\(([^)]+)\)$/);
    if (!m) return null;
    return { alt: m[1], url: m[2], isVideo: VIDEO_EXT.test(m[2]) };
  })();

  if (mediaOnly) {
    const cardH = size?.height ?? 360;
    const inner: React.CSSProperties = {
      display: "block",
      width: "100%",
      height: "100%",
      objectFit: "contain",
      background: "#000",
    };
    return (
      <div ref={wrapRef} data-cell-id={cellId} style={{ width: W, position: "relative" }}>
        <Handle type="target" position={Position.Left} />
        <div
          className="doodle-card relative p-0 overflow-hidden"
          style={{ height: cardH, background: fill, borderRadius: 18 }}
        >
          {mediaOnly.isVideo ? (
            <video
              src={mediaOnly.url}
              autoPlay
              loop
              muted
              playsInline
              preload="auto"
              style={inner}
            />
          ) : (
            <img src={mediaOnly.url} alt={mediaOnly.alt} style={inner} />
          )}
        </div>
        <ResizeHandle cellId={cellId} baseWidth={W} baseHeight={cardH} />
        <Handle type="source" position={Position.Right} />
      </div>
    );
  }

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
          className="relative -mx-3 -mt-3 px-3 py-1.5 mb-2 border-b-2 border-ink/60 dark:border-white/60 rounded-t-lg"
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
        </div>
        <div className="relative">
          {data.image && (
            // Top-level cell image: render at its NATURAL size,
            // constrained only by card width. The user can drag the
            // corner to resize. Card auto-grows to fit.
            <span
              className="block mb-2 rounded-lg border-2 border-ink/70 dark:border-white/60"
              style={{
                resize: "both",
                overflow: "hidden",
                display: "inline-block",
                maxWidth: "100%",
              }}
            >
              <img
                src={data.image}
                alt={data.title ?? ""}
                style={{ display: "block", width: "100%", height: "auto" }}
              />
            </span>
          )}
          <div
            style={{
              transform: textScale === 1 ? undefined : `scale(${textScale})`,
              transformOrigin: "top left",
              width: textScale > 1 ? `${100 / textScale}%` : "100%",
            }}
          >
            {rendered}
          </div>
        </div>
        <ResizeHandle cellId={cellId} baseWidth={W} baseHeight={size?.height ?? 200} />
      </div>
      <Handle type="source" position={Position.Right} />
    </div>
  );
}
