# doodlecode format-version: 2
# Auto-converted from module_58_classification_finetune.ipynb
# Open with 📂 Open → press 🎬 Present.


# %% [markdown] color=rose title="Module 58 Classification Finetune"
# # Module 58 Classification Finetune
#
# A live walkthrough — one card per concept.
# Use → / ← to step through. Press 🎬 Present to begin.



# %% [markdown] color=sky title="Module 58 — Classification Fine-Tune"
# # Module 58 — Classification Fine-Tune
#
# > M57 trained a GPT to *generate* text. Many production tasks don't want generation at all — they want a **label**: is this email spam? is this comment toxic? is this ticket urgent? **Classification fine-tuning** is a different beast from M39's chat-SFT or M59's instruction-SFT. The differences are small but load-bearing: you **replace the output head**, you **read the last token's logits**, and you **freeze most of the model**. This module walks the spam classifier from Raschka Ch 6.
#
# ### What you'll cover
# 1. Classification fine-tune vs instruction fine-tune — what changes
# 2. The SMS Spam dataset (`SpamCollection`) + **balanced undersampling**
# 3. **`SpamDataset`** — tokenize, pad to a fixed length, return `(ids, label)`
# …


# %% [markdown] color=mint title="1 · Classification fine-tune vs instruction fine-tune"
# # 1 · Classification fine-tune vs instruction fine-tune
#
# | | Instruction fine-tune (M39 / M59) | Classification fine-tune (this module) |
# |---|---|---|
# | Output | free-form text | a class id |
# | Loss | next-token cross-entropy over the *response* tokens | cross-entropy over **one** classification at the last token |
# | Head | the existing LM head over the full vocab | **swap** for a `Linear(emb_dim, num_classes)` |
# | Useful for | chat, agents, RAG | content moderation, intent, routing, sentiment, urgency |
# …


# %% [markdown] color=peach title="2 · Get + prepare the data"
# # 2 · Get + prepare the data
#


# %% color=violet title="!pip -q install tiktoken torch pandas matplotlib"
# @explain: Run this cell to see the output.
!pip -q install tiktoken torch pandas matplotlib


# %% color=amber title="UCI SMS Spam Collection"
# @explain: UCI SMS Spam Collection — 5,572 messages, label "ham" or "spam"
# UCI SMS Spam Collection — 5,572 messages, label "ham" or "spam"
import urllib.request, zipfile, io, pandas as pd, pathlib

URL = "https://archive.ics.uci.edu/static/public/228/sms+spam+collection.zip"
zpath = "/content/sms_spam_collection.zip"
if not pathlib.Path(zpath).exists():
    urllib.request.urlretrieve(URL, zpath)
with zipfile.ZipFile(zpath) as z:
    with z.open("SMSSpamCollection") as f:
        df = pd.read_csv(f, sep="\t", header=None, names=["label","text"])
print(df.head()); print("class balance:\n", df["label"].value_counts())


# %% color=rose title="Balanced undersample: same number of ham as spam"
# @explain: Balanced undersample: same number of ham as spam, so accuracy is meaningful
# @explain: 70 / 10 / 20 train / val / test split
# Balanced undersample: same number of ham as spam, so accuracy is meaningful
spam = df[df["label"]=="spam"]
ham  = df[df["label"]=="ham"].sample(n=len(spam), random_state=123)
balanced = pd.concat([spam, ham]).sample(frac=1.0, random_state=123).reset_index(drop=True)
balanced["label"] = balanced["label"].map({"ham":0, "spam":1})

# 70 / 10 / 20 train / val / test split
n = len(balanced)
n_tr, n_va = int(0.7*n), int(0.1*n)
train_df = balanced.iloc[:n_tr]
val_df   = balanced.iloc[n_tr:n_tr+n_va]
test_df  = balanced.iloc[n_tr+n_va:]
print(len(train_df), len(val_df), len(test_df))


# %% [markdown] color=lime title="Why balanced.** The raw dataset is ~87% ham, ~13% spam"
# # Why balanced.** The raw dataset is ~87% ham, ~13% spam
#
# **Why balanced.** The raw dataset is ~87% ham, ~13% spam. A model that always predicts "ham" gets 87% accuracy and learns nothing. Balanced undersampling forces the model to look at the text. The trade-off is throwing away ham data, but for a classifier with thousands of rows it's the right call.


# %% [markdown] color=teal title="3 · `SpamDataset` — tokenize, pad, return `(ids, label)`"
# # 3 · `SpamDataset` — tokenize, pad, return `(ids, label)`
#


# %% color=sky title="cap to the longest train example"
# @explain: cap to the longest train example (so we can pad shorter ones)
# @explain: truncate longer; pad shorter to max_length
import torch, tiktoken
from torch.utils.data import Dataset, DataLoader

