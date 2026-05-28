# Diagram + Chart Blocks Explanation

This file explains the source code that powers the doodle-style Diagram + Chart block in the Doodle Code Presenter app.

## Source Files

- `public/diagramBlocks.js` contains the complete diagram and chart compiler.
- `public/app.js` imports `renderDoodleDiagramBlocks()` and uses it to render the Diagram + Chart tab.
- `public/styles.css` contains the visual styling for `.diagram-preview`, `.flow-svg`, and `.chart-svg`.

## What The Block Does

The Diagram + Chart block takes a small text format and compiles it into inline SVG. Inline SVG was chosen because it is portable, responsive, easy to style, and does not require a charting dependency.

Example input:

```text
flowchart
Idea --> Markdown
Idea --> Whiteboard
Markdown --> Presentation
Whiteboard --> Presentation
Presentation --> Python

chart: Demo energy
Markdown: 8
Whiteboard: 9
Browser: 6
Python: 10
```

The compiler reads two kinds of lines:

- Flow lines use `From --> To`.
- Chart lines use `Label: Number`.

The `chart: Demo energy` line sets the bar chart title. The `flowchart` line is accepted as a friendly header so the syntax feels close to Mermaid.

## Main Functions

`parseDiagramBlocks(source)` converts text into structured data:

```js
{
  flow: [{ from: "Idea", to: "Markdown" }],
  charts: [{ label: "Markdown", value: 8 }],
  chartTitle: "Demo energy"
}
```

`renderDoodleFlow(edges, idSeed)` takes the parsed flow edges and returns an SVG flowchart.

`renderDoodleChart(items, title)` takes chart values and returns an SVG bar chart.

`renderDoodleDiagramBlocks(source, options)` is the public function used by the app. It parses the source, renders the flowchart, renders the chart, and joins both SVG strings together.

## How The Doodle Flowchart Is Created

The flowchart starts by collecting every unique node name from all `from` and `to` values. Then it places nodes into a simple three-column grid:

- Each node has a fixed width of `150`.
- Each node has a fixed height of `58`.
- Horizontal and vertical gaps create whiteboard-like breathing room.
- The SVG `viewBox` is calculated from the number of rows and columns.

Connections are drawn with cubic Bezier paths:

```text
M startX startY C midX upperY, midX lowerY, endX endY
```

That curved connector is what makes the diagram feel hand-drawn instead of rigid. Each line uses a dark stroke, a thick width, and an arrow marker.

Nodes are rendered as SVG rectangles with:

- Thick dark borders.
- Small corner radius.
- Alternating soft fills.
- Bold centered text.

The app also creates a stable unique arrow marker id with `stableId()` so multiple diagrams can exist on the page without marker collisions.

## How The Doodle Chart Is Created

The chart renderer calculates the maximum chart value, then scales every bar relative to that maximum:

```js
const w = 420 * item.value / max;
```

Each chart row contains:

- A left-side label.
- A colored SVG rectangle for the bar.
- A numeric value at the end of the bar.

The bars use the same thick dark stroke as the flowchart nodes. The colors rotate through coral, mint, blue, and gold so the chart feels playful without becoming one-note.

## How The Doodle Style Works

The doodle look is made from several choices working together:

- The app uses a casual handwritten font stack: `"Comic Sans MS", "Trebuchet MS", system-ui, sans-serif`.
- SVG lines use thick dark strokes, usually `stroke-width="3"`.
- Diagram containers use dashed borders through `.flow-svg` and `.chart-svg`.
- The page background uses a faint grid to feel like sketch paper.
- Cards and panels use bold borders and offset shadows.
- Nodes use soft pastel fills instead of flat corporate colors.
- Curved arrows make connections feel drawn by hand.

The important part is that the code does not need a canvas for the diagram. It creates normal SVG markup, then CSS makes that SVG feel like it belongs inside the doodle presentation surface.

## Supported Syntax

Flowchart:

```text
flowchart
Start --> Draft
Draft --> Review
Review --> Present
```

Bar chart:

```text
chart: Sprint confidence
Design: 7
Frontend: 9
Backend: 8
Demo: 10
```

Combined block:

```text
flowchart
Input --> Compiler
Compiler --> SVG
SVG --> Doodle View

chart: Build status
Parser: 9
Renderer: 10
Styles: 8
```

## How To Reuse It

Import the module:

```js
import { renderDoodleDiagramBlocks } from "./diagramBlocks.js";
```

Render text into a container:

```js
const source = `flowchart
Idea --> Diagram

chart: Score
Idea: 8
Diagram: 10`;

document.querySelector("#diagramPreview").innerHTML = renderDoodleDiagramBlocks(source);
```

For repeated diagrams on one page, pass a stable id seed:

```js
renderDoodleDiagramBlocks(source, { idSeed: "slide-1" });
```

## Current Limitations

- Flowchart layout is simple and grid-based.
- It supports `-->` arrows, not the full Mermaid grammar.
- Chart blocks currently render as horizontal bar charts only.
- Very long node labels may need wrapping in a future version.

Those limits are intentional for the first version: the block is small, readable, dependency-free, and easy to extend.
