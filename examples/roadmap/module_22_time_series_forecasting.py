# doodlecode format-version: 2
# Auto-converted from module_22_time_series_forecasting.ipynb
# Open with 📂 Open → press 🎬 Present.


# %% [markdown] color=rose title="Module 22 Time Series Forecasting"
# # Module 22 Time Series Forecasting
#
# A live walkthrough — one card per concept.
# Use → / ← to step through. Press 🎬 Present to begin.



# %% [markdown] color=sky title="Module 22 — Time-Series Forecasting"
# # Module 22 — Time-Series Forecasting
#
# *When rows have an order. Sales by day, sensor readings by minute, stock prices by tick.*
#
# Everything in M11–M16 quietly assumed your rows were **independent**. For time-series that assumption breaks: yesterday's value tells you a lot about today's. This module covers the three workhorse forecasting approaches:
#
# 1. **Classical statistics** — ARIMA (the textbook choice for 50 years)
# 2. **Business-friendly** — Facebook Prophet (handles seasonality + holidays out of the box)
# 3. **Neural** — LSTM (when patterns are complex and you have enough data)
# …


# %% color=mint title="!pip -q install prophet pmdarima statsmodels"
# @explain: Run this cell to see the output.
!pip -q install prophet pmdarima statsmodels
import numpy as np, pandas as pd, matplotlib.pyplot as plt
import warnings; warnings.filterwarnings("ignore")
np.random.seed(0)


# %% [markdown] color=peach title="1. What makes time-series different"
# # 1. What makes time-series different
#
# | Standard ML assumption | Time-series reality |
# |---|---|
# | Rows are i.i.d. | Today depends on yesterday (autocorrelation) |
# | You can shuffle and train/test split randomly | You CAN'T shuffle — train must be earlier than test |
# | Features are simultaneous | Features include **lags** of the target itself |
# | Cross-validation = K random folds | Walk-forward / rolling-origin only |
# …


# %% [markdown] color=violet title="2. Decomposition — what's inside a time series"
# # 2. Decomposition — what's inside a time series
#
# A time series typically has three components:
#
# $$y_t = \text{trend}_t + \text{seasonality}_t + \text{residual}_t$$
#
# (Or multiplicative, depending on whether amplitude grows with the level.)
#
# …


# %% color=amber title="Build a synthetic series with trend + weekly…"
# @explain: Build a synthetic series with trend + weekly seasonality + noise
# Build a synthetic series with trend + weekly seasonality + noise
dates = pd.date_range("2022-01-01", periods=730)              # 2 years
t = np.arange(len(dates))
trend = 0.05 * t                                               # rising
seasonality = 5 * np.sin(2*np.pi * t/7)                        # weekly cycle
noise = np.random.normal(0, 1, len(t))
y = 50 + trend + seasonality + noise

ts = pd.Series(y, index=dates, name="value")
ts.plot(figsize=(10, 3), title="Synthetic series (trend + weekly + noise)")
plt.show()


# %% color=rose title="from statsmodels.tsa.seasonal import seasonal_decompose"
# @explain: Run this cell to see the output.
from statsmodels.tsa.seasonal import seasonal_decompose
decomp = seasonal_decompose(ts, model="additive", period=7)
fig = decomp.plot(); fig.set_size_inches(10, 7); plt.show()


# %% [markdown] color=lime title="3. Stationarity — does the distribution drift?"
# # 3. Stationarity — does the distribution drift?
#
# A series is **stationary** if its mean, variance, and autocorrelation **don't change over time**. Many classical models (ARIMA) require stationarity.
#
# **Test:** Augmented Dickey-Fuller (ADF). p-value < 0.05 → stationary.
# **Fix when not stationary:** **differencing** — replace `y_t` with `y_t - y_{t-1}`. This usually removes a linear trend.


# %% color=teal title="from statsmodels.tsa.stattools import adfuller"
# @explain: Run this cell to see the output.
from statsmodels.tsa.stattools import adfuller

def adf(s, name):
    p = adfuller(s.dropna())[1]
    verdict = "STATIONARY" if p < 0.05 else "non-stationary"
    print(f"{name:12} ADF p={p:.4f} → {verdict}")

adf(ts,            "raw")
adf(ts.diff(),     "diff(1)")     # first difference removes the trend
adf(ts.diff().diff(), "diff(2)")   # second difference

ts.diff().plot(figsize=(10, 3), title="First difference — flat mean now"); plt.show()


# %% [markdown] color=sky title="4. ARIMA(p, d, q)"
# # 4. ARIMA(p, d, q)
#
# Three knobs:
#
# - **AR(p)** — `y_t` is regressed on its **p** previous values
# - **I(d)** — apply `d` differences to make it stationary
# - **MA(q)** — model the residual as a moving average of the last `q` errors
#
# …


