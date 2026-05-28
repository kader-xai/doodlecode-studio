# DoodleCode Studio v2 — project rules (CLAUDE.md)

> **Load-bearing.** This file is the canonical contract for any
> contributor (human or AI) editing v2. Rules captured here are the
> ones we've already paid for in bugs. Don't re-learn them.

## Architecture (one-pager)

```
v2/
├─ backend/                       FastAPI on :8001
│  └─ app/
│     ├─ main.py                  routes — /api/{ping,execute,save,open,
│     │                                    kernel/reset,install,proxy,
│     │                                    tools/ppt-to-png,demo}
│     ├─ kernel.py + runner.py    persistent Python child process
│     │                           (JSON-line protocol over stdin/stdout,
│     │                           threading.Lock, timeout reaper)
│     ├─ executor.py              façade in front of the kernel
│     ├─ notebook_io.py           .py serializer + parser (format v3)
│     ├─ models.py                Pydantic — wire types
│     ├─ proxy.py                 X-Frame-bypass + SSRF guard
│     ├─ installer.py             pip install + shell-injection regex
│     └─ tools.py                 PPT → PNG (soffice + pdftoppm)
└─ frontend/                      React 18 + Vite + Zustand + ReactFlow
   └─ src/
      ├─ store.ts                 SINGLE source of truth (cells, theme,
      │                           selection, presenter state, layout
      │                           snapshot, fileHandle, modes, …)
      ├─ App.tsx                  global keyboard, modal mounts, route hint
      ├─ ToolsPage.tsx            standalone /tools route
      ├─ api.ts                   thin fetch wrappers
      ├─ types.ts                 mirrors backend models
      ├─ lib/
      │  ├─ markdown.tsx          tiny zero-dep renderer
      │  └─ doodleDiagram.ts      flow+chart compiler (port of Codex
      │                           prototype, arrows fixed)
      └─ components/              one file per cell type + toolbar
                                  + modals + overlays
```

## Product principles

1. **One `.py` file per notebook.** Everything — code, markdown,
   media URLs, browser URLs, whiteboard strokes (JSON), diagrams,
   callout text, callout images (data URLs), cell positions, cell
   sizes — round-trips through that one file. No sidecar JSON.
2. **Backward compatibility is mandatory.** New file-format fields
   are additive. Old `.py` files always open. `# @explain:` from
   earlier versions auto-migrates to `callouts[0]`.
3. **Outputs live below the editor, never on the right.** The right-
   side bubbles are *user-authored callouts only* — never AI commentary.
4. **One single source of truth.** The Zustand store owns the
   notebook. No component duplicates cell fields into local state.
   When you find yourself wanting `useState` for shared data, add it
   to the store instead.
5. **No `Claude` / `claude` / `Anthropic` references in code, docs,
   or comments.** The execution + install + proxy layers speak in
   generic terms.

## UX rules (paid for in bugs)

6. **Two tool modes, not three.** `select` (V — default, drag moves
   cells, click selects) and `hand` (H — drag pans canvas, cells
   locked). A third "pure cursor" mode was experimented with and
   abandoned — it broke "just grab a card and drag it" intuition.
7. **`nodrag` belongs on interactive children, not the whole row.**
   Cell titles (and tool strips) must be drag handles. Put `nodrag`
   only on the buttons / selectors / inputs inside them. Putting it
   on the wrapping row locks the cell from being dragged.
8. **Cell drag commit reads post-`applyNodeChanges` state.**
   ReactFlow's `dragging:false` event sometimes arrives WITHOUT a
   `position` field. Always read the final position from the freshly-
   applied local node array, never from `ch.position` directly.
9. **`onMouseDown` with `preventDefault()` on commit-buttons in
   editors.** Otherwise the textarea blurs first, fires its own
   commit, the button re-renders as "Edit" via state update, and the
   subsequent click reopens edit mode — the v2 "Done button doesn't
   work" bug.
10. **Local-draft pattern in every text editor.** Bind the textarea
    to a local `draft` state; commit to the store on blur / Esc / ✓.
    Direct binding to `cell.source` causes a Canvas → ReactFlow → node
    re-render storm during typing that blurs the input. Affects
    MarkdownCell, CalloutEditor, DiagramCell, BrowserCell URL bar.
