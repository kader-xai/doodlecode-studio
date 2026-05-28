import { DoodleBorder } from "./DoodleBorder";

const ROWS: { keys: string; what: string; when?: string }[] = [
  { keys: "V / H", what: "Select-and-move / Hand-pan tool mode", when: "anywhere" },
  { keys: "F5 / Shift+P", what: "Toggle presentation mode", when: "anywhere" },
  { keys: "S", what: "Toggle Space (one-per-slide) / Together layout", when: "anywhere" },
  { keys: "→ / Space / PageDown", what: "Next slide", when: "presenting" },
  { keys: "← / PageUp", what: "Previous slide", when: "presenting" },
  { keys: "Home / End", what: "First / last slide", when: "presenting" },
  { keys: "P", what: "Pen ink (red, fades ~1.4s)", when: "presenting" },
  { keys: "H", what: "Highlighter ink (yellow, fades ~4s)", when: "presenting" },
  { keys: "X", what: "Fixed pen (red, stays until erased)", when: "presenting" },
  { keys: "E", what: "Erase all presenter ink", when: "presenting" },
  { keys: "F", what: "Toggle fullscreen", when: "presenting" },
  { keys: "R", what: "Run focused code cell", when: "presenting" },
  { keys: "＋ Code / N", what: "Add a new code cell", when: "anywhere" },
  { keys: "＋ Text / T", what: "Add a new text/markdown cell", when: "anywhere" },
  { keys: "＋ Media / M", what: "Add an image/video cell (prompts for URL)", when: "anywhere" },
  { keys: "＋ Browser / W", what: "Add a browser cell (live website)", when: "anywhere" },
  { keys: "＋ Draw / D", what: "Add a whiteboard cell", when: "anywhere" },
  { keys: "＋ Diagram / G", what: "Add a Mermaid diagram cell", when: "anywhere" },
  { keys: "💬 / C", what: "Add or edit a callout on the selected cell", when: "cell selected" },
  { keys: "B", what: "Toggle interact mode for selected browser cell", when: "browser cell selected" },
  { keys: "▶ button", what: "Run focused code cell", when: "anywhere" },
  { keys: "Cmd/Ctrl+Shift+Enter", what: "Run All code cells in order (▶▶)", when: "anywhere" },
  { keys: "Cmd/Ctrl+Shift+L", what: "Clear every cell's output (kernel survives)", when: "anywhere" },
  { keys: "Backspace / Delete", what: "Delete selected cell(s) — works on groups", when: "anywhere" },
  { keys: "F2", what: "Rename the selected cell's title", when: "anywhere" },
  { keys: "Cmd/Ctrl+D", what: "Duplicate selected cell(s) — works on groups", when: "anywhere" },
  { keys: "Cmd/Ctrl+A", what: "Select every cell on the canvas", when: "anywhere" },
  { keys: "Shift / Cmd-click", what: "Add a cell to the current selection", when: "anywhere" },
  { keys: "Drag empty pane", what: "Lasso-select cells (Select mode)", when: "anywhere" },
  { keys: "← ↑ → ↓", what: "Nudge selected cells (10 px; Shift = 50 px)", when: "anywhere" },
  { keys: "Tab / Shift+Tab", what: "Select next / previous cell", when: "anywhere" },
  { keys: "Esc", what: "Deselect / close overlays", when: "anywhere" },
  { keys: "?", what: "Toggle this help overlay", when: "anywhere" },
];

export function ShortcutsHelp({ onClose }: { onClose: () => void }) {
  return (
    <div
      className="fixed inset-0 z-[100] bg-black/40 backdrop-blur-sm flex items-center justify-center p-6"
      onClick={onClose}
    >
      <div
        className="relative p-6 max-w-lg w-full"
        onClick={(e) => e.stopPropagation()}
      >
        <DoodleBorder
          stroke="var(--doodle-stroke, #2a2a2a)"
          fill="var(--doodle-help-fill, #fff8e1)"
          strokeWidth={3}
          radius={18}
        />
        <div className="relative">
          <div className="flex items-center justify-between mb-3">
            <h2 className="font-hand text-3xl">⌨️ Keyboard shortcuts</h2>
            <button
              onClick={onClose}
              className="font-hand text-xl px-2 rounded-md border-2 border-ink dark:border-white/70 hover:translate-y-[1px] transition"
              title="Close (Esc)"
            >
              ✕
            </button>
          </div>
          <table className="w-full font-hand text-lg">
            <tbody>
              {ROWS.map((r, i) => (
                <tr
                  key={i}
                  className={i % 2 === 0 ? "bg-white/40 dark:bg-black/20" : ""}
                >
                  <td className="py-1 px-2 align-top whitespace-nowrap">
                    <code className="font-mono text-sm bg-marker-yellow/60 dark:bg-amber-700/40 px-1.5 py-0.5 rounded border-2 border-ink/30 dark:border-white/30">
                      {r.keys}
                    </code>
                  </td>
                  <td className="py-1 px-2">{r.what}</td>
                </tr>
              ))}
            </tbody>
          </table>
          <p className="font-hand text-base mt-3 text-ink/70 dark:text-white/70">
            Tip — double-click a cell's title to rename it inline. Click an empty
            spot on the canvas (or press Esc) to deselect. With 2+ cells selected
            an Align bar appears in the toolbar for left/center/right/top/middle/
            bottom + distribute-H/V.
          </p>
        </div>
      </div>
      <style>{`
        :root { --doodle-help-fill: #fff8e1; }
        html.dark { --doodle-help-fill: #2a2f37; }
      `}</style>
    </div>
  );
}
