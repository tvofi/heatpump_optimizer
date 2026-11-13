# Review packet #3541
head: 740e6074cf5bace0302c7f2896b72149c918f010
base: 8a550692da2c80d7ea7f5f26a9c95fc81090a841

Start here (fix-review.md). Re-read the live check state before a verdict: the digest is as read at render.

## Gate digest: red
CodeQL id=131759586694 success
arch-score / arch-score id=131767902668 success
arm id=131759238001 skipped
budget-raise-gate / budget-raise-gate id=131767858876 success
cancel-superseded id=131767857080 success
codeql id=131767858717 skipped
codeql / Analyze (actions) id=131759522390 success
codeql / Analyze (javascript-typescript) id=131759522442 success
codeql / Analyze (python) id=131759522478 success
gate id=131767857033 success
governance id=131767857730 skipped
governance / delivery-status id=131759522395 success
governance / delivery-status-publish id=131759524678 skipped
governance / env-matrix id=131759522364 success
governance / instrument-self-tests id=131759522277 success
governance / policy-docs id=131759522324 success
governance / record id=131759524219 skipped
governance / wave-script id=131759522452 success
hassfest id=131767906504 skipped
hassfest / hassfest id=131759522056 success
kernel-points id=131767886893 skipped
pr-contract id=131767858691 skipped
pr-contract / pr-contract id=131766945685 success
prelude id=131767903166 success
refresh id=131767899973 success
sweep-self id=131768285911 skipped
tests id=131767858793 skipped
tests / arch-instrument id=131759778896 success
tests / briefs id=131759522278 success
tests / browser id=131759778914 success
tests / ci-ratchet id=131766947234 skipped
tests / claims-autofix id=131761238552 skipped
tests / closure-scope id=131759522401 success
tests / closures id=131759778845 success
tests / closures-autofix id=131766947007 skipped
tests / coverage id=131759778754 success
tests / coverage-ratchet id=131760577608 success
tests / fast (3.14) id=131759778791 success
tests / graders-head-copy id=131760577561 success
tests / lane-proofs id=131761603255 success
tests / mutation id=131759522341 success
tests / mutation-autofix id=131759903157 skipped
tests / mutation-pins id=131759901724 skipped
tests / nightly-ha id=131759780792 skipped
tests / nightly-status id=131759522273 failure
tests / replay id=131759780499 skipped
tests / typing id=131759778786 success
validate id=131767916385 skipped
validate / validate-hacs id=131759522088 success

## Refusals
none

## Advisories
hot-file: HPO_BUS_TRAIN_STATE is unset, so every merge verdict reads unboarded

## carry_audit at the head
CARRY-AUDIT: 0 finding item(s): 0 routed, 0 unrouted, 0 bad destination(s)

## figure_lint at the head
ok         bash tools/audit/seat/cloud_relay.sh --self-test
             `tools/audit/seat/cloud_relay.sh` is in the tree at this head
  ok         python3 tests/structure.py
             `tests/structure.py` is in the tree at this head

FIGURES: 2 resolved, 0 not verified, 0 refused

## Finder's harness: none named
### at the base
not run
### at the head
not run

## Mutation-ledger diff
none

## Review scope: full (first round: no --reviewed-head)

## Three-dot diff
diff --git a/dev/programme/delivery/3541.md b/dev/programme/delivery/3541.md
new file mode 100644
index 0000000000..fa3c54e990
--- /dev/null
+++ b/dev/programme/delivery/3541.md
@@ -0,0 +1 @@
+- [#3541](https://github.com/tvofi/heatpump_optimizer/pull/3541) — **open**, R10-REVIEW-DISPATCH-RESIDUE (part 2): r10 review dispatch residue p2 (R10-REVIEW-DISPATCH-RESIDUE)
diff --git a/tools/audit/seat/cloud_relay.sh b/tools/audit/seat/cloud_relay.sh
index c41821c16f..916e567030 100644
--- a/tools/audit/seat/cloud_relay.sh
+++ b/tools/audit/seat/cloud_relay.sh
@@ -218,6 +218,11 @@ ev_case_collision() { # <commit> -> "<a> and <b>" for the first two names under
       if ((k in s) && s[k] != q) { print s[k] " and " q; exit } s[k] = q } }'
 }
 
