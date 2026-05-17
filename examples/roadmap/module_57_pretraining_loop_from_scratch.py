# doodlecode format-version: 2
# Auto-converted from module_57_pretraining_loop_from_scratch.ipynb
# Open with 📂 Open → press 🎬 Present.


# %% [markdown] color=rose title="Module 57 Pretraining Loop From Scratch"
# # Module 57 Pretraining Loop From Scratch
#
# A live walkthrough — one card per concept.
# Use → / ← to step through. Press 🎬 Present to begin.



# %% [markdown] color=sky title="Module 57 — Pretraining a GPT from Scratch"
# # Module 57 — Pretraining a GPT from Scratch
#
# > M56 **loaded** OpenAI's weights into our model. This module trains the model **ourselves** — the full pretraining loop. We'll keep it tiny so it fits a Colab CPU: train a fresh GPT-2-shaped model on a single short text, plot loss, compute **perplexity**, swap greedy decoding for **temperature + top-k sampling**, sample text every N steps, and save/load checkpoints. Same recipe as the real thing, just scaled down.
#
# ### What you'll cover
# 1. The pretraining objective — cross-entropy on next-token prediction
# 2. **`calc_loss_batch`** & **`calc_loss_loader`** — the two helper losses
# 3. **`train_model_simple`** — the full training loop
# …


# %% [markdown] color=mint title="1 · The objective — next-token cross-entropy"
# # 1 · The objective — next-token cross-entropy
#
# For each window `[x₀, x₁, …, x_{T-1}]` the target is `[x₁, x₂, …, x_T]` (M55's shift-by-one). At every position the model outputs a logits vector over the vocab, and we ask: how surprised was the model by the actual next token? **Cross-entropy** is that surprise:
#
# $$\mathcal{L} = -\frac{1}{B \cdot T} \sum_{b,t} \log p_\theta(x_{t+1} \mid x_{\le t})$$
#
# Lower is better. The exponentiated cross-entropy is **perplexity** — "the effective branching factor of the model."


# %% [markdown] color=peach title="2 · Set up a tiny model + data"
# # 2 · Set up a tiny model + data
#


# %% color=violet title="!pip -q install tiktoken torch"
# @explain: Run this cell to see the output.
!pip -q install tiktoken torch


# %% color=amber title="(re)use the M55 dataset + M56 model"
# @explain: (re)use the M55 dataset + M56 model — abbreviated versions inline so the notebook is self-contained
import torch, torch.nn as nn, urllib.request, pathlib, tiktoken
from torch.utils.data import Dataset, DataLoader

# (re)use the M55 dataset + M56 model — abbreviated versions inline so the notebook is self-contained
URL = "https://raw.githubusercontent.com/rasbt/LLMs-from-scratch/main/ch02/01_main-chapter-code/the-verdict.txt"
p = pathlib.Path("/content/the-verdict.txt")
if not p.exists(): urllib.request.urlretrieve(URL, p)
text = p.read_text()
print("characters:", len(text))


# %% color=rose title="90/10 split"
# @explain: 90/10 split
class GPTDatasetV1(Dataset):
    def __init__(self, text, tokenizer, max_length, stride):
        self.input_ids, self.target_ids = [], []
        ids = tokenizer.encode(text, allowed_special={"<|endoftext|>"})
        for i in range(0, len(ids) - max_length, stride):
            self.input_ids.append(torch.tensor(ids[i:i+max_length]))
            self.target_ids.append(torch.tensor(ids[i+1:i+max_length+1]))
    def __len__(self): return len(self.input_ids)
    def __getitem__(self, idx): return self.input_ids[idx], self.target_ids[idx]

def make_loader(text, batch_size, max_length, stride, shuffle):
    tok = tiktoken.get_encoding("gpt2")
    return DataLoader(GPTDatasetV1(text, tok, max_length, stride),
                      batch_size=batch_size, shuffle=shuffle, drop_last=True)

