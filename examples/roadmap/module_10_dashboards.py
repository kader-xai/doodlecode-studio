# doodlecode format-version: 2
# Auto-converted from module_10_dashboards.ipynb
# Open with 📂 Open → press 🎬 Present.


# %% [markdown] color=rose title="Module 10 Dashboards"
# # Module 10 Dashboards
#
# A live walkthrough — one card per concept.
# Use → / ← to step through. Press 🎬 Present to begin.



# %% [markdown] color=sky title="Module 10 — Dashboards & Final Project"
# # Module 10 — Dashboards & Final Project
#
# *IBM Data Visualization · Module 5 of 5 (Module 10 of 16)*
#
# A dashboard is **several charts arranged to answer one business question**. The hard part isn't the charts — it's picking the question.
#
# ### What you'll cover
# 1. The dashboard mental model — start with the question
# 2. Static dashboards with `matplotlib` subplots
# …


# %% color=mint title="!pip -q install pandas numpy matplotlib seaborn…"
# @explain: Run this cell to see the output.
!pip -q install pandas numpy matplotlib seaborn plotly dash


# %% [markdown] color=peach title="1. The dashboard mental model"
# # 1. The dashboard mental model
#
# Bad dashboards add charts until the page is full. Good dashboards answer **one question** with the **fewest charts** that make the answer obvious.
#
# ### Six-step recipe
# 1. **State the question** ("Are we growing?", "Which segment is leaking customers?")
# 2. **Pick the headline number** — one figure that summarises the answer.
# 3. **Pick the trend** — does it move with time?
# …


# %% [markdown] color=violet title="2. Static dashboard — matplotlib subplots"
# # 2. Static dashboard — matplotlib subplots
#
# A static dashboard is a single figure with a thoughtful subplot grid. Use this when the audience reads a PDF or printout.


# %% color=amber title="Synthetic sales data"
# @explain: Synthetic sales data
import numpy as np, pandas as pd, matplotlib.pyplot as plt
rng = np.random.default_rng(7)

# Synthetic sales data
dates  = pd.date_range("2024-01-01", periods=180)
sales = pd.DataFrame({
    "date":     dates,
    "channel":  rng.choice(["Online","Retail","Wholesale"], 180, p=[.5,.3,.2]),
    "amount":   rng.lognormal(4.5, .3, 180).round(2),
    "region":   rng.choice(["North","South","East","West"], 180),
})
sales["month"] = sales["date"].dt.to_period("M").dt.to_timestamp()
sales.head()


# %% color=rose title="Build the dashboard"
# @explain: Build the dashboard — 2x3 grid, each chart with one job
# @explain: headline: total sales, trend
# @explain: trend
# @explain: channel mix
# @explain: region breakdown
# Build the dashboard — 2x3 grid, each chart with one job.
fig, axes = plt.subplots(2, 3, figsize=(15, 7))
fig.suptitle("Sales dashboard — H1 2024", fontsize=15, fontweight="bold")

# headline: total sales, trend
total = sales["amount"].sum()
axes[0,0].text(0.5, 0.5, f"${total:,.0f}", ha="center", va="center",
               fontsize=30, fontweight="bold", color="#1f77b4",
               transform=axes[0,0].transAxes)
axes[0,0].text(0.5, 0.18, "Total revenue", ha="center", fontsize=11,
               color="grey", transform=axes[0,0].transAxes)
axes[0,0].axis("off")

# trend
sales.groupby("month")["amount"].sum().plot(ax=axes[0,1], marker="o",
                                             title="Revenue by month")
axes[0,1].set_ylabel("$")

# channel mix
sales.groupby("channel")["amount"].sum().sort_values()     .plot.barh(ax=axes[0,2], color="steelblue", title="Revenue by channel")

# region breakdown
sales.groupby("region")["amount"].sum().sort_values(ascending=False)     .plot.bar(ax=axes[1,0], color="darkorange", title="Revenue by region", rot=0)

# distribution of order sizes
sales["amount"].plot.hist(bins=30, ax=axes[1,1], color="grey",
                           title="Distribution of order sizes")
axes[1,1].axvline(sales["amount"].median(), color="red", linestyle="--",
                  label=f"median=${sales.amount.median():.0f}")
axes[1,1].legend()

# top 10 days
sales.groupby("date")["amount"].sum().nlargest(10).sort_values()     .plot.barh(ax=axes[1,2], color="#2ca02c", title="Top 10 sales days")

plt.tight_layout(rect=[0, 0, 1, 0.96])
plt.show()


