import { useEffect, useRef, useState } from "react";
import type { CalloutBlock, CellMeta } from "../types";
import { useStore } from "../store";
import { PALETTE } from "../lib/rough";

const COLORS = ["mint", "sky", "yellow", "pink", "peach", "lavender", "rose", "cyan", "violet"] as const;

const POPOVER_W = 400;
const POPOVER_H_GUESS = 540;
const MARGIN = 12;

type Block = CalloutBlock;

function metaToBlocks(meta: CellMeta | null | undefined): Block[] {
  if (!meta) return [{ color: "sky" }];
  const primary: Block = {
    title: meta.title,
    explain: meta.explain,
    color: meta.color,
    kind: meta.kind,
    image: meta.image,
    tags: meta.tags ?? [],
  };
  return [primary, ...(meta.callouts ?? [])];
}

function blocksToMeta(blocks: Block[]): CellMeta | null {
  const cleaned = blocks
    .map((b) => ({
      title: b.title?.trim() || undefined,
      explain: b.explain?.trim() || undefined,
      color: b.color || undefined,
      kind: b.kind?.trim() || undefined,
      image: b.image || undefined,
      tags: b.tags ?? [],
    }))
    .filter((b) => b.title || b.explain || b.image);
  if (cleaned.length === 0) return null;
  const [first, ...rest] = cleaned;
  return {
    title: first.title,
    explain: first.explain,
    color: first.color,
    kind: first.kind,
    image: first.image,
    tags: first.tags,
    callouts: rest,
  };
}

function clamp(n: number, lo: number, hi: number) {
  return Math.max(lo, Math.min(hi, n));
}

/**
 * Positions itself to the LEFT of the cell card by default, with the
 * top-left of the popover aligned to the top of the cell. If the cell
 * is near the left edge of the viewport the popover flips to the right
 * of the cell instead — either way it stays fully on-screen and the
 * user can drag the title bar to move it.
 */
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
  if (x < MARGIN) x = r.right + MARGIN; // flip to right if no room on left
  x = clamp(x, MARGIN, vw - POPOVER_W - MARGIN);
  const y = clamp(r.top, MARGIN, vh - POPOVER_H_GUESS - MARGIN);
  return { x, y };
}

