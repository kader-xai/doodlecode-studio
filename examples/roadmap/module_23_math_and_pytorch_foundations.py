# doodlecode format-version: 2
# Auto-converted from module_23_math_and_pytorch_foundations.ipynb
# Open with 📂 Open → press 🎬 Present.


# %% [markdown] color=rose title="Module 23 Math And Pytorch Foundations"
# # Module 23 Math And Pytorch Foundations
#
# A live walkthrough — one card per concept.
# Use → / ← to step through. Press 🎬 Present to begin.



# %% [markdown] color=sky title="Module 23 — Math & PyTorch Foundations for AI Research"
# # Module 23 — Math & PyTorch Foundations for AI Research
#
# *The math under every neural network, plus the PyTorch tensor mechanics you'll use every day.*
#
# Most ML courses (including ours, M11–M22) skim the math because the libraries hide it. That works — until you hit a paper, a debug session, or a custom layer. Then the math has to live in your head.
#
# This module is the deepest of the "tools" modules. It assumes you've finished Module 17 (Python for ML) and gives you the **math foundations** plus a **deeper PyTorch primer** before you tackle attention (M19), diffusion (M21), or DeepSeek (M24).
#
# ### What you'll cover
# …


# %% color=mint title="!pip -q install numpy matplotlib torch"
# @explain: Run this cell to see the output.
!pip -q install numpy matplotlib torch
import numpy as np, matplotlib.pyplot as plt, torch
np.random.seed(0); torch.manual_seed(0)
print(f"numpy {np.__version__}, torch {torch.__version__}")


# %% [markdown] color=peach title="1 · Functions — `y = f(x)`"
# # 1 · Functions — `y = f(x)`
#
# A function maps an input `x` to an output `y`. Three families to know cold:


# %% color=violet title="x = np.linspace(-5"
# @explain: Run this cell to see the output.
x = np.linspace(-5, 5, 200)
fig, axes = plt.subplots(1, 4, figsize=(15, 3))

axes[0].plot(x, 2*x + 1);            axes[0].set_title("Linear  y = 2x + 1")
axes[1].plot(x, x**2);                axes[1].set_title("Quadratic  y = x²")
axes[2].plot(x, np.exp(x));           axes[2].set_title("Exponential  y = eˣ")
axes[3].plot(x[x>0], np.log(x[x>0])); axes[3].set_title("Log  y = ln(x)")

for ax in axes: ax.grid(alpha=.3); ax.axhline(0, color="grey", lw=.5)
plt.tight_layout(); plt.show()


# %% [markdown] color=amber title="Why these matter in ML"
# # Why these matter in ML
#
# **Why these matter in ML:**
#
# | Function | Where it shows up |
# |---|---|
# | Linear | every weight matrix `Wx + b` |
# | Quadratic | mean-squared-error loss is `(y - ŷ)²` |
# | Exponential | softmax, the function turning logits into probabilities |
# | Log | log-likelihood loss, log-softmax (numerical stability) |


# %% [markdown] color=rose title="2 · Derivatives — the slope at a point"
# # 2 · Derivatives — the slope at a point
#
# The derivative `f'(x)` tells you **how y changes when x nudges**. The whole of training a neural network is: *compute the derivative of the loss with respect to every weight, then take a small step in the opposite direction*.
#
# ### Three derivatives to memorise
# | f(x)   | f'(x)         |
# |--------|---------------|
# | x²     | 2x            |
# …


# %% color=lime title="Numerical check: derivative of x² at x=3 should be…"
# @explain: Numerical check: derivative of x² at x=3 should be 2x = 6
# @explain: PyTorch can compute it automatically — autograd
# Numerical check: derivative of x² at x=3 should be 2x = 6
x0 = 3.0
h = 1e-5
slope = ((x0+h)**2 - x0**2) / h
print(f"numerical slope at x=3: {slope:.4f}")     # ≈ 6.0

# PyTorch can compute it automatically — autograd
x = torch.tensor(3.0, requires_grad=True)
y = x**2
y.backward()
print(f"autograd slope at x=3:  {x.grad.item():.4f}")


