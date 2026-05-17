# doodlecode format-version: 2
# Auto-converted from module_02_data_structures.ipynb
# Open with 📂 Open → press 🎬 Present.


# %% [markdown] color=rose title="Module 02 Data Structures"
# # Module 02 Data Structures
#
# A live walkthrough — one card per concept.
# Use → / ← to step through. Press 🎬 Present to begin.



# %% [markdown] color=sky title="Module 2 — Python Data Structures"
# # Module 2 — Python Data Structures
#
# *IBM Python for Data Science · Module 2 of 16*
#
# You learned the alphabet in Module 1. Now we learn the **containers** — the four built-in types that hold *collections* of values. Every DataFrame, every JSON response, every CSV row eventually lands in one of these.
#
# ### The four containers — at a glance
#
# | Type | Ordered? | Mutable? | Duplicates? | Best for |
# …


# %% [markdown] color=mint title="1. Lists — the workhorse"
# # 1. Lists — the workhorse
#
# A list is an **ordered, mutable** collection. Items can be any type, even mixed.


# %% color=peach title="Creating lists"
# @explain: Creating lists
# Creating lists
empty   = []
nums    = [3, 1, 4, 1, 5, 9, 2, 6]
mixed   = [1, "two", 3.0, True, None]   # legal but usually a smell
from_range = list(range(5))             # [0, 1, 2, 3, 4]

print(empty, nums, mixed, from_range)
print("length:", len(nums))


# %% [markdown] color=violet title="Indexing & slicing — same rules as strings"
# # Indexing & slicing — same rules as strings
#
# 0-based, negatives count from the end, `[start:stop:step]` and `stop` is exclusive.


# %% color=amber title="0   1   2   3   4"
# @explain: 0   1   2   3   4
# @explain: -5  -4  -3  -2  -1
nums = [10, 20, 30, 40, 50]
#       0   1   2   3   4
#      -5  -4  -3  -2  -1

print(nums[0], nums[-1])    # 10 50
print(nums[1:4])            # [20, 30, 40]
print(nums[:3])             # [10, 20, 30]
print(nums[::2])            # [10, 30, 50]
print(nums[::-1])           # [50, 40, 30, 20, 10]  (reversed)


# %% [markdown] color=rose title="Mutating a list — what makes it different from a string"
# # Mutating a list — what makes it different from a string
#
# Strings are immutable; lists are not. You can change items, add, remove, extend.


# %% color=lime title="Concatenation and repetition"
# @explain: Concatenation and repetition (creates NEW lists)
items = ["apple", "banana", "cherry"]

items[1] = "blueberry"          # replace by index
print(items)

items.append("date")            # add to end
items.insert(0, "apricot")      # insert at index 0
print(items)

items.remove("cherry")          # remove first matching value
last = items.pop()              # remove + return last item
print(items, "popped:", last)

items.extend(["elderberry", "fig"])   # add many at once
print(items)

# Concatenation and repetition (creates NEW lists)
a = [1, 2] + [3, 4]
b = [0] * 5
print(a, b)


# %% [markdown] color=teal title="Membership and counting"
# # Membership and counting
#


# %% color=sky title="nums = [3"
# @explain: Run this cell to see the output.
nums = [3, 1, 4, 1, 5, 9, 2, 6, 1]
print(1 in nums)          # True
print(7 not in nums)      # True
print(nums.count(1))      # 3
print(nums.index(5))      # 4 — position of first 5


# %% [markdown] color=mint title="2. Sorting — `sort` vs `sorted`"
# # 2. Sorting — `sort` vs `sorted`
#
# | Form | Returns | Mutates? | Use when |
# |---|---|---|---|
# | `list.sort()` | `None` | ✅ in place | you don't need the original |
# | `sorted(iterable)` | new list | ❌ | you need to keep the original, or input isn't a list |
#
# Both accept `key=` (a function) and `reverse=True`.


# %% color=peach title="sorted"
# @explain: sorted — returns a new list, original untouched
# @explain: .sort() — mutates in place, returns None
# @explain: Sort strings by length using key=
# @explain: Sort list of (name, age) tuples by age
nums = [3, 1, 4, 1, 5, 9, 2, 6]

# sorted — returns a new list, original untouched
print(sorted(nums))
print(sorted(nums, reverse=True))
print(nums)               # unchanged

# .sort() — mutates in place, returns None
nums.sort()
print(nums)

# Sort strings by length using key=
words = ["banana", "fig", "apple", "kiwi"]
print(sorted(words, key=len))                   # ['fig', 'kiwi', 'apple', 'banana']
print(sorted(words, key=str.lower))             # case-insensitive

