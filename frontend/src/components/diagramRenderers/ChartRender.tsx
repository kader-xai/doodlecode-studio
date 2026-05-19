import { useEffect, useRef, useState } from "react";
import rough from "roughjs";

/** Sketchy chart renderer using roughjs (already a dep — no extra
 *  bundle cost). Source is JSON:
 *    {
 *      "type": "bar" | "line" | "pie",
 *      "title": "optional",
 *      "data": [["Python", 82], ["Rust", 38]]   // [label, value]
 *    }
 */

type ChartSpec = {
  type?: "bar" | "line" | "pie";
  title?: string;
  data?: Array<[string, number]>;
  colors?: string[];
};

const DEFAULT_COLORS = [
  "#fcc419", "#74c0fc", "#ff8787", "#69db7c",
  "#b197fc", "#3bc9db", "#ffa94d", "#e599f7",
];

function parseSpec(src: string): { spec: ChartSpec; err: string | null } {
  if (!src.trim()) return { spec: {}, err: null };
  try {
    const spec = JSON.parse(src) as ChartSpec;
    return { spec, err: null };
  } catch (e) {
    return { spec: {}, err: e instanceof Error ? e.message : String(e) };
  }
}

function drawBar(svg: SVGSVGElement, spec: ChartSpec, w: number, h: number, fs: number) {
  const rc = rough.svg(svg);
  const padL = 60, padR = 20, padT = 50, padB = 60;
  const data = spec.data ?? [];
  if (!data.length) return;
  const max = Math.max(...data.map(([, v]) => v));
  const barW = (w - padL - padR) / data.length;
  const colors = spec.colors ?? DEFAULT_COLORS;
  // Title
  if (spec.title) {
    const t = document.createElementNS("http://www.w3.org/2000/svg", "text");
    t.setAttribute("x", String(w / 2));
    t.setAttribute("y", String(28));
    t.setAttribute("text-anchor", "middle");
    t.setAttribute("font-family", "Caveat, Patrick Hand, cursive");
    t.setAttribute("font-size", String(Math.round(26 * fs)));
    t.setAttribute("fill", "#2a2a2a");
    t.textContent = spec.title;
    svg.appendChild(t);
  }
  // Axis
  svg.appendChild(rc.line(padL, h - padB, w - padR, h - padB, { stroke: "#2a2a2a", strokeWidth: 1.5 }));
  svg.appendChild(rc.line(padL, padT, padL, h - padB, { stroke: "#2a2a2a", strokeWidth: 1.5 }));
  // Bars + labels
  data.forEach(([label, val], i) => {
    const bh = ((val / max) * (h - padT - padB)) | 0;
    const x = padL + i * barW + barW * 0.15;
    const bw = barW * 0.7;
    const y = h - padB - bh;
    svg.appendChild(
      rc.rectangle(x, y, bw, bh, {
        fill: colors[i % colors.length],
        fillStyle: "hachure",
        hachureGap: 6,
        stroke: "#2a2a2a",
        strokeWidth: 1.5,
        roughness: 1.6,
      })
    );
    // Value above bar
    const vtxt = document.createElementNS("http://www.w3.org/2000/svg", "text");
    vtxt.setAttribute("x", String(x + bw / 2));
    vtxt.setAttribute("y", String(y - 6));
    vtxt.setAttribute("text-anchor", "middle");
    vtxt.setAttribute("font-family", "JetBrains Mono, monospace");
    vtxt.setAttribute("font-size", String(Math.round(13 * fs)));
    vtxt.setAttribute("fill", "#2a2a2a");
    vtxt.textContent = String(val);
    svg.appendChild(vtxt);
    // X-axis label
    const lt = document.createElementNS("http://www.w3.org/2000/svg", "text");
    lt.setAttribute("x", String(x + bw / 2));
    lt.setAttribute("y", String(h - padB + 22));
    lt.setAttribute("text-anchor", "middle");
    lt.setAttribute("font-family", "Caveat, Patrick Hand, cursive");
    lt.setAttribute("font-size", String(Math.round(18 * fs)));
    lt.setAttribute("fill", "#2a2a2a");
    lt.textContent = label;
    svg.appendChild(lt);
  });
}

function drawLine(svg: SVGSVGElement, spec: ChartSpec, w: number, h: number, fs: number) {
  const rc = rough.svg(svg);
  const padL = 60, padR = 30, padT = 50, padB = 60;
  const data = spec.data ?? [];
  if (data.length < 2) return;
  const max = Math.max(...data.map(([, v]) => v));
  const min = Math.min(...data.map(([, v]) => v));
  const step = (w - padL - padR) / (data.length - 1);
  if (spec.title) {
    const t = document.createElementNS("http://www.w3.org/2000/svg", "text");
    t.setAttribute("x", String(w / 2));
    t.setAttribute("y", String(28));
    t.setAttribute("text-anchor", "middle");
    t.setAttribute("font-family", "Caveat, Patrick Hand, cursive");
    t.setAttribute("font-size", String(Math.round(26 * fs)));
    t.setAttribute("fill", "#2a2a2a");
    t.textContent = spec.title;
    svg.appendChild(t);
  }
  svg.appendChild(rc.line(padL, h - padB, w - padR, h - padB, { stroke: "#2a2a2a", strokeWidth: 1.5 }));
  svg.appendChild(rc.line(padL, padT, padL, h - padB, { stroke: "#2a2a2a", strokeWidth: 1.5 }));
  const pts: [number, number][] = data.map(([, v], i) => [
    padL + i * step,
    h - padB - ((v - min) / (max - min || 1)) * (h - padT - padB),
  ]);
  for (let i = 1; i < pts.length; i++) {
    svg.appendChild(
      rc.line(pts[i - 1][0], pts[i - 1][1], pts[i][0], pts[i][1], {
        stroke: "#1971c2",
        strokeWidth: 2.4,
        roughness: 1.4,
      })
    );
  }
  pts.forEach(([x, y], i) => {
    svg.appendChild(
      rc.circle(x, y, 10, {
        fill: "#fcc419",
        fillStyle: "solid",
        stroke: "#2a2a2a",
        strokeWidth: 1.5,
      })
    );
    const lt = document.createElementNS("http://www.w3.org/2000/svg", "text");
    lt.setAttribute("x", String(x));
    lt.setAttribute("y", String(h - padB + 22));
    lt.setAttribute("text-anchor", "middle");
    lt.setAttribute("font-family", "Caveat, Patrick Hand, cursive");
    lt.setAttribute("font-size", String(Math.round(16 * fs)));
    lt.textContent = data[i][0];
    svg.appendChild(lt);
  });
}

