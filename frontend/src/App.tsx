import { useEffect } from "react";
import { DoodleCanvas } from "./components/DoodleCanvas";
import { PresenterBar } from "./components/PresenterBar";
import { PresenterOverlay } from "./components/PresenterOverlay";
import { Toolbar } from "./components/Toolbar";
import { About } from "./components/About";
import { CalloutEditor } from "./components/CalloutEditor";
import { TextEditor } from "./components/TextEditor";
import { InstallModal } from "./components/InstallModal";
import { useStore } from "./store";

export default function App() {
  const theme = useStore((s) => s.theme);
  const aboutOpen = useStore((s) => s.aboutOpen);
  const presenting = useStore((s) => s.presenting);
  const openEditor = useStore((s) => s.openEditor);
  const setOpenEditor = useStore((s) => s.setOpenEditor);
  const installOpen = useStore((s) => s.installOpen);
  const setInstallOpen = useStore((s) => s.setInstallOpen);
  const setMode = useStore((s) => s.setInteractionMode);
  const cell = useStore((s) =>
    openEditor ? s.notebook.cells.find((c) => c.id === openEditor.cellId) : undefined
  );

  useEffect(() => {
    document.documentElement.classList.toggle("dark", theme === "dark");
  }, [theme]);

  // Apply the active design as a class on <html> so the font CSS
  // custom properties switch instantly.
  const design = useStore((s) => s.design);
  useEffect(() => {
    const root = document.documentElement;
    root.classList.remove(
      "design-doodle",
      "design-professional",
      "design-serif",
      "design-mono"
    );
    root.classList.add(`design-${design}`);
  }, [design]);

  // Global font scaling — rem-based Tailwind utilities all rescale when
  // we change the root font-size. Default browser is 16px → 100%.
  const fontScale = useStore((s) => s.fontScale);
  useEffect(() => {
    document.documentElement.style.fontSize = `${fontScale * 100}%`;
  }, [fontScale]);

  // Mirror the browser's fullscreen state into the store + a body class
  // so CSS / components can react. Auto-flips off if the user presses
  // Esc (which exits fullscreen but we shouldn't lose presentation).
  const setFullscreen = useStore((s) => s.setFullscreen);
  useEffect(() => {
    const onChange = () => {
      const fs = !!document.fullscreenElement;
      setFullscreen(fs);
      document.documentElement.classList.toggle("fullscreen", fs);
    };
    document.addEventListener("fullscreenchange", onChange);
    return () => document.removeEventListener("fullscreenchange", onChange);
  }, [setFullscreen]);

  // Tool shortcuts: V = cursor, H = hand, M = move (Figma convention).
  // Off while presenting or typing.
  useEffect(() => {
    if (presenting) return;
    const onKey = (e: KeyboardEvent) => {
      const tag = (e.target as HTMLElement | null)?.tagName?.toLowerCase();
      if (tag === "input" || tag === "textarea" || tag === "select") return;
      if (e.metaKey || e.ctrlKey || e.altKey) return;
      if (e.key === "v" || e.key === "V") setMode("cursor");
      else if (e.key === "h" || e.key === "H") setMode("hand");
      else if (e.key === "m" || e.key === "M") setMode("move");
    };
    window.addEventListener("keydown", onKey);
    return () => window.removeEventListener("keydown", onKey);
  }, [presenting, setMode]);

  // Close any open editor on Escape (in addition to its own Close button).
  useEffect(() => {
    if (!openEditor) return;
    const onKey = (e: KeyboardEvent) => {
      if (e.key === "Escape") setOpenEditor(null);
    };
    window.addEventListener("keydown", onKey);
    return () => window.removeEventListener("keydown", onKey);
  }, [openEditor, setOpenEditor]);

  return (
    <div
      className={`${theme === "dark" ? "dark" : ""} ${
        presenting ? "presenting" : ""
      } w-screen h-screen relative overflow-hidden`}
    >
      <Toolbar />
      <DoodleCanvas />
      <PresenterBar />
      <PresenterOverlay />
      {aboutOpen && <About />}
      {installOpen && <InstallModal onClose={() => setInstallOpen(false)} />}

      {/* Singleton popovers. Mounted once at the top so they can't be
          hidden by ReactFlow's transform and there's only ever one. */}
      {openEditor?.kind === "callout" && cell && (
        <CalloutEditor
          cellId={openEditor.cellId}
          meta={cell.meta}
          onClose={() => setOpenEditor(null)}
        />
      )}
      {openEditor?.kind === "text" && cell && (
        <TextEditor
          cellId={openEditor.cellId}
          source={cell.source}
          meta={cell.meta}
          onClose={() => setOpenEditor(null)}
        />
      )}
    </div>
  );
}
