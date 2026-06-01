# Graph Report - .  (2026-05-31)

## Corpus Check
- Corpus is ~42,518 words - fits in a single context window. You may not need a graph.

## Summary
- 218 nodes · 540 edges · 15 communities (12 shown, 3 thin omitted)
- Extraction: 95% EXTRACTED · 5% INFERRED · 0% AMBIGUOUS · INFERRED: 25 edges (avg confidence: 0.82)
- Token cost: 321,689 input · 0 output

## Community Hubs (Navigation)
- [[_COMMUNITY_Store + API Persistence|Store + API Persistence]]
- [[_COMMUNITY_Modals, Pickers & Presenter HUD|Modals, Pickers & Presenter HUD]]
- [[_COMMUNITY_Canvas & Cell Renderers|Canvas & Cell Renderers]]
- [[_COMMUNITY_Notebook State Actions|Notebook State Actions]]
- [[_COMMUNITY_Doodle Diagram Compiler|Doodle Diagram Compiler]]
- [[_COMMUNITY_Media & Whiteboard Cells|Media & Whiteboard Cells]]
- [[_COMMUNITY_Output Panel|Output Panel]]
- [[_COMMUNITY_Cell Palette Preview|Cell Palette Preview]]
- [[_COMMUNITY_App Root & Tools Page|App Root & Tools Page]]
- [[_COMMUNITY_Presentation Framing Math|Presentation Framing Math]]
- [[_COMMUNITY_Cell-to-Cell Links|Cell-to-Cell Links]]
- [[_COMMUNITY_Reveal Steps|Reveal Steps]]
- [[_COMMUNITY_Align & Distribute|Align & Distribute]]
- [[_COMMUNITY_New Notebook|New Notebook]]

## God Nodes (most connected - your core abstractions)
1. `useStore` - 56 edges
2. `App()` - 26 edges
3. `DoodleBorder()` - 23 edges
4. `useStore` - 14 edges
5. `Cell` - 13 edges
6. `CodeCell()` - 11 edges
7. `EditableTitle()` - 10 edges
8. `BrowserCell()` - 9 edges
9. `WhiteboardCell()` - 9 edges
10. `CanvasInner()` - 9 edges

## Surprising Connections (you probably didn't know these)
- `spawnPosition()` --semantically_similar_to--> `cellsInOrder`  [INFERRED] [semantically similar]
  v2/frontend/src/store.ts → store.ts
- `Root` --references--> `App()`  [EXTRACTED]
  main.tsx → v2/frontend/src/App.tsx
- `setExplain` --shares_data_with--> `Callout`  [INFERRED]
  store.ts → v2/frontend/src/types.ts
- `runCell` --shares_data_with--> `CellRuntime`  [INFERRED]
  store.ts → v2/frontend/src/types.ts
- `App()` --calls--> `addBrowserCell`  [EXTRACTED]
  v2/frontend/src/App.tsx → store.ts

## Import Cycles
- None detected.

## Hyperedges (group relationships)
- **Notebook persistence round-trip (store + api + types)** — src_store_downloadnotebook, src_store_loadnotebookfromtext, src_api_savenotebook, src_api_opennotebook, src_types_cell [INFERRED 0.85]
- **Presentation focus + framing flow** — src_store_cellsinorder, src_store_nextcell, src_store_setpresenting, lib_present_slidecentery, lib_present_progressfraction [INFERRED 0.75]
- **Reveal-step authoring, advance, and effective-source run** — src_store_setreveals, src_store_revealnext, lib_reveal_effectivesource, src_store_runcell [INFERRED 0.85]
- **ReactFlow cell-node renderer family** — components_codecell_codecell, components_browsercell_browsercell, components_diagramcell_diagramcell, components_calloutbubble_calloutbubble [INFERRED 0.85]
- **DoodleBorder hand-drawn frame consumers** — components_codecell_codecell, components_browsercell_browsercell, components_diagramcell_diagramcell, components_calloutbubble_calloutbubble, components_callouteditor_callouteditor, components_cellpalette_cellpalette [INFERRED 0.80]
- **Callout bubble / editor / source-cell triangle** — components_calloutbubble_calloutbubble, components_callouteditor_callouteditor, components_codecell_codecell [INFERRED 0.75]
- **Singleton store-driven local-draft editor modals** — components_noteeditor_noteeditor, components_revealeditor_revealeditor, components_installmodal_installmodal [INFERRED 0.85]
- **Presenter HUD overlay family (coordinate presenting state + focused slide)** — components_presenterbar_presenterbar, components_presenteroverlay_presenteroverlay, components_presenterprogress_presenterprogress, components_presenternotes_presenternotes [INFERRED 0.85]
- **Pointer-capture ref-driven drawing surfaces** — components_whiteboardcell_whiteboardcell, components_presenteroverlay_presenteroverlay, components_resizehandle_resizehandle [INFERRED 0.75]

