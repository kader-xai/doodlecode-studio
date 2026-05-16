import { Handle, Position, NodeProps } from "reactflow";
import { useMemo } from "react";
import { DoodleBorder } from "./DoodleBorder";
import { colorFor } from "../lib/rough";
import { useStore } from "../store";

const W = 560;

// Minimal markdown: headings, bold, inline code, bullets.
function renderInline(s: string) {
  const parts: (string | JSX.Element)[] = [];
  const re = /(\*\*[^*]+\*\*|`[^`]+`)/g;
  let last = 0;
  let m: RegExpExecArray | null;
  let key = 0;
  while ((m = re.exec(s))) {
    if (m.index > last) parts.push(s.slice(last, m.index));
    const tok = m[0];
    if (tok.startsWith("**")) {
      parts.push(<strong key={key++}>{tok.slice(2, -2)}</strong>);
    } else {
      parts.push(
        <code key={key++} className="font-mono text-[0.9em] bg-marker-yellow/40 px-1 rounded">
          {tok.slice(1, -1)}
        </code>
      );
    }
    last = m.index + tok.length;
  }
  if (last < s.length) parts.push(s.slice(last));
  return parts;
}

function renderBody(src: string) {
  const lines = src.split("\n");
  const out: JSX.Element[] = [];
  let i = 0;
  let key = 0;
  while (i < lines.length) {
    const line = lines[i];
    if (/^###\s+/.test(line)) {
      out.push(
        <h3 key={key++} className="font-hand text-2xl mt-1">
          {renderInline(line.replace(/^###\s+/, ""))}
        </h3>
      );
      i++;
    } else if (/^##\s+/.test(line)) {
      out.push(
        <h2 key={key++} className="font-hand text-3xl mt-1">
          {renderInline(line.replace(/^##\s+/, ""))}
        </h2>
      );
      i++;
    } else if (/^#\s+/.test(line)) {
      out.push(
        <h1 key={key++} className="font-hand text-4xl mt-1">
          {renderInline(line.replace(/^#\s+/, ""))}
        </h1>
      );
      i++;
    } else if (/^[-*]\s+/.test(line)) {
      const items: string[] = [];
      while (i < lines.length && /^[-*]\s+/.test(lines[i])) {
        items.push(lines[i].replace(/^[-*]\s+/, ""));
        i++;
      }
      out.push(
        <ul key={key++} className="list-disc pl-6 font-hand text-xl leading-snug space-y-0.5">
          {items.map((it, j) => (
            <li key={j}>{renderInline(it)}</li>
          ))}
        </ul>
      );
    } else if (line.trim() === "") {
      out.push(<div key={key++} className="h-2" />);
      i++;
    } else {
      out.push(
        <p key={key++} className="font-hand text-xl leading-snug">
          {renderInline(line)}
        </p>
      );
      i++;
    }
  }
  return out;
}

export function MarkdownNode({
  data,
}: NodeProps<{ cellId: string; source: string; color?: string; kind?: string; title?: string }>) {
  const rendered = useMemo(() => renderBody(data.source), [data.source]);
  const dark = useStore((s) => s.theme === "dark");
  const fill = colorFor({ color: data.color, kind: data.kind ?? "intro", dark });
  const approxH = Math.max(140, Math.ceil(data.source.length / 50) * 26 + 60);

  return (
    <div style={{ width: W, position: "relative" }}>
      <Handle type="target" position={Position.Left} />
      <div className="doodle-card" style={{ minHeight: approxH, background: "transparent" }}>
        <DoodleBorder width={W + 8} height={approxH + 8} fill={fill} stroke={dark ? "#ececec" : "#2a2a2a"} />
        <div className="relative">{rendered}</div>
      </div>
      <Handle type="source" position={Position.Right} />
    </div>
  );
}
