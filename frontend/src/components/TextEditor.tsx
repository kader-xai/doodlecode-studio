import { useEffect, useRef, useState } from "react";
import type { CellMeta } from "../types";
import { useStore } from "../store";
import { PALETTE } from "../lib/rough";

const COLORS = [
  "sky",
  "mint",
  "yellow",
  "pink",
  "peach",
  "lavender",
  "rose",
  "cyan",
  "violet",
  "paper",
] as const;

const POPOVER_W = 460;
const POPOVER_H_GUESS = 560;
const MARGIN = 12;

function clamp(n: number, lo: number, hi: number) {
  return Math.max(lo, Math.min(hi, n));
}

function computeInitialPosition(anchor: HTMLElement | null) {
  const vw = window.innerWidth;
  const vh = window.innerHeight;
  if (!anchor) {
    return {
      x: clamp(MARGIN, MARGIN, vw - POPOVER_W - MARGIN),
      y: clamp(80, MARGIN, vh - POPOVER_H_GUESS - MARGIN),
    };
  }
  const r = anchor.getBoundingClientRect();
  let x = r.left - POPOVER_W - MARGIN;
  if (x < MARGIN) x = r.right + MARGIN;
  x = clamp(x, MARGIN, vw - POPOVER_W - MARGIN);
  const y = clamp(r.top, MARGIN, vh - POPOVER_H_GUESS - MARGIN);
  return { x, y };
}

/**
 * Edits a presentation/text cell: title bar, color, body text, optional
 * inline image. Draggable, viewport-clamped.
 */
