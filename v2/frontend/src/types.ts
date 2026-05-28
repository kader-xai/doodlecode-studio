/** Types shared between the store, components, and the API layer. */

export type OutputType = "stdout" | "stderr" | "error" | "done" | "image_png";

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
