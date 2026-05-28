/**
 * Pure helpers for derived presentation strings shown on cells.
 * Extracted from CellPalette + BrowserCell in iter 73 so they can
 * be exercised directly by vitest without rendering anything.
 */

/**
 * Pull a short, readable first-line out of a cell body so the user
 * recognizes untitled cells in the Cmd+K palette. Strips leading
 * markdown markers (`#`, `-`, `*`) and Python comment `#` so a
 * heading or a comment previews cleanly. Truncates at 60 chars.
 */
export function firstLine(source: string, kind: string): string {
  for (const raw of source.split("\n")) {
    const t = raw.trim();
    if (!t) continue;
    let s = t;
    if (kind === "markdown") {
      s = s.replace(/^#+\s*/, "").replace(/^[-*]\s+/, "");
    } else if (kind === "code") {
      s = s.replace(/^#\s*/, "");
    }
    return s.length > 60 ? s.slice(0, 57) + "…" : s;
  }
  return "";
}

/**
 * Extract the hostname for the collapsed-browser host chip. Strips
 * the leading `www.` so the chip is shorter. Falls back to the raw
 * string when URL parsing fails (still works for "example.com").
 */
export function hostOf(source: string): string {
  try {
    const u = new URL(source);
    return u.host.replace(/^www\./, "");
  } catch {
    const stripped = source.replace(/^https?:\/\//, "").split("/")[0];
    return stripped || "(blank)";
  }
}
