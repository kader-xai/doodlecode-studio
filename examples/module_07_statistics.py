# %% [markdown]
# # Module 7 — Statistics for Machine Learning
# Every ML algorithm is built on these primitives: averages, spread,
# correlation, distributions, and hypothesis tests.

# %% kind=install color=rose title="Install scipy"
import importlib, subprocess, sys
if importlib.util.find_spec("scipy") is None:
    subprocess.check_call([sys.executable, "-m", "pip", "install", "--quiet", "scipy"])
print("scipy ready.")


# %% kind=import color=sky title="Imports"
import numpy as np
import pandas as pd
from scipy import stats
np.random.seed(0)


# %% kind=assign color=peach title="Mean, median, mode"
# @explain: Mean = sum/N (sensitive to outliers). Median = middle value
# @explain: (robust). Mode = most frequent (categorical or discrete).
x = np.array([2, 4, 4, 4, 5, 5, 7, 9])
print("mean   :", x.mean())
print("median :", np.median(x))
print("mode   :", stats.mode(x, keepdims=False).mode)


# %% kind=assign color=peach title="Variance and standard deviation"
# @explain: Variance = avg squared distance from the mean. Std = √var
# @explain: (same units as the data). Use ddof=1 for SAMPLE variance.
print("var (population):", x.var())
print("var (sample)    :", x.var(ddof=1))
print("std (sample)    :", x.std(ddof=1))


# %% kind=assign color=peach title="Range, IQR, percentiles"
# @explain: Range = max − min. IQR = 75th − 25th percentile (robust to
# @explain: outliers). Percentiles give you any cutoff you want.
print("range:", x.max() - x.min())
q1, q3 = np.percentile(x, [25, 75])
print(f"IQR: {q3 - q1}")
print("p10, p90:", np.percentile(x, [10, 90]))


# %% [markdown]
# ## Distributions
# Most ML assumes data comes from some distribution. Knowing them helps
# you pick models, generate synthetic data, and interpret results.


# %% kind=function color=mint title="Normal (Gaussian)"
# @explain: The bell curve — symmetric, defined by mean and std.
# @explain: Many real measurements (height, error terms) are approx normal.
rv = stats.norm(loc=0, scale=1)
sample = rv.rvs(size=5)
print("samples       :", sample.round(2))
print("pdf(0)        :", rv.pdf(0))
print("cdf(1.96)     :", rv.cdf(1.96))   # ≈ 0.975
print("P(|Z| < 1.96) :", rv.cdf(1.96) - rv.cdf(-1.96))


# %% kind=function color=mint title="Binomial"
# @explain: Number of successes in n independent yes/no trials, each
# @explain: with probability p. Foundation of A/B testing and Naive Bayes.
n, p = 10, 0.3
rv = stats.binom(n=n, p=p)
print("mean    :", rv.mean())   # n*p
print("var     :", rv.var())    # n*p*(1-p)
print("P(X=3)  :", rv.pmf(3))
print("samples :", rv.rvs(size=8))


# %% kind=function color=mint title="Poisson — counting rare events"
# @explain: For things like number of calls per hour or defects per
# @explain: batch. One parameter (λ) = average rate.
rv = stats.poisson(mu=4)
print("P(X=2):", rv.pmf(2))
print("samples:", rv.rvs(size=8))


# %% [markdown]
# ## Correlation — how do two variables move together?


# %% kind=function color=mint title="Pearson, Spearman, covariance"
# @explain: Pearson = linear correlation in [-1, 1]. Spearman = rank
# @explain: correlation (monotonic, not just linear). Covariance is
# @explain: unnormalised — its sign tells you direction.
x = np.random.randn(200)
y = 2 * x + np.random.randn(200) * 0.5
z = np.random.randn(200)

print("Pearson(x,y)  :", stats.pearsonr(x, y).statistic.round(3))
print("Pearson(x,z)  :", stats.pearsonr(x, z).statistic.round(3))
print("Spearman(x,y) :", stats.spearmanr(x, y).statistic.round(3))
print("cov(x,y)      :", np.cov(x, y)[0, 1].round(3))