11. **Stable per-cellId `data` objects in Canvas.** ReactFlow re-
    renders the node component when `data` identity changes. Cache one
    `{cellId}` object per id in a ref so prop identity is stable while
    the user types.
12. **Click → select, never reset zoom.** Clicking a cell pans nothing.
    Presentation `setCenter` keeps the user's current zoom.
13. **Presentation centering uses the bounding box (cell + callout
    column).** Cells with no callouts center on cell midpoint; cells
    with callouts include the `CALLOUT_GAP + BUBBLE_W` extra width in
    the box so cell + bubble are balanced together.
14. **Presenter ink lives at z-9999 when active, z-25 idle.** Active
    pen MUST clear iframes / Monaco / react-flow pane (`html.ink-active`
    CSS rule sets `pointer-events: none !important` on them).
    `setPointerCapture` on `e.currentTarget` (the SVG), never on
    `e.target` (children can be non-capturable). `touchAction: none`
    on the SVG so trackpad gestures don't pan/zoom mid-stroke.
15. **First Esc in presentation drops the pen; second Esc exits.**
    Wiping ink shouldn't accidentally exit the talk.
16. **Browser cell interact-mode gate.** Iframes get
    `pointer-events: none` by default behind a "🖱 Click to interact"
    overlay. Only one browser cell is interactive at a time. **B** /
    Esc / the 🚪 Exit pill release.
17. **Whiteboard drawing uses pointer-capture + refs.** Active stroke
    in a `useRef`, paint segments directly to canvas in pointer-move,
    commit ONE stroke to the store on pointer-up. Never call
    `setState` per pointer-move (drops points, kills FPS, blurs other
    widgets).
