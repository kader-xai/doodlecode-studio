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
/** Iter 160: a labelled line-chart series — one polyline of values. */
export interface LineSeries { label: string; points: number[] }
/** Iter 172: an area series — a line filled to the baseline. */
export interface AreaSeries { label: string; points: number[] }
/** Iter 164: one slice of a pie / donut chart. */
export interface PieSlice { label: string; value: number }
/** Iter 166: one (x, y) dot of a scatter plot. */
export interface ScatterPoint { x: number; y: number }
/** Iter 187: a horizontal reference/threshold line on a y-axis chart. */
export interface HLine { value: number; label?: string }
/** Iter 190: one category row of a stacked bar (segments = series). */
export interface StackBar { label: string; values: number[] }

export interface Parsed {
  flow: FlowEdge[];
  charts: ChartItem[];
  lines: LineSeries[];
  areas: AreaSeries[];
  pies: PieSlice[];
  points: ScatterPoint[];
  /** Iter 187: dashed reference lines, shared by line / area / scatter. */
  hlines: HLine[];
  /** Iter 190: stacked-bar category rows + their series legend + title. */
  stacks: StackBar[];
  stackSeries: string[];
  stackTitle: string;
  chartTitle: string;
  pieTitle: string;
  scatterTitle: string;
  /** Iter 168: optional axis titles, shared by line + scatter charts. */
  xLabel: string;
  yLabel: string;
}

