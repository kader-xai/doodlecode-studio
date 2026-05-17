# doodlecode format-version: 2
# Auto-converted from module_59_instruction_tuning_internals.ipynb
# Open with 📂 Open → press 🎬 Present.


# %% [markdown] color=rose title="Module 59 Instruction Tuning Internals"
# # Module 59 Instruction Tuning Internals
#
# A live walkthrough — one card per concept.
# Use → / ← to step through. Press 🎬 Present to begin.



# %% [markdown] color=sky title="Module 59 — Instruction-Tuning Internals"
# # Module 59 — Instruction-Tuning Internals
#
# > M39 instruction-tuned via Unsloth + TRL's `SFTTrainer`. That's the right production answer — but it **hides every interesting decision** behind one call. This module re-implements the same thing in pure PyTorch so you understand exactly what's happening: the **prompt format**, the **dynamic padding collate**, the **`ignore_index=-100` masking trick**, the **instruction-loss masking** (train only on the response, not the instruction), and **LLM-as-judge evaluation**.
# >
# > Once you've done it by hand, `SFTTrainer` is no longer magic — it's just a wrapper around what you wrote.
#
# ### What you'll cover
# 1. The Alpaca prompt format — `format_input` (with / without `### Input:`)
# …


# %% [markdown] color=mint title="1 · The Alpaca prompt format"
# # 1 · The Alpaca prompt format
#
# The de-facto SFT format since 2023. Same shape in every modern dataset (Alpaca, Dolly, OpenAssistant, OpenHermes, UltraChat — all variants of this):
#
# ```
# Below is an instruction that describes a task. Write a response that appropriately completes the request.
#
# ### Instruction:
# …


# %% color=peach title="example"
# @explain: example
def format_input(entry):
    instruction = (
        "Below is an instruction that describes a task. "
        "Write a response that appropriately completes the request."
        f"\n\n### Instruction:\n{entry['instruction']}"
    )
    input_block = f"\n\n### Input:\n{entry['input']}" if entry.get("input") else ""
    return instruction + input_block

# example
example = {"instruction": "Translate to French.", "input": "Hello, world.", "output": "Bonjour, le monde."}
print(format_input(example))
print()
print(format_input({"instruction": "List three primary colors.", "input": "", "output": "Red, blue, yellow."}))


# %% [markdown] color=violet title="Why this matters.** A chat-tuned model has learned…"
# # Why this matters.** A chat-tuned model has learned…
#
# **Why this matters.** A chat-tuned model has learned that *"after `### Response:` comes the answer"*. At inference time you send the prompt **up to and including `### Response:\n`** and the model continues. Mess up the format and the model produces nonsense.


# %% [markdown] color=amber title="2 · `InstructionDataset` — pre-format + tokenize"
# # 2 · `InstructionDataset` — pre-format + tokenize
#


# %% color=rose title="!pip -q install tiktoken torch"
# @explain: Run this cell to see the output.
!pip -q install tiktoken torch


# %% color=lime title="A small Alpaca-style file"
# @explain: A small Alpaca-style file (Raschka's): 1,100 entries; we'll use 50 for demo speed
import torch, tiktoken, urllib.request, json, pathlib
from torch.utils.data import Dataset, DataLoader

# A small Alpaca-style file (Raschka's): 1,100 entries; we'll use 50 for demo speed
URL = "https://raw.githubusercontent.com/rasbt/LLMs-from-scratch/main/ch07/01_main-chapter-code/instruction-data.json"
p = pathlib.Path("/content/instruction-data.json")
if not p.exists(): urllib.request.urlretrieve(URL, p)
data = json.loads(p.read_text())[:50]
print("n examples:", len(data))
print("sample:", data[0])


# %% color=teal title="tok = tiktoken.get_encoding('gpt2')"
# @explain: Run this cell to see the output.
tok = tiktoken.get_encoding("gpt2")