18. **No internal scrollbars on cells.** Cells auto-grow as content
    grows. Modals use the unobtrusive scrollbar. Monaco's own scroll
    is the one exception (it's a code editor).
19. **OS-default cursor everywhere except `cursor-move` on cell
    titles, `crosshair` while a presenter pen is active, `grab` in
    Hand mode.**
20. **`pip install` shell-injection guard.** Every package token must
    match the regex `^[A-Za-z0-9][...]$` before being passed to pip.
    Plain words like `rm` are fine (pip just looks for a non-existent
    package); the guard exists to block `&&`, `$(...)`, `` ` ``, `;`,
    `|`, `..`, path separators.
21. **`/api/proxy` SSRF guard.** Resolve the hostname and refuse any
    private / loopback / link-local / multicast / reserved / metadata
    address. 8 MB cap, 15 s timeout, GET only, http/https only.
21c. **Cell↔cell links are symmetric.** `linkCells(a, b)` writes the
    link on BOTH endpoints (a.links += b, b.links += a). Same for
    `unlinkCells`. `deleteCell` then prunes the dangling reference
    from every survivor. The visual is a single line drawn once
    (ConnectionsLayer dedupes by sorted-id key); the bidirectional
    storage exists so deletion of either endpoint cleans up — if
    only the outgoing side were tracked we'd leak references on
    delete.

21e. **`selectedId` must always be a member of `selectedIds`, or
    `null`.** Any writer of `selectedIds` (lasso, shift-click, Cmd+A,
    palette pick, deleteCell prune…) must reconcile the primary:
    keep it if still in the new set, fall back to `ids[0]`, set
    `null` when the set is empty. Otherwise the toolbar surfaces
    bound to `selectedId` (Delete, Callout, size presets) keep
    pointing at a cell the user already deselected — visible bug.

21f. **`duplicateCell` drops outgoing links and deep-clones
    callouts.** Spread-cloning a cell carries `links` to the
    duplicate, but the target cells don't know about the new id —
    the link graph goes asymmetric. The spread also shares the
    `callouts` array reference; editing a bubble on the copy would
    mutate the source. Fix: `links: []` and
    `callouts: src.callouts?.map(co => ({...co}))`.

21d. **`DoodleBorder` must render at the parent's real W×H, not a
    100×100 stretched viewBox.** The original implementation used
    `viewBox="0 0 100 100"` + `preserveAspectRatio="none"`, which
    visibly distorted the wobble pattern on non-square cells
    (browsers, media). The current implementation uses a
    `ResizeObserver` to read the parent box and renders the path at
    1:1 inside `viewBox="0 0 W H"`, with anchors resampled along
    each edge every ~64 px so long sides actually wobble. Don't
    revert to the stretched-viewBox approach.

21b. **Never trust ReactFlow's `<EdgeRenderer>` for overlays we
    derive ourselves.** ReactFlow drops edges whose source/target
    nodes don't have measured handle bounds (see `getNodeData`
    in `@reactflow/core`). When `nodes` is driven by local
    `useState` instead of ReactFlow's `setNodes` pipeline, our
    synthetic pseudo-nodes (callouts, future link-edges) never get
    measured and every edge is silently filtered. Use a custom
    SVG layer inside the ReactFlow viewport instead —
    `ConnectionsLayer.tsx` is the reference. Subscribe to
    `useViewport()` so pan + zoom carry the lines.

## Code rules

22. **TypeScript strict mode stays on.** No `any` without a documented
    reason.
23. **Default to no comments.** Comment the *why* of non-obvious code,
    never the *what*.
24. **No new dependencies without a reason.** Each one in
    `package.json` or `requirements.txt` pulls its weight. Justify in
    the PR description.
25. **Components that read the store use selectors, not `getState`** —
    unless you specifically need a side-effect-only read inside a
    handler (e.g. `useStore.getState().deleteCell(id)` from a global
    keyboard handler).
26. **`nodrag nowheel` go on canvas-interactive children** (Monaco
    container, whiteboard `<canvas>`, scrollable output panes).
    Not on rows that should still drag the cell.
27. **Hooks before early returns. ALWAYS.** Conditional returns above
    a `useEffect` cause React error #300 ("rendered fewer hooks").
    Put `if (!cell) return null;` AFTER every hook call.

## Process rules

28. **CI-equivalent must pass before commit**: `cd v2/frontend && npx
    tsc -b --noEmit && npm run build && npm test`, and `cd v2/backend
    && .venv/bin/python -m pytest tests/ -q`.
29. **Versions in lockstep**: `backend/app/__init__.py:__version__`,
    `frontend/package.json:"version"`, AND
    `frontend/src/types.ts:APP_VERSION` are bumped together. The
    third pin (iter 98) is the one surfaced in the help overlay
    footer, so if it drifts the user sees the wrong version.
30. **One logical change per commit.** Refactors live in their own
    commit, separately from feature work.
31. **README + CLAUDE.md updated in the same commit** that changes
    behavior worth documenting.

## Testing discipline (per user directive)

32. **Visual verification with screenshots.** When iterating on UX:
    take a screenshot of the relevant state, confirm visually, attach
    to the PR or session log. Don't claim "works" from a log line
    alone.
33. **DevTools Console check on every UX iteration.** Open the
    browser console after each frontend change. Zero red lines is the
    bar. Yellow warnings get triaged.
34. **End-to-end behavioral test, not just unit.** Don't just test
    that the store action fires — actually click the button via the
    UI driver, observe the result, verify state, refresh the page,
    confirm persistence.
35. **Server-side actions via the harness.** Use `curl` (or the
    backend test harness) to exercise `/api/execute`, `/api/save`,
    `/api/install`, `/api/proxy`, `/api/tools/ppt-to-png` and confirm
    the round-trip — never assume.
36. **Refresh-then-verify for anything autosaved.** After Save (or
    after a long edit session), reload the page and confirm the state
    came back exactly. localStorage autosave + .py round-trip both
    need this check.
37. **Run the dev-tools console assertions** (or the backend tests)
    BEFORE marking an iteration complete. Never close out an
    in-progress task until the green checks are recorded.

## Where rules came from

Most of these were learned by:
- bug → root cause → fix → write down so it doesn't happen again
- a specific user complaint that prompted a paradigm change
  (e.g. "still the boxes are not moving" → simplify tool modes
  from 3 → 2 → which is rule #6)
- v1 post-mortems carried forward to v2 with the underlying invariant
  preserved

When adding a new rule, write the bug or constraint it prevents in
plain English. If you can't, the rule probably isn't real — leave it
out.
