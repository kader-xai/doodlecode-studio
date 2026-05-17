# doodlecode format-version: 2
# Auto-converted from module_26_sql_for_data_science.ipynb
# Open with 📂 Open → press 🎬 Present.


# %% [markdown] color=rose title="Module 26 Sql For Data Science"
# # Module 26 Sql For Data Science
#
# A live walkthrough — one card per concept.
# Use → / ← to step through. Press 🎬 Present to begin.



# %% [markdown] color=sky title="Module 26 — SQL for Data Science"
# # Module 26 — SQL for Data Science
#
# > A working data scientist spends roughly **40% of their day in SQL**. Every BI tool, every database, every modern data warehouse (BigQuery, Snowflake, Redshift, DuckDB) speaks SQL. If Python is the language for *modelling*, SQL is the language for *answering questions*.
#
# This module uses **SQLite** (file-based, no server) so every cell runs anywhere — Colab, your laptop, anywhere. The syntax is 95% portable to Postgres / MySQL / BigQuery / Snowflake.
#
# ### What you'll cover
# 1. Why SQL — and how it fits with Pandas
# …


# %% [markdown] color=mint title="1 · Why SQL — and How It Fits with Pandas"
# # 1 · Why SQL — and How It Fits with Pandas
#
# | Task | Better in SQL | Better in Pandas |
# |---|---|---|
# | Pull data from a database | ✅ | ❌ |
# | Aggregate billions of rows | ✅ | ❌ (won't fit in memory) |
# | Quick exploration / charts | ❌ | ✅ |
# | Reshape / pivot complex tables | ❌ | ✅ |
# …


# %% [markdown] color=peach title="2 · Setup — Build a Demo Database"
# # 2 · Setup — Build a Demo Database
#


# %% color=violet title="import sqlite3"
# @explain: Run this cell to see the output.
import sqlite3, pandas as pd
con = sqlite3.connect(":memory:")     # in-memory database — no file written
cur = con.cursor()

cur.executescript("""
DROP TABLE IF EXISTS customers;
DROP TABLE IF EXISTS products;
DROP TABLE IF EXISTS orders;
DROP TABLE IF EXISTS order_items;

CREATE TABLE customers (
    customer_id INTEGER PRIMARY KEY,
    name TEXT, country TEXT, signup_date TEXT
);
CREATE TABLE products (
    product_id INTEGER PRIMARY KEY,
    name TEXT, category TEXT, price REAL
);
CREATE TABLE orders (
    order_id INTEGER PRIMARY KEY,
    customer_id INTEGER, order_date TEXT
);
CREATE TABLE order_items (
    order_id INTEGER, product_id INTEGER, qty INTEGER
);
""")
print("schema created")


# %% color=amber title="cur.executescript('''"
# @explain: Run this cell to see the output.
cur.executescript("""
INSERT INTO customers VALUES
  (1,'Ada',     'UK',     '2023-01-15'),
  (2,'Linus',   'Finland','2023-02-20'),
  (3,'Grace',   'USA',    '2023-03-10'),
  (4,'Guido',   'NL',     '2023-04-05'),
  (5,'Yukihiro','Japan',  '2024-01-12');

INSERT INTO products VALUES
  (10,'Laptop',     'Hardware', 1200.00),
  (11,'Keyboard',   'Hardware',   80.00),
  (12,'IDE Pro',    'Software',  149.00),
  (13,'Cloud Plan', 'Service',    49.00),
  (14,'GPU Hour',   'Service',     2.50);

INSERT INTO orders VALUES
  (100, 1, '2024-03-01'),
  (101, 2, '2024-03-05'),
  (102, 1, '2024-03-12'),
  (103, 3, '2024-04-02'),
  (104, 4, '2024-04-15'),
  (105, 2, '2024-05-01'),
  (106, 1, '2024-05-20'),
  (107, 5, '2024-06-03');

INSERT INTO order_items VALUES
  (100, 10, 1), (100, 11, 2),
  (101, 12, 1),
  (102, 13, 3),
  (103, 10, 1), (103, 14, 50),
  (104, 12, 2), (104, 13, 1),
  (105, 14, 100),
  (106, 11, 1),
  (107, 13, 6), (107, 14, 200);
""")
con.commit()

def q(sql):
    """Run SQL and return a Pandas DataFrame for nice display."""
    return pd.read_sql_query(sql, con)

q("SELECT name FROM sqlite_master WHERE type='table'")


# %% [markdown] color=rose title="3 · SELECT / FROM / WHERE — the Foundation"
# # 3 · SELECT / FROM / WHERE — the Foundation
#
# The shape of every query:
#
# ```sql
# SELECT  <columns>          -- WHAT you want
# FROM    <table>            -- WHERE the data lives
# WHERE   <conditions>       -- WHICH rows
# …


