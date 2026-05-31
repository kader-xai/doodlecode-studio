/**
 * Iter 176: accessible focus management for modal dialogs.
 *
 * `useFocusTrap(active, ref)`:
 *   - on open, focuses the first focusable element inside the dialog
 *     (unless something inside is already focused, e.g. an autoFocus
 *     input),
 *   - keeps Tab / Shift+Tab cycling *within* the dialog, and
 *   - on close, restores focus to whatever was focused before it opened
 *     (the trigger).
 *
 * The wrap math is split into the pure `nextTrapTarget` so it can be
 * unit-tested without a DOM.
 */
import { useEffect, useRef } from "react";

export const FOCUSABLE_SELECTOR =
  'a[href], button:not([disabled]), textarea:not([disabled]), ' +
  'input:not([disabled]), select:not([disabled]), [tabindex]:not([tabindex="-1"])';

/**
 * Given the focusable count, the index of the currently-focused element
 * (or -1 if focus is outside the dialog), and whether Shift is held,
 * return the index to move focus to — or -1 when the browser's native
 * Tab order already keeps focus inside (no intervention needed).
 */
export function nextTrapTarget(
  count: number,
  activeIndex: number,
  shift: boolean,
): number {
  if (count === 0) return -1;
  const last = count - 1;
  if (shift) {
    // Shift+Tab off the first element (or from outside) wraps to last.
    return activeIndex <= 0 ? last : -1;
  }
  // Tab off the last element (or from outside) wraps to first.
  return activeIndex === -1 || activeIndex >= last ? 0 : -1;
}

function focusableEls(root: HTMLElement): HTMLElement[] {
  return Array.from(
    root.querySelectorAll<HTMLElement>(FOCUSABLE_SELECTOR),
  ).filter((el) => el.offsetParent !== null || el === document.activeElement);
}

export function useFocusTrap(
  active: boolean,
  ref: React.RefObject<HTMLElement>,
): void {
  const prevFocus = useRef<HTMLElement | null>(null);
  useEffect(() => {
    const root = ref.current;
    if (!active || !root) return;

    prevFocus.current = document.activeElement as HTMLElement | null;
    // Respect a pre-focused field (autoFocus); otherwise focus the first.
    if (!root.contains(document.activeElement)) {
      focusableEls(root)[0]?.focus();
    }

    const onKey = (e: KeyboardEvent) => {
      if (e.key !== "Tab") return;
      const els = focusableEls(root);
      const idx = els.indexOf(document.activeElement as HTMLElement);
      const target = nextTrapTarget(els.length, idx, e.shiftKey);
      if (target >= 0) {
        e.preventDefault();
        els[target].focus();
      }
    };
    root.addEventListener("keydown", onKey);

    return () => {
      root.removeEventListener("keydown", onKey);
      // Restore focus to the trigger so keyboard users aren't dumped at
      // the top of the page.
      prevFocus.current?.focus?.();
    };
  }, [active, ref]);
}
