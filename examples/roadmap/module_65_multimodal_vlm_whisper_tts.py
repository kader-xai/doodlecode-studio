# doodlecode format-version: 2
# Auto-converted from module_65_multimodal_vlm_whisper_tts.ipynb
# Open with 📂 Open → press 🎬 Present.


# %% [markdown] color=rose title="Module 65 Multimodal Vlm Whisper Tts"
# # Module 65 Multimodal Vlm Whisper Tts
#
# A live walkthrough — one card per concept.
# Use → / ← to step through. Press 🎬 Present to begin.



# %% [markdown] color=sky title="Module 65 — Multimodal"
# # Module 65 — Multimodal
#
# > The course so far is **text-only**. But every modern AI product takes images, audio, and increasingly video. This module covers the *modalities you'll actually ship*: **Vision-Language Models (VLMs)** for "describe this screenshot," **Whisper** for speech-to-text, and the **TTS stack** for voice output. You'll see the architecture (it's the same transformer with an encoder swapped onto the front) and the production patterns that follow.
#
# ### What you'll cover
# 1. The multimodal landscape in one diagram
# 2. How a **Vision-Language Model** is built (CLIP → projector → LLM)
# 3. **CLIP** — encode an image into the *same vector space as text*
# …


# %% [markdown] color=mint title="1 · The multimodal landscape"
# # 1 · The multimodal landscape
#
# ```
#                 ┌──────────── text-only LLMs (M16-M63) ─────────────┐
#                 │  GPT-2, Llama, Qwen — everything we built          │
#                 └────────────────────────────────────────────────────┘
#                                           ▼  add modality encoders
#                 ┌────────────────────────────────────────────────────┐
# …


# %% [markdown] color=peach title="2 · VLM architecture in one picture"
# # 2 · VLM architecture in one picture
#
# ```
#    image (224×224)
#         │
#         ▼
#    ┌────────────────────┐
#    │  ViT image encoder │  (CLIP / SigLIP / EVA — ~300M params)
# …


# %% [markdown] color=violet title="3 · CLIP — the encoder that started it all"
# # 3 · CLIP — the encoder that started it all
#


# %% color=amber title="!pip -q install transformers Pillow torch torchaudio"
# @explain: Run this cell to see the output.
!pip -q install transformers Pillow torch torchaudio


# %% color=rose title="CLIP encodes images AND text into the SAME 512-d"
# @explain: CLIP encodes images AND text into the SAME 512-d (or 768-d) vector space
# @explain: Cosine similarity in that space tells you how well a caption matches an image
# @explain: Grab a sample image
# @explain: logits_per_image is the image-vs-caption similarity matrix
# CLIP encodes images AND text into the SAME 512-d (or 768-d) vector space.
# Cosine similarity in that space tells you how well a caption matches an image.
import torch
from PIL import Image
from transformers import CLIPProcessor, CLIPModel
import urllib.request

# Grab a sample image
url = "https://images.cocodataset.org/val2017/000000039769.jpg"
img_path = "/content/cats.jpg"
urllib.request.urlretrieve(url, img_path)
img = Image.open(img_path)

model_id = "openai/clip-vit-base-patch32"
proc = CLIPProcessor.from_pretrained(model_id)
clip = CLIPModel.from_pretrained(model_id).eval()

captions = [
    "a photo of two cats sleeping on a couch",
    "a photo of a dog running on the beach",
    "a screenshot of a Python error traceback",
    "a city skyline at sunset",
]

inputs = proc(text=captions, images=img, return_tensors="pt", padding=True)
with torch.no_grad():
    out = clip(**inputs)

# logits_per_image is the image-vs-caption similarity matrix
probs = out.logits_per_image.softmax(dim=-1)[0]
for caption, p in zip(captions, probs):
    print(f"{p.item():.3f}  {caption}")


# %% [markdown] color=lime title="That's CLIP.** One forward pass and you have an…"
# # That's CLIP.** One forward pass and you have an…
#
# **That's CLIP.** One forward pass and you have an image embedding plus four text embeddings, all comparable in the same space. CLIP-style training is the foundation of every modern VLM:
# - **Image search** — encode every photo once; encode the query text; nearest-neighbour.
# - **Zero-shot classification** — embed `"a photo of a {label}"` for every label, pick the closest.
# - **Safety filters** — embed banned-content captions, flag images close to them.
# - **VLM front-end** — feed the image embeddings (the *patch* embeddings, not the final pooled vector) into an LLM.