# 90/10 split
split = int(0.9 * len(text))
train_loader = make_loader(text[:split], batch_size=2, max_length=256, stride=256, shuffle=True)
val_loader   = make_loader(text[split:], batch_size=2, max_length=256, stride=256, shuffle=False)
print("train batches:", len(train_loader), " val batches:", len(val_loader))


# %% color=lime title="Tiny GPT"
# @explain: Tiny GPT — same architecture as M56, smaller config so it runs on CPU
# Tiny GPT — same architecture as M56, smaller config so it runs on CPU
class LayerNorm(nn.Module):
    def __init__(self, d):
        super().__init__(); self.eps=1e-5
        self.s=nn.Parameter(torch.ones(d)); self.b=nn.Parameter(torch.zeros(d))
    def forward(self,x):
        m=x.mean(-1,keepdim=True); v=x.var(-1,keepdim=True,unbiased=False)
        return self.s*(x-m)/torch.sqrt(v+self.eps)+self.b

class GELU(nn.Module):
    def forward(self,x): return 0.5*x*(1+torch.tanh(torch.sqrt(torch.tensor(2/torch.pi))*(x+0.044715*x**3)))

class MHA(nn.Module):
    def __init__(self, d, ctx, n_heads, drop, bias):
        super().__init__(); self.h=n_heads; self.hd=d//n_heads; self.d=d
        self.Wq=nn.Linear(d,d,bias=bias); self.Wk=nn.Linear(d,d,bias=bias); self.Wv=nn.Linear(d,d,bias=bias)
        self.op=nn.Linear(d,d); self.dp=nn.Dropout(drop)
        self.register_buffer("m", torch.triu(torch.ones(ctx,ctx), diagonal=1))
    def forward(self,x):
        b,T,_=x.shape
        Q=self.Wq(x).view(b,T,self.h,self.hd).transpose(1,2)
        K=self.Wk(x).view(b,T,self.h,self.hd).transpose(1,2)
        V=self.Wv(x).view(b,T,self.h,self.hd).transpose(1,2)
        a=(Q@K.transpose(-2,-1))/self.hd**0.5
        a=a.masked_fill(self.m.bool()[:T,:T], -torch.inf)
        a=self.dp(torch.softmax(a,-1))
        return self.op((a@V).transpose(1,2).contiguous().view(b,T,self.d))

class FFN(nn.Module):
    def __init__(self,d):
        super().__init__()
        self.net=nn.Sequential(nn.Linear(d,4*d), GELU(), nn.Linear(4*d,d))
    def forward(self,x): return self.net(x)

class Block(nn.Module):
    def __init__(self,cfg):
        super().__init__()
        self.att=MHA(cfg["emb_dim"],cfg["context_length"],cfg["n_heads"],cfg["drop_rate"],cfg["qkv_bias"])
        self.ff=FFN(cfg["emb_dim"])
        self.n1=LayerNorm(cfg["emb_dim"]); self.n2=LayerNorm(cfg["emb_dim"])
        self.dp=nn.Dropout(cfg["drop_rate"])
    def forward(self,x):
        x=x+self.dp(self.att(self.n1(x)))
        x=x+self.dp(self.ff(self.n2(x)))
        return x

class GPT(nn.Module):
    def __init__(self,cfg):
        super().__init__()
        self.te=nn.Embedding(cfg["vocab_size"], cfg["emb_dim"])
        self.pe=nn.Embedding(cfg["context_length"], cfg["emb_dim"])
        self.dp=nn.Dropout(cfg["drop_rate"])
        self.blocks=nn.Sequential(*[Block(cfg) for _ in range(cfg["n_layers"])])
        self.fn=LayerNorm(cfg["emb_dim"])
        self.head=nn.Linear(cfg["emb_dim"], cfg["vocab_size"], bias=False)
        self.head.weight = self.te.weight   # weight tying
    def forward(self,idx):
        b,T=idx.shape
        x=self.te(idx)+self.pe(torch.arange(T,device=idx.device))
        x=self.dp(x)
        return self.head(self.fn(self.blocks(x)))