# %% [markdown] color=teal title="Visualise the slope** at three points on `y = x²`"
# # Visualise the slope** at three points on `y = x²`
#
# **Visualise the slope** at three points on `y = x²`:


# %% color=sky title="x = np.linspace(-3"
# @explain: Run this cell to see the output.
x = np.linspace(-3, 3, 200)
fig, ax = plt.subplots(figsize=(7, 4))
ax.plot(x, x**2, label="y = x²")

for x0, color in zip([-2, 0, 2], ["red", "green", "blue"]):
    slope = 2 * x0                              # derivative of x²
    tangent = slope * (x - x0) + x0**2          # line through (x0, x0²) with that slope
    ax.plot(x, tangent, "--", color=color, alpha=.7,
            label=f"slope at x={x0}: {slope}")

ax.set_ylim(-2, 10); ax.legend(); ax.grid(alpha=.3); plt.show()


# %% [markdown] color=mint title="3 · Vectors — magnitude, dot product, cosine similarity"
# # 3 · Vectors — magnitude, dot product, cosine similarity
#
# A vector is just a list of numbers, but the geometric interpretation is what makes ML work.
#
# - **magnitude (length)** of `v` is `√Σ vᵢ²`
# - **dot product** `a·b = Σ aᵢ·bᵢ` measures how aligned two vectors are
# - **cosine similarity** = `(a·b) / (|a||b|)` — the angle between them, in [-1, 1]
#
# …


# %% color=peach title="a = np.array([1.0"
# @explain: Run this cell to see the output.
a = np.array([1.0, 2.0, 3.0])
b = np.array([2.0, 4.0, 6.0])    # 2× of a — same direction
c = np.array([3.0, -2.0, 1.0])   # different direction

def cos_sim(u, v):
    return np.dot(u, v) / (np.linalg.norm(u) * np.linalg.norm(v))

print(f"cos(a, b) = {cos_sim(a, b):.4f}   ← 1.0, perfectly aligned")
print(f"cos(a, c) = {cos_sim(a, c):.4f}   ← near zero, roughly orthogonal")
print(f"cos(a,-a) = {cos_sim(a, -a):.4f}   ← -1.0, opposite directions")


# %% [markdown] color=violet title="4 · Gradients — derivatives in N dimensions"
# # 4 · Gradients — derivatives in N dimensions
#
# A gradient is the vector of partial derivatives. For `f(x, y) = x² + y²`:
# $$\nabla f = \big[\frac{\partial f}{\partial x},\ \frac{\partial f}{\partial y}\big] = [2x,\ 2y]$$
#
# The gradient **points uphill** — in the direction of steepest *ascent*. Gradient *descent* is just stepping the OPPOSITE way.


# %% color=amber title="gradient = [2x, 2y]"
# @explain: gradient = [2x, 2y] — these are the two slope components
xs = np.linspace(-3, 3, 25)
ys = np.linspace(-3, 3, 25)
X, Y = np.meshgrid(xs, ys)
Z = X**2 + Y**2

# gradient = [2x, 2y] — these are the two slope components
U, V = 2*X, 2*Y

fig, ax = plt.subplots(figsize=(6, 6))
ax.contourf(X, Y, Z, levels=20, cmap="viridis", alpha=.6)
ax.quiver(X, Y, U, V, scale=80, color="white", alpha=.8)
ax.set_title("Gradient field of f(x,y) = x² + y² — arrows point uphill")
ax.set_aspect("equal"); plt.show()


# %% [markdown] color=rose title="5 · Matrices — the operation every layer is doing"
# # 5 · Matrices — the operation every layer is doing
#
# A neural-network layer is mostly **`output = input @ W + b`** where `@` is matrix multiplication. Three rules to internalise:
#
# 1. `(m × k) @ (k × n) → (m × n)` — the inner dimensions must match and they cancel.
# 2. Matrix multiplication is **NOT commutative**: `A @ B ≠ B @ A` in general.
# 3. Transpose `Aᵀ` swaps rows and columns: `(m × n)ᵀ → (n × m)`.


# %% color=lime title="Identity: A @ I = A"
# @explain: Identity: A @ I = A
A = np.array([[1, 2], [3, 4]])           # 2x2
B = np.array([[5, 6, 7], [8, 9, 10]])    # 2x3

