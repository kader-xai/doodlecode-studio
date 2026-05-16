# %% [markdown]
# # Module 9 — Probability for Machine Learning
# Random variables, distributions, conditional probability, Bayes'
# theorem, and the law of large numbers — all the priors you need
# before reading any ML paper.

# %% kind=import color=sky title="Imports"
import numpy as np
import matplotlib.pyplot as plt
from scipy import stats
np.random.seed(0)


# %% kind=intro color=sky title="The two interpretations"
# @explain: Frequentist: probability = long-run frequency.
# @explain: Bayesian: probability = degree of belief, updated by data.
# @explain: Both produce the same arithmetic — disagree on philosophy.
# @tags: intro


# %% kind=expr color=peach title="Sample space and events"
# @explain: A coin flip has Ω = {H, T}. P(H) = 0.5.
# @explain: A die has Ω = {1..6}. P(even) = 3/6 = 0.5.
flips = np.random.choice(["H", "T"], size=10_000, p=[0.5, 0.5])
heads = (flips == "H").mean()
print(f"observed P(H) ≈ {heads:.3f}")


# %% [markdown]
# ## Discrete distributions


# %% kind=function color=mint title="Bernoulli — a single yes/no trial"
# @explain: P(X=1) = p, P(X=0) = 1-p. Mean = p, Variance = p(1-p).
p = 0.3
samples = (np.random.rand(5000) < p).astype(int)
print(f"empirical p = {samples.mean():.3f}  (true: {p})")


# %% kind=function color=mint title="Binomial — n Bernoulli trials"
# @explain: Number of successes in n trials, each with probability p.
# @explain: Classic example: number of correct answers on a quiz.
n, p = 10, 0.4
rv = stats.binom(n, p)
print("P(X = 3)   :", rv.pmf(3))
print("P(X ≤ 4)   :", rv.cdf(4))
print("E[X]       :", rv.mean())   # n*p
print("Var[X]     :", rv.var())    # n*p*(1-p)


# %% kind=function color=mint title="Poisson — rare event counts"
# @explain: Events per fixed interval (calls/hour, defects/batch).
# @explain: One parameter, λ = expected count. Variance = λ too.
rv = stats.poisson(mu=2.5)
print("P(X = 0):", rv.pmf(0))
print("P(X ≥ 5):", 1 - rv.cdf(4))


# %% [markdown]
# ## Continuous distributions


# %% kind=function color=mint title="Uniform"
# @explain: Equal density on [a, b]. The reference distribution for
# @explain: 'no information': max-entropy on a bounded interval.
rv = stats.uniform(loc=0, scale=10)
print("pdf at 3:", rv.pdf(3))
print("P(2 < X < 5):", rv.cdf(5) - rv.cdf(2))


# %% kind=function color=mint title="Normal (Gaussian)"
# @explain: Most measurements with many small random influences end up
# @explain: roughly normal (CLT). Default noise model in linear models.
rv = stats.norm(loc=0, scale=1)
xs = np.linspace(-4, 4, 200)
plt.figure(figsize=(5, 3))
plt.plot(xs, rv.pdf(xs), color="#1971c2")
plt.fill_between(xs, rv.pdf(xs), where=(xs > -1) & (xs < 1), alpha=0.3, color="#74c0fc")
plt.title("Standard normal — 68% within ±1σ")
plt.show()


# %% kind=function color=mint title="Exponential — time until next event"
# @explain: How long you wait for the next bus, given a constant arrival
# @explain: rate. Memoryless: P(wait > t+s | wait > s) = P(wait > t).
rv = stats.expon(scale=1 / 0.5)   # rate λ = 0.5
samples = rv.rvs(size=1000)
print(f"mean wait ≈ {samples.mean():.2f}  (true 1/λ = 2.00)")


# %% [markdown]
# ## Conditional probability and Bayes' theorem


