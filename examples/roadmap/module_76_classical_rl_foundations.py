# doodlecode format-version: 2
# Auto-converted from module_76_classical_rl_foundations.ipynb
# Open with 📂 Open → press 🎬 Present.


# %% [markdown] color=rose title="Module 76 Classical Rl Foundations"
# # Module 76 Classical Rl Foundations
#
# A live walkthrough — one card per concept.
# Use → / ← to step through. Press 🎬 Present to begin.



# %% [markdown] color=sky title="Module 76 — Classical RL Foundations"
# # Module 76 — Classical RL Foundations
#
# > M67's RLHF / GRPO assumed you knew RL. This module fills that in **from first principles**. We'll walk: **MDP → Bellman → value iteration → tabular Q-learning → DQN → REINFORCE → Actor-Critic → PPO**. At the end, you'll see why **PPO** is the algorithm RLHF picked, why **DPO** (M62) reframed the problem as supervised learning, and why **GRPO** (M67) drops the value function entirely.
#
# ### What you'll cover
# 1. The RL setting — agent, environment, reward
# 2. **MDPs** — `(S, A, P, R, γ)` and the discounted return
# 3. **Bellman equations** — the recursive structure that makes RL tractable
# …


# %% [markdown] color=mint title="1 · The RL setting"
# # 1 · The RL setting
#
# ```
#                     ┌─────────────────────┐
#                     │      AGENT          │
#                     │  (policy π_θ)       │
#                     └────────┬────────────┘
#                 action a_t   │   ▲   reward r_t , next state s_{t+1}
# …


# %% [markdown] color=peach title="2 · Markov Decision Processes"
# # 2 · Markov Decision Processes
#
# A finite **MDP** is a 5-tuple `(S, A, P, R, γ)`:
#
# | Symbol | Meaning |
# |---|---|
# | `S` | set of states |
# | `A` | set of actions |
# …


# %% [markdown] color=violet title="3 · Bellman equations — the recursion"
# # 3 · Bellman equations — the recursion
#
# Define two **value functions**:
# - **State value** `V^π(s)` = expected return starting from `s` following policy `π`.
# - **Action value** `Q^π(s, a)` = expected return after taking `a` in `s`, then following `π`.
#
# They satisfy **Bellman's equations**:
#
# …


# %% [markdown] color=amber title="4 · Value iteration in GridWorld"
# # 4 · Value iteration in GridWorld
#
# Tiny 4×4 grid. Start top-left, goal bottom-right. Each step costs −1; reaching the goal ends the episode. Four actions: up, down, left, right. Walls bounce you back.


# %% color=rose title="!pip -q install numpy matplotlib torch gymnasium"
# @explain: Run this cell to see the output.
!pip -q install numpy matplotlib torch gymnasium


# %% color=lime title="Initialise V(s) = 0"
# @explain: Initialise V(s) = 0
import numpy as np
np.set_printoptions(precision=2, suppress=True)

ROWS, COLS = 4, 4
GOAL = (3, 3)
ACTIONS = {"U": (-1, 0), "D": (1, 0), "L": (0, -1), "R": (0, 1)}
GAMMA = 0.99

def step(state, action):
    r, c = state
    dr, dc = ACTIONS[action]
    nr, nc = min(max(r + dr, 0), ROWS - 1), min(max(c + dc, 0), COLS - 1)
    nstate = (nr, nc)
    reward = 0.0 if nstate == GOAL else -1.0
    done = nstate == GOAL
    return nstate, reward, done

# Initialise V(s) = 0
V = np.zeros((ROWS, COLS))
for sweep in range(50):
    new_V = V.copy()
    for r in range(ROWS):
        for c in range(COLS):
            if (r, c) == GOAL: continue
            best = -np.inf
            for a in ACTIONS:
                (nr, nc), reward, done = step((r, c), a)
                best = max(best, reward + GAMMA * V[nr, nc] * (0.0 if done else 1.0))
            new_V[r, c] = best
    if np.allclose(new_V, V, atol=1e-6): print(f"converged at sweep {sweep}"); V = new_V; break
    V = new_V