function drawPie(svg: SVGSVGElement, spec: ChartSpec, w: number, h: number, fs: number) {
  const rc = rough.svg(svg);
  const data = spec.data ?? [];
  if (!data.length) return;
  const total = data.reduce((s, [, v]) => s + v, 0);
  const cx = w / 2;
  const cy = h / 2 + 10;
  const r = Math.min(w, h) * 0.35;
  const colors = spec.colors ?? DEFAULT_COLORS;
  if (spec.title) {
    const t = document.createElementNS("http://www.w3.org/2000/svg", "text");
    t.setAttribute("x", String(w / 2));
    t.setAttribute("y", String(30));
    t.setAttribute("text-anchor", "middle");
    t.setAttribute("font-family", "Caveat, Patrick Hand, cursive");
    t.setAttribute("font-size", String(Math.round(26 * fs)));
    t.setAttribute("fill", "#2a2a2a");
    t.textContent = spec.title;
    svg.appendChild(t);
  }
  let a0 = -Math.PI / 2;
  data.forEach(([label, v], i) => {
    const a1 = a0 + (v / total) * Math.PI * 2;
    const large = a1 - a0 > Math.PI ? 1 : 0;
    const x1 = cx + r * Math.cos(a0);
    const y1 = cy + r * Math.sin(a0);
    const x2 = cx + r * Math.cos(a1);
    const y2 = cy + r * Math.sin(a1);
    const pathD = `M ${cx} ${cy} L ${x1} ${y1} A ${r} ${r} 0 ${large} 1 ${x2} ${y2} Z`;
    svg.appendChild(
      rc.path(pathD, {
        fill: colors[i % colors.length],
        fillStyle: "hachure",
        hachureGap: 7,
        stroke: "#2a2a2a",
        strokeWidth: 1.5,
        roughness: 1.5,
      })
    );
    const am = (a0 + a1) / 2;
    const lx = cx + (r + 24) * Math.cos(am);
    const ly = cy + (r + 24) * Math.sin(am);
    const lt = document.createElementNS("http://www.w3.org/2000/svg", "text");
    lt.setAttribute("x", String(lx));
    lt.setAttribute("y", String(ly));
    lt.setAttribute("text-anchor", lx < cx ? "end" : "start");
    lt.setAttribute("font-family", "Caveat, Patrick Hand, cursive");
    lt.setAttribute("font-size", String(Math.round(18 * fs)));
    lt.setAttribute("fill", "#2a2a2a");
    lt.textContent = `${label} (${v})`;
    svg.appendChild(lt);
    a0 = a1;
  });
}

export function ChartRender({
  source,
  fontScale = 1,
}: {
  source: string;
  fontScale?: number;
}) {
  const ref = useRef<SVGSVGElement | null>(null);
  const wrapRef = useRef<HTMLDivElement | null>(null);
  const [size, setSize] = useState<{ w: number; h: number }>({ w: 720, h: 420 });
  const { spec, err } = parseSpec(source);

  useEffect(() => {
    const el = wrapRef.current;
    if (!el) return;
    const ro = new ResizeObserver((entries) => {
      for (const e of entries) {
        const w = Math.max(360, Math.floor(e.contentRect.width));
        const h = Math.max(240, Math.floor(e.contentRect.height));
        setSize((cur) => (cur.w === w && cur.h === h ? cur : { w, h }));
      }
    });
    ro.observe(el);
    return () => ro.disconnect();
  }, []);

  useEffect(() => {
    const svg = ref.current;
    if (!svg) return;
    while (svg.firstChild) svg.removeChild(svg.firstChild);
    if (err) return;
    const { w, h } = size;
    const draw =
      spec.type === "line" ? drawLine
      : spec.type === "pie"  ? drawPie
      : drawBar;
    draw(svg, spec, w, h, fontScale);
  }, [spec, size, err, fontScale]);

  if (err) {
    return (
      <pre className="m-2 p-3 rounded-lg border-2 border-red-500 bg-red-50 text-red-700 text-xs font-mono whitespace-pre-wrap">
        Chart JSON error:
        {"\n"}
        {err}
      </pre>
    );
  }
  return (
    <div ref={wrapRef} className="w-full h-full p-2 flex items-center justify-center">
      <svg ref={ref} width={size.w} height={size.h} />
    </div>
  );
}
