# doodlecode format-version: 2
# Auto-converted from module_85_gans_autoencoders_vae.ipynb
# Open with 📂 Open → press 🎬 Present.


# %% [markdown] color=rose title="Module 85 Gans Autoencoders Vae"
# # Module 85 Gans Autoencoders Vae
#
# A live walkthrough — one card per concept.
# Use → / ← to step through. Press 🎬 Present to begin.



# %% [markdown] color=sky title="Module 85 — GANs · Autoencoders · VAE"
# # Module 85 — GANs · Autoencoders · VAE
#
# > M21 covered **diffusion**, the dominant generative model in 2026. But for the decade before that — and **still under the hood today** — the field was carved up between **autoencoders (AE)**, **variational autoencoders (VAE)**, **generative adversarial networks (GAN)**, and their discrete cousin **VQ-VAE**. Stable Diffusion's latent space *is a VAE*. DALL-E 1, MUSE, AudioCraft, and most audio tokenisers *are VQ-VAEs*. StyleGAN is still the SOTA for human-face editing. This module is that depth pass.
#
# ### What you'll cover
# 1. **The generative-model taxonomy** — explicit density vs implicit vs score-based
# 2. **Autoencoders** — the bottleneck idea + denoising / sparse / contractive variants
# 3. **Variational AE (VAE)** — the probabilistic upgrade + KL term + **reparameterisation trick**
# …


# %% [markdown] color=mint title="1 · The generative-model taxonomy"
# # 1 · The generative-model taxonomy
#
# Every generative model wants to learn `p(x)` (or sample from it). The taxonomy:
#
# ```
#                                        Generative models
#                                               │
#         ┌─────────────────────────────────────┼─────────────────────────────────────┐
# …


# %% [markdown] color=peach title="2 · Autoencoders — the bottleneck"
# # 2 · Autoencoders — the bottleneck
#
# The simplest generative-ish architecture: an **encoder** compresses input `x` to a low-dimensional **code** `z`; a **decoder** reconstructs `x` from `z`. Loss = reconstruction error.
#
# ```
#    x  ──► [ encoder ]  ──► z  ──► [ decoder ]  ──► x̂      loss = ||x − x̂||²
#                             │
#                             └── small bottleneck dim (e.g. 32) forces the network
# …


# %% color=violet title="Training is just MSE / BCE"
# @explain: Training is just MSE / BCE
import torch, torch.nn as nn

class AutoEncoder(nn.Module):
    def __init__(self, in_dim=784, z_dim=32):
        super().__init__()
        self.encoder = nn.Sequential(nn.Linear(in_dim, 256), nn.ReLU(),
                                      nn.Linear(256, z_dim))
        self.decoder = nn.Sequential(nn.Linear(z_dim, 256), nn.ReLU(),
                                      nn.Linear(256, in_dim), nn.Sigmoid())
    def forward(self, x):
        z = self.encoder(x)
        return self.decoder(z), z

# Training is just MSE / BCE
ae = AutoEncoder()
x = torch.rand(64, 784)             # batch of MNIST-flattened images
x_hat, z = ae(x)
loss = nn.functional.binary_cross_entropy(x_hat, x)
print(loss.item(), "  z shape:", z.shape)


# %% [markdown] color=amber title="The AE limitation that motivated VAE:** the latent…"
# # The AE limitation that motivated VAE:** the latent…
#
# **The AE limitation that motivated VAE:** the latent space `z` has **no probability structure**. You can't sample new `z` and decode it — interpolation produces garbage, novel `z` is undefined. That's what VAE fixes.


# %% [markdown] color=rose title="3 · VAE — the probabilistic upgrade"
# # 3 · VAE — the probabilistic upgrade
#
# Kingma & Welling (2013). Instead of a deterministic `z`, the encoder outputs a **distribution** `q(z|x) = N(μ(x), σ(x)²)`. Sample `z` from it, decode, reconstruct.
#
# The loss has **two terms**:
#
# $$\mathcal{L}_{VAE} = \underbrace{\mathbb{E}_{q(z|x)}[-\log p(x|z)]}_{\text{reconstruction}} + \underbrace{\beta \cdot D_{KL}(q(z|x) \,\|\, p(z))}_{\text{regularises latent toward }\mathcal{N}(0, I)}$$
#
# …


