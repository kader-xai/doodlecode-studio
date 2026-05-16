# %% [markdown]
# # Module 2 — File Handling in Python
# Reading and writing files is how programs talk to the world. By the end
# of this module you can open, read, write, and append text files, work with
# CSV and JSON, handle paths safely, and avoid the three classic file bugs.

# %% [markdown]
# ## What you'll cover
# - The `open()` function and file modes (`r`, `w`, `a`, `x`, `b`, `+`)
# - The `with` statement — the only correct way to open files
# - Reading: `.read()`, `.readline()`, `.readlines()`, iterating line-by-line
# - Writing: `.write()`, `.writelines()`, `print(..., file=f)`
# - Encodings — why `utf-8` is the right default
# - Binary files (images, pickles)
# - CSV files with the `csv` module
# - JSON with `json.load` / `json.dump`
# - Paths with `os.path` and the modern `pathlib`
# - Checking existence, creating folders, listing directories
# - Exceptions you must handle: `FileNotFoundError`, `PermissionError`
# - Temp files, line counts, and a tiny log-rotator example


# %% kind=intro color=sky title="1. What is a file, in Python's eyes?"
# @explain: A file is a stream of bytes on disk that Python wraps in a
# @explain: "file object". You open it, read or write through it, then
# @explain: close it. The OS keeps a handle until you close — leaking
# @explain: handles is a real bug, which is why we use `with`.
# @tags: intro, files


# %% kind=intro color=sky title="open() — modes you need to know"
# @explain: open(path, mode, encoding=...) returns a file object.
# @explain: 'r' read (default) · 'w' write (truncates!) · 'a' append.
# @explain: 'x' create-new (fails if exists) · '+' read AND write.
# @explain: Append 'b' for binary (e.g. 'rb', 'wb'). Default is text mode.
# @tags: open, modes


# %% kind=function color=mint title="Setting up a sandbox folder"
# @explain: We make a dedicated tmp directory so every example writes
# @explain: somewhere safe. pathlib.Path makes path math readable.
from pathlib import Path

SANDBOX = Path("/tmp/doodlecode_files")
SANDBOX.mkdir(parents=True, exist_ok=True)
print("sandbox:", SANDBOX)


# %% [markdown]
# ## 2. The `with` statement — always use it
# `with open(...) as f:` guarantees `f.close()` runs even if the block
# raises. Forgetting to close is the most common file bug in Python — it
# leaks OS handles and on Windows can lock the file from other processes.


# %% kind=context color=sky title="Writing a text file with `with`"
# @explain: 'w' truncates any existing file before writing.
# @explain: Indent everything that uses `f` inside the with-block.
# @explain: Outside the block, the file is closed automatically.
path = SANDBOX / "hello.txt"

with open(path, "w", encoding="utf-8") as f:
    f.write("Hello, doodle world!\n")
    f.write("This is line two.\n")

print("wrote:", path)


# %% kind=context color=sky title="Reading the whole file at once"
# @explain: .read() returns the WHOLE file as one string. Fine for small
# @explain: files; risky for gigabyte logs — use the streaming loop below.
with open(path, "r", encoding="utf-8") as f:
    text = f.read()

print(text)


# %% kind=loop color=yellow title="Iterating line by line (the streaming way)"
# @explain: A file object is iterable — each iteration yields one line
# @explain: WITH its trailing newline. .rstrip() removes the newline.
# @explain: This is memory-efficient for huge files.
with open(path, "r", encoding="utf-8") as f:
    for i, line in enumerate(f, start=1):
        print(f"{i:>2}: {line.rstrip()}")


# %% kind=context color=sky title=".readline() and .readlines()"
# @explain: .readline() reads ONE line at a time (cursor advances).
# @explain: .readlines() returns a LIST of all lines — loads everything
# @explain: into memory, so prefer iteration for big files.
with open(path, "r", encoding="utf-8") as f:
    first = f.readline()
    rest = f.readlines()

