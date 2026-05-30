/**
 * Iter 162: presentation vertical framing.
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
