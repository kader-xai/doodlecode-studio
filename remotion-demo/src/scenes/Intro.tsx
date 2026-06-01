import React from "react";
import { AbsoluteFill, interpolate, spring, useCurrentFrame, useVideoConfig } from "remotion";
import { C, FONT_HAND } from "../theme";
import { PaperBg } from "../components/Doodle";

export const Intro: React.FC = () => {
  const frame = useCurrentFrame();
  const { fps } = useVideoConfig();
  const pop = spring({ frame, fps, config: { damping: 12 } });
  const sub = interpolate(frame, [18, 34], [0, 1], { extrapolateRight: "clamp" });
  const colors = [C.pink, C.sky, C.mint, C.yellow, C.violet, C.peach];
  return (
    <AbsoluteFill>
      <PaperBg />
      {/* floating doodle marks */}
      {colors.map((col, i) => {
        const a = (i / colors.length) * Math.PI * 2 + frame * 0.01;
        return (
          <div
            key={i}
            style={{
              position: "absolute",
              left: 960 + Math.cos(a) * 560 - 18,
              top: 540 + Math.sin(a) * 300 - 18,
              width: 36,
              height: 36,
              borderRadius: i % 2 ? 18 : 6,
              background: col,
              opacity: 0.25,
              transform: `rotate(${frame * (i % 2 ? 1 : -1)}deg)`,
            }}
          />
        );
      })}
      <AbsoluteFill style={{ justifyContent: "center", alignItems: "center" }}>
        <div
          style={{
            fontFamily: FONT_HAND,
            fontSize: 150,
            color: C.ink,
            transform: `scale(${0.6 + pop * 0.4})`,
            textShadow: "4px 6px 0 rgba(0,0,0,0.08)",
          }}
        >
          🎨 DoodleCode
        </div>
        <div
          style={{
            fontFamily: FONT_HAND,
            fontSize: 46,
            color: C.pink,
            opacity: sub,
            marginTop: 8,
          }}
        >
          present · explain · visualize — in one doodle canvas
        </div>
      </AbsoluteFill>
    </AbsoluteFill>
  );
};
