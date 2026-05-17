# doodlecode format-version: 2
# Auto-converted from module_18_six_core_models.ipynb
# Open with 📂 Open → press 🎬 Present.


# %% [markdown] color=rose title="Module 18 Six Core Models"
# # Module 18 Six Core Models
#
# A live walkthrough — one card per concept.
# Use → / ← to step through. Press 🎬 Present to begin.



# %% [markdown] color=sky title="Six Core Models — End-to-End in One Notebook"
# # Six Core Models — End-to-End in One Notebook
#
# **Companion to the AI Explainer video series.**
#
# This notebook walks through six foundational models in machine-learning history, each with the **full pipeline** — load data → define model → train → evaluate → visualize. Every dataset is open and downloads in-notebook. Total runtime ≈ 10 min on free Colab CPU (≈ 2 min on T4 GPU).
#
# | # | Model | Dataset | What it shows |
# |---|-------|---------|---------------|
# …


# %% [markdown] color=mint title="0 · Setup"
# # 0 · Setup
#
# Most packages are pre-installed on Colab; we just import what we need. PyTorch and torchvision come pre-installed.


# %% color=peach title="import os"
# @explain: Run this cell to see the output.
import os, time, math, urllib.request
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt

import sklearn
from sklearn.datasets import fetch_california_housing, load_breast_cancer, load_iris
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import StandardScaler
from sklearn.linear_model import LinearRegression, LogisticRegression
from sklearn.cluster import KMeans
from sklearn.decomposition import PCA
from sklearn.metrics import (
    mean_squared_error, mean_absolute_error, r2_score,
    accuracy_score, precision_score, recall_score, f1_score,
    confusion_matrix, classification_report, roc_curve, roc_auc_score,
    silhouette_score, adjusted_rand_score,
)

import torch
import torch.nn as nn
import torch.nn.functional as F
from torch.utils.data import DataLoader
from torchvision import datasets, transforms

DEVICE = 'cuda' if torch.cuda.is_available() else 'cpu'
torch.manual_seed(42); np.random.seed(42)
print(f'sklearn {sklearn.__version__}  ·  torch {torch.__version__}  ·  device = {DEVICE}')


# %% [markdown] color=violet title="1 · Linear Regression"
# # 1 · Linear Regression
#
# ---
# # 1 · Linear Regression
#
# **Goal.** Predict a *continuous* target — California median house value — from features like income, house age, rooms-per-household, latitude/longitude.
#
# **Model.** A linear function $\hat{y} = w \cdot x + b$. Training finds $w, b$ that minimize **mean squared error** (MSE) on the training set.
#
# **Why it's first.** Every neural network is, at heart, a stack of linear layers with non-linearities between them. Understand this and the rest is layered repetition.


# %% color=amber title="1a · Load California Housing"
# @explain: 1a · Load California Housing
# 1a · Load California Housing
cal = fetch_california_housing(as_frame=True)
X, y = cal.data, cal.target
print(f'shape: X={X.shape}  y={y.shape}')
print(f'features: {list(X.columns)}')
X.head()


# %% color=rose title="1b · Train / test split + standardize"
# @explain: 1b · Train / test split + standardize
# @explain: 1c · Fit
# @explain: 1d · Evaluate
# @explain: Coefficients tell us which features matter
# 1b · Train / test split + standardize
Xtr, Xte, ytr, yte = train_test_split(X, y, test_size=0.2, random_state=42)

scaler = StandardScaler().fit(Xtr)
Xtr_s = scaler.transform(Xtr)
Xte_s = scaler.transform(Xte)

# 1c · Fit
lin = LinearRegression().fit(Xtr_s, ytr)

# 1d · Evaluate
yhat_tr = lin.predict(Xtr_s)
yhat_te = lin.predict(Xte_s)

print('TRAIN  MSE = {:.3f}   RMSE = {:.3f}   R² = {:.3f}'.format(
    mean_squared_error(ytr, yhat_tr),
    np.sqrt(mean_squared_error(ytr, yhat_tr)),
    r2_score(ytr, yhat_tr)))
print('TEST   MSE = {:.3f}   RMSE = {:.3f}   R² = {:.3f}'.format(
    mean_squared_error(yte, yhat_te),
    np.sqrt(mean_squared_error(yte, yhat_te)),
    r2_score(yte, yhat_te)))

# Coefficients tell us which features matter
coefs = pd.Series(lin.coef_, index=X.columns).sort_values()
print('\nLearned weights (standardized):')
print(coefs.to_string())


