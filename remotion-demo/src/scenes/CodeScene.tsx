import React from "react";
import { AbsoluteFill, interpolate, useCurrentFrame } from "remotion";
import { C, FONT_HAND, FONT_MONO } from "../theme";
import { PaperBg, PopCard, SceneLabel, CellTitle, Chip } from "../components/Doodle";

const CODE = `import matplotlib.pyplot as plt
import numpy as np

x = np.linspace(0, 6.28, 200)
plt.plot(x, np.sin(x))
plt.title("live in the cell")
plt.show()`;

// Code cell runs real Python; matplotlib renders inline.
export const CodeScene: React.FC = () => {
  const frame = useCurrentFrame();
  const chars = Math.floor(interpolate(frame, [6, 50], [0, CODE.length], { extrapolateRight: "clamp" }));
  const typed = CODE.slice(0, chars);
  const ran = frame > 58;

  // sine plot "matplotlib output" draws on after Run.
  const draw = interpolate(frame, [62, 90], [0, 1], { extrapolateLeft: "clamp", extrapolateRight: "clamp" });
  const W = 560;
  const H = 230;
  const pad = 30;
  const pts = Array.from({ length: 80 }, (_, i) => {
    const t = i / 79;
    const px = pad + t * (W - pad * 2);
    const py = H / 2 - Math.sin(t * Math.PI * 2) * (H / 2 - pad);
    return `${i === 0 ? "M" : "L"} ${px} ${py}`;
  }).join(" ");

  return (
    <AbsoluteFill>
      <PaperBg />
      <SceneLabel text="Run real Python" color={C.sky} />

      <PopCard delay={4} x={150} y={250} w={720} h={560} stroke={C.sky} fill="#fff">
        <CellTitle color={C.sky}>🐍 Hello, matplotlib</CellTitle>
        <div
          style={{
            background: "#1f2228",
            borderRadius: 12,
            padding: 18,
            height: 320,
            border: `3px solid ${C.ink}`,
          }}
        >
          <pre style={{ fontFamily: FONT_MONO, fontSize: 22, color: "#e9ecef", margin: 0, lineHeight: 1.5 }}>
            {typed}
            <span style={{ opacity: frame % 20 < 10 ? 1 : 0 }}>▌</span>
          </pre>
        </div>
        <div style={{ marginTop: 16 }}>
          <Chip bg={ran ? C.mint : "#adb5bd"}>{ran ? "✓ ran in 0.04s" : "▶ Run"}</Chip>
        </div>
      </PopCard>

      <PopCard delay={56} x={970} y={300} w={620} h={460} stroke={C.peach} fill="#fff">
        <CellTitle color={C.peach}>📈 Output — inline plot</CellTitle>
        <svg width={W} height={H}>
          <line x1={pad} y1={H / 2} x2={W - pad} y2={H / 2} stroke="#ced4da" strokeWidth={2} />
          <path
            d={pts}
            fill="none"
            stroke={C.sky}
            strokeWidth={4}
            strokeLinecap="round"
            pathLength={1}
            strokeDasharray={1}
            strokeDashoffset={1 - draw}
          />
        </svg>
        <div style={{ fontFamily: FONT_HAND, fontSize: 24, color: C.inkSoft, marginTop: 6 }}>
          plt.show() → renders right below the editor
        </div>
      </PopCard>
    </AbsoluteFill>
  );
};