print(V)


# %% [markdown] color=teal title="Read the output.** The number in each cell is the…"
# # Read the output.** The number in each cell is the…
#
# **Read the output.** The number in each cell is the value `V*(s)` — the expected discounted return from that cell under the optimal policy. Closer to the goal → less negative → better.
#
# Two algorithms hide in this loop:
# - **Value iteration**: update `V ← max_a [R + γ · V(s')]` each sweep until convergence.
# - **Policy iteration**: alternate (1) **evaluate** `V^π` for fixed `π`, (2) **improve** `π ← argmax_a Q^π(s, a)`. Same fixed point.
#
# In a real environment we don't know `P` and `R` up front. We have to **learn them by interaction**. That's where Q-learning starts.


# %% [markdown] color=sky title="5 · Tabular Q-learning"
# # 5 · Tabular Q-learning
#
# **TD(0)** update — adjust `Q(s,a)` toward the *bootstrapped* one-step return:
#
# $$Q(s, a) \leftarrow Q(s, a) + \alpha \big[ r + \gamma \max_{a'} Q(s', a') - Q(s, a) \big]$$
#
# This is the famous **off-policy** TD update. The trick that makes it work in practice: **ε-greedy** exploration — take the best action `1 - ε` of the time, a random action `ε` of the time. Without exploration, the agent gets stuck.


# %% color=mint title="import random"
# @explain: Run this cell to see the output.
import random

Q = np.zeros((ROWS, COLS, len(ACTIONS)))
ACT_LIST = list(ACTIONS.keys())
EPS = 0.2
LR  = 0.1

def ep_greedy(s, eps):
    if random.random() < eps:
        return random.randint(0, len(ACT_LIST) - 1)
    return int(np.argmax(Q[s[0], s[1]]))

for episode in range(2000):
    s = (0, 0)
    for _ in range(50):
        ai = ep_greedy(s, EPS)
        s2, r, done = step(s, ACT_LIST[ai])
        target = r + GAMMA * (0.0 if done else Q[s2[0], s2[1]].max())
        Q[s[0], s[1], ai] += LR * (target - Q[s[0], s[1], ai])
        s = s2
        if done: break

print("learned policy (greedy direction per cell):")
print(np.vectorize(lambda i: ACT_LIST[i])(np.argmax(Q, axis=-1)))


# %% [markdown] color=peach title="You should see arrows pointing roughly toward the…"
# # You should see arrows pointing roughly toward the…
#
# You should see arrows pointing roughly toward the goal — the agent **learned the optimal policy by interaction**, with no access to `P` or `R` up front. Two key properties of Q-learning:
#
# - **Off-policy**: the data-collection policy (ε-greedy) can be different from the policy we're learning (greedy on `Q`).
# - **Bootstrapping**: the target uses our own `Q` estimate (`max_a Q(s', a')`) — risky in theory, robust in practice.


# %% [markdown] color=violet title="6 · From table to network — DQN"
# # 6 · From table to network — DQN
#
# Tabular Q-learning blows up when `|S|` is huge (Atari pixels, robot joints, language). **Function approximation** with a neural net solves it:
#
# $$Q_\theta(s, a) \approx Q^*(s, a)$$
#
# The training objective is the same TD target, now a regression loss:
#
# …


# %% [markdown] color=amber title="7 · Policy gradients — REINFORCE"
# # 7 · Policy gradients — REINFORCE
#
# Q-learning learns a value function and *derives* a policy. **Policy gradient** methods directly learn a parameterised policy `π_θ(a|s)` (e.g. a small neural net that outputs action logits).
#
# The **policy gradient theorem** says:
#
# $$\nabla_\theta J(\theta) = \mathbb{E}_{\tau \sim \pi_\theta}\!\left[\sum_t \nabla_\theta \log \pi_\theta(a_t|s_t) \cdot G_t\right]$$
#
# …


