# doodlecode format-version: 2
# Auto-converted from module_03_programming_fundamentals.ipynb
# Open with 📂 Open → press 🎬 Present.


# %% [markdown] color=rose title="Module 03 Programming Fundamentals"
# # Module 03 Programming Fundamentals
#
# A live walkthrough — one card per concept.
# Use → / ← to step through. Press 🎬 Present to begin.



# %% [markdown] color=sky title="Module 3 — Programming Fundamentals"
# # Module 3 — Programming Fundamentals
#
# *IBM Python for Data Science · Module 3 of 16*
#
# You have the alphabet (M1) and the containers (M2). Now we wire them together with **logic** — branching, looping, reusable functions, error handling, and your first taste of OOP.
#
# By the end of this module you'll have written your own mini text-analysis tool, the same kind that powers a word-cloud or a sentiment summary in real DS work.
#
# ### What you'll cover
# …


# %% [markdown] color=mint title="1. Conditions — `if / elif / else`"
# # 1. Conditions — `if / elif / else`
#
# The general shape:
#
# ```python
# if condition_1:
#     ...
# elif condition_2:
# …


# %% color=peach title="def grade(score)"
# @explain: Run this cell to see the output.
def grade(score):
    if score >= 90:
        return "A"
    elif score >= 80:
        return "B"
    elif score >= 70:
        return "C"
    elif score >= 60:
        return "D"
    else:
        return "F"

for s in [95, 82, 71, 58]:
    print(s, "->", grade(s))


# %% [markdown] color=violet title="Comparison operators (recap from M1)"
# # Comparison operators (recap from M1)
#
# `==`, `!=`, `<`, `>`, `<=`, `>=`. They return a `bool`.
#
# ### Logical operators
# `and`, `or`, `not`. Two important properties:
#
# - **Short-circuit** — `and` stops at the first falsy value, `or` stops at the first truthy. Use this to guard against errors.
# - They return one of the *operands*, not always `True`/`False`. `"hi" or "bye"` → `"hi"`.


# %% color=amber title="Short-circuit guard"
# @explain: Short-circuit guard — avoids ZeroDivisionError when n is 0
# @explain: `or` for default values (a Python idiom)
age = 25
has_id = True

print(age >= 18 and has_id)            # True
print(age < 12 or age > 65)            # False
print(not has_id)                       # False

# Short-circuit guard — avoids ZeroDivisionError when n is 0
def safe_avg(total, n):
    return n != 0 and total / n        # if n == 0, returns False; otherwise returns the avg

print(safe_avg(10, 2), safe_avg(10, 0))

# `or` for default values (a Python idiom)
name = "" or "anonymous"
print(name)


# %% [markdown] color=rose title="The ternary expression — `x if cond else y`"
# # The ternary expression — `x if cond else y`
#
# A one-line `if/else` that returns a value.


# %% color=lime title="Common in list comprehensions"
# @explain: Common in list comprehensions
age = 17
status = "adult" if age >= 18 else "minor"
print(status)

# Common in list comprehensions
nums = [1, 2, 3, 4, 5]
print(["even" if n % 2 == 0 else "odd" for n in nums])


# %% [markdown] color=teal title="2. `match` — pattern matching (Python 3.10+)"
# # 2. `match` — pattern matching (Python 3.10+)
#
# Like `switch` in other languages but more powerful — it can destructure tuples, lists, and dicts.


# %% color=sky title="def describe(point)"
# @explain: Run this cell to see the output.
def describe(point):
    match point:
        case (0, 0):
            return "origin"
        case (x, 0):
            return f"on the x-axis at x={x}"
        case (0, y):
            return f"on the y-axis at y={y}"
        case (x, y):
            return f"point at ({x}, {y})"
        case _:
            return "not a point"

print(describe((0, 0)))
print(describe((3, 0)))
print(describe((4, 5)))


# %% [markdown] color=mint title="3. Loops"
# # 3. Loops
#
# Two flavours: `for` (iterate over a collection) and `while` (run while a condition holds).
#
# ### `for` — the workhorse
# A `for` loop walks any **iterable** (list, tuple, dict, set, string, range, file, generator…).


# %% color=peach title="Over a list"
# @explain: Over a list
# @explain: Over a string
# @explain: Over a dict — by default, keys
# @explain: Cleaner: items()
# Over a list
for fruit in ["apple", "banana", "cherry"]:
    print(fruit)

