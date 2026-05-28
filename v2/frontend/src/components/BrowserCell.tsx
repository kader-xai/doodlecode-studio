import { useEffect, useRef, useState } from "react";
import { Handle, NodeProps, Position } from "reactflow";
import { DoodleBorder } from "./DoodleBorder";
import { EditableTitle } from "./EditableTitle";
import { ResizeHandle } from "./ResizeHandle";
import { useStore } from "../store";

const DEFAULT_W = 720;
const DEFAULT_H = 480;

const PROXY_PREFIX = "/api/proxy?url=";

/** A "browser cell" URL may already be proxied. We surface the
 *  underlying target URL in the URL bar regardless. */
function unwrapProxied(source: string): { url: string; proxied: boolean } {
  if (source.startsWith(PROXY_PREFIX)) {
    try {
      return { url: decodeURIComponent(source.slice(PROXY_PREFIX.length)), proxied: true };
    } catch {
      return { url: source, proxied: false };
    }
  }
  return { url: source, proxied: false };
}

function wrapProxied(url: string): string {
  return PROXY_PREFIX + encodeURIComponent(url);
}

/**
 * Browser cell — iframe with URL bar + Back/Forward/Refresh.
 *
 * **Interact-mode gate** (the v1 lesson written down): an iframe with
 * normal pointer events traps clicks/keys, making the canvas feel
 * frozen. So by default the iframe gets `pointer-events: none` and an
 * overlay sits on top saying "Click to interact". When the user clicks
 * (or presses B), `interactiveBrowserId` flips to this cell and the
 * iframe receives events. Esc / B / the floating "Exit" pill releases.
 *
 * Navigation history is local — back/forward stacks live in the
 * component (useState). The "current URL" is `cell.source`, persisted
 * to file. Refreshes are implemented by bumping a key on the iframe.
 *
 * Cross-origin pages cannot be navigated via JS, so the URL bar
 * effectively replaces the iframe src each time. That's fine: this is
 * a display surface, not a real browser shell.
 */