# %% [markdown] color=teal title="4 · A real VLM — image-question-answering"
# # 4 · A real VLM — image-question-answering
#


# %% [markdown] color=sky title="For a true VLM that takes `(image, text question) →…"
# # For a true VLM that takes `(image, text question) →…
#
# For a true VLM that takes `(image, text question) → text answer` we use **Qwen2-VL** or **LLaVA** or **Moondream2** (very small).


# %% color=mint title="We'll use Moondream2"
# @explain: We'll use Moondream2 — ~1.9B params, runs on free Colab CPU/T4
# @explain: It's tiny but produces real captions and answers
# @explain: Encode the image once, then ask multiple questions
# We'll use Moondream2 — ~1.9B params, runs on free Colab CPU/T4.
# It's tiny but produces real captions and answers.
from transformers import AutoModelForCausalLM, AutoTokenizer

MODEL_ID = "vikhyatk/moondream2"
moondream = AutoModelForCausalLM.from_pretrained(
    MODEL_ID, trust_remote_code=True, revision="2024-08-26",
).eval()
tok = AutoTokenizer.from_pretrained(MODEL_ID, revision="2024-08-26")

# Encode the image once, then ask multiple questions
enc_image = moondream.encode_image(img)

for q in [
    "Describe this image in one sentence.",
    "How many cats are there?",
    "What surface are they on?",
]:
    a = moondream.answer_question(enc_image, q, tok)
    print(f"Q: {q}\nA: {a}\n")


# %% [markdown] color=peach title="When to pick which VLM"
# # When to pick which VLM
#
# **Notice the pattern.** Encode the image **once**, then run multiple questions against that cached encoding. That's the standard production shape — pay the image-encoder cost once per upload, run cheap text-only forwards per follow-up question.
#
# ### When to pick which VLM
#
# | Model | Params | Cost | Quality |
# |---|---|---|---|
# | **Moondream2** | 1.9B | runs on a phone | great captions, fair OCR |
# | **LLaVA-1.5/1.6** | 7-34B | one GPU | strong all-rounder |
# …


# %% [markdown] color=violet title="5 · Whisper — speech-to-text"
# # 5 · Whisper — speech-to-text
#


# %% color=amber title="Use a small Whisper variant so it runs on free Colab"
# @explain: Use a small Whisper variant so it runs on free Colab
# @explain: whisper-tiny is ~75M params; whisper-large-v3 is ~1.5B (much better) on a GPU
# @explain: Sample audio: a public-domain 16-second clip
# Use a small Whisper variant so it runs on free Colab.
# whisper-tiny is ~75M params; whisper-large-v3 is ~1.5B (much better) on a GPU.
from transformers import pipeline

asr = pipeline(task="automatic-speech-recognition",
               model="openai/whisper-tiny.en",
               chunk_length_s=30)

# Sample audio: a public-domain 16-second clip
audio_url = "https://huggingface.co/datasets/Narsil/asr_dummy/resolve/main/1.flac"
audio_path = "/content/sample.flac"
urllib.request.urlretrieve(audio_url, audio_path)

out = asr(audio_path)
print("transcript:", out["text"])


# %% [markdown] color=rose title="Whisper specifics worth knowing"
# # Whisper specifics worth knowing
#
# **Whisper specifics worth knowing.**
# - **Multilingual + translation** — whisper-large-v3 transcribes 99 languages and can translate any of them *to English* in one pass.
# - **Timestamps** — pass `return_timestamps=True` to get per-segment start/end times. Critical for subtitles, search, diarization.
# - **Hallucinations** — Whisper invents text during long silences. Set `no_speech_threshold` higher; chunk audio with VAD (Silero VAD) first.
# - **Speed**:
#   - `faster-whisper` (CTranslate2 backend) is **4× faster** than HF Transformers with the same weights.
#   - **`distil-whisper`** is 6× faster and 50% smaller with similar quality.
#   - For real-time, **`whisper.cpp`** + `tiny`/`base` on an M1 hits 1× real-time on CPU.


# %% [markdown] color=lime title="6 · TTS — voice synthesis"
# # 6 · TTS — voice synthesis
#