# Over a string
for ch in "abc":
    print(ch)

# Over a dict — by default, keys
d = {"x": 1, "y": 2, "z": 3}
for k in d:
    print(k, d[k])

# Cleaner: items()
for k, v in d.items():
    print(f"{k} -> {v}")


# %% [markdown] color=violet title="`range`, `enumerate`, `zip` — three helpers you'll use daily"
# # `range`, `enumerate`, `zip` — three helpers you'll use daily
#
# | Helper | What it gives you |
# |---|---|
# | `range(stop)` / `range(start, stop, step)` | a lazy sequence of integers |
# | `enumerate(seq)` | `(index, value)` pairs — when you need the position too |
# | `zip(a, b)` | parallel pairs from two iterables |


# %% color=amber title="range"
# @explain: range
# @explain: enumerate — when you need both index and value
# @explain: zip — walk two lists in lockstep
# @explain: zip stops at the shortest — itertools.zip_longest fills missing
# range
for i in range(5):                # 0..4
    print(i, end=" ")
print()
print(list(range(2, 11, 2)))      # [2,4,6,8,10]

# enumerate — when you need both index and value
words = ["alpha", "beta", "gamma"]
for i, w in enumerate(words):
    print(i, w)

# zip — walk two lists in lockstep
names  = ["Ada", "Linus", "Grace"]
scores = [85, 92, 78]
for name, score in zip(names, scores):
    print(f"{name}: {score}")

# zip stops at the shortest — itertools.zip_longest fills missing
from itertools import zip_longest
for a, b in zip_longest([1,2,3], ["x","y"], fillvalue="-"):
    print(a, b)


# %% [markdown] color=rose title="`while` — when you don't know how many iterations"
# # `while` — when you don't know how many iterations
#
# Use `while` when the *condition* drives the loop, not a known sequence.


# %% color=lime title="Classic: keep dividing until small enough"
# @explain: Classic: keep dividing until small enough
# @explain: Counted loop with while (a for+range is usually cleaner)
# Classic: keep dividing until small enough
n = 100
while n > 1:
    n = n // 2
    print(n, end=" ")
print()

# Counted loop with while (a for+range is usually cleaner)
i = 0
while i < 5:
    print(i, end=" ")
    i += 1
print()


# %% [markdown] color=teal title="`break`, `continue`, and the (rare) `else` on a loop"
# # `break`, `continue`, and the (rare) `else` on a loop
#
# - `break` — stop the loop immediately.
# - `continue` — skip to the next iteration.
# - `else` on a loop — runs **only if the loop finished without `break`**. Useful for "search and report not-found".


# %% color=sky title="break and continue"
# @explain: break and continue
# @explain: for/else — runs only when loop completed without break
# break and continue
for n in range(10):
    if n == 7:
        break             # stop entirely
    if n % 2 == 0:
        continue          # skip evens
    print(n, end=" ")
print()

# for/else — runs only when loop completed without break
def find_first_even(nums):
    for n in nums:
        if n % 2 == 0:
            print(f"found even: {n}")
            break
    else:
        print("no even number found")

find_first_even([1, 3, 4, 5])
find_first_even([1, 3, 5, 7])


# %% [markdown] color=mint title="4. Functions — turn logic into a name"
# # 4. Functions — turn logic into a name
#
# A function is a **named, reusable block of code** with inputs (parameters) and an output (`return` value). Use them whenever you'd be tempted to copy-paste a few lines.
#
# ### Anatomy
# ```python
# def name(param1, param2=default, *args, **kwargs):
#     """Docstring — what this does."""
# …


# %% color=peach title="def add(a"
# @explain: Run this cell to see the output.
def add(a, b):
    """Return a + b."""
    return a + b

print(add(2, 3))
print(add.__doc__)        # access the docstring


# %% [markdown] color=violet title="Default values"
# # Default values
#
# Parameters with `=` get a default. Defaults make the parameter optional at the call site.


# %% color=amber title="def greet(name"
# @explain: Run this cell to see the output.
def greet(name, greeting="Hello"):
    return f"{greeting}, {name}!"

print(greet("Kader"))
print(greet("Ada", "Hi"))


