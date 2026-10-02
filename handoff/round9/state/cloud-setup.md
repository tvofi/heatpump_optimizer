# Cloud environment setup for heatpump_optimizer seats (R9-PROC-3, process review item 5)

Source of truth: `tools/audit/seat/cloud-setup.sh` on handoff/r9-proc-3 (code head eff1a2a3). Nothing runs it from the tree; these are settings changes only tvofi can make.

## 1. Setup script

Paste the script below into **Project settings > Environment > Setup script**. New sessions run it; a cold test run here took 11 min 22 s (the pip installs dominate).

What it gives a cloud seat: the Python version `tests/typing_budgets.json` records for the typing census (3.14.7 today), installed by a current uv from PyPI because the image's uv 0.8.17 has no build past 3.14.0rc,, `venv-ci` from `tests/requirements-ci.txt` first on PATH, `venv-ha` from `tests/requirements-typing.txt` (homeassistant and homeassistant-stubs 2026.9.3, mypy) as `HPO_TYPING_PYTHON`, and `OPENBLAS_CORETYPE=Haswell` to match CI's BLAS kernel. Pins are read from the checkout, so lock edits flow through. In the test, real Home Assistant `ha_contract --contracts-only` passed all 61 contracts.

```bash
#!/bin/bash
# The cloud environment's setup script for heatpump_optimizer seats (R9-PROC-3).
#
# NOT APPLIED CONFIG. A seat cannot change its own environment: tvofi pastes this
# into Project settings > Environment > Setup script, and new sessions run it.
# It gives a cloud seat the interpreter and pins CI runs, so `typing_ruler --mypy`
# and the real-Home-Assistant `ha_contract` run in the seat instead of on the Mac
# or only in CI (round-9 process review, item 5).
#
#   python   the version tests/typing_budgets.json records for the `typing`
#            census (census.environment.python), read at run time
#   venv-ci  tests/requirements-ci.txt, hash-pinned: numpy, scipy and the rest
#            of what `fast` installs; first on PATH, so `python3` is this one
#   venv-ha  tests/requirements-typing.txt, hash-pinned, --no-deps exactly as
#            the `typing` job installs it: mypy, homeassistant 2026.9.3 and
#            homeassistant-stubs 2026.9.3; exported as HPO_TYPING_PYTHON
#
# The pins are read from the checkout, never restated here, so this script
# cannot drift from the lock files; a lock edit reaches the next session.
set -euo pipefail

REPO=${HPO_REPO:-/home/user/heatpump_optimizer}
PREFIX=${HPO_PREFIX:-/opt/hpo}
PROFILE=${HPO_PROFILE:-/etc/profile.d/hpo-toolchain.sh}

# The tree-rewriting hooks: the hiway-kit plugin's auto-format.py (PostToolUse)
# and stop-validator.py (Stop) run `ruff format` and `ruff check --fix`, and
# both skip when `ruff` is not on PATH. Nothing in this repository or its CI
# uses ruff, so removing the image's copy switches them off for this
# environment only, with or without a checkout. Disabling the plugin in
# settings is the complete answer.
if [ -z "${HPO_KEEP_RUFF:-}" ]; then
  for r in $(type -ap ruff); do rm -f "$r" || true; done
fi

# A missing checkout warns and exits 0: a failing setup script would stop
# every session from starting, which costs more than a seat without pins.
[ -f "$REPO/tests/requirements-ci.txt" ] || {
  echo "cloud-setup: no checkout at $REPO, so no pins installed (set HPO_REPO)" >&2; exit 0; }

PYVER=$(python3 -c 'import json, sys; print(json.load(open(sys.argv[1]))["census"]["environment"]["python"])' \
  "$REPO/tests/typing_budgets.json")

# The image's uv 0.8.17 has no build past 3.14.0rc ("No download found for
# request"), so a current uv comes from PyPI first; it fetches the interpreter.
python3 -m pip install -q --target "$PREFIX/uv" uv
UV="$PREFIX/uv/bin/uv"
export UV_PYTHON_INSTALL_DIR="$PREFIX/python"
"$UV" python install --no-bin "$PYVER"
PY=$("$UV" python find "$PYVER")
"$PY" -c 'import sys; v = "%d.%d.%d" % sys.version_info[:3]; assert v == sys.argv[1], v' "$PYVER"

pins() { # venv, pip arguments...
  local v=$1; shift
  "$PY" -m venv "$PREFIX/$v"
  "$PREFIX/$v/bin/python" -m pip install -q --upgrade pip
  "$PREFIX/$v/bin/python" -m pip install -q --require-hashes \
    --build-constraint "$REPO/tests/requirements-build.txt" "$@"
}
pins venv-ci -r "$REPO/tests/requirements-ci.txt"
pins venv-ha --no-deps -r "$REPO/tests/requirements-typing.txt"

"$PREFIX/venv-ci/bin/python" -c 'import numpy, scipy, voluptuous'
"$PREFIX/venv-ha/bin/python" -c 'import homeassistant.const as c; assert c.__version__ == "2026.9.3", c.__version__'

cat > "$PROFILE" <<EOF
export PATH="$PREFIX/venv-ci/bin:\$PATH"
export HPO_TYPING_PYTHON="$PREFIX/venv-ha/bin/python"
export OPENBLAS_CORETYPE=Haswell
EOF
[ -n "${HPO_PROFILE:-}" ] || grep -qF "$PROFILE" "$HOME/.bashrc" 2>/dev/null \
  || echo ". $PROFILE" >> "$HOME/.bashrc"

echo "cloud-setup: python $PYVER, venv-ci and venv-ha under $PREFIX"
```

## 2. Turning off the tree-rewriting plugin hooks

The hooks that rewrite the tree come from the **hiway-kit** plugin (synced from the claude.ai account's plugin directory, marketplace `anthropic-plugin-directory`): `auto-format.py` on PostToolUse runs `ruff format` and `ruff check --fix` on every edited file, and `stop-validator.py` on Stop runs the same at turn end. That is what rewrote 252 files on F1.10 and stripped imports on F6.4.

- **Already handled by the script above:** both hooks skip when `ruff` is not on PATH, and nothing in this repository or its CI uses ruff, so the script deletes the image's `ruff`. That switches them off for this environment only. Set `HPO_KEEP_RUFF=1` to keep it.
- **The complete fix (tvofi):** turn the hiway-kit plugin off in the claude.ai account's plugin settings, which stops all its hooks (it also runs pytest at Stop). The same list has **frugal**, whose hooks block a seat after five reads per prompt and refuse general-purpose subagents (it fired repeatedly in this seat), and **hats**, which guards edits. Turning those off too is recommended for this project's seats.
- **Project-only alternative, unverified:** Claude Code's `enabledPlugins` setting in the repository's `.claude/settings.json`, e.g. `"enabledPlugins": {"hiway-kit@anthropic-plugin-directory": false}`. I could not test whether that overrides an account-synced plugin in a cloud session, and it would be a repo change through a fixer seat.