CFG = {"vocab_size":50257, "context_length":256, "emb_dim":128, "n_heads":4, "n_layers":4, "drop_rate":0.1, "qkv_bias":True}
torch.manual_seed(123)
model = GPT(CFG)
print(f"params: {sum(p.numel() for p in model.parameters()):,}")


# %% [markdown] color=teal title="3 · `calc_loss_batch` and `calc_loss_loader`"
# # 3 · `calc_loss_batch` and `calc_loss_loader`
#


# %% color=sky title="flatten"
# @explain: flatten (B,T,V) → (B*T, V) and (B,T) → (B*T) so cross_entropy can consume it
def calc_loss_batch(input_batch, target_batch, model, device):
    input_batch = input_batch.to(device)
    target_batch = target_batch.to(device)
    logits = model(input_batch)                            # (B, T, V)
    # flatten (B,T,V) → (B*T, V) and (B,T) → (B*T) so cross_entropy can consume it
    loss = torch.nn.functional.cross_entropy(
        logits.flatten(0, 1), target_batch.flatten()
    )
    return loss

def calc_loss_loader(loader, model, device, num_batches=None):
    total = 0.0
    n = 0
    if num_batches is None:
        num_batches = len(loader)
    for i, (x, y) in enumerate(loader):
        if i >= num_batches: break
        total += calc_loss_batch(x, y, model, device).item()
        n += 1
    return total / max(n, 1)


# %% [markdown] color=mint title="Why flatten.** `F.cross_entropy` expects 2-D logits…"
# # Why flatten.** `F.cross_entropy` expects 2-D logits…
#
# **Why flatten.** `F.cross_entropy` expects 2-D logits `(N, V)` and 1-D targets `(N,)`. We collapse the batch and time axes — every position contributes one classification loss.


# %% [markdown] color=peach title="4 · `train_model_simple` — the full loop"
# # 4 · `train_model_simple` — the full loop
#


# %% color=violet title="def text_to_token_ids(text"
# @explain: Run this cell to see the output.
def text_to_token_ids(text, tokenizer):
    return torch.tensor(tokenizer.encode(text, allowed_special={"<|endoftext|>"})).unsqueeze(0)

def token_ids_to_text(token_ids, tokenizer):
    return tokenizer.decode(token_ids.squeeze(0).tolist())

def generate_simple(model, ctx_ids, max_new, context_size):
    model.eval()
    for _ in range(max_new):
        ctx = ctx_ids[:, -context_size:]
        with torch.no_grad(): logits = model(ctx)
        next_id = torch.argmax(logits[:, -1, :], dim=-1, keepdim=True)
        ctx_ids = torch.cat((ctx_ids, next_id), dim=1)
    return ctx_ids

def evaluate_model(model, train_loader, val_loader, device, eval_iter):
    model.eval()
    with torch.no_grad():
        train_loss = calc_loss_loader(train_loader, model, device, eval_iter)
        val_loss   = calc_loss_loader(val_loader,   model, device, eval_iter)
    model.train()
    return train_loss, val_loss

def generate_and_print_sample(model, tokenizer, device, start_context):
    model.eval()
    enc = text_to_token_ids(start_context, tokenizer).to(device)
    out = generate_simple(model, enc, max_new=30, context_size=CFG["context_length"])
    print("  >", token_ids_to_text(out, tokenizer).replace("\n", " ")[:120])
    model.train()

def train_model_simple(model, train_loader, val_loader, optimizer, device,
                       num_epochs, eval_freq, eval_iter, start_context, tokenizer):
    train_losses, val_losses, track_tokens = [], [], []
    tokens_seen, global_step = 0, -1
    for epoch in range(num_epochs):
        model.train()
        for x, y in train_loader:
            optimizer.zero_grad()
            loss = calc_loss_batch(x, y, model, device)
            loss.backward()
            optimizer.step()
            tokens_seen += x.numel()
            global_step += 1
            if global_step % eval_freq == 0:
                tl, vl = evaluate_model(model, train_loader, val_loader, device, eval_iter)
                train_losses.append(tl); val_losses.append(vl); track_tokens.append(tokens_seen)
                print(f"Ep{epoch+1} step{global_step:>4}  train {tl:.3f}  val {vl:.3f}")
        generate_and_print_sample(model, tokenizer, device, start_context)
    return train_losses, val_losses, track_tokens


