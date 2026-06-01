import React from "react";
import { AbsoluteFill } from "remotion";
import { C, FONT_HAND } from "../theme";
import { PaperBg, PopCard, SceneLabel, CellTitle, Mono } from "../components/Doodle";

// One canvas, many cell types — the column + connector idea.
export const CanvasScene: React.FC = () => {
  return (
    <AbsoluteFill>
      <PaperBg />
      <SceneLabel text="One canvas, any cell" color={C.sky} />

      {/* connector line down the column */}
      <svg style={{ position: "absolute", inset: 0 }}>
        <path
          d="M 360 300 L 360 470 M 360 560 L 360 720"
          stroke={C.ink}
          strokeWidth={3}
          strokeDasharray="2 9"
          opacity={0.55}
        />
      </svg>

      <PopCard delay={6} x={150} y={220} w={420} h={90} stroke={C.sky} fill="#fff">
        <CellTitle color={C.sky}>🐍 Code</CellTitle>
      </PopCard>
      <PopCard delay={12} x={150} y={470} w={420} h={90} stroke={C.yellow} fill="#fff">
        <CellTitle color={C.peach}>📝 Markdown</CellTitle>
      </PopCard>
      <PopCard delay={18} x={150} y={720} w={420} h={90} stroke={C.mint} fill="#fff">
        <CellTitle color={C.mint}>🧭 Diagram</CellTitle>
      </PopCard>

      {/* the Add menu */}
      <PopCard delay={24} x={680} y={250} w={560} h={560} stroke={C.ink} fill="#fff">
        <div style={{ fontFamily: FONT_HAND, fontSize: 38, color: C.ink, marginBottom: 18 }}>➕ Add ▾</div>
        {[
          ["🐍", "Code", C.sky],
          ["📝", "Text / markdown", C.yellow],
          ["🖼", "Image / video", C.violet],
          ["🌐", "Browser", C.peach],
          ["✏️", "Whiteboard", C.mint],
          ["🧭", "Diagram / chart", C.pink],
          ["🎞", "Animation", C.sky],
        ].map(([ic, name], i) => (
          <div
            key={i}
            style={{
              fontFamily: FONT_HAND,
              fontSize: 30,
              color: C.ink,
              padding: "8px 6px",
              borderBottom: "2px dashed rgba(0,0,0,.12)",
            }}
          >
            {ic as string}  {name as string}
          </div>
        ))}
      </PopCard>

      <PopCard delay={30} x={1300} y={250} w={470} h={260} stroke={C.violet} fill="#fff">
        <CellTitle color={C.violet}>It's all one .py file</CellTitle>
        <Mono size={20} color={C.inkSoft}>{`# %% kind=code id=c1
# @title: Hello
print("hi")`}</Mono>
      </PopCard>
      <PopCard delay={36} x={1300} y={560} w={470} h={250} stroke={C.pink} fill="#fff">
        <CellTitle color={C.pink}>💬 Callouts</CellTitle>
        <div style={{ fontFamily: FONT_HAND, fontSize: 26, color: C.inkSoft }}>
          notes that ride beside any cell — text + images
        </div>
      </PopCard>
    </AbsoluteFill>
  );
};