# %% color=lime title="q('SELECT * FROM customers')"
# @explain: Run this cell to see the output.
q("SELECT * FROM customers")


# %% color=teal title="q('SELECT name"
# @explain: Run this cell to see the output.
q("SELECT name, country FROM customers WHERE country = 'UK'")


# %% color=sky title="q('SELECT name"
# @explain: Run this cell to see the output.
q("SELECT name, signup_date FROM customers ORDER BY signup_date DESC LIMIT 3")


# %% [markdown] color=mint title="Comparison & logical operators (same as Python, slightly different syntax)"
# # Comparison & logical operators (same as Python, slightly different syntax)
#
# | SQL | Python |
# |---|---|
# | `=` | `==` |
# | `<>` or `!=` | `!=` |
# | `AND` / `OR` / `NOT` | `and` / `or` / `not` |
# | `IN ('UK','USA')` | `country in {'UK','USA'}` |
# …


# %% color=peach title="q('SELECT name, country FROM customers WHERE country IN"
# @explain: Run this cell to see the output.
q("SELECT name, country FROM customers WHERE country IN ('UK','USA') AND name LIKE 'A%'")


# %% [markdown] color=violet title="4 · Aggregations — `COUNT`, `SUM`, `AVG`, `GROUP BY`, `HAVING`"
# # 4 · Aggregations — `COUNT`, `SUM`, `AVG`, `GROUP BY`, `HAVING`
#


# %% color=amber title="q('''"
# @explain: Run this cell to see the output.
q("""
SELECT
  COUNT(*)             AS n_customers,
  COUNT(DISTINCT country) AS n_countries
FROM customers
""")


# %% color=rose title="q('''"
# @explain: Run this cell to see the output.
q("""
SELECT country, COUNT(*) AS n_customers
FROM customers
GROUP BY country
ORDER BY n_customers DESC
""")


# %% [markdown] color=lime title="`HAVING` vs `WHERE`:** `WHERE` filters ROWS…"
# # `HAVING` vs `WHERE`:** `WHERE` filters ROWS…
#
# **`HAVING` vs `WHERE`:** `WHERE` filters ROWS *before* aggregation, `HAVING` filters GROUPS *after*. You almost always want this distinction on interview questions.


# %% color=teal title="q('''"
# @explain: Run this cell to see the output.
q("""
SELECT country, COUNT(*) AS n
FROM customers
GROUP BY country
HAVING COUNT(*) >= 1
ORDER BY n DESC
""")


# %% [markdown] color=sky title="5 · JOINs — Combining Tables"
# # 5 · JOINs — Combining Tables
#
# Picture two tables side by side, glued on a shared key:
#
# ```
# customers           orders
# +------+-----+      +------+----------+
# | id=1 | Ada |  ←→  | 100  | cust_id=1|
# …


# %% color=mint title="q('''"
# @explain: Run this cell to see the output.
q("""
SELECT o.order_id, o.order_date, c.name AS customer
FROM orders o
INNER JOIN customers c ON c.customer_id = o.customer_id
ORDER BY o.order_date
""")


# %% [markdown] color=peach title="Multi-table join — orders × customers × items × products"
# # Multi-table join — orders × customers × items × products
#
# The most common real-world query: *"what did each customer actually buy?"*


# %% color=violet title="q('''"
# @explain: Run this cell to see the output.
q("""
SELECT
  c.name      AS customer,
  o.order_id,
  p.name      AS product,
  oi.qty,
  p.price,
  oi.qty * p.price AS line_total
FROM orders o
JOIN customers   c  ON c.customer_id = o.customer_id
JOIN order_items oi ON oi.order_id   = o.order_id
JOIN products    p  ON p.product_id  = oi.product_id
ORDER BY o.order_date, o.order_id
""")


# %% [markdown] color=amber title="LEFT JOIN — 'who has zero orders?'"
# # LEFT JOIN — "who has zero orders?"
#
# A customer with **no orders** would get dropped by an INNER JOIN. LEFT JOIN keeps them with NULLs.


# %% color=rose title="q('''"
# @explain: Run this cell to see the output.
q("""
SELECT c.name, COUNT(o.order_id) AS n_orders
FROM customers c
LEFT JOIN orders o ON o.customer_id = c.customer_id
GROUP BY c.name
ORDER BY n_orders DESC
""")


# %% [markdown] color=lime title="6 · Subqueries vs CTEs (`WITH ...`)"
# # 6 · Subqueries vs CTEs (`WITH ...`)
#
# Both let you build a query in steps. CTEs read top-to-bottom — much easier on the eyes.


