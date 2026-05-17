# doodlecode format-version: 2
# Auto-converted from module_28_ab_testing.ipynb
# Open with 📂 Open → press 🎬 Present.


# %% [markdown] color=rose title="Module 28 Ab Testing"
# # Module 28 Ab Testing
#
# A live walkthrough — one card per concept.
# Use → / ← to step through. Press 🎬 Present to begin.



# %% [markdown] color=sky title="Module 28 — A/B Testing & Inferential Statistics"
# # Module 28 — A/B Testing & Inferential Statistics
#
# > Every product company runs A/B tests. Every product-DS interview asks about them. This module covers the math, the pitfalls, and the code — using `scipy.stats` and `statsmodels`.
#
# ### What you'll cover
# 1. The mental model — null vs alternative, p-values, type-I/II errors
# 2. **Two-proportion z-test** — conversion rates, click rates (binary metrics)
# 3. **Two-sample t-test** — revenue per user, time on site (continuous metrics)
# …


# %% [markdown] color=mint title="1 · The Mental Model"
# # 1 · The Mental Model
#
# | Concept | Plain English |
# |---|---|
# | **Null hypothesis (H₀)** | "the change does NOTHING" |
# | **Alternative (H₁)** | "the change does something" |
# | **p-value** | probability of seeing data this extreme IF H₀ is true |
# | **α (significance)** | acceptable false-positive rate. Default 0.05. |
# …


# %% color=peach title="!pip -q install statsmodels scipy"
# @explain: Run this cell to see the output.
!pip -q install statsmodels scipy
import numpy as np, pandas as pd, matplotlib.pyplot as plt
from scipy import stats
import statsmodels.stats.api as sms
import warnings; warnings.filterwarnings("ignore")
np.random.seed(0)


# %% [markdown] color=violet title="2 · Two-Proportion z-Test — Conversion Rates"
# # 2 · Two-Proportion z-Test — Conversion Rates
#
# The most common A/B test: **does the new variant change a binary outcome?** (clicked / converted / signed up)
#
# We compare the proportion of successes in the two groups.


# %% color=amber title="Control"
# @explain: Control (A): 1000 users, 80 conversions  → 8.0%
# @explain: Variant (B): 1000 users, 100 conversions → 10.0%
# @explain: Two-proportion z-test
# Control (A): 1000 users, 80 conversions  → 8.0%
# Variant (B): 1000 users, 100 conversions → 10.0%
n_a, x_a = 1000, 80
n_b, x_b = 1000, 100

p_a, p_b = x_a / n_a, x_b / n_b
print(f"control: {p_a:.3%}    variant: {p_b:.3%}    lift: {(p_b - p_a)/p_a:+.1%}")

# Two-proportion z-test
from statsmodels.stats.proportion import proportions_ztest

stat, pval = proportions_ztest([x_b, x_a], [n_b, n_a], alternative="larger")
print(f"\nz-statistic: {stat:.3f}    p-value: {pval:.4f}")
print("verdict:", "REJECT H0 (variant wins)" if pval < 0.05 else "fail to reject H0")


# %% [markdown] color=rose title="Reading the output:** with α = 0.05, a p-value…"
# # Reading the output:** with α = 0.05, a p-value…
#
# **Reading the output:** with α = 0.05, a p-value below 0.05 lets us say "the lift is statistically significant." Note we used `alternative="larger"` for a one-sided test (we asked: is B *bigger* than A). For a two-sided test, drop the alternative argument.


# %% [markdown] color=lime title="3 · Two-Sample t-Test — Continuous Metrics"
# # 3 · Two-Sample t-Test — Continuous Metrics
#
# For metrics like **revenue per user**, **session length**, **load time** — anything continuous.


# %% color=teal title="Control: revenue per user"
# @explain: Control: revenue per user, mean ~$10, std ~$15
# @explain: Variant: bumps mean to ~$11.5
# @explain: Welch's t-test — does NOT assume equal variances
rng = np.random.default_rng(42)

# Control: revenue per user, mean ~$10, std ~$15
revenue_a = rng.normal(10, 15, 500).clip(min=0)
# Variant: bumps mean to ~$11.5
revenue_b = rng.normal(11.5, 15, 500).clip(min=0)

print(f"A: mean=${revenue_a.mean():.2f} ± ${revenue_a.std():.2f}    (n={len(revenue_a)})")
print(f"B: mean=${revenue_b.mean():.2f} ± ${revenue_b.std():.2f}    (n={len(revenue_b)})")

# Welch's t-test — does NOT assume equal variances. Almost always the right choice.
stat, pval = stats.ttest_ind(revenue_b, revenue_a, equal_var=False, alternative="greater")
print(f"\nt-statistic: {stat:.3f}    p-value: {pval:.4f}")


