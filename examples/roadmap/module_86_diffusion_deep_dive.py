# doodlecode format-version: 2
# Auto-converted from module_86_diffusion_deep_dive.ipynb
# Open with 📂 Open → press 🎬 Present.


# %% [markdown] color=rose title="Module 86 Diffusion Deep Dive"
# # Module 86 Diffusion Deep Dive
#
# A live walkthrough — one card per concept.
# Use → / ← to step through. Press 🎬 Present to begin.



# %% [markdown] color=sky title="Module 86 — Diffusion Deep Dive"
# # Module 86 — Diffusion Deep Dive
#
# > M21 was the *primer* — what diffusion is and how a tiny DDPM trains on MNIST. This module is the **production version**: how **Stable Diffusion**, **FLUX**, **SD3** and **DiT-based** models actually work in 2026, the **scheduler zoo** (DDIM, Euler, DPM++, LCM, TCD), **classifier-free guidance**, **ControlNet** + **image-LoRA**, and the **distillation tricks** (LCM, Turbo, Schnell) that get 50-step diffusion down to 1-4 steps. By the end you'll know which model to pick, which scheduler matches it, how to fine-tune a character LoRA, and how to wire ControlNet onto any of them.
#
# ### What you'll cover
# 1. The diffusion math recap (one page)
# 2. **Latent Diffusion Models** — why SD works in latent space (M85 VAE callback)
# 3. The **U-Net architecture** that powers SD1.5 / SDXL
# …


# %% [markdown] color=mint title="1 · The diffusion math in one page"
# # 1 · The diffusion math in one page
#
# Two processes:
#
# **Forward (q):** add Gaussian noise step by step over `T` timesteps. With the cosine / linear `β_t` schedule:
#
# $$x_t = \sqrt{\bar\alpha_t}\, x_0 + \sqrt{1 - \bar\alpha_t}\, \epsilon, \qquad \epsilon \sim \mathcal{N}(0, I)$$
#
# …


# %% [markdown] color=peach title="2 · Latent Diffusion Models — why SD works in latent space"
# # 2 · Latent Diffusion Models — why SD works in latent space
#
# Pure-pixel diffusion on a 512×512 RGB image runs 50 U-Net forwards over **786 432 numbers per step**. Slow + expensive.
#
# **LDM (Rombach et al. 2021)** — the architecture that became Stable Diffusion:
#
# ```
#    image x (512×512×3)
# …


# %% [markdown] color=violet title="3 · The U-Net architecture (SD1.5 / SDXL backbone)"
# # 3 · The U-Net architecture (SD1.5 / SDXL backbone)
#
# The denoiser that won 2020-2023.
#
# ```
#        z_t (64×64×4)  +  t_emb  +  c_text
#               │
#               ▼
# …


# %% [markdown] color=amber title="4 · Diffusion Transformers (DiT) — what powers SD3 / FLUX / Sora"
# # 4 · Diffusion Transformers (DiT) — what powers SD3 / FLUX / Sora
#
# In 2022 Peebles & Xie asked: **what if we replace the U-Net with a Transformer?** Result: **DiT** — the architecture under SD3, FLUX, Stable Cascade, OpenAI Sora, and Veo.
#
# ```
#    z_t  ─►  PatchEmbed (2×2 → tokens)
#                               │
#                               ▼
# …


# %% [markdown] color=rose title="5 · Schedulers — the inference-time knob that matters"
# # 5 · Schedulers — the inference-time knob that matters
#
# A scheduler is the **numerical ODE solver** that takes the noise-prediction at each step and produces `x_{t-1}` from `x_t`. Same model, different scheduler → different quality, different number of steps.
#
# | Scheduler | Year | Steps for "OK" | Steps for "great" | Notes |
# |---|---|---|---|---|
# | **DDPM** | 2020 | ~1000 | ~1000 | the original; almost never used in production |
# | **DDIM** | 2020 | 25 | 50 | deterministic, the production default for years |
# …


# %% color=lime title="How a scheduler is used in HuggingFace Diffusers"
# @explain: How a scheduler is used in HuggingFace Diffusers
# @explain: Swap to DPM++ 2M Karras
# How a scheduler is used in HuggingFace Diffusers
scheduler_snippet = '''
from diffusers import StableDiffusionXLPipeline, DPMSolverMultistepScheduler

pipe = StableDiffusionXLPipeline.from_pretrained("stabilityai/stable-diffusion-xl-base-1.0")

# Swap to DPM++ 2M Karras
pipe.scheduler = DPMSolverMultistepScheduler.from_config(
    pipe.scheduler.config,
    use_karras_sigmas=True,
    algorithm_type="dpmsolver++",
)

image = pipe(
    prompt="a photo of a cat in space, detailed, 4k",
    num_inference_steps=25,        # ← scheduler-specific sweet spot
    guidance_scale=7.5,             # ← CFG (next section)
).images[0]
'''
print(scheduler_snippet)