export function BrowserCell({ data, selected }: NodeProps<{ cellId: string }>) {
  const cellId = data.cellId;
  const cell = useStore((s) => s.cells.find((c) => c.id === cellId));
  const setSource = useStore((s) => s.setSource);
  const setTitle = useStore((s) => s.setTitle);
  const setSelected = useStore((s) => s.setSelected);
  const toggleCollapse = useStore((s) => s.toggleCollapse);
  const interactiveBrowserId = useStore((s) => s.interactiveBrowserId);
  const setInteractiveBrowser = useStore((s) => s.setInteractiveBrowser);
  const renameTick = useStore((s) => s.renameTick[cellId] ?? 0);

  // F2 → title rename bridge.
  const [forceEditTitle, setForceEditTitle] = useState(false);
  useEffect(() => {
    if (renameTick > 0) {
      setForceEditTitle(true);
      const t = setTimeout(() => setForceEditTitle(false), 50);
      return () => clearTimeout(t);
    }
  }, [renameTick]);

  // URL bar shows the *unwrapped* URL even when the cell is
  // currently going through the proxy. That's what the user typed
  // last, and what they want to edit.
  const wrapped = unwrapProxied(cell?.source ?? "");
  const [urlDraft, setUrlDraft] = useState(wrapped.url);
  useEffect(() => {
    setUrlDraft(wrapped.url);
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [cell?.source]);

  // Navigation history (in-memory only). Each commit pushes the new
  // URL onto `back` and clears `forward`.
  const backRef = useRef<string[]>([]);
  const forwardRef = useRef<string[]>([]);
  const [refreshKey, setRefreshKey] = useState(0);
  // useState only to force re-render when nav history changes (refs alone don't).
  const [, bumpNav] = useState(0);

  const commit = (raw: string) => {
    if (!cell) return;
    const trimmed = raw.trim();
    if (!trimmed) return;
    const url = /^https?:\/\//i.test(trimmed) ? trimmed : `https://${trimmed}`;
    // Preserve the current proxy mode when navigating.
    const next = wrapped.proxied ? wrapProxied(url) : url;
    if (next === cell.source) return;
    backRef.current.push(cell.source);
    forwardRef.current = [];
    setSource(cellId, next);
    setUrlDraft(url);
    bumpNav((n) => n + 1);
  };

  /** Toggle the proxy on/off without committing to history. */
  const toggleProxy = () => {
    if (!cell) return;
    const { url, proxied } = unwrapProxied(cell.source);
    setSource(cellId, proxied ? url : wrapProxied(url));
    setRefreshKey((k) => k + 1);
  };

  const goBack = () => {
    if (!cell || !backRef.current.length) return;
    const prev = backRef.current.pop()!;
    forwardRef.current.push(cell.source);
    setSource(cellId, prev);
    setUrlDraft(prev);
    bumpNav((n) => n + 1);
  };

  const goForward = () => {
    if (!cell || !forwardRef.current.length) return;
    const next = forwardRef.current.pop()!;
    backRef.current.push(cell.source);
    setSource(cellId, next);
    setUrlDraft(next);
    bumpNav((n) => n + 1);
  };

  if (!cell) return null;

  const w = cell.w ?? DEFAULT_W;
  const h = cell.h ?? DEFAULT_H;
  const interactive = interactiveBrowserId === cellId;
  const ringColor = selected ? "#c2255c" : "var(--doodle-stroke, #2a2a2a)";
  const ringWidth = selected ? 3.5 : 2.5;

  return (
    <div
      className="relative"
      // Iter 61: collapsed cells shrink to ~44 px so just the title
      // strip is visible (URL bar + iframe both hidden).
      style={{ width: w, height: cell.collapsed ? 44 : h }}
      onClickCapture={() => setSelected(cellId)}
    >
      <Handle type="target" position={Position.Left} className="!bg-transparent !border-0" />

      <div className="absolute inset-0">
        <DoodleBorder stroke={ringColor} fill="#ffffff" strokeWidth={ringWidth} radius={14} />

        <div className="absolute inset-1 flex flex-col overflow-hidden rounded-lg bg-white dark:bg-[#262a31]">
          {/* URL bar — hidden when collapsed (iter 56). */}
          {!cell.collapsed && (
          <div className="flex items-center gap-1 px-1.5 py-1 border-b-2 border-ink/30 dark:border-white/30 bg-white/80 dark:bg-[#1f2228] nodrag">
            <NavBtn label="◀" title="Back" onClick={goBack} disabled={!backRef.current.length} />
            <NavBtn label="▶" title="Forward" onClick={goForward} disabled={!forwardRef.current.length} />
            <NavBtn label="↻" title="Refresh" onClick={() => setRefreshKey((k) => k + 1)} />
            <form
              className="flex-1"
              onSubmit={(e) => { e.preventDefault(); commit(urlDraft); }}
            >
              <input
                type="text"
                value={urlDraft}
                onChange={(e) => setUrlDraft(e.target.value)}
                onKeyDown={(e) => e.stopPropagation()}
                onPointerDown={(e) => e.stopPropagation()}
                onClick={(e) => e.stopPropagation()}
                placeholder="https://example.com"
                spellCheck={false}
                className="w-full px-2 py-0.5 font-mono text-xs rounded-md border-2 border-ink/30 dark:border-white/30 bg-white dark:bg-[#1a1d23] text-ink dark:text-white outline-none focus:border-[#c2255c]"
              />
            </form>
            <button
              type="button"
              onClick={(e) => { e.stopPropagation(); commit(urlDraft); }}
              onPointerDown={(e) => e.stopPropagation()}
              className="font-hand text-sm px-2 py-0.5 rounded-md border-2 border-ink dark:border-white/70 bg-marker-mint dark:bg-[#2b8a3e] text-ink dark:text-white shadow-sketch hover:translate-y-[1px] transition"
            >
              Go
            </button>
            <button
              type="button"
              onClick={(e) => { e.stopPropagation(); toggleProxy(); }}
              onPointerDown={(e) => e.stopPropagation()}
              title={wrapped.proxied
                ? "Proxy ON — bypassing X-Frame-Options. Click to go direct."
                : "Direct mode. Click to load through the server proxy (works on Google, GitHub, etc.)."}
              className={`font-hand text-sm w-7 h-7 rounded-md border-2 transition shrink-0 ${
                wrapped.proxied
                  ? "bg-marker-mint border-ink dark:bg-[#2b8a3e] dark:border-white text-ink dark:text-white shadow-sketch"
                  : "bg-white/90 dark:bg-[#262a31] border-ink/40 dark:border-white/30 text-ink dark:text-white"
              }`}
            >
              🛡
            </button>
          </div>
          )}

          {/* Title strip — drag-handle (no `nodrag`). The Exit button
           *  carries its own nodrag so clicks pass through. */}
          <div className="px-2 py-0.5 flex items-center justify-between gap-2 border-b border-ink/10 dark:border-white/10">
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
              placeholder="(untitled site)"
            />
            {interactive && (
              <button
                type="button"
                onClick={(e) => { e.stopPropagation(); setInteractiveBrowser(null); }}
                onPointerDown={(e) => e.stopPropagation()}
                onMouseDown={(e) => e.stopPropagation()}
                className="nodrag font-hand text-sm px-2 py-0.5 rounded-md border-2 border-ink dark:border-white/70 bg-marker-pink dark:bg-[#a61e4d] text-ink dark:text-white shadow-sketch hover:translate-y-[1px] transition shrink-0"
                title="Stop interacting (Esc / B)"
              >
                🚪 Exit
              </button>
            )}
          </div>

          {/* Iframe + interact-mode overlay — hidden when collapsed (iter 56). */}
          {!cell.collapsed && (
          <div className="relative flex-1 overflow-hidden">
            <iframe
              key={refreshKey}
              src={cell.source || "about:blank"}
              title={cell.title ?? "browser"}
              referrerPolicy="strict-origin-when-cross-origin"
              sandbox="allow-scripts allow-same-origin allow-forms allow-popups allow-popups-to-escape-sandbox"
              style={{
                display: "block",
                width: "100%",
                height: "100%",
                border: "0",
                background: "#fafafa",
                // The toggle: when not interactive, the iframe ignores
                // pointer events so canvas/overlay get clicks instead.
                pointerEvents: interactive ? "auto" : "none",
              }}
            />
            {!interactive && (
              <div
                className="absolute inset-0 flex items-center justify-center bg-black/0 hover:bg-black/10 transition cursor-pointer"
                onClick={(e) => {
                  e.stopPropagation();
                  setSelected(cellId);
                  setInteractiveBrowser(cellId);
                }}
                title="Click to interact (B). Esc / B to release."
              >
                <div className="font-hand text-xl px-3 py-1.5 rounded-xl border-2 border-ink dark:border-white/70 bg-white/80 dark:bg-[#262a31]/90 shadow-sketch">
                  🖱  Click to interact
                </div>
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

function NavBtn({
  label,
  title,
  onClick,
  disabled,
}: {
  label: string;
  title: string;
  onClick: () => void;
  disabled?: boolean;
}) {
  return (
    <button
      type="button"
      onClick={(e) => { e.stopPropagation(); onClick(); }}
      onPointerDown={(e) => e.stopPropagation()}
      disabled={disabled}
      title={title}
      className="font-hand text-base w-7 h-7 rounded-md border-2 border-ink dark:border-white/70 bg-white/90 dark:bg-[#262a31] text-ink dark:text-white shadow-sketch hover:translate-y-[1px] transition disabled:opacity-30 disabled:cursor-not-allowed"
    >
      {label}
    </button>
  );
}