# Sort list of (name, age) tuples by age
people = [("Ada", 36), ("Linus", 54), ("Grace", 85)]
print(sorted(people, key=lambda p: p[1]))       # by index 1 (age)


# %% [markdown] color=violet title="3. Nested lists + the shallow-copy trap"
# # 3. Nested lists + the shallow-copy trap
#
# Lists can contain lists — that's how you build matrices and tables.
#
# The trap: `=` doesn't copy a list — it creates *another name* for the same list. To copy, use `list(x)`, `x[:]`, or `copy.deepcopy(x)` if it's nested.


# %% color=amber title="Nested list = matrix"
# @explain: Nested list = matrix
# @explain: Walk a 2D list
# Nested list = matrix
matrix = [
    [1, 2, 3],
    [4, 5, 6],
    [7, 8, 9],
]
print(matrix[0])       # first row: [1, 2, 3]
print(matrix[1][2])    # row 1, col 2 → 6

# Walk a 2D list
for row in matrix:
    for v in row:
        print(v, end=" ")
    print()


# %% color=rose title="THE TRAP"
# @explain: THE TRAP — = doesn't copy
# THE TRAP — = doesn't copy
a = [1, 2, 3]
b = a              # same object, two names
b.append(99)
print("a:", a)     # [1, 2, 3, 99]  ← surprised?
print("b:", b)
print("same object?", a is b)


# %% color=lime title="Copying"
# @explain: Copying — three ways
# @explain: Nested? Shallow copy still shares the inner lists
# @explain: Deep copy fixes this
# Copying — three ways
import copy

a = [1, 2, 3]
c1 = a[:]            # slice copy
c2 = list(a)         # constructor copy
c3 = a.copy()        # method (3.3+)

a.append(99)
print("a:", a, "  copies unchanged:", c1, c2, c3)

# Nested? Shallow copy still shares the inner lists.
nested = [[1, 2], [3, 4]]
shallow = nested[:]
shallow[0].append(99)
print("nested:", nested, "  shallow:", shallow)   # both changed!

# Deep copy fixes this
deep = copy.deepcopy(nested)
deep[0].append(777)
print("nested:", nested, "  deep:", deep)         # only deep changed


# %% [markdown] color=teal title="4. List comprehensions — Python's most-loved feature"
# # 4. List comprehensions — Python's most-loved feature
#
# A compact way to build a list from another iterable. Pattern:
# ```
# [expression for item in iterable if condition]
# ```
# Reads almost like English: "expression, for each item in iterable, if condition."
#
# …


# %% color=sky title="Squares of all numbers"
# @explain: Squares of all numbers
# @explain: Squares of even numbers only
# @explain: Conditional expression INSIDE the output
# @explain: Nested — flatten a 2D list
# @explain: Equivalent comprehensions exist for sets and dicts too:
nums = [1, 2, 3, 4, 5, 6, 7, 8, 9, 10]

# Squares of all numbers
squares = [n**2 for n in nums]
print(squares)

# Squares of even numbers only
even_squares = [n**2 for n in nums if n % 2 == 0]
print(even_squares)

# Conditional expression INSIDE the output
labels = ["even" if n % 2 == 0 else "odd" for n in nums]
print(labels)

# Nested — flatten a 2D list
matrix = [[1,2,3],[4,5,6],[7,8,9]]
flat = [v for row in matrix for v in row]
print(flat)

# Equivalent comprehensions exist for sets and dicts too:
print({n % 3 for n in nums})                       # set comp
print({n: n**2 for n in nums})                     # dict comp


# %% [markdown] color=mint title="5. Tuples — immutable sequences"
# # 5. Tuples — immutable sequences
#
# A tuple looks like a list but uses parentheses and **cannot be changed** after creation.
#
# ### When to prefer tuples over lists
# - Fixed records: `(latitude, longitude)`, `(name, age)`.
# - Multiple return values from a function.
# - Keys in a dict (lists can't be keys; tuples can — they're hashable).
# …


# %% color=peach title="Creating"
# @explain: Creating
# @explain: Indexing/slicing — same as lists
# @explain: Immutability
# @explain: point[0] = 5     # TypeError
# @explain: Unpacking — the killer feature
# Creating
point  = (10.0, 20.5)
single = (42,)            # NOTE the trailing comma — without it, it's just int 42
empty  = ()
print(point, single, empty, type(single))

# Indexing/slicing — same as lists
print(point[0], point[-1])

# Immutability
# point[0] = 5     # TypeError

# Unpacking — the killer feature
x, y = point
print(x, y)

# Swap (under the hood: pack into tuple, unpack into two names)
a, b = 1, 2
a, b = b, a
print(a, b)

