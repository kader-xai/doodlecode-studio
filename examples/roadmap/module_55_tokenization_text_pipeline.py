# doodlecode format-version: 2
# Auto-converted from module_55_tokenization_text_pipeline.ipynb
# Open with 📂 Open → press 🎬 Present.


# %% [markdown] color=rose title="Module 55 Tokenization Text Pipeline"
# # Module 55 Tokenization Text Pipeline
#
# A live walkthrough — one card per concept.
# Use → / ← to step through. Press 🎬 Present to begin.



# %% [markdown] color=sky title="Module 55 — Tokenization + Text Pipeline"
# # Module 55 — Tokenization + Text Pipeline
#
# > M19 / M20 / M24 built a transformer architecture, but **every input was a random integer ID** — there was no real text. This module fills that gap. We do exactly what Raschka does in Chapter 2: walk from raw text → a tokenizer → a sliding-window dataset → DataLoader-ready batches → token + positional embeddings. At the end you have **real inputs** for the model M20 was missing.
#
# ### What you'll cover
# 1. Why tokenization is the first hard problem
# 2. **A toy tokenizer** — split on whitespace + punctuation, build a vocab
# 3. **`SimpleTokenizerV1`** — round-trip encode/decode
# …


# %% [markdown] color=mint title="1 · Why tokenization"
# # 1 · Why tokenization
#
# A transformer can only see **integers**. So the very first job in any LLM pipeline is: split a string into atomic pieces (**tokens**) and assign each piece a stable integer ID.
#
# | Approach | Pros | Cons |
# |---|---|---|
# | **Character-level** | tiny vocab (~256) | sequences become very long |
# | **Word-level** | short sequences | huge vocab; out-of-vocabulary explosions |
# …


# %% [markdown] color=peach title="2 · Grab a text corpus"
# # 2 · Grab a text corpus
#


# %% color=violet title="!pip -q install tiktoken torch"
# @explain: Run this cell to see the output.
!pip -q install tiktoken torch


# %% color=amber title="Use a tiny public-domain story so the notebook fits…"
# @explain: Use a tiny public-domain story so the notebook fits in memory
# Use a tiny public-domain story so the notebook fits in memory
import urllib.request, pathlib, re

URL = "https://raw.githubusercontent.com/rasbt/LLMs-from-scratch/main/ch02/01_main-chapter-code/the-verdict.txt"
path = pathlib.Path("/content/the-verdict.txt")
if not path.exists():
    urllib.request.urlretrieve(URL, path)
text = path.read_text()
print("characters:", len(text))
print("preview:", text[:120], "...")


# %% [markdown] color=rose title="3 · Toy tokenizer — split on whitespace + punctuation"
# # 3 · Toy tokenizer — split on whitespace + punctuation
#


# %% color=lime title="A regex that keeps the punctuation as separate tokens"
# @explain: A regex that keeps the punctuation as separate tokens (so we can reconstruct text)
# A regex that keeps the punctuation as separate tokens (so we can reconstruct text)
preproc = re.compile(r'([,.:;?_!"()\']|--|\s)')

def tokenize(s):
    return [t for t in preproc.split(s) if t.strip()]

tokens = tokenize(text)
print("total tokens:", len(tokens))
print("first 20:", tokens[:20])


# %% color=teal title="Build the vocab"
# @explain: Build the vocab — sorted unique tokens, each gets an integer ID
# Build the vocab — sorted unique tokens, each gets an integer ID
vocab = {tok: i for i, tok in enumerate(sorted(set(tokens)))}
print("vocab size:", len(vocab))
print("a few:", list(vocab.items())[:8])


# %% [markdown] color=sky title="4 · `SimpleTokenizerV1` — encode/decode round-trip"
# # 4 · `SimpleTokenizerV1` — encode/decode round-trip
#


# %% color=mint title="tighten spaces before punctuation"
# @explain: tighten spaces before punctuation
class SimpleTokenizerV1:
    def __init__(self, vocab):
        self.str_to_int = vocab
        self.int_to_str = {i: s for s, i in vocab.items()}

    def encode(self, text):
        tokens = [t for t in preproc.split(text) if t.strip()]
        return [self.str_to_int[t] for t in tokens]

    def decode(self, ids):
        text = " ".join(self.int_to_str[i] for i in ids)
        # tighten spaces before punctuation
        return re.sub(r'\s+([,.:;?_!"()\'])', r'\1', text)

tok = SimpleTokenizerV1(vocab)
ids = tok.encode("It was the best of times.")
print(ids)
print(tok.decode(ids))


# %% [markdown] color=peach title="Catch:** if you feed `SimpleTokenizerV1` a word…"
# # Catch:** if you feed `SimpleTokenizerV1` a word…
#
# **Catch:** if you feed `SimpleTokenizerV1` a word that wasn't in the training text, it crashes with `KeyError`. Real tokenizers must handle the **unknown token** case.


