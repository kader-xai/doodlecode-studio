import { useMemo } from "react";

/**
 * Pure-SVG wavy border. No roughjs dependency — we generate a closed
 * path with `Math.sin` perturbations so the line looks hand-drawn but
 * stays crisp at any zoom level.
 *
 * Props:
 *   - radius:    corner radius of the underlying rectangle
 *   - jitter:    px of random-feeling deviation
 *   - stroke:    line color
 *   - strokeWidth
 *   - fill:      paint inside the border (any CSS color)
 *
 * The SVG is absolutely positioned and `pointer-events: none`, so
 * the border is decorative — the parent stays interactive.
 */
export function DoodleBorder({
  radius = 18,
  jitter = 2.5,
  stroke = "#2a2a2a",
  strokeWidth = 2.5,
  fill = "transparent",
  className = "",
}: {
  radius?: number;
  jitter?: number;
  stroke?: string;
  strokeWidth?: number;
  fill?: string;
  className?: string;
}) {
  // We render at 0..100 viewBox and stretch with preserveAspectRatio
  // so the wobble pattern scales with the card.
  const path = useMemo(() => buildPath(radius, jitter), [radius, jitter]);
  return (
    <svg
      aria-hidden
      className={`absolute inset-0 w-full h-full pointer-events-none ${className}`}
      viewBox="0 0 100 100"
      preserveAspectRatio="none"
    >
      <path
        d={path}
        stroke={stroke}
        strokeWidth={strokeWidth}
        fill={fill}
        strokeLinecap="round"
        strokeLinejoin="round"
        vectorEffect="non-scaling-stroke"
      />
    </svg>
  );
}

function buildPath(radius: number, jitter: number): string {
  // Normalize radius to the 0..100 viewBox.
  const r = Math.min(radius, 25);
  const j = jitter * 0.4;
  // Walk a rounded rectangle, perturbing every line/arc point a
  // little. Seeded by a small deterministic noise so re-renders
  // produce the same wobble.
  const noise = (i: number) => (Math.sin(i * 12.9898) * 43758.5453) % 1;
  const n = (i: number) => (noise(i) - 0.5) * j * 2;

  let d = "";
  d += `M ${r + n(1)} ${0 + n(2)} `;
  d += `L ${100 - r + n(3)} ${0 + n(4)} `;
  d += `Q ${100 + n(5)} ${0 + n(6)} ${100 + n(7)} ${r + n(8)} `;
  d += `L ${100 + n(9)} ${100 - r + n(10)} `;
  d += `Q ${100 + n(11)} ${100 + n(12)} ${100 - r + n(13)} ${100 + n(14)} `;
  d += `L ${r + n(15)} ${100 + n(16)} `;
  d += `Q ${0 + n(17)} ${100 + n(18)} ${0 + n(19)} ${100 - r + n(20)} `;
  d += `L ${0 + n(21)} ${r + n(22)} `;
  d += `Q ${0 + n(23)} ${0 + n(24)} ${r + n(25)} ${0 + n(26)} `;
  d += "Z";
  return d;
}
