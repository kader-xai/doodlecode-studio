import { Handle, Position, NodeProps } from "reactflow";
import { useCallback, useEffect, useRef, useState } from "react";
import { ResizeHandle } from "./ResizeHandle";
import { useStore } from "../store";

// 16:9 default at presentation-friendly size. fitBounds during
// presentation uses this exact width via the per-type fallback in
// DoodleCanvas, so the iframe fills the screen on every step-pan.
const DEFAULT_W = 1280;
const DEFAULT_H = 760;

function normalizeUrl(raw: string): string {
  const t = raw.trim();
  if (!t) return "";
  if (/^[a-z][a-z0-9+.-]*:\/\//i.test(t) || t.startsWith("//")) return t;
  return (t.startsWith("localhost") || t.startsWith("127.0.0.1")
    ? "http://"
    : "https://") + t;
}

/**
 * Browser cell — iframe with a small navigation bar.
 *
 * Maintains its own URL stack so Back / Forward work even when the
 * embedded page is cross-origin (where we can't touch the real
 * iframe.contentWindow.history). Refresh remounts the iframe by
 * bumping a reload counter that gets folded into the iframe `key`.
 *
 * Created via the toolbar's "＋ Browser" button. Identified by
 * meta.cell_type === "browser"; current URL lives in meta.browser_url.
 */
export function BrowserNode({ data }: NodeProps<{ cellId: string }>) {
  const cellId = data.cellId;
  const cell = useStore((s) => s.notebook.cells.find((c) => c.id === cellId));
  const updateMeta = useStore((s) => s.updateCellMeta);
  const size = useStore((s) => s.cellSize[cellId]);
  const reportCellHeight = useStore((s) => s.reportCellHeight);
  const wrapRef = useRef<HTMLDivElement>(null);

  const url = cell?.meta?.browser_url ?? "";
  const [urlInput, setUrlInput] = useState(url);
  // Local nav stack. We DON'T persist it to .py — back/forward state
  // is session-only, the saved cell only stores the current URL.
  const [history, setHistory] = useState<string[]>(url ? [url] : []);
  const [historyIdx, setHistoryIdx] = useState<number>(url ? 0 : -1);
  const [reloadKey, setReloadKey] = useState<number>(0);
  /**
   * When true, the iframe loads through the FastAPI /api/proxy
   * endpoint, which strips X-Frame-Options and CSP frame-ancestors so
   * public sites that refuse direct iframing can be embedded. The
   * trade-offs (no auth cookies, anti-bot challenges) are shown in
   * the UI hint right next to the toggle.
   */
  const [proxyOn, setProxyOn] = useState<boolean>(false);
  // Load state — "loading" until iframe onLoad fires; "loaded" once;
  // "blocked" if onLoad doesn't fire within 7 s (likely X-Frame-Options /
  // CSP frame-ancestors block — we surface a one-click "Try proxy"
  // hint). "proxy-error" if the proxy returns a non-2xx.
  const [loadState, setLoadState] = useState<"idle" | "loading" | "loaded" | "blocked" | "proxy-error">("idle");
  const [proxyError, setProxyError] = useState<string | null>(null);
  const blockTimerRef = useRef<number | null>(null);

  // Sync if external edits change the URL — but only push onto
  // history if it's actually a new url (otherwise typing the
  // current url and pressing Go would inflate the stack).
  useEffect(() => {
    setUrlInput(url);
    if (!url) {
      setHistory([]);
      setHistoryIdx(-1);
      return;
    }
    if (historyIdx < 0 || history[historyIdx] !== url) {
      // Truncate forward stack on a new navigation.
      const trimmed = history.slice(0, historyIdx + 1);
      const next = [...trimmed, url];
      setHistory(next);
      setHistoryIdx(next.length - 1);
    }
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [url]);

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

  const navigate = (next: string) => {
    const n = normalizeUrl(next);
    if (!n || n === (cell.meta?.browser_url ?? "")) return;
    updateMeta(cellId, { ...(cell.meta ?? {}), cell_type: "browser", browser_url: n });
  };

  const canGoBack = historyIdx > 0;
  const canGoForward = historyIdx >= 0 && historyIdx < history.length - 1;

  const goBack = () => {
    if (!canGoBack) return;
    const i = historyIdx - 1;
    const target = history[i];
    setHistoryIdx(i);
    // Update the underlying URL without pushing again onto history.
    updateMeta(cellId, { ...(cell.meta ?? {}), cell_type: "browser", browser_url: target });
  };
  const goForward = () => {
    if (!canGoForward) return;
    const i = historyIdx + 1;
    const target = history[i];
    setHistoryIdx(i);
    updateMeta(cellId, { ...(cell.meta ?? {}), cell_type: "browser", browser_url: target });
  };
  const refresh = () => setReloadKey((k) => k + 1);

  // Track iframe load + apply a heuristic "blocked" timeout. Some sites
  // refuse iframing via X-Frame-Options / CSP frame-ancestors — in
  // those cases the iframe just stays blank. We can't reliably detect
  // it cross-origin, so we fall back to: if `onLoad` doesn't fire
  // within 7 s of (re)assigning src, surface a friendly hint.
  useEffect(() => {
    if (!url) { setLoadState("idle"); setProxyError(null); return; }
    setLoadState("loading");
    setProxyError(null);
    if (proxyOn) {
      // Pre-fetch through the proxy so we can show a nice error if the
      // upstream is unreachable / SSRF-blocked / 5xx. Result is cheap —
      // the iframe will also load /api/proxy?url=… but our error path
      // gives a clearer message than the raw JSON the iframe would show.
      const ctl = new AbortController();
      fetch(`/api/proxy?url=${encodeURIComponent(url)}`, { method: "GET", signal: ctl.signal })
        .then(async (r) => {
          if (r.ok) return;
          const text = await r.text();
          let msg = text;
          try {
            const parsed = JSON.parse(text);
            msg = parsed.detail ?? text;
          } catch { /* keep raw */ }
          setLoadState("proxy-error");
          setProxyError(`HTTP ${r.status} — ${msg}`);
        })
        .catch((e) => {
          if (e?.name === "AbortError") return;
          setLoadState("proxy-error");
          setProxyError(String(e?.message ?? e));
        });
      return () => ctl.abort();
    }
    // Direct mode — start blocked-detection timer.
    if (blockTimerRef.current) window.clearTimeout(blockTimerRef.current);
    blockTimerRef.current = window.setTimeout(() => {
      setLoadState((prev) => (prev === "loading" ? "blocked" : prev));
    }, 7000);
    return () => {
      if (blockTimerRef.current) {
        window.clearTimeout(blockTimerRef.current);
        blockTimerRef.current = null;
      }
    };
  }, [url, proxyOn, reloadKey]);

  const onIframeLoad = useCallback(() => {
    setLoadState("loaded");
    if (blockTimerRef.current) {
      window.clearTimeout(blockTimerRef.current);
      blockTimerRef.current = null;
    }
  }, []);

  const navBtn = (enabled: boolean) =>
    `font-hand text-base w-8 h-8 rounded border-2 transition ${
      enabled
        ? "border-ink dark:border-white/70 bg-white/80 dark:bg-black/40 text-ink dark:text-white hover:translate-x-[1px] hover:translate-y-[1px]"
        : "border-ink/30 dark:border-white/30 bg-white/40 dark:bg-black/20 text-ink/40 dark:text-white/40 cursor-not-allowed"
    }`;

  return (
    <div ref={wrapRef} data-cell-id={cellId} style={{ width: w, position: "relative" }}>
      <Handle type="target" position={Position.Left} />
      <div className="doodle-card relative p-0 overflow-hidden" style={{ height: h, borderRadius: 18 }}>
        <form
          className="flex items-center gap-1.5 px-2 py-1.5 border-b-2 border-ink/60 dark:border-white/60 nodrag"
          style={{ background: "rgba(255,255,255,0.7)" }}
          onSubmit={(e) => {
            e.preventDefault();
            navigate(urlInput);
          }}
        >
          <button
            type="button"
            className={navBtn(canGoBack)}
            onClick={goBack}
            disabled={!canGoBack}
            title="Back"
            aria-label="Back"
          >
            ◀
          </button>
          <button
            type="button"
            className={navBtn(canGoForward)}
            onClick={goForward}
            disabled={!canGoForward}
            title="Forward"
            aria-label="Forward"
          >
            ▶
          </button>
          <button
            type="button"
            className={navBtn(!!url)}
            onClick={refresh}
            disabled={!url}
            title="Refresh"
            aria-label="Refresh"
          >
            ↻
          </button>
          <span className="font-mono text-xs text-ink/60 dark:text-white/60 select-none ml-1">🌐</span>
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
          <button
            type="button"
            onClick={() => setProxyOn((v) => !v)}
            className={`font-hand text-xs px-2 py-0.5 rounded border-2 transition ${
              proxyOn
                ? "border-pink-500 bg-pink-100 dark:bg-pink-900/40 text-ink dark:text-white"
                : "border-ink/40 dark:border-white/40 bg-white/70 dark:bg-black/40 text-ink/70 dark:text-white/70"
            }`}
            title={
              proxyOn
                ? "Proxy ON — fetching via backend so sites with X-Frame-Options can load. Cookies / login DON'T carry over."
                : "Proxy OFF — direct iframe. Toggle ON to bypass X-Frame-Options on public sites."
            }
          >
            {proxyOn ? "🛡 Proxy" : "🌐 Direct"}
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
        {url ? (
          <div className="relative" style={{ height: `calc(100% - 44px)` }}>
            <iframe
              key={`${proxyOn ? "p" : "d"}:${url}#${reloadKey}`}
              src={proxyOn ? `/api/proxy?url=${encodeURIComponent(url)}` : url}
              title={`Browser ${cellId.slice(0, 6)}`}
              sandbox="allow-scripts allow-forms allow-same-origin allow-popups allow-popups-to-escape-sandbox allow-modals"
              referrerPolicy="no-referrer-when-downgrade"
              onLoad={onIframeLoad}
              style={{
                width: "100%",
                height: "100%",
                border: 0,
                background: "white",
                display: "block",
              }}
            />
            {/* Loading bar — animated stripe while waiting for onLoad. */}
            {loadState === "loading" && (
              <div className="absolute inset-x-0 top-0 h-1 bg-sky-200 dark:bg-sky-900/40 overflow-hidden">
                <div className="h-full w-1/3 bg-sky-500 animate-[browser-progress_1.2s_linear_infinite]" />
              </div>
            )}
            {/* Blocked-hint overlay (direct mode, didn't load in 7 s). */}
            {loadState === "blocked" && (
              <div className="absolute inset-0 bg-white/95 dark:bg-[#1f2228]/95 flex items-center justify-center p-6">
                <div className="max-w-md text-center font-hand">
                  <div className="text-3xl mb-2">🚧 Page didn't load</div>
                  <div className="text-base text-ink/80 dark:text-white/80 mb-4">
                    Most likely this site refuses to be iframed
                    (<code className="font-mono text-sm">X-Frame-Options</code> /
                    <code className="font-mono text-sm">CSP frame-ancestors</code>).
                    Try the proxy or open in a new tab.
                  </div>
                  <div className="flex gap-2 justify-center">
                    <button
                      type="button"
                      onClick={() => setProxyOn(true)}
                      className="btn-sketch pink text-base"
                    >
                      🛡 Try Proxy
                    </button>
                    <a
                      href={url}
                      target="_blank"
                      rel="noopener noreferrer"
                      className="btn-sketch sky text-base inline-block"
                    >
                      ↗ Open in new tab
                    </a>
                  </div>
                </div>
              </div>
            )}
            {/* Proxy-error overlay. */}
            {loadState === "proxy-error" && (
              <div className="absolute inset-0 bg-white/95 dark:bg-[#1f2228]/95 flex items-center justify-center p-6">
                <div className="max-w-md text-center font-hand">
                  <div className="text-3xl mb-2">⚠️ Proxy couldn't fetch the page</div>
                  <div className="text-sm font-mono text-red-700 dark:text-red-300 mb-3 break-words">
                    {proxyError ?? "Unknown error"}
                  </div>
                  <div className="text-sm text-ink/70 dark:text-white/70 mb-3">
                    Common causes: site needs login, anti-bot challenge,
                    private/SSRF address, slow response (&gt; 15 s), or
                    payload &gt; 8 MB.
                  </div>
                  <div className="flex gap-2 justify-center">
                    <button
                      type="button"
                      onClick={() => setProxyOn(false)}
                      className="btn-sketch text-base"
                    >
                      🌐 Try Direct
                    </button>
                    <a
                      href={url}
                      target="_blank"
                      rel="noopener noreferrer"
                      className="btn-sketch sky text-base inline-block"
                    >
                      ↗ Open in new tab
                    </a>
                  </div>
                </div>
              </div>
            )}
          </div>
        ) : (
          <div
            className="flex items-center justify-center text-ink/70 dark:text-white/70 font-hand text-lg"
            style={{ height: `calc(100% - 44px)` }}
          >
            Type a URL above and press Enter.
          </div>
        )}
      </div>
      <ResizeHandle cellId={cellId} baseWidth={w} baseHeight={h} />
      <Handle type="source" position={Position.Right} />
    </div>
  );
}
