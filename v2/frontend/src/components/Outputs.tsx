import type { CellOutput, ExecuteResponse } from "../types";

/** Renders the stdout/stderr/error/image stream below a code cell. */
export function Outputs({ result }: { result?: ExecuteResponse }) {
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
  return (
    <div className="rounded-lg border-2 border-ink/40 dark:border-white/30 bg-white dark:bg-[#262a31] overflow-hidden">
      <div className="px-2 py-0.5 text-xs font-mono border-b-2 border-ink/20 dark:border-white/20 text-ink/70 dark:text-white/70 flex items-center justify-between">
        <span>↳ output</span>
        <span>{result.status} · {result.elapsed_ms} ms</span>
      </div>
      <div className="p-2 space-y-1">
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
  return (
    <pre
      className={`${cls} font-mono text-sm whitespace-pre-wrap break-words m-0`}
    >
      {output.text}
    </pre>
  );
}
