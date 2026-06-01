// DoodleCode Studio brand palette + type, mirrored from the app so the
// video feels native to the product.
export const C = {
  // Backgrounds (the app's "Sandal" page).
  bg: "#fff5e6",
  bgDark: "#1f2228",
  ink: "#2a2a2a",
  inkSoft: "#5a5048",
  // Marker colors (tailwind.config.js marker-*).
  pink: "#e64980",
  sky: "#1864ab",
  mint: "#2b8a3e",
  yellow: "#f59f00",
  violet: "#5f3dc4",
  peach: "#d9480f",
  paper: "#ffffff",
};

// Hand-drawn + monospace stacks (no font dependency required; swap in a
// Google font via @remotion/google-fonts if you want a crisper marker look).
export const FONT_HAND =
  '"Comic Sans MS", "Marker Felt", "Bradley Hand", "Segoe Print", cursive';
export const FONT_MONO =
  '"JetBrains Mono", "SFMono-Regular", "Menlo", "Consolas", monospace';

export const VIDEO = {
  fps: 30,
  width: 1920,
  height: 1080,
  durationInFrames: 30 * 60, // 60s
};
