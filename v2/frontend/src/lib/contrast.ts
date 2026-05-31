/**
 * Iter 179: WCAG 2.1 contrast utilities.
 *
 * The doodle palette pairs very dark "ink" text (#2a2a2a) with light
 * pastel fills, and charts draw labels in a near-black/near-white
 * `stroke` on the card background — so contrast is structurally high.
 * These helpers exist to *prove* and *lock in* that contract: the
 * accompanying test asserts every text/background pair clears WCAG AA,
 * so a future palette tweak can't silently break readability.
 *
 * Pure + dependency-free.
 */

/** Parse `#rgb` or `#rrggbb` into [r, g, b] (0–255). */
export function hexToRgb(hex: string): [number, number, number] {
  let h = hex.trim().replace(/^#/, "");
  if (h.length === 3) h = h.split("").map((c) => c + c).join("");
  if (!/^[0-9a-fA-F]{6}$/.test(h)) {
    throw new Error(`bad hex color: ${hex}`);
  }
  return [
    parseInt(h.slice(0, 2), 16),
    parseInt(h.slice(2, 4), 16),
    parseInt(h.slice(4, 6), 16),
  ];
}

/** Relative luminance per WCAG 2.1 (sRGB). */
export function relativeLuminance(hex: string): number {
  const channel = (v: number) => {
    const s = v / 255;
    return s <= 0.03928 ? s / 12.92 : Math.pow((s + 0.055) / 1.055, 2.4);
  };
  const [r, g, b] = hexToRgb(hex);
  return 0.2126 * channel(r) + 0.7152 * channel(g) + 0.0722 * channel(b);
}

/** Contrast ratio between two colors, 1 (none) … 21 (black/white). */
export function contrastRatio(fg: string, bg: string): number {
  const l1 = relativeLuminance(fg);
  const l2 = relativeLuminance(bg);
  const lighter = Math.max(l1, l2);
  const darker = Math.min(l1, l2);
  return (lighter + 0.05) / (darker + 0.05);
}

/**
 * WCAG AA: 4.5:1 for normal text, 3:1 for large text (≥18.66px bold or
 * ≥24px). The doodle UI uses a large hand-drawn font, so `large` is the
 * common case — but the helper defaults to the stricter normal bar.
 */
export function meetsAA(fg: string, bg: string, large = false): boolean {
  return contrastRatio(fg, bg) >= (large ? 3 : 4.5);
}
