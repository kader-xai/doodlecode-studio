import { useEffect, useRef, useState } from "react";
import { useStore } from "../store";

/**
 * Iter 237: a single "➕ Add ▾" dropdown that gathers every cell-type
 * adder (Code / Text / Media / Browser / Draw / Diagram / Animate) so the
 * toolbar isn't a wall of seven ＋ buttons. Each item dispatches the same
 * store action the old buttons did; the keyboard shortcuts (N / T / M / W
 * / D / G) still work independently.
 */
export function AddMenu() {
  const addCell = useStore((s) => s.addCell);
  const addMarkdownCell = useStore((s) => s.addMarkdownCell);
  const addMediaCell = useStore((s) => s.addMediaCell);
  const addBrowserCell = useStore((s) => s.addBrowserCell);
  const addWhiteboardCell = useStore((s) => s.addWhiteboardCell);
  const addDiagramCell = useStore((s) => s.addDiagramCell);
  const addAnimationCell = useStore((s) => s.addAnimationCell);

  const [open, setOpen] = useState(false);
  const wrapRef = useRef<HTMLDivElement>(null);

  useEffect(() => {
    if (!open) return;
    const onDocDown = (e: MouseEvent) => {
      if (wrapRef.current && !wrapRef.current.contains(e.target as Node)) setOpen(false);
    };
    window.addEventListener("mousedown", onDocDown);
    return () => window.removeEventListener("mousedown", onDocDown);
  }, [open]);

  const run = (fn: () => void) => {
    fn();
    setOpen(false);
  };

  const promptMedia = () => {
    const url = window.prompt(
      "Image or video URL\n(.png, .jpg, .gif, .mp4, .webm, .mov, YouTube, Vimeo…)",
      "",
    );
    if (url != null && url.trim()) addMediaCell(url);
  };
  const promptBrowser = () => {
    const url = window.prompt("Website URL", "https://example.com");
    if (url != null && url.trim()) addBrowserCell(url);
  };

  return (
    <div className="relative" ref={wrapRef}>
      <button
        onClick={() => setOpen((v) => !v)}
        className="font-hand text-xl px-3 py-0.5 rounded-lg border-2 border-ink dark:border-white/70 bg-marker-sky dark:bg-[#1864ab] text-ink dark:text-white shadow-sketch hover:translate-y-[1px] transition"
        title="Add a cell"
      >
        ➕ Add ▾
      </button>

      {open && (
        <div
          className="absolute left-0 top-full mt-1 min-w-[210px] rounded-xl border-2 border-ink dark:border-white/60 bg-white dark:bg-[#262a31] shadow-sketch overflow-hidden z-[60]"
          role="menu"
        >
          <Item label="🐍  Code" hint="N" onClick={() => run(() => addCell())} />
          <Item label="📝  Text / markdown" hint="T" onClick={() => run(() => addMarkdownCell())} />
          <Item label="🖼  Image / video…" hint="M" onClick={() => run(promptMedia)} />
          <Item label="🌐  Browser (live site)…" hint="W" onClick={() => run(promptBrowser)} />
          <Item label="✏️  Whiteboard" hint="D" onClick={() => run(() => addWhiteboardCell())} />
          <Item label="🧭  Diagram / chart" hint="G" onClick={() => run(() => addDiagramCell())} />
          <Item label="🎞  Animation" onClick={() => run(() => addAnimationCell())} />
        </div>
      )}
    </div>
  );
}

function Item({ label, hint, onClick }: { label: string; hint?: string; onClick: () => void }) {
  return (
    <button
      onClick={onClick}
      role="menuitem"
      className="w-full flex items-center justify-between gap-4 px-3 py-2 text-left font-hand text-lg text-ink dark:text-white hover:bg-marker-yellow/40 dark:hover:bg-amber-700/30 transition"
    >
      <span>{label}</span>
      {hint && (
        <kbd className="font-mono text-xs px-1.5 py-0.5 rounded border border-ink/30 dark:border-white/30 text-ink/60 dark:text-white/60">
          {hint}
        </kbd>
      )}
    </button>
  );
}
