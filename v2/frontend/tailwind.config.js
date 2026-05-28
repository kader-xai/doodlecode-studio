/** @type {import('tailwindcss').Config} */
export default {
  content: ["./index.html", "./src/**/*.{ts,tsx}"],
  darkMode: "class",
  theme: {
    extend: {
      fontFamily: {
        hand: ['"Patrick Hand"', '"Caveat"', "ui-sans-serif", "system-ui"],
        mono: ['"JetBrains Mono"', "ui-monospace", "monospace"],
      },
      colors: {
        ink: "#2a2a2a",
        sandal: "#f5ecd6",
        "marker-yellow": "#ffe066",
        "marker-pink":   "#fcc2d7",
        "marker-mint":   "#b2f2bb",
        "marker-sky":    "#a5d8ff",
        "marker-peach":  "#ffd8a8",
        "marker-violet": "#d0bfff",
      },
      boxShadow: {
        sketch: "3px 3px 0 0 rgba(42,42,42,0.85)",
      },
    },
  },
  plugins: [],
};
