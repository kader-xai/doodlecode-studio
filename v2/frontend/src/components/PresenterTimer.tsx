import { useEffect, useRef, useState } from "react";
import { useStore } from "../store";
import { formatDuration } from "../lib/present";

/**
 * Iter 235: an elapsed-time clock pinned to the top-right corner during
 * presentation. Starts at 00:00 when a talk begins and ticks every
 * second; click it to reset to zero (handy if you start over). Resets
 * automatically when presentation exits, so the next talk starts fresh.
 *
 * Sits at z-30 (presenter-UI tier, below modals at 50+); only the chip
 * itself is clickable so it never blocks the canvas or ink.
 */
export function PresenterTimer() {
  const presenting = useStore((s) => s.presenting);
  const [elapsed, setElapsed] = useState(0);
  const startRef = useRef<number>(0);

  useEffect(() => {
    if (!presenting) {
      startRef.current = 0;
      setElapsed(0);
      return;
    }
    startRef.current = Date.now();
    setElapsed(0);
    const id = setInterval(() => {
      setElapsed(Date.now() - startRef.current);
    }, 500);
    return () => clearInterval(id);
  }, [presenting]);

  if (!presenting) return null;

  return (
    <div className="fixed top-3 right-3 z-30 pointer-events-none flex">
      <button
        type="button"
        onClick={() => {
          startRef.current = Date.now();
          setElapsed(0);
        }}
        className="pointer-events-auto font-mono text-lg tabular-nums px-3 py-1 rounded-xl border-2 border-ink/70 dark:border-white/60 bg-white/85 dark:bg-[#1f2228]/90 text-ink dark:text-white shadow-sketch backdrop-blur-sm hover:bg-marker-yellow/60 dark:hover:bg-amber-700/40 transition"
        title="Talk timer — click to reset"
        aria-label={`Presentation time ${formatDuration(elapsed)}`}
      >
        ⏱ {formatDuration(elapsed)}
      </button>
    </div>
  );
}
