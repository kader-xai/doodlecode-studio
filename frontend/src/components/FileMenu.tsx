import { useEffect, useRef, useState } from "react";
import { exportNotebook, uploadNotebook } from "../api";
import { useStore } from "../store";

/**
 * File operations dropdown — replaces the loose "📄 New / 📂 Open /
 * 💾 Save" toolbar buttons with a single compact menu.
 */
export function FileMenu() {
  const fileRef = useRef<HTMLInputElement>(null);
  const ref = useRef<HTMLDivElement>(null);
  const [open, setOpen] = useState(false);

  const setNotebook = useStore((s) => s.setNotebook);
  const newNotebook = useStore((s) => s.newNotebook);
  const notebook = useStore((s) => s.notebook);

  useEffect(() => {
    if (!open) return;
    const onDown = (e: MouseEvent) => {
      if (!ref.current?.contains(e.target as Node)) setOpen(false);
    };
    const onKey = (e: KeyboardEvent) => { if (e.key === "Escape") setOpen(false); };
    window.addEventListener("mousedown", onDown);
    window.addEventListener("keydown", onKey);
    return () => {
      window.removeEventListener("mousedown", onDown);
      window.removeEventListener("keydown", onKey);
    };
  }, [open]);

  const onNew = () => {
    setOpen(false);
    const name = window.prompt(
      "Name for the new file (e.g. lesson_intro.py):",
      "untitled.py"
    );
    if (!name || !name.trim()) return;
    newNotebook(name);
  };

  const onOpenPick = () => {
    setOpen(false);
    fileRef.current?.click();
  };

  const onUpload = async (f: File) => {
    const nb = await uploadNotebook(f);
    nb.name = f.name;
    setNotebook(nb);
  };

  const onSave = async () => {
    setOpen(false);
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

  return (
    <div ref={ref} className="relative">
      <button
        className="btn-sketch sky"
        onClick={() => setOpen((v) => !v)}
        title="File operations"
      >
        📁 File ▾
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
      {open && (
        <div className="absolute top-12 left-0 z-50 w-52 bg-white dark:bg-[#1f2228] text-ink dark:text-white border-2 border-ink dark:border-white rounded-2xl shadow-sketch p-1.5">
          <button
            type="button"
            onClick={onNew}
            className="w-full text-left px-3 py-2 rounded-lg font-hand text-lg hover:bg-marker-yellow dark:hover:bg-amber-700/60"
          >
            📄 New notebook
          </button>
          <button
            type="button"
            onClick={onOpenPick}
            className="w-full text-left px-3 py-2 rounded-lg font-hand text-lg hover:bg-marker-yellow dark:hover:bg-amber-700/60"
          >
            📂 Open…
          </button>
          <button
            type="button"
            onClick={onSave}
            className="w-full text-left px-3 py-2 rounded-lg font-hand text-lg hover:bg-marker-yellow dark:hover:bg-amber-700/60"
          >
            💾 Save (download .py)
          </button>
        </div>
      )}
    </div>
  );
}
