import React from "react";
import { AbsoluteFill, interpolate, useCurrentFrame } from "remotion";
import { C, FONT_HAND, FONT_MONO } from "../theme";
import { PaperBg, PopCard, SceneLabel, CellTitle, Chip } from "../components/Doodle";

const PKG = "transformers torch scikit-learn";

// Install any package or model, live, without leaving the canvas.
export const InstallScene: React.FC = () => {
  const frame = useCurrentFrame();
  const chars = Math.floor(interpolate(frame, [8, 40], [0, PKG.length], { extrapolateRight: "clamp" }));
  const typed = PKG.slice(0, chars);
  const installing = frame > 44 && frame < 80;
  const done = frame >= 80;
  const bar = interpolate(frame, [46, 78], [0, 1], { extrapolateLeft: "clamp", extrapolateRight: "clamp" });

  return (
    <AbsoluteFill>
      <PaperBg />
      <SceneLabel text="Install anything, live" color={C.violet} />

      <PopCard delay={4} x={560} y={270} w={800} h={520} stroke={C.violet} fill="#fff">
        <CellTitle color={C.violet}>📦 pip install</CellTitle>

        <div
          style={{
            background: "#f8f9fa",
            border: `3px solid ${C.ink}`,
            borderRadius: 12,
            padding: "14px 18px",
            fontFamily: FONT_MONO,
            fontSize: 26,
            color: C.ink,
          }}
        >
          $ {typed}
          <span style={{ opacity: frame % 20 < 10 && !done ? 1 : 0 }}>▌</span>
        </div>

        <div style={{ marginTop: 18, height: 18, background: "#e9ecef", borderRadius: 10, border: `2px solid ${C.ink}`, overflow: "hidden" }}>
          <div style={{ height: "100%", width: `${bar * 100}%`, background: done ? C.mint : C.sky }} />
        </div>

        <div style={{ fontFamily: FONT_MONO, fontSize: 20, color: C.inkSoft, marginTop: 14, minHeight: 90 }}>
          {installing && (
            <>
              Collecting transformers…<br />
              Downloading torch (≈ 200 MB)…<br />
              Building wheels…
            </>
          )}
          {done && (
            <div style={{ fontFamily: FONT_HAND, fontSize: 30, color: C.mint }}>
              ✓ Installed — import caches refreshed
            </div>
          )}
        </div>

        <div style={{ marginTop: 8 }}>
          <Chip bg={C.peach}>🤖 add models</Chip>
          <Chip bg={C.sky}>numpy</Chip>
          <Chip bg={C.mint}>pandas</Chip>
          <Chip bg={C.yellow} fg={C.ink}>matplotlib</Chip>
        </div>
        <div style={{ fontFamily: FONT_HAND, fontSize: 24, color: C.inkSoft, marginTop: 6 }}>
          the next <span style={{ fontFamily: FONT_MONO }}>import</span> just works — no restart
        </div>
      </PopCard>
    </AbsoluteFill>
  );
};
