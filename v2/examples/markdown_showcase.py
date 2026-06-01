# doodlecode format-version: 4
# notebook: Markdown showcase — every text-cell construct

# %% kind=markdown id=m0 x=120.0 y=80.0 w=640.0
# @title: Welcome
# @note: Open by promising "everything a tutorial slide needs, in plain text."
# @link_to: m1

# Text cells speak **markdown** ✍️

A DoodleCode *text cell* renders a small, zero-dependency markdown
dialect — enough for technical and educational writing, nothing more.

You get **bold**, *italic*, ~~struck-through~~, and `inline code`, plus
[named links](https://example.com) and bare ones like
https://github.com that autolink on their own.

Press **F5 / Shift+P** to present, **→** to advance, **N** to read a
slide's speaker note.

# %% kind=markdown id=m1 x=120.0 y=520.0 w=640.0
# @title: Lists
# @note: Bullets, numbers, and checkboxes — point at the checked item.
# @link_to: m2

## Three kinds of list

- A plain bullet
- Another bullet

1. First numbered step
2. Second numbered step

- [x] A finished task
- [ ] A task still to do

# %% kind=markdown id=m2 x=120.0 y=1000.0 w=640.0
# @title: Tables
# @note: Mention the colon-alignment in the separator row.
# @link_to: m3

## A comparison table

| Feature   | Doodle | Plain slides |
|:----------|:------:|-------------:|
| Hand-drawn | yes    | no           |
| Runs code  | yes    | no           |
| One `.py`  | yes    | n/a          |

Colons in the separator row set per-column alignment (left / center /
right).

# %% kind=markdown id=m3 x=120.0 y=1480.0 w=640.0
# @title: Code & quotes
# @note: Fenced code is literal — markdown inside it shows verbatim.
# @link_to: m4

### Show a snippet, quote a source

```python
def greet(name):
    return f"Hello, {name}!"
```

> A fenced block renders **literally** — `**this**` stays text, not bold.

---

Use `inline code` for short identifiers inside a sentence.

# %% kind=markdown id=m4 x=120.0 y=1960.0 w=640.0
# @title: Recap

## One plain-text file 🎉

- **Inline**: bold · italic · strike · code · links (named + bare)
- **Blocks**: headings · lists · task lists · tables · fenced code ·
  blockquotes · rules
- Everything round-trips through a single `.py` — drop this file back
  into DoodleCode and the whole deck returns.

See the [README](README.md) for the full reference table.
