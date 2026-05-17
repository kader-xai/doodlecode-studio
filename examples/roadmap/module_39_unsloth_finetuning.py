# doodlecode format-version: 2
# Auto-converted from module_39_unsloth_finetuning.ipynb
# Open with 📂 Open → press 🎬 Present.


# %% [markdown] color=rose title="Module 39 Unsloth Finetuning"
# # Module 39 Unsloth Finetuning
#
# A live walkthrough — one card per concept.
# Use → / ← to step through. Press 🎬 Present to begin.



# %% [markdown] color=sky title="Module 39 — Fine-tuning LLMs with Unsloth"
# # Module 39 — Fine-tuning LLMs with Unsloth
#
# > Up to here we used pretrained models as-is. Now you'll **teach a model your data** — your tone, your domain, your structured outputs — without burning a $50K H100 budget. **Unsloth** is a drop-in replacement for `transformers` that makes LoRA fine-tuning **2× faster** and **60% lighter on VRAM** with no accuracy loss. A free Colab T4 (16 GB) can fine-tune a 7-8 B model.
#
# ### What you'll cover
# 1. Full fine-tune vs LoRA vs QLoRA — what's actually being trained
# 2. Why Unsloth — kernel rewrites, manual autograd, GGUF export
# 3. Setup — install Unsloth + verify GPU
# …


# %% [markdown] color=mint title="1 · Full fine-tune vs LoRA vs QLoRA"
# # 1 · Full fine-tune vs LoRA vs QLoRA
#
# | Method | What's trained | VRAM (7B) | When |
# |---|---|---|---|
# | **Full fine-tune** | every weight (~7 B params) | ~80 GB | rare; you're nearly retraining the model |
# | **LoRA** | low-rank adapters on attention/MLP (~10–50 M params) | ~16 GB | **default for style/domain adaptation** |
# | **QLoRA** | LoRA + base model in 4-bit | **~7 GB** | what you'll use on a free Colab T4 |
#
# …


# %% [markdown] color=peach title="2 · Why Unsloth"
# # 2 · Why Unsloth
#
# | Feature | Effect |
# |---|---|
# | **Custom Triton kernels** | fused QKV / RMSNorm / RoPE — ~2× speedup over vanilla HF |
# | **Manual autograd** | no PyTorch autograd overhead → ~30% less VRAM |
# | **4-bit native** | no extra cost for QLoRA |
# | **`save_pretrained_gguf`** | one call → GGUF file you can `ollama run` |
# …


# %% [markdown] color=violet title="3 · Setup"
# # 3 · Setup
#


# %% color=amber title="Unsloth pins specific torch/triton versions"
# @explain: Unsloth pins specific torch/triton versions; their installer figures it out
# Unsloth pins specific torch/triton versions; their installer figures it out.
!pip -q install "unsloth[colab-new] @ git+https://github.com/unslothai/unsloth.git"
!pip -q install --no-deps "trl<0.9.0" "peft<0.12.0" "accelerate" "bitsandbytes"


# %% color=rose title="import torch"
# @explain: Run this cell to see the output.
import torch
print("CUDA available:", torch.cuda.is_available())
if torch.cuda.is_available():
    print("GPU:", torch.cuda.get_device_name(0))
    print("VRAM:", round(torch.cuda.get_device_properties(0).total_memory / 1e9, 1), "GB")


# %% [markdown] color=lime title="4 · Load a model in 4-bit"
# # 4 · Load a model in 4-bit
#


# %% color=teal title="from unsloth import FastLanguageModel"
# @explain: Run this cell to see the output.
from unsloth import FastLanguageModel

MAX_SEQ_LEN = 2048
DTYPE       = None      # let Unsloth pick (bf16 on Ampere+, fp16 on Turing)
LOAD_IN_4BIT = True

model, tokenizer = FastLanguageModel.from_pretrained(
    model_name      = "unsloth/Qwen2.5-0.5B-Instruct",  # tiny — fits on free T4 fast
    max_seq_length  = MAX_SEQ_LEN,
    dtype           = DTYPE,
    load_in_4bit    = LOAD_IN_4BIT,
)