class InstructionDataset(Dataset):
    def __init__(self, data, tokenizer):
        self.encoded = []
        for e in data:
            prompt   = format_input(e)
            response = f"\n\n### Response:\n{e['output']}"
            full     = prompt + response
            self.encoded.append(tokenizer.encode(full))
    def __len__(self): return len(self.encoded)
    def __getitem__(self, i): return self.encoded[i]

ds = InstructionDataset(data, tok)
print("first row length:", len(ds[0]))
print("preview decoded:", tok.decode(ds[0][:80]) + " …")


# %% [markdown] color=sky title="Note what we *don't* do here.** We don't pad"
# # Note what we *don't* do here.** We don't pad
#
# **Note what we *don't* do here.** We don't pad. We don't truncate to a fixed length. We don't slap labels on. Those decisions happen later, in the **collate function** — which is the key idea of this module.


# %% [markdown] color=mint title="3 · `custom_collate_fn` — dynamic padding + shift-by-one"
# # 3 · `custom_collate_fn` — dynamic padding + shift-by-one
#
# The DataLoader gives us a list of variable-length lists. The collate function turns it into a batched tensor. *How* we pad matters a lot:
#
# - **Bad**: pad every example to the global max length → wastes compute on short examples.
# - **Good**: pad to the **longest in this batch only** (dynamic padding).
# - **Also**: build a `targets` tensor that's the input shifted by one (M55's trick), but with **the padding tokens masked out of the loss**.


# %% color=peach title="1"
# @explain: 1
# @explain: mask all but the FIRST pad in the targets — cross-entropy will skip them
def custom_collate_fn(batch, pad_id=50256, ignore_idx=-100, device="cpu", allowed_max_length=None):
    # 1. figure out the longest sequence in THIS batch (+1 for the shift)
    batch_max_length = max(len(item) + 1 for item in batch)

    inputs_list, targets_list = [], []

    for item in batch:
        new_item = item.copy()
        new_item += [pad_id]                                  # one trailing EOT
        padded = new_item + [pad_id] * (batch_max_length - len(new_item))

        inputs  = torch.tensor(padded[:-1])                   # input  = drop last
        targets = torch.tensor(padded[1:])                    # target = drop first  (shift-by-1)

        # mask all but the FIRST pad in the targets — cross-entropy will skip them
        mask = targets == pad_id
        idx_first_pad = torch.argmax(mask.int()).item()
        if mask.any():
            targets[idx_first_pad + 1:] = ignore_idx          # leave one EOT to learn end-of-text

        if allowed_max_length is not None:
            inputs  = inputs[:allowed_max_length]
            targets = targets[:allowed_max_length]

        inputs_list.append(inputs)
        targets_list.append(targets)

    return (
        torch.stack(inputs_list).to(device),
        torch.stack(targets_list).to(device),
    )


# %% color=violet title="tiny verification"
# @explain: tiny verification
# tiny verification
batch = [ds[0], ds[1], ds[2]]
x, y = custom_collate_fn(batch)
print("inputs shape :", x.shape)
print("targets shape:", y.shape)
print("first row, last 12 targets:", y[0, -12:].tolist(), "  (-100 = ignored)")


# %% [markdown] color=amber title="Three things that one function did"
# # Three things that one function did
#
# Three things that one function did:
# 1. **Dynamic padding** — the batch is sized to its longest item, not the global max.
# 2. **Shift-by-one** — `inputs = padded[:-1]`, `targets = padded[1:]`.
# 3. **`ignore_index` masking** — every pad in `targets` (except the first one) becomes **`-100`**.


# %% [markdown] color=rose title="4 · `ignore_index=-100`"
# # 4 · `ignore_index=-100`
#
# `F.cross_entropy(..., ignore_index=-100)` **drops those positions from the loss entirely**. They contribute 0 gradient. This is the cleanest way to handle variable-length sequences in a single tensor — no attention mask gymnastics needed for the loss itself (you'd still want one for attention, but small models usually skip that and rely on the padding being learned as "EOT").
#
# **Why keep *one* pad in `targets`?** So the model can still learn `"... last real token → <|endoftext|>"`. Otherwise it never produces an EOT.


