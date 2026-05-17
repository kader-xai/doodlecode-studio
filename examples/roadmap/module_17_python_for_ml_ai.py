# doodlecode format-version: 2
# Auto-converted from module_17_python_for_ml_ai.ipynb
# Open with 📂 Open → press 🎬 Present.


# %% [markdown] color=rose title="Module 17 Python For Ml Ai"
# # Module 17 Python For Ml Ai
#
# A live walkthrough — one card per concept.
# Use → / ← to step through. Press 🎬 Present to begin.



# %% [markdown] color=sky title="Python for Machine Learning & AI — Practice Notebook"
# # Python for Machine Learning & AI — Practice Notebook
#
# **Companion to the *Python for ML & AI* course doc.**
#
# The doc explains the *why*. This notebook is the *do* — every concept comes with runnable code and short exercises so the muscle memory sticks.
#
# Suggested workflow:
# 1. Read a chapter in the doc.
# …


# %% [markdown] color=mint title="Module 1 — Python Language Essentials"
# # Module 1 — Python Language Essentials
#
# ### 1.1 Types, truthiness, `is` vs `==`


# %% color=peach title="Truthiness"
# @explain: Truthiness — empty containers are False, zero is False, None is False
# Truthiness — empty containers are False, zero is False, None is False
test_values = [0, 1, "", "hello", [], [1], None, True, False, {}, {"a": 1}]
for v in test_values:
    print(f"{repr(v):>15}  -> bool: {bool(v)}")


# %% color=violet title="is vs =="
# @explain: is vs == — the classic gotcha
# @explain: Always use `is` for None
# is vs == — the classic gotcha
a = [1, 2, 3]
b = [1, 2, 3]
print("a == b :", a == b)    # True  -> same value
print("a is b :", a is b)    # False -> different objects

# Always use `is` for None
result = None
print("is None:", result is None)


# %% [markdown] color=amber title="Exercise 1.1.** Write a function `safe_divide(a,…"
# # Exercise 1.1.** Write a function `safe_divide(a,…
#
# **Exercise 1.1.** Write a function `safe_divide(a, b)` that returns `None` if `b == 0`, otherwise `a / b`. Then write a one-liner that prints "ok" if the result is not None, "skip" otherwise.


# %% color=rose title="Your code here"
# @explain: Your code here
# @explain: Test
# Your code here
def safe_divide(a, b):
    pass  # TODO

# Test
for a, b in [(10, 2), (10, 0), (3, 4)]:
    result = safe_divide(a, b)
    print("ok" if result is not None else "skip", result)


# %% [markdown] color=lime title="1.2 Control flow & enumerate / zip"
# # 1.2 Control flow & enumerate / zip
#


# %% color=teal title="Bad"
# @explain: Bad
# @explain: Good
# @explain: zip — iterate two lists in lockstep
words = ["transformer", "attention", "embedding", "tokenizer"]

# Bad
for i in range(len(words)):
    print(i, words[i])

print()

# Good
for i, w in enumerate(words):
    print(i, w)

print()

# zip — iterate two lists in lockstep
labels = [0, 1, 0, 1]
for w, lbl in zip(words, labels):
    print(f"{w:>12} -> {lbl}")


# %% [markdown] color=sky title="Exercise 1.2.** Given two lists `predictions = [1,…"
# # Exercise 1.2.** Given two lists `predictions = [1,…
#
# **Exercise 1.2.** Given two lists `predictions = [1, 0, 1, 1, 0]` and `labels = [1, 1, 1, 0, 0]`, compute the accuracy (fraction correct) using a single comprehension + `sum()`. Don't use NumPy yet.


# %% color=mint title="Your code here"
# @explain: Your code here
predictions = [1, 0, 1, 1, 0]
labels      = [1, 1, 1, 0, 0]

# Your code here
accuracy = ...   # TODO
print(f"accuracy: {accuracy}")


# %% [markdown] color=peach title="Module 2 — Data Structures"
# # Module 2 — Data Structures
#
# ### 2.1 Lists, sets, dicts — and choosing between them


# %% color=violet title="Membership test: list vs set on big data"
# @explain: Membership test: list vs set on big data
# Membership test: list vs set on big data
import time