# %% [markdown] color=sky title="4 · Confidence Intervals — What They Actually Mean"
# # 4 · Confidence Intervals — What They Actually Mean
#
# A 95% CI: *"if we ran this experiment many times, 95% of the resulting CIs would contain the true mean."*
#
# It is **not** "there's a 95% chance the true value is in this interval" (that's a Bayesian credible interval).


# %% color=mint title="CI for the DIFFERENCE in conversion rates"
# @explain: CI for the DIFFERENCE in conversion rates
# CI for the DIFFERENCE in conversion rates
from statsmodels.stats.proportion import confint_proportions_2indep

low, high = confint_proportions_2indep(x_b, n_b, x_a, n_a, method="wald")
print(f"95% CI for (p_B − p_A): [{low:+.4f}, {high:+.4f}]")
print("contains 0?", low <= 0 <= high, "  → if NO, statistically significant")


# %% color=peach title="CI for the difference in revenue means"
# @explain: CI for the difference in revenue means
# CI for the difference in revenue means
from scipy.stats import t

diff = revenue_b.mean() - revenue_a.mean()
se   = np.sqrt(revenue_a.var(ddof=1)/len(revenue_a) + revenue_b.var(ddof=1)/len(revenue_b))
ci_low, ci_high = diff - 1.96 * se, diff + 1.96 * se
print(f"diff = ${diff:.2f}    95% CI = [${ci_low:.2f}, ${ci_high:.2f}]")


# %% [markdown] color=violet title="5 · Sample-Size & Power Calculation"
# # 5 · Sample-Size & Power Calculation
#
# **Do this BEFORE you launch.** The formula tells you how many users each arm needs to reliably detect a given lift, with a given α and power.
#
# Inputs:
# - baseline conversion rate
# - minimum detectable effect (MDE) — the smallest lift you'd care to detect
# - α (usually 0.05)
# …


# %% color=amber title="from statsmodels.stats.power import NormalIndPower"
# @explain: Run this cell to see the output.
from statsmodels.stats.power import NormalIndPower
from statsmodels.stats.proportion import proportion_effectsize

baseline = 0.08
mde      = 0.02         # detect 8% → 10%, i.e. 2pp absolute
effect   = proportion_effectsize(baseline + mde, baseline)

n_per_arm = NormalIndPower().solve_power(
    effect_size=effect, alpha=0.05, power=0.80, ratio=1, alternative="larger")
print(f"need ~{int(np.ceil(n_per_arm)):,} users per arm  →  ~{int(np.ceil(2*n_per_arm)):,} total")


# %% [markdown] color=rose title="Power vs sample size — visualise the trade-off"
# # Power vs sample size — visualise the trade-off
#


# %% color=lime title="sizes = np.arange(200"
# @explain: Run this cell to see the output.
sizes = np.arange(200, 5000, 200)
effects = [0.005, 0.01, 0.02, 0.04]   # MDE values

fig, ax = plt.subplots(figsize=(9, 4))
for mde in effects:
    es = proportion_effectsize(baseline + mde, baseline)
    powers = [NormalIndPower().solve_power(effect_size=es, nobs1=n,
                                            alpha=0.05, ratio=1, alternative="larger")
              for n in sizes]
    ax.plot(sizes, powers, label=f"MDE = {mde:.1%}")

ax.axhline(0.80, color="grey", linestyle="--", label="80% power")
ax.set(xlabel="users per arm", ylabel="power",
       title=f"Power vs sample size (baseline {baseline:.0%})")
ax.legend(); ax.grid(alpha=.3); plt.show()


# %% [markdown] color=teal title="Reading the chart:** smaller effects need larger…"
# # Reading the chart:** smaller effects need larger…
#
# **Reading the chart:** smaller effects need larger samples. To detect a 0.5% lift you might need 100k users per arm; for 4% lift, a few hundred suffices.


# %% [markdown] color=sky title="6 · Multiple-Testing Correction"
# # 6 · Multiple-Testing Correction
#
# Run 20 independent tests at α = 0.05 → expect ~1 false positive even if NOTHING works. Two standard fixes:
#
# | Method | What it does |
# |---|---|
# | **Bonferroni** | divide α by the number of tests. Strict but simple. |
# | **Benjamini-Hochberg (BH)** | controls the *false discovery rate* — fewer false positives without losing too much power. The modern default. |


# %% color=mint title="Imagine we ran 20 metric tests"
# @explain: Imagine we ran 20 metric tests; 18 nulls, 2 real effects
from statsmodels.stats.multitest import multipletests

