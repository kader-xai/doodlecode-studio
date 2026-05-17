# doodlecode format-version: 2
# Auto-converted from module_21_diffusion_models.ipynb
# Open with 📂 Open → press 🎬 Present.


# %% [markdown] color=rose title="Module 21 Diffusion Models"
# # Module 21 Diffusion Models
#
# A live walkthrough — one card per concept.
# Use → / ← to step through. Press 🎬 Present to begin.



# %% [markdown] color=sky title="Module 21 — Diffusion Models From Scratch"
# # Module 21 — Diffusion Models From Scratch
#
# *The math behind Stable Diffusion, Imagen, and DALL-E — built on a 2D toy dataset where you can see every step.*
#
# Transformers (M19, M20) are the dominant architecture for **language**. Diffusion models are the dominant architecture for **images, audio, and video**. They work on a startlingly different principle: *destroy data with noise, then learn to undo the destruction*.
#
# This notebook builds the whole pipeline on a **2D point distribution** so every plot tells you exactly what's happening — no GPU needed.
#
# ### What you'll cover
# …


# %% color=mint title="import torch"
# @explain: Run this cell to see the output.
import torch, torch.nn as nn, torch.nn.functional as F
import numpy as np, matplotlib.pyplot as plt
from sklearn.datasets import make_moons
torch.manual_seed(0); np.random.seed(0)
print("torch:", torch.__version__)


# %% [markdown] color=peach title="1. The one-paragraph mental model"
# # 1. The one-paragraph mental model
#
# > Take a real image. Add a tiny bit of noise. Then a bit more. Then more. After T steps it's pure Gaussian noise — completely random. Now train a neural network to **predict the noise that was added at each step**. To generate a new image: start from pure noise, and run the trained network *backwards*, subtracting the predicted noise step by step until something photorealistic falls out.
#
# That's it. That's diffusion.


# %% [markdown] color=violet title="2. The toy dataset — 'two moons'"
# # 2. The toy dataset — "two moons"
#
# We'll use 2D points so we can visualise the entire process. Each point has 2 coordinates `(x1, x2)`. Real diffusion does the same thing but on `(3, 256, 256)`-shaped image tensors.


# %% color=amber title="X"
# @explain: Run this cell to see the output.
X, _ = make_moons(n_samples=2000, noise=0.05, random_state=0)
X = torch.from_numpy(X).float()           # shape (2000, 2)

plt.figure(figsize=(5,5))
plt.scatter(X[:, 0], X[:, 1], s=4, alpha=.5)
plt.title("Real data (two moons)"); plt.axis("equal"); plt.show()
print("data shape:", X.shape, "  range:", X.min().item(), "..", X.max().item())


# %% [markdown] color=rose title="3. The forward process — adding noise"
# # 3. The forward process — adding noise
#
# We define a **schedule** `beta_t` that controls how much noise is added at each step `t`. From this we derive `alpha_t = 1 - beta_t` and the cumulative `alpha_bar_t = ∏ alpha_s` (s=1..t).
#
# The neat trick: at any step `t` we can sample directly from the noisy version of `x_0` without iterating:
#
# $$x_t = \sqrt{\bar\alpha_t}\, x_0 + \sqrt{1 - \bar\alpha_t}\, \epsilon, \quad \epsilon \sim \mathcal{N}(0, I)$$
#
# …


# %% color=lime title="T = 200                                          #…"
# @explain: Run this cell to see the output.
T = 200                                          # number of diffusion steps
betas       = torch.linspace(1e-4, 0.02, T)      # linear noise schedule
alphas      = 1 - betas
alpha_bars  = torch.cumprod(alphas, dim=0)        # cumulative product
sqrt_ab     = torch.sqrt(alpha_bars)
sqrt_1mab   = torch.sqrt(1 - alpha_bars)

print(f"alpha_bar at t=0   : {alpha_bars[0]:.4f}  (mostly clean)")
print(f"alpha_bar at t={T-1}: {alpha_bars[-1]:.4f}  (mostly noise)")


# %% color=teal title="Visualise the forward process"
# @explain: Visualise the forward process
def q_sample(x0, t, noise=None):
    """Forward process: jump straight to step t in one operation."""
    if noise is None: noise = torch.randn_like(x0)
    return sqrt_ab[t][:, None] * x0 + sqrt_1mab[t][:, None] * noise

