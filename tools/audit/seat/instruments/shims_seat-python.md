# `shims/seat-python`, `shims/seat-python3`

- `shims/seat-python`, `shims/seat-python3` — the seat interpreter: execs the
  venv-ci `seat_venv.sh` builds, under `$HPO_STATE_DIR` first and the default
  state root `~/.local/state/hpo` second, and refuses naming that build command
  when neither holds one; exports `HPO_TYPING_PYTHON` to venv-ha/bin/python
  under the same two roots, only when that interpreter exists and the variable
  is unset. When: a seat's PATH needs a pinned interpreter, and the scoped gate
  should check the mypy census.
