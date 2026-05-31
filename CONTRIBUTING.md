# Contributing to DoodleCode Studio

Thanks for considering a contribution! This project is small and friendly —
issues and PRs are both welcome.

## Ground rules

- Be kind. See the [Code of Conduct](CODE_OF_CONDUCT.md).
- For anything more than a small fix, **open an issue first** to discuss the
  approach.
- Keep PRs focused — one logical change per PR. Refactors separate from
  feature work.
- All contributors agree to license their contribution under the project's
  [MIT license](LICENSE).

## Setting up a dev environment

You need:

- **Python 3.9+** with `python3 -m venv` available.
- **Node.js 18+** with `npm`.

```bash
git clone https://github.com/kader-xai/doodlecode-studio.git
cd doodlecode-studio
./start.sh
```

`start.sh` creates `backend/.venv`, installs deps, registers an IPython
kernel, and launches both servers. After the first run, you can launch the
two parts independently — see [docs/DEVELOPMENT.md](docs/DEVELOPMENT.md).

## Project layout

```
backend/        FastAPI + jupyter_client. Pure Python, no build step.
  app/
    main.py         HTTP routes
    kernel.py       Kernel pool
    parser.py       AST → blocks (used by stub explainer)
    explain.py      Callout generator (stub — wire an LLM here)
    notebook.py     .py / .ipynb / .md parsing
    serialize.py    Notebook → .py round-trip
    models.py       Pydantic schemas
frontend/       React + Vite. TypeScript strict.
  src/
    components/    UI nodes & toolbar
    lib/rough.ts   Hand-drawn helpers + color palette
    api.ts         Fetch wrappers
    store.ts       zustand store + autosave
    types.ts       Mirrors backend pydantic shapes
docs/           Architecture, file format, usage, dev, roadmap.
examples/       Tutorial files in the project's own format.
```

### Active app lives in `v2/`

**New work should target `v2/`** — the current DoodleCode Studio (FastAPI
on :8001 + React/Vite/Zustand/ReactFlow). It has the same
`backend/` + `frontend/` shape and its own `v2/CLAUDE.md` capturing the
load-bearing rules, plus `v2/ROADMAP.md` and `v2/CHANGELOG.md`.

```bash
cd v2 && ./start.sh          # build UI once + serve everything on :8001
cd v2 && ./start.sh --dev    # Vite hot-reload on :5174 + API on :8001
```

CI runs the v1 *and* v2 suites on every PR (see
`.github/workflows/ci.yml`). The v2 CI-equivalent you should run locally
before pushing:

```bash
cd v2/frontend && npx tsc -b --noEmit && npm test && npm run build
cd v2/backend  && .venv/bin/python -m pytest -q
```

## Style

- **Python**: PEP 8, 100-char lines, `from __future__ import annotations`.
  Avoid `print`-debugging in committed code.
- **TypeScript**: strict mode is on. No `any` unless you can't avoid it.
- **CSS**: prefer Tailwind utilities; reach for plain CSS only for things
  Tailwind can't express (e.g. ReactFlow internals).
- Don't add comments that restate the code. Do add a one-line comment for
  *why* something non-obvious exists.

## Testing

The current test coverage is light — adding tests is one of the most
welcome contributions.

- **Backend smoke tests** (recommended pattern):

  ```bash
  cd backend
  source .venv/bin/activate
  python -c "from app.notebook import from_py; ..."
  ```

  A `pytest`-based suite under `backend/tests/` would be ideal — see the
  open issue.

- **Frontend type-check** is the current substitute for unit tests:

  ```bash
  cd frontend
  npx tsc -b --noEmit
  npm run build
  ```

  Both run in CI on every PR.

## Commit messages

Use [Conventional Commits](https://www.conventionalcommits.org/) if you can:

- `feat: …` new user-facing feature
- `fix: …` bug fix
- `docs: …` documentation
- `refactor: …` no behavior change
- `chore: …` build/CI/tooling

A one-line body explaining *why* is more useful than restating the diff.

## Submitting a PR

1. Fork → branch off `main`.
2. Make your change, plus tests / docs if applicable.
3. `npx tsc -b --noEmit` and `python -m compileall backend/app` should pass.
4. Open the PR using the template. Link the issue you're closing.
5. Be patient — this is a side-project; reviews can take a few days.

Thank you! 🎨
