import rough from "roughjs";

/**
 * SVG dimensions MATCH the card's dimensions exactly (no over-paint).
 * The hand-drawn rectangle is inset by `BORDER_INSET` so the wavy
 * stroke (roughness + bowing + stroke-width) stays inside the SVG
 * bounds — i.e. inside the card. Result: the border never visibly
 * leaks past the box edge.
 */
const BORDER_INSET = 5;

export function sketchyBorder(
  width: number,
  height: number,
  opts: { stroke?: string; fill?: string; roughness?: number; seed?: number } = {}
): SVGSVGElement {
  const svg = document.createElementNS("http://www.w3.org/2000/svg", "svg");
  svg.setAttribute("width", String(width));
  svg.setAttribute("height", String(height));
  svg.classList.add("doodle-border");
  const rc = rough.svg(svg);
  const node = rc.rectangle(
    BORDER_INSET,
    BORDER_INSET,
    Math.max(8, width - 2 * BORDER_INSET),
    Math.max(8, height - 2 * BORDER_INSET),
    {
      roughness: opts.roughness ?? 1.4,
      bowing: 1.0,
      stroke: opts.stroke ?? "#2a2a2a",
      strokeWidth: 1.6,
      // No fill — the CSS .doodle-card paints the background. We use
      // the SVG ONLY for the hand-drawn wavy stroke on top.
      fill: opts.fill,
      fillStyle: opts.fill ? "solid" : undefined,
      seed: opts.seed ?? 42,
    }
  );
  svg.appendChild(node);
  return svg;
}

/** Excalidraw-inspired vibrant palette. Pastel fills designed to look good
 * on both white paper and dark backgrounds. */
export const PALETTE: Record<string, string> = {
  yellow: "#ffec99",
  pink: "#fcc2d7",
  mint: "#b2f2bb",
  sky: "#a5d8ff",
  peach: "#ffd8a8",
  lavender: "#d0bfff",
  rose: "#ffc9c9",
  cyan: "#99e9f2",
  violet: "#eebefa",
  green: "#8ce99a",
  blue: "#74c0fc",
  orange: "#ffa94d",
  red: "#ff8787",
  paper: "#fdf7e6",
  white: "#ffffff",
};

/** Dark-mode palette — same hues as light, slightly muted so light text
 * stays readable on top. Goal: WCAG AA against #ececec foreground. */
export const PALETTE_DARK: Record<string, string> = {
  yellow: "#735a05",
  pink: "#862e5a",
  mint: "#1e6b34",
  sky: "#0d4f8c",
  peach: "#9a3505",
  lavender: "#553aa8",
  rose: "#a3201f",
  cyan: "#076b7d",
  violet: "#6b2380",
  green: "#207a37",
  blue: "#1456a3",
  orange: "#a83a0a",
  red: "#a3201f",
  paper: "#1c1f25",
  white: "#1a1a1a",
};

const KIND_FALLBACK: Record<string, string> = {
  import: "sky",
  function: "mint",
  class: "pink",
  loop: "yellow",
  conditional: "yellow",
  assign: "peach",
  return: "lavender",
  try: "rose",
  context: "sky",
  intro: "sky",
};

export function colorFor(opts: { color?: string; kind?: string; dark?: boolean }): string {
  const name = opts.color || (opts.kind ? KIND_FALLBACK[opts.kind] : undefined);
  if (!name) return opts.dark ? "#2a2a2a" : "#f4f4f4";
  const table = opts.dark ? PALETTE_DARK : PALETTE;
  return table[name] ?? name;
}