+pending_red_seen() { # <state dir> <ref sha head> -> the epoch of that key's first RED read, nothing when none (R10-REVIEW-DISPATCH-RESIDUE)
+  awk -v k="$2 " 'index($0, k) == 1 { print substr($0, length(k) + 1); exit }' "$1/cloud-pending-red" 2>/dev/null; }
+pending_red_clear() { # <state dir> <ref sha head>: a check ran (WAIT or GREEN), so the next RED starts a new clock
+  [ -f "$1/cloud-pending-red" ] && { awk -v k="$2 " 'index($0, k) != 1' "$1/cloud-pending-red" > "$1/cloud-pending-red.$$"; mv -f "$1/cloud-pending-red.$$" "$1/cloud-pending-red"; }; return 0; }
+
 relay() { # <pr> <nonce> <head> [<topic>]: with a topic, the verdict was returned at the handoff (probe/revt-<topic>-<n8>, subject `verdict <topic> <head>`)
   local pr=$1 nonce=$2 head=$3 topic=${4:-} ref sha d subj first state led key=$1
   case $pr in ''|*[!0-9]*) die "pr '$pr' is not a number"; return;; esac
@@ -259,19 +264,39 @@ relay() { # <pr> <nonce> <head> [<topic>]: with a topic, the verdict was returne
   # PENDING-CI (R10-CLOUD-POOL carry 5, moved to R10-DISPATCH-AT-HANDOFF): a reviewer whose review is complete
   # while CI at the head is still pending returns the verdict with a `pending-ci: <why>` line instead of waiting
   # without bound. The relay posts it only once classify reads the head GREEN; WAIT holds it (rc 75, one line
-  # each pass, retried); RED refuses it (the PR goes back to its fixer); a PR head that moved refuses the draft,
-  # with the head it was drafted at and the head now.
+  # each pass, retried). A PR head that moved is asked of review_carry (--verdict-only): CARRY classifies the LIVE
+  # head and posts on GREEN (the verdict names the drafted head, as a handoff verdict does), anything else refuses
+  # the draft, with the head it was drafted at and the head now. RED holds as WAIT does (a red the branch did not
+  # cause clears when main is merged, or when a judged run ends, with no fixer work: PRs 3425 and 3430) and is
+  # refused only after HPO_RELAY_PENDING_RED_SECS (default 21600) since the first RED read at that head, no
+  # check having run in between (a WAIT or GREEN read clears the record). Both refusals are OWED re-dispatch.
   if grep -q '^pending-ci: ' "$d/verdict.md"; then  # mut:pendingci
-    local live cls crc
+    local live cls crc cl=$head carried= rkey redsecs=${HPO_RELAY_PENDING_RED_SECS:-21600} seen reds
     live=$(if [ -n "${HPO_RELAY_PRHEAD:-}" ]; then "$HPO_RELAY_PRHEAD" "$pr"; else gh pr view "$pr" -R "${HPO_RELAY_REPO:-tvofi/heatpump_optimizer}" --json headRefOid --jq .headRefOid; fi 2>/dev/null)
     if ! printf '%s' "$live" | grep -Eq '^[0-9a-f]{40}$'; then echo "cloud_relay: #$pr's head could not be read, so its pending-ci draft is held" >&2; return 75; fi
-    [ "$live" = "$head" ] || { die "the head moved under a pending-ci draft: drafted at $head, #$pr is at $live; it is not posted, and the PR is re-dispatched at its head"; return; }  # mut:pendinghead
-    cls=$(${HPO_RELAY_CLASSIFY:-python3 -I "$HERE/merge_train.py" classify} "$head" --repo "${HPO_RELAY_REPO:-tvofi/heatpump_optimizer}" --pr "$pr" 2>&1); crc=$?
+    case $redsecs in ''|*[!0-9]*) echo "cloud_relay: HPO_RELAY_PENDING_RED_SECS must be seconds; the pending-ci draft is held" >&2; return 75;; esac
+    if [ "$live" != "$head" ]; then
+      git fetch -q origin "$head" "$live" 2>/dev/null || :
+      if ${HPO_RELAY_CARRY:-python3 -I "$HERE/review_carry.py"} "$head" "$live" --verdict-only >/dev/null 2>&1; then  # mut:pendingcarry
+        cl=$live; carried=" (the verdict carried from ${head:0:12}: review_carry CARRY)"
+      else
+        echo "cloud_relay: OWED re-dispatch #$pr $live"
+        die "the head moved under a pending-ci draft: drafted at $head, #$pr is at $live; it is not posted"; return  # mut:pendinghead
+      fi
+    fi
+    rkey="$ref $sha $cl"
+    cls=$(${HPO_RELAY_CLASSIFY:-python3 -I "$HERE/merge_train.py" classify} "$cl" --repo "${HPO_RELAY_REPO:-tvofi/heatpump_optimizer}" --pr "$pr" 2>&1); crc=$?
     case $crc in
