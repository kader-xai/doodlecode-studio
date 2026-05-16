# Development guide

## Local setup

Pre-requisites: Python 3.9+, Node 18+.

```bash
git clone https://github.com/kader-xai/doodlecode-studio.git
cd doodlecode-studio
./start.sh           # one-shot launcher
```

After the first launch, you can run the two servers independently — this
gives you faster restarts and per-side logs:

```bash
# terminal 1 — backend
cd backend
source .venv/bin/activate
uvicorn app.main:app --reload --port 8000

# terminal 2 — frontend
cd frontend
npm run dev
```

The frontend proxies `/api/*` to `localhost:8000`, so there's no CORS
preflight in dev.

## Codebase tour

```
backend/
  app/
    main.py        ← FastAPI routes
    kernel.py      ← Kernel pool (jupyter_client)
    parser.py      ← AST → block list (used by stub explainer)
    explain.py     ← Callout generator — wire your LLM here
    notebook.py    ← `# %%` + `# @explain:` parser
    serialize.py   ← Same format, the other direction
    models.py      ← Pydantic schemas shared with the frontend
  requirements.txt
  pyproject.toml   ← Optional metadata (no install hook yet)
frontend/
  src/
    main.tsx
    App.tsx
    components/    ← one file per UI piece
    lib/rough.ts   ← Hand-drawn helpers + palette
    api.ts         ← fetch wrappers
    store.ts       ← zustand store + localStorage + debounced autosave
    types.ts       ← mirrors models.py
docs/              ← architecture, file-format, usage, dev, roadmap
examples/          ← tutorial files in our own format
start.sh           ← combined launcher
```

## Plugging in a real LLM

`backend/app/explain.py` is intentionally tiny. To replace the stub:

1. Add your provider's SDK to `requirements.txt` (e.g. `openai`, `ollama`).
2. Rewrite `explain_code()` to call the model and return an
   `ExplainResponse`. Pattern:
   ```python
   def explain_code(code, mode, cell_id, meta):
       if meta and (meta.title or meta.explain):
           return _from_meta(meta, cell_id)   # keep user-authored callouts
       body = _ask_llm(_build_prompt(code, mode))
       return ExplainResponse(
           blocks=[],
           explanations=[Explanation(
               block_id=f"{cell_id}-ai",
               title="Notes",
               body=body,
               tags=["ai"],
               color="lavender",
           )],
       )
   ```
3. The `Explanation` object has a `color` field — set it to keep the
   bubble visually grouped with the cell.
4. Add an env-var gate so the stub is the default and the LLM only
   activates when the provider key is set.

## Adding a new node type

Adding e.g. a tensor-flow visualizer node:

1. Create `frontend/src/components/TensorNode.tsx` returning a doodle
   card. It receives `data` via `NodeProps<T>`.
2. Register it in `DoodleCanvas.tsx`:
   ```ts
   const nodeTypes = { code: CodeCellNode, explain: ExplanationNode,
                       markdown: MarkdownNode, tensor: TensorNode };
   ```
3. Generate the node in `buildGraph()` based on something — maybe a new
   `# %% kind=tensor` value, or a sibling endpoint that produces tensor
   layouts.
4. Done. ReactFlow handles dragging / connection / zoom for you.

## Adding a palette color

1. Add hex values to **both** `PALETTE` (light) and `PALETTE_DARK` in
   `frontend/src/lib/rough.ts`.
2. Update `COLORS` in `components/CalloutEditor.tsx` so the swatch
   appears in the color picker.
3. Add a row to the palette table in
   [docs/FILE_FORMAT.md](FILE_FORMAT.md#palette).
4. (Optional) Map it to a `kind` default in `lib/rough.ts:KIND_FALLBACK`
   and `backend/app/explain.py:KIND_COLOR`.

## Adding a backend endpoint

1. Add a pydantic request/response model to `models.py`.
2. Add the route in `main.py`. Pure functions go in their own module if
   they grow > a few lines.
3. Add a wrapper in `frontend/src/api.ts`.
4. Add tests under `backend/tests/` (see below) and a CI assertion if it
   affects the file format.

## Testing

There is **no test suite yet** — adding one is the highest-impact
contribution today.

For now CI runs:

- `python -m compileall backend/app` — catches syntax errors.
- A round-trip smoke test (`from_py → serialize → from_py` equality).
- `npx tsc -b --noEmit` — TypeScript strict mode.
- `npm run build` — production bundle.

When you add real tests, please target:

| Module | What to test |
|--------|--------------|
| `notebook.py`  | Edge cases of the marker / directive parser, including unicode, malformed headers, mixed indentation. |
| `serialize.py` | Round-trip for fuzzed inputs (every example file should round-trip exactly). |
| `explain.py`   | The "no meta → empty" contract; meta-driven callout shape. |
| `store.ts`     | Debounce semantics, autosave invocation count. |
| `Outputs.tsx`  | All four mime-bundle branches render. |

Recommended frameworks:

- Backend → `pytest` + `pytest-asyncio`.
- Frontend → `vitest` + `@testing-library/react`.
- End-to-end → Playwright (one happy-path test covering open → run →
  save → reopen).

## Common gotchas

- **Monaco wheel events** — the editor container must have the `nowheel`
  class so ReactFlow doesn't fight it for the scroll wheel. Already set
  in `CodeCellNode.tsx`; remove with caution.
- **Kernel state** — the IPython kernel is **persistent**. State from
  cell N is alive in cell N+1. Use ↻ Kernel to clear.
- **CORS** — open `*` in dev. Tighten before any non-localhost deploy.
- **localStorage size** — the autosave snapshot includes the full
  notebook. Very large notebooks (>1 MB) may bump into quota; the store
  swallows the error silently.

## Releasing (maintainers)

1. Bump version in `frontend/package.json`, `backend/pyproject.toml`.
2. Update `CHANGELOG.md` — move `[Unreleased]` items under a new
   version heading with today's date.
3. Tag: `git tag -a v0.x.y -m "v0.x.y"` and push tags.
4. Draft a GitHub Release pointing at the changelog entry.

There is no PyPI / npm publish yet — both packages are repo-only for
the moment.
