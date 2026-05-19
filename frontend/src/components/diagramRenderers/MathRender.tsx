import { useEffect, useState } from "react";

/** KaTeX renderer. Each non-blank line is rendered as a display
 *  equation. KaTeX is small (~30 KB gz) so we bundle it directly. */
let katexPromise: Promise<typeof import("katex").default> | null = null;
let cssLoaded = false;
function loadKatex() {
  if (!katexPromise) {
    katexPromise = import("katex").then((m) => m.default);
    if (!cssLoaded) {
      const link = document.createElement("link");
      link.rel = "stylesheet";
      link.href =
        "https://cdn.jsdelivr.net/npm/katex@0.16.11/dist/katex.min.css";
      document.head.appendChild(link);
      cssLoaded = true;
    }
  }
  return katexPromise;
}

export function MathRender({
  source,
  fontScale = 1,
}: {
  source: string;
  fontScale?: number;
}) {
  const [html, setHtml] = useState<string>("");
  const [err, setErr] = useState<string | null>(null);

  useEffect(() => {
    let cancelled = false;
    if (!source.trim()) {
      setHtml("");
      setErr(null);
      return;
    }
    loadKatex()
      .then((katex) => {
        if (cancelled) return;
        // Strip `$$ … $$` wrappers and split into display blocks.
        const cleaned = source
          .replace(/\$\$/g, "")
          .split(/\n\s*\n/)
          .map((b) => b.trim())
          .filter(Boolean);
        try {
          const out = cleaned
            .map((tex) =>
              katex.renderToString(tex, {
                displayMode: true,
                throwOnError: false,
                errorColor: "#e03131",
              })
            )
            .join("\n");
          setHtml(out);
          setErr(null);
        } catch (e) {
          setErr(e instanceof Error ? e.message : String(e));
        }
      })
      .catch((e) => !cancelled && setErr(String(e)));
    return () => { cancelled = true; };
  }, [source]);

  if (err) {
    return (
      <pre className="m-2 p-3 rounded-lg border-2 border-red-500 bg-red-50 text-red-700 text-xs font-mono whitespace-pre-wrap">
        KaTeX error:
        {"\n"}
        {err}
      </pre>
    );
  }
  return (
    <div
      className="w-full h-full overflow-auto p-6 flex flex-col gap-4 items-center justify-center"
      style={{ fontSize: `${Math.round(20 * fontScale)}px` }}
      dangerouslySetInnerHTML={{ __html: html }}
    />
  );
}
