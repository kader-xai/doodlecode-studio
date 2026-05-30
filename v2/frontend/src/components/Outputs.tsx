import { useEffect, useRef, useState } from "react";
import type { CellOutput, ExecuteResponse } from "../types";

/**
 * Iter 161: the output panel used to auto-grow without bound, so a
 * cell that printed thousands of lines made the card stretch off the
 * canvas with no way to scroll (the user's "scrolling indefinitely"
 * bug). Output is the documented exception to CLAUDE rule 18: it caps
 * at MAX_OUTPUT_H and becomes its own scroll region (with `nowheel` so
 * the wheel scrolls the output, not the ReactFlow canvas). When it
 * overflows, ↑ Top / ↓ End jump buttons appear in the header.
 */
const MAX_OUTPUT_H = 360; // px — panel caps here, then scrolls
/** Guard against a single multi-MB string freezing the DOM. */
export const PER_ITEM_CHAR_CAP = 100_000;

/** Pure, testable: clamp text to the cap, reporting how much was cut. */
export function clampText(
  text: string,
  cap: number = PER_ITEM_CHAR_CAP,
): { shown: string; truncated: number } {
  if (text.length <= cap) return { shown: text, truncated: 0 };
  return { shown: text.slice(0, cap), truncated: text.length - cap };
}

/** Renders the stdout/stderr/error/image stream below a code cell. */
export function Outputs({ result }: { result?: ExecuteResponse }) {
  const scrollRef = useRef<HTMLDivElement | null>(null);
  const [overflowing, setOverflowing] = useState(false);

  // Recompute overflow whenever the result changes or the panel resizes
  // (images decode asynchronously, so a ResizeObserver is needed).
  useEffect(() => {
    const el = scrollRef.current;
    if (!el) {
      setOverflowing(false);
      return;
    }
    const check = () => setOverflowing(el.scrollHeight - el.clientHeight > 4);
    check();
    const ro = new ResizeObserver(check);
    ro.observe(el);
    return () => ro.disconnect();
  }, [result]);

  if (!result) return null;
  const visible = result.outputs.filter(
    (o) => o.type !== "done" && (o.text.length > 0 || o.type === "image_png"),
  );
  if (!visible.length) {
    return (
      <div className="font-mono text-xs text-ink/60 dark:text-white/60 px-2 py-1">
        ↳ {result.status} ({result.elapsed_ms} ms) · no output
      </div>
    );
  }

  const scrollTo = (where: "top" | "end") => {
    const el = scrollRef.current;
    if (!el) return;
    el.scrollTo({ top: where === "top" ? 0 : el.scrollHeight, behavior: "smooth" });
  };

  const jumpBtn =
    "font-mono text-[11px] leading-none px-1.5 py-0.5 rounded border-2 " +
    "border-ink/30 dark:border-white/30 bg-white/70 dark:bg-black/30 " +
    "text-ink/70 dark:text-white/70 hover:bg-marker-yellow/50 dark:hover:bg-amber-700/30 " +
    "transition nodrag";

  return (
    <div className="rounded-lg border-2 border-ink/40 dark:border-white/30 bg-white dark:bg-[#262a31] overflow-hidden">
      <div className="px-2 py-0.5 text-xs font-mono border-b-2 border-ink/20 dark:border-white/20 text-ink/70 dark:text-white/70 flex items-center justify-between gap-2">
        <span className="shrink-0">↳ output</span>
        <div className="flex items-center gap-2 min-w-0">
          {overflowing && (
            <span className="flex gap-1 shrink-0">
              <button type="button" className={jumpBtn} title="Scroll to top"
                onClick={(e) => { e.stopPropagation(); scrollTo("top"); }}
                onPointerDown={(e) => e.stopPropagation()}>
                ↑ Top
              </button>
              <button type="button" className={jumpBtn} title="Scroll to end"
                onClick={(e) => { e.stopPropagation(); scrollTo("end"); }}
                onPointerDown={(e) => e.stopPropagation()}>
                ↓ End
              </button>
            </span>
          )}
          <span className="shrink-0">{result.status} · {result.elapsed_ms} ms</span>
        </div>
      </div>
      <div
        ref={scrollRef}
        className="p-2 space-y-1 overflow-auto nowheel nodrag"
        style={{ maxHeight: MAX_OUTPUT_H }}
      >
        {visible.map((o, i) => (
          <OutputItem key={i} output={o} />
        ))}
      </div>
    </div>
  );
}

function OutputItem({ output }: { output: CellOutput }) {
  if (output.type === "image_png") {
    return (
      <img
        src={`data:image/png;base64,${output.text}`}
        alt="figure"
        className="block max-w-full rounded border-2 border-ink/30 dark:border-white/30 bg-white"
      />
    );
  }
  const cls =
    output.type === "stderr" || output.type === "error"
      ? "text-[#c2255c] dark:text-[#fcc2d7]"
      : "text-ink dark:text-white";
  const { shown, truncated } = clampText(output.text);
  return (
    <>
      <pre className={`${cls} font-mono text-sm whitespace-pre-wrap break-words m-0`}>
        {shown}
      </pre>
      {truncated > 0 && (
        <div className="font-mono text-[11px] text-ink/55 dark:text-white/55 px-1 py-0.5 border-t border-dashed border-ink/20 dark:border-white/20">
          … {truncated.toLocaleString()} more characters truncated for performance.
          Print less, or write the full output to a file.
        </div>
      )}
    </>
  );
}