print("first:", repr(first))
print("rest :", rest)


# %% [markdown]
# ## 3. Write modes — `w`, `a`, `x` in one picture
# - **`w`** — open for writing. **Truncates** the file to zero length first.
#   If the file does not exist, it is created.
# - **`a`** — append. Existing content is kept; new writes go to the end.
# - **`x`** — exclusive create. Raises `FileExistsError` if the file exists.
#   Useful when you must not overwrite (lock files, one-shot exports).


# %% kind=context color=sky title="Append vs overwrite"
# @explain: We append two lines, then read the file back to see all four.
log = SANDBOX / "log.txt"

with open(log, "w", encoding="utf-8") as f:
    f.write("first run\n")

with open(log, "a", encoding="utf-8") as f:
    f.write("second run\n")
    f.write("third run\n")

with open(log, "r", encoding="utf-8") as f:
    print(f.read())


# %% kind=try color=rose title="Exclusive create with 'x'"
# @explain: 'x' refuses to overwrite. We wrap it in try/except so the
# @explain: second attempt prints a friendly message instead of crashing.
once = SANDBOX / "once.lock"

try:
    with open(once, "x") as f:
        f.write("locked")
    print("created", once)
except FileExistsError:
    print(once, "already exists — not overwriting")

try:
    with open(once, "x") as f:
        f.write("locked again")
except FileExistsError:
    print(once, "already exists — not overwriting")


# %% [markdown]
# ## 4. Writing — three good ways
# - `f.write(s)` — write one string. No newline added; you add `\n` yourself.
# - `f.writelines(seq)` — write a sequence of strings. Same: no newlines added.
# - `print(*args, file=f)` — uses `print`'s nice defaults (sep, end='\n').


# %% kind=context color=sky title="writelines + print(file=f)"
# @explain: writelines does NOT add newlines — you must include them.
# @explain: print(file=f) IS happy to add the newline for you, and accepts
# @explain: sep/end/flush like normal print.
out = SANDBOX / "fruits.txt"

with open(out, "w", encoding="utf-8") as f:
    f.writelines(["apple\n", "banana\n", "cherry\n"])
    print("date", "elderberry", sep="\n", file=f)

print(out.read_text(encoding="utf-8"))


# %% [markdown]
# ## 5. Encodings — always set `encoding="utf-8"`
# A text file on disk is bytes; Python decodes them into a `str` using an
# encoding. The OS default differs (Windows = `cp1252`, macOS/Linux usually
# `utf-8`). **Pinning `encoding="utf-8"` makes your code portable.**


# %% kind=context color=sky title="Non-ASCII text — utf-8 vs latin-1"
# @explain: We write a Turkish word with utf-8 then read it back twice:
# @explain: once correctly with utf-8, once incorrectly with latin-1.
# @explain: The mismatch is exactly how mojibake (€ñ) is born.
unicode_path = SANDBOX / "unicode.txt"
unicode_path.write_text("güneş çiçeği — sunflower\n", encoding="utf-8")

print("utf-8  :", unicode_path.read_text(encoding="utf-8"))
print("latin-1:", unicode_path.read_text(encoding="latin-1"))


# %% [markdown]
# ## 6. Binary files
# Open with `'rb'` / `'wb'` to read/write **bytes**, not text. Use this for
# images, audio, pickled objects, gzipped data — anything where decoding to
# `str` would be wrong.


# %% kind=context color=sky title="Writing and reading a tiny PNG header"
# @explain: PNG files always start with this 8-byte magic number.
# @explain: 'wb' means write-binary; the data must be a bytes object.
png_header = b"\x89PNG\r\n\x1a\n"

bin_path = SANDBOX / "fake.png"
with open(bin_path, "wb") as f:
    f.write(png_header)

with open(bin_path, "rb") as f:
    head = f.read(8)

print("bytes:", head)
print("hex  :", head.hex())


