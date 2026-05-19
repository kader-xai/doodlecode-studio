/**
 * Shape catalogs for the presenter ambient layer. Each entry is a
 * standalone SVG path drawn inside a uniform 60×60 viewBox so the
 * floating layer can mix shapes without per-shape size juggling.
 *
 * Paths are intentionally hand-drawn: quadratic curves, slight
 * imperfection, open endings — the goal is "doodle on a whiteboard",
 * not "vector icon".
 */

export type AmbientTheme = "doodle" | "zen" | "tech" | "ideas" | "off";

export type ShapeDef = {
  /** SVG path d-string in 60×60 viewBox */
  d: string;
  /** Optional secondary path drawn over the first (no fill, same stroke). */
  d2?: string;
  /** Visual weight in px stroke-width; default 2.2 */
  weight?: number;
};

// -------------------- Doodle (original squiggles) --------------------
const DOODLE: ShapeDef[] = [
  { d: "M2 30 q8 -16 16 0 t16 0 t16 0 t10 -6" },
  { d: "M5 40 q12 -30 24 0 t24 0", weight: 2 },
  { d: "M30 6 a24 24 0 1 0 0.1 0", weight: 2.4 },
  { d: "M4 8 h10 m6 0 h10 m6 0 h10 m6 0 h6" },
  { d: "M30 6 L56 50 L4 50 Z", weight: 2 },
  { d: "M5 30 q8 -12 16 0 t16 0 t16 0", weight: 2 },
];

// -------------------- Zen (calm, philosophical) --------------------
const ZEN: ShapeDef[] = [
  // Enso (almost-closed circle, opening at top-right)
  { d: "M45 12 a22 22 0 1 0 6 22", weight: 3 },
  // Bamboo segment
  { d: "M28 6 v18 M28 28 v18 M28 50 v6 M22 24 h12 M22 46 h12", weight: 2 },
  // Mountain pair
  { d: "M4 50 L18 22 L28 36 L40 14 L56 50 Z", weight: 2 },
  // Wave
  { d: "M2 38 q8 -10 16 0 t16 0 t16 0 t10 -2", weight: 2 },
  // Cloud
  { d: "M10 36 q-6 -10 4 -12 q0 -10 12 -10 q6 -10 16 -2 q12 0 10 12 q10 4 4 12 z", weight: 2 },
  // Leaf
  { d: "M30 6 q14 18 0 48 q-14 -30 0 -48 z", weight: 2 },
  // Sun + 4 rays
  {
    d: "M30 30 m-10 0 a10 10 0 1 0 20 0 a10 10 0 1 0 -20 0",
    d2: "M30 6 v8 M30 46 v8 M6 30 h8 M46 30 h8 M14 14 L20 20 M40 40 L46 46 M14 46 L20 40 M40 20 L46 14",
    weight: 2,
  },
  // Yin-yang style two-dot
  { d: "M30 12 a18 18 0 1 0 0 36 a9 9 0 1 1 0 -18 a9 9 0 1 0 0 -18", weight: 2.4 },
];