# %% [markdown] color=sky title="5 · Add LoRA adapters"
# # 5 · Add LoRA adapters
#


# %% color=mint title="Sanity-check what fraction of params is actually…"
# @explain: Sanity-check what fraction of params is actually trainable
model = FastLanguageModel.get_peft_model(
    model,
    r              = 16,                       # LoRA rank — 8/16/32 are typical
    lora_alpha     = 16,                       # scaling factor; usually = r
    lora_dropout   = 0,                        # 0 is faster + Unsloth-optimised
    bias           = "none",
    use_gradient_checkpointing = "unsloth",    # extra VRAM savings
    target_modules = ["q_proj","k_proj","v_proj","o_proj",
                      "gate_proj","up_proj","down_proj"],
    random_state   = 42,
)

# Sanity-check what fraction of params is actually trainable
trainable = sum(p.numel() for p in model.parameters() if p.requires_grad)
total     = sum(p.numel() for p in model.parameters())
print(f"trainable: {trainable/1e6:.2f} M  ({100*trainable/total:.2f}% of {total/1e9:.2f} B total)")


# %% [markdown] color=peach title="6 · Format the dataset"
# # 6 · Format the dataset
#
# We'll use a tiny synthetic dataset that teaches the model to respond as a deadpan, one-sentence support agent. In practice you'd load a JSONL of (instruction, output) pairs, or a chat dataset with multiple turns.


# %% color=violet title="from datasets import Dataset"
# @explain: Run this cell to see the output.
from datasets import Dataset

raw = [
    {"instruction":"My order hasn't arrived.",       "output":"That's unfortunate; I'll check tracking now."},
    {"instruction":"Can I return this?",              "output":"Yes, returns are accepted within 30 days."},
    {"instruction":"Where's my refund?",              "output":"Refunds post within 5–7 business days."},
    {"instruction":"How do I cancel my subscription?","output":"Visit Settings > Billing > Cancel."},
    {"instruction":"Is your store open today?",       "output":"Yes, daily 9 AM to 9 PM local time."},
    {"instruction":"Do you ship internationally?",    "output":"Yes, to over 60 countries."},
    {"instruction":"My password isn't working.",      "output":"Use the Forgot Password link to reset."},
    {"instruction":"What's your return policy?",      "output":"Full refund within 30 days, unused items only."},
    {"instruction":"Do you have this in red?",        "output":"Stock varies by size; check the listing page."},
    {"instruction":"How long does shipping take?",    "output":"Standard shipping is 3–5 business days."},
] * 8   # tiny multiplier so we have ~80 examples — enough to overfit a style

ds = Dataset.from_list(raw)
print(ds)


# %% color=amber title="Use the model's own chat template so we match its…"
# @explain: Use the model's own chat template so we match its expected format exactly
# Use the model's own chat template so we match its expected format exactly.
def format_example(ex):
    msgs = [
        {"role":"system","content":"You are a deadpan support agent. One sentence only."},
        {"role":"user",  "content": ex["instruction"]},
        {"role":"assistant","content": ex["output"]},
    ]
    return {"text": tokenizer.apply_chat_template(msgs, tokenize=False, add_generation_prompt=False)}

ds = ds.map(format_example)
print(ds[0]["text"])


# %% [markdown] color=rose title="7 · Train with SFTTrainer"
# # 7 · Train with SFTTrainer
#


# %% color=lime title="from trl import SFTTrainer"
# @explain: Run this cell to see the output.
from trl import SFTTrainer
from transformers import TrainingArguments

trainer = SFTTrainer(
    model           = model,
    tokenizer       = tokenizer,
    train_dataset   = ds,
    dataset_text_field = "text",
    max_seq_length  = MAX_SEQ_LEN,
    args = TrainingArguments(
        per_device_train_batch_size = 2,
        gradient_accumulation_steps = 4,        # effective batch = 8
        warmup_steps    = 5,
        max_steps       = 30,                   # tiny — pure demo; raise for real runs
        learning_rate   = 2e-4,
        fp16            = not torch.cuda.is_bf16_supported(),
        bf16            = torch.cuda.is_bf16_supported(),
        logging_steps   = 5,
        optim           = "adamw_8bit",         # 8-bit Adam saves memory
        weight_decay    = 0.01,
        lr_scheduler_type = "linear",
        seed            = 42,
        output_dir      = "outputs",
        report_to       = "none",
    ),
)

