#!/usr/bin/env bash
# R10-HOTFIX-TICK-SELFTEST-CHECKOUT: tick_loop.sh's self-test must read and move
# no checkout but scratch clones of its own, whatever its caller's checkout,
# GIT_DIR or PATH. The finder's control (the self-test run from a checkout
# behind origin/main: a branch fails a row, a detached head is moved) and the
# mutants that take each guard back out, on <rev>'s copy of the script.
#
#   bash dev/audit/harnesses/r10_tick_selftest_checkout.sh <rev> [arm...]
#
# Nothing runs in the caller's checkout: <rev>'s tick_loop.sh, heartbeat.sh,
# ref_privacy.py and tests/throwaway_git.sh are written to a scratch directory
# and every self-test runs from there or from a throwaway clone of it.
#
# Shape arms -- <rev>'s self-test run from a throwaway clone, its nested rows
# skipped (the clone is the nesting); each prints
#   <arm> behind=<n>: <the self-test's tally line> HEAD-MOVED|HEAD-UNMOVED
# and the failing rows:
#   branch    a branch clone one commit behind origin/main on tick_loop.sh
#   detached  the same clone, detached
#   gitdir    a detached clone behind, named by GIT_DIR and GIT_WORK_TREE (a git hook's environment)
#   shim      a branch clone at origin/main, the state dir's bin holding a gh with the seat shim's marker (a live seat's)
#   level     a branch clone at origin/main: the null control
# Every arm but shim runs under a scratch HPO_STATE_DIR whose bin holds a plain gh, so the
# caller's own gh, shim or not, decides nothing.
# Mutant arms -- <rev>'s whole self-test from a scratch copy that is no checkout,
# one guard taken back out; each prints `<arm>: <tally line> rc=<n>` and the failing rows:
#   whole       no mutation: the control every mutant is read against
#   nocheckout  the HPO_TICK_CODE_DIR export back below the TICK-GH rows
#   gitenv      throwaway_git_env back below the heartbeat rows
#   plaingh     the no-shim row's own plain gh taken off its PATH
#   envscrub    the line dropping the caller's HPO_TICK_* and HPO_SWEEP_MANDATE deleted (a rev before envi)
#   envi        --self-test runs the rows in the caller's environment, not re-run under env -i
#   allowlist   the rows' entry point lets a name off the allowlist through
#   pipefail    the self-test's `set +o pipefail` deleted
# A mutant arm needs the `# mut:selftest-*` markers and says so on a <rev> without them.
# No arm named runs the five shapes.
set -uo pipefail
rev=${1:?usage: r10_tick_selftest_checkout.sh <rev> [branch|detached|gitdir|shim|level|whole|nocheckout|gitenv|plaingh|envscrub|envi|allowlist|pipefail]...}; shift
[ $# -gt 0 ] || set -- branch detached gitdir shim level
top=$(git rev-parse --show-toplevel) || exit 2
sha=$(git -C "$top" rev-parse --verify -q "$rev^{commit}") || { echo "no commit $rev"; exit 2; }
d=$(mktemp -d) || exit 2
trap 'rm -rf "$d"' EXIT
L=tools/audit/seat/tick_loop.sh
extract() { # <dir>: <rev>'s five files, in a directory that is no checkout
  local f; mkdir -p "$1/tools/audit/seat" "$1/tests"
  for f in "$L" tools/audit/seat/heartbeat.sh tools/audit/seat/ref_privacy.py tools/audit/seat/offline_spy.py tests/throwaway_git.sh; do
    git -C "$top" show "$sha:$f" > "$1/$f" || exit 2
  done
}
extract "$d/src"
# shellcheck source=/dev/null
. "$d/src/tests/throwaway_git.sh"
mkdir -p "$d/plain/bin" "$d/shim/bin"
printf '#!/bin/sh\nexit 0\n' > "$d/plain/bin/gh"; printf '#!/bin/sh\n# hpo-gh-shim\nexit 0\n' > "$d/shim/bin/gh"
chmod +x "$d/plain/bin/gh" "$d/shim/bin/gh"
bare() { env -u HPO_TICK_CODE_DIR -u HPO_TICK_HEARTBEAT -u GIT_CEILING_DIRECTORIES HPO_STATE_DIR="$d/plain" "$@"; }
rows() { sed -n 's/^  FAIL /    FAIL /p; s/^    nested FAIL: /      nested FAIL: /p' "$1"; }

clones() { # the scratch origin, one commit ahead of the `old` clone on tick_loop.sh
  [ -d "$d/o.git" ] && return 0
  (
    throwaway_git_env
    cp -R "$d/src" "$d/n"
    throwaway_git_init "$d/o.git" -q --bare -b main && throwaway_git_init "$d/n" -q -b main || exit 2
    git -C "$d/n" add -A && git -C "$d/n" commit -qm base && git -C "$d/o.git" fetch -q "$d/n" main:main || exit 2
    throwaway_git_clone -q "$d/o.git" "$d/old" || exit 2
    printf '# ahead\n' >> "$d/n/$L"
    git -C "$d/n" commit -qam ahead && git -C "$d/o.git" fetch -q "$d/n" main:main || exit 2
    throwaway_git_clone -q "$d/o.git" "$d/new" || exit 2
  ) || { echo "the scratch clones could not be built"; exit 2; }
}

shape() { # <arm>
  local arm=$1 c=$d/c-$1 h0 h1 n m
  local -a pre=()
  clones; rm -rf "$c"
  case $arm in
    branch) cp -R "$d/old" "$c" ;;
    detached) cp -R "$d/old" "$c"; (throwaway_git_env; git -C "$c" checkout -q --detach) ;;
    gitdir) cp -R "$d/old" "$c"; (throwaway_git_env; git -C "$c" checkout -q --detach); pre=(GIT_DIR="$c/.git" GIT_WORK_TREE="$c") ;;
    shim) cp -R "$d/new" "$c"; pre=(HPO_STATE_DIR="$d/shim") ;;
    level) cp -R "$d/new" "$c" ;;
  esac
  h0=$(throwaway_git_env; git -C "$c" rev-parse HEAD)
  HPO_TICK_SELFTEST_NESTED=1 bare ${pre[@]+"${pre[@]}"} bash "$c/$L" --self-test > "$d/$arm.log" 2>&1
  h1=$(throwaway_git_env; git -C "$c" rev-parse HEAD)
  n=$(throwaway_git_env; git -C "$c" fetch -q origin main; git -C "$c" rev-list --count "$h0..origin/main")
  [ "$h0" = "$h1" ] && m=HEAD-UNMOVED || m=HEAD-MOVED
  echo "$arm behind=$n: $(tail -n 1 "$d/$arm.log") $m"; rows "$d/$arm.log"
}