# %% color=lime title="1e · Visualize"
# @explain: 1e · Visualize
# @explain: Predicted vs actual
# @explain: Residuals
# 1e · Visualize
fig, axes = plt.subplots(1, 2, figsize=(12, 4))

# Predicted vs actual
axes[0].scatter(yte, yhat_te, s=8, alpha=0.4)
lim = [yte.min(), yte.max()]
axes[0].plot(lim, lim, 'r--', lw=1.5, label='perfect')
axes[0].set_xlabel('actual house value')
axes[0].set_ylabel('predicted')
axes[0].set_title(f'Predicted vs Actual (R² = {r2_score(yte, yhat_te):.3f})')
axes[0].legend()

# Residuals
residuals = yte - yhat_te
axes[1].hist(residuals, bins=40, color='steelblue', edgecolor='white')
axes[1].axvline(0, color='red', ls='--')
axes[1].set_title(f'Residuals  (mean = {residuals.mean():.3f})')
axes[1].set_xlabel('y_true - y_pred')
plt.tight_layout(); plt.show()


# %% [markdown] color=teal title="Interpretation.** R² ≈ 0.6 means the model explains…"
# # Interpretation.** R² ≈ 0.6 means the model explains…
#
# **Interpretation.** R² ≈ 0.6 means the model explains ~60% of the variance in house prices using only 8 features and a *straight line*. The residual histogram is roughly bell-shaped around zero — what we want. Heavy tails on the right say the model under-predicts the most expensive homes (linear models can't capture exponential luxury markets).
#
# **Limit of this model.** A line. To capture non-linear patterns we need… (sections 4–6).


# %% [markdown] color=sky title="2 · Logistic Regression — Binary Classification"
# # 2 · Logistic Regression — Binary Classification
#
# ---
# # 2 · Logistic Regression — Binary Classification
#
# **Goal.** Predict a *category*: from 30 cell-nucleus measurements, decide if a tumor is benign (1) or malignant (0).
#
# **Model.** Logistic regression — a linear combination passed through a sigmoid:  $p(y=1\,|\,x) = \sigma(w \cdot x + b)$. Trained by **cross-entropy** loss.
#
# **Why it matters.** Most real-world ML in production (spam filters, churn prediction, fraud) is a logistic-regression head sitting on top of engineered features — not a neural net.


# %% color=mint title="2a · Load Breast Cancer"
# @explain: 2a · Load Breast Cancer
# 2a · Load Breast Cancer
bc = load_breast_cancer(as_frame=True)
Xc, yc = bc.data, bc.target
print(f'shape: X={Xc.shape}  y={yc.shape}')
print(f'classes: {dict(zip(bc.target_names, np.bincount(yc)))}')
Xc.head()


# %% color=peach title="2b · Split + scale"
# @explain: 2b · Split + scale
# @explain: 2c · Fit
# @explain: 2d · Predict + evaluate
# 2b · Split + scale
Xtr, Xte, ytr, yte = train_test_split(Xc, yc, test_size=0.2, stratify=yc, random_state=42)
scaler = StandardScaler().fit(Xtr)
Xtr_s = scaler.transform(Xtr); Xte_s = scaler.transform(Xte)

# 2c · Fit
clf = LogisticRegression(max_iter=2000, C=1.0).fit(Xtr_s, ytr)

# 2d · Predict + evaluate
yhat = clf.predict(Xte_s)
yprob = clf.predict_proba(Xte_s)[:, 1]

print(f'Accuracy : {accuracy_score(yte, yhat):.4f}')
print(f'Precision: {precision_score(yte, yhat):.4f}')
print(f'Recall   : {recall_score(yte, yhat):.4f}')
print(f'F1       : {f1_score(yte, yhat):.4f}')
print(f'AUC      : {roc_auc_score(yte, yprob):.4f}')
print()
print(classification_report(yte, yhat, target_names=bc.target_names))


# %% color=violet title="2e · Visualize: confusion matrix + ROC"
# @explain: 2e · Visualize: confusion matrix + ROC
# 2e · Visualize: confusion matrix + ROC
fig, axes = plt.subplots(1, 2, figsize=(12, 4.5))

cm = confusion_matrix(yte, yhat)
axes[0].imshow(cm, cmap='Blues')
for i in range(2):
    for j in range(2):
        axes[0].text(j, i, cm[i, j], ha='center', va='center',
                     color='white' if cm[i, j] > cm.max() / 2 else 'black', fontsize=14)
axes[0].set_xticks([0, 1]); axes[0].set_yticks([0, 1])
axes[0].set_xticklabels(bc.target_names); axes[0].set_yticklabels(bc.target_names)
axes[0].set_xlabel('predicted'); axes[0].set_ylabel('actual')
axes[0].set_title('Confusion matrix')