# Imagine we ran 20 metric tests; 18 nulls, 2 real effects
np.random.seed(0)
true_pvals  = np.random.uniform(0, 1, 18)              # uniform under H0
real_pvals  = np.array([0.001, 0.01])                  # genuine effects
pvals = np.concatenate([true_pvals, real_pvals])

reject_bonf, pvals_bonf, _, _ = multipletests(pvals, alpha=0.05, method="bonferroni")
reject_bh,   pvals_bh,   _, _ = multipletests(pvals, alpha=0.05, method="fdr_bh")

print("raw      < 0.05:", (pvals < 0.05).sum(), "rejected (incl. false positives)")
print("Bonferroni     :", reject_bonf.sum(), "rejected")
print("BH (FDR)       :", reject_bh.sum(), "rejected")


# %% [markdown] color=peach title="7 · Sequential Testing — Why Peeking Inflates False Positives"
# # 7 · Sequential Testing — Why Peeking Inflates False Positives
#
# **The mistake:** check the p-value daily, stop the experiment as soon as `p < 0.05`. This **does not work** — running 30 separate tests gives you ~80% chance of a false positive, even if nothing is happening.


# %% color=violet title="Simulate: NO real effect (both groups same true rate)"
# @explain: Simulate: NO real effect (both groups same true rate)
# Simulate: NO real effect (both groups same true rate). Peek every day.
N_DAYS = 30
USERS_PER_DAY = 100

def run_one_experiment_with_peeking(seed):
    rng = np.random.default_rng(seed)
    p_true = 0.10
    a_x, a_n = 0, 0
    b_x, b_n = 0, 0
    for d in range(N_DAYS):
        a_x += rng.binomial(USERS_PER_DAY, p_true); a_n += USERS_PER_DAY
        b_x += rng.binomial(USERS_PER_DAY, p_true); b_n += USERS_PER_DAY
        _, pv = proportions_ztest([b_x, a_x], [b_n, a_n])
        if pv < 0.05:
            return True   # we (incorrectly) declare significance
    return False

n_runs = 1000
false_positives = sum(run_one_experiment_with_peeking(s) for s in range(n_runs))
print(f"daily peeking with α=0.05: false-positive rate = {false_positives/n_runs:.1%}")
print("(expected near 5%; actual is much higher because we kept looking)")


# %% [markdown] color=amber title="The fix:** decide your sample size BEFORE the test,…"
# # The fix:** decide your sample size BEFORE the test,…
#
# **The fix:** decide your sample size BEFORE the test, look at it once at the end. Or use proper sequential methods (Always Valid Inference, group-sequential designs).


# %% [markdown] color=rose title="8 · Common Pitfalls"
# # 8 · Common Pitfalls
#
# ### Sample Ratio Mismatch (SRM)
# If you split traffic 50/50 but observe 51/49, something is broken — bot filters, redirects, broken assignment. Test with a chi-square goodness-of-fit BEFORE looking at metrics.


# %% color=lime title="observed = [4900, 5100]            # users in A vs B"
# @explain: Run this cell to see the output.
observed = [4900, 5100]            # users in A vs B (expected 5000/5000)
expected = [5000, 5000]
chi2, p = stats.chisquare(observed, expected)
print(f"SRM check  χ² = {chi2:.2f}    p = {p:.3f}")
print("any SRM?", "YES — investigate before trusting results" if p < 0.001 else "NO")


# %% [markdown] color=teal title="Simpson's Paradox"
# # Simpson's Paradox
#
# The aggregate trend can REVERSE inside subgroups. Always slice by key segments (device, country, new vs returning).
#
# ### Novelty Effects
# Users react to *anything new* in the first few days. Run for at least 1-2 full weeks for a typical consumer product. Check if effect persists in the latter half.
#
# ### Multiple Comparisons
# You ran ONE test → trust it. You ran 20 tests → use Bonferroni or FDR. Section 6 has the code.
# …


# %% [markdown] color=sky title="9 · End-to-End Walkthrough"
# # 9 · End-to-End Walkthrough
#
# We'll **design**, **simulate**, and **analyse** a complete test.
#
# ### Question
# > "Will adding social-proof badges increase signup conversion?"
#
# **Baseline:** 8% conversion. **MDE:** 1pp absolute (8% → 9%). **α=0.05, power=0.80.**


# %% color=mint title="baseline = 0.08"
# @explain: Run this cell to see the output.
baseline = 0.08
mde      = 0.01
effect   = proportion_effectsize(baseline + mde, baseline)
n_per_arm = NormalIndPower().solve_power(
    effect_size=effect, alpha=0.05, power=0.80, ratio=1, alternative="larger")