# %% color=lime title="class VAE(nn.Module)"
# @explain: Run this cell to see the output.
class VAE(nn.Module):
    def __init__(self, in_dim=784, z_dim=32):
        super().__init__()
        self.enc = nn.Sequential(nn.Linear(in_dim, 256), nn.ReLU())
        self.mu_head     = nn.Linear(256, z_dim)
        self.logvar_head = nn.Linear(256, z_dim)
        self.dec = nn.Sequential(nn.Linear(z_dim, 256), nn.ReLU(),
                                  nn.Linear(256, in_dim), nn.Sigmoid())
    def encode(self, x):
        h = self.enc(x)
        return self.mu_head(h), self.logvar_head(h)
    def reparameterise(self, mu, logvar):
        std = torch.exp(0.5 * logvar)
        eps = torch.randn_like(std)
        return mu + std * eps                              # ← the trick
    def forward(self, x):
        mu, logvar = self.encode(x)
        z = self.reparameterise(mu, logvar)
        x_hat = self.dec(z)
        return x_hat, mu, logvar

def vae_loss(x_hat, x, mu, logvar, beta=1.0):
    recon = nn.functional.binary_cross_entropy(x_hat, x, reduction="sum")
    kl    = -0.5 * torch.sum(1 + logvar - mu.pow(2) - logvar.exp())
    return recon + beta * kl

vae = VAE()
x = torch.rand(64, 784)
x_hat, mu, lv = vae(x)
print("loss:", vae_loss(x_hat, x, mu, lv).item())


# %% [markdown] color=teal title="β-VAE and the disentanglement story"
# # β-VAE and the disentanglement story
#
# Higgins et al. (2017) added a `β` knob in front of the KL term. **High β** forces a tighter prior → individual latent dimensions become more interpretable (one captures rotation, another scale, …). **The trade-off:** higher β = blurrier reconstructions. β-VAE was a major step toward "controllable" generation.
#
# ### Where VAEs survive in 2026
# - **Stable Diffusion's first stage** is a VAE. It compresses 512×512 images to 64×64×4 *latent* space; diffusion then runs there. Without the VAE, diffusion on full pixels would be ~32× more expensive.
# - **VQ-VAE** (next section) — discrete-latent variant powering many audio + image tokenisers.
# - **Tabular VAE** (TVAE, CTGAN's sibling) — synthetic structured data for tabular ML.


# %% [markdown] color=sky title="4 · GAN — the adversarial game"
# # 4 · GAN — the adversarial game
#
# Goodfellow et al. (2014). Two networks play a minimax game:
#
# ```
#    Generator G : noise z ~ N(0,I)  ──► fake sample G(z)
#                                             │
#                                             ▼
# …


# %% color=mint title="A tiny DCGAN sketch — generator + discriminator"
# @explain: A tiny DCGAN sketch — generator + discriminator
# @explain: adds BatchNorm + transpose-conv + LeakyReLU on D; this is the minimal idea
# @explain: Training loop sketch
# @explain: (training loop omitted for brevity — alternate D, G updates with BCE loss)
# A tiny DCGAN sketch — generator + discriminator. Production-grade DCGAN
# adds BatchNorm + transpose-conv + LeakyReLU on D; this is the minimal idea.
class Generator(nn.Module):
    def __init__(self, z_dim=64, out_dim=784):
        super().__init__()
        self.net = nn.Sequential(
            nn.Linear(z_dim, 256), nn.ReLU(),
            nn.Linear(256, 512),   nn.ReLU(),
            nn.Linear(512, out_dim), nn.Tanh(),   # outputs in [-1, 1]
        )
    def forward(self, z): return self.net(z)