# Star-unpacking — first, *middle, last
first, *middle, last = [1, 2, 3, 4, 5]
print(first, middle, last)         # 1 [2, 3, 4] 5


# %% [markdown] color=violet title="Named tuples — tuples with field names"
# # Named tuples — tuples with field names
#
# When a tuple has more than 2-3 fields, names beat positions for readability.


# %% color=amber title="p.x = 99  # AttributeError"
# @explain: p.x = 99  # AttributeError — still immutable
from collections import namedtuple

Point = namedtuple("Point", ["x", "y"])
p = Point(10, 20)
print(p, p.x, p.y)
print(p[0])             # still works as a regular tuple
# p.x = 99  # AttributeError — still immutable


# %% [markdown] color=rose title="6. Dictionaries — the most-used structure in data work"
# # 6. Dictionaries — the most-used structure in data work
#
# A `dict` maps **keys** to **values**. Keys must be hashable (strings, numbers, tuples — not lists).
#
# Why central to data work:
# - JSON deserialises to a dict.
# - A row from a CSV is naturally `{column: value}`.
# - Pandas `DataFrame` is essentially a dict of columns.


# %% color=lime title="Creating"
# @explain: Creating — three styles
# @explain: Access, add, update
# @explain: Safe lookup — never KeyError again
# @explain: Delete
# @explain: Membership tests check KEYS
# Creating — three styles
d1 = {"name": "Kader", "age": 38}
d2 = dict(name="Kader", age=38)
d3 = dict([("name","Kader"), ("age", 38)])
print(d1 == d2 == d3)

# Access, add, update
print(d1["name"])
d1["city"] = "Riyadh"          # add
d1["age"] += 1                  # update
print(d1)

# Safe lookup — never KeyError again
print(d1.get("email"))                      # None
print(d1.get("email", "not provided"))      # custom default

# Delete
del d1["city"]
removed = d1.pop("age")        # remove + return
print(d1, "popped:", removed)

# Membership tests check KEYS
print("name" in d1)            # True
print("Kader" in d1)           # False — that's a value


# %% [markdown] color=teal title="Iteration — three patterns"
# # Iteration — three patterns
#


# %% color=sky title="Over keys"
# @explain: Over keys (default)
# @explain: Over values
# @explain: Over key+value pairs — most common
# @explain: Build a dict from two parallel lists
d = {"name": "Kader", "age": 38, "city": "Riyadh"}

# Over keys (default)
for k in d:
    print(k)

# Over values
for v in d.values():
    print(v)

# Over key+value pairs — most common
for k, v in d.items():
    print(f"{k} -> {v}")

# Build a dict from two parallel lists
keys, values = ["a","b","c"], [1, 2, 3]
print(dict(zip(keys, values)))


# %% [markdown] color=mint title="Useful methods"
# # Useful methods
#


# %% color=peach title="update"
# @explain: update — merge another dict in
# @explain: setdefault — return existing or insert default
# @explain: Counting with a dict (poor-man's Counter)
# @explain: Cleaner: collections.Counter
d = {"a": 1, "b": 2}

# update — merge another dict in
d.update({"b": 99, "c": 3})
print(d)                             # {'a':1, 'b':99, 'c':3}

# setdefault — return existing or insert default
d.setdefault("x", 0)
d.setdefault("x", 999)               # ignored — 'x' already exists
print(d)

# Counting with a dict (poor-man's Counter)
text = "data data science science science python"
counts = {}
for word in text.split():
    counts[word] = counts.get(word, 0) + 1
print(counts)

# Cleaner: collections.Counter
from collections import Counter
print(Counter(text.split()))


# %% [markdown] color=violet title="Nested dicts (and how a JSON response looks)"
# # Nested dicts (and how a JSON response looks)
#


# %% color=amber title="user = {"
# @explain: Run this cell to see the output.
user = {
    "name": "Kader",
    "address": {
        "city": "Riyadh",
        "country": "Saudi Arabia"
    },
    "skills": ["Python", "SQL"]
}
print(user["address"]["city"])
print(user["skills"][0])


# %% [markdown] color=rose title="7. Sets — uniqueness and set algebra"
# # 7. Sets — uniqueness and set algebra
#
# A set is an **unordered, mutable** collection of **unique, hashable** items.
#
# ### Why sets exist
# Two things sets do that lists do badly:
# 1. **Membership test in O(1).** `x in some_set` is hash-based; for a list it's a scan.
# 2. **Set algebra** — union, intersection, difference — straight from math.