# %% [markdown] color=rose title="Keyword arguments"
# # Keyword arguments
#
# You can pass arguments **by name** at the call site. Improves readability and lets you skip earlier args.


# %% color=lime title="Positional"
# @explain: Positional
# @explain: Mix positional and keyword (keyword args must come last)
def report(name, score, max_score=100, passed=True):
    return f"{name}: {score}/{max_score} ({'PASS' if passed else 'FAIL'})"

# Positional
print(report("Ada", 85))

# Mix positional and keyword (keyword args must come last)
print(report("Linus", 95, passed=True))
print(report("Grace", score=78, passed=False))


# %% [markdown] color=teal title="`*args` and `**kwargs` — variable-length arguments"
# # `*args` and `**kwargs` — variable-length arguments
#
# - `*args` collects extra positional arguments into a **tuple**.
# - `**kwargs` collects extra keyword arguments into a **dict**.


# %% color=sky title="Combine"
# @explain: Combine
def stats(*nums):
    """Mean of any number of values."""
    return sum(nums) / len(nums)

print(stats(1, 2, 3))
print(stats(1, 2, 3, 4, 5, 6, 7))

def describe(**props):
    for k, v in props.items():
        print(f"{k} = {v}")

describe(name="Kader", age=38, city="Riyadh")

# Combine
def log(level, *messages, **meta):
    print(f"[{level}]", *messages, "| meta:", meta)

log("INFO", "user logged in", "from web", user_id=42, ip="1.2.3.4")


# %% [markdown] color=mint title="Returning multiple values"
# # Returning multiple values
#
# A function can return a tuple — and the caller can unpack it.


# %% color=peach title="def min_max(values)"
# @explain: Run this cell to see the output.
def min_max(values):
    return min(values), max(values)         # returns a tuple

lo, hi = min_max([3, 1, 4, 1, 5, 9, 2, 6])
print(lo, hi)


# %% [markdown] color=violet title="5. Variable scope — the LEGB rule"
# # 5. Variable scope — the LEGB rule
#
# When you reference a name, Python looks it up in this order:
#
# 1. **L**ocal — inside the current function.
# 2. **E**nclosing — inside any outer function (for nested defs).
# 3. **G**lobal — module level.
# 4. **B**uilt-in — names like `print`, `len`, `sum`.
# …


# %% color=amber title="x = 'global x'"
# @explain: Run this cell to see the output.
x = "global x"

def outer():
    x = "outer x"
    def inner():
        x = "inner x"
        print("inner sees:", x)
    inner()
    print("outer sees:", x)

outer()
print("module sees:", x)


# %% color=rose title="global"
# @explain: global — modify a module-level variable from inside a function
# @explain: nonlocal — modify the enclosing function's variable
# global — modify a module-level variable from inside a function
counter = 0
def bump():
    global counter
    counter += 1

bump(); bump(); bump()
print("counter =", counter)

# nonlocal — modify the enclosing function's variable
def make_counter():
    n = 0
    def inc():
        nonlocal n
        n += 1
        return n
    return inc

c = make_counter()
print(c(), c(), c())


# %% [markdown] color=lime title="6. Lambdas — tiny anonymous functions"
# # 6. Lambdas — tiny anonymous functions
#
# Syntax: `lambda args: expression`. Use only when you need a **single-expression** function inline (most often as a `key=` argument).


# %% color=teal title="Where lambdas shine: as `key=` for sort/min/max"
# @explain: Where lambdas shine: as `key=` for sort/min/max
# @explain: Functions are first-class — pass them around like any value
square = lambda x: x ** 2
print(square(7))

# Where lambdas shine: as `key=` for sort/min/max
people = [("Ada", 36), ("Linus", 54), ("Grace", 85)]
print(sorted(people, key=lambda p: p[1]))   # sort by age

# Functions are first-class — pass them around like any value
def apply(fn, x):
    return fn(x)

print(apply(square, 5))
print(apply(lambda s: s.upper(), "hi"))


# %% [markdown] color=sky title="7. Exception handling — never let one bad row crash a pipeline"
# # 7. Exception handling — never let one bad row crash a pipeline
#
# ```python
# try:
#     risky_thing()
# except SomeError as e:
#     handle_it(e)
# except (OtherError, AnotherError):
# …