C = A @ B                                # (2x2) @ (2x3) → (2x3)
print("A:\n", A)
print("B:\n", B)
print("A @ B:\n", C)
print("Aᵀ:\n", A.T)

# Identity: A @ I = A
I = np.eye(2)
assert np.allclose(A @ I, A)
print("\nA @ I = A ✓")


# %% [markdown] color=teal title="A linear layer in 3 lines"
# # A linear layer in 3 lines
#


# %% color=sky title="1 'layer' that maps a 4-dim input to a 2-dim output"
# @explain: 1 'layer' that maps a 4-dim input to a 2-dim output
# 1 'layer' that maps a 4-dim input to a 2-dim output
batch = 8
x = np.random.randn(batch, 4)        # 8 input rows of dim 4
W = np.random.randn(4, 2)            # weight matrix
b = np.random.randn(2)               # bias

y = x @ W + b
print("input shape :", x.shape)
print("output shape:", y.shape)      # (8, 2) — that's a layer


# %% [markdown] color=mint title="6 · Probability — distributions, expected value, KL divergence"
# # 6 · Probability — distributions, expected value, KL divergence
#
# Three concepts behind every loss function:
#
# - **Probability distribution** — a non-negative function summing to 1 over its outcomes.
# - **Expected value** `E[X] = Σ xᵢ·p(xᵢ)` — the long-run average.
# - **KL divergence** — how different two distributions are; the foundation of **cross-entropy loss**.


# %% color=peach title="Coin toss: p(heads)=0.5"
# @explain: Coin toss: p(heads)=0.5, p(tails)=0.5  → fair
# @explain: Loaded coin:  p(heads)=0.8, p(tails)=0.2
# @explain: expected number of heads in 10 flips, fair coin
# @explain: KL divergence: D_KL(p || q) = Σ p_i · log(p_i / q_i)
# Coin toss: p(heads)=0.5, p(tails)=0.5  → fair
# Loaded coin:  p(heads)=0.8, p(tails)=0.2

p = np.array([0.5, 0.5])
q = np.array([0.8, 0.2])

# expected number of heads in 10 flips, fair coin
print("E[heads in 10 flips, fair]:", 10 * p[0])

# KL divergence: D_KL(p || q) = Σ p_i · log(p_i / q_i)
def kl(p, q):
    return np.sum(p * np.log(p / q))

print(f"KL(p || q) = {kl(p, q):.4f}   ← > 0, distributions differ")
print(f"KL(p || p) = {kl(p, p):.4f}   ← exactly 0, identical")


# %% [markdown] color=violet title="The softmax → cross-entropy pipeline (every classifier)"
# # The softmax → cross-entropy pipeline (every classifier)
#


# %% color=amber title="Toy classifier output for a 3-class problem"
# @explain: Toy classifier output for a 3-class problem
# @explain: softmax: turn logits into a probability distribution
# @explain: true class is index 0 → target distribution is [1, 0, 0]
# @explain: cross-entropy = -Σ target * log(probs)  (equivalent to KL up to a constant)
# Toy classifier output for a 3-class problem
logits = np.array([2.0, 1.0, 0.1])

# softmax: turn logits into a probability distribution
def softmax(x):
    e = np.exp(x - x.max())              # subtract max for numerical stability
    return e / e.sum()

probs = softmax(logits)
print("probs:", probs.round(3), " sum:", probs.sum().round(3))

# true class is index 0 → target distribution is [1, 0, 0]
target = np.array([1, 0, 0])

# cross-entropy = -Σ target * log(probs)  (equivalent to KL up to a constant)
ce = -np.sum(target * np.log(probs))
print(f"cross-entropy loss: {ce:.4f}")


# %% [markdown] color=rose title="7 · PyTorch — Creating Tensors (six ways)"
# # 7 · PyTorch — Creating Tensors (six ways)
#
# ---
#
# ## 7 · PyTorch — Creating Tensors (six ways)
#
# A `torch.Tensor` is NumPy's `ndarray` with two superpowers:
# 1. It runs on GPU.
# 2. It tracks gradients (autograd).


