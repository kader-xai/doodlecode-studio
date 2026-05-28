import { useMemo } from "react";
import { useStore } from "../store";

/**
 * Background ambient layer — soft floating doodle shapes behind the
 * canvas. CSS-only animation (no RAF / state churn): each shape is a
 * positioned span with two CSS variables (`--dx`, `--dy`) feeding a
 * keyframe that drifts and rotates it forever.
 *
 * Sits at `z: 0`, `pointer-events: none`, so cells (z: 10+) and the
 * ReactFlow pane stay fully interactive on top.
 *
 * Themes are just emoji/symbol arrays — keeps the asset size at zero
 * and reads "doodle" without an icon-font dependency.
 */
const THEMES: Record<"geometry" | "nature" | "science", string[]> = {
  geometry: ["◯", "△", "□", "✦", "✚", "◊", "✱"],
  nature:   ["🌱", "🍃", "💧", "🌸", "🪶", "🌿", "🍂"],
  science:  ["⚛", "🧪", "🔬", "📐", "🧮", "🪐", "⚙"],
};

const COUNT = 22;

interface Shape {
  symbol: string;
  left: number;
  top: number;
  size: number;
  duration: number;
  delay: number;
  dx: number;
  dy: number;
  rotate: number;
}

function buildShapes(symbols: string[]): Shape[] {
  // Deterministic per-mount using Math.random — re-generated every
  // theme change so the new shapes feel fresh.
  const out: Shape[] = [];
  for (let i = 0; i < COUNT; i++) {
    out.push({
      symbol: symbols[i % symbols.length],
      left: Math.random() * 100,
      top: Math.random() * 100,
      size: 20 + Math.random() * 28,
      duration: 28 + Math.random() * 24,
      delay: -Math.random() * 40, // negative so they're mid-animation on mount
      dx: (Math.random() * 2 - 1) * 80,
      dy: (Math.random() * 2 - 1) * 80,
      rotate: Math.round((Math.random() * 2 - 1) * 30),
    });
  }
  return out;
}

export function AmbientLayer() {
  const ambient = useStore((s) => s.ambient);
  const presenting = useStore((s) => s.presenting);
  const shapes = useMemo<Shape[]>(
    () => (ambient === "off" ? [] : buildShapes(THEMES[ambient])),
    [ambient],
  );

  if (ambient === "off") return null;

  // Slightly more opaque in editor than during presentation so it
  // doesn't compete with the active slide.
  const baseOpacity = presenting ? 0.05 : 0.08;

  return (
    <div
      aria-hidden
      className="fixed inset-0 z-0 pointer-events-none overflow-hidden"
    >
      {shapes.map((s, i) => (
        <span
          key={`${ambient}-${i}`}
          className="absolute select-none"
          style={{
            left: `${s.left}%`,
            top: `${s.top}%`,
            fontSize: s.size,
            opacity: baseOpacity,
            ["--dx" as string]: `${s.dx}px`,
            ["--dy" as string]: `${s.dy}px`,
            ["--rot" as string]: `${s.rotate}deg`,
            animation: `doodle-drift ${s.duration}s ease-in-out ${s.delay}s infinite alternate`,
            willChange: "transform",
          }}
        >
          {s.symbol}
        </span>
      ))}
    </div>
  );
}
