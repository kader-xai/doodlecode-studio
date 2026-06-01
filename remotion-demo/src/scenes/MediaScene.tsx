import React from "react";
import { AbsoluteFill, interpolate, useCurrentFrame } from "remotion";
import { C, FONT_HAND, FONT_MONO } from "../theme";
import { PaperBg, PopCard, SceneLabel, CellTitle } from "../components/Doodle";

// Embed live media — YouTube, GIFs, and real websites.
//
// NOTE: to use REAL footage instead of these mockups, drop files in
// public/assets/ and swap the mock blocks for, e.g.:
//   <OffthreadVideo src={staticFile("assets/clip.mp4")} />
//   <Img src={staticFile("assets/wikipedia.png")} />
//   <Img src={staticFile("assets/ai.gif")} />   (animated gifs play in Remotion)
export const MediaScene: React.FC = () => {
  const frame = useCurrentFrame();
  const prog = interpolate(frame % 120, [0, 120], [0, 1]);
  const pulse = (i: number) => 0.5 + 0.5 * Math.sin(frame * 0.15 + i);

  return (
    <AbsoluteFill>
      <PaperBg />
      <SceneLabel text="Embed live media" color={C.violet} />

      {/* YouTube mock */}
      <PopCard delay={4} x={110} y={250} w={560} h={400} stroke={C.peach} fill="#000">
        <div style={{ position: "relative", width: "100%", height: "78%", background: "#111", borderRadius: 8, overflow: "hidden" }}>
          <div style={{ position: "absolute", inset: 0, background: "linear-gradient(135deg,#3a1c1c,#1a1a2a)" }} />
          <div style={{ position: "absolute", left: "50%", top: "44%", transform: "translate(-50%,-50%)" }}>
            <svg width="92" height="92" viewBox="0 0 92 92">
              <rect width="92" height="64" y="14" rx="14" fill="#ff0000" />
              <path d="M38 32 L62 46 L38 60 Z" fill="#fff" />
            </svg>
          </div>
          <div style={{ position: "absolute", left: 0, right: 0, bottom: 8, height: 6, background: "#444", margin: "0 12px", borderRadius: 4 }}>
            <div style={{ width: `${prog * 100}%`, height: "100%", background: "#ff0000", borderRadius: 4 }} />
          </div>
        </div>
        <div style={{ fontFamily: FONT_HAND, fontSize: 28, color: "#fff", marginTop: 10 }}>▶ YouTube · Vimeo · MP4</div>
      </PopCard>

      {/* AI GIF mock — pulsing neural net */}
      <PopCard delay={12} x={710} y={250} w={460} h={400} stroke={C.sky} fill="#0b1020">
        <svg width={400} height={250}>
          {[0, 1, 2].map((layer) =>
            [0, 1, 2, 3].slice(0, layer === 1 ? 4 : 3).map((n, j) => {
              const x = 60 + layer * 140;
              const y = 50 + j * 56;
              return <circle key={`${layer}-${j}`} cx={x} cy={y} r={14 + pulse(layer + j) * 6} fill={[C.sky, C.pink, C.yellow][layer]} opacity={0.85} />;
            }),
          )}
          {/* edges */}
          {[0, 1].map((layer) =>
            [0, 1, 2].map((a) =>
              [0, 1, 2].map((b) => (
                <line
                  key={`${layer}-${a}-${b}`}
                  x1={60 + layer * 140}
                  y1={50 + a * 56}
                  x2={60 + (layer + 1) * 140}
                  y2={50 + b * 56}
                  stroke="#ffffff"
                  strokeWidth={1}
                  opacity={0.15 + pulse(a + b) * 0.2}
                />
              )),
            ),
          )}
        </svg>
        <div style={{ fontFamily: FONT_MONO, fontSize: 26, color: "#74c0fc", marginTop: 6 }}>ai-net.gif 🤖</div>
      </PopCard>

      {/* Wikipedia / live browser mock */}
      <PopCard delay={20} x={1210} y={250} w={580} h={500} stroke={C.mint} fill="#fff">
        <div style={{ display: "flex", gap: 8, alignItems: "center", marginBottom: 10 }}>
          <span style={{ width: 14, height: 14, borderRadius: 7, background: "#ff5f57", border: "1px solid #0003" }} />
          <span style={{ width: 14, height: 14, borderRadius: 7, background: "#febc2e", border: "1px solid #0003" }} />
          <span style={{ width: 14, height: 14, borderRadius: 7, background: "#28c840", border: "1px solid #0003" }} />
          <div style={{ flex: 1, marginLeft: 8, background: "#f1f3f5", borderRadius: 10, padding: "4px 14px", fontFamily: FONT_MONO, fontSize: 18, color: C.inkSoft }}>
            🔒 en.wikipedia.org
          </div>
        </div>
        <div style={{ borderTop: `2px solid ${C.ink}`, paddingTop: 12 }}>
          <div style={{ fontFamily: "Georgia, serif", fontSize: 32, color: C.ink, borderBottom: "1px solid #ddd", paddingBottom: 6 }}>
            DoodleCode
          </div>
          <div style={{ display: "flex", gap: 12, marginTop: 10 }}>
            <div style={{ flex: 1 }}>
              {[100, 92, 96, 70, 88, 60].map((wd, i) => (
                <div key={i} style={{ height: 10, width: `${wd}%`, background: "#e9ecef", borderRadius: 4, margin: "9px 0" }} />
              ))}
            </div>
            <div style={{ width: 120, height: 120, background: "#dee2e6", borderRadius: 6, border: "1px solid #adb5bd" }} />
          </div>
        </div>
        <div style={{ fontFamily: FONT_HAND, fontSize: 24, color: C.mint, marginTop: 10 }}>🌐 real sites — even X-Frame-blocked ones, via the proxy</div>
      </PopCard>
    </AbsoluteFill>
  );
};
