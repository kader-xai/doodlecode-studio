import { Handle, Position, NodeProps } from "reactflow";
import { useEffect, useRef, useState } from "react";
import { ResizeHandle } from "./ResizeHandle";
import { useStore } from "../store";

const DEFAULT_W = 960;
const DEFAULT_H = 600;

/**
 * Browser cell. Renders an iframe loading any URL.
 * Uses native iframe — the lightest possible "embedded browser"
 * (no headless Chromium, no extra runtime). Sites that send
 * X-Frame-Options: DENY can't be embedded — we show a hint then.
 *
 * Created via the toolbar's "＋ Browser" button. Identified by
 * meta.cell_type === "browser"; URL lives in meta.browser_url.
 */
export function BrowserNode({ data }: NodeProps<{ cellId: string }>) {
  const cellId = data.cellId;
  const cell = useStore((s) => s.notebook.cells.find((c) => c.id === cellId));
  const updateMeta = useStore((s) => s.updateCellMeta);
  const size = useStore((s) => s.cellSize[cellId]);
  const reportCellHeight = useStore((s) => s.reportCellHeight);
  const wrapRef = useRef<HTMLDivElement>(null);
  const [urlInput, setUrlInput] = useState(cell?.meta?.browser_url ?? "");

  // Sync if external edits change the URL.
  useEffect(() => {
    setUrlInput(cell?.meta?.browser_url ?? "");
  }, [cell?.meta?.browser_url]);

  // Report measured height so the next cell shifts down.
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
  const url = cell.meta?.browser_url ?? "";

  const commitUrl = (v: string) => {
    let next = v.trim();
    if (!next) return;
    // Auto-prefix protocol so "localhost:3000" / "example.com" Just Work.
    if (!/^[a-z][a-z0-9+.-]*:\/\//i.test(next) && !next.startsWith("//")) {
      next = (next.startsWith("localhost") || next.startsWith("127.0.0.1")
        ? "http://"
        : "https://") + next;
    }
    if (next === (cell.meta?.browser_url ?? "")) return;
    updateMeta(cellId, { ...(cell.meta ?? {}), cell_type: "browser", browser_url: next });
  };

  return (
    <div ref={wrapRef} data-cell-id={cellId} style={{ width: w, position: "relative" }}>
      <Handle type="target" position={Position.Left} />
      <div className="doodle-card relative p-0 overflow-hidden" style={{ height: h, borderRadius: 18 }}>
        {/* URL bar.
         *  Form's onSubmit is preventDefault'd — even though there is
         *  no real submission target, this guarantees Enter / Go can
         *  never accidentally navigate the parent page. */}
        <form
          className="flex items-center gap-2 px-2 py-1.5 border-b-2 border-ink/60 dark:border-white/60 nodrag"
          style={{ background: "rgba(255,255,255,0.7)" }}
          onSubmit={(e) => {
            e.preventDefault();
            commitUrl(urlInput);
          }}
        >
          <span className="font-mono text-xs text-ink/60 dark:text-white/60 select-none">🌐</span>
          <input
            type="text"
            inputMode="url"
            className="flex-1 font-mono text-sm bg-white dark:bg-[#0f1115] text-ink dark:text-white px-2 py-1 rounded border border-ink/40 dark:border-white/40"
            placeholder="example.com  or  http://localhost:3000"
            value={urlInput}
            onChange={(e) => setUrlInput(e.target.value)}
            onPointerDown={(e) => e.stopPropagation()}
            onMouseDown={(e) => e.stopPropagation()}
          />
          <button
            type="submit"
            className="font-hand text-base px-2 py-0.5 rounded border-2 border-ink dark:border-white/70 bg-white/80 dark:bg-black/40 text-ink dark:text-white hover:translate-x-[1px] hover:translate-y-[1px] transition"
            title="Load URL"
          >
            Go
          </button>
          {url && (
            <a
              href={url}
              target="_blank"
              rel="noopener noreferrer"
              className="text-sm underline decoration-dotted underline-offset-2 text-ink/70 dark:text-white/70"
              title="Open in a new browser tab"
              onClick={(e) => e.stopPropagation()}
            >
              ↗
            </a>
          )}
        </form>
        {/* iframe */}
        {url ? (
          <iframe
            key={url}
            src={url}
            title={`Browser ${cellId.slice(0, 6)}`}
            sandbox="allow-scripts allow-forms allow-same-origin allow-popups allow-popups-to-escape-sandbox allow-modals"
            referrerPolicy="no-referrer-when-downgrade"
            style={{
              width: "100%",
              height: `calc(100% - 40px)`,
              border: 0,
              background: "white",
              display: "block",
            }}
          />
        ) : (
          <div className="flex items-center justify-center text-ink/70 dark:text-white/70 font-hand text-lg" style={{ height: `calc(100% - 40px)` }}>
            Type a URL above and press Enter.
          </div>
        )}
      </div>
      <ResizeHandle cellId={cellId} baseWidth={w} baseHeight={h} />
      <Handle type="source" position={Position.Right} />
    </div>
  );
}