# %% [markdown] color=teal title="6 · Classifier-Free Guidance (CFG)"
# # 6 · Classifier-Free Guidance (CFG)
#
# How does the model know "make it look more like the prompt"? The CFG trick.
#
# At inference, the model is run **twice**:
# - once with the actual text conditioning `c`,
# - once with the **empty / null** conditioning `∅`.
#
# …


# %% [markdown] color=sky title="7 · Conditioning — text, image, sketch, depth, pose"
# # 7 · Conditioning — text, image, sketch, depth, pose
#
# The whole point of "controllable" diffusion is feeding more than just text into the denoiser. Five families to know:
#
# | Mechanism | What it adds | Where |
# |---|---|---|
# | **CLIP text encoder** | text → 77×768 tokens | SD1.5, SDXL |
# | **T5 text encoder** | longer, richer text → tokens | SD3, FLUX, PixArt |
# …


# %% color=mint title="ControlNet usage in 8 lines"
# @explain: ControlNet usage in 8 lines (HuggingFace Diffusers)
# ControlNet usage in 8 lines (HuggingFace Diffusers)
controlnet_snippet = '''
from diffusers import StableDiffusionXLControlNetPipeline, ControlNetModel
from controlnet_aux import OpenposeDetector

cn = ControlNetModel.from_pretrained("diffusers/controlnet-openpose-sdxl-1.0", torch_dtype=torch.float16)
pipe = StableDiffusionXLControlNetPipeline.from_pretrained(
    "stabilityai/stable-diffusion-xl-base-1.0", controlnet=cn, torch_dtype=torch.float16).to("cuda")

pose_img = OpenposeDetector.from_pretrained("lllyasviel/Annotators")(reference_image)
out = pipe(prompt="a woman dancing in a city", image=pose_img,
           controlnet_conditioning_scale=0.8, num_inference_steps=25).images[0]
'''
print(controlnet_snippet)


# %% [markdown] color=peach title="8 · Image-LoRA — fine-tuning in 10 minutes"
# # 8 · Image-LoRA — fine-tuning in 10 minutes
#
# The same LoRA recipe from M39 / M58 (text LLMs) applies to image diffusion U-Nets and DiTs. Three flavours:
#
# | Flavour | What you teach | Typical effort |
# |---|---|---|
# | **Dreambooth** | a *specific subject* (your face, your dog) | 10-30 images, 1-4 K steps |
# | **Textual Inversion** | a new token via embedding learning only | tiny — a couple-MB file |
# …


# %% [markdown] color=violet title="9 · Distillation — 50 steps → 4 → 1"
# # 9 · Distillation — 50 steps → 4 → 1
#
# The biggest 2023-25 advance in diffusion was **distillation** — train a small student to match a big teacher's *trajectory* in far fewer steps.
#
# | Method | Steps | Notes |
# |---|---|---|
# | **Progressive Distillation** (2022) | halved per round | the original recipe; ~4-8 steps |
# | **LCM** (Latent Consistency Models, 2023) | **4 steps** | hugely popular SDXL distillation; CFG = 0 baked in |
# …


# %% [markdown] color=amber title="10 · The 2026 model zoo + production stack"
# # 10 · The 2026 model zoo + production stack
#
# ### Open-weights model zoo
#
# | Model | Released | Type | License | Niche |
# |---|---|---|---|---|
# | **SD 1.5** | 2022 | U-Net + CLIP | open, RAIL | LARGEST community / LoRA / ControlNet ecosystem |
# | **SD XL** | 2023 | U-Net + 2× CLIP | open, RAIL | production quality, fast inference |
# …


# %% [markdown] color=rose title="✅ Recap"
# # ✅ Recap
#
# - Diffusion = noise-prediction over `T` steps; **LDM** runs that in a `64×64×4` **VAE latent** (M85) ≈ 32× cheaper than pixel-space.
# - **U-Net** (SD1.5 / SDXL) → **DiT** (SD3 / FLUX / Sora / Veo) is the architectural arc.
# - **Schedulers** matter as much as the model — **DPM++ 2M Karras** (25 steps) is the SDXL default; **flow-matching Euler** for FLUX; **LCM / TCD** for distilled 4-step models.
# - **CFG** = run with + without conditioning; mix with scale `s`. Sweet spots: SDXL `~6-8`, FLUX `~3.5-5`, distilled `0`.
# - **ControlNet / IP-Adapter / T2I-Adapter** for spatial / image conditioning. **Stack LoRAs** for character × style × lighting.
# - **Distillation** (LCM / Hyper-SD / Turbo / Schnell / DMD) gets you to 1-4 steps for interactive UX.
# …


# %% [markdown] color=lime title="Thanks"
# # End of Module
#
# Next module continues the roadmap.
# Source: https://github.com/kader-xai/data-science-roadmap