# %% color=mint title="def safe_divide(a"
# @explain: Run this cell to see the output.
def safe_divide(a, b):
    try:
        return a / b
    except ZeroDivisionError:
        return float("inf")
    except TypeError as e:
        return f"bad input: {e}"

print(safe_divide(10, 2))
print(safe_divide(10, 0))
print(safe_divide(10, "x"))


# %% color=peach title="Multiple except clauses + else + finally"
# @explain: Multiple except clauses + else + finally
# Multiple except clauses + else + finally
def parse_int(s):
    try:
        n = int(s)
    except ValueError:
        print("can't parse", repr(s))
        return None
    except TypeError:
        print("wrong type:", type(s))
        return None
    else:
        print("parsed cleanly")
        return n
    finally:
        print("done with", repr(s))

print(parse_int("42"))
print(parse_int("abc"))
print(parse_int(None))


# %% [markdown] color=violet title="Raising your own exceptions"
# # Raising your own exceptions
#
# When the input violates an assumption, **raise** rather than returning a magic value.


# %% color=amber title="def take_square_root(x)"
# @explain: Run this cell to see the output.
def take_square_root(x):
    if x < 0:
        raise ValueError(f"need non-negative; got {x}")
    return x ** 0.5

print(take_square_root(9))

try:
    take_square_root(-1)
except ValueError as e:
    print("caught:", e)


# %% [markdown] color=rose title="8. Objects and Classes — first taste of OOP"
# # 8. Objects and Classes — first taste of OOP
#
# A **class** is a blueprint. An **instance** is a concrete thing built from it.
#
# Why care: every Pandas `DataFrame`, every NumPy `array`, every scikit-learn model is an object. Knowing how classes work demystifies the libraries.
#
# ### Anatomy
# ```python
# …


# %% color=lime title="class BankAccount"
# @explain: Run this cell to see the output.
class BankAccount:
    """A toy bank account."""

    def __init__(self, owner, balance=0):
        self.owner   = owner       # attribute
        self.balance = balance

    def deposit(self, amount):
        self.balance += amount
        return self.balance

    def withdraw(self, amount):
        if amount > self.balance:
            raise ValueError("insufficient funds")
        self.balance -= amount
        return self.balance

    def __repr__(self):
        return f"BankAccount(owner={self.owner!r}, balance={self.balance})"


a = BankAccount("Kader", 100)
a.deposit(50)
a.withdraw(30)
print(a)
print(a.balance, a.owner)


# %% [markdown] color=teal title="Class vs instance attributes"
# # Class vs instance attributes
#


# %% color=sky title="class Dog"
# @explain: Run this cell to see the output.
class Dog:
    species = "Canis familiaris"      # class attribute — shared by all instances

    def __init__(self, name):
        self.name = name              # instance attribute — per dog

d1 = Dog("Rex")
d2 = Dog("Buddy")
print(d1.name, d2.name, d1.species, d2.species)
print(Dog.species)


# %% [markdown] color=mint title="Inheritance — reuse with a tweak"
# # Inheritance — reuse with a tweak
#


# %% color=peach title="class Animal"
# @explain: Run this cell to see the output.
class Animal:
    def __init__(self, name):
        self.name = name
    def speak(self):
        return "..."

class Dog(Animal):
    def speak(self):           # override
        return "woof"

class Cat(Animal):
    def speak(self):
        return "meow"

for a in [Dog("Rex"), Cat("Whiskers")]:
    print(a.name, "says", a.speak())


# %% [markdown] color=violet title="9. Mini project — text analysis"
# # 9. Mini project — text analysis
#
# We'll build a small text analyser that:
# 1. Cleans text (lowercase, strip punctuation).
# 2. Tokenises into words.
# 3. Removes common stopwords.
# 4. Returns the top-N most frequent words.
#
# …


# %% color=amber title="import string"
# @explain: Run this cell to see the output.
import string
from collections import Counter

STOPWORDS = {"the","a","an","and","or","but","is","are","was","were","of","to",
             "in","on","at","for","with","this","that","it","its","by","as","be"}

def clean(text):
    """Lowercase and strip punctuation."""
    text = text.lower()
    text = text.translate(str.maketrans("", "", string.punctuation))
    return text

def tokenize(text):
    return clean(text).split()

def remove_stopwords(tokens, extra=None):
    stops = STOPWORDS | (extra or set())
    return [t for t in tokens if t not in stops]

