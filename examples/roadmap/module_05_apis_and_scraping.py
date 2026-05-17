# doodlecode format-version: 2
# Auto-converted from module_05_apis_and_scraping.ipynb
# Open with 📂 Open → press 🎬 Present.


# %% [markdown] color=rose title="Module 05 Apis And Scraping"
# # Module 05 Apis And Scraping
#
# A live walkthrough — one card per concept.
# Use → / ← to step through. Press 🎬 Present to begin.



# %% [markdown] color=sky title="Module 5 — APIs, Web Scraping & Stock Data"
# # Module 5 — APIs, Web Scraping & Stock Data
#
# *IBM Python for Data Science · Module 5 of 16 — last Python-foundations module*
#
# Most useful data isn't on your disk. It's behind an HTTP endpoint or on a web page. This module gives you the three patterns that cover ~95% of cases:
#
# 1. **REST API** — `requests.get(url).json()`
# 2. **Web tables** — `pd.read_html(url)`
# 3. **Messy HTML** — `BeautifulSoup`
# …


# %% color=mint title="!pip -q install requests beautifulsoup4 lxml…"
# @explain: Run this cell to see the output.
!pip -q install requests beautifulsoup4 lxml yfinance pandas matplotlib


# %% [markdown] color=peach title="1. HTTP in 60 seconds"
# # 1. HTTP in 60 seconds
#
# Every API call is an HTTP request:
#
# | Verb | Meaning |
# |---|---|
# | **GET** | "give me data" — most APIs |
# | **POST** | "here's data, do something" — login, create |
# …


# %% [markdown] color=violet title="2. REST APIs with `requests`"
# # 2. REST APIs with `requests`
#


# %% color=amber title="Public"
# @explain: Public, no-auth API
import requests

# Public, no-auth API
r = requests.get("https://api.github.com/users/torvalds", timeout=10)
print("status:", r.status_code)

data = r.json()
print(f"name: {data['name']}, public repos: {data['public_repos']}")


# %% [markdown] color=rose title="Query parameters and headers"
# # Query parameters and headers
#


# %% color=lime title="Query params via the `params=` dict"
# @explain: Query params via the `params=` dict (proper URL-encoding for free)
# Query params via the `params=` dict (proper URL-encoding for free)
r = requests.get(
    "https://api.github.com/search/repositories",
    params={"q": "language:python stars:>50000", "per_page": 5},
    headers={"Accept": "application/vnd.github+json", "User-Agent": "minitorch-course"},
    timeout=10,
)
r.raise_for_status()                # raises on 4xx/5xx
items = r.json()["items"]
for repo in items:
    print(f"{repo['full_name']:<40} ★ {repo['stargazers_count']:,}")


# %% [markdown] color=teal title="Robust API calls — retry, timeout, error handling"
# # Robust API calls — retry, timeout, error handling
#


# %% color=sky title="def safe_get_json(url"
# @explain: Run this cell to see the output.
def safe_get_json(url, **kwargs):
    """A defensive wrapper for one-off API calls."""
    try:
        r = requests.get(url, timeout=10, **kwargs)
        r.raise_for_status()
        return r.json()
    except requests.Timeout:
        print(f"timeout: {url}")
    except requests.HTTPError as e:
        print(f"HTTP {e.response.status_code}: {url}")
    except requests.RequestException as e:
        print(f"network error: {e}")

print(safe_get_json("https://api.github.com/users/torvalds")["login"])


# %% [markdown] color=mint title="3. HTML basics for scraping"
# # 3. HTML basics for scraping
#
# A web page is a tree of **tags** with **attributes** and **text**:
#
# ```html
# <div class="post" id="p1">
#   <h2>Title</h2>
#   <p>Some <a href="/x">link</a> text.</p>
# …


# %% [markdown] color=peach title="4. BeautifulSoup — parsing & navigating"
# # 4. BeautifulSoup — parsing & navigating
#


