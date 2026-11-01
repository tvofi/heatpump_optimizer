# Review packet #3086
head: f4f7daf6ce71185391f69f09d4bd26e4932fe233
base: 6421fe135d9f5a9e65433a4433f000d2419486bf

Start here (fix-review.md). Re-read the live check state before a verdict: the digest is as read at render.

## Gate digest: pending
CodeQL id=124832898156 neutral
arch-score / arch-score id=124832739350 success
arm id=124832654384 skipped
budget-raise-gate / budget-raise-gate id=124832739390 success
cancel-superseded id=124832633257 success
codeql / Analyze (actions) id=124832739641 success
codeql / Analyze (javascript-typescript) id=124832739508 success
codeql / Analyze (python) id=124832739551 in_progress
governance / delivery-status id=124832739577 success
governance / delivery-status-publish id=124832740776 skipped
governance / env-matrix id=124832739418 in_progress
governance / instrument-self-tests id=124832739397 in_progress
governance / policy-docs id=124832739513 success
governance / record id=124832740901 skipped
governance / wave-script id=124832739430 success
hassfest / hassfest id=124832739413 success
kernel-points id=124832740384 skipped
prelude id=124832633207 in_progress
refresh id=124832633034 success
tests / arch-instrument id=124832848061 success
tests / briefs id=124832739417 success
tests / browser id=124832847969 success
tests / closure-scope id=124832739503 success
tests / closures id=124832848072 in_progress
tests / coverage id=124832848021 in_progress
tests / fast (3.14) id=124832847994 in_progress
tests / mutation id=124832739455 success
tests / mutation-autofix id=124832925440 skipped
tests / mutation-pins id=124832924542 skipped
tests / nightly-ha id=124832849227 skipped
tests / nightly-status id=124832739491 success
tests / replay id=124832849328 skipped
tests / typing id=124832848213 success
validate / validate-hacs id=124832739362 success

## Refusals
none

## Advisories
hot-file: HPO_BUS_TRAIN_STATE is unset, so every merge verdict reads unboarded

## carry_audit at the head
CARRY-AUDIT: 0 finding item(s): 0 routed, 0 unrouted, 0 bad destination(s)

## figure_lint at the head
ok         bash dev/audit/harnesses/r10_uutils_sleep.sh 6421fe135 emu
             `dev/audit/harnesses/r10_uutils_sleep.sh` is in the tree at this head
  ok         bash dev/audit/harnesses/r10_uutils_sleep.sh 783e189f3 emu
             `dev/audit/harnesses/r10_uutils_sleep.sh` is in the tree at this head
  ok         bash dev/audit/harnesses/r10_uutils_sleep.sh 783e189f3 emu symlink
             `dev/audit/harnesses/r10_uutils_sleep.sh` is in the tree at this head
  ok         bash dev/audit/harnesses/r10_uutils_sleep.sh 783e189f3 gnu
             `dev/audit/harnesses/r10_uutils_sleep.sh` is in the tree at this head
  ok         python3 tests/closure.py select --diff $(git merge-base origin/main HEAD) --workdir "$D"
             `tests/closure.py` is in the tree at this head
  ok         python3 tests/structure.py
             `tests/structure.py` is in the tree at this head
  unverified git grep -nE '\bln +-[a-zA-Z]*s' -- ':!*.md' ':!*.mdc'
             `git grep` resolves; its flags are not checked -- git prints a man page rather than a flag list, and a list carried in this file would rot into false refusals
  unverified git grep -nE 'os\.symlink\(|symlink_to\(|hardlink_to\(|os\.link\(' -- '*.py' '*.mjs' '*.js'
             `git grep` resolves; its flags are not checked -- git prints a man page rather than a flag list, and a list carried in this file would rot into false refusals
  unverified git grep -nE 'exec -a' -- '*.sh' '*.py'
             `git grep` resolves; its flags are not checked -- git prints a man page rather than a flag list, and a list carried in this file would rot into false refusals
  ok         tools/audit/seat/pr_args.sh
             `tools/audit/seat/pr_args.sh` is in the tree at this head
  ok         tools/audit/seat/train.sh
             `tools/audit/seat/train.sh` is in the tree at this head
  ok         dev/audit/harnesses/r10_seat_selftests_mutants.py
             `dev/audit/harnesses/r10_seat_selftests_mutants.py` is in the tree at this head
  ok         tools/audit/seat/offline_spy.py
             `tools/audit/seat/offline_spy.py` is in the tree at this head
  unverified python3
             python3 with no script argument
  unverified python
             python with no script argument
  ok         tests/entities.py
             `tests/entities.py` is in the tree at this head
  ok         dev/audit/harnesses/r10_fly_nightly_hb.py
             `dev/audit/harnesses/r10_fly_nightly_hb.py` is in the tree at this head
  ok         tools/audit/worktree_gc.sh
             `tools/audit/worktree_gc.sh` is in the tree at this head
  ok         tools/pr/prepr.sh
             `tools/pr/prepr.sh` is in the tree at this head
  ok         tools/pr/gh_comment.py
             `tools/pr/gh_comment.py` is in the tree at this head
  ok         tests/arch_score.py
             `tests/arch_score.py` is in the tree at this head
  ok         tests/gate_lock.py
             `tests/gate_lock.py` is in the tree at this head

FIGURES: 17 resolved, 5 not verified, 0 refused

## Finder's harness: none named
### at the base
not run
### at the head
not run

## Mutation-ledger diff
none

