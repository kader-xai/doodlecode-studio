/**
 * Doodle-style flowchart + bar-chart compiler.
 *
 * Adapted from the Codex `diagramBlocks.js` prototype, ported to
 * TypeScript and rewritten to fix two layout bugs in the original:
 *
 *   1. Arrows landed ~10px short of the target box edge (the path
 *      stopped at `x - 10` to leave room for the marker, but the
 *      marker's `refX` already accounts for that — so the arrowhead
 *      hovered in space). We now end the path exactly at the chosen
 *      edge and let the marker's `refX` overlap by stroke width.
 *
 *   2. When a node wrapped to the next grid row, the Bezier still
 *      curved left-to-right, producing tangled connectors. We now
 *      pick the source/target edge (top/bottom/left/right) based on
 *      the relative positions of the boxes and adjust the Bezier
 *      control points accordingly, so the arrow always emerges from
 *      the "nearest" side and lands on the "nearest" side.
 *
 * Input syntax (line-by-line):
 *
 *     flowchart                # optional, ignored
 *     Idea --> Markdown
 *     Markdown --> Slides
 *
 *     chart: Demo energy        # optional title for the bar chart
 *     Markdown: 8
 *     Slides: 10
 *
 * Any line containing `-->` is a flow edge. Any remaining line that
 * looks like `Label: number` is a chart bar. Lines starting with
 * `chart:` set the bar-chart title. Blank lines are ignored.
 *
 * Output: an SVG string ready for `dangerouslySetInnerHTML`. We hand
 * the consumer the explicit width/height so the surrounding box can
 * scale or scroll.
 */

const FLOW_COLORS  = ["#fff2c6", "#dff7ee", "#ffe2e8", "#e8eeff", "#f4e8ff"];
const CHART_COLORS = ["#e85d75", "#1f9d8a", "#3867d6", "#f2b544", "#7a4ec6"];

export interface FlowEdge { from: string; to: string }
export interface ChartItem { label: string; value: number }

export interface Parsed {
  flow: FlowEdge[];
  charts: ChartItem[];
  chartTitle: string;
}

export function parseDoodleDiagram(source: string): Parsed {
  const lines = source.split("\n").map((l) => l.trim()).filter(Boolean);
  const flow: FlowEdge[] = [];
  const charts: ChartItem[] = [];
  let chartTitle = "";

  for (const line of lines) {
    const normalized = line.toLowerCase();

    // Mermaid-style header — just skip.
    if (normalized === "flowchart" || normalized.startsWith("graph ")) continue;

    // Chart title line.
    if (normalized.startsWith("chart:")) {
      chartTitle = line.split(":").slice(1).join(":").trim() || "Chart";
      continue;
    }

    // Flow edge (must come before the Label: Number test).
    if (line.includes("-->")) {
      const [from, to] = line.split("-->").map((p) => p.trim());
      if (from && to) flow.push({ from, to });
      continue;
    }

    // Chart bar.
    if (line.includes(":")) {
      const idx = line.indexOf(":");
      const label = line.slice(0, idx).trim();
      const value = Number(line.slice(idx + 1).trim());
      if (label && Number.isFinite(value)) {
        charts.push({ label, value });
      }
    }
  }

  return { flow, charts, chartTitle };
}

export function renderDoodleDiagram(source: string, dark = false): string {
  const parsed = parseDoodleDiagram(source);
  const flow = renderFlow(parsed.flow, dark);
  const chart = renderChart(parsed.charts, parsed.chartTitle || "Chart", dark);
  if (!flow && !chart) {
    return placeholder(dark);
  }
  return `<div class="doodle-diagram-stack" style="display:flex;flex-direction:column;gap:14px;align-items:center;">${flow}${chart}</div>`;
}

// ───────────────────────── Flowchart ────────────────────────────

function renderFlow(edges: FlowEdge[], dark: boolean): string {
  if (!edges.length) return "";

  const labels = [...new Set(edges.flatMap((e) => [e.from, e.to]))];
  const cols = Math.min(3, Math.max(1, labels.length));
  const nodeW = 150;
  const nodeH = 58;
  const gapX = 74;
  const gapY = 60;
  const padX = 40;
  const padY = 38;

  const positions = new Map<string, { x: number; y: number }>();
  labels.forEach((label, index) => {
    const col = index % cols;
    const row = Math.floor(index / cols);
    positions.set(label, {
      x: padX + col * (nodeW + gapX),
      y: padY + row * (nodeH + gapY),
    });
  });

  const rows = Math.ceil(labels.length / cols);
  const width  = padX + cols * nodeW + (cols - 1) * gapX + padX;
  const height = padY + rows * nodeH + (rows - 1) * gapY + padY;

  const arrowId = `arrow-${hash(edges.map((e) => `${e.from}>${e.to}`).join("|"))}`;
  const stroke = dark ? "#f0f0f0" : "#202124";

  const paths = edges
    .map((edge) => {
      const a = positions.get(edge.from);
      const b = positions.get(edge.to);
      if (!a || !b) return "";
      return drawEdge(a, b, nodeW, nodeH, arrowId, stroke);
    })
    .join("");

  const nodes = labels
    .map((label, index) => {
      const pos = positions.get(label)!;
      const fill = FLOW_COLORS[index % FLOW_COLORS.length];
      const textColor = "#202124"; // dark text on pastels works in both themes
      return `<g>
        <rect x="${pos.x}" y="${pos.y}" width="${nodeW}" height="${nodeH}" rx="10"
              fill="${fill}" stroke="${stroke}" stroke-width="3" />
        <text x="${pos.x + nodeW / 2}" y="${pos.y + nodeH / 2 + 6}"
              text-anchor="middle" font-family="Patrick Hand, Caveat, sans-serif"
              font-size="20" font-weight="700" fill="${textColor}">${escape(label)}</text>
      </g>`;
    })
    .join("");

  return `<svg viewBox="0 0 ${width} ${height}"
               width="${width}" height="${height}"
               style="max-width:100%; height:auto;"
               role="img" aria-label="Flowchart">
    <defs>
      <marker id="${arrowId}" markerWidth="10" markerHeight="10"
              refX="9" refY="3" orient="auto" markerUnits="strokeWidth">
        <path d="M0,0 L0,6 L9,3 z" fill="${stroke}"/>
      </marker>
    </defs>
    ${paths}
    ${nodes}
  </svg>`;
}

