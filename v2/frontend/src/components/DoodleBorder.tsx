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
 *
 * Iter 153: two-pass rendering. A real pencil drawn rectangle isn't
 * a single perfect line — it's two slightly-different strokes that
 * almost overlap. We render the same path twice with different
 * noise seeds; the second pass is thinner and inset by a couple of
 * pixels. The result reads as a confident hand-drawn box instead of
 * a wobbly CAD line.
 */
export function DoodleBorder({
  radius = 18,
  jitter = 2.2,
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

  // Iter 153: pass A is the main stroke. Pass B is a thinner ghost
  // inset by ~1.5px with a different noise seed — it reads as the
  // "second swipe" of the pencil. The two together look more like a
  // confident hand-drawn box.
  const pathA = useMemo(
    () => buildPath(size.w, size.h, radius, jitter, 0, 0, 0),
    [size.w, size.h, radius, jitter],
  );
  const pathB = useMemo(
    () => buildPath(size.w, size.h, radius, jitter * 0.7, 1.4, 1.4, 100),
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
        d={pathA}
        stroke={stroke}
        strokeWidth={strokeWidth}
        fill={fill}
        strokeLinecap="round"
        strokeLinejoin="round"
        vectorEffect="non-scaling-stroke"
      />
      <path
        d={pathB}
        stroke={stroke}
        strokeWidth={strokeWidth * 0.55}
        fill="transparent"
        strokeLinecap="round"
        strokeLinejoin="round"
        strokeOpacity={0.45}
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
/**
 * iter 153: `insetX` / `insetY` shift the path inward (>0) so the
 * ghost pass sits inside the main stroke. `seedOffset` shifts the
 * noise lookup so the two passes don't trace exactly the same wobble.
 */
function buildPath(
  w: number,
  h: number,
  radius: number,
  jitter: number,
  insetX = 0,
  insetY = 0,
  seedOffset = 0,
): string {
  const W = w - 2 * insetX;
  const H = h - 2 * insetY;
  const r = Math.max(2, Math.min(radius, Math.min(W, H) / 2 - 2));
  // One anchor every ~64 px so the line stays "alive" across long
  // edges instead of looking like a straight CAD vector.
  const stepX = Math.max(1, Math.round((W - 2 * r) / 64));
  const stepY = Math.max(1, Math.round((H - 2 * r) / 64));
  // Deterministic sin-noise so re-renders produce the same wobble.
  const noise = (i: number) => {
    const v = Math.sin((i + seedOffset) * 12.9898 + 78.233) * 43758.5453;
    return v - Math.floor(v);
  };
  const j = (i: number) => (noise(i) - 0.5) * 2 * jitter;
  const x0 = insetX;
  const y0 = insetY;
  const x1 = insetX + W; // right edge
  const y1 = insetY + H; // bottom edge

  let d = `M ${x0 + r + j(1)} ${y0 + j(2)} `;
  let k = 3;
  // Top edge, left→right.
  for (let s = 1; s <= stepX; s++) {
    const t = s / (stepX + 1);
    const x = x0 + r + (W - 2 * r) * t;
    d += `L ${x + j(k++)} ${y0 + j(k++)} `;
  }
  d += `L ${x1 - r + j(k++)} ${y0 + j(k++)} `;
  // Top-right corner.
  d += `Q ${x1 + j(k++)} ${y0 + j(k++)} ${x1 + j(k++)} ${y0 + r + j(k++)} `;
  // Right edge, top→bottom.
  for (let s = 1; s <= stepY; s++) {
    const t = s / (stepY + 1);
    const y = y0 + r + (H - 2 * r) * t;
    d += `L ${x1 + j(k++)} ${y + j(k++)} `;
  }
  d += `L ${x1 + j(k++)} ${y1 - r + j(k++)} `;
  // Bottom-right corner.
  d += `Q ${x1 + j(k++)} ${y1 + j(k++)} ${x1 - r + j(k++)} ${y1 + j(k++)} `;
  // Bottom edge, right→left.
  for (let s = 1; s <= stepX; s++) {
    const t = s / (stepX + 1);
    const x = x1 - r - (W - 2 * r) * t;
    d += `L ${x + j(k++)} ${y1 + j(k++)} `;
  }
  d += `L ${x0 + r + j(k++)} ${y1 + j(k++)} `;
  // Bottom-left corner.
  d += `Q ${x0 + j(k++)} ${y1 + j(k++)} ${x0 + j(k++)} ${y1 - r + j(k++)} `;
  // Left edge, bottom→top.
  for (let s = 1; s <= stepY; s++) {
    const t = s / (stepY + 1);
    const y = y1 - r - (H - 2 * r) * t;
    d += `L ${x0 + j(k++)} ${y + j(k++)} `;
  }
  d += `L ${x0 + j(k++)} ${y0 + r + j(k++)} `;
  // Top-left corner.
  d += `Q ${x0 + j(k++)} ${y0 + j(k++)} ${x0 + r + j(k++)} ${y0 + j(k++)} `;
  d += "Z";
  return d;
}
