/** Types shared between the store, components, and the API layer. */

export type OutputType = "stdout" | "stderr" | "error" | "done" | "image_png";

/**
 * Iter 98: app version. CLAUDE rule 29 — kept in lockstep with
 * `backend/app/__init__.py:__version__` and `frontend/package.json`.
 * Surfaced in the help overlay so users can tell what they're on
 * without opening the source.
 */
export const APP_VERSION = "2.6.0";

export interface CellOutput {
  type: OutputType;
  text: string;
}

export interface ExecuteResponse {
  status: "ok" | "error" | "timeout";
  elapsed_ms: number;
  outputs: CellOutput[];
}

export type CellKind = "code" | "markdown" | "media" | "browser" | "whiteboard" | "diagram";

export interface Cell {
  id: string;
  kind: CellKind;
  source: string;
  title?: string;
  /** Canvas coordinates (set by drag in iter 3). */
  x: number;
  y: number;
  /** Optional explicit size; undefined → cell-type default. */
  w?: number;
  h?: number;
  /** "mermaid" | "math" | "doodle" — only set when kind === "diagram". */
  diagram_kind?: string;
  /** Legacy single callout. Loaded from old files; rewritten into
   *  `callouts[0]` on first interaction. Don't read this directly. */
  explain?: string;
  /** Zero or more speech bubbles, rendered top-to-bottom beside the cell. */
  callouts?: Callout[];
  /** Iter 45: outgoing cell→cell links. Each entry is the target
   *  cell's id. Rendered as solid sketchy lines by ConnectionsLayer
   *  (distinct from the dashed callout chains). Survives round-trip
   *  through the .py file via `# @link_to:` directives. */
  links?: string[];
  /** Iter 53: when true the cell collapses to just its title strip;
   *  the editor/output panel is hidden. UI-only for now — the field
   *  is in the store (and therefore the localStorage autosave) but
   *  isn't yet serialized into the .py file. */
  collapsed?: boolean;
  /** Iter 165: presenter-only speaker note. Shown in the bottom-left
   *  HUD during presentation; never on the slide itself. Any cell
   *  kind. Round-trips as a `# @note:` directive. */
  note?: string;
  /** Iter 154: ordered "reveal" code fragments (code cells only).
   *  `source` is the pristine base shown at step 0. Each Reveal press
   *  appends the next fragment below the current code (build-up), so
   *  the displayed/run code = source + revealed steps. The steps are
   *  authored ahead of time in the Reveal Steps editor and round-trip
   *  as `# @reveal:` blocks. The number currently revealed is the
   *  ephemeral `revealStep` in the store — it is NOT persisted and
   *  resets to 0 on load. */
  reveals?: string[];
}

export interface Callout {
  text: string;
  /** Optional image — data URL or remote URL. Embedded in the bubble. */
  image?: string;
}

export interface CellRuntime {
  running: boolean;
  result?: ExecuteResponse;
  /** Iter 37: monotonic execution counter assigned the moment a run
   *  completes — like Jupyter's `In [n]`. Reset to 0 on ↻ Kernel. */
  execCount?: number;
}
