import { useRef, useState } from "react";

type PptResult = {
  ok: boolean;
  deck: string;
  folder: string;
  slides: string[];
  notes_file: string;
  renderer: string;
  message?: string;
  slide_urls: string[];
  notes_url: string;
};

export function ToolsPage() {
  const fileRef = useRef<HTMLInputElement>(null);
  const [busy, setBusy] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [result, setResult] = useState<PptResult | null>(null);

  const onUpload = async (f: File) => {
    setError(null);
    setResult(null);
    setBusy(true);
    try {
      const fd = new FormData();
      fd.append("file", f);
      const r = await fetch("/api/tools/ppt-to-images", { method: "POST", body: fd });
      if (!r.ok) {
        const text = await r.text();
        throw new Error(`HTTP ${r.status} — ${text}`);
      }
      const data = (await r.json()) as PptResult;
      setResult(data);
    } catch (e) {
      setError(e instanceof Error ? e.message : String(e));
    } finally {
      setBusy(false);
    }
  };

  return (
    <div className="min-h-screen bg-[#fdf7e6] dark:bg-[#15171b] text-ink dark:text-white font-hand p-6">
      <header className="flex items-center justify-between mb-6 max-w-5xl mx-auto">
        <div className="flex items-baseline gap-3">
          <a href="/" className="font-hand text-3xl underline decoration-wavy underline-offset-2">
            🎨 DoodleCode
          </a>
          <span className="text-2xl text-ink/60 dark:text-white/60">/ tools</span>
        </div>
        <a
          href="/"
          className="btn-sketch sky text-base"
          title="Back to the presentation canvas"
        >
          ← Back to deck
        </a>
      </header>

      <main className="max-w-5xl mx-auto">
        <section className="doodle-card mb-6">
          <h2 className="text-3xl mb-1">📑 PPT → Images</h2>
          <p className="text-lg text-ink/80 dark:text-white/80 mb-3">
            Upload a <code className="font-mono text-base bg-marker-yellow/40 px-1 rounded">.pptx</code> file.
            Each slide is rendered to a PNG and the speaker notes are extracted to a single
            <code className="font-mono text-base bg-marker-yellow/40 px-1 rounded ml-1">notes.txt</code>.
            Output goes to <code className="font-mono text-base">~/.doodlecode/tools/&lt;deck&gt;/</code>.
          </p>
          <div className="flex items-center gap-3 flex-wrap mt-2">
            <input
              ref={fileRef}
              type="file"
              accept=".pptx,.pptm,application/vnd.openxmlformats-officedocument.presentationml.presentation"
              className="hidden"
              onChange={(e) => {
                const f = e.target.files?.[0];
                if (f) onUpload(f);
                e.currentTarget.value = "";
              }}
            />
            <button
              className="btn-sketch mint text-xl"
              onClick={() => fileRef.current?.click()}
              disabled={busy}
            >
              {busy ? "Converting…" : "📂 Choose a .pptx"}
            </button>
            {result && (
              <a
                href={result.notes_url}
                target="_blank"
                rel="noopener noreferrer"
                className="btn-sketch sky text-base"
                title="Open the notes file"
              >
                📝 Open notes.txt
              </a>
            )}
          </div>
          {error && (
            <div className="mt-3 px-3 py-2 rounded-lg border-2 border-red-500 bg-red-50 dark:bg-red-900/40 text-red-700 dark:text-red-200 text-sm font-mono">
              {error}
            </div>
          )}
          {result?.message && (
            <div className="mt-3 px-3 py-2 rounded-lg border-2 border-amber-400 bg-amber-50 dark:bg-amber-900/30 text-ink dark:text-white text-sm">
              {result.message}
            </div>
          )}
        </section>

        {result && (
          <section>
            <h3 className="text-2xl mb-2">
              ✅ Done — <span className="font-mono text-lg">{result.deck}</span>{" "}
              <span className="text-base text-ink/70 dark:text-white/70">
                ({result.slides.length} slides · renderer: {result.renderer})
              </span>
            </h3>
            <p className="text-base text-ink/70 dark:text-white/70 font-mono mb-3 break-all">
              {result.folder}
            </p>
            <div className="grid grid-cols-2 md:grid-cols-3 gap-3">
              {result.slide_urls.map((url, i) => (
                <a
                  key={url}
                  href={url}
                  target="_blank"
                  rel="noopener noreferrer"
                  className="block rounded-xl border-2 border-ink dark:border-white/70 overflow-hidden bg-white"
                  title={result.slides[i]}
                >
                  <img
                    src={url}
                    alt={result.slides[i]}
                    className="w-full h-auto block"
                    loading="lazy"
                  />
                  <div className="px-2 py-1 text-sm font-mono bg-marker-yellow/40 text-ink">
                    {result.slides[i]}
                  </div>
                </a>
              ))}
            </div>
          </section>
        )}
      </main>
    </div>
  );
}