big_list = list(range(100_000))
big_set  = set(big_list)

target = 99_999

t0 = time.perf_counter()
for _ in range(1000):
    target in big_list
list_time = time.perf_counter() - t0

t0 = time.perf_counter()
for _ in range(1000):
    target in big_set
set_time  = time.perf_counter() - t0

print(f"list membership: {list_time*1000:.1f} ms")
print(f"set  membership: {set_time*1000:.1f} ms")
print(f"speedup: {list_time/set_time:.0f}x")


# %% [markdown] color=amber title="2.2 Dict idioms"
# # 2.2 Dict idioms
#


# %% color=rose title="Group strings by their first letter"
# @explain: Group strings by their first letter
# @explain: Count occurrences
# @explain: Invert a mapping
from collections import defaultdict, Counter

# Group strings by their first letter
words = ["apple", "ant", "banana", "berry", "cherry", "blueberry"]
grouped = defaultdict(list)
for w in words:
    grouped[w[0]].append(w)
print(dict(grouped))

# Count occurrences
text = "the quick brown fox jumps over the lazy dog the fox"
counts = Counter(text.split())
print(counts.most_common(3))

# Invert a mapping
id_to_label = {0: "cat", 1: "dog", 2: "bird"}
label_to_id = {v: k for k, v in id_to_label.items()}
print(label_to_id)


# %% [markdown] color=lime title="Exercise 2.2.** You have transaction records"
# # Exercise 2.2.** You have transaction records
#
# **Exercise 2.2.** You have transaction records. Group them by category and compute total spend per category in one go.
#
# ```
# transactions = [
#     {"category": "food",      "amount": 25.50},
#     {"category": "transport", "amount": 12.00},
#     {"category": "food",      "amount": 18.75},
#     {"category": "books",     "amount": 45.00},
# …


# %% color=teal title="Your code here"
# @explain: Your code here — try with defaultdict
transactions = [
    {"category": "food",      "amount": 25.50},
    {"category": "transport", "amount": 12.00},
    {"category": "food",      "amount": 18.75},
    {"category": "books",     "amount": 45.00},
    {"category": "transport", "amount": 8.50},
]

# Your code here — try with defaultdict
totals = ...   # TODO
print(totals)


# %% [markdown] color=sky title="Module 3 — Comprehensions & Generators"
# # Module 3 — Comprehensions & Generators
#


# %% color=mint title="List comprehension vs loop"
# @explain: List comprehension vs loop
# @explain: Old way
# @explain: Pythonic
# @explain: Dict / set comprehensions
# List comprehension vs loop
nums = range(20)

# Old way
squares = []
for n in nums:
    if n % 2 == 0:
        squares.append(n * n)

# Pythonic
squares = [n * n for n in nums if n % 2 == 0]
print(squares)

# Dict / set comprehensions
word_lengths = {w: len(w) for w in ["foo", "bar", "longer"]}
print(word_lengths)

unique_lengths = {len(w) for w in ["foo", "bar", "longer"]}
print(unique_lengths)


# %% color=peach title="Generators"
# @explain: Generators — lazy, memory-efficient
# @explain: Materialize when you need a list
# @explain: Or stream — useful for big datasets
# Generators — lazy, memory-efficient
def first_n_primes(n):
    found = []
    candidate = 2
    while len(found) < n:
        if all(candidate % p != 0 for p in found):
            yield candidate
            found.append(candidate)
        candidate += 1

# Materialize when you need a list
print(list(first_n_primes(10)))

# Or stream — useful for big datasets
for prime in first_n_primes(5):
    print(prime, end=" ")


# %% [markdown] color=violet title="Exercise 3.** Write a generator `batched(iterable,…"
# # Exercise 3.** Write a generator `batched(iterable,…
#
# **Exercise 3.** Write a generator `batched(iterable, batch_size)` that yields tuples of size `batch_size`. The last batch may be smaller. This is a common pattern for ML data loaders.
#
# Example: `list(batched(range(7), 3))` → `[(0,1,2), (3,4,5), (6,)]`


# %% color=amber title="Test"
# @explain: Test
# @explain: Expected: [(0,1,2), (3,4,5), (6,)]
def batched(iterable, batch_size):
    pass  # TODO

# Test
print(list(batched(range(7), 3)))
# Expected: [(0,1,2), (3,4,5), (6,)]


# %% [markdown] color=rose title="Module 4 — Functions"
# # Module 4 — Functions
#
# ### 4.1 Argument handling


# %% color=lime title="Keyword-only args after *"
# @explain: Keyword-only args after *
# @explain: Unpack a dict as kwargs
def train(model, dataset, *, epochs=10, lr=1e-3, **extras):
    print(f"model={model}, dataset={dataset}")
    print(f"epochs={epochs}, lr={lr}")
    print(f"extras={extras}")

# Keyword-only args after *
train("gpt2", "wikipedia", epochs=5, lr=3e-4, weight_decay=0.01)

# Unpack a dict as kwargs
config = {"epochs": 3, "lr": 1e-3}
train("bert", "imdb", **config)


# %% [markdown] color=teal title="4.2 Decorators"
# # 4.2 Decorators
#


# %% color=sky title="import time"
# @explain: Run this cell to see the output.
import time
from functools import wraps

def timed(fn):
    @wraps(fn)
    def wrapper(*args, **kwargs):
        t0 = time.perf_counter()
        result = fn(*args, **kwargs)
        print(f"{fn.__name__} took {time.perf_counter()-t0:.4f}s")
        return result
    return wrapper

@timed
def slow_loop(n):
    total = 0
    for i in range(n):
        total += i
    return total

slow_loop(1_000_000)


# %% [markdown] color=mint title="Exercise 4.** Write a decorator `@retry(n=3)` that…"
# # Exercise 4.** Write a decorator `@retry(n=3)` that…
#
# **Exercise 4.** Write a decorator `@retry(n=3)` that re-runs a function up to `n` times if it raises an exception. After `n` failures, re-raise the last exception. Test it on a function that fails the first two times.


# %% color=peach title="Your code here"
# @explain: Your code here
# @explain: Test scaffolding
# @explain: print(flaky())   # uncomment after implementing
# Your code here
def retry(n=3):
    pass  # TODO

# Test scaffolding
attempt = {"count": 0}

@retry(n=3)
def flaky():
    attempt["count"] += 1
    if attempt["count"] < 3:
        raise RuntimeError(f"fail #{attempt['count']}")
    return "succeeded on attempt 3"

# print(flaky())   # uncomment after implementing


# %% [markdown] color=violet title="Module 5 — Object-Oriented Python"
# # Module 5 — Object-Oriented Python
#


# %% color=amber title="Iteration works for free once __getitem__ is defined"
# @explain: Iteration works for free once __getitem__ is defined
class Dataset:
    def __init__(self, name, samples):
        self.name = name
        self.samples = samples

    def __len__(self):                    # makes len(ds) work
        return len(self.samples)

    def __getitem__(self, idx):           # makes ds[i] work
        return self.samples[idx]

    def __repr__(self):
        return f"Dataset({self.name!r}, n={len(self)})"

ds = Dataset("toy", [(1, "a"), (2, "b"), (3, "c")])
print(ds)
print(len(ds))
print(ds[1])

# Iteration works for free once __getitem__ is defined
for item in ds:
    print(item)


# %% color=rose title="@dataclass"
# @explain: @dataclass — for data containers
# @dataclass — for data containers
from dataclasses import dataclass, field

@dataclass
class TrainConfig:
    model_name: str
    epochs: int = 10
    lr: float = 1e-4
    tags: list[str] = field(default_factory=list)

cfg = TrainConfig("gpt2", epochs=3, lr=3e-4, tags=["small", "smoke-test"])
print(cfg)


# %% [markdown] color=lime title="Exercise 5.** Build a `RunningStats` class that…"
# # Exercise 5.** Build a `RunningStats` class that…
#
# **Exercise 5.** Build a `RunningStats` class that incrementally tracks the mean and standard deviation of a stream of numbers. It should support `.add(x)` and have `.mean` and `.std` properties. Use Welford's online algorithm or just keep running sums — your call.


# %% color=teal title="Your code here"
# @explain: Your code here
# @explain: Test
# @explain: stats = RunningStats()
# @explain: for x in [4.0, 8.0, 6.0, 5.0, 3.0, 7.0]:
# @explain: stats.add(x)
# Your code here
class RunningStats:
    def __init__(self):
        pass  # TODO

# Test
# stats = RunningStats()
# for x in [4.0, 8.0, 6.0, 5.0, 3.0, 7.0]:
#     stats.add(x)
# print(f"mean={stats.mean:.3f}, std={stats.std:.3f}")
# Expected approx: mean=5.5, std=1.71


# %% [markdown] color=sky title="Module 6 — Errors, Files, Modules"
# # Module 6 — Errors, Files, Modules
#


# %% color=mint title="Specific exception handling"
# @explain: Specific exception handling
# Specific exception handling
def safe_int(s, default=None):
    try:
        return int(s)
    except ValueError:
        return default

print(safe_int("42"))      # 42
print(safe_int("abc"))     # None
print(safe_int("abc", -1)) # -1


# %% color=peach title="Files & context managers"
# @explain: Files & context managers
# @explain: Stream line-by-line for big files
# Files & context managers
sample_path = "/tmp/sample.txt"

with open(sample_path, "w") as f:
    f.write("line 1\nline 2\nline 3\n")

# Stream line-by-line for big files
with open(sample_path) as f:
    for line_num, line in enumerate(f, start=1):
        print(f"{line_num}: {line.rstrip()}")


# %% color=violet title="Custom context manager"
# @explain: Custom context manager — for timing or any 'enter/exit' pattern
# Custom context manager — for timing or any 'enter/exit' pattern
from contextlib import contextmanager
import time

@contextmanager
def timer(label):
    t0 = time.perf_counter()
    yield
    print(f"{label}: {time.perf_counter()-t0:.4f}s")

with timer("squares"):
    sum(i*i for i in range(1_000_000))


# %% [markdown] color=amber title="Module 7 — NumPy"
# # Module 7 — NumPy
#
# NumPy is where the speed comes from. Master broadcasting and indexing here and you'll write 10× less code in PyTorch.


# %% color=rose title="Creation"
# @explain: Creation
import numpy as np

# Creation
a = np.array([1, 2, 3, 4])
b = np.zeros((3, 4))
c = np.ones((2, 2), dtype=np.int32)
d = np.arange(0, 1, 0.1)
e = np.linspace(0, 1, 11)
f = np.random.randn(3, 4)

print(f"a: shape={a.shape}, dtype={a.dtype}")
print(f"b: shape={b.shape}")
print(f"f.shape={f.shape}, f.size={f.size}, f.ndim={f.ndim}")


# %% color=lime title="Vectorization"
# @explain: Vectorization — operations on whole arrays
# @explain: Pure Python
# @explain: NumPy
# Vectorization — operations on whole arrays
import numpy as np
import time

N = 1_000_000
arr_py  = list(range(N))
arr_np  = np.arange(N)

# Pure Python
t0 = time.perf_counter()
result = [x * 2 + 1 for x in arr_py]
py_time = time.perf_counter() - t0

# NumPy
t0 = time.perf_counter()
result = arr_np * 2 + 1
np_time = time.perf_counter() - t0

print(f"Python list comp: {py_time*1000:.1f} ms")
print(f"NumPy vectorized: {np_time*1000:.1f} ms")
print(f"Speedup: {py_time/np_time:.0f}x")


# %% color=teal title="Broadcasting"
# @explain: Broadcasting
# @explain: Add a row vector to every row
# @explain: Per-column normalization (mean 0, std 1)
# Broadcasting
import numpy as np

X = np.array([[1, 2, 3],
              [4, 5, 6],
              [7, 8, 9]])

# Add a row vector to every row
bias = np.array([10, 20, 30])
print("X + bias:")
print(X + bias)

# Per-column normalization (mean 0, std 1)
data = np.random.randn(100, 5)
mean = data.mean(axis=0, keepdims=True)
std  = data.std(axis=0, keepdims=True)
normalized = (data - mean) / std
print(f"\nNormalized shape: {normalized.shape}")
print(f"Per-column mean (~0): {normalized.mean(axis=0)}")
print(f"Per-column std (~1):  {normalized.std(axis=0)}")


# %% color=sky title="Boolean masking & fancy indexing"
# @explain: Boolean masking & fancy indexing
# @explain: Top-3 scores
# Boolean masking & fancy indexing
import numpy as np

scores = np.array([72, 85, 91, 68, 79, 95, 88, 60, 73, 99])

print("scores > 80 :", scores[scores > 80])
print("min, max, mean:", scores.min(), scores.max(), scores.mean())
print("argmax (best score idx):", scores.argmax())

# Top-3 scores
top3 = scores[np.argsort(scores)[::-1][:3]]
print("Top 3:", top3)


# %% [markdown] color=mint title="Exercise 7.** Given a 2D NumPy array of shape…"
# # Exercise 7.** Given a 2D NumPy array of shape…
#
# **Exercise 7.** Given a 2D NumPy array of shape `(1000, 10)` (1000 samples, 10 features) drawn from a standard normal:
#
# 1. Add a bias of `[1, 2, 3, 4, 5, 6, 7, 8, 9, 10]` to every sample.
# 2. Compute the per-feature mean and standard deviation.
# 3. Find the row indices of the 5 samples with the largest sum across features.
#
# All without any explicit Python `for` loop.


# %% color=peach title="Your code here"
# @explain: Your code here
# @explain: 1
# @explain: 2
# @explain: 3
# @explain: print(feat_mean.round(2))
import numpy as np
np.random.seed(42)

X = np.random.randn(1000, 10)
bias = np.arange(1, 11)

# Your code here
# 1. Add bias
X_biased = ...   # TODO
# 2. Mean and std per feature
feat_mean = ...
feat_std  = ...
# 3. Top 5 rows by row-sum
top5_idx = ...

# print(feat_mean.round(2))
# print(top5_idx)


# %% [markdown] color=violet title="Module 8 — Pandas"
# # Module 8 — Pandas
#


# %% color=amber title="Build a DataFrame"
# @explain: Build a DataFrame
import pandas as pd
import numpy as np

# Build a DataFrame
np.random.seed(42)
df = pd.DataFrame({
    "user_id":  range(1, 11),
    "country":  np.random.choice(["US", "UK", "IN", "SA"], 10),
    "age":      np.random.randint(18, 65, 10),
    "spend":    np.random.uniform(10, 200, 10).round(2),
    "premium":  np.random.choice([True, False], 10),
})
print(df)
print()
print(df.describe())


# %% color=rose title="Filtering & selection"
# @explain: Filtering & selection
# Filtering & selection
print(df[df["spend"] > 100])
print()
print(df.loc[df["country"] == "US", ["user_id", "spend"]])


# %% color=lime title="GroupBy"
# @explain: GroupBy
# GroupBy
print("Mean spend by country:")
print(df.groupby("country")["spend"].mean().round(2))

print("\nMultiple aggregates:")
print(df.groupby("country").agg(
    avg_spend=("spend", "mean"),
    max_spend=("spend", "max"),
    n_users=("user_id", "count"),
).round(2))


# %% color=teal title="Joining"
# @explain: Joining
# Joining
users = pd.DataFrame({
    "user_id": [1, 2, 3, 4],
    "name":    ["alice", "bob", "carol", "dave"],
})
orders = pd.DataFrame({
    "user_id": [1, 1, 2, 4, 5],
    "amount":  [50, 75, 30, 100, 200],
})

print("Inner join:")
print(pd.merge(users, orders, on="user_id"))
print("\nLeft join (keep all users):")
print(pd.merge(users, orders, on="user_id", how="left"))


# %% [markdown] color=sky title="Exercise 8.** From the `df` above, find the country…"
# # Exercise 8.** From the `df` above, find the country…
#
# **Exercise 8.** From the `df` above, find the country with the highest mean spend among premium users only. Use chained operations (`df[mask].groupby(...).agg(...)`).


# %% color=mint title="Your code here"
# @explain: Your code here
# @explain: print(result)
# Your code here
result = ...   # TODO
# print(result)


# %% [markdown] color=peach title="Module 9 — Visualization"
# # Module 9 — Visualization
#


# %% color=violet title="import matplotlib.pyplot as plt"
# @explain: Run this cell to see the output.
import matplotlib.pyplot as plt
import numpy as np

x = np.linspace(0, 2*np.pi, 200)
fig, ax = plt.subplots(figsize=(8, 4))
ax.plot(x, np.sin(x), label="sin", linewidth=2)
ax.plot(x, np.cos(x), label="cos", linestyle="--")
ax.set_xlabel("x")
ax.set_ylabel("f(x)")
ax.set_title("Trig functions")
ax.legend()
ax.grid(alpha=0.3)
plt.tight_layout()
plt.show()


# %% color=amber title="Multi-panel"
# @explain: Multi-panel
# Multi-panel
import numpy as np
import matplotlib.pyplot as plt

data = np.random.randn(1000)

fig, axes = plt.subplots(1, 3, figsize=(12, 3.5))
axes[0].hist(data, bins=30, color="steelblue", edgecolor="white")
axes[0].set_title("Histogram")

axes[1].plot(np.cumsum(data))
axes[1].set_title("Cumulative sum")

axes[2].scatter(data[:-1], data[1:], s=5, alpha=0.4)
axes[2].set_title("Lag plot")

plt.tight_layout()
plt.show()


# %% color=rose title="Seaborn"
# @explain: Seaborn — built-in datasets and one-line statistical plots
# Seaborn — built-in datasets and one-line statistical plots
import seaborn as sns
import matplotlib.pyplot as plt

tips = sns.load_dataset("tips")
print(tips.head())

fig, axes = plt.subplots(1, 2, figsize=(12, 4))
sns.histplot(tips["total_bill"], kde=True, ax=axes[0])
axes[0].set_title("Total bill distribution")

sns.boxplot(data=tips, x="day", y="total_bill", hue="sex", ax=axes[1])
axes[1].set_title("Bill by day & sex")
plt.tight_layout()
plt.show()


# %% [markdown] color=lime title="Module 10 — scikit-learn"
# # Module 10 — scikit-learn
#
# The `fit` / `predict` / `transform` pattern. Memorize this rhythm — every Python ML library uses it.


# %% color=teal title="from sklearn.datasets import load_iris"
# @explain: Run this cell to see the output.
from sklearn.datasets import load_iris
from sklearn.model_selection import train_test_split
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import accuracy_score, classification_report

X, y = load_iris(return_X_y=True)
print(f"X shape: {X.shape}, y shape: {y.shape}")

X_train, X_test, y_train, y_test = train_test_split(
    X, y, test_size=0.2, random_state=42, stratify=y
)

model = LogisticRegression(max_iter=1000)
model.fit(X_train, y_train)

y_pred = model.predict(X_test)
print(f"\nTest accuracy: {accuracy_score(y_test, y_pred):.3f}")
print(classification_report(y_test, y_pred,
      target_names=["setosa", "versicolor", "virginica"]))


# %% color=sky title="Pipeline + cross-validation"
# @explain: Pipeline + cross-validation — leak-proof model evaluation
# Pipeline + cross-validation — leak-proof model evaluation
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import StandardScaler
from sklearn.linear_model import LogisticRegression
from sklearn.model_selection import cross_val_score
from sklearn.datasets import load_iris

X, y = load_iris(return_X_y=True)

pipe = Pipeline([
    ("scaler", StandardScaler()),
    ("clf",    LogisticRegression(max_iter=1000)),
])

scores = cross_val_score(pipe, X, y, cv=5, scoring="accuracy")
print(f"CV accuracy: {scores.mean():.3f} ± {scores.std():.3f}")
print(f"All folds: {scores.round(3)}")


# %% color=mint title="Hyperparameter search"
# @explain: Hyperparameter search
# Hyperparameter search
from sklearn.model_selection import GridSearchCV
from sklearn.ensemble import RandomForestClassifier
from sklearn.datasets import load_iris

X, y = load_iris(return_X_y=True)

param_grid = {
    "n_estimators": [50, 100, 200],
    "max_depth":    [None, 5, 10],
}

search = GridSearchCV(
    RandomForestClassifier(random_state=42),
    param_grid, cv=5, scoring="accuracy", n_jobs=-1,
)
search.fit(X, y)

print(f"Best params: {search.best_params_}")
print(f"Best CV acc: {search.best_score_:.3f}")


# %% [markdown] color=peach title="Exercise 10.** Load…"
# # Exercise 10.** Load…
#
# **Exercise 10.** Load `sklearn.datasets.load_breast_cancer`. Build a Pipeline with `StandardScaler` + `LogisticRegression`. Get a 5-fold cross-validation accuracy. Should be > 0.97 — if it's much lower, something's off.


# %% color=violet title="Your code here"
# @explain: Your code here
# @explain: 
# Your code here
from sklearn.datasets import load_breast_cancer
# ... TODO


# %% [markdown] color=amber title="Module 11 — PyTorch"
# # Module 11 — PyTorch
#


# %% color=rose title="Tensors"
# @explain: Tensors — like NumPy arrays
# @explain: Math like NumPy
import torch
print(f"PyTorch: {torch.__version__}")
print(f"CUDA available: {torch.cuda.is_available()}")

# Tensors — like NumPy arrays
a = torch.tensor([1.0, 2.0, 3.0])
b = torch.randn(2, 3)
print(a, a.dtype, a.device)
print(b.shape)

# Math like NumPy
print(a + 10)
print(b.mean(), b.std())


# %% color=lime title="Autograd"
# @explain: Autograd — the magic that trains neural networks
# @explain: Compute dy/dx for y = 3x^2 + 2x + 1 at x = 4
# Autograd — the magic that trains neural networks
import torch

# Compute dy/dx for y = 3x^2 + 2x + 1 at x = 4
x = torch.tensor(4.0, requires_grad=True)
y = 3 * x**2 + 2 * x + 1
y.backward()
print(f"dy/dx at x=4: {x.grad.item()}")
print(f"Expected (6x+2): {6*4 + 2}")


# %% color=teal title="Linear regression by gradient descent"
# @explain: Linear regression by gradient descent — no nn.Module yet
# @explain: Learnable parameters
# Linear regression by gradient descent — no nn.Module yet
import torch

torch.manual_seed(0)
N = 100
true_w, true_b = 2.0, -1.0
X = torch.randn(N, 1)
Y = true_w * X + true_b + 0.1 * torch.randn(N, 1)

# Learnable parameters
w = torch.zeros(1, requires_grad=True)
b = torch.zeros(1, requires_grad=True)
lr = 0.1

for step in range(200):
    pred = X * w + b
    loss = ((pred - Y) ** 2).mean()
    loss.backward()
    with torch.no_grad():
        w -= lr * w.grad
        b -= lr * b.grad
        w.grad.zero_()
        b.grad.zero_()
    if step % 50 == 0:
        print(f"step {step:>3} | loss {loss.item():.4f} | w {w.item():.3f}, b {b.item():.3f}")

print(f"\nLearned: w={w.item():.3f}, b={b.item():.3f}")
print(f"True:    w={true_w}, b={true_b}")


# %% color=sky title="Real model: nn.Module + DataLoader + training loop"
# @explain: Real model: nn.Module + DataLoader + training loop
# @explain: THE FIVE STEPS, every iteration:
# @explain: 1
# Real model: nn.Module + DataLoader + training loop
import torch
import torch.nn as nn
from torch.utils.data import DataLoader, TensorDataset

torch.manual_seed(0)
N, D = 1000, 10
X = torch.randn(N, D)
true_w = torch.randn(D, 1)
y = (X @ true_w + 0.1 * torch.randn(N, 1)).squeeze()

dataset = TensorDataset(X, y)
loader = DataLoader(dataset, batch_size=32, shuffle=True)

class MLP(nn.Module):
    def __init__(self, in_dim, hidden=64):
        super().__init__()
        self.net = nn.Sequential(
            nn.Linear(in_dim, hidden), nn.ReLU(),
            nn.Linear(hidden, hidden), nn.ReLU(),
            nn.Linear(hidden, 1),
        )
    def forward(self, x):
        return self.net(x).squeeze(-1)

model = MLP(in_dim=D)
opt = torch.optim.AdamW(model.parameters(), lr=1e-3)
loss_fn = nn.MSELoss()

# THE FIVE STEPS, every iteration:
#   1. forward   2. loss   3. zero_grad   4. backward   5. step
for epoch in range(5):
    total = 0.0
    for xb, yb in loader:
        pred = model(xb)
        loss = loss_fn(pred, yb)
        opt.zero_grad()
        loss.backward()
        opt.step()
        total += loss.item() * xb.size(0)
    print(f"epoch {epoch} | mean loss {total/N:.4f}")


# %% [markdown] color=mint title="Exercise 11.** Modify the MLP above to be a…"
# # Exercise 11.** Modify the MLP above to be a…
#
# **Exercise 11.** Modify the MLP above to be a *classifier* on synthetic 2-class data:
#
# 1. Generate `X = torch.randn(1000, 5)`, then `y = (X.sum(dim=1) > 0).long()`.
# 2. Change the model's last layer to `nn.Linear(hidden, 2)`.
# 3. Use `nn.CrossEntropyLoss` instead of `MSELoss`.
# 4. Train for 5 epochs and print the final accuracy on the training data.
#
# Expected: accuracy > 0.95 because the task is easy.


# %% color=peach title="Your code here"
# @explain: Your code here
# @explain: 
# Your code here
# ... TODO


# %% [markdown] color=violet title="Module 12 — The ML Engineer's Toolkit"
# # Module 12 — The ML Engineer's Toolkit
#
# ### 12.1 Hugging Face — load any pretrained model in 3 lines


# %% color=amber title="pip install transformers   # already installed in Colab"
# @explain: pip install transformers   # already installed in Colab
# @explain: A pretrained sentiment classifier
# pip install transformers   # already installed in Colab
from transformers import pipeline

# A pretrained sentiment classifier
sentiment = pipeline("sentiment-analysis",
                      model="distilbert-base-uncased-finetuned-sst-2-english")

print(sentiment("I love this product!"))
print(sentiment("This was a complete waste of money."))
print(sentiment("It's okay, nothing special."))


# %% color=rose title="More control: load tokenizer and model separately"
# @explain: More control: load tokenizer and model separately
# More control: load tokenizer and model separately
from transformers import AutoTokenizer, AutoModelForSequenceClassification
import torch

name = "distilbert-base-uncased-finetuned-sst-2-english"
tokenizer = AutoTokenizer.from_pretrained(name)
model     = AutoModelForSequenceClassification.from_pretrained(name)
model.eval()

texts = [
    "Honestly, the food was incredible.",
    "Worst service I have ever received.",
    "It exists. It is a thing.",
]
inputs = tokenizer(texts, return_tensors="pt", padding=True, truncation=True)
with torch.no_grad():
    logits = model(**inputs).logits
probs = logits.softmax(dim=-1)
labels = ["NEGATIVE", "POSITIVE"]
for text, p in zip(texts, probs):
    print(f"{labels[p.argmax()]:>9} ({p.max():.1%}) — {text}")


# %% [markdown] color=lime title="12.2 Logging & timing"
# # 12.2 Logging & timing
#


# %% color=teal title="import logging"
# @explain: Run this cell to see the output.
import logging
import time

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
)
log = logging.getLogger(__name__)

log.info("Starting fake training")
for epoch in range(3):
    time.sleep(0.1)
    fake_loss = 1.0 / (epoch + 1)
    log.info(f"Epoch {epoch}: loss={fake_loss:.4f}")
log.info("Done")


# %% [markdown] color=sky title="Where to go next"
# # Where to go next
#
# ---
#
# ## Where to go next
#
# You now have working knowledge of every tool a Python ML engineer uses day-to-day. The way to consolidate it:
#
# **Pick a small project that matters to you** and build it end-to-end. A few suggestions tailored to ML/AI work:
#
# …


# %% [markdown] color=lime title="Thanks"
# # End of Module
#
# Next module continues the roadmap.
# Source: https://github.com/kader-xai/data-science-roadmap