def top_n(tokens, n=5):
    return Counter(tokens).most_common(n)


sample = """
Python is a popular language for data science. Data science with Python is fun,
because Python has Pandas, NumPy, and many libraries. Many libraries make data
science productive. Practice Python every day to master data science!
"""

tokens = remove_stopwords(tokenize(sample))
print("token count:", len(tokens))
print("top 5:")
for word, n in top_n(tokens, 5):
    print(f"  {word:>10} {n}")


# %% color=rose title="Now wrap it in a class"
# @explain: Now wrap it in a class — the OO version of the same thing
# Now wrap it in a class — the OO version of the same thing
class TextAnalyzer:
    def __init__(self, text, extra_stopwords=None):
        self.text = text
        self.stops = STOPWORDS | (extra_stopwords or set())
        self._tokens = None

    @property
    def tokens(self):
        if self._tokens is None:           # cache after first computation
            self._tokens = [t for t in tokenize(self.text) if t not in self.stops]
        return self._tokens

    def top(self, n=5):
        return Counter(self.tokens).most_common(n)

    def __repr__(self):
        return f"TextAnalyzer({len(self.text)} chars, {len(self.tokens)} words)"


a = TextAnalyzer(sample)
print(a)
print(a.top(3))


# %% [markdown] color=lime title="10. Practice — try before you peek"
# # 10. Practice — try before you peek
#
# 1. Write a function `fizzbuzz(n)` that returns a list of strings 1..n where multiples of 3 → `"Fizz"`, multiples of 5 → `"Buzz"`, multiples of both → `"FizzBuzz"`, others → the number as a string.
# 2. Write `count_vowels(s)` that returns how many vowels (`a, e, i, o, u`) are in a string, case-insensitive.
# 3. Write a class `Rectangle` with `width`, `height`, methods `area()` and `perimeter()`, and a `__repr__`. Bonus: make a subclass `Square` that takes only `side`.
# 4. Wrap `int(input(...))` in a function `read_int(prompt)` that re-asks (in a loop) until the user enters a valid integer.


# %% color=teal title="--- Try yours first ---"
# @explain: --- Try yours first ---
# @explain: --- Solutions ---
# @explain: 1)
# @explain: 2)
# @explain: 3)
# --- Try yours first ---



# --- Solutions ---

# 1)
def fizzbuzz(n):
    out = []
    for i in range(1, n+1):
        if i % 15 == 0:    out.append("FizzBuzz")
        elif i % 3 == 0:   out.append("Fizz")
        elif i % 5 == 0:   out.append("Buzz")
        else:              out.append(str(i))
    return out
print(fizzbuzz(15))

# 2)
def count_vowels(s):
    return sum(1 for ch in s.lower() if ch in "aeiou")
print(count_vowels("Hello World"))     # 3

# 3)
class Rectangle:
    def __init__(self, width, height):
        self.width, self.height = width, height
    def area(self):       return self.width * self.height
    def perimeter(self):  return 2 * (self.width + self.height)
    def __repr__(self):   return f"Rectangle({self.width}x{self.height})"

class Square(Rectangle):
    def __init__(self, side):
        super().__init__(side, side)

print(Rectangle(3, 4).area(), Square(5).area(), Square(5))

# 4)
def read_int(prompt):
    while True:
        raw = input(prompt)
        try:
            return int(raw)
        except ValueError:
            print("  not an integer, try again.")
# read_int("enter age: ")     # uncomment to try interactively
print("(read_int defined — call it interactively)")


# %% [markdown] color=sky title="Recap — what you can now do"
# # Recap — what you can now do
#
# ✅ Branch with `if/elif/else` and the ternary `x if c else y`
# ✅ Use `match` for pattern-style branching
# ✅ Loop with `for` and `while`; use `range`, `enumerate`, `zip`, `break`, `continue`, loop-`else`
# ✅ Write functions with defaults, keyword args, `*args`, `**kwargs`, and docstrings
# ✅ Reason about scope using LEGB; reach for `global`/`nonlocal` only when needed
# ✅ Pass functions and lambdas as values
# …


# %% [markdown] color=lime title="Thanks"
# # End of Module
#
# Next module continues the roadmap.
# Source: https://github.com/kader-xai/data-science-roadmap


