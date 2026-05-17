# doodlecode format-version: 2
# Auto-converted from module_83_cnns_deep_dive.ipynb
# Open with 📂 Open → press 🎬 Present.


# %% [markdown] color=rose title="Module 83 Cnns Deep Dive"
# # Module 83 Cnns Deep Dive
#
# A live walkthrough — one card per concept.
# Use → / ← to step through. Press 🎬 Present to begin.



# %% [markdown] color=sky title="Module 83 — CNNs Deep Dive"
# # Module 83 — CNNs Deep Dive
#
# > Transformers (M19–M24) and VLMs (M65) eat all the headlines, but the **convolutional neural network** is still under almost every production computer-vision pipeline: defect detection, medical imaging, autonomous driving, OCR, satellite imagery, mobile-app photo features, and as the *image encoder* of every VLM. **This module is the depth pass on CNNs the course referenced but never built standalone** — from the 1998 original to 2024-era detectors.
# >
# > By the end you can read every CV paper, pick the right backbone, fine-tune a pretrained model with one notebook, and decide between YOLO, Mask-RCNN, DETR, and SAM for any vision task.
#
# ### What you'll cover
# 1. Why convolutions — the inductive bias that makes them win on images
# …


# %% [markdown] color=mint title="1 · Why convolutions"
# # 1 · Why convolutions
#
# A **fully-connected layer** treats a 224×224 RGB image as a 150 528-dim vector. The first layer alone needs ~150 528 × hidden units of parameters and *throws away* the spatial structure entirely.
#
# A **convolution** does three things instead:
# - **Local receptive field** — each output pixel looks at a small `k × k` window of the input, not the whole image.
# - **Weight sharing** — the same kernel slides across every position, so the same feature detector applies everywhere.
# - **Translation equivariance** — if the input shifts, the activations shift in lockstep. A face two pixels to the left fires the same "eye" detector.
# …


# %% [markdown] color=peach title="2 · The convolution operation"
# # 2 · The convolution operation
#


# %% color=violet title="A single 2-D convolution: 3 input channels"
# @explain: A single 2-D convolution: 3 input channels, 16 output channels, 3x3 kernel
import torch, torch.nn as nn

# A single 2-D convolution: 3 input channels, 16 output channels, 3x3 kernel
conv = nn.Conv2d(in_channels=3, out_channels=16, kernel_size=3, stride=1, padding=1)
x = torch.randn(8, 3, 32, 32)        # (B, C_in, H, W) — 8 images, 32x32, RGB
y = conv(x)
print("input :", x.shape)              # torch.Size([8, 3, 32, 32])
print("output:", y.shape)              # torch.Size([8, 16, 32, 32])
print("params:", sum(p.numel() for p in conv.parameters()))   # 3*16*3*3 + 16


# %% [markdown] color=amber title="The five knobs you'll tune 1000 times"
# # The five knobs you'll tune 1000 times
#
# **The five knobs you'll tune 1000 times:**
#
# | Knob | What it does |
# |---|---|
# | `kernel_size` | window the kernel sees per output (3 or 5 in practice) |
# | `stride` | how many pixels the kernel hops per step (2 halves the resolution) |
# | `padding` | pixels added at the borders (`padding=1` with `kernel=3` keeps H/W) |
# | `dilation` | spacing between kernel taps — for atrous convs (semantic seg) |
# …


# %% [markdown] color=rose title="3 · LeNet-5 (1998) — the original"
# # 3 · LeNet-5 (1998) — the original
#
# Yann LeCun's 1998 architecture for handwritten-digit recognition. Two conv blocks + two FC layers + a softmax over 10 classes.


# %% color=lime title="class LeNet5(nn.Module)"
# @explain: Run this cell to see the output.
class LeNet5(nn.Module):
    """~60 000-param CNN — runs in ~30 seconds on MNIST CPU."""
    def __init__(self, num_classes=10):
        super().__init__()
        self.features = nn.Sequential(
            nn.Conv2d(1, 6, kernel_size=5, padding=2), nn.Tanh(),
            nn.AvgPool2d(kernel_size=2, stride=2),
            nn.Conv2d(6, 16, kernel_size=5),           nn.Tanh(),
            nn.AvgPool2d(kernel_size=2, stride=2),
        )
        self.classifier = nn.Sequential(
            nn.Flatten(),
            nn.Linear(16 * 5 * 5, 120), nn.Tanh(),
            nn.Linear(120, 84),         nn.Tanh(),
            nn.Linear(84, num_classes),
        )
    def forward(self, x):
        return self.classifier(self.features(x))