fpr, tpr, _ = roc_curve(yte, yprob)
axes[1].plot(fpr, tpr, lw=2, label=f'AUC = {roc_auc_score(yte, yprob):.3f}')
axes[1].plot([0, 1], [0, 1], 'r--', lw=1)
axes[1].set_xlabel('false positive rate'); axes[1].set_ylabel('true positive rate')
axes[1].set_title('ROC curve'); axes[1].legend()
plt.tight_layout(); plt.show()


# %% [markdown] color=amber title="Interpretation.** A simple linear classifier with…"
# # Interpretation.** A simple linear classifier with…
#
# **Interpretation.** A simple linear classifier with one sigmoid hits >97% accuracy on a clinically meaningful task. The confusion matrix shows where it errs — those are the cases that warrant a second look. AUC ≈ 0.99 means the model's *ranking* of malignancy probabilities is nearly perfect.
#
# **The two metrics that matter most here:** *recall* on malignant (don't miss cancer) and *precision* on malignant (don't trigger unnecessary biopsies). In practice you'd pick the decision threshold on the ROC curve based on which kind of mistake costs more.


# %% [markdown] color=rose title="3 · K-Means — Unsupervised Clustering"
# # 3 · K-Means — Unsupervised Clustering
#
# ---
# # 3 · K-Means — Unsupervised Clustering
#
# **Goal.** Group flowers into clusters using only their measurements (sepal/petal length & width). We'll *drop the labels* and ask the algorithm to discover the species on its own — then check how well its groupings match the truth.
#
# **Model.** K-Means iteratively does two things:
# 1. Assign each point to its nearest centroid.
# 2. Move each centroid to the mean of its assigned points.
# …


# %% color=lime title="3a · Load Iris and DROP the labels"
# @explain: 3a · Load Iris and DROP the labels (unsupervised)
# @explain: Standardize
# 3a · Load Iris and DROP the labels (unsupervised)
iris = load_iris()
X = iris.data
y_true = iris.target  # held aside ONLY for post-hoc evaluation
print(f'X shape: {X.shape}  (we\'re pretending we don\'t have y)')

# Standardize
X_s = StandardScaler().fit_transform(X)


# %% color=teal title="3b · How do we pick k?  →  ELBOW METHOD + SILHOUETTE"
# @explain: 3b · How do we pick k?  →  ELBOW METHOD + SILHOUETTE
# 3b · How do we pick k?  →  ELBOW METHOD + SILHOUETTE
ks = range(2, 8)
inertias, sils = [], []
for k in ks:
    km = KMeans(n_clusters=k, n_init=10, random_state=42).fit(X_s)
    inertias.append(km.inertia_)
    sils.append(silhouette_score(X_s, km.labels_))

fig, axes = plt.subplots(1, 2, figsize=(12, 4))
axes[0].plot(ks, inertias, 'o-'); axes[0].set_xlabel('k'); axes[0].set_ylabel('inertia (within-cluster sum-sq)')
axes[0].set_title('Elbow method')
axes[1].plot(ks, sils, 'o-', color='green')
axes[1].set_xlabel('k'); axes[1].set_ylabel('silhouette score (-1 → +1)')
axes[1].set_title('Silhouette score')
plt.tight_layout(); plt.show()


# %% color=sky title="3c · Pick k = 3"
# @explain: 3c · Pick k = 3 (matches the elbow + we know there are 3 species)
# @explain: How well do the discovered clusters align with actual species?
# 3c · Pick k = 3 (matches the elbow + we know there are 3 species)
k = 3
km = KMeans(n_clusters=k, n_init=10, random_state=42).fit(X_s)
labels = km.labels_

print(f'Inertia        : {km.inertia_:.2f}')
print(f'Silhouette     : {silhouette_score(X_s, labels):.3f}')
print(f'Adjusted Rand  : {adjusted_rand_score(y_true, labels):.3f}   (vs true species)')

# How well do the discovered clusters align with actual species?
print('\nCluster ↔ species cross-tab:')
print(pd.crosstab(
    pd.Series(labels, name='cluster'),
    pd.Series(iris.target_names[y_true], name='actual species')
))


# %% color=mint title="3d · Visualize in 2D via PCA"
# @explain: 3d · Visualize in 2D via PCA
# 3d · Visualize in 2D via PCA
pca = PCA(n_components=2)
X2 = pca.fit_transform(X_s)
centroids2 = pca.transform(km.cluster_centers_)

fig, axes = plt.subplots(1, 2, figsize=(12, 4.5))

