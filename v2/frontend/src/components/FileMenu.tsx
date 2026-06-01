import { useEffect, useRef, useState } from "react";
import { exportMarkdown, fetchDemo, saveNotebook } from "../api";
import { useStore } from "../store";

/** Feature-detect the File System Access API. Available in Chrome,
 *  Edge, Opera. Missing in Safari and Firefox — those fall through
 *  to the legacy <input type=file> + download path. */
const HAS_FS_ACCESS =
  typeof window !== "undefined" &&
  typeof (window as unknown as { showOpenFilePicker?: unknown }).showOpenFilePicker === "function";

/**
 * File menu — New / Open / Save / Rename.
 *
 * "Open" uses a hidden `<input type=file>` so we don't have to fight
 * with browser file pickers. "Save" downloads a .py via Blob URL.
 * Both are dispatched through store actions, so there's exactly one
 * place that mutates the notebook.
 */
export function FileMenu() {
  const [open, setOpen] = useState(false);
  const fileInputRef = useRef<HTMLInputElement>(null);
  const wrapRef = useRef<HTMLDivElement>(null);

  const newNotebook = useStore((s) => s.newNotebook);
  const loadNotebookFromText = useStore((s) => s.loadNotebookFromText);
  const downloadNotebook = useStore((s) => s.downloadNotebook);
  const notebookName = useStore((s) => s.notebookName);
  const setNotebookName = useStore((s) => s.setNotebookName);
  const fileHandle = useStore((s) => s.fileHandle);
  const setFileHandle = useStore((s) => s.setFileHandle);

  // Close the dropdown when clicking outside.
  useEffect(() => {
    if (!open) return;
    const onDocClick = (e: MouseEvent) => {
      if (!wrapRef.current?.contains(e.target as Node)) setOpen(false);
    };
    window.addEventListener("mousedown", onDocClick);
    return () => window.removeEventListener("mousedown", onDocClick);
  }, [open]);

  const onNew = () => {
    if (window.confirm("Discard the current notebook and start fresh?")) {
      newNotebook();
      setFileHandle(null);
    }
    setOpen(false);
  };

  const onOpen = async () => {
    setOpen(false);
    if (HAS_FS_ACCESS) {
      try {
        const [handle] = await (window as unknown as {
          showOpenFilePicker: (opts: unknown) => Promise<FileSystemFileHandle[]>;
        }).showOpenFilePicker({
          types: [{ description: "DoodleCode .py", accept: { "text/x-python": [".py"] } }],
          multiple: false,
        });
        const f = await handle.getFile();
        const text = await f.text();
        await loadNotebookFromText(text);
        setNotebookName(f.name.replace(/\.py$/i, ""));
        setFileHandle(handle);
        return;
      } catch (err) {
        // AbortError when user cancels — silently swallow.
        if ((err as { name?: string }).name !== "AbortError") {
          window.alert(`Could not open the file: ${err}`);
        }
        return;
      }
    }
    // Legacy path.
    fileInputRef.current?.click();
  };

  const onFile = async (e: React.ChangeEvent<HTMLInputElement>) => {
    const f = e.target.files?.[0];
    e.target.value = ""; // reset so the same file can be re-picked
    if (!f) return;
    try {
      const text = await f.text();
      await loadNotebookFromText(text);
      setNotebookName(f.name.replace(/\.py$/i, ""));
      // Browser file picker doesn't give us a write handle — clear
      // any prior binding so Save falls back to download.
      setFileHandle(null);
    } catch (err) {
      window.alert(`Could not open the file: ${err}`);
    }
  };

  const onSave = async () => {
    try {
      await downloadNotebook();
    } catch (err) {
      window.alert(`Save failed: ${err}`);
    }
    setOpen(false);
  };

  /** "Save As…" — always prompt for a new disk location (or fall
   *  back to download in unsupported browsers). */
  const onSaveAs = async () => {
    setOpen(false);
    const safe = (notebookName || "Untitled").replace(/[^A-Za-z0-9_-]+/g, "_");
    if (HAS_FS_ACCESS) {
      try {
        const handle = await (window as unknown as {
          showSaveFilePicker: (opts: unknown) => Promise<FileSystemFileHandle>;
        }).showSaveFilePicker({
          suggestedName: `${safe}.py`,
          types: [{ description: "DoodleCode .py", accept: { "text/x-python": [".py"] } }],
        });
        const s = useStore.getState();
        const r = await saveNotebook({ name: s.notebookName, cells: s.cells });
        const w = await handle.createWritable();
        await w.write(r.text);
        await w.close();
        setFileHandle(handle);
        // Update notebook name to match the picked filename.
        setNotebookName(handle.name.replace(/\.py$/i, ""));
        return;
      } catch (err) {
        if ((err as { name?: string }).name === "AbortError") return;
        window.alert(`Save As failed: ${err}`);
        return;
      }
    }
    // Legacy browsers: just trigger download.
    await onSave();
  };

  /** "Export Markdown" — render the deck to a shareable .md handout. */
  const onExportMd = async () => {
    setOpen(false);
    try {
      const s = useStore.getState();
      const { text } = await exportMarkdown({ name: s.notebookName, cells: s.cells });
      const safe = (s.notebookName || "Untitled").replace(/[^A-Za-z0-9_-]+/g, "_");
      const url = URL.createObjectURL(new Blob([text], { type: "text/markdown" }));
      const a = document.createElement("a");
      a.href = url;
      a.download = `${safe}.md`;
      a.click();
      URL.revokeObjectURL(url);
    } catch (err) {
      window.alert(`Export Markdown failed: ${err}`);
    }
  };

  const onRename = () => {
    const next = window.prompt("Notebook name", notebookName);
    if (next != null && next.trim()) setNotebookName(next.trim());
    setOpen(false);
  };

  const onLoadDemo = async () => {
    setOpen(false);
    if (!window.confirm("Replace the current notebook with the demo tour?")) return;
    try {
      const text = await fetchDemo();
      await loadNotebookFromText(text);
      setNotebookName("v2-tour");
    } catch (err) {
      window.alert(`Could not load demo: ${err}`);
    }
  };

  return (
    <div className="relative" ref={wrapRef}>
      <button
        onClick={() => setOpen((v) => !v)}
        className="font-hand text-xl px-3 py-0.5 rounded-lg border-2 border-ink dark:border-white/70 bg-marker-peach dark:bg-[#9a4f10] text-ink dark:text-white shadow-sketch hover:translate-y-[1px] transition"
        title="File: New / Open / Save / Rename"
      >
        🗂 File ▾
      </button>

      <input
        ref={fileInputRef}
        type="file"
        accept=".py,text/x-python"
        className="hidden"
        onChange={onFile}
      />

      {open && (
        <div
          className="absolute left-0 top-full mt-1 min-w-[200px] rounded-xl border-2 border-ink dark:border-white/60 bg-white dark:bg-[#262a31] shadow-sketch overflow-hidden"
          role="menu"
        >
          <MenuItem label="🆕  New notebook" onClick={onNew} />
          <MenuItem label="📂  Open .py…" onClick={onOpen} />
          <MenuItem
            label={fileHandle ? "💾  Save  (⌘S)" : "💾  Save / download  (⌘S)"}
            onClick={onSave}
            hint={fileHandle ? fileHandle.name : undefined}
          />
          <MenuItem label="💾  Save As…" onClick={onSaveAs} />
          <MenuItem label="📝  Export Markdown…" onClick={onExportMd} hint=".md handout" />
          <div className="border-t-2 border-ink/20 dark:border-white/20" />
          <MenuItem label="🎁  Load demo tour" onClick={onLoadDemo} />
          <div className="border-t-2 border-ink/20 dark:border-white/20" />
          <MenuItem label="✏️  Rename…" onClick={onRename} hint={notebookName} />
        </div>
      )}
    </div>
  );
}

function MenuItem({ label, hint, onClick }: { label: string; hint?: string; onClick: () => void }) {
  return (
    <button
      onClick={onClick}
      className="w-full px-3 py-1.5 font-hand text-lg text-left text-ink dark:text-white hover:bg-marker-yellow/40 dark:hover:bg-[#3a3f47] flex items-baseline justify-between gap-3"
      role="menuitem"
    >
      <span>{label}</span>
      {hint && <span className="font-mono text-xs text-ink/60 dark:text-white/60 truncate max-w-[120px]">{hint}</span>}
    </button>
  );
}
