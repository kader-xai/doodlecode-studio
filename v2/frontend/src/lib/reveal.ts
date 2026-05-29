import type { Cell } from "../types";

/**
 * Iter 154: derive the code a cell should display / run given how many
 * reveal steps have been revealed so far.
 *
 * `source` is the pristine base (step 0). Each revealed step is
 * appended below, separated by a blank line, so the program builds up
 * function-by-function. `step` is clamped to the available reveals so
 * a stale count never throws.
 *
 * Reveals are code-only — for any non-code kind, or when there are no
 * reveals, this returns the source unchanged.
 */
export function effectiveSource(cell: Cell, step: number): string {
  if (cell.kind !== "code") return cell.source;
  const reveals = cell.reveals ?? [];
  if (reveals.length === 0 || step <= 0) return cell.source;
  const n = Math.min(step, reveals.length);
  const shown = reveals.slice(0, n);
  // Trim trailing whitespace on the base so the join is predictable,
  // then separate each fragment with one blank line.
  return [cell.source.replace(/\s+$/, ""), ...shown].join("\n\n");
}

/** How many reveal steps a cell has (0 if none / not a code cell). */
export function revealCount(cell: Cell): number {
  if (cell.kind !== "code") return 0;
  return cell.reveals?.length ?? 0;
}
