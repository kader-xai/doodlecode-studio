import { useEffect, useRef, useState } from "react";

/** Lazily-loaded Mermaid renderer.
 *  Mermaid is ~700 KB gzipped; we don't want to pay that on the
 *  landing page. The import only fires when a Diagram cell mounts.
 *  Once loaded, subsequent renders use the cached promise. */
let mermaidPromise: Promise<typeof import("mermaid").default> | null = null;
function loadMermaid() {
  if (!mermaidPromise) {
    mermaidPromise = import("mermaid").then((m) => m.default);
  }
  return mermaidPromise;
}

const BASE_FONT_PX = 16;

export function MermaidRender({
  source,
  fontScale = 1,
}: {
  source: string;
  fontScale?: number;
}) {
  const ref = useRef<HTMLDivElement>(null);
  const [err, setErr] = useState<string | null>(null);
  const [svg, setSvg] = useState<string>("");

  useEffect(() => {
    let cancelled = false;
    if (!source.trim()) {
      setSvg("");
      setErr(null);
      return;
    }
    loadMermaid()
      .then(async (mermaid) => {
        // Re-initialize on every render — Mermaid stores config
        // globally so the most recent fontSize wins. Cheap (no
        // re-download since import() is cached).
        mermaid.initialize({
          startOnLoad: false,
          theme: "neutral",
          securityLevel: "loose",
          fontFamily: "Caveat, Patrick Hand, cursive",
          fontSize: Math.round(BASE_FONT_PX * fontScale),
          flowchart: { curve: "basis", padding: 12 },
        });
        const id = "m_" + Math.random().toString(36).slice(2);
        try {
          const { svg } = await mermaid.render(id, source);
          if (!cancelled) {
            setSvg(svg);
            setErr(null);
          }
        } catch (e) {
          if (!cancelled) {
            setErr(e instanceof Error ? e.message : String(e));
            setSvg("");
          }
        }
      })
      .catch((e) => !cancelled && setErr(String(e)));
    return () => { cancelled = true; };
  }, [source, fontScale]);

  if (err) {
    return (
      <pre className="m-2 p-3 rounded-lg border-2 border-red-500 bg-red-50 dark:bg-red-900/40 text-red-700 dark:text-red-200 text-xs font-mono whitespace-pre-wrap">
        Mermaid parse error:
        {"\n"}
        {err}
      </pre>
    );
  }
  return (
    <div
      ref={ref}
      className="w-full h-full flex items-center justify-center p-4 overflow-auto"
      dangerouslySetInnerHTML={{ __html: svg }}
    />
  );
}
