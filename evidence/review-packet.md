# Review packet #3089
head: b283c082dd86080164a684ae52905cdbdebd387a
base: fb0a6d5a30aa2e3a0b1ce4dd926c057d34a32fa8

Start here (fix-review.md). Re-read the live check state before a verdict: the digest is as read at render.

## Gate digest: green
CodeQL id=124858089612 success
arch-score / arch-score id=124873865036 success
arm id=124856360356 skipped
budget-raise-gate / budget-raise-gate id=124873864883 success
cancel-superseded id=124873864187 success
codeql id=124868359217 skipped
codeql / Analyze (actions) id=124873864979 success
codeql / Analyze (javascript-typescript) id=124873864938 success
codeql / Analyze (python) id=124873865470 success
gate id=124873865702 success
governance id=124868359098 skipped
governance / delivery-status id=124873865263 success
governance / delivery-status-publish id=124873865055 skipped
governance / env-matrix id=124873864844 success
governance / instrument-self-tests id=124873864944 success
governance / policy-docs id=124873864983 success
governance / record id=124873865282 skipped
governance / wave-script id=124873865495 success
hassfest id=124868359801 skipped
hassfest / hassfest id=124873864825 success
kernel-points id=124873865382 skipped
pr-contract / pr-contract id=124873867029 success
prelude id=124873864562 success
refresh id=124873899026 success
tests id=124868359743 skipped
tests / arch-instrument id=124873866260 success
tests / briefs id=124873865034 success
tests / browser id=124873865462 success
tests / ci-ratchet id=124873866002 skipped
tests / claims-autofix id=124873866195 skipped
tests / closure-scope id=124873864753 success
tests / closures id=124873865805 success
tests / closures-autofix id=124873866731 skipped
tests / coverage id=124873865863 success
tests / coverage-ratchet id=124873866360 success
tests / fast (3.14) id=124873866152 success
tests / graders-head-copy id=124873866325 success
tests / lane-proofs id=124873866438 success
tests / mutation id=124873865303 success
tests / mutation-autofix id=124873866585 skipped
tests / mutation-pins id=124873866575 skipped
tests / nightly-ha id=124873865852 skipped
tests / nightly-status id=124873864832 success
tests / replay id=124873866472 skipped
tests / typing id=124873865948 success
validate id=124868359346 skipped
validate / validate-hacs id=124873865407 success

## Refusals
none

## Advisories
hot-file: HPO_BUS_TRAIN_STATE is unset, so every merge verdict reads unboarded

## carry_audit at the head
NOTE stale tree: c2156686d6c2b728a334c307ef957ffebd28ea4f lacks origin/main 93d171a66c3bdd1d931ce5d91b7b4ddcf744dd58; roster read at origin/main
NOTE body item a8d598e9: R10-FLOW-BODY-ONLY
CARRY-AUDIT: 1 finding item(s): 1 routed, 0 unrouted, 0 bad destination(s)

## figure_lint at the head
ok         bash tools/audit/seat/cloud_relay.sh --self-test
             `tools/audit/seat/cloud_relay.sh` is in the tree at this head
  ok         bash tools/audit/seat/update_pr.sh --self-test
             `tools/audit/seat/update_pr.sh` is in the tree at this head
  ok         python3 dev/audit/harnesses/r10_seat_selftests_mutants.py cloud_relay-8 cloud_relay-9 cloud_relay-39 cloud_relay-40 cloud_relay-41 cloud_relay-42 cloud_relay-43 cloud_relay-44 cloud_relay-45 update_pr-1 update_pr-2 update_pr-3 update_pr-4 update_pr-5
             `dev/audit/harnesses/r10_seat_selftests_mutants.py` is in the tree at this head
  ok         python3 tests/closure.py select --diff $(git merge-base origin/main HEAD) --workdir "$D"
             `tests/closure.py` is in the tree at this head
  ok         PYTHONPATH=tests/hastub python3 tests/doc_claims.py
             `tests/doc_claims.py` is in the tree at this head
  ok         tests/env_drift.py --claims-only
             `tests/env_drift.py` is in the tree at this head
  ok         tests/closure.py selftest
             `tests/closure.py` is in the tree at this head
  ok         tests/layout.py
             `tests/layout.py` is in the tree at this head
  ok         tests/harness_headers.py
             `tests/harness_headers.py` is in the tree at this head
  ok         python3 tests/structure.py
             `tests/structure.py` is in the tree at this head
  ok         python3 tests/throwaway_git.py --check
             `tests/throwaway_git.py` is in the tree at this head
  ok         PREPR_SKIP_CLOSURES=1 tools/pr/prepr.sh <this body>
             `tools/pr/prepr.sh` is in the tree at this head

FIGURES: 12 resolved, 0 not verified, 0 refused

## Finder's harness: none named
### at the base
not run
### at the head
not run

## Mutation-ledger diff
none

## Three-dot diff
diff --git a/dev/audit/harnesses/r10_seat_selftests_mutants.py b/dev/audit/harnesses/r10_seat_selftests_mutants.py
index 2defad3e7..c21ce2e78 100644
--- a/dev/audit/harnesses/r10_seat_selftests_mutants.py
+++ b/dev/audit/harnesses/r10_seat_selftests_mutants.py
@@ -55,7 +55,7 @@ sys.path.insert(0, str(Path(__file__).resolve().parent))
 import mutant_guard  # noqa: E402 -- restores the mutated file on a kill (SIGTERM/SIGINT) and refuses a leftover mutant
 
 # cloud_relay.sh's handoff-arm lines the hold's ordering mutants swap
-_CONTAINED = 'git merge-base --is-ancestor "$hs" "$head" && continue\n'
+_CONTAINED = 'bonly=""; if git merge-base --is-ancestor "$hs" "$head"; then\n'
 _HOLD = 'if grep -qxF "$pr" <<< "$held_prs"; then echo "cloud_relay: HELD #$pr $hs"; continue; fi\n'
 _FAILED = 'if [ -f "$f" ] && grep -qxF "$topic $hs" "$f"; then continue; fi\n'
 
@@ -394,8 +394,9 @@ MUTANTS = [
      'level_set'),
     ("cloud_relay-7", "cloud_relay.sh", '  held) shift; held "$@"; exit $?;;\n', ''),
     # the two orderings the hold is a design choice of: after the contained test, before the failed ledger
