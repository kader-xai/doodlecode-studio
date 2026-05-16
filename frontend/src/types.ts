/** Bumped manually on user-visible changes. Mirrors backend/app/__init__.py. */
export const APP_VERSION = "1.3.2";

/** File-format level. Bump on schema changes. */
export const FILE_FORMAT_VERSION = 2;

export type CalloutBlock = {
  title?: string;
  explain?: string;
  color?: string;
  kind?: string;
  image?: string;
  tags?: string[];
};

export type CellMeta = {
  kind?: string;
  color?: string;
  title?: string;
  explain?: string;
  tags?: string[];
  /** Primary callout's bubble image. */
  image?: string;
  callouts?: CalloutBlock[];
  /** Image rendered INSIDE the text cell's body (📝 Edit owns this). */
  box_image?: string;
};

export type Cell = {
  id: string;
  kind: "code" | "markdown";
  source: string;
  meta?: CellMeta | null;
};

export type Notebook = {
  name: string;
  cells: Cell[];
  format_version?: number;
};

export type ExecuteOutput =
  | { type: "stream"; name?: "stdout" | "stderr"; text?: string }
  | { type: "result"; data?: Record<string, string> }
  | { type: "display"; data?: Record<string, string> }
  | { type: "error"; ename?: string; evalue?: string; traceback?: string[] };

export type ExecuteResponse = {
  outputs: ExecuteOutput[];
  status: "ok" | "error" | "aborted";
  execution_count?: number;
};

export type CodeBlock = {
  id: string;
  start_line: number;
  end_line: number;
  kind: string;
  name?: string;
  summary: string;
};

export type Explanation = {
  block_id: string;
  title: string;
  body: string;
  tags: string[];
  color?: string;
  image?: string;
};

export type ExplainResponse = {
  blocks: CodeBlock[];
  explanations: Explanation[];
};