# %% color=violet title="Easy tag access"
# @explain: Easy tag access
# @explain: find / find_all
from bs4 import BeautifulSoup
import requests

html = requests.get("https://example.com", timeout=10).text
soup = BeautifulSoup(html, "lxml")

# Easy tag access
print("title:", soup.title.string)
print("h1:", soup.h1.get_text())
print("first link href:", soup.a["href"])

# find / find_all
for p in soup.find_all("p"):
    print("p:", p.get_text()[:80])


# %% color=amber title="CSS selectors"
# @explain: CSS selectors — usually the cleanest way
# CSS selectors — usually the cleanest way
for link in soup.select("a"):
    print(link.get_text(), "->", link.get("href"))


# %% [markdown] color=rose title="A real scrape — extract H1s from a Wikipedia page"
# # A real scrape — extract H1s from a Wikipedia page
#


# %% color=lime title="Page title"
# @explain: Page title
# @explain: All section headings on the page
url  = "https://en.wikipedia.org/wiki/Python_(programming_language)"
soup = BeautifulSoup(requests.get(url, timeout=10).text, "lxml")

# Page title
print("page:", soup.find(id="firstHeading").get_text())

# All section headings on the page
for h in soup.select("h2, h3")[:8]:
    print("-", h.get_text(strip=True))


# %% [markdown] color=teal title="5. Scraping tables with `pd.read_html`"
# # 5. Scraping tables with `pd.read_html`
#
# If the data is in an HTML `<table>`, **don't reach for BeautifulSoup**. `pandas.read_html` parses every table on a page into a list of DataFrames in one line.


# %% color=sky title="import pandas as pd"
# @explain: Run this cell to see the output.
import pandas as pd
url = "https://en.wikipedia.org/wiki/List_of_largest_companies_by_revenue"
tables = pd.read_html(url)
print(f"{len(tables)} tables found; first one preview:")
print(tables[0].head())


# %% [markdown] color=mint title="6. Stock prices with `yfinance`"
# # 6. Stock prices with `yfinance`
#
# `yfinance` is a free wrapper around Yahoo Finance. You don't need an API key.


# %% color=peach title="import yfinance as yf"
# @explain: Run this cell to see the output.
import yfinance as yf
import pandas as pd

tsla = yf.Ticker("TSLA")
hist = tsla.history(period="1y")[["Open","High","Low","Close","Volume"]]
print(hist.tail())


# %% color=violet title="import matplotlib.pyplot as plt"
# @explain: Run this cell to see the output.
import matplotlib.pyplot as plt
hist["Close"].plot(figsize=(9,3), title="TSLA — daily close (1y)")
plt.ylabel("USD"); plt.show()


# %% [markdown] color=amber title="Historical periods"
# # Historical periods
#


# %% color=rose title="Common periods:…"
# @explain: Common periods: '1d','5d','1mo','3mo','6mo','1y','5y','max'
# Common periods: '1d','5d','1mo','3mo','6mo','1y','5y','max'
gme = yf.Ticker("GME").history(period="6mo")[["Close"]]
print(gme.head(3))
print(gme.describe())


# %% [markdown] color=lime title="7. Revenue extraction — quarterly & annual financials"
# # 7. Revenue extraction — quarterly & annual financials
#
# `yfinance` exposes the income statement, balance sheet, and cash flow.


# %% color=teal title="Annual income statement"
# @explain: Annual income statement (transposed so dates are rows)
tsla = yf.Ticker("TSLA")

# Annual income statement (transposed so dates are rows)
income = tsla.financials.T.sort_index()
print("Tesla — annual revenue:")
revenue = income[["Total Revenue"]].dropna()
print(revenue)


# %% color=sky title="Quarterly version"
# @explain: Quarterly version
# Quarterly version
qrev = tsla.quarterly_financials.T[["Total Revenue"]].dropna().sort_index()
print("Tesla — quarterly revenue:")
print(qrev.tail(8))


