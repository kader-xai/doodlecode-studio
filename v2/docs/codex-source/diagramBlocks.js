const FLOW_COLORS = ["#fff2c6", "#dff7ee", "#ffe2e8", "#e8eeff"];
const CHART_COLORS = ["#e85d75", "#1f9d8a", "#3867d6", "#f2b544"];

function escapeHtml(value) {
  return String(value).replace(/[&<>"']/g, (char) => ({
    "&": "&amp;",
    "<": "&lt;",
    ">": "&gt;",
    '"': "&quot;",
    "'": "&#039;"
  })[char]);
}

function stableId(value) {
  let hash = 0;
  for (let index = 0; index < value.length; index += 1) {
    hash = ((hash << 5) - hash + value.charCodeAt(index)) | 0;
  }
  return Math.abs(hash).toString(36);
}

export function parseDiagramBlocks(source) {
  const lines = source.split("\n").map((line) => line.trim()).filter(Boolean);
  const flow = [];
  const charts = [];
  let chartTitle = "";

  for (const line of lines) {
    const normalized = line.toLowerCase();

    if (normalized === "flowchart" || normalized.startsWith("graph ")) {
      continue;
    }

    if (normalized.startsWith("chart:")) {
      chartTitle = line.split(":").slice(1).join(":").trim() || "Chart";
      continue;
    }

    if (line.includes("-->")) {
      const [from, to] = line.split("-->").map((part) => part.trim());
      if (from && to) flow.push({ from, to });
      continue;
    }

    if (line.includes(":")) {
      const [label, raw] = line.split(":");
      const value = Number(raw.trim());
      if (label.trim() && Number.isFinite(value)) {
        charts.push({ label: label.trim(), value });
      }
    }
  }

  return { flow, charts, chartTitle };
}

export function renderDoodleFlow(edges, idSeed = "flow") {
  if (!edges.length) return "";

  const labels = [...new Set(edges.flatMap((edge) => [edge.from, edge.to]))];
  const cols = Math.min(3, Math.max(1, labels.length));
  const nodeW = 150;
  const nodeH = 58;
  const gapX = 74;
  const gapY = 58;
  const positions = new Map();
  const arrowId = `arrow-${stableId(idSeed + JSON.stringify(edges))}`;

  labels.forEach((label, index) => {
    const col = index % cols;
    const row = Math.floor(index / cols);
    positions.set(label, {
      x: 40 + col * (nodeW + gapX),
      y: 38 + row * (nodeH + gapY)
    });
  });

  const rows = Math.ceil(labels.length / cols);
  const width = 40 + cols * nodeW + (cols - 1) * gapX + 40;
  const height = 38 + rows * nodeH + (rows - 1) * gapY + 42;

  const paths = edges.map((edge) => {
    const a = positions.get(edge.from);
    const b = positions.get(edge.to);
    const x1 = a.x + nodeW;
    const y1 = a.y + nodeH / 2;
    const x2 = b.x;
    const y2 = b.y + nodeH / 2;
    const mid = (x1 + x2) / 2;

    return `<path d="M ${x1} ${y1} C ${mid} ${y1 - 18}, ${mid} ${y2 + 18}, ${x2 - 10} ${y2}" fill="none" stroke="#202124" stroke-width="3" marker-end="url(#${arrowId})"/>`;
  }).join("");

  const nodes = labels.map((label, index) => {
    const pos = positions.get(label);
    const fill = FLOW_COLORS[index % FLOW_COLORS.length];

    return `<g>
      <rect x="${pos.x}" y="${pos.y}" width="${nodeW}" height="${nodeH}" rx="8" fill="${fill}" stroke="#202124" stroke-width="3"/>
      <text x="${pos.x + nodeW / 2}" y="${pos.y + 36}" text-anchor="middle" font-size="16" font-weight="800" fill="#202124">${escapeHtml(label)}</text>
    </g>`;
  }).join("");

  return `<svg class="flow-svg" viewBox="0 0 ${width} ${height}" role="img" aria-label="Flowchart">
    <defs>
      <marker id="${arrowId}" markerWidth="10" markerHeight="10" refX="8" refY="3" orient="auto" markerUnits="strokeWidth">
        <path d="M0,0 L0,6 L9,3 z" fill="#202124"></path>
      </marker>
    </defs>
    ${paths}
    ${nodes}
  </svg>`;
}

export function renderDoodleChart(items, title = "Chart") {
  if (!items.length) return "";

  const max = Math.max(...items.map((item) => item.value), 1);
  const barH = 34;
  const gap = 18;
  const width = 680;
  const height = 82 + items.length * (barH + gap);

  const bars = items.map((item, index) => {
    const w = 420 * item.value / max;
    const y = 62 + index * (barH + gap);
    const color = CHART_COLORS[index % CHART_COLORS.length];

    return `<g>
      <text x="24" y="${y + 23}" font-size="15" font-weight="800" fill="#202124">${escapeHtml(item.label)}</text>
      <rect x="160" y="${y}" width="${w}" height="${barH}" rx="6" fill="${color}" stroke="#202124" stroke-width="3"/>
      <text x="${174 + w}" y="${y + 23}" font-size="15" font-weight="900" fill="#202124">${item.value}</text>
    </g>`;
  }).join("");

  return `<svg class="chart-svg" viewBox="0 0 ${width} ${height}" role="img" aria-label="Bar chart">
    <text x="24" y="36" font-size="24" font-weight="900" fill="#202124">${escapeHtml(title)}</text>
    ${bars}
  </svg>`;
}

export function renderDoodleDiagramBlocks(source, options = {}) {
  const parsed = parseDiagramBlocks(source);
  return [
    renderDoodleFlow(parsed.flow, options.idSeed || source),
    renderDoodleChart(parsed.charts, parsed.chartTitle || "Chart")
  ].join("");
}
