import { useLayoutEffect, useRef } from "react";
import { sketchyBorder } from "../lib/rough";

/**
 * Hand-drawn SVG border that ALWAYS tracks its parent's actual rendered
 * size, with zero dependency on React state or props for sizing.
 *
 * How:
 *   1. The wrapper div is `position: absolute; inset: 0` — stretches
 *      to fill the parent (the doodle-card) via CSS.
 *   2. A `ResizeObserver` watches the parent. On every size change
 *      (initial mount, content reflow, drag resize, font load, image
 *      load, anything) we synchronously read `getBoundingClientRect`
 *      and rebuild the SVG inside the wrapper to match.
 *
 * Because the SVG is mutated imperatively from the observer callback
 * (which fires immediately after layout) the wavy outline can NEVER
 * lag behind the box. There's also no need to pass width/height props
 * from React — the only React inputs are the colors and the seed.
 */
export function DoodleBorder({
  fill,
  stroke,
  seed,
}: {
  fill?: string;
  stroke?: string;
  seed?: number;
}) {
  const ref = useRef<HTMLDivElement>(null);

  useLayoutEffect(() => {
    const el = ref.current;
    if (!el) return;
    const parent = el.parentElement;
    if (!parent) return;

    let lastW = -1;
    let lastH = -1;

    const render = () => {
      const rect = parent.getBoundingClientRect();
      const w = Math.max(8, Math.ceil(rect.width));
      const h = Math.max(8, Math.ceil(rect.height));
      // Skip if dimensions haven't actually changed (avoids needless
      // rough.js work when only colors or content text changed).
      if (w === lastW && h === lastH) return;
      lastW = w;
      lastH = h;
      el.replaceChildren(sketchyBorder(w, h, { fill, stroke, seed }));
    };

    render();
    const ro = new ResizeObserver(render);
    ro.observe(parent);
    return () => ro.disconnect();
  }, [fill, stroke, seed]);

  return (
    <div
      ref={ref}
      style={{ position: "absolute", inset: 0, pointerEvents: "none" }}
    />
  );
}