# %% [markdown] color=violet title="5 · `SimpleTokenizerV2` — special tokens `<|unk|>` and `<|endoftext|>`"
# # 5 · `SimpleTokenizerV2` — special tokens `<|unk|>` and `<|endoftext|>`
#


# %% color=amber title="Add two reserved tokens at the end of the vocab"
# @explain: Add two reserved tokens at the end of the vocab
# @explain: concatenate two docs with the doc-separator special token
# Add two reserved tokens at the end of the vocab
specials = ["<|unk|>", "<|endoftext|>"]
vocab2 = {**vocab}
for s in specials:
    vocab2[s] = len(vocab2)

class SimpleTokenizerV2:
    def __init__(self, vocab):
        self.str_to_int = vocab
        self.int_to_str = {i: s for s, i in vocab.items()}

    def encode(self, text):
        tokens = [t for t in preproc.split(text) if t.strip()]
        tokens = [t if t in self.str_to_int else "<|unk|>" for t in tokens]
        return [self.str_to_int[t] for t in tokens]

    def decode(self, ids):
        text = " ".join(self.int_to_str[i] for i in ids)
        return re.sub(r'\s+([,.:;?_!"()\'])', r'\1', text)

tok2 = SimpleTokenizerV2(vocab2)

# concatenate two docs with the doc-separator special token
mix = "Hello, do you like tea? <|endoftext|> In the sunlit terraces of the palace."
print(tok2.encode(mix))
print(tok2.decode(tok2.encode(mix)))


# %% [markdown] color=rose title="`<|endoftext|>`** is a real GPT-2 special token…"
# # `<|endoftext|>`** is a real GPT-2 special token…
#
# **`<|endoftext|>`** is a real GPT-2 special token used to separate documents during pretraining. **`<|unk|>`** catches anything not in the vocab. Real tokenizers have many more (e.g. `<|im_start|>`, `<|im_end|>` in chat-tuned models).


# %% [markdown] color=lime title="6 · BPE via `tiktoken` — the real GPT-2 tokenizer"
# # 6 · BPE via `tiktoken` — the real GPT-2 tokenizer
#
# Hand-built word tokenizers are clear but useless in practice. GPT-2 ships with a **byte-pair encoding** that handles any UTF-8 string with no `<|unk|>` ever needed. `tiktoken` is OpenAI's fast Rust BPE.


# %% color=teal title="import tiktoken"
# @explain: Run this cell to see the output.
import tiktoken

bpe = tiktoken.get_encoding("gpt2")
print("vocab size:", bpe.n_vocab)               # 50257

ids = bpe.encode("It's hot. Why didn't they Akwirw ier?",
                 allowed_special={"<|endoftext|>"})
print("ids:", ids)
print("each token →", [bpe.decode([i]) for i in ids])


# %% [markdown] color=sky title="Key BPE properties"
# # Key BPE properties
#
# **Key BPE properties.**
# - Vocab is **50 257**. The full GPT-2 model has that many output logits.
# - **No `<unk>`**: any byte-sequence decomposes into pieces that exist.
# - **Unicode-safe**: `"Akwirw ier"` breaks into `['Ak', 'wir', 'w', ' ier']`. Strange word? Still fine.
# - The tokenizer is **deterministic** and **shared** between training and inference.


# %% [markdown] color=mint title="7 · The sliding-window dataset — `GPTDatasetV1`"
# # 7 · The sliding-window dataset — `GPTDatasetV1`
#
# A language model is trained to **predict the next token** given the previous ones. So for a long sequence of token IDs we slide a window of size `max_length` across, and for each window the **target** is the input shifted by one position.


# %% color=peach title="import torch"
# @explain: Run this cell to see the output.
import torch
from torch.utils.data import Dataset, DataLoader

class GPTDatasetV1(Dataset):
    def __init__(self, text, tokenizer, max_length, stride):
        self.input_ids  = []
        self.target_ids = []
        ids = tokenizer.encode(text, allowed_special={"<|endoftext|>"})
        for i in range(0, len(ids) - max_length, stride):
            inp = ids[i: i + max_length]
            tgt = ids[i + 1: i + max_length + 1]
            self.input_ids.append(torch.tensor(inp))
            self.target_ids.append(torch.tensor(tgt))

    def __len__(self):
        return len(self.input_ids)

    def __getitem__(self, idx):
        return self.input_ids[idx], self.target_ids[idx]

ds = GPTDatasetV1(text, bpe, max_length=8, stride=8)
inp, tgt = ds[0]
print("input :", inp.tolist())
print("target:", tgt.tolist())
print("decoded input :", bpe.decode(inp.tolist()))
print("decoded target:", bpe.decode(tgt.tolist()))


# %% [markdown] color=violet title="Notice the off-by-one.** Position 0 of `target` is…"
# # Notice the off-by-one.** Position 0 of `target` is…
#
# **Notice the off-by-one.** Position 0 of `target` is position 1 of `input`. That's the next-token prediction objective in a single line of indexing.
#
# - `max_length=8` → context window per example (real GPT-2 uses 1024).
# - `stride=8` → no overlap; `stride < max_length` makes overlapping windows (more data, but also more duplication).


