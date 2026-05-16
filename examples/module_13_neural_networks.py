# %% [markdown]
# # Module 13 — Neural Networks Intro
# Build a neural network from scratch with NumPy (so you actually
# understand what fit/predict does), then do the same in scikit-learn
# and finally PyTorch.

# %% kind=install color=rose title="Install PyTorch (optional)"
# @explain: NumPy + sklearn are required for the first two parts. PyTorch
# @explain: is optional and pulls ~700 MB on first install.
import importlib, subprocess, sys
for pkg in ["scikit-learn", "matplotlib"]:
    if importlib.util.find_spec(pkg.replace("-", "_") if pkg == "scikit-learn" else pkg) is None:
        subprocess.check_call([sys.executable, "-m", "pip", "install", "--quiet", pkg])
HAS_TORCH = importlib.util.find_spec("torch") is not None
print("scikit-learn ready. torch installed?", HAS_TORCH)


# %% kind=import color=sky title="Imports"
import numpy as np
import matplotlib.pyplot as plt
from sklearn.datasets import make_moons
from sklearn.model_selection import train_test_split
from sklearn.metrics import accuracy_score
np.random.seed(0)


# %% kind=intro color=sky title="The 3-line summary of a neural net"
# @explain: 1. Forward: stack of (linear → nonlinear) layers turns x → y.
# @explain: 2. Loss   : a single number measuring how wrong y is.
# @explain: 3. Backward: gradients tell each weight which way to move
# @explain:              to make the loss smaller. Step. Repeat.
# @tags: intro


# %% [markdown]
# # Part 1 — A 2-layer net by hand (NumPy)


# %% kind=assign color=peach title="Dataset — two interleaved moons"
# @explain: Two classes that aren't linearly separable. Logistic regression
# @explain: would fail here; a small NN with one hidden layer can solve it.
X, y = make_moons(n_samples=400, noise=0.2, random_state=0)
y = y.reshape(-1, 1).astype(np.float32)
X = X.astype(np.float32)
X_tr, X_te, y_tr, y_te = train_test_split(X, y, test_size=0.25, random_state=0)
print("train:", X_tr.shape, "  test:", X_te.shape)

plt.figure(figsize=(4, 3))
plt.scatter(X[:, 0], X[:, 1], c=y.ravel(), cmap="coolwarm", edgecolor="k", alpha=0.7)
plt.title("Two-moons dataset")
plt.show()


# %% kind=function color=mint title="Activations and their gradients"
# @explain: Sigmoid squashes any number into (0, 1). Its derivative,
# @explain: σ(x)(1-σ(x)), is what backprop multiplies by.
def sigmoid(z):
    return 1.0 / (1.0 + np.exp(-z))

def sigmoid_grad(a):           # given a = sigmoid(z)
    return a * (1 - a)

def relu(z):
    return np.maximum(0, z)

def relu_grad(z):
    return (z > 0).astype(z.dtype)


# %% kind=function color=mint title="Initialise weights"
# @explain: Small random weights, zero biases. Bigger nets need fancier
# @explain: schemes (He / Xavier) — for one hidden layer this is fine.
def init(in_dim, hidden, out_dim, scale=0.5):
    rng = np.random.default_rng(0)
    return {
        "W1": rng.standard_normal((in_dim, hidden)) * scale,
        "b1": np.zeros((1, hidden)),
        "W2": rng.standard_normal((hidden, out_dim)) * scale,
        "b2": np.zeros((1, out_dim)),
    }


# %% kind=function color=mint title="Forward pass"
# @explain: z1 = X·W1 + b1; a1 = relu(z1);
# @explain: z2 = a1·W2 + b2; a2 = sigmoid(z2) = P(class=1).
def forward(X, p):
    z1 = X @ p["W1"] + p["b1"]
    a1 = relu(z1)
    z2 = a1 @ p["W2"] + p["b2"]
    a2 = sigmoid(z2)
    return a2, {"X": X, "z1": z1, "a1": a1, "z2": z2, "a2": a2}


# %% kind=function color=mint title="Binary cross-entropy loss"
# @explain: BCE = -[y log p + (1-y) log(1-p)]. Use a tiny ε to avoid
# @explain: log(0). The mean over the batch is the scalar we differentiate.
def bce_loss(a2, y, eps=1e-9):
    return float(-(y * np.log(a2 + eps) + (1 - y) * np.log(1 - a2 + eps)).mean())


# %% kind=function color=mint title="Backward pass (manual gradients)"
# @explain: Chain rule applied step by step. For sigmoid + BCE the
# @explain: gradient at the output simplifies beautifully to (a2 - y).
def backward(p, cache, y):
    a2, a1, z1, X = cache["a2"], cache["a1"], cache["z1"], cache["X"]
    n = y.shape[0]

    dz2 = (a2 - y) / n
    dW2 = a1.T @ dz2
    db2 = dz2.sum(axis=0, keepdims=True)

    da1 = dz2 @ p["W2"].T
    dz1 = da1 * relu_grad(z1)
    dW1 = X.T @ dz1
    db1 = dz1.sum(axis=0, keepdims=True)

    return {"W1": dW1, "b1": db1, "W2": dW2, "b2": db2}


