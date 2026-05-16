# %% [markdown]
# # Module 1 — Python Basics
# IBM Python for Data Science · Module 1 of 16.
#
# This is the alphabet of every other module. Skip nothing — every later
# notebook assumes the ideas here.

# %% [markdown]
# ## What you'll cover
# - What Python is and why DS uses it
# - Jupyter Notebook basics (cells, kernels, shortcuts, magics)
# - Python syntax — indentation, comments, statements
# - Variables, expressions, dynamic typing
# - Numbers (int, float) and arithmetic
# - Booleans and None
# - Strings — create, index, slice, methods
# - Format strings — f"", .format(), %
# - input() and print() — first interactive programs
# - Type conversion (casting)
# - Comparisons, truthiness, chained comparisons
# - Reading tracebacks — basic debugging
# - Three first programs (calculator, temp converter, name greeter)


# %% kind=intro color=sky title="1. What is Python?"
# @explain: Python is a high-level, interpreted, dynamically-typed
# @explain: general-purpose language. High-level — no manual memory.
# @explain: Interpreted — runs line by line. Dynamic typing — a name's
# @explain: type is decided by the value bound to it, not declared.
# @tags: intro, language


# %% kind=intro color=sky title="Why data science chose Python"
# @explain: Huge scientific stack (NumPy, Pandas, scikit-learn, PyTorch).
# @explain: Readable enough to use as pseudocode in a paper.
# @explain: Glue language — talks to C, SQL, Spark, REST APIs.
# @explain: Cost: pure Python is slow. The libraries above sidestep this
# @explain: by running hot loops in C/Fortran.
# @tags: intro


# %% kind=expr color=peach title="Python as a calculator"
# @explain: An expression evaluates to a value. In a notebook, the LAST
# @explain: expression in a cell is auto-printed.
2 + 2


# %% kind=expr color=peach title="Two statements per cell"
# @explain: Earlier statements need print(); only the last expression
# @explain: gets auto-printed.
print("hello")
3 * 7


# %% [markdown]
# ## 2. Jupyter Notebook basics
# A notebook is a sequence of **cells**. Two types matter:
#
# - **Code** cells — run Python, output appears below.
# - **Markdown** cells — render formatted text (like this paragraph).
#
# The **kernel** is the Python process attached to your notebook. Variables
# set in cell 3 are still alive in cell 7 because the same kernel is running
# them. Restart the kernel and they vanish.


# %% kind=expr color=peach title="Timing a single line"
# @explain: %time measures wall-clock for one line. Inside DoodleCode the
# @explain: kernel is real IPython, so the magic works — uncomment to try.
# @explain: The plain-Python fallback below runs without magics.
total = sum(range(1_000_000))
print(total)


# %% kind=loop color=yellow title="Timing a whole cell"
# @explain: %%time at the top of a cell measures the whole cell. The loop
# @explain: below totals 0..999_999 the slow way.
total = 0
for i in range(1_000_000):
    total += i
print(total)


# %% kind=expr color=peach title="Running shell commands"
# @explain: In IPython a leading ! sends the line to the shell.
# @explain: The cross-platform fallback used here is sys.version.
import sys
print(sys.version)


# %% [markdown]
# ## 3. Python syntax — the rules
# **Indentation defines scope.** Most languages use `{ }`. Python uses
# indentation (4 spaces by convention). Mixing tabs and spaces or being
# inconsistent → `IndentationError`.


# %% kind=conditional color=yellow title="Indentation is scope"
# @explain: The 4-space indent under `if x > 0:` puts both prints INSIDE
# @explain: the if-block. The unindented print is OUTSIDE.
x = 10
if x > 0:
    print("positive")
    print("still inside the if")
print("outside the if")


# %% [markdown]
# ## 4. Variables and expressions
# A variable is a **name bound to a value**. Assignment uses `=`.
#
# **Naming rules**
# - Letters, digits, underscores. Cannot start with a digit.
# - Case-sensitive: `Age` and `age` are different.
# - PEP 8 convention: `snake_case` for variables/functions, `CapWords` for
#   classes, `UPPER_SNAKE` for constants.


