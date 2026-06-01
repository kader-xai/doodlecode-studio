import { useEffect, useState } from "react";
import { AmbientLayer } from "./components/AmbientLayer";
import { CalloutEditor } from "./components/CalloutEditor";
import { RevealEditor } from "./components/RevealEditor";
import { NoteEditor } from "./components/NoteEditor";
import { PresenterNotes } from "./components/PresenterNotes";
import { CellPalette } from "./components/CellPalette";
import { Canvas } from "./components/Canvas";
import { EmptyNotebookHint } from "./components/EmptyNotebookHint";
import { InstallModal } from "./components/InstallModal";
import { PresenterBar } from "./components/PresenterBar";
import { PresenterProgress } from "./components/PresenterProgress";
import { PresenterOverlay } from "./components/PresenterOverlay";
import { ShortcutsHelp } from "./components/ShortcutsHelp";
import { Toolbar } from "./components/Toolbar";
import { useStore } from "./store";
import { frameCount } from "./lib/animation";

interface Ping {
  ok: boolean;
  version: string;
  name: string;
}

export function App() {
  const [version, setVersion] = useState<string | null>(null);
  const [helpOpen, setHelpOpen] = useState(false);

  useEffect(() => {
    fetch("/api/ping")
      .then((r) => (r.ok ? r.json() : Promise.reject(r.statusText)))
      .then((p: Ping) => setVersion(p.version))
      .catch(() => setVersion("offline"));
  }, []);

  // Keep the store in sync with native Fullscreen API state. The
  // user can exit fullscreen via Esc / browser chrome — we listen
  // for that and clear the flag accordingly.
  useEffect(() => {
    const onChange = () => {
      useStore.getState().setFullscreen(document.fullscreenElement != null);
    };
    document.addEventListener("fullscreenchange", onChange);
    return () => document.removeEventListener("fullscreenchange", onChange);
  }, []);

  // Global keyboard handler. Mounted on `window` so it fires no
  // matter which inner widget has focus — except inside editable
  // elements (Monaco, inputs, contenteditable) where the raw key
  // should type instead of trigger a shortcut.
  useEffect(() => {
    // Fullscreen toggle helper. The Fullscreen API throws in some
    // browser/policy combinations, so we swallow rejection to keep
    // the ErrorBoundary quiet.
    const toggleFullscreen = () => {
      try {
        if (document.fullscreenElement) {
          const p = document.exitFullscreen?.();
          if (p && typeof p.catch === "function") p.catch(() => {});
        } else {
          const p = document.documentElement.requestFullscreen?.();
          if (p && typeof p.catch === "function") p.catch(() => {});
        }
      } catch { /* ignore */ }
    };

    const onKey = (e: KeyboardEvent) => {
      const tgt = e.target as HTMLElement | null;
      const tag = tgt?.tagName?.toLowerCase();
      const inEditor =
        tag === "input" ||
        tag === "textarea" ||
        tag === "select" ||
        tgt?.isContentEditable;
      // Monaco handles its own keys via its own listener — those events
      // never bubble out to here. So we only have to guard inputs.
      if (inEditor) {
        // Esc + ? still work even inside editable to be helpful.
        if (e.key === "Escape") {
          (tgt as HTMLElement | null)?.blur?.();
        }
        return;
      }

      const state = useStore.getState();
      const sid = state.selectedId;

      // Iter 158: Shift+R reveals the next code step on the active
      // cell — works both in presentation (focused cell) and on the
      // canvas (selected cell). Placed before the presentation
      // "R runs the cell" handler so Shift+R doesn't trigger a run.
      if (e.shiftKey && (e.key === "R" || e.key === "r") && !e.metaKey && !e.ctrlKey && !e.altKey) {
        const target = state.presenting ? state.focusedCellId : sid;
        if (!target) return;
        const cell = state.cells.find((c) => c.id === target);
        if (cell?.kind !== "code" || !(cell.reveals?.length)) return;
        e.preventDefault();
        state.revealNext(target);
        return;
      }

      // Iter 165: N opens the speaker-note editor for the selected cell
      // (any kind). Plain key, no modifiers; skipped while presenting so
      // it doesn't interfere with navigation/ink.
      if (
        (e.key === "n" || e.key === "N") &&
        !e.metaKey && !e.ctrlKey && !e.altKey && !e.shiftKey &&
        !state.presenting
      ) {
        const target = sid ?? state.focusedCellId;
        if (!target) return;
        e.preventDefault();
        state.openNoteEditor(target);
        return;
      }

      if (e.key === "?" || (e.key === "/" && e.shiftKey)) {
        e.preventDefault();
        setHelpOpen((v) => !v);
        return;
      }

      // Cmd/Ctrl+S → Save. Works from anywhere INCLUDING inside text
      // inputs (Monaco intercepts its own ⌘S, that's fine). preventDefault
      // so the browser's "save page" dialog doesn't pop up.
      if ((e.metaKey || e.ctrlKey) && (e.key === "s" || e.key === "S")) {
        e.preventDefault();
        // Iter 84: Shift = Save As (always prompts), no Shift = Save.
        const save = e.shiftKey ? state.saveNotebookAs() : state.downloadNotebook();
        save.catch((err) => window.alert(`Save failed: ${err}`));
        return;
      }

      // Iter 83: Cmd/Ctrl+\ toggles dark/light theme.
      if ((e.metaKey || e.ctrlKey) && e.key === "\\") {
        e.preventDefault();
        state.toggleTheme();
        return;
      }

      // Iter 71: Cmd/Ctrl+/ toggles collapse on the selected cell.
      // No-op without a selection. Works on every cell kind that has
      // a chevron (Code / Markdown / Diagram / Browser / Whiteboard).
      if ((e.metaKey || e.ctrlKey) && e.key === "/") {
        if (!sid) return;
        e.preventDefault();
        state.toggleCollapse(sid);
        return;
      }

      // Iter 57: Cmd/Ctrl+Shift+[ collapses every cell;
      //          Cmd/Ctrl+Shift+] expands every cell.
      if ((e.metaKey || e.ctrlKey) && e.shiftKey && (e.key === "[" || e.key === "{")) {
        e.preventDefault();
        state.setAllCollapsed(true);
        return;
      }
      if ((e.metaKey || e.ctrlKey) && e.shiftKey && (e.key === "]" || e.key === "}")) {
        e.preventDefault();
        state.setAllCollapsed(false);
        return;
      }

      // Iter 38: Cmd/Ctrl+Shift+L — clear every output panel.
      if ((e.metaKey || e.ctrlKey) && e.shiftKey && (e.key === "l" || e.key === "L")) {
        e.preventDefault();
        if (window.confirm("Clear every cell's output?")) state.clearAllOutputs();
        return;
      }

      // Iter 51/91: Shift+Enter OR Cmd/Ctrl+Enter runs the selected
      // code cell. Jupyter has both — Shift advances in real Jupyter,
      // Cmd doesn't — but we don't auto-advance so they're the same
      // thing. Accepting both matches what muscle memory expects.
      if (
        e.key === "Enter" &&
        !e.altKey &&
        ((e.shiftKey && !e.metaKey && !e.ctrlKey) ||
          ((e.metaKey || e.ctrlKey) && !e.shiftKey))
      ) {
        if (!sid) return;
        const cell = state.cells.find((c) => c.id === sid);
        if (cell?.kind !== "code") return;
        e.preventDefault();
        state.runCell(sid);
        return;
      }

      // Iter 36: Cmd/Ctrl+Shift+Enter — run every code cell sequentially.
      if ((e.metaKey || e.ctrlKey) && e.shiftKey && e.key === "Enter") {
        e.preventDefault();
        state.runAllCells().then((failed) => {
          if (failed) {
            const t =
              useStore.getState().cells.find((c) => c.id === failed)?.title ?? failed;
            window.alert(`Run All stopped at "${t}" — see its output for the error.`);
          }
        });
        return;
      }

      // Iter 62: Cmd/Ctrl+K — open the cell palette (filter & jump).
      if ((e.metaKey || e.ctrlKey) && (e.key === "k" || e.key === "K")) {
        e.preventDefault();
        state.setPaletteOpen(!state.paletteOpen);
        return;
      }

      // Iter 34: Cmd/Ctrl+A — select every cell on the canvas.
      if ((e.metaKey || e.ctrlKey) && (e.key === "a" || e.key === "A")) {
        e.preventDefault();
        state.setSelectedIds(state.cells.map((c) => c.id));
        return;
      }

      // Iter 34: arrow keys nudge the selected group (10px, Shift = 50px).
      if (
        (e.key === "ArrowLeft" ||
          e.key === "ArrowRight" ||
          e.key === "ArrowUp" ||
          e.key === "ArrowDown") &&
        !state.presenting &&
        !e.metaKey &&
        !e.ctrlKey &&
        !e.altKey
      ) {
        const ids = state.selectedIds.length ? state.selectedIds : sid ? [sid] : [];
        if (!ids.length) return;
        e.preventDefault();
        const step = e.shiftKey ? 50 : 10;
        const dx =
          e.key === "ArrowLeft" ? -step : e.key === "ArrowRight" ? step : 0;
        const dy = e.key === "ArrowUp" ? -step : e.key === "ArrowDown" ? step : 0;
        const idSet = new Set(ids);
        for (const c of state.cells) {
          if (idSet.has(c.id)) state.moveCell(c.id, c.x + dx, c.y + dy);
        }
        return;
      }

      // ── Presentation shortcuts ───────────────────────────────
      if (e.key === "F5" || (e.shiftKey && (e.key === "P" || e.key === "p"))) {
        e.preventDefault();
        state.setPresenting(!state.presenting);
        return;
      }
      if (state.presenting) {
        if (
          e.key === "ArrowRight" ||
          e.key === "PageDown" ||
          e.key === " "
        ) {
          e.preventDefault();
          // Iter 226: on an animation cell, Space/→ steps through the
          // frames in place (with a transition) before advancing to the
          // next slide — the in-slide build the user asked for.
          const fid = state.focusedCellId;
          const fcell = fid ? state.cells.find((c) => c.id === fid) : null;
          if (fcell?.kind === "animation") {
            const total = frameCount(fcell.source);
            const cur = state.revealStep[fid!] ?? 0;
            if (cur < total - 1) {
              state.revealNext(fid!);
              return;
            }
          }
          state.nextCell();
          return;
        }
        if (e.key === "ArrowLeft" || e.key === "PageUp") {
          e.preventDefault();
          state.prevCell();
          return;
        }
        if (e.key === "Home") { e.preventDefault(); state.focusCell(state.cellsInOrder()[0]?.id ?? null); return; }
        if (e.key === "End") {
          e.preventDefault();
          const ord = state.cellsInOrder();
          state.focusCell(ord[ord.length - 1]?.id ?? null);
          return;
        }
        // Digit 1-9 jumps straight to that slide (no modifiers).
        if (/^[1-9]$/.test(e.key) && !e.metaKey && !e.ctrlKey && !e.altKey) {
          e.preventDefault();
          state.goToSlide(Number(e.key) - 1);
          return;
        }
        // Presenter ink tools. Toggle off if the same tool was active.
        if (e.key === "p" || e.key === "P") {
          e.preventDefault();
          state.setPresenterTool(state.presenterTool === "pen" ? "none" : "pen");
          return;
        }
        if (e.key === "h" || e.key === "H") {
          e.preventDefault();
          state.setPresenterTool(state.presenterTool === "highlighter" ? "none" : "highlighter");
          return;
        }
        if (e.key === "x" || e.key === "X") {
          e.preventDefault();
          state.setPresenterTool(state.presenterTool === "fixedPen" ? "none" : "fixedPen");
          return;
        }
        if (e.key === "e" || e.key === "E") {
          e.preventDefault();
          state.clearPresenterInk();
          return;
        }
        if (e.key === "f" || e.key === "F") {
          e.preventDefault();
          toggleFullscreen();
          return;
        }
        if (e.key === "r" || e.key === "R") {
          // Live demo helper: run the focused code cell.
          const fid = state.focusedCellId;
          if (!fid) return;
          const cell = state.cells.find((c) => c.id === fid);
          if (cell?.kind !== "code") return;
          e.preventDefault();
          state.runCell(fid);
          return;
        }
      }

      if (e.key === "Escape") {
        if (state.presenting && state.presenterTool !== "none") {
          // First Esc only deactivates the pen; user has to press
          // Esc again to actually leave the presentation.
          state.setPresenterTool("none");
        } else if (state.presenting) {
          state.setPresenting(false);
        } else if (state.interactiveBrowserId) {
          state.setInteractiveBrowser(null);
          (document.activeElement as HTMLElement | null)?.blur?.();
        } else if (helpOpen) {
          setHelpOpen(false);
        } else if (state.paletteOpen) {
          // Iter 123: belt-and-braces — the palette's own input
          // handles Esc when focused, but if focus drifts (user
          // moused outside the input) the App-level fallback fires.
          state.setPaletteOpen(false);
        } else if (sid) {
          state.setSelected(null);
        }
        return;
      }
      if (e.key === "b" || e.key === "B") {
        if (e.metaKey || e.ctrlKey) return;
        // Toggle interact mode on the currently selected browser cell.
        if (!sid) return;
        const cell = state.cells.find((c) => c.id === sid);
        if (cell?.kind !== "browser") return;
        e.preventDefault();
        state.setInteractiveBrowser(state.interactiveBrowserId === sid ? null : sid);
        return;
      }
      if (e.key === "w" || e.key === "W") {
        if (e.metaKey || e.ctrlKey) return; // let browser handle Cmd+W
        e.preventDefault();
        const url = window.prompt("Website URL", "https://example.com");
        if (url != null && url.trim()) state.addBrowserCell(url);
        return;
      }
      if (e.key === "d" || e.key === "D") {
        // Cmd/Ctrl+D is duplicate (handled above). Plain D adds a whiteboard.
        if (e.metaKey || e.ctrlKey) return;
        e.preventDefault();
        state.addWhiteboardCell();
        return;
      }
      if (e.key === "g" || e.key === "G") {
        if (e.metaKey || e.ctrlKey) return;
        e.preventDefault();
        state.addDiagramCell();
        return;
      }
      // Tool-mode shortcuts (V/H). Skip Cmd/Ctrl variants.
      if (!e.metaKey && !e.ctrlKey) {
        if (e.key === "v" || e.key === "V") { e.preventDefault(); state.setInteractionMode("select"); return; }
        // H is also used for highlighter ink later; that handler will
        // run first when presenting because it checks `presenting`.
        if (e.key === "h" || e.key === "H") { e.preventDefault(); state.setInteractionMode("hand"); return; }
      }
      // S toggles Space / Together (auto-arrange).
      if ((e.key === "s" || e.key === "S") && !e.metaKey && !e.ctrlKey) {
        e.preventDefault();
        if (state.originalPositions) state.rollbackLayout();
        else state.spaceForPresentation();
        return;
      }
      if (e.key === "c" || e.key === "C") {
        // Cmd/Ctrl+C = copy; we never override the OS shortcut.
        if (e.metaKey || e.ctrlKey) return;
        if (!sid) return;
        e.preventDefault();
        state.openCalloutEditor(sid);
        return;
      }
      if (e.key === "Backspace" || e.key === "Delete") {
        // Iter 33: when the user has multi-selected, delete the
        // whole group in one shot. Fall back to single-cell delete
        // when only the primary is selected.
        const ids = state.selectedIds.length ? state.selectedIds : sid ? [sid] : [];
        if (!ids.length) return;
        e.preventDefault();
        if (ids.length === 1) {
          const title = state.cells.find((c) => c.id === ids[0])?.title ?? ids[0];
          if (window.confirm(`Delete "${title}"?`)) state.deleteCell(ids[0]);
        } else {
          if (window.confirm(`Delete ${ids.length} cells?`)) state.deleteCells(ids);
        }
        return;
      }
      if (e.key === "F2") {
        if (!sid) return;
        e.preventDefault();
        state.requestRename(sid);
        return;
      }
      if ((e.key === "d" || e.key === "D") && (e.metaKey || e.ctrlKey)) {
        // Iter 34: duplicate the entire group when multi-selected.
        const ids = state.selectedIds.length ? state.selectedIds : sid ? [sid] : [];
        if (!ids.length) return;
        e.preventDefault();
        const newIds: string[] = [];
        for (const id of ids) {
          const dup = state.duplicateCell(id);
          if (dup) newIds.push(dup);
        }
        if (newIds.length) useStore.getState().setSelectedIds(newIds);
        return;
      }
      if (e.key === "n" || e.key === "N") {
        if (e.metaKey || e.ctrlKey) return; // let browser handle Cmd+N
        e.preventDefault();
        state.addCell();
        return;
      }
      if (e.key === "t" || e.key === "T") {
        if (e.metaKey || e.ctrlKey) return;
        e.preventDefault();
        state.addMarkdownCell();
        return;
      }
      if (e.key === "m" || e.key === "M") {
        if (e.metaKey || e.ctrlKey) return;
        e.preventDefault();
        const url = window.prompt("Image or video URL", "");
        if (url != null && url.trim()) state.addMediaCell(url);
        return;
      }
      if (e.key === "Tab") {
        e.preventDefault();
        const cells = state.cells;
        if (!cells.length) return;
        const idx = cells.findIndex((c) => c.id === sid);
        // Iter 121: from null selection, Tab → first, Shift+Tab → last.
        const next =
          idx < 0
            ? (e.shiftKey ? cells[cells.length - 1] : cells[0])
            : cells[(idx + (e.shiftKey ? -1 : 1) + cells.length) % cells.length];
        state.setSelected(next.id);
        return;
      }
    };
    window.addEventListener("keydown", onKey);
    return () => window.removeEventListener("keydown", onKey);
  }, [helpOpen]);

  return (
    <div className="h-screen w-screen overflow-hidden bg-sandal dark:bg-[#1a1d23] text-ink dark:text-white">
      <AmbientLayer />
      <Toolbar version={version} onHelp={() => setHelpOpen(true)} />
      <main className="absolute inset-0">
        <Canvas />
      </main>
      <EmptyNotebookHint />

      {helpOpen && <ShortcutsHelp onClose={() => setHelpOpen(false)} />}
      <CellPalette />
      <CalloutEditor />
      <RevealEditor />
      <NoteEditor />
      <InstallModal />
      <PresenterBar />
      <PresenterProgress />
      <PresenterNotes />
      <PresenterOverlay />

      <style>{`
        :root { --doodle-stroke: #2a2a2a; }
        html.dark { --doodle-stroke: #f0f0f0; }
        html.dark .react-flow__controls-button {
          background: rgba(38, 42, 49, 0.9) !important;
          color: #fff !important;
          border-color: rgba(255, 255, 255, 0.3) !important;
        }
        html.dark .react-flow__controls-button:hover {
          background: rgba(55, 60, 68, 0.95) !important;
        }
      `}</style>
    </div>
  );
}