for c in range(k):
    m = labels == c
    axes[0].scatter(X2[m, 0], X2[m, 1], s=30, label=f'cluster {c}')
axes[0].scatter(centroids2[:, 0], centroids2[:, 1],
                marker='X', s=200, c='black', label='centroids')
axes[0].set_title('K-Means clusters (no labels)'); axes[0].legend()

for c in range(3):
    m = y_true == c
    axes[1].scatter(X2[m, 0], X2[m, 1], s=30, label=iris.target_names[c])
axes[1].set_title('True species (held-out)'); axes[1].legend()

for ax in axes:
    ax.set_xlabel('PC1'); ax.set_ylabel('PC2')
plt.tight_layout(); plt.show()


# %% [markdown] color=peach title="Interpretation.** With no labels at all, k-means…"
# # Interpretation.** With no labels at all, k-means…
#
# **Interpretation.** With no labels at all, k-means recovers the three species correctly for ≈90% of flowers — Adjusted Rand Index ≈ 0.62 (1.0 = perfect, 0 = random). The setosa cluster separates cleanly; versicolor / virginica overlap a bit, just like in nature. That's the whole pitch of unsupervised learning: structure that was already in the data, surfaced for free.


# %% [markdown] color=violet title="4 · MLP — Multi-Layer Perceptron on Fashion-MNIST"
# # 4 · MLP — Multi-Layer Perceptron on Fashion-MNIST
#
# ---
# # 4 · MLP — Multi-Layer Perceptron on Fashion-MNIST
#
# **Goal.** Classify 28×28 grayscale clothing images into 10 categories (T-shirt, trouser, pullover, dress, coat, sandal, shirt, sneaker, bag, ankle-boot).
#
# **Model.** A flat MLP — flatten the image to 784 numbers, push through 2 hidden layers with ReLU, output 10 logits. Trained with **cross-entropy** loss and **Adam**.
#
# **Why this dataset.** Same data goes into the CNN in Section 5 → you'll see the accuracy lift directly.


# %% color=amber title="4a · Load Fashion-MNIST"
# @explain: 4a · Load Fashion-MNIST (downloads ~30 MB on first run)
# @explain: Peek
# 4a · Load Fashion-MNIST (downloads ~30 MB on first run)
tx = transforms.Compose([transforms.ToTensor()])
train_ds = datasets.FashionMNIST(root='./data', train=True,  download=True, transform=tx)
test_ds  = datasets.FashionMNIST(root='./data', train=False, download=True, transform=tx)

CLASS_NAMES = ['T-shirt', 'Trouser', 'Pullover', 'Dress', 'Coat',
               'Sandal', 'Shirt', 'Sneaker', 'Bag', 'Boot']
print(f'train: {len(train_ds)}   test: {len(test_ds)}   image: {train_ds[0][0].shape}')

# Peek
fig, axes = plt.subplots(1, 8, figsize=(12, 2))
for ax, (img, lbl) in zip(axes, train_ds):
    ax.imshow(img.squeeze(), cmap='gray'); ax.set_title(CLASS_NAMES[lbl]); ax.axis('off')
plt.tight_layout(); plt.show()


# %% color=rose title="4b · Define the MLP"
# @explain: 4b · Define the MLP
# 4b · Define the MLP
class MLP(nn.Module):
    def __init__(self):
        super().__init__()
        self.net = nn.Sequential(
            nn.Flatten(),
            nn.Linear(28 * 28, 256), nn.ReLU(),
            nn.Linear(256, 128),     nn.ReLU(),
            nn.Linear(128, 10),  # 10 logits
        )
    def forward(self, x): return self.net(x)

mlp = MLP().to(DEVICE)
n_params = sum(p.numel() for p in mlp.parameters())
print(mlp); print(f'\nparameters: {n_params:,}')


# %% color=lime title="4c · Training loop"
# @explain: 4c · Training loop
# 4c · Training loop
train_loader = DataLoader(train_ds, batch_size=256, shuffle=True)
test_loader  = DataLoader(test_ds,  batch_size=512)

opt = torch.optim.Adam(mlp.parameters(), lr=1e-3)
loss_fn = nn.CrossEntropyLoss()
EPOCHS = 3

def evaluate(model, loader):
    model.eval()
    correct = total = 0
    with torch.no_grad():
        for xb, yb in loader:
            xb, yb = xb.to(DEVICE), yb.to(DEVICE)
            preds = model(xb).argmax(1)
            correct += (preds == yb).sum().item(); total += yb.size(0)
    return correct / total

