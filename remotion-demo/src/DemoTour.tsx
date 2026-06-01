import React from "react";
import { AbsoluteFill, Sequence, interpolate, useCurrentFrame } from "remotion";
import { Intro } from "./scenes/Intro";
import { CanvasScene } from "./scenes/CanvasScene";
import { CodeScene } from "./scenes/CodeScene";
import { DiagramScene } from "./scenes/DiagramScene";
import { ChartsScene } from "./scenes/ChartsScene";
import { AnimationScene } from "./scenes/AnimationScene";
import { MediaScene } from "./scenes/MediaScene";
import { PresentScene } from "./scenes/PresentScene";
import { InstallScene } from "./scenes/InstallScene";
import { Outro } from "./scenes/Outro";

/** Fades a scene in/out at its edges so cuts feel smooth. */
const Fade: React.FC<{ dur: number; children: React.ReactNode }> = ({ dur, children }) => {
  const frame = useCurrentFrame();
  const op = interpolate(frame, [0, 8, dur - 8, dur], [0, 1, 1, 0], {
    extrapolateLeft: "clamp",
    extrapolateRight: "clamp",
  });
  return <AbsoluteFill style={{ opacity: op }}>{children}</AbsoluteFill>;
};

// 60s @ 30fps = 1800 frames. Timeline (from / duration):
const SCENES: { from: number; dur: number; el: React.ReactNode }[] = [
  { from: 0, dur: 130, el: <Intro /> },
  { from: 130, dur: 190, el: <CanvasScene /> },
  { from: 320, dur: 220, el: <CodeScene /> },
  { from: 540, dur: 190, el: <DiagramScene /> },
  { from: 730, dur: 190, el: <ChartsScene /> },
  { from: 920, dur: 190, el: <AnimationScene /> },
  { from: 1110, dur: 210, el: <MediaScene /> },
  { from: 1320, dur: 200, el: <PresentScene /> },
  { from: 1520, dur: 160, el: <InstallScene /> },
  { from: 1680, dur: 120, el: <Outro /> },
];

export const DemoTour: React.FC = () => (
  <AbsoluteFill>
    {SCENES.map((s, i) => (
      <Sequence key={i} from={s.from} durationInFrames={s.dur}>
        <Fade dur={s.dur}>{s.el}</Fade>
      </Sequence>
    ))}
  </AbsoluteFill>
);
