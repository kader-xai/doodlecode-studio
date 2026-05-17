# doodlecode format-version: 2
# Auto-converted from module_63_bpe_tokenizer_from_scratch.ipynb
# Open with 📂 Open → press 🎬 Present.


# %% [markdown] color=rose title="Module 63 Bpe Tokenizer From Scratch"
# # Module 63 Bpe Tokenizer From Scratch
#
# A live walkthrough — one card per concept.
# Use → / ← to step through. Press 🎬 Present to begin.



# %% [markdown] color=sky title="Module 63 — BPE from Scratch"
# # Module 63 — BPE from Scratch
#
# > M55 *used* `tiktoken`'s GPT-2 BPE as a black box: encode/decode and done. This module **trains a BPE tokenizer** on a tiny corpus end-to-end so you understand what `tiktoken` actually computed at training time. Same algorithm, same outputs (modulo the corpus), 70-ish lines of pure Python.
#
# ### What you'll cover
# 1. Why subword tokenisation exists (recap from M55)
# 2. **Byte-level pre-tokenisation** — text → list of byte sequences
# 3. The BPE training algorithm in 4 steps
# …


# %% [markdown] color=mint title="1 · Why subword"
# # 1 · Why subword
#
# Recap from M55:
# - **Character-level** → tiny vocab (~256), but sequences become very long.
# - **Word-level** → short sequences, but vocab is huge and OOV explodes.
# - **Subword (BPE / WordPiece / Unigram)** → small vocab + **no OOV** (anything falls back to bytes or shorter pieces).
#
# **BPE** = Byte Pair Encoding. Start with bytes; repeatedly merge the most frequent adjacent pair into a new symbol; stop when the vocab hits a target size. Used by **GPT-2, GPT-3, GPT-4, Llama, Mistral, Qwen, DeepSeek, Gemma**. The dominant subword algorithm.


# %% [markdown] color=peach title="2 · Byte-level pre-tokenisation"
# # 2 · Byte-level pre-tokenisation
#


# %% color=violet title="Start with a tiny corpus"
# @explain: Start with a tiny corpus
# Start with a tiny corpus
text = ("low low low low low "
        "lower lower "
        "newest newest newest newest newest newest "
        "widest widest widest")
print(text)


# %% color=amber title="Pre-tokenisation: split on whitespace into 'words'"
# @explain: Pre-tokenisation: split on whitespace into 'words', then break each word into a tuple of bytes
# @explain: The end-of-word marker '</w>' lets us treat word boundaries as fixed
# Pre-tokenisation: split on whitespace into 'words', then break each word into a tuple of bytes.
# The end-of-word marker '</w>' lets us treat word boundaries as fixed.

def initial_words(text):
    words = {}
    for w in text.split():
        symbol_seq = tuple(list(w) + ["</w>"])
        words[symbol_seq] = words.get(symbol_seq, 0) + 1
    return words

vocab = initial_words(text)
print("words (with multiplicity):")
for s, c in vocab.items():
    print(f"  {' '.join(s)!r}  x{c}")


# %% [markdown] color=rose title="Three things this step buys us"
# # Three things this step buys us
#
# **Three things this step buys us.**
# - **Whitespace pre-split** — merges never cross word boundaries (GPT-2 uses a much richer pre-tokeniser; we keep it simple).
# - **`</w>` end-of-word marker** — distinguishes "the merged `est`" from "the suffix `-est`."
# - **Counts on tuples** — multiplicity matters when we count pair frequencies later.


# %% [markdown] color=lime title="3 · The BPE training algorithm"
# # 3 · The BPE training algorithm
#
# ```
# 1. Pre-tokenise: text → {word_tuple: count, ...}
# 2. Initialise alphabet = all unique symbols
# 3. Repeat until vocab size = TARGET:
#      a. Count every adjacent pair across the corpus, weighted by word count
#      b. Pick the most frequent pair (a, b)
# …


# %% [markdown] color=teal title="4 · `get_stats` — count adjacent pairs"
# # 4 · `get_stats` — count adjacent pairs
#


