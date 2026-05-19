import { useEffect, useRef, useState } from "react";
import { useStore } from "../store";
import { THEME_OPTIONS, shapesFor, type AmbientTheme } from "./presenterShapes";

/** Toolbar dropdown for the presenter ambient theme. */
export function AmbientPicker() {
  const theme = useStore((s) => s.presenterAmbient);
  const setTheme = useStore((s) => s.setPresenterAmbient);
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

  const current = THEME_OPTIONS.find((t) => t.id === theme) ?? THEME_OPTIONS[0];

  return (
    <div ref={ref} className="relative">
      <button
        className="btn-sketch violet"
        onClick={() => setOpen((v) => !v)}
        title="Pick the ambient theme that floats behind cards in presentation"
      >
        ✨ Vibe
      </button>
      {open && (
        <div className="absolute top-12 right-0 z-50 w-80 bg-white dark:bg-[#1f2228] text-ink dark:text-white border-2 border-ink dark:border-white rounded-2xl shadow-sketch p-2">
          <div className="font-hand text-lg px-2 py-1 text-ink/70 dark:text-white/70 flex items-baseline justify-between">
            <span>Presenter vibe</span>
            <span className="text-xs">current: <b>{current.label}</b></span>
          </div>
          {THEME_OPTIONS.map((opt) => {
            const sample = shapesFor(opt.id).slice(0, 4);
            const selected = theme === opt.id;
            return (
              <button
                key={opt.id}
                onClick={() => { setTheme(opt.id as AmbientTheme); setOpen(false); }}
                className={`w-full text-left px-2 py-2 rounded-lg border-2 mt-1 transition ${
                  selected
                    ? "border-ink dark:border-white bg-marker-yellow dark:bg-amber-700/60"
                    : "border-transparent hover:border-ink/30 dark:hover:border-white/30"
                }`}
              >
                <div className="flex items-center justify-between gap-2">
                  <div className="font-hand text-lg">{opt.label}</div>
                  <div className="flex gap-1">
                    {sample.map((s, i) => (
                      <svg key={i} width={20} height={20} viewBox="0 0 60 60">
                        <path
                          d={s.d}
                          fill="none"
                          stroke="#c2255c"
                          strokeWidth={s.weight ?? 2.2}
                          strokeLinecap="round"
                          strokeLinejoin="round"
                        />
                        {s.d2 && (
                          <path
                            d={s.d2}
                            fill="none"
                            stroke="#c2255c"
                            strokeWidth={(s.weight ?? 2.2) * 0.85}
                            strokeLinecap="round"
                            strokeLinejoin="round"
                          />
                        )}
                      </svg>
                    ))}
                  </div>
                </div>
                <div className="text-xs font-mono text-ink/60 dark:text-white/60 mt-0.5">
                  {opt.subtitle}
                </div>
              </button>
            );
          })}
        </div>
      )}
    </div>
  );
}