# %% color=amber title="device = 'cuda' if torch.cuda.is_available() else 'cpu'"
# @explain: Run this cell to see the output.
device = "cuda" if torch.cuda.is_available() else "cpu"
model.to(device)
optimizer = torch.optim.AdamW(model.parameters(), lr=4e-4, weight_decay=0.1)
tok = tiktoken.get_encoding("gpt2")

train_losses, val_losses, track_tokens = train_model_simple(
    model, train_loader, val_loader, optimizer, device,
    num_epochs=3, eval_freq=5, eval_iter=5,
    start_context="Every effort moves you", tokenizer=tok,
)


# %% [markdown] color=rose title="You should see the **train loss drop** every few…"
# # You should see the **train loss drop** every few…
#
# You should see the **train loss drop** every few steps and the **sample text gradually become more text-shaped** (it won't write a novel — the corpus is tiny). That's the real pretraining loop.


# %% [markdown] color=lime title="5 · Perplexity"
# # 5 · Perplexity
#


# %% color=teal title="import math"
# @explain: Run this cell to see the output.
import math

def perplexity(loss): return math.exp(loss)
print("final train ppl:", perplexity(train_losses[-1]))
print("final val   ppl:", perplexity(val_losses[-1]))


# %% [markdown] color=sky title="Perplexity** = `exp(cross-entropy)`"
# # Perplexity** = `exp(cross-entropy)`
#
# **Perplexity** = `exp(cross-entropy)`. Intuition: if PPL = 100, the model is as confused as if every token were an independent uniform choice over 100 options. State-of-the-art models on Wikipedia get PPL ≤ 10.


# %% [markdown] color=mint title="6 · Temperature scaling"
# # 6 · Temperature scaling
#


# %% color=peach title="Why greedy is boring: it always picks argmax"
# @explain: Why greedy is boring: it always picks argmax, so generations are deterministic AND repetitive
# @explain: Temperature divides the logits BEFORE softmax
# Why greedy is boring: it always picks argmax, so generations are deterministic AND repetitive.
# Temperature divides the logits BEFORE softmax. T<1 sharpens (more deterministic), T>1 flattens.
import torch.nn.functional as F

vocab = ["forward","toward","across","backward","sideways"]
logits = torch.tensor([4.2, 3.9, 0.5, 0.1, -1.5])

for T in [1e-6, 0.5, 1.0, 2.0, 10.0]:
    p = F.softmax(logits / T, dim=-1)
    print(f"T={T:>6.3g}:", " ".join(f"{w}={pi:.2f}" for w,pi in zip(vocab,p)))


# %% [markdown] color=violet title="`T ≈ 0` is **argmax** (greedy)"
# # `T ≈ 0` is **argmax** (greedy)
#
# `T ≈ 0` is **argmax** (greedy). `T = 1` is the raw distribution. `T → ∞` is uniform random. In practice **0.6–0.9** is the sweet spot for chat models.


# %% [markdown] color=amber title="7 · Top-k sampling"
# # 7 · Top-k sampling
#


# %% color=rose title="example: keep only top-3 of the previous distribution"
# @explain: example: keep only top-3 of the previous distribution, then sample
def top_k_sample(logits, k=10):
    top_logits, top_idx = torch.topk(logits, k)             # k highest logits
    min_top = top_logits[-1]
    logits = torch.where(logits < min_top,
                          torch.tensor(-float("inf"), device=logits.device),
                          logits)
    return logits

# example: keep only top-3 of the previous distribution, then sample
restricted = top_k_sample(logits, k=3)
print("restricted logits:", restricted.tolist())
probs = F.softmax(restricted, dim=-1)
print("probs:", probs.tolist())