# Visualise the forward process
fig, axes = plt.subplots(1, 5, figsize=(15, 3))
for i, t in enumerate([0, 50, 100, 150, 199]):
    t_batch = torch.full((len(X),), t, dtype=torch.long)
    x_t = q_sample(X, t_batch)
    axes[i].scatter(x_t[:, 0], x_t[:, 1], s=4, alpha=.4)
    axes[i].set_title(f"t={t}\nα̅={alpha_bars[t]:.2f}")
    axes[i].axis("equal"); axes[i].set_xlim(-3, 3); axes[i].set_ylim(-3, 3)
plt.suptitle("Forward process — clean → pure noise"); plt.tight_layout(); plt.show()


# %% [markdown] color=sky title="4. The model — predict the noise"
# # 4. The model — predict the noise
#
# The neural network's only job: given `(x_t, t)`, predict the noise `ε` that was added to get there.
#
# We use a tiny MLP. For real images, this would be a UNet with attention.


# %% color=mint title="class NoisePredictor(nn.Module)"
# @explain: Run this cell to see the output.
class NoisePredictor(nn.Module):
    """Tiny MLP that takes (x_t, t) and predicts the noise."""
    def __init__(self, d_data=2, d_hidden=128, T=200):
        super().__init__()
        self.t_emb = nn.Embedding(T, d_hidden)        # learned timestep embeddings
        self.net = nn.Sequential(
            nn.Linear(d_data + d_hidden, d_hidden), nn.SiLU(),
            nn.Linear(d_hidden, d_hidden),           nn.SiLU(),
            nn.Linear(d_hidden, d_hidden),           nn.SiLU(),
            nn.Linear(d_hidden, d_data),
        )

    def forward(self, x, t):
        h = torch.cat([x, self.t_emb(t)], dim=-1)
        return self.net(h)

model = NoisePredictor()
print("params:", sum(p.numel() for p in model.parameters()))


# %% [markdown] color=peach title="5. Training loop"
# # 5. Training loop
#
# The loss is **MSE between the true noise and the predicted noise**. That's the entire training objective.


# %% color=violet title="1) sample a batch of clean points"
# @explain: 1) sample a batch of clean points
# @explain: 2) sample a random timestep for each one
# @explain: 3) sample noise, get the noisy version
# @explain: 4) ask the model to predict the noise
# @explain: 5) MSE loss
opt = torch.optim.Adam(model.parameters(), lr=2e-3)
losses = []

for step in range(3000):
    # 1) sample a batch of clean points
    idx = torch.randint(0, len(X), (256,))
    x0 = X[idx]

    # 2) sample a random timestep for each one
    t = torch.randint(0, T, (256,))

    # 3) sample noise, get the noisy version
    eps = torch.randn_like(x0)
    x_t = q_sample(x0, t, eps)

    # 4) ask the model to predict the noise
    pred = model(x_t, t)

    # 5) MSE loss
    loss = F.mse_loss(pred, eps)
    opt.zero_grad(); loss.backward(); opt.step()
    losses.append(loss.item())

    if step % 500 == 0:
        print(f"step {step:4d}  loss={loss.item():.4f}")

plt.figure(figsize=(7,3))
plt.plot(losses); plt.title("Training loss"); plt.yscale("log"); plt.grid(alpha=.3); plt.show()


# %% [markdown] color=amber title="6. Sampling — running the network backwards"
# # 6. Sampling — running the network backwards
#
# Now we generate new data by starting from pure noise and stepping backwards from `t=T-1` to `t=0`. At each step:
#
# $$x_{t-1} = \frac{1}{\sqrt{\alpha_t}}\Big(x_t - \frac{\beta_t}{\sqrt{1 - \bar\alpha_t}}\,\hat\epsilon_\theta(x_t, t)\Big) + \sigma_t\, z$$
#
# (`z` is fresh noise, `σ_t = √β_t`). The first term subtracts a scaled version of the predicted noise; the last term adds a tiny bit of fresh noise to keep the chain stochastic.


# %% color=rose title="@torch.no_grad()"
# @explain: Run this cell to see the output.
@torch.no_grad()
def sample(n_samples=2000, capture_steps=(199, 150, 100, 50, 0)):
    x = torch.randn(n_samples, 2)             # start from pure Gaussian noise
    snapshots = {}
    for t in reversed(range(T)):
        t_batch = torch.full((n_samples,), t, dtype=torch.long)
        eps_pred = model(x, t_batch)

        coef    = (1 - alphas[t]) / sqrt_1mab[t]
        x = (x - coef * eps_pred) / torch.sqrt(alphas[t])
        if t > 0:
            x = x + torch.sqrt(betas[t]) * torch.randn_like(x)
        if t in capture_steps:
            snapshots[t] = x.clone()
    return x, snapshots

