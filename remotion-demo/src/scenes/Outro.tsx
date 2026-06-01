import React from "react";
import { AbsoluteFill, interpolate, spring, useCurrentFrame, useVideoConfig } from "remotion";
import { C, FONT_HAND, FONT_MONO } from "../theme";
import { PaperBg, Chip } from "../components/Doodle";

// Wrap-up — one file, every medium, open source.
export const Outro: React.FC = () => {
  const frame = useCurrentFrame();
  const { fps } = useVideoConfig();
  const pop = spring({ frame, fps, config: { damping: 13 } });
  const line = interpolate(frame, [16, 30], [0, 1], { extrapolateRight: "clamp" });
  return (
    <AbsoluteFill>
      <PaperBg />
      <AbsoluteFill style={{ justifyContent: "center", alignItems: "center" }}>
        <div style={{ fontFamily: FONT_HAND, fontSize: 120, color: C.ink, transform: `scale(${0.7 + pop * 0.3})` }}>
          🎨 DoodleCode
        </div>
        <div style={{ fontFamily: FONT_HAND, fontSize: 40, color: C.pink, opacity: line, marginTop: 6 }}>
          code · charts · diagrams · media · animation — one .py, one canvas
        </div>
        <div style={{ marginTop: 26, opacity: line }}>
          <Chip bg={C.sky}>F5 to present</Chip>
          <Chip bg={C.mint}>open source</Chip>
          <Chip bg={C.yellow} fg={C.ink}>export .md</Chip>
        </div>
        <div style={{ fontFamily: FONT_MONO, fontSize: 26, color: C.inkSoft, opacity: line, marginTop: 22 }}>
          github.com/kader-xai/doodlecode-studio
        </div>
      </AbsoluteFill>
    </AbsoluteFill>
  );
};