# %% color=teal title="Subquery"
# @explain: Subquery — nested, hard to read past 2 levels
# Subquery — nested, hard to read past 2 levels
q("""
SELECT name, country FROM customers
WHERE customer_id IN (
    SELECT customer_id FROM orders
    GROUP BY customer_id HAVING COUNT(*) >= 2
)
""")


# %% color=sky title="Same query as a CTE"
# @explain: Same query as a CTE — reads top-to-bottom
# Same query as a CTE — reads top-to-bottom
q("""
WITH frequent_buyers AS (
    SELECT customer_id
    FROM orders
    GROUP BY customer_id
    HAVING COUNT(*) >= 2
)
SELECT c.name, c.country
FROM customers c
JOIN frequent_buyers f ON f.customer_id = c.customer_id
""")


# %% [markdown] color=mint title="Industry rule of thumb:** when a query has more…"
# # Industry rule of thumb:** when a query has more…
#
# **Industry rule of thumb:** when a query has more than one subquery or you have to break it into steps, use CTEs. They're easier to read, debug, and modify.


# %% [markdown] color=peach title="7 · Window Functions — the SQL Superpower"
# # 7 · Window Functions — the SQL Superpower
#
# Window functions compute a value for each row **using a window of related rows** — without collapsing the table the way `GROUP BY` does. The syntax: `<func>() OVER (PARTITION BY ... ORDER BY ...)`.
#
# | Function | What it does |
# |---|---|
# | `ROW_NUMBER()` | unique sequential number per row in window |
# | `RANK()` / `DENSE_RANK()` | rank, with ties handled differently |
# …


# %% color=violet title="Most recent order per customer"
# @explain: Most recent order per customer
# Most recent order per customer
q("""
SELECT customer_id, order_id, order_date,
       ROW_NUMBER() OVER (PARTITION BY customer_id ORDER BY order_date DESC) AS rn
FROM orders
ORDER BY customer_id, rn
""")


# %% color=amber title="Days since the customer's PREVIOUS order"
# @explain: Days since the customer's PREVIOUS order
# Days since the customer's PREVIOUS order
q("""
SELECT
  customer_id, order_date,
  LAG(order_date) OVER (PARTITION BY customer_id ORDER BY order_date) AS prev_date,
  julianday(order_date) - julianday(LAG(order_date) OVER (PARTITION BY customer_id ORDER BY order_date)) AS days_since_prev
FROM orders
""")


# %% color=rose title="Running revenue total per customer"
# @explain: Running revenue total per customer
# Running revenue total per customer
q("""
WITH line AS (
    SELECT o.customer_id, o.order_date, oi.qty * p.price AS amount
    FROM orders o
    JOIN order_items oi ON oi.order_id = o.order_id
    JOIN products p ON p.product_id = oi.product_id
)
SELECT customer_id, order_date, amount,
       SUM(amount) OVER (PARTITION BY customer_id ORDER BY order_date) AS running_total
FROM line
ORDER BY customer_id, order_date
""")


# %% [markdown] color=lime title="8 · Date Functions + `CASE WHEN`"
# # 8 · Date Functions + `CASE WHEN`
#
# SQLite uses string dates with `julianday()` and `strftime()`. Postgres / BigQuery have richer functions but the patterns are the same.


# %% color=teal title="q('''"
# @explain: Run this cell to see the output.
q("""
SELECT
  order_id,
  order_date,
  strftime('%Y',  order_date) AS year,
  strftime('%m',  order_date) AS month,
  strftime('%w',  order_date) AS weekday,
  julianday('now') - julianday(order_date) AS days_ago
FROM orders
LIMIT 5
""")


# %% [markdown] color=sky title="`CASE WHEN` — SQL's if/elif/else"
# # `CASE WHEN` — SQL's if/elif/else
#


# %% color=mint title="q('''"
# @explain: Run this cell to see the output.
q("""
SELECT
  customer_id,
  COUNT(*) AS n_orders,
  CASE
    WHEN COUNT(*) >= 3 THEN 'whale'
    WHEN COUNT(*) = 2  THEN 'repeat'
    WHEN COUNT(*) = 1  THEN 'one-time'
    ELSE 'never'
  END AS segment
FROM orders
GROUP BY customer_id
ORDER BY n_orders DESC
""")


# %% [markdown] color=peach title="9 · SQL ↔ Pandas"
# # 9 · SQL ↔ Pandas
#
# You'll constantly move between them. Two patterns to memorise:


# %% color=violet title="1) Pull a query result into a DataFrame"
# @explain: 1) Pull a query result into a DataFrame
# 1) Pull a query result into a DataFrame
df = pd.read_sql_query("""
SELECT c.country, COUNT(*) AS n_orders
FROM orders o JOIN customers c ON c.customer_id = o.customer_id
GROUP BY c.country
""", con)
print(df)

import matplotlib.pyplot as plt
df.set_index("country")["n_orders"].plot.bar(title="Orders by country")
plt.show()


# %% color=amber title="2) Push a Pandas DataFrame INTO the database (e.g"
# @explain: 2) Push a Pandas DataFrame INTO the database (e.g
# 2) Push a Pandas DataFrame INTO the database (e.g. for joining with native tables)
new = pd.DataFrame({"customer_id":[1,2,3], "is_premium":[1,0,1]})
new.to_sql("premium", con, if_exists="replace", index=False)

q("""
SELECT c.name, p.is_premium
FROM customers c
JOIN premium p ON p.customer_id = c.customer_id
""")


# %% [markdown] color=rose title="10 · Practice — Try Yourself"
# # 10 · Practice — Try Yourself
#
# Use the database we built. Each exercise has a hidden answer below it.
#
# **Ex 26.1** — Total revenue per CUSTOMER, sorted descending.
# **Ex 26.2** — Top 3 PRODUCTS by total quantity sold.
# **Ex 26.3** — For each customer, their LATEST order date and the number of days since (use `julianday('now')`).
# **Ex 26.4** — Customers who have NEVER bought a 'Service' product. (Hint: LEFT JOIN + filter on NULL, or `NOT IN`.)
# …


# %% color=lime title="Try yours first"
# @explain: Try yours first, then peek
# @explain: 26.1
# @explain: 26.2
# @explain: 26.3
# @explain: 26.4
# Try yours first, then peek

# 26.1
print("\n--- 26.1 ---")
print(q("""
SELECT c.name, ROUND(SUM(oi.qty * p.price), 2) AS revenue
FROM customers c
JOIN orders o      ON o.customer_id = c.customer_id
JOIN order_items oi ON oi.order_id  = o.order_id
JOIN products p     ON p.product_id  = oi.product_id
GROUP BY c.name
ORDER BY revenue DESC
"""))

# 26.2
print("\n--- 26.2 ---")
print(q("""
SELECT p.name, SUM(oi.qty) AS units_sold
FROM products p
JOIN order_items oi ON oi.product_id = p.product_id
GROUP BY p.name
ORDER BY units_sold DESC
LIMIT 3
"""))

# 26.3
print("\n--- 26.3 ---")
print(q("""
SELECT c.name, MAX(o.order_date) AS last_order,
       julianday('now') - julianday(MAX(o.order_date)) AS days_ago
FROM customers c
JOIN orders o ON o.customer_id = c.customer_id
GROUP BY c.name
ORDER BY days_ago
"""))

# 26.4
print("\n--- 26.4 ---")
print(q("""
SELECT name FROM customers
WHERE customer_id NOT IN (
    SELECT DISTINCT o.customer_id
    FROM orders o
    JOIN order_items oi ON oi.order_id   = o.order_id
    JOIN products p     ON p.product_id   = oi.product_id
    WHERE p.category = 'Service'
)
"""))

# 26.5
print("\n--- 26.5 ---")
print(q("""
WITH monthly AS (
  SELECT strftime('%Y-%m', o.order_date) AS month,
         oi.qty * p.price AS amount,
         o.order_id
  FROM orders o
  JOIN order_items oi ON oi.order_id = o.order_id
  JOIN products p     ON p.product_id = oi.product_id
)
SELECT month,
       ROUND(SUM(amount), 2) AS revenue,
       COUNT(DISTINCT order_id) AS n_orders,
       ROUND(SUM(SUM(amount)) OVER (ORDER BY month), 2) AS running_total
FROM monthly
GROUP BY month
"""))


# %% [markdown] color=teal title="11 · Where This Scales"
# # 11 · Where This Scales
#
# You now have ~95% of the SQL you'll write at most jobs. The remaining 5% is **dialect-specific** and learned on the job:
#
# | Database | Things specific to it |
# |---|---|
# | **PostgreSQL** | `JSONB` operators, `array` type, `LATERAL` joins, full-text search |
# | **BigQuery** | partitioned tables, `STRUCT` / `ARRAY` types, `APPROX_*` functions, ML inside SQL (`CREATE MODEL`) |
# …


# %% [markdown] color=lime title="Thanks"
# # End of Module
#
# Next module continues the roadmap.
# Source: https://github.com/kader-xai/data-science-roadmap


