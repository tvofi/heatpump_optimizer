#!/bin/bash
# seat_venv.sh -- build the seat interpreter on a workstation, reproducibly.
#
#   tools/audit/seat/seat_venv.sh                    build (or rebuild) the venv
#   tools/audit/seat/seat_venv.sh --install-shims <bin dir>
#   tools/audit/seat/seat_venv.sh --check            report what the venv holds
#   tools/audit/seat/seat_venv.sh --self-test        the recipe and shim arms
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
# WHAT IT BUILDS. Under $HPO_STATE_DIR (default ~/.local/state/hpo):
#   python   the version tests/typing_budgets.json records for the `typing`
#            census (census.environment.python), read at run time, fetched by
#            `uv` when $HPO_PYTHON does not name an interpreter of that version
#   venv-ci  tests/requirements-ci.txt with --require-hashes, and every sdist
#            build under --build-constraint tests/requirements-build.txt --
#            exactly what CI's `fast` job installs
#   venv-ha  tests/requirements-typing.txt, hash-pinned, --no-deps, and the
#            homeassistant version assertion -- cloud-setup.sh's pins call,
#            so a Mac seat's scoped gate checks the mypy census (#1951)
# A rebuild replaces each venv wholesale; it never upgrades in place.
#
# THE SHIMS. tools/audit/seat/shims/seat-python and seat-python3 exec the
# venv-ci interpreter through the same $HPO_STATE_DIR default, so they hold no
# machine path, and export HPO_TYPING_PYTHON to venv-ha/bin/python only when
# that interpreter exists and the variable is unset -- never overriding a
# value the seat set. --install-shims copies them, as `python` and `python3`,
# into the bin directory you name, which goes first on the seats' PATH:
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
VENV_HA=$STATE/venv-ha
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
  [ -x "$VENV_HA/bin/python" ] || die "no typing venv at $VENV_HA; run $0 to build it"
  "$VENV_HA/bin/python" -c 'import homeassistant.const as c; assert c.__version__ == "2026.9.3", c.__version__' \
    || die "$VENV_HA is missing a pinned homeassistant: rebuild"
  printf 'seat_venv: %s homeassistant %s\n' "$VENV_HA" \
    "$("$VENV_HA/bin/python" -c 'import homeassistant.const as c; print(c.__version__)')"
}