# %% color=mint title="from pmdarima import auto_arima"
# @explain: Run this cell to see the output.
from pmdarima import auto_arima

train, test = ts[:-30], ts[-30:]
model = auto_arima(train, seasonal=True, m=7,         # weekly seasonality
                   suppress_warnings=True, stepwise=True, error_action="ignore")
print(model.summary().tables[0])

pred = pd.Series(model.predict(n_periods=30), index=test.index)
mae = (pred - test).abs().mean()
print(f"\nARIMA MAE on 30-day forecast: {mae:.2f}")

ax = ts[-90:].plot(figsize=(10, 3), label="actual")
pred.plot(ax=ax, label="ARIMA forecast", color="red")
ax.legend(); ax.set_title("ARIMA forecast"); plt.show()


# %% [markdown] color=peach title="5. Prophet — Facebook's 'just works' forecaster"
# # 5. Prophet — Facebook's "just works" forecaster
#
# Prophet was built at Meta for business-friendly forecasting. It models:
#
# $$y(t) = \text{trend}(t) + \text{seasonality}(t) + \text{holidays}(t) + \epsilon$$
#
# It handles missing data, multiple seasonalities, and holidays out of the box. Great default when you don't have time to tune ARIMA.


# %% color=violet title="Prophet needs columns named 'ds'"
# @explain: Prophet needs columns named 'ds' (date) and 'y' (value)
from prophet import Prophet

# Prophet needs columns named 'ds' (date) and 'y' (value)
df = ts.reset_index().rename(columns={"index":"ds", "value":"y"})
df_train, df_test = df[:-30], df[-30:]

m = Prophet(daily_seasonality=False, weekly_seasonality=True, yearly_seasonality=False)
m.fit(df_train)

future = m.make_future_dataframe(periods=30)
fc = m.predict(future)

prophet_pred = fc[["ds","yhat"]].set_index("ds").iloc[-30:]
mae = (prophet_pred["yhat"].values - df_test["y"].values).mean()
print(f"Prophet MAE on 30-day forecast: {abs(mae):.2f}")

fig = m.plot(fc); fig.set_size_inches(10, 4); plt.title("Prophet forecast"); plt.show()
fig2 = m.plot_components(fc); fig2.set_size_inches(10, 4); plt.show()


# %% [markdown] color=amber title="6. LSTM — neural sequence model"
# # 6. LSTM — neural sequence model
#
# For complex patterns or non-linear seasonality, a recurrent network can do better. We'll build a simple LSTM in PyTorch.
#
# **Key idea:** turn the series into windows. Given the last `n` values, predict the next one.


# %% color=rose title="Normalise to [0"
# @explain: Normalise to [0, 1]
# @explain: Create sliding windows (n past steps -> next step)
# @explain: Train/test split — chronological, never random
import torch, torch.nn as nn

# Normalise to [0, 1]
v = ts.values.astype("float32")
v_min, v_max = v.min(), v.max()
v_norm = (v - v_min) / (v_max - v_min)

# Create sliding windows (n past steps -> next step)
N = 14
def make_windows(arr, n):
    X = np.array([arr[i:i+n] for i in range(len(arr)-n)])
    y = arr[n:]
    return torch.from_numpy(X).unsqueeze(-1), torch.from_numpy(y).unsqueeze(-1)

X, y = make_windows(v_norm, N)
print("X shape:", X.shape, "y shape:", y.shape)   # (samples, seq, 1)

# Train/test split — chronological, never random
split = len(X) - 30
X_tr, X_te = X[:split], X[split:]
y_tr, y_te = y[:split], y[split:]


# %% color=lime title="Evaluate"
# @explain: Evaluate
class LSTMForecaster(nn.Module):
    def __init__(self, hidden=32, layers=1):
        super().__init__()
        self.lstm = nn.LSTM(input_size=1, hidden_size=hidden, num_layers=layers, batch_first=True)
        self.head = nn.Linear(hidden, 1)
    def forward(self, x):
        out, _ = self.lstm(x)         # (B, T, hidden)
        return self.head(out[:, -1])   # only the last timestep -> (B, 1)

model = LSTMForecaster()
opt = torch.optim.Adam(model.parameters(), lr=1e-3)
loss_fn = nn.MSELoss()

for epoch in range(200):
    model.train()
    pred = model(X_tr)
    loss = loss_fn(pred, y_tr)
    opt.zero_grad(); loss.backward(); opt.step()
    if epoch % 50 == 0:
        print(f"epoch {epoch:3d}  loss={loss.item():.4f}")

# Evaluate
model.eval()
with torch.no_grad():
    pred_test = model(X_te).numpy().flatten()
pred_test = pred_test * (v_max - v_min) + v_min
y_test_real = y_te.numpy().flatten() * (v_max - v_min) + v_min

mae_lstm = np.abs(pred_test - y_test_real).mean()
print(f"\nLSTM MAE on 30-day forecast: {mae_lstm:.2f}")