# %% color=lime title="1) From a Python list"
# @explain: 1) From a Python list
# @explain: 2) From numpy
# @explain: 3) Filled with zeros / ones
# @explain: 4) Random (uniform 0..1, normal 0/1)
# @explain: 5) Range / linspace
# 1) From a Python list
a = torch.tensor([[1, 2, 3], [4, 5, 6]])
print(a, a.dtype, a.shape)

# 2) From numpy
b = torch.from_numpy(np.array([1.0, 2.0, 3.0]))
print(b, b.dtype)

# 3) Filled with zeros / ones
print(torch.zeros(2, 3))
print(torch.ones(2, 3))

# 4) Random (uniform 0..1, normal 0/1)
print(torch.rand(2, 3))
print(torch.randn(2, 3))

# 5) Range / linspace
print(torch.arange(0, 10, 2))
print(torch.linspace(0, 1, 5))

# 6) Same shape as another tensor
ref = torch.tensor([[1.0, 2.0], [3.0, 4.0]])
print(torch.zeros_like(ref))
print(torch.randn_like(ref))


# %% [markdown] color=teal title="`dtype` and `device`"
# # `dtype` and `device`
#


# %% color=sky title="Move to GPU when available"
# @explain: Move to GPU when available
x = torch.tensor([1, 2, 3], dtype=torch.float32)
print(x.dtype, x.device)

# Move to GPU when available
device = "cuda" if torch.cuda.is_available() else "cpu"
print("using:", device)
x_gpu = x.to(device)
print("device:", x_gpu.device)


# %% [markdown] color=mint title="8 · Matrix Multiplication in PyTorch"
# # 8 · Matrix Multiplication in PyTorch
#
# Four ways, each for a different shape regime:
#
# | Operator | Shapes | Use |
# |---|---|---|
# | `A @ B` | (m,k) @ (k,n) | the universal one |
# | `A.matmul(B)` | same | method form |
# …


# %% color=peach title="Batched: 8 separate"
# @explain: Batched: 8 separate (3,4) @ (4,5) matmuls in parallel
A = torch.randn(3, 4)
B = torch.randn(4, 5)

print("A @ B            :", (A @ B).shape)
print("A.matmul(B)      :", A.matmul(B).shape)
print("einsum 'ij,jk':", torch.einsum("ij,jk->ik", A, B).shape)

# Batched: 8 separate (3,4) @ (4,5) matmuls in parallel
A_b = torch.randn(8, 3, 4)
B_b = torch.randn(8, 4, 5)
print("\nbmm shape         :", torch.bmm(A_b, B_b).shape)   # (8, 3, 5)


# %% [markdown] color=violet title="9 · Transposing — `.T` vs `.transpose` vs `.permute`"
# # 9 · Transposing — `.T` vs `.transpose` vs `.permute`
#
# | Op | When |
# |---|---|
# | `t.T` | quick swap of last two dims for ≤2D tensors |
# | `t.transpose(dim_a, dim_b)` | swap any two specific dims |
# | `t.permute(2, 0, 1)` | re-order **all** dims at once (most flexible) |


# %% color=amber title=".T on 2D is shorthand for .transpose(0"
# @explain: .T on 2D is shorthand for .transpose(0, 1)
t = torch.arange(24).reshape(2, 3, 4)
print("original  :", t.shape)         # (2, 3, 4)
print(".transpose(1, 2):", t.transpose(1, 2).shape)   # (2, 4, 3)
print(".permute(2, 0, 1):", t.permute(2, 0, 1).shape) # (4, 2, 3)

# .T on 2D is shorthand for .transpose(0, 1)
m = torch.randn(3, 5)
print("m.T:", m.T.shape)              # (5, 3)


# %% [markdown] color=rose title="10 · Reshape · view · squeeze · unsqueeze"
# # 10 · Reshape · view · squeeze · unsqueeze
#
# Four ops that change *shape* without changing *contents*:
#
# - **`reshape(...)`** — most common; works regardless of memory layout
# - **`view(...)`** — like reshape but requires CONTIGUOUS memory; faster
# - **`squeeze()`** — drop dimensions of size 1
# - **`unsqueeze(dim)`** — INSERT a dimension of size 1 (used constantly to add a batch dim)


