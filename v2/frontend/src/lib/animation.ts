/**
 * Animation-cell helpers (iter 224+).
 *
 * An animation cell's `source` is a frame script: one frame per line.
 * During presentation each Space/→ advances the revealed step; the cell
 * shows `frameAt(frames, step)` with a transition. Pure + dependency-free
 * so it unit-tests without React.
 */

export const TRANSITIONS = ["fade", "slide", "draw-on", "pop"] as const;
export type TransitionKind = (typeof TRANSITIONS)[number];

export const DEFAULT_TRANSITION: TransitionKind = "fade";

/** Split a frame script into frames — one non-blank line each, trimmed. */
export function parseFrames(source: string): string[] {
  return source
    .split("\n")
    .map((l) => l.trim())
    .filter((l) => l.length > 0);
}

/** How many frames the script defines. */
export function frameCount(source: string): number {
  return parseFrames(source).length;
}

/** The frame shown at `step`, clamped into range. Empty string when there
 *  are no frames (so the cell renders a placeholder, never crashes). */
export function frameAt(frames: string[], step: number): string {
  if (frames.length === 0) return "";
  const i = Math.max(0, Math.min(step, frames.length - 1));
  return frames[i];
}

/** Normalize a possibly-unknown transition value to a valid one. */
export function normalizeTransition(t: string | undefined): TransitionKind {
  return (TRANSITIONS as readonly string[]).includes(t ?? "")
    ? (t as TransitionKind)
    : DEFAULT_TRANSITION;
}