# %% [markdown]
# ## 7. CSV — the bread and butter of data files
# Don't split CSV lines with `.split(",")` — real CSVs have commas inside
# quoted fields, multi-line cells, different delimiters, and quoting rules.
# The stdlib `csv` module handles all of that for you.


# %% kind=function color=mint title="Writing a CSV with csv.writer"
# @explain: newline='' is REQUIRED on Windows or you get blank lines
# @explain: between rows. csv.writer takes any iterable of values per row.
import csv

people = [
    ["name", "age", "city"],
    ["Kader", 38, "Istanbul"],
    ["Ada", 27, "London, UK"],
    ["Yusuf", 41, "Berlin"],
]

csv_path = SANDBOX / "people.csv"
with open(csv_path, "w", encoding="utf-8", newline="") as f:
    writer = csv.writer(f)
    writer.writerows(people)

print(csv_path.read_text(encoding="utf-8"))


# %% kind=function color=mint title="Reading a CSV with csv.DictReader"
# @explain: DictReader uses the first row as the header and yields each
# @explain: subsequent row as a dict — much nicer than index access.
with open(csv_path, "r", encoding="utf-8", newline="") as f:
    reader = csv.DictReader(f)
    for row in reader:
        print(row["name"], "is", row["age"], "from", row["city"])


# %% [markdown]
# ## 8. JSON — structured data in/out
# JSON maps cleanly to Python: object → dict, array → list, string → str,
# number → int/float, true/false/null → True/False/None. Use `json.dump`
# to write, `json.load` to read.


# %% kind=function color=mint title="Writing and reading JSON"
# @explain: indent=2 pretty-prints; ensure_ascii=False keeps real Unicode
# @explain: characters instead of turning them into \uXXXX escapes.
import json

data = {
    "module": "file handling",
    "topics": ["open", "with", "csv", "json", "pathlib"],
    "stars": 4.7,
    "active": True,
    "owner": None,
}

json_path = SANDBOX / "module.json"
with open(json_path, "w", encoding="utf-8") as f:
    json.dump(data, f, indent=2, ensure_ascii=False)

print(json_path.read_text(encoding="utf-8"))

with open(json_path, "r", encoding="utf-8") as f:
    loaded = json.load(f)

print("type:", type(loaded).__name__, "| topics:", loaded["topics"])


# %% kind=function color=mint title="JSON Lines (one object per line)"
# @explain: JSONL is what most ML datasets and log pipelines use: each
# @explain: line is its OWN valid JSON object. Easy to stream, easy to
# @explain: append, easy to grep.
events = [
    {"t": 1, "user": "a", "action": "login"},
    {"t": 2, "user": "b", "action": "buy"},
    {"t": 3, "user": "a", "action": "logout"},
]

jsonl_path = SANDBOX / "events.jsonl"
with open(jsonl_path, "w", encoding="utf-8") as f:
    for ev in events:
        f.write(json.dumps(ev) + "\n")

with open(jsonl_path, "r", encoding="utf-8") as f:
    for line in f:
        ev = json.loads(line)
        print(ev["t"], ev["user"], ev["action"])


# %% [markdown]
# ## 9. Paths — `os.path` vs `pathlib`
# **Use `pathlib`.** It treats paths as proper objects with methods
# (`.exists()`, `.is_file()`, `.suffix`, `.parent`, `.stem`, `.read_text()`)
# and uses `/` for joining instead of clunky `os.path.join`.


# %% kind=function color=mint title="Path arithmetic with pathlib"
# @explain: Path("a") / "b" / "c.txt" is the cross-platform way to build
# @explain: paths. Each Path has stem, suffix, name, and parent fields.
from pathlib import Path

p = SANDBOX / "subdir" / "report.csv"
print("full   :", p)
print("name   :", p.name)
print("stem   :", p.stem)
print("suffix :", p.suffix)
print("parent :", p.parent)
print("parts  :", p.parts)


