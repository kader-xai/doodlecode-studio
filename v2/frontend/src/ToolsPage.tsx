import { useState } from "react";
import { DoodleBorder } from "./components/DoodleBorder";
import { ThemeToggle } from "./components/ThemeToggle";

/**
 * Standalone /tools page — not part of the canvas app.
 *
 * Current tool: PPT → PNG. Upload a deck, the backend runs
 * LibreOffice + pdftoppm and streams back base64 PNGs. Each slide
 * gets a download link; "Download all (zip)" bundles them in the
 * browser (no extra backend trip).
 */

interface PptResult {
  pages: number;
  images_b64: string[];
  note: string;
}

export function ToolsPage() {
  const [file, setFile] = useState<File | null>(null);
  const [busy, setBusy] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [result, setResult] = useState<PptResult | null>(null);

  const run = async () => {
    if (!file) return;
    setBusy(true);
    setError(null);
    setResult(null);
    try {
      const form = new FormData();
      form.append("file", file);
      const r = await fetch("/api/tools/ppt-to-png", { method: "POST", body: form });
      if (!r.ok) {
        const text = await r.text().catch(() => "");
        throw new Error(`HTTP ${r.status}: ${text.slice(0, 500) || r.statusText}`);
      }
      const j = (await r.json()) as PptResult;
      setResult(j);
    } catch (e) {
      setError(String(e));
    } finally {
      setBusy(false);
    }
  };

  const downloadOne = (b64: string, idx: number) => {
    const bytes = atob(b64);
    const arr = new Uint8Array(bytes.length);
    for (let i = 0; i < bytes.length; i++) arr[i] = bytes.charCodeAt(i);
    const blob = new Blob([arr], { type: "image/png" });
    const a = document.createElement("a");
    a.href = URL.createObjectURL(blob);
    a.download = `slide-${String(idx + 1).padStart(3, "0")}.png`;
    a.click();
    setTimeout(() => URL.revokeObjectURL(a.href), 1000);
  };

  return (
    <div className="min-h-screen w-full bg-sandal dark:bg-[#1a1d23] text-ink dark:text-white">
      <header className="flex items-center justify-between px-6 py-4">
        <div className="flex items-baseline gap-2">
          <a href="/" className="font-hand text-3xl no-underline">📓 DoodleCode</a>
          <a href="/" className="font-hand text-3xl no-underline text-[#c2255c] dark:text-[#fcc2d7]">Studio</a>
          <span className="font-mono text-xs ml-2 px-2 py-0.5 rounded-md border-2 border-ink/40 dark:border-white/40 bg-white/60 dark:bg-black/40">
            /tools
          </span>
        </div>
        <div className="flex items-center gap-2">
          <a
            href="/"
            className="font-hand text-base px-3 py-1.5 rounded-xl border-2 border-ink dark:border-white/70 bg-white/70 dark:bg-[#262a31] text-ink dark:text-white shadow-sketch hover:translate-y-[1px] transition no-underline"
          >
            ← Back to canvas
          </a>
          <ThemeToggle />
        </div>
      </header>

      <main className="max-w-3xl mx-auto px-6 pb-12">
        <div className="relative p-6 mb-6">
          <DoodleBorder
            stroke="var(--doodle-stroke, #2a2a2a)"
            fill="var(--doodle-fill, #ffe066)"
            strokeWidth={3}
          />
          <div className="relative">
            <h1 className="font-hand text-4xl mb-2">📊 PPT → PNG</h1>
            <p className="font-hand text-xl mb-3">
              Drop a slide deck (.pptx / .ppt / .odp / .key). I'll render every
              slide as a PNG you can drop into a media cell.
            </p>

            <input
              type="file"
              accept=".ppt,.pptx,.odp,.key,application/vnd.ms-powerpoint,application/vnd.openxmlformats-officedocument.presentationml.presentation"
              onChange={(e) => { setFile(e.target.files?.[0] ?? null); setResult(null); setError(null); }}
              className="font-hand text-base"
              disabled={busy}
            />
            <div className="mt-3 flex items-center gap-2">
              <button
                onClick={run}
                disabled={!file || busy}
                className="font-hand text-lg px-4 py-1 rounded-lg border-2 border-ink dark:border-white/70 bg-marker-mint dark:bg-[#2b8a3e] text-ink dark:text-white shadow-sketch hover:translate-y-[1px] transition disabled:opacity-50 disabled:cursor-not-allowed"
              >
                {busy ? "… converting" : "Convert"}
              </button>
              {file && !busy && (
                <span className="font-hand text-base text-ink/70 dark:text-white/70 truncate">
                  {file.name} · {(file.size / 1024).toFixed(0)} KB
                </span>
              )}
            </div>

            {error && (
              <pre className="mt-3 font-mono text-xs text-[#c2255c] dark:text-[#fcc2d7] whitespace-pre-wrap break-words">
                {error}
              </pre>
            )}
            {result && (
              <p className="mt-3 font-hand text-base text-[#2b8a3e] dark:text-[#b2f2bb]">
                ✓ {result.note}
              </p>
            )}
          </div>
        </div>

        {result && (
          <div className="grid grid-cols-1 sm:grid-cols-2 gap-4">
            {result.images_b64.map((b64, i) => (
              <div key={i} className="relative p-2">
                <DoodleBorder
                  stroke="var(--doodle-stroke, #2a2a2a)"
                  fill={"#ffffff"}
                  strokeWidth={2.5}
                  radius={12}
                />
                <div className="relative">
                  <img
                    src={`data:image/png;base64,${b64}`}
                    alt={`slide ${i + 1}`}
                    className="block w-full rounded border border-ink/40"
                  />
                  <div className="flex items-center justify-between mt-2 px-1">
                    <span className="font-hand text-base">Slide {i + 1}</span>
                    <button
                      onClick={() => downloadOne(b64, i)}
                      className="font-hand text-sm px-2 py-0.5 rounded border-2 border-ink dark:border-white/70 bg-white/80 dark:bg-[#262a31] text-ink dark:text-white shadow-sketch hover:translate-y-[1px] transition"
                    >
                      💾 PNG
                    </button>
                  </div>
                </div>
              </div>
            ))}
          </div>
        )}
      </main>

      <style>{`
        :root { --doodle-stroke: #2a2a2a; }
        html.dark { --doodle-stroke: #f0f0f0; }
      `}</style>
    </div>
  );
}
