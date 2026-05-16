import { useEffect, useRef, useState } from "react";
import { useStore } from "../store";

type Design = "doodle" | "professional" | "serif" | "mono";

const OPTIONS: { id: Design; label: string; sample: string; fontFamily: string }[] = [
  {
    id: "doodle",
    label: "Doodle (original)",
    sample: "Aa — the golden one",
    fontFamily: "'Caveat', 'Patrick Hand', cursive",
  },
  {
    id: "professional",
    label: "Professional",
    sample: "Aa — clean sans-serif",
    fontFamily: "'Inter', system-ui, sans-serif",
  },
  {
    id: "serif",
    label: "Serif",
    sample: "Aa — editorial",
    fontFamily: "'Lora', Georgia, serif",
  },
  {
    id: "mono",
    label: "Mono",
    sample: "Aa — terminal feel",
    fontFamily: "'JetBrains Mono', ui-monospace, monospace",
  },
];

export function DesignPicker() {
  const design = useStore((s) => s.design);
  const setDesign = useStore((s) => s.setDesign);
  const fontScale = useStore((s) => s.fontScale);
  const setFontScale = useStore((s) => s.setFontScale);
  const [open, setOpen] = useState(false);
  const ref = useRef<HTMLDivElement>(null);

  useEffect(() => {
    if (!open) return;
    const onDown = (e: MouseEvent) => {
      if (!ref.current?.contains(e.target as Node)) setOpen(false);
    };
    const onKey = (e: KeyboardEvent) => {
      if (e.key === "Escape") setOpen(false);
    };
    window.addEventListener("mousedown", onDown);
    window.addEventListener("keydown", onKey);
    return () => {
      window.removeEventListener("mousedown", onDown);
      window.removeEventListener("keydown", onKey);
    };
  }, [open]);

  return (
    <div ref={ref} className="relative flex gap-1 items-center">
      <button
        className="btn-sketch peach"
        onClick={() => setOpen((v) => !v)}
        title="Pick a font theme"
      >
        🎨 Design
      </button>
      <div
        className="flex items-center gap-0.5 border-2 border-ink/40 dark:border-white/40 rounded-xl px-1 py-0.5 bg-white/40 dark:bg-black/30"
        title={`Font size ${Math.round(fontScale * 100)}%`}
      >
        <button
          className="w-7 h-7 rounded-md font-hand text-lg text-ink dark:text-white hover:bg-marker-yellow dark:hover:bg-amber-700 disabled:opacity-40"
          onClick={() => setFontScale(fontScale - 0.1)}
          disabled={fontScale <= 0.8}
          title="Smaller font (A−)"
        >
          A−
        </button>
        <span className="font-mono text-xs px-1 text-ink/70 dark:text-white/70 select-none w-8 text-center">
          {Math.round(fontScale * 100)}%
        </span>
        <button
          className="w-7 h-7 rounded-md font-hand text-xl text-ink dark:text-white hover:bg-marker-yellow dark:hover:bg-amber-700 disabled:opacity-40"
          onClick={() => setFontScale(fontScale + 0.1)}
          disabled={fontScale >= 1.6}
          title="Larger font (A+)"
        >
          A+
        </button>
      </div>
      {open && (
        <div
          className="absolute top-12 left-0 z-50 w-72 bg-white dark:bg-[#1f2228] text-ink dark:text-white border-2 border-ink dark:border-white rounded-2xl shadow-sketch p-2"
        >
          <div className="font-hand text-lg px-2 py-1 text-ink/70 dark:text-white/70">
            Font theme
          </div>
          {OPTIONS.map((opt) => (
            <button
              key={opt.id}
              onClick={() => {
                setDesign(opt.id);
                setOpen(false);
              }}
              className={`w-full text-left px-2 py-2 rounded-lg border-2 mt-1 transition ${
                design === opt.id
                  ? "border-ink dark:border-white bg-marker-yellow dark:bg-amber-700/60"
                  : "border-transparent hover:border-ink/30 dark:hover:border-white/30"
              }`}
            >
              <div
                className="text-xl leading-tight text-ink dark:text-white"
                style={{ fontFamily: opt.fontFamily }}
              >
                {opt.sample}
              </div>
              <div className="text-sm font-mono text-ink/60 dark:text-white/70 mt-0.5">
                {opt.label}
                {opt.id === "doodle" && (
                  <span className="ml-2 px-1.5 py-0.5 rounded bg-marker-yellow text-ink text-[10px]">
                    GOLDEN
                  </span>
                )}
              </div>
            </button>
          ))}
        </div>
      )}
    </div>
  );
}
