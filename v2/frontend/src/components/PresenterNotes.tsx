import { useStore } from "../store";

/**
 * Iter 165: presenter-only speaker-note HUD. Pinned bottom-left during
 * presentation, it shows the focused cell's `note` so the speaker has
 * their script without it appearing on the slide. Hidden when the cell
 * has no note. `pointer-events:none` so it never blocks the canvas or
 * the PresenterBar (which sits bottom-center).
 */
export function PresenterNotes() {
  const presenting = useStore((s) => s.presenting);
  const focusedCellId = useStore((s) => s.focusedCellId);
  const note = useStore((s) =>
    s.cells.find((c) => c.id === s.focusedCellId)?.note,
  );

  if (!presenting || !focusedCellId || !note) return null;

  return (
    <div className="fixed bottom-4 left-4 z-40 max-w-sm pointer-events-none">
      <div className="rounded-2xl border-2 border-ink/70 dark:border-white/50 bg-white/92 dark:bg-[#1f2228]/95 shadow-sketch px-4 py-3">
        <div className="font-hand text-sm text-ink/60 dark:text-white/60 mb-1 flex items-center gap-1">
          📝 Speaker note
        </div>
        <p className="font-hand text-lg leading-snug text-ink dark:text-white whitespace-pre-wrap break-words">
          {note}
        </p>
      </div>
    </div>
  );
}