## Communities (15 total, 3 thin omitted)

### Community 0 - "Store + API Persistence"
Cohesion: 0.09
Nodes (28): effectiveSource(), revealCount(), executeCode(), installPackages(), InstallResponse, interruptKernel(), openNotebook(), OpenResponse (+20 more)

### Community 1 - "Modals, Pickers & Presenter HUD"
Cohesion: 0.12
Nodes (27): AmbientLayer(), Shape, THEMES, AmbientPicker(), CalloutEditor(), CellPalette(), EmptyNotebookHint(), FileMenu() (+19 more)

### Community 2 - "Canvas & Cell Renderers"
Cohesion: 0.11
Nodes (21): BrowserCell(), unwrapProxied(), CalloutBubble(), Canvas(), CanvasInner(), CELL_WIDTH_FALLBACK, nodeTypes, CodeCell() (+13 more)

### Community 3 - "Notebook State Actions"
Cohesion: 0.13
Nodes (24): App(), addBrowserCell, addCell, addDiagramCell, addMarkdownCell, addMediaCell, addWhiteboardCell, cellsInOrder (+16 more)

### Community 4 - "Doodle Diagram Compiler"
Cohesion: 0.16
Nodes (16): CHART_COLORS, ChartItem, escape(), FLOW_COLORS, FlowEdge, LineSeries, Parsed, parseDoodleDiagram() (+8 more)

### Community 5 - "Media & Whiteboard Cells"
Cohesion: 0.16
Nodes (12): MediaCell(), vimeoEmbed(), youTubeEmbed(), ResizeHandle(), BG_COLOR, COLORS, hitStroke(), Stroke (+4 more)

### Community 6 - "Output Panel"
Cohesion: 0.43
Nodes (5): clampText(), OutputItem(), Outputs(), Outputs.test, CellOutput

### Community 7 - "Cell Palette Preview"
Cohesion: 0.43
Nodes (3): KIND_ICON, firstLine(), hostOf()

### Community 8 - "App Root & Tools Page"
Cohesion: 0.38
Nodes (4): ThemeToggle(), Root, PptResult, ToolsPage()

### Community 9 - "Presentation Framing Math"
Cohesion: 0.67
Nodes (3): progressFraction(), slideCenterY(), topFractionOf()

### Community 10 - "Cell-to-Cell Links"
Cohesion: 1.00
Nodes (3): linkCells, toggleLinkSelected, unlinkCells

## Knowledge Gaps
- **44 isolated node(s):** `Ping`, `SaveResponse`, `InstallResponse`, `OutputType`, `CellKind` (+39 more)
  These have ≤1 connection - possible missing edges or undocumented components.
- **3 thin communities (<3 nodes) omitted from report** — run `graphify query` to explore isolated nodes.

## Suggested Questions
_Questions this graph is uniquely positioned to answer:_

- **Why does `useStore` connect `Modals, Pickers & Presenter HUD` to `Store + API Persistence`, `Canvas & Cell Renderers`, `Notebook State Actions`, `Media & Whiteboard Cells`, `Cell Palette Preview`, `App Root & Tools Page`, `Presentation Framing Math`?**
  _High betweenness centrality (0.283) - this node is a cross-community bridge._
- **Why does `App()` connect `Notebook State Actions` to `Store + API Persistence`, `Modals, Pickers & Presenter HUD`, `App Root & Tools Page`?**
  _High betweenness centrality (0.168) - this node is a cross-community bridge._
- **Why does `DoodleBorder()` connect `Canvas & Cell Renderers` to `Store + API Persistence`, `Modals, Pickers & Presenter HUD`, `Media & Whiteboard Cells`, `Cell Palette Preview`, `App Root & Tools Page`?**
  _High betweenness centrality (0.037) - this node is a cross-community bridge._
- **What connects `Ping`, `SaveResponse`, `InstallResponse` to the rest of the system?**
  _44 weakly-connected nodes found - possible documentation gaps or missing edges._
- **Should `Store + API Persistence` be split into smaller, more focused modules?**
  _Cohesion score 0.08826945412311266 - nodes in this community are weakly interconnected._
- **Should `Modals, Pickers & Presenter HUD` be split into smaller, more focused modules?**
  _Cohesion score 0.12179487179487179 - nodes in this community are weakly interconnected._
- **Should `Canvas & Cell Renderers` be split into smaller, more focused modules?**
  _Cohesion score 0.11201079622132254 - nodes in this community are weakly interconnected._