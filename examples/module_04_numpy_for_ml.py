# %% [markdown]
# # Module 4 — NumPy for Machine Learning
# Every ML library is a thin layer over NumPy arrays. This module covers
# the array operations you'll use every day: creation, dtypes, indexing,
# slicing, broadcasting, vectorisation, reductions, and reshaping.

# %% kind=install color=rose title="Install NumPy"
# @explain: Run once. If numpy is already installed in the kernel's venv
# @explain: this is a no-op.
import importlib, subprocess, sys
if importlib.util.find_spec("numpy") is None:
    subprocess.check_call([sys.executable, "-m", "pip", "install", "--quiet", "numpy"])
print("numpy ready.")


# %% kind=import color=sky title="Imports"
# @explain: `np` is the universal alias for numpy. The seed makes any
# @explain: random examples in this notebook reproducible.
import numpy as np
np.random.seed(0)


# %% kind=intro color=sky title="Why NumPy?"
# @explain: Python lists are flexible but slow. NumPy stores numbers in
# @explain: a packed C array and runs operations in compiled loops —
# @explain: 10-100x faster, with vectorised syntax instead of for-loops.
# @tags: intro


# %% kind=assign color=peach title="Creating arrays"
# @explain: From a list, from a range, from a shape filled with zeros
# @explain: or ones, and as a random sample. dtype controls precision.
a = np.array([1, 2, 3, 4])
b = np.arange(0, 10, 2)
zeros = np.zeros((2, 3))
ones = np.ones((3,), dtype=np.float32)
rand = np.random.rand(2, 3)

print("a    :", a, a.dtype)
print("b    :", b)
print("zeros:\n", zeros)
print("ones :", ones, ones.dtype)
print("rand :\n", rand)


# %% kind=assign color=peach title="Shape, ndim, size, dtype"
# @explain: Every array has these four attributes. Knowing them prevents
# @explain: the matmul/broadcasting errors that bite every ML beginner.
x = np.array([[1, 2, 3], [4, 5, 6]])
print("shape:", x.shape)
print("ndim :", x.ndim)
print("size :", x.size)
print("dtype:", x.dtype)


# %% kind=expr color=peach title="Indexing and slicing"
# @explain: Same syntax as lists, but on N dimensions: arr[row, col].
# @explain: `:` means "all", negative indices count from the end.
m = np.arange(12).reshape(3, 4)
print("m =\n", m)
print("m[0]      =", m[0])         # first row
print("m[:, 0]   =", m[:, 0])      # first column
print("m[1:, 2:] =\n", m[1:, 2:])  # bottom-right block
print("m[-1, -1] =", m[-1, -1])    # last element


# %% kind=expr color=peach title="Boolean (mask) indexing"
# @explain: A boolean array of the same shape selects only the True
# @explain: entries. The cornerstone of "where the label is positive..."
# @explain: filtering in tabular ML.
scores = np.array([0.1, 0.9, 0.4, 0.8, 0.2])
high = scores > 0.5
print("mask :", high)
print("kept :", scores[high])
scores[scores < 0.3] = 0.0  # bulk update
print("after:", scores)


# %% kind=expr color=peach title="Fancy indexing"
# @explain: An array of indices picks elements in arbitrary order — used
# @explain: for shuffling, mini-batch sampling, and re-ordering features.
arr = np.array([10, 20, 30, 40, 50])
idx = np.array([4, 0, 2])
print(arr[idx])


# %% [markdown]
# ## Vectorisation — replace Python loops with NumPy ops
# A vectorised expression runs in compiled C; a Python for-loop runs in
# the interpreter. Same answer, often **50–100×** speed difference.


# %% kind=loop color=yellow title="Loop vs vectorised"
# @explain: Both compute element-wise squares. The vectorised line is
# @explain: shorter, faster, and more readable.
xs = np.arange(1_000_000)

py = [v * v for v in xs.tolist()[:5]]  # demo on 5 elements
vec = (xs * xs)[:5]

print("python loop sample :", py)
print("vectorised sample  :", vec)


# %% kind=expr color=peach title="Element-wise math + ufuncs"
# @explain: +, -, *, /, ** all work element-wise. np.exp, np.log, np.sqrt
# @explain: are "universal functions" (ufuncs) that broadcast over shape.
v = np.array([1.0, 2.0, 4.0])
print("v + 1   =", v + 1)
print("v * 3   =", v * 3)
print("v ** 2  =", v ** 2)
print("exp(v)  =", np.exp(v))
print("log(v)  =", np.log(v))
print("sqrt(v) =", np.sqrt(v))


# %% [markdown]
# ## Broadcasting
# When two arrays have different but compatible shapes, NumPy stretches
# the smaller along the missing axis. This is how `(N, D)` − `(D,)`
# centres every row in one line — no loop required.


