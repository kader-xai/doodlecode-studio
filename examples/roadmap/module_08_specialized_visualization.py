# doodlecode format-version: 2
# Auto-converted from module_08_specialized_visualization.ipynb
# Open with 📂 Open → press 🎬 Present.


# %% [markdown] color=rose title="Module 08 Specialized Visualization"
# # Module 08 Specialized Visualization
#
# A live walkthrough — one card per concept.
# Use → / ← to step through. Press 🎬 Present to begin.



# %% [markdown] color=sky title="Module 8 — Specialized Visualization Tools"
# # Module 8 — Specialized Visualization Tools
#
# *IBM Data Visualization · Module 3 of 5 (Module 8 of 16)*
#
# The basic charts cover most cases. This module covers the **specialised** ones — narrower in use, but high-impact when they fit.
#
# ### What you'll cover
# 1. Waffle charts — share-of-whole as a 10×10 grid
# 2. Word clouds — text frequency as a picture
# …


# %% color=mint title="!pip -q install pandas numpy matplotlib seaborn…"
# @explain: Run this cell to see the output.
!pip -q install pandas numpy matplotlib seaborn wordcloud folium requests pywaffle
import pandas as pd, numpy as np, matplotlib.pyplot as plt


# %% [markdown] color=peach title="1. Waffle charts — share of whole, square-by-square"
# # 1. Waffle charts — share of whole, square-by-square
#
# A waffle chart is a 10×10 grid where each square represents 1% of the total. Easier to compare than a pie because you can count squares.


# %% color=violet title="from pywaffle import Waffle"
# @explain: Run this cell to see the output.
from pywaffle import Waffle

skills = {"Python": 45, "SQL": 25, "Excel": 20, "Other": 10}

fig = plt.figure(FigureClass=Waffle, rows=10, columns=10,
                 values=skills, figsize=(7, 4),
                 legend={"loc":"lower center", "bbox_to_anchor":(0.5,-0.15), "ncol":4},
                 title={"label":"Skill mix (each square = 1%)", "fontsize":13})
plt.show()


# %% [markdown] color=amber title="2. Word clouds — visualising text frequency"
# # 2. Word clouds — visualising text frequency
#
# Word size = word frequency. Great for quick "what's this corpus about?" questions; not great for precise comparison.


# %% color=rose title="from wordcloud import WordCloud"
# @explain: Run this cell to see the output.
from wordcloud import WordCloud

text = ("data science python pandas numpy matplotlib seaborn scikit-learn " * 30 +
        "regression classification clustering visualization analysis " * 15 +
        "tensor gradient descent neural network deep learning " * 10)

wc = WordCloud(width=800, height=400, background_color="white",
               colormap="viridis").generate(text)
plt.figure(figsize=(10, 5)); plt.imshow(wc); plt.axis("off")
plt.title("Word cloud"); plt.show()


# %% [markdown] color=lime title="From a real dataframe — Wikipedia article"
# # From a real dataframe — Wikipedia article
#


# %% color=teal title="import requests"
# @explain: Run this cell to see the output.
import requests, re
from collections import Counter

html = requests.get("https://en.wikipedia.org/wiki/Data_science", timeout=10).text
words = re.findall(r"[A-Za-z]{4,}", html.lower())
stop = {"this","that","with","from","have","data","which","they","were","been","also"}
words = [w for w in words if w not in stop]
freq = Counter(words).most_common(120)
wc = WordCloud(width=900, height=400, background_color="white").generate_from_frequencies(dict(freq))
plt.figure(figsize=(10,4)); plt.imshow(wc); plt.axis("off")
plt.title("Words on the 'Data science' Wikipedia page"); plt.show()


# %% [markdown] color=sky title="3. Regression plot — line + confidence band"
# # 3. Regression plot — line + confidence band
#
# `seaborn.regplot` fits a regression line to a scatter and shades the 95% CI.


# %% color=mint title="import seaborn as sns"
# @explain: Run this cell to see the output.
import seaborn as sns
rng = np.random.default_rng(0)
df = pd.DataFrame({"x": rng.normal(0, 1, 100)})
df["y"] = 2*df["x"] + 1 + rng.normal(0, 0.5, 100)

fig, ax = plt.subplots(figsize=(7, 4))
sns.regplot(data=df, x="x", y="y", ax=ax,
            scatter_kws={"alpha":.6}, line_kws={"color":"red"})
ax.set_title("Regression plot: y = 2x + 1 + noise"); plt.show()


# %% [markdown] color=peach title="`lmplot` — same idea, but split by a category"
# # `lmplot` — same idea, but split by a category
#


# %% color=violet title="rng = np.random.default_rng(1)"
# @explain: Run this cell to see the output.
rng = np.random.default_rng(1)
df2 = pd.concat([
    pd.DataFrame({"x": rng.normal(0,1,100), "y": 2*rng.normal(0,1,100)+1, "group":"A"}),
    pd.DataFrame({"x": rng.normal(0,1,100), "y": -1*rng.normal(0,1,100)+1, "group":"B"}),
])
sns.lmplot(data=df2, x="x", y="y", hue="group", height=4, aspect=1.4)
plt.show()


# %% [markdown] color=amber title="4. Correlation heatmap"
# # 4. Correlation heatmap
#
# A heatmap of a correlation matrix surfaces the 2-3 features that move together.