# %% [markdown] color=lime title="5 · Instruction-loss masking — only train on the **response**"
# # 5 · Instruction-loss masking — only train on the **response**
#
# This is the big idea you don't get from `SFTTrainer`'s default config.
#
# If you compute cross-entropy on the **entire prompt + response**, the model is graded for predicting the boilerplate of the prompt too. That's wasted gradient — the prompt is always the same shape. **Instruction-loss masking** sets the target tokens that correspond to the **instruction part** to `-100` so the loss only counts the response:


# %% color=teal title="example: show which positions get gradient"
# @explain: example: show which positions get gradient
def make_instruction_masked_targets(item, tokenizer, prompt_text, ignore_idx=-100):
    """Return inputs + targets with all PROMPT tokens masked out (set to -100)."""
    prompt_ids = tokenizer.encode(prompt_text)
    inputs  = torch.tensor(item[:-1])
    targets = torch.tensor(item[1:])
    n_prompt = len(prompt_ids) - 1   # -1 because we already shifted
    targets[:n_prompt] = ignore_idx
    return inputs, targets

# example: show which positions get gradient
sample = data[0]
prompt = format_input(sample)
full_ids = tok.encode(prompt + f"\n\n### Response:\n{sample['output']}")
inp, tgt = make_instruction_masked_targets(full_ids, tok, prompt + "\n\n### Response:\n")
mask_get_loss = (tgt != -100).int().tolist()
print("len(prompt+resp):", len(tgt))
print("first positions ignored, last positions trainable:")
print("get-loss mask (last 30):", mask_get_loss[-30:])


# %% [markdown] color=sky title="Trade-off: **simpler** (default Raschka recipe) is…"
# # Trade-off: **simpler** (default Raschka recipe) is…
#
# Trade-off: **simpler** (default Raschka recipe) is mask only padding, train on the full sequence. **Better but uglier** is also mask the instruction. Most modern training pipelines (`SFTTrainer`'s `assistant_only_loss=True`, Unsloth's chat templates) **do** mask the instruction. We show both so you know the trade-off.


# %% [markdown] color=mint title="6 · Plug into the M57 training loop"
# # 6 · Plug into the M57 training loop
#
# Reuse the **same** `train_model_simple` from M57. The only difference is the **DataLoader** uses our custom collate. PyTorch's `F.cross_entropy(..., ignore_index=-100)` handles the masking automatically.


# %% color=peach title="from functools import partial"
# @explain: Run this cell to see the output.
from functools import partial

device = "cuda" if torch.cuda.is_available() else "cpu"
collate = partial(custom_collate_fn, device=device, allowed_max_length=512)

train_loader = DataLoader(ds, batch_size=4, shuffle=True, drop_last=True, collate_fn=collate)
x, y = next(iter(train_loader))
print("batch shapes:", x.shape, y.shape)


# %% [markdown] color=violet title="Then the rest of the training is identical to M57"
# # Then the rest of the training is identical to M57
#
# Then the rest of the training is identical to M57 — the helper just needs to pass `ignore_index=-100` to `cross_entropy`:


# %% color=amber title="def calc_loss_batch(x"
# @explain: Run this cell to see the output.
def calc_loss_batch(x, y, model):
    logits = model(x)
    return torch.nn.functional.cross_entropy(
        logits.flatten(0, 1), y.flatten(),
        ignore_index=-100,                  # <-- the masking gets respected here
    )


# %% [markdown] color=rose title="7 · What gets better — the *shape* of an SFT run"
# # 7 · What gets better — the *shape* of an SFT run
#
# You wouldn't run this in the notebook (the M57 tiny model can't form sentences), but here's what to expect on a real run:
#
# | Stage | Behaviour |
# |---|---|
# | Base GPT-2 | continues your prompt with bland next-token completions |
# | After 100 instruction steps | starts emitting `### Response:` boilerplate even when not asked |
# …