history = {'train_loss': [], 'test_acc': []}
t0 = time.time()
for ep in range(EPOCHS):
    mlp.train(); running = 0; n = 0
    for xb, yb in train_loader:
        xb, yb = xb.to(DEVICE), yb.to(DEVICE)
        opt.zero_grad()
        loss = loss_fn(mlp(xb), yb)
        loss.backward(); opt.step()
        running += loss.item() * yb.size(0); n += yb.size(0)
    tr_loss = running / n
    te_acc = evaluate(mlp, test_loader)
    history['train_loss'].append(tr_loss); history['test_acc'].append(te_acc)
    print(f'epoch {ep+1}/{EPOCHS}   train_loss={tr_loss:.4f}   test_acc={te_acc:.4f}')
print(f'\nTrained in {time.time() - t0:.1f}s')


# %% color=teal title="4d · Visualize training + sample predictions"
# @explain: 4d · Visualize training + sample predictions
# @explain: Sample predictions
# 4d · Visualize training + sample predictions
mlp_test_acc = history['test_acc'][-1]

fig, axes = plt.subplots(1, 2, figsize=(12, 4))
axes[0].plot(history['train_loss'], 'o-'); axes[0].set_title('Train loss'); axes[0].set_xlabel('epoch')
axes[1].plot(history['test_acc'], 'o-', color='green'); axes[1].set_title(f'Test accuracy (final = {mlp_test_acc:.3f})')
axes[1].set_xlabel('epoch')
plt.tight_layout(); plt.show()

# Sample predictions
mlp.eval()
fig, axes = plt.subplots(2, 8, figsize=(14, 4))
with torch.no_grad():
    for i, ax in enumerate(axes.flat):
        img, true = test_ds[i]
        pred = mlp(img.unsqueeze(0).to(DEVICE)).argmax(1).item()
        ax.imshow(img.squeeze(), cmap='gray'); ax.axis('off')
        ok = pred == true
        ax.set_title(f'{CLASS_NAMES[pred]}\n{"" if ok else "≠ " + CLASS_NAMES[true]}',
                     color='green' if ok else 'red', fontsize=9)
plt.tight_layout(); plt.show()


# %% [markdown] color=sky title="Interpretation.** ~88% test accuracy on a…"
# # Interpretation.** ~88% test accuracy on a…
#
# **Interpretation.** ~88% test accuracy on a non-trivial 10-class image task with no convolutions — just stacked linear layers and ReLU. This is the *baseline* to beat.
#
# Notice the failures: the MLP struggles most on *similar-shaped* clothing (shirts vs T-shirts vs pullovers) because it sees flat pixel rows with no notion of 2-D structure.


# %% [markdown] color=mint title="5 · CNN — Convolutional Network on Fashion-MNIST"
# # 5 · CNN — Convolutional Network on Fashion-MNIST
#
# ---
# # 5 · CNN — Convolutional Network on Fashion-MNIST
#
# **Goal.** Same dataset, same task — but now the architecture *knows the input is 2-D*.
#
# **Model.** Two conv blocks (each: Conv2d → ReLU → MaxPool) + two fully-connected layers. Convolutions learn translation-invariant features (edges, textures, then patterns of patterns).
#
# **Why this is here.** AlexNet (2012) showed that swapping flat MLPs for convolutions wins big on images. We'll see the same lift in miniature.


# %% color=peach title="5a · Define the CNN"
# @explain: 5a · Define the CNN (same dataset/loaders as Section 4)
# 5a · Define the CNN (same dataset/loaders as Section 4)
class CNN(nn.Module):
    def __init__(self):
        super().__init__()
        self.features = nn.Sequential(
            nn.Conv2d(1, 32, kernel_size=3, padding=1), nn.ReLU(),
            nn.MaxPool2d(2),                                     # 28→14
            nn.Conv2d(32, 64, kernel_size=3, padding=1), nn.ReLU(),
            nn.MaxPool2d(2),                                     # 14→7
        )
        self.classifier = nn.Sequential(
            nn.Flatten(),
            nn.Linear(64 * 7 * 7, 128), nn.ReLU(),
            nn.Linear(128, 10),
        )
    def forward(self, x): return self.classifier(self.features(x))

cnn = CNN().to(DEVICE)
n_params = sum(p.numel() for p in cnn.parameters())
print(cnn); print(f'\nparameters: {n_params:,}')


# %% color=violet title="5b · Train"
# @explain: 5b · Train (same recipe as MLP)
# 5b · Train (same recipe as MLP)
opt = torch.optim.Adam(cnn.parameters(), lr=1e-3)
loss_fn = nn.CrossEntropyLoss()
EPOCHS = 3

