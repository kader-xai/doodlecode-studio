# Roadmap

This is a side-project roadmap — directional, not committed. Order
roughly matches priority.

## Near term

- [ ] **Test suite**: `pytest` for backend, `vitest` for frontend, one
      Playwright happy-path. CI is already wired to run them.
- [ ] **Streaming kernel output**: replace request/response with WebSocket
      so long-running cells don't block the UI.
- [ ] **Pluggable explanation backend**: Anthropic / OpenAI / Ollama
      switch behind an env var. See
      [docs/DEVELOPMENT.md](DEVELOPMENT.md#plugging-in-a-real-llm).
- [ ] **Save back to the original path**: today 💾 always downloads;
      keep a notion of "open file path" and overwrite by default.
- [ ] **Cell reordering**: drag handles on the canvas, persisted in
      cell array order on save.

## Medium term

- [ ] **PDF / PPTX export**: print the canvas (or each cell) to a
      shareable deck.
- [ ] **Tensor flow visualizer**: a custom node type that introspects a
      `nn.Module` and draws the layer graph next to the code.
- [ ] **`nbconvert` integration**: opening a `.ipynb` already works;
      add the inverse so `jupyter nbconvert` produces a DoodleCode `.py`.
- [ ] **Search & jump**: Cmd-P palette listing every cell title.
- [ ] **Cell-level run-all + run-above-this**.

## Longer term

- [ ] **Plugin system**: third-party node types loaded from npm.
- [ ] **Multiplayer**: Y.js / Liveblocks-style collaboration.
      Non-trivial because kernel state can't be naively shared.
- [ ] **Sandboxed hosted mode**: a deployable Docker target that
      sandboxes the kernel (gVisor / Firejail) so it can be shared
      publicly without giving away shell access.
- [ ] **Electron / Tauri desktop build** with auto-update.
- [ ] **Voice narration**: TTS for each callout in presentation mode.

## Definitely not

- A custom Python parser. We rely on `ast` and `jupyter_client`; both
  pull their weight.
- A custom syntax highlighter. Monaco's is excellent.
- AI auto-generated callouts overwriting user-authored ones. The right
  column is the user's voice — that's the product.

## How to influence the roadmap

Open an issue with a concrete use case. "It would be cool if…" is fine,
but "I tried to do X, and the missing piece was Y" is the most useful
shape — it tells us what to prioritise.
