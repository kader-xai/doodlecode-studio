import { Handle, Position, NodeProps } from "reactflow";
import { colorFor } from "../lib/rough";
import { useStore } from "../store";

const W = 320;

export function ExplanationNode({
  data,
}: NodeProps<{
  title: string;
  body: string;
  kind: string;
  color?: string;
  image?: string;
}>) {
  const dark = useStore((s) => s.theme === "dark");
  const fill = colorFor({ color: data.color, kind: data.kind, dark });
  const textCls = dark ? "text-white" : "text-ink";
  const subCls = dark ? "text-white/90" : "text-ink/85";

  // No need to manage SVG sizing here — DoodleBorder measures its own
  // parent via ResizeObserver and rebuilds the wavy outline whenever
  // the card resizes. The colored CSS background covers the card so
  // text always sits on the section color even mid-resize.

  return (
    <div style={{ width: W, position: "relative" }}>
      <Handle type="target" position={Position.Left} />
      <div
        className="doodle-card relative"
        style={{
          minHeight: 80,
          background: fill,
          borderRadius: 18,
        }}
      >
        <div className="relative">
          <div
            className={`font-hand text-xl leading-tight ${textCls} break-words`}
            style={{ overflowWrap: "anywhere" }}
          >
            {data.title}
          </div>
          {data.body && (
            <div
              className={`font-hand text-lg mt-1 leading-snug whitespace-pre-wrap break-words ${subCls}`}
              style={{ overflowWrap: "anywhere" }}
            >
              {data.body}
            </div>
          )}
          {data.image && (
            <img
              src={data.image}
              alt={data.title}
              className="mt-2 rounded-lg border-2 border-ink/70 dark:border-white/60 max-w-full object-contain bg-white/40"
            />
          )}
        </div>
      </div>
      <Handle type="source" position={Position.Right} />
    </div>
  );
}
