/**
 * Single source of truth for a cell's ON-SCREEN size (iter 239).
 *
 * Code / markdown / animation cells render at a FIXED card width and
 * ignore `cell.w` (they auto-grow in height only). The resizable kinds
 * (diagram / media / browser / whiteboard) honor `cell.w` / `cell.h`.
 *
 * Callout placement (Canvas) and the connector lines (ConnectionsLayer)
 * must use the *real* rendered width, not `cell.w`, or the bubble + its
 * line float away from the card (the "gap in the connector" bug — a
 * 720-wide stored width on a 560-wide card left a ~160px gap).
 */
type SizedCell = { kind: string; w?: number; h?: number };

/** Fixed card widths — must match the `CARD_WIDTH` constants in the
 *  respective cell components. These cells ignore `cell.w`. */
const FIXED_W: Record<string, number> = {
  code: 580,
  markdown: 560,
  animation: 560,
};

/** Default widths for the resizable kinds when `cell.w` is unset. */
const RESIZE_DEFAULT_W: Record<string, number> = {
  diagram: 560,
  media: 480,
  browser: 720,
  whiteboard: 640,
};

/** Best-effort heights when a cell hasn't stored an explicit `h`. The
 *  auto-grow kinds (code/markdown/animation) only get an estimate. */
const EST_H: Record<string, number> = {
  code: 300,
  markdown: 200,
  animation: 240,
  diagram: 360,
  media: 320,
  browser: 480,
  whiteboard: 420,
};

const RESIZABLE = new Set(["diagram", "media", "browser", "whiteboard"]);

export function cellDisplayWidth(cell: SizedCell): number {
  const fixed = FIXED_W[cell.kind];
  if (fixed != null) return fixed; // fixed-width cards ignore cell.w
  return cell.w ?? RESIZE_DEFAULT_W[cell.kind] ?? 560;
}

export function cellDisplayHeight(cell: SizedCell): number {
  if (RESIZABLE.has(cell.kind)) return cell.h ?? EST_H[cell.kind] ?? 320;
  // Auto-grow kinds: prefer a stored h if present, else estimate.
  return cell.h ?? EST_H[cell.kind] ?? 300;
}