m = LeNet5()
print(m)
print("params:", sum(p.numel() for p in m.parameters()))


# %% [markdown] color=teal title="What LeNet got right** (and most modern CNNs still…"
# # What LeNet got right** (and most modern CNNs still…
#
# **What LeNet got right** (and most modern CNNs still inherit): **conv → activation → spatial-downsample**, repeated. **What it got wrong by 2012:** tanh activation (slow), average pooling (lossy), too shallow.


# %% [markdown] color=sky title="4 · AlexNet (2012) — three changes that started the deep-learning era"
# # 4 · AlexNet (2012) — three changes that started the deep-learning era
#
# Krizhevsky-Sutskever-Hinton's ImageNet winner. Five conv layers + three FC layers, 60M parameters. **Three changes** turned LeNet from a toy into a category-winner:
#
# | Change | Why it mattered |
# |---|---|
# | **ReLU activation** | non-saturating gradient → trains much deeper nets |
# | **GPU training** | first big CV model trained on consumer GPUs |
# …


# %% [markdown] color=mint title="5 · VGG (2014) — go deep, stack 3×3"
# # 5 · VGG (2014) — go deep, stack 3×3
#
# VGG-16 and VGG-19 stripped the architecture down to **one block type**: stacked `3×3` convs followed by `2×2` max-pool. Two insights:
#
# - **Three stacked `3×3` convs = one `7×7` receptive field with 1/3 the params**.
# - **Doubling channels every time you halve resolution** keeps compute roughly constant per block.
#
# ```
# …


# %% [markdown] color=peach title="6 · Inception / GoogLeNet (2014) — parallel branches"
# # 6 · Inception / GoogLeNet (2014) — parallel branches
#
# Google's ImageNet 2014 winner. Instead of stacking, **run multiple kernel sizes in parallel** and concatenate the outputs. The **Inception block**:
#
# ```
#                     ┌── 1×1 conv ──────────────────►─┐
#    input ── split ──┼── 1×1 conv → 3×3 conv ──────►─┼── concat ─→ next
#                     ├── 1×1 conv → 5×5 conv ──────►─│
# …


# %% [markdown] color=violet title="7 · ResNet (2015) — the breakthrough"
# # 7 · ResNet (2015) — the breakthrough
#
# He et al. showed that *naively* stacking more layers makes training **harder**, not easier. Their fix: **skip connections**.
#
# ```
#    x ─────────────────────────────┐
#        ┌─ 3×3 conv → BN → ReLU ─┐ │
#        │     ↓                    │ │
# …


# %% color=amber title="Loading a pre-trained ResNet-50 and replacing the…"
# @explain: Loading a pre-trained ResNet-50 and replacing the final head — the classic
# @explain: CV transfer-learning recipe, alive and well
# Loading a pre-trained ResNet-50 and replacing the final head — the classic
# CV transfer-learning recipe, alive and well.
from torchvision.models import resnet50, ResNet50_Weights
m = resnet50(weights=ResNet50_Weights.IMAGENET1K_V2)
m.fc = nn.Linear(m.fc.in_features, 10)        # custom 10-way classifier
print("trainable params (head only):", sum(p.numel() for p in m.fc.parameters()))
print("backbone params (frozen):", sum(p.numel() for p in m.parameters() if not p.requires_grad))


# %% [markdown] color=rose title="8 · EfficientNet (2019) — compound scaling"
# # 8 · EfficientNet (2019) — compound scaling
#
# Tan & Le's insight: depth, width, and input resolution should all scale **together**, by a principled formula:
#
# ```
#    depth        d = α^φ        (more layers)
#    width        w = β^φ        (more channels per layer)
#    resolution   r = γ^φ        (bigger input image)
# …