# %% [markdown] color=mint title="8. Tesla vs GameStop — putting it together"
# # 8. Tesla vs GameStop — putting it together
#
# The classic IBM final exercise: pull both companies' close prices and revenue, plot them on the same figure.


# %% color=peach title="import yfinance as yf"
# @explain: Run this cell to see the output.
import yfinance as yf, pandas as pd, matplotlib.pyplot as plt

tickers = {"TSLA": "Tesla", "GME": "GameStop"}
prices, revenues = {}, {}
for sym in tickers:
    t = yf.Ticker(sym)
    prices[sym]   = t.history(period="2y")["Close"]
    revenues[sym] = t.financials.T["Total Revenue"].dropna().sort_index()

fig, axes = plt.subplots(2, 2, figsize=(12, 6))
for i, (sym, name) in enumerate(tickers.items()):
    prices[sym].plot(ax=axes[0, i], title=f"{name} ({sym}) — close (2y)")
    revenues[sym].plot.bar(ax=axes[1, i], title=f"{name} — annual revenue")
    axes[1, i].set_xticklabels([str(d.year) for d in revenues[sym].index], rotation=0)
plt.tight_layout(); plt.show()


# %% [markdown] color=violet title="9. Practice — try before you peek"
# # 9. Practice — try before you peek
#
# 1. Use `requests` to fetch the latest Bitcoin price from `https://api.coindesk.com/v1/bpi/currentprice.json` and print the USD rate.
# 2. Scrape the *Programming language* table from Wikipedia and find how many "languages" appear with "Python" in the row text. (Hint: `pd.read_html` then string filter.)
# 3. Use `yfinance` to compute Apple's (`AAPL`) total return % over the last year.
# 4. Make a 2-line chart comparing **TSLA** and **GME** normalised to start at 100, over 1 year.


# %% color=amber title="1)"
# @explain: 1)
# @explain: 2) — finding tables on a Python article
# @explain: 3)
# @explain: 4)
import requests, pandas as pd, yfinance as yf, matplotlib.pyplot as plt

# 1)
btc = requests.get("https://api.coindesk.com/v1/bpi/currentprice.json", timeout=10).json()
print("BTC USD:", btc["bpi"]["USD"]["rate"])

# 2) — finding tables on a Python article
url = "https://en.wikipedia.org/wiki/Python_(programming_language)"
tabs = pd.read_html(url)
hits = sum(1 for t in tabs if t.astype(str).apply(lambda c: c.str.contains("Python", case=False, na=False)).any().any())
print(f"tables that mention 'Python': {hits} / {len(tabs)}")

# 3)
aapl = yf.Ticker("AAPL").history(period="1y")["Close"]
print(f"AAPL 1y total return: {(aapl.iloc[-1]/aapl.iloc[0]-1)*100:.1f}%")

# 4)
both = pd.concat({"TSLA": yf.Ticker("TSLA").history(period="1y")["Close"],
                  "GME":  yf.Ticker("GME").history(period="1y")["Close"]}, axis=1).dropna()
norm = both / both.iloc[0] * 100
norm.plot(figsize=(9,3), title="TSLA vs GME — normalised to 100"); plt.show()


# %% [markdown] color=rose title="Recap — what you can now do"
# # Recap — what you can now do
#
# ✅ Make GET requests with query params, headers, and proper error handling
# ✅ Parse HTML with BeautifulSoup using tag, attribute, and CSS-selector queries
# ✅ One-line scrape of HTML tables with `pd.read_html`
# ✅ Pull historical prices and financial statements with `yfinance`
# ✅ Build a multi-panel chart that combines API data and scraped data
#
# …


# %% [markdown] color=lime title="Thanks"
# # End of Module
#
# Next module continues the roadmap.
# Source: https://github.com/kader-xai/data-science-roadmap