export function CalloutEditor({
  cellId,
  meta,
  onClose,
}: {
  cellId: string;
  meta: CellMeta | null | undefined;
  onClose: () => void;
}) {
  const update = useStore((s) => s.updateCellMeta);
  const [blocks, setBlocks] = useState<Block[]>(metaToBlocks(meta));
  const [active, setActive] = useState(0);
  const fileRef = useRef<HTMLInputElement>(null);

  const rootRef = useRef<HTMLDivElement>(null);
  const [pos, setPos] = useState<{ x: number; y: number } | null>(null);

  // Compute initial position once, relative to the cell that opened us.
  useEffect(() => {
    const anchor =
      rootRef.current?.closest(`[data-cell-id="${cellId}"]`) as HTMLElement | null;
    setPos(computeInitialPosition(anchor));
  }, [cellId]);

  // Re-clamp on window resize so it never escapes the viewport.
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

  // Drag the popover by its header bar.
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

  const current = blocks[active] ?? { color: "sky" };
  const patch = (p: Partial<Block>) =>
    setBlocks((bs) => bs.map((b, i) => (i === active ? { ...b, ...p } : b)));

  const addBlock = () => {
    setBlocks((bs) => [...bs, { color: "peach", title: "", explain: "" }]);
    setActive(blocks.length);
  };

  const removeBlock = () => {
    if (blocks.length <= 1) {
      setBlocks([{ color: "sky" }]);
      setActive(0);
      return;
    }
    setBlocks((bs) => bs.filter((_, i) => i !== active));
    setActive((a) => Math.max(0, a - 1));
  };

  const save = () => {
    update(cellId, blocksToMeta(blocks));
    onClose();
  };

  const clearAll = () => {
    update(cellId, null);
    onClose();
  };

  const onPickImage = async (e: React.ChangeEvent<HTMLInputElement>) => {
    const f = e.target.files?.[0];
    if (!f) return;
    if (f.size > 1.5 * 1024 * 1024) {
      alert("Image is over 1.5 MB — embedding will bloat the .py file. Pick smaller.");
      e.currentTarget.value = "";
      return;
    }
    const reader = new FileReader();
    reader.onload = () => patch({ image: String(reader.result) });
    reader.readAsDataURL(f);
    e.currentTarget.value = "";
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
        {/* Draggable title bar */}
        <div
          onMouseDown={startDrag}
          className="flex items-center justify-between px-3 py-1.5 bg-marker-yellow dark:bg-amber-700 border-b-2 border-ink dark:border-white/70 cursor-move select-none"
          title="Drag to move"
        >
          <div className="text-xl">✎ Edit callout</div>
          <div className="flex items-center gap-2 text-base text-ink/70 dark:text-white/80">
            <span>{active + 1} / {blocks.length}</span>
            <button
              className="ml-2 px-1.5 rounded border border-ink/60 dark:border-white/60 hover:bg-white/40 dark:hover:bg-black/30"
              onClick={(e) => {
                e.stopPropagation();
                onClose();
              }}
              title="Close"
            >
              ✕
            </button>
          </div>
        </div>

        {/* Scrollable body so it can't overflow off the page */}
        <div className="p-3 max-h-[80vh] overflow-auto scrollbar-none">
          {/* Tabs */}
          <div className="flex gap-1 flex-wrap mb-2">
            {blocks.map((b, i) => (
              <button
                key={i}
                className={`px-2 py-0.5 rounded-md border-2 text-base ${
                  i === active
                    ? "border-ink dark:border-white"
                    : "border-ink/30 dark:border-white/30"
                }`}
                style={{ background: PALETTE[b.color || "sky"] ?? "#eee" }}
                onClick={() => setActive(i)}
              >
                #{i + 1}
              </button>
            ))}
            <button
              className="px-2 py-0.5 rounded-md border-2 border-dashed border-ink/50 dark:border-white/50 text-base"
              onClick={addBlock}
            >
              ＋ add
            </button>
          </div>

          <label className="block text-lg mt-1">Title</label>
          <input
            className="w-full border-2 border-ink/70 dark:border-white/40 rounded px-2 py-1 text-base font-mono bg-white dark:bg-[#0f1115]"
            value={current.title ?? ""}
            onChange={(e) => patch({ title: e.target.value })}
            placeholder="What this section is about"
          />

          <label className="block text-lg mt-2">Explanation</label>
          <textarea
            className="w-full border-2 border-ink/70 dark:border-white/40 rounded px-2 py-1 text-base font-mono h-24 bg-white dark:bg-[#0f1115]"
            value={current.explain ?? ""}
            onChange={(e) => patch({ explain: e.target.value })}
            placeholder="What does this code do? Why does it matter?"
          />

          <label className="block text-lg mt-2">Image (optional)</label>
          <div className="flex items-center gap-2">
            <button
              className="btn-sketch sky text-base px-2 py-0.5"
              onClick={() => fileRef.current?.click()}
            >
              🖼 Choose…
            </button>
            {current.image ? (
              <>
                <img src={current.image} alt="preview" className="h-10 rounded border border-ink/60" />
                <button
                  className="btn-sketch pink text-base px-2 py-0.5"
                  onClick={() => patch({ image: undefined })}
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

          <label className="block text-lg mt-2">Section kind (optional)</label>
          <input
            className="w-full border-2 border-ink/70 dark:border-white/40 rounded px-2 py-1 text-base font-mono bg-white dark:bg-[#0f1115]"
            value={current.kind ?? ""}
            onChange={(e) => patch({ kind: e.target.value })}
            placeholder="e.g. data, model, loss, loop"
          />

          <label className="block text-lg mt-2">Color</label>
          <div className="flex gap-1.5 flex-wrap">
            {COLORS.map((c) => (
              <button
                key={c}
                onClick={() => patch({ color: c })}
                className={`w-9 h-9 rounded-lg border-2 ${
                  current.color === c
                    ? "border-ink dark:border-white"
                    : "border-ink/30 dark:border-white/30"
                } transition`}
                style={{ background: PALETTE[c] }}
                title={c}
              />
            ))}
          </div>

          <div className="flex justify-between mt-3">
            <div className="flex gap-2">
              <button className="btn-sketch pink" onClick={removeBlock} title="Remove this callout">
                🗑 Callout
              </button>
              <button className="btn-sketch pink" onClick={clearAll} title="Remove ALL callouts">
                Clear all
              </button>
            </div>
            <div className="flex gap-2">
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
    </div>
  );
}
