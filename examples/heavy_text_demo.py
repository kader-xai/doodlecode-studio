# doodlecode format-version: 2
# Exercises the auto-grow border on cells with a LOT of text.
# Every cell here is designed to be tall on load — if the doodle border
# wraps tightly around every word without scrolling or overflow, the
# auto-grow code is working.


# %% [markdown] color=rose title="A wall of text — and the box should still fit"
# # The problem with traditional Python notebooks for presentations
#
# Plain Jupyter cells are perfectly fine when you are the only reader,
# sitting alone at your desk, scrolling through your own code at your
# own pace. They were designed for that workflow and they excel at it.
#
# The trouble starts the moment you try to **show** that notebook to
# someone else. Suddenly the vertical scroll becomes your enemy. Your
# audience loses their place every time you jump back to remind them
# what variable a function expected. The wall of monochrome cells
# blends together. There is no obvious way to attach a written caption
# next to a piece of code. The output panel sits stacked below — fine
# when you're alone, awkward when you're trying to keep eyes on both
# the code and the result simultaneously.
#
# You can paper over some of this with `nbconvert` and a slide
# template, but then you lose the live execution. Or you can use the
# RISE plugin, but you give up the flexibility to edit on the fly.
# Or you can switch to a slide deck entirely and lose code execution.
#
# **DoodleCode Studio** sits on top of the same kernel API that
# Jupyter uses, but rearranges the surface for the case where the
# audience matters. Code on the left as colored hand-drawn cards.
# Your own callouts on the right — written by you, stored in the
# `.py` file as comments. A presenter mode that fits one card to the
# viewport at a time. A laser pen and a highlighter for the moments
# when you need to point. All running locally so there is no
# dependency on a network connection during your talk.
#
# This card itself is the test case for v1.0.5+ — open it from a
# fresh load and the wavy doodle border should fit tightly around
# this paragraph from the moment it appears, no manual resize needed.


# %% [markdown] color=sky title="Three more paragraphs to make sure"
# Lorem ipsum dolor sit amet, consectetur adipiscing elit. Sed do
# eiusmod tempor incididunt ut labore et dolore magna aliqua. Ut enim
# ad minim veniam, quis nostrud exercitation ullamco laboris nisi ut
# aliquip ex ea commodo consequat.
#
# Duis aute irure dolor in reprehenderit in voluptate velit esse
# cillum dolore eu fugiat nulla pariatur. Excepteur sint occaecat
# cupidatat non proident, sunt in culpa qui officia deserunt mollit
# anim id est laborum.
#
# Sed ut perspiciatis unde omnis iste natus error sit voluptatem
# accusantium doloremque laudantium, totam rem aperiam, eaque ipsa
# quae ab illo inventore veritatis et quasi architecto beatae vitae
# dicta sunt explicabo. Nemo enim ipsam voluptatem quia voluptas sit
# aspernatur aut odit aut fugit, sed quia consequuntur magni dolores
# eos qui ratione voluptatem sequi nesciunt.


# %% kind=function color=mint title="Code cell with a long body that scrolls in Monaco"
# @explain: Code cells use Monaco as the editor, which has its OWN
# @explain: internal scrollbar — the cell box itself only grows up to
# @explain: a sensible ceiling. So a 200-line function doesn't push
# @explain: the whole canvas down; you scroll inside the editor.
def long_demo(items):
    """Walk through every item, transform it, accumulate the result."""
    out = []
    for i, item in enumerate(items):
        if i % 2 == 0:
            out.append(item.upper())
        else:
            out.append(item.lower())
    return out


for line in long_demo(["Hello", "World", "Python", "Doodle", "Notebook"]):
    print(line)


# %% [markdown] color=mint title="Bulleted list — also a content-driven height"
# # Why doodle?
#
# - **Code stays runnable.** Real IPython kernel underneath. Pip
#   install, plt.show, all of it works.
# - **Explanations live with the code.** Your callouts are `# @explain:`
#   comments in the file. They diff cleanly, they version-control
#   cleanly, they survive copying the file to a thumb drive.
# - **Presentation built in.** No second app to launch, no export
#   step. Hit 🎬 Present and step through with the arrow keys.
# - **One file format.** Open, edit, save, share — always a `.py`.
#   It runs end-to-end with plain `python file.py` outside the app.
# - **Local-first.** No account, no cloud, no token. Auto-saves to
#   `~/.doodlecode/` and to your browser's localStorage.
# - **Open source.** MIT licensed. Star and fork it from the About
#   modal (top-right ⓘ).


# %% [markdown] color=violet title="Thanks for testing"
# # 🎉 Thanks for being the test case
#
# If you got to this slide and every card above wrapped its border
# snugly around the text — even on the very first paint — the
# auto-grow geometry is working.
#
# If you spot any cell where the border floats above empty space
# below the last line of text, or any cell where text spills outside
# the wavy line, file an issue with a screenshot.
