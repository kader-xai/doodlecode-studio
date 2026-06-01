import React from "react";
import { AbsoluteFill, interpolate, useCurrentFrame } from "remotion";
import { C, FONT_HAND, FONT_MONO } from "../theme";
import { PaperBg, PopCard, CellTitle } from "../components/Doodle";

// Present full-screen, then scribble live with pen + highlighter.
export const PresentScene: React.FC = () => {
  const frame = useCurrentFrame();
  const prog = interpolate(frame, [0, 120], [0.2, 0.8], { extrapolateRight: "clamp" });
  const sec = Math.floor(frame / 30);
  const mm = String(Math.floor(sec / 60)).padStart(2, "0");
  const ss = String(sec % 60).padStart(2, "0");

  // highlighter sweep (yellow) then pen circle (red), both fading.
  const hl = interpolate(frame - 36, [0, 18], [0, 1], { extrapolateLeft: "clamp", extrapolateRight: "clamp" });
  const hlFade = interpolate(frame - 36, [18, 70], [1, 0.5], { extrapolateLeft: "clamp", extrapolateRight: "clamp" });
  const pen = interpolate(frame - 66, [0, 22], [0, 1], { extrapolateLeft: "clamp", extrapolateRight: "clamp" });

  return (
    <AbsoluteFill>
      <PaperBg />

      {/* top progress bar */}
      <div style={{ position: "absolute", top: 0, left: 0, right: 0, height: 8, background: "#0001" }}>
        <div style={{ height: "100%", width: `${prog * 100}%`, background: C.pink }} />
      </div>

      {/* talk timer */}
      <div
        style={{
          position: "absolute",
          top: 22,
          right: 28,
          fontFamily: FONT_MONO,
          fontSize: 30,
          background: "#fff",
          border: `3px solid ${C.ink}`,
          borderRadius: 14,
          padding: "4px 16px",
          boxShadow: "2px 3px 0 rgba(0,0,0,.15)",
        }}
      >
        ⏱ {mm}:{ss}
      </div>

      <div style={{ position: "absolute", top: 60, left: 90, fontFamily: FONT_HAND, fontSize: 46, color: C.pink }}>
        🎬 Presentation mode
      </div>

      {/* centered slide */}
      <PopCard delay={4} x={560} y={300} w={800} h={420} stroke={C.sky} fill="#fff">
        <CellTitle color={C.sky}>How a request flows</CellTitle>
        <div style={{ fontFamily: FONT_HAND, fontSize: 44, color: C.ink, lineHeight: 1.5, marginTop: 18 }}>
          Type a URL →<br />
          the server answers →<br />
          the page paints ✨
        </div>
      </PopCard>

      {/* ink overlay — explicit 1920×1080 so the strokes aren't clipped to
          the SVG's default 300×150 intrinsic size. */}
      <svg
        width={1920}
        height={1080}
        viewBox="0 0 1920 1080"
        style={{ position: "absolute", inset: 0, pointerEvents: "none" }}
      >
        {/* highlighter sweep across the heading */}
        <path
          d="M 600 380 L 1080 376"
          stroke={C.yellow}
          strokeWidth={26}
          strokeLinecap="round"
          opacity={0.45 * hlFade}
          pathLength={1}
          strokeDasharray={1}
          strokeDashoffset={1 - hl}
        />
        {/* red pen circle around "page paints" */}
        <path
          d="M 600 600 C 560 560, 1040 540, 1060 600 C 1080 660, 560 660, 600 600"
          fill="none"
          stroke={C.peach}
          strokeWidth={6}
          strokeLinecap="round"
          pathLength={1}
          strokeDasharray={1}
          strokeDashoffset={1 - pen}
        />
      </svg>

      {/* presenter bar */}
      <div style={{ position: "absolute", bottom: 36, left: "50%", transform: "translateX(-50%)", display: "flex", gap: 10 }}>
        {["◀", "▶", "✏️ Pen", "🖍 Highlighter", "🧽 Erase"].map((b, i) => (
          <span
            key={i}
            style={{
              fontFamily: FONT_HAND,
              fontSize: 26,
              background: i === 2 && pen > 0 ? C.peach : i === 3 && hl > 0 && pen === 0 ? C.yellow : "#fff",
              color: i === 2 && pen > 0 ? "#fff" : C.ink,
              border: `3px solid ${C.ink}`,
              borderRadius: 12,
              padding: "6px 16px",
              boxShadow: "2px 3px 0 rgba(0,0,0,.15)",
            }}
          >
            {b}
          </span>
        ))}
      </div>
    </AbsoluteFill>
  );
};
