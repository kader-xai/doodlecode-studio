import { useEffect, useRef, useState } from "react";
import { useStore } from "../store";

/**
 * "+ Add" dropdown — replaces the long row of + Code / + Text /
 * + Image / + Video / + Browser / + Whiteboard / + Diagram buttons
 * with one compact menu.
 */
export function AddMenu() {
  const ref = useRef<HTMLDivElement>(null);
  const [open, setOpen] = useState(false);

  const addCell = useStore((s) => s.addCell);
  const addMediaCell = useStore((s) => s.addMediaCell);
  const addBrowserCell = useStore((s) => s.addBrowserCell);
  const addWhiteboardCell = useStore((s) => s.addWhiteboardCell);
  const addDiagramCell = useStore((s) => s.addDiagramCell);

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

  const close = () => setOpen(false);
  const onAddImage = () => {
    close();
    const url = window.prompt("Image URL (e.g. /demo/chart.png or https://…)");
    if (url && url.trim()) addMediaCell(url.trim(), "image");
  };
  const onAddVideo = () => {
    close();
    const url = window.prompt("Video / GIF URL (.mp4, .webm, .gif…)");
    if (url && url.trim()) addMediaCell(url.trim(), "video");
  };
  const onAddBrowser = () => {
    close();
    const url = window.prompt(
      "URL to embed (any web app that allows iframes; localhost works)",
      "http://localhost:3000"
    );
    addBrowserCell(url ?? undefined);
  };

  const items: { label: string; subtitle: string; onClick: () => void }[] = [
    { label: "＋ Code",       subtitle: "Python + side callout",              onClick: () => { close(); addCell(undefined, "code"); } },
    { label: "＋ Text",       subtitle: "Markdown slide",                     onClick: () => { close(); addCell(undefined, "markdown"); } },
    { label: "＋ Image",      subtitle: "Frameless full-bleed image",         onClick: onAddImage },
    { label: "＋ Video",      subtitle: "Auto-playing video / GIF",           onClick: onAddVideo },
    { label: "＋ Browser",    subtitle: "Iframe with URL bar",                onClick: onAddBrowser },
    { label: "＋ Whiteboard", subtitle: "Pen / shapes / stickers",            onClick: () => { close(); addWhiteboardCell(); } },
    { label: "＋ Diagram",    subtitle: "Mermaid / Math / Chart",             onClick: () => { close(); addDiagramCell("mermaid"); } },
  ];

  return (
    <div ref={ref} className="relative">
      <button
        className="btn-sketch mint"
        onClick={() => setOpen((v) => !v)}
        title="Add a new cell"
      >
        ＋ Add ▾
      </button>
      {open && (
        <div className="absolute top-12 left-0 z-50 w-64 bg-white dark:bg-[#1f2228] text-ink dark:text-white border-2 border-ink dark:border-white rounded-2xl shadow-sketch p-1.5">
          {items.map((it) => (
            <button
              key={it.label}
              type="button"
              onClick={it.onClick}
              className="w-full text-left px-3 py-1.5 rounded-lg hover:bg-marker-yellow dark:hover:bg-amber-700/60"
            >
              <div className="font-hand text-lg leading-tight">{it.label}</div>
              <div className="text-xs font-mono text-ink/60 dark:text-white/60">{it.subtitle}</div>
            </button>
          ))}
        </div>
      )}
    </div>
  );
}
