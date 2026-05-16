# %% [markdown]
# # Python, presented as a doodle
# A 6-minute walk through Python with hand-drawn callouts on every cell.
# Open this file in DoodleCode Studio, hit 🎬 Present, then `→` through it.


# %% kind=intro color=sky title="What you'll see"
# @explain: Each colored cell on the left is real, runnable Python.
# @explain: Each bubble on the right is a written explanation that ships
# @explain: WITH the file. Click ▶ Run to execute; ← / → to navigate.
# @tags: intro


# %% kind=expr color=peach title="Python is a calculator"
# @explain: Numbers, operators, parentheses — works exactly as you'd
# @explain: write it on paper.
print(2 + 2)
print(7 * 6)
print((10 + 2) / 3)


# %% kind=assign color=peach title="Variables hold values"
# @explain: A name on the left, a value on the right. No type declaration
# @explain: needed — Python figures it out from the value.
name = "Kader"
year = 2026
pi = 3.14159

print(name, year, pi)


# %% kind=expr color=peach title="f-strings format text"
# @explain: Put a variable inside { } in an f-string to interpolate it.
# @explain: :.2f means "2 decimal places" — the standard formatting spec.
print(f"Hello {name}!")
print(f"π is approximately {pi:.2f}")
print(f"You have {2026 - year} years to learn.")


# %% kind=conditional color=yellow title="if / else — choosing a branch"
# @explain: Indentation is scope. The block under `if` runs only when
# @explain: the condition is True.
age = 22
if age >= 18:
    print("adult")
else:
    print("minor")


# %% kind=loop color=yellow title="for — repeating a block"
# @explain: range(5) gives 0, 1, 2, 3, 4. The body of the loop runs
# @explain: once per value, with `i` bound to that value.
for i in range(5):
    print(f"step {i}")


# %% kind=function color=mint title="Functions package up reusable logic"
# @explain: `def` names a function. `return` sends a value back to the
# @explain: caller. Same input → same output, every time.
def area_of_circle(radius):
    return 3.14159 * radius * radius


print(area_of_circle(3))
print(area_of_circle(10))


# %% kind=assign color=peach title="Lists hold multiple values"
# @explain: Square brackets, comma-separated. Indexable from 0.
# @explain: Length with len(). Iterable with for.
fruits = ["apple", "banana", "cherry"]
print(fruits)
print(fruits[0])
print(len(fruits))


# %% kind=loop color=yellow title="Looping over a list"
# @explain: Same `for` loop, but iterating values directly instead of
# @explain: indices. The Pythonic way.
for fruit in fruits:
    print(fruit.upper())


# %% kind=function color=mint title="Putting it together — average"
# @explain: A real function that takes a list, computes the sum, divides
# @explain: by the count, returns the result.
def average(numbers):
    return sum(numbers) / len(numbers)


scores = [88, 92, 75, 99, 81]
print(f"average score: {average(scores):.1f}")


# %% kind=intro color=sky title="That's Python — almost"
# @explain: From here: dictionaries, classes, modules, libraries.
# @explain: But these 9 cells cover what you'll use in 80% of real code.
# @tags: outro


# %% [markdown]
# ## Recap — what just played
# - Numbers, variables, f-strings
# - if / for / functions
# - Lists and the average function
#
# **Try this:** edit `area_of_circle` to use `math.pi` instead of `3.14159`,
# `import math` at the top, and run again. The callout stays; only the
# code changes.