/**
 * Draw one edge from box `a` to box `b`. We pick the source/target
 * EDGE based on the dominant relative position, then offset the Bezier
 * control points along that axis so the curve emerges and arrives
 * perpendicular to the chosen edges.
 */
function drawEdge(
  a: { x: number; y: number },
  b: { x: number; y: number },
  w: number,
  h: number,
  arrowId: string,
  stroke: string,
): string {
  const ac = { x: a.x + w / 2, y: a.y + h / 2 };
  const bc = { x: b.x + w / 2, y: b.y + h / 2 };
  const dx = bc.x - ac.x;
  const dy = bc.y - ac.y;

  let x1: number, y1: number, x2: number, y2: number, cx1: number, cy1: number, cx2: number, cy2: number;

  if (Math.abs(dx) >= Math.abs(dy)) {
    // Mostly horizontal — leave from right/left, arrive at left/right.
    if (dx >= 0) {
      x1 = a.x + w; y1 = ac.y;
      x2 = b.x;     y2 = bc.y;
    } else {
      x1 = a.x;     y1 = ac.y;
      x2 = b.x + w; y2 = bc.y;
    }
    const k = Math.max(40, Math.abs(dx) * 0.45);
    cx1 = x1 + (dx >= 0 ?  k : -k); cy1 = y1;
    cx2 = x2 + (dx >= 0 ? -k :  k); cy2 = y2;
  } else {
    // Mostly vertical — leave from top/bottom, arrive at bottom/top.
    if (dy >= 0) {
      x1 = ac.x; y1 = a.y + h;
      x2 = bc.x; y2 = b.y;
    } else {
      x1 = ac.x; y1 = a.y;
      x2 = bc.x; y2 = b.y + h;
    }
    const k = Math.max(40, Math.abs(dy) * 0.45);
    cx1 = x1; cy1 = y1 + (dy >= 0 ?  k : -k);
    cx2 = x2; cy2 = y2 + (dy >= 0 ? -k :  k);
  }

  return `<path d="M ${x1} ${y1} C ${cx1} ${cy1}, ${cx2} ${cy2}, ${x2} ${y2}"
                fill="none" stroke="${stroke}" stroke-width="3"
                stroke-linecap="round" marker-end="url(#${arrowId})"/>`;
}

// ───────────────────────── Bar chart ────────────────────────────

function renderChart(items: ChartItem[], title: string, dark: boolean): string {
  if (!items.length) return "";

  const max = Math.max(...items.map((i) => i.value), 1);
  const barH = 32;
  const gap = 16;
  const labelGutter = 150;
  const barAreaW = 380;
  const padX = 24;
  const titleH = 40;
  const padBottom = 18;

  const width = padX + labelGutter + barAreaW + padX + 60;
  const height = titleH + items.length * (barH + gap) + padBottom;
  const stroke = dark ? "#f0f0f0" : "#202124";

  const bars = items
    .map((item, index) => {
      const w = (barAreaW * item.value) / max;
      const y = titleH + index * (barH + gap);
      const color = CHART_COLORS[index % CHART_COLORS.length];
      return `<g>
        <text x="${padX}" y="${y + barH / 2 + 5}"
              font-family="Patrick Hand, Caveat, sans-serif"
              font-size="17" font-weight="700" fill="${stroke}">${escape(item.label)}</text>
        <rect x="${padX + labelGutter}" y="${y}" width="${w}" height="${barH}" rx="6"
              fill="${color}" stroke="${stroke}" stroke-width="3"/>
        <text x="${padX + labelGutter + w + 8}" y="${y + barH / 2 + 5}"
              font-family="Patrick Hand, Caveat, sans-serif"
              font-size="17" font-weight="800" fill="${stroke}">${item.value}</text>
      </g>`;
    })
    .join("");

  return `<svg viewBox="0 0 ${width} ${height}"
               width="${width}" height="${height}"
               style="max-width:100%; height:auto;"
               role="img" aria-label="Bar chart">
    <text x="${padX}" y="${titleH - 12}"
          font-family="Patrick Hand, Caveat, sans-serif"
          font-size="24" font-weight="800" fill="${stroke}">${escape(title)}</text>
    ${bars}
  </svg>`;
}

// ───────────────────────── Helpers ──────────────────────────────

function placeholder(dark: boolean): string {
  const c = dark ? "#aaa" : "#555";
  return `<div style="padding:18px;text-align:center;color:${c};font-family:Patrick Hand,Caveat,sans-serif;font-size:18px;">
    Empty diagram — write <code>A --&gt; B</code> lines or <code>Label: 5</code> for charts.
  </div>`;
}

function escape(value: string): string {
  return String(value).replace(/[&<>"']/g, (ch) => {
    switch (ch) {
      case "&": return "&amp;";
      case "<": return "&lt;";
      case ">": return "&gt;";
      case "\"": return "&quot;";
      case "'": return "&#039;";
    }
    return ch;
  });
}

function hash(s: string): string {
  let h = 0;
  for (let i = 0; i < s.length; i++) h = ((h << 5) - h + s.charCodeAt(i)) | 0;
  return Math.abs(h).toString(36);
}
