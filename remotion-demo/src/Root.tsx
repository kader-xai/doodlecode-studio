import React from "react";
import { Composition } from "remotion";
import { DemoTour } from "./DemoTour";
import { VIDEO } from "./theme";

export const RemotionRoot: React.FC = () => {
  return (
    <Composition
      id="DoodleTour"
      component={DemoTour}
      durationInFrames={VIDEO.durationInFrames}
      fps={VIDEO.fps}
      width={VIDEO.width}
      height={VIDEO.height}
    />
  );
};
