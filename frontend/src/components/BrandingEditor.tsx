import { useEffect, useState } from "react";
import { useStore } from "../store";

export function BrandingEditor() {
  const branding = useStore((s) => s.branding);
  const setBranding = useStore((s) => s.setBranding);
  const close = useStore((s) => s.setBrandingOpen);
  const [logo, setLogo] = useState(branding.logo);
  const [byline, setByline] = useState(branding.byline);

  useEffect(() => {
    const onKey = (e: KeyboardEvent) => {
      if (e.key === "Escape") close(false);
    };
    window.addEventListener("keydown", onKey);
    return () => window.removeEventListener("keydown", onKey);
  }, [close]);

  const onSave = () => {
    setBranding({ logo: logo.trim(), byline: byline.trim() });
    close(false);
  };

  const onReset = () => {
    setLogo("🎨");
    setByline("Co-AI Developed by Kader Mohideen");
  };

  return (
    <div
      className="fixed inset-0 z-50 flex items-center justify-center bg-black/60"
      onClick={() => close(false)}
    >
      <div
        className="relative w-[460px] max-w-[92vw] bg-white dark:bg-[#1f2228] border-2 border-ink dark:border-white rounded-3xl shadow-sketch p-6 font-hand text-ink dark:text-white"
        onClick={(e) => e.stopPropagation()}
      >
        <button
          className="absolute top-3 right-3 w-9 h-9 rounded-full border-2 border-ink dark:border-white bg-white dark:bg-[#0f1115] text-ink dark:text-white text-xl"
          onClick={() => close(false)}
        >
          ✕
        </button>

        <div className="text-3xl mb-1 text-ink dark:text-white">✏️ Edit Logo</div>
        <div className="text-base text-ink/80 dark:text-white/85 mb-4">
          Personalize the toolbar logo and the author byline. Stored on this
          browser only.
        </div>

        {/* Live preview */}
        <div className="px-3 py-2 mb-4 rounded-xl border-2 border-dashed border-ink/40 dark:border-white/40 bg-white/60 dark:bg-black/30">
          <div className="font-hand text-2xl text-ink dark:text-white leading-tight">
            {logo || "🎨"} DoodleCode{" "}
            <span className="text-[#c2255c] dark:text-[#fcc2d7]">Studio</span>
          </div>
          <div className="font-hand text-base text-ink/70 dark:text-white/70 mt-1">
            <span className="text-[#c2255c] dark:text-[#fcc2d7] underline decoration-wavy underline-offset-2">
              {byline || "Co-AI Developed by Kader Mohideen"}
            </span>
          </div>
        </div>

        <label className="block mb-3">
          <div className="text-lg text-ink dark:text-white mb-1">Logo</div>
          <input
            className="w-full px-3 py-2 rounded-lg border-2 border-ink dark:border-white bg-white dark:bg-[#0f1115] text-ink dark:text-white text-xl"
            value={logo}
            onChange={(e) => setLogo(e.target.value)}
            placeholder="🎨"
            maxLength={64}
          />
          <div className="text-xs font-mono text-ink/60 dark:text-white/60 mt-1">
            Any emoji or short text. Tip: ⚡ 🚀 📚 🧪 🦊 🌈
          </div>
        </label>

        {/* Section information — full byline */}
        <div className="mt-2 pt-3 border-t-2 border-dashed border-ink/30 dark:border-white/30">
          <div className="text-sm font-mono text-ink/60 dark:text-white/60 uppercase tracking-wider mb-2">
            Section information
          </div>
          <label className="block">
            <div className="text-lg text-ink dark:text-white mb-1">Byline</div>
            <input
              className="w-full px-3 py-2 rounded-lg border-2 border-ink dark:border-white bg-white dark:bg-[#0f1115] text-ink dark:text-white text-xl"
              value={byline}
              onChange={(e) => setByline(e.target.value)}
              placeholder="Co-AI Developed by Kader Mohideen"
              maxLength={160}
            />
            <div className="text-xs font-mono text-ink/60 dark:text-white/60 mt-1">
              The whole line under the logo. Write whatever you want —
              "Built by …", "Made with ❤ by …", a tagline, anything.
            </div>
          </label>
        </div>

        <div className="mt-5 flex items-center gap-2 justify-end">
          <button
            className="btn-sketch"
            onClick={onReset}
            title="Restore the original logo + name"
          >
            ↺ Reset
          </button>
          <button className="btn-sketch mint" onClick={onSave}>
            💾 Save
          </button>
        </div>
      </div>
    </div>
  );
}
