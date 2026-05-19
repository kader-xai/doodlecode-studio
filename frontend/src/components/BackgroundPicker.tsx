import { useEffect, useRef, useState } from "react";
import { useStore } from "../store";

type Bg = "sandal" | "gray" | "white" | "black";

const OPTIONS: { id: Bg; label: string; swatch: string; preview: string; dark: boolean }[] = [
  { id: "sandal", label: "Sandal", swatch: "#fdf7e6", preview: "warm paper feel — default", dark: false },
  { id: "gray",   label: "Gray",   swatch: "#e9ecef", preview: "neutral, low-glare",        dark: false },
  { id: "white",  label: "White",  swatch: "#ffffff", preview: "clean, projector-ready",     dark: false },
  { id: "black",  label: "Black",  swatch: "#0f1115", preview: "dark mode — high contrast", dark: true  },
];

export function BackgroundPicker() {
  const pageBg = useStore((s) => s.pageBg);
  const setPageBg = useStore((s) => s.setPageBg);
  const [open, setOpen] = useState(false);
  const ref = useRef<HTMLDivElement>(null);

  useEffect(() => {
    if (!open) return;
    const onDown = (e: MouseEvent) => {
      if (!ref.current?.contains(e.target as Node)) setOpen(false);
    };
    const onKey = (e: KeyboardEvent) => { if (e.key === "Escape") setOpen(false); };
    window.addEventListener("mousedown", onDown);
    window.addEventListener("keydown", onKey);
    return () => {
      window.removeEventListener("mousedown", onDown);
      window.removeEventListener("keydown", onKey);
    };
  }, [open]);

  const current = OPTIONS.find((o) => o.id === pageBg) ?? OPTIONS[0];

  return (
    <div ref={ref} className="relative">
      <button
        className="btn-sketch violet flex items-center gap-2"
        onClick={() => setOpen((v) => !v)}
        title="Pick the page background color"
      >
        <span
          className="inline-block w-4 h-4 rounded-full border-2 border-current"
          style={{ background: current.swatch }}
        />
        <span>BG</span>
      </button>
      {open && (
        <div className="absolute top-12 right-0 z-50 w-64 bg-white dark:bg-[#1f2228] text-ink dark:text-white border-2 border-ink dark:border-white rounded-2xl shadow-sketch p-2">
          <div className="font-hand text-lg px-2 py-1 text-ink/70 dark:text-white/70">
            Page background
          </div>
          {OPTIONS.map((opt) => {
            const selected = pageBg === opt.id;
            return (
              <button
                key={opt.id}
                onClick={() => { setPageBg(opt.id); setOpen(false); }}
                className={`w-full text-left px-2 py-2 rounded-lg border-2 mt-1 flex items-center gap-3 transition ${
                  selected
                    ? "border-ink dark:border-white bg-marker-yellow dark:bg-amber-700/60"
                    : "border-transparent hover:border-ink/30 dark:hover:border-white/30"
                }`}
              >
                <span
                  className="inline-block w-8 h-8 rounded-lg border-2 border-ink dark:border-white/70 shrink-0"
                  style={{ background: opt.swatch }}
                />
                <span className="flex-1">
                  <span className="font-hand text-lg block leading-tight">{opt.label}</span>
                  <span className="text-xs font-mono text-ink/60 dark:text-white/60 block">
                    {opt.preview}
                  </span>
                </span>
                {opt.dark && (
                  <span className="text-[10px] font-mono px-1.5 py-0.5 rounded bg-marker-yellow text-ink">
                    DARK
                  </span>
                )}
              </button>
            );
          })}
        </div>
      )}
    </div>
  );
}
