import { useEffect, useRef } from "react";
import { sketchyBorder } from "../lib/rough";

export function DoodleBorder({
  width,
  height,
  fill,
  stroke,
  seed,
}: {
  width: number;
  height: number;
  fill?: string;
  stroke?: string;
  seed?: number;
}) {
  const ref = useRef<HTMLDivElement>(null);
  useEffect(() => {
    if (!ref.current) return;
    ref.current.innerHTML = "";
    const svg = sketchyBorder(width, height, { fill, stroke, seed });
    ref.current.appendChild(svg);
  }, [width, height, fill, stroke, seed]);
  return <div ref={ref} style={{ position: "absolute", inset: -4, pointerEvents: "none" }} />;
}