# %% kind=assign color=peach title="Binding values to names"
# @explain: Four bindings of different types. type() returns the runtime
# @explain: type — Python does not declare types up front.
age = 38
name = "Kader"
height_m = 1.75
PI = 3.14159

print(name, age, height_m, PI)


# %% kind=assign color=peach title="Dynamic typing — rebinding"
# @explain: A name can be rebound to a different type. Legal, but usually
# @explain: a smell — readers expect the type to stay stable.
age = 38
age = "thirty-eight"
print(age, type(age))


# %% kind=assign color=peach title="Multiple assignment and swap"
# @explain: Tuple-unpacking lets you assign several names at once and
# @explain: swap two variables without a temporary.
a, b, c = 1, 2, 3
print(a, b, c)

x, y = 10, 20
x, y = y, x
print(x, y)


# %% [markdown]
# ## 5. Numbers
# Two main numeric types:
# - **int** — whole numbers, arbitrary precision.
# - **float** — IEEE-754 double, ~15 significant digits, with the usual
#   binary-fraction quirks.
#
# **Operator precedence:** `**` (power) → unary `-` → `*  /  //  %` → `+  -`.


# %% kind=expr color=peach title="Arithmetic basics"
# @explain: / is true division (always float). // is floor division.
# @explain: % is modulo. ** is power, and ints have arbitrary precision.
print(7 + 3, 7 - 3, 7 * 3)
print(7 / 3)
print(7 // 3)
print(7 % 3)
print(2 ** 10)
print(2 ** 100)

million = 1_000_000
print(million)


# %% kind=expr color=rose title="The float-equality trap"
# @explain: 0.1 + 0.2 is not exactly 0.3 in binary floating point.
# @explain: Never compare floats with ==. Use math.isclose instead.
print(0.1 + 0.2)
print(0.1 + 0.2 == 0.3)

import math
print(math.isclose(0.1 + 0.2, 0.3))


# %% [markdown]
# ## 6. Booleans and None
# - `bool` has exactly two values: `True` and `False` (capitalised).
# - `None` is Python's "nothing here" singleton; its type is `NoneType`.
#
# **Truthiness.** Falsy values: `False`, `0`, `0.0`, `""`, `[]`, `{}`, `()`,
# `None`. Everything else is truthy.


# %% kind=loop color=yellow title="Truthiness in action"
# @explain: bool() forces a value into True/False. Useful when you want to
# @explain: see why a value behaves as truthy or falsy.
flag = True
empty = None

print(flag, type(flag))
print(empty, type(empty))

for v in [0, 1, "", "x", [], [0], None, 3.14]:
    print(repr(v), "->", bool(v))


# %% [markdown]
# ## 7. Strings — creating them
# A string is a sequence of characters. Quotes can be single, double, or
# triple (for multi-line).


# %% kind=assign color=peach title="Three ways to quote a string"
# @explain: Single and double quotes are identical. Triple quotes span
# @explain: multiple lines and preserve newlines.
a = 'single quotes'
b = "double quotes"
c = """triple quotes
let you span
multiple lines"""
print(a)
print(b)
print(c)


# %% kind=expr color=peach title="Escape sequences and raw strings"
# @explain: Backslash starts an escape. \t is tab, \n is newline, \\ is a
# @explain: literal backslash. r"..." disables escapes — great for paths.
print("tab\there")
print("newline\nhere")
print("a backslash: \\")
print("a quote: \"")

print(r"C:\Users\kader\file.txt")


# %% kind=expr color=peach title="Indexing and slicing"
# @explain: Strings are 0-indexed. Negative indices count from the end.
# @explain: s[start:stop:step] — stop is exclusive, step can be negative.
s = "Data Science"
print(s[0])
print(s[-1])
print(s[5:12])
print(s[:4])
print(s[5:])
print(s[::2])
print(s[::-1])
print(len(s))


# %% kind=expr color=peach title="Common string methods"
# @explain: Strings are immutable — methods return a NEW string.
# @explain: strip, upper/lower, replace, split, join, in, find, startswith.
s = "  Data Science  "
print(s.strip())
print(s.upper(), s.lower())
print(s.replace("Data", "Real"))
print(s.split())
print("-".join(["2024", "12", "31"]))
print("Data" in s, "X" in s)
print(s.find("Sci"), s.find("xx"))
print("data".startswith("da"), "data".endswith("ta"))


# %% kind=assign color=rose title="Immutability pitfall"
# @explain: You cannot assign to s[i] — strings are immutable. Build a new
# @explain: string by slicing and concatenating instead.
s = "hello"
s = "H" + s[1:]
print(s)


# %% [markdown]
# ## 8. Format strings (the modern way)
# Three styles you will see, in order of preference:
#
# - **f-strings** (3.6+): `f"{name} is {age}"` — use this.
# - **.format()**: older codebases.
# - **%-formatting**: legacy code and logging configs.
#
# Inside `{ ... }` you can append `:spec` to control width, precision,
# alignment, padding (e.g. `:.2f`, `:>10`, `:,`).


# %% kind=expr color=peach title="f-strings with format specs"
# @explain: :.4f → four decimals. :>10 / :<10 / :^10 → align in width 10.
# @explain: :, → thousands separator. :.1% → percent. :08b / :#x → bin/hex.
# @explain: {var=} → prints the variable name and value (3.8+).
name, age, pi = "Kader", 38, 3.14159265

print(f"{name} is {age} years old.")
print(f"π is approximately {pi:.4f}")
print(f"|{name:>10}|")
print(f"|{name:<10}|")
print(f"|{name:^10}|")
print(f"{1234567:,}")
print(f"{0.045:.1%}")
print(f"{255:08b} {255:#x}")
print(f"{age=}")


# %% kind=expr color=peach title="Older formatting styles"
# @explain: .format takes positional/keyword args. % uses C-style %s/%d.
# @explain: Both are still common in older codebases.
name, age = "Kader", 38
print("{} is {}".format(name, age))
print("{0} {0} {1}".format("ha", "!"))
print("%s is %d years old" % (name, age))


# %% [markdown]
# ## 9. Type conversion (casting)
# Use the type's name as a function: `int(x)`, `float(x)`, `str(x)`, `bool(x)`.
#
# **Gotchas**
# - `int("3.5")` is a `ValueError` — go via float: `int(float("3.5"))`.
# - `bool(0) == False`; everything non-zero / non-empty is `True`.
# - `int(3.9) == 3` — truncates toward zero, does NOT round.


# %% kind=expr color=peach title="Casting between types"
# @explain: int/float/str all accept strings and numbers. Casting truncates,
# @explain: it does NOT round (use round() for that).
print(int("42"), type(int("42")))
print(float("3.14"))
print(str(99) + "%")
print(int(3.9))


# %% [markdown]
# ## 10. input() and print()
# - `input(prompt)` reads a line from the user and **always returns a `str`**.
#   Cast to int/float if you need a number.
# - `print(*objects, sep=' ', end='\n')` accepts any number of values,
#   separated by `sep`, terminated by `end`.


# %% kind=expr color=peach title="print() with sep and end"
# @explain: sep controls what goes BETWEEN args; end controls what goes
# @explain: AFTER the line. Use end="" to keep the cursor on the same line.
print("a", "b", "c")
print("a", "b", "c", sep=" | ")
print("no newline ", end="")
print("then this on the same line")


# %% kind=expr color=peach title="Reading user input (hard-coded for the demo)"
# @explain: input() blocks until the user types and presses Enter. To use
# @explain: it as a number, wrap it in int() or float().
name = "Kader"
age = 38
print(f"Hello {name}, you'll be {age + 1} next year.")


# %% [markdown]
# ## 11. Comparisons and boolean logic
# - **Comparison:** `== != < > <= >=`
# - **Logic:** `and`, `or`, `not` (lowercase, NOT `&&` / `||`).
# - **`==` vs `is`:** `==` compares values, `is` compares identity. Almost
#   always use `==`. The one place `is` is right: comparing to `None`.
# - **Chained comparisons:** `18 <= age < 65` works the way it reads.


# %% kind=conditional color=yellow title="Comparing and chaining"
# @explain: Two equivalent age checks: explicit `and` vs chained comparison.
age = 22
print(age >= 18 and age < 65)
print(18 <= age < 65)
print(not (age < 18))


# %% kind=conditional color=yellow title="is vs =="
# @explain: Two lists with the same contents compare equal (==) but are
# @explain: different objects (is False). For None always use `is None`.
a = [1, 2, 3]
b = [1, 2, 3]
print(a == b)
print(a is b)
print(a is a)

x = None
print(x is None)


# %% [markdown]
# ## 12. Reading a Python traceback
# When something breaks, Python prints a traceback. Read it **bottom-up** —
# the last line tells you *what* went wrong; the lines above tell you *where*.
#
# **The five errors you'll meet first**
# - **NameError** — used a variable that doesn't exist.
# - **TypeError** — wrong type for the operation.
# - **ValueError** — right type, bad value (`int("abc")`).
# - **SyntaxError** — code can't be parsed.
# - **IndentationError** — mixed or misaligned spaces.


# %% kind=function color=mint title="Print debugging"
# @explain: The simplest debugger that actually works: print the values
# @explain: at the suspicious point. Cheap, always available, easy to remove.
def avg(values):
    print(f"DEBUG: values={values}, len={len(values)}")
    return sum(values) / len(values)


print(avg([3, 5, 7, 9]))


# %% [markdown]
# ## 13. Your first three programs
# Read each, predict the output, then run.


# %% kind=expr color=peach title="Program 1 — Personal greeting"
# @explain: Build a sentence by interpolating two variables into an f-string.
name = "Kader"
year = 2026
print(f"Hello, {name}! You will be coding in {year}.")


# %% kind=expr color=peach title="Program 2 — Tiny calculator"
# @explain: Demonstrates all six basic arithmetic operators side by side.
# @explain: :.2f on division shows the float to two decimals.
a, b = 17, 4
print(f"{a} + {b} = {a + b}")
print(f"{a} - {b} = {a - b}")
print(f"{a} * {b} = {a * b}")
print(f"{a} / {b} = {a / b:.2f}")
print(f"{a} // {b} = {a // b}")
print(f"{a} % {b}  = {a % b}")


# %% kind=function color=mint title="Program 3 — Temperature converter"
# @explain: C → F uses 9/5+32. F → C reverses it: (f-32) * 5/9.
celsius = 25
fahrenheit = celsius * 9 / 5 + 32
print(f"{celsius}°C = {fahrenheit}°F")

f = 98.6
c = (f - 32) * 5 / 9
print(f"{f}°F = {c:.1f}°C")


# %% [markdown]
# ## 14. Practice
# Try these before peeking at the answers.
#
# 1. Print your name in upper case followed by the length of your name.
# 2. Compute the area of a circle of radius 7. Round to 2 decimals.
# 3. Given `s = "data science is fun"`, print it with the words in reverse
#    order: `"fun is science data"`.
# 4. Hard-code an age of 21. Print `"adult"` if ≥18, `"minor"` otherwise —
#    inside a single f-string that includes the age.


# %% kind=function color=mint title="Exercise 1 — name upper and length"
# @explain: .upper() returns the uppercase copy; len() returns the count.
name = "Kader"
print(f"{name.upper()} ({len(name)})")


# %% kind=function color=mint title="Exercise 2 — circle area"
# @explain: π·r². math.pi is the constant. :.2f rounds to 2 decimals.
import math

r = 7
print(f"area = {math.pi * r ** 2:.2f}")


# %% kind=function color=mint title="Exercise 3 — reverse the words"
# @explain: split() → list of words. [::-1] reverses any sequence.
# @explain: " ".join(...) glues the words back together.
s = "data science is fun"
print(" ".join(s.split()[::-1]))


# %% kind=conditional color=yellow title="Exercise 4 — adult or minor"
# @explain: A conditional expression inside an f-string: value-if-true if
# @explain: condition else value-if-false.
age = 21
print(f"You are {age} — {'adult' if age >= 18 else 'minor'}")


# %% [markdown]
# ## Recap — what you can now do
# - ✅ Run code in Jupyter cells, use shortcuts and magics
# - ✅ Use Python as a calculator with int/float/bool/str/None
# - ✅ Create, index, slice, and format strings
# - ✅ Use f-strings with format specs (`:.2f`, `:>10`, `:,`)
# - ✅ Convert between types and avoid the float-equality trap
# - ✅ Read a traceback and pick the right fix from the five common errors
# - ✅ Write small interactive programs
#
# **Next module:** Module 2 — Python Data Structures.
