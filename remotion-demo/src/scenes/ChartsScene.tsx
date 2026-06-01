import React from "react";
import { AbsoluteFill } from "remotion";
import { C } from "../theme";
import { PaperBg, PopCard, SceneLabel, CellTitle } from "../components/Doodle";
import { DoodleBars, DoodleLine, DoodlePie } from "../components/Charts";

// Data viz — bars, lines, pies, all hand-drawn from one tiny syntax.
export const ChartsScene: React.FC = () => {
  return (
    <AbsoluteFill>
      <PaperBg />
      <SceneLabel text="Data, hand-drawn" color={C.peach} />

      <PopCard delay={4} x={120} y={250} w={560} h={420} stroke={C.sky} fill="#fff">
        <CellTitle color={C.sky}>📊 bar</CellTitle>
        <DoodleBars
          w={500}
          h={300}
          start={10}
          data={[
            { label: "Idea", value: 6, color: C.yellow },
            { label: "Sketch", value: 8, color: C.sky },
            { label: "Try", value: 9, color: C.mint },
            { label: "Ship", value: 10, color: C.pink },
          ]}
        />
      </PopCard>

      <PopCard delay={12} x={710} y={250} w={520} h={420} stroke={C.mint} fill="#fff">
        <CellTitle color={C.mint}>📈 line</CellTitle>
        <DoodleLine w={460} h={300} start={20} points={[3, 5, 4, 7, 6, 9, 8, 11]} color={C.peach} />
      </PopCard>

      <PopCard delay={20} x={1260} y={250} w={520} h={420} stroke={C.pink} fill="#fff">
        <CellTitle color={C.pink}>🥧 pie</CellTitle>
        <div style={{ display: "flex", alignItems: "center", gap: 14 }}>
          <DoodlePie
            size={250}
            start={28}
            data={[
              { label: "A", value: 45, color: C.sky },
              { label: "B", value: 30, color: C.yellow },
              { label: "C", value: 25, color: C.mint },
            ]}
          />
        </div>
      </PopCard>

      <PopCard delay={30} x={520} y={720} w={880} h={120} stroke={C.violet} fill="#fff">
        <div style={{ fontFamily: "JetBrains Mono, monospace", fontSize: 26, color: C.inkSoft }}>
          chart: progress &nbsp;·&nbsp; Idea: 6 &nbsp;·&nbsp; Ship: 10 &nbsp;→&nbsp; instant doodle chart
        </div>
      </PopCard>
    </AbsoluteFill>
  );
};
