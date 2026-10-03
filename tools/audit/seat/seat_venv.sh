#!/bin/bash
# seat_venv.sh -- build the seat interpreter on a workstation, reproducibly.
#
#   tools/audit/seat/seat_venv.sh                    build (or rebuild) the venv
#   tools/audit/seat/seat_venv.sh --install-shims <bin dir>
#   tools/audit/seat/seat_venv.sh --check            report what the venv holds
#
# WHY THIS EXISTS. The Mac seats ran `python3` through two shims in a seat
# bin directory pointing at a hand-built venv in a temp dir. A temp
# cleanup on 2026-10-03 deleted it, and nothing in the tree said how it had
# been made; it was rebuilt by hand from the same pins this script reads. The
# venv now lives in a state directory a temp cleanup does not touch, and the
# recipe lives here. `cloud-setup.sh` is the same recipe for a cloud seat
# (Linux, /opt, a login profile); this one writes nothing outside its prefix
# and the bin directory you name.
#
# WHAT IT BUILDS. $HPO_STATE_DIR/venv-ci (default ~/.local/state/hpo/venv-ci):
#   python   the version tests/typing_budgets.json records for the `typing`
#            census (census.environment.python), read at run time, fetched by
#            `uv` when $HPO_PYTHON does not name an interpreter of that version
#   pins     tests/requirements-ci.txt with --require-hashes, and every sdist
#            build under --build-constraint tests/requirements-build.txt --
#            exactly what CI's `fast` job installs
# A rebuild replaces the venv wholesale; it never upgrades in place.
#
# THE SHIMS. tools/audit/seat/shims/seat-python and seat-python3 exec the
# venv's interpreter through the same $HPO_STATE_DIR default, so they hold no
# machine path. --install-shims copies them, as `python` and `python3`, into
# the bin directory you name, which goes first on the seats' PATH:
#
#   tools/audit/seat/seat_venv.sh && tools/audit/seat/seat_venv.sh --install-shims <seat bin dir>
#
# Environment: HPO_STATE_DIR, HPO_PYTHON (an interpreter to use instead of uv's,
# and the first one tried for reading the census).
# Plain variables, no arrays: macOS /bin/bash 3.2 rejects an empty array under -u.
set -euo pipefail

ROOT=$(cd "$(dirname -- "$0")/../../.." && pwd)
STATE=${HPO_STATE_DIR:-$HOME/.local/state/hpo}
VENV=$STATE/venv-ci
die() { printf 'seat_venv: %s\n' "$*" >&2; exit 1; }

pyver() { "$1" -c 'import sys; print("%d.%d.%d" % sys.version_info[:3])' 2>/dev/null; }
# The census is read by an interpreter named by absolute path, never by the
# first `python3` on PATH: in the state this script exists to repair, that one
# is a seat shim pointing at the venv that was deleted (#1879 round 1, N4).
reader() {
  for c in "${HPO_PYTHON:-}" /usr/bin/python3 /usr/local/bin/python3 /opt/homebrew/bin/python3; do
    [ -n "$c" ] && [ -x "$c" ] && "$c" -c 'import json' >/dev/null 2>&1 && { printf '%s\n' "$c"; return 0; }
  done
  return 1
}
R=$(reader) || die "no working interpreter at \$HPO_PYTHON, /usr/bin/python3, /usr/local/bin/python3 or /opt/homebrew/bin/python3 to read the census"
want=$("$R" -c 'import json, sys; print(json.load(open(sys.argv[1]))["census"]["environment"]["python"])' \
  "$ROOT/tests/typing_budgets.json") || die "cannot read the census python from tests/typing_budgets.json"

check() {
  [ -x "$VENV/bin/python3" ] || die "no venv at $VENV; run $0 to build it"
  have=$(pyver "$VENV/bin/python3")
  [ "$have" = "$want" ] || die "$VENV runs python $have, the census records $want: rebuild"
  "$VENV/bin/python3" -c 'import numpy, scipy, voluptuous, aiohttp, yaml' || die "$VENV is missing a pinned package: rebuild"
  printf 'seat_venv: %s python %s, numpy %s, scipy %s\n' "$VENV" "$have" \
    "$("$VENV/bin/python3" -c 'import numpy; print(numpy.__version__)')" \
    "$("$VENV/bin/python3" -c 'import scipy; print(scipy.__version__)')"
}

case ${1:-} in
  --check) check; exit 0 ;;
  --install-shims)
    dest=${2:?--install-shims takes the bin directory}
    mkdir -p "$dest"
    for s in python python3; do
      cp "$ROOT/tools/audit/seat/shims/seat-$s" "$dest/$s" && chmod 755 "$dest/$s"
    done
    printf 'seat_venv: shims installed in %s; they run %s/bin/python3\n' "$dest" "$VENV"
    "$dest/python3" -c 'import sys; print("seat_venv: shim resolves to", sys.executable)' \
      || die "the installed shim does not start; build the venv first"
    exit 0 ;;
  '') ;;
  *) sed -n '2,6p' "$0" >&2; exit 2 ;;
esac

PY=${HPO_PYTHON:-}
if [ -z "$PY" ] || [ "$(pyver "$PY")" != "$want" ]; then
  command -v uv >/dev/null || die "python $want is not \$HPO_PYTHON and there is no uv to fetch it (https://docs.astral.sh/uv/)"
  uv python install "$want" >/dev/null
  PY=$(uv python find "$want")
fi
[ "$(pyver "$PY")" = "$want" ] || die "$PY is not python $want"

mkdir -p "$STATE"
rm -rf "$VENV.new"
"$PY" -m venv "$VENV.new"
"$VENV.new/bin/python3" -m pip install -q --upgrade pip
"$VENV.new/bin/python3" -m pip install -q --require-hashes \
  --build-constraint "$ROOT/tests/requirements-build.txt" -r "$ROOT/tests/requirements-ci.txt"
rm -rf "$VENV" && mv "$VENV.new" "$VENV"
# A venv records its own path in its scripts; the move above leaves only
# `bin/python*` in use, which resolve through pyvenv.cfg and not that path.
check