# %% color=rose title="discounted returns G_t"
# @explain: discounted returns G_t
import gymnasium as gym
import torch, torch.nn as nn, torch.nn.functional as F

env = gym.make("CartPole-v1")
torch.manual_seed(0)

class Policy(nn.Module):
    def __init__(self, in_dim=4, out_dim=2, hidden=64):
        super().__init__()
        self.net = nn.Sequential(nn.Linear(in_dim, hidden), nn.Tanh(),
                                 nn.Linear(hidden, out_dim))
    def forward(self, x):
        return F.softmax(self.net(x), dim=-1)

pi = Policy()
opt = torch.optim.Adam(pi.parameters(), lr=3e-3)

def run_episode():
    obs, _ = env.reset(seed=None)
    log_probs, rewards = [], []
    for _ in range(500):
        x = torch.tensor(obs, dtype=torch.float32)
        probs = pi(x)
        m = torch.distributions.Categorical(probs)
        a = m.sample()
        log_probs.append(m.log_prob(a))
        obs, r, term, trunc, _ = env.step(int(a.item()))
        rewards.append(r)
        if term or trunc: break
    return log_probs, rewards

GAMMA_ = 0.99
for ep in range(200):
    log_probs, rewards = run_episode()
    # discounted returns G_t
    Gs = []
    g = 0
    for r in reversed(rewards):
        g = r + GAMMA_ * g
        Gs.insert(0, g)
    Gs = torch.tensor(Gs, dtype=torch.float32)
    Gs = (Gs - Gs.mean()) / (Gs.std() + 1e-8)   # variance reduction
    loss = -sum(lp * G for lp, G in zip(log_probs, Gs))
    opt.zero_grad(); loss.backward(); opt.step()
    if ep % 20 == 0: print(f"ep {ep:>3}  reward={sum(rewards):.0f}  loss={loss.item():.2f}")

env.close()


# %% [markdown] color=lime title="Read the trace.** Reward should climb from ~20…"
# # Read the trace.** Reward should climb from ~20…
#
# **Read the trace.** Reward should climb from ~20 (random) to ~200-500 over a few hundred episodes. That's CartPole solved by **REINFORCE**.
#
# Notice three things:
# 1. We **standardise** the returns (`G - mean(G) / std(G)`). Pure REINFORCE has notoriously high variance — this is a cheap baseline.
# 2. The loss has a **`-`** in front. PyTorch minimises; we want to *maximise* expected return.
# 3. We need a **full episode** before doing one update — no bootstrap, no TD. Slow.
#
# That last property is what motivates Actor-Critic.


# %% [markdown] color=teal title="8 · Actor-Critic — variance reduction with a critic"
# # 8 · Actor-Critic — variance reduction with a critic
#
# REINFORCE's variance bites at scale. The fix: subtract a **baseline** `b(s)` from the return. The gradient is **unbiased** as long as the baseline doesn't depend on the action.
#
# The natural baseline is `V(s)` — the value function. The remainder `G_t - V(s_t)` is called the **advantage** `A_t`:
#
# $$\nabla_\theta J = \mathbb{E}\!\left[\sum_t \nabla_\theta \log \pi_\theta(a_t|s_t) \cdot \hat{A}_t\right]$$
#
# …


# %% [markdown] color=sky title="9 · PPO — proximal policy optimisation"
# # 9 · PPO — proximal policy optimisation
#
# Vanilla policy gradient has a stability problem: one large gradient step can ruin the policy permanently. **PPO** (Schulman et al., 2017) fixes that with a **clipped surrogate loss**:
#
# $$\mathcal{L}_{PPO}(\theta) = \mathbb{E}_t\!\left[ \min\!\big( \rho_t \hat{A}_t,\; \text{clip}(\rho_t, 1-\epsilon, 1+\epsilon)\hat{A}_t \big) \right]$$
#
# where the **importance ratio** is
#
# …


