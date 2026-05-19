# doodlecode format-version: 2
# Media capability tour — images, GIFs, videos, fast transitions.


# %% [markdown] color=rose title="Media Demo"
# # 🎬 Media in DoodleCode Studio
#
# A 7-slide tour of what the markdown cells can render.
# Press 🎬 Present, then use → / ← to flip through.
# Watch how the next 4 slides arrive **much faster** — that's
# the media auto-detect kicking in.


# %% [markdown] color=mint title="1. Animated GIF (natural size)"
# # 1. Animated GIF
#
# Four bouncing balls. The browser auto-loops GIFs — no controls needed.
# Drag the bottom-right corner of the image to resize.
#
# ![bouncing demo](/demo/bouncing_ball.gif)


# %% [markdown] color=sky title="2. MP4 video (auto-playing, looping)"
# # 2. MP4 video
#
# Live matplotlib wave animation, encoded as H.264. The `<video>` tag
# is set to **autoplay + loop + muted**, so it starts the moment you
# land on the slide.
#
# ![wave](/demo/wave_visualization.mp4)


# %% [markdown] color=peach title="3. PNG screenshot (full pixel size)"
# # 3. PNG screenshot
#
# A bar chart rendered with matplotlib and saved as PNG. Renders at
# its actual pixel dimensions — no more 288 px cap.
#
# ![chart](/demo/chart_screenshot.png)


# %% [markdown] color=violet title="4. Architecture diagram (PNG)"
# # 4. Hand-drawn-style diagram
#
# Boxes + arrows showing the single-port architecture (Browser →
# FastAPI + Jupyter kernel + React static build).
#
# ![architecture](/demo/architecture_diagram.png)


# %% [markdown] color=amber title="5. Mixing text and an image"
# # 5. Mix text with media
#
# - Markdown above
# - Image in the middle:
#
# ![chart again](/demo/chart_screenshot.png)
#
# - Bullets below
# - Headings, **bold**, `code spans`, and images coexist


# %% color=lime title="6. Live code still works"
# @explain: Media slides don't disable Python — this still runs.
# @explain: ▶ Run produces a matplotlib chart inline, like always.
import matplotlib.pyplot as plt

xs = [i / 10 for i in range(0, 63)]
ys = [pow(2.718, -((x - 3) ** 2) / 2) for x in xs]

plt.figure(figsize=(7, 3.5))
plt.fill_between(xs, ys, alpha=0.4, color="#74c0fc")
plt.plot(xs, ys, lw=2.5, color="#1864ab")
plt.title("Gaussian — runs every time")
plt.grid(alpha=0.3)
plt.tight_layout()
plt.show()


# %% [markdown] color=teal title="7. Recap"
# # 🧭 What you just saw
#
# - GIF, MP4, and PNG all render at natural size.
# - Each media element is **resizable** — drag the corner.
# - Videos / GIFs **auto-play**.
# - Transitions to media slides are ~4.5× faster (550 ms → 120 ms).
# - Plain text + code slides keep the original smooth pan.
