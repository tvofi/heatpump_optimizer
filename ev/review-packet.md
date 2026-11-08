# Review packet #3317
head: 4bfb5d134a0d5fe0c8bbc716b41ca981d24dbbe1
base: 2a3c05644d85b7ee5c2c314fde5aca950e4aba91

Start here (fix-review.md). Re-read the live check state before a verdict: the digest is as read at render.

## Gate digest: green
CodeQL id=128687413133 success
arch-score / arch-score id=128696149221 success
arm id=128687160122 skipped
budget-raise-gate / budget-raise-gate id=128696178104 success
cancel-superseded id=128696173771 success
codeql id=128696149095 skipped
codeql / Analyze (actions) id=128687355047 success
codeql / Analyze (javascript-typescript) id=128687355206 success
codeql / Analyze (python) id=128687355044 success
gate id=128696148656 success
governance id=128696175465 skipped
governance / delivery-status id=128687355231 success
governance / delivery-status-publish id=128687356484 skipped
governance / env-matrix id=128687355077 success
governance / instrument-self-tests id=128687355052 success
governance / policy-docs id=128687355007 success
governance / record id=128687356006 skipped
governance / wave-script id=128687355221 success
hassfest id=128696178132 skipped
hassfest / hassfest id=128687354931 success
kernel-points id=128696184285 skipped
pr-contract id=128696149538 skipped
pr-contract / pr-contract id=128695811438 success
prelude id=128696148836 success
refresh id=128696179364 success
tests id=128696149092 skipped
tests / arch-instrument id=128687777153 success
tests / briefs id=128687355024 success
tests / browser id=128687777138 success
tests / ci-ratchet id=128695199624 skipped
tests / claims-autofix id=128688489775 skipped
tests / closure-scope id=128687355064 success
tests / closures id=128687777440 success
tests / closures-autofix id=128691580990 skipped
tests / coverage id=128687777303 success
tests / coverage-ratchet id=128695198757 success
tests / fast (3.14) id=128687777100 success
tests / graders-head-copy id=128695198763 success
tests / lane-proofs id=128695198794 success
tests / mutation id=128687355042 success
tests / mutation-autofix id=128687657150 skipped
tests / mutation-pins id=128687657277 skipped
tests / nightly-ha id=128687778276 skipped
tests / nightly-status id=128687354935 success
tests / replay id=128687778280 skipped
tests / typing id=128687777141 success
validate id=128696169739 skipped
validate / validate-hacs id=128687354844 success

## Refusals
none

## Advisories
hot-file: HPO_BUS_TRAIN_STATE is unset, so every merge verdict reads unboarded

## carry_audit at the head
CARRY-AUDIT: 0 finding item(s): 0 routed, 0 unrouted, 0 bad destination(s)

## figure_lint at the head
ok         bash tools/audit/seat/pr_args.sh --self-test
             `tools/audit/seat/pr_args.sh` is in the tree at this head
  ok         bash tools/audit/seat/cloud_relay.sh --self-test
             `tools/audit/seat/cloud_relay.sh` is in the tree at this head
  ok         python3 tests/structure.py
             `tests/structure.py` is in the tree at this head
  ok         PYTHONPATH=tests/hastub python3 tests/doc_claims.py
             `tests/doc_claims.py` is in the tree at this head
  ok         python3 tests/closure.py select --diff $(git merge-base origin/main HEAD)
             `tests/closure.py` is in the tree at this head

FIGURES: 5 resolved, 0 not verified, 0 refused

## Finder's harness: none named
### at the base
not run
### at the head
not run

## Mutation-ledger diff
none

