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
#            the `typing` job installs it: mypy, homeassistant and
#            homeassistant-stubs; exported as HPO_TYPING_PYTHON, and asserted
#            to import the lock's homeassistant pin, read from the lock
#            (typing only: it has no scipy and no paho by design. The suites
#            run under venv-ci with PYTHONPATH=tests/hastub, the stub standing
#            in for Home Assistant; never put venv-ha first on PATH for them)
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
# narrowed (a test's stub directory ahead of the venv) is left alone, and it
# sets every other variable only where it is unset: a BASH_ENV naming it runs
# it ahead of every nested bash, and an unconditional RUNNER_TEMP there
# replaced the one each tests/entities.py harness hands its child
# (dev/audit/rca/R10-RCA-CLOUD-ENTITIES-ENV.md).
# Where the variables are unset, .claude/hooks/session-start.sh appends
# --variables, exported and quoted, to the harness's CLAUDE_ENV_FILE, which
# the harness sources before each Bash call, and prints its `toolchain:` line
# either way (dev/audit/rca/R10-RCA-FIXER-MD-KEY.md).
#
#   cloud-setup.sh --variables   print those variables, one NAME=value a line
#   cloud-setup.sh --check       in a seat: OK when python3 is venv-ci's,
#                                HPO_TYPING_PYTHON is executable and
#                                OPENBLAS_CORETYPE is the pinned core type
#                                (the golden fixtures' BLAS floats depend on
#                                it); else REFUSE naming the variables; exit 0
#                                or 1
#   cloud-setup.sh --self-test   the profile, variables and check arms, in a temp dir
set -euo pipefail

REPO=${HPO_REPO:-/home/user/heatpump_optimizer}
PREFIX=${HPO_PREFIX:-/opt/hpo}
PROFILE=${HPO_PROFILE:-/etc/profile.d/hpo-toolchain.sh}
CORETYPE=Haswell
# The seat identity (P320): an author in the environment overrides `git config`,
# so the four variables git reads first are exported; a runner default
# (Claude <noreply@anthropic.com>) then cannot author a seat's commit. The values
# are cloud_dispatch.py's SEAT_NAME and SEAT_EMAIL (its self-test asserts they agree).
SEAT_NAME=hpo-fixer
SEAT_EMAIL=70032254+tvofi@users.noreply.github.com
# RUNNER_TEMP (D): a governance job's `run:` steps read it; a seat replaying one
# has none. It is exported, not created: the replay does `mkdir -p "$RUNNER_TEMP"`.
SELF=$(readlink -f "${BASH_SOURCE[0]}")
. "$(dirname "$SELF")/../../../tests/throwaway_git.sh" # the one way a script builds a throwaway repository

write_profile() { # profile, prefix
  cat > "$1" <<EOF
# Written by tools/audit/seat/cloud-setup.sh, for login shells.
case ":\$PATH:" in *":$2/venv-ci/bin:"*) ;; *) export PATH="$2/venv-ci/bin:\$PATH" ;; esac
export HPO_TYPING_PYTHON="\${HPO_TYPING_PYTHON:-$2/venv-ha/bin/python}"
export OPENBLAS_CORETYPE="\${OPENBLAS_CORETYPE:-$CORETYPE}"
export GIT_AUTHOR_NAME="\${GIT_AUTHOR_NAME:-$SEAT_NAME}" GIT_AUTHOR_EMAIL="\${GIT_AUTHOR_EMAIL:-$SEAT_EMAIL}"
export GIT_COMMITTER_NAME="\${GIT_COMMITTER_NAME:-$SEAT_NAME}" GIT_COMMITTER_EMAIL="\${GIT_COMMITTER_EMAIL:-$SEAT_EMAIL}"
export RUNNER_TEMP="\${RUNNER_TEMP:-$2/runner-temp}"
EOF
}

variables() { # prefix: the environment variables a seat's shell needs
  local d rest="" parts
  IFS=: read -ra parts <<< "$PATH"
  for d in ${parts[@]+"${parts[@]}"}; do [ "$d" = "$1/venv-ci/bin" ] || rest="${rest:+$rest:}$d"; done
  printf '%s\n' "PATH=$1/venv-ci/bin:$rest" \
    "HPO_TYPING_PYTHON=$1/venv-ha/bin/python" "OPENBLAS_CORETYPE=$CORETYPE" \
    "GIT_AUTHOR_NAME=$SEAT_NAME" "GIT_AUTHOR_EMAIL=$SEAT_EMAIL" "GIT_COMMITTER_NAME=$SEAT_NAME" "GIT_COMMITTER_EMAIL=$SEAT_EMAIL" \
    "RUNNER_TEMP=$1/runner-temp"
}

