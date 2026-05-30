import { useStore } from "../store";
import { progressFraction } from "../lib/present";

/**
 * Iter 163: a thin doodle progress bar pinned to the very top of the
 * screen during presentation. It fills to (currentSlide / total) so the
 * audience always knows how far through the deck they are. Pure
 * presentational — reads the focused slide + reading order from the
 * store. Sits above the canvas but below modals; pointer-events off so
 * it never blocks clicks.
 */
export function PresenterProgress() {
  const presenting = useStore((s) => s.presenting);
  const focusedCellId = useStore((s) => s.focusedCellId);
  const ordered = useStore((s) => s.cellsInOrder());

  if (!presenting || ordered.length === 0) return null;

  const idx = Math.max(0, ordered.findIndex((c) => c.id === focusedCellId));
  const total = ordered.length;
  const frac = progressFraction(idx, total);

  return (
    <div
      aria-hidden
      className="fixed top-0 left-0 right-0 z-[45] pointer-events-none"
    >
      {/* Track — faint, full width. */}
      <div className="h-[6px] w-full bg-ink/10 dark:bg-white/10">
        {/* Fill — marker-pink, grows with the deck. The slight rounded
         *  right cap + transition give it a hand-drawn, alive feel. */}
        <div
          className="h-full bg-marker-pink dark:bg-[#e64980] rounded-r-full transition-[width] duration-300 ease-out"
          style={{ width: `${(frac * 100).toFixed(2)}%` }}
        />
      </div>
      {/* Per-slide notches so the deck length is legible at a glance. */}
      <div className="absolute inset-x-0 top-0 h-[6px] flex">
        {ordered.map((c, i) => (
          <div
            key={c.id}
            className="flex-1 border-r border-ink/15 dark:border-white/15 last:border-r-0"
            style={{ opacity: i <= idx ? 0 : 1 }}
          />
        ))}
      </div>
    </div>
  );
}