# %% color=sky title="from collections import defaultdict"
# @explain: Run this cell to see the output.
from collections import defaultdict

def get_stats(vocab):
    pairs = defaultdict(int)
    for symbols, count in vocab.items():
        for i in range(len(symbols) - 1):
            pairs[(symbols[i], symbols[i + 1])] += count
    return pairs

stats = get_stats(vocab)
for pair, cnt in sorted(stats.items(), key=lambda x: -x[1])[:8]:
    print(f"  {pair}  x{cnt}")


# %% [markdown] color=mint title="For each *type* of word (a tuple), we look at every…"
# # For each *type* of word (a tuple), we look at every…
#
# For each *type* of word (a tuple), we look at every adjacent symbol pair. We add the word's **multiplicity**, not 1 — that's how BPE learns frequent substrings.


# %% [markdown] color=peach title="5 · `merge` — apply one merge rule"
# # 5 · `merge` — apply one merge rule
#


# %% color=violet title="apply the most common pair once and see the corpus…"
# @explain: apply the most common pair once and see the corpus change
def merge(pair, vocab):
    """Replace every occurrence of `pair` in the corpus with the joined token."""
    a, b = pair
    joined = a + b
    new_vocab = {}
    for symbols, count in vocab.items():
        new_symbols = []
        i = 0
        while i < len(symbols):
            if i < len(symbols) - 1 and symbols[i] == a and symbols[i + 1] == b:
                new_symbols.append(joined); i += 2
            else:
                new_symbols.append(symbols[i]); i += 1
        new_vocab[tuple(new_symbols)] = count
    return new_vocab

# apply the most common pair once and see the corpus change
best = max(stats, key=stats.get)
print("merging:", best)
vocab2 = merge(best, vocab)
for s, c in vocab2.items():
    print(f"  {' '.join(s)!r}  x{c}")


# %% [markdown] color=amber title="6 · Train the tokenizer"
# # 6 · Train the tokenizer
#


# %% color=rose title="initial alphabet: every unique single symbol in the…"
# @explain: initial alphabet: every unique single symbol in the corpus
def train_bpe(text, target_vocab_size, verbose=True):
    vocab = initial_words(text)

    # initial alphabet: every unique single symbol in the corpus
    symbols = set()
    for word in vocab:
        symbols.update(word)

    merges = {}          # (a, b) -> rank
    rank = 0

    while len(symbols) + len(merges) < target_vocab_size:
        stats = get_stats(vocab)
        if not stats: break
        best = max(stats, key=stats.get)
        if stats[best] < 2: break          # nothing left to merge
        vocab = merge(best, vocab)
        merges[best] = rank
        symbols.add(best[0] + best[1])
        if verbose:
            print(f"merge #{rank:>3}: {best!s:>20}  freq={stats[best]:>3}")
        rank += 1

    return merges, symbols, vocab

merges, alphabet, final_vocab = train_bpe(text, target_vocab_size=18, verbose=True)
print()
print("alphabet size:", len(alphabet))
print("learned merges:", len(merges))
print("final vocab in corpus:")
for s, c in final_vocab.items():
    print(f"  {' '.join(s)!r}  x{c}")


# %% [markdown] color=lime title="Read the output.** Early merges combine…"
# # Read the output.** Early merges combine…
#
# **Read the output.** Early merges combine super-common pairs (`'e' + 'r'`, `'es' + 't'`). Later merges combine *those* into longer pieces (`'est' + '</w>'`). Each merge **rank** is permanent — `tiktoken`'s `merges.txt` is exactly this list, ordered.


# %% [markdown] color=teal title="7 · Encode — apply merges greedily by rank"
# # 7 · Encode — apply merges greedily by rank
#


