# %% [markdown]
# # ✨ Simple Python
# A gentle, one-sitting walk through the building blocks of Python.
# Read the callout on the right, run the code on the left, and watch
# how each idea snaps into place.


# %% [markdown]
# ## 1. Saying hello


# %% kind=expr color=sky title="Hello, world"
# @explain: `print` puts whatever you give it on the screen.
# @explain: The quotes mark it as a string — a piece of text.
print("Hello, world!")


# %% kind=expr color=sky title="Many things at once"
# @explain: Give print several values and it puts a space between them.
# @explain: That little detail saves so much typing.
print("Python", "is", "friendly")


# %% [markdown]
# ## 2. Boxes with names — variables
# A **variable** is a label you stick on a value. Once labelled, you
# can refer to the value by its name anywhere later.


# %% kind=assign color=peach title="Naming a value"
# @explain: `name` is the label. `"Ada"` is the value.
# @explain: The `=` sign means "store this on the right under that name".
name = "Ada"
age = 32

print(name, age)


# %% kind=assign color=peach title="Numbers do math"
# @explain: + − × ÷ work as you'd expect. Python uses `*` for times
# @explain: and `/` for divide. Parentheses change the order.
price = 9.99
quantity = 3

total = price * quantity
print("total:", total)


# %% [markdown]
# ## 3. Talking with text — f-strings
# Curly braces inside an `f"..."` string get replaced by the value
# of whatever you put in them. The fastest way to build sentences.


# %% kind=expr color=mint title="Building a sentence"
# @explain: `f"…{name}…"` plugs the value of `name` into the string.
# @explain: Numbers can be formatted too — `:.2f` keeps 2 decimals.
print(f"Hi {name}, you ordered {quantity} items for ${total:.2f}.")


# %% [markdown]
# ## 4. Choosing — `if`
# A condition is a question that returns **True** or **False**.
# The block under `if` only runs when the answer is True.


# %% kind=conditional color=yellow title="If the answer is yes…"
# @explain: `>=` means "greater than or equal to". The indent matters —
# @explain: it tells Python which lines belong to the `if`.
temperature = 28

if temperature > 25:
    print("☀️  warm — wear a t-shirt")
else:
    print("🧥  cool — grab a jacket")


# %% [markdown]
# ## 5. Repeating — `for`
# A `for` loop runs the same block once for each value in a sequence.
# Perfect when you have many similar things to do.


# %% kind=loop color=violet title="Counting"
# @explain: `range(5)` yields 0, 1, 2, 3, 4 — five values.
# @explain: `i` takes each one in turn.
for i in range(5):
    print(f"  step {i}")


# %% kind=loop color=violet title="Looping over real items"
# @explain: A square-bracket list holds many values in order.
# @explain: The loop visits each fruit on its own line.
fruits = ["apple", "banana", "cherry", "date"]
for fruit in fruits:
    print(f"  🍇 {fruit}")


# %% [markdown]
# ## 6. Packaging up — functions
# A **function** is a reusable mini-program. You give it inputs,
# it does its work, and `return`s an answer.


# %% kind=function color=mint title="Your first function"
# @explain: `def` starts the recipe. The names in parens are the inputs.
# @explain: `return` hands the answer back to the caller.
def greet(person, language="English"):
    if language == "Spanish":
        return f"¡Hola, {person}!"
    if language == "Japanese":
        return f"こんにちは、{person}さん"
    return f"Hello, {person}!"


print(greet("Ada"))
print(greet("Ada", language="Spanish"))
print(greet("Ada", language="Japanese"))


# %% kind=function color=mint title="Functions can call functions"
# @explain: `average` uses `sum` and `len` — both built-in.
# @explain: Functions stay small by leaning on each other.
def average(numbers):
    return sum(numbers) / len(numbers)


scores = [88, 92, 75, 99, 81]
print(f"average: {average(scores):.1f}")
print(f"highest: {max(scores)}")
print(f"lowest : {min(scores)}")


# %% [markdown]
# ## 7. Putting it all together
# Six cells of work, one tiny program. This is how real Python
# looks — small pieces, each doing one thing well.


# %% kind=function color=pink title="A friendly report"
# @explain: We combine a list, a loop, a function, and an f-string
# @explain: to print a tidy summary. Nothing here you haven't seen.
def report(name, scores):
    avg = average(scores)
    verdict = "great work" if avg >= 85 else "keep going"
    print(f"📋  {name}'s report")
    print(f"   scores : {scores}")
    print(f"   average: {avg:.1f}  →  {verdict}")


report("Ada", [88, 92, 75, 99, 81])
print()
report("Linus", [70, 65, 80, 60])


# %% [markdown]
# ## 🎉 You can now…
# - Print, name values, do arithmetic
# - Format sentences with **f-strings**
# - Choose with **if / else**
# - Repeat with **for**
# - Package logic into **functions**
#
# That's enough to start solving real problems. Next stops:
# **lists & dictionaries**, **reading files**, **importing libraries**.
# Open the other modules in `examples/` whenever you're ready.