# %% kind=function color=mint title="Correlation matrix on a DataFrame"
# @explain: pandas .corr() returns a square matrix — visualise with a
# @explain: heatmap (see Module 6). The diagonal is always 1.
df = pd.DataFrame({
    "x":  np.random.randn(200),
    "y":  np.random.randn(200),
    "z":  np.random.randn(200),
})
df["x2y"] = 0.8 * df["x"] + 0.2 * df["y"]
print(df.corr().round(2))


# %% [markdown]
# ## The Central Limit Theorem
# The mean of many samples from ANY finite-variance distribution
# approaches a normal distribution. This is why so much statistics
# assumes normality — even when the data isn't.


# %% kind=loop color=yellow title="CLT in code — uniform → normal"
# @explain: Average n=30 uniform samples, repeat 5000 times, plot the
# @explain: histogram of those averages. It looks bell-shaped even
# @explain: though uniform samples are flat.
import matplotlib.pyplot as plt
trials = 5_000
n = 30
means = np.array([np.random.uniform(0, 1, n).mean() for _ in range(trials)])

plt.figure(figsize=(5, 3))
plt.hist(means, bins=40, color="#5c7cfa", edgecolor="k")
plt.title(f"Means of {n} uniform samples ({trials} trials)")
plt.show()


# %% [markdown]
# ## Hypothesis testing — is the difference real?


# %% kind=function color=mint title="t-test on two samples"
# @explain: We ask: are these two groups drawn from populations with the
# @explain: same mean? p < 0.05 → unlikely the difference is by chance.
group_a = np.random.normal(loc=10, scale=2, size=80)
group_b = np.random.normal(loc=11, scale=2, size=80)

res = stats.ttest_ind(group_a, group_b)
print(f"means: {group_a.mean():.2f} vs {group_b.mean():.2f}")
print(f"t = {res.statistic:.3f}, p = {res.pvalue:.4f}")
print("=> reject H0?" , res.pvalue < 0.05)


# %% kind=function color=mint title="Chi-squared on a contingency table"
# @explain: Are two categorical variables independent?
# @explain: H0: independence. Small p → reject → they're related.
table = np.array([
    [20, 30],
    [35, 15],
])
chi2, p, dof, exp = stats.chi2_contingency(table)
print(f"chi2 = {chi2:.3f}, dof = {dof}, p = {p:.4f}")


# %% [markdown]
# ## Why "ddof"?
# `ddof=1` divides by N−1 instead of N. Use it for SAMPLE statistics
# (when you have a subset of the population). Most ML uses ddof=0
# because the data IS the population (the training set).


# %% [markdown]
# ## Practice
# 1. Draw 1000 samples from N(50, 5²). Confirm 95% are within ±1.96·5.
# 2. Compute Spearman corr between `x = arange(20)` and `y = x²`. It
#    should be 1.0 (perfectly monotonic) even though it's not linear.


# %% kind=function color=mint title="Practice 1 — 95% within ±1.96σ"
# @explain: For a normal distribution this is 95% by definition. With
# @explain: a finite sample the number is close but not exact.
mu, sigma = 50, 5
samples = np.random.normal(mu, sigma, size=1000)
inside = np.abs(samples - mu) < 1.96 * sigma
print(f"inside fraction: {inside.mean():.3f}")


# %% kind=function color=mint title="Practice 2 — Spearman on nonlinear pair"
# @explain: Spearman cares only about order. Squaring preserves order
# @explain: for positive x, so rank correlation is perfect.
x = np.arange(20)
y = x ** 2
print("Pearson :", stats.pearsonr(x, y).statistic.round(3))
print("Spearman:", stats.spearmanr(x, y).statistic.round(3))


# %% [markdown]
# ## Recap
# - ✅ Centre and spread (mean, median, std, IQR, percentiles)
# - ✅ Common distributions (normal, binomial, Poisson)
# - ✅ Correlation (Pearson, Spearman, covariance)
# - ✅ Central Limit Theorem
# - ✅ t-test and chi-squared
#
# **Next:** Module 8 — Linear algebra for ML.