# %% kind=function color=mint title="SGD update"
# @explain: Each parameter takes a step in the direction that reduces
# @explain: the loss. lr (learning rate) controls the step size.
def step(p, grads, lr=0.5):
    for k in p:
        p[k] -= lr * grads[k]


# %% kind=loop color=peach title="Train the network"
# @explain: Forward → loss → backward → step. Repeat 2000 times. We
# @explain: print the loss every 200 epochs to watch it fall.
params = init(in_dim=2, hidden=16, out_dim=1)
losses = []
for epoch in range(2000):
    a2, cache = forward(X_tr, params)
    loss = bce_loss(a2, y_tr)
    grads = backward(params, cache, y_tr)
    step(params, grads, lr=0.5)
    losses.append(loss)
    if epoch % 200 == 0:
        print(f"epoch {epoch:>4}  loss {loss:.4f}")


# %% kind=function color=mint title="Evaluate + plot decision boundary"
# @explain: Threshold the probability at 0.5 for accuracy. The contour
# @explain: plot shows the model's confidence across the input plane.
def predict(X, p):
    a2, _ = forward(X, p)
    return (a2 > 0.5).astype(int)

acc = accuracy_score(y_te, predict(X_te, params))
print(f"test accuracy: {acc:.3f}")

xx, yy = np.meshgrid(np.linspace(-2, 3, 200), np.linspace(-1.5, 2, 200))
grid = np.c_[xx.ravel(), yy.ravel()]
Z, _ = forward(grid.astype(np.float32), params)
plt.figure(figsize=(5, 4))
plt.contourf(xx, yy, Z.reshape(xx.shape), levels=20, cmap="coolwarm", alpha=0.7)
plt.scatter(X[:, 0], X[:, 1], c=y.ravel(), cmap="coolwarm", edgecolor="k")
plt.title(f"From-scratch NN — test acc {acc:.2f}")
plt.show()


# %% [markdown]
# # Part 2 — Same thing in sklearn (one line)


# %% kind=function color=mint title="sklearn MLPClassifier"
# @explain: Multi-Layer Perceptron with one hidden layer of 16 neurons,
# @explain: relu activation, adam optimiser. Same shape as Part 1.
from sklearn.neural_network import MLPClassifier
clf = MLPClassifier(hidden_layer_sizes=(16,), activation="relu",
                    solver="adam", max_iter=2000, random_state=0)
clf.fit(X_tr, y_tr.ravel())
print(f"sklearn MLP accuracy: {clf.score(X_te, y_te.ravel()):.3f}")


# %% [markdown]
# # Part 3 — Same idea in PyTorch (skip if not installed)


# %% kind=function color=mint title="PyTorch version"
# @explain: PyTorch builds the network as nn.Module, computes gradients
# @explain: with autograd, updates with torch.optim. The pattern matches
# @explain: Part 1 one-to-one — but now you can run on a GPU.
if HAS_TORCH:
    import torch
    import torch.nn as nn

    Xt = torch.from_numpy(X_tr); yt = torch.from_numpy(y_tr)
    Xte = torch.from_numpy(X_te); yte = torch.from_numpy(y_te)

    model = nn.Sequential(
        nn.Linear(2, 16), nn.ReLU(),
        nn.Linear(16, 1), nn.Sigmoid(),
    )
    loss_fn = nn.BCELoss()
    opt = torch.optim.Adam(model.parameters(), lr=0.05)

    for epoch in range(500):
        pred = model(Xt)
        loss = loss_fn(pred, yt)
        opt.zero_grad()
        loss.backward()
        opt.step()
        if epoch % 100 == 0:
            print(f"epoch {epoch:>3}  loss {loss.item():.4f}")

    with torch.no_grad():
        acc = ((model(Xte) > 0.5).float() == yte).float().mean().item()
    print(f"PyTorch test accuracy: {acc:.3f}")
else:
    print("torch not installed — click the 📦 Install button or run cell 0.")


# %% [markdown]
# ## Practice
# 1. Increase the hidden size from 16 to 64 in the from-scratch model.
#    Does the loss go lower? Does test accuracy improve?
# 2. Try MLPClassifier with hidden_layer_sizes=(64, 32) on the moons set.


# %% kind=function color=mint title="Practice 2 — deeper sklearn MLP"
clf = MLPClassifier(hidden_layer_sizes=(64, 32), activation="relu",
                    solver="adam", max_iter=2000, random_state=0)
clf.fit(X_tr, y_tr.ravel())
print(f"accuracy: {clf.score(X_te, y_te.ravel()):.3f}")


# %% [markdown]
# ## Recap
# - ✅ Forward pass = matmul + activation, stacked
# - ✅ Loss = a scalar (BCE for binary classification)
# - ✅ Backprop = chain rule, layer by layer
# - ✅ SGD = repeat: forward, loss, backward, step
# - ✅ Same model in sklearn (MLPClassifier) and PyTorch (nn.Sequential)
#
# **Where to go from here**
# - Convolutional networks for images
# - Recurrent / Transformer architectures for sequences
# - Practical tips: dropout, batch norm, data augmentation
