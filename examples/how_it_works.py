# %% [markdown]
# # How DoodleCode Studio works
#
# This file is the user manual. Open it in the app, then read each cell
# and try the action it describes. Everything updates live.

# %% [markdown]
# ## The two areas
# - **Left** — code cards. The Monaco editor is your real Python. Run it
#   with ▶ Run; output appears **below** the editor only.
# - **Right** — callout bubbles. These are **your explanations**, written
#   by you, not generated. One callout per code cell.

# %% kind=intro color=sky title="Try me — edit my callout"
# @explain: Click the ✎ button in this cell's header.
# @explain: A popup appears with Title / Explanation / Kind / Color.
# @explain: Change the color to mint, hit Save — both the bubble on the
# @explain: right and the editor's left strip turn green.
print("editing the callout doesn't change this code")


# %% kind=loop color=peach title="The editor itself is color-coded"
# @explain: The Monaco editor's left edge is painted in this cell's color
# @explain: so you can tell which section a piece of code belongs to at
# @explain: a glance. The header strip matches; the right-side bubble
# @explain: matches. Everything is one visual unit.
for i in range(3):
    print("step", i)


# %% kind=function color=mint title="Outputs live BELOW only"
# @explain: Whatever this cell prints, raises, or displays appears in the
# @explain: white "↳ output" box under the editor. It never escapes into
# @explain: the callout column on the right.
def greet(name):
    return f"hello {name}!"

print(greet("world"))


# %% [markdown]
# ## Saving and exporting
# - **Autosave** — every edit is saved automatically. The toolbar shows
#   "saved Ns ago". The file is also kept in your browser's localStorage,
#   so a reload restores your work.
# - **💾 Save** — downloads the current notebook as a real `.py` file.
#   Callouts come along, encoded as `# %% kind=… color=… title="…"` plus
#   `# @explain:` lines — the format you're reading right now.
# - **📂 Open** — uploads any `.py` (with or without these markers) or a
#   `.ipynb`. Callouts you've written are preserved.

# %% kind=intro color=lavender title="Round-trip is exact"
# @explain: Save this file, reopen it, and the callouts come back
# @explain: identical. That means you can: write code + callouts in the
# @explain: app → export → commit to git → reopen later → keep editing.
# @tags: workflow, export
print("export → reopen → keep going")


# %% [markdown]
# ## Presentation mode
# Press **🎬 Present** in the toolbar. Use **◀ Prev / Next ▶** at the bottom
# to step through cells. The canvas **pans** to each cell at your current
# zoom — it no longer zooms out. Set your zoom once with Cmd+scroll (or
# pinch), then step through.

# %% [markdown]
# ## The 60-second workflow
# 1. **📂 Open** a Python file (or just start typing into the seeded cell).
# 2. For each section, click ✎ → write a Title and an Explanation, pick a
#    Color. The callout bubble appears on the right.
# 3. Run cells with ▶ to verify the code still works.
# 4. **🎬 Present** to walk through them like slides.
# 5. **💾 Save** to download the `.py` you can share or commit.
