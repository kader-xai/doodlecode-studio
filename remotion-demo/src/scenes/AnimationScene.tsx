import React from "react";
import { AbsoluteFill, interpolate, useCurrentFrame } from "remotion";
import { C, FONT_HAND } from "../theme";
import { PaperBg, PopCard, SceneLabel, CellTitle, Chip } from "../components/Doodle";

const FRAMES = ["Input goes in →", "Something happens", "← Output comes out", "Ship it ✨"];

// Animation cell — reveal one beat at a time, with a transition.
export const AnimationScene: React.FC = () => {
  const frame = useCurrentFrame();
  // advance a new frame roughly every 22 video frames.
  const step = Math.min(FRAMES.length - 1, Math.floor(interpolate(frame, [10, 98], [0, FRAMES.length], { extrapolateRight: "clamp" })));
  const localStart = 10 + step * 22;
  const reveal = interpolate(frame - localStart, [0, 10], [0, 1], { extrapolateLeft: "clamp", extrapolateRight: "clamp" });

  return (
    <AbsoluteFill>
      <PaperBg />
      <SceneLabel text="Build it up live" color={C.sky} />

      <PopCard delay={4} x={460} y={280} w={1000} h={420} stroke={C.sky} fill="#fff">
        <CellTitle color={C.sky}>🎞 Animation cell — press → to reveal</CellTitle>
        <div style={{ height: 230, display: "flex", alignItems: "center", justifyContent: "center" }}>
          <div
            style={{
              fontFamily: FONT_HAND,
              fontSize: 74,
              color: C.ink,
              opacity: reveal,
              transform: `translateY(${(1 - reveal) * 16}px) scale(${0.9 + reveal * 0.1})`,
              textAlign: "center",
            }}
          >
            {FRAMES[step]}
          </div>
        </div>
        <div style={{ display: "flex", justifyContent: "center", alignItems: "center", gap: 14 }}>
          {FRAMES.map((_, i) => (
            <span
              key={i}
              style={{
                width: 16,
                height: 16,
                borderRadius: 8,
                border: `2px solid ${C.ink}`,
                background: i === step ? C.pink : "transparent",
              }}
            />
          ))}
          <span style={{ marginLeft: 12 }}>
            <Chip bg={C.yellow} fg={C.ink}>🎞 fade · slide · pop · draw-on</Chip>
          </span>
        </div>
      </PopCard>
    </AbsoluteFill>
  );
};