trainer.train()


# %% [markdown] color=teal title="8 · Inference with the trained adapter"
# # 8 · Inference with the trained adapter
#


# %% color=sky title="FastLanguageModel.for_inference(model)   # Unsloth:…"
# @explain: Run this cell to see the output.
FastLanguageModel.for_inference(model)   # Unsloth: switch to fast inference mode

msgs = [
    {"role":"system","content":"You are a deadpan support agent. One sentence only."},
    {"role":"user","content":"Why is my package late?"},
]
inputs = tokenizer.apply_chat_template(msgs, return_tensors="pt", add_generation_prompt=True).to("cuda")
out = model.generate(input_ids=inputs, max_new_tokens=64, do_sample=False, temperature=0.0)
print(tokenizer.decode(out[0][inputs.shape[-1]:], skip_special_tokens=True))


# %% [markdown] color=mint title="9 · Save → GGUF → run anywhere"
# # 9 · Save → GGUF → run anywhere
#
# Unsloth's killer feature: **`save_pretrained_gguf`** merges your LoRA into the base, quantises, and writes a single `.gguf` file. That file works in Ollama, llama.cpp, LM Studio — any GGUF runtime.


# %% color=peach title="Save the LoRA adapters separately first"
# @explain: Save the LoRA adapters separately first (small ~50 MB)
# @explain: Merge + quantise + write GGUF (single file ~400 MB for a 0.5B at Q4_K_M)
# @explain: Note: this requires `llama.cpp` to be present — Unsloth fetches it on demand
# Save the LoRA adapters separately first (small ~50 MB)
model.save_pretrained("lora_support_agent")
tokenizer.save_pretrained("lora_support_agent")

# Merge + quantise + write GGUF (single file ~400 MB for a 0.5B at Q4_K_M)
# Note: this requires `llama.cpp` to be present — Unsloth fetches it on demand.
model.save_pretrained_gguf("gguf_support_agent",
                          tokenizer,
                          quantization_method="q4_k_m")

!ls -lh gguf_support_agent | head


# %% [markdown] color=violet title="From here you can build an Ollama Modelfile and…"
# # From here you can build an Ollama Modelfile and…
#
# From here you can build an Ollama Modelfile and `ollama create my-support-agent -f Modelfile` — covered in M38.


# %% [markdown] color=amber title="10 · Fine-tune vs RAG vs prompt"
# # 10 · Fine-tune vs RAG vs prompt
#
# | Need | First try |
# |---|---|
# | Different **tone / format** (e.g. always JSON, always terse) | **prompt + 1-shot example** |
# | Consistent style across thousands of calls | **LoRA fine-tune** |
# | **New facts** the model never saw (your docs, your DB) | **RAG** (M30) |
# | Both new style **and** new domain knowledge | **RAG + LoRA** |
# …


# %% [markdown] color=rose title="✅ Recap"
# # ✅ Recap
#
# - LoRA trains a **low-rank delta**, not the whole model. QLoRA = LoRA on a 4-bit base.
# - **Unsloth** = drop-in HF replacement that's 2× faster and 60% lighter — free-T4-friendly for 7-8B.
# - Workflow: `from_pretrained` → `get_peft_model` → format with chat template → `SFTTrainer.train()` → `save_pretrained_gguf`.
# - Fine-tune for **style/format**; RAG for **facts**.
#
# Next: **M40 — TensorFlow & Keras** (the other half of the deep-learning ecosystem).


# %% [markdown] color=lime title="Thanks"
# # End of Module
#
# Next module continues the roadmap.
# Source: https://github.com/kader-xai/data-science-roadmap