class SpamDataset(Dataset):
    def __init__(self, df, tokenizer, max_length=None, pad_id=50256):
        self.encoded = [tokenizer.encode(t) for t in df["text"]]
        # cap to the longest train example (so we can pad shorter ones)
        if max_length is None:
            max_length = max(len(x) for x in self.encoded)
        self.max_length = max_length
        self.pad_id = pad_id
        # truncate longer; pad shorter to max_length
        self.encoded = [(ids[:max_length] + [pad_id] * (max_length - len(ids)))[:max_length]
                        for ids in self.encoded]
        self.labels = df["label"].tolist()

    def __len__(self): return len(self.encoded)

    def __getitem__(self, idx):
        return torch.tensor(self.encoded[idx]), torch.tensor(self.labels[idx])

tok = tiktoken.get_encoding("gpt2")
train_ds = SpamDataset(train_df, tok)
val_ds   = SpamDataset(val_df,   tok, max_length=train_ds.max_length)
test_ds  = SpamDataset(test_df,  tok, max_length=train_ds.max_length)
print("max_length:", train_ds.max_length)
print(train_ds[0][0][:20], "label:", train_ds[0][1].item())


# %% color=mint title="train_loader = DataLoader(train_ds"
# @explain: Run this cell to see the output.
train_loader = DataLoader(train_ds, batch_size=8, shuffle=True,  drop_last=True)
val_loader   = DataLoader(val_ds,   batch_size=8, shuffle=False, drop_last=False)
test_loader  = DataLoader(test_ds,  batch_size=8, shuffle=False, drop_last=False)
x, y = next(iter(train_loader))
print("batch shape:", x.shape, "label shape:", y.shape)


# %% [markdown] color=peach title="Two design choices to notice"
# # Two design choices to notice
#
# **Two design choices to notice.**
# 1. **Fixed-length padding** (with the GPT-2 EOT id 50256). Real LLM SFT uses *dynamic* per-batch padding + an `attention_mask` (we'll see that in M59). For classification, fixed-length is fine and simpler.
# 2. **Cap to the longest training example.** This means the val/test sets reuse the same length — no padding-vs-truncation drift.


# %% [markdown] color=violet title="4 · Load the pretrained GPT-2 from M56"
# # 4 · Load the pretrained GPT-2 from M56
#
# For the notebook to stand alone we'll use a small from-scratch GPT (same as M57). In real life you'd `load_weights_into_gpt` from M56 first — that's the whole point of starting from a pretrained model.


# %% color=amber title="import torch.nn as nn"
# @explain: Run this cell to see the output.
import torch.nn as nn

class LayerNorm(nn.Module):
    def __init__(self,d):
        super().__init__(); self.eps=1e-5
        self.s=nn.Parameter(torch.ones(d)); self.b=nn.Parameter(torch.zeros(d))
    def forward(self,x):
        m=x.mean(-1,keepdim=True); v=x.var(-1,keepdim=True,unbiased=False)
        return self.s*(x-m)/torch.sqrt(v+self.eps)+self.b

class GELU(nn.Module):
    def forward(self,x): return 0.5*x*(1+torch.tanh(torch.sqrt(torch.tensor(2/torch.pi))*(x+0.044715*x**3)))

class MHA(nn.Module):
    def __init__(self,d,ctx,h,drop,bias):
        super().__init__(); self.h=h; self.hd=d//h; self.d=d
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
        self.out_head=nn.Linear(cfg["emb_dim"], cfg["vocab_size"], bias=False)
        self.out_head.weight = self.te.weight
    def forward(self,idx):
        b,T=idx.shape
        x=self.te(idx)+self.pe(torch.arange(T,device=idx.device))
        x=self.dp(x)
        return self.out_head(self.fn(self.blocks(x)))

CFG = {"vocab_size":50257, "context_length":max(120, train_ds.max_length),
       "emb_dim":128, "n_heads":4, "n_layers":4, "drop_rate":0.1, "qkv_bias":True}
torch.manual_seed(123)
model = GPT(CFG)
print(f"params: {sum(p.numel() for p in model.parameters()):,}")


# %% [markdown] color=rose title="5 · Swap the output head"
# # 5 · Swap the output head
#


# %% color=lime title="The model's LM head outputs over vocab_size (50257)"
# @explain: The model's LM head outputs over vocab_size (50257)
# The model's LM head outputs over vocab_size (50257). Replace it with a 2-way head.
NUM_CLASSES = 2
model.out_head = nn.Linear(in_features=CFG["emb_dim"],
                            out_features=NUM_CLASSES)
print(model.out_head)


