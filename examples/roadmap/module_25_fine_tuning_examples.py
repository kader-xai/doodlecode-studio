# doodlecode format-version: 2
# Auto-converted from module_25_fine_tuning_examples.ipynb
# Open with 📂 Open → press 🎬 Present.


# %% [markdown] color=rose title="Module 25 Fine Tuning Examples"
# # Module 25 Fine Tuning Examples
#
# A live walkthrough — one card per concept.
# Use → / ← to step through. Press 🎬 Present to begin.



# %% [markdown] color=sky title="Module 25 — Fine-Tuning Examples"
# # Module 25 — Fine-Tuning Examples
#
# > **Premise:** in M17 you saw `pipeline("sentiment-analysis")` — load any pretrained model in 3 lines. But what if no model on Hugging Face does *exactly* what you need? You **fine-tune** one. This module shows the four ways modern teams do it, with runnable examples that fit on free Colab.
#
# ### What you'll cover
# 1. The fine-tuning landscape — full vs LoRA vs QLoRA vs SFT
# 2. When to fine-tune (vs prompt engineering vs RAG)
# 3. **Example 1:** Full fine-tuning a small model on a custom corpus
# …


# %% [markdown] color=mint title="0 · Setup"
# # 0 · Setup
#


# %% color=peach title="!pip -q install -U transformers datasets peft trl…"
# @explain: Run this cell to see the output.
!pip -q install -U transformers datasets peft trl accelerate bitsandbytes evaluate

import os, torch, numpy as np, random
from datasets import Dataset
from transformers import (AutoTokenizer, AutoModelForCausalLM,
                          TrainingArguments, Trainer)

def set_seed(s=42):
    random.seed(s); np.random.seed(s); torch.manual_seed(s)
    if torch.cuda.is_available(): torch.cuda.manual_seed_all(s)

set_seed(42)
device = "cuda" if torch.cuda.is_available() else "cpu"
print("device:", device, "| torch:", torch.__version__)


# %% [markdown] color=violet title="1 · The Fine-Tuning Landscape"
# # 1 · The Fine-Tuning Landscape
#
# | Method | What changes | Memory | Speed | When to use |
# |---|---|---|---|---|
# | **Full fine-tuning** | every weight | huge — N × forward | slow | small model, lots of GPU, custom domain |
# | **LoRA** | tiny low-rank adapters next to each weight matrix | ~1% of full | fast | the modern default for most fine-tuning |
# | **QLoRA** | LoRA on top of a 4-bit quantised base model | runs 70B on 1× 4090 | medium | huge models on small hardware |
# | **SFT** (Supervised Fine-Tuning) | usually LoRA, but on instruction-response pairs | as LoRA | as LoRA | teaching a base LM to follow instructions |
# …


# %% [markdown] color=amber title="2 · A Tiny Custom Dataset"
# # 2 · A Tiny Custom Dataset
#
# We'll teach a small GPT-2 to write in the style of a fictional company's marketing voice. ~50 examples, just enough to see fine-tuning take effect.


# %% color=rose title="marketing_examples = ["
# @explain: Run this cell to see the output.
marketing_examples = [
    "Our cloud platform is built for teams that ship daily, not quarterly.",
    "Stop juggling 12 tools. Run your entire pipeline from one dashboard.",
    "Built by engineers who actually use the product they ship.",
    "Real-time collaboration, with no Slack required.",
    "Your data stays in your VPC. Always.",
    "Migrate from legacy systems in days, not months.",
    "AI-assisted, human-approved, customer-loved.",
    "Audit logs that pass SOC 2 without a fight.",
    "Single-tenant when you need it; multi-tenant when you want it.",
    "Free for solo devs. Affordable for teams. Honest pricing for enterprises.",
] * 5   # repeat 5x for a tiny but learnable signal

print(f"{len(marketing_examples)} training examples")
print("sample:", marketing_examples[0])

ds = Dataset.from_dict({"text": marketing_examples})
ds = ds.train_test_split(test_size=0.1, seed=42)
print(ds)


# %% [markdown] color=lime title="3 · Example 1 — Full Fine-Tuning"
# # 3 · Example 1 — Full Fine-Tuning
#
# Update **every weight** in `distilgpt2` (88M params). Slow and memory-hungry, but the simplest mental model.


# %% color=teal title="MODEL_NAME = 'distilgpt2'"
# @explain: Run this cell to see the output.
MODEL_NAME = "distilgpt2"
tok = AutoTokenizer.from_pretrained(MODEL_NAME)
tok.pad_token = tok.eos_token
model = AutoModelForCausalLM.from_pretrained(MODEL_NAME).to(device)
print(f"params: {sum(p.numel() for p in model.parameters()):,}")


# %% color=sky title="def tokenize(batch)"
# @explain: Run this cell to see the output.
def tokenize(batch):
    out = tok(batch["text"], truncation=True, padding="max_length", max_length=64)
    out["labels"] = out["input_ids"].copy()    # for causal LM, labels = inputs
    return out

ds_tok = ds.map(tokenize, batched=True, remove_columns=["text"])
print(ds_tok)