## Three-dot diff
diff --git a/dev/audit/harnesses/r10_uutils_sleep.sh b/dev/audit/harnesses/r10_uutils_sleep.sh
new file mode 100644
index 000000000..403cf415d
--- /dev/null
+++ b/dev/audit/harnesses/r10_uutils_sleep.sh
@@ -0,0 +1,42 @@
+#!/usr/bin/env bash
+# r10-hotfix-uutils-sleep: pr_args.sh's self-test on a host whose sleep is a
+# uutils-style multicall binary (ubuntu-26.04's /bin/sleep), which refuses to
+# run when argv[0]'s basename is not `sleep`. Linux only: a private mount
+# namespace binds an emulating script over /usr/bin/sleep (and so /bin/sleep);
+# macOS has no uutils and no namespace, so no cheaper host reproduces it.
+#
+#   bash dev/audit/harnesses/r10_uutils_sleep.sh <rev> [emu|gnu] [symlink]
+#
+# Runs `pr_args.sh --self-test` in a fresh detached worktree at <rev>, under the
+# emulation (emu, the default) or the host's own sleep (gnu, the null control).
+# `symlink` first restores the bystander fixture's renamed link to /bin/sleep
+# (the mutant). Prints the self-test's tally line and rc=<its exit status>.
+set -uo pipefail
+rev=${1:?usage: r10_uutils_sleep.sh <rev> [emu|gnu] [symlink]}; mode=${2:-emu}; mut=${3:-}
+top=$(git rev-parse --show-toplevel) || exit 2
+d=$(mktemp -d); wt=$d/wt
+trap 'git -C "$top" worktree remove --force "$wt" 2>/dev/null; rm -rf "$d"' EXIT
+git -C "$top" worktree add -q --detach "$wt" "$rev" || exit 2
+if [ "$mut" = symlink ]; then
+  python3 - "$wt/tools/audit/seat/pr_args.sh" <<'PY' || exit 2
+import sys
+p = sys.argv[1]; s = open(p).read()
+old = """  printf '#!/bin/sh\\nexec sleep "$1"\\n' > "$REAP_DIR/unrelated-sleep"; chmod +x "$REAP_DIR/unrelated-sleep"\n"""
+if s.count(old) != 1:
+    sys.exit("mutant anchor not found exactly once")
+open(p, "w").write(s.replace(old, '  ln -s /bin/sleep "$REAP_DIR/unrelated-sleep"\n'))
+PY
+fi
+mkdir "$d/real"; cp "$(readlink -f /usr/bin/sleep)" "$d/real/sleep"  # basename kept: a multicall host sleep runs too
+printf '%s\n' '#!/bin/sh' \
+  "case \${0##*/} in sleep) exec $d/real/sleep \"\$@\" ;; esac" \
+  "printf 'Security violation: Requested utility \`%s\` does not match executable name \`sleep\`\\n' \"\${0##*/}\" >&2; exit 1" > "$d/sleep"
+chmod +x "$d/sleep"
+run='cd "$0" && bash tools/audit/seat/pr_args.sh --self-test > "$1/out" 2>&1; echo "rc=$?" >> "$1/out"'
+if [ "$mode" = emu ]; then
+  ns=(unshare -m); [ "$(id -u)" = 0 ] || ns=(unshare -rm)
+  "${ns[@]}" bash -c "mount --bind '$d/sleep' /usr/bin/sleep && $run" "$wt" "$d" || exit 2
+else
+  bash -c "$run" "$wt" "$d"
+fi
+grep -E '^ *FAIL|^pr_args self-test:|^rc=' "$d/out"
diff --git a/dev/programme/delivery/3086.md b/dev/programme/delivery/3086.md
new file mode 100644
index 000000000..58b6dd79b
--- /dev/null
+++ b/dev/programme/delivery/3086.md
@@ -0,0 +1 @@
+- [#3086](https://github.com/tvofi/heatpump_optimizer/pull/3086) — **open**, R10-HOTFIX-UUTILS-SLEEP: hotfix uutils sleep (R10-HOTFIX-UUTILS-SLEEP)
diff --git a/tests/closures.json b/tests/closures.json
index 673fddd35..361b84499 100644
--- a/tests/closures.json
+++ b/tests/closures.json
@@ -4030,6 +4030,7 @@
    "dev/audit/harnesses/r10_triage_gate_replay.py",
    "dev/audit/harnesses/r10_trust_relative_bundle.py",
    "dev/audit/harnesses/r10_u9a_ratchet_nulls.py",
+   "dev/audit/harnesses/r10_uutils_sleep.sh",
    "dev/audit/harnesses/r10_vent_bias_window.py",
    "dev/audit/harnesses/r10_vent_probe_companion.py",
    "dev/audit/harnesses/r10_vent_sun_transient.py",
diff --git a/tools/audit/seat/pr_args.sh b/tools/audit/seat/pr_args.sh
index f36786f8e..cab8ab07b 100644
--- a/tools/audit/seat/pr_args.sh
+++ b/tools/audit/seat/pr_args.sh
@@ -622,7 +622,9 @@ STUB
   # each arm counts what is still alive after the signal. The bystander sleeper
   # started here descends from no pusher: it is the null control for "kills only
   # what it started", and the arm the by-pid rule is mutated against.
-  ln -s /bin/sleep "$REAP_DIR/unrelated-sleep"
+  # A wrapper, never a link to the sleep binary: uutils' multicall sleep (ubuntu-26.04's
+  # /bin/sleep) refuses an argv[0] that is not `sleep`. The exec keeps $UNREL the sleeper's pid.
+  printf '#!/bin/sh\nexec sleep "$1"\n' > "$REAP_DIR/unrelated-sleep"; chmod +x "$REAP_DIR/unrelated-sleep"
   "$REAP_DIR/unrelated-sleep" "${PR_SELFTEST_SECONDS:-1200}" & UNREL=$!  # the bound's session ends it at the latest
   ralive() { # <pids file> -> how many of its pids are alive; polled, since a killed child can be a zombie for a moment
     local p n k=0

