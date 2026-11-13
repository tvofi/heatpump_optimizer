# Review packet #3520
head: c17c11af72a8af22fc19e5cd7360bf8adf0acabe
base: b6577827b4823cfacb0a309911f3572a6fccd7d2

Start here (fix-review.md). Re-read the live check state before a verdict: the digest is as read at render.

## Gate digest: red
CodeQL id=131864029247 success
arch-score / arch-score id=131863510992 success
arm id=131861784509 skipped
budget-raise-gate / budget-raise-gate id=131863511152 success
cancel-superseded id=131861745254 success
codeql id=131862994628 skipped
codeql / Analyze (actions) id=131863511239 success
codeql / Analyze (javascript-typescript) id=131863511321 success
codeql / Analyze (python) id=131863511259 success
gate id=131863947261 failure
governance id=131862995129 skipped
governance / delivery-status id=131863511307 success
governance / delivery-status-publish id=131863513146 skipped
governance / env-matrix id=131863511326 in_progress
governance / instrument-self-tests id=131863511389 queued
governance / policy-docs id=131863511297 success
governance / record id=131863513325 skipped
governance / wave-script id=131863511323 queued
hassfest id=131862994129 skipped
hassfest / hassfest id=131863511199 success
kernel-points id=131863513035 skipped
pr-contract id=131863949185 skipped
prelude id=131861745607 success
refresh id=131861745749 success
sweep-self id=131864809122 skipped
tests id=131862994410 skipped
tests / arch-instrument id=131865496036 queued
tests / briefs id=131863511294 in_progress
tests / browser id=131865496181 queued
tests / closure-scope id=131863511254 success
tests / closures id=131865496142 queued
tests / coverage id=131865496073 queued
tests / fast (3.14) id=131865496080 queued
tests / mutation id=131863511235 success
tests / mutation-autofix id=131864216250 skipped
tests / mutation-pins id=131864216720 skipped
tests / nightly-ha id=131865497811 skipped
tests / nightly-status id=131863511365 success
tests / replay id=131865499981 skipped
tests / typing id=131865496021 queued
validate id=131862994349 skipped
validate / validate-hacs id=131863510948 success

## Refusals
introduced-red: unreadable: head governance / instrument-self-tests job 131863511389: queued has not concluded: an introduced red cannot be ruled out (fail closed)

## Advisories
required-wait: required context `gate` reads concluded failure at c17c11af72a8af22fc19e5cd7360bf8adf0acabe in the digest, but merge_train.py classify --pr reads WAIT (pending: gate red: none): classify decides, as bus.sh's dispatch does, and a pending check never refuses

## carry_audit at the head
CARRY-AUDIT: 0 finding item(s): 0 routed, 0 unrouted, 0 bad destination(s)

