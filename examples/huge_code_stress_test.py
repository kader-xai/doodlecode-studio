# doodlecode format-version: 2
# %% kind=intro color=violet title="Huge code stress test"
# @explain: One big code cell — ~250 lines, pure stdlib. Tests that the
# @explain: kernel handles long programs, deep recursion, lots of stdout,
# @explain: timers, and a final summary table without truncation.
"""Single-cell stress test for DoodleCode Studio.

Drop this whole file in (📂 Open) or paste the body of the cell into a
fresh code cell and press ▶ Run. It exercises:

  * arithmetic & list comprehensions
  * recursion (memoized Fibonacci up to F(120))
  * a tiny class hierarchy + dunder methods
  * itertools / collections / statistics
  * a mini-benchmark with `time.perf_counter`
  * regex, JSON round-trip, base64
  * a 20×20 ASCII Mandelbrot
  * a final summary table

No third-party packages required.
"""

import base64
import json
import math
import random
import re
import statistics
import time
from collections import Counter, defaultdict, deque
from dataclasses import dataclass, field
from functools import lru_cache, reduce
from itertools import accumulate, chain, combinations, groupby, islice

random.seed(42)

# ---------------------------------------------------------------------------
# 1. Arithmetic + comprehensions
# ---------------------------------------------------------------------------
print("=" * 60)
print("1. Arithmetic & comprehensions")
print("=" * 60)

squares = [n * n for n in range(1, 21)]
cubes = {n: n ** 3 for n in range(1, 11)}
primes = [n for n in range(2, 100)
          if all(n % d != 0 for d in range(2, int(math.isqrt(n)) + 1))]
print(f"squares 1..20    : {squares}")
print(f"cubes 1..10      : {cubes}")
print(f"primes <100 ({len(primes)}): {primes}")
print(f"sum of squares   : {sum(squares)}")
print(f"product via reduce: {reduce(lambda a, b: a * b, range(1, 11))}")
print()

# ---------------------------------------------------------------------------
# 2. Recursion with memoization
# ---------------------------------------------------------------------------
print("=" * 60)
print("2. Memoized recursion")
print("=" * 60)

@lru_cache(maxsize=None)
def fib(n: int) -> int:
    if n < 2:
        return n
    return fib(n - 1) + fib(n - 2)

for n in (10, 20, 50, 100, 120):
    print(f"fib({n:>3}) = {fib(n)}")
print(f"cache info: {fib.cache_info()}")
print()

# ---------------------------------------------------------------------------
# 3. Class hierarchy
# ---------------------------------------------------------------------------
print("=" * 60)
print("3. Classes & dataclasses")
print("=" * 60)

@dataclass(order=True)
class Vec2:
    x: float
    y: float = 0.0

    def __add__(self, other: "Vec2") -> "Vec2":
        return Vec2(self.x + other.x, self.y + other.y)

    def __mul__(self, k: float) -> "Vec2":
        return Vec2(self.x * k, self.y * k)

    def length(self) -> float:
        return math.hypot(self.x, self.y)

@dataclass
class Particle:
    name: str
    pos: Vec2
    vel: Vec2
    trail: list = field(default_factory=list)

    def step(self, dt: float) -> None:
        self.pos = self.pos + self.vel * dt
        self.trail.append((round(self.pos.x, 2), round(self.pos.y, 2)))

ps = [
    Particle("alpha", Vec2(0, 0), Vec2(1.0, 0.5)),
    Particle("beta",  Vec2(5, 5), Vec2(-0.3, 0.8)),
    Particle("gamma", Vec2(-3, 2), Vec2(0.7, -0.4)),
]
for _ in range(8):
    for p in ps:
        p.step(0.5)
for p in ps:
    print(f"{p.name:>5} → pos={p.pos}, |v|={p.vel.length():.3f}, trail={p.trail[-3:]}")
print()

# ---------------------------------------------------------------------------
# 4. itertools / collections / statistics
# ---------------------------------------------------------------------------
print("=" * 60)
print("4. itertools, collections, statistics")
print("=" * 60)

data = [random.gauss(50, 12) for _ in range(1000)]
print(f"n              : {len(data)}")
print(f"mean           : {statistics.mean(data):.3f}")
print(f"median         : {statistics.median(data):.3f}")
print(f"stdev          : {statistics.stdev(data):.3f}")
print(f"quantiles(4)   : {[round(q, 2) for q in statistics.quantiles(data, n=4)]}")

words = "the quick brown fox jumps over the lazy dog the fox is quick".split()
print(f"word counts    : {Counter(words).most_common(3)}")

