import { useRef } from "react";
import { exportNotebook, resetKernel, uploadNotebook } from "../api";
import { useStore } from "../store";
import { DesignPicker } from "./DesignPicker";

export function Toolbar() {
  const fileRef = useRef<HTMLInputElement>(null);
  const setNotebook = useStore((s) => s.setNotebook);
  const newNotebook = useStore((s) => s.newNotebook);
  const addCell = useStore((s) => s.addCell);
  const presenting = useStore((s) => s.presenting);
  const setPresenting = useStore((s) => s.setPresenting);
  const notebook = useStore((s) => s.notebook);
  const savedAt = useStore((s) => s.savedAt);
  const theme = useStore((s) => s.theme);
  const toggleTheme = useStore((s) => s.toggleTheme);
  const setAboutOpen = useStore((s) => s.setAboutOpen);
  const installing = useStore((s) => s.installing);
  const setInstallOpen = useStore((s) => s.setInstallOpen);
  const fullscreen = useStore((s) => s.fullscreen);
  const positionOverrides = useStore((s) => s.cellPositionOverrides);
  const autoSpace = useStore((s) => s.autoSpaceForPresentation);
  const rollback = useStore((s) => s.rollbackLayout);
  const mode = useStore((s) => s.interactionMode);
  const setMode = useStore((s) => s.setInteractionMode);

  // In fullscreen presentation mode the toolbar would be a distraction
  // (and would steal click events). Hide it completely — but AFTER all
  // hooks have run so React's hook count stays stable.
  if (fullscreen && presenting) return null;

  const onUpload = async (f: File) => {
    const nb = await uploadNotebook(f);
    nb.name = f.name;
    setNotebook(nb);
  };

  const onNew = () => {
    const name = window.prompt(
      "Name for the new file (e.g. lesson_intro.py):",
      "untitled.py"
    );
    if (!name || !name.trim()) return;
    newNotebook(name);
  };

  const onSave = async () => {
    const text = await exportNotebook(notebook);
    const blob = new Blob([text], { type: "text/x-python" });
    const url = URL.createObjectURL(blob);
    const a = document.createElement("a");
    a.href = url;
    a.download = notebook.name.endsWith(".py") ? notebook.name : `${notebook.name}.py`;
    document.body.appendChild(a);
    a.click();
    a.remove();
    URL.revokeObjectURL(url);
  };

  const savedLabel = savedAt
    ? `saved ${Math.max(1, Math.round((Date.now() - savedAt) / 1000))}s ago`
    : "unsaved";

  return (
    <div className="absolute top-3 left-3 right-3 z-30 flex items-start justify-between pointer-events-none">
      <div className="flex flex-col gap-1 pointer-events-auto">
        <div className="flex gap-2 items-center flex-wrap">
          <div className="font-hand text-3xl mr-1 select-none leading-none text-ink dark:text-white">
            🎨 DoodleCode <span className="text-[#c2255c] dark:text-[#fcc2d7]">Studio</span>
          </div>

          {/* Three tools: cursor / hand / move (V / H / M). Like Figma. */}
          <div className="flex gap-1 border-2 border-ink/40 dark:border-white/40 rounded-xl p-0.5 bg-white/40 dark:bg-black/30">
            {[
              { id: "cursor", icon: "➤", label: "Cursor — click selects, double-click edits (V)" },
              { id: "hand", icon: "✋", label: "Hand — drag to pan the canvas (H)" },
              { id: "move", icon: "✥", label: "Move — drag to reposition boxes (M)" },
            ].map((t) => (
              <button
                key={t.id}
                title={t.label}
                onClick={() => setMode(t.id as "cursor" | "hand" | "move")}
                className={`w-8 h-8 rounded-md border-2 text-lg font-hand transition ${
                  mode === t.id
                    ? "bg-marker-yellow border-ink dark:bg-amber-700 dark:border-white text-ink dark:text-white shadow-sketch"
                    : "bg-white/70 dark:bg-[#1f2228] border-ink/30 dark:border-white/30 text-ink/70 dark:text-white/70"
                }`}
              >
                {t.icon}
              </button>
            ))}
          </div>

          <button className="btn-sketch" onClick={onNew}>
            📄 New
          </button>
          <button className="btn-sketch sky" onClick={() => fileRef.current?.click()}>
            📂 Open
          </button>
          <input
            ref={fileRef}
            type="file"
            accept=".py,.ipynb,.md,.markdown,.txt"
            className="hidden"
            onChange={(e) => {
              const f = e.target.files?.[0];
              if (f) onUpload(f);
              e.currentTarget.value = "";
            }}
          />
          <button className="btn-sketch mint" onClick={onSave} title="Download notebook.name as .py">
            💾 Save
          </button>
          <button className="btn-sketch mint" onClick={() => addCell(undefined, "code")} title="Add a new code cell">
            ＋ Code
          </button>
          <button className="btn-sketch sky" onClick={() => addCell(undefined, "markdown")} title="Add a text / slide box">
            ＋ Text
          </button>
          <button
            className="btn-sketch violet"
            onClick={() => setInstallOpen(true)}
            title="Pip-install packages into the kernel"
          >
            📦 Install
          </button>
          <button className="btn-sketch peach" onClick={() => resetKernel()}>
            ↻ Kernel
          </button>
          {positionOverrides ? (
            <button
              className="btn-sketch"
              onClick={() => rollback()}
              title="Bring cells back close together for editing"
            >
              🔗 Together
            </button>
          ) : (
            <button
              className="btn-sketch violet"
              onClick={() => autoSpace(window.innerHeight)}
              title="Spread cells one-per-slide for presenting"
            >
              📐 Auto-Space [Presentation]
            </button>
          )}
          <button className="btn-sketch pink" onClick={() => setPresenting(!presenting)}>
            {presenting ? "✕ Exit" : "🎬 Present"}
          </button>
        </div>
        <div className="font-hand text-lg ml-1 text-ink/70 dark:text-white/70 select-none flex items-center gap-3 flex-wrap">
          <span>
            Co-AI Developed by{" "}
            <button
              onClick={() => setAboutOpen(true)}
              className="text-[#c2255c] dark:text-[#fcc2d7] underline decoration-wavy underline-offset-2 hover:opacity-80"
            >
              Kader Mohideen
            </button>
          </span>
          <span className="text-ink/40 dark:text-white/40">·</span>
          <span>{notebook.name}</span>
          <span className="text-ink/40 dark:text-white/40">·</span>
          <span>{savedLabel}</span>
          <span className="text-ink/40 dark:text-white/40">·</span>
          <span className="font-mono text-base">
            {mode === "cursor" ? "Cursor tool (V)" : mode === "hand" ? "Hand tool (H)" : "Move tool (M)"}
          </span>
        </div>
      </div>
      <div className="flex gap-2 pointer-events-auto">
        <DesignPicker />
        <button
          className="btn-sketch violet"
          onClick={toggleTheme}
          title={theme === "dark" ? "Switch to light mode" : "Switch to dark mode"}
        >
          {theme === "dark" ? "☀ Light" : "🌙 Dark"}
        </button>
        <button className="btn-sketch sky" onClick={() => setAboutOpen(true)}>
          ⓘ About
        </button>
      </div>
      {installing && (
        <div className="fixed bottom-4 left-4 z-40 pointer-events-auto bg-white dark:bg-[#1f2228] border-2 border-ink dark:border-white/70 rounded-xl px-3 py-2 font-hand text-lg shadow-sketch">
          📦 installing {installing.packages}…
        </div>
      )}
    </div>
  );
}
