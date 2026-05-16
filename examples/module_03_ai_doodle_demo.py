# %% [markdown]
# # Module 3 — Simple AI Doodle Explainer Demo
# A six-line journey through a working neural network:
# **data → model → loss → optimizer → training loop → prediction.**
#
# Each section is rendered as a code cell on the left and a colored doodle
# callout on the right — the callout palette matches the section's purpose:
#
# - 🟢 **mint** — data
# - 🔵 **sky** — model
# - 🟡 **yellow** — loss
# - 🩷 **pink** — optimizer
# - 🟠 **peach** — training loop
# - 🟣 **lavender** — prediction


# %% kind=install color=rose title="0. Install PyTorch (one-time)"
# @explain: Run this cell once if `import torch` fails. The kernel persists
# @explain: between runs, so you only have to install it the first time.
# @explain: This pulls ~700 MB on first install — be patient.
import importlib
import subprocess
import sys

if importlib.util.find_spec("torch") is None:
    subprocess.check_call([sys.executable, "-m", "pip", "install", "--quiet", "torch"])
    print("torch installed.")
else:
    print("torch already available.")


# %% kind=import color=sky title="Imports"
# @explain: torch is the tensor library; torch.nn holds the building
# @explain: blocks for neural networks (layers, losses, containers).
# @tags: import, torch
import torch
import torch.nn as nn


# %% kind=assign color=mint title="1. Input Data"
# @explain: These tensors are the training examples. `x` is the input and
# @explain: `y` is the expected output. The pattern is y = 2 · x — the
# @explain: model's job is to discover that "2".
# @tags: data, tensor
x = torch.tensor([[1.0], [2.0], [3.0]])
y = torch.tensor([[2.0], [4.0], [6.0]])

print("x:", x.squeeze().tolist())
print("y:", y.squeeze().tolist())


# %% kind=class color=sky title="2. Neural Network"
# @explain: A single fully-connected layer with one input and one output.
# @explain: It learns the equation y = w · x + b. The two learnable
# @explain: parameters start random — training tunes them.
# @tags: model, linear
model = nn.Linear(1, 1)

w, b = model.weight.item(), model.bias.item()
print(f"initial weight = {w:+.4f}")
print(f"initial bias   = {b:+.4f}")


# %% kind=function color=yellow title="3. Loss Function"
# @explain: The loss function measures how wrong the predictions are.
# @explain: MSE = mean of (prediction − target)². Smaller = better.
# @explain: We hand this number to the optimizer so it knows which way to
# @explain: nudge the weights.
# @tags: loss, mse
loss_function = nn.MSELoss()


# %% kind=function color=pink title="4. Optimizer"
# @explain: SGD = stochastic gradient descent. It updates the network's
# @explain: weights using the gradients computed by `.backward()`.
# @explain: `lr=0.01` is the learning rate — how big each update step is.
# @tags: optimizer, sgd
optimizer = torch.optim.SGD(model.parameters(), lr=0.01)


# %% kind=loop color=peach title="5. Training Loop"
# @explain: Repeat 100 times: predict → measure loss → zero old gradients
# @explain: → backprop new gradients → step the weights forward.
# @explain: We print every 20 epochs so you can watch the loss fall.
# @tags: training, loop
for epoch in range(100):
    prediction = model(x)
    loss = loss_function(prediction, y)

    optimizer.zero_grad()
    loss.backward()
    optimizer.step()

    if epoch % 20 == 0 or epoch == 99:
        print(f"epoch {epoch:>3} · loss = {loss.item():.6f}")


# %% kind=expr color=lavender title="6. Final Prediction"
# @explain: The trained model predicts the value for input 5.0.
# @explain: It should be close to 10.0 (because y = 2 · x). The learned
# @explain: weight should be near 2 and the bias near 0.
# @tags: predict, inference
test_input = torch.tensor([[5.0]])
result = model(test_input).item()

print(f"model(5.0) = {result:.4f}   (target: 10.0)")
print(f"learned w  = {model.weight.item():+.4f}  (target: +2.0)")
print(f"learned b  = {model.bias.item():+.4f}   (target:  0.0)")


# %% [markdown]
# ## What just happened?
# Six small ideas, in order, are everything a neural network does:
#
# 1. **Data** — tensors of inputs and the answers we want.
# 2. **Model** — a function with learnable parameters.
# 3. **Loss** — a single number saying how wrong we are.
# 4. **Optimizer** — the rule for how to change the parameters.
# 5. **Training loop** — repeat: predict, measure, backprop, update.
# 6. **Inference** — use the trained model on new data.
#
# Click any colored callout on the right to zoom into the matching code.
# In Presentation mode (🎬 in the toolbar) you can step through the cells
# slide by slide.
#
# **Next:** swap `nn.Linear(1, 1)` for a deeper `nn.Sequential([...])`,
# add a non-linear pattern in `y`, and watch the same loop learn it.