# %% color=mint title="Sample BEFORE training"
# @explain: Sample BEFORE training
args = TrainingArguments(
    output_dir="/tmp/full_ft",
    num_train_epochs=3,
    per_device_train_batch_size=4,
    learning_rate=5e-5,
    logging_steps=10,
    report_to="none",
    save_strategy="no",
)

trainer = Trainer(
    model=model,
    args=args,
    train_dataset=ds_tok["train"],
    eval_dataset=ds_tok["test"],
)

# Sample BEFORE training
def generate(prompt, max_new=30):
    ids = tok(prompt, return_tensors="pt").to(device)
    out = model.generate(**ids, max_new_tokens=max_new, do_sample=True,
                         top_p=0.9, temperature=0.8, pad_token_id=tok.eos_token_id)
    return tok.decode(out[0], skip_special_tokens=True)

print("BEFORE FT:", generate("Our platform is"))
trainer.train()
print("AFTER  FT:", generate("Our platform is"))


# %% [markdown] color=peach title="You should see the post-training output adopt the…"
# # You should see the post-training output adopt the…
#
# You should see the post-training output adopt the choppy "marketing one-liner" cadence of the training data — that's fine-tuning working.


# %% [markdown] color=violet title="4 · Example 2 — LoRA (Low-Rank Adaptation)"
# # 4 · Example 2 — LoRA (Low-Rank Adaptation)
#
# Instead of updating every weight, **add a tiny low-rank adapter** to each attention matrix and only train those. Result: ~0.1-1% of parameters trained, almost-equivalent quality.
#
# The math:
# $$W'\,x = (W + \alpha \cdot AB)\,x \quad\text{where } A \in \mathbb{R}^{d \times r},\ B \in \mathbb{R}^{r \times d}, r \ll d$$


# %% color=amber title="Re-load a clean base model so the LoRA adapter…"
# @explain: Re-load a clean base model so the LoRA adapter starts from scratch
from peft import LoraConfig, get_peft_model

# Re-load a clean base model so the LoRA adapter starts from scratch
model = AutoModelForCausalLM.from_pretrained(MODEL_NAME).to(device)

lora_cfg = LoraConfig(
    r=8,                    # rank — usually 4–32
    lora_alpha=16,           # scaling
    target_modules=["c_attn"],   # which weight matrices to adapt (GPT-2 attention)
    lora_dropout=0.05,
    bias="none",
    task_type="CAUSAL_LM",
)

model = get_peft_model(model, lora_cfg)
model.print_trainable_parameters()


# %% color=rose title="args = TrainingArguments("
# @explain: Run this cell to see the output.
args = TrainingArguments(
    output_dir="/tmp/lora_ft",
    num_train_epochs=3,
    per_device_train_batch_size=4,
    learning_rate=3e-4,        # LoRA tolerates much higher LR
    logging_steps=10,
    report_to="none",
    save_strategy="no",
)

trainer = Trainer(model=model, args=args,
                  train_dataset=ds_tok["train"], eval_dataset=ds_tok["test"])

print("BEFORE LoRA:", generate("Our platform is"))
trainer.train()
print("AFTER  LoRA:", generate("Our platform is"))


# %% [markdown] color=lime title="5 · Example 3 — Save & Load the LoRA Adapter"
# # 5 · Example 3 — Save & Load the LoRA Adapter
#
# LoRA adapters are tiny (~1-10 MB) — easy to share, swap, version. The full base model stays unchanged.


# %% color=teal title="ADAPTER_DIR = '/tmp/lora-marketing'"
# @explain: Run this cell to see the output.
ADAPTER_DIR = "/tmp/lora-marketing"
model.save_pretrained(ADAPTER_DIR)

import os
size_mb = sum(os.path.getsize(os.path.join(ADAPTER_DIR, f))
              for f in os.listdir(ADAPTER_DIR) if not f.startswith(".")) / 1e6
print(f"adapter folder: {size_mb:.2f} MB")
print("contents:", os.listdir(ADAPTER_DIR))


# %% color=sky title="Load the base model + apply the adapter"
# @explain: Load the base model + apply the adapter — full pipeline in 3 lines
# @explain: Replace global `model` so generate() uses the restored one
# Load the base model + apply the adapter — full pipeline in 3 lines
from peft import PeftModel

base = AutoModelForCausalLM.from_pretrained(MODEL_NAME).to(device)
restored = PeftModel.from_pretrained(base, ADAPTER_DIR).to(device)

# Replace global `model` so generate() uses the restored one
model = restored
print("RESTORED model:", generate("Our platform is"))


# %% [markdown] color=mint title="6 · Example 4 — SFT with TRL (the modern way)"
# # 6 · Example 4 — SFT with TRL (the modern way)
#
# `trl` (Hugging Face's RLHF library) gives you a `SFTTrainer` that handles instruction-tuning datasets out of the box. Same engine, much less boilerplate.
#
# Dataset format: each row has an `instruction` and a `response`. Standard for fine-tuning chat/instruct models.


# %% color=peach title="Tiny instruction-tuning dataset"
# @explain: Tiny instruction-tuning dataset
from trl import SFTTrainer, SFTConfig