# %% color=rose title="rng = np.random.default_rng(0)"
# @explain: Run this cell to see the output.
rng = np.random.default_rng(0)
df3 = pd.DataFrame(rng.normal(0, 1, (200, 5)), columns=list("ABCDE"))
df3["F"] = df3["A"] + 0.5 * df3["B"] + rng.normal(0, .3, 200)   # F correlated with A and B

fig, ax = plt.subplots(figsize=(6, 5))
sns.heatmap(df3.corr(), annot=True, fmt=".2f", cmap="coolwarm", center=0, ax=ax)
ax.set_title("Correlation heatmap"); plt.show()


# %% [markdown] color=lime title="5. Folium — interactive maps"
# # 5. Folium — interactive maps
#
# Folium renders Leaflet.js maps directly in a Jupyter cell.


# %% color=teal title="import folium"
# @explain: Run this cell to see the output.
import folium
m = folium.Map(location=[24.7136, 46.6753], zoom_start=11)   # Riyadh

folium.Marker([24.7136, 46.6753], popup="Riyadh — capital",
              icon=folium.Icon(color="red")).add_to(m)
folium.Marker([24.6877, 46.7219], popup="Olaya district").add_to(m)
folium.CircleMarker([24.7743, 46.7386], radius=20,
                    color="orange", fill=True, popup="Diplomatic Quarter").add_to(m)
m


# %% [markdown] color=sky title="Marker cluster — when you have hundreds of points"
# # Marker cluster — when you have hundreds of points
#


# %% color=mint title="from folium.plugins import MarkerCluster"
# @explain: Run this cell to see the output.
from folium.plugins import MarkerCluster
import numpy as np
m = folium.Map(location=[24.7, 46.7], zoom_start=10)
mc = MarkerCluster().add_to(m)
rng = np.random.default_rng(0)
for lat, lon in zip(rng.uniform(24.5, 24.9, 200), rng.uniform(46.5, 46.9, 200)):
    folium.Marker([lat, lon]).add_to(mc)
m


# %% [markdown] color=peach title="6. Choropleth — colouring regions by a value"
# # 6. Choropleth — colouring regions by a value
#
# A choropleth ("kor-O-pleth") colours each region of a map according to some numeric variable. You need a **GeoJSON** describing the region shapes plus a DataFrame mapping region → value.


# %% color=violet title="import folium"
# @explain: Run this cell to see the output.
import folium, requests, random, pandas as pd

geo = requests.get(
    "https://raw.githubusercontent.com/python-visualization/folium/main/tests/us-states.json",
    timeout=10).json()

random.seed(0)
data = pd.DataFrame([{"State": f["properties"]["name"],
                      "score": random.randint(0, 100)} for f in geo["features"]])

m = folium.Map(location=[39.8, -98.6], zoom_start=4)
folium.Choropleth(geo_data=geo, data=data,
                  columns=["State","score"],
                  key_on="feature.properties.name",
                  fill_color="YlOrRd", fill_opacity=0.7,
                  legend_name="Score (0-100)").add_to(m)
m


# %% [markdown] color=amber title="7. Practice"
# # 7. Practice
#
# 1. Build a waffle chart of your own time allocation across 4 activities (must sum to 100).
# 2. Make a word cloud from the text of a Wikipedia article of your choice (replace the URL).
# 3. Plot a regression of `mpg` vs `weight` for the auto-mpg dataset (URL provided).
# 4. Place 5 markers in your country on a Folium map.


# %% color=rose title="1)"
# @explain: 1)
# @explain: 2) — left as exercise (pattern shown above)
# @explain: 3)
# @explain: 4) Riyadh-area example
# 1)
from pywaffle import Waffle
plt.figure(FigureClass=Waffle, rows=10, values={"Code":35,"Read":25,"Sleep":30,"Eat":10},
           legend={"loc":"lower center","bbox_to_anchor":(0.5,-0.1),"ncol":4},
           title={"label":"My day"}); plt.show()

# 2) — left as exercise (pattern shown above)

# 3)
url = "https://archive.ics.uci.edu/ml/machine-learning-databases/auto-mpg/auto-mpg.data"
cols = ["mpg","cyl","disp","hp","weight","acc","year","origin","name"]
cars = pd.read_csv(url, sep=r"\s+", names=cols, na_values="?")
sns.regplot(data=cars, x="weight", y="mpg",
            scatter_kws={"alpha":.4}, line_kws={"color":"red"})
plt.title("mpg vs weight (negative correlation)"); plt.show()

# 4) Riyadh-area example
m = folium.Map(location=[24.7, 46.7], zoom_start=10)
for lat, lon, name in [(24.7136,46.6753,"Riyadh"),(24.6877,46.7219,"Olaya"),
                       (24.7743,46.7386,"DQ"),(24.5247,46.7193,"Diriyah"),
                       (24.6308,46.7728,"Murabba")]:
    folium.Marker([lat,lon], popup=name).add_to(m)
m


# %% [markdown] color=lime title="Recap"
# # Recap
#
# ✅ Waffle charts for compositional data with a precise grid
# ✅ Word clouds for "what is this text about?"
# ✅ Regression plots (`regplot`, `lmplot`) for relationships
# ✅ Correlation heatmaps for "which features move together?"
# ✅ Folium for interactive markers and marker clusters
# ✅ Choropleth for colour-by-region maps
# …


# %% [markdown] color=lime title="Thanks"
# # End of Module
#
# Next module continues the roadmap.
# Source: https://github.com/kader-xai/data-science-roadmap


