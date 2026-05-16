import { useEffect, useState } from "react";
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

  useEffect(() => {
    const onKey = (e: KeyboardEvent) => {
      if (e.key === "Escape") onClose();
    };
    window.addEventListener("keydown", onKey);
    return () => window.removeEventListener("keydown", onKey);
  }, [onClose]);

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
      className="fixed inset-0 flex items-center justify-center bg-black/60"
      style={{ zIndex: 200 }}
      onClick={onClose}
    >
      <div
        className="relative w-[560px] max-w-[92vw] bg-white dark:bg-[#1f2228] border-2 border-ink dark:border-white rounded-3xl shadow-sketch p-5 font-hand text-ink dark:text-white"
        onClick={(e) => e.stopPropagation()}
        onMouseDown={(e) => e.stopPropagation()}
      >
        <button
          onClick={onClose}
          className="absolute top-3 right-3 w-9 h-9 rounded-full border-2 border-ink dark:border-white bg-white dark:bg-[#0f1115] text-ink dark:text-white text-xl hover:bg-red-100 dark:hover:bg-red-900 transition"
          title="Close (Esc)"
          style={{ cursor: "pointer" }}
        >
          ✕
        </button>

        <div className="text-3xl mb-1 text-ink dark:text-white">📦 Install package</div>
        <div className="text-base text-ink/80 dark:text-white/85 mb-3">
          Runs <span className="font-mono">pip install</span> in the kernel's
          virtualenv. Newly installed packages are importable on the next{" "}
          <span className="font-mono">import</span> — no kernel restart, no page
          refresh.
        </div>

        <label className="block text-lg text-ink dark:text-white">
          Packages (space-separated)
        </label>
        <input
          className="w-full border-2 border-ink/70 dark:border-white/50 rounded px-2 py-1 text-base font-mono bg-white dark:bg-[#0f1115] text-ink dark:text-white"
          value={pkg}
          onChange={(e) => setPkg(e.target.value)}
          onKeyDown={(e) => e.key === "Enter" && !busy && run()}
          placeholder="matplotlib  seaborn  pandas"
          disabled={busy}
          autoFocus
        />
        <div className="text-base text-ink/70 dark:text-white/70 mt-1">
          Tip: heavy installs like <span className="font-mono">torch</span> take
          1–2 minutes. You can close this dialog any time — the install keeps
          going in the background.
        </div>

        <pre
          className={`mt-3 rounded-lg border-2 ${
            ok === false ? "border-red-500" : "border-ink/40 dark:border-white/40"
          } bg-stone-50 dark:bg-[#0f1115] text-ink dark:text-stone-100 p-2 text-xs font-mono whitespace-pre-wrap`}
          style={{ maxHeight: 220, overflow: "auto" }}
        >
          {log || (busy ? "installing…" : "(no output yet)")}
        </pre>

        {ok === true && (
          <div className="mt-2 px-3 py-2 rounded-lg bg-[#b2f2bb] dark:bg-[#2b8a3e] text-ink dark:text-white font-hand text-lg">
            ✅ Installed. Close this dialog and re-run your cell — no refresh
            needed.
          </div>
        )}
        {ok === false && (
          <div className="mt-2 px-3 py-2 rounded-lg bg-[#ffc9c9] dark:bg-[#a3201f] text-ink dark:text-white font-hand text-lg">
            ❌ Install failed. Check the log above, edit the package name, and
            click ▶ Install again.
          </div>
        )}

        <div className="flex justify-between mt-3">
          <button
            className="btn-sketch pink"
            style={{ cursor: "pointer" }}
            onClick={onClose}
          >
            {busy ? "Hide (install continues)" : "Close"}
          </button>
          <button
            className="btn-sketch mint"
            style={{ cursor: pkg.trim() && !busy ? "pointer" : "not-allowed" }}
            onClick={run}
            disabled={busy || !pkg.trim()}
          >
            {busy ? "Installing…" : ok === false ? "▶ Retry" : "▶ Install"}
          </button>
        </div>
      </div>
    </div>
  );
}