# %% [markdown] color=lime title="Top-k** caps the candidate set to the `k` most…"
# # Top-k** caps the candidate set to the `k` most…
#
# **Top-k** caps the candidate set to the `k` most likely tokens (everything else gets `-inf`). Combined with temperature, this is the standard sampling recipe used by GPT-2 / Llama / Mistral / Qwen.
#
# **Top-p (nucleus)** is an alternative: keep tokens until the cumulative probability mass exceeds `p`. We won't implement it here, but it composes the same way.


# %% [markdown] color=teal title="8 · `generate` — temperature + top-k + multinomial"
# # 8 · `generate` — temperature + top-k + multinomial
#


# %% color=sky title="generate three samples with different settings"
# @explain: generate three samples with different settings
def generate(model, idx, max_new, context_size, temperature=0.0, top_k=None, eos_id=None):
    for _ in range(max_new):
        ctx = idx[:, -context_size:]
        with torch.no_grad(): logits = model(ctx)[:, -1, :]

        if top_k is not None:
            logits = top_k_sample(logits[0], top_k).unsqueeze(0)

        if temperature > 0.0:
            probs = torch.softmax(logits / temperature, dim=-1)
            next_id = torch.multinomial(probs, num_samples=1)
        else:
            next_id = torch.argmax(logits, dim=-1, keepdim=True)   # greedy fallback

        if eos_id is not None and (next_id == eos_id).all(): break
        idx = torch.cat((idx, next_id), dim=1)
    return idx

# generate three samples with different settings
torch.manual_seed(42)
for T,k in [(0.0,None),(0.8,10),(1.2,20)]:
    enc = text_to_token_ids("Every effort moves you", tok).to(device)
    out = generate(model, enc, max_new=20, context_size=CFG["context_length"], temperature=T, top_k=k)
    print(f"T={T} k={k}:", token_ids_to_text(out, tok).replace("\n"," ")[:120])


# %% [markdown] color=mint title="This `generate` function is the production-shape…"
# # This `generate` function is the production-shape…
#
# **This `generate` function is the production-shape sampler.** Real serving stacks (vLLM, llama.cpp, Ollama — M38, M44) implement exactly this, plus prefix caching and KV cache (M60).


# %% [markdown] color=peach title="9 · Checkpointing"
# # 9 · Checkpointing
#


# %% color=violet title="Save model + optimiser so you can resume training later"
# @explain: Save model + optimiser so you can resume training later
# @explain: Resume — example
# Save model + optimiser so you can resume training later
torch.save({
    "model_state_dict":      model.state_dict(),
    "optimizer_state_dict":  optimizer.state_dict(),
}, "/content/ckpt.pt")

# Resume — example
model2 = GPT(CFG).to(device)
opt2   = torch.optim.AdamW(model2.parameters(), lr=4e-4, weight_decay=0.1)
ck = torch.load("/content/ckpt.pt", map_location=device)
model2.load_state_dict(ck["model_state_dict"])
opt2.load_state_dict(ck["optimizer_state_dict"])
print("checkpoint reloaded; param count:", sum(p.numel() for p in model2.parameters()))


# %% [markdown] color=amber title="Two things you'll always save: the **model state…"
# # Two things you'll always save: the **model state…
#
# Two things you'll always save: the **model state dict** *and* the **optimiser state** (AdamW keeps momentum/variance — without it, your resumed training stutters).
#
# For real training also save: **scheduler state**, **RNG state**, the **step count**, and the **config dict**. Format your checkpoint name with the step so you can keep several.


# %% [markdown] color=rose title="10 · What real pretraining adds"
# # 10 · What real pretraining adds
#
# | Feature | What it does | When |
# |---|---|---|
# | **AdamW** (we used it) | decoupled weight decay → cleaner regularisation | always for LLMs |
# | **Linear warmup** | LR ramps up from 0 to peak over first ~1% of steps | always |
# | **Cosine LR decay** | peak → small over the rest of training | most LLMs |
# | **Grad-clipping** (`torch.nn.utils.clip_grad_norm_`) | clip gradient norm to e.g. 1.0; prevents loss spikes | always |
# …


# %% [markdown] color=lime title="Thanks"
# # End of Module
#
# Next module continues the roadmap.
# Source: https://github.com/kader-xai/data-science-roadmap


