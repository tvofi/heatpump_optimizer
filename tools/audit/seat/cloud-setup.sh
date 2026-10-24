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
#
# THE TOOLCHAIN REACHES A SEAT ONLY THROUGH THE ENVIRONMENT'S VARIABLES. A
# seat's Bash call is `bash -c` inheriting the agent's environment, and Claude
# Code's shell snapshot re-exports the agent's own PATH; so neither the profile
# this script writes nor BASH_ENV reaches it (a first-level bash on a socket
# stdin, as the agent's is, reads ~/.bashrc in place of BASH_ENV, and the stock
# ~/.bashrc returns at once), and nothing this script does can. Set, beside
# the setup script, the variables its last line prints: PATH with venv-ci/bin
# first, HPO_TYPING_PYTHON and OPENBLAS_CORETYPE. The profile is for login
# shells; it prepends venv-ci/bin only when absent, so a PATH a caller
# narrowed (a test's stub directory ahead of the venv) is left alone.
#
#   cloud-setup.sh --variables   print those variables, one NAME=value a line
#   cloud-setup.sh --check       in a seat: OK when python3 is venv-ci's, else
#                                REFUSE naming the variables; exit 0 or 1
#   cloud-setup.sh --self-test   the profile and check arms, in a temp dir
set -euo pipefail

REPO=${HPO_REPO:-/home/user/heatpump_optimizer}
PREFIX=${HPO_PREFIX:-/opt/hpo}
PROFILE=${HPO_PROFILE:-/etc/profile.d/hpo-toolchain.sh}

write_profile() { # profile, prefix
  cat > "$1" <<EOF
# Written by tools/audit/seat/cloud-setup.sh, for login shells.
case ":\$PATH:" in *":$2/venv-ci/bin:"*) ;; *) export PATH="$2/venv-ci/bin:\$PATH" ;; esac
export HPO_TYPING_PYTHON="$2/venv-ha/bin/python"
export OPENBLAS_CORETYPE=Haswell
EOF
}

variables() { # prefix: the environment variables a seat's shell needs
  local d rest="" parts
  IFS=: read -ra parts <<< "$PATH"
  for d in "${parts[@]}"; do [ "$d" = "$1/venv-ci/bin" ] || rest="${rest:+$rest:}$d"; done
  printf '%s\n' "PATH=$1/venv-ci/bin:$rest" \
    "HPO_TYPING_PYTHON=$1/venv-ha/bin/python" OPENBLAS_CORETYPE=Haswell
}

check() { # prefix
  local py; py=$(command -v python3 || true)
  if [ "$py" = "$1/venv-ci/bin/python3" ] && [ -x "${HPO_TYPING_PYTHON:-}" ]; then
    echo "cloud-setup check: OK python3 is $py"; return 0
  fi
  echo "cloud-setup check: REFUSE python3 is ${py:-absent}, not $1/venv-ci/bin/python3;" \
    "set the environment's variables: $(variables "$1" | tr '\n' ' ')"
  return 1
}

# Every child runs with stdin from /dev/null: `env -i` drops SHLVL, and a
# first-level bash on a socket stdin (the agent's) skips BASH_ENV.
self_test() (
  set +e; pass=0; fail=0
  W=$(mktemp -d) || { echo "self-test: no temporary directory"; return 1; }
  trap 'rm -rf "$W"' EXIT
  ok() { pass=$((pass + 1)); echo "ok   $1"; }
  bad() { fail=$((fail + 1)); echo "FAIL $1"; }
  expect() { if [ "$2" = 0 ]; then ok "$1"; else bad "$1"; fi; }
  stub() { mkdir -p "$1"; printf '#!/bin/sh\necho %s\n' "$2" > "$1/$3"; chmod +x "$1/$3"; }
  P="$W/hpo"; stub "$P/venv-ci/bin" venv python3; stub "$P/venv-ha/bin" ha python
  stub "$W/stub" stub python3; stub "$W/sys" system python3
  write_profile "$W/profile.sh" "$P"
  base="$W/sys:/usr/bin:/bin"
  run() { env -i HOME="$W" PATH="$base" "$@" </dev/null; }
  fns="$(declare -f variables check)"

  out=$(run bash -c 'python3')
  [ "$out" = system ]; expect "control: a non-login bash with no variables set gets the system python3 (the defect)" $?
  mapfile -t vars < <(PATH="$base" variables "$P")
  out=$(PATH="$P/venv-ci/bin:$base:$P/venv-ci/bin" variables "$P" | head -n 1)
  [ "$out" = "${vars[0]}" ]; expect "the printed PATH holds venv-ci/bin once, first, from a PATH holding it twice" $?
  out=$(run "${vars[@]}" bash -c python3)
  [ "$out" = venv ]; expect "a non-login bash under the printed variables gets venv-ci's python3" $?
  run "${vars[@]}" bash -c "$fns; check \"\$1\"" _ "$P" >/dev/null
  expect "check is OK under the printed variables" $?
  out=$(run bash -c "$fns; check \"\$1\"" _ "$P"); rc=$?
  [ "$rc" = 1 ] && case $out in *"REFUSE"*"PATH=$P/venv-ci/bin:$base HPO_TYPING_PYTHON=$P/venv-ha/bin/python"*) true ;; *) false ;; esac
  expect "check refuses without them, naming each variable" $?
  run "${vars[0]}" bash -c "$fns; check \"\$1\"" _ "$P" >/dev/null
  [ $? = 1 ]; expect "check refuses venv-ci's python3 without HPO_TYPING_PYTHON" $?
  out=$(run bash -c '. "$1"; . "$1"; echo "$PATH"' _ "$W/profile.sh")
  [ "$out" = "$P/venv-ci/bin:$base" ]; expect "the profile sourced twice puts venv-ci/bin on PATH once" $?
  out=$(run BASH_ENV="$W/profile.sh" bash -c 'PATH="$1:$PATH" bash -c python3' _ "$W/stub")
  [ "$out" = stub ]; expect "under BASH_ENV a nested bash keeps a stub its caller put ahead of the venv (#2452)" $?

  printf 'cloud_setup self-test: %s checks, %s failed\n' "$((pass + fail))" "$fail"
  [ "$fail" = 0 ]
)

case ${1:-} in
  --variables) variables "$PREFIX"; exit 0 ;;
  --check) check "$PREFIX"; exit $? ;;
  --self-test) self_test; exit $? ;;
  "") ;;
  *) echo "usage: cloud-setup.sh [--variables | --check | --self-test]" >&2; exit 2 ;;
esac

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

write_profile "$PROFILE" "$PREFIX"

echo "cloud-setup: python $PYVER, venv-ci and venv-ha under $PREFIX;" \
  "a seat's shell needs these environment variables: $(variables "$PREFIX" | tr '\n' ' ')"
