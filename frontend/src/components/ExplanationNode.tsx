import { Handle, Position, NodeProps } from "reactflow";
import { DoodleBorder } from "./DoodleBorder";
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
  const lines = Math.max(3, Math.ceil((data.body?.length ?? 0) / 32));
  const imgH = data.image ? 140 : 0;
  const h = 70 + lines * 20 + imgH;
  const textCls = dark ? "text-white" : "text-ink";
  const subCls = dark ? "text-white/90" : "text-ink/85";
  return (
    <div style={{ width: W, position: "relative" }}>
      <Handle type="target" position={Position.Left} />
      <div className="doodle-card" style={{ minHeight: h, background: "transparent" }}>
        <DoodleBorder
          width={W + 8}
          height={h + 8}
          fill={fill}
          stroke={dark ? "#ececec" : "#2a2a2a"}
        />
        <div className="relative">
          <div className={`font-hand text-xl leading-tight ${textCls}`}>{data.title}</div>
          {data.body && (
            <div className={`font-hand text-lg mt-1 leading-snug whitespace-pre-wrap ${subCls}`}>
              {data.body}
            </div>
          )}
          {data.image && (
            <img
              src={data.image}
              alt={data.title}
              className="mt-2 rounded-lg border-2 border-ink/70 dark:border-white/60 max-h-32 w-full object-contain bg-white/40"
            />
          )}
        </div>
      </div>
      <Handle type="source" position={Position.Right} />
    </div>
  );
}