# %% [markdown] color=amber title="8 · `create_dataloader_v1` — batched, shuffled, ready for training"
# # 8 · `create_dataloader_v1` — batched, shuffled, ready for training
#


# %% color=rose title="def create_dataloader_v1(text"
# @explain: Run this cell to see the output.
def create_dataloader_v1(text, batch_size=4, max_length=256, stride=128,
                          shuffle=True, drop_last=True, num_workers=0):
    tokenizer = tiktoken.get_encoding("gpt2")
    dataset = GPTDatasetV1(text, tokenizer, max_length, stride)
    return DataLoader(dataset,
                      batch_size=batch_size,
                      shuffle=shuffle,
                      drop_last=drop_last,
                      num_workers=num_workers)

loader = create_dataloader_v1(text, batch_size=8, max_length=4, stride=4, shuffle=False)
inputs, targets = next(iter(loader))
print("inputs.shape :", inputs.shape)   # (B, T)
print("targets.shape:", targets.shape)
print(inputs[0], "->", targets[0])


# %% [markdown] color=lime title="Real GPT-2 pretraining used something like…"
# # Real GPT-2 pretraining used something like…
#
# Real GPT-2 pretraining used something like `batch_size=512` and `max_length=1024`. The shape stays `(B, T)` — that's what every block in M20 / M24 expects.


# %% [markdown] color=teal title="9 · Token embeddings"
# # 9 · Token embeddings
#
# Now we map each integer ID to a **dense vector**. This is just a lookup table — but a *trainable* one.


# %% color=sky title="pull one batch and embed it"
# @explain: pull one batch and embed it
torch.manual_seed(123)

vocab_size = bpe.n_vocab          # 50257
output_dim = 256                   # demo size (real GPT-2 is 768)

tok_embedding_layer = torch.nn.Embedding(vocab_size, output_dim)

# pull one batch and embed it
inputs, _ = next(iter(create_dataloader_v1(text, batch_size=8, max_length=4, stride=4, shuffle=False)))
tok_embeds = tok_embedding_layer(inputs)
print("inputs:", inputs.shape, "→ embeddings:", tok_embeds.shape)   # (8,4) → (8,4,256)


# %% [markdown] color=mint title="10 · Positional embeddings — and the final input tensor"
# # 10 · Positional embeddings — and the final input tensor
#
# A vanilla self-attention block is **permutation-invariant** — it sees a *set* of vectors, not a sequence. So we add **positional embeddings** to inject order. GPT-2 uses **learned absolute** positional embeddings (one vector per position).


# %% color=peach title="broadcast-add"
# @explain: broadcast-add: (B,T,D) + (T,D)
context_length = 4                                          # = max_length
pos_embedding_layer = torch.nn.Embedding(context_length, output_dim)

pos_ids = torch.arange(context_length)                       # [0,1,2,3]
pos_embeds = pos_embedding_layer(pos_ids)
print("pos_embeds:", pos_embeds.shape)                       # (T, D)

# broadcast-add: (B,T,D) + (T,D)
input_embeddings = tok_embeds + pos_embeds
print("final input_embeddings.shape:", input_embeddings.shape)   # (B, T, D)


# %% [markdown] color=violet title="That tensor"
# # That tensor
#
# **That tensor — `(B, T, D)` — is exactly what M20's `CausalMultiHeadAttention` and M24's transformer blocks consume.** You've now closed the loop: raw text → tokens → embedded sequences ready for a transformer.
#
# > 🔬 Modern alternatives to learned-absolute pos-emb:
# > - **Sinusoidal** (original "Attention Is All You Need").
# > - **RoPE** (Llama, Qwen, DeepSeek) — rotate Q/K by position. We cover this in M61.
# > - **ALiBi** — bias the attention scores by relative distance.


# %% [markdown] color=amber title="✅ Recap"
# # ✅ Recap
#
# - Tokenization turns text → integer IDs. Subword schemes (BPE) win in practice.
# - `SimpleTokenizerV1/V2` build vocab from a corpus; `tiktoken` ships the real GPT-2 BPE (50 257 tokens, no `<unk>`).
# - A **sliding-window dataset** + **shift-by-one** target gives you next-token-prediction pairs.
# - Token embedding + positional embedding produce a `(B, T, D)` tensor.
# - **That tensor is what M19 / M20 / M24's attention blocks have been waiting for.**
#
# Next: **M56 — Real GPT-2 124M Assembly + Loading Pretrained Weights** (we wire today's tensors into the full GPT-2 from M20 and generate from OpenAI's checkpoint).


# %% [markdown] color=lime title="Thanks"
# # End of Module
#
# Next module continues the roadmap.
# Source: https://github.com/kader-xai/data-science-roadmap


