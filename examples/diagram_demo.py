# doodlecode format-version: 2
# Diagram demo — exercises the three renderers (Mermaid / KaTeX / Chart)
# and the # @step layered-reveal markers.
# Open with 📂 Open → 🎬 Present.


# %% [markdown] color=rose title="Diagram demo"
# # 🧭 Diagram cells, three flavors
#
# - **Mermaid** for graphs, trees, mindmaps, flowcharts.
# - **KaTeX** for LaTeX math (matrices, equations).
# - **Chart** (sketchy roughjs) for bar / line / pie.
#
# Each can be split into reveal layers with `# @step N` markers — the
# right-arrow advances one layer at a time before moving on.


# %% [markdown] color=violet title="Mermaid · layered transformer"
# @cell_type: diagram
# @diagram_kind: mermaid
# @step 1
graph LR
  X[Input tokens] --> E[Embeddings]
# @step 2
  E --> A[Self-attention]
  A --> F[Feed-forward]
# @step 3
  F --> O[Output logits]
  O --> S[Softmax]
# @step 4
  S --> P[Predicted token]


# %% [markdown] color=violet title="Mermaid · ML pipeline"
# @cell_type: diagram
# @diagram_kind: mermaid
graph TB
  D[Raw data] --> C[Clean]
  C --> F[Feature engineer]
  F --> T{Train / Eval split}
  T -->|train| M[Fit model]
  T -->|eval|  V[Validate]
  M --> V
  V --> R[Report]


# %% [markdown] color=violet title="Math · matrix multiplication, step by step"
# @cell_type: diagram
# @diagram_kind: math
# @step 1
A = \begin{bmatrix} 1 & 2 \\ 3 & 4 \end{bmatrix}, \quad
b = \begin{bmatrix} 5 \\ 6 \end{bmatrix}
# @step 2
A b = \begin{bmatrix} (1)(5) + (2)(6) \\ (3)(5) + (4)(6) \end{bmatrix}
# @step 3
A b = \begin{bmatrix} 5 + 12 \\ 15 + 24 \end{bmatrix}
    = \begin{bmatrix} 17 \\ 39 \end{bmatrix}


# %% [markdown] color=violet title="Math · gradient descent rule"
# @cell_type: diagram
# @diagram_kind: math
\theta_{t+1} = \theta_t - \eta \, \nabla_\theta \mathcal{L}(\theta_t)

\mathcal{L}(\theta) = \frac{1}{N} \sum_{i=1}^{N} \ell\big(f_\theta(x_i),\, y_i\big)


# %% [markdown] color=violet title="Chart · language popularity (sketchy)"
# @cell_type: diagram
# @diagram_kind: chart
{
  "type": "bar",
  "title": "Stars (k) — illustrative",
  "data": [
    ["Python", 82],
    ["JavaScript", 74],
    ["Rust", 38],
    ["Go", 41],
    ["Java", 29],
    ["TypeScript", 56]
  ]
}


# %% [markdown] color=violet title="Chart · loss curve (line)"
# @cell_type: diagram
# @diagram_kind: chart
{
  "type": "line",
  "title": "Training loss",
  "data": [
    ["ep1", 2.41],
    ["ep2", 1.82],
    ["ep3", 1.27],
    ["ep4", 0.93],
    ["ep5", 0.71],
    ["ep6", 0.58],
    ["ep7", 0.49]
  ]
}


# %% [markdown] color=violet title="Chart · token mix (pie)"
# @cell_type: diagram
# @diagram_kind: chart
{
  "type": "pie",
  "title": "Token type distribution",
  "data": [
    ["Words", 62],
    ["Punctuation", 18],
    ["Numbers", 8],
    ["Special", 12]
  ]
}


# %% [markdown] color=lime title="Recap"
# # 🧭 Recap
#
# - **＋ Diagram** in the toolbar creates a diagram cell.
# - **✏️ Edit** in the toolbar action bar opens the source editor —
#   pick **Mermaid / Math / Chart** from the dropdown, write notation
#   in the textarea, hit Save.
# - **`# @step N`** markers split the source into reveal layers.
# - During **🎬 Present**, → advances the next step on a diagram
#   slide; only once you've reached the last step does → move on.