-      0|4) echo "cloud_relay: pending-ci draft for #$pr: CI at $head is now GREEN (classify rc $crc); relaying" ;;
-      3) echo "cloud_relay: HELD-PENDING-CI #$pr $head: $(sed -n 's/^WAIT *//p' <<< "$cls" | head -n 1) (classify WAIT); the draft posts when CI is green"; return 75 ;;
-      1) die "CI is red at $head (classify RED): a pending-ci draft is not posted over a red; the PR goes back to its fixer"; return ;;
-      *) echo "cloud_relay: classify could not read $head (rc $crc): $(last_line "$cls"); the pending-ci draft is held" >&2; return 75 ;;
+      0|4) pending_red_clear "$state" "$rkey"; echo "cloud_relay: pending-ci draft for #$pr: CI at $cl is now GREEN (classify rc $crc)$carried; relaying" ;;
+      3) pending_red_clear "$state" "$rkey"; echo "cloud_relay: HELD-PENDING-CI #$pr $cl: $(sed -n 's/^WAIT *//p' <<< "$cls" | head -n 1) (classify WAIT); the draft posts when CI is green"; return 75 ;;
+      1) reds=$(sed -n 's/^RED *//p' <<< "$cls" | head -n 1); seen=$(pending_red_seen "$state" "$rkey")
+        if [ -n "$seen" ] && [ $(($(date +%s) - seen)) -ge "$redsecs" ]; then  # mut:pendingredbound
+          echo "cloud_relay: OWED re-dispatch #$pr $cl"
+          die "CI has read RED at $cl since $(date -u -d "@$seen" +%FT%TZ) with no check running ($reds; classify RED): a pending-ci draft is not posted over a red"; return
+        fi
+        [ -n "$seen" ] || { mkdir -p "$state" && printf '%s %s\n' "$rkey" "$(date +%s)" >> "$state/cloud-pending-red"; }
+        echo "cloud_relay: HELD-PENDING-CI-RED #$pr $cl: $reds (classify RED)"; return 75 ;;  # mut:pendingredhold
+      *) echo "cloud_relay: classify could not read $cl (rc $crc): $(last_line "$cls"); the pending-ci draft is held" >&2; return 75 ;;
     esac
   fi
   local out sha2 wt tip tries=0
@@ -340,6 +365,7 @@ probe_arm() { # one pass over every probe/* ref: rev-* relays each unseen ref+sh
     case $ref in refs/heads/probe/rev-*|refs/heads/probe/revt-*) ;;
       *) disposed "$ref" "$sha" || { level_line probe-ref "$ref" "$sha" >> "$state/cloud-level-probe.$$"; echo "cloud_relay: OWED probe-ref $ref $sha"; }; continue;; esac
     if [ -f "$led" ] && grep -qxF "$ref $sha" "$led"; then continue; fi
+    if disposed "$ref" "$sha"; then continue; fi  # mut:probedispose -- handled by the orchestrator at this sha; relayed again once it moves
     if [ -f "$led.refused" ] && grep -qxF "$ref $sha" "$led.refused"; then
       # a refusal is owed until disposed; one recorded before reasons were kept stays silent
       why=$(awk -v r="$ref" -v s="$sha" '$1 == r && $2 == s { $1 = $2 = ""; w = substr($0, 3) } END { print w }' "$led.refused-why" 2>/dev/null)
@@ -760,21 +786,47 @@ stuck_arm() { # one pass over the branch locks: each held past HPO_PUSH_STUCK_SE
 # cloud-sessions file is written anywhere in the tree, so the session id is not named; the
 # dispatch tip and its age are. Past HPO_RELAY_NORETURN_WINDOW_SECS (default 172800) a dispatch
 # falls off: its refs may be gone with a merged branch. Deleting the dispatch ref disposes it.
-# A listing or fetch that fails leaves the level as it was. Reviewer and designer seats are out
-# of scope: a reviewer's missing verdict is reviewer-fire's, in the ledger.
+# A listing or fetch that fails leaves the level as it was. Designer seats are out of scope.
+# A reviewer on dispatch/reviewer-* is covered by the same arm with its own bound,
+# HPO_RELAY_NORETURN_REVIEWER_SECS (default 5400, above the 66 min longest returner measured in the
+# s13/rca-noreturn RCA; the fixer's bound stays HPO_RELAY_NORETURN_SECS): one whose dispatch tip is older than
+# that, whose PROMPT.md nonce (first 8) names no probe/rev-<pr>-<n8> or probe/revt-<topic>-<n8>, and whose PR
+# head (read by HPO_RELAY_PRHEAD, else gh) is still the dispatched head, is owed on the same level. A moved
+# head means the dispatch was superseded, and an unreadable head is silent (unknown is not owed). The
+# ledger's reviewer-fire entry closes at the fire, so nothing else owes a reviewer that never returned.
 noreturn_arm() {
-  local state=${HPO_STATE_DIR:-$HOME/.local/state/hpo} lim=${HPO_RELAY_NORETURN_SECS:-7200} win=${HPO_RELAY_NORETURN_WINDOW_SECS:-172800}
-  local now sha ref topic t age r rs moved
-  case $lim$win in *[!0-9]*) echo "cloud_relay: HPO_RELAY_NORETURN_SECS/WINDOW must be seconds; the level stays" >&2; return 0;; esac
+  local state=${HPO_STATE_DIR:-$HOME/.local/state/hpo} lim=${HPO_RELAY_NORETURN_SECS:-7200} win=${HPO_RELAY_NORETURN_WINDOW_SECS:-172800} rlim=${HPO_RELAY_NORETURN_REVIEWER_SECS:-5400}
+  local now sha ref topic t age r rs moved first rpr rhead rn8 rlive
+  case $lim$win$rlim in *[!0-9]*) echo "cloud_relay: HPO_RELAY_NORETURN_SECS/WINDOW/REVIEWER_SECS must be seconds; the level stays" >&2; return 0;; esac
   mkdir -p "$state" || return 0
   # Only the dispatch refs are listed by glob; each candidate's return refs are asked by name, so no
   # glob here lists a handoff-wip step ref (cloud_dispatch.py pins that no handoff arm sees one).