export function TextEditor({
  cellId,
  source,
  meta,
  onClose,
}: {
  cellId: string;
  source: string;
  meta: CellMeta | null | undefined;
  onClose: () => void;
}) {
  const updateSource = useStore((s) => s.updateCellSource);
  const updateMeta = useStore((s) => s.updateCellMeta);

  const [title, setTitle] = useState(meta?.title ?? "");
  const [color, setColor] = useState(meta?.color ?? "sky");
  // Use the cell-body image, NOT the callout bubble image. They live in
  // separate fields so editing one never bleeds into the other.
  const [image, setImage] = useState<string | undefined>(meta?.box_image);
  const [body, setBody] = useState(source);

  const rootRef = useRef<HTMLDivElement>(null);
  const fileRef = useRef<HTMLInputElement>(null);
  const [pos, setPos] = useState<{ x: number; y: number } | null>(null);

  useEffect(() => {
    const anchor =
      rootRef.current?.closest(`[data-cell-id="${cellId}"]`) as HTMLElement | null;
    setPos(computeInitialPosition(anchor));
  }, [cellId]);

  useEffect(() => {
    const onResize = () =>
      setPos((p) =>
        p
          ? {
              x: clamp(p.x, MARGIN, window.innerWidth - POPOVER_W - MARGIN),
              y: clamp(p.y, MARGIN, window.innerHeight - POPOVER_H_GUESS - MARGIN),
            }
          : p
      );
    window.addEventListener("resize", onResize);
    return () => window.removeEventListener("resize", onResize);
  }, []);

  const startDrag = (e: React.MouseEvent) => {
    if (!pos) return;
    e.preventDefault();
    e.stopPropagation();
    const startX = e.clientX;
    const startY = e.clientY;
    const origin = { ...pos };
    const move = (ev: MouseEvent) => {
      const x = clamp(
        origin.x + (ev.clientX - startX),
        MARGIN,
        window.innerWidth - POPOVER_W - MARGIN
      );
      const y = clamp(
        origin.y + (ev.clientY - startY),
        MARGIN,
        window.innerHeight - POPOVER_H_GUESS - MARGIN
      );
      setPos({ x, y });
    };
    const up = () => {
      window.removeEventListener("mousemove", move);
      window.removeEventListener("mouseup", up);
    };
    window.addEventListener("mousemove", move);
    window.addEventListener("mouseup", up);
  };

  const onPickImage = (e: React.ChangeEvent<HTMLInputElement>) => {
    const f = e.target.files?.[0];
    if (!f) return;
    if (f.size > 1.5 * 1024 * 1024) {
      alert("Image is over 1.5 MB — embedding will bloat the .py file. Pick smaller.");
      e.currentTarget.value = "";
      return;
    }
    const reader = new FileReader();
    reader.onload = () => setImage(String(reader.result));
    reader.readAsDataURL(f);
    e.currentTarget.value = "";
  };

  const save = () => {
    updateSource(cellId, body);
    // Preserve any callouts already attached; only patch the box-level
    // meta fields (title/color/box_image). `image` stays UNTOUCHED so
    // the callout editor and text editor never overwrite each other.
    const nextMeta: CellMeta = {
      ...(meta ?? {}),
      title: title.trim() || undefined,
      color: color || undefined,
      box_image: image || undefined,
    };
    const hasContent =
      nextMeta.title ||
      nextMeta.color ||
      nextMeta.box_image ||
      nextMeta.image ||
      nextMeta.explain ||
      (nextMeta.callouts && nextMeta.callouts.length > 0);
    updateMeta(cellId, hasContent ? nextMeta : null);
    onClose();
  };

  return (
    <div
      ref={rootRef}
      className="nodrag nowheel font-hand"
      style={{
        position: "fixed",
        left: pos?.x ?? -9999,
        top: pos?.y ?? -9999,
        width: POPOVER_W,
        zIndex: 60,
        opacity: pos ? 1 : 0,
        transition: "opacity 120ms",
      }}
      onClick={(e) => e.stopPropagation()}
      onMouseDown={(e) => e.stopPropagation()}
    >
      <div className="bg-white dark:bg-[#1f2228] border-2 border-ink dark:border-white/70 rounded-2xl shadow-sketch overflow-hidden">
        <div
          onMouseDown={startDrag}
          className="flex items-center justify-between px-3 py-1.5 bg-marker-yellow dark:bg-amber-700 border-b-2 border-ink dark:border-white/70 cursor-move select-none"
          title="Drag to move"
        >
          <div className="text-xl">📝 Edit text box</div>
          <button
            className="px-1.5 rounded border border-ink/60 dark:border-white/60 hover:bg-white/40 dark:hover:bg-black/30"
            onClick={onClose}
            title="Close"
          >
            ✕
          </button>
        </div>

        <div className="p-3 max-h-[80vh] overflow-auto scrollbar-none">
          <label className="block text-lg">Title (optional)</label>
          <input
            className="w-full border-2 border-ink/70 dark:border-white/40 rounded px-2 py-1 text-base font-mono bg-white dark:bg-[#0f1115]"
            value={title}
            onChange={(e) => setTitle(e.target.value)}
            placeholder="Slide title"
          />

          <label className="block text-lg mt-2">Body (markdown)</label>
          <textarea
            className="w-full border-2 border-ink/70 dark:border-white/40 rounded px-2 py-1 text-base font-mono h-40 bg-white dark:bg-[#0f1115]"
            value={body}
            onChange={(e) => setBody(e.target.value)}
            placeholder={"# Heading\n\nText, **bold**, `inline code`, - bullets."}
          />

          <label className="block text-lg mt-2">Image (optional)</label>
          <div className="flex items-center gap-2">
            <button
              className="btn-sketch sky text-base px-2 py-0.5"
              onClick={() => fileRef.current?.click()}
            >
              🖼 Choose…
            </button>
            {image ? (
              <>
                <img src={image} alt="preview" className="h-10 rounded border border-ink/60" />
                <button
                  className="btn-sketch pink text-base px-2 py-0.5"
                  onClick={() => setImage(undefined)}
                >
                  remove
                </button>
              </>
            ) : (
              <span className="text-base text-ink/60 dark:text-white/60">no image</span>
            )}
            <input
              ref={fileRef}
              type="file"
              accept="image/*"
              className="hidden"
              onChange={onPickImage}
            />
          </div>

          <label className="block text-lg mt-2">Color</label>
          <div className="flex gap-1.5 flex-wrap">
            {COLORS.map((c) => (
              <button
                key={c}
                onClick={() => setColor(c)}
                className={`w-9 h-9 rounded-lg border-2 ${
                  color === c
                    ? "border-ink dark:border-white"
                    : "border-ink/30 dark:border-white/30"
                } transition`}
                style={{ background: PALETTE[c] }}
                title={c}
              />
            ))}
          </div>

          <div className="flex justify-end gap-2 mt-3">
            <button className="btn-sketch sky" onClick={onClose}>
              Cancel
            </button>
            <button className="btn-sketch mint" onClick={save}>
              Save
            </button>
          </div>
        </div>
      </div>
    </div>
  );
}
