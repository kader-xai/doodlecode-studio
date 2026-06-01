import React from "react";
import { interpolate, useCurrentFrame } from "remotion";
import { C, FONT_HAND } from "../theme";

/** Animated hand-drawn bar chart — bars grow in. */
export const DoodleBars: React.FC<{
  data: { label: string; value: number; color: string }[];
  w: number;
  h: number;
  start?: number;
}> = ({ data, w, h, start = 0 }) => {
  const frame = useCurrentFrame();
  const max = Math.max(...data.map((d) => d.value));
  const pad = 46;
  const bw = (w - pad * 2) / data.length;
  return (
    <svg width={w} height={h}>
      <line x1={pad} y1={h - pad} x2={w - pad} y2={h - pad} stroke={C.ink} strokeWidth={3} />
      <line x1={pad} y1={pad - 10} x2={pad} y2={h - pad} stroke={C.ink} strokeWidth={3} />
      {data.map((d, i) => {
        const grow = interpolate(frame - start - i * 4, [0, 14], [0, 1], {
          extrapolateLeft: "clamp",
          extrapolateRight: "clamp",
        });
        const barH = ((d.value / max) * (h - pad * 2)) * grow;
        const x = pad + i * bw + bw * 0.18;
        const bwIn = bw * 0.64;
        return (
          <g key={i}>
            <rect
              x={x}
              y={h - pad - barH}
              width={bwIn}
              height={barH}
              fill={d.color}
              stroke={C.ink}
              strokeWidth={3}
              rx={6}
            />
            <text x={x + bwIn / 2} y={h - pad + 30} textAnchor="middle" fontFamily={FONT_HAND} fontSize={24} fill={C.ink}>
              {d.label}
            </text>
          </g>
        );
      })}
    </svg>
  );
};

/** Animated hand-drawn line chart — the stroke draws on. */
export const DoodleLine: React.FC<{
  points: number[];
  w: number;
  h: number;
  color?: string;
  start?: number;
}> = ({ points, w, h, color = C.sky, start = 0 }) => {
  const frame = useCurrentFrame();
  const pad = 46;
  const max = Math.max(...points);
  const min = Math.min(...points);
  const sx = (i: number) => pad + (i / (points.length - 1)) * (w - pad * 2);
  const sy = (v: number) => h - pad - ((v - min) / (max - min || 1)) * (h - pad * 2);
  const d = points.map((v, i) => `${i === 0 ? "M" : "L"} ${sx(i)} ${sy(v)}`).join(" ");
  const draw = interpolate(frame - start, [0, 26], [0, 1], { extrapolateLeft: "clamp", extrapolateRight: "clamp" });
  return (
    <svg width={w} height={h}>
      <line x1={pad} y1={h - pad} x2={w - pad} y2={h - pad} stroke={C.ink} strokeWidth={3} />
      <line x1={pad} y1={pad - 10} x2={pad} y2={h - pad} stroke={C.ink} strokeWidth={3} />
      <path
        d={d}
        fill="none"
        stroke={color}
        strokeWidth={5}
        strokeLinecap="round"
        strokeLinejoin="round"
        pathLength={1}
        strokeDasharray={1}
        strokeDashoffset={1 - draw}
      />
      {points.map((v, i) =>
        frame - start > i * 3 ? (
          <circle key={i} cx={sx(i)} cy={sy(v)} r={6} fill="#fff" stroke={color} strokeWidth={4} />
        ) : null,
      )}
    </svg>
  );
};

/** Animated hand-drawn pie/donut — slices sweep in. */
export const DoodlePie: React.FC<{
  data: { label: string; value: number; color: string }[];
  size: number;
  start?: number;
}> = ({ data, size, start = 0 }) => {
  const frame = useCurrentFrame();
  const total = data.reduce((s, d) => s + d.value, 0);
  const cx = size / 2;
  const cy = size / 2;
  const R = size / 2 - 24;
  const sweep = interpolate(frame - start, [0, 30], [0, 1], { extrapolateLeft: "clamp", extrapolateRight: "clamp" });
  let acc = -Math.PI / 2;
  const arc = (a0: number, a1: number) => {
    const x0 = cx + R * Math.cos(a0);
    const y0 = cy + R * Math.sin(a0);
    const x1 = cx + R * Math.cos(a1);
    const y1 = cy + R * Math.sin(a1);
    const large = a1 - a0 > Math.PI ? 1 : 0;
    return `M ${cx} ${cy} L ${x0} ${y0} A ${R} ${R} 0 ${large} 1 ${x1} ${y1} Z`;
  };
  return (
    <svg width={size} height={size}>
      {data.map((d, i) => {
        const frac = (d.value / total) * sweep;
        const a0 = acc;
        const a1 = acc + frac * Math.PI * 2;
        acc = a0 + (d.value / total) * Math.PI * 2;
        return <path key={i} d={arc(a0, a1)} fill={d.color} stroke={C.ink} strokeWidth={3} strokeLinejoin="round" />;
      })}
      <circle cx={cx} cy={cy} r={R * 0.42} fill="#fff5e6" stroke={C.ink} strokeWidth={3} />
    </svg>
  );
};
