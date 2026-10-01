#!/bin/bash
# The cloud environment's setup script for heatpump_optimizer seats (R9-PROC-3).
#
# NOT APPLIED CONFIG. A seat cannot change its own environment: tvofi pastes this
# into Project settings > Environment > Setup script, and new sessions run it.
# It gives a cloud seat the interpreter and pins CI runs, so `typing_ruler --mypy`
# and the real-Home-Assistant `ha_contract` run in the seat instead of on the Mac
# or only in CI (round-9 process review, item 5).
#
#   python   3.14.2, CI's `fast` and `typing` interpreter line (tests.yml)
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
PYVER=3.14.2

# A missing checkout warns and exits 0: a failing setup script would stop
# every session from starting, which costs more than a seat without pins.
[ -f "$REPO/tests/requirements-ci.txt" ] || {
  echo "cloud-setup: no checkout at $REPO, so no pins installed (set HPO_REPO)" >&2; exit 0; }

# The image's uv predates 3.14.2 ("No download found for request"), so a
# current uv comes from PyPI first; it fetches the interpreter itself.
python3 -m pip install -q --target "$PREFIX/uv" uv
UV="$PREFIX/uv/bin/uv"
export UV_PYTHON_INSTALL_DIR="$PREFIX/python"
"$UV" python install "$PYVER"
PY=$("$UV" python find "$PYVER")
"$PY" -c 'import sys; assert sys.version_info[:3] == (3, 14, 2), sys.version'

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