check() { # prefix
  local py; py=$(command -v python3 || true)
  if [ "$py" = "$1/venv-ci/bin/python3" ] && [ -x "${HPO_TYPING_PYTHON:-}" ] \
    && [ "${OPENBLAS_CORETYPE:-}" = "$CORETYPE" ]; then
    echo "cloud-setup check: OK python3 is $py"; return 0
  fi
  echo "cloud-setup check: REFUSE python3 is ${py:-absent}," \
    "HPO_TYPING_PYTHON is ${HPO_TYPING_PYTHON:-unset}, OPENBLAS_CORETYPE is ${OPENBLAS_CORETYPE:-unset};" \
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
  fns="CORETYPE=$CORETYPE; $(declare -f variables check)"

  out=$(run bash -c 'python3')
  [ "$out" = system ]; expect "control: a non-login bash with no variables set gets the system python3 (the defect)" $?
  mapfile -t vars < <(PATH="$base" variables "$P")
  out=$(PATH="$P/venv-ci/bin:$base:$P/venv-ci/bin" variables "$P" | head -n 1)
  [ "$out" = "${vars[0]}" ]; expect "the printed PATH holds venv-ci/bin once, first, from a PATH holding it twice" $?
  out=$(run "${vars[@]}" bash -c python3)  # never-empty: vars is the seven-line output of variables, asserted above
  [ "$out" = venv ]; expect "a non-login bash under the printed variables gets venv-ci's python3" $?
  run "${vars[@]}" bash -c "$fns; check \"\$1\"" _ "$P" >/dev/null  # never-empty: vars is the seven-line output of variables, asserted above
  expect "check is OK under the printed variables" $?
  out=$(run bash -c "$fns; check \"\$1\"" _ "$P"); rc=$?
  [ "$rc" = 1 ] && case $out in *"REFUSE"*"PATH=$P/venv-ci/bin:$base HPO_TYPING_PYTHON=$P/venv-ha/bin/python OPENBLAS_CORETYPE=$CORETYPE"*) true ;; *) false ;; esac
  expect "check refuses without them, naming each variable" $?
  run "${vars[0]}" "${vars[2]}" bash -c "$fns; check \"\$1\"" _ "$P" >/dev/null
  [ $? = 1 ]; expect "check refuses venv-ci's python3 without HPO_TYPING_PYTHON" $?
  out=$(run "${vars[1]}" "${vars[2]}" bash -c "$fns; check \"\$1\"" _ "$P"); rc=$?
  [ "$rc" = 1 ] && case $out in *"REFUSE python3 is $W/sys/python3,"*) true ;; *) false ;; esac
  expect "check refuses the system python3 beside an executable HPO_TYPING_PYTHON" $?
  run "${vars[0]}" "${vars[1]}" bash -c "$fns; check \"\$1\"" _ "$P" >/dev/null
  [ $? = 1 ]; expect "check refuses without OPENBLAS_CORETYPE" $?
  run bash -c ". \"\$2\"; $fns; check \"\$1\"" _ "$P" "$W/profile.sh" >/dev/null
  expect "check is OK in a shell that sourced the profile" $?
  out=$(run "${vars[@]}" HPO_PREFIX="$P" bash "$SELF" --check); rc=$?  # never-empty: vars is the seven-line output of variables, asserted above
  [ "$rc" = 0 ] && case $out in *" OK "*) true ;; *) false ;; esac
  expect "cloud-setup.sh --check exits 0 under the printed variables" $?
  out=$(run HPO_PREFIX="$P" bash "$SELF" --check); rc=$?
  [ "$rc" = 1 ] && case $out in *"REFUSE"*) true ;; *) false ;; esac
  expect "cloud-setup.sh --check exits 1 without them" $?
  out=$(run bash -c '. "$1"; . "$1"; echo "$PATH"' _ "$W/profile.sh")
  [ "$out" = "$P/venv-ci/bin:$base" ]; expect "the profile sourced twice puts venv-ci/bin on PATH once" $?
  out=$(run BASH_ENV="$W/profile.sh" bash -c 'PATH="$1:$PATH" bash -c python3' _ "$W/stub")
  [ "$out" = stub ]; expect "under BASH_ENV a nested bash keeps a stub its caller put ahead of the venv (#2452)" $?
  [ "$(printf '%s\n' "${vars[@]}" | grep -cxF "RUNNER_TEMP=$P/runner-temp")" = 1 ]  # never-empty: vars is the seven-line output of variables, asserted above
  expect "variables prints RUNNER_TEMP" $?
  out=$(run bash -c '. "$1"; echo "$RUNNER_TEMP"' _ "$W/profile.sh")
  [ "$out" = "$P/runner-temp" ]; expect "the profile exports RUNNER_TEMP" $?
  # Every name the profile exports, from a shell that sourced it against one that
  # did not; PATH has its own arm above. Each must keep a caller's value through
  # a BASH_ENV-sourced nested bash (R10-RCA-CLOUD-ENTITIES-ENV).
  names=$(comm -13 <(run bash -c 'compgen -e' | sort) <(run bash -c '. "$1"; compgen -e' _ "$W/profile.sh" | sort) | grep -vx PATH)
  [ "$(printf '%s\n' "$names" | grep -c .)" = 7 ]; expect "the profile exports seven names besides PATH" $?
  out=$(run BASH_ENV="$W/profile.sh" bash -c 'echo "$RUNNER_TEMP"')
  [ "$out" = "$P/runner-temp" ]; expect "control: a nested bash under BASH_ENV runs the profile" $?
  kept=""
  for n in $names; do
    out=$(run "$n=caller" BASH_ENV="$W/profile.sh" bash -c 'printf %s "${!1}"' _ "$n")
    [ "$out" = caller ] || kept="$kept $n=$out"
  done
  [ -z "$kept" ] || echo "     overwritten:$kept"
  [ -z "$kept" ]; expect "under BASH_ENV a nested bash keeps every variable its caller set" $?
  n=$(printf '%s\n' "${vars[@]}" | grep -c '^GIT_\(AUTHOR\|COMMITTER\)_\(NAME\|EMAIL\)=')  # never-empty: vars is the seven-line output of variables, asserted above
  [ "$n" = 4 ]; expect "variables prints the four GIT_AUTHOR/COMMITTER exports" $?
  out=$(run bash -c '. "$1"; echo "$GIT_AUTHOR_NAME $GIT_AUTHOR_EMAIL $GIT_COMMITTER_NAME $GIT_COMMITTER_EMAIL"' _ "$W/profile.sh")
  [ "$out" = "$SEAT_NAME $SEAT_EMAIL $SEAT_NAME $SEAT_EMAIL" ]; expect "the profile exports the seat identity" $?
  throwaway_git_init "$W/r" -q  # its GIT_* identity lives in the init subshell only; run below is env -i
  git -C "$W/r" config user.name Claude; git -C "$W/r" config user.email noreply@anthropic.com
  run git -C "$W/r" commit -q --allow-empty -m x
  out=$(git -C "$W/r" log -1 --format='%an <%ae> %cn <%ce>')
  [ "$out" = "Claude <noreply@anthropic.com> Claude <noreply@anthropic.com>" ]
  expect "control: without the exports the config identity authors the commit" $?
  run "${vars[@]}" git -C "$W/r" commit -q --allow-empty -m y  # never-empty: vars is the seven-line output of variables, asserted above
  out=$(git -C "$W/r" log -1 --format='%an <%ae> %cn <%ce>')
  [ "$out" = "$SEAT_NAME <$SEAT_EMAIL> $SEAT_NAME <$SEAT_EMAIL>" ]
  expect "a commit made under the exports is authored and committed as the seat even with a conflicting user.name in config" $?

  printf 'cloud_setup self-test: %s checks, %s failed\n' "$((pass + fail))" "$fail"
  [ "$fail" = 0 ]
)

case ${1:-} in
  --variables) variables "$PREFIX"; exit 0 ;;
  --check) check "$PREFIX"; exit $? ;;
  --self-test) [ -n "${PR_BOUND:-}" ] || { . "$(dirname -- "$0")/pr_args.sh"; pr_bounded cloud_setup bash "$0" --self-test; }; self_test; exit $? ;;
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
HA_PIN=$(sed -n 's/^homeassistant==\([^ ]*\) .*/\1/p' "$REPO/tests/requirements-typing.txt")
"$PREFIX/venv-ha/bin/python" -c 'import homeassistant.const as c, sys; assert c.__version__ == sys.argv[1], c.__version__' "$HA_PIN"

write_profile "$PROFILE" "$PREFIX"

echo "cloud-setup: python $PYVER, venv-ci and venv-ha under $PREFIX;" \
  "a seat's shell needs these environment variables: $(variables "$PREFIX" | tr '\n' ' ')"