-  git ls-remote origin 'refs/heads/dispatch/fixer-*' > "$state/cloud-nr.$$" \
-    && git fetch -q origin '+refs/heads/dispatch/fixer-*:refs/hpo-relay/dispatch/fixer-*' 2>/dev/null \
+  git ls-remote origin 'refs/heads/dispatch/fixer-*' 'refs/heads/dispatch/reviewer-*' > "$state/cloud-nr.$$" \
+    && git fetch -q origin '+refs/heads/dispatch/fixer-*:refs/hpo-relay/dispatch/fixer-*' '+refs/heads/dispatch/reviewer-*:refs/hpo-relay/dispatch/reviewer-*' 2>/dev/null \
     || { echo "cloud_relay: the dispatch refs could not be read; the no-return level stays" >&2; rm -f "$state/cloud-nr.$$"; return 0; }
   now=$(date +%s); : > "$state/cloud-level-nr.$$"
   while read -r sha ref; do
-    case $ref in refs/heads/dispatch/fixer-?*) topic=${ref#refs/heads/dispatch/fixer-} ;; *) continue ;; esac
+    case $ref in
+      refs/heads/dispatch/reviewer-?*)
+        t=$(git log -1 --format=%ct "$sha" 2>/dev/null) || continue; age=$((now - t))
+        [ "$age" -gt "$rlim" ] && [ "$age" -le "$win" ] || continue  # mut:noreturnrevage
+        first=$(git show "$sha:PROMPT.md" 2>/dev/null | head -n 1)
+        rn8=$(sed -n 's/^CLOUD REVIEWER seat for .*, at head [0-9a-f]\{40\}\. Bus nonce: \([0-9a-f]\{8\}\)[0-9a-f]*\..*/\1/p' <<< "$first")
+        rhead=$(sed -n 's/^CLOUD REVIEWER seat for .*, at head \([0-9a-f]\{40\}\)\. Bus nonce:.*/\1/p' <<< "$first")
+        rpr=$(sed -n 's/^CLOUD REVIEWER seat for PR #\([0-9][0-9]*\) of .*/\1/p' <<< "$first")
+        [ -n "$rn8" ] && [ -n "$rhead" ] || continue  # not a reviewer's prompt, or no nonce to match a return by
+        git ls-remote origin "refs/heads/probe/rev-*-$rn8" "refs/heads/probe/revt-*-$rn8" > "$state/cloud-nrr.$$" || continue
+        [ -s "$state/cloud-nrr.$$" ] && continue  # mut:noreturnrevret -- the verdict came back
+        if [ -n "$rpr" ]; then  # mut:noreturnrevmoved
+          rlive=$(if [ -n "${HPO_RELAY_PRHEAD:-}" ]; then "$HPO_RELAY_PRHEAD" "$rpr"; else gh pr view "$rpr" -R "${HPO_RELAY_REPO:-tvofi/heatpump_optimizer}" --json headRefOid --jq .headRefOid; fi 2>/dev/null)
+          [ "$rlive" = "$rhead" ] || continue
+        fi
+        echo "cloud_relay: SEAT ENDED NO RETURN reviewer ${rpr:+#$rpr }${ref#refs/heads/dispatch/reviewer-} (dispatch ${sha:0:12}, $((age / 60))min, no probe/rev ref and the PR head unmoved)"
+        level_line seat-no-return "$ref" "$sha" "SEAT ENDED NO RETURN reviewer ${rpr:+#$rpr }${ref#refs/heads/dispatch/reviewer-} $((age / 60))min" >> "$state/cloud-level-nr.$$"
+        continue ;;
+      refs/heads/dispatch/fixer-?*) topic=${ref#refs/heads/dispatch/fixer-} ;;
+      *) continue ;;
+    esac
     t=$(git log -1 --format=%ct "$sha" 2>/dev/null) || continue
     age=$((now - t))
     [ "$age" -gt "$lim" ] && [ "$age" -le "$win" ] || continue  # mut:noreturnage
