import { useMemo } from "react";
import { useStore } from "../store";
import { shapesFor } from "./presenterShapes";

/**
 * Doodle ambient — themed hand-drawn shapes drifting behind the cards
 * during 🎬 Present. Theme is chosen via the toolbar's Vibe picker;
 * "off" hides the layer entirely. Pure CSS motion + a single SVG path
 * per shape (plus an optional decorative inner path).
 */

type Drift = {
  shapeIndex: number;
  size: number;
  top: string;
  left: string;
  rotate: number;
  delay: number;
  duration: number;
  hueDelay: number;
};

function rand(seed: number): number {
  const x = Math.sin(seed * 9301 + 49297) * 233280;
  return x - Math.floor(x);
}

function buildDrift(count: number, shapeCount: number): Drift[] {
  const out: Drift[] = [];
  for (let i = 0; i < count; i++) {
    out.push({
      shapeIndex: Math.floor(rand(i + 101) * shapeCount),
      size: 70 + Math.floor(rand(i + 1) * 80),         // 70–150
      top: `${Math.floor(rand(i + 11) * 84) + 5}%`,
      left: `${Math.floor(rand(i + 31) * 90) + 2}%`,
      rotate: Math.floor(rand(i + 41) * 360),
      delay: -Math.floor(rand(i + 51) * 22),
      duration: 26 + Math.floor(rand(i + 61) * 18),    // 26–44s
      hueDelay: -Math.floor(rand(i + 71) * 30),
    });
  }
  return out;
}

export function PresenterAmbient() {
  const presenting = useStore((s) => s.presenting);
  const theme = useStore((s) => s.presenterAmbient);
  const catalog = useMemo(() => shapesFor(theme), [theme]);
  const drifts = useMemo(
    () => buildDrift(12, Math.max(1, catalog.length)),
    [catalog.length]
  );
  if (theme === "off" || catalog.length === 0) return null;

  // Lower opacity when not actively presenting so the vibe stays
  // subtle while editing, then comes alive during the talk.
  const wrapperClass = `doodle-ambient${presenting ? " doodle-ambient--presenting" : ""}`;

  return (
    <div className={wrapperClass} aria-hidden>
      {drifts.map((s, i) => {
        const shape = catalog[s.shapeIndex] ?? catalog[0];
        return (
          <svg
            key={`${theme}-${i}`}
            width={s.size}
            height={s.size}
            viewBox="0 0 60 60"
            style={{
              position: "absolute",
              top: s.top,
              left: s.left,
              animation: `doodle-drift ${s.duration}s ease-in-out ${s.delay}s infinite, doodle-hue 24s linear ${s.hueDelay}s infinite`,
              transform: `rotate(${s.rotate}deg)`,
            }}
          >
            <path
              d={shape.d}
              fill="none"
              strokeWidth={shape.weight ?? 2.2}
              strokeLinecap="round"
              strokeLinejoin="round"
            />
            {shape.d2 && (
              <path
                d={shape.d2}
                fill="none"
                strokeWidth={(shape.weight ?? 2.2) * 0.85}
                strokeLinecap="round"
                strokeLinejoin="round"
              />
            )}
          </svg>
        );
      })}
    </div>
  );
}