generated, snapshots = sample(2000)

fig, axes = plt.subplots(1, 6, figsize=(18, 3))
axes[0].scatter(X[:, 0], X[:, 1], s=4, alpha=.4, color="green")
axes[0].set_title("REAL"); axes[0].axis("equal"); axes[0].set_xlim(-3,3); axes[0].set_ylim(-3,3)

for ax, t in zip(axes[1:], [199, 150, 100, 50, 0]):
    pts = snapshots[t]
    ax.scatter(pts[:, 0], pts[:, 1], s=4, alpha=.4, color="orange")
    ax.set_title(f"reverse t={t}"); ax.axis("equal"); ax.set_xlim(-3,3); ax.set_ylim(-3,3)

plt.suptitle("Reverse process — pure noise → two moons"); plt.tight_layout(); plt.show()


# %% [markdown] color=lime title="Compare** the leftmost panel (real data) with the…"
# # Compare** the leftmost panel (real data) with the…
#
# **Compare** the leftmost panel (real data) with the rightmost (model output at `t=0`). Both should show the two-moons shape. The middle panels show the model gradually "sculpting" the moons out of random noise.


# %% [markdown] color=teal title="7. Where this scales to"
# # 7. Where this scales to
#
# The toy version uses an MLP on 2D points. Real diffusion changes three things:
#
# | Component | Toy (this notebook) | Real (e.g. Stable Diffusion) |
# |---|---|---|
# | **Network** | 4-layer MLP, 100k params | UNet with attention, ~860M params |
# | **Data** | 2D points | (3, 64, 64) latents → decoded to (3, 512, 512) images |
# …


# %% [markdown] color=sky title="8. Practice"
# # 8. Practice
#
# 1. **Reduce T** from 200 to 50 and retrain. Does the generated distribution still look like two moons? What about T=10?
# 2. **Different dataset**: use `from sklearn.datasets import make_circles` and rerun the same pipeline. The model code shouldn't need changes.
# 3. **Plot the training loss histogram per timestep** — group losses by `t` and plot mean. You'll see the noise-prediction job is harder at certain steps.
# 4. **Visualise the "vector field"** the model has learned: build a grid of points in `[-3, 3]²`, compute the predicted noise at `t=0`, and plot arrows. The arrows should point *away from the moons*.


# %% color=mint title="4) Visualise the learned vector field at t=0"
# @explain: 4) Visualise the learned vector field at t=0
# @explain: Negative direction = where the model "pulls" points
import numpy as np, matplotlib.pyplot as plt

# 4) Visualise the learned vector field at t=0
xs = torch.linspace(-3, 3, 25)
ys = torch.linspace(-3, 3, 25)
xx, yy = torch.meshgrid(xs, ys, indexing="xy")
grid = torch.stack([xx.flatten(), yy.flatten()], dim=1)

with torch.no_grad():
    t_zero = torch.zeros(len(grid), dtype=torch.long)
    eps_pred = model(grid, t_zero)

# Negative direction = where the model "pulls" points
u = -eps_pred[:, 0].reshape(25, 25)
v = -eps_pred[:, 1].reshape(25, 25)

plt.figure(figsize=(7,7))
plt.quiver(xx, yy, u, v, alpha=.5)
plt.scatter(X[:, 0], X[:, 1], s=2, color="green", alpha=.3, label="data")
plt.title("Learned 'denoising' vector field (arrows pull toward the data)")
plt.axis("equal"); plt.legend(); plt.show()


# %% [markdown] color=peach title="Recap"
# # Recap
#
# ✅ The diffusion mental model: destroy → learn to undo
# ✅ Forward process closed form: `x_t = √α̅·x_0 + √(1-α̅)·ε`
# ✅ Trained an MLP to predict noise (the *only* training objective)
# ✅ Sampled from pure noise back to the data distribution
# ✅ Visualised the entire process on a 2D toy
#
# …


# %% [markdown] color=lime title="Thanks"
# # End of Module
#
# Next module continues the roadmap.
# Source: https://github.com/kader-xai/data-science-roadmap