# %% color=lime title="Creating"
# @explain: Creating
# @explain: Mutate
# @explain: Length & membership
# Creating
a = {1, 2, 3, 4}
b = set([3, 4, 5, 6])     # from any iterable
empty = set()             # NOTE: {} is an EMPTY DICT, not a set
print(a, b, empty, type(empty))

# Mutate
a.add(5)
a.discard(99)             # no error if missing (vs .remove which raises)
print(a)

# Length & membership
print(len(a), 3 in a)


# %% [markdown] color=teal title="Set algebra"
# # Set algebra
#


# %% color=sky title="Method form"
# @explain: Method form (slightly more readable in long pipelines)
# @explain: Subset / superset
a = {1, 2, 3, 4}
b = {3, 4, 5, 6}

print(a | b)    # union              {1,2,3,4,5,6}
print(a & b)    # intersection       {3,4}
print(a - b)    # difference         {1,2}
print(b - a)    # difference (other direction)  {5,6}
print(a ^ b)    # symmetric diff     {1,2,5,6}

# Method form (slightly more readable in long pipelines)
print(a.union(b), a.intersection(b), a.difference(b))

# Subset / superset
print({1,2}.issubset(a))
print(a.issuperset({1,2}))


# %% [markdown] color=mint title="Two daily-life uses of sets"
# # Two daily-life uses of sets
#


# %% color=peach title="1) Dedupe a list (note: sets lose order"
# @explain: 1) Dedupe a list (note: sets lose order — use dict.fromkeys to keep order)
# @explain: 2) "Which items are in A but not in B?" — common in data validation
# 1) Dedupe a list (note: sets lose order — use dict.fromkeys to keep order)
nums = [3, 1, 4, 1, 5, 9, 2, 6, 5, 3]
print(list(set(nums)))                       # order not guaranteed
print(list(dict.fromkeys(nums)))              # de-duped, order preserved

# 2) "Which items are in A but not in B?" — common in data validation
expected_columns = {"name", "age", "email", "city"}
actual_columns   = {"name", "age", "email"}
missing = expected_columns - actual_columns
extra   = actual_columns - expected_columns
print("missing:", missing, "  extra:", extra)


# %% [markdown] color=violet title="8. Choosing the right structure"
# # 8. Choosing the right structure
#
# | Question | Use |
# |---|---|
# | "I'll change items by position" | **list** |
# | "I want to look up by name" | **dict** |
# | "Are these two values a fixed pair forever?" | **tuple** |
# | "Does this item already exist? (fast)" | **set** |
# …


# %% [markdown] color=amber title="9. Practice — try before you peek"
# # 9. Practice — try before you peek
#
# 1. From the list `[5, 2, 9, 1, 5, 6, 7, 2]`, get a **sorted list of unique values** in descending order.
# 2. Given `prices = {"apple": 0.5, "banana": 0.25, "cherry": 2.0}`, print each item as `"apple: $0.50"` (two decimal places, sorted alphabetically by name).
# 3. From two lists `students = ["Ada","Linus","Grace"]` and `scores = [85, 92, 78]`, build a dict mapping name → score.
# 4. You have two sets of users who completed Course A and Course B. Print: who finished both, who finished only A, who finished either.


# %% color=rose title="--- Try yours first ---"
# @explain: --- Try yours first ---
# @explain: --- Solutions ---
# @explain: 1)
# @explain: 2)
# @explain: 3)
# --- Try yours first ---



# --- Solutions ---
# 1)
print(sorted(set([5, 2, 9, 1, 5, 6, 7, 2]), reverse=True))

# 2)
prices = {"apple": 0.5, "banana": 0.25, "cherry": 2.0}
for name in sorted(prices):
    print(f"{name}: ${prices[name]:.2f}")

# 3)
students = ["Ada", "Linus", "Grace"]
scores   = [85, 92, 78]
print(dict(zip(students, scores)))

# 4)
A = {"ada", "linus", "grace", "guido"}
B = {"linus", "ada", "yukihiro"}
print("both:",   A & B)
print("only A:", A - B)
print("either:", A | B)


# %% [markdown] color=lime title="Recap — what you can now do"
# # Recap — what you can now do
#
# ✅ Pick the right container in 5 seconds (list / tuple / dict / set)
# ✅ Index, slice, sort, and mutate lists; copy them safely
# ✅ Read and write list/dict/set comprehensions
# ✅ Unpack tuples, including with `*rest`
# ✅ Use a dict like a mini-database (lookup, update, iterate, count)
# ✅ Use a set for dedup, fast membership, and set algebra
# …


# %% [markdown] color=lime title="Thanks"
# # End of Module
#
# Next module continues the roadmap.
# Source: https://github.com/kader-xai/data-science-roadmap


