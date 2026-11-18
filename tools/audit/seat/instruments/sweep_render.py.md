# `sweep_render.py`

- `sweep_render.py` — renders the orchestrator sweep from
  `sweep_template.md` and a session's JSON overlay (stdout or `--out`). The
  template's `## Placeholders` table is the one registry of names. When: a
  session or round sets up its recurring sweep -- render it, never hand-copy
  the last session's prompt; the overlay stays out of the tree. Refusal: an
  unfilled, empty or non-scalar value, an undeclared placeholder or overlay
  key, a declared name the sweep never uses, a cited `tools/`, `tests/`,
  `dev/` or `.github/` path that is not in the tree, and a home directory
  (`ref_privacy.py`'s `HOME_DIR`) in the rendered text that no overlay value
  supplied -- each exits 1 and writes nothing. `--self-test` renders the
  tracked template and drives every refusal beside its null control.
