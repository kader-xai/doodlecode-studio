# doodlecode format-version: 3
# notebook: Sigmoid Neuron — a visual walk-through

# %% kind=markdown id=c0 x=120.0 y=80.0 w=620.0
# @title: Welcome
# @link_to: c1

# Building a Sigmoid Neuron 🧠

A one-stop **visual** walk-through. This deck mixes:

- **Code** you can run live
- **Reveal steps** that type code in during the talk
- **Charts** for intuition (line + bar)
- A **flowchart** of the forward pass
- A **live browser** demo

Hit **F5 / Shift+P** to present, then **→** to advance.

# %% kind=code id=c1 x=120.0 y=420.0 w=600.0
# @title: Build it live (press ✨ Reveal)
# @link_to: c2
# @explain: Run shows the base. Press ✨ Reveal (or Shift+R) to type in the function, then the test loop.
# @reveal: def sigmoid(x):\n    return 1 / (1 + math.exp(-x))
# @reveal: for x in (-2, -1, 0, 1, 2):\n    print(f"sigmoid({x:+}) = {sigmoid(x):.3f}")

import math

# We'll build a sigmoid neuron step by step.
print("Base ready — press ✨ Reveal to add the function")

# %% kind=diagram id=c2 x=120.0 y=900.0 w=620.0 h=380.0
# @title: Training loss (line chart)
# @diagram_kind: doodle
# @link_to: c3
# @explain: Two series, hand-drawn. Trends jump out instantly.

chart: Training loss
line Train: 0.92, 0.61, 0.43, 0.31, 0.24, 0.2
line Val: 0.95, 0.7, 0.55, 0.46, 0.42, 0.4

# %% kind=diagram id=c3 x=120.0 y=1380.0 w=620.0 h=360.0
# @title: Forward pass (flowchart)
# @diagram_kind: doodle
# @link_to: c4

flowchart
Inputs --> Weights
Weights --> Sum
Sum --> Sigmoid
Sigmoid --> Output

# %% kind=diagram id=c4 x=120.0 y=1840.0 w=620.0 h=320.0
# @title: Activations compared (bar chart)
# @diagram_kind: doodle
# @link_to: c5

chart: Output at x = 1.5
ReLU: 9
Sigmoid: 5
Tanh: 6

# %% kind=code id=c5 x=120.0 y=2260.0 w=600.0
# @title: The point of sigmoid
# @link_to: c6
# @explain: sigmoid(0) = 0.5 exactly — the neuron is perfectly undecided at the origin.

import math

def sigmoid(x):
    return 1 / (1 + math.exp(-x))

print("sigmoid(0)  =", sigmoid(0))
print("sigmoid(2)  =", round(sigmoid(2), 3))
print("sigmoid(-2) =", round(sigmoid(-2), 3))

# %% kind=browser id=c6 x=120.0 y=2640.0 w=720.0 h=460.0
# @title: Live demo in the deck
# @link_to: c7

https://example.com

# %% kind=markdown id=c7 x=120.0 y=3180.0 w=620.0
# @title: Recap

## What we just did 🎉

- Built `sigmoid` **live** with reveal steps
- Read the **loss curve** at a glance (line chart)
- Saw the **forward pass** as a flow
- Compared activations with a **bar chart**
- Embedded a **live page** — all in one `.py` file

> Everything here round-trips through this single file. Drag it back in
> any time and the whole deck comes with it.