history_cnn = {'train_loss': [], 'test_acc': []}
t0 = time.time()
for ep in range(EPOCHS):
    cnn.train(); running = 0; n = 0
    for xb, yb in train_loader:
        xb, yb = xb.to(DEVICE), yb.to(DEVICE)
        opt.zero_grad()
        loss = loss_fn(cnn(xb), yb)
        loss.backward(); opt.step()
        running += loss.item() * yb.size(0); n += yb.size(0)
    tr_loss = running / n
    te_acc = evaluate(cnn, test_loader)
    history_cnn['train_loss'].append(tr_loss); history_cnn['test_acc'].append(te_acc)
    print(f'epoch {ep+1}/{EPOCHS}   train_loss={tr_loss:.4f}   test_acc={te_acc:.4f}')
print(f'\nTrained in {time.time() - t0:.1f}s')


# %% color=amber title="5c · Compare MLP vs CNN side by side"
# @explain: 5c · Compare MLP vs CNN side by side
# 5c · Compare MLP vs CNN side by side
cnn_test_acc = history_cnn['test_acc'][-1]

fig, ax = plt.subplots(figsize=(7, 4))
ax.plot(range(1, EPOCHS + 1), history['test_acc'],     'o-', label=f'MLP (final {mlp_test_acc:.3f})')
ax.plot(range(1, EPOCHS + 1), history_cnn['test_acc'], 'o-', label=f'CNN (final {cnn_test_acc:.3f})')
ax.set_xlabel('epoch'); ax.set_ylabel('test accuracy'); ax.legend()
ax.set_title('Same data · MLP vs CNN'); ax.grid(alpha=0.3)
plt.tight_layout(); plt.show()

print(f'CNN beats MLP by {(cnn_test_acc - mlp_test_acc) * 100:+.2f} percentage points')


# %% [markdown] color=rose title="Interpretation.** Same dataset, same epochs, same…"
# # Interpretation.** Same dataset, same epochs, same…
#
# **Interpretation.** Same dataset, same epochs, same optimizer — just a different architecture. The CNN gains 2–4 percentage points by *baking spatial structure into the model* instead of asking it to learn that structure from scratch. That's the entire pitch of inductive bias.


# %% [markdown] color=lime title="6 · Transformer — Base Language Model from Scratch"
# # 6 · Transformer — Base Language Model from Scratch
#
# ---
# # 6 · Transformer — Base Language Model from Scratch
#
# **Goal.** Train a tiny **base** language model — *no instruction tuning, no RLHF, no chat format* — that simply predicts the next character given the previous ones. Then sample from it and look at what raw next-token prediction produces.
#
# **Dataset.** Tiny Shakespeare (~1 MB of text from his complete works). Karpathy's classic.
#
# **Architecture.** Decoder-only transformer (GPT-style):
# …


# %% color=teal title="6a · Download Tiny Shakespeare"
# @explain: 6a · Download Tiny Shakespeare
# 6a · Download Tiny Shakespeare
url = 'https://raw.githubusercontent.com/karpathy/char-rnn/master/data/tinyshakespeare/input.txt'
if not os.path.exists('shakespeare.txt'):
    urllib.request.urlretrieve(url, 'shakespeare.txt')
text = open('shakespeare.txt').read()
print(f'corpus: {len(text):,} characters')
print('\n--- first 250 chars ---')
print(text[:250])


# %% color=sky title="6b · Character-level tokenizer"
# @explain: 6b · Character-level tokenizer
# @explain: Train / val split
# 6b · Character-level tokenizer
chars = sorted(set(text))
vocab_size = len(chars)
stoi = {c: i for i, c in enumerate(chars)}
itos = {i: c for c, i in stoi.items()}
encode = lambda s: [stoi[c] for c in s]
decode = lambda l: ''.join(itos[i] for i in l)
print(f'vocab size: {vocab_size}')
print(f'characters: {"".join(chars)!r}')

# Train / val split
data = torch.tensor(encode(text), dtype=torch.long)
n = int(0.9 * len(data))
train_data, val_data = data[:n], data[n:]
print(f'train tokens: {len(train_data):,}   val tokens: {len(val_data):,}')


# %% color=mint title="6c · Hyperparameters + batch sampler"
# @explain: 6c · Hyperparameters + batch sampler
# 6c · Hyperparameters + batch sampler
BLOCK_SIZE = 64    # context length
BATCH_SIZE = 32
N_EMBD     = 96
N_HEADS    = 4
N_LAYERS   = 4
LR         = 3e-4
STEPS      = 1500
EVAL_EVERY = 250