# %% [markdown] color=lime title="8 · Generation after fine-tuning"
# # 8 · Generation after fine-tuning
#
# Use the **`generate()` from M57** with `temperature=0.7, top_k=50`, but stop on the **`<|endoftext|>`** token id (`50256` for GPT-2 BPE).
#
# ```python
# out = generate(model, prompt_ids, max_new=200,
#                context_size=1024, temperature=0.7, top_k=50,
#                eos_id=tok.eot_token)
# …


# %% [markdown] color=teal title="9 · LLM-as-judge with Ollama Llama 3"
# # 9 · LLM-as-judge with Ollama Llama 3
#
# Once you have an SFT model, you need a way to *score* it. Reference-metric scoring (BLEU / ROUGE) is unreliable for open-ended answers. **LLM-as-judge** asks a strong model (Llama-3 / Claude / GPT-4o) to rate your model's output 0–100.


# %% color=sky title="(Concept demo"
# @explain: (Concept demo — requires Ollama running at localhost:11434, see M38.)
# @explain: Real flow:
# @explain: 1
# @explain: 2
# @explain: 3
# (Concept demo — requires Ollama running at localhost:11434, see M38.)
# Real flow:
# 1. For each test example: generate model_output
# 2. Build a judge prompt with (instruction, reference_output, model_output)
# 3. Ask Llama-3 to score 0-100; parse the integer
# 4. Average → your model's score

import json
def make_judge_prompt(entry, model_output):
    return (
        "Below is an instruction, a reference answer, and a model answer.\n"
        "Score the model answer on a scale of 0 to 100. Respond with ONLY the integer.\n\n"
        f"### Instruction:\n{entry['instruction']}\n\n"
        + (f"### Input:\n{entry['input']}\n\n" if entry.get('input') else "")
        + f"### Reference:\n{entry['output']}\n\n"
        + f"### Model:\n{model_output}\n\n"
        + "### Score:\n"
    )

# Call Ollama via its REST API (M38)
def ollama_score(prompt, model="llama3"):
    import urllib.request
    body = json.dumps({"model": model, "prompt": prompt, "stream": False}).encode()
    req  = urllib.request.Request("http://localhost:11434/api/generate", data=body)
    resp = json.loads(urllib.request.urlopen(req).read())["response"]
    # parse the first integer 0-100 the judge outputs
    import re
    m = re.search(r"\b(\d{1,3})\b", resp)
    return int(m.group(1)) if m and 0 <= int(m.group(1)) <= 100 else None

# scores = []
# for entry in eval_set:
#     model_out = generate_with_my_model(entry)
#     score     = ollama_score(make_judge_prompt(entry, model_out))
#     scores.append(score)
# print("avg judge score:", sum(s for s in scores if s)/sum(1 for s in scores if s))
print("Judge pipeline written; pair with Ollama (M38) to run for real.")


# %% [markdown] color=mint title="Why this matters.** Every modern LLM lab uses…"
# # Why this matters.** Every modern LLM lab uses…
#
# **Why this matters.** Every modern LLM lab uses LLM-as-judge for ablation and ranking (Lmsys Arena, MT-Bench, AlpacaEval, Wild-Bench). Cheaper than humans, faster than crowdsourcing, more nuanced than BLEU. We cover full eval pipelines (Promptfoo, lm-eval-harness, Langfuse evals) in **M70**.


# %% [markdown] color=peach title="10 · What `SFTTrainer` (and friends) hide"
# # 10 · What `SFTTrainer` (and friends) hide
#
# You've now reproduced, by hand:
#
# | `SFTTrainer` argument | What you implemented |
# |---|---|
# | `formatting_func=…` | `format_input(entry)` |
# | `data_collator=…` | `custom_collate_fn` |
# …


# %% [markdown] color=lime title="Thanks"
# # End of Module
#
# Next module continues the roadmap.
# Source: https://github.com/kader-xai/data-science-roadmap