# Stub interpreters, not a live Home Assistant wheel: what is pinned here is
# the recipe and the shim export, which need no toolchain. The disk figure
# for a real venv-ha is a body measurement, not an arm.
# A subshell so `set +e` cannot leak into the build path.
self_test() (
  set +e
  W=$(mktemp -d) || { echo "self-test: no temporary directory"; return 1; }
  pass=0; fail=0
  ok() { pass=$((pass + 1)); printf '  ok   %s\n' "$1"; }
  bad() { fail=$((fail + 1)); printf '  FAIL %s\n' "$1"; }
  eq() { # name got want -- no command substitution on this line
    if [ "$2" = "$3" ]; then ok "$1"; else bad "$1"; printf '         got %s\n         want %s\n' "$2" "$3"; fi
  }
  expect() { if [ "$2" = 0 ]; then ok "$1"; else bad "$1"; fi; }
  real_py=$(command -v python3)
  # If python3 on PATH is itself a seat shim, follow it to a real interpreter
  # so `import os` in the shim arms is not a second shim exec.
  case $real_py in
    */hpo-seats/bin/python3|*/hpo-seats/bin/python)
      real_py="${HPO_STATE_DIR:-$HOME/.local/state/hpo}/venv-ci/bin/python3" ;;
  esac
  [ -x "$real_py" ] || real_py=/usr/bin/python3
  mkdir -p "$W/venv-ci/bin" "$W/venv-ha/bin" "$W/bin"
  # Wrapper: the shim execs this; it must be a real interpreter so os.environ
  # is the one the shim exported (or did not).
  printf '#!/bin/sh\nexec %s "$@"\n' "$real_py" > "$W/venv-ci/bin/python3"
  chmod 755 "$W/venv-ci/bin/python3"
  printf '#!/bin/sh\nexit 0\n' > "$W/venv-ha/bin/python"
  chmod 755 "$W/venv-ha/bin/python"
  # HOME is part of the fixture: the shim's second root is the documented
  # default state root (`$HOME/.local/state/hpo`), so every arm here controls
  # it. Without that, the "exports nothing when venv-ha is absent" null
  # control would depend on the box the self-test runs on (#2039).
  run_shim() { # shim-path; remaining args to the interpreter
    s=$1; shift
    HOME=$W/fakehome HPO_STATE_DIR=$W env -u HPO_TYPING_PYTHON "$s" "$@"
  }
  probe='import os; print(os.environ["HPO_TYPING_PYTHON"] if "HPO_TYPING_PYTHON" in os.environ else "UNSET")'
  ha=$W/venv-ha/bin/python
  for s in "$ROOT/tools/audit/seat/shims/seat-python" "$ROOT/tools/audit/seat/shims/seat-python3"; do
    name=${s##*/}
    out=$(run_shim "$s" -c "$probe")
    eq "$name exports HPO_TYPING_PYTHON when venv-ha exists and the variable is unset" "$out" "$ha"
    out=$(HOME=$W/fakehome HPO_STATE_DIR=$W HPO_TYPING_PYTHON=/already "$s" -c "$probe")
    eq "$name does not override a value the seat set" "$out" "/already"
    out=$(HOME=$W/fakehome HPO_STATE_DIR=$W HPO_TYPING_PYTHON= "$s" -c "$probe")
    eq "$name does not override an empty value the seat set" "$out" ""
  done
  rm -f "$W/venv-ha/bin/python"
  out=$(run_shim "$ROOT/tools/audit/seat/shims/seat-python3" -c "$probe")
  eq "the shim exports nothing when venv-ha is absent (null control)" "$out" "UNSET"
  : > "$W/venv-ha/bin/python" && chmod 755 "$W/venv-ha/bin/python"

  # #2039: the shim reaches the pinned interpreter across state roots, and
  # refuses naming the build command when no root holds one. The seat's own
  # state root wins; the documented default root is the fallback, because the
  # pin is a machine toolchain and not per-seat state. The base this replaces
  # exec'd `$HPO_STATE_DIR/venv-ci/bin/python3` unconditionally: with a state
  # that holds no venv-ci it died `rc 126, no such file` -- no interpreter and
  # no remedy -- which is the #2039 shape.
  # The fallback interpreter is a stub that answers for the DEFAULT root and no
  # other, so reaching it is what the arm reads; a wrapper over the ambient
  # interpreter would answer identically from either root and pin nothing.
  mkdir -p "$W/fakehome/.local/state/hpo/venv-ci/bin" "$W/seat"
  printf '#!/bin/sh\nprintf "DEFAULT-ROOT-VENV-CI\\n"\n' \
    > "$W/fakehome/.local/state/hpo/venv-ci/bin/python3"
  chmod 755 "$W/fakehome/.local/state/hpo/venv-ci/bin/python3"
  for s in "$ROOT/tools/audit/seat/shims/seat-python" "$ROOT/tools/audit/seat/shims/seat-python3"; do
    name=${s##*/}
    got=$(HOME=$W/fakehome HPO_STATE_DIR=$W/seat "$s" -c 'print(1)')
    eq "$name reaches the default root's venv-ci when the seat's state holds none" "$got" "DEFAULT-ROOT-VENV-CI"
  done
  rm -rf "$W/fakehome/.local/state/hpo/venv-ci"
  for s in "$ROOT/tools/audit/seat/shims/seat-python" "$ROOT/tools/audit/seat/shims/seat-python3"; do
    name=${s##*/}
    got=$(HOME=$W/fakehome HPO_STATE_DIR=$W/seat "$s" -c 'print(1)' 2>&1)
    rc=$?
    [ "$rc" != 0 ] && printf '%s' "$got" | grep -qF 'tools/audit/seat/seat_venv.sh'
    expect "$name refuses naming the build command when no root holds a pinned interpreter" $?
    got=$(HOME=$W/fakehome HPO_STATE_DIR=$W/seat "$s" -c 'print(2)' 2>&1)
    case $got in
      2) bad "$name never falls through to an unpinned interpreter (null control)" ;;
      *) ok "$name never falls through to an unpinned interpreter (null control)" ;;
    esac
  done

  # --check: stub venv-ci so the numpy import is hermetic, then drive the
  # homeassistant assertion the recipe owes.
  ci_stub=$W/venv-ci/bin/python3
  cat > "$ci_stub" <<STUB
#!/bin/sh
if [ "\$1" = "-c" ]; then
  case "\$2" in
    *version_info*) printf '%s\n' "$want" ;;
    *numpy.__version*) echo stub-numpy ;;
    *scipy.__version*) echo stub-scipy ;;
    *) exit 0 ;;
  esac
  exit 0
fi
exit 0
STUB
  chmod 755 "$ci_stub"
  ha_ok=$W/venv-ha/bin/python
  cat > "$ha_ok" <<'STUB'
#!/bin/sh
if [ "$1" = "-c" ]; then
  case "$2" in
    *print\(c.__version__*) echo 2026.9.3 ;;
    *homeassistant.const*) exit 0 ;;
  esac