# %% kind=function color=mint title="exists / is_file / is_dir / mkdir"
# @explain: mkdir(parents=True, exist_ok=True) is the idiomatic
# @explain: "ensure this folder exists" — like `mkdir -p` in a shell.
p = SANDBOX / "new_folder"
p.mkdir(parents=True, exist_ok=True)
print("exists :", p.exists())
print("is_dir :", p.is_dir())
print("is_file:", p.is_file())


# %% kind=loop color=yellow title="Listing a directory"
# @explain: iterdir() yields each child Path. .glob('*.txt') filters by
# @explain: pattern. .rglob() recurses into subdirectories.
for child in sorted(SANDBOX.iterdir()):
    kind = "DIR " if child.is_dir() else "FILE"
    print(kind, child.name)

print("--- txt files ---")
for txt in sorted(SANDBOX.glob("*.txt")):
    print(txt.name, "·", txt.stat().st_size, "bytes")


# %% [markdown]
# ## 10. Errors you must handle
# - **FileNotFoundError** — the path does not exist (or a typo).
# - **PermissionError** — the OS refused. Check ownership/ACLs.
# - **IsADirectoryError / NotADirectoryError** — wrong kind of path.
# - **UnicodeDecodeError** — wrong `encoding` for the file's actual bytes.


# %% kind=try color=rose title="Graceful missing-file handling"
# @explain: Two correct patterns: try/except, or check first with .exists().
# @explain: Both are valid; try/except is preferred ("EAFP" — Easier to
# @explain: Ask Forgiveness than Permission) because it has no race window.
missing = SANDBOX / "does_not_exist.txt"

try:
    text = missing.read_text(encoding="utf-8")
except FileNotFoundError:
    print("file missing — falling back to empty string")
    text = ""

print("got:", repr(text))


# %% [markdown]
# ## 11. A practical mini-example: a tiny log rotator
# Append a line per "event"; once the log exceeds N bytes, move it to
# `name.1` and start fresh. This pattern is the seed of every logging
# library you'll ever use.


# %% kind=function color=mint title="rotate_log(path, max_bytes)"
# @explain: If the log exceeds max_bytes, rename it to a .1 backup
# @explain: (replacing any previous .1) and the next append starts a new
# @explain: empty file.
def rotate_log(path: Path, max_bytes: int) -> None:
    if path.exists() and path.stat().st_size > max_bytes:
        backup = path.with_suffix(path.suffix + ".1")
        backup.unlink(missing_ok=True)
        path.rename(backup)


# %% kind=function color=mint title="Append entries and rotate"
# @explain: We write 20 events to a tiny 200-byte limit so the rotation
# @explain: happens during the loop. After it, both files exist on disk.
import datetime as dt

events_log = SANDBOX / "events.log"
events_log.unlink(missing_ok=True)  # start fresh for the demo

for i in range(20):
    rotate_log(events_log, max_bytes=200)
    with open(events_log, "a", encoding="utf-8") as f:
        stamp = dt.datetime(2026, 1, 1, 12, 0, i).isoformat(timespec="seconds")
        f.write(f"{stamp} event #{i}\n")

print("current :", events_log.name, "·", events_log.stat().st_size, "bytes")
backup = events_log.with_suffix(events_log.suffix + ".1")
if backup.exists():
    print("rotated :", backup.name, "·", backup.stat().st_size, "bytes")


# %% [markdown]
# ## 12. Counting lines without loading the file
# Useful sanity check for big files (millions of rows). Stream and count.


# %% kind=function color=mint title="count_lines(path)"
# @explain: Iterating a file yields lines one at a time, so memory use
# @explain: stays constant regardless of file size. sum(1 for _ in f)
# @explain: is the fast idiom — no list is built.
def count_lines(path: Path) -> int:
    with open(path, "r", encoding="utf-8") as f:
        return sum(1 for _ in f)


print("lines in fruits.txt :", count_lines(SANDBOX / "fruits.txt"))
print("lines in events.jsonl:", count_lines(SANDBOX / "events.jsonl"))