ax = pd.Series(y_test_real, index=ts.index[-30:]).plot(figsize=(10, 3), label="actual")
pd.Series(pred_test, index=ts.index[-30:]).plot(ax=ax, label="LSTM forecast", color="red")
ax.legend(); ax.set_title("LSTM forecast"); plt.show()


# %% [markdown] color=teal title="7. Walk-forward validation — the honest way to score"
# # 7. Walk-forward validation — the honest way to score
#
# A single train/test split tells you *one number*. **Walk-forward validation** retrains the model many times on growing windows, giving you a distribution of errors that reflects how the model would actually perform in production.
#
# ```
# fold 1:  train [████░░░░░░░░░░] test [██░░░░░░░░]
# fold 2:  train [██████░░░░░░░░] test [██░░░░░░░░]
# fold 3:  train [████████░░░░░░] test [██░░░░░░░░]
# …


# %% color=sky title="from pmdarima import auto_arima"
# @explain: Run this cell to see the output.
from pmdarima import auto_arima

n_folds, h = 5, 14         # 5 folds, 14-day-ahead each
errors = []
total = len(ts) - h * n_folds
for k in range(n_folds):
    end_train = total + k * h
    train = ts[:end_train]
    test  = ts[end_train:end_train + h]
    m = auto_arima(train, seasonal=True, m=7, suppress_warnings=True,
                   stepwise=True, error_action="ignore")
    pred = m.predict(n_periods=h)
    mae = np.abs(pred - test.values).mean()
    errors.append(mae)
    print(f"fold {k+1}  train_size={end_train}  MAE={mae:.2f}")

print(f"\nWalk-forward MAE: {np.mean(errors):.2f} ± {np.std(errors):.2f}")


# %% [markdown] color=mint title="8. Picking the right model"
# # 8. Picking the right model
#
# | Situation | Try first |
# |---|---|
# | Small dataset (< 1k points), one series | **ARIMA / auto_arima** |
# | Business series with holidays + multiple seasonalities | **Prophet** |
# | Many related series (1000s of products), need cross-learning | **LSTM** or modern alternatives (DeepAR, N-BEATS, Temporal Fusion Transformer) |
# | Heavy non-linearity, lots of data, GPU available | **LSTM / Transformer-based** |
# …


# %% [markdown] color=peach title="9. Practice"
# # 9. Practice
#
# 1. Fit auto-ARIMA on Apple stock close prices over the last 2 years (`yfinance`). Forecast 30 days. Plot.
# 2. Use Prophet on the same series. Compare MAE.
# 3. Build a synthetic series with **monthly seasonality** (period=30) instead of weekly. Does ARIMA find the right `m`?
# 4. Implement a **rolling-origin** evaluation function that takes a model and series and returns an array of MAE values across `k` folds with horizon `h`.


# %% color=violet title="1)"
# @explain: 1)
# @explain: 4) rolling-origin
# 1)
import yfinance as yf, pandas as pd
aapl = yf.Ticker("AAPL").history(period="2y")["Close"].asfreq("B").ffill()
train, test = aapl[:-30], aapl[-30:]

m = auto_arima(train, seasonal=False, suppress_warnings=True, stepwise=True, error_action="ignore")
pred = pd.Series(m.predict(n_periods=30), index=test.index)
print(f"ARIMA MAE on AAPL 30-day forecast: {(pred-test).abs().mean():.2f}")
ax = aapl[-120:].plot(figsize=(10,3), label="actual")
pred.plot(ax=ax, color="red", label="ARIMA forecast"); ax.legend(); plt.show()

# 4) rolling-origin
def rolling_origin(series, model_fn, h=30, k=5):
    out = []
    n = len(series) - k * h
    for i in range(k):
        end = n + i * h
        m = model_fn(series[:end])
        p = m.predict(n_periods=h)
        out.append(np.abs(p - series[end:end+h].values).mean())
    return np.array(out)

errs = rolling_origin(aapl,
    lambda s: auto_arima(s, suppress_warnings=True, error_action="ignore", stepwise=True),
    h=30, k=4)
print(f"\nrolling MAE: {errs.round(2)}, mean={errs.mean():.2f}")


# %% [markdown] color=amber title="Recap"
# # Recap
#
# ✅ Recognise time-series specifics — autocorrelation, no shuffling
# ✅ Decompose into trend + seasonality + residual
# ✅ Test stationarity (ADF) and fix it (differencing)
# ✅ Fit ARIMA via `auto_arima`
# ✅ Use Prophet for business-friendly forecasts with holidays
# ✅ Train an LSTM on rolling windows
# …


# %% [markdown] color=lime title="Thanks"
# # End of Module
#
# Next module continues the roadmap.
# Source: https://github.com/kader-xai/data-science-roadmap