export function parseDoodleDiagram(source: string): Parsed {
  const rawLines = source.split("\n").map((l) => l.trim()).filter(Boolean);
  const flow: FlowEdge[] = [];
  const charts: ChartItem[] = [];
  const series: LineSeries[] = [];
  const areas: AreaSeries[] = [];
  const pies: PieSlice[] = [];
  const points: ScatterPoint[] = [];
  const hlines: HLine[] = [];
  const stacks: StackBar[] = [];
  let stackSeries: string[] = [];
  let stackTitle = "";
  let chartTitle = "";
  let pieTitle = "";
  let scatterTitle = "";
  let xLabel = "";
  let yLabel = "";

  for (const line of rawLines) {
    const normalized = line.toLowerCase();

    // Mermaid-style header — just skip.
    if (normalized === "flowchart" || normalized.startsWith("graph ")) continue;

    // Iter 168: axis titles (`xlabel: …` / `ylabel: …`). Checked
    // before the bar rule so they're never read as a `Label: Number`.
    if (normalized.startsWith("xlabel:")) {
      xLabel = line.slice(line.indexOf(":") + 1).trim();
      continue;
    }
    if (normalized.startsWith("ylabel:")) {
      yLabel = line.slice(line.indexOf(":") + 1).trim();
      continue;
    }

    // Chart title line.
    if (normalized.startsWith("chart:")) {
      chartTitle = line.split(":").slice(1).join(":").trim() || "Chart";
      continue;
    }

    // Iter 190: stacked-bar legend — `series: Q1, Q2, Q3`. Checked
    // before the bar rule (shared colon).
    if (normalized.startsWith("series:")) {
      stackSeries = line
        .slice(line.indexOf(":") + 1)
        .split(",")
        .map((s) => s.trim())
        .filter(Boolean);
      continue;
    }

    // Iter 190: stacked-bar title — `stack: Title`. Before the `stack
    // <Label>:` row rule so an empty-label row isn't created.
    if (normalized.startsWith("stack:")) {
      stackTitle = line.split(":").slice(1).join(":").trim() || "Stacked";
      continue;
    }

    // Iter 190: stacked-bar category row — `stack <Label>: 3, 5, 2`.
    if (normalized.startsWith("stack ")) {
      const colon = line.indexOf(":");
      if (colon !== -1) {
        const label = line.slice(0, colon).replace(/^stack\b\s*/i, "").trim();
        const values = line
          .slice(colon + 1)
          .split(/[,\s]+/)
          .map((n) => n.trim())
          .filter(Boolean)
          .map(Number)
          .filter((n) => Number.isFinite(n) && n >= 0);
        if (label && values.length) stacks.push({ label, values });
        continue;
      }
    }

    // Iter 187: reference line — `hline: 0.5` or `hline Target: 0.5`.
    // A dashed threshold drawn across line / area / scatter charts.
    if (normalized.startsWith("hline:") || normalized.startsWith("hline ")) {
      const colon = line.indexOf(":");
      if (colon !== -1) {
        const label = line.slice(0, colon).replace(/^hline\b\s*/i, "").trim();
        const value = Number(line.slice(colon + 1).trim());
        if (Number.isFinite(value)) {
          hlines.push(label ? { value, label } : { value });
        }
        continue;
      }
    }

    // Iter 166: scatter title (`scatter: Title`) — checked before the
    // `point:` rule so an empty point isn't created.
    if (normalized.startsWith("scatter:")) {
      scatterTitle = line.split(":").slice(1).join(":").trim() || "Scatter";
      continue;
    }

    // Iter 166: scatter point — `point: x, y`. Needs exactly two finite
    // numbers; checked before the bar `Label: Number` rule (shared colon).
    if (normalized.startsWith("point ") || normalized.startsWith("point:")) {
      const colon = line.indexOf(":");
      if (colon !== -1) {
        const nums = line
          .slice(colon + 1)
          .split(/[,\s]+/)
          .map((n) => n.trim())
          .filter(Boolean)
          .map(Number)
          .filter((n) => Number.isFinite(n));
        if (nums.length >= 2) points.push({ x: nums[0], y: nums[1] });
        continue;
      }
    }

    // Iter 164: pie title (`pie: Title`) — checked before the slice
    // rule below so an empty-label slice isn't created.
    if (normalized.startsWith("pie:")) {
      pieTitle = line.split(":").slice(1).join(":").trim() || "Breakdown";
      continue;
    }

    // Iter 164: pie slice — `pie <Label>: <value>`. Positive values
    // only; checked before the bar `Label: Number` rule (shared colon).
    if (normalized.startsWith("pie ")) {
      const colon = line.indexOf(":");
      if (colon !== -1) {
        const label = line.slice(0, colon).replace(/^pie\b\s*/i, "").trim();
        const value = Number(line.slice(colon + 1).trim());
        if (label && Number.isFinite(value) && value > 0) {
          pies.push({ label, value });
        }
        continue;
      }
    }

    // Iter 160: line-chart series — `line <Label>: 0.9, 0.6, 0.4`.
    // Must be tested before the bar `Label: Number` rule (it also has
    // a colon). Numbers are comma- or space-separated.
    if (normalized.startsWith("line:") || normalized.startsWith("line ")) {
      const colon = line.indexOf(":");
      if (colon !== -1) {
        const head = line.slice(0, colon).trim(); // "line" or "line Loss"
        const label = head.replace(/^line\b\s*/i, "").trim() || `Series ${series.length + 1}`;
        const points = line
          .slice(colon + 1)
          .split(/[,\s]+/)
          .map((n) => n.trim())
          .filter(Boolean) // drop empty tokens — Number("") is 0, a phantom point
          .map(Number)
          .filter((n) => Number.isFinite(n));
        if (points.length) series.push({ label, points });
        continue;
      }
    }

    // Iter 172: area series — `area <Label>: 1, 3, 2`. A filled line.
    // Same parsing as `line`; checked before the bar rule.
    if (normalized.startsWith("area:") || normalized.startsWith("area ")) {
      const colon = line.indexOf(":");
      if (colon !== -1) {
        const head = line.slice(0, colon).trim();
        const label = head.replace(/^area\b\s*/i, "").trim() || `Area ${areas.length + 1}`;
        const points = line
          .slice(colon + 1)
          .split(/[,\s]+/)
          .map((n) => n.trim())
          .filter(Boolean)
          .map(Number)
          .filter((n) => Number.isFinite(n));
        if (points.length) areas.push({ label, points });
        continue;
      }
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

  return { flow, charts, lines: series, areas, pies, points, hlines, stacks, stackSeries, stackTitle, chartTitle, pieTitle, scatterTitle, xLabel, yLabel };
}

/**
 * Iter 187: render dashed horizontal reference lines + right-edge labels
 * for any y-axis chart. `yAt` maps a data value to a pixel y; lines
 * outside the plot's [minV, maxV] band are skipped. Dashed strokes are
 * the conventional threshold marker — distinct from the "no dashed
 * structure" rule, which is about cell connectors, not chart data.
 */
function renderHLines(
  hlines: HLine[],
  yAt: (v: number) => number,
  minV: number,
  maxV: number,
  padL: number,
  plotW: number,
  stroke: string,
): string {
  return hlines
    .filter((h) => h.value >= minV && h.value <= maxV)
    .map((h) => {
      const y = yAt(h.value).toFixed(1);
      const line = `<line x1="${padL}" y1="${y}" x2="${padL + plotW}" y2="${y}"
        stroke="#c2255c" stroke-width="2" stroke-dasharray="6 4" opacity="0.85"/>`;
      const tag = h.label
        ? `<text x="${padL + plotW - 4}" y="${(yAt(h.value) - 4).toFixed(1)}" text-anchor="end"
            font-family="Patrick Hand, Caveat, sans-serif" font-size="13" font-weight="700"
            fill="#c2255c">${escape(h.label)}</text>`
        : "";
      void stroke;
      return line + tag;
    })
    .join("");
}

export function renderDoodleDiagram(source: string, dark = false): string {
  const parsed = parseDoodleDiagram(source);
  const flow = renderFlow(parsed.flow, dark);
  const chart = renderChart(parsed.charts, parsed.chartTitle || "Chart", dark);
  const stackedChart = renderStackedBar(parsed.stacks, parsed.stackSeries, parsed.stackTitle || "Stacked", dark);
  const lineChart = renderLineChart(parsed.lines, parsed.chartTitle || "Trend", dark, parsed.xLabel, parsed.yLabel, parsed.hlines);
  const areaChart = renderAreaChart(parsed.areas, parsed.chartTitle || "Area", dark, parsed.xLabel, parsed.yLabel, parsed.hlines);
  const pieChart = renderPieChart(parsed.pies, parsed.pieTitle || "Breakdown", dark);
  const scatterChart = renderScatterChart(parsed.points, parsed.scatterTitle || "Scatter", dark, parsed.xLabel, parsed.yLabel, parsed.hlines);
  if (!flow && !chart && !stackedChart && !lineChart && !areaChart && !pieChart && !scatterChart) {
    return placeholder(dark);
  }
  return `<div class="doodle-diagram-stack" style="display:flex;flex-direction:column;gap:14px;align-items:center;">${flow}${chart}${stackedChart}${lineChart}${areaChart}${pieChart}${scatterChart}</div>`;
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

// ───────────────────────── Stacked bar ──────────────────────────

function renderStackedBar(rows: StackBar[], seriesNames: string[], title: string, dark: boolean): string {
  if (!rows.length) return "";
  // Bar length scales to the widest row total, so proportions read true.
  const totals = rows.map((r) => r.values.reduce((s, v) => s + v, 0));
  const maxTotal = Math.max(...totals, 1);
  const segCount = Math.max(...rows.map((r) => r.values.length));

  const barH = 30;
  const gap = 18;
  const labelGutter = 130;
  const barAreaW = 380;
  const padX = 24;
  const titleH = 40;
  const legendH = seriesNames.length ? 26 : 0;
  const padBottom = 16;

  const width = padX + labelGutter + barAreaW + padX + 50;
  const height = titleH + legendH + rows.length * (barH + gap) + padBottom;
  const stroke = dark ? "#f0f0f0" : "#202124";

  // Legend — coloured chip + series name across the top.
  const legend = seriesNames
    .map((name, si) => {
      const color = CHART_COLORS[si % CHART_COLORS.length];
      const lx = padX + si * 130;
      const ly = titleH + 6;
      return `<rect x="${lx}" y="${ly - 10}" width="12" height="12" rx="2" fill="${color}" stroke="${stroke}" stroke-width="2"/>
        <text x="${lx + 18}" y="${ly}" font-family="Patrick Hand, Caveat, sans-serif"
              font-size="14" font-weight="700" fill="${stroke}">${escape(name)}</text>`;
    })
    .join("");

  const bars = rows
    .map((row, ri) => {
      const y = titleH + legendH + ri * (barH + gap);
      const total = totals[ri];
      const fullW = (barAreaW * total) / maxTotal;
      let x = padX + labelGutter;
      const segs = row.values
        .map((v, si) => {
          const segW = total > 0 ? (fullW * v) / total : 0;
          const color = CHART_COLORS[si % CHART_COLORS.length];
          const rect = `<rect x="${x.toFixed(1)}" y="${y}" width="${segW.toFixed(1)}" height="${barH}"
            fill="${color}" stroke="${stroke}" stroke-width="2.5"/>`;
          x += segW;
          return rect;
        })
        .join("");
      return `<g>
        <text x="${padX}" y="${y + barH / 2 + 5}"
              font-family="Patrick Hand, Caveat, sans-serif"
              font-size="16" font-weight="700" fill="${stroke}">${escape(row.label)}</text>
        ${segs}
        <text x="${(padX + labelGutter + fullW + 8).toFixed(1)}" y="${y + barH / 2 + 5}"
              font-family="Patrick Hand, Caveat, sans-serif"
              font-size="15" font-weight="800" fill="${stroke}">${trimNum(total)}</text>
      </g>`;
    })
    .join("");

  void segCount;
  return `<svg viewBox="0 0 ${width} ${height}" width="${width}" height="${height}"
               style="max-width:100%; height:auto;" role="img" aria-label="Stacked bar chart">
    <text x="${padX}" y="${titleH - 12}" font-family="Patrick Hand, Caveat, sans-serif"
          font-size="24" font-weight="800" fill="${stroke}">${escape(title)}</text>
    ${legend}
    ${bars}
  </svg>`;
}

// ───────────────────────── Line chart ───────────────────────────

function renderLineChart(series: LineSeries[], title: string, dark: boolean, xLabel = "", yLabel = "", hlines: HLine[] = []): string {
  if (!series.length) return "";
  const all = series.flatMap((s) => s.points);
  if (!all.length) return "";

  const minV = Math.min(...all, 0);
  const maxV = Math.max(...all, 1);
  const range = maxV - minV || 1;

  const padL = 50, padR = 26, padTop = 52, padBottom = xLabel ? 48 : 30;
  const plotW = 460, plotH = 220;
  const width = padL + plotW + padR;
  const height = padTop + plotH + padBottom;
  const stroke = dark ? "#f0f0f0" : "#202124";
  const grid = dark ? "rgba(255,255,255,0.14)" : "rgba(0,0,0,0.12)";

  const xAt = (i: number, n: number) =>
    padL + (n <= 1 ? plotW / 2 : (plotW * i) / (n - 1));
  const yAt = (v: number) => padTop + plotH - ((v - minV) / range) * plotH;

  // Faint horizontal gridlines (quartiles) for readability.
  const gridLines = [0, 0.25, 0.5, 0.75, 1]
    .map((t) => {
      const y = (padTop + plotH - t * plotH).toFixed(1);
      return `<line x1="${padL}" y1="${y}" x2="${padL + plotW}" y2="${y}" stroke="${grid}" stroke-width="1.5"/>`;
    })
    .join("");

  // Hand-drawn axes (L-shape, round caps/joins).
  const axis = `<path d="M ${padL} ${padTop} L ${padL} ${padTop + plotH} L ${padL + plotW} ${padTop + plotH}"
        fill="none" stroke="${stroke}" stroke-width="3" stroke-linecap="round" stroke-linejoin="round"/>`;

  const seriesSvg = series
    .map((s, si) => {
      const color = CHART_COLORS[si % CHART_COLORS.length];
      const n = s.points.length;
      if (!n) return "";
      let d = "";
      s.points.forEach((v, i) => {
        d += `${i === 0 ? "M" : "L"} ${xAt(i, n).toFixed(1)} ${yAt(v).toFixed(1)} `;
      });
      const dots = s.points
        .map(
          (v, i) =>
            `<circle cx="${xAt(i, n).toFixed(1)}" cy="${yAt(v).toFixed(1)}" r="4.5" fill="${color}" stroke="${stroke}" stroke-width="2"/>`,
        )
        .join("");
      return `<path d="${d}" fill="none" stroke="${color}" stroke-width="3.5" stroke-linecap="round" stroke-linejoin="round"/>${dots}`;
    })
    .join("");

  // Inline legend under the title — coloured dot + series label.
  const legend = series
    .map((s, si) => {
      const color = CHART_COLORS[si % CHART_COLORS.length];
      const lx = padL + si * 140;
      const ly = padTop - 18;
      return `<circle cx="${lx + 5}" cy="${ly - 4}" r="5" fill="${color}" stroke="${stroke}" stroke-width="2"/>
        <text x="${lx + 16}" y="${ly}" font-family="Patrick Hand, Caveat, sans-serif"
              font-size="15" font-weight="700" fill="${stroke}">${escape(s.label)}</text>`;
    })
    .join("");

  // Min/max y tick labels for scale.
  const yTicks = `
    <text x="${padL - 8}" y="${(yAt(maxV) + 5).toFixed(1)}" text-anchor="end"
          font-family="Patrick Hand, Caveat, sans-serif" font-size="13" fill="${stroke}">${trimNum(maxV)}</text>
    <text x="${padL - 8}" y="${(yAt(minV) + 5).toFixed(1)}" text-anchor="end"
          font-family="Patrick Hand, Caveat, sans-serif" font-size="13" fill="${stroke}">${trimNum(minV)}</text>`;

  const axisTitles = axisTitleSvg(xLabel, yLabel, padL, padTop, plotW, plotH, height, stroke);
  const refLines = renderHLines(hlines, yAt, minV, maxV, padL, plotW, stroke);

  return `<svg viewBox="0 0 ${width} ${height}" width="${width}" height="${height}"
        style="max-width:100%; height:auto;" role="img" aria-label="Line chart">
    <text x="${padL}" y="26" font-family="Patrick Hand, Caveat, sans-serif"
          font-size="24" font-weight="800" fill="${stroke}">${escape(title)}</text>
    ${legend}
    ${gridLines}
    ${axis}
    ${yTicks}
    ${refLines}
    ${seriesSvg}
    ${axisTitles}
  </svg>`;
}

/**
 * Iter 168: shared axis-title renderer for line + scatter charts.
 * X title is centered under the plot; Y title is rotated -90° along
 * the left edge. Both no-op when their label is empty.
 */
function axisTitleSvg(
  xLabel: string,
  yLabel: string,
  padL: number,
  padTop: number,
  plotW: number,
  plotH: number,
  height: number,
  stroke: string,
): string {
  const parts: string[] = [];
  if (xLabel) {
    const cx = padL + plotW / 2;
    parts.push(
      `<text x="${cx}" y="${height - 6}" text-anchor="middle"
        font-family="Patrick Hand, Caveat, sans-serif" font-size="16" font-weight="700"
        fill="${stroke}">${escape(xLabel)}</text>`,
    );
  }
  if (yLabel) {
    const cy = padTop + plotH / 2;
    parts.push(
      `<text x="14" y="${cy}" text-anchor="middle"
        transform="rotate(-90 14 ${cy})"
        font-family="Patrick Hand, Caveat, sans-serif" font-size="16" font-weight="700"
        fill="${stroke}">${escape(yLabel)}</text>`,
    );
  }
  return parts.join("");
}

// ───────────────────────── Pie / donut chart ────────────────────

function renderPieChart(slices: PieSlice[], title: string, dark: boolean): string {
  if (!slices.length) return "";
  const total = slices.reduce((sum, s) => sum + s.value, 0);
  if (total <= 0) return "";

  const stroke = dark ? "#f0f0f0" : "#202124";
  const R = 96;          // pie radius
  const HOLE = 40;       // donut hole radius — reads cleaner than a solid pie
  const cx = R + 16;
  const cy = R + 48;
  const legendX = cx + R + 28;
  const titleH = 30;
  const width = legendX + 200;
  const height = Math.max(cy + R + 20, titleH + slices.length * 26 + 40);

  // Donut wedges. Each slice is an annular sector (outer arc + inner arc).
  let angle = -Math.PI / 2; // start at 12 o'clock
  const wedges = slices
    .map((s, i) => {
      const frac = s.value / total;
      const a0 = angle;
      const a1 = angle + frac * Math.PI * 2;
      angle = a1;
      const color = CHART_COLORS[i % CHART_COLORS.length];
      const large = a1 - a0 > Math.PI ? 1 : 0;
      const ox0 = cx + R * Math.cos(a0), oy0 = cy + R * Math.sin(a0);
      const ox1 = cx + R * Math.cos(a1), oy1 = cy + R * Math.sin(a1);
      const ix1 = cx + HOLE * Math.cos(a1), iy1 = cy + HOLE * Math.sin(a1);
      const ix0 = cx + HOLE * Math.cos(a0), iy0 = cy + HOLE * Math.sin(a0);
      const d =
        `M ${ox0.toFixed(1)} ${oy0.toFixed(1)} ` +
        `A ${R} ${R} 0 ${large} 1 ${ox1.toFixed(1)} ${oy1.toFixed(1)} ` +
        `L ${ix1.toFixed(1)} ${iy1.toFixed(1)} ` +
        `A ${HOLE} ${HOLE} 0 ${large} 0 ${ix0.toFixed(1)} ${iy0.toFixed(1)} Z`;
      return `<path d="${d}" fill="${color}" stroke="${stroke}" stroke-width="2.5" stroke-linejoin="round"/>`;
    })
    .join("");

  // Legend — colour dot + label + percentage.
  const legend = slices
    .map((s, i) => {
      const color = CHART_COLORS[i % CHART_COLORS.length];
      const pct = Math.round((s.value / total) * 100);
      const ly = titleH + 18 + i * 26;
      return `<circle cx="${legendX + 6}" cy="${ly - 5}" r="6" fill="${color}" stroke="${stroke}" stroke-width="2"/>
        <text x="${legendX + 20}" y="${ly}" font-family="Patrick Hand, Caveat, sans-serif"
              font-size="17" font-weight="700" fill="${stroke}">${escape(s.label)} · ${pct}%</text>`;
    })
    .join("");

  return `<svg viewBox="0 0 ${width} ${height}" width="${width}" height="${height}"
        style="max-width:100%; height:auto;" role="img" aria-label="Pie chart">
    <text x="16" y="${titleH - 6}" font-family="Patrick Hand, Caveat, sans-serif"
          font-size="24" font-weight="800" fill="${stroke}">${escape(title)}</text>
    ${wedges}
    ${legend}
  </svg>`;
}

// ───────────────────────── Area chart ───────────────────────────

function renderAreaChart(series: AreaSeries[], title: string, dark: boolean, xLabel = "", yLabel = "", hlines: HLine[] = []): string {
  if (!series.length) return "";
  const all = series.flatMap((s) => s.points);
  if (!all.length) return "";

  const minV = Math.min(...all, 0);
  const maxV = Math.max(...all, 1);
  const range = maxV - minV || 1;

  const padL = 50, padR = 26, padTop = 52, padBottom = xLabel ? 48 : 30;
  const plotW = 460, plotH = 220;
  const width = padL + plotW + padR;
  const height = padTop + plotH + padBottom;
  const stroke = dark ? "#f0f0f0" : "#202124";
  const grid = dark ? "rgba(255,255,255,0.14)" : "rgba(0,0,0,0.12)";
  const baseY = padTop + plotH;

  const xAt = (i: number, n: number) =>
    padL + (n <= 1 ? plotW / 2 : (plotW * i) / (n - 1));
  const yAt = (v: number) => padTop + plotH - ((v - minV) / range) * plotH;

  const gridLines = [0, 0.25, 0.5, 0.75, 1]
    .map((t) => {
      const y = (padTop + plotH - t * plotH).toFixed(1);
      return `<line x1="${padL}" y1="${y}" x2="${padL + plotW}" y2="${y}" stroke="${grid}" stroke-width="1.5"/>`;
    })
    .join("");

  const axis = `<path d="M ${padL} ${padTop} L ${padL} ${padTop + plotH} L ${padL + plotW} ${padTop + plotH}"
        fill="none" stroke="${stroke}" stroke-width="3" stroke-linecap="round" stroke-linejoin="round"/>`;

  // Later series draw first (behind) so earlier ones read on top.
  const seriesSvg = series
    .map((s, si) => {
      const color = CHART_COLORS[si % CHART_COLORS.length];
      const n = s.points.length;
      if (!n) return "";
      let line = "";
      s.points.forEach((v, i) => {
        line += `${i === 0 ? "M" : "L"} ${xAt(i, n).toFixed(1)} ${yAt(v).toFixed(1)} `;
      });
      // Fill polygon: line, down to baseline, back to start.
      const x0 = xAt(0, n).toFixed(1);
      const xN = xAt(n - 1, n).toFixed(1);
      const fill = `${line} L ${xN} ${baseY} L ${x0} ${baseY} Z`;
      return `<path d="${fill}" fill="${color}" fill-opacity="0.28" stroke="none"/>` +
        `<path d="${line}" fill="none" stroke="${color}" stroke-width="3" stroke-linecap="round" stroke-linejoin="round"/>`;
    })
    .reverse()
    .join("");

  const legend = series
    .map((s, si) => {
      const color = CHART_COLORS[si % CHART_COLORS.length];
      const lx = padL + si * 140;
      const ly = padTop - 18;
      return `<rect x="${lx}" y="${ly - 11}" width="12" height="12" rx="2" fill="${color}" fill-opacity="0.5" stroke="${stroke}" stroke-width="2"/>
        <text x="${lx + 18}" y="${ly}" font-family="Patrick Hand, Caveat, sans-serif"
              font-size="15" font-weight="700" fill="${stroke}">${escape(s.label)}</text>`;
    })
    .join("");

  const yTicks = `
    <text x="${padL - 8}" y="${(yAt(maxV) + 5).toFixed(1)}" text-anchor="end"
          font-family="Patrick Hand, Caveat, sans-serif" font-size="13" fill="${stroke}">${trimNum(maxV)}</text>
    <text x="${padL - 8}" y="${(yAt(minV) + 5).toFixed(1)}" text-anchor="end"
          font-family="Patrick Hand, Caveat, sans-serif" font-size="13" fill="${stroke}">${trimNum(minV)}</text>`;

  const axisTitles = axisTitleSvg(xLabel, yLabel, padL, padTop, plotW, plotH, height, stroke);
  const refLines = renderHLines(hlines, yAt, minV, maxV, padL, plotW, stroke);

  return `<svg viewBox="0 0 ${width} ${height}" width="${width}" height="${height}"
        style="max-width:100%; height:auto;" role="img" aria-label="Area chart">
    <text x="${padL}" y="26" font-family="Patrick Hand, Caveat, sans-serif"
          font-size="24" font-weight="800" fill="${stroke}">${escape(title)}</text>
    ${legend}
    ${gridLines}
    ${seriesSvg}
    ${axis}
    ${yTicks}
    ${refLines}
    ${axisTitles}
  </svg>`;
}

// ───────────────────────── Scatter plot ─────────────────────────

function renderScatterChart(points: ScatterPoint[], title: string, dark: boolean, xLabel = "", yLabel = "", hlines: HLine[] = []): string {
  if (!points.length) return "";

  const xs = points.map((p) => p.x);
  const ys = points.map((p) => p.y);
  // Include 0 in the range so the axes read as a real origin when the
  // data is all-positive; otherwise frame to the data extent.
  const minX = Math.min(...xs, 0), maxX = Math.max(...xs, 1);
  const minY = Math.min(...ys, 0), maxY = Math.max(...ys, 1);
  const rangeX = maxX - minX || 1;
  const rangeY = maxY - minY || 1;

  const padL = 50, padR = 26, padTop = 52, padBottom = xLabel ? 52 : 34;
  const plotW = 360, plotH = 240;
  const width = padL + plotW + padR;
  const height = padTop + plotH + padBottom;
  const stroke = dark ? "#f0f0f0" : "#202124";
  const grid = dark ? "rgba(255,255,255,0.14)" : "rgba(0,0,0,0.12)";
  const dotColor = CHART_COLORS[0];

  const xAt = (x: number) => padL + ((x - minX) / rangeX) * plotW;
  const yAt = (y: number) => padTop + plotH - ((y - minY) / rangeY) * plotH;

  // Faint gridlines on both axes (quartiles).
  const gridLines = [0.25, 0.5, 0.75]
    .map((t) => {
      const y = (padTop + plotH - t * plotH).toFixed(1);
      const x = (padL + t * plotW).toFixed(1);
      return `<line x1="${padL}" y1="${y}" x2="${padL + plotW}" y2="${y}" stroke="${grid}" stroke-width="1.5"/>` +
        `<line x1="${x}" y1="${padTop}" x2="${x}" y2="${padTop + plotH}" stroke="${grid}" stroke-width="1.5"/>`;
    })
    .join("");

  const axis = `<path d="M ${padL} ${padTop} L ${padL} ${padTop + plotH} L ${padL + plotW} ${padTop + plotH}"
        fill="none" stroke="${stroke}" stroke-width="3" stroke-linecap="round" stroke-linejoin="round"/>`;

  const dots = points
    .map(
      (p) =>
        `<circle cx="${xAt(p.x).toFixed(1)}" cy="${yAt(p.y).toFixed(1)}" r="5" fill="${dotColor}" fill-opacity="0.8" stroke="${stroke}" stroke-width="2"/>`,
    )
    .join("");

  // Min/max ticks on each axis for scale.
  const ticks = `
    <text x="${padL - 8}" y="${(yAt(maxY) + 5).toFixed(1)}" text-anchor="end"
          font-family="Patrick Hand, Caveat, sans-serif" font-size="13" fill="${stroke}">${trimNum(maxY)}</text>
    <text x="${padL - 8}" y="${(yAt(minY) + 5).toFixed(1)}" text-anchor="end"
          font-family="Patrick Hand, Caveat, sans-serif" font-size="13" fill="${stroke}">${trimNum(minY)}</text>
    <text x="${xAt(minX).toFixed(1)}" y="${padTop + plotH + 20}" text-anchor="middle"
          font-family="Patrick Hand, Caveat, sans-serif" font-size="13" fill="${stroke}">${trimNum(minX)}</text>
    <text x="${xAt(maxX).toFixed(1)}" y="${padTop + plotH + 20}" text-anchor="middle"
          font-family="Patrick Hand, Caveat, sans-serif" font-size="13" fill="${stroke}">${trimNum(maxX)}</text>`;

  const axisTitles = axisTitleSvg(xLabel, yLabel, padL, padTop, plotW, plotH, height, stroke);
  const refLines = renderHLines(hlines, yAt, minY, maxY, padL, plotW, stroke);

  return `<svg viewBox="0 0 ${width} ${height}" width="${width}" height="${height}"
        style="max-width:100%; height:auto;" role="img" aria-label="Scatter plot">
    <text x="${padL}" y="26" font-family="Patrick Hand, Caveat, sans-serif"
          font-size="24" font-weight="800" fill="${stroke}">${escape(title)}</text>
    ${gridLines}
    ${axis}
    ${ticks}
    ${refLines}
    ${dots}
    ${axisTitles}
  </svg>`;
}

// ───────────────────────── Helpers ──────────────────────────────

function trimNum(v: number): string {
  // Compact tick label — drop trailing zeros, cap at 2 decimals.
  return String(Math.round(v * 100) / 100);
}

function placeholder(dark: boolean): string {
  const c = dark ? "#aaa" : "#555";
  return `<div style="padding:18px;text-align:center;color:${c};font-family:Patrick Hand,Caveat,sans-serif;font-size:18px;">
    Empty diagram — write <code>A --&gt; B</code> flows, <code>Label: 5</code> bars, <code>stack Q1: 3, 5</code> stacked bars, <code>line Loss: 0.9, 0.6</code> lines, <code>area Users: 1, 3</code> areas, <code>pie Cats: 30</code> slices, or <code>point: 1, 2</code> scatter dots.
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