# %% color=sky title="find every adjacent pair currently in `symbols`"
# @explain: find every adjacent pair currently in `symbols`
# @explain: the pair with the LOWEST rank merge is the one we apply
# @explain: apply that merge once across the symbols
def encode_word(word, merges):
    """Encode a single space-stripped word into a list of BPE tokens."""
    symbols = list(word) + ["</w>"]
    while True:
        # find every adjacent pair currently in `symbols`
        pairs = list(zip(symbols, symbols[1:]))
        if not pairs:
            break
        # the pair with the LOWEST rank merge is the one we apply
        ranked = [(merges.get(p, float("inf")), p) for p in pairs]
        rank, best_pair = min(ranked, key=lambda x: x[0])
        if rank == float("inf"):
            break    # no more known merges → stop
        # apply that merge once across the symbols
        new_symbols, i = [], 0
        a, b = best_pair
        while i < len(symbols):
            if i < len(symbols) - 1 and symbols[i] == a and symbols[i + 1] == b:
                new_symbols.append(a + b); i += 2
            else:
                new_symbols.append(symbols[i]); i += 1
        symbols = new_symbols
    return symbols

def encode(text, merges):
    tokens = []
    for w in text.split():
        tokens.extend(encode_word(w, merges))
    return tokens

for w in ["low", "lower", "newest", "lowest", "wide"]:
    print(f"{w!r:>10} → {encode_word(w, merges)}")


# %% [markdown] color=mint title="Two subtle points"
# # Two subtle points
#
# **Two subtle points.**
# - We **always pick the lowest-rank merge** that exists in our current symbol list. That makes encoding deterministic and reproducible.
# - If we hit a word with pieces we never saw (e.g. `"lowest"` — we trained on `low` and `lowest` was never explicit), the algorithm still works: it merges what it can and falls back to single bytes for the rest. **No `<unk>`.**


# %% [markdown] color=peach title="8 · Decode"
# # 8 · Decode
#


# %% color=violet title="def decode(tokens)"
# @explain: Run this cell to see the output.
def decode(tokens):
    text = "".join(tokens)
    return text.replace("</w>", " ").rstrip()

ids = encode("low lower newest", merges)
print("ids:", ids)
print("decoded:", repr(decode(ids)))


# %% [markdown] color=amber title="Decoding is trivial because every token is a string"
# # Decoding is trivial because every token is a string
#
# Decoding is trivial because every token is a string. Real implementations map (token_string → integer id) for storage; decode then goes (integer ids → token_strings → joined text).


# %% [markdown] color=rose title="9 · Compare with `tiktoken`"
# # 9 · Compare with `tiktoken`
#


# %% color=lime title="!pip -q install tiktoken"
# @explain: Run this cell to see the output.
!pip -q install tiktoken


# %% color=teal title="import tiktoken"
# @explain: Run this cell to see the output.
import tiktoken
tok = tiktoken.get_encoding("gpt2")

sample = "lower the newest test."
ours = encode(sample, merges)
their = [tok.decode([i]) for i in tok.encode(sample)]
print(f"ours  ({len(ours):>2}): {ours}")
print(f"gpt-2 ({len(their):>2}): {their}")


# %% [markdown] color=sky title="Different splits — because we trained on **4…"
# # Different splits — because we trained on **4…
#
# Different splits — because we trained on **4 sentences**, GPT-2 trained on **40 GB of web text**. Same algorithm; vastly different vocab. The shape of `tiktoken`'s output is what you'd get from running our trainer with `target_vocab_size=50 257` on a huge corpus.


# %% [markdown] color=mint title="10 · What real BPE adds"
# # 10 · What real BPE adds
#
# Toy BPE (this module) handles whitespace-separated words made of ASCII letters. Production BPE handles **everything** — emoji, code, languages without spaces, weird Unicode. Real implementations add:
#
# | Addition | Why |
# |---|---|
# | **Byte-level fallback** | every code-point first decomposes to UTF-8 *bytes* — guarantees full Unicode coverage with a 256-byte alphabet |
# | **Pre-tokeniser regex** | GPT-2's regex separates `'s 've 're 't` contractions, punctuation runs, digits, … |
# …


# %% [markdown] color=lime title="Thanks"
# # End of Module
#
# Next module continues the roadmap.
# Source: https://github.com/kader-xai/data-science-roadmap