bag = defaultdict(list)
for i, w in enumerate(words):
    bag[len(w)].append(w)
print(f"by word length : {dict(bag)}")

q = deque(maxlen=5)
for n in range(20):
    q.append(n)
print(f"deque tail-5   : {list(q)}")

print(f"first 5 squares (islice): {list(islice((n * n for n in range(1, 100)), 5))}")
print(f"running sum     : {list(accumulate(range(1, 8)))}")
print(f"C(5,2) pairs    : {list(combinations(range(5), 2))}")
chained = list(chain([1, 2], (3, 4), {5, 6}))
print(f"chained iter    : {chained}")
grouped = {k: list(g) for k, g in groupby(sorted(words), key=len)}
print(f"groupby length  : {grouped}")
print()

# ---------------------------------------------------------------------------
# 5. Mini-benchmark
# ---------------------------------------------------------------------------
print("=" * 60)
print("5. Mini-benchmark")
print("=" * 60)

def bench(label, fn, iters=5):
    times = []
    for _ in range(iters):
        t0 = time.perf_counter()
        fn()
        times.append(time.perf_counter() - t0)
    print(f"{label:>20}: best={min(times)*1000:7.3f}ms  mean={statistics.mean(times)*1000:7.3f}ms")

N = 200_000
bench("list comprehension", lambda: [i * i for i in range(N)])
bench("map+lambda",         lambda: list(map(lambda i: i * i, range(N))))
bench("sum 1..N",           lambda: sum(range(N)))
bench("sorted random",      lambda: sorted(random.random() for _ in range(20_000)))
bench("dict build",         lambda: {i: i * i for i in range(N // 2)})
print()

# ---------------------------------------------------------------------------
# 6. Regex, JSON, base64
# ---------------------------------------------------------------------------
print("=" * 60)
print("6. Regex, JSON, base64")
print("=" * 60)

text = """
Contact: alice@example.com, bob+test@dev.io, NOT_AN_EMAIL, charlie@studio.app
Phone: +1-415-555-0142, +44 20 7946 0958
"""
emails = re.findall(r"[\w+.-]+@[\w.-]+\.\w+", text)
phones = re.findall(r"\+?\d[\d \-]{7,}\d", text)
print(f"emails: {emails}")
print(f"phones: {phones}")

payload = {"vectors": [{"x": p.pos.x, "y": p.pos.y} for p in ps], "primes": primes[:10]}
encoded = json.dumps(payload, separators=(",", ":"))
print(f"json bytes      : {len(encoded)}")
print(f"json roundtrip  : {json.loads(encoded) == payload}")
print(f"base64 (first 60): {base64.b64encode(encoded.encode())[:60].decode()}…")
print()

# ---------------------------------------------------------------------------
# 7. ASCII Mandelbrot (20×40)
# ---------------------------------------------------------------------------
print("=" * 60)
print("7. ASCII Mandelbrot")
print("=" * 60)

def mandel(width=60, height=20, max_iter=40):
    chars = " .:-=+*#%@"
    for y in range(height):
        row = []
        for x in range(width):
            c = complex(-2.2 + 3.0 * x / width, -1.1 + 2.2 * y / height)
            z, i = 0, 0
            while abs(z) <= 2 and i < max_iter:
                z = z * z + c
                i += 1
            row.append(chars[min(len(chars) - 1, i * len(chars) // max_iter)])
        print("".join(row))

mandel()
print()

# ---------------------------------------------------------------------------
# 8. Big stdout — make sure long output renders
# ---------------------------------------------------------------------------
print("=" * 60)
print("8. Long output (500 lines)")
print("=" * 60)
for i in range(1, 501):
    print(f"line {i:>3}  |  φ^{i % 12} = {((1 + 5 ** 0.5) / 2) ** (i % 12):.6f}")
print()

# ---------------------------------------------------------------------------
# 9. Final summary table
# ---------------------------------------------------------------------------
print("=" * 60)
print("9. Summary")
print("=" * 60)

rows = [
    ("squares",   len(squares),  sum(squares)),
    ("primes<100", len(primes),  sum(primes)),
    ("fib(120)",  120,           fib(120)),
    ("samples",   len(data),     round(statistics.mean(data), 2)),
    ("emails",    len(emails),   ", ".join(emails)[:40]),
    ("phones",    len(phones),   ", ".join(phones)[:40]),
]
print(f"{'item':<12} {'count':>8}  value")
print("-" * 60)
for name, count, value in rows:
    print(f"{name:<12} {count:>8}  {value}")

print()
print("✅ All sections ran end-to-end.")