class Discriminator(nn.Module):
    def __init__(self, in_dim=784):
        super().__init__()
        self.net = nn.Sequential(
            nn.Linear(in_dim, 512), nn.LeakyReLU(0.2),
            nn.Linear(512, 256),    nn.LeakyReLU(0.2),
            nn.Linear(256, 1),      nn.Sigmoid(),
        )
    def forward(self, x): return self.net(x)

# Training loop sketch
G, D = Generator(), Discriminator()
opt_G = torch.optim.Adam(G.parameters(), lr=2e-4, betas=(0.5, 0.999))
opt_D = torch.optim.Adam(D.parameters(), lr=2e-4, betas=(0.5, 0.999))

# (training loop omitted for brevity — alternate D, G updates with BCE loss)
print("G params:", sum(p.numel() for p in G.parameters()))
print("D params:", sum(p.numel() for p in D.parameters()))


# %% [markdown] color=peach title="5 · The GAN lineage"
# # 5 · The GAN lineage
#
# | Architecture | Year | Key insight |
# |---|---|---|
# | **GAN** | 2014 | the original minimax setup |
# | **DCGAN** | 2015 | transposed convs in G, strided convs in D, BatchNorm, no FC layers → first stable GAN |
# | **InfoGAN** | 2016 | maximise mutual info between code and output → disentanglement |
# | **Pix2Pix** | 2017 | conditional GAN; paired image translation |
# …


# %% [markdown] color=violet title="6 · VQ-VAE — discrete latents"
# # 6 · VQ-VAE — discrete latents
#
# van den Oord et al. (2017). A VAE where the latent space is **a finite codebook** instead of continuous Gaussian. The encoder outputs a continuous vector `z_e`; we then **snap** it to the nearest codebook entry `e_k`:
#
# ```
#    x ──► encoder ──► z_e (continuous)
#                        │
#                        ▼  argmin over codebook
# …


# %% [markdown] color=amber title="7 · Where each still matters in 2026"
# # 7 · Where each still matters in 2026
#
# ```
#    AE              still everywhere as: pretraining, anomaly detection,
#                    embedding learning, masked-AE pretraining for ViT
#    Denoising AE    direct conceptual ancestor of diffusion (M21, M86)
#    VAE             encoder/decoder INSIDE Stable Diffusion's latent space
#                    tabular synthetic data (TVAE)
# …


# %% [markdown] color=rose title="8 · Train them on MNIST in 5 minutes"
# # 8 · Train them on MNIST in 5 minutes
#
# A skeleton training loop you can run yourself. The three models share the same data pipeline; only the loss and the inner update differ.
#
# ```python
# from torchvision import datasets, transforms
# from torch.utils.data import DataLoader
#
# …


# %% [markdown] color=lime title="✅ Recap"
# # ✅ Recap
#
# - The generative-model taxonomy: **explicit density** (autoregressive, flows, VAE) · **implicit** (GAN) · **score-based** (diffusion, M21 / M86).
# - **Autoencoders** compress to a bottleneck; **denoising AE** is the direct ancestor of diffusion; **MAE** is the SSL pretraining recipe for ViT (M65).
# - **VAE** adds probabilistic structure to AE: Normal prior + KL term + **reparameterisation trick**. VAEs live inside Stable Diffusion's latent space.
# - **GAN** is a minimax game between G and D. Mode collapse, instability, hyperparameter brittleness — every successful GAN paper is more about *stabilising training* than architecture.
# - **GAN lineage**: DCGAN → WGAN → WGAN-GP → Progressive → **StyleGAN-3** (still SOTA for face editing) + **BigGAN** + conditional GANs (Pix2Pix / CycleGAN).
# - **VQ-VAE** is the universal **tokeniser** behind audio (Encodec / Mimi / Soundstream), image (MAGVIT-v2), and video autoregressive models.
# …


# %% [markdown] color=lime title="Thanks"
# # End of Module
#
# Next module continues the roadmap.
# Source: https://github.com/kader-xai/data-science-roadmap