# %% kind=function color=mint title="Bayes' theorem in code"
# @explain: P(A|B) = P(B|A) · P(A) / P(B).
# @explain: Classic example: disease test with 99% sensitivity and
# @explain: 95% specificity. Disease prevalence is 1%. If you test
# @explain: positive, what's the chance you actually have it?
prevalence = 0.01
sensitivity = 0.99   # P(test+ | disease)
specificity = 0.95   # P(test- | healthy)

p_pos_given_disease = sensitivity
p_pos_given_healthy = 1 - specificity
p_disease = prevalence
p_healthy = 1 - prevalence

p_pos = p_pos_given_disease * p_disease + p_pos_given_healthy * p_healthy
p_disease_given_pos = (p_pos_given_disease * p_disease) / p_pos

print(f"P(disease | test+) = {p_disease_given_pos:.3f}")
print("Even with a 99%-accurate test, only ~16% of positives are real")
print("because the disease itself is rare. This is base-rate neglect.")


# %% [markdown]
# ## The law of large numbers
# Empirical averages converge to the true mean as the sample size grows.


# %% kind=loop color=yellow title="Running mean converges"
# @explain: Average a growing sample of standard-normal draws. The
# @explain: cumulative mean rattles around at first, then settles near 0.
samples = np.random.randn(5_000)
running_mean = np.cumsum(samples) / np.arange(1, len(samples) + 1)

plt.figure(figsize=(6, 3))
plt.plot(running_mean, color="#2f9e44")
plt.axhline(0, color="black", linestyle="--", linewidth=1)
plt.title("Running mean → true mean (= 0)")
plt.xlabel("samples")
plt.show()


# %% [markdown]
# ## Maximum likelihood — fitting distributions to data


# %% kind=function color=mint title="MLE for a normal"
# @explain: The MLE estimates for a normal are just the sample mean and
# @explain: the sample variance. Many ML losses are NLL = -log L under
# @explain: some assumed distribution.
data = np.random.normal(loc=5, scale=2, size=500)
mu_hat = data.mean()
sigma_hat = data.std()
print(f"true       : mu=5.00, sigma=2.00")
print(f"MLE        : mu={mu_hat:.3f}, sigma={sigma_hat:.3f}")


# %% [markdown]
# ## Why probabilities multiply / add


# %% kind=function color=mint title="Independence"
# @explain: For independent events, P(A and B) = P(A) · P(B).
# @explain: For ANY events, P(A or B) = P(A) + P(B) - P(A and B).
p_rain = 0.3
p_traffic = 0.4
# Assume independent for the demo.
print("P(rain AND traffic) =", p_rain * p_traffic)
print("P(rain OR  traffic) =", p_rain + p_traffic - p_rain * p_traffic)


# %% [markdown]
# ## Practice
# 1. Estimate π by Monte Carlo: sample points uniformly in [-1,1]² and
#    count the fraction inside the unit circle.
# 2. A coin is flipped 100 times. What is P(≥ 60 heads) under a fair coin?


# %% kind=function color=mint title="Practice 1 — Monte Carlo π"
# @explain: Area of unit circle / square = π/4. Multiply the fraction
# @explain: of points inside by 4 to get an estimate of π.
n = 200_000
xs = np.random.uniform(-1, 1, n)
ys = np.random.uniform(-1, 1, n)
inside = (xs ** 2 + ys ** 2) <= 1
pi_hat = inside.mean() * 4
print(f"π estimate: {pi_hat:.4f}  (true 3.1416)")


# %% kind=function color=mint title="Practice 2 — Binomial tail"
# @explain: scipy makes this a one-liner.
p_geq_60 = 1 - stats.binom(100, 0.5).cdf(59)
print(f"P(≥60 heads out of 100) = {p_geq_60:.4f}")


# %% [markdown]
# ## Recap
# - ✅ Discrete and continuous distributions
# - ✅ Sampling, PMF, PDF, CDF
# - ✅ Conditional probability and Bayes
# - ✅ Law of large numbers, MLE
# - ✅ Monte Carlo estimation
#
# **Next:** Module 10 — Data preprocessing.
