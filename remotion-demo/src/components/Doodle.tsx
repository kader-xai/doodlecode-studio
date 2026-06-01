import React from "react";
import { interpolate, spring, useCurrentFrame, useVideoConfig } from "remotion";
import { C, FONT_HAND, FONT_MONO } from "../theme";

/**
 * Hand-drawn rounded-rect border. A two-pass wobbly stroke so it reads
 * like the app's DoodleBorder. Pure SVG, deterministic (no randomness).
 */
export const SketchBorder: React.FC<{
  w: number;
  h: number;
  stroke?: string;
  fill?: string;
  strokeWidth?: number;
  radius?: number;
}> = ({ w, h, stroke = C.ink, fill = C.paper, strokeWidth = 4, radius = 22 }) => {
  const r = radius;
  // Slight asymmetric control points give the wobble.
  const d = `M ${r} 3
    L ${w - r} 6 Q ${w - 4} 5 ${w - 5} ${r}
    L ${w - 3} ${h - r} Q ${w - 5} ${h - 4} ${w - r} ${h - 5}
    L ${r} ${h - 3} Q 5 ${h - 5} 6 ${h - r}
    L 3 ${r} Q 4 6 ${r} 4 Z`;
  return (
    <svg
      width={w}
      height={h}
      viewBox={`0 0 ${w} ${h}`}
      style={{ position: "absolute", inset: 0, overflow: "visible" }}
    >
      <path d={d} fill={fill} stroke={stroke} strokeWidth={strokeWidth} strokeLinejoin="round" />
      <path
        d={d}
        fill="none"
        stroke={stroke}
        strokeWidth={strokeWidth * 0.6}
        strokeLinejoin="round"
        opacity={0.35}
        transform="translate(1.5,2)"
      />
    </svg>
  );
};

/** A card that springs up into view (matches the app's slide-enter). */
export const PopCard: React.FC<{
  delay?: number;
  x?: number;
  y?: number;
  w: number;
  h: number;
  stroke?: string;
  fill?: string;
  children?: React.ReactNode;
  style?: React.CSSProperties;
}> = ({ delay = 0, x = 0, y = 0, w, h, stroke, fill, children, style }) => {
  const frame = useCurrentFrame();
  const { fps } = useVideoConfig();
  const s = spring({ frame: frame - delay, fps, config: { damping: 16, mass: 0.7 } });
  const op = interpolate(frame - delay, [0, 8], [0, 1], { extrapolateRight: "clamp" });
  return (
    <div
      style={{
        position: "absolute",
        left: x,
        top: y,
        width: w,
        height: h,
        opacity: op,
        transform: `translateY(${(1 - s) * 28}px) scale(${0.96 + s * 0.04})`,
        ...style,
      }}
    >
      <SketchBorder w={w} h={h} stroke={stroke} fill={fill} />
      <div style={{ position: "absolute", inset: 0, padding: 22 }}>{children}</div>
    </div>
  );
};

/** The doodle title strip used at the top of each app cell. */
export const CellTitle: React.FC<{ children: React.ReactNode; color?: string }> = ({
  children,
  color = C.ink,
}) => (
  <div
    style={{
      fontFamily: FONT_HAND,
      fontSize: 34,
      color,
      lineHeight: 1.1,
      marginBottom: 14,
    }}
  >
    {children}
  </div>
);

/** Big scene label (top-left), animates in. */
export const SceneLabel: React.FC<{ text: string; color?: string }> = ({
  text,
  color = C.pink,
}) => {
  const frame = useCurrentFrame();
  const x = interpolate(frame, [0, 12], [-40, 0], { extrapolateRight: "clamp" });
  const op = interpolate(frame, [0, 12], [0, 1], { extrapolateRight: "clamp" });
  return (
    <div
      style={{
        position: "absolute",
        top: 64,
        left: 90,
        transform: `translateX(${x}px)`,
        opacity: op,
        fontFamily: FONT_HAND,
        fontSize: 64,
        fontWeight: 700,
        color,
        textShadow: "2px 3px 0 rgba(0,0,0,0.08)",
      }}
    >
      {text}
    </div>
  );
};

export const Mono: React.FC<{ children: React.ReactNode; size?: number; color?: string }> = ({
  children,
  size = 24,
  color = C.ink,
}) => (
  <pre
    style={{
      fontFamily: FONT_MONO,
      fontSize: size,
      color,
      margin: 0,
      whiteSpace: "pre-wrap",
      lineHeight: 1.5,
    }}
  >
    {children}
  </pre>
);

/** A small rounded "chip" / button like the toolbar. */
export const Chip: React.FC<{ children: React.ReactNode; bg: string; fg?: string }> = ({
  children,
  bg,
  fg = "#fff",
}) => (
  <span
    style={{
      display: "inline-block",
      fontFamily: FONT_HAND,
      fontSize: 26,
      padding: "6px 18px",
      borderRadius: 14,
      background: bg,
      color: fg,
      border: `3px solid ${C.ink}`,
      boxShadow: "2px 3px 0 rgba(0,0,0,0.15)",
      margin: 6,
    }}
  >
    {children}
  </span>
);

/** A fake cursor that glides + clicks — sells the "interactive" feel. */
export const Cursor: React.FC<{ from: [number, number]; to: [number, number]; start: number; travel?: number; click?: number }>
  = ({ from, to, start, travel = 22, click }) => {
  const frame = useCurrentFrame();
  const p = interpolate(frame - start, [0, travel], [0, 1], {
    extrapolateLeft: "clamp",
    extrapolateRight: "clamp",
  });
  const x = from[0] + (to[0] - from[0]) * easeInOut(p);
  const y = from[1] + (to[1] - from[1]) * easeInOut(p);
  const clicking = click != null && frame >= click && frame < click + 6;
  return (
    <div style={{ position: "absolute", left: x, top: y, zIndex: 50 }}>
      {clicking && (
        <div
          style={{
            position: "absolute",
            left: -18,
            top: -18,
            width: 36,
            height: 36,
            borderRadius: 18,
            border: `3px solid ${C.pink}`,
            opacity: interpolate(frame - click!, [0, 6], [0.9, 0]),
            transform: `scale(${interpolate(frame - click!, [0, 6], [0.4, 1.6])})`,
          }}
        />
      )}
      <svg width="34" height="42" viewBox="0 0 24 30" style={{ filter: "drop-shadow(1px 2px 1px rgba(0,0,0,.3))" }}>
        <path d="M2 2 L2 22 L8 16 L12 26 L16 24 L12 14 L20 14 Z" fill="#fff" stroke={C.ink} strokeWidth="2" strokeLinejoin="round" />
      </svg>
    </div>
  );
};

export function easeInOut(t: number): number {
  return t < 0.5 ? 2 * t * t : 1 - Math.pow(-2 * t + 2, 2) / 2;
}

/** A faint paper-grid background (the app canvas dot grid). */
export const PaperBg: React.FC<{ dark?: boolean }> = ({ dark = false }) => (
  <div
    style={{
      position: "absolute",
      inset: 0,
      background: dark ? C.bgDark : C.bg,
      backgroundImage: `radial-gradient(${dark ? "#ffffff18" : "#0000000f"} 2px, transparent 2px)`,
      backgroundSize: "34px 34px",
    }}
  />
);