# %% [markdown]
# ## 13. Temporary files
# When you need a scratch file that auto-deletes, use `tempfile`. It picks
# a unique name in the OS tmp dir and (with a context manager) cleans up.


# %% kind=context color=sky title="A NamedTemporaryFile demo"
# @explain: delete=False keeps the file around after the with-block so we
# @explain: can re-open it. Otherwise it would vanish at block exit.
import tempfile

with tempfile.NamedTemporaryFile(
    mode="w", suffix=".txt", encoding="utf-8", delete=False
) as tmp:
    tmp.write("scratch data\n")
    tmp_path = Path(tmp.name)

print("tmp path:", tmp_path)
print("contents:", tmp_path.read_text(encoding="utf-8"))
tmp_path.unlink()
print("deleted :", not tmp_path.exists())


# %% [markdown]
# ## 14. Practice
# 1. Write the numbers 1..10 to `numbers.txt`, one per line. Read them back
#    as a list of `int`s.
# 2. Given the `people.csv` above, write a new CSV `adults.csv` containing
#    only rows where `age >= 30`.
# 3. Read `module.json` and pretty-print only the value at key `topics`.
# 4. Walk `SANDBOX` and print the total number of bytes across all files.


# %% kind=function color=mint title="Exercise 1 — round-trip integers"
# @explain: Cast to int on the way out, str on the way in.
nums_path = SANDBOX / "numbers.txt"
with open(nums_path, "w", encoding="utf-8") as f:
    for n in range(1, 11):
        f.write(f"{n}\n")

with open(nums_path, "r", encoding="utf-8") as f:
    nums = [int(line) for line in f if line.strip()]

print(nums, "sum =", sum(nums))


# %% kind=function color=mint title="Exercise 2 — filter a CSV"
# @explain: DictReader → filter on int(row['age']) → DictWriter with the
# @explain: same fieldnames. We never call .split(',') ourselves.
src = SANDBOX / "people.csv"
dst = SANDBOX / "adults.csv"

with open(src, "r", encoding="utf-8", newline="") as fin, open(
    dst, "w", encoding="utf-8", newline=""
) as fout:
    reader = csv.DictReader(fin)
    writer = csv.DictWriter(fout, fieldnames=reader.fieldnames)
    writer.writeheader()
    for row in reader:
        if int(row["age"]) >= 30:
            writer.writerow(row)

print(dst.read_text(encoding="utf-8"))


# %% kind=function color=mint title="Exercise 3 — pretty-print one JSON key"
# @explain: Load the whole file, index into it, then dump JUST that value
# @explain: with indent=2 to stdout via json.dumps.
with open(SANDBOX / "module.json", "r", encoding="utf-8") as f:
    obj = json.load(f)

print(json.dumps(obj["topics"], indent=2, ensure_ascii=False))


# %% kind=function color=mint title="Exercise 4 — total bytes under SANDBOX"
# @explain: rglob('*') walks every descendant; .stat().st_size gives the
# @explain: size of each file. We skip directories with .is_file().
total = sum(p.stat().st_size for p in SANDBOX.rglob("*") if p.is_file())
print(f"{total:,} bytes across {sum(1 for p in SANDBOX.rglob('*') if p.is_file())} files")


# %% [markdown]
# ## Recap — what you can now do
# - ✅ Open files in the right mode (`r`, `w`, `a`, `x`, `b`)
# - ✅ Always use `with` — files close themselves
# - ✅ Read whole-file or streaming (line-by-line) and choose correctly
# - ✅ Write with `.write`, `.writelines`, and `print(file=f)`
# - ✅ Pin `encoding="utf-8"` so your code travels across OSes
# - ✅ Read and write CSV with the `csv` module, JSON / JSONL with `json`
# - ✅ Use `pathlib` for paths, existence checks, and directory listings
# - ✅ Handle `FileNotFoundError` and friends with try/except
# - ✅ Build a tiny log rotator and count lines without loading the file
#
# **Next module:** Module 3 — Errors, Exceptions, and Defensive Programming.