# %% color=mint title="Minimal PPO update skeleton"
# @explain: Minimal PPO update skeleton — for full code see stable-baselines3 / CleanRL
# @explain: Rollout phase: collect (s, a, r, log_prob_old, value_old) for T steps
# @explain: Then K epochs of mini-batch updates:
# @explain: 1
# @explain: 2
# Minimal PPO update skeleton — for full code see stable-baselines3 / CleanRL.
ppo_sketch = '''
# Rollout phase: collect (s, a, r, log_prob_old, value_old) for T steps
# Then K epochs of mini-batch updates:

for epoch in range(K_EPOCHS):
    for mb in mini_batches(rollout):
        # 1. Compute current policy log-probs + values
        new_logp = policy.log_prob(mb.actions, mb.states)
        new_value = critic(mb.states)

        # 2. Importance ratio
        ratio = (new_logp - mb.old_logp).exp()

        # 3. Advantage (GAE), normalised
        adv = mb.advantages

        # 4. Clipped surrogate
        unclipped = ratio * adv
        clipped   = ratio.clamp(1 - EPS, 1 + EPS) * adv
        policy_loss = -torch.min(unclipped, clipped).mean()

        # 5. Value loss
        value_loss = F.mse_loss(new_value, mb.returns)

        # 6. Entropy bonus (encourages exploration)
        entropy = policy.entropy(mb.states).mean()

        # 7. Total
        loss = policy_loss + 0.5 * value_loss - 0.01 * entropy
        opt.zero_grad(); loss.backward()
        nn.utils.clip_grad_norm_(policy.parameters(), 0.5)
        opt.step()
'''
print(ppo_sketch)


# %% [markdown] color=peach title="That's modern RL in 30 lines.** Production libraries"
# # That's modern RL in 30 lines.** Production libraries
#
# **That's modern RL in 30 lines.** Production libraries — **stable-baselines3**, **CleanRL**, **RLlib**, **TorchRL** — wrap exactly this loop with logging, checkpointing, env vectorisation, and a few extra tricks (advantage clipping, target value clipping, learning-rate annealing).


# %% [markdown] color=violet title="10 · Connecting back to M62 (DPO) and M67 (GRPO)"
# # 10 · Connecting back to M62 (DPO) and M67 (GRPO)
#
# Now you can read M62 and M67 *as RL algorithms*, not as magic LLM tricks.
#
# ### RLHF / PPO (the original)
# 1. **Collect human preferences** `(prompt, chosen, rejected)`.
# 2. Train a **reward model** `r_θ(x, y)` that predicts which side wins (M67 §3).
# 3. Treat **text generation** as RL: state = prompt so far, action = next token, reward = `r_θ(full response) − β · KL(π‖π_ref)`.
# …


# %% [markdown] color=amber title="✅ Recap"
# # ✅ Recap
#
# - RL is **agent + environment + reward**. Find the policy that maximises expected discounted return.
# - **MDPs** make it tractable (Markov property). **Bellman equations** give us the recursion.
# - **Value iteration / policy iteration** solve known-MDP problems.
# - **Q-learning** + ε-greedy learns from interaction; **DQN** scales it to neural nets.
# - **REINFORCE** is the simplest policy-gradient method — high variance, needs full episodes.
# - **Actor-Critic** + **GAE** + parallel envs is the recipe behind every modern RL paper.
# - **PPO** is Actor-Critic + a *clipped surrogate* that prevents catastrophic updates. It's the algorithm RLHF picked.
# …


# %% [markdown] color=lime title="Thanks"
# # End of Module
#
# Next module continues the roadmap.
# Source: https://github.com/kader-xai/data-science-roadmap