# %% [markdown] color=teal title="That's literally the whole change to the…"
# # That's literally the whole change to the…
#
# **That's literally the whole change to the architecture.** Same body, new tiny head. The new `out_head` is **untied** (its weights are fresh — they had nothing to do with the LM embedding) and **trainable** (no `requires_grad=False`).
#
# If you wanted *N* classes (say spam / promo / legit / urgent) you'd swap `out_features=N`. Everything else is the same.


# %% [markdown] color=sky title="6 · Selective freezing — train only the head + last block + final LN"
# # 6 · Selective freezing — train only the head + last block + final LN
#


# %% color=mint title="Freeze ALL parameters first"
# @explain: Freeze ALL parameters first
# @explain: Then UNFREEZE: final LN, the last transformer block, and the new head
# Freeze ALL parameters first
for p in model.parameters():
    p.requires_grad = False

# Then UNFREEZE: final LN, the last transformer block, and the new head
for p in model.fn.parameters():           p.requires_grad = True
for p in model.blocks[-1].parameters():   p.requires_grad = True
for p in model.out_head.parameters():     p.requires_grad = True

trainable = sum(p.numel() for p in model.parameters() if p.requires_grad)
total     = sum(p.numel() for p in model.parameters())
print(f"trainable: {trainable:,} / {total:,}  ({100*trainable/total:.1f}%)")


# %% [markdown] color=peach title="Why partial freezing wins"
# # Why partial freezing wins
#
# **Why partial freezing wins.**
# - Fine-tuning the whole model burns memory + time and *overfits* a small classification corpus.
# - The bottom layers of GPT learn generic features (token co-occurrence, syntax) that are already useful for spam. Don't touch them.
# - The **top block + new head** are where task-specific adaptation happens.
# - This is **functionally LoRA-without-LoRA** — it gets you most of the benefit (small trainable set, fast, doesn't catastrophically forget) without adding the LoRA machinery.


# %% [markdown] color=violet title="7 · Read the **last-token** logits"
# # 7 · Read the **last-token** logits
#


# %% color=amber title="When you classify a sentence with a causal LM"
# @explain: When you classify a sentence with a causal LM, you ALWAYS read the last position
# @explain: Why: with a causal mask, only position t can see positions ≤ t — only the LAST token
# @explain: has "seen" the whole sequence
# When you classify a sentence with a causal LM, you ALWAYS read the last position.
# Why: with a causal mask, only position t can see positions ≤ t — only the LAST token
# has "seen" the whole sequence. So its hidden state summarises the message.

inputs = train_ds[0][0].unsqueeze(0)        # (1, T)
with torch.no_grad():
    logits = model(inputs)                  # (1, T, 2)
print("logits over all positions:", logits.shape)
print("last-token logits:", logits[:, -1, :])   # → (1, 2)
print("predicted class :", logits[:, -1, :].argmax(dim=-1).item())


# %% [markdown] color=rose title="The non-obvious bit.** Beginners sometimes pool…"
# # The non-obvious bit.** Beginners sometimes pool…
#
# **The non-obvious bit.** Beginners sometimes pool *all* positions (mean / max-pool). Causal-LM classification works *better* with just the last position because the model is *already* causal — the last token's hidden state has been computed from every preceding token. Pooling earlier positions wastes information (they couldn't see the rest of the message).
#
# (BERT-style encoder classifiers use the `[CLS]` token at position 0 instead — same idea, flipped.)


# %% [markdown] color=lime title="8 · Loss + accuracy helpers"
# # 8 · Loss + accuracy helpers
#


# %% color=teal title="def calc_loss_batch(x"
# @explain: Run this cell to see the output.
def calc_loss_batch(x, y, model, device):
    x, y = x.to(device), y.to(device)
    logits = model(x)[:, -1, :]                # (B, 2)
    return torch.nn.functional.cross_entropy(logits, y)

def calc_loss_loader(loader, model, device, num_batches=None):
    total, n = 0.0, 0
    if num_batches is None: num_batches = len(loader)
    for i, (x, y) in enumerate(loader):
        if i >= num_batches: break
        total += calc_loss_batch(x, y, model, device).item()
        n += 1
    return total / max(n, 1)

def calc_accuracy_loader(loader, model, device, num_batches=None):
    model.eval()
    correct, n = 0, 0
    if num_batches is None: num_batches = len(loader)
    with torch.no_grad():
        for i, (x, y) in enumerate(loader):
            if i >= num_batches: break
            x, y = x.to(device), y.to(device)
            preds = model(x)[:, -1, :].argmax(dim=-1)
            correct += (preds == y).sum().item()
            n += y.numel()
    return correct / max(n, 1)


# %% [markdown] color=sky title="Notice the **only difference from M57's pretraining…"
# # Notice the **only difference from M57's pretraining…
#
# Notice the **only difference from M57's pretraining loss** is `model(x)[:, -1, :]` — that single slice tells PyTorch *"classify on the last position."* Everything else is vanilla CE.


