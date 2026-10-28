# Review packet #2920
head: 67c7fdf39849f8b51222004e84812ec5bd2807de
base: b6f6ceca4f0323b24171c45a2a2372ba2e2cbaaa

Start here (fix-review.md). Re-read the live check state before a verdict: the digest is as read at render.

## Gate digest: pending
arm id=123056498406 skipped
cancel-superseded id=123056506283 queued
prelude id=123056505824 queued
refresh id=123056506440 queued

## Refusals
none

## Advisories
hot-file: HPO_BUS_TRAIN_STATE is unset, so every merge verdict reads unboarded

## carry_audit at the head
NOTE body item 1938b7f7: #2721
CARRY-AUDIT: 1 finding item(s): 1 routed, 0 unrouted, 0 bad destination(s)

## figure_lint at the head
ok         bash dev/audit/harnesses/r10_fly_orphans_landed.sh <checkout> 57f0c9c77cfd5958e0a2443e158bea8326bedae2
             `dev/audit/harnesses/r10_fly_orphans_landed.sh` is in the tree at this head
  ok         tests/entities.py
             `tests/entities.py` is in the tree at this head
  ok         tests/harness_headers.py
             `tests/harness_headers.py` is in the tree at this head
  unverified python3
             python3 with no script argument
  ok         python3 tests/closure.py select --diff $(git merge-base origin/main HEAD)
             `tests/closure.py` is in the tree at this head
  ok         tests/env_drift.py --claims-only
             `tests/env_drift.py` is in the tree at this head
  ok         tests/closure.py selftest
             `tests/closure.py` is in the tree at this head
  ok         tests/layout.py
             `tests/layout.py` is in the tree at this head
  ok         python3 tests/structure.py
             `tests/structure.py` is in the tree at this head
  ok         bash tools/audit/seat/bus.sh --self-test
             `tools/audit/seat/bus.sh` is in the tree at this head
  ok         python3 -I tools/audit/seat/ledger.py --self-test
             `tools/audit/seat/ledger.py` is in the tree at this head
  ok         bash tools/audit/seat/cloud_relay.sh --self-test
             `tools/audit/seat/cloud_relay.sh` is in the tree at this head
  ok         python3 -I tools/audit/seat/orchestrator_tick.py --self-test
             `tools/audit/seat/orchestrator_tick.py` is in the tree at this head
  ok         python3 -I tools/audit/seat/r10_ledger_mutants.py --self-test
             `tools/audit/seat/r10_ledger_mutants.py` is in the tree at this head
  ok         dev/audit/harnesses/r10_fly_orphans_landed.sh
             `dev/audit/harnesses/r10_fly_orphans_landed.sh` is in the tree at this head
  ok         python3 tools/audit/archscore/score.py --diff $(git merge-base origin/main HEAD)
             `tools/audit/archscore/score.py` is in the tree at this head

FIGURES: 15 resolved, 1 not verified, 0 refused

## Finder's harness: none named
### at the base
not run
### at the head
not run

## Mutation-ledger diff
none