## Three-dot diff
diff --git a/dev/programme/delivery/3317.md b/dev/programme/delivery/3317.md
new file mode 100644
index 000000000..1a857fd9c
--- /dev/null
+++ b/dev/programme/delivery/3317.md
@@ -0,0 +1 @@
+- [#3317](https://github.com/tvofi/heatpump_optimizer/pull/3317) — **open**, R10-HANDOFF-PATH: handoff path, part 3 (R10-HANDOFF-PATH)
diff --git a/tools/audit/seat/cloud_relay.sh b/tools/audit/seat/cloud_relay.sh
index f55b4c35a..1423d3c05 100644
--- a/tools/audit/seat/cloud_relay.sh
+++ b/tools/audit/seat/cloud_relay.sh
@@ -98,10 +98,13 @@
 #     dispatch; an update neither opens a PR nor enters WIP).
 #     A handoff already contained in its PR, or with no body ref, does nothing;
 #     a topic whose update failed is noted in `<ledger>.handoff-failed` by
-#     `<topic> <code-sha>` and retried only when handoff/<topic> moves, owed
+#     `<topic> <code-sha> <body-sha>` and retried only when handoff/<topic> or its body moves, owed
 #     meanwhile as `OWED <utc> handoff-update <ref> <sha> <why>` in <log>.level, <why>
 #     kept in `<ledger>.handoff-failed.why`; a body whose `Code:` trailer names
-#     another head is `handoff-body-stale` (retried). The
+#     another head is `handoff-body-stale` (retried). A refusal of a body-content step (unpinned sites, carry,
+#     figures, the body contract) stays recorded until the body ref moves; any other (ancestry reds, ci predict)
+#     reruns after HPO_RELAY_RETRY_BACKOFF (default 1800 s), three runs at most (`<ledger>.handoff-failed.tries`),
+#     then stays recorded and owed as above (carry 12). The
 #     `handoff-no-pr` lines there are `ledger.py level`'s fold of every
 #     handoff/* and handoff-body/* ref: owed unless its topic has an open PR,
 #     it is disposed at its sha, or main already carries the change (`ledger.py
@@ -500,7 +503,7 @@ handoff_level() { # the handoff-no-pr and hold-stale levels, derived from this p
 }
 handoff_arm() { # one pass over open PRs; updates one whose handoff is ahead of its head
   local state=${HPO_STATE_DIR:-$HOME/.local/state/hpo} repo=${HPO_RELAY_REPO:-tvofi/heatpump_optimizer} f pr br head topic hs bs bd body iss nh nonce urc held_prs released upd why code
-  local bf bonly key seed=""
+  local bf bonly key seed="" tries n cls
   f=$state/cloud-handoff-failed; mkdir -p "$state"
   # BODY-ONLY (R10-FLOW-BODY-ONLY part (c)): `<topic> <body sha>` per body this relay has applied, by an
   # update or a body-only run. With no file yet, this pass records every contained topic's body as
@@ -542,12 +545,15 @@ handoff_arm() { # one pass over open PRs; updates one whose handoff is ahead of
       echo "cloud_relay: HELD-${why%% *} #$pr $hs${why#"${why%% *}"} (head $head under review; merge it, or list #$pr in $(release_file) and re-dispatch)"
       level_line handoff-held "refs/heads/handoff/$topic" "$hs" "#$pr $why" >> "$state/cloud-level-held.$$"; continue
     fi
-    # A failed body-only run is keyed on the body sha too (carry 4, P22): a new body re-triggers it.
-    key="$topic $hs"; [ -z "$bonly" ] || key="$key $bs"
+    # A failed run is keyed on the body sha too (P22, carry 8): a new body re-triggers it, and the reason stays.
+    key="$topic $hs $bs"
     if [ -f "$f" ] && grep -qxF "$key" "$f"; then
       why=$(awk -F'\t' -v k="$key" '$1 == k { w = $2 } END { print w }' "$f.why" 2>/dev/null)
       level_line handoff-update "refs/heads/handoff/$topic" "$hs" "$why" >> "$state/cloud-level-update.$$"; continue
     fi
+    # A retryable refusal (carry 12) waits out its backoff, owed meanwhile with its reason; $f.tries is `<key>\t<n>\t<epoch>`.
+    tries=$(awk -F'\t' -v k="$key" '$1 == k { n = $2; t = $3 } END { print (n == "" ? "0 0" : n " " t) }' "$f.tries" 2>/dev/null)
+    if [ "${tries% *}" != 0 ] && [ "$(date +%s)" -lt $(( ${tries#* } + ${HPO_RELAY_RETRY_BACKOFF:-1800} )) ]; then why=$(awk -F'\t' -v k="$key" '$1 == k { w = $2 } END { print w }' "$f.why" 2>/dev/null); level_line handoff-update "refs/heads/handoff/$topic" "$hs" "$why" >> "$state/cloud-level-update.$$"; continue; fi  # mut:backoff
     # The body goes in a directory of this run's own, under the state dir: a file directly in a
     # shared temp root ($TMPDIR, /tmp) is refused by prepr's body-path check, so every relay
     # update failed there (#2469, #2471) -- and still raced the manual update it was meant to spare.
@@ -606,10 +612,20 @@ handoff_arm() { # one pass over open PRs; updates one whose handoff is ahead of
     if [ "$urc" = 75 ]; then echo "cloud_relay: update_pr busy on $br; the next pass retries" >&2; rm -rf "$bd"; continue; fi
     if [ "$urc" != 0 ]; then
       why=$(grep REFUSE "$bd/update.out" | tail -n 1); [ -n "$why" ] || why=$(last_line "$(cat "$bd/update.out")")
-      echo "$key" >> "$f"; printf '%s\t%s\n' "$key" "$why" >> "$f.why"
+      # A refusal of a body-content step (unpinned sites, carry, figures, the body contract) clears only when the body
+      # ref moves, which is a new key: recorded at once. Any other (ancestry reds, ci predict) can clear with no ref
+      # moving: it reruns after HPO_RELAY_RETRY_BACKOFF (30 min), three runs at most, then it is recorded and owed.
+      n=${tries% *}; n=$((n + 1)); cls=retry
+      ! grep -qiE 'REFUSE[: ]+(unpinned sites?|carry|pr-body|figures|brief)|unpinned site' "$bd/update.out" || cls=content  # mut:retryall
+      [ "$n" -lt 3 ] || cls=content  # mut:trylimit
+      if [ "$cls" = content ]; then
+        echo "$key" >> "$f"
+      else printf '%s\t%s\t%s\n' "$key" "$n" "$(date +%s)" >> "$f.tries"; fi
+      printf '%s\t%s\n' "$key" "$why" >> "$f.why"
       level_line handoff-update "refs/heads/handoff/$topic" "$hs" "$why" >> "$state/cloud-level-update.$$"; rm -rf "$bd"; continue
     fi
     rm -rf "$bd"; echo "$topic $bs" >> "$bf"  # this body is applied: a later pass leaves it alone
+    [ ! -f "$f.tries" ] || { grep -vF "$key	" "$f.tries" > "$f.tries.$$" || :; mv -f "$f.tries.$$" "$f.tries"; }
     if [ -n "$bonly" ]; then echo "cloud_relay: BODIED #$pr $head with handoff-body/$topic $bs" >&2; continue; fi
     nh=$( { if [ -n "${HPO_RELAY_PRS:-}" ]; then "$HPO_RELAY_PRS"; else gh pr list -R "$repo" --state open --limit 100 --json number,headRefName,headRefOid \
       -q '.[] | [.number, .headRefName, .headRefOid] | @tsv'; fi; } | awk -F'\t' -v p="$pr" '$1 == p { print $3; exit }')
@@ -1054,7 +1070,7 @@ EOF
   hf=$t/state/cloud-handoff-hold; hu=$t/hu.sh; printf '#!/bin/sh\necho "$1 $2${HPO_UPDATE_BODY_ONLY:+ body-only}" >> "%s/hupdated"\n' "$t" > "$hu"; chmod +x "$hu"; HPO_RELAY_UPDATE=$hu
   printf '41\n' > "$hf"; ho=$(handoff_arm 2>&1)
   chk "a held PR whose handoff is already in its head prints no HELD (nothing to hold)" 1 grep -q HELD <<< "$ho"
-  rm -f "$t/updated" "$t/hupdated" "$t/state/cloud-handoff-failed" "$t/events.tsv"; : > "$LOG"
+  rm -f "$t/updated" "$t/hupdated" "$t/state/cloud-handoff-failed" "$t/events.tsv"; : > "$LOG"; rm -f "$t/state/cloud-handoff-failed.tries"
   git -C "$t/pr" reset -q --hard "$PRH"; mkref fix/topic-a-pr; printf '%s\t%s\t%s\n' 41 fix/topic-a-pr "$PRH" > "$prs"
   printf '99\n41\n' > "$hf"; ho=$(handoff_arm 2>&1)
   chk "a held PR whose handoff is ahead is not updated" 0 test ! -e "$t/hupdated"
@@ -1067,7 +1083,7 @@ EOF
   chk "and HELD names the moved tip" 0 grep -q "HELD #41 $HS2\$" <<< "$ho"
   echo "topic-a $HS2" > "$t/state/cloud-handoff-failed"; ho=$(handoff_arm 2>&1)
   chk "a hold outranks a recorded failed update: still HELD" 0 grep -q "HELD #41 $HS2\$" <<< "$ho"
-  rm -f "$t/state/cloud-handoff-failed"
+  rm -f "$t/state/cloud-handoff-failed"; rm -f "$t/state/cloud-handoff-failed.tries"
   printf '99\n' > "$hf"; ho=$(handoff_arm 2>&1)
   chk "an unheld PR is updated as before (null control)" 0 grep -q "^fix/topic-a-pr $HS2\$" "$t/hupdated"
   chk "and prints no HELD" 1 grep -q HELD <<< "$ho"
@@ -1232,25 +1248,45 @@ EOF
   chk "and owes handoff-update in the level file, at the topic's tip, with the update's last line" 0 grep -q "^OWED .* handoff-update refs/heads/handoff/topic-a $HS2 (no output)$" "$LOG.level"
   chk "once after two passes (a level, rewritten)" 0 test "$(grep -c handoff-update "$LOG.level")" = 1
   # a BUSY update (75: another update_pr.sh holds the branch's worktree) is no failure: not recorded, retried next pass
-  rm -f "$t/updated" "$t/state/cloud-handoff-failed"; : > "$LOG"
+  rm -f "$t/updated" "$t/state/cloud-handoff-failed"; : > "$LOG"; rm -f "$t/state/cloud-handoff-failed.tries"
   bu=$t/bu.sh; printf '#!/bin/sh\necho x >> "%s/updated"\nexit 75\n' "$t" > "$bu"; chmod +x "$bu"; HPO_RELAY_UPDATE=$bu
   handoff_arm >/dev/null 2>&1; handoff_arm >/dev/null 2>&1
   chk "a busy update is tried again on the next pass" 0 test "$(wc -l < "$t/updated" | tr -d ' ')" = 2
   chk "and is not recorded failed" 0 test ! -s "$t/state/cloud-handoff-failed"
   chk "nor owed" 1 grep -q "handoff-update" "$LOG.level"
+  bodyc() { git -C "$t/b" -c user.name=t -c user.email=t@t commit -q --allow-empty -m body ${1:+-m "Code: $1"}; mkref2; }
+  # Carry 12: a refusal that clears with no ref moving is rerun after a backoff, three runs at most; a body-content refusal waits for the body.
+  rt=$t/rt.sh; printf '#!/bin/sh\nn=$(cat "%s/rtn" 2>/dev/null || echo 0); echo $((n + 1)) > "%s/rtn"\ncase "$RT_MODE" in\n ok1) [ "$n" = 0 ] && { echo "update_pr: REFUSE: ancestry reds: r"; exit 1; }; exit 0;;\n *) echo "update_pr: REFUSE: $RT_MODE: r"; exit 1;;\nesac\n' "$t" "$t" > "$rt"; chmod +x "$rt"; HPO_RELAY_UPDATE=$rt
+  rtreset() { rm -f "$t/rtn" "$t/state/cloud-handoff-failed" "$t/state/cloud-handoff-failed.why" "$t/state/cloud-handoff-failed.tries"; : > "$LOG"; rm -f "$LOG.level"; }
+  rtcalls() { cat "$t/rtn" 2>/dev/null || echo 0; }
+  export HPO_RELAY_RETRY_BACKOFF=0
+  rtreset; RT_MODE=ok1; export RT_MODE; handoff_arm >/dev/null 2>&1; handoff_arm >/dev/null 2>&1
+  chk "(a) an ancestry-reds refusal that then clears updates on the retry, with no ref moved" 0 test "$(rtcalls)" = 2 -a ! -s "$t/state/cloud-handoff-failed"
+  rtreset; RT_MODE="ancestry reds"; handoff_arm >/dev/null 2>&1; handoff_arm >/dev/null 2>&1; handoff_arm >/dev/null 2>&1; handoff_arm >/dev/null 2>&1; handoff_arm >/dev/null 2>&1
+  chk "(c) three refusals of a retryable class stop: three runs over five passes" 0 test "$(rtcalls)" = 3
+  chk "(c) and the third is recorded and owed with its reason" 0 grep -q "^OWED .* handoff-update refs/heads/handoff/topic-a $HS2 update_pr: REFUSE: ancestry reds: r\$" "$LOG.level"
+  rtreset; RT_MODE="unpinned sites"; handoff_arm >/dev/null 2>&1; handoff_arm >/dev/null 2>&1
+  chk "(b) an unpinned-sites refusal with the same body is not rerun" 0 test "$(rtcalls)" = 1
+  chk "(b) and it is recorded at once, owed with its reason" 0 grep -q "^OWED .* handoff-update refs/heads/handoff/topic-a $HS2 update_pr: REFUSE: unpinned sites: r\$" "$LOG.level"
+  bodyc "$HS2"; handoff_arm >/dev/null 2>&1
+  chk "(b) a new body reruns it" 0 test "$(rtcalls)" = 2
+  rtreset; HPO_RELAY_RETRY_BACKOFF=3600; RT_MODE="ancestry reds"; handoff_arm >/dev/null 2>&1; handoff_arm >/dev/null 2>&1
+  chk "the backoff holds a retryable refusal back: one run in two passes" 0 test "$(rtcalls)" = 1
+  chk "  and owes it meanwhile with its reason" 0 grep -q "handoff-update refs/heads/handoff/topic-a $HS2 update_pr: REFUSE: ancestry reds: r\$" "$LOG.level"
+  export HPO_RELAY_RETRY_BACKOFF=0; rtreset; RT_MODE="ancestry reds"; handoff_arm >/dev/null 2>&1; handoff_arm >/dev/null 2>&1; handoff_arm >/dev/null 2>&1; handoff_arm >/dev/null 2>&1
+  unset HPO_RELAY_RETRY_BACKOFF; rtreset; HPO_RELAY_UPDATE=$hu; unset RT_MODE
   # V147: a failed update records why; a body updates only the code head its Code: trailer names
-  rm -f "$t/state/cloud-handoff-failed" "$t/state/cloud-handoff-failed.why"; : > "$LOG"
-  ru=$t/ru.sh; printf '#!/bin/sh\necho "update_pr: REFUSE: X"\necho "update_pr: cleaned up"\nexit 1\n' > "$ru"; chmod +x "$ru"; HPO_RELAY_UPDATE=$ru
+  rm -f "$t/state/cloud-handoff-failed" "$t/state/cloud-handoff-failed.why"; : > "$LOG"; rm -f "$t/state/cloud-handoff-failed.tries"
+  ru=$t/ru.sh; printf '#!/bin/sh\necho "update_pr: REFUSE: carry X"\necho "update_pr: cleaned up"\nexit 1\n' > "$ru"; chmod +x "$ru"; HPO_RELAY_UPDATE=$ru
   handoff_arm >/dev/null 2>&1
-  chk "a failed update's handoff-update line ends in its last REFUSE line" 0 grep -q "^OWED .* handoff-update refs/heads/handoff/topic-a $HS2 update_pr: REFUSE: X\$" "$LOG.level"
+  chk "a failed update's handoff-update line ends in its last REFUSE line" 0 grep -q "^OWED .* handoff-update refs/heads/handoff/topic-a $HS2 update_pr: REFUSE: carry X\$" "$LOG.level"
   handoff_arm >/dev/null 2>&1
-  chk "and keeps it on the next pass, which does not retry" 0 grep -q "^OWED .* handoff-update refs/heads/handoff/topic-a $HS2 update_pr: REFUSE: X\$" "$LOG.level"
-  chk "while cloud-handoff-failed keeps its bare <topic> <sha> line" 0 test "$(cat "$t/state/cloud-handoff-failed")" = "topic-a $HS2"
-  rm -f "$t/state/cloud-handoff-failed" "$t/state/cloud-handoff-failed.why"
+  chk "and keeps it on the next pass, which does not retry" 0 grep -q "^OWED .* handoff-update refs/heads/handoff/topic-a $HS2 update_pr: REFUSE: carry X\$" "$LOG.level"
+  chk "while cloud-handoff-failed keeps its <topic> <code sha> <body sha> line" 0 test "$(cat "$t/state/cloud-handoff-failed")" = "topic-a $HS2 $(git -C "$t/o.git" rev-parse refs/heads/handoff-body/topic-a)"
+  rm -f "$t/state/cloud-handoff-failed" "$t/state/cloud-handoff-failed.why"; rm -f "$t/state/cloud-handoff-failed.tries"
   printf '#!/bin/sh\necho "update_pr: merging"\necho "update_pr: STALE CHECKOUT"\nexit 1\n' > "$ru"; handoff_arm >/dev/null 2>&1
   chk "an update failing with no REFUSE line records its last line" 0 grep -q "^OWED .* handoff-update refs/heads/handoff/topic-a $HS2 update_pr: STALE CHECKOUT\$" "$LOG.level"
-  rm -f "$t/state/cloud-handoff-failed" "$t/state/cloud-handoff-failed.why" "$t/hupdated"; : > "$LOG"; HPO_RELAY_UPDATE=$hu
-  bodyc() { git -C "$t/b" -c user.name=t -c user.email=t@t commit -q --allow-empty -m body ${1:+-m "Code: $1"}; mkref2; }
+  rm -f "$t/state/cloud-handoff-failed" "$t/state/cloud-handoff-failed.why" "$t/hupdated"; : > "$LOG"; HPO_RELAY_UPDATE=$hu; rm -f "$t/state/cloud-handoff-failed.tries"
   bodyc "$HS"; handoff_arm >/dev/null 2>&1; handoff_arm >/dev/null 2>&1
   chk "a body whose Code: names the previous handoff head runs no update_pr" 0 test ! -e "$t/hupdated"
   chk "and owes one handoff-body-stale line at the handoff tip, naming the body's head" \
@@ -1295,13 +1331,13 @@ EOF
   chk "a contained body naming another code head runs nothing and is owed stale" 0 test ! -e "$t/hupdated" -a "$(grep -c "handoff-body-stale refs/heads/handoff/topic-a $HS2 body names ${HS:0:12}\$" "$LOG.level")" = 1
   # a failed body-only run: its reason is the LAST REFUSE line (#3037 review M2), its output is
   # replayed to the relay's stderr (M5), it is keyed on the body sha, and a new body re-triggers it
-  r2=$t/r2.sh; printf '#!/bin/sh\necho "$1 $2" >> "%s/hupdated"\necho "update_pr: REFUSE: first"\necho "update_pr: REFUSE: second"\necho "update_pr: replayed tail"\nexit 1\n' "$t" > "$r2"; chmod +x "$r2"; HPO_RELAY_UPDATE=$r2
-  rm -f "$t/state/cloud-handoff-failed" "$t/state/cloud-handoff-failed.why"; bodyc "$HS2"; ho=$(handoff_arm 2>&1)
-  chk "a failed update's handoff-update line ends in the last of its REFUSE lines" 0 grep -q "^OWED .* handoff-update refs/heads/handoff/topic-a $HS2 update_pr: REFUSE: second\$" "$LOG.level"
+  r2=$t/r2.sh; printf '#!/bin/sh\necho "$1 $2" >> "%s/hupdated"\necho "update_pr: REFUSE: carry first"\necho "update_pr: REFUSE: carry second"\necho "update_pr: replayed tail"\nexit 1\n' "$t" > "$r2"; chmod +x "$r2"; HPO_RELAY_UPDATE=$r2
+  rm -f "$t/state/cloud-handoff-failed" "$t/state/cloud-handoff-failed.why"; bodyc "$HS2"; ho=$(handoff_arm 2>&1); rm -f "$t/state/cloud-handoff-failed.tries"
+  chk "a failed update's handoff-update line ends in the last of its REFUSE lines" 0 grep -q "^OWED .* handoff-update refs/heads/handoff/topic-a $HS2 update_pr: REFUSE: carry second\$" "$LOG.level"
   chk "and the update's whole output reaches the relay's stderr" 0 grep -qx "update_pr: replayed tail" <<< "$ho"
   chk "a failed body-only run is recorded on topic, code and body sha" 0 test "$(cat "$t/state/cloud-handoff-failed")" = "topic-a $HS2 $(bsha)"
   handoff_arm >/dev/null 2>&1
-  chk "and not retried on the next pass, which keeps its reason" 0 test "$(grep -c . "$t/hupdated")-$(grep -c "handoff-update refs/heads/handoff/topic-a $HS2 update_pr: REFUSE: second\$" "$LOG.level")" = 1-1
+  chk "and not retried on the next pass, which keeps its reason" 0 test "$(grep -c . "$t/hupdated")-$(grep -c "handoff-update refs/heads/handoff/topic-a $HS2 update_pr: REFUSE: carry second\$" "$LOG.level")" = 1-1
   bodyc "$HS2"; handoff_arm >/dev/null 2>&1
   chk "a new body re-triggers it" 0 test "$(grep -c . "$t/hupdated")" = 2
   HPO_RELAY_UPDATE=$hu; rm -f "$t/hupdated" "$t/state/cloud-handoff-failed" "$t/state/cloud-handoff-failed.why"
@@ -1359,7 +1395,7 @@ EOF
   HB=$(hxc b 1700000100); git -C "$t/o.git" fetch -qf "$hx" HEAD:refs/heads/handoff/topic-h
   printf '#!/bin/sh\nprintf "51\\tfix/topic-h-pr\\t%%s\\n" "$HX_HEAD"\n' > "$hprs"; chmod +x "$hprs"; export HX_HEAD=$HA
   printf 'Code head: %s\n' "${HA:0:8}" > "$hbd/BODY.md"; git -C "$hbd" add BODY.md; hbc 1700000150 >/dev/null
-  rm -f "$t/hupdated" "$t/state/cloud-handoff-failed" "$t/state/cloud-handoff-failed.why" "$hf"; : > "$LOG"; rm -f "$LV"; HPO_RELAY_UPDATE=$hu
+  rm -f "$t/hupdated" "$t/state/cloud-handoff-failed" "$t/state/cloud-handoff-failed.why" "$hf"; : > "$LOG"; rm -f "$LV"; HPO_RELAY_UPDATE=$hu; rm -f "$t/state/cloud-handoff-failed.tries"
   ho=$(HPO_RELAY_PRS=$hprs handoff_arm 2>&1)
   chk "a handoff ahead of its PR whose body names the old tip prints HELD-BODY once per pass" 0 test "$(grep -c "^cloud_relay: HELD-BODY #51 ${HB:0:8}\$" <<< "$ho")" = 1
   chk "and runs no update and owes one handoff-held line with why BODY" 0 test "$([ -e "$t/hupdated" ] && echo ran)-$(hlv "handoff-held refs/heads/handoff/topic-h $HB #51 BODY\$")" = -1
@@ -1482,7 +1518,7 @@ $cfo2") $(calls 67)" = "1 1"
   printf '#!/bin/bash\necho $$ >> "%s/tpids"\nbash -c '"'"'sleep 30 & echo $! >> "$0"; wait'"'"' "%s/tpids" & echo $! >> "%s/tpids"\nwait\n' "$t" "$t" "$t" > "$t/tree.sh"; chmod +x "$t/tree.sh"
   local rp k tn live p
   stoprelay() { # <relay script> <pids wanted>: one pass, TERMed once the update's tree is up; sets tn and live
-    rm -f "$t/state/cloud-handoff-failed"; : > "$t/tpids"; : > "$t/marks"; : > "$LOG"; printf '%s\t%s\t%s\n' 41 fix/topic-a-pr "$PRH" > "$prs"
+    rm -f "$t/state/cloud-handoff-failed"; : > "$t/tpids"; : > "$t/marks"; : > "$LOG"; printf '%s\t%s\t%s\n' 41 fix/topic-a-pr "$PRH" > "$prs"; rm -f "$t/state/cloud-handoff-failed.tries"
     bash "$1" pass --log "$LOG" >/dev/null 2>&1 & rp=$!
     k=0; while [ "$(wc -l < "$t/tpids")" -lt "$2" ] && [ $k -lt 300 ]; do sleep 0.05; k=$((k + 1)); done
     tn=$(wc -l < "$t/tpids" | tr -d ' '); kill -TERM "$rp"
@@ -1519,7 +1555,7 @@ $cfo2") $(calls 67)" = "1 1"
   printf '#!/bin/bash\necho $$ >> "%s/tpids"\nk=0; while [ ! -e "%s/go" ] && [ $k -lt 400 ]; do sleep 0.05; k=$((k + 1)); done\necho done >> "%s/marks"\n' \
     "$t" "$t" "$t" > "$t/finish.sh"; chmod +x "$t/finish.sh"
   grprelay() {
-    rm -f "$t/state/cloud-handoff-failed" "$t/go"; : > "$t/tpids"; : > "$t/marks"; : > "$LOG"; printf '%s\t%s\t%s\n' 41 fix/topic-a-pr "$PRH" > "$prs"
+    rm -f "$t/state/cloud-handoff-failed" "$t/go"; : > "$t/tpids"; : > "$t/marks"; : > "$LOG"; printf '%s\t%s\t%s\n' 41 fix/topic-a-pr "$PRH" > "$prs"; rm -f "$t/state/cloud-handoff-failed.tries"
     HPO_RELAY_UPDATE=$1 python3 -I -c 'import os, sys; os.setpgid(0, 0); os.execvp("bash", sys.argv[1:])' bash "$HERE/cloud_relay.sh" pass --log "$LOG" >/dev/null 2>&1 & rp=$!
     k=0; while [ "$(wc -l < "$t/tpids")" -lt "$2" ] && [ $k -lt 300 ]; do sleep 0.05; k=$((k + 1)); done
     tn=$(wc -l < "$t/tpids" | tr -d ' '); kill -"$3" -- "-$rp"; wait "$rp" 2>/dev/null; touch "$t/go"
diff --git a/tools/audit/seat/instruments/cloud_relay.sh.md b/tools/audit/seat/instruments/cloud_relay.sh.md
index 31318c704..ab4aa6cd5 100644
--- a/tools/audit/seat/instruments/cloud_relay.sh.md
+++ b/tools/audit/seat/instruments/cloud_relay.sh.md
@@ -141,11 +141,13 @@
   left unapplied while its body tip is newer than the PR head's commit) are
   published before the serial update loops, so a slow update cannot delay them.
   A failed update is noted in `cloud-handoff-failed` by
-  `<topic> <code-sha>` (a body-only one by `<topic> <code-sha> <body-sha>`, so
-  a new body re-triggers it), its reason, the update's last `REFUSE` line else
+  `<topic> <code-sha> <body-sha>` (so a new body re-triggers it), its reason, the update's last `REFUSE` line else
   its last line, kept beside it in `cloud-handoff-failed.why` (tab-separated),
   owed as `OWED <utc> handoff-update <ref> <sha> <why>` (the `<why>` is the line kept in `cloud-handoff-failed.why`) in `<log>.level` while
-  that entry matches, and retried only when the handoff (or body) moves. The
+  that entry matches, and retried only when the handoff (or body) moves, except a
+  refusal that is not of a body-content step (`ancestry reds`, `ci predict`): it reruns after
+  `HPO_RELAY_RETRY_BACKOFF` (1800 s), three runs at most (`cloud-handoff-failed.tries`), and is then
+  recorded and owed as above. A refusal of `unpinned sites`, `carry`, `figures` or the body contract is recorded at once. The
   update's output is held in a file until it ends, then replayed to the
   relay's stderr. An update that
   exits 75 is BUSY (another `open_pr.sh` or `update_pr.sh` run holds the branch's
diff --git a/tools/audit/seat/open_pr.sh b/tools/audit/seat/open_pr.sh
index 0baf9c450..a0f8a2ca3 100755
--- a/tools/audit/seat/open_pr.sh
+++ b/tools/audit/seat/open_pr.sh
@@ -14,6 +14,9 @@
 # fails says ROWLESS, and update_pr.sh's ensure_row adds the row; #2719). Every exit's last act,
 # under the branch lock, is pr_release_wt (pr_args.sh): the worktree is detached at the pushed head,
 # removed with its branch when origin never had it, or kept and named (P-D, P64, P72).
+# Once the PR exists and its row is pushed (PR_ATTEMPT opened), the opener's checkout is collected
+# (pr_collect_wt, carry 6): update_pr.sh keeps the one per-PR checkout from then on, so a PR holds one
+# ~140 MB checkout, not two; a dirty or unpushed one is kept and named by pr_release_wt.
 # The tools are refused when origin/main is ahead of their checkout under tools/ (pr_tools_fresh).
 # The row is written and committed by delivery_row.sh's commit_row, the one
 # function update_pr.sh's ensure_row also calls (its header says why).
@@ -44,6 +47,7 @@ mkdir -p "$D"; cd "$M"
 # between the two pushes below and left the PR without its row (#2547, #2548); it now answers BUSY.
 pr_branch_lock "$(dirname -- "$D")/upd-${BR//\//-}.lock" "$BR" "$WT"  # mut:oplock
 PR_TIDY='pr_release_wt "$WT" "$BR" "${PR_PUSHED:-}"'  # set once the lock is this run's: a BUSY exit touches nothing
+PR_TIDY="$PR_TIDY"'; case "${PR_ATTEMPT:-}" in opened,PR=*) pr_collect_wt "$WT" "${PR_PUSHED:-}";; esac'  # mut:opcollect
 pr_handoff_tips "$T" 1
 # The attempt is the ledger's (R10-ORCH-LEDGER): `started` now, and on every exit, a stop
 # signal's included, `opened,PR=<n>` or `unopened` (bash's $? in an EXIT trap after a TERM is the
diff --git a/tools/audit/seat/pr_args.sh b/tools/audit/seat/pr_args.sh
index bb6e4b756..58f2a4c10 100644
--- a/tools/audit/seat/pr_args.sh
+++ b/tools/audit/seat/pr_args.sh
@@ -59,6 +59,7 @@ pr_code_in_handoff() { # <sha> <topic>: after the fetch of handoff/<topic>; PR_H
   [ "$1" != "$PR_BT" ] || pr_refuse "code sha $1 is not an ancestor of origin/handoff/$2 ($PR_HT); it is the tip of handoff-body/$2: that is the BODY sha; pass the CODE sha"  # mut:body
   pr_refuse "code sha $1 is not an ancestor of origin/handoff/$2 ($PR_HT), and it is not the tip of handoff-body/$2 (${PR_BT:-absent})"  # mut:ancestor
 }
+pr_busy() { printf '%s: BUSY: %s; nothing was changed, run again when it ends\n' "${PR_NAME:-pr}" "$*" >&2; exit 75; }  # a stop that is a live run's, not a permanent refusal (carry 8)
 pr_lock_busy() { # <lock-file> <branch> <worktree>: the holder did not take the lock: BUSY (75) when another holder has it
   local rc=0 o
   kill -0 "$LKP" 2>/dev/null && pr_refuse "the lock holder for $1 did not report within 20 s"
@@ -156,6 +157,16 @@ pr_release_wt() { # <worktree> <branch> <pushed sha|''>: detach, remove or keep
   git branch -q -D "$br" 2>/dev/null || :
   printf '%s: removed %s and its local branch %s, which origin never had\n' "${PR_NAME:-pr}" "$wt" "$br" >&2
 }
+pr_collect_wt() { # <worktree> <pushed sha>: remove the run's worktree once pr_release_wt left it detached, clean, at the sha origin holds
+  local wt=$1 sha=$2 c
+  [ -n "$sha" ] && [ -d "$wt" ] || return 0
+  [ -z "$(git -C "$wt" symbolic-ref -q HEAD 2>/dev/null)" ] || return 0  # still on its branch: pr_release_wt kept it and named why
+  [ "$(git -C "$wt" rev-parse HEAD 2>/dev/null)" = "$sha" ] || return 0
+  [ -z "$(git -C "$wt" status --porcelain 2>/dev/null)" ] || { pr_kept "$wt" detached "it is dirty"; return 0; }
+  c=$(git -C "$wt" rev-parse --path-format=absolute --git-common-dir) && cd "$c"
+  git worktree remove "$wt" 2>/dev/null || { pr_kept "$wt" detached "git worktree remove refused it"; return 0; }  # mut:colremove
+  printf '%s: collected %s (the PR exists with its row; update_pr.sh keeps the per-PR checkout from here)\n' "${PR_NAME:-pr}" "$wt" >&2
+}
 pr_kept() { printf '%s: KEPT %s on %s: %s\n' "${PR_NAME:-pr}" "$1" "$2" "$3" >&2; }
 
 # ---- the tools' freshness (P-P) ----------------------------------------------
@@ -917,9 +928,15 @@ STUB
     local sd=$t/sd-$1 hk=$m/.git/hooks/post-checkout
     rm -rf "$t/s$i"; git -C "$m" worktree prune  # the last run's worktree holds fix/x
     copyin "$1"
+    # mut:unlock leaves the holder to its own 0.2 s parent poll, so reading it alive at the run's return raced that
+    # poll under CPU load (1 FAIL in 9 with five self-tests at once): that copy polls every 30 s, so it is alive at the
+    # read whatever the load, and is ended and awaited below (a bound, not one kill -0 inside the poll).
+    [ "$1" != unlock ] || sed -i 's/time.sleep(0.2)  # mut:watch/time.sleep(30)  # mut:watch/' "$m/tools/audit/seat/pr_args.sh"
     printf '#!/bin/sh\nsleep 30 </dev/null >/dev/null 2>&1 &\necho $! >> "%s/sleepers"\n' "$t" > "$hk"; chmod +x "$hk"
     cp "$t/body.md" "$t/b.md"; HPO_STATE_DIR=$sd bash "$m/tools/audit/seat/update_pr.sh" fix/x - "$t/b.md" > "$t/out1" 2>&1
-    if kill -0 "$(cut -d' ' -f2 "$sd/pr/upd-fix-x.lock")" 2>/dev/null; then echo 1 > "$t/hold1"; else echo 0 > "$t/hold1"; fi
+    hp=$(cut -d' ' -f2 "$sd/pr/upd-fix-x.lock")
+    if kill -0 "$hp" 2>/dev/null; then echo 1 > "$t/hold1"; kill -USR1 "$hp" 2>/dev/null; else echo 0 > "$t/hold1"; fi
+    for _ in $(seq 100); do kill -0 "$hp" 2>/dev/null || break; sleep 0.1; done  # the holder's exit, bounded (10 s)
     rm -f "$hk"; git -C "$m" worktree remove --force "$sd/pr/upd-fix-x" 2>/dev/null
     cp "$t/body.md" "$t/b.md"; HPO_STATE_DIR=$sd bash "$m/tools/audit/seat/update_pr.sh" fix/x - "$t/b.md" > "$t/out" 2>&1
     echo $? > "$t/rc"
@@ -935,6 +952,36 @@ STUB
   ck "update_pr: the lock holder has exited by the time a run returns" $?
   detrun unlock; [ "$(cat "$t/hold1")" = 1 ]
   ck "  mutant mut:unlock (its line deleted): the holder is still alive when the run returns" $?
+  # Carry 8: a branch checked out in a worktree that is not the run's own (outside the PR scratch root, so
+  # never detached for it) is BUSY (75), not a permanent refusal. Null control: with none, the run reaches its push.
+  elserun() { # <mutant> <worktree: 1|0>
+    local sd=$t/else-$1-$2
+    rm -rf "$t/s$i"; git -C "$m" worktree prune; copyin "$1"
+    [ "$2" = 0 ] || git -C "$m" worktree add -q -B fix/x "$t/else-wt" "$base" || return 1
+    cp "$t/body.md" "$t/b.md"; HPO_STATE_DIR=$sd bash "$m/tools/audit/seat/update_pr.sh" fix/x - "$t/b.md" > "$t/out" 2>&1; echo $? > "$t/rc"
+    reap; git -C "$m" worktree remove --force "$t/else-wt" 2>/dev/null; git -C "$m" worktree remove --force "$sd/pr/upd-fix-x" 2>/dev/null; git -C "$m" worktree prune; rm -rf "$sd"
+  }
+  elserun - 1; [ "$(cat "$t/rc")" = 75 ] && grep -qF "update_pr: BUSY: branch fix/x checked out elsewhere" "$t/out"
+  ck "update_pr: a branch checked out in a worktree that is not the run's own is BUSY (75), nothing changed" $?
+  elserun elsewhere 1; [ "$(cat "$t/rc")" != 75 ] && ! grep -qF "update_pr: BUSY: branch" "$t/out"
+  ck "  mutant mut:elsewhere (its line deleted): the run goes on past a branch held elsewhere" $?
+  elserun - 0; [ "$(cat "$t/rc")" != 75 ] && ! grep -qF "update_pr: BUSY" "$t/out" && grep -qF "update_pr: REFUSE: the push failed" "$t/out"
+  ck "null control: with the branch checked out nowhere else, the run reaches its push" $?
+  # Carry 6: one checkout per pull request. A second update finds the first's worktree, resets it onto the branch
+  # (leftovers cleaned) and reuses it instead of removing and cutting it again.
+  reuserun() { # <mutant>
+    local sd=$t/ru-$1 gd
+    rm -rf "$t/s$i"; git -C "$m" worktree prune; copyin "$1"
+    cp "$t/body.md" "$t/b.md"; HPO_STATE_DIR=$sd bash "$m/tools/audit/seat/update_pr.sh" fix/x - "$t/b.md" > "$t/out1" 2>&1
+    gd=$(git -C "$sd/pr/upd-fix-x" rev-parse --absolute-git-dir) && : > "$gd/reuse-marker" && echo scratch > "$sd/pr/upd-fix-x/leftover.txt"
+    cp "$t/body.md" "$t/b.md"; HPO_STATE_DIR=$sd bash "$m/tools/audit/seat/update_pr.sh" fix/x - "$t/b.md" > "$t/out" 2>&1
+    { [ -e "$gd/reuse-marker" ] && echo 1 || echo 0; } > "$t/reused"; { [ -e "$sd/pr/upd-fix-x/leftover.txt" ] && echo 1 || echo 0; } > "$t/leftover"
+    reap; git -C "$m" worktree remove --force "$sd/pr/upd-fix-x" 2>/dev/null; git -C "$m" worktree prune; rm -rf "$sd"
+  }
+  reuserun -; [ "$(cat "$t/reused")" = 1 ] && [ "$(cat "$t/leftover")" = 0 ] && grep -qF "update_pr: REFUSE: the push failed" "$t/out"
+  ck "update_pr: a second update reuses the first's checkout (same worktree), cleaned of leftovers, and reaches its push" $?
+  reuserun updreusewt; [ "$(cat "$t/reused")" = 0 ] && grep -qF "update_pr: REFUSE: the push failed" "$t/out"
+  ck "  mutant mut:updreusewt (its line deleted): the checkout is removed and cut again, a second one per update" $?
   # A stopped run reaps its whole descendant tree (R10-PUSHER-REAP): branch fix/t
   # carries the same stub app_push, so a TERM is judged by what survives it.
   # SIGKILL runs no trap, so sigrun below judges that case by the lock alone.
@@ -1162,9 +1209,11 @@ STUB
     HPO_STATE_DIR=$sd STUB_DIR=$sdir BR=fix/r BR_FIXED=1 bash "$m/tools/audit/seat/open_pr.sh" r "$codeR" T G > "$t/outo" 2>&1 & op=$!
     while [ ! -e "$sdir/p2started" ] && [ $k -lt 400 ]; do sleep 0.05; k=$((k + 1)); done
     HPO_STATE_DIR=$sd STUB_DIR=$sdir bash "$m/tools/audit/seat/update_pr.sh" fix/r - "$t/bR.md" > "$t/outu" 2>&1; echo $? > "$t/rcu"
+    [ -z "${RDIRTY:-}" ] || echo scratch > "$sd/pr/r/wt/scratch.txt"  # a dirty opener checkout (carry 6's third control)
     touch "$sdir/release"; wait "$op"; echo $? > "$t/rco"
     git -C "$o" cat-file -e fix/r:dev/programme/delivery/5.md 2>/dev/null && echo 1 > "$t/rowpushed" || echo 0 > "$t/rowpushed"
     git -C "$sd/pr/r/wt" symbolic-ref -q HEAD >/dev/null 2>&1 && echo branch > "$t/opwt" || echo detached > "$t/opwt"
+    { [ -d "$sd/pr/r/wt" ] && echo 1 || echo 0; } > "$t/opdir"; git -C "$m" worktree list > "$t/opwtl"
     cp "$sdir/argv" "$t/argv" 2>/dev/null || : > "$t/argv"
     reap; git -C "$m" worktree remove --force "$sd/pr/r/wt" 2>/dev/null; git -C "$m" worktree remove --force "$sd/pr/upd-fix-r" 2>/dev/null; true
   }
@@ -1185,6 +1234,16 @@ STUB
   ck "  mutant mut:opreuse (its line deleted): the code push asks no reuse verdict, so it runs the full prepr" $?
   racerun release; [ "$(cat "$t/opwt")" = branch ] && [ "$(cat "$t/rowpushed")" = 1 ]
   ck "  mutant mut:release (its line deleted): the opened PR's worktree still holds its branch" $?
+  # Carry 6: once the PR exists with its row, the opener's checkout is collected (update_pr.sh keeps the one
+  # per-PR checkout); one holding work is kept and named, as before.
+  racerun -; [ "$(cat "$t/opdir")" = 0 ] && ! grep -qF "/pr/r/wt" "$t/opwtl" && grep -qF "open_pr: collected " "$t/outo" && [ "$(cat "$t/rowpushed")" = 1 ]
+  ck "open_pr: after the PR opens with its row, no opener checkout remains (collected, and no worktree registered)" $?
+  RDIRTY=1 racerun -; [ "$(cat "$t/opdir")" = 1 ] && grep -qF "open_pr: KEPT " "$t/outo" && grep -qF "it is dirty" "$t/outo" && ! grep -qF "open_pr: collected " "$t/outo"
+  ck "  null control: a dirty opener checkout is kept on its branch and reported, not collected" $?
+  racerun colremove; [ "$(cat "$t/opdir")" = 1 ] && [ "$(cat "$t/rowpushed")" = 1 ]
+  ck "  mutant mut:colremove (its line deleted): the opener's checkout stays after the PR opens (the defect)" $?
+  racerun opcollect; [ "$(cat "$t/opdir")" = 1 ] && [ "$(cat "$t/rowpushed")" = 1 ]
+  ck "  mutant mut:opcollect (its line deleted): open_pr.sh never asks for the collection" $?
   racerun oprowonly; [ "$(sed -n 2p "$t/argv" | cut -d' ' -f1)" = tvofi/heatpump_optimizer ]
   ck "  mutant mut:oprowonly (its line deleted): the row push runs the full prepr" $?
   # R10-FLOW-BODY-ONLY parts (a) and (b), ruling R4: update_pr.sh merges origin/main only when the PR
@@ -1379,7 +1438,7 @@ GH
   [ "$(cat "$t/wtq")" = kept ] && grep -qF "it is dirty" "$t/outq"
   ck "  mutant mut:mergeabort (its line deleted): the conflicted worktree is kept as dirty work (the defect)" $?
   git -C "$o" reset -q --hard HEAD~1; git -C "$o" branch -qD handoff/q; git -C "$o" update-ref -d refs/heads/handoff-body/q
-  racerun oplock; [ "$(cat "$t/rcu")" != 75 ] && ! grep -qF "update_pr: BUSY" "$t/outu" && [ "$(cat "$t/rco")" = 0 ] && [ "$(cat "$t/rowpushed")" = 1 ]
+  racerun oplock; ! grep -qF "update_pr: BUSY: the lock" "$t/outu" && grep -qF "(unpushed work" "$t/outu" && [ "$(cat "$t/rco")" = 0 ] && [ "$(cat "$t/rowpushed")" = 1 ]
   ck "  mutant mut:oplock (its line deleted): update_pr.sh takes the branch (not BUSY); the unpushed-work refusal alone keeps the row" $?
   racerun oplock+unpushed; [ "$(cat "$t/rco")" != 0 ] && grep -qF "is not the committed tip" "$t/outo" && [ "$(cat "$t/rowpushed")" = 0 ]
   ck "  mutants mut:oplock and mut:unpushed (both deleted): the row's push is refused, HEAD detached under it, and the PR keeps no row (the defect)" $?
@@ -1400,9 +1459,11 @@ GH
     reap; git -C "$m" worktree remove --force "$sd/pr/u/wt" 2>/dev/null; git -C "$m" worktree remove --force "$sd/pr/upd-fix-u" 2>/dev/null; git -C "$m" worktree prune; git -C "$m" branch -qD fix/u 2>/dev/null; true
   }
   unpushed - 1
-  [ "$(cat "$t/rcu")" != 0 ] && grep -qF "update_pr: REFUSE: worktree" "$t/outu" && grep -qF "(unpushed work" "$t/outu" \
+  [ "$(cat "$t/rcu")" != 0 ] && grep -qF "update_pr: BUSY: worktree" "$t/outu" && grep -qF "(unpushed work" "$t/outu" \
     && [ "$(cat "$t/attached")" = refs/heads/fix/u ]
   ck "update_pr: a worktree holding the branch with a commit origin lacks is refused and stays on its branch" $?
+  [ "$(cat "$t/rcu")" = 75 ] && grep -qF "update_pr: BUSY: worktree" "$t/outu"
+  ck "  and that refusal is BUSY (75), as a live run's worktree is, so the relay retries it (carry 8)" $?
   unpushed unpushed 1; [ "$(cat "$t/attached")" = detached ] && ! grep -qF "(unpushed work" "$t/outu"
   ck "  mutant mut:unpushed (its line deleted): the worktree is detached under its unpushed commit" $?
   unpushed - 0
diff --git a/tools/audit/seat/update_pr.sh b/tools/audit/seat/update_pr.sh
index fe9c85f6b..60a11a9b9 100755
--- a/tools/audit/seat/update_pr.sh
+++ b/tools/audit/seat/update_pr.sh
@@ -11,8 +11,9 @@
 # `fix/` and then less `-pr` (the first that origin holds). The body is a file here, so a missing
 # handoff-body/<topic> is no refusal; its tip is what names a body sha as one.
 # One run per branch, open_pr.sh's included (pr_args.sh's pr_branch_lock): a second run while one holds
-# the branch's lock ($WT.lock) exits 75, BUSY, having changed nothing (cloud_relay.sh retries it on its next pass); no
-# other stop exits 75. A stopped (TERM/INT/HUP, to the run or its whole group) run reaps its push's whole tree and ends
+# the branch's lock ($WT.lock) exits 75, BUSY, having changed nothing (cloud_relay.sh retries it on its next pass), and so
+# does a branch checked out in a worktree that is not this run's, or a worktree of it holding unpushed commits (pr_busy:
+# a live train's worktree is not a permanent refusal, carry 8); no other stop exits 75. A stopped (TERM/INT/HUP, to the run or its whole group) run reaps its push's whole tree and ends
 # (pr_args.sh's pr_exit_trap); the lock is freed only once that push has ended, a SIGKILLed run's too (pr_push_hold).
 # The lock's holder leaves $WT detached once that push has ended, not holding the branch, a SIGKILLed
 # run's too; a merge the run left stopped on a conflict is aborted first (P276).
@@ -62,12 +63,16 @@ git fetch -q origin "$BR" main
 pr_tools_fresh  # the checkout holding these tools, against the main just fetched (pr_args.sh)
 OWN=$(git worktree list | grep -F "[$BR]" | awk '{print $1}' | grep "^$P/" || true); for o in $OWN; do  # another instrument's clean worktree on the branch is detached, never one holding work origin lacks
   [ "$o" = "$WT" ] && continue; [ -z "$(git -C $o status --porcelain)" ] || continue
-  git merge-base --is-ancestor "$(git -C $o rev-parse HEAD)" "origin/$BR" || pr_refuse "worktree $o holds commits of $BR that origin/$BR lacks (unpushed work, e.g. a PR's row): not detaching it"  # mut:unpushed
+  git merge-base --is-ancestor "$(git -C $o rev-parse HEAD)" "origin/$BR" || pr_busy "worktree $o holds commits of $BR that origin/$BR lacks (unpushed work, e.g. a PR's row): not detaching it"  # mut:unpushed
   git -C $o checkout -q --detach
 done
-git worktree list | grep -F "[$BR]" | grep -vqF "$WT " && { echo "branch $BR checked out elsewhere: $(git worktree list | grep -F "[$BR]")"; exit 1; }
-[ -d $WT ] && git worktree remove --force $WT
-git worktree add -q -B "$BR" $WT origin/$BR; cd $WT
+git worktree list | grep -F "[$BR]" | grep -vqF "$WT " && pr_busy "branch $BR checked out elsewhere: $(git worktree list | grep -F "[$BR]")"  # mut:elsewhere
+# One checkout per pull request (carry 6): the worktree an earlier run left is reset onto the branch and reused, not
+# removed and cut again; anything that cannot be reset falls back to the removal.
+if [ -e "$WT/.git" ]; then git -C "$WT" merge --abort 2>/dev/null || :; fi
+RE=; if [ -e "$WT/.git" ] && git -C "$WT" checkout -q -f -B "$BR" "origin/$BR" 2>/dev/null && git -C "$WT" clean -fdq 2>/dev/null; then RE=1; fi  # mut:updreusewt
+if [ -z "$RE" ]; then [ ! -d $WT ] || git worktree remove --force $WT; git worktree add -q -B "$BR" $WT origin/$BR; fi
+cd $WT
 G="git -c user.name=tvofi -c user.email=70032254+tvofi@users.noreply.github.com"
 LIVE=$(git rev-parse HEAD)  # the pull request's head as origin holds it
 N=${PR_N:-$(gh pr list -R $R --head "$BR" --state open --json number -q '.[0].number')}

## Before you return the verdict (P275)
Run `python3 -I tools/audit/carry_audit.py check --body <PR body file> --comments <file holding [{"id": 0, "body": <verdict.md text>}]>`. Give every reported item its own `Carry: <GROUP> | #<issue> | O<n> | dismissed: <reason>`;
an evidence line flagged by its wording takes `Carry: dismissed: evidence, not a finding`. Return the verdict only at rc 0.
