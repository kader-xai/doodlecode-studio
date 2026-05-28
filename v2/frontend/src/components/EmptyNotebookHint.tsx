import { fetchDemo } from "../api";
import { useStore } from "../store";
import { DoodleBorder } from "./DoodleBorder";

/**
 * Friendly bottom-right pill shown when the notebook has zero cells.
 * Disappears the moment any cell is added (or the demo is loaded).
 * Stays out of the way otherwise — never blocks the canvas.
 */
export function EmptyNotebookHint() {
  const empty = useStore((s) => s.cells.length === 0);
  const addCell = useStore((s) => s.addCell);
  const addMarkdownCell = useStore((s) => s.addMarkdownCell);
  const loadFromText = useStore((s) => s.loadNotebookFromText);
  const setNotebookName = useStore((s) => s.setNotebookName);

  if (!empty) return null;

  const onDemo = async () => {
    try {
      const text = await fetchDemo();
      await loadFromText(text);
      setNotebookName("v2-tour");
    } catch (err) {
      window.alert(`Could not load demo: ${err}`);
    }
  };

  return (
    <div className="fixed right-5 bottom-5 z-30 max-w-sm pointer-events-auto">
      <div className="relative p-4">
        <DoodleBorder
          stroke="var(--doodle-stroke, #2a2a2a)"
          fill="#fff8e1"
          strokeWidth={3}
          radius={16}
        />
        <div className="relative">
          <div className="font-hand text-2xl text-ink">Empty notebook</div>
          <p className="font-hand text-base text-ink/80 mt-1 mb-3">
            Add a cell from the toolbar, or take the guided tour.
          </p>
          <div className="flex gap-2 flex-wrap">
            <button
              onClick={onDemo}
              className="font-hand text-base px-3 py-0.5 rounded-lg border-2 border-ink bg-marker-pink text-ink shadow-sketch hover:translate-y-[1px] transition"
            >
              🎁 Load demo tour
            </button>
            <button
              onClick={() => addCell()}
              className="font-hand text-base px-3 py-0.5 rounded-lg border-2 border-ink bg-marker-sky text-ink shadow-sketch hover:translate-y-[1px] transition"
            >
              ＋ Code cell
            </button>
            <button
              onClick={() => addMarkdownCell()}
              className="font-hand text-base px-3 py-0.5 rounded-lg border-2 border-ink bg-marker-yellow text-ink shadow-sketch hover:translate-y-[1px] transition"
            >
              ＋ Text cell
            </button>
          </div>
        </div>
      </div>
    </div>
  );
}
