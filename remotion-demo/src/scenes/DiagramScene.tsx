import React from "react";
import { AbsoluteFill, interpolate, useCurrentFrame } from "remotion";
import { C, FONT_HAND } from "../theme";
import { PaperBg, PopCard, SceneLabel, CellTitle } from "../components/Doodle";

const NODES = [
  { t: "Idea", c: C.yellow },
  { t: "Sketch", c: C.sky },
  { t: "Try it", c: C.mint },
  { t: "Ship 🚀", c: C.pink },
];

// Mermaid + flowcharts — one source becomes a hand-drawn diagram.
export const DiagramScene: React.FC = () => {
  const frame = useCurrentFrame();
  return (
    <AbsoluteFill>
      <PaperBg />
      <SceneLabel text="Mermaid + flowcharts" color={C.mint} />

      <PopCard delay={4} x={150} y={250} w={760} h={560} stroke={C.mint} fill="#fff">
        <CellTitle color={C.mint}>🧭 flowchart</CellTitle>
        <svg width={700} height={420} style={{ marginTop: 10 }}>
          {NODES.map((n, i) => {
            const show = interpolate(frame - 12 - i * 8, [0, 8], [0, 1], {
              extrapolateLeft: "clamp",
              extrapolateRight: "clamp",
            });
            const y = 20 + i * 96;
            return (
              <g key={i} opacity={show} transform={`translate(${260}, ${y})`}>
                <rect width={200} height={64} rx={14} fill={n.c} stroke={C.ink} strokeWidth={3} />
                <text x={100} y={40} textAnchor="middle" fontFamily={FONT_HAND} fontSize={30} fill="#fff">
                  {n.t}
                </text>
              </g>
            );
          })}
          {NODES.slice(0, -1).map((_, i) => {
            const show = interpolate(frame - 18 - i * 8, [0, 8], [0, 1], {
              extrapolateLeft: "clamp",
              extrapolateRight: "clamp",
            });
            const y = 84 + i * 96;
            return (
              <path
                key={i}
                d={`M 360 ${y} L 360 ${y + 32}`}
                stroke={C.ink}
                strokeWidth={3}
                markerEnd="url(#arrow)"
                opacity={show}
              />
            );
          })}
          <defs>
            <marker id="arrow" markerWidth="12" markerHeight="12" refX="6" refY="6" orient="auto">
              <path d="M1 1 L9 6 L1 11" fill="none" stroke={C.ink} strokeWidth="2" />
            </marker>
          </defs>
        </svg>
      </PopCard>

      <PopCard delay={26} x={990} y={300} w={600} h={460} stroke={C.violet} fill="#fff">
        <CellTitle color={C.violet}>+ Mermaid sequence · state · KaTeX math</CellTitle>
        <svg width={540} height={300}>
          {/* tiny sequence diagram */}
          <line x1={70} y1={20} x2={70} y2={280} stroke="#adb5bd" strokeWidth={2} strokeDasharray="4 6" />
          <line x1={420} y1={20} x2={420} y2={280} stroke="#adb5bd" strokeWidth={2} strokeDasharray="4 6" />
          <rect x={30} y={6} width={80} height={36} rx={8} fill={C.sky} stroke={C.ink} strokeWidth={2} />
          <text x={70} y={30} textAnchor="middle" fontFamily={FONT_HAND} fontSize={20} fill="#fff">User</text>
          <rect x={380} y={6} width={80} height={36} rx={8} fill={C.peach} stroke={C.ink} strokeWidth={2} />
          <text x={420} y={30} textAnchor="middle" fontFamily={FONT_HAND} fontSize={20} fill="#fff">App</text>
          {[80, 150, 220].map((y, i) => {
            const show = interpolate(frame - 34 - i * 7, [0, 6], [0, 1], { extrapolateLeft: "clamp", extrapolateRight: "clamp" });
            const ltr = i % 2 === 0;
            return (
              <path
                key={i}
                d={ltr ? `M 70 ${y} L 420 ${y}` : `M 420 ${y} L 70 ${y}`}
                stroke={C.ink}
                strokeWidth={2.5}
                markerEnd="url(#arrow)"
                opacity={show}
              />
            );
          })}
          <text x={270} y={272} textAnchor="middle" fontFamily="serif" fontSize={26} fill={C.ink}>
            ∫ e^(−x²) dx = √π
          </text>
        </svg>
      </PopCard>
    </AbsoluteFill>
  );
};
