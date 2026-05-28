import { useEffect, useMemo, useRef, useState } from "react";
import { DoodleBorder } from "./DoodleBorder";
import { useStore } from "../store";

/**
 * Iter 62: Cmd/Ctrl+K palette. Lists every cell by title (with kind
 * emoji), filters as the user types, and on pick:
 *   - selects the cell
 *   - bumps `panToTick` so Canvas pans the viewport to it
 *
 * Keyboard:
 *   - ↑ / ↓ move the highlight, Enter picks, Esc closes.
 *   - Type to filter (case-insensitive substring on the visible title).
 */
/**
 * Iter 64: pull a short, readable first-line out of a cell body.
 * Stripping leading markdown markers (`#`, `-`, `*`) and Python
 * comment `#` keeps the preview informative on common cells.
 */
function firstLine(source: string, kind: string): string {
  for (const raw of source.split("\n")) {
    const t = raw.trim();
    if (!t) continue;
    let s = t;
    if (kind === "markdown") {
      s = s.replace(/^#+\s*/, "").replace(/^[-*]\s+/, "");
    } else if (kind === "code") {
      // Strip a comment marker so "# header" becomes "header".
      s = s.replace(/^#\s*/, "");
    }
    return s.length > 60 ? s.slice(0, 57) + "…" : s;
  }
  return "";
}

const KIND_ICON: Record<string, string> = {
  code: "🐍",
  markdown: "📝",
  media: "🖼",
  browser: "🌐",
  whiteboard: "✏️",
  diagram: "🧭",
};

export function CellPalette() {
  const open = useStore((s) => s.paletteOpen);
  const close = useStore((s) => () => s.setPaletteOpen(false));
  const cells = useStore((s) => s.cells);
  const panToCell = useStore((s) => s.panToCell);

  const [q, setQ] = useState("");
  const [idx, setIdx] = useState(0);
  const inputRef = useRef<HTMLInputElement | null>(null);

  // Reset on each open + focus the input.
  useEffect(() => {
    if (open) {
      setQ("");
      setIdx(0);
      // Defer one frame so the input mounts first.
      const t = setTimeout(() => inputRef.current?.focus(), 0);
      return () => clearTimeout(t);
    }
  }, [open]);

  const matches = useMemo(() => {
    const needle = q.trim().toLowerCase();
    const list = cells.map((c, i) => {
      const hasTitle = !!c.title?.trim();
      return {
        cell: c,
        label: hasTitle ? c.title!.trim() : `(untitled ${c.kind} #${i + 1})`,
        // Iter 64: when there's no title, surface the first non-
        // blank line of the source as a dim preview line so the
        // user has SOMETHING to recognize. Skip when titled (the
        // title already conveys the cell's purpose).
        preview: hasTitle ? "" : firstLine(c.source ?? "", c.kind),
      };
    });
    if (!needle) return list;
    // Iter 63: also match against the cell's source so the user can
    // jump to a code cell by typing a variable name, or a markdown
    // cell by a phrase inside it. Title still wins ties because we
    // check it first.
    return list.filter((m) => {
      if (m.label.toLowerCase().includes(needle)) return true;
      const body = (m.cell.source ?? "").toLowerCase();
      return body.includes(needle);
    });
  }, [cells, q]);

  // Clamp the highlight to the filtered list.
  useEffect(() => {
    if (idx >= matches.length) setIdx(Math.max(0, matches.length - 1));
  }, [matches, idx]);

  if (!open) return null;

  const pick = (id: string) => {
    panToCell(id);
    close();
  };

  return (
    <div
      className="fixed inset-0 z-[120] bg-black/40 backdrop-blur-sm flex items-start justify-center p-6 pt-24"
      onClick={close}
    >
      <div
        className="relative w-full max-w-md"
        onClick={(e) => e.stopPropagation()}
      >
        <DoodleBorder
          stroke="var(--doodle-stroke, #2a2a2a)"
          fill="var(--doodle-help-fill, #fff8e1)"
          strokeWidth={3}
          radius={18}
        />
        <div className="relative p-3">
          <input
            ref={inputRef}
            type="text"
            value={q}
            onChange={(e) => { setQ(e.target.value); setIdx(0); }}
            onKeyDown={(e) => {
              if (e.key === "Escape") { e.preventDefault(); close(); return; }
              if (e.key === "ArrowDown") {
                e.preventDefault();
                setIdx((i) => Math.min(matches.length - 1, i + 1));
                return;
              }
              if (e.key === "ArrowUp") {
                e.preventDefault();
                setIdx((i) => Math.max(0, i - 1));
                return;
              }
              if (e.key === "Enter") {
                e.preventDefault();
                const sel = matches[idx];
                if (sel) pick(sel.cell.id);
                return;
              }
            }}
            placeholder="Jump to cell — match title or body…"
            spellCheck={false}
            className="w-full px-2 py-1 font-hand text-lg rounded-md border-2 border-ink/40 dark:border-white/30 bg-white/90 dark:bg-[#1a1d23] text-ink dark:text-white outline-none focus:border-[#c2255c]"
          />
          <ul className="mt-2 max-h-72 overflow-auto scrollbar-none">
            {matches.length === 0 && (
              <li className="font-hand text-base text-ink/60 dark:text-white/60 px-2 py-1">
                No matching cells.
              </li>
            )}
            {matches.map((m, i) => (
              <li
                key={m.cell.id}
                onClick={() => pick(m.cell.id)}
                onMouseEnter={() => setIdx(i)}
                className={
                  "font-hand text-base px-2 py-1 rounded-md cursor-pointer flex items-start gap-2 " +
                  (i === idx
                    ? "bg-marker-yellow/70 dark:bg-amber-700/60 text-ink dark:text-white"
                    : "text-ink/80 dark:text-white/80 hover:bg-white/50 dark:hover:bg-black/30")
                }
              >
                <span className="text-lg leading-none mt-[2px]">{KIND_ICON[m.cell.kind] ?? "•"}</span>
                <div className="flex-1 min-w-0">
                  <div className="truncate">{m.label}</div>
                  {m.preview && (
                    <div className="font-mono text-xs truncate text-ink/45 dark:text-white/45">
                      {m.preview}
                    </div>
                  )}
                </div>
                {m.cell.collapsed && (
                  <span className="font-mono text-xs text-ink/40 dark:text-white/40 mt-[2px]">collapsed</span>
                )}
              </li>
            ))}
          </ul>
          <p className="mt-2 font-hand text-sm text-ink/50 dark:text-white/50 px-2">
            ↑↓ pick · Enter jumps · Esc closes
          </p>
        </div>
      </div>
    </div>
  );
}