## Three-dot diff
diff --git a/dev/audit/harnesses/r10_fly_orphans_landed.sh b/dev/audit/harnesses/r10_fly_orphans_landed.sh
new file mode 100644
index 000000000..851263032
--- /dev/null
+++ b/dev/audit/harnesses/r10_fly_orphans_landed.sh
@@ -0,0 +1,79 @@
+#!/bin/bash
+# r10_fly_orphans_landed.sh -- drive a checkout's own `bus.sh orphans` over
+# handoffs whose change is already on main (R10-FLY-ORPHANS-REWRITTEN).
+#
+#   bash dev/audit/harnesses/r10_fly_orphans_landed.sh <checkout> [<main sha>]
+#
+# Builds a throwaway bare remote borrowing this repository's objects, sets its
+# main to <main sha> (default origin/main), pushes one handoff/<t> and
+# handoff-body/<t> pair per case, and runs <checkout>/tools/audit/seat/bus.sh
+# orphans --min-age-h 0 against it, so each end of a fix is measured by its
+# own production classifier. One line per case:
+#   RESULT <case>=<ORPHAN|SUPERSEDED|discharged> expect=<landed|stranded>
+# then `MISREAD <n>`: the landed cases read ORPHAN plus the stranded read
+# otherwise. Then the relay's level over the same refs, <checkout>'s own
+# `ledger.py level`, given each pr<N> topic as `pr<N> merged=<merge commit
+# time>` (what the relay reads from `gh pr list --state merged`; a checkout
+# that predates that line ignores it): `LEVEL <case>=<owed|closed>`, and
+# `LEVEL-MISREAD <n>` alike. The cases:
+#   earlycutoff  ecaf178cb, the handoff #2397 landed by another commit, read
+#                stranded 121.8 h (the brief's evidence)                landed
+#   pr<N>        #2513 #2465 #2485 #2519 #2525, the five merged handoffs the
+#                level owed until archived, SIMULATED: their refs are gone, so
+#                each tip is the PR head's tree rewritten as one commit on the
+#                merge base of the merge's parents (an App push's shape) landed
+#   null         one commit adding a file main lacks, off main     stranded
+# Needs a full clone (git fetch --unshallow) holding those commits.
+set -u
+CO=$(cd "${1:?usage: r10_fly_orphans_landed.sh <checkout> [<main sha>]}" && pwd)
+SRC=$(git rev-parse --show-toplevel)
+MAIN=${2:-$(git -C "$SRC" rev-parse origin/main)}
+ROOT=$(git -C "$(dirname -- "$0")" rev-parse --show-toplevel) || exit 2
+# shellcheck source=tests/throwaway_git.sh
+. "$ROOT/tests/throwaway_git.sh" # the one way a script builds a throwaway repository
+W=$(mktemp -d); trap 'rm -rf "$W"' EXIT
+throwaway_git_init "$W/o.git" -q --bare && throwaway_git_init "$W/seat" -q || exit 2
+for r in "$W/o.git" "$W/seat/.git"; do
+  echo "$(git -C "$SRC" rev-parse --path-format=absolute --git-common-dir)/objects" > "$r/objects/info/alternates"
+done
+g() { git -C "$W/seat" "$@"; }
+g remote add origin "$W/o.git"
+cases=() merged=() pushes=("$MAIN:refs/heads/main")
+add() { [ -n "$2" ] || { echo "case $1: no tip built" >&2; exit 2; }; cases+=("$1 $2 $3"); pushes+=("$2:refs/heads/handoff/$1" "$2:refs/heads/handoff-body/$1"); }
+add earlycutoff ecaf178cbd4eef5e3b30425bd4693bef8ceb4b24 landed
+for n in 2513 2465 2485 2519 2525; do
+  m=$(git -C "$SRC" log -1 --format=%H --grep="^Merge pull request #$n " "$MAIN") || exit 2
+  [ -n "$m" ] || { echo "no merge of #$n on $MAIN" >&2; exit 2; }
+  base=$(git -C "$SRC" merge-base "$m^1" "$m^2")
+  merged+=("pr$n merged=$(git -C "$SRC" log -1 --format=%cI "$m")")
+  add "pr$n" "$(GIT_AUTHOR_DATE="1790000000 +0000" GIT_COMMITTER_DATE="1790000000 +0000" g commit-tree "$m^2^{tree}" -p "$base" -m "#$n rewritten")" landed
+done
+b=$(printf 'r10-fly-orphans null control\n' | g hash-object -w --stdin)
+GIT_INDEX_FILE=$W/idx g read-tree "$MAIN"
+GIT_INDEX_FILE=$W/idx g update-index --add --cacheinfo "100644,$b,r10_fly_null.txt"
+add null "$(GIT_AUTHOR_DATE="1790000000 +0000" GIT_COMMITTER_DATE="1790000000 +0000" g commit-tree "$(GIT_INDEX_FILE=$W/idx g write-tree)" -p "$MAIN" -m null)" stranded
+g push -q origin "${pushes[@]}" || exit 2
+out=$(cd "$W/seat" && HPO_BUS_STATE=$W/state bash "$CO/tools/audit/seat/bus.sh" orphans --min-age-h 0 2>&1)
+echo "$out" | grep -q '^orphans: ' || { echo "$out" >&2; echo "no orphans summary line" >&2; exit 2; }
+bad=0
+for c in "${cases[@]}"; do
+  set -- $c
+  st=$(echo "$out" | awk -v t="$1" '($1 == "ORPHAN" || $1 == "SUPERSEDED") && $2 == t { print $1 }')
+  echo "RESULT $1=${st:-discharged} expect=$3"
+  case $3/${st:-discharged} in landed/ORPHAN|stranded/SUPERSEDED|stranded/discharged) bad=$((bad + 1)) ;; esac
+done
+echo "$out" | tail -n 1
+echo "MISREAD $bad"
+git -C "$W/seat" ls-remote origin 'refs/heads/handoff/*' 'refs/heads/handoff-body/*' > "$W/hrefs"
+printf '%s\n' "${merged[@]}" > "$W/topics"
+lv=$(cd "$W/seat" && python3 -I "$CO/tools/audit/seat/ledger.py" --log "$W/lv/l" level "$W/hrefs" "$W/topics" 2>"$W/lv.err")
+[ $? -le 1 ] || { cat "$W/lv.err" >&2; echo "the level could not be derived" >&2; exit 2; }
+bad=0
+for c in "${cases[@]}"; do
+  set -- $c
+  st=closed; echo "$lv" | grep -q " handoff-no-pr refs/heads/handoff[a-z-]*/$1 " && st=owed
+  echo "LEVEL $1=$st expect=$3"
+  case $3/$st in landed/owed|stranded/closed) bad=$((bad + 1)) ;; esac
+done
+echo "LEVEL-LINES $(echo "$lv" | grep -c handoff-no-pr) for ${#cases[@]} topics; $(cat "$W/lv.err")"
+echo "LEVEL-MISREAD $bad"
diff --git a/dev/programme/delivery/2920.md b/dev/programme/delivery/2920.md
new file mode 100644
index 000000000..e099b12d6
--- /dev/null
+++ b/dev/programme/delivery/2920.md
@@ -0,0 +1 @@
+- [#2920](https://github.com/tvofi/heatpump_optimizer/pull/2920) — **open**, fix(orphans): one landed classifier, shared by bus.sh orphans and the relay's level (R10-FLY-ORPHANS-REWRITTEN) (R10-FLY-ORPHANS-REWRITTEN)
diff --git a/tests/closures.json b/tests/closures.json
index 6063b8d8c..b68ca4e57 100644
--- a/tests/closures.json
+++ b/tests/closures.json
@@ -3705,6 +3705,7 @@
    "dev/audit/harnesses/r10_flow_autotrain_live.py",
    "dev/audit/harnesses/r10_flow_autotrain_mutants.sh",
    "dev/audit/harnesses/r10_flow_dispatch_mutants.py",
+   "dev/audit/harnesses/r10_fly_orphans_landed.sh",
    "dev/audit/harnesses/r10_ftol_cell_search.py",
    "dev/audit/harnesses/r10_gate_defer_race.py",
    "dev/audit/harnesses/r10_gate_priority_base.py",
diff --git a/tools/audit/seat/INSTRUMENTS.md b/tools/audit/seat/INSTRUMENTS.md
index c2a5128fe..88bd04cf4 100644
--- a/tools/audit/seat/INSTRUMENTS.md
+++ b/tools/audit/seat/INSTRUMENTS.md
@@ -417,7 +417,9 @@ sweep's standing-seat liveness step keep them alive.
   `handoff-no-pr` lines in `<log>.level` are `ledger.py level`'s fold of
   every `handoff/*` and `handoff-body/*` ref, rewritten every pass: owed unless
   its topic has an open pull request, it is disposed at its sha, or main
-  already carries the change (ancestry, or content: see `ledger.py`), each
+  already carries the change (`ledger.py landed`, the one classifier `bus.sh
+  orphans` asks too: ancestry, clean merges, reverse-apply, content), one line
+  per topic (a body ref rides its code ref's), each
   with its tip's commit time and last opener attempt; a failed PR listing or
   ledger read leaves those lines as they were, since an empty list would make
   every ref look orphaned. Every event the relay owes (`verdict-unposted` at
diff --git a/tools/audit/seat/bus.sh b/tools/audit/seat/bus.sh
index 9636471cd..94b282eab 100755
--- a/tools/audit/seat/bus.sh
+++ b/tools/audit/seat/bus.sh
@@ -36,12 +36,14 @@
 # owed a pull request -- `open_pr.sh` fetches both and fails without the body --
 # and is reported in one of three states. IN FLIGHT: its tip is younger than
 # --min-age-h hours (default 2), a lane's own push, silently counted, never a
-# line. STRANDED: no `fix/<t>` or `fix/<t>-pr` head carries the tip, the tip is
-# no ancestor of `main` or a live `fix/*` head, and the change is not already on
-# main. SUPERSEDED: flagged by that ancestry test, but a content-equivalence
-# arm (`content_superseded`) finds main already carries every path the ref's
-# uncovered commits touch -- a recovery rewrote the commit and landed the
-# change under another, so the ref needs pruning, not an opener. Each STRANDED
+# line. STRANDED: no `fix/<t>` or `fix/<t>-pr` head carries the tip, and
+# `ledger.py landed` -- the one classifier, which the relay's level shares --
+# finds neither its commits inside `main` and the live `fix/*` heads (merges
+# with no resolution of their own aside) nor its change on main. SUPERSEDED:
+# flagged by that ancestry test, but main carries the change: the patch applies
+# to main reversed and not forward, or every file it touches is on main
+# (`covered`) -- a recovery rewrote the commit, or another pull request landed
+# the patch, so the ref needs pruning, not an opener. Each STRANDED
 # line names the repair it needs, never works it: `opener` (no pull request:
 # `open_pr.sh`), `update` (its pull request's head is behind the ref:
 # `update_pr.sh`) or `review` (a pull request that diverged from the ref, a
@@ -564,40 +566,9 @@ watch() {
   done
 }
 
-# content_superseded TIP -> rc 0 when main already carries every path the ref's
-# uncovered commits touch, so the ref is SUPERSEDED rather than stranded: a
-# modification byte-identical on main, an addition whose basename main holds (a
-# recovery that moved or renamed the file, e.g. the tools/ -> dev/ restructure),
-# a deletion main already made, a rename to a basename main holds. The ancestry
-# arm asks "is this work inside main"; this one asks "is it on main under
-# another commit" -- a recovery that rewrote the commit leaves a non-ancestral
-# ref whose content main has. Reads the caller's `main`, `main_basenames`, `LF`.
-content_superseded() { # tip -> 0 superseded, 1 stranded
-  local tip=$1 mb st a b base b1 b2
-  mb=$(git merge-base "$main" "$tip") || return 1
-  while IFS=$'\t' read -r st a b; do
-    [ -n "$st" ] || continue
-    case $st in
-      A) base=${a##*/}
-         case $main_basenames in *"$LF$base$LF"*) ;; *) return 1 ;; esac ;;
-      M) b1=$(git rev-parse "$tip:$a" 2>/dev/null) || return 1
-         b2=$(git rev-parse "$main:$a" 2>/dev/null) || return 1
-         [ "$b1" = "$b2" ] || return 1 ;;
-      D) git rev-parse "$main:$a" >/dev/null 2>&1 && return 1 ;;
-      R*) base=${b##*/}
-          case $main_basenames in *"$LF$base$LF"*) ;; *) return 1 ;; esac
-          git rev-parse "$main:$a" >/dev/null 2>&1 && return 1 ;;
-      *) return 1 ;;
-    esac
-  done <<EOF
-$(git diff --name-status "$mb" "$tip")
-EOF
-  return 0
-}
-
 orphans() { # [--min-age-h N] [--no-body] [--no-ancestry] [--no-content] [--exclude-topic T]... -> one ORPHAN line each, rc 1 when any stranded
   local ns=refs/hpo-orphans LF=$'\n' min_age=2 no_body=0 no_ancestry=0 no_content=0 excl=$'\n'
-  local t ref tip main fix_nl fix_heads bodies_nl main_basenames h hit
+  local t ref tip main fix_nl fix_heads bodies_nl landed_nl why hit arms
   local reported=0 superseded=0 nb=0 named=0 anc=0 young=0
   local ct now age_s age_t word dn H bt
   while [ $# -gt 0 ]; do
@@ -629,7 +600,15 @@ orphans() { # [--min-age-h N] [--no-body] [--no-ancestry] [--no-content] [--excl
   fix_nl=$LF"$(git for-each-ref --format='%(refname)' "$ns/fix/")"$LF
   fix_heads=$(git for-each-ref --format='%(objectname)' "$ns/fix/")
   bodies_nl=$LF"$(git for-each-ref --format='%(refname)' "$ns/handoff-body/")"$LF
-  main_basenames=$LF"$(git ls-tree -r --name-only "$main" | sed 's#.*/##')"$LF
+  # LANDED: ledger.py's classifier, the one owner of "main already carries this
+  # tip" (the relay's handoff-no-pr level folds through the same function), asked
+  # once for every handoff tip: `<tip> <why>`, `-` when nothing carries it.
+  arms=()
+  [ "$no_ancestry" = 1 ] && arms+=(--no-ancestry)
+  [ "$no_content" = 1 ] && arms+=(--no-content)
+  landed_nl=$LF"$(git for-each-ref --format='%(objectname)' "$ns/handoff/" \
+    | python3 -I "$ROOT/tools/audit/seat/ledger.py" landed "${arms[@]}" "$main" $fix_heads)"$LF \
+    || die "orphans: ledger.py landed could not classify the handoff tips"
   now=$(date +%s)
   # A while-read over a heredoc, not a pipe: the counters survive the loop.
   while read -r ref tip; do
@@ -653,15 +632,11 @@ orphans() { # [--min-age-h N] [--no-body] [--no-ancestry] [--no-content] [--excl
       esac
     done
     if [ "$hit" = 1 ]; then named=$((named + 1)); continue; fi
-    # DISCHARGED, ancestry half: the tip is inside `main` or a live `fix/*`
-    # head already. Both halves are required; each alone over-reports.
-    if [ "$no_ancestry" != 1 ]; then
-      hit=0
-      for h in "$main" $fix_heads; do
-        git merge-base --is-ancestor "$tip" "$h" && { hit=1; break; }
-      done
-      if [ "$hit" = 1 ]; then anc=$((anc + 1)); continue; fi
-    fi
+    # DISCHARGED, ancestry half: the tip is inside `main` or the live `fix/*`
+    # heads already, or outside them only by clean merges. Both halves are
+    # required; each alone over-reports.
+    why=${landed_nl#*"$LF$tip "}; why=${why%%"$LF"*}
+    case $why in ancestor|merges-only) anc=$((anc + 1)); continue ;; esac
     # AGED: a ref pushed moments ago is a lane's own in-flight handoff, not an
     # orphan. A stamp ahead of the clock reads as young, never as aged.
     ct=$(git log -1 --format=%ct "$tip" 2>/dev/null) || ct=""
@@ -673,9 +648,10 @@ orphans() { # [--min-age-h N] [--no-body] [--no-ancestry] [--no-content] [--excl
     if [ "$((age_s / 3600))" -lt "$min_age" ]; then young=$((young + 1)); continue; fi
     age_t=$((age_s / 360))
     # SUPERSEDED: not ancestral to main, but main already carries the change
-    # (the recovery rewrote the commit). Report it so the ref can be pruned
-    # deliberately; it is not stranded and does not fail the run.
-    if [ "$no_content" != 1 ] && content_superseded "$tip"; then
+    # (the recovery rewrote the commit, or another pull request landed the
+    # patch). Report it so the ref can be pruned deliberately; it is not
+    # stranded and does not fail the run.
+    if [ "$why" = reverse-apply ] || [ "$why" = content ]; then
       printf 'SUPERSEDED %s %s %s.%sh\n' "$t" "$tip" "$((age_t / 10))" "$((age_t % 10))"
       superseded=$((superseded + 1)); continue
     fi
@@ -1152,6 +1128,14 @@ B
     sub=$(printf '100644 blob %s\t%s\n' "$b" "$f" | git -C "$W/seat" mktree)
     printf 'add %s/%s\n' "$d" "$f" | git -C "$W/seat" commit-tree "$(printf '040000 tree %s\t%s\n' "$sub" "$d" | git -C "$W/seat" mktree)" -p "$p"
   }
+  mkf() { # <parent> <file> <content> [<parent2>] -> a commit setting top-level <file> in <parent>'s tree
+    local p=$1 f=$2 b t
+    b=$(printf '%b' "$3" | git -C "$W/seat" hash-object -w --stdin)
+    GIT_INDEX_FILE=$W/mkf.idx git -C "$W/seat" read-tree "$p"
+    GIT_INDEX_FILE=$W/mkf.idx git -C "$W/seat" update-index --add --cacheinfo "100644,$b,$f"
+    t=$(GIT_INDEX_FILE=$W/mkf.idx git -C "$W/seat" write-tree)
+    printf 'set %s\n' "$f" | git -C "$W/seat" commit-tree "$t" -p "$p" ${4:+-p "$4"}
+  }
   mb=$(git -C "$W/seat" rev-parse HEAD)
   # A stranded opener: owed, no pull request, no ancestor of main -> exit 1.
   o1=$(mkc "$mb" orph1)
@@ -1212,6 +1196,51 @@ B
   out=$(run orphans --min-age-h 0 --no-content)
   echo "$out" | grep -qx "ORPHAN orp-super $s1 .* repair=opener"
   expect "the content arm is load-bearing: --no-content reads the same ref as stranded" $?
+  # The earlycutoff shape (#2397): a hunk another pull request landed into a file
+  # main has since changed. The byte-identical arm read it stranded for 121.8 h.
+  b0=$(mkf "$m1" hunk.txt 'a\nb\n'); git -C "$W/seat" push -q origin "$b0:refs/heads/main"
+  e1=$(mkf "$b0" hunk.txt 'a\nb\nblock1\nblock2\n')
+  git -C "$W/seat" push -q origin "$e1:refs/heads/handoff/orp-hunk" "$e1:refs/heads/handoff-body/orp-hunk"
+  m2=$(mkf "$b0" hunk.txt 'z\na\nb\nblock1\nblock2\n'); git -C "$W/seat" push -q origin "$m2:refs/heads/main"
+  out=$(run orphans --min-age-h 0)
+  echo "$out" | grep -qx "SUPERSEDED orp-hunk $e1 .*"
+  expect "a hunk main carries in a file that moved on is SUPERSEDED, not stranded (#2397's shape)" $?
+  # A patch on main, context and all, whose removed line main still holds
+  # elsewhere: only the reverse-apply arm sees it (applies reversed, not forward).
+  r0=$(mkf "$m2" rev.txt 'x\nfi\ny\nfi\np\nq\nr\ns\nt\n'); git -C "$W/seat" push -q origin "$r0:refs/heads/main"
+  r1=$(mkf "$r0" rev.txt 'x\nfi\ny\np\nq\nr\ns\nt\n')
+  git -C "$W/seat" push -q origin "$r1:refs/heads/handoff/orp-rev2" "$r1:refs/heads/handoff-body/orp-rev2"
+  m3=$(mkf "$r0" rev.txt 'x\nfi\ny\np\nq\nr\ns\nT\n'); git -C "$W/seat" push -q origin "$m3:refs/heads/main"
+  out=$(run orphans --min-age-h 0)
+  echo "$out" | grep -qx "SUPERSEDED orp-rev2 $r1 .*"
+  expect "a patch that applies to main reversed and not forward is SUPERSEDED" $?
+  # Null control: the same removal of a line main has NOT removed stays stranded.
+  r2=$(mkf "$r0" rev.txt 'x\ny\nfi\np\nq\nr\ns\nt\n')
+  git -C "$W/seat" push -q origin "$r2:refs/heads/handoff/orp-rev3" "$r2:refs/heads/handoff-body/orp-rev3"
+  out=$(run orphans --min-age-h 0)
+  echo "$out" | grep -qx "ORPHAN orp-rev3 $r2 .* repair=opener"
+  expect "null control: a patch main does not hold stays stranded" $?
+  # The merge-tip shape (a457acaf4): the tip merges a main commit with a commit
+  # a live fix/* head carries; no non-merge commit is outside main and the heads.
+  q1=$(mkf "$m3" mA.txt 'A\n'); git -C "$W/seat" push -q origin "$q1:refs/heads/main"
+  q2=$(mkf "$m3" mB.txt 'B\n')
+  q3=$(mkf "$q2" mA.txt 'A\n' "$q1"); qf=$(mkf "$q3" mC.txt 'C\n')
+  q4=$(git -C "$W/seat" commit-tree "$q3^{tree}" -p "$q2" -p "$q1" -m 'merge main')
+  git -C "$W/seat" push -q origin "$qf:refs/heads/fix/orp-merge-other" \
+    "$q4:refs/heads/handoff/orp-merge" "$q4:refs/heads/handoff-body/orp-merge"
+  out=$(run orphans --min-age-h 0)
+  ! echo "$out" | grep -q "^ORPHAN orp-merge " && ! echo "$out" | grep -q "^SUPERSEDED orp-merge "
+  expect "a tip outside main and the fix heads only by a clean merge is discharged with the ancestry" $?
+  # Null controls: a merge carrying a resolution of its own, and one non-merge
+  # commit outside main and every head, stay stranded.
+  q5=$(mkf "$q3" evil.txt 'E\n'); q5=$(git -C "$W/seat" commit-tree "$q5^{tree}" -p "$q2" -p "$q1" -m 'evil merge')
+  q6=$(mkf "$q2" mD.txt 'D\n')
+  git -C "$W/seat" push -q origin "$q5:refs/heads/handoff/orp-evil" "$q5:refs/heads/handoff-body/orp-evil" \
+    "$q6:refs/heads/handoff/orp-nonm" "$q6:refs/heads/handoff-body/orp-nonm"
+  out=$(run orphans --min-age-h 0)
+  echo "$out" | grep -qx "ORPHAN orp-evil $q5 .*" && echo "$out" | grep -qx "ORPHAN orp-nonm $q6 .*"
+  expect "null control: a merge with its own resolution, or a non-merge commit absent everywhere, stays stranded" $?
+  git -C "$W/seat" push -q origin :refs/heads/handoff/orp-rev3 :refs/heads/handoff/orp-evil :refs/heads/handoff/orp-nonm
   # Green: every stranded ref carries a pull request at its tip now; the
   # superseded ref stays, and neither is stranded -> exit 0.
   git -C "$W/seat" push -q origin "$o1:refs/heads/fix/orph1" \
@@ -1230,6 +1259,15 @@ B
   out=$(run orphans --min-age-h 0); rc=$?
   echo "$out" | grep -qx "ORPHAN orp-force $f2 .* repair=opener" && [ $rc = 1 ]
   expect "a handoff ref rewritten non-fast-forward after a run is still read, at its new tip" $?
+  # Null control: a classifier that cannot answer refuses the run; it never
+  # reads every tip as stranded (a loud list is still a wrong one).
+  mkdir -p "$W/pyfail"; rp=$(command -v python3)
+  printf '#!/bin/sh\ncase "$*" in *ledger.py\ landed*) exit 3 ;; esac\nexec "%s" "$@"\n' "$rp" > "$W/pyfail/python3"
+  chmod +x "$W/pyfail/python3"
+  out=$(PATH=$W/pyfail:$PATH run orphans --min-age-h 0); rc=$?
+  echo "$out" | grep -q "REFUSE: orphans: ledger.py landed could not classify" && [ $rc != 0 ] \
+    && ! echo "$out" | grep -q "^ORPHAN "
+  expect "null control: a classifier that fails refuses orphans, never an all-ORPHAN list" $?
   # Null control: a remote that cannot answer still refuses, never a clean zero.
   out=$(HPO_BUS_REMOTE=$W/nowhere.git run orphans --min-age-h 0); rc=$?
   [ $rc != 0 ] && echo "$out" | grep -q "could not fetch the refs of" && ! echo "$out" | grep -q "^orphans: "
diff --git a/tools/audit/seat/cloud_relay.sh b/tools/audit/seat/cloud_relay.sh
index 35741074e..c7909dd10 100644
--- a/tools/audit/seat/cloud_relay.sh
+++ b/tools/audit/seat/cloud_relay.sh
@@ -100,8 +100,9 @@
 #     meanwhile as `OWED <utc> handoff-update <ref> <sha>` in <log>.level. The
 #     `handoff-no-pr` lines there are `ledger.py level`'s fold of every
 #     handoff/* and handoff-body/* ref: owed unless its topic has an open PR,
-#     it is disposed at its sha, or main already carries the change (ancestry
-#     or content), each with its tip's commit time; rewritten every pass, and
+#     it is disposed at its sha, or main already carries the change (`ledger.py
+#     landed`, the classifier bus.sh orphans asks too), one line per topic
+#     (a body ref rides its code ref's), each with its tip's commit time; rewritten every pass, and
 #     a failed PR listing or ledger read leaves them as they were.
 #     HOLD. `<state>/cloud-handoff-hold` lists PR numbers, one per line (blank
 #     lines and `#` lines allowed); only the orchestrator writes or edits it.
@@ -458,11 +459,18 @@ handoff_arm() { # one pass over open PRs; updates one whose handoff is ahead of
   level_set handoff-held "$state/cloud-level-held.$$"
   # a handoff or handoff-body ref whose topic has no open PR is OWED on every pass until disposed
   cut -f2 "$state/cloud-prs.$$" | sed -e 's,^fix/,,' -e 's,-pr$,,' > "$state/cloud-topics.$$"
+  # and the merged ones, `<topic> merged=<utc>`: a merge closes a handoff committed by then (RCA section 5.1)
+  { if [ -n "${HPO_RELAY_MERGED:-}" ]; then "$HPO_RELAY_MERGED"
+    else gh pr list -R "$repo" --state merged --limit 200 --json headRefName,mergedAt \
+      -q '.[] | [.headRefName, .mergedAt] | @tsv'; fi; } > "$state/cloud-merged.$$" \
+    || { echo "cloud_relay: could not list merged PRs; the handoff level stays as it was" >&2
+         rm -f "$state/cloud-prs.$$" "$state/cloud-hrefs.$$" "$state/cloud-topics.$$" "$state/cloud-vrefs.$$" "$state/cloud-merged.$$"; return 0; }
+  awk -F'\t' 'NF == 2 { t = $1; sub(/^fix\//, "", t); sub(/-pr$/, "", t); print t " merged=" $2 }' "$state/cloud-merged.$$" >> "$state/cloud-topics.$$"
   # The level is ledger.py's fold (rc 0 none owed, 1 owed, 2 unreadable: the level stays as it was).
   ledger level "$state/cloud-hrefs.$$" "$state/cloud-topics.$$" > "$state/cloud-level-handoff.$$"
   case $? in 0|1) level_set handoff-no-pr "$state/cloud-level-handoff.$$";;
     *) echo "cloud_relay: the ledger could not derive the handoff level; it stays as it was" >&2; rm -f "$state/cloud-level-handoff.$$";; esac
-  rm -f "$state/cloud-prs.$$" "$state/cloud-hrefs.$$" "$state/cloud-topics.$$" "$state/cloud-vrefs.$$"
+  rm -f "$state/cloud-prs.$$" "$state/cloud-hrefs.$$" "$state/cloud-topics.$$" "$state/cloud-vrefs.$$" "$state/cloud-merged.$$"
 }
 
 # THE STUCK ANDON (triage P163; a trial, report-only, removed if it reports no STUCK line in its first
@@ -718,6 +726,7 @@ EOF
   rm -rf "$t/pr"; throwaway_git_init "$t/pr" -q; hc base; mkref fix/topic-a-pr; PRH=$(git -C "$t/pr" rev-parse HEAD)
   printf '%s\t%s\t%s\n' 41 fix/topic-a-pr "$PRH" > "$prs"
   printf '#!/bin/sh\ncat "%s"\n' "$prs" > "$t/lister.sh"; chmod +x "$t/lister.sh"; export HPO_RELAY_PRS=$t/lister.sh
+  : > "$t/merged.tsv"; printf '#!/bin/sh\ncat "%s"\n' "$t/merged.tsv" > "$t/mlister.sh"; chmod +x "$t/mlister.sh"; export HPO_RELAY_MERGED=$t/mlister.sh
   # update stub: records args, advances the PR head to a new commit that contains the handoff
   printf '#!/bin/sh\necho "$1 $2 $(basename "$3" | cut -c1-0) $4 $5" >> "%s/updated"\ncp "$3" "%s/body.seen"\necho "$3" > "%s/body.path"\nprintf "41\\tfix/topic-a-pr\\t%s\\n" > "%s"\n' "$t" "$t" "$t" "$N40" "$prs" > "$ustub"
   printf '#!/bin/sh\necho "$1" >> "%s/approved"\n' "$t" > "$astub"
@@ -905,6 +914,19 @@ EOF
   handoff_arm >/dev/null 2>&1; handoff_arm >/dev/null 2>&1
   chk "after three passes the no-PR ref is owed once (rewritten, never appended)" 0 test "$(grep -c "handoff-no-pr refs/heads/handoff/topic-b" "$LV")" = 1
   chk "the event log carries no level line" 1 grep -q "handoff-no-pr" "$LOG"
+  # one obligation per topic: a no-PR topic's body ref rides its code ref's line (32 of 37 lines were noise, 20 of them body twins)
+  git -C "$t/o.git" update-ref refs/heads/handoff-body/topic-b "$OB"; handoff_arm >/dev/null 2>&1
+  chk "a no-PR topic with a body ref is one line, its code ref's, naming the body" 0 test "$(grep -c "handoff-no-pr refs/heads/handoff.*/topic-b " "$LV")-$(grep -c "handoff-no-pr refs/heads/handoff/topic-b $OB ct=[0-9]* body=$OB" "$LV")" = 1-1
+  git -C "$t/o.git" update-ref -d refs/heads/handoff-body/topic-b
+  # RCA 5.1: a merged PR of the topic closes a handoff committed by its merge; a re-handoff after it stays owed
+  printf 'fix/topic-b-pr\t2099-01-01T00:00:00Z\n' > "$t/merged.tsv"; handoff_arm >/dev/null 2>&1
+  chk "a handoff its topic's merged PR delivered (committed by the merge) is not owed" 1 grep -q "handoff-no-pr refs/heads/handoff/topic-b " "$LV"
+  failm=$t/failm.sh; printf '#!/bin/sh\nexit 1\n' > "$failm"; chmod +x "$failm"
+  HPO_RELAY_MERGED=$failm handoff_arm >/dev/null 2>&1
+  chk "an unlisted merged set leaves the level as it was, never re-owing what a merge closed" 1 grep -q "handoff-no-pr refs/heads/handoff/topic-b " "$LV"
+  printf 'fix/topic-b-pr\t2001-01-01T00:00:00Z\n' > "$t/merged.tsv"; handoff_arm >/dev/null 2>&1
+  chk "null control: a handoff committed after its topic's merge stays owed" 0 grep -q "handoff-no-pr refs/heads/handoff/topic-b $OB " "$LV"
+  : > "$t/merged.tsv"
   git -C "$t/o.git" update-ref refs/heads/handoff/topic-z "$PRH"; handoff_arm >/dev/null 2>&1
   chk "a no-PR handoff ref a live fix/ head carries is not owed (the ledger's ancestry close)" 1 grep -q "handoff/topic-z" "$LV"
   git -C "$t/o.git" update-ref -d refs/heads/handoff/topic-z
diff --git a/tools/audit/seat/ledger.py b/tools/audit/seat/ledger.py
index 5758febfa..8828ee4b6 100644
--- a/tools/audit/seat/ledger.py
+++ b/tools/audit/seat/ledger.py
@@ -8,6 +8,7 @@
     python3 -I tools/audit/seat/ledger.py [--log FILE] attempt <ref> <sha40> <outcome>
     python3 -I tools/audit/seat/ledger.py [--log FILE] level <hrefs-file> <topics-file>
     python3 -I tools/audit/seat/ledger.py [--log FILE] board
+    python3 -I tools/audit/seat/ledger.py landed [--no-ancestry] [--no-content] <main> [<head>...] < tips
     python3 -I tools/audit/seat/ledger.py --self-test
 
 WHY. An obligation was a level read out of append-only history: the relay
@@ -50,14 +51,24 @@ An obligation of no kind in KINDS is refused, never stored.
 LEVEL (`level`): the relay's handoff level for one pass. Each `handoff/<t>`
 and `handoff-body/<t>` ref listed is owed (`handoff-no-pr`) unless: a state
 ref by name (`audit-r<N>-plan`, `audit-r<N>-roster`); <t> has an open pull
-request (the topics file); the ref is disposed at its sha; or main already
-carries the change -- the code tip is inside main or a live `fix/*` head, or
-every line its uncovered commits add is on main's copy of that file and every
-line they remove is gone (`covered`: a hunk re-applied by another pull request
-into a file main has since changed, which a byte-identical test cannot see).
-A body ref follows its code ref there. Each owed line carries `ct=<epoch>`
+request (the topics file's bare lines); a pull request of <t> merged at or
+after the tip's commit time (its `<t> merged=<utc>` lines: a squash or an App
+push rewrote the commits, and the merge's own record moved the files on, so
+no content test can see it; a re-handoff committed later stays owed); the ref
+is disposed at its sha; or main already
+carries the change, by `landed`: the code tip is inside main or a live `fix/*`
+head, or outside them only by clean merges; its patch applies to main reversed
+and not forward; or `covered` finds every file it touches on main (a hunk
+re-applied by another pull request into a file main has since changed, which
+a byte-identical test cannot see). A body ref follows its code ref: one line
+per topic, the code ref's, naming the body as `body=<sha>`; only a body ref
+with no code ref is a line of its own. Each owed line carries `ct=<epoch>`
 (the tip's commit time) and the topic's last opener attempt at that tip.
 
+LANDED (`landed`): the same classifier for bus.sh orphans, one owner. Main
+and the live heads are arguments, the tips stdin; one `<tip> <why>` line each,
+`-` when nothing carries it. --no-ancestry and --no-content drop an arm.
+
 AGING. `escalate` turns those lines into a queue: DISPATCH at the first
 threshold, oldest first, naming the roster group and the repair; an OWNER FLAG
 at the second. The thresholds are policy (tvofi's); the switch is
@@ -358,13 +369,41 @@ def attempts(rows: list) -> dict:
 
 # ------------------------------------------------------------------- level
 def covered(git, main: str, tip: str) -> bool:
-    """Every line tip's uncovered commits add is on main's copy of its file,
-    and every line they remove is gone from it: main carries the change."""
+    """Main carries every file tip's uncovered commits touch: the same bytes at
+    the path; an added file's bytes elsewhere (a recovery moved it); a deletion
+    main already made; or every line they add on main's copy and every line
+    they remove gone from it (a hunk re-applied into a file main has changed)."""
     rc, mb = git(["merge-base", main, tip])
     if rc:
         return False
-    rc, diff = git(["diff", "--no-color", "--no-renames", "-U0", mb.strip(), tip])
-    if rc or not diff.strip():
+    mb = mb.strip()
+    rc, names = git(["diff", "--name-status", "--no-renames", mb, tip])
+    if rc or not names.strip():
+        return False
+    blobs, by_line = None, []
+    for row in names.splitlines():
+        st, path = row.split("\t", 1)
+        rc_t, b_tip = git(["rev-parse", f"{tip}:{path}"])
+        rc_m, b_main = git(["rev-parse", f"{main}:{path}"])
+        if st == "D":
+            if rc_m == 0:
+                return False
+        elif rc_t:
+            return False
+        elif rc_m == 0 and b_main == b_tip:
+            continue
+        elif rc_m:
+            if blobs is None:
+                rc, out = git(["ls-tree", "-r", main])
+                blobs = {l.split()[2] for l in out.splitlines()} if rc == 0 else set()
+            if b_tip.strip() not in blobs:
+                return False
+        else:
+            by_line.append(path)
+    if not by_line:
+        return True
+    rc, diff = git(["diff", "--no-color", "--no-renames", "-U0", mb, tip, "--", *by_line])
+    if rc:
         return False
     files: dict[str, tuple[set, set]] = {}
     path = None
@@ -372,9 +411,7 @@ def covered(git, main: str, tip: str) -> bool:
         if l.startswith("Binary files "):
             return False
         if l.startswith("+++ "):
-            path = l[6:] if l.startswith("+++ b/") else None
-            if path is None:
-                return False  # a deletion: covered only by a byte-identical arm, not this one
+            path = l[6:]
             files.setdefault(path, (set(), set()))
         elif path and l.startswith("+") and l[1:].strip():
             files[path][0].add(l[1:].strip())
@@ -387,24 +424,78 @@ def covered(git, main: str, tip: str) -> bool:
         have = {l.strip() for l in text.splitlines()}
         if not add <= have or rem & have:
             return False
-    return bool(files)
+    return True
 
 
-def handoff_level(hrefs: list, topics: set, git, disp: dict, att: dict, now: str):
-    """(level lines, Counter of why each listed ref is or is not owed)."""
+def reverse_applies(git, main: str, tip: str) -> bool:
+    """Tip's patch from its merge base with main applies to main reversed and
+    not forward: main holds the change, context and all (the brief's test),
+    checked in a throwaway index, never the work tree."""
+    rc, mb = git(["merge-base", main, tip])
+    if rc:
+        return False
+    with tempfile.TemporaryDirectory() as d:
+        patch, env = os.path.join(d, "p.diff"), {"GIT_INDEX_FILE": os.path.join(d, "index")}
+        rc, diff = git(["diff", "--binary", "--full-index", "--no-renames", mb.strip(), tip])
+        if rc or not diff.strip():
+            return False
+        Path(patch).write_text(diff if diff.endswith("\n") else diff + "\n")
+        if git(["read-tree", main], env)[0]:
+            return False
+        return (git(["apply", "--cached", "--check", "--reverse", patch], env)[0] == 0
+                and git(["apply", "--cached", "--check", patch], env)[0] != 0)
+
+
+ANCESTRY_WHY, CONTENT_WHY = ("ancestor", "merges-only"), ("reverse-apply", "content")
+
+
+def landed(git, main: str, tip: str, heads=(), ancestry: bool = True, content: bool = True) -> "str | None":
+    """Why main, or a live fix/* head, already carries tip; None when nothing
+    does. The one classifier of a handoff's landing: `level` folds the relay's
+    handoff-no-pr through it and bus.sh orphans asks it (`landed` below).
+      ancestor       every commit of tip is inside main or a head
+      merges-only    the only commits outside them are merges whose combined
+                     diff is empty (no resolution of their own)
+      reverse-apply  reverse_applies: the patch is on main, context and all
+      content        covered: the change is on main under another commit"""
+    if ancestry:
+        rc, out = git(["rev-list", "--count", tip, "--not", main, *heads])
+        if rc == 0 and out.strip() == "0":
+            return "ancestor"
+        rc, out = git(["rev-list", "--no-merges", "--count", tip, "--not", main, *heads])
+        if rc == 0 and out.strip() == "0":
+            rc, merges = git(["rev-list", "--merges", tip, "--not", main, *heads])
+            if rc == 0 and all((lambda r: r[0] == 0 and not r[1].strip())(
+                    git(["diff-tree", "--cc", "--no-commit-id", "-p", m])) for m in merges.split()):
+                return "merges-only"
+    if content:
+        if reverse_applies(git, main, tip):
+            return "reverse-apply"
+        if covered(git, main, tip):
+            return "content"
+    return None
+
+
+def handoff_level(hrefs: list, topics: set, git, disp: dict, att: dict, now: str, merged: "dict | None" = None):
+    """(level lines, Counter of why each listed ref is or is not owed). merged:
+    {topic: epoch} of merged pull requests, which close a tip committed by then."""
+    merged = merged or {}
     rc, main = git(["rev-parse", "--verify", f"{NS}/main"])
     if rc:
         raise Unreadable("no main in the ledger's fetched namespace")
     main = main.strip()
+    rc, out = git(["for-each-ref", "--format=%(objectname)", f"{NS}/fix/"])
+    if rc:
+        raise Unreadable("the fetched fix/* heads could not be listed")
+    heads = sorted(set(out.split()))
     code = {topic_of(r): s for s, r in hrefs if r.startswith("refs/heads/handoff/")}
+    body = {topic_of(r): s for s, r in hrefs if r.startswith("refs/heads/handoff-body/")}
     carried: dict[str, bool] = {}
 
     def is_carried(t: str) -> bool:
         if t not in carried:
             sha = code.get(t)
-            rc, out = git(["for-each-ref", "--contains", sha, "--format=%(refname)", f"{NS}/main", f"{NS}/fix/"]) \
-                if sha else (1, "")
-            carried[t] = bool(sha) and ((rc == 0 and bool(out.strip())) or covered(git, main, sha))
+            carried[t] = bool(sha) and landed(git, main, sha, heads) is not None
         return carried[t]
 
     ct = {}
@@ -417,20 +508,41 @@ def handoff_level(hrefs: list, topics: set, git, disp: dict, att: dict, now: str
         t = topic_of(ref)
         if STATE_REF.match(t):
             why["state-ref"] += 1
+        elif t in code and not ref.startswith("refs/heads/handoff/"):
+            why["body-follows-code"] += 1  # one obligation per topic: its code ref's line stands for both
         elif t in topics:
             why["open-pr"] += 1
         elif disp.get(ref, ("",))[0] == sha:
             why["disposed"] += 1
+        elif t in merged and ct.get(code.get(t, sha), "").isdigit() and int(ct[code.get(t, sha)]) <= merged[t]:
+            why["merged-pr"] += 1  # delivered by that merge; a re-handoff committed after it stays owed
         elif is_carried(t):
             why["carried"] += 1
         else:
             why["owed"] += 1
             a = att.get(f"refs/heads/handoff/{t}")
             tail = f" attempt={a[1]},{a[2].replace(' ', '_')}" if a and a[0] == code.get(t) else ""
-            lines.append(f"OWED {now} handoff-no-pr {ref} {sha} ct={ct.get(sha, '?')}{tail}")
+            bref = f" body={body[t]}" if ref.startswith("refs/heads/handoff/") and t in body else ""
+            lines.append(f"OWED {now} handoff-no-pr {ref} {sha} ct={ct.get(sha, '?')}{bref}{tail}")
     return lines, why
 
 
+def read_topics(text: str) -> "tuple[set, dict]":
+    """The level's topics file: open-PR topics, and {topic: epoch} of each
+    topic's latest merged pull request (a reused topic can merge twice)."""
+    topics, merged = set(), {}
+    for l in text.splitlines():
+        f = l.split()
+        if len(f) == 2 and f[1].startswith("merged="):
+            when = datetime.datetime.fromisoformat(f[1][7:].replace("Z", "+00:00")).timestamp()
+            merged[f[0]] = max(merged.get(f[0], 0), int(when))
+        elif len(f) == 1:
+            topics.add(f[0])
+        elif f:
+            raise Refused(f"topics: '{l}' is neither '<topic>' nor '<topic> merged=<utc>'")
+    return topics, merged
+
+
 def fetch_world(git) -> None:
     rc, out = git(["fetch", "-q", "--prune", "origin", f"+refs/heads/main:{NS}/main",
                    f"+refs/heads/handoff/*:{NS}/handoff/*", f"+refs/heads/handoff-body/*:{NS}/handoff-body/*",
@@ -473,7 +585,8 @@ def escalate(level_rows: list, now: datetime.datetime, aging, group_of) -> list[
         if not kv.get("ct", "").isdigit():
             continue
         age = (now.timestamp() - int(kv["ct"])) / 3600  # ahead of the clock: < 0, below any threshold
-        repair = "opener" if len(refs) == 2 else "no code ref" if "code" not in refs else "no body ref"
+        repair = ("no code ref" if "code" not in refs
+                  else "opener" if "body" in refs or "body" in refs["code"][2] else "no body ref")
         queue.append((age, t, ref, sha, repair, kv.get("attempt")))
     queue.sort(key=lambda q: -q[0])
     out = [f"DISPATCH: {group_of(t) or '?'} {ref} {sha[:12]} {repair} ({age:.1f}h"
@@ -532,8 +645,9 @@ def app_approve_carries(cwd: str, main: str, env=None):
 
 
 # --------------------------------------------------------------------- CLI
-def _git_cwd(argv: list) -> "tuple[int, str]":
-    r = subprocess.run(["git", *argv], capture_output=True, text=True)
+def _git_cwd(argv: list, env: "dict | None" = None) -> "tuple[int, str]":
+    r = subprocess.run(["git", *argv], capture_output=True, text=True,
+                       env={**os.environ, **env} if env else None)
     return r.returncode, r.stdout + (r.stderr if r.returncode else "")
 
 
@@ -562,13 +676,25 @@ def main(argv: list) -> int:
             return 0
         if cmd == "level" and len(args) == 2:
             hrefs = [tuple(l.split()[:2]) for l in Path(args[0]).read_text().splitlines() if len(l.split()) >= 2]
-            topics = {l.strip() for l in Path(args[1]).read_text().splitlines() if l.strip()}
+            topics, merged = read_topics(Path(args[1]).read_text())
             fetch_world(_git_cwd)
             lines, why = handoff_level(hrefs, topics, _git_cwd, dispositions(home),
-                                       attempts(events(home, log)), utc())
+                                       attempts(events(home, log)), utc(), merged)
             print("".join(l + "\n" for l in lines), end="")
             print("ledger: level " + " ".join(f"{k}={v}" for k, v in sorted(why.items())), file=sys.stderr)
             return 1 if lines else 0
+        if cmd == "landed" and args:
+            flags = {a for a in args if a in ("--no-ancestry", "--no-content")}
+            shas = [a for a in args if a not in flags]
+            if not shas or not all(is_sha(a) for a in shas):
+                raise Refused("landed takes <main> [<head>...] as 40-hex shas, the tips on stdin")
+            for tip in sys.stdin.read().split():
+                if not is_sha(tip):
+                    raise Refused(f"'{tip}' is no 40-hex tip")
+                why = landed(_git_cwd, shas[0], tip, shas[1:], "--no-ancestry" not in flags,
+                             "--no-content" not in flags)
+                print(f"{tip} {why or '-'}")
+            return 0
         if cmd == "board" and not args:
             open_, closed = fold(events(home, log))
             for ob in open_:
@@ -793,25 +919,118 @@ def self_test() -> int:
           f"{unc}:refs/heads/handoff-body/unc", f"{anc}:refs/heads/handoff/anc",
           f"{unc}:refs/heads/handoff/audit-r10-roster", f"{unc}:refs/heads/handoff/open",
           f"{unc}:refs/heads/handoff/disp")
-        gw = lambda argv: (lambda r: (r.returncode, r.stdout + (r.stderr if r.returncode else "")))(
-            subprocess.run(["git", "-C", str(w), *argv], capture_output=True, text=True, env=env))
+        gw = lambda argv, extra=None: (lambda r: (r.returncode, r.stdout + (r.stderr if r.returncode else "")))(
+            subprocess.run(["git", "-C", str(w), *argv], capture_output=True, text=True, env={**env, **(extra or {})}))
         fetch_world(gw)
         mn = g("rev-parse", "main")
         check("covered: a hunk main carries beside a later change (the ecaf178c shape)", covered(gw, mn, cov))
         check("null control: a hunk adding a line main lacks is not covered", not covered(gw, mn, unc))
+        # ---- landed: the one classifier bus.sh orphans shares
+        g("checkout", "-qb", "work4", cov + "~1")
+        put("g.txt", "x\nfi\ny\nfi\np\nq\nr\ns\nt\n", "g base")
+        gb = g("rev-parse", "HEAD")
+        rv = put("g.txt", "x\nfi\ny\np\nq\nr\ns\nt\n", "drop the second fi")
+        g("checkout", "-qb", "work5", gb)
+        put("g.txt", "x\nfi\ny\np\nq\nr\ns\nT\n", "main lands it beside a change")
+        rvm = g("rev-parse", "HEAD")
+        g("checkout", "-qb", "work6", gb)
+        rvn = put("g.txt", "x\ny\nfi\np\nq\nr\ns\nt\n", "drop the first fi")
+        check("landed: a patch main holds whose removed line main keeps elsewhere is reverse-apply, not content",
+              landed(gw, rvm, rv) == "reverse-apply" and not covered(gw, rvm, rv))
+        check("null control: a patch main does not hold lands nowhere", landed(gw, rvm, rvn) is None)
+        g("checkout", "-qb", "work13", gb)
+        body_ = ["h1", "h2", "h3", "h4", "c1", "c2", "c3", "fi", "c4", "c5", "c6", "t1", "t2", "t3", "t4"]
+        put("d.txt", "\n".join(body_) + "\n", "d base")
+        db = g("rev-parse", "HEAD")
+        dt = put("d.txt", "\n".join(x for x in body_ if x != "fi") + "\n", "drop fi")
+        g("checkout", "-qb", "work14", db)
+        dm = put("d.txt", "\n".join([x for x in body_ if x != "fi"] + body_[4:11] + ["e1", "e2", "e3"]) + "\n",
+                 "main holds the patched region and an unpatched copy")
+        check("null control: a patch that applies both ways (an unpatched copy remains) is not landed",
+              landed(gw, dm, dt) is None and not reverse_applies(gw, dm, dt))
+        check("landed: a tip inside main reads ancestor, not merges-only", landed(gw, mn, anc) == "ancestor")
+        check("landed: the re-applied hunk is content (reverse-apply cannot: forward applies too)",
+              landed(gw, mn, cov) == "content" and not reverse_applies(gw, mn, cov))
+        g("checkout", "-qb", "work7", gb)
+        mv = put("moved.txt", "same bytes\n", "add a file")
+        g("checkout", "-qb", "work8", gb)
+        (w / "sub").mkdir()
+        mvm = put("sub/moved.txt", "same bytes\n", "main holds it at another path")
+        check("covered: an added file whose bytes main holds at another path is carried (a moved file)",
+              covered(gw, mvm, mv))
+        check("null control: the same add with other bytes is not", not covered(gw, mvm, put("x.txt", "other\n", "x")))
+        g("checkout", "-qb", "work15", gb)
+        g("rm", "-q", "g.txt")
+        tipd = put("y.txt", "same bytes\n", "delete g.txt, add bytes main holds elsewhere")
+        check("null control: a tip deleting a file main still holds is not covered, beside a carried add",
+              not covered(gw, mvm, tipd) and landed(gw, mvm, tipd) is None)
+        g("checkout", "-qb", "work16", gb)
+        g("rm", "-q", "g.txt")
+        (w / "sub").mkdir(exist_ok=True)
+        mdel = put("sub/moved.txt", "same bytes\n", "main deletes g.txt too and holds the add elsewhere")
+        check("covered: a deletion main already made is carried", covered(gw, mdel, tipd))
+        g("checkout", "-qb", "work17", gb)
+        sbm = put("g.txt", "x\nfi\ny\np\nq\nr\ns\nt\n", "main holds rv's bytes under its own commit")
+        check("covered: the same bytes at the path are carried, a removed line kept elsewhere notwithstanding",
+              covered(gw, sbm, rv))
+        g("checkout", "-qb", "work9", mvm)
+        m_a = put("ma.txt", "A\n", "main side")
+        g("checkout", "-qb", "work10", mvm)
+        f_b = put("fb.txt", "B\n", "fix side")
+        g("merge", "-q", "--no-edit", m_a)
+        tipm = g("rev-parse", "HEAD")
+        g("checkout", "-qb", "work11", f_b)
+        fixh = put("fc.txt", "C\n", "the fix head carries both parents' work")
+        g("merge", "-q", "--no-edit", m_a)
+        fixh = g("rev-parse", "HEAD")
+        check("landed: a merge tip whose parents main and a fix head carry is merges-only",
+              landed(gw, m_a, tipm, [fixh]) == "merges-only")
+        check("null control: without that fix head the same tip is not ancestry-carried",
+              landed(gw, m_a, tipm, [], content=False) is None)
+        g("checkout", "-qb", "work12", f_b)
+        g("merge", "-q", "--no-commit", m_a)
+        put("evil.txt", "E\n", "a merge with a resolution of its own")
+        check("null control: a merge carrying its own resolution is not merges-only",
+              landed(gw, m_a, g("rev-parse", "HEAD"), [fixh], content=False) is None)
+        g("checkout", "-q", "main")
         hr = [tuple(l.split()) for l in g("ls-remote", "origin", "refs/heads/handoff/*",
                                            "refs/heads/handoff-body/*").splitlines()]
         att = {"refs/heads/handoff/unc": (unc, "2026-10-20T11:50:33Z", "rc=143")}
         lines, why = handoff_level(hr, {"open"}, gw, {"refs/heads/handoff/disp": (unc, "t", "h")}, att, "NOW")
         owed = sorted(l.split()[3] for l in lines)
-        check("the level owes exactly the uncovered topic's two refs and the body-only ref",
-              owed == ["refs/heads/handoff-body/bodyonly", "refs/heads/handoff-body/unc", "refs/heads/handoff/unc"])
-        check("and names each close: state ref, open PR, disposed, carried (ancestry and content)",
-              dict(why) == {"owed": 3, "state-ref": 1, "open-pr": 1, "disposed": 1, "carried": 2})
+        check("the level owes the uncovered topic once, at its code ref, and the body-only ref",
+              owed == ["refs/heads/handoff-body/bodyonly", "refs/heads/handoff/unc"])
+        check("the code ref's line names its body ref, which is no line of its own (one obligation per topic)",
+              any(l.split()[3] == "refs/heads/handoff/unc" and f" body={unc}" in l for l in lines))
+        check("and names each close: state ref, open PR, disposed, carried (ancestry and content), body",
+              dict(why) == {"owed": 2, "state-ref": 1, "open-pr": 1, "disposed": 1, "carried": 2,
+                            "body-follows-code": 1})
+        l2, w2 = handoff_level(hr, {"open"}, gw, {}, att, "NOW", {"unc": 4102444800})
+        check("a topic whose PR merged after its tip's commit is closed by the merge (RCA 5.1)",
+              not any("/unc " in l for l in l2) and w2["merged-pr"] == 1)
+        l2, w2 = handoff_level(hr, {"open"}, gw, {}, att, "NOW", {"unc": int(g("log", "-1", "--format=%ct", unc))})
+        check("a merge in the tip's own commit second closes it (at or before, not strictly before)",
+              not any("/unc " in l for l in l2) and w2["merged-pr"] == 1)
+        tp, mg = read_topics("open\nt merged=2026-01-02T00:00:00Z\nt merged=2026-01-01T00:00:00Z\n")
+        check("the topics reader keeps a topic's latest merge, whatever the listing order",
+              tp == {"open"} and mg == {"t": 1767312000})
+        l2, w2 = handoff_level(hr, {"open"}, gw, {}, att, "NOW", {"unc": 1})
+        check("null control: a tip committed after its topic's merge stays owed",
+              any(" refs/heads/handoff/unc " in l for l in l2) and "merged-pr" not in w2)
         check("every owed line, an orphan body ref's included, carries its tip's commit time",
               all(" ct=" in l and not l.split("ct=")[1].startswith("?") for l in lines))
         check("the code ref's topic carries the opener attempt at that tip",
-              sum("attempt=2026-10-20T11:50:33Z,rc=143" in l for l in lines) == 2)
+              sum("attempt=2026-10-20T11:50:33Z,rc=143" in l for l in lines) == 1)
+        bo_t = g("ls-remote", "origin", "refs/heads/handoff-body/bodyonly").split()[0]
+        check("escalate: a code line naming its body is an opener; a body-only line has no code ref",
+              sorted(re.sub(r"^DISPATCH: G (\S+) \S+ (.*) \(.*$", r"\1 \2", q) for q in escalate(
+                  [f"OWED x handoff-no-pr refs/heads/handoff/unc {unc} ct=1 body={unc}",
+                   f"OWED x handoff-no-pr refs/heads/handoff/nob {unc} ct=1",
+                   f"OWED x handoff-no-pr refs/heads/handoff-body/bodyonly {bo_t} ct=1"],
+                  datetime.datetime.now(datetime.timezone.utc), (1.0, 1e9), lambda t: "G")
+                  if q.startswith("DISPATCH")) == ["refs/heads/handoff-body/bodyonly no code ref",
+                                                    "refs/heads/handoff/nob no body ref",
+                                                    "refs/heads/handoff/unc opener"])
         r = subprocess.run([sys.executable, "-I", __file__, "--log", str(e / "cloud-relay.log"), "board"],
                            capture_output=True, text=True)
         check("board: obligations exist is rc 1 with its summary line (a finding, not a failure)",
@@ -828,7 +1047,7 @@ def self_test() -> int:
         r = subprocess.run([sys.executable, "-I", __file__, "--log", str(D / "lv" / "l"), "level",
                             str(D / "hr"), str(D / "tp")], capture_output=True, text=True, cwd=w, env=env)
         check("level CLI: owed lines on stdout, rc 1, the counts on stderr",
-              r.returncode == 1 and r.stdout.count("handoff-no-pr") == 4 and "owed=4" in r.stderr)
+              r.returncode == 1 and r.stdout.count("handoff-no-pr") == 3 and "owed=3" in r.stderr)
         g("remote", "set-url", "origin", str(D / "absent.git"))
         r = subprocess.run([sys.executable, "-I", __file__, "--log", str(D / "lv" / "l"), "level",
                             str(D / "hr"), str(D / "tp")], capture_output=True, text=True, cwd=w, env=env)
diff --git a/tools/audit/seat/r10_ledger_mutants.py b/tools/audit/seat/r10_ledger_mutants.py
index 6c614a8b0..331858f75 100644
--- a/tools/audit/seat/r10_ledger_mutants.py
+++ b/tools/audit/seat/r10_ledger_mutants.py
@@ -26,9 +26,10 @@ import sys
 from pathlib import Path
 
 ROOT = Path(__file__).resolve().parents[3]
+BUS = "tools/audit/seat/bus.sh"
 LEDGER, RELAY, TICK, OPENER = ("tools/audit/seat/ledger.py", "tools/audit/seat/cloud_relay.sh",
                                "tools/audit/seat/orchestrator_tick.py", "tools/audit/seat/open_pr.sh")
-OWNER = {LEDGER: LEDGER, OPENER: LEDGER, RELAY: RELAY, TICK: TICK}
+OWNER = {LEDGER: LEDGER, OPENER: LEDGER, RELAY: RELAY, TICK: TICK, BUS: BUS}
 PLANTS = {
     # the ledger: event closers, the level's closers, aging, refusals, stores
     "L1_readback_no_close": (LEDGER, '                how = "read-back"', "                how = None"),
@@ -36,10 +37,33 @@ PLANTS = {
     "L3_any_verdict_posts": (LEDGER, '(text in lines if kind == "verdict-unposted"',
                              '(bool(lines) if kind == "verdict-unposted"'),
     "L4_added_lines_unchecked": (LEDGER, "if not add <= have or rem & have:", "if rem & have:"),
-    "L5_no_ancestry_close": (LEDGER, "carried[t] = bool(sha) and ((rc == 0 and bool(out.strip())) or covered(git, main, sha))",
-                             "carried[t] = bool(sha) and covered(git, main, sha)"),
-    "L6_no_content_close": (LEDGER, "carried[t] = bool(sha) and ((rc == 0 and bool(out.strip())) or covered(git, main, sha))",
-                            "carried[t] = bool(sha) and (rc == 0 and bool(out.strip()))"),
+    "L5_no_ancestry_close": (LEDGER, '''        if rc == 0 and out.strip() == "0":
+            return "ancestor"''', '''        if False:
+            return "ancestor"'''),
+    "L6_no_content_close": (LEDGER, '        if covered(git, main, tip):\n            return "content"',
+                            '        if False:\n            return "content"'),
+    "L19_no_reverse_apply": (LEDGER, '        if reverse_applies(git, main, tip):', '        if False:'),
+    "L20_forward_not_refused": (LEDGER, '                and git(["apply", "--cached", "--check", patch], env)[0] != 0)', '                and True)'),
+    "L21_merges_unchecked": (LEDGER, '            rc, merges = git(["rev-list", "--merges", tip, "--not", main, *heads])\n            if rc == 0 and all(',
+                             '            rc, merges = git(["rev-list", "--merges", tip, "--not", main, *heads])\n            if rc == 0 and True or all('),
+    "L22_merges_with_nonmerges": (LEDGER, '["rev-list", "--no-merges", "--count", tip,', '["rev-list", "--count", tip,'),
+    "L23_moved_add_unchecked": (LEDGER, "            if b_tip.strip() not in blobs:\n                return False",
+                                "            if False:\n                return False"),
+    "L24_body_own_line": (LEDGER, '        elif t in code and not ref.startswith("refs/heads/handoff/"):', '        elif False:'),
+    "L25_merged_ignored": (LEDGER, "        elif t in merged and ct.get(", "        elif False and ct.get("),
+    "L26_merged_any_time": (LEDGER, "and int(ct[code.get(t, sha)]) <= merged[t]:", ":"),
+    "L27_deletion_unguarded": (LEDGER, '        if st == "D":\n            if rc_m == 0:', '        if st == "D":\n            if False:'),
+    "L28_deletion_always_refused": (LEDGER, '        if st == "D":\n            if rc_m == 0:', '        if st == "D":\n            if True:'),
+    "L29_same_blob_arm_off": (LEDGER, "        elif rc_m == 0 and b_main == b_tip:\n            continue",
+                              "        elif False:\n            continue"),
+    "L30_merged_strictly_before": (LEDGER, "and int(ct[code.get(t, sha)]) <= merged[t]:", "and int(ct[code.get(t, sha)]) < merged[t]:"),
+    "L31_merged_last_listed": (LEDGER, "merged[f[0]] = max(merged.get(f[0], 0), int(when))", "merged[f[0]] = int(when)"),
+    "R6_merged_unread_clears": (RELAY, '"$state/cloud-merged.$$" \\\n    || { echo "cloud_relay: could not list merged PRs',
+                                '"$state/cloud-merged.$$" \\\n    || true || { echo "cloud_relay: could not list merged PRs'),
+    "B1_orphans_merges_stranded": (BUS, "    case $why in ancestor|merges-only) anc=", "    case $why in ancestor) anc="),
+    "B3_orphans_classifier_unchecked": (BUS, '    || die "orphans: ledger.py landed could not classify',
+                                        '    || true || die "orphans: ledger.py landed could not classify'),
+    "B2_orphans_no_content": (BUS, '    if [ "$why" = reverse-apply ] || [ "$why" = content ]; then', '    if [ "$why" = content ]; then'),
     "L7_no_threshold": (LEDGER, "           if age >= aging[0]]", "           if True]"),
     "L8_one_tip_blanks_all": (LEDGER, '        if rc == 0 and out.strip().isdigit():\n            ct[sha]',
                               '        if rc == 0 and out.strip().isdigit() and False:\n            ct[sha]'),