@@ -1176,6 +1228,14 @@ EOF
   X=$t/other.log; printf 'OWED 2026-01-01T00:00:00Z probe-ref refs/heads/probe/scan-y %s\n' "$h" > "$X.level"
   chk "dispose --log FILE (the CLI) takes the ref" 0 bash "$HERE/cloud_relay.sh" dispose --log "$X" refs/heads/probe/scan-y "$h"
   chk "and drops its line from the level beside that log" 1 grep -q scan-y "$X.level"
+  # Carry 30: a rev-/revt- ref the orchestrator disposed at its sha is not relayed; once it moves it is relayed at the new sha.
+  rm -f "$t/state/cloud-relayed" "$t/state/cloud-relayed.refused" "$t/state/cloud-relayed.refused-why" "$t/state/cloud-relayed.tries" "$t/pushed"
+  R30=refs/heads/probe/rev-5-${n:0:8}; mk 5 $h $h $n; probe_arm >/dev/null 2>&1
+  chk "null control: an undisposed rev- ref is relayed (pushed for #5)" 0 test "$(cat "$t/pushed" 2>/dev/null)" = 5
+  mk 5 $h $h $n; P30=$(git -C "$t/o.git" rev-parse "$R30"); dispose "$R30" "$P30" >/dev/null; rm -f "$t/pushed"; T30=$(rtip 5); probe_arm >/dev/null 2>&1
+  chk "a rev- ref disposed at its sha is not relayed: nothing pushed, review/5 unmoved" 0 test ! -s "$t/pushed" -a "$(rtip 5)" = "$T30" -a -z "$(grep -x "$R30 $P30" "$t/state/cloud-relayed")"
+  mk 5 $h $h $n; P30B=$(git -C "$t/o.git" rev-parse "$R30"); probe_arm >/dev/null 2>&1
+  chk "null control: a disposed ref whose tip moved is relayed at the new sha" 0 test "$P30B" != "$P30" -a "$(cat "$t/pushed" 2>/dev/null)" = 5 -a -n "$(grep -x "$R30 $P30B" "$t/state/cloud-relayed")"
   # A verdict returned at the handoff (Carry 0): probe/revt-<topic>-<n8>, held until the topic's PR opens (bus.sh rekey),
   # relayed when review_carry answers CARRY for handoff-head..PR-head, refused as stale when it does not.
   LOG=$t/topicv.log; LV=$LOG.level; : > "$LOG"; rm -f "$LV" "$t/state/cloud-relayed" "$t/state/cloud-relayed.refused" "$t/state/cloud-relayed.refused-why" "$t/state/cloud-relayed.tries"
@@ -1208,12 +1268,16 @@ EOF
   chk "null control: the same verdict over a head that carries is relayed at the handoff head, on #71" 0 test "$(cat "$t/pushed")" = 71
   chk "and the carry predicate was asked handoff-head then PR-head" 0 grep -qx "$th $PH --verdict-only" "$t/carry.args"
   chk "and its ref and sha are recorded as relayed" 0 grep -q "^refs/heads/probe/revt-tp-1-${tn:0:8} " "$t/state/cloud-relayed"
+  mkt tp-1 $th; RT30=refs/heads/probe/revt-tp-1-${tn:0:8}; PT30=$(git -C "$t/o.git" rev-parse "$RT30"); dispose "$RT30" "$PT30" >/dev/null; : > "$t/pushed"; out=$(probe_arm 2>&1)
+  chk "Carry 30: a revt- ref disposed at its sha is not relayed either" 0 test ! -s "$t/pushed" -a -z "$(grep -x "$RT30 $PT30" "$t/state/cloud-relayed")"
+  mkt tp-1 $th; probe_arm >/dev/null 2>&1
+  chk "and a disposed revt- ref that moved is relayed at its new sha (null control)" 0 test "$(cat "$t/pushed")" = 71
   unset HPO_RELAY_PRHEAD HPO_RELAY_CARRY
   # PENDING-CI drafts (R10-CLOUD-POOL carry 5): a verdict carrying `pending-ci:` posts only when classify reads its head GREEN.
   rm -f "$t/state/cloud-relayed" "$t/pushed"; HPO_RELAY_PUSH=$stub; CONFIRM=
   clstub=$t/classify.sh; printf '#!/bin/sh\necho "$@" > "%s/classify.args"\ncase "$(cat "%s/cls")" in 0) echo GREEN;; 3) echo "WAIT tests / fast gate";; 1) echo "RED tests / fast gate red: x";; *) echo boom;; esac\nexit "$(cat "%s/cls")"\n' "$t" "$t" "$t" > "$clstub"; chmod +x "$clstub"
   phh=$t/ph-h.sh; printf '#!/bin/sh\necho %s\n' "$h" > "$phh"; chmod +x "$phh"; phm=$t/ph-m.sh; printf '#!/bin/sh\necho %s\n' "$PH" > "$phm"; chmod +x "$phm"