# %% [markdown] color=mint title="9 · Train + plot"
# # 9 · Train + plot
#


# %% color=peach title="device = 'cuda' if torch.cuda.is_available() else 'cpu'"
# @explain: Run this cell to see the output.
device = "cuda" if torch.cuda.is_available() else "cpu"
model.to(device)
optimizer = torch.optim.AdamW(filter(lambda p: p.requires_grad, model.parameters()),
                              lr=5e-5, weight_decay=0.1)

train_losses, val_losses, train_accs, val_accs = [], [], [], []

for epoch in range(2):                          # tiny demo budget
    model.train()
    for x, y in train_loader:
        optimizer.zero_grad()
        loss = calc_loss_batch(x, y, model, device)
        loss.backward()
        optimizer.step()
    tl = calc_loss_loader(train_loader, model, device, num_batches=5)
    vl = calc_loss_loader(val_loader,   model, device, num_batches=5)
    ta = calc_accuracy_loader(train_loader, model, device, num_batches=5)
    va = calc_accuracy_loader(val_loader,   model, device, num_batches=5)
    train_losses.append(tl); val_losses.append(vl)
    train_accs.append(ta);   val_accs.append(va)
    print(f"ep{epoch+1}  train_loss={tl:.3f} val_loss={vl:.3f}  train_acc={ta:.2%} val_acc={va:.2%}")


# %% color=violet title="import matplotlib.pyplot as plt"
# @explain: Run this cell to see the output.
import matplotlib.pyplot as plt
fig, axes = plt.subplots(1, 2, figsize=(10, 3.4))
axes[0].plot(train_losses, label="train"); axes[0].plot(val_losses, label="val")
axes[0].set_title("loss"); axes[0].legend()
axes[1].plot(train_accs, label="train"); axes[1].plot(val_accs, label="val")
axes[1].set_title("accuracy"); axes[1].set_ylim(0,1.05); axes[1].legend()
plt.tight_layout(); plt.show()


# %% [markdown] color=amber title="On the real Raschka run (full GPT-2 124M as the…"
# # On the real Raschka run (full GPT-2 124M as the…
#
# On the real Raschka run (full GPT-2 124M as the base, 6+ epochs) this gets to **96–97% test accuracy** — competitive with a from-scratch BERT on the same data, but you reuse the same checkpoint as your generative model. With our tiny demo model the absolute numbers will be lower, but the *shape* of the curves is identical.


# %% [markdown] color=rose title="10 · `classify_review` — production inference"
# # 10 · `classify_review` — production inference
#


# %% color=lime title="def classify_review(text"
# @explain: Run this cell to see the output.
def classify_review(text, model, tokenizer, device, max_length, pad_id=50256):
    ids = tokenizer.encode(text)[:max_length]
    ids = ids + [pad_id] * (max_length - len(ids))
    x = torch.tensor(ids).unsqueeze(0).to(device)
    model.eval()
    with torch.no_grad():
        logits = model(x)[:, -1, :]
        pred = logits.argmax(dim=-1).item()
    return "spam" if pred == 1 else "ham"

for sample in [
    "You are a winner! WIN $1000 cash NOW. Click http://shady.url",
    "hey are we still on for coffee at 4?",
    "URGENT! Your account has been suspended, verify here",
]:
    print(f"{classify_review(sample, model, tok, device, train_ds.max_length):>4} | {sample[:60]}")


# %% [markdown] color=teal title="When to use this vs. an LLM tool call"
# # When to use this vs. an LLM tool call
#
# | Use a classification fine-tune | Use an LLM tool / prompt |
# |---|---|
# | High-volume, latency-sensitive (>100 QPS) | low-volume, batchy |
# | Stable class set | classes change weekly |
# | You have labelled data | you don't |
# | Need explainability via embedding probes | you can live with "the model said so" |
# …


# %% [markdown] color=sky title="✅ Recap"
# # ✅ Recap
#
# - Classification fine-tune = **swap the head + read the last token's logits**. Everything else is vanilla CE.
# - **Balanced undersampling** stops the model from cheating on imbalanced data.
# - **Selective freezing** (head + final LN + last block) ≈ LoRA-without-LoRA — fast, doesn't overfit.
# - **`model(x)[:, -1, :]`** is the one-liner that turns a causal LM into a classifier.
# - Two-class CE on the last token; `argmax` for inference.
# - Pair with prompt-based LLMs in the production stack: classifiers for the fast path, LLMs for the tail.
#
# …


# %% [markdown] color=lime title="Thanks"
# # End of Module
#
# Next module continues the roadmap.
# Source: https://github.com/kader-xai/data-science-roadmap