fi
exit 0
STUB
  chmod 755 "$ha_ok"
  out=$(HPO_STATE_DIR=$W bash "$ROOT/tools/audit/seat/seat_venv.sh" --check 2>&1)
  rc=$?
  echo "$out" | grep -q 'venv-ha' && [ "$rc" = 0 ]
  expect "--check reports venv-ha when it is present" $?
  ha_bad=$W/ha-bad
  mkdir -p "$ha_bad/bin"
  printf '#!/bin/sh\nexit 1\n' > "$ha_bad/bin/python"
  chmod 755 "$ha_bad/bin/python"
  # Point STATE at a tree whose venv-ha python refuses the assertion.
  mkdir -p "$W/bad/venv-ci/bin"
  cp "$ci_stub" "$W/bad/venv-ci/bin/python3"
  mkdir -p "$W/bad/venv-ha/bin"
  cp "$ha_bad/bin/python" "$W/bad/venv-ha/bin/python"
  out=$(HPO_STATE_DIR=$W/bad bash "$ROOT/tools/audit/seat/seat_venv.sh" --check 2>&1)
  rc=$?
  [ "$rc" != 0 ]
  expect "--check refuses a venv-ha whose homeassistant assertion fails" $?
  rm -rf "$W/missing/venv-ha"
  mkdir -p "$W/missing/venv-ci/bin"
  cp "$ci_stub" "$W/missing/venv-ci/bin/python3"
  out=$(HPO_STATE_DIR=$W/missing bash "$ROOT/tools/audit/seat/seat_venv.sh" --check 2>&1)
  rc=$?
  [ "$rc" != 0 ] && echo "$out" | grep -q 'venv-ha'
  expect "--check refuses a missing venv-ha" $?

  # The Mac recipe's venv-ha install is cloud-setup.sh's pins call: hashed,
  # --no-deps, the typing lock. Drop this function's body so its own strings
  # cannot satisfy the grep; keep check() above and the pins() call below.
  prod=$(awk '/^self_test\(\)/{p=1; next} p && /^)$/{p=0; next} !p' \
    "$ROOT/tools/audit/seat/seat_venv.sh")
  echo "$prod" | grep -qF -- '-m pip install -q --require-hashes'
  expect "pins() still hash-pins (venv-ci control)" $?
  echo "$prod" | grep -qF 'pins "$VENV_HA" --no-deps -r "$ROOT/tests/requirements-typing.txt"'
  expect "the build calls pins() for venv-ha with --no-deps from the typing lock" $?
  echo "$prod" | grep -qF 'import homeassistant.const as c; assert c.__version__ == "2026.9.3"'
  expect "check() carries cloud-setup.sh's homeassistant assertion" $?
  grep -qF 'pins venv-ha --no-deps -r "$REPO/tests/requirements-typing.txt"' \
    "$ROOT/tools/audit/seat/cloud-setup.sh"
  expect "cloud-setup.sh is still the oracle for that pins call" $?

  rm -rf "$W"
  printf 'seat_venv self-test: %s checks, %s failed\n' "$((pass + fail))" "$fail"
  [ "$fail" = 0 ]
)

case ${1:-} in
  --check) check; exit 0 ;;
  --self-test) self_test; exit $? ;;
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
  *) sed -n '2,7p' "$0" >&2; exit 2 ;;
esac

PY=${HPO_PYTHON:-}
if [ -z "$PY" ] || [ "$(pyver "$PY")" != "$want" ]; then
  command -v uv >/dev/null || die "python $want is not \$HPO_PYTHON and there is no uv to fetch it (https://docs.astral.sh/uv/)"
  uv python install "$want" >/dev/null
  PY=$(uv python find "$want")
fi
[ "$(pyver "$PY")" = "$want" ] || die "$PY is not python $want"

mkdir -p "$STATE"
# dest, pip arguments... -- cloud-setup.sh's pins(), with an atomic replace
# so a failed install does not leave a half-written venv. venv-ha is the
# same call: hash-pinned, --no-deps, the typing lock.
pins() {
  dest=$1; shift
  rm -rf "$dest.new"
  "$PY" -m venv "$dest.new"
  "$dest.new/bin/python" -m pip install -q --upgrade pip
  "$dest.new/bin/python" -m pip install -q --require-hashes \
    --build-constraint "$ROOT/tests/requirements-build.txt" "$@"
  rm -rf "$dest" && mv "$dest.new" "$dest"
}
pins "$VENV" -r "$ROOT/tests/requirements-ci.txt"
pins "$VENV_HA" --no-deps -r "$ROOT/tests/requirements-typing.txt"
# A venv records its own path in its scripts; the move above leaves only
# `bin/python*` in use, which resolve through pyvenv.cfg and not that path.
check
