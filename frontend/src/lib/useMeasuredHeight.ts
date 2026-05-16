import { RefObject, useLayoutEffect, useState } from "react";

/**
 * Returns the actual rendered height of `ref.current`, kept in sync
 * via two mechanisms:
 *
 *  1. `useLayoutEffect` — runs synchronously after every commit, BEFORE
 *     the browser paints. Catches the post-render size on first render
 *     and on every prop/content change with no visible flicker.
 *  2. `ResizeObserver` — catches everything that mutates AFTER paint:
 *     web-font load, image load, parent-driven layout shifts,
 *     ResizeHandle drags, etc.
 *
 * A 2 px dead-band prevents sub-pixel feedback loops.
 *
 * Used by every node whose doodle border has to track content height
 * exactly (MarkdownNode, ExplanationNode).
 */
export function useMeasuredHeight(
  ref: RefObject<HTMLElement | null>,
  initial = 60,
  minHeight = 50
): number {
  const [h, setH] = useState<number>(initial);

  // Synchronous measure on every commit. Cheap (one getBoundingClientRect
  // per render) and guarded by the dead-band so it doesn't loop.
  useLayoutEffect(() => {
    const el = ref.current;
    if (!el) return;
    const next = Math.max(minHeight, Math.ceil(el.getBoundingClientRect().height));
    setH((prev) => (Math.abs(prev - next) < 2 ? prev : next));
  });

  // Async observer for post-paint size changes (fonts, images, drags).
  useLayoutEffect(() => {
    const el = ref.current;
    if (!el) return;
    const ro = new ResizeObserver(() => {
      const next = Math.max(minHeight, Math.ceil(el.getBoundingClientRect().height));
      setH((prev) => (Math.abs(prev - next) < 2 ? prev : next));
    });
    ro.observe(el);
    return () => ro.disconnect();
  }, [ref, minHeight]);

  return h;
}