def get_batch(split):
    d = train_data if split == 'train' else val_data
    ix = torch.randint(len(d) - BLOCK_SIZE, (BATCH_SIZE,))
    x = torch.stack([d[i:i + BLOCK_SIZE] for i in ix])
    y = torch.stack([d[i + 1:i + BLOCK_SIZE + 1] for i in ix])
    return x.to(DEVICE), y.to(DEVICE)


# %% color=peach title="6d · The model: decoder-only transformer"
# @explain: 6d · The model: decoder-only transformer
# 6d · The model: decoder-only transformer

class CausalSelfAttention(nn.Module):
    def __init__(self, n_embd, n_heads, block_size):
        super().__init__()
        assert n_embd % n_heads == 0
        self.n_heads = n_heads
        self.head_dim = n_embd // n_heads
        self.qkv = nn.Linear(n_embd, 3 * n_embd, bias=False)
        self.proj = nn.Linear(n_embd, n_embd)
        self.register_buffer('mask',
            torch.tril(torch.ones(block_size, block_size)).view(1, 1, block_size, block_size))
    def forward(self, x):
        B, T, C = x.shape
        q, k, v = self.qkv(x).split(C, dim=2)
        q = q.view(B, T, self.n_heads, self.head_dim).transpose(1, 2)  # (B,h,T,d)
        k = k.view(B, T, self.n_heads, self.head_dim).transpose(1, 2)
        v = v.view(B, T, self.n_heads, self.head_dim).transpose(1, 2)
        att = (q @ k.transpose(-2, -1)) * (1.0 / math.sqrt(self.head_dim))
        att = att.masked_fill(self.mask[:, :, :T, :T] == 0, float('-inf'))
        att = F.softmax(att, dim=-1)
        out = att @ v                                  # (B,h,T,d)
        out = out.transpose(1, 2).contiguous().view(B, T, C)
        return self.proj(out)

class FeedForward(nn.Module):
    def __init__(self, n_embd):
        super().__init__()
        self.net = nn.Sequential(
            nn.Linear(n_embd, 4 * n_embd), nn.GELU(),
            nn.Linear(4 * n_embd, n_embd),
        )
    def forward(self, x): return self.net(x)

class Block(nn.Module):
    def __init__(self, n_embd, n_heads, block_size):
        super().__init__()
        self.ln1 = nn.LayerNorm(n_embd)
        self.attn = CausalSelfAttention(n_embd, n_heads, block_size)
        self.ln2 = nn.LayerNorm(n_embd)
        self.ff = FeedForward(n_embd)
    def forward(self, x):
        x = x + self.attn(self.ln1(x))
        x = x + self.ff(self.ln2(x))
        return x

class TinyGPT(nn.Module):
    def __init__(self, vocab_size, n_embd, n_heads, n_layers, block_size):
        super().__init__()
        self.block_size = block_size
        self.tok_emb = nn.Embedding(vocab_size, n_embd)
        self.pos_emb = nn.Embedding(block_size, n_embd)
        self.blocks = nn.Sequential(*[Block(n_embd, n_heads, block_size) for _ in range(n_layers)])
        self.ln_f = nn.LayerNorm(n_embd)
        self.head = nn.Linear(n_embd, vocab_size, bias=False)
    def forward(self, idx, targets=None):
        B, T = idx.shape
        pos = torch.arange(T, device=idx.device)
        x = self.tok_emb(idx) + self.pos_emb(pos)
        x = self.blocks(x)
        x = self.ln_f(x)
        logits = self.head(x)
        loss = None
        if targets is not None:
            loss = F.cross_entropy(logits.view(-1, logits.size(-1)), targets.view(-1))
        return logits, loss
    @torch.no_grad()
    def generate(self, idx, max_new_tokens, temperature=1.0, top_k=None):
        for _ in range(max_new_tokens):
            idx_cond = idx[:, -self.block_size:]
            logits, _ = self(idx_cond)
            logits = logits[:, -1, :] / temperature
            if top_k is not None:
                v, _ = torch.topk(logits, top_k)
                logits[logits < v[:, [-1]]] = float('-inf')
            probs = F.softmax(logits, dim=-1)
            nxt = torch.multinomial(probs, 1)
            idx = torch.cat([idx, nxt], dim=1)
        return idx

model = TinyGPT(vocab_size, N_EMBD, N_HEADS, N_LAYERS, BLOCK_SIZE).to(DEVICE)
n_params = sum(p.numel() for p in model.parameters())
print(f'parameters: {n_params:,}')