# %% color=lime title="reshape to a 3x4 grid"
# @explain: reshape to a 3x4 grid
# @explain: 4D tensor with two trivial dims
# @explain: Add a batch dimension at position 0
t = torch.arange(12)
print("flat:", t.shape)                # (12,)

# reshape to a 3x4 grid
grid = t.reshape(3, 4)
print("grid:", grid.shape)              # (3, 4)

# 4D tensor with two trivial dims
x = torch.zeros(1, 5, 1, 7)
print("\noriginal :", x.shape)           # (1, 5, 1, 7)
print("squeeze  :", x.squeeze().shape)   # (5, 7) — both 1s gone
print("squeeze(0):", x.squeeze(0).shape)# (5, 1, 7) — only the FIRST 1 dropped

# Add a batch dimension at position 0
v = torch.tensor([1.0, 2.0, 3.0])
print("\nv          :", v.shape)        # (3,)
print("v.unsqueeze(0):", v.unsqueeze(0).shape)   # (1, 3) — now batched


# %% [markdown] color=teal title="11 · Indexing & Slicing"
# # 11 · Indexing & Slicing
#
# Same syntax as NumPy, plus boolean masks and fancy indexing.


# %% color=sky title="Standard slicing"
# @explain: Standard slicing
# @explain: Boolean mask
# @explain: Fancy indexing — pick specific rows/cols by index list
t = torch.arange(20).reshape(4, 5)
print(t)

# Standard slicing
print("\nrow 0:        ", t[0])
print("col 2:        ", t[:, 2])
print("bottom-right :", t[2:, 3:])

# Boolean mask
mask = t > 10
print("\n>10 values:", t[mask])

# Fancy indexing — pick specific rows/cols by index list
print("\nrows 0 and 3:")
print(t[[0, 3]])

print("\ndiagonal-ish (rows 0..3, cols 0..3):")
print(t[range(4), range(4)])


# %% [markdown] color=mint title="12 · Concatenation — `torch.cat` vs `torch.stack`"
# # 12 · Concatenation — `torch.cat` vs `torch.stack`
#
# The difference matters and beginners trip on it constantly:
#
# - **`cat`** glues tensors along an *existing* axis. Shapes must match on every other axis.
# - **`stack`** inserts a *new* axis and stacks tensors along it.


# %% color=peach title="cat: along an existing axis"
# @explain: cat: along an existing axis (dim=0)
# @explain: stack: new axis appears
# @explain: Mnemonic: cat = "more of the same" · stack = "now they're a batch"
a = torch.tensor([1, 2, 3])
b = torch.tensor([4, 5, 6])

# cat: along an existing axis (dim=0)
c = torch.cat([a, b], dim=0)
print("cat shape :", c.shape, " values:", c)            # (6,)

# stack: new axis appears
s = torch.stack([a, b], dim=0)
print("stack shape:", s.shape, "\nvalues:\n", s)        # (2, 3)

# Mnemonic: cat = "more of the same" · stack = "now they're a batch"


# %% [markdown] color=violet title="Daily-life use case — building a batch from samples"
# # Daily-life use case — building a batch from samples
#


# %% color=amber title="5 separate sample tensors"
# @explain: 5 separate sample tensors
# 5 separate sample tensors
samples = [torch.randn(3, 28, 28) for _ in range(5)]    # each is (C, H, W)

batch = torch.stack(samples, dim=0)
print("batch shape:", batch.shape)     # (5, 3, 28, 28) — exactly what a CNN expects


# %% [markdown] color=rose title="Recap"
# # Recap
#
# ---
#
# ## Recap
#
# ✅ Read a function and recognise it in an ML loss / activation
# ✅ Compute a derivative by hand AND with `loss.backward()`
# ✅ Use vectors for cosine similarity and embedding-search intuition
# ✅ Visualise a gradient field; understand "downhill = -gradient"
# …


# %% [markdown] color=lime title="Thanks"
# # End of Module
#
# Next module continues the roadmap.
# Source: https://github.com/kader-xai/data-science-roadmap