# %% [markdown] color=teal title="TTS is messier than ASR"
# # TTS is messier than ASR
#
# TTS is messier than ASR. The trade-offs:
#
# | Engine | Quality | Speed | Voice cloning | Latency |
# |---|---|---|---|---|
# | **OpenAI TTS** (tts-1, tts-1-hd) | very good | hosted, fast | no | ~700ms |
# | **ElevenLabs** | best in class | hosted | yes (3-min sample) | ~400ms |
# | **Coqui XTTS-v2** | very good | local GPU | yes (6-sec sample) | ~2s |
# | **Bark** (Suno) | quirky / character voices | local GPU | clone via prompt | ~5s |
# …


# %% color=sky title="Demo with a tiny Hugging Face TTS model that runs…"
# @explain: Demo with a tiny Hugging Face TTS model that runs without a GPU
# @explain: SpeechT5 needs a speaker embedding (xvector) — load one of the canonical ones
# Demo with a tiny Hugging Face TTS model that runs without a GPU.
from transformers import pipeline
import soundfile as sf

tts = pipeline("text-to-speech", model="microsoft/speecht5_tts")
# SpeechT5 needs a speaker embedding (xvector) — load one of the canonical ones
from datasets import load_dataset
embeddings_ds = load_dataset("Matthijs/cmu-arctic-xvectors", split="validation")
speaker_embedding = torch.tensor(embeddings_ds[7306]["xvector"]).unsqueeze(0)

result = tts("Multimodal AI is just text-only AI with a couple of encoders on the front.",
             forward_params={"speaker_embeddings": speaker_embedding})
sf.write("/content/out.wav", result["audio"], samplerate=result["sampling_rate"])
print("wrote /content/out.wav  shape:", result["audio"].shape, "  sr:", result["sampling_rate"])


# %% [markdown] color=mint title="You can play `/content/out.wav` in Colab with…"
# # You can play `/content/out.wav` in Colab with…
#
# You can play `/content/out.wav` in Colab with `IPython.display.Audio('/content/out.wav')`.


# %% [markdown] color=peach title="7 · End-to-end voice agent pipeline"
# # 7 · End-to-end voice agent pipeline
#
# ```
#    🎤 user audio
#         │
#         ▼  ASR (Whisper)              ← M65 §5
#    "what's the weather in Paris?"
#         │
# …


# %% [markdown] color=violet title="8 · Multimodal RAG"
# # 8 · Multimodal RAG
#
# When your corpus has images (slides, screenshots, PDFs with figures), text-only RAG misses them. Two patterns:
#
# ### Pattern A — caption-then-embed
# 1. For each image, run a VLM to produce a caption.
# 2. Embed the caption with `sentence-transformers`.
# 3. RAG normally (M30) against text + captions.
# …


# %% [markdown] color=amber title="9 · Costs and the hosted vs local trade-off"
# # 9 · Costs and the hosted vs local trade-off
#
# | Workload | Self-host? | Why |
# |---|---|---|
# | Light VLM usage (< 10k images/day) | hosted (GPT-4o, Claude 3.5, Gemini Flash) | ~$0.01/image; not worth GPU ops |
# | Heavy VLM usage (millions of images) | local Qwen2-VL or LLaVA on A100 | break-even at ~50k images/day |
# | ASR at any scale | local **distil-whisper** or **faster-whisper** | hosted ASR ~$0.006/min adds up fast |
# | TTS — small consumer app | hosted (OpenAI / ElevenLabs) | per-character pricing, no GPU ops |
# …


# %% [markdown] color=rose title="10 · What's next — frontier multimodal"
# # 10 · What's next — frontier multimodal
#
# | Model / model family | What it adds |
# |---|---|
# | **GPT-4o** (2024) | speech-in / speech-out in one model; ~200 ms first audio |
# | **Gemini 2.5 Pro / Flash** | million-token context; video understanding native |
# | **Claude 3.5 Sonnet** (2024) | excellent OCR, complex chart reading, computer-use (M72) |
# | **Qwen2-VL / Qwen2.5-VL** | best open-source VLM as of 2025; strong OCR + video |
# …


# %% [markdown] color=lime title="Thanks"
# # End of Module
#
# Next module continues the roadmap.
# Source: https://github.com/kader-xai/data-science-roadmap


