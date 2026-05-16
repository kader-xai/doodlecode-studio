/** @type {import('tailwindcss').Config} */
export default {
  darkMode: "class",
  content: ["./index.html", "./src/**/*.{ts,tsx}"],
  theme: {
    extend: {
      fontFamily: {
        hand: ["'Caveat'", "'Patrick Hand'", "'Comic Neue'", "cursive"],
        mono: ["'JetBrains Mono'", "ui-monospace", "monospace"],
      },
      colors: {
        paper: "#fdf7e6",
        ink: "#2a2a2a",
        marker: {
          yellow: "#fff394",
          pink: "#ffc4d6",
          mint: "#c4f4d2",
          sky: "#cde7ff",
          peach: "#ffd6a5",
        },
      },
      boxShadow: {
        sketch: "3px 4px 0 0 rgba(0,0,0,0.85)",
      },
    },
  },
  plugins: [],
};