# Tiny instruction-tuning dataset
sft_examples = [
    {"instruction": "Write a one-line marketing tagline.", "response": "Built for teams that ship daily."},
    {"instruction": "Write a one-line marketing tagline.", "response": "Honest pricing. Real engineers. Zero lock-in."},
    {"instruction": "Write a one-line marketing tagline.", "response": "Real-time collaboration without the meetings."},
    {"instruction": "Summarize SOC 2 compliance in one sentence.", "response": "Audit logs and access controls that pass third-party review without a fight."},
    {"instruction": "Write a friendly error message for a 500.", "response": "Something went wrong on our side — we have been notified and we are looking into it."},
] * 8

def format_row(row):
    return {"text": f"### Instruction:\n{row['instruction']}\n\n### Response:\n{row['response']}"}

sft_ds = Dataset.from_list(sft_examples).map(format_row)
print(sft_ds[0]["text"])


# %% color=violet title="base =…"
# @explain: Run this cell to see the output.
base = AutoModelForCausalLM.from_pretrained(MODEL_NAME).to(device)
peft_model = get_peft_model(base, lora_cfg)

sft_args = SFTConfig(
    output_dir="/tmp/sft_lora",
    num_train_epochs=3,
    per_device_train_batch_size=4,
    learning_rate=3e-4,
    logging_steps=10,
    report_to="none",
    save_strategy="no",
    max_seq_length=128,
    packing=False,
)

sft_trainer = SFTTrainer(
    model=peft_model,
    args=sft_args,
    train_dataset=sft_ds,
)

sft_trainer.train()


# %% color=amber title="def chat(prompt)"
# @explain: Run this cell to see the output.
def chat(prompt):
    full = f"### Instruction:\n{prompt}\n\n### Response:\n"
    ids = tok(full, return_tensors="pt").to(device)
    out = peft_model.generate(**ids, max_new_tokens=40, do_sample=True,
                               top_p=0.9, temperature=0.7, pad_token_id=tok.eos_token_id)
    return tok.decode(out[0], skip_special_tokens=True)

print(chat("Write a one-line marketing tagline."))


# %% [markdown] color=rose title="7 · Where This Scales — Beyond SFT"
# # 7 · Where This Scales — Beyond SFT
#
# | Technique | Purpose | Library |
# |---|---|---|
# | **QLoRA** | LoRA on a 4-bit quantised base — fine-tune 70B models on a single 24GB GPU | `bitsandbytes` + `peft` |
# | **DPO** (Direct Preference Optimization) | Align a model to chosen/rejected pairs without a reward model | `trl.DPOTrainer` |
# | **RLHF (PPO)** | Classical 3-stage: SFT → reward model → PPO. What ChatGPT used. | `trl.PPOTrainer` |
# | **Constitutional AI** | Self-critique + revision; what Claude is trained with. | research-stage |
# …


# %% [markdown] color=lime title="8 · Practice"
# # 8 · Practice
#
# 1. **Different style** — replace the marketing dataset with **pirate-speak** examples (~30 rows) and re-run the full fine-tuning section. Does the model learn "ahoy" / "matey" / "ye scallywag"?
#
# 2. **Compare LR** — re-run LoRA training at `learning_rate=1e-5`, `1e-4`, `3e-4`, `1e-3`. Plot final training loss for each. LoRA is famously LR-tolerant.
#
# 3. **Adapter swapping** — train two adapters on two different styles, save both, load each onto the SAME base, generate from the same prompt. Compare outputs.
#
# …


# %% color=teal title="Sketch for Practice #1"
# @explain: Sketch for Practice #1 — pirate dataset
# @explain: (then build a fresh model, attach LoRA, train as in section 4)
# Sketch for Practice #1 — pirate dataset
pirate = [
    "Avast ye, the cloud platform be ready, matey!",
    "Hoist the data flag, set sail for production!",
    "No scallywag shall touch yer VPC, on me word.",
    "Pieces of eight in the audit log, every transaction!",
    "Walk the plank, legacy CMS — we sail with the new!",
] * 8

ds_pirate = Dataset.from_dict({"text": pirate}).train_test_split(test_size=0.1, seed=42)
ds_pirate_tok = ds_pirate.map(tokenize, batched=True, remove_columns=["text"])
print(ds_pirate_tok)
# (then build a fresh model, attach LoRA, train as in section 4)


# %% [markdown] color=sky title="Recap"
# # Recap
#
# ✅ Pick the right fine-tuning method from the situation (full / LoRA / QLoRA / SFT / DPO).
# ✅ Tokenise a custom dataset for causal-LM training.
# ✅ Run **full fine-tuning** with `Trainer`.
# ✅ Run **LoRA fine-tuning** with `peft` — ~1% trainable params, much faster.
# ✅ Save and load LoRA adapters as small portable files.
# ✅ Use **`SFTTrainer`** for instruction-tuning with the standard `### Instruction / ### Response` format.
# …


# %% [markdown] color=lime title="Thanks"
# # End of Module
#
# Next module continues the roadmap.
# Source: https://github.com/kader-xai/data-science-roadmap


