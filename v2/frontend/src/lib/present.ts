/**
 * Iter 206: the focused slide is centered DEAD-CENTER in the viewport on
 * both axes (owner request — every slide sits in the middle of the
 * screen). Horizontally we center on the bounding box of the cell PLUS
 * any callout column to its right (`calloutExtra` = `CALLOUT_GAP +
 * BUBBLE_W` when callouts exist, else 0) so a cell+bubble pair reads
 * balanced; vertically on the cell midpoint. `setCenter(cx, cy)` then
 * puts that point at the viewport center. Pure + zoom-independent.
 */
export function slideCenter(
  x: number,
  y: number,
  w: number,
  h: number,
  calloutExtra = 0,
): { cx: number; cy: number } {
  return { cx: x + (w + calloutExtra) / 2, cy: y + h / 2 };
}

/**
 * Iter 162: presentation vertical framing.
 *
 * @deprecated since iter 206 — slides now center dead-center via
 * `slideCenter`. Kept for the existing test + back-reference.
 *
 * ReactFlow's `setCenter(x, y)` places the world point (x, y) at the
 * viewport's vertical CENTER (50%). The old code passed the cell's
 * midpoint (`cell.y + h/2`), so every slide sat mid-screen and tall
 * cells ran off the bottom — the "stuck below the center" complaint.
 *
 * Instead we want the cell's TOP to land `topFraction` of the way down
 * (≈33%), so each slide reads top-to-bottom from the upper third.
 *
 * Derivation: a world y' maps to screen `0.5*H + (y' - cy)*zoom`.
 * Setting y' = cellTopY and solving for the centered point cy so the
 * cell top lands at `topFraction*H` gives:
 *     cy = cellTopY + (0.5 - topFraction) * (H / zoom)
 */
export function slideCenterY(
  cellTopY: number,
  viewportH: number,
  zoom: number,
  topFraction = 0.33,
): number {
  return cellTopY + (0.5 - topFraction) * (viewportH / zoom);
}

/**
 * Inverse helper for tests/sanity: given the centered point `cy`, where
 * (as a 0..1 fraction of viewport height) does a world `cellTopY` land?
 */
export function topFractionOf(
  cellTopY: number,
  cy: number,
  viewportH: number,
  zoom: number,
): number {
  const screenTop = viewportH / 2 + (cellTopY - cy) * zoom;
  return screenTop / viewportH;
}

/**
 * Iter 163: deck progress as a 0..1 fraction for the presentation
 * progress bar. `index` is the 0-based focused slide; the bar fills to
 * (index + 1) / total so the last slide reads as 100%. Empty / unknown
 * decks return 0. The result is always clamped to [0, 1].
 */
export function progressFraction(index: number, total: number): number {
  if (total <= 0) return 0;
  const i = Math.max(0, Math.min(index, total - 1));
  return (i + 1) / total;
}

/**
 * Iter 235: format an elapsed presentation time (in ms) for the corner
 * timer. `MM:SS`, or `H:MM:SS` once past an hour. Negative / NaN clamps
 * to `00:00`. Pure so it unit-tests without a clock.
 */
export function formatDuration(ms: number): string {
  const totalSec = Number.isFinite(ms) ? Math.max(0, Math.floor(ms / 1000)) : 0;
  const h = Math.floor(totalSec / 3600);
  const m = Math.floor((totalSec % 3600) / 60);
  const s = totalSec % 60;
  const mm = String(m).padStart(2, "0");
  const ss = String(s).padStart(2, "0");
  return h > 0 ? `${h}:${mm}:${ss}` : `${mm}:${ss}`;
}
