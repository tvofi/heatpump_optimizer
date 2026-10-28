# Review packet #2933
head: 172afa85d2bc2f68b402217981f22cfb26e86b56
base: b6f6ceca4f0323b24171c45a2a2372ba2e2cbaaa

Start here (fix-review.md). Re-read the live check state before a verdict: the digest is as read at render.

## Gate digest: pending
arm id=123094962283 skipped
cancel-superseded id=123094959135 queued
prelude id=123094959249 queued
refresh id=123094958843 queued

## Refusals
hot-file: #2920 holds an unboarded merge verdict and shares tools/audit/seat/cloud_relay.sh

## Advisories
hot-file: HPO_BUS_TRAIN_STATE is unset, so every merge verdict reads unboarded

## carry_audit at the head
NOTE stale tree: 172afa85d2bc2f68b402217981f22cfb26e86b56 lacks origin/main b0b2d7697f8c5baaef2c082d9bf3242b57249e68; roster read at origin/main
NOTE body item 8779c3f0: dismissed:one command's cost on an out-of-tree brief; `--help` names the arm.
CARRY-AUDIT: 1 finding item(s): 1 routed, 0 unrouted, 0 bad destination(s)

## figure_lint at the head
ok         python3 tools/audit/seat/review_carry.py 253dc4867cf39f2aa9875f5f2540c5b67b7c1018 d08647f0513a5a568b5ac917748df02adf9fded6 --main 53c4b9cb0de45bbfadb19ea6adbe15dd7d7034e1
             `tools/audit/seat/review_carry.py` is in the tree at this head
  ok         python3 tools/audit/seat/review_carry.py fccb883716ce7f8677ea64a2107971baa5381ea9 9f424cf742eee1c00ab13a75a926874f72470eab
             `tools/audit/seat/review_carry.py` is in the tree at this head
  ok         bash tools/pr/app_approve.sh --carry 253dc4867cf39f2aa9875f5f2540c5b67b7c1018 d08647f0513a5a568b5ac917748df02adf9fded6 53c4b9cb0de45bbfadb19ea6adbe15dd7d7034e1
             `tools/pr/app_approve.sh` is in the tree at this head
  unverified git log --merges --first-parent -n 200 --format=%H origin/main | while read c; do set -- $(git rev-list --parents -n 1 $c); shift; [ $# -eq 2 ] || continue; for f in $(git show origin/main:.gitattributes | awk '$2=="merge=claimnotes"{print $1}'); do got=$(git show $c:$f 2>/dev/null | awk NF | sort -u); want=$({ git show $1:$f 2>/dev/null; git show $2:$f 2>/dev/null; } | awk NF | sort -u); [ "$got" = "$want" ] && echo pure || { echo other; comm -13 <(printf '%s\n' "$want") <(printf '%s\n' "$got") | wc -l | sed 's/^/added /'; }; done; done | sort | uniq -c
             `git log` resolves; its flags are not checked -- git prints a man page rather than a flag list, and a list carried in this file would rot into false refusals
  ok         bash tools/audit/seat/cloud_relay.sh --self-test
             `tools/audit/seat/cloud_relay.sh` is in the tree at this head
  ok         bash tools/audit/seat/bus.sh --self-test
             `tools/audit/seat/bus.sh` is in the tree at this head
  ok         python3 tools/audit/seat/review_carry.py --self-test
             `tools/audit/seat/review_carry.py` is in the tree at this head
  ok         bash tools/pr/app_approve.sh --self-test
             `tools/pr/app_approve.sh` is in the tree at this head
  ok         node tools/policy/policy_lint.mjs --budgets
             `tools/policy/policy_lint.mjs` is in the tree at this head
  ok         node tools/policy/policy_lint.mjs
             `tools/policy/policy_lint.mjs` is in the tree at this head
  ok         python3 tests/closure.py select --diff $(git merge-base origin/main HEAD)
             `tests/closure.py` is in the tree at this head
  ok         tests/entities.py
             `tests/entities.py` is in the tree at this head
  ok         tests/harness_headers.py
             `tests/harness_headers.py` is in the tree at this head
  ok         python3 tests/structure.py
             `tests/structure.py` is in the tree at this head

FIGURES: 13 resolved, 1 not verified, 0 refused

## Finder's harness: none named
### at the base
not run
### at the head
not run

## Mutation-ledger diff
none

## Three-dot diff
diff --git a/.github/workflows/governance.yml b/.github/workflows/governance.yml
index 59f45b2d4..ac257e613 100644
--- a/.github/workflows/governance.yml
+++ b/.github/workflows/governance.yml
@@ -731,6 +731,13 @@ jobs:
           python3 -I tools/audit/seat/review_packet.py --self-test | tee "$RUNNER_TEMP/review-packet-self-test.txt"
           grep -Eq '^review_packet self-test: [1-9][0-9]* checks, 0 failed$' "$RUNNER_TEMP/review-packet-self-test.txt"
 
+      - name: Show the review carry deciding its own fixtures
+        if: ${{ !cancelled() }}
+        run: |
+          set -o pipefail
+          python3 -I tools/audit/seat/review_carry.py --self-test | tee "$RUNNER_TEMP/review-carry-self-test.txt"
+          grep -Eq '^review_carry self-test: [1-9][0-9]* checks, 0 failed$' "$RUNNER_TEMP/review-carry-self-test.txt"
+
       - name: Show the roster editor refusing its own fixtures
         if: ${{ !cancelled() }}
         run: |
diff --git a/dev/governance/roles/fix-review.md b/dev/governance/roles/fix-review.md
index 0c06d901b..52ccc8949 100644
--- a/dev/governance/roles/fix-review.md
+++ b/dev/governance/roles/fix-review.md
@@ -4,7 +4,7 @@ You review one fix PR adversarially, fresh, from a worktree at
 the PR's head SHA. You check that the numbers are real, not that the code looks right.
 **Its copy of this contract is frozen with the tree, so can be old**; start from the dispatch's `review-packet:`, whose check digest is as rendered: re-read live checks before a verdict.
 Before step 1: `git diff $(git merge-base origin/main HEAD)...origin/main -- dev/governance/roles/`; empty is current.
-Before the handoff freezes the branch (`fixer.md`), prepare against the merge base only: steps 2, 12 govern after. Publish it with `tools/audit/seat/bus.sh push-verdict <pr> <verdict file> <evidence dir>` (a file there names the head; it carries your brief's `bus-nonce:`) and report its output in your thread to be confirmed; it posts as `hpo-approver` (decision 0013) -- never as the author App (#1233) or the owner's approving review, which code-owned paths need.
+Before the handoff freezes the branch (`fixer.md`), prepare against the merge base only: steps 2, 12 govern after. Publish it with `tools/audit/seat/bus.sh push-verdict <pr> <verdict file> <evidence dir>` and report its output in your thread to be confirmed; it posts as `hpo-approver` (decision 0013) -- never as the author App (#1233) or the owner's approving review, which code-owned paths need.
 A long job, or a wait on CI, runs as `fixer.md`'s preamble says: one watcher whose exit wakes you, never sleeping and polling. Rotate to a fresh context between rounds through refs, never mid-review, by ~150 k tokens.
 
 1. Re-run the mutation proof: delete the production line(s) the PR names,
@@ -32,8 +32,8 @@ A long job, or a wait on CI, runs as `fixer.md`'s preamble says: one watcher who
 8. **A quoted number you cannot re-derive is not verified — say so.** Re-derive
    under the PR's stated rule before trusting its count; if you cannot, or
    if you had to build your own definition to check it, write that in the verdict.
-9. **When the finding has no committed harness, that is itself a finding**
-   (#373's was an issue-body `grep`, #258's a judge comment). A fixer who builds their own instrument must
+9. **When the finding has no committed harness, that is itself a finding**.
+   A fixer who builds their own instrument must
    disclose it as their own, not the finder's -- so do you, if you built one;
    one rebuilt because a copy lived out of tree is named, and lands (`fixer.md` 18).
    Read the judge ruling first (#290's brief prescribed a refused harness).
@@ -71,10 +71,8 @@ A long job, or a wait on CI, runs as `fixer.md`'s preamble says: one watcher who
     **A GREEN `mutation` does not mean the baseline was green.** Since #1120 the
     lane prints `MUTATION TABLE INCONCLUSIVE` and exits 0 on `--scope changed`
     when its baseline is red, so a green conclusion means either no mutant
-    survived or none was evaluated, and only the run's own log separates them.
-    A diff that writes no production code line draws no mutant at all
-    (`changed_lines`). Where the answer turns on it, read the lane's log
-    rather than its conclusion.
+    survived or none was evaluated; a diff writing no production code line draws
+    no mutant (`changed_lines`). Where the answer turns on it, read the lane's log.
 
     **Cite CI's heavy runs** (tvofi, 2026-09-30): never re-run the gate or the
     mutation table. Cheap checks (seconds: a lint, one
@@ -84,14 +82,14 @@ A long job, or a wait on CI, runs as `fixer.md`'s preamble says: one watcher who
     verdict, and check it is still the head when you post it; if it moved, say
     which of your numbers survive and which you re-took.
 
-    The handoff makes the head yours from then on, so one that moved under you
-    is a broken rule rather than an accident: `blocked <sha> head-moved: measured <sha>, head is <other>`. Re-measuring
-    instead is yours to offer, never owed.
+    The handoff makes the head yours, so one that moved under you is a broken
+    rule: `blocked <sha> head-moved: measured <sha>, head is <other>`. Re-measuring
+    is yours to offer, never owed.
 
-    **A `merge` verdict carries** (#1667) to a head passing `orchestrator.md`
-    section 11's carry predicate: no reviewer turn, not `head-moved`. Any other
-    main merge returns as its **resolution delta**, which alone you judge;
-    any other move is re-reviewed.
+    **A `merge` verdict attaches to the head its first line names and carries**
+    (#1667; tvofi 2026-10-27) while `tools/audit/seat/review_carry.py
+    <verdicted> <new>` prints `CARRY`: no branch-only commit, not `head-moved`.
+    Else a main merge is its **resolution delta**, alone yours; any other move is re-reviewed.
 
 13. **A conflict is a measurement, not a status field.** `mergeStateStatus:
     DIRTY` is GitHub's, computed where the `claimnotes` driver cannot run
@@ -133,8 +131,10 @@ A long job, or a wait on CI, runs as `fixer.md`'s preamble says: one watcher who
 15. **Judge `fixer.md` step 17 on added lines**: a breach, or a departure
     from the architect or approved design note, is `blocked <sha> architecture-unsound: <how>`.
 
-Return a verdict with your RESULT lines, in your dispatch prompt's exact
-shape: `.claude/workflows/web-fix-wave.js` parses the comment's first
-line and routes on it, so one that does not parse is recorded blocked.
+Return a verdict with your RESULT lines under a first line `Fix review: merge <head40>`
+or `Fix review: blocked <head40> <class>: <reason>`, class `[a-z-]+` (a script routes on it), then
+`bus-nonce: <nonce>`; an evidence file names the head. A cloud seat, with no `push-verdict`,
+commits them in `cloud_relay.sh`'s layout (`ev/`, subject `verdict <pr> <head40>`) to a
+fresh repository and pushes `probe/rev-<pr>-<nonce first 8>`.
 
 **Say which round this is**: from the fourth, `fixer.md` owes a re-cut, not a repair.
diff --git a/dev/governance/roles/orchestrator.md b/dev/governance/roles/orchestrator.md
index 2b235dea3..1f078aee1 100644
--- a/dev/governance/roles/orchestrator.md
+++ b/dev/governance/roles/orchestrator.md
@@ -163,17 +163,16 @@ one reason to absorb `main` into a head (`nudge.md` 9).
 ## 7. You hold the freeze
 
 `fixer.md`'s handoff freezes a branch and **only the orchestrator moves the
-head**, so you break it. A reviewer works in a fresh *detached*
-worktree at the head SHA, so the branch has no worktree and no marker: a liveness
-check looking for either will not see it. Check whether a review is in flight on
-the pull request before moving anything. A head that moves under a review costs
-that review; a move that re-issues the verdict needs
-a fresh `bus.sh dispatch` at the new head before the reviewer publishes, since
-`push-verdict` refuses a nonce whose dispatch head is not the head the verdict
-names. **A conflict with main after the
-handoff is resolved by merge, never a re-cut**: merge
-`origin/main` into the head, or hand a semantic one to the fixer, and send the
-resolution delta to the same reviewer.
+head**, so you break it. A reviewer works in a fresh *detached* worktree at the
+head SHA, invisible to a liveness check for its worktree or marker. A
+head moving under an in-flight review costs it; a code-carrying move re-issuing
+the verdict needs a fresh `bus.sh dispatch` before the reviewer publishes, since
+`push-verdict` refuses a nonce minted at another head.
+Dispatching a second reviewer over a range clean against the reviewed head
+(`--reviewed-head`) is the error, not diligence (tvofi, 2026-10-27);
+`review_carry.py`'s `CARRY` refuses it. **A conflict after the handoff is
+resolved by merge, never a re-cut**: merge `origin/main` in, or hand a
+semantic one to the fixer; the resolution delta goes to that reviewer.
 
 **Stopping a seat is not neutral.** A seat killed between applying a mutation and
 restoring it leaves a production file broken in its worktree. Check
@@ -229,8 +228,8 @@ Through the roster seat, on `standing-roster.md`'s terms.
 - A `merge` verdict from a reviewer that measured **this** head, or a **carry**,
   with no reviewer turn (tvofi, 2026-10-01): `tools/pr/app_approve.sh --carry
   <verdict> <head>` reports carried, the files `git diff --name-only <verdict>
-  <head>` names miss the branch's own diff, and the claim files equal
-  `origin/main`'s. Anything else is a resolution delta for the same reviewer.
+  <head>` names miss the branch's own diff, and each claim file a pure union of
+  both sides. Anything else is a resolution delta for the same reviewer.
 - CI green at the verdicted head, landed onto a green `main` by
   `tools/audit/seat/merge_train.py batch` (tvofi, 2026-10-07), the only bypass:
   a proved batch merges while `main`'s tree equals its proof's; one entry merges
diff --git a/dev/programme/delivery/2933.md b/dev/programme/delivery/2933.md
new file mode 100644
index 000000000..32884b825
--- /dev/null
+++ b/dev/programme/delivery/2933.md
@@ -0,0 +1 @@
+- [#2933](https://github.com/tvofi/heatpump_optimizer/pull/2933) — **open**, Carry a previous review when the commit range holds no code change (R10-REVIEW-CARRY)
diff --git a/tests/closures.json b/tests/closures.json
index 6063b8d8c..bf12ec3ff 100644
--- a/tests/closures.json
+++ b/tests/closures.json
@@ -3607,6 +3607,7 @@
    "tools/audit/seat/r10_roster_ops_mutants.py",
    "tools/audit/seat/r10_roster_sync_mutants.py",
    "tools/audit/seat/record_row.py",
+   "tools/audit/seat/review_carry.py",
    "tools/audit/seat/review_packet.py",
    "tools/audit/seat/review_strength.py",
    "tools/audit/seat/roster_lib.py",
diff --git a/tools/audit/seat/INSTRUMENTS.md b/tools/audit/seat/INSTRUMENTS.md
index c2a5128fe..4f53fb1a4 100644
--- a/tools/audit/seat/INSTRUMENTS.md
+++ b/tools/audit/seat/INSTRUMENTS.md
@@ -20,7 +20,10 @@ re-runnable measurement harnesses a fixer or judge lands with a PR — its
 
 - `app_approve.sh` — approves a pull request as the `hpo-approver` App at one
   exact head SHA, only on a `merge` verdict for that SHA from an allowlisted
-  account (`--carry` re-approves a carried verdict). When: landing a
+  account (`--carry` re-approves a carried verdict: no branch-authored commit
+  in `git rev-list <verdict>..<head> --not main`, every merge git's automatic
+  one and each `claimnotes` file a pure union of its parents' lines). When:
+  landing a
   non-code-owned verdicted PR whose head the reviewer measured. Refusal: a
   head SHA that is not the PR's current head, or a verdict whose SHA or
   account does not match — the approval names one tree or it does nothing.
@@ -887,6 +890,24 @@ sweep's standing-seat liveness step keep them alive.
   PR state, under a byte budget. When: a state beat; regenerate rather than
   hand-edit the resume. Refusal: over-budget output refuses with `--out`
   unwritten — archive before regenerating.
+- `review_carry.py` — answers, from two shas and the commit range alone,
+  whether a moved head still needs its own review: `review_carry.py
+  <reviewed> <new>` prints the branch-only commit count, their subjects and
+  exactly one `CARRY`/`FRESH-REVIEW` (`git rev-list --count <reviewed>..<new>
+  --not origin/main`; zero, or every commit in it a merge, is the only CARRY,
+  since a merge authors no commit and what it joins is either main's history
+  or branch commits the range already returns — so a merge of the branch's
+  own previous head, update_pr.sh's re-cut, is not a change). When: before
+  dispatching a reviewer at a moved head, and in a verdict that re-issues a
+  prior one — the owner's 2026-10-27 ruling, "if there are no code changes,
+  the previous review can be carried", made mechanical. Refusal: an unknown
+  sha, a missing main ref or a missing commit cannot be decided (exit 2, no
+  verdict line, so it is never read as CARRY); a force-push, a non-merge
+  commit — including the commits a merge of a non-main branch brings in — and
+  a `ci:`/`claims:` commit are all `FRESH-REVIEW`. A claim file resolved
+  INSIDE a merge is `app_approve.sh --carry`'s read, not this one's.
+  `--verdict-only` prints the token alone; `bus.sh dispatch --reviewed-head`
+  is its caller, and `--self-test` grades the ranges.
 - `review_strength.py` — real-catch blocks per reviewed PR, incidence and
   first-pass share from the `review/*` bus and its `archive/review/*` tags,
   over git only (no REST), per window and per stratum: reviewer kind (a
diff --git a/tools/audit/seat/bus.sh b/tools/audit/seat/bus.sh
index 9636471cd..eac752dd7 100755
--- a/tools/audit/seat/bus.sh
+++ b/tools/audit/seat/bus.sh
@@ -5,7 +5,7 @@
 #
 #   bus.sh push-verdict <pr> <VERDICT.md> <evidence dir>       (reviewer)
 #   bus.sh watch [--once] [--post] [--every <seconds>]          (orchestrator)
-#   bus.sh dispatch <pr> <head> <reviewer> [--nonce N] [--model M] [--past-three <reason>]
+#   bus.sh dispatch <pr> <head> <reviewer> [--reviewed-head <sha>] [--nonce N] [--model M] [--past-three <reason>]
 #                   [--harness <path> | --harness-file <file>]
 #   bus.sh confirm <pr> <review commit>                         (orchestrator)
 #   bus.sh post <pr>                                            (orchestrator)
@@ -30,7 +30,13 @@
 # one the reviewer measured, which `app_approve.sh --carry` refuses as a
 # commit of the branch's own, so it costs a re-review (R9-RCA-1990 class E).
 # A verdict posts only against a dispatch's nonce, so this is the one place
-# that can keep the row from landing late.
+# that can keep the row from landing late. `dispatch` also REFUSES TO MINT a
+# nonce for a head whose `review_carry.py <reviewed-head> <head>` answers
+# CARRY -- no branch-authored commit since the head the caller names with
+# --reviewed-head (tvofi, 2026-10-27: "if there are no code changes, the
+# previous review can be carried"). The refusal is what makes the ruling
+# mechanical rather than a judgement a seat can talk itself out of; a
+# `--nonce` re-record mints nothing and is left alone.
 # `orphans` is the handoff family's level-triggered obligation, which `watch`
 # only ever reports once. A `handoff/<t>` whose `handoff-body/<t>` ref exists
 # owed a pull request -- `open_pr.sh` fetches both and fails without the body --
@@ -417,11 +423,12 @@ three_rounds() { # pr past-three-reason -> 0 to dispatch; else why
 # render` writes $S/packets/<pr>-<head>.md, refusing on its mechanical signals, and dispatch
 # names it only once `check` reads that head in it. --harness/--harness-file is the finder's.
 # HPO_BUS_PACKER replaces the renderer (the self-test's stub).
-dispatch() { # pr head reviewer [--nonce N] [--model M] [--past-three <reason>] [--harness P|--harness-file F] -> records, closes, prints the packet and nonce lines
-  local pr=${1:-} h=${2:-} r=${3:-} n="" m=- p3="" row why hk="" hv="" pk prc=0 pmsg="" pkline=""
+dispatch() { # pr head reviewer [--reviewed-head <sha>] [--nonce N] [--model M] [--past-three <reason>] [--harness P|--harness-file F] -> records, closes, prints the packet and nonce lines
+  local pr=${1:-} h=${2:-} r=${3:-} n="" m=- p3="" row why rh="" carry rc hk="" hv="" pk prc=0 pmsg="" pkline=""
   shift 3 2>/dev/null || shift $#
   while [ $# -gt 0 ]; do
     case $1 in
+      --reviewed-head) [[ ${2:-} =~ ^[0-9a-f]{40}$ ]] || die "dispatch: --reviewed-head takes a 40-hex commit"; rh=$2; shift 2 ;;
       --nonce) [[ ${2:-} =~ ^[0-9a-f]{32}$ ]] || die "dispatch: --nonce takes a 32-hex nonce"; n=$2; shift 2 ;;
       --model) [[ ${2:-} =~ ^[A-Za-z0-9._-]+$ ]] || die "dispatch: --model takes one token"; m=$2; shift 2 ;;
       --past-three) [ -n "${2:-}" ] && [ "${2#--}" = "$2" ] || die "dispatch: --past-three needs a reason"; p3=$2; shift 2 ;;
@@ -445,6 +452,24 @@ dispatch() { # pr head reviewer [--nonce N] [--model M] [--past-three <reason>]
     || die "dispatch: the head $h is not readable in this checkout; fetch it, then dispatch"
   git cat-file -e "$h:$row" 2>/dev/null \
     || die "dispatch: #$pr's head $h carries no $row; the row lands before the review (delivery-status-tracking.md) -- write it and re-push, then dispatch"
+  # THE REVIEW CARRY (tvofi, 2026-10-27: "if there are no code changes, the
+  # previous review can be carried"). A fresh nonce over a head whose range
+  # against the reviewed head the caller names is clean starts a second
+  # reviewer for a proof that did not move. `review_carry.py` answers from the
+  # commit range alone, so the seat cannot judge; this refusal is a refusal,
+  # not a warning, because a warning is what let the second reviewer start.
+  # --nonce mints nothing (a relay-minted nonce re-recorded for the seat
+  # fired with it), so it is left alone.
+  if [ -n "$rh" ] && [ -z "$n" ]; then
+    git cat-file -e "$rh^{commit}" 2>/dev/null || git fetch -q "$REMOTE" "$rh" 2>/dev/null
+    carry=$(python3 -I "$ROOT/tools/audit/seat/review_carry.py" "$rh" "$h" \
+              --verdict-only 2>&1); rc=$?
+    if [ "$rc" = 2 ]; then
+      die "dispatch: cannot read the range $rh..$h: ${carry#review_carry: CANNOT DECIDE: }"
+    elif [ "$rc" = 0 ]; then
+      die "dispatch: #$pr's head $h carries no branch-authored commit since the reviewed head $rh (review_carry: CARRY) -- the prior review carries, so no second reviewer is dispatched (tvofi, 2026-10-27)"
+    fi
+  fi
   why=$(three_rounds "$pr" "$p3") || die "dispatch: $why"
   pk=$S/packets/$pr-$h.md
   # THE PACKET IS AN AID, NEVER A GATE ON THE DISPATCH. Two failures are different:
@@ -709,7 +734,7 @@ EOF
 self_test() {
   local W pass=0 fail=0 out rc h1 h2 norow r1 r2 r9 v1 v2 ra rf t tt ev n N0 N1 N1b N1c N2 N9
   local N3 N3b N3c N3d N4 DT fa g1 ro n0 realgit want wanttree
-  local o1 o2 u1 u2 x1 x2 c1 c2 s1 m1 mb f1 f2
+  local o1 o2 u1 u2 x1 x2 c1 c2 s1 m1 mb f1 f2 hm mainadv cbase
   W=$(mktemp -d) || { echo "self-test: no temporary directory"; return 1; }
   ok() { pass=$((pass + 1)); printf '  ok   %s\n' "$1"; }
   bad() { fail=$((fail + 1)); printf '  FAIL %s\n' "$1"; }
@@ -878,6 +903,37 @@ bus-nonce: $N1b" ] && [ "$(grep -c " $N1b " "$W/state/dispatched")" = 2 ] \
   out=$(run dispatch 7 "$h1" cmsg_Z2); rc=$?
   [ $rc = 0 ] && echo "$out" | grep -q '^bus-nonce: '
   expect "dispatch accepts the same pull request once its row is on the head (null control)" $?
+  # THE REVIEW CARRY (R10-REVIEW-CARRY; tvofi, 2026-10-27). A fresh nonce over a
+  # head whose range against the named reviewed head is clean starts a second
+  # reviewer for a proof that did not move. `hm` is a merge-only move (main
+  # advances, the branch merges it); `h2` carries a non-merge commit. One
+  # command, opposite answers: `review_carry.py` decides, dispatch refuses or
+  # mints. origin/main is restored below so the orphans arms keep their base.
+  cbase=$(git -C "$W/seat" rev-parse "origin/main")
+  git -C "$W/seat" checkout -q -b carry-main "$h1"
+  printf 'main moves\n' > "$W/seat/main-move.txt"
+  git -C "$W/seat" add main-move.txt
+  git -C "$W/seat" -c user.name=t -c user.email=t@t commit -q -m "main moves on"
+  mainadv=$(git -C "$W/seat" rev-parse HEAD)
+  git -C "$W/seat" push -q origin HEAD:refs/heads/main
+  git -C "$W/seat" checkout -q -b carry "$h1"
+  git -C "$W/seat" -c user.name=t -c user.email=t@t merge -q --no-ff \
+    -m "Merge remote-tracking branch 'origin/main' into carry" "$mainadv"
+  hm=$(git -C "$W/seat" rev-parse HEAD)
+  out=$(seat dispatch 31 "$hm" cmsg_C1 --reviewed-head "$h1"); rc=$?
+  [ $rc != 0 ] && echo "$out" | grep -q "review_carry: CARRY" \
+    && echo "$out" | grep -q "reviewed head $h1" \
+    && ! echo "$out" | grep -q '^bus-nonce: ' \
+    && [ "$(grep -c "^31 " "$W/state/dispatched")" = 0 ] \
+    && ! python3 -I "$ROOT/tools/audit/seat/ledger.py" --log "$W/ledger/cloud-relay.log" board 2>/dev/null \
+         | grep -q "reviewer-fire 31 "
+  expect "dispatch refuses to mint a nonce over a clean range, naming the reviewed head, and records nothing" $?
+  out=$(seat dispatch 31 "$h2" cmsg_C2 --reviewed-head "$h1"); rc=$?
+  [ $rc = 0 ] && echo "$out" | grep -q '^bus-nonce: ' \
+    && [ "$(grep -c "^31 $h2 " "$W/state/dispatched")" = 1 ]
+  expect "null control: dispatch mints at a head that does carry code" $?
+  git -C "$W/seat" checkout -q main
+  git -C "$W/seat" push -q -f origin "$cbase:refs/heads/main"
   printf 'Fix review: merge %s\n\nbus-nonce: %s\n' "$h1" "$N1" > "$W/merge.md"
   printf 'Fix review: merge %s\n\nbus-nonce: %s\n' "$h1" "$N1b" > "$W/othernonce.md"
   # push-verdict binds the nonce to its dispatch before it proposes. A nonce no
diff --git a/tools/audit/seat/cloud_relay.sh b/tools/audit/seat/cloud_relay.sh
index 35741074e..4bfd60257 100644
--- a/tools/audit/seat/cloud_relay.sh
+++ b/tools/audit/seat/cloud_relay.sh
@@ -556,6 +556,25 @@ EOF
   mk 8 $h $h $n;           chk "a ref pushed for PR 8 leaves PR 7 with no ref" 2 relay 7 $n $h
   git -C "$t/o.git" update-ref refs/heads/probe/rev-7-${n:0:8} "$(git -C "$t/o.git" rev-parse refs/heads/probe/rev-8-${n:0:8})"
   chk "a commit subject naming PR 8 under PR 7's ref is refused" 2 relay 7 $n $h
+  # THE STATED LAYOUT RELAYS (P200, R10-REVIEW-CARRY). A cloud reviewer reads fix-review.md,
+  # never this script, so the probe is built from the templates that file states -- the ref,
+  # the subject, the first line, the nonce line and ev/ -- and must relay (the verdict file's
+  # name is this header's alone: policy_lint refuses a path not in the tree). A
+  # template the file drops, or one this relay would refuse, fails here instead of on a verdict.
+  doc() { # doc <template regex> : the first backticked span in fix-review.md matching it, placeholders filled
+    grep -o "\`$1[^\`]*\`" "$HERE/../../../dev/governance/roles/fix-review.md" | head -n 1 | tr -d '\`' \
+      | sed -e "s/<pr>/9/g" -e "s/<head40>/$h/g" -e "s/<nonce first 8>/${n:0:8}/g" -e "s/<nonce>/$n/g"; }
+  stated() { local ref subj first nl
+    ref=$(doc 'probe/rev-'); subj=$(doc 'verdict <pr> '); first=$(doc 'Fix review: merge '); nl=$(doc 'bus-nonce: ')
+    grep -q '`ev/`' "$HERE/../../../dev/governance/roles/fix-review.md" || return 3
+    [ -n "$ref" ] && [ -n "$subj" ] && [ -n "$first" ] && [ -n "$nl" ] || return 3
+    case "$ref$subj$first$nl" in *'<'*) return 3;; esac
+    rm -rf "$t/pr"; throwaway_git_init "$t/pr" -q; mkdir "$t/pr/ev"; echo "$h" > "$t/pr/ev/head"
+    printf '%s\n\n%s\n' "$first" "$nl" > "$t/pr/verdict.md"
+    git -C "$t/pr" add -A; git -C "$t/pr" commit -qm "$subj"
+    git -C "$t/o.git" fetch -qf "$t/pr" "HEAD:refs/heads/$ref" || return 3
+    relay 9 $n $h; }
+  chk "the probe layout fix-review.md states relays" 0 stated
   chk "a short head is refused" 2 relay 7 $n ${h%?}
   chk "a short nonce is refused" 2 relay 7 abc $h
   chk "a non-numeric PR is refused" 2 relay x $n $h
diff --git a/tools/audit/seat/review_carry.py b/tools/audit/seat/review_carry.py
new file mode 100755
index 000000000..bd852f34b
--- /dev/null
+++ b/tools/audit/seat/review_carry.py
@@ -0,0 +1,351 @@
+#!/usr/bin/env python3
+"""review_carry.py -- does a new head carry branch-authored change since the
+head a review measured?
+
+THE RULING (tvofi, 2026-10-27, verbatim): "if there are no code changes, the
+previous review can be carried". This makes it mechanical, because a seat that
+has to decide by eye whether a move carried code will eventually decide wrong
+in the direction that merges unreviewed code (R10-REVIEW-CARRY).
+
+THE TEST IS A COMMIT RANGE, NOT AN OPINION:
+
+    git rev-list --count <reviewed-head>..<new-head> --not origin/main
+
+Zero, or a count whose commits are all merges, means no branch-authored
+change and the prior verdict carries: this prints CARRY. A merge authors no
+code of its own -- what it joins is main's history (`--not` drops it) or
+branch commits, which are in the range as non-merge commits and counted -- so
+a merge of the branch's own previous head, the shape update_pr.sh re-cuts one
+into, is not a change either. Any non-merge commit in that range means the
+head carries code and takes a fresh review: this prints FRESH-REVIEW. A body
+rewrite never by itself voids a verdict, because it is not a commit in the
+range. A claim-file resolution, or a `ci:`/`claims:` bot commit, inside the
+range IS a change when it lands as a commit: it is a non-merge commit, and no
+subject is exempt -- the range is read before the merge is trusted. A claim
+file resolved INSIDE a merge is not read here; `tools/pr/app_approve.sh
+--carry` reads it, and a pure union of both parents is the only resolution it
+accepts. (This answers the reviewer's verdict carrying. `merge_train.py`'s
+owner-approval carry answers a different question -- the owner's approval, not
+the reviewer's verdict -- and is not this instrument.)
+
+THE MEASURED INSTANCES, the null control: one command, opposite answers.
+
+    #2876  253dc4867 -> e0237e6d0  branch-only 1, the merge itself -> CARRY
+    #2876  253dc4867 -> d08647f05  branch-only 3, all merges       -> CARRY
+    #2854  fccb88371 -> 9f424cf74  branch-only 41 (incl. ce277f1d6) -> FRESH-REVIEW
+
+DEGENERATE CASES, each explicit rather than a guess:
+  - an unknown sha cannot be decided: CANNOT DECIDE, exit 2, no verdict line;
+  - the reviewed head is the new head (head did not move): CARRY;
+  - the reviewed head is an ancestor of the new head: the range is read;
+  - the new head is not a descendant of the reviewed head (force-push): the
+    branch-only range is still counted and printed, and the answer is
+    FRESH-REVIEW, because a rewritten head is not the head the review measured.
+
+Usage:
+    review_carry.py <reviewed-head> <new-head> [--main <ref>] [--verdict-only]
+                    [--repo <dir>]
+    review_carry.py --self-test
+
+Exit: 0 CARRY, 1 FRESH-REVIEW, 2 cannot decide.
+
+The verdict is also the last line, `review_carry: CARRY|FRESH-REVIEW`, so a
+seat can paste the whole output into a brief or a verdict.
+"""
+import os
+import subprocess
+import sys
+import tempfile
+
+CARRY = "CARRY"
+FRESH = "FRESH-REVIEW"
+
+
+class Undecidable(Exception):
+    pass
+
+
+def git(repo, *args):
+    proc = subprocess.run(
+        ["git", "-C", repo, *args], capture_output=True, text=True
+    )
+    return proc.returncode, proc.stdout, proc.stderr
+
+
+def must(repo, *args):
+    code, out, err = git(repo, *args)
+    if code != 0:
+        raise Undecidable("git %s failed: %s" % (" ".join(args), err.strip()[:200]))
+    return out
+
+
+def resolve_commit(repo, rev):
+    code, out, _ = git(repo, "rev-parse", "--verify", "--quiet", rev + "^{commit}")
+    sha = out.strip()
+    if code != 0 or len(sha) != 40:
+        raise Undecidable("unknown sha %r: no commit of that name in %s" % (rev, repo))
+    return sha
+
+
+def is_ancestor(repo, a, b):
+    code, _, _ = git(repo, "merge-base", "--is-ancestor", a, b)
+    return code == 0
+
+
+def parents_of(repo, commit):
+    fields = must(repo, "rev-list", "--parents", "-n", "1", commit).split()
+    return fields[1:]
+
+
+def branch_only(repo, reviewed, new, main):
+    """The range the rule names: reviewed..new, excluding main's history."""
+    count = int(must(repo, "rev-list", "--count", "%s..%s" % (reviewed, new),
+                     "--not", main).strip() or "0")
+    commits = []
+    if count:
+        for line in must(repo, "log", "--reverse", "--format=%H%x09%s",
+                         "%s..%s" % (reviewed, new), "--not", main).splitlines():
+            if line.strip():
+                sha, _, subject = line.partition("\t")
+                commits.append((sha, subject))
+    return count, commits
+
+
+def classify(repo, reviewed, new, main):
+    """-> (verdict, reason, count, commits). Raises Undecidable when it cannot
+    judge. `main` is a resolved commit id."""
+    if reviewed == new:
+        return CARRY, "head did not move", 0, []
+    descendant = is_ancestor(repo, reviewed, new)
+    count, commits = branch_only(repo, reviewed, new, main)
+    carrying = []
+    for sha, subject in commits:
+        # A merge joins history; it does not author a commit. What it joins is
+        # either main's (excluded by --not) or branch commits, which the range
+        # returns as non-merge commits of their own. So it counts as carrying
+        # only if it is not a merge at all.
+        if len(parents_of(repo, sha)) < 2:
+            carrying.append((sha, subject))
+    if not descendant:
+        reason = ("force-push: %s is not a descendant of %s"
+                  % (new[:9], reviewed[:9]))
+        if carrying:
+            reason += "; %d of %d branch-only commit(s) carry code" % (
+                len(carrying), count)
+        return FRESH, reason, count, commits
+    if count == 0:
+        return CARRY, "no branch-only commit", 0, []
+    if carrying:
+        return (FRESH,
+                "%d of %d branch-only commit(s) carry code"
+                % (len(carrying), count),
+                count, commits)
+    return (CARRY,
+            "all %d branch-only commit(s) are merges" % count,
+            count, commits)
+
+
+def render(reviewed, new, main_name, verdict, reason, count, commits):
+    lines = ["review_carry: %s -> %s  main=%s" % (reviewed[:9], new[:9], main_name),
+             "  branch-only commits: %d" % count,
+             "  why: %s" % reason]
+    for sha, subject in commits:
+        lines.append("  %s  %s" % (sha[:9], subject))
+    lines.append("review_carry: %s" % verdict)
+    return "\n".join(lines)
+
+
+def run(argv):
+    args = list(argv)
+    main_name = "origin/main"
+    verdict_only = False
+    repo = None
+    positional = []
+    while args:
+        a = args.pop(0)
+        if a in ("-h", "--help"):
+            sys.stdout.write(__doc__)
+            return 0
+        if a == "--verdict-only":
+            verdict_only = True
+        elif a == "--main":
+            if not args:
+                raise Undecidable("--main needs a ref")
+            main_name = args.pop(0)
+        elif a == "--repo":
+            if not args:
+                raise Undecidable("--repo needs a directory")
+            repo = args.pop(0)
+        elif a.startswith("--"):
+            raise Undecidable("unknown argument %r" % a)
+        else:
+            positional.append(a)
+    if len(positional) != 2:
+        raise Undecidable("usage: review_carry.py <reviewed-head> <new-head> "
+                          "[--main <ref>] [--verdict-only] [--repo <dir>]")
+    repo = repo or os.getcwd()
+    if not os.path.isdir(repo):
+        raise Undecidable("not a directory: %s" % repo)
+    reviewed = resolve_commit(repo, positional[0])
+    new = resolve_commit(repo, positional[1])
+    main = resolve_commit(repo, main_name)
+    verdict, reason, count, commits = classify(repo, reviewed, new, main)
+    if verdict_only:
+        print(verdict)
+    else:
+        print(render(reviewed, new, main_name, verdict, reason, count, commits))
+    return 0 if verdict == CARRY else 1
+
+
+# ---- self-test -------------------------------------------------------------
+def _t(repo, *args):
+    proc = subprocess.run(["git", "-C", repo, *args], capture_output=True,
+                          text=True, env=_GIT_ENV)
+    if proc.returncode != 0:
+        raise SystemExit("self-test: git %s failed: %s"
+                         % (" ".join(args), proc.stderr.strip()))
+    return proc.stdout
+
+
+def _commit(repo, message):
+    _t(repo, "-c", "user.name=t", "-c", "user.email=t@t", "commit", "-q",
+       "--allow-empty", "-m", message)
+    return _t(repo, "rev-parse", "HEAD").strip()
+
+
+_GIT_ENV = {}
+
+
+def self_test():
+    global _GIT_ENV
+    failures = 0
+    checks = 0
+
+    def check(name, got, want):
+        nonlocal failures, checks
+        checks += 1
+        if got != want:
+            failures += 1
+            print("  FAIL %s: got %r, want %r" % (name, got, want))
+        else:
+            print("  ok   %s" % name)
+
+    # Every scratch repository comes from the shared helper (tests/throwaway_git.py,
+    # #2051), whose env also carries the identity the commits below need.
+    sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)),
+                                    "..", "..", "..", "tests"))
+    from throwaway_git import throwaway_git_init
+    root = tempfile.mkdtemp(prefix="review_carry_selftest.")
+    origin = os.path.join(root, "origin.git")
+    seat = os.path.join(root, "seat")
+    throwaway_git_init(origin, "-q", "--bare")
+    _GIT_ENV = throwaway_git_init(seat, "-q")
+    _t(seat, "remote", "add", "origin", origin)
+    _t(seat, "checkout", "-q", "-b", "main")
+    _t(seat, "commit", "-q", "--allow-empty", "-m", "base")
+    base = _t(seat, "rev-parse", "HEAD").strip()
+    _t(seat, "push", "-q", "origin", "HEAD:refs/heads/main")
+    # main advances on its own line, so a branch can merge it in.
+    _t(seat, "checkout", "-q", "-b", "main2", "main")
+    _t(seat, "commit", "-q", "--allow-empty", "-m", "main moves on")
+    main1 = _t(seat, "rev-parse", "HEAD").strip()
+    _t(seat, "push", "-q", "origin", "HEAD:refs/heads/main")
+    _t(seat, "checkout", "-q", "main")
+    _t(seat, "reset", "-q", "--hard", main1)
+    # the reviewed head: reviewed work on a branch
+    _t(seat, "checkout", "-q", "-b", "fix/x", base)
+    with open(os.path.join(seat, "code.txt"), "w") as fh:
+        fh.write("reviewed\n")
+    _t(seat, "add", "code.txt")
+    reviewed = _commit(seat, "reviewed: the code")
+    # a merge-only move: merge main1 in
+    _t(seat, "merge", "-q", "--no-ff", "-m",
+       "Merge remote-tracking branch 'origin/main' into fix/x", main1)
+    merged = _t(seat, "rev-parse", "HEAD").strip()
+    # update_pr.sh's re-cut: a merge whose second parent is the branch's own
+    # previous head, so neither parent is main and the range is merges only.
+    recut = _t(seat, "commit-tree",
+               _t(seat, "rev-parse", merged + "^{tree}").strip(),
+               "-p", reviewed, "-p", merged, "-m",
+               "Merge commit 'x' into fix/x").strip()
+    # a code move: a non-merge commit on top
+    with open(os.path.join(seat, "code.txt"), "w") as fh:
+        fh.write("changed\n")
+    _t(seat, "add", "code.txt")
+    coded = _commit(seat, "fix: change the code")
+    # a bot-subject commit is still a non-merge commit: no exemption
+    bot = _commit(seat, "ci: pin killed mutants")
+    # a merge of a NON-main branch is a branch-authored change
+    _t(seat, "checkout", "-q", "-b", "feat/y", merged)
+    _commit(seat, "feat: unreviewed work")
+    _t(seat, "checkout", "-q", "fix/x")
+    _t(seat, "merge", "-q", "--no-ff", "-m", "Merge branch 'feat/y' into fix/x",
+       "feat/y")
+    feat_merge = _t(seat, "rev-parse", "HEAD").strip()
+
+    def answer(rev, new, main="origin/main"):
+        return classify(seat, resolve_commit(seat, rev), resolve_commit(seat, new),
+                        resolve_commit(seat, main))
+
+    v, why, n, cs = answer(reviewed, merged)
+    check("a merge-only move answers CARRY", v, CARRY)
+    check("the merge-only move's branch-only count is 1", n, 1)
+    check("the merge it counted is the merge itself", cs[0][0], merged)
+
+    v, _, n, _ = answer(reviewed, coded)
+    check("a code move answers FRESH-REVIEW", v, FRESH)
+    check("the code move's branch-only count is 2", n, 2)
+
+    v, why, n, _ = answer(reviewed, recut)
+    check("a re-cut merge of the branch's own previous head answers CARRY",
+          v, CARRY)
+    check("its branch-only count is 2, both merges", n, 2)
+
+    v, _, _, _ = answer(reviewed, reviewed)
+    check("head did not move answers CARRY", v, CARRY)
+
+    v, _, _, _ = answer(reviewed, bot)
+    check("a bot-subject commit is a code move", v, FRESH)
+
+    v, _, _, _ = answer(reviewed, feat_merge)
+    check("a merge of a non-main branch answers FRESH-REVIEW", v, FRESH)
+
+    v, why, _, _ = answer(reviewed, merged, main="main")
+    check("a newer main ref does not change the answer", v, CARRY)
+
+    # force-push: a head that does not descend from the reviewed head
+    _t(seat, "checkout", "-q", "-b", "fix/force", reviewed)
+    _t(seat, "reset", "-q", "--hard", base)
+    with open(os.path.join(seat, "code.txt"), "w") as fh:
+        fh.write("rewritten\n")
+    _t(seat, "add", "code.txt")
+    forced = _commit(seat, "fix: rewritten history")
+    v, why, _, _ = answer(reviewed, forced)
+    check("a force-push answers FRESH-REVIEW", v, FRESH)
+    check("the force-push names itself", why.startswith("force-push:"), True)
+
+    try:
+        answer("0" * 40, merged)
+        check("an unknown sha cannot decide", "no error", "Undecidable")
+    except Undecidable:
+        check("an unknown sha cannot decide", "Undecidable", "Undecidable")
+
+    print("review_carry self-test: %d checks, %d failed" % (checks, failures))
+    return 0 if failures == 0 else 1
+
+
+def main(argv):
+    if not argv:
+        sys.stderr.write("review_carry: CANNOT DECIDE: no arguments\n")
+        return 2
+    if argv[0] == "--self-test":
+        return self_test()
+    try:
+        return run(argv)
+    except Undecidable as exc:
+        sys.stderr.write("review_carry: CANNOT DECIDE: %s\n" % exc)
+        return 2
+
+
+if __name__ == "__main__":
+    sys.exit(main(sys.argv[1:]))
diff --git a/tools/pr/app_approve.sh b/tools/pr/app_approve.sh
index 7b348fa8e..4969ed21d 100755
--- a/tools/pr/app_approve.sh
+++ b/tools/pr/app_approve.sh
@@ -54,12 +54,20 @@
 #     or empty CODEOWNERS refuses. Matching errs toward owning, which refuses;
 #   - the head is still <sha> when re-read after minting, just before the POST.
 #
-# THE CARRY (#1667, D13-s1-02). A verdict at V carries to a later head H only
-# when (1) V is an ancestor of H; (2) every first-parent commit V..H is a
-# two-parent merge of a main commit whose tree is git's automatic merge of its
-# parents (`merge-tree`, outside the driver files below), or a single-parent
-# `ci:` commit that changes only those driver files; and
-# (3) the branch's own diff against its merge base with main is byte-identical
+# THE CARRY (#1667, D13-s1-02; R10-REVIEW-CARRY). A verdict at V carries to a
+# later head H only when (1) V is an ancestor of H; (2) every commit
+# `git rev-list V..H --not main` returns is a merge, or a single-parent `ci:`/
+# bot commit confined to the files its subject names -- a merge authors no
+# code of its own, because what it joins is main's history (outside the
+# range) or branch commits (inside it, refused by this clause), so a merge of
+# the branch's own previous head, which is how update_pr.sh re-cuts a head,
+# is no change (tvofi, 2026-10-27: "if there are no code changes, the
+# previous review can be carried"); (3) each merge's tree is git's automatic
+# merge of its parents outside the driver files below, and it resolves each
+# `merge=claimnotes` file to a pure union of its two parents' lines, because
+# a resolution that drops, adds or rewrites a line is content no review
+# measured; and (4) the branch's own diff against its merge base with main is
+# byte-identical
 # at V and at H, read with two relaxations measured over round 9's window
 # (the literal byte rule carried 0 of its 22 re-verification rounds): each
 # hunk header (line numbers, and the function line git reads from above the
@@ -68,10 +76,10 @@
 # `.gitattributes` gives a merge driver are left out, because stamps and CI
 # bots rewrite those on main and required checks grade them at every head.
 # Anything else -- a rewrite, a commit of the branch's own, one changed byte
-# in a hunk or its context -- keeps today's re-review. Condition (3) is the
-# guard; (1) and (2) name the moves it applies to, and a `ci:` subject buys
-# nothing on its own. The evidence gate then reads V, the head the reviewer
-# measured.
+# in a hunk or its context -- keeps today's re-review. Condition (4) is the
+# guard; (1), (2) and (3) name the moves it applies to, and a `ci:` subject
+# buys nothing on its own. The evidence gate then reads V, the head the
+# reviewer measured.
 #
 # THE SECRETS. The key files are `$HPO_IDENTITY_DIR/identity-approver.appid`
 # and `identity-approver.pem` (default directory `~/.zcode`). The JWT and the
@@ -219,7 +227,7 @@ bot_paths() { # subject -> one pathspec per line, nothing for an unknown subject
 
 # carry <verdict sha> <head sha> <main ref>: prints the reason; 0 only on a carry.
 carry() {
-  local v=$1 h=$2 main=$3 c ps ae subj p mv mh t x y b ba bt e
+  local v=$1 h=$2 main=$3 c ps ae subj p mv mh t x y b ba bt e cp got want
   git merge-base --is-ancestor "$v" "$h" 2>/dev/null || { echo "$v is not an ancestor of $h"; return 1; }
   # Read at main, never at a head: a branch that gave a file a driver would
   # otherwise take it out of the comparisons itself.
@@ -229,21 +237,58 @@ carry() {
   t=$(git show "$main:.gitattributes" 2>/dev/null | awk '!/^#/ && / merge=/ {print ":(exclude)" $1}')
   x=()
   while IFS= read -r p; do [ -z "$p" ] || x[${#x[@]}]=$p; done <<<"$t"
+  # The claim files, the one driver whose resolution a human is expected to
+  # write by hand when the driver refuses. Read at main like the list above,
+  # and keyed on the driver NAME, so a branch that gives another file a driver
+  # cannot move it into this check.
+  cp=$(git show "$main:.gitattributes" 2>/dev/null \
+    | awk '!/^#/ {for (i = 2; i <= NF; i++) if ($i == "merge=claimnotes") {print $1; break}}')
   local bots=""
+  # The whole range, not the first-parent chain: a commit the branch merged in
+  # from another branch is branch-authored too, and it is refused below as a
+  # non-merge commit. `--not "$main"` drops main's own history and nothing
+  # else, so what remains is exactly what the branch authored.
   while IFS=$'\t' read -r c ps ae subj; do
     set -- $ps
     if [ $# -ge 2 ]; then
+      # A merge authors no code of its own: what it joins is main's history
+      # (outside this range) or branch commits (inside it, refused above), so
+      # it is no code change whatever its parents are -- including a merge of
+      # the branch's own previous head, which is the shape update_pr.sh
+      # re-cuts a head into (tvofi, 2026-10-27: "if there are no code changes,
+      # the previous review can be carried"). Two things it can still smuggle
+      # in, and both are read below: content its own resolution added, and a
+      # claim file resolved by hand rather than unioned.
       [ $# -eq 2 ] || { echo "$c merges more than one branch"; return 1; }
-      # A parent off main is a head a seat merged main into and handed off,
-      # which update_pr.sh merged in turn (#2876): it carries, or nothing does.
-      git merge-base --is-ancestor "$2" "$main" || e=$(carry "$v" "$2" "$main") \
-        || { echo "$c merges $2, which is not on $main and does not carry: $e"; return 1; }
+      # A parent off main -- a head a seat merged main into and handed off,
+      # which update_pr.sh merged in turn (#2876) -- needs no check of its
+      # own: the range walks into it, so its commits are read here like the
+      # head's, and its own main merge must be automatic too.
       # A hand-resolved merge can move the branch's change to another place
       # with the same context, which the header-free comparison below cannot
-      # see: the merge must be git's own automatic result.
-      t=$(git merge-tree --write-tree --no-messages "$1" "$2" | head -1)
+      # see: the merge must be git's own automatic result outside the driver
+      # files, whose resolutions the next check reads.
+      # The drivers are quiet here on purpose: a claim driver refusing is what
+      # leaves a human the resolution read below, and printing its refusal
+      # beside a CARRY reads as a contradiction of a check that did pass.
+      t=$(git merge-tree --write-tree --no-messages "$1" "$2" 2>/dev/null | head -1)
+      case $t in
+        ""|*[!0-9a-f]*)
+          echo "$c: git merge-tree wrote no tree for its parents"; return 1 ;;
+      esac
       git diff --quiet "$t" "$c" -- . ${x[@]+"${x[@]}"} \
         || { echo "$c is not the automatic merge of its parents"; return 1; }
+      # A claim file is where a driver refusal leaves a human deciding, and a
+      # pure union of both sides is the only resolution that changes nothing:
+      # it carries the branch's note and main's. A line dropped, added or
+      # rewritten is content no review measured, so it is a change.
+      while IFS= read -r p; do
+        [ -z "$p" ] && continue
+        got=$(git show "$c:$p" 2>/dev/null | awk 'NF' | sort -u)
+        want=$({ git show "$1:$p" 2>/dev/null; git show "$2:$p" 2>/dev/null; } | awk 'NF' | sort -u)
+        [ "$got" = "$want" ] \
+          || { echo "$c resolves $p to something other than the union of its parents"; return 1; }
+      done <<<"$cp"
     elif [[ $subj != ci:* ]] && [ -z "$(bot_paths "$subj")" ]; then
       echo "$c is a commit of the branch's own ($subj)"; return 1
     else
@@ -301,7 +346,7 @@ carry() {
         done <<<"$b"
       fi
     fi
-  done < <(git log --first-parent --format='%H%x09%P%x09%ae%x09%s' "$v..$h")
+  done < <(git log --format='%H%x09%P%x09%ae%x09%s' "$v..$h" --not "$main")
   # What a carried bot commit wrote is no part of the branch's own diff.
   # Each path a bot commit added is excluded as a literal, not a pattern: a
   # pathspec is a glob, and git's default `*` matches across `/`, so one added
@@ -319,7 +364,7 @@ carry() {
   norm() { "${d[@]}" "$1" "$2" -- . ${x[@]+"${x[@]}"} | sed -e '/^index /d' -e 's/^@@ .*/@@/'; }
   cmp -s <(norm "$mv" "$v") <(norm "$mh" "$h") \
     || { echo "the branch's own diff differs: $mv..$v against $mh..$h"; return 1; }
-  echo "only automatic merges from $main, ci: commits and the autofix bot's own, and the branch's own diff compares equal"
+  echo "no branch-authored commit in the range, every merge the automatic one with its claim files a pure union of both sides, and the branch's own diff compares equal"
 }
 
 cleanup() {
@@ -1536,6 +1581,61 @@ carried "$H_TOUCH"; st $? 0 "CARRY: a merge from main that shifted the branch's
 carried "$H_CTX"; st $? 1 "NO CARRY: a merge from main that changed a context line of the branch's hunk"
 ( cd "$W/clone" && bash "$SELF" --carry "$V_A" "$H_A" origin/main ) >/dev/null 2>&1
 st $? 1 "NO CARRY: a driver the branch gave its own file, since drivers are read at main"
+# A merge of the branch's OWN previous head (#2876's shape, R10-REVIEW-CARRY):
+# update_pr.sh re-cuts a head this way, and the merge authors no commit. The
+# rule that refused it required every merge's second parent to be on main.
+( R="$W/recut"; throwaway_git_init "$R" -q -b main && cd "$R" || exit 2
+  printf 'one\ntwo\nthree\n' > f.txt; git add f.txt; git commit -qm m0
+  git checkout -qb fix; sed -i.bak 's/^two$/TWO/' f.txt; rm f.txt.bak; git commit -qam "fix: own"
+  git rev-parse HEAD > ../recut.v
+  git checkout -q main; printf 'main\n' > g.txt; git add g.txt; git commit -qm m1
+  git checkout -q --detach "$(cat ../recut.v)"; git merge -q --no-ff --no-edit main >/dev/null
+  git rev-parse HEAD > ../recut.m
+  git commit-tree "$(git rev-parse "$(cat ../recut.m)^{tree}")" -p "$(cat ../recut.v)" \
+    -p "$(cat ../recut.m)" -m "Merge commit 'x' into fix" > ../recut.h
+  bash "$SELF" --carry "$(cat ../recut.v)" "$(cat ../recut.h)" main ) > "$W/carry.out" 2>&1
+st $? 0 "CARRY: a re-cut merge of the branch's own previous head (#2876's shape)"
+# The claim files, where a driver refusal leaves a human deciding. Only a pure
+# union of both parents' lines changes nothing; a line dropped, added or
+# rewritten is content no review measured. The driver here refuses loudly, as
+# the real one does, so the check also pins that its refusal is not printed
+# beside a carry that passed.
+R="$W/claims"; throwaway_git_init "$R" -q -b main
+( cd "$R" || exit 2
+  git config merge.claimnotes.name claims
+  git config merge.claimnotes.driver 'sh -c "echo FIXTURE-DRIVER-REFUSED >&2; exit 1"'
+  mkdir -p tests/golden
+  printf 'tests/golden/claimed_drift.txt merge=claimnotes\n' > .gitattributes
+  printf '# note\nc1 # one\nc2 # two\n' > tests/golden/claimed_drift.txt
+  git add -A; git commit -qm main0
+  git checkout -qb fix
+  printf '# note\nc1 # one\nc2 # two\nc3 # three\n' > tests/golden/claimed_drift.txt
+  git commit -qam "fix: own"; git rev-parse HEAD > ../claims.v
+  git checkout -q main
+  printf '# note\nc1 # one\nc2 # two\nc4 # four\n' > tests/golden/claimed_drift.txt
+  git commit -qam "main: its own claim" )
+VC=$(cat "$W/claims.v")
+claim_merge() { # the resolved file as a printf format -> the merge commit
+  ( cd "$R" || exit 2
+    git checkout -q --detach "$VC"
+    git merge -q --no-ff --no-edit main >/dev/null 2>&1 || true
+    printf "$1" > tests/golden/claimed_drift.txt
+    git add tests/golden/claimed_drift.txt
+    git commit -q --no-edit
+    git rev-parse HEAD )
+}
+H_CU=$(claim_merge '# note\nc1 # one\nc2 # two\nc3 # three\nc4 # four\n')
+( cd "$R" && bash "$SELF" --carry "$VC" "$H_CU" main ) > "$W/carry.out" 2>&1
+st $? 0 "CARRY: a claim file resolved to the pure union of both sides"
+st "$(grep -c FIXTURE-DRIVER-REFUSED "$W/carry.out")" 0 "with the refusing driver's own words kept out of the carry"
+H_CD=$(claim_merge '# note\nc1 # one\nc2 # two\nc3 # three\n')
+( cd "$R" && bash "$SELF" --carry "$VC" "$H_CD" main ) > "$W/carry.out" 2>&1
+st $? 1 "NO CARRY: a claim resolution that drops a line"
+st "$(grep -c "union of its parents" "$W/carry.out")" 1 "refused as a claim resolution that is not the union"
+H_CR=$(claim_merge '# note\nc1 # one\nc2 # two\nc3 # three, reworded\nc4 # four\n')
+( cd "$R" && bash "$SELF" --carry "$VC" "$H_CR" main ) > "$W/carry.out" 2>&1
+st $? 1 "NO CARRY: a claim resolution that rewrites a line"
+st "$(grep -c "union of its parents" "$W/carry.out")" 1 "refused as a claim resolution that is not the union"
 EVV="$W/ev-v"; mkdir -p "$EVV"; printf 'fix review at head %s\n' "$V" > "$EVV/verdict.md"
 CARRYV="[$(comment 2 "Fix review: merge $V" "$APPR" NONE "evidence: $EVV")]"
 setpr "$H_MERGE"; mkcase carry open false "$H_MERGE" "$CARRYV"

