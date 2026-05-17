# doodlecode format-version: 2
# Module 1 — Python Basics. Presentation-ready deck.


# %% [markdown] color=rose title="Module 1 — Python Basics"
# # 🐍 Module 1 — Python Basics
#
# The alphabet of every other module in the data-science roadmap.
# We'll move fast: syntax, variables, types, operators, strings, input.


# %% [markdown] color=sky title="Why Python?"
# # Why Python for data science?
#
# - **High-level** — no memory or pointer management.
# - **Interpreted** — run line-by-line, no compile step.
# - **Huge ecosystem** — NumPy, pandas, scikit-learn, PyTorch.
# - **Readable** — close to pseudocode; teams onboard fast.


# %% color=mint title="Python as a calculator"
# @explain: Last expression in a cell auto-displays — no print needed.
# @explain: Try replacing 2 + 2 with anything: 17 * 23, 2 ** 10, etc.
2 + 2


# %% color=peach title="print vs auto-display"
# @explain: Earlier lines need print(); only the last line auto-shows.
# @explain: This is THE most common surprise for Python beginners.
print("hello")
3 * 7


# %% [markdown] color=violet title="Jupyter in one slide"
# # Jupyter notebooks, condensed
#
# - A notebook is a sequence of **cells** — code or markdown.
# - The **kernel** is the Python process; variables persist between cells.
# - **Shift+Enter** runs the current cell and moves to the next.
# - Magics: `%time` times a line, `%%time` times a whole cell.


# %% color=amber title="Timing a line with %time"
# @explain: %time prints how long the line took — useful for benchmarking.
# @explain: For a whole cell, put %%time on the FIRST line of the cell.
%time sum(range(1_000_000))


# %% [markdown] color=lime title="Indentation is the syntax"
# # Indentation defines scope
#
# Most languages use `{ }`. Python uses **4 spaces** of indentation.
# Mix tabs and spaces and you'll see `IndentationError`.
# This is the single biggest "Python feels weird" moment.


# %% color=teal title="if-block in action"
# @explain: Both prints belong to the if because they're indented under it.
# @explain: The third print is OUTSIDE the if — note the de-indent.
x = 10
if x > 0:
    print("positive")
    print("still inside the if")
print("outside the if")


# %% [markdown] color=rose title="Comments"
# # Two ways to comment
#
# - `# everything after the hash is ignored` — single-line.
# - `"""triple-quoted strings"""` — technically string literals, but
#   used as **docstrings** at the top of functions, classes, modules.


# %% color=sky title="Variables — no declarations"
# @explain: Python figures out the type from the value you assign.
# @explain: type() asks the interpreter "what type is this right now?"
age = 30           # int
height = 1.78      # float
name = "Alice"     # str
is_admin = True    # bool

print(type(age), type(height), type(name), type(is_admin))


# %% color=mint title="Type conversion"
# @explain: int(), float(), str(), bool() — explicit casts.
# @explain: int("42") works; int("forty-two") raises ValueError.
n = int("42")
pi = float("3.14")
label = str(99)

print(n + 8, pi * 2, label + "%")


# %% color=peach title="Arithmetic operators"
# @explain: / always returns float; // is integer division.
# @explain: % is remainder, ** is power. Same precedence as math class.
a, b = 17, 5
print("a + b  =", a + b)
print("a - b  =", a - b)
print("a * b  =", a * b)
print("a / b  =", a / b)
print("a // b =", a // b)
print("a % b  =", a % b)
print("a ** b =", a ** b)


# %% color=violet title="Strings — the friendly type"
# @explain: f"..." inserts variables right inside the string.
# @explain: .upper(), .lower(), .replace() return NEW strings.
name = "ada lovelace"

print(name.upper())
print(name.title())
print(len(name))
print(f"Hello, {name.title()}!")


# %% color=amber title="String slicing"
# @explain: text[start:stop] — stop is exclusive, like range().
# @explain: Negative indices count from the end: text[-1] is last char.
text = "data science"

print(text[0:4])     # "data"
print(text[5:])      # "science"
print(text[-7:])     # "science"
print(text[::-1])    # reversed


# %% color=lime title="Reading input from the user"
# @explain: input() always returns a STRING, even if you type digits.
# @explain: Wrap with int() / float() if you need a number.
# (In a script: prompt = input("Your name: "))
prompt = "Kader"  # pretend the user typed this
print(f"Welcome, {prompt}!")


# %% [markdown] color=teal title="Recap"
# # 🧭 Module 1 recap
#
# - Python is high-level, interpreted, dynamically typed.
# - Notebooks = cells + a persistent kernel.
# - Indentation defines scope.
# - Variables don't need declarations; `type()` tells you the type.
# - `/` is float, `//` is integer; `**` is power.
# - Strings are objects with methods (`.upper()`, `.title()`, slicing).


# %% [markdown] color=rose title="Next"
# # ➡️ Next module
#
# **Module 2 — Data Structures.** Lists, tuples, sets, dictionaries.
# Source: <https://github.com/kader-xai/data-science-roadmap>