print(f"design says: need {int(np.ceil(n_per_arm)):,} users per arm")


# %% color=peach title="SIMULATE: assume the badge actually gives +0.8pp"
# @explain: SIMULATE: assume the badge actually gives +0.8pp (NOT enough to be detectable per design)
# SIMULATE: assume the badge actually gives +0.8pp (NOT enough to be detectable per design)
rng = np.random.default_rng(123)
n = int(np.ceil(n_per_arm))
a = rng.binomial(1, 0.080, n).sum()
b = rng.binomial(1, 0.088, n).sum()
print(f"observed: A={a/n:.3%}    B={b/n:.3%}    lift = {(b-a)/a:+.2%}")

stat, pval = proportions_ztest([b, a], [n, n], alternative="larger")
print(f"z = {stat:.2f}    p = {pval:.4f}")
print("verdict:", "REJECT H0" if pval < 0.05 else "fail to reject H0")


# %% [markdown] color=violet title="Lesson:** the simulated true effect (+0.8pp) was…"
# # Lesson:** the simulated true effect (+0.8pp) was…
#
# **Lesson:** the simulated true effect (+0.8pp) was BELOW the MDE (1pp), so the test usually fails to detect it — exactly as the power calculation predicted. Statistically-correct outcome, not a model failure.


# %% [markdown] color=amber title="10 · Practice — Try Yourself"
# # 10 · Practice — Try Yourself
#
# 1. **Two-proportion test** — control 200/2000, variant 250/2000. Compute lift, run a two-sided z-test, and report whether to ship.
# 2. **Sample-size calc** — baseline 12% conversion, you want to detect a 1.5% absolute lift with α=0.01 and power=0.90. How many users per arm?
# 3. **Power curve** — for baseline 5% conversion and n=10,000 per arm, plot achieved power as a function of MDE from 0.1% to 2%. What's the smallest detectable lift at 80% power?
# 4. **Multiple testing** — you have 50 hypothetical p-values uniformly distributed. Apply Bonferroni and BH at α=0.05. How many would you reject under each?


# %% color=rose title="1) Two-proportion test"
# @explain: 1) Two-proportion test
# @explain: 2) Sample-size calc
# @explain: 3) Power curve
# @explain: 4) Multiple testing
# 1) Two-proportion test
from statsmodels.stats.proportion import proportions_ztest
n_a, x_a = 2000, 200
n_b, x_b = 2000, 250
p_a, p_b = x_a/n_a, x_b/n_b
print(f"A: {p_a:.2%}   B: {p_b:.2%}   lift: {(p_b-p_a)/p_a:+.1%}")
stat, pval = proportions_ztest([x_b, x_a], [n_b, n_a])
print(f"z = {stat:.3f}   p = {pval:.4f}   ship: {pval < 0.05}")

# 2) Sample-size calc
baseline, mde = 0.12, 0.015
es = proportion_effectsize(baseline + mde, baseline)
n = NormalIndPower().solve_power(effect_size=es, alpha=0.01, power=0.90,
                                 ratio=1, alternative="larger")
print(f"\nneed {int(np.ceil(n)):,} users per arm")

# 3) Power curve
mdes = np.arange(0.001, 0.021, 0.001)
powers = [NormalIndPower().solve_power(
    effect_size=proportion_effectsize(0.05 + m, 0.05),
    nobs1=10000, alpha=0.05, ratio=1, alternative="larger") for m in mdes]

import matplotlib.pyplot as plt
plt.plot(mdes*100, powers)
plt.axhline(0.80, color="grey", linestyle="--")
plt.xlabel("MDE (percentage points)"); plt.ylabel("power")
plt.title("Power at n=10k per arm, baseline 5%"); plt.grid(alpha=.3); plt.show()

# 4) Multiple testing
np.random.seed(7)
pv = np.random.uniform(0, 1, 50)
print("\nraw  rejects:", (pv < 0.05).sum())
print("Bonf rejects:", multipletests(pv, alpha=0.05, method="bonferroni")[0].sum())
print("BH   rejects:", multipletests(pv, alpha=0.05, method="fdr_bh")[0].sum())


# %% [markdown] color=lime title="Recap"
# # Recap
#
# ✅ State a null hypothesis and read a p-value correctly
# ✅ Run two-proportion z-test for binary metrics
# ✅ Run Welch's t-test for continuous metrics
# ✅ Compute and interpret confidence intervals
# ✅ Calculate required sample size BEFORE launching
# ✅ Apply Bonferroni or BH correction for multiple metrics
# …


# %% [markdown] color=lime title="Thanks"
# # End of Module
#
# Next module continues the roadmap.
# Source: https://github.com/kader-xai/data-science-roadmap