# %% color=violet title="6e · Train"
# @explain: 6e · Train (cross-entropy on next-token prediction)
# 6e · Train (cross-entropy on next-token prediction)
opt = torch.optim.AdamW(model.parameters(), lr=LR)

@torch.no_grad()
def estimate_loss(eval_iters=50):
    model.eval()
    out = {}
    for split in ['train', 'val']:
        losses = []
        for _ in range(eval_iters):
            x, y = get_batch(split)
            _, loss = model(x, y)
            losses.append(loss.item())
        out[split] = sum(losses) / len(losses)
    model.train()
    return out

tr_losses, val_losses, steps_logged = [], [], []
t0 = time.time()
for step in range(STEPS + 1):
    if step % EVAL_EVERY == 0:
        l = estimate_loss()
        tr_losses.append(l['train']); val_losses.append(l['val']); steps_logged.append(step)
        print(f'step {step:>5}/{STEPS}   train={l["train"]:.4f}   val={l["val"]:.4f}   '
              f'val_perplexity={math.exp(l["val"]):.2f}')
    x, y = get_batch('train')
    _, loss = model(x, y)
    opt.zero_grad(set_to_none=True); loss.backward(); opt.step()
print(f'\nTrained in {time.time() - t0:.1f}s')


# %% color=amber title="6f · Evaluate: loss curves + perplexity"
# @explain: 6f · Evaluate: loss curves + perplexity
# 6f · Evaluate: loss curves + perplexity
fig, axes = plt.subplots(1, 2, figsize=(12, 4))
axes[0].plot(steps_logged, tr_losses, 'o-', label='train')
axes[0].plot(steps_logged, val_losses, 'o-', label='val')
axes[0].set_xlabel('step'); axes[0].set_ylabel('cross-entropy loss')
axes[0].legend(); axes[0].set_title('Loss curves')

ppl = [math.exp(v) for v in val_losses]
axes[1].plot(steps_logged, ppl, 'o-', color='purple')
axes[1].set_xlabel('step'); axes[1].set_ylabel('val perplexity (lower is better)')
axes[1].set_title(f'Val perplexity   (random ≈ {vocab_size})')
plt.tight_layout(); plt.show()

print(f'final val loss        : {val_losses[-1]:.4f}')
print(f'final val perplexity  : {math.exp(val_losses[-1]):.2f}')
print(f'random-baseline perp. : {vocab_size}  (uniform over the vocab)')


# %% color=rose title="6g · Generate from the BASE model"
# @explain: 6g · Generate from the BASE model — no instructions, just a prompt to continue
# 6g · Generate from the BASE model — no instructions, just a prompt to continue
PROMPTS = [
    'ROMEO:',
    'JULIET:',
    'To be, or not to be,',
    'My lord,',
]
model.eval()
for p in PROMPTS:
    ctx = torch.tensor([encode(p)], dtype=torch.long, device=DEVICE)
    out = model.generate(ctx, max_new_tokens=200, temperature=0.9, top_k=40)[0].tolist()
    print('=' * 60)
    print(f'PROMPT  ▸ {p!r}')
    print('-' * 60)
    print(decode(out))
    print()


# %% [markdown] color=lime title="Interpretation"
# # Interpretation
#
# **Interpretation.**
# - **Loss / perplexity.** Started at ≈ ln(vocab_size) ≈ 4.2 (uniform random) and dropped to ≈ 1.5–1.8 (perplexity ≈ 5). The model is learning real character-level structure.
# - **The output.** Looks Shakespearean *in shape* — character names in CAPS, line breaks, vaguely-iambic rhythms — but the words drift into nonsense. **That is exactly what a base LM should look like at this scale.** It learned the *form* of the corpus, not its *meaning*.
# - **What's missing for ChatGPT.** Bigger model + bigger corpus + then *instruction tuning* + *RLHF*. None of those are happening here. This is the raw next-token predictor.
#
# If you want the model to follow instructions, that's a separate training stage (SFT + RLHF) on top of a base model like this one — and would be the topic of a follow-up notebook.


# %% [markdown] color=teal title="Summary"
# # Summary
#
# ---
# # Summary
#
# Six models, one notebook. Same pipeline shape every time: **load → split → fit → evaluate → visualize**. What changed across them was *what kind of structure the model could capture*.
#
# | Model | Test metric | Score | What it captures |
# |---|---|---|---|
# | Linear Regression | R² | ≈ 0.6 | Linear additive effects |
# …


# %% [markdown] color=lime title="Thanks"
# # End of Module
#
# Next module continues the roadmap.
# Source: https://github.com/kader-xai/data-science-roadmap