// -------------------- Tech (servers, code, infra) --------------------
const TECH: ShapeDef[] = [
  // Server rack (three U's + status dots)
  {
    d: "M6 12 h48 v8 h-48 z M6 26 h48 v8 h-48 z M6 40 h48 v8 h-48 z",
    d2: "M48 16 h2 M48 30 h2 M48 44 h2",
    weight: 2,
  },
  // Terminal window with prompt
  {
    d: "M4 10 h52 v40 h-52 z M4 18 h52",
    d2: "M10 30 L14 34 L10 38 M18 38 h10",
    weight: 2,
  },
  // Code brackets { }
  {
    d: "M22 8 q-8 0 -8 8 v6 q0 6 -6 8 q6 2 6 8 v6 q0 8 8 8",
    d2: "M38 8 q8 0 8 8 v6 q0 6 6 8 q-6 2 -6 8 v6 q0 8 -8 8",
    weight: 2.4,
  },
  // Database cylinder
  {
    d: "M14 14 a16 6 0 0 0 32 0 a16 6 0 0 0 -32 0 v32 a16 6 0 0 0 32 0 v-32",
    d2: "M14 26 a16 6 0 0 0 32 0 M14 38 a16 6 0 0 0 32 0",
    weight: 2,
  },
  // Chip / IC with pins
  {
    d: "M14 14 h32 v32 h-32 z",
    d2: "M14 22 h-6 M14 30 h-6 M14 38 h-6 M46 22 h6 M46 30 h6 M46 38 h6 M22 14 v-6 M30 14 v-6 M38 14 v-6 M22 46 v6 M30 46 v6 M38 46 v6",
    weight: 2,
  },
  // Gear (octagonal)
  {
    d: "M30 18 a12 12 0 1 0 0 24 a12 12 0 1 0 0 -24",
    d2: "M30 6 v6 M30 48 v6 M6 30 h6 M48 30 h6 M13 13 L17 17 M43 43 L47 47 M13 47 L17 43 M43 17 L47 13",
    weight: 2,
  },
  // Wi-Fi waves
  {
    d: "M30 50 a3 3 0 1 0 0 0.01",
    d2: "M18 42 q12 -12 24 0 M10 34 q20 -18 40 0 M2 26 q28 -22 56 0",
    weight: 2,
  },
  // Cloud + upload arrow
  {
    d: "M10 36 q-6 -10 4 -12 q0 -10 12 -10 q6 -10 16 -2 q12 0 10 12 q10 4 4 12 z",
    d2: "M30 30 v18 M24 36 L30 30 L36 36",
    weight: 2,
  },
  // Monitor + stand
  {
    d: "M6 10 h48 v30 h-48 z",
    d2: "M22 40 v6 h16 v-6 M16 46 h28 M14 18 L20 24 L14 30 M22 30 h12",
    weight: 2,
  },
];

// -------------------- Ideas (creativity, sparks) --------------------
const IDEAS: ShapeDef[] = [
  // Light bulb
  {
    d: "M30 6 q-12 0 -12 14 q0 8 6 14 v8 h12 v-8 q6 -6 6 -14 q0 -14 -12 -14 z",
    d2: "M24 46 h12 M26 50 h8",
    weight: 2,
  },
  // 4-point sparkle
  {
    d: "M30 4 L33 27 L56 30 L33 33 L30 56 L27 33 L4 30 L27 27 Z",
    weight: 2,
  },
  // 6-point star
  {
    d: "M30 6 L36 24 L54 24 L40 36 L46 54 L30 42 L14 54 L20 36 L6 24 L24 24 Z",
    weight: 2,
  },
  // Paper plane
  {
    d: "M6 30 L54 8 L30 54 L26 36 Z",
    d2: "M26 36 L54 8",
    weight: 2,
  },
  // Sticky note (folded corner)
  {
    d: "M8 8 h36 l8 8 v36 h-44 z",
    d2: "M44 8 v8 h8",
    weight: 2,
  },
  // Curved arrow (eureka swoop)
  {
    d: "M8 50 q12 -40 44 -30",
    d2: "M46 14 L52 20 L46 26",
    weight: 2.4,
  },
  // Question mark
  {
    d: "M22 18 q0 -14 14 -14 t14 14 q0 8 -14 12 v8",
    d2: "M36 50 a2 2 0 1 0 0.01 0",
    weight: 2.4,
  },
  // Speech bubble
  {
    d: "M6 10 h48 v32 h-30 L14 52 L18 42 h-12 z",
    d2: "M16 22 h28 M16 30 h20",
    weight: 2,
  },
];

const CATALOGS: Record<Exclude<AmbientTheme, "off">, ShapeDef[]> = {
  doodle: DOODLE,
  zen: ZEN,
  tech: TECH,
  ideas: IDEAS,
};

export function shapesFor(theme: AmbientTheme): ShapeDef[] {
  if (theme === "off") return [];
  return CATALOGS[theme] ?? DOODLE;
}

export const THEME_OPTIONS: { id: AmbientTheme; label: string; subtitle: string }[] = [
  { id: "doodle", label: "🎨 Doodle", subtitle: "the original squiggles" },
  { id: "zen",    label: "🌿 Zen",    subtitle: "calm, philosophical — clouds, leaves, ensō" },
  { id: "tech",   label: "💻 Tech",   subtitle: "servers, code, chips, terminals" },
  { id: "ideas",  label: "💡 Ideas",  subtitle: "sparkles, lightbulbs, paper planes" },
  { id: "off",    label: "🚫 Off",    subtitle: "no ambient — pure focus" },
];
