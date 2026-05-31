/**
 * Iter 174: live data-driven doodle charts.
 *
 * A Doodle diagram source may contain `live: <codeCellId>` directive
 * lines. Each is replaced with the *current stdout* of that code cell
 * before the chart compiles — so a code cell can `print(doodle.bar(…))`
 * and a linked diagram renders it with no paste step.
 *
 * Pure + dependency-free so it unit-tests without the store. A raw,
 * unresolved `live:` line is harmless: the chart parser reads it as a
 * `Label: number` bar with `Number("<id>") === NaN`, which it drops.
 */
import type { CellRuntime } from "../types";

const LIVE_RE = /^\s*live:\s*(\S+)\s*$/i;

/** Concatenated stdout text of a code cell's last run (no stderr). */
export function stdoutOf(rt: CellRuntime | undefined): string {
  if (!rt?.result) return "";
  return rt.result.outputs
    .filter((o) => o.type === "stdout")
    .map((o) => o.text)
    .join("");
}

/** True if the source references at least one live code cell. */
export function hasLiveDirective(source: string): boolean {
  return source.split("\n").some((l) => LIVE_RE.test(l));
}

/** The cell ids referenced by `live:` directives, in order. */
export function liveSourceIds(source: string): string[] {
  const ids: string[] = [];
  for (const line of source.split("\n")) {
    const m = line.match(LIVE_RE);
    if (m) ids.push(m[1]);
  }
  return ids;
}

/**
 * Replace every `live: <id>` line with that cell's stdout. Other lines
 * pass through untouched, so static chart syntax can sit alongside live
 * blocks in the same diagram.
 */
export function resolveLiveDoodleSource(
  source: string,
  getStdout: (cellId: string) => string,
): string {
  return source
    .split("\n")
    .map((line) => {
      const m = line.match(LIVE_RE);
      if (!m) return line;
      return getStdout(m[1]) ?? "";
    })
    .join("\n");
}