# %% [markdown] color=lime title="3. Interactive dashboard — Plotly + Dash (concept)"
# # 3. Interactive dashboard — Plotly + Dash (concept)
#
# For a *web* dashboard with filters and dropdowns, use **Plotly Dash**. The pattern is small:
#
# 1. Define the layout (HTML + Plotly graphs).
# 2. Define **callbacks** — functions that recompute a chart when an input changes.
#
# > Dash runs a local web server. In Colab you call `app.run_server(mode="inline")` to embed it in the notebook.


# %% color=teal title="import plotly.express as px"
# @explain: Run this cell to see the output.
import plotly.express as px
fig = px.bar(sales.groupby(["month","channel"])["amount"].sum().reset_index(),
             x="month", y="amount", color="channel",
             title="Plotly — interactive stacked bar by channel")
fig.show()


# %% color=sky title="Minimal Dash app"
# @explain: Minimal Dash app — note: only runs in Colab if jupyter-dash is installed
# @explain: Concept-only; uncomment to try locally
# @explain: app.run_server(mode='inline')   # uncomment in Jupyter+jupyter-dash
# Minimal Dash app — note: only runs in Colab if jupyter-dash is installed
# Concept-only; uncomment to try locally.
"""
from dash import Dash, dcc, html, Input, Output

app = Dash(__name__)
app.layout = html.Div([
    html.H2("Sales explorer"),
    dcc.Dropdown(id="channel",
                 options=[{"label": c, "value": c} for c in sales.channel.unique()],
                 value="Online"),
    dcc.Graph(id="chart"),
])

@app.callback(Output("chart","figure"), Input("channel","value"))
def update(ch):
    sub = sales[sales.channel == ch]
    return px.line(sub.groupby("date")["amount"].sum().reset_index(),
                   x="date", y="amount", title=f"{ch} — daily")

# app.run_server(mode='inline')   # uncomment in Jupyter+jupyter-dash
"""
print("Dash code shown as a string — see comments to run locally.")


# %% [markdown] color=mint title="4. Case study — narrative across the dashboard"
# # 4. Case study — narrative across the dashboard
#
# Read the dashboard above as a 30-second elevator pitch:
#
# > *"Total H1 revenue was \$X. We grew from January to March, then plateaued in Q2. The growth came from **Online**, which now beats Retail. **South** is our largest region, and the order-size distribution shows a long tail — a few large orders move the headline. Top sales days cluster in March."*
#
# Every sentence above maps to one chart. **That's the goal**: every chart earns its place by adding one sentence to the story.


# %% [markdown] color=peach title="5. Data storytelling — three rules"
# # 5. Data storytelling — three rules
#
# 1. **Lead with the headline.** First chart = the answer to the question.
# 2. **One idea per chart.** If you're tempted to add a second axis or third series, ask "is this still about one idea?"
# 3. **Annotate the takeaway.** Don't make the reader infer it.
#
# A dashboard without annotations is a coffee-table picture. With annotations it becomes a memo.


# %% [markdown] color=violet title="6. Practice — build your own dashboard"
# # 6. Practice — build your own dashboard
#
# Use the `sales` dataframe from this module to answer:
#
# > *"Which channel × region combination has the strongest growth in the second half of the period?"*
#
# Suggested layout:
# - Headline number: total revenue in the second half vs first half
# …


# %% color=amber title="Heatmap channel × region"
# @explain: Heatmap channel × region (full period)
half = len(sales) // 2
first_half  = sales.iloc[:half]
second_half = sales.iloc[half:]

# Heatmap channel × region (full period)
heat = sales.pivot_table(index="region", columns="channel", values="amount", aggfunc="sum")

import seaborn as sns, matplotlib.pyplot as plt
fig, ax = plt.subplots(1, 2, figsize=(13, 4))
sns.heatmap(heat, annot=True, fmt=".0f", cmap="YlGnBu", ax=ax[0])
ax[0].set_title("Revenue by region × channel (H1)")

growth = second_half.groupby(["channel","region"])["amount"].sum() -          first_half.groupby(["channel","region"])["amount"].sum()
top3 = growth.sort_values(ascending=False).head(3)
top3.plot.barh(ax=ax[1], color="#2ca02c", title="Top 3 channel×region by growth (Q2 − Q1)")
ax[1].set_xlabel("revenue change ($)")
plt.tight_layout(); plt.show()
print(top3)


# %% [markdown] color=rose title="Recap — what you can now do"
# # Recap — what you can now do
#
# ✅ Pick the *one question* a dashboard should answer
# ✅ Lay out a static dashboard with subplots
# ✅ Drop into Plotly/Dash for interactive web dashboards
# ✅ Tell a 30-second story across a multi-chart figure
#
# ### Halfway point
# …


# %% [markdown] color=lime title="Thanks"
# # End of Module
#
# Next module continues the roadmap.
# Source: https://github.com/kader-xai/data-science-roadmap