## figure_lint at the head
unverified channels fn-all: tick_loop self-test: 41 checks, 0 failed rc=0 fn-calls=0 victim-refs=0
             no segment of this names a program this check knows
  unverified channels bashenv-all: tick_loop self-test: 41 checks, 0 failed rc=0 fn-calls=0 victim-refs=0
             no segment of this names a program this check knows
  unverified channels fn-exec: ...line 67: refused: --self-test refused: ...; no row ran rc=1 fn-calls=1 victim-refs=0
             no segment of this names a program this check knows
  unverified channels posix: /usr/bin/bash: `exec': is a special builtin rc=2 fn-calls=0 victim-refs=0
             no segment of this names a program this check knows
  unverified channels shellopts-posix: tick_loop self-test: 41 checks, 0 failed rc=0 fn-calls=0 victim-refs=0
             no segment of this names a program this check knows
  unverified channels noexec:  rc=0 fn-calls=0 victim-refs=0
             no segment of this names a program this check knows
  unverified channels opts: tick_loop self-test: 41 checks, 0 failed rc=0 fn-calls=0 victim-refs=0
             no segment of this names a program this check knows
  unverified channels env: tick_loop self-test: 41 checks, 0 failed rc=0 fn-calls=0 victim-refs=0
             no segment of this names a program this check knows
  unverified channels path: tick_loop self-test: 41 checks, 0 failed rc=0 fn-calls=0 victim-refs=0
             no segment of this names a program this check knows
  unverified channels ifs: tick_loop self-test: 41 checks, 0 failed rc=0 fn-calls=0 victim-refs=0
             no segment of this names a program this check knows
  unverified channels null control fn: fn-calls=4
             no segment of this names a program this check knows
  unverified channels null control bashenv: fn-calls=4
             no segment of this names a program this check knows
  unverified channels null control env: fn-calls=1
             no segment of this names a program this check knows
  unverified channels null control path: fn-calls=1
             no segment of this names a program this check knows
  unverified channels corpus: 85 function names
             no segment of this names a program this check knows
  ok         bash dev/audit/harnesses/r10_tick_selftest_checkout.sh HEAD channels
             `dev/audit/harnesses/r10_tick_selftest_checkout.sh` is in the tree at this head
  unverified bash sources it, 1. -
             `sources` does not look like a path in this tree
  unverified is a special builtin there; bash refuses to import the function (rc 2) or never reads
             `refuses` does not look like a path in this tree

FIGURES: 1 resolved, 17 not verified, 0 refused

## Finder's harness: none named
### at the base
not run
### at the head
not run

## Mutation-ledger diff
none

## Review scope: full (no verdict on verdict/<pr> names the reviewed head 510c46643055f5f2f9f61b815258a960518eabe0, so there is no finding to confirm resolved)

## Three-dot diff
diff --git a/dev/audit/harnesses/r10_tick_selftest_checkout.sh b/dev/audit/harnesses/r10_tick_selftest_checkout.sh
new file mode 100644
index 0000000000..8028b86031
--- /dev/null
+++ b/dev/audit/harnesses/r10_tick_selftest_checkout.sh
@@ -0,0 +1,217 @@
+#!/usr/bin/env bash
+# R10-HOTFIX-TICK-SELFTEST-CHECKOUT: tick_loop.sh's self-test must read and move
+# no checkout but scratch clones of its own, whatever its caller's checkout,
+# GIT_DIR or PATH. The finder's control (the self-test run from a checkout
+# behind origin/main: a branch fails a row, a detached head is moved) and the
+# mutants that take each guard back out, on <rev>'s copy of the script.
+#
+#   bash dev/audit/harnesses/r10_tick_selftest_checkout.sh <rev> [arm...]
+#
+# Nothing runs in the caller's checkout: <rev>'s tick_loop.sh, heartbeat.sh,
+# ref_privacy.py and tests/throwaway_git.sh are written to a scratch directory
+# and every self-test runs from there or from a throwaway clone of it.
+#
+# Shape arms -- <rev>'s self-test run from a throwaway clone, its nested rows
+# skipped (the clone is the nesting); each prints
+#   <arm> behind=<n>: <the self-test's tally line> HEAD-MOVED|HEAD-UNMOVED
+# and the failing rows:
+#   branch    a branch clone one commit behind origin/main on tick_loop.sh
+#   detached  the same clone, detached
+#   gitdir    a detached clone behind, named by GIT_DIR and GIT_WORK_TREE (a git hook's environment)
+#   shim      a branch clone at origin/main, the state dir's bin holding a gh with the seat shim's marker (a live seat's)
+#   level     a branch clone at origin/main: the null control
+# Every arm but shim runs under a scratch HPO_STATE_DIR whose bin holds a plain gh, so the
+# caller's own gh, shim or not, decides nothing.
+# Mutant arms -- <rev>'s whole self-test from a scratch copy that is no checkout,
+# one guard taken back out; each prints `<arm>: <tally line> rc=<n>` and the failing rows:
+#   whole       no mutation: the control every mutant is read against
+#   nocheckout  the HPO_TICK_CODE_DIR export back below the TICK-GH rows
+#   gitenv      throwaway_git_env back below the heartbeat rows
+#   plaingh     the no-shim row's own plain gh taken off its PATH
+#   envscrub    the line dropping the caller's HPO_TICK_* and HPO_SWEEP_MANDATE deleted (a rev before envi)
+#   envi        the re-exec under env -i dropped: --self-test runs the rows in the caller's environment
+#   carry       the re-exec copies one caller variable through (SPY_REAL_GIT, round 3's first channel)
+#   pathfirst   the seat-bin PATH computed above the re-exec and carried by it (round 3's second channel)
+#   allowlist   the rows' entry point lets a name off the allowlist through (a rev before the re-cut)
+#   pipefail    the self-test's `set +o pipefail` deleted
+#   failopen    the refusal after the re-exec replaced by a run of the rows: a --self-test whose re-exec a
+#               caller's function named exec skipped runs every row in the caller's environment (round 4)
+# Channel arm -- <rev>'s whole self-test from a scratch copy, once per channel a caller has into the
+# process before line 1 and at the re-exec, every run beside a scratch bare repository named as
+# HPO_HEARTBEAT_REMOTE and TICK_RC=1 (either acts if a row runs in the caller's environment); each prints
+#   channels <channel>: <the run's last line> rc=<n> fn-calls=<n> victim-refs=<n>
+#   fn-all      an exported function for every bash builtin but exec and every command the script runs,
+#               each touching a file when called (a bare redirection, so it looks up no command itself)
+#   bashenv-all the same functions defined by a BASH_ENV file
+#   fn-exec     an exported exec that skips the /usr/bin/env call (the round-4 attack)
+#   posix       fn-exec under POSIXLY_CORRECT, and under SHELLOPTS=posix: exec is a special builtin there
+#   noexec      SHELLOPTS=noexec: bash runs no line of any script
+#   opts        SHELLOPTS=errexit:nounset:xtrace and BASHOPTS=execfail:extglob
+#   env         ENV naming a file that touches one when sourced
+#   path        PATH led by a directory whose bash, env, git and python3 touch a file
+#   ifs         IFS=/ in the caller
+# A mutant arm needs the `# mut:selftest-*` markers and says so on a <rev> without them.
+# No arm named runs the five shapes.
+set -uo pipefail
+rev=${1:?usage: r10_tick_selftest_checkout.sh <rev> [branch|detached|gitdir|shim|level|whole|nocheckout|gitenv|plaingh|envscrub|envi|carry|pathfirst|allowlist|pipefail|failopen|channels]...}; shift
+[ $# -gt 0 ] || set -- branch detached gitdir shim level
+top=$(git rev-parse --show-toplevel) || exit 2
+sha=$(git -C "$top" rev-parse --verify -q "$rev^{commit}") || { echo "no commit $rev"; exit 2; }
+d=$(mktemp -d) || exit 2
+trap 'rm -rf "$d"' EXIT
+L=tools/audit/seat/tick_loop.sh
+extract() { # <dir>: <rev>'s five files, in a directory that is no checkout
+  local f; mkdir -p "$1/tools/audit/seat" "$1/tests"
+  for f in "$L" tools/audit/seat/heartbeat.sh tools/audit/seat/ref_privacy.py tools/audit/seat/offline_spy.py tests/throwaway_git.sh; do
+    git -C "$top" show "$sha:$f" > "$1/$f" || exit 2
+  done
+}
+extract "$d/src"
+# shellcheck source=/dev/null
+. "$d/src/tests/throwaway_git.sh"
+mkdir -p "$d/plain/bin" "$d/shim/bin"
+printf '#!/bin/sh\nexit 0\n' > "$d/plain/bin/gh"; printf '#!/bin/sh\n# hpo-gh-shim\nexit 0\n' > "$d/shim/bin/gh"
+chmod +x "$d/plain/bin/gh" "$d/shim/bin/gh"
+bare() { env -u HPO_TICK_CODE_DIR -u HPO_TICK_HEARTBEAT -u GIT_CEILING_DIRECTORIES HPO_STATE_DIR="$d/plain" "$@"; }
+rows() { sed -n 's/^  FAIL /    FAIL /p; s/^    nested FAIL: /      nested FAIL: /p' "$1"; }
+
+clones() { # the scratch origin, one commit ahead of the `old` clone on tick_loop.sh
+  [ -d "$d/o.git" ] && return 0
+  (
+    throwaway_git_env
+    cp -R "$d/src" "$d/n"
+    throwaway_git_init "$d/o.git" -q --bare -b main && throwaway_git_init "$d/n" -q -b main || exit 2
+    git -C "$d/n" add -A && git -C "$d/n" commit -qm base && git -C "$d/o.git" fetch -q "$d/n" main:main || exit 2
+    throwaway_git_clone -q "$d/o.git" "$d/old" || exit 2
+    printf '# ahead\n' >> "$d/n/$L"
+    git -C "$d/n" commit -qam ahead && git -C "$d/o.git" fetch -q "$d/n" main:main || exit 2
+    throwaway_git_clone -q "$d/o.git" "$d/new" || exit 2
+  ) || { echo "the scratch clones could not be built"; exit 2; }
+}
+
+shape() { # <arm>
+  local arm=$1 c=$d/c-$1 h0 h1 n m
+  local -a pre=()
+  clones; rm -rf "$c"
+  case $arm in
+    branch) cp -R "$d/old" "$c" ;;
+    detached) cp -R "$d/old" "$c"; (throwaway_git_env; git -C "$c" checkout -q --detach) ;;
+    gitdir) cp -R "$d/old" "$c"; (throwaway_git_env; git -C "$c" checkout -q --detach); pre=(GIT_DIR="$c/.git" GIT_WORK_TREE="$c") ;;
+    shim) cp -R "$d/new" "$c"; pre=(HPO_STATE_DIR="$d/shim") ;;
+    level) cp -R "$d/new" "$c" ;;
+  esac
+  h0=$(throwaway_git_env; git -C "$c" rev-parse HEAD)
+  HPO_TICK_SELFTEST_NESTED=1 bare ${pre[@]+"${pre[@]}"} bash "$c/$L" --self-test --nested > "$d/$arm.log" 2>&1
+  h1=$(throwaway_git_env; git -C "$c" rev-parse HEAD)
+  n=$(throwaway_git_env; git -C "$c" fetch -q origin main; git -C "$c" rev-list --count "$h0..origin/main")
+  [ "$h0" = "$h1" ] && m=HEAD-UNMOVED || m=HEAD-MOVED
+  echo "$arm behind=$n: $(tail -n 1 "$d/$arm.log") $m"; rows "$d/$arm.log"
+}
+
+mutant() { # <arm>
+  local arm=$1 m=$d/m-$1 rc
+  rm -rf "$m"; extract "$m"
+  python3 - "$m/$L" "$arm" 2>/dev/null <<'PY' || { echo "$arm: NOT RUN, the mutation did not apply (no '# mut:selftest-*' marker at this rev?)"; return; }
+import sys
+p, arm = sys.argv[1:]
+s = open(p).read().split("\n")
+def marked(marker):
+    g = [i for i, l in enumerate(s) if l.rstrip().endswith("# mut:" + marker)]
+    assert len(g) == 1, (marker, g)
+    return g[0]
+def move(marker, after):  # the marked line, back to where the merge base ran it
+    line = s.pop(marked(marker))
+    a = [i for i, l in enumerate(s) if after in l]
+    assert len(a) == 1, (after, a)
+    s.insert(a[0] + 1, line)
+if arm == "nocheckout":
+    move("selftest-nocheckout", 'ck "a seat bin dir with no gh shim')
+elif arm == "gitenv":
+    move("selftest-gitenv", "# The real script against a bare remote")
+elif arm == "plaingh":
+    i = marked("selftest-plaingh")
+    assert 'PATH="$t/bare:$PATH" ' in s[i]
+    s[i] = s[i].replace('PATH="$t/bare:$PATH" ', "")
+elif arm == "envscrub":
+    s.pop(marked("selftest-envscrub"))
+elif arm == "envi":
+    i = marked("selftest-envi")
+    s[i] = '  tick_loop_self_test  # mut:selftest-envi' if "selftest_allowlisted" in "\n".join(s) else ""
+elif arm == "carry":
+    i = marked("selftest-envi")
+    assert "env -i PATH=" in s[i]
+    s[i] = s[i].replace("env -i PATH=", 'env -i SPY_REAL_GIT="${SPY_REAL_GIT-}" PATH=')
+elif arm == "pathfirst":
+    i = marked("selftest-envi")
+    lit = 'PATH="/usr/local/bin:/usr/bin:/bin:/usr/sbin:/sbin:${BASH%/*}"'
+    assert lit in s[i]
+    s[i] = s[i].replace(lit, 'PATH="$PATH"')
+    k = marked("seatbin")
+    assert s[k - 1].startswith("SEAT_BIN=") and s[k + 1] == "export PATH"
+    block = s[k - 1:k + 2]
+    del s[k - 1:k + 2]
+    i = marked("selftest-envi")
+    s[i:i] = block
+elif arm == "allowlist":
+    i = marked("selftest-allowlist")
+    assert '*" $v "*) ;; *)' in s[i]
+    s[i] = s[i].replace('*" $v "*) ;; *)', '*) ;; *" $v "*)')
+elif arm == "pipefail":
+    s.pop(marked("selftest-pipefail"))
+elif arm == "failopen":
+    i = marked("selftest-failclosed")
+    assert s[i].startswith("case ${1:-} in --self-test) refused=")
+    s[i] = 'case ${1:-} in --self-test) set -- --self-test-rows "${@:2}" ;; esac  # mut:selftest-failclosed'
+else:
+    assert arm == "whole"
+open(p, "w").write("\n".join(s))
+PY
+  bash -n "$m/$L" || { echo "$arm: NOT RUN, the mutant does not parse"; return; }
+  bare bash "$m/$L" --self-test > "$d/$arm.log" 2>&1; rc=$?
+  echo "$arm: $(tail -n 1 "$d/$arm.log") rc=$rc"; rows "$d/$arm.log"
+}
+
+channels() { # every channel in parallel, one line each
+  local c b=$BASH x=$d/ch o
+  mkdir -p "$x"
+  local -a names=() fenv=()
+  while read -r o; do [ "$o" = exec ] || names+=("$o"); done < <(compgen -b)
+  names+=(git mktemp python3 sed grep env bash head tr cat chmod mkdir cp rm mv date sleep timeout kill tail wc cut sort dirname pwd)
+  run1() { # <channel> [env args...]: one whole self-test under that caller
+    local c=$1 v=$x/victim-$1.git rc; shift
+    mkdir -p "$x/calls-$c"; (throwaway_git_env; throwaway_git_init "$v" -q --bare) || return
+    (cd "$x" && env HPO_HEARTBEAT_REMOTE="$v" TICK_RC=1 "$@" "$d/src/$L" --self-test) > "$x/$c.log" 2>&1; rc=$?
+    echo "channels $c: $(tail -n 1 "$x/$c.log") rc=$rc fn-calls=$(ls "$x/calls-$c" | grep -c .) victim-refs=$(git -C "$v" for-each-ref | grep -c .)" > "$x/$c.line"; }
+  fdefs() { # <channel>: the function corpus, as a BASH_ENV file's text
+    local i=0 n; for n in "${names[@]}"; do i=$((i + 1)); printf '%s() { >> %q; }\n' "$n" "$x/calls-$1/fn-$i-${n//[^a-z0-9]/_}"; done; }
+  while IFS= read -r c; do fenv+=("BASH_FUNC_${c%%()*}%%=()${c#*()}"); done < <(fdefs fn-all)
+  printf 'exec() { if [ "${1:-}" = /usr/bin/env ]; then >> %q; return 0; fi; builtin exec "$@"; }\n' "$x/calls-shellopts-posix/exec" > "$x/execfn-posix"
+  fdefs bashenv-all > "$x/bashenv-all"; echo ">> $x/calls-env/sourced" > "$x/envfile"
+  mkdir -p "$x/pbin"; for o in bash env git python3; do printf '#!/bin/sh\n>> %q\nexit 1\n' "$x/calls-path/$o" > "$x/pbin/$o"; chmod +x "$x/pbin/$o"; done
+  run1 fn-all "${fenv[@]}" "$b" & run1 bashenv-all BASH_ENV="$x/bashenv-all" "$b" &
+  run1 fn-exec "BASH_FUNC_exec%%=() { if [ \"\${1:-}\" = /usr/bin/env ]; then >> $x/calls-fn-exec/exec; return 0; fi; builtin exec \"\$@\"; }" "$b" &
+  run1 posix POSIXLY_CORRECT=1 "BASH_FUNC_exec%%=() { if [ \"\${1:-}\" = /usr/bin/env ]; then >> $x/calls-posix/exec; return 0; fi; builtin exec \"\$@\"; }" "$b" &
+  run1 shellopts-posix SHELLOPTS=posix BASH_ENV="$x/execfn-posix" "$b" &
+  run1 noexec SHELLOPTS=noexec "$b" & run1 opts SHELLOPTS=errexit:nounset:xtrace BASHOPTS=execfail:extglob "$b" &
+  run1 env ENV="$x/envfile" "$b" & run1 path PATH="$x/pbin:$PATH" "$b" & run1 ifs IFS=/ "$b" &
+  wait; cat "$x"/*.line
+  # The null controls: each channel's instrument records a call when one is made.
+  local -a fctl=(); mkdir -p "$x/calls-fn-ctl" "$x/calls-bashenv-ctl" "$x/calls-env-ctl" "$x/calls-path-ctl" "$x/qbin"
+  while IFS= read -r c; do fctl+=("BASH_FUNC_${c%%()*}%%=()${c#*()}"); done < <(fdefs fn-ctl)
+  env "${fctl[@]}" "$b" -c 'cd /; git status; mktemp; exit 0'
+  fdefs bashenv-ctl > "$x/bashenv-ctl"; env BASH_ENV="$x/bashenv-ctl" "$b" -c 'cd /; git status; mktemp; exit 0'
+  echo ">> $x/calls-env-ctl/sourced" > "$x/envfile-ctl"; env ENV="$x/envfile-ctl" "$b" --posix -i -c : 2>/dev/null
+  printf '#!/bin/sh\n>> %q\n' "$x/calls-path-ctl/git" > "$x/qbin/git"; chmod +x "$x/qbin/git"; env PATH="$x/qbin:$PATH" "$b" -c 'git status'
+  for c in fn bashenv env path; do echo "channels null control $c: fn-calls=$(ls "$x/calls-$c-ctl" | grep -c .)"; done
+  echo "channels corpus: ${#names[@]} function names"
+}
+
+echo "rev $sha"
+for arm in "$@"; do
+  case $arm in
+    branch|detached|gitdir|shim|level) shape "$arm" ;;
+    whole|nocheckout|gitenv|plaingh|envscrub|envi|carry|pathfirst|allowlist|pipefail|failopen) mutant "$arm" ;;
+    channels) channels ;;
+    *) echo "unknown arm '$arm'"; exit 2 ;;
+  esac
+done
diff --git a/dev/programme/delivery/3520.md b/dev/programme/delivery/3520.md
new file mode 100644
index 0000000000..99ff6e09e8
--- /dev/null
+++ b/dev/programme/delivery/3520.md
@@ -0,0 +1 @@
+- [#3520](https://github.com/tvofi/heatpump_optimizer/pull/3520) — **open**, R10-HOTFIX-TICK-SELFTEST-CHECKOUT: r10 hotfix tick selftest checkout (R10-HOTFIX-TICK-SELFTEST-CHECKOUT)
diff --git a/tests/closures.json b/tests/closures.json
index b4bd2b1e26..6d61ec126b 100644
--- a/tests/closures.json
+++ b/tests/closures.json
@@ -4316,6 +4316,7 @@
    "dev/audit/harnesses/r10_thermal_power_option.py",
    "dev/audit/harnesses/r10_tick_drivers.py",
    "dev/audit/harnesses/r10_tick_owed_level.py",
+   "dev/audit/harnesses/r10_tick_selftest_checkout.sh",
    "dev/audit/harnesses/r10_tick_train_mutants.sh",
    "dev/audit/harnesses/r10_tick_which_roster.py",
    "dev/audit/harnesses/r10_title_seam.sh",
diff --git a/tools/audit/seat/instruments/tick_loop.sh.md b/tools/audit/seat/instruments/tick_loop.sh.md
index c020eb9a54..3a449c5398 100644
--- a/tools/audit/seat/instruments/tick_loop.sh.md
+++ b/tools/audit/seat/instruments/tick_loop.sh.md
@@ -19,6 +19,24 @@
   `--once` makes one pass, `--interval` defaults to 300 s. Refusal: a
   non-numeric `--interval` or an unknown option; a failing relay pass or tick
   is reported and the loop goes on. `--self-test` drives it over stubs.
+  The self-test reads and moves no checkout but scratch clones of its own:
+  `--self-test`'s first statement re-runs it under `env -i` carrying no
+  caller variable (`PATH` a literal of system directories and the running
+  bash's, `HOME` and `TMPDIR` fresh), and the rows run only from the
+  `--self-test-rows` entry that re-exec names. The barrier fails closed: a
+  `--self-test` the re-exec did not replace (a caller's function named
+  `exec`, exported or defined by a `BASH_ENV` file, shadows the builtin)
+  refuses with rc 1 and runs no row, by an expansion error that looks up no
+  command a function could shadow; rows pin both shadows and the null
+  control. So no caller variable, nor a value computed from one, reaches a
+  row, unless a caller's own code runs the rows entry itself (a
+  `BASH_ENV` file is code run inside this process, out of any script
+  line's reach); its poison row exports every name the
+  script and its helpers read (derived by grep, never listed) to a sentinel
+  and finds none in a nested run's environment, arguments or output. It
+  points `HPO_TICK_CODE_DIR` at scratch, and it runs itself whole from a
+  branch and a detached clone behind origin/main to pin that, so it is safe
+  from any checkout, whatever origin/main does.
   Each pass then calls `heartbeat.sh --once` (the andon, below), bounded at
   60 s; `HPO_TICK_HEARTBEAT` replaces it.
   Before the relay, the freshness check (P14): `git fetch -q origin main`
diff --git a/tools/audit/seat/tick_loop.sh b/tools/audit/seat/tick_loop.sh
index f3ce6b003e..ffdc23d451 100644
--- a/tools/audit/seat/tick_loop.sh
+++ b/tools/audit/seat/tick_loop.sh
@@ -54,7 +54,21 @@
 # --interval defaults to 300 (the five-minute GitHub poll). Run it detached
 # (daemonize.py): a background task dies at two hours. HPO_TICK_RELAY and
 # HPO_TICK_CMD replace the relay script and the tick command (the self-test's stubs).
+# --self-test re-runs itself before anything else runs, under env -i with no caller variable carried
+# at all: PATH a literal of system directories and this bash's own, HOME and TMPDIR fresh (below).
+# So nothing a caller exports, nor anything computed from it, reaches a row, and no list of names
+# has to keep up with what a row reads. Its rows run from --self-test-rows, the internal entry, and
+# from nowhere else: the barrier fails closed. A --self-test still here was not replaced by the
+# re-exec -- a caller's function named exec (exported, or defined by a BASH_ENV file) shadowed the
+# builtin, or the exec failed -- and it refuses, rc 1, no row run, before any other command name is
+# looked up. The refusal is an expansion error, which runs no command a function could shadow and
+# ends a non-interactive bash.
+case ${1:-} in --self-test) exec /usr/bin/env -i PATH="/usr/local/bin:/usr/bin:/bin:/usr/sbin:/sbin:${BASH%/*}" "$BASH" "$0" --self-test-rows "${@:2}" ;; esac  # mut:selftest-envi
+case ${1:-} in --self-test) refused=; refused=${refused:?--self-test refused: the env -i re-exec did not replace this process (a caller function named exec?); no row ran} ;; esac  # mut:selftest-failclosed
 set -uo pipefail
+case ${1:-} in --self-test-rows)  # the rows' HOME and TMPDIR: fresh, the caller's never
+  SELFTEST_TMP=$(mktemp -d) || exit 1; export HOME=$SELFTEST_TMP/home TMPDIR=$SELFTEST_TMP/tmp
+  mkdir "$HOME" "$TMPDIR" || exit 1 ;; esac
 HERE=$(cd "$(dirname -- "$0")" && pwd)
 # The seat bin dir (seat_venv.sh --install-shims; $HPO_STATE_DIR/bin) goes first on the
 # PATH every child inherits -- orchestrator_tick.py, cloud_relay.sh, the sweep's train --
@@ -188,15 +202,33 @@ tick_pass() { # <out> [tick args...]: one pass; prints the banner
   [ $? = 0 ] || echo "HEARTBEAT NOT PUSHED: heartbeat.sh did not finish cleanly"
 }
 
-tick_loop_self_test() (
-  local t f=0 n=0 out
+tick_loop_self_test() ( # [--nested]: the rows; --nested (a row's own run) skips the block that nests
+  local t f=0 n=0 out nested=
+  case ${1:-} in '') ;; --nested) nested=1 ;; *) echo "tick_loop self-test: unknown argument $1"; return 2 ;; esac
+  # A row's verdict is its reader's. Under pipefail a `grep -q` that leaves at its match can kill
+  # the printf feeding it (141), and the row reads a match as none: prepr.sh's PIPE_GREP_Q class,
+  # seen here under load as one stray FAIL in a different row each time.
+  set +o pipefail  # mut:selftest-pipefail
   t=$(mktemp -d) || { echo "tick_loop self-test: no temporary directory"; return 1; }
   ck() { n=$((n + 1)); if [ "$2" = 0 ]; then echo "  ok   $1"; else f=$((f + 1)); echo "  FAIL $1"; fi; }
-  printf '#!/bin/bash\necho "relay $*" >> "%s/order"; exit "${RELAY_RC:-0}"\n' "$t" > "$t/relay.sh"
-  printf '#!/bin/bash\necho "tick $*" >> "%s/order"; echo BOARD; exit "${TICK_RC:-0}"\n' "$t" > "$t/tick.sh"
+  # A nested run prints what its rows start from, and at its end what each stub row saw (the poison
+  # row below reads both for a caller's value).
+  [ -z "$nested" ] || { env | sed 's/^/  env: /'; echo "  argv: $0 $*"; }
+  # 2 MB after the match makes the SIGPIPE certain: with pipefail on, this row reads its match as none.
+  out=$(head -c 2097152 /dev/zero | tr '\0' x)
+  printf 'MATCH\n%s\n' "$out" | grep -q '^MATCH$'
+  ck "a row's verdict is its reader's: a grep -q that leaves at its match, its writer killed mid-write, still reads the match" $?
+  printf '#!/bin/bash\n{ env; echo "argv: $0 $*"; } >> "%s/envdump"; echo "relay $*" >> "%s/order"; exit "${RELAY_RC:-0}"\n' "$t" "$t" > "$t/relay.sh"
+  printf '#!/bin/bash\n{ env; echo "argv: $0 $*"; } >> "%s/envdump"; echo "tick $*" >> "%s/order"; echo BOARD; exit "${TICK_RC:-0}"\n' "$t" "$t" > "$t/tick.sh"
   chmod +x "$t/tick.sh"
-  printf '#!/bin/bash\necho "hb $*" >> "%s/hb"; exit "${HB_RC:-0}"\n' "$t" > "$t/hb.sh"
+  printf '#!/bin/bash\n{ env; echo "argv: $0 $*"; } >> "%s/envdump"; echo "hb $*" >> "%s/hb"; exit "${HB_RC:-0}"\n' "$t" "$t" > "$t/hb.sh"
   export HPO_TICK_HEARTBEAT=$t/hb.sh
+  # No row reads or moves the caller's checkout: an extra TICK-STALE from a branch behind
+  # origin/main, a restart's checkout of a detached one. Before the first row, the repository a
+  # caller's environment names is dropped (a git hook exports GIT_DIR, which outranks -C) and
+  # every row but the freshness rows, which name their own clone, runs from no checkout.
+  . "$HERE/../../../tests/throwaway_git.sh" && throwaway_git_env || return 1  # mut:selftest-gitenv
+  mkdir "$t/nogit"; export HPO_TICK_CODE_DIR=$t/nogit GIT_CEILING_DIRECTORIES=$t  # mut:selftest-nocheckout
   # The seat bin dir under a scratch state dir, holding a gh that carries the shim marker,
   # so a host whose gh is not the shim (CI's) prints no TICK-GH line in the rows below.
   mkdir -p "$t/state/bin" "$t/bare/bin"; export HPO_STATE_DIR=$t/state
@@ -209,13 +241,13 @@ tick_loop_self_test() (
   out=$(PATH="$t/state/bin:$PATH" HPO_TICK_RELAY=$t/absent.sh HPO_TICK_CMD="bash $t/pathtick.sh" bash "$0" --once --out "$t/b.txt")
   [ "$(tr ':' '\n' < "$t/path" | grep -cx "$t/state/bin")" = 1 ]
   ck "a PATH already led by the seat bin dir (a restart's exec) is not prepended twice" $?
-  out=$(HPO_STATE_DIR=$t/bare HPO_TICK_RELAY=$t/absent.sh HPO_TICK_CMD="bash $t/pathtick.sh" bash "$0" --once --out "$t/b.txt")
+  # A plain gh of the row's own leads the PATH: the caller's may be the seat shim (a live seat's
+  # is, and the lines above put its state dir's bin first before this self-test began).
+  printf '#!/bin/sh\nexit 0\n' > "$t/bare/gh"; chmod +x "$t/bare/gh"
+  out=$(PATH="$t/bare:$PATH" HPO_STATE_DIR=$t/bare HPO_TICK_RELAY=$t/absent.sh HPO_TICK_CMD="bash $t/pathtick.sh" bash "$0" --once --out "$t/b.txt")  # mut:selftest-plaingh
   g=$(cat "$t/gh"); printf '%s\n' "$out" | grep -Eq "^TICK-GH [0-9T:-]+Z gh=${g:-none}: not the seat gh shim" \
     && [ "$(printf '%s\n' "$out" | grep -c '^TICK-')" = 2 ]
   ck "a seat bin dir with no gh shim: one TICK-GH flag line naming the gh found, beside the banner" $?
-  # The rows before the freshness rows run from no checkout: never the real one, whose
-  # fetch and checkout a restart would move.
-  mkdir "$t/nogit"; export HPO_TICK_CODE_DIR=$t/nogit GIT_CEILING_DIRECTORIES=$t
   out=$(HPO_TICK_RELAY=$t/relay.sh HPO_TICK_CMD="bash $t/tick.sh" bash "$0" --once --out "$t/b.txt" -- --only PRS)
   [ "$(cat "$t/order")" = "relay pass --confirm
 tick --only PRS" ] && [ "$(cat "$t/b.txt")" = BOARD ] \
@@ -231,9 +263,11 @@ tick --only PRS" ] && [ "$(cat "$t/b.txt")" = BOARD ] \
   ck "a failing relay pass is reported and the tick still runs; the tick's status is reported" $?
   # A relay slower than the interval (update_pr.sh's prepr, #2525) must not hold the board.
   printf '#!/bin/bash\necho start >> "%s/slow"; sleep "${RELAY_SLEEP:-0}"; echo done >> "%s/slow"; echo SLOW-LOG\n' "$t" "$t" > "$t/slow.sh"
-  rm -f "$t/order" "$t/b.txt"; s0=$SECONDS
+  # No wall-clock bound: the pass is back, its board written, while the 6 s relay has not finished
+  # (a bound in whole seconds over a pass that already waits one failed on a loaded host).
+  rm -f "$t/order" "$t/b.txt" "$t/slow"
   out=$(RELAY_SLEEP=6 HPO_TICK_RELAY_WAIT=1 HPO_TICK_RELAY=$t/slow.sh HPO_TICK_CMD="bash $t/tick.sh" bash "$0" --once --interval 3 --out "$t/b.txt")
-  [ $((SECONDS - s0)) -lt 3 ] && [ "$(cat "$t/b.txt" 2>/dev/null)" = BOARD ] && printf '%s\n' "$out" | grep -q 'relay=running tick=0'
+  ! grep -qx done "$t/slow" 2>/dev/null && [ "$(cat "$t/b.txt" 2>/dev/null)" = BOARD ] && printf '%s\n' "$out" | grep -q 'relay=running tick=0'
   ck "a relay slower than the interval does not delay the board; the banner says relay=running" $?
   out=$(RELAY_SLEEP=6 HPO_TICK_RELAY_WAIT=1 HPO_TICK_RELAY=$t/slow.sh HPO_TICK_CMD="bash $t/tick.sh" bash "$0" --once --out "$t/b.txt")
   [ "$(cat "$t/slow")" = start ] && printf '%s\n' "$out" | grep -q 'relay=running tick=0' && [ "$(grep -c '^tick' "$t/order")" = 2 ]
@@ -293,7 +327,6 @@ sweep" ] && printf '%s\n' "$out" | grep -q '^TICK-SWEEP '
   [ $rc = 0 ] && printf '%s\n' "$out" | grep -q '^TICK-SWEEP .* rc=2 SWEEP REFUSED queue: x$' && printf '%s\n' "$out" | grep -q 'tick=0'
   ck "a refused sweep is reported with its rc and the pass still completes" $?
   # The real script against a bare remote: a pass moves the ref.
-  . "$HERE/../../../tests/throwaway_git.sh" && throwaway_git_env || return 1
   throwaway_git_init "$t/remote.git" -q --bare && throwaway_git_init "$t/w" -q -b main
   git -C "$t/w" remote add origin "$t/remote.git"; mkdir -p "$t/w/seat"
   cp "$HERE/heartbeat.sh" "$HERE/ref_privacy.py" "$t/w/seat/"
@@ -360,6 +393,93 @@ f = open(sys.argv[1], "a"); fcntl.flock(f, fcntl.LOCK_EX); open(sys.argv[1] + ".
     && printf '%s\n' "$out" | grep -qx "NEW-LOOP --once --out $t/f.txt --sweep" \
     && [ "$(git -C "$t/c" rev-parse HEAD)" = "$(git -C "$t/c" rev-parse origin/main)" ] && [ ! -f "$t/order" ]
   ck "freshness: a loop-file change with a free lock and a clean detached tree checks out origin/main and execs it with the same args" $?
+  # The self-test run as a live seat runs it -- from a checkout behind origin/main on the watched
+  # paths, a branch and then a detached head, its state dir's bin holding the gh shim -- reads nothing of
+  # that checkout and leaves its HEAD where it was; so does one a git hook's GIT_DIR names. (The
+  # TICK-GH rows once ran against the real checkout: a branch printed an extra TICK-STALE, a
+  # detached head was moved by the restart arm.) The nested run is the whole self-test, so it
+  # skips this block.
+  if [ -z "$nested" ]; then
+    mkdir -p "$t/n/tools/audit/seat" "$t/n/tests"
+    cp "$HERE/tick_loop.sh" "$HERE/heartbeat.sh" "$HERE/ref_privacy.py" "$t/n/tools/audit/seat/"
+    cp "$HERE/../../../tests/throwaway_git.sh" "$t/n/tests/"
+    throwaway_git_init "$t/n.git" -q --bare -b main && throwaway_git_init "$t/n" -q -b main
+    git -C "$t/n" add -A && git -C "$t/n" commit -qm base && git -C "$t/n.git" fetch -q "$t/n" main:main
+    throwaway_git_clone -q "$t/n.git" "$t/nb"
+    printf '# ahead\n' >> "$t/n/tools/audit/seat/tick_loop.sh"
+    git -C "$t/n" commit -qam ahead && git -C "$t/n.git" fetch -q "$t/n" main:main
+    for c in nd nh; do cp -R "$t/nb" "$t/$c"; git -C "$t/$c" checkout -q --detach; done
+    throwaway_git_clone -q "$t/n.git" "$t/n0"
+    nest() { # <checkout> [VAR=value...]: the clone's own self-test, those set in its caller's environment
+      local c=$1 h; shift; h=$(git -C "$c" rev-parse HEAD)
+      out=$(/usr/bin/env "$@" "$BASH" "$c/tools/audit/seat/tick_loop.sh" --self-test --nested 2>&1)
+      printf '%s\n' "$out" | sed -n 's/^  FAIL /    nested FAIL: /p'  # which nested row, when one fails
+      printf '%s\n' "$out" | grep -Eq '^tick_loop self-test: [1-9][0-9]* checks, 0 failed$' && [ "$(git -C "$c" rev-parse HEAD)" = "$h" ]; }
+    nest "$t/nb"
+    ck "the self-test run from a branch checkout behind origin/main passes and does not move its HEAD" $?
+    nest "$t/nd"
+    ck "the self-test run from a detached checkout behind origin/main passes and does not move its HEAD" $?
+    nest "$t/nh" GIT_DIR="$t/nh/.git" GIT_WORK_TREE="$t/nh"
+    ck "the self-test run with GIT_DIR naming a detached checkout behind origin/main passes and does not move its HEAD" $?
+    # The poison row. Every name this script and the helpers its rows source or run read is derived,
+    # never listed: a $-reference in a shell file, an environ/getenv key in a Python one. Each is
+    # exported in the caller to a URL-shaped sentinel carrying this run's nonce (PATH's keeps two
+    # system directories behind it, so a leaked PATH still runs), and the self-test runs nested under
+    # offline_spy.py. No sentinel may reach its rows' environment, arguments or output.
+    names=$({ grep -ohE '\$\{?[A-Za-z_][A-Za-z0-9_]*' "$HERE/tick_loop.sh" "$HERE/heartbeat.sh" "$HERE/../../../tests/throwaway_git.sh" | sed 's/^\$[{]*//'
+      grep -ohE "(environ(\.get)?[[(]|getenv\()[\"'][A-Za-z_][A-Za-z0-9_]*" "$HERE/ref_privacy.py" "$HERE/offline_spy.py" | sed -E "s/.*[\"']//"; } | sort -u)
+    nonce=hpo-poison-$$-$RANDOM$RANDOM k=$(printf '%s\n' $names | grep -c .)
+    { echo '#!/bin/bash'; printf /usr/bin/env
+      for v in $names; do
+        if [ "$v" = PATH ]; then printf ' %q' "PATH=https://127.0.0.1:9/$nonce-PATH.git:/usr/bin:/bin"
+        else printf ' %q' "$v=https://127.0.0.1:9/$nonce-$v.git"; fi
+      done
+      printf ' %q' "$BASH" "$HERE/tick_loop.sh"; printf ' --self-test --nested > %q 2>&1; rc=$?\n' "$t/poison.out"
+      printf 'tail -n 1 %q; exit $rc\n' "$t/poison.out"; } > "$t/poisoned.sh"
+    out=$(python3 -I "$HERE/offline_spy.py" "$t/poisoned.sh" 2>/dev/null)
+    grep -m 3 -- "$nonce" "$t/poison.out" 2>/dev/null | cut -c 1-200 | sed 's/^/    leaked: /'
+    [ -n "$names" ] && printf '%s\n' "$out" | grep -Eq "^offline_spy: $t/poisoned.sh rc=0 network=0 remote_git=0 .* [|] tick_loop self-test: [1-9][0-9]* checks, 0 failed$" \
+      && grep -q '^  env: PATH=' "$t/poison.out" && grep -q '^  row env: PATH=' "$t/poison.out" && ! grep -q -- "$nonce" "$t/poison.out"
+    ck "the poison row: the $k names the script and its helpers read, each a sentinel in the caller's environment, reach no row's environment, arguments or output, and the run passes under offline_spy.py with no network or remote git call" $?
+    # The barrier fails closed. A caller's function named exec, exported or defined by a BASH_ENV file,
+    # skips the env -i re-exec (it logs the skipped call to $t/shadow, so the row sees the shadow taken);
+    # the caller also names a scratch bare repository as HPO_HEARTBEAT_REMOTE and sets TICK_RC=1, either
+    # of which a row run in the caller's environment would act on (round 4: 18 rows failed, the
+    # repository took a forced heartbeat/orchestrator). The run must refuse, run no row, and leave the
+    # repository holding no ref; the null control, the same caller without the function, passes.
+    printf 'exec() { if [ "${1:-}" = /usr/bin/env ]; then echo "shadowed: $*" >> %q; return 0; fi; builtin exec "$@"; }\n' "$t/shadow" > "$t/execfn"
+    shadowed() { # <func|bashenv|none>: the nested self-test under that caller; sets out, src, refs
+      local v=$t/victim-$1.git; rm -f "$t/shadow"; throwaway_git_init "$v" -q --bare || return 1
+      out=$(export HPO_HEARTBEAT_REMOTE=$v TICK_RC=1
+        case $1 in
+          func) . "$t/execfn"; export -f exec; "$BASH" "$HERE/tick_loop.sh" --self-test --nested ;;
+          bashenv) BASH_ENV=$t/execfn "$BASH" "$HERE/tick_loop.sh" --self-test --nested ;;
+          none) "$BASH" "$HERE/tick_loop.sh" --self-test --nested ;;
+        esac 2>&1); src=$?
+      refs=$(git -C "$v" for-each-ref | grep -c .); }
+    for c in func bashenv; do
+      shadowed $c
+      [ "$src" != 0 ] && [ -s "$t/shadow" ] && [ "$refs" = 0 ] && printf '%s\n' "$out" | grep -q -- '--self-test refused: the env -i re-exec' \
+        && ! printf '%s\n' "$out" | grep -q '^tick_loop self-test:'
+      ck "fail closed ($c): a caller function named exec that skips the env -i re-exec ends in a refusal, no row run, the HPO_HEARTBEAT_REMOTE repository holding no ref" $?
+    done
+    shadowed none
+    [ "$src" = 0 ] && [ ! -e "$t/shadow" ] && [ "$refs" = 0 ] && printf '%s\n' "$out" | grep -Eq '^tick_loop self-test: [1-9][0-9]* checks, 0 failed$'
+    ck "null control: the same caller with no function named exec runs every row under env -i, passes, and touches no repository it names" $?
+    # The rows themselves under offline_spy.py, which counts every git call that can reach a remote
+    # by its target URL; its SPY_REAL_GIT is the one it finds on this run's own PATH.
+    printf '#!/bin/bash\nexec "%s" "%s/tick_loop.sh" --self-test-rows --nested\n' "$BASH" "$HERE" > "$t/spied.sh"
+    printf '#!/bin/bash\ngit ls-remote https://127.0.0.1:9/hb.git >/dev/null 2>&1; exit 0\n' > "$t/spyctl.sh"
+    out=$(python3 -I "$HERE/offline_spy.py" "$t/spied.sh" 2>/dev/null)
+    printf '%s\n' "$out" | grep -Eq "^offline_spy: $t/spied.sh rc=0 network=0 remote_git=0 git=[1-9][0-9]* .* offline [|] tick_loop self-test: [1-9][0-9]* checks, 0 failed$"
+    ck "the self-test's rows pass under offline_spy.py: no network call, no remote git call, their git calls seen" $?
+    out=$(python3 -I "$HERE/offline_spy.py" "$t/spyctl.sh" 2>/dev/null)
+    printf '%s\n' "$out" | grep -Eq "^offline_spy: $t/spyctl.sh rc=0 network=0 remote_git=1 git=1 .* REFUSED"
+    ck "null control: offline_spy.py counts one git call at that URL as a remote git call" $?
+    [ "$(git -C "$t/n0" rev-list --count HEAD..origin/main)" = 0 ] && nest "$t/n0"
+    ck "null control: a branch checkout at origin/main (behind 0) passes and stays put" $?
+  fi
+  [ -z "$nested" ] || sed 's/^/  row env: /' "$t/envdump" 2>/dev/null
   rm -rf "$t"
   echo "tick_loop self-test: $n checks, $f failed"
   [ "$f" = 0 ]
@@ -369,7 +489,7 @@ ARGV=("$@")  # a restart execs the new loop with these
 once=; sweep=; every=300; out=${HPO_STATE_DIR:-$HOME/.local/state/hpo}/tick.txt
 while [ $# -gt 0 ]; do
   case $1 in
-    --self-test) tick_loop_self_test; exit ;;
+    --self-test-rows) shift; tick_loop_self_test "$@"; rc=$?; rm -rf "$SELFTEST_TMP"; exit $rc ;;
     --once) once=1; shift ;;
     --sweep) sweep=1; shift ;;
     --interval) every=${2:-}; shift 2 || shift ;;

## Before you return the verdict (P275)
Run `python3 -I tools/audit/carry_audit.py check --body <PR body file> --comments <file holding [{"id": 0, "body": <verdict.md text>}]>`. Give every reported item its own `Carry: <GROUP> | #<issue> | O<n> | dismissed: <reason>`;
an evidence line flagged by its wording takes `Carry: dismissed: evidence, not a finding`. Return the verdict only at rc 0.
