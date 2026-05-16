import { useState } from "react";
import { installPackages } from "../api";
import { useStore } from "../store";

export function InstallModal({
  initial,
  onClose,
}: {
  initial?: string;
  onClose: () => void;
}) {
  const [pkg, setPkg] = useState(initial ?? "");
  const [busy, setBusy] = useState(false);
  const [log, setLog] = useState<string>("");
  const [ok, setOk] = useState<boolean | null>(null);
  const setInstalling = useStore((s) => s.setInstalling);

  const run = async () => {
    if (!pkg.trim() || busy) return;
    setBusy(true);
    setOk(null);
    setLog(`$ pip install ${pkg}\n`);
    setInstalling({ packages: pkg, log: "" });
    try {
      const r = await installPackages(pkg, false);
      const combined = `${r.stdout}\n${r.stderr}`.trim() || "(no output)";
      setLog((l) => `${l}\n${combined}\n\n${r.ok ? "✅ done." : `❌ exit ${r.returncode}`}`);
      setOk(r.ok);
    } catch (e: any) {
      setLog((l) => `${l}\n${String(e)}`);
      setOk(false);
    } finally {
      setBusy(false);
      setInstalling(null);
    }
  };

  return (
    <div
      className="fixed inset-0 z-50 flex items-center justify-center bg-black/50"
      onClick={() => !busy && onClose()}
    >
      <div
        className="relative w-[560px] max-w-[92vw] bg-white dark:bg-[#1f2228] border-2 border-ink dark:border-white/70 rounded-3xl shadow-sketch p-5 font-hand"
        onClick={(e) => e.stopPropagation()}
      >
        <div className="text-3xl mb-1">📦 Install package</div>
        <div className="text-base text-ink/70 dark:text-white/70 mb-3">
          Runs <span className="font-mono">pip install</span> in the kernel's
          virtualenv. Newly installed packages are importable on the next{" "}
          <span className="font-mono">import</span> — no kernel restart needed.
        </div>

        <label className="block text-lg">Packages (space-separated)</label>
        <input
          className="w-full border-2 border-ink/70 dark:border-white/40 rounded px-2 py-1 text-base font-mono bg-white dark:bg-[#0f1115]"
          value={pkg}
          onChange={(e) => setPkg(e.target.value)}
          onKeyDown={(e) => e.key === "Enter" && run()}
          placeholder="torch  pandas  matplotlib==3.9.*"
          disabled={busy}
          autoFocus
        />
        <div className="text-base text-ink/60 dark:text-white/60 mt-1">
          Tip: pinning works (<span className="font-mono">numpy==1.26.4</span>).
          Heavy installs like <span className="font-mono">torch</span> take 1–2 minutes.
        </div>

        <pre
          className={`mt-3 nowheel max-h-64 overflow-auto rounded-lg border-2 ${
            ok === false ? "border-red-500" : "border-ink/40 dark:border-white/40"
          } bg-stone-50 dark:bg-[#0f1115] p-2 text-xs font-mono whitespace-pre-wrap`}
        >
          {log || (busy ? "installing…" : "(no output yet)")}
        </pre>

        <div className="flex justify-between mt-3">
          <button className="btn-sketch pink" onClick={onClose} disabled={busy}>
            Close
          </button>
          <button className="btn-sketch mint" onClick={run} disabled={busy || !pkg.trim()}>
            {busy ? "Installing…" : "▶ Install"}
          </button>
        </div>
      </div>
    </div>
  );
}