-    ("cloud_relay-8", "cloud_relay.sh", _HOLD + "    " + _FAILED, _FAILED + "    " + _HOLD),
-    ("cloud_relay-9", "cloud_relay.sh", _CONTAINED + "    " + _HOLD, _HOLD + "    " + _CONTAINED),
+    # (the freeze now sits between hold and ledger, so the mutant puts a silent ledger test first)
+    ("cloud_relay-8", "cloud_relay.sh", "    " + _HOLD, "    " + _FAILED + "    " + _HOLD),
+    ("cloud_relay-9", "cloud_relay.sh", "    " + _CONTAINED, "    " + _HOLD + "    " + _CONTAINED),
     # the refusal is a level (#2547): the pre-merge event-log line, and a level never cleared
     ("cloud_relay-10", "cloud_relay.sh",
      'level_line handoff-hold-malformed "$(hold_file)" - >> "$state/cloud-level-hold.$$"; level_set',
@@ -436,6 +437,16 @@ MUTANTS = [
      'level_line handoff-update "refs/heads/handoff/$topic" "$hs" >> "$state/cloud-level-update.$$"; rm -rf'),
     ("cloud_relay-37", "cloud_relay.sh", 'why=$(grep REFUSE "$bd/update.out" | tail -n 1); [ -n "$why" ] ||', 'why=; [ -n "$why" ] ||'),
     ("cloud_relay-38", "cloud_relay.sh", 'END { print w }\' "$f.why" 2>/dev/null)', 'END { print w }\' /dev/null)'),
+    # R10-FLOW-BODY-ONLY part (c): a contained head's new body is applied body-only, once per body
+    # move, never on the seeding pass; a failed one is keyed on the body sha; #3037's review
+    # survivors M2 (the first REFUSE line read as the last) and M5 (no replay of the update's output).
+    ("cloud_relay-39", "cloud_relay.sh", '      grep -qxF "$topic $bs" "$bf" && continue\n', '      false && continue\n'),
+    ("cloud_relay-40", "cloud_relay.sh", '[ -z "$seed" ] || { echo "$topic $bs" >> "$bf"; continue; }', ':'),
+    ("cloud_relay-41", "cloud_relay.sh", '"$([ -n "$bonly" ] && echo - || echo "$hs")"', '"$hs"'),
+    ("cloud_relay-42", "cloud_relay.sh", 'why=$(grep REFUSE "$bd/update.out" | tail -n 1);', 'why=$(grep REFUSE "$bd/update.out" | head -n 1);'),
+    ("cloud_relay-43", "cloud_relay.sh", '    cat "$bd/update.out" >&2\n', ''),
+    ("cloud_relay-44", "cloud_relay.sh", '[ -z "$bonly" ] || key="$key $bs"', ':'),
+    ("cloud_relay-45", "cloud_relay.sh", 'rm -rf "$bd"; echo "$topic $bs" >> "$bf"  #', 'rm -rf "$bd"  #'),
     # R10-UPDATE-PR-SIGNALS (#2549): the update in the loop's own process group again
     ("cloud_relay-29", "cloud_relay.sh", '    pr_own_group "${upd[@]}" "$br"', '    "${upd[@]}" "$br"'),
     # R10-UPDATE-PR-SIGNALS carry 6 (P163): the STUCK andon's age, its bound, its held test, its wiring
@@ -446,6 +457,13 @@ MUTANTS = [
     ("cloud_relay-33", "cloud_relay.sh", 'confirm_arm; stuck_arm; [ -z "$loop" ]', 'confirm_arm; [ -z "$loop" ]'),
     ("ledger-1", "ledger.py", '"confirm-owed": "derived", "push-stuck": "derived",', '"confirm-owed": "derived",'),
     ("pr_args-1", "pr_args.sh", 'p = os.getppid(); start = int(time.time())', 'p = os.getppid(); start = 0'),
+    # R10-FLOW-BODY-ONLY parts (a) and (b), graded by update_pr.sh's step (pr_args.sh's fixture):
+    # main merged only when DIRTY or conflicting; an unmoved head is re-bodied with no push.
+    ("update_pr-1", "update_pr.sh", 'git merge-tree --write-tree origin/main HEAD >/dev/null 2>&1 || MAIN=1', 'MAIN=1'),
+    ("update_pr-2", "update_pr.sh", '[ "$ST" != DIRTY ] || MAIN=1', ':'),
+    ("update_pr-3", "update_pr.sh", 'if [ "$H" = "$LIVE" ]; then', 'if false; then'),
+    ("update_pr-4", "update_pr.sh", 'git merge-base --is-ancestor "$HT" "$H" || pr_refuse', 'true || pr_refuse'),
+    ("update_pr-5", "update_pr.sh", '[ "$rc" = 0 ] || pr_refuse "body-only:', 'true || pr_refuse "body-only:'),
     ("tick_loop-3", "tick_loop.sh", 'pass --confirm </dev/null', 'pass </dev/null'),
     # r10-flow-andon: ids are per file (tick_loop-N, heartbeat-N), never a new S number.
     ("tick_loop-1", "tick_loop.sh", '  timeout 60 bash "${HPO_TICK_HEARTBEAT:-$HERE/heartbeat.sh}" --once --message "TICK-PASS $now relay=$rrc tick=$trc"  # mut:heartbeat\n', ""),
diff --git a/dev/programme/delivery/3089.md b/dev/programme/delivery/3089.md
new file mode 100644
index 000000000..72ad69434
--- /dev/null
+++ b/dev/programme/delivery/3089.md
@@ -0,0 +1 @@
+- [#3089](https://github.com/tvofi/heatpump_optimizer/pull/3089) — **open**, R10-FLOW-BODY-ONLY: a handoff updates only with the body pushed for it; update_pr merges main only when dirty, body-only mode (R10-FLOW-BODY-ONLY)
diff --git a/tools/audit/seat/cloud_relay.sh b/tools/audit/seat/cloud_relay.sh
index 12dd735b8..d6b38b872 100644
--- a/tools/audit/seat/cloud_relay.sh
+++ b/tools/audit/seat/cloud_relay.sh
@@ -390,7 +390,12 @@ review_freeze() { # <pr> <head> <verdict refs file>: prints VERDICT, REVIEW or U
 }
 handoff_arm() { # one pass over open PRs; updates one whose handoff is ahead of its head
   local state=${HPO_STATE_DIR:-$HOME/.local/state/hpo} repo=${HPO_RELAY_REPO:-tvofi/heatpump_optimizer} f pr br head topic hs bs bd body iss nh nonce urc held_prs released upd why code
+  local bf bonly key seed=""
   f=$state/cloud-handoff-failed; mkdir -p "$state"
+  # BODY-ONLY (R10-FLOW-BODY-ONLY part (c)): `<topic> <body sha>` per body this relay has applied, by an
+  # update or a body-only run. With no file yet, this pass records every contained topic's body as
+  # applied (the seed) and runs nothing, so the first pass does not re-body every open PR.
+  bf=$state/cloud-handoff-bodied; [ -f "$bf" ] || seed=1; touch "$bf"
   : > "$state/cloud-level-hold.$$"   # the refusal is a level: owed while the file is malformed, gone once it is not
   held_prs=$(hold_list) || { level_line handoff-hold-malformed "$(hold_file)" - >> "$state/cloud-level-hold.$$"; level_set handoff-hold-malformed "$state/cloud-level-hold.$$"; return 2; }
   released=$(hold_list "$(release_file)") || { level_line handoff-hold-malformed "$(release_file)" - >> "$state/cloud-level-hold.$$"; level_set handoff-hold-malformed "$state/cloud-level-hold.$$"; return 2; }
@@ -413,14 +418,22 @@ handoff_arm() { # one pass over open PRs; updates one whose handoff is ahead of
     [ -n "$hs" ] && [ -n "$bs" ] || continue
     git fetch -q origin "refs/heads/handoff/$topic" "refs/heads/$br" 2>/dev/null
     git cat-file -e "$hs^{commit}" 2>/dev/null && git cat-file -e "$head^{commit}" 2>/dev/null || continue
-    git merge-base --is-ancestor "$hs" "$head" && continue
+    # A head holding the handoff tip has its code; only a body this relay has not applied moves it,
+    # and that move is body-only: update_pr.sh with code `-`, which PATCHes the body and pushes nothing.
+    bonly=""; if git merge-base --is-ancestor "$hs" "$head"; then
+      grep -qxF "$topic $bs" "$bf" && continue
+      [ -z "$seed" ] || { echo "$topic $bs" >> "$bf"; continue; }
+      bonly=1; fi
     if grep -qxF "$pr" <<< "$held_prs"; then echo "cloud_relay: HELD #$pr $hs"; continue; fi
-    if ! grep -qxF "$pr" <<< "$released" && why=$(review_freeze "$pr" "$head" "$state/cloud-vrefs.$$"); then
+    # a body-only move leaves the head under review where it is, so no review freezes it
+    if [ -z "$bonly" ] && ! grep -qxF "$pr" <<< "$released" && why=$(review_freeze "$pr" "$head" "$state/cloud-vrefs.$$"); then
       echo "cloud_relay: HELD-$why #$pr $hs (head $head under review; merge it, or list #$pr in $(release_file) and re-dispatch)"
       level_line handoff-held "refs/heads/handoff/$topic" "$hs" "#$pr $why" >> "$state/cloud-level-held.$$"; continue
     fi
-    if [ -f "$f" ] && grep -qxF "$topic $hs" "$f"; then
-      why=$(awk -F'\t' -v k="$topic $hs" '$1 == k { w = $2 } END { print w }' "$f.why" 2>/dev/null)
+    # A failed body-only run is keyed on the body sha too (carry 4, P22): a new body re-triggers it.
+    key="$topic $hs"; [ -z "$bonly" ] || key="$key $bs"
+    if [ -f "$f" ] && grep -qxF "$key" "$f"; then
+      why=$(awk -F'\t' -v k="$key" '$1 == k { w = $2 } END { print w }' "$f.why" 2>/dev/null)
       level_line handoff-update "refs/heads/handoff/$topic" "$hs" "$why" >> "$state/cloud-level-update.$$"; continue
     fi
     # The body goes in a directory of this run's own, under the state dir: a file directly in a
@@ -438,8 +451,12 @@ handoff_arm() { # one pass over open PRs; updates one whose handoff is ahead of
       echo "cloud_relay: STALE handoff-body/$topic names ${code:0:12}, handoff/$topic is at ${hs:0:12}; the next pass retries" >&2
       level_line handoff-body-stale "refs/heads/handoff/$topic" "$hs" "body names ${code:0:12}" >> "$state/cloud-level-stale.$$"; rm -rf "$bd"; continue
     fi
+    # A body-only move is made with the body pushed for this head: one with no `Code:` line, which
+    # predates the trailer, is recorded as applied and left alone, as before this arm existed.
+    if [ -n "$bonly" ] && [ -z "$code" ]; then echo "$topic $bs" >> "$bf"; rm -rf "$bd"; continue; fi
     iss=$(grep -oiE '\b(close[sd]?|fix(e[sd])?|resolve[sd]?)[: ]+#[0-9]+' "$body" | grep -oE '[0-9]+' | sort -un | tr '\n' ' ')
-    echo "$(date -u +%FT%TZ) cloud_relay: handoff/$topic $hs is ahead of #$pr $head; updating"
+    if [ -n "$bonly" ]; then echo "$(date -u +%FT%TZ) cloud_relay: handoff-body/$topic $bs is new for #$pr $head; body-only"
+    else echo "$(date -u +%FT%TZ) cloud_relay: handoff/$topic $hs is ahead of #$pr $head; updating"; fi
     # The update is the reap's lead (pr_args.sh's PR_REAP_LEAD): a stopped relay TERMs it alone,
     # so update_pr.sh ends its push before it frees the branch lock, and reaps what is left after.
     # It runs in a process group of its own (pr_own_group), so a signal to the loop's whole group
@@ -448,7 +465,7 @@ handoff_arm() { # one pass over open PRs; updates one whose handoff is ahead of
     # One launch for both routes, so the self-test's stub runs the production launch line.
     urc=0; upd=(bash "$HERE/update_pr.sh"); [ -z "${HPO_RELAY_UPDATE:-}" ] || upd=("$HPO_RELAY_UPDATE")
     # Its output is kept until it ends, so a failure records its reason: the last REFUSE line, else the last line.
-    pr_own_group "${upd[@]}" "$br" "$hs" "$body" $iss > "$bd/update.out" 2>&1 &
+    pr_own_group "${upd[@]}" "$br" "$([ -n "$bonly" ] && echo - || echo "$hs")" "$body" $iss > "$bd/update.out" 2>&1 &
     PR_REAP_LEAD=$!; wait "$PR_REAP_LEAD" || urc=$?
     cat "$bd/update.out" >&2
     # 75 is update_pr.sh's BUSY: another run (the orchestrator's) holds this branch's worktree. Not
@@ -456,10 +473,11 @@ handoff_arm() { # one pass over open PRs; updates one whose handoff is ahead of
     if [ "$urc" = 75 ]; then echo "cloud_relay: update_pr busy on $br; the next pass retries" >&2; rm -rf "$bd"; continue; fi
     if [ "$urc" != 0 ]; then
       why=$(grep REFUSE "$bd/update.out" | tail -n 1); [ -n "$why" ] || why=$(last_line "$(cat "$bd/update.out")")
-      echo "$topic $hs" >> "$f"; printf '%s %s\t%s\n' "$topic" "$hs" "$why" >> "$f.why"
+      echo "$key" >> "$f"; printf '%s\t%s\n' "$key" "$why" >> "$f.why"
       level_line handoff-update "refs/heads/handoff/$topic" "$hs" "$why" >> "$state/cloud-level-update.$$"; rm -rf "$bd"; continue
     fi
-    rm -rf "$bd"
+    rm -rf "$bd"; echo "$topic $bs" >> "$bf"  # this body is applied: a later pass leaves it alone
+    if [ -n "$bonly" ]; then echo "cloud_relay: BODIED #$pr $head with handoff-body/$topic $bs" >&2; continue; fi
     nh=$( { if [ -n "${HPO_RELAY_PRS:-}" ]; then "$HPO_RELAY_PRS"; else gh pr list -R "$repo" --state open --limit 100 --json number,headRefName,headRefOid \
       -q '.[] | [.number, .headRefName, .headRefOid] | @tsv'; fi; } | awk -F'\t' -v p="$pr" '$1 == p { print $3; exit }')
     if [ -n "${HPO_RELAY_APPROVE:-}" ]; then "$HPO_RELAY_APPROVE" "$br"; else bash "$HERE/../../pr/approve_held_runs.sh" "$repo" "$br"; fi >&2 \
@@ -964,6 +982,34 @@ EOF
   bodyc; rm -f "$t/hupdated"; handoff_arm >/dev/null 2>&1
   chk "a body with no Code: line updates as before (null control)" 0 grep -q "^fix/topic-a-pr $HS2\$" "$t/hupdated"
   rm -f "$t/hupdated"
+  # R10-FLOW-BODY-ONLY part (c): a head holding its handoff tip is re-bodied once per body move, with
+  # code `-` (update_pr.sh's body-only mode), and never on the pass that seeds the bodied record.
+  BF=$t/state/cloud-handoff-bodied; bsha() { git -C "$t/o.git" rev-parse refs/heads/handoff-body/topic-a; }
+  printf '%s\t%s\t%s\n' 41 fix/topic-a-pr "$HS2" > "$prs"; : > "$LOG"; bodyc "$HS2"; rm -f "$BF"; handoff_arm >/dev/null 2>&1
+  chk "a pass with no bodied record seeds it with the contained topic's body and runs nothing" 0 test ! -e "$t/hupdated" -a "$(cat "$BF")" = "topic-a $(bsha)"
+  handoff_arm >/dev/null 2>&1
+  chk "a body already applied runs nothing on the next pass (null control)" 0 test ! -e "$t/hupdated"
+  bodyc "$HS2"; handoff_arm >/dev/null 2>&1; handoff_arm >/dev/null 2>&1
+  chk "a new body for a head holding its handoff runs update_pr once, body-only (code -)" 0 test "$(cat "$t/hupdated")" = "fix/topic-a-pr -"
+  bodyc "$HS2"; handoff_arm >/dev/null 2>&1
+  chk "the next body move runs it once more" 0 test "$(grep -cx "fix/topic-a-pr -" "$t/hupdated")" = 2
+  rm -f "$t/hupdated"; bodyc; handoff_arm >/dev/null 2>&1
+  chk "a contained body with no Code: line runs nothing, and is recorded applied" 0 test ! -e "$t/hupdated" -a "$(tail -n 1 "$BF")" = "topic-a $(bsha)"
+  bodyc "$HS"; ho=$(handoff_arm 2>&1)
+  chk "a contained body naming another code head runs nothing and is owed stale" 0 test ! -e "$t/hupdated" -a "$(grep -c "handoff-body-stale refs/heads/handoff/topic-a $HS2 body names ${HS:0:12}\$" "$LOG.level")" = 1
+  # a failed body-only run: its reason is the LAST REFUSE line (#3037 review M2), its output is
+  # replayed to the relay's stderr (M5), it is keyed on the body sha, and a new body re-triggers it
+  r2=$t/r2.sh; printf '#!/bin/sh\necho "$1 $2" >> "%s/hupdated"\necho "update_pr: REFUSE: first"\necho "update_pr: REFUSE: second"\necho "update_pr: replayed tail"\nexit 1\n' "$t" > "$r2"; chmod +x "$r2"; HPO_RELAY_UPDATE=$r2
+  rm -f "$t/state/cloud-handoff-failed" "$t/state/cloud-handoff-failed.why"; bodyc "$HS2"; ho=$(handoff_arm 2>&1)
+  chk "a failed update's handoff-update line ends in the last of its REFUSE lines" 0 grep -q "^OWED .* handoff-update refs/heads/handoff/topic-a $HS2 update_pr: REFUSE: second\$" "$LOG.level"
+  chk "and the update's whole output reaches the relay's stderr" 0 grep -qx "update_pr: replayed tail" <<< "$ho"
+  chk "a failed body-only run is recorded on topic, code and body sha" 0 test "$(cat "$t/state/cloud-handoff-failed")" = "topic-a $HS2 $(bsha)"
+  handoff_arm >/dev/null 2>&1
+  chk "and not retried on the next pass, which keeps its reason" 0 test "$(grep -c . "$t/hupdated")-$(grep -c "handoff-update refs/heads/handoff/topic-a $HS2 update_pr: REFUSE: second\$" "$LOG.level")" = 1-1
+  bodyc "$HS2"; handoff_arm >/dev/null 2>&1
+  chk "a new body re-triggers it" 0 test "$(grep -c . "$t/hupdated")" = 2
+  HPO_RELAY_UPDATE=$hu; rm -f "$t/hupdated" "$t/state/cloud-handoff-failed" "$t/state/cloud-handoff-failed.why"
+  printf '%s\t%s\t%s\n' 41 fix/topic-a-pr "$PRH" > "$prs"; : > "$LOG"
   # handoff refs with no open PR are OWED on every pass until disposed
   LV=$LOG.level; : > "$LOG"; rm -f "$LV"; hc topic-b; mkref handoff/topic-b; OB=$(git -C "$t/pr" rev-parse HEAD)
   handoff_arm >/dev/null 2>&1
diff --git a/tools/audit/seat/instruments/body_push.sh.md b/tools/audit/seat/instruments/body_push.sh.md
index cee2b6d4f..8f8531856 100644
--- a/tools/audit/seat/instruments/body_push.sh.md
+++ b/tools/audit/seat/instruments/body_push.sh.md
@@ -12,3 +12,9 @@
   non-fast-forward — a rewrite is never forced through; the body commit it
   wrote is read back through `ref_privacy.py guard --commits`, message and
   identity, before the push.
+  A PR body's commit (a `handoff/<topic>` exists) ends its message in a
+  trailer line `Code: <handoff/<topic> tip>`, the sha the script has proved
+  equal to the checkout's HEAD; a result body writes none. `cloud_relay.sh`'s
+  handoff arm reads it: a body naming another head is held as
+  `handoff-body-stale`, and a body naming a tip the PR head already holds is
+  applied body-only (`update_pr.sh` with code `-`).
diff --git a/tools/audit/seat/instruments/cloud_relay.sh.md b/tools/audit/seat/instruments/cloud_relay.sh.md
index e8a39a7a5..b9a4356ab 100644
--- a/tools/audit/seat/instruments/cloud_relay.sh.md
+++ b/tools/audit/seat/instruments/cloud_relay.sh.md
@@ -112,10 +112,26 @@
   `OWED <utc> handoff-held <ref> <tip> #<pr> <why>` in `<log>.level`;
   `cloud-handoff-release` (the hold file's grammar) releases a listed PR from the
   freeze, never from the hold, for new work that voids a merge verdict.
-  A handoff already inside its PR, or with no body ref, does nothing; a failed
-  update is noted in `cloud-handoff-failed` by `<topic> <code-sha>`, owed as
-  `OWED <utc> handoff-update <ref> <sha>` in `<log>.level` while that entry
-  matches the handoff's tip, and retried only when the handoff moves. An update that
+  A handoff with no body ref does nothing. A body names the code head it was
+  pushed for in its commit's `Code: <sha>` trailer (`body_push.sh`, V147): one
+  naming another head than the handoff tip runs no update, is owed as
+  `OWED <utc> handoff-body-stale <ref> <tip> body names <sha12>`, records no
+  failure and is retried next pass; a body with no `Code:` line updates as
+  before. A handoff already inside its PR is body-only (R10-FLOW-BODY-ONLY):
+  its body, when this relay has not yet applied it and its `Code:` names the
+  tip, goes to `update_pr.sh <branch> - <body>`, which PATCHes the body and
+  pushes nothing, once per body move. `cloud-handoff-bodied` holds
+  `<topic> <body-sha>` for every body applied, by an update or body-only; a pass
+  that finds no such file records every contained topic's body and runs
+  nothing (the seed), and a contained body with no `Code:` line is recorded
+  and left alone. A failed update is noted in `cloud-handoff-failed` by
+  `<topic> <code-sha>` (a body-only one by `<topic> <code-sha> <body-sha>`, so
+  a new body re-triggers it), its reason, the update's last `REFUSE` line else
+  its last line, kept beside it in `cloud-handoff-failed.why` (tab-separated),
+  owed as `OWED <utc> handoff-update <ref> <sha> <why>` in `<log>.level` while
+  that entry matches, and retried only when the handoff (or body) moves. The
+  update's output is held in a file until it ends, then replayed to the
+  relay's stderr. An update that
   exits 75 is BUSY (another `open_pr.sh` or `update_pr.sh` run holds the branch's
   `upd-<branch>.lock`, typically the orchestrator's own update of that PR, or an `open_pr.sh` between its two pushes): it is
   not recorded, and the next pass retries it. The update runs in a process
diff --git a/tools/audit/seat/instruments/update_pr.sh.md b/tools/audit/seat/instruments/update_pr.sh.md
index 5e33ba2b4..31ad7edf5 100644
--- a/tools/audit/seat/instruments/update_pr.sh.md
+++ b/tools/audit/seat/instruments/update_pr.sh.md
@@ -1,12 +1,21 @@
 # `update_pr.sh`
 
 - `update_pr.sh` — brings an open PR branch to its head + a code SHA (merge) +
-  origin/main (merge), adds the PR's own delivery row when the head lacks
-  it (`delivery_row.sh`), prefixes ## Head with what happened, pushes as
-  `hpo-author`. With code sha `-` it asks `app_push.sh --row-only`, so a push
-  that only adds the row takes the body contract instead of the full prepr,
-  and prints app_push's `ROW-ONLY:` line naming which ran and why.
-  When: updating a PR after review prep or a main merge.
+  origin/main (merged only when the PR is `DIRTY` or `git merge-tree
+  --write-tree origin/main HEAD` conflicts: ruling R4), adds the PR's own
+  delivery row when the head lacks it (`delivery_row.sh`), prefixes ## Head
+  with what happened, pushes as `hpo-author`. A head that is the live head
+  plus one commit asks `app_push.sh --row-only`, so a push that only adds the
+  row takes the body contract instead of the full prepr, and prints
+  app_push's `ROW-ONLY:` line naming which ran and why. A head the run leaves
+  exactly where it was (the code sha already in it, or `-`; main clean; the
+  row present) is BODY-ONLY: nothing is pushed, `body_patch.sh` runs the body
+  contract at that head from the run's own worktree and PATCHes the body, and
+  `update_pr: BODY-ONLY: #<n> at <sha>` says so; body_patch's refusal (a head
+  that moved) is the run's. With `-`, a `handoff/<topic>` tip the head lacks
+  refuses (pass it as the code sha). `cloud_relay.sh` calls this mode once per
+  body move of a PR whose head holds its handoff.
+  When: updating a PR after review prep or a main merge, or re-bodying it.
   Refusal: as `remerge_main.sh` — a conflict stops, it is never resolved
   silently; no open PR at the branch stops before any push. Up front, each an
   `update_pr: REFUSE:` line (`pr_args.sh`): fewer than three arguments; a
diff --git a/tools/audit/seat/pr_args.sh b/tools/audit/seat/pr_args.sh
index cab8ab07b..57ca8312b 100644
--- a/tools/audit/seat/pr_args.sh
+++ b/tools/audit/seat/pr_args.sh
@@ -1149,6 +1149,63 @@ STUB
   ck "  mutant mut:release (its line deleted): the opened PR's worktree still holds its branch" $?
   racerun oprowonly; [ "$(sed -n 2p "$t/argv" | cut -d' ' -f1)" = tvofi/heatpump_optimizer ]
   ck "  mutant mut:oprowonly (its line deleted): the row push runs the full prepr" $?
+  # R10-FLOW-BODY-ONLY parts (a) and (b), ruling R4: update_pr.sh merges origin/main only when the PR
+  # is DIRTY or the merge would conflict, and a head the run leaves unmoved is re-bodied by
+  # body_patch.sh (here a stub, HPO_BODY_PATCH) with no push. handoff/v carries a push stub that
+  # records its arguments and pushes; fix/v starts at handoff/v's tip, without its row.
+  if [ ! -e "$t/fixv" ]; then
+    git -C "$o" checkout -q -b handoff/v "$base" && mkdir -p "$o/tools/pr" && printf 'v\n' > "$o/v" \
+      && printf '#!/bin/bash\nprintf "%%s\\n" "$*" >> "$STUB_DIR/argv"; [ "$1" != --row-only ] || shift\ngit -C "$2" push -q origin "$3" || exit 1; echo "app_push: PUSHED"\n' > "$o/tools/pr/app_push.sh" \
+      && git -C "$o" add v tools/pr/app_push.sh && git -C "$o" commit -q -m "code v" \
+      && git -C "$o" branch fix/v HEAD && git -C "$o" checkout -q main && touch "$t/fixv"
+  fi
+  codeV=$(git -C "$o" rev-parse handoff/v); wsd=$t/vstub; rm -rf "$wsd"; mkdir -p "$wsd"
+  printf '#!/bin/sh\ncase "$*" in *--head*) echo 5 ;; *mergeStateStatus*) [ -e "%s/dirty" ] && echo DIRTY || echo CLEAN ;; "pr view"*) echo "a title" ;; *) exit 99 ;; esac\n' "$wsd" > "$t/bin/gh"
+  printf '#!/bin/bash\nprintf "%%s %%s\\n" "$(pwd -P)" "$*" >> "%s/bp"\n[ ! -e "%s/bpmoved" ] || { echo "body_patch: REFUSE: the head moved"; exit 1; }\necho "body_patch: OK"\n' "$wsd" "$wsd" > "$wsd/bp.sh"
+  upd() { # <mutant> <code sha|->: update_pr.sh fix/v; origin's fix/v before and after in $t/vbefore, $t/vafter
+    git -C "$o" rev-parse fix/v > "$t/vbefore"; cp "$t/body.md" "$t/bv.md"
+    STUB_DIR=$wsd HPO_BODY_PATCH=$wsd/bp.sh run "$1" update_pr.sh fix/v "$2" "$t/bv.md"
+    git -C "$o" rev-parse fix/v > "$t/vafter"
+  }
+  pushes() { cat "$wsd/argv" 2>/dev/null | wc -l | tr -d ' '; }
+  bpcalls() { cat "$wsd/bp" 2>/dev/null | wc -l | tr -d ' '; }
+  upd - -
+  [ "$(cat "$t/rc")" = 0 ] && [ "$(pushes)" = 1 ] && [ "$(cut -d' ' -f1 "$wsd/argv")" = --row-only ] && [ "$(bpcalls)" = 0 ] \
+    && git -C "$o" cat-file -e fix/v:dev/programme/delivery/5.md
+  ck "update_pr: a head that only gains its row pushes once, asking for --row-only" $?
+  upd - -
+  [ "$(cat "$t/rc")" = 0 ] && [ "$(cat "$t/vbefore")" = "$(cat "$t/vafter")" ] && [ "$(pushes)" = 1 ] && [ "$(bpcalls)" = 1 ] \
+    && grep -qF "update_pr: BODY-ONLY: #5 at $(cat "$t/vafter"), the head unmoved" "$t/out" \
+    && grep -qF "$(cat "$t/vafter") " "$wsd/bp" && grep -qF "/pr/upd-fix-v --repo tvofi/heatpump_optimizer 5 $(cat "$t/vafter") " "$wsd/bp" \
+    && grep -qF "is this PR's head, unchanged" "$t/bv.md"
+  ck "update_pr: a body-only run (code -, row present) PATCHes the body at the unmoved head from its worktree and pushes nothing" $?
+  upd - "$codeV"
+  [ "$(cat "$t/rc")" = 0 ] && [ "$(cat "$t/vbefore")" = "$(cat "$t/vafter")" ] && [ "$(pushes)" = 1 ] && [ "$(bpcalls)" = 2 ]
+  ck "update_pr: a code sha the head already holds runs no push and no prepr: body-only (card 4's re-run)" $?
+  printf 'm\n' > "$o/mainw" && git -C "$o" add mainw && git -C "$o" commit -q -m "main: mainw"
+  upd - -
+  [ "$(cat "$t/rc")" = 0 ] && [ "$(cat "$t/vbefore")" = "$(cat "$t/vafter")" ] && [ "$(pushes)" = 1 ] && [ "$(bpcalls)" = 3 ] \
+    && ! git -C "$o" merge-base --is-ancestor main fix/v
+  ck "update_pr: with main ahead and a clean merge-tree, the head sha is identical before and after (R4)" $?
+  touch "$wsd/bpmoved"; upd - -
+  [ "$(cat "$t/rc")" = 1 ] && grep -qF "update_pr: REFUSE: body-only: body_patch.sh refused #5" "$t/out" \
+    && grep -qF "body_patch: REFUSE: the head moved" "$t/out" && [ "$(pushes)" = 1 ]
+  ck "update_pr: a body-only run on a moved head refuses, with body_patch.sh's reason, and pushes nothing" $?
+  rm -f "$wsd/bpmoved"
+  git -C "$o" checkout -q handoff/v && printf 'v2\n' > "$o/v" && git -C "$o" commit -q -am "code v2" && git -C "$o" checkout -q main
+  codeV2=$(git -C "$o" rev-parse handoff/v)
+  upd - -
+  [ "$(cat "$t/rc")" = 1 ] && grep -qF "update_pr: REFUSE: handoff/v ($codeV2) is not in the head" "$t/out" && [ "$(bpcalls)" = 4 ]
+  ck "update_pr: code - with a handoff tip the head lacks refuses, and patches no body" $?
+  upd - "$codeV2"
+  [ "$(cat "$t/rc")" = 0 ] && [ "$(pushes)" = 2 ] && [ "$(sed -n 2p "$wsd/argv" | cut -d' ' -f1)" = tvofi/heatpump_optimizer ] \
+    && git -C "$o" merge-base --is-ancestor "$codeV2" fix/v && ! git -C "$o" merge-base --is-ancestor main fix/v
+  ck "null control: a new code sha is merged and pushed through the full prepr, main still unmerged" $?
+  touch "$wsd/dirty"; upd - -
+  [ "$(cat "$t/rc")" = 0 ] && [ "$(pushes)" = 3 ] && git -C "$o" merge-base --is-ancestor main fix/v \
+    && [ "$(sed -n 3p "$wsd/argv" | cut -d' ' -f1)" = tvofi/heatpump_optimizer ] && grep -qF "merges origin/main" "$t/bv.md"
+  ck "update_pr: a DIRTY pull request still absorbs main, through the full prepr" $?
+  printf '#!/bin/sh\n[ -e "%s/gh.fail" ] && { echo "HTTP 403" >&2; exit 1; }\ncase "$*" in *--head*) echo 5 ;; "pr list"*) cat "%s/prs.json" ;; "pr view"*) echo "a title" ;; "pr edit"*|"pr ready"*) exit 0 ;; *) exit 99 ;; esac\n' "$t" "$t" > "$t/bin/gh"
   # A refused row push (#2625, #2629: prepr refused p2 on a red CI reported after p1) left the row
   # commit unpushed in the opener's worktree, on the branch, and update_pr.sh refused it as unpushed
   # work; the PR stayed open without its row. The opener now returns its worktree to the pushed head,
@@ -1282,8 +1339,9 @@ GH
   unpushed - 0
   [ "$(cat "$t/attached")" = detached ] && grep -qF "update_pr: REFUSE: the push failed" "$t/outu" && ! grep -qF "(unpushed work" "$t/outu"
   ck "null control: a worktree whose HEAD origin has is detached as before, and the run reaches its push" $?
-  # The row-only arm (R10-ROW-ONLY-UPDATE): with code sha `-` update_pr.sh asks app_push.sh for
-  # --row-only, whose own verdict decides whether a full prepr is owed; a code sha never asks.
+  # The row-only arm (R10-ROW-ONLY-UPDATE): a head that is the live head plus one commit (here code
+  # sha `-` adding the row) asks app_push.sh for --row-only, whose own verdict decides whether a
+  # full prepr is owed; a head merging new code never asks.
   # Branch fix/w carries an app_push.sh stub that records its arguments, then fails the push.
   if [ ! -e "$t/fixw" ]; then
     git -C "$o" checkout -q -b fix/w "$base" && mkdir -p "$o/tools/pr" \
@@ -1297,7 +1355,7 @@ GH
   rowrun rowonly -; [[ $(cat "$t/argv" 2>/dev/null) == "tvofi/heatpump_optimizer "* ]]
   ck "  mutant mut:rowonly (its line deleted): code sha '-' runs the full prepr" $?
   rowrun - "$code"; [[ $(cat "$t/argv" 2>/dev/null) == "tvofi/heatpump_optimizer "* ]]
-  ck "null control: a code sha never asks for --row-only, so its push runs the full prepr" $?
+  ck "null control: a code sha the head lacks is merged and never asks for --row-only, so its push runs the full prepr" $?
   for c in "$code" -; do
     cp "$t/body.md" "$t/b.md"; run - update_pr.sh fix/x "$c" "$t/b.md"
     [ "$(cat "$t/rc")" != 0 ] && ! grep -q 'REFUSE: code sha\|REFUSE: origin has\|argument(s)' "$t/out" \
diff --git a/tools/audit/seat/update_pr.sh b/tools/audit/seat/update_pr.sh
index 0e7a671db..e7be8de02 100755
--- a/tools/audit/seat/update_pr.sh
+++ b/tools/audit/seat/update_pr.sh
@@ -1,5 +1,6 @@
 #!/bin/bash
-# updatepr.sh <branch> <code-sha|-> <body-file> [issues...]: bring the PR branch to: its current head + code-sha (merge) + origin/main (merge),
+# updatepr.sh <branch> <code-sha|-> <body-file> [issues...]: bring the PR branch to: its current head + code-sha (merge) + origin/main
+# (merged only when the PR is DIRTY or `git merge-tree --write-tree origin/main HEAD` conflicts: ruling R4, K12),
 # prefix ## Head with what happened, push as hpo-author. Prints HEAD. Uses a private worktree
 # $HPO_STATE_DIR/pr/upd-<branch> (default ~/.local/state/hpo); PATH as open_pr.sh's.
 # A head without the PR's own delivery row gains it (delivery_row.sh's ensure_row, open_pr.sh's
@@ -15,17 +16,24 @@
 # (pr_args.sh's pr_exit_trap); the lock is freed only once that push has ended, a SIGKILLed run's too (pr_push_hold).
 # The lock's holder leaves $WT detached once that push has ended, not holding the branch, a SIGKILLed
 # run's too; a merge the run left stopped on a conflict is aborted first (P276).
-# With code sha `-` the push asks app_push.sh for --row-only (R10-ROW-ONLY-UPDATE): app_push.sh's
-# own verdict replaces the full prepr with the body contract when the push is exactly this PR's
-# row added onto its live head under the body plus this run's note, and runs prepr otherwise; its
-# `app_push: ROW-ONLY:` line, naming which and why, is printed here. A code sha never asks.
+# A head that is exactly the live head plus one commit asks app_push.sh for --row-only
+# (R10-ROW-ONLY-UPDATE): app_push.sh's own verdict replaces the full prepr with the body contract
+# when the push is exactly this PR's row added onto its live head under the body plus this run's
+# note, and runs prepr otherwise; its `app_push: ROW-ONLY:` line, naming which and why, is printed
+# here. A head that merges new code, or main, never asks.
+# BODY-ONLY (R10-FLOW-BODY-ONLY): when the merges and the row leave the head exactly the live head
+# (the code sha already in it, or `-`; main clean; the row present), nothing is pushed:
+# body_patch.sh runs the body contract at that head from this run's worktree and PATCHes the body,
+# and `update_pr: BODY-ONLY:` says so. With `-`, a handoff/<topic> tip the head lacks refuses
+# (pass it as the code sha). pr-contract re-runs on the `edited` event. HPO_BODY_PATCH replaces
+# body_patch.sh (the self-test's stub).
 # --self-test runs delivery_row.sh's self-test, then pr_args.sh's, under pr_args.sh's self-test bound.
 . "$(dirname -- "$0")/delivery_row.sh"; . "$(dirname -- "$0")/pr_args.sh"
 [ "${1:-}" = --self-test ] && { [ -n "${PR_BOUND:-}" ] || pr_bounded update_pr bash "$0" --self-test  # pr_args.sh's bound
   bash "$(dirname -- "$0")/delivery_row.sh" --self-test; r=$?
   bash "$(dirname -- "$0")/pr_args.sh" --self-test || exit 1; exit $r; }
 PR_NAME=update_pr; pr_trap; unset GIT_AUTHOR_NAME; export PATH=${HPO_STATE_DIR:-$HOME/.local/state/hpo}/venv-ci/bin:$PATH
-PRT=$(cd "$(dirname -- "$0")/../../pr" && pwd)  # head_note.py: each ## Head note goes under the heading, not a quote of it
+SEAT=$(cd "$(dirname -- "$0")" && pwd); PRT=$(cd "$(dirname -- "$0")/../../pr" && pwd)  # head_note.py: each ## Head note goes under the heading, not a quote of it
 pr_need_args 3 $# "update_pr.sh <branch> <code-sha|-> <body-file> [issues...]"
 [ "$2" = - ] || pr_code_sha_shape "$2"
 [ -f "$3" ] || pr_refuse "no body file at $3"
@@ -58,30 +66,61 @@ git worktree list | grep -F "[$BR]" | grep -vqF "$WT " && { echo "branch $BR che
 [ -d $WT ] && git worktree remove --force $WT
 git worktree add -q -B "$BR" $WT origin/$BR; cd $WT
 G="git -c user.name=tvofi -c user.email=70032254+tvofi@users.noreply.github.com"
+LIVE=$(git rev-parse HEAD)  # the pull request's head as origin holds it
+N=${PR_N:-$(gh pr list -R $R --head "$BR" --state open --json number -q '.[0].number')}
+[ -n "$N" ] || { echo "no open pull request at $BR, so no row to check"; exit 1; }
 NOTE=""
 if [ "$C" != "-" ]; then $G merge -q --no-edit $C; NOTE="merges the authored code head \`$C\`"; fi
 OLD=$(git rev-parse HEAD)
-$G merge -q --no-edit origin/main
+# Ruling R4 (Lean flow K12): origin/main is merged only when the pull request is DIRTY or the merge
+# would conflict; a clean head is not moved to absorb main (fixer.md step 6, nudge.md step 9). An
+# unread merge state is not DIRTY: the merge-tree reading below is the local proof either way.
+ST=$(gh pr view "$N" -R $R --json mergeStateStatus -q .mergeStateStatus 2>/dev/null) || ST=unread
+MAIN=""
+git merge-tree --write-tree origin/main HEAD >/dev/null 2>&1 || MAIN=1
+[ "$ST" != DIRTY ] || MAIN=1
+[ -z "$MAIN" ] || $G merge -q --no-edit origin/main
 # Keys taken at the code sha, or at the previous head when none was given, re-keyed where the merges
 # only shifted their lines (ci_predict.py --rekey-body; open_pr.sh's why).
 python3 "$PRT/ci_predict.py" --rekey-body "$B" --from "$([ "$C" = - ] && echo "$OLD" || echo "$C")" || echo "update_pr: the unpinned-site re-key did not run; prepr reads the body as written" >&2
-N=${PR_N:-$(gh pr list -R $R --head "$BR" --state open --json number -q '.[0].number')}
-[ -n "$N" ] || { echo "no open pull request at $BR, so no row to check"; exit 1; }
 # ensure_row's own guard decides; its output names the row only when it added one.
 # The title first, in an assignment: a failing `gh` inside an argument stops nothing.
 TTL=$(gh pr view "$N" -R $R --json title -q .title)
 _added=$(ensure_row . "$N" "$(row_line "$N" $R "$TTL")")
 ROW=""; [ -z "$_added" ] || ROW="adds one commit containing only this PR's own row, \`$_added\`"
 M=$(git rev-parse --short origin/main); H=$(git rev-parse HEAD)
+# BODY-ONLY (R10-FLOW-BODY-ONLY part (b)): nothing to commit -- the code sha, if any, is already in the
+# head, main needs no merge and the row exists -- so the head stays where it is and the body goes to
+# body_patch.sh, which runs the body contract at that head and PATCHes the body with no push. Run from
+# this worktree, the head's own checkout, so the contract resolves the paths the head adds (V115).
+if [ "$H" = "$LIVE" ]; then
+  if [ "$C" = - ]; then
+    T=${HANDOFF_TOPIC:-${BR#fix/}}; [ -n "$(git ls-remote origin "refs/heads/handoff/$T")" ] || T=${T%-pr}
+    HT=$(git ls-remote origin "refs/heads/handoff/$T" | cut -f1)
+    if [ -n "$HT" ]; then git fetch -q origin "refs/heads/handoff/$T"
+      git merge-base --is-ancestor "$HT" "$H" || pr_refuse "handoff/$T ($HT) is not in the head $H: pass it as the code sha, not -"; fi
+  fi
+  PYTHONPATH="$PRT" python3 - "$B" "$H" <<'E'
+import sys; from head_note import prefix
+p,H=sys.argv[1:3]; s=open(p).read()
+s=prefix(s,"`%s` is this PR's head, unchanged: its code was already in it and main merged cleanly, so the orchestrator's script set this body without a push.\n\n"%H); open(p,'w').write(s)
+E
+  rc=0; ( cd "$WT" && bash "${HPO_BODY_PATCH:-$SEAT/body_patch.sh}" --repo $R "$N" "$H" "$B" ) > $WT.log 2>&1 || rc=$?
+  cat $WT.log
+  [ "$rc" = 0 ] || pr_refuse "body-only: body_patch.sh refused #$N at $H (exit $rc); its log is $WT.log"
+  echo "update_pr: BODY-ONLY: #$N at $H, the head unmoved"
+  echo "HEAD=$H"; exit 0
+fi
 [ "$(git log -1 --format=%an)" = tvofi ] || { echo "author wrong"; exit 1; }
-PYTHONPATH="$PRT" python3 - $B $H "$NOTE" $M "$ROW" <<'E'
+PYTHONPATH="$PRT" python3 - $B $H "$NOTE" $M "$ROW" "$MAIN" <<'E'
 import sys; from head_note import prefix
-p,H,N,M,R=sys.argv[1:6]; s=open(p).read()
-pre="`%s` "%H + ((N+" and then ") if N else "") + "merges origin/main `%s` (an automatic merge by the orchestrator\'s script; any resolution inside the code head is described below) into this PR's previous head"%M + ((", and then "+R) if R else "") + ".\n\n"
+p,H,N,M,R,MM=sys.argv[1:7]; s=open(p).read()
+if MM: pre="`%s` "%H + ((N+" and then ") if N else "") + "merges origin/main `%s` (an automatic merge by the orchestrator\'s script; any resolution inside the code head is described below) into this PR's previous head"%M + ((", and then "+R) if R else "") + ".\n\n"
+else: pre="`%s` "%H + " and then ".join(x for x in (N, R) if x) + ".\n\n"  # main merged cleanly: not merged (R4)
 s=prefix(s,pre); open(p,'w').write(s)
 E
 if test -f tools/audit/app_push.sh; then _push=tools/audit/app_push.sh; else _push=tools/pr/app_push.sh; fi
-RO=""; [ "$C" != - ] || RO=--row-only  # mut:rowonly
+RO=""; [ "$(git rev-parse "$H^@")" != "$LIVE" ] || RO=--row-only  # mut:rowonly
 # Asynchronous, so a stop signal interrupts the `wait` and the EXIT trap reaps
 # the tree (pr_args.sh's why).
 { pr_push_hold; PREPR_SKIP_CLOSURES=1 PYTHONPATH=tests/hastub bash "$_push" $RO $R $WT $BR $B $ISS > $WT.log 2>&1 & } 9>>"$PR_PUSH_LOCK"

## Before you return the verdict (P275)
Run `python3 -I tools/audit/carry_audit.py check --body <PR body file> --comments <file holding [{"id": 0, "body": <verdict.md text>}]>`. Give every reported item its own `Carry: <GROUP> | #<issue> | O<n> | dismissed: <reason>`;
an evidence line flagged by its wording takes `Carry: dismissed: evidence, not a finding`. Return the verdict only at rc 0.