# %% [markdown] color=lime title="9 · MobileNet (2017+) — depthwise separable convs for phones"
# # 9 · MobileNet (2017+) — depthwise separable convs for phones
#
# Google's mobile-first CNN. The core trick: a normal `3×3` conv mixes both **spatial** and **channel** info. Split that into two cheaper ops:
#
# ```
#    normal 3×3 conv:           cost ≈ k·k·C_in·C_out
#    depthwise-separable:
#        1) depthwise 3×3 conv  (per channel, no mixing)   ≈ k·k·C_in
# …


# %% [markdown] color=teal title="10 · ConvNeXt (2022) — modernised CNN, post-ViT"
# # 10 · ConvNeXt (2022) — modernised CNN, post-ViT
#
# When Vision Transformers (ViT, 2020) started beating CNNs on ImageNet, Liu et al. asked: **can a CNN with similar design choices match a ViT?** Yes — they updated ResNet step-by-step with:
#
# | Modernisation | Borrowed from |
# |---|---|
# | Patchify stem (4×4 stride-4 conv replaces conv+pool) | ViT |
# | Inverted bottleneck (96 → 384 → 96 channels) | MobileNet-V2 |
# …


# %% [markdown] color=sky title="11 · Detection + segmentation"
# # 11 · Detection + segmentation
#
# Image classification = one label per image. Two harder tasks dominate production CV:
#
# ### Object detection — "what + where + bounding box"
#
# | Family | Idea | When |
# |---|---|---|
# …


# %% [markdown] color=mint title="12 · CNNs ↔ ViT in 2026 — what to pick"
# # 12 · CNNs ↔ ViT in 2026 — what to pick
#
# ```
#    small image (< 224²)              MobileNet / EfficientNet-Lite
#    accuracy-first classification     ConvNeXt or ViT-L (close)
#    detection production              YOLOv10 / RT-DETR
#    detection accuracy-frontier       DINO-DETR / Co-DETR
#    semantic segmentation             Mask2Former / SegFormer
# …


# %% [markdown] color=peach title="13 · Production CV patterns"
# # 13 · Production CV patterns
#
# | Pattern | When |
# |---|---|
# | **Pretrained backbone + new head** | almost always; `timm` + `torchvision` ship hundreds |
# | **`torch.compile`** | 1.3–2× training speedup with minimal code change |
# | **ONNX export → ONNX Runtime / TensorRT (M71)** | for cross-language / GPU-edge serving |
# | **TFLite / Core ML / GGUF** | mobile, embedded (M90) |
# …


# %% [markdown] color=violet title="Three tools to know by name"
# # Three tools to know by name
#
# **Three tools to know by name:**
# - **`timm`** (Ross Wightman / HF) — hundreds of pretrained image models, one API.
# - **`torchvision.models`** — the curated PyTorch subset.
# - **Ultralytics** — `pip install ultralytics`; YOLO + utilities + export to ONNX/TensorRT in one CLI.
#
# For the *interview*: be able to sketch ResNet, explain skip connections, name 3 detection families and when each wins.


# %% [markdown] color=amber title="✅ Recap"
# # ✅ Recap
#
# - Convolutions encode **locality**, **weight sharing**, and **translation equivariance** — the right prior for natural images.
# - **LeNet → AlexNet → VGG → Inception → ResNet → EfficientNet → MobileNet → ConvNeXt** is the architectural arc.
# - The single most important idea is **skip connections** — without ResNet we don't have networks deeper than ~20 layers.
# - **EfficientNet** taught us to scale depth + width + resolution **together** with a principled rule.
# - **MobileNet** depthwise-separable convs are the on-device default; **ConvNeXt** is the modern desktop/server backbone.
# - **Detection**: YOLO v10 for production speed, DETR family for accuracy, SAM 2 for interactive seg.
# - CNN backbones are still under almost every production CV pipeline and most VLM image encoders (M65).
# …


# %% [markdown] color=lime title="Thanks"
# # End of Module
#
# Next module continues the roadmap.
# Source: https://github.com/kader-xai/data-science-roadmap