-  mkp() { mk 72 $h $h $n; rm -rf "$t/pr"; throwaway_git_init "$t/pr" -q; mkdir "$t/pr/ev"; echo "pc $h" > "$t/pr/ev/e"
+  mkp() { mk 72 $h $h $n; rm -rf "$t/pr"; throwaway_git_init "$t/pr" -q; mkdir "$t/pr/ev"; echo "pc $h $((c=c+1))" > "$t/pr/ev/e"
     printf 'Fix review: merge %s\n\nbus-nonce: %s\npending-ci: tests / fast gate\n' "$h" "$n" > "$t/pr/verdict.md"
     git -C "$t/pr" add -A; git -C "$t/pr" commit -qm "verdict 72 $h"; git -C "$t/o.git" fetch -qf "$t/pr" "HEAD:refs/heads/probe/rev-72-${n:0:8}"; }
   export HPO_RELAY_CLASSIFY=$clstub HPO_RELAY_PRHEAD=$phh; mkp
@@ -1222,8 +1286,8 @@ EOF
   chk "and nothing is pushed or recorded while it is held" 0 test ! -s "$t/pushed" -a ! -s "$t/state/cloud-relayed"
   chk "classify was asked the head and the PR" 0 grep -qx "$h --repo tvofi/heatpump_optimizer --pr 72" "$t/classify.args"
   echo 1 > "$t/cls"; out=$(relay 72 $n $h 2>&1); rc=$?
-  chk "a pending-ci draft over a RED head is refused (rc 2), naming the red" 0 test "$rc" = 2 -a -n "$(grep -m1 'classify RED' <<< "$out")"
-  export HPO_RELAY_PRHEAD=$phm; echo 0 > "$t/cls"; out=$(relay 72 $n $h 2>&1); rc=$?
+  chk "a pending-ci draft over a RED head is held (rc 75), naming the red, not refused (R10-REVIEW-DISPATCH-RESIDUE carry 23)" 0 test "$rc" = 75 -a -n "$(grep -m1 "HELD-PENDING-CI-RED #72 $h: tests / fast gate red: x (classify RED)" <<< "$out")"
+  export HPO_RELAY_PRHEAD=$phm HPO_RELAY_CARRY=$cstubno; echo 0 > "$t/cls"; out=$(relay 72 $n $h 2>&1); rc=$?
   chk "a pending-ci draft whose PR head moved is refused (rc 2), naming both heads, though CI is green" 0 test "$rc" = 2 -a -n "$(grep -m1 "drafted at $h, #72 is at $PH" <<< "$out")"
   export HPO_RELAY_PRHEAD=$phh; echo 9 > "$t/cls"; out=$(relay 72 $n $h 2>&1); rc=$?
   chk "an unreadable classify holds the draft (rc 75), never reads it as green" 0 test "$rc" = 75 -a ! -s "$t/pushed"
@@ -1231,6 +1295,35 @@ EOF
   chk "null control: the same draft over a GREEN head at the same head relays on #72" 0 test "$rc" = 0 -a "$(cat "$t/pushed")" = 72
   rm -f "$t/state/cloud-relayed" "$t/pushed"; mk 72 $h $h $n; echo 3 > "$t/cls"; out=$(relay 72 $n $h 2>&1); rc=$?
   chk "null control: a verdict with no pending-ci line never asks classify (a WAIT head still relays)" 0 test "$rc" = 0 -a "$(cat "$t/pushed")" = 72
+  # Carry 21: a moved head is asked of review_carry; CARRY classifies the LIVE head and posts on GREEN.
+  rm -f "$t/state/cloud-relayed" "$t/pushed" "$t/carry.args" "$t/classify.args"; mkp
+  export HPO_RELAY_PRHEAD=$phm HPO_RELAY_CARRY=$cstubok; echo 0 > "$t/cls"; out=$(relay 72 $n $h 2>&1); rc=$?
+  chk "moved head + review_carry CARRY + GREEN at the live head posts on #72, saying the verdict was carried" 0 test "$rc" = 0 -a "$(cat "$t/pushed")" = 72 -a -n "$(grep -m1 'GREEN.*verdict carried from' <<< "$out")"
+  chk "and review_carry was asked drafted head then live head, and classify the live head" 0 grep -qx "$h $PH --verdict-only" "$t/carry.args" -a "$(cut -d' ' -f1 "$t/classify.args")" = "$PH"
+  rm -f "$t/state/cloud-relayed" "$t/pushed"; mkp; export HPO_RELAY_CARRY=$cstubno; out=$(relay 72 $n $h 2>&1); rc=$?
+  chk "moved head + review_carry FRESH-REVIEW + GREEN refuses (rc 2), posts nothing, owes the re-dispatch" 0 test "$rc" = 2 -a ! -s "$t/pushed" -a -n "$(grep -m1 "^cloud_relay: OWED re-dispatch #72 $PH" <<< "$out")"
+  export HPO_RELAY_CARRY=$cstubun; out=$(relay 72 $n $h 2>&1); rc=$?
+  chk "moved head + review_carry CANNOT DECIDE refuses as today (rc 2)" 0 test "$rc" = 2 -a ! -s "$t/pushed"
+  export HPO_RELAY_CARRY=$cstubok; echo 3 > "$t/cls"; out=$(relay 72 $n $h 2>&1); rc=$?
+  chk "moved head + CARRY + WAIT at the live head holds (rc 75), naming the live head" 0 test "$rc" = 75 -a ! -s "$t/pushed" -a -n "$(grep -m1 "HELD-PENDING-CI #72 $PH" <<< "$out")"
+  echo 1 > "$t/cls"; out=$(relay 72 $n $h 2>&1); rc=$?
+  chk "moved head + CARRY + RED at the live head posts nothing (held rc 75, the red is not the carry's to post over)" 0 test "$rc" = 75 -a ! -s "$t/pushed"
+  rm -f "$t/state/cloud-pending-red"
+  export HPO_RELAY_PRHEAD=$phh; rm -f "$t/carry.args"; echo 0 > "$t/cls"; out=$(relay 72 $n $h 2>&1); rc=$?
+  chk "null control: the same head + GREEN posts as today and never asks review_carry" 0 test "$rc" = 0 -a "$(cat "$t/pushed")" = 72 -a ! -e "$t/carry.args"
+  # Carry 23: RED holds (rc 75) and is refused only past the bound since its first read at that head.
+  rm -f "$t/state/cloud-relayed" "$t/pushed" "$t/state/cloud-pending-red"; mkp; echo 1 > "$t/cls"; out=$(relay 72 $n $h 2>&1); rc=$?
+  chk "RED records its first read in the state dir, keyed ref sha head" 0 grep -qE "^refs/heads/probe/rev-72-${n:0:8} [0-9a-f]{40} $h [0-9]+$" "$t/state/cloud-pending-red"
+  echo 1 > "$t/cls"; out=$(relay 72 $n $h 2>&1); rc=$?
+  chk "a second RED pass holds again and keeps the first read (one record)" 0 test "$rc" = 75 -a "$(grep -c . "$t/state/cloud-pending-red")" = 1
+  echo 0 > "$t/cls"; out=$(relay 72 $n $h 2>&1); rc=$?
+  chk "RED, then GREEN at the same head, posts on #72 and clears the record" 0 test "$rc" = 0 -a "$(cat "$t/pushed")" = 72 -a ! -s "$t/state/cloud-pending-red"
+  rm -f "$t/state/cloud-relayed" "$t/pushed"; mkp; echo 1 > "$t/cls"; relay 72 $n $h >/dev/null 2>&1; echo 3 > "$t/cls"; relay 72 $n $h >/dev/null 2>&1
+  chk "a WAIT read between two REDs clears the record (a check ran, so the clock restarts)" 0 test ! -s "$t/state/cloud-pending-red"
+  echo 1 > "$t/cls"; relay 72 $n $h >/dev/null 2>&1; export HPO_RELAY_PENDING_RED_SECS=0; out=$(relay 72 $n $h 2>&1); rc=$?
+  chk "RED past the bound refuses (rc 2), prints the OWED re-dispatch line, posts nothing" 0 test "$rc" = 2 -a ! -s "$t/pushed" -a -n "$(grep -m1 "^cloud_relay: OWED re-dispatch #72 $h$" <<< "$out")"
+  chk "and the first RED read never refuses, whatever the bound (null control: nothing to age yet)" 0 test "$(rm -f "$t/state/cloud-pending-red"; relay 72 $n $h >/dev/null 2>&1; echo $?)" = 75
+  unset HPO_RELAY_PENDING_RED_SECS HPO_RELAY_CARRY; rm -f "$t/state/cloud-pending-red"
   unset HPO_RELAY_CLASSIFY HPO_RELAY_PRHEAD
   # the handoff arm (a bare origin holds PR branches, handoff/ and handoff-body/ refs)
   unset HPO_RELAY_PUSH; export HPO_RELAY_PUSH=$stub; LOG=$t/pass.log; : > "$LOG"; CONFIRM=
@@ -1878,6 +1971,24 @@ open(sys.argv[1], "w").close(); time.sleep(60)' "$t/stuck.held" "$t/state/pr/upd
   LOG=$t/nr2.log; : > "$LOG"; nrc dispatch/fixer-nr-p 10800
   nro=$(handoff_arm() { :; }; probe_arm() { :; }; CONFIRM= pass 2>&1)
   chk "a pass runs the no-return arm" 0 grep -q "SEAT ENDED NO RETURN nr-p " <<< "$nro"
+  # Carry 7: a reviewer dispatched (dispatch/reviewer-*) past HPO_RELAY_NORETURN_REVIEWER_SECS with no probe/rev ref and an unmoved PR head.
+  LOG=$t/nr3.log; : > "$LOG"; rm -f "$LOG.level"; RH=$h; RM=2222222222222222222222222222222222222222
+  printf '#!/bin/sh\ncase "$1" in 3400) echo %s;; *) echo %s;; esac\n' "$RM" "$RH" > "$t/nrph.sh"; chmod +x "$t/nrph.sh"; export HPO_RELAY_PRHEAD=$t/nrph.sh
+  nrn() { printf '%08d%s' "$1" abcdef0123456789abcdef01; }  # the nonce for PR <n>: its first 8 name the return ref
+  nrv() { # <pr> <age s> <returned 0|1>: dispatch/reviewer-rev-<pr> aged <age>, its PROMPT.md first line as cloud_dispatch.py renders it
+    printf 'CLOUD REVIEWER seat for PR #%s of tvofi/heatpump_optimizer, at head %s. Bus nonce: %s. Never send push notifications.\n' "$1" "$RH" "$(nrn "$1")" > "$t/nr/PROMPT.md"
+    git -C "$t/nr" add PROMPT.md; nrc dispatch/reviewer-rev-$1 "$2"; git -C "$t/nr" rm -q --cached PROMPT.md; rm -f "$t/nr/PROMPT.md"
+    [ "$3" != 1 ] || nrc probe/rev-$1-$(nrn "$1" | cut -c1-8) 60; }
+  for pr in 3339 3350 3297 3325; do nrv $pr 6000 0; done; for pr in 3352 3353 3304 3359; do nrv $pr 6000 1; done
+  nrv 3400 6000 0; nrv 3401 4000 0; nrc dispatch/fixer-nr-mid 6000
+  nro=$(noreturn_arm 2>&1)
+  for pr in 3339 3350 3297 3325; do chk "Carry 7: reviewer #$pr dispatched 100 min ago with no probe/rev ref is SEAT ENDED NO RETURN" 0 grep -q "SEAT ENDED NO RETURN reviewer #$pr rev-$pr (dispatch [0-9a-f]\{12\}, 100min" <<< "$nro"; done
+  chk "and owed seat-no-return on the level" 0 grep -qE "^OWED [^ ]+ seat-no-return refs/heads/dispatch/reviewer-rev-3339 [0-9a-f]{40} SEAT ENDED NO RETURN reviewer #3339 rev-3339 100min$" "$LOG.level"
+  for pr in 3352 3353 3304 3359; do chk "Carry 7: reviewer #$pr whose probe/rev-$pr-<n8> came back is silent" 1 grep -q "reviewer #$pr " <<< "$nro"; done
+  chk "a reviewer whose PR head moved since the dispatch is silent" 1 grep -q "reviewer #3400 " <<< "$nro"
+  chk "a reviewer dispatched 4000 s ago (under 5400 s) is silent" 1 grep -q "reviewer #3401 " <<< "$nro"
+  chk "the bounds are distinct: a fixer dispatched 6000 s ago (under 7200 s) is silent beside the reviewers" 1 grep -q " nr-mid " <<< "$nro"
+  unset HPO_RELAY_PRHEAD
   # THE CARRY-FOLD ARM (R10-CARRY-RESIDUE-2 carry 14): a BLOCKED.md naming CARRY-LANDED alone, with its body kept on
   # handoff-wip/<topic>-body, is folded (carry_fold.py) and re-pushed (body_push.sh); any other block prints a line and folds nothing.
   throwaway_git_init "$t/cf.git" -q --bare; throwaway_git_init "$t/cfw" -q; cd "$t/cfw" || exit 1

## Before you return the verdict (P275)
Run `python3 -I tools/audit/carry_audit.py check --body <PR body file> --comments <file holding [{"id": 0, "body": <verdict.md text>}]>`. Give every reported item its own `Carry: <GROUP> | #<issue> | O<n> | dismissed: <reason>`;
an evidence line flagged by its wording takes `Carry: dismissed: evidence, not a finding`. Return the verdict only at rc 0.
