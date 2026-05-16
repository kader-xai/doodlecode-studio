import { useEffect } from "react";
import { DoodleCanvas } from "./components/DoodleCanvas";
import { PresenterBar } from "./components/PresenterBar";
import { Toolbar } from "./components/Toolbar";
import { About } from "./components/About";
import { useStore } from "./store";

export default function App() {
  const theme = useStore((s) => s.theme);
  const aboutOpen = useStore((s) => s.aboutOpen);
  const presenting = useStore((s) => s.presenting);

  useEffect(() => {
    document.documentElement.classList.toggle("dark", theme === "dark");
  }, [theme]);

  return (
    <div
      className={`${theme === "dark" ? "dark" : ""} ${
        presenting ? "presenting" : ""
      } w-screen h-screen relative overflow-hidden`}
    >
      <Toolbar />
      <DoodleCanvas />
      <PresenterBar />
      {aboutOpen && <About />}
    </div>
  );
}