# %% kind=assign color=peach title="Broadcasting rules — a vector minus its mean"
# @explain: `X - X.mean(axis=0)` subtracts the column means from every
# @explain: row. Shapes: (5,3) − (3,) → broadcasts to (5,3).
X = np.array([
    [1.0, 10.0, 100.0],
    [2.0, 20.0, 200.0],
    [3.0, 30.0, 300.0],
    [4.0, 40.0, 400.0],
    [5.0, 50.0, 500.0],
])
mu = X.mean(axis=0)
centred = X - mu
print("means     :", mu)
print("centred   :\n", centred)
print("col means after:", centred.mean(axis=0))


# %% kind=expr color=peach title="axis=0 vs axis=1"
# @explain: axis=0 collapses ROWS (one number per column).
# @explain: axis=1 collapses COLS (one number per row).
print("sum axis=0 :", X.sum(axis=0))
print("sum axis=1 :", X.sum(axis=1))
print("max axis=0 :", X.max(axis=0))


# %% [markdown]
# ## Statistics in one line


# %% kind=expr color=peach title="Common reductions"
# @explain: All ML preprocessing relies on these — means, stds, variance,
# @explain: percentiles. Pass axis to compute per row or per column.
data = np.random.normal(loc=5, scale=2, size=(4, 6))
print("mean   :", data.mean())
print("std    :", data.std())
print("min/max:", data.min(), data.max())
print("median :", np.median(data))
print("percentiles 25/50/75:", np.percentile(data, [25, 50, 75]))


# %% [markdown]
# ## Reshape, transpose, stack


# %% kind=expr color=peach title="Reshape and transpose"
# @explain: Reshape rearranges the same data into a different shape
# @explain: (total size must match). `.T` is shorthand for transpose.
a = np.arange(12)
print("flat        :", a)
print("(3, 4)      :\n", a.reshape(3, 4))
print("(2, 2, 3)   :\n", a.reshape(2, 2, 3))
print("transpose   :\n", a.reshape(3, 4).T)


# %% kind=expr color=peach title="Stacking arrays"
# @explain: vstack stacks rows, hstack stacks columns. concatenate is
# @explain: the general form — pick the axis you want to glue along.
A = np.array([[1, 2], [3, 4]])
B = np.array([[5, 6], [7, 8]])
print("vstack:\n", np.vstack([A, B]))
print("hstack:\n", np.hstack([A, B]))
print("concat axis=0:\n", np.concatenate([A, B], axis=0))


# %% [markdown]
# ## Linear algebra previews — what models do under the hood


# %% kind=function color=mint title="Dot product (manual prediction)"
# @explain: A linear model's prediction is just `weights · features + b`.
# @explain: This is the building block of every regression, every layer.
weights = np.array([0.4, -0.6, 0.2])
features = np.array([2.0, 1.0, 3.0])
bias = 0.1
pred = weights @ features + bias  # same as np.dot
print("prediction:", pred)


# %% kind=function color=mint title="Batch prediction with matmul"
# @explain: For a whole batch we use matrix-matrix multiply:
# @explain: X @ W where X is (batch, features), W is (features, outputs).
X = np.random.randn(4, 3)        # 4 samples, 3 features
W = np.random.randn(3, 2)        # 3 features, 2 outputs
b = np.array([0.5, -0.5])
Y = X @ W + b
print("X shape:", X.shape, "  W shape:", W.shape, "  Y shape:", Y.shape)
print("predictions:\n", Y)


# %% [markdown]
# ## Practice
# 1. Make a (1000, 5) standard-normal array. Confirm each column's mean
#    is close to 0 and std close to 1.
# 2. Z-score normalise a (100, 4) array so each column has mean 0 std 1.
# 3. Given `y = np.array([1, 0, 1, 1, 0])`, compute the fraction of 1s.


# %% kind=function color=mint title="Practice 1 — column statistics"
# @explain: With a large enough sample, the empirical mean ≈ 0 and
# @explain: std ≈ 1 because that's the true distribution.
A = np.random.randn(1000, 5)
print("means:", A.mean(axis=0).round(3))
print("stds :", A.std(axis=0).round(3))


# %% kind=function color=mint title="Practice 2 — z-score normalisation"
# @explain: The standard scaling formula: (x - mean) / std. Broadcasting
# @explain: makes it one line, no loop.
A = np.random.randn(100, 4) * 5 + 10
A_norm = (A - A.mean(axis=0)) / A.std(axis=0)
print("after means:", A_norm.mean(axis=0).round(3))
print("after stds :", A_norm.std(axis=0).round(3))


# %% kind=function color=mint title="Practice 3 — fraction of positive labels"
# @explain: bool array → mean is the fraction True. Common pattern when
# @explain: checking class balance in a dataset.
y = np.array([1, 0, 1, 1, 0])
print("positive fraction:", y.mean())


# %% [markdown]
# ## Recap
# - ✅ Build, shape, index, slice arrays
# - ✅ Boolean masks and fancy indexing
# - ✅ Vectorised ops + broadcasting
# - ✅ Reductions per axis
# - ✅ Reshape / transpose / stack
# - ✅ Dot product and batched matmul — the heart of ML inference
#
# **Next:** Module 5 — Pandas for tabular data.