mutant() { # <arm>
  local arm=$1 m=$d/m-$1 rc
  rm -rf "$m"; extract "$m"
  python3 - "$m/$L" "$arm" 2>/dev/null <<'PY' || { echo "$arm: NOT RUN, the mutation did not apply (no '# mut:selftest-*' marker at this rev?)"; return; }
import sys
p, arm = sys.argv[1:]
s = open(p).read().split("\n")
def marked(marker):
    g = [i for i, l in enumerate(s) if l.rstrip().endswith("# mut:" + marker)]
    assert len(g) == 1, (marker, g)
    return g[0]
def move(marker, after):  # the marked line, back to where the merge base ran it
    line = s.pop(marked(marker))
    a = [i for i, l in enumerate(s) if after in l]
    assert len(a) == 1, (after, a)
    s.insert(a[0] + 1, line)
if arm == "nocheckout":
    move("selftest-nocheckout", 'ck "a seat bin dir with no gh shim')
elif arm == "gitenv":
    move("selftest-gitenv", "# The real script against a bare remote")
elif arm == "plaingh":
    i = marked("selftest-plaingh")
    assert 'PATH="$t/bare:$PATH" ' in s[i]
    s[i] = s[i].replace('PATH="$t/bare:$PATH" ', "")
elif arm == "envscrub":
    s.pop(marked("selftest-envscrub"))
elif arm == "envi":
    i = marked("selftest-envi")
    s[i] = '  tick_loop_self_test  # mut:selftest-envi'
elif arm == "allowlist":
    i = marked("selftest-allowlist")
    assert '*" $v "*) ;; *)' in s[i]
    s[i] = s[i].replace('*" $v "*) ;; *)', '*) ;; *" $v "*)')
elif arm == "pipefail":
    s.pop(marked("selftest-pipefail"))
else:
    assert arm == "whole"
open(p, "w").write("\n".join(s))
PY
  bash -n "$m/$L" || { echo "$arm: NOT RUN, the mutant does not parse"; return; }
  bare bash "$m/$L" --self-test > "$d/$arm.log" 2>&1; rc=$?
  echo "$arm: $(tail -n 1 "$d/$arm.log") rc=$rc"; rows "$d/$arm.log"
}

echo "rev $sha"
for arm in "$@"; do
  case $arm in
    branch|detached|gitdir|shim|level) shape "$arm" ;;
    whole|nocheckout|gitenv|plaingh|envscrub|envi|allowlist|pipefail) mutant "$arm" ;;
    *) echo "unknown arm '$arm'"; exit 2 ;;
  esac
done
