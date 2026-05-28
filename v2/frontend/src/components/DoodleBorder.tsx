import { useEffect, useMemo, useRef, useState } from "react";

/**
 * Pure-SVG wavy border. No roughjs dependency — we generate a closed
 * path with deterministic sin-noise perturbations so the line looks
 * hand-drawn but stays crisp at any zoom level.
 *
 * Iter 46: dropped `preserveAspectRatio="none"` and the 0..100 viewBox
 * trick. That approach stretched the wobble pattern asymmetrically on
 * wide cells (browser 720×480, media 480×320, etc.) — the corners
 * looked elongated and the jitter pinched in one axis. We now read
 * the parent's actual rendered size via ResizeObserver and render the
 * path at 1:1 with that box, so the wobble keeps a consistent
 * amplitude on every side and the corners stay round.
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
  const svgRef = useRef<SVGSVGElement | null>(null);
  // Default to a square so the path is non-empty on first paint.
  const [size, setSize] = useState({ w: 320, h: 320 });

  useEffect(() => {
    const el = svgRef.current;
    if (!el) return;
    const ro = new ResizeObserver((entries) => {
      for (const e of entries) {
        const r = e.contentRect;
        if (r.width > 0 && r.height > 0) {
          setSize((prev) =>
            Math.abs(prev.w - r.width) < 0.5 && Math.abs(prev.h - r.height) < 0.5
              ? prev
              : { w: r.width, h: r.height },
          );
        }
      }
    });
    ro.observe(el);
    // Seed from current bounds (RO doesn't fire until next frame).
    const r = el.getBoundingClientRect();
    if (r.width > 0 && r.height > 0) setSize({ w: r.width, h: r.height });
    return () => ro.disconnect();
  }, []);

  const path = useMemo(
    () => buildPath(size.w, size.h, radius, jitter),
    [size.w, size.h, radius, jitter],
  );

  return (
    <svg
      ref={svgRef}
      aria-hidden
      className={`absolute inset-0 w-full h-full pointer-events-none ${className}`}
      viewBox={`0 0 ${Math.max(1, size.w)} ${Math.max(1, size.h)}`}
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

/**
 * Build a closed rounded-rectangle path with deterministic jitter
 * applied to every anchor. Anchors are sampled along the four edges
 * — count scales with edge length so a wide cell gets more anchors
 * on its long sides and the wobble stays at a consistent amplitude.
 */
function buildPath(w: number, h: number, radius: number, jitter: number): string {
  const r = Math.max(2, Math.min(radius, Math.min(w, h) / 2 - 2));
  // One anchor every ~64 px so the line stays "alive" across long
  // edges instead of looking like a straight CAD vector.
  const stepX = Math.max(1, Math.round((w - 2 * r) / 64));
  const stepY = Math.max(1, Math.round((h - 2 * r) / 64));
  // Deterministic sin-noise so re-renders produce the same wobble.
  const noise = (i: number) => {
    const v = Math.sin(i * 12.9898 + 78.233) * 43758.5453;
    return v - Math.floor(v);
  };
  const j = (i: number) => (noise(i) - 0.5) * 2 * jitter;

  let d = `M ${r + j(1)} ${0 + j(2)} `;
  let k = 3;
  // Top edge, left→right.
  for (let s = 1; s <= stepX; s++) {
    const t = s / (stepX + 1);
    const x = r + (w - 2 * r) * t;
    d += `L ${x + j(k++)} ${0 + j(k++)} `;
  }
  d += `L ${w - r + j(k++)} ${0 + j(k++)} `;
  // Top-right corner.
  d += `Q ${w + j(k++)} ${0 + j(k++)} ${w + j(k++)} ${r + j(k++)} `;
  // Right edge, top→bottom.
  for (let s = 1; s <= stepY; s++) {
    const t = s / (stepY + 1);
    const y = r + (h - 2 * r) * t;
    d += `L ${w + j(k++)} ${y + j(k++)} `;
  }
  d += `L ${w + j(k++)} ${h - r + j(k++)} `;
  // Bottom-right corner.
  d += `Q ${w + j(k++)} ${h + j(k++)} ${w - r + j(k++)} ${h + j(k++)} `;
  // Bottom edge, right→left.
  for (let s = 1; s <= stepX; s++) {
    const t = s / (stepX + 1);
    const x = w - r - (w - 2 * r) * t;
    d += `L ${x + j(k++)} ${h + j(k++)} `;
  }
  d += `L ${r + j(k++)} ${h + j(k++)} `;
  // Bottom-left corner.
  d += `Q ${0 + j(k++)} ${h + j(k++)} ${0 + j(k++)} ${h - r + j(k++)} `;
  // Left edge, bottom→top.
  for (let s = 1; s <= stepY; s++) {
    const t = s / (stepY + 1);
    const y = h - r - (h - 2 * r) * t;
    d += `L ${0 + j(k++)} ${y + j(k++)} `;
  }
  d += `L ${0 + j(k++)} ${r + j(k++)} `;
  // Top-left corner.
  d += `Q ${0 + j(k++)} ${0 + j(k++)} ${r + j(k++)} ${0 + j(k++)} `;
  d += "Z";
  return d;
}
