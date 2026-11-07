# Review packet #3252
head: b9cc5e32e26b8ebdec66cc8bba9ee110a96c04a0
base: 601b9695a68533814c68e36caba36fda57fe2d77

Start here (fix-review.md). Re-read the live check state before a verdict: the digest is as read at render.

## Gate digest: red
CodeQL id=128377977460 success
arch-score / arch-score id=128377933244 success
arm id=128377835719 skipped
budget-raise-gate / budget-raise-gate id=128377933372 success
cancel-superseded id=128377835113 success
codeql / Analyze (actions) id=128377933315 success
codeql / Analyze (javascript-typescript) id=128377933414 success
codeql / Analyze (python) id=128377933411 success
governance / delivery-status id=128377933322 success
governance / delivery-status-publish id=128377934714 skipped
governance / env-matrix id=128377933359 success
governance / instrument-self-tests id=128377933374 in_progress
governance / policy-docs id=128377933348 success
governance / record id=128377934679 skipped
governance / wave-script id=128377933349 success
hassfest / hassfest id=128377933338 success
kernel-points id=128377933999 skipped
prelude id=128377835075 success
refresh id=128377834945 success
tests / arch-instrument id=128378041840 success
tests / briefs id=128377933435 success
tests / browser id=128378041808 success
tests / claims-autofix id=128380985010 skipped
tests / closure-scope id=128377933389 success
tests / closures id=128378041835 success
tests / closures-autofix id=128382372457 skipped
tests / coverage id=128378041756 in_progress
tests / fast (3.14) id=128378041774 success
tests / mutation id=128377933387 success
tests / mutation-autofix id=128378077070 skipped
tests / mutation-pins id=128378076689 skipped
tests / nightly-ha id=128378042772 skipped
tests / nightly-status id=128377933403 failure
tests / replay id=128378042733 skipped
tests / typing id=128378041923 success
validate / validate-hacs id=128377933353 success

## Refusals
none

## Advisories
hot-file: HPO_BUS_TRAIN_STATE is unset, so every merge verdict reads unboarded

## carry_audit at the head
CARRY-AUDIT: 0 finding item(s): 0 routed, 0 unrouted, 0 bad destination(s)

## figure_lint at the head
ok         bash tools/audit/seat/bus.sh --self-test
             `tools/audit/seat/bus.sh` is in the tree at this head
  ok         python3 -I tools/audit/seat/orchestrator_tick.py --self-test
             `tools/audit/seat/orchestrator_tick.py` is in the tree at this head
  ok         bash tools/audit/seat/cloud_relay.sh --self-test
             `tools/audit/seat/cloud_relay.sh` is in the tree at this head
  ok         bash tools/audit/seat/tick_loop.sh --self-test
             `tools/audit/seat/tick_loop.sh` is in the tree at this head
  ok         python3 tests/closure.py select --diff $(git merge-base origin/main HEAD) --workdir $D
             `tests/closure.py` is in the tree at this head
  ok         python3 tests/structure.py
             `tests/structure.py` is in the tree at this head
  ok         node tools/policy/policy_lint.mjs
             `tools/policy/policy_lint.mjs` is in the tree at this head
  ok         node tools/policy/rules_sync.mjs --check
             `tools/policy/rules_sync.mjs` is in the tree at this head
  ok         python3 tools/audit/seat/bare_array.py --check
             `tools/audit/seat/bare_array.py` is in the tree at this head
  unverified bash --version
             bash with no script argument

FIGURES: 9 resolved, 1 not verified, 0 refused

## Finder's harness: none named
### at the base
not run
### at the head
not run

## Mutation-ledger diff
none

## Three-dot diff
diff --git a/dev/audit/rca/R10-RELAY-REPLAY.md b/dev/audit/rca/R10-RELAY-REPLAY.md
new file mode 100644
index 000000000..b0fe0609b
--- /dev/null
+++ b/dev/audit/rca/R10-RELAY-REPLAY.md
@@ -0,0 +1,55 @@
+# R10-RELAY-REPLAY: a restarted relay loop replayed 93 probes onto review refs
+
+Root-cause seat, `root-cause.md`. Figures are the ones measured when the defect was
+found; they are not re-derived here.
+
+## Defect
+
+`cloud_relay.sh`'s `relay()` pushed a `probe/rev-*` verdict to `review/<pr>` whenever
+the probe was missing from its ledger. A loop restarted without `HPO_STATE_DIR` read the
+stale default ledger (`$HOME/.local/state/hpo/cloud-relayed`), found no entry for any
+probe, and replayed 93 probes as 92 commits on 56 `review/<pr>` refs, 53 of them on
+closed PRs.
+
+## Cause
+
+The ledger was the only record of delivery, and the loop's state directory came from an
+environment variable nothing printed. A wrong or empty ledger therefore read as "nothing
+delivered", and relay's only reaction to "not in the ledger" was to push.
+
+## Process state
+
+(c): the process was followed and did not produce the intended result. The restart
+followed the documented loop command; the ledger rule ("push once, then record") held
+only while the ledger was the right one.
+
+## Countermeasure
+
+- Delivered guard in `relay()`: if `review/<pr>` already has a commit with the probe's
+  tree, record the probe as relayed and push nothing.
+- Each pass prints `cloud_relay: state dir <dir>, ledger <path>, log <path>` once, so
+  a wrong state directory is visible in the first log line.
+- Self-tests: `cloud_relay.sh --self-test` (new tree pushed, delivered tree skipped,
+  oldest of many review commits found, one state-dir line per pass).
+
+## Cost test
+
+    cost(countermeasure) < cost(defect) x P(recurrence)
+
+cost(defect): 92 spurious commits on 56 refs, 53 on closed PRs, each a notification
+and a ref a reader must tell from a real verdict; cleanup is by hand, per ref.
+P(recurrence): every restart of the loop without `HPO_STATE_DIR` repeats it.
+cost(countermeasure): one `ls-tree`/tree comparison per relayed probe and one printed
+line per pass. Passes.
+
+## Dropped condition
+
+An earlier design also required that the review commit be "committed after the
+probe". That condition had no historical case behind it and the self-test shows the
+guard works without it (a review commit dated after the probe is skipped too), so it
+was dropped.
+
+## Class
+
+No entry in `dev/audit/config/bugclasses.json` matches (the nearest, `N-log-flood`, is
+a log-volume class, not a replay); no `rca` field is cited or edited.
diff --git a/dev/governance/roles/fix-review.md b/dev/governance/roles/fix-review.md
index 0e272a7c0..9d4cc79ff 100644
--- a/dev/governance/roles/fix-review.md
+++ b/dev/governance/roles/fix-review.md
@@ -4,7 +4,7 @@ You review one fix PR adversarially, fresh, from a worktree at
 the PR's head SHA. You check that the numbers are real, not that the code looks right.
 **Its copy of this contract is frozen with the tree, so can be old**; start from the dispatch's `review-packet:`, whose check digest is as rendered: re-read live checks before a verdict.
 Before step 1: `git diff $(git merge-base origin/main HEAD)...origin/main -- dev/governance/roles/`; empty is current.
-Before the handoff freezes the branch (`fixer.md`), prepare against the merge base only: steps 2, 12 govern after. Publish with `tools/audit/seat/bus.sh push-verdict <pr> <verdict file> <evidence dir>` (a file there names the head) and report its output to be confirmed; a cloud seat, with no `push-verdict`, commits `cloud_relay.sh`'s verdict file and `ev/` in one commit, subject `verdict <pr> <head40>`, to a fresh repository and pushes `probe/rev-<pr>-<nonce first 8>`. First line: `Fix review: merge <head40>` or `Fix review: blocked <head40> <class>: <reason>`, class `[a-z-]+` (a script routes on it), then your brief's `bus-nonce: <nonce>`. It posts as `hpo-approver` (0013), never the author App (#1233) or the owner's review.
+Before the handoff freezes the branch (`fixer.md`), prepare against the merge base only: steps 2, 12 govern after. Publish with `tools/audit/seat/bus.sh push-verdict <pr> <verdict file> <evidence dir>` (a file there names the head) and report its output to be confirmed; a cloud seat, with no `push-verdict`, commits `cloud_relay.sh`'s verdict file and `ev/` in one commit, subject `verdict <pr> <head40>`, to a fresh repository and pushes `probe/rev-<pr>-<nonce first 8>`. Evidence names differ beyond case. First line: `Fix review: merge <head40>` or `Fix review: blocked <head40> <class>: <reason>`, class `[a-z-]+` (a script routes on it), then your brief's `bus-nonce: <nonce>`. It posts as `hpo-approver` (0013), never the author App (#1233) or the owner's review.
 Long jobs and CI waits follow `fixer.md`'s preamble; rotate context between rounds through refs, never mid-review, by ~150 k tokens.
 
 1. Re-run the mutation proof: delete the production line(s) the PR names,
diff --git a/dev/programme/delivery/3252.md b/dev/programme/delivery/3252.md
new file mode 100644
index 000000000..8c218d2cf
--- /dev/null
+++ b/dev/programme/delivery/3252.md
@@ -0,0 +1 @@
+- [#3252](https://github.com/tvofi/heatpump_optimizer/pull/3252) — **open**, R10-RELAY-SWEEP: the relay's residue on one seam, cloud_relay.sh (R10-RELAY-SWEEP)
diff --git a/tools/audit/seat/bus.sh b/tools/audit/seat/bus.sh
index 62e20564b..ceffa817b 100755
--- a/tools/audit/seat/bus.sh
+++ b/tools/audit/seat/bus.sh
@@ -261,6 +261,12 @@ carry_gate() { # verdict-file -> rc 0 when each finding item routes, else why, n
   return 1
 }
 
+# Names that differ only by case collide on a case-insensitive checkout (ancestors count: file
+# `a` against dir `A/x`). Prints "<one> and <other>" for the first pair, rc 0; rc 1 if none.
+case_collision() { # dir
+  (cd "$1" && find . -mindepth 1 | sed 's|^\./||' | LC_ALL=C sort | awk '{ n=split($0,p,"/"); q=""; for(i=1;i<=n;i++){ q=(i==1?p[i]:q "/" p[i]); k=tolower(q); if((k in s)&&s[k]!=q){print s[k] " and " q; f=1; exit} s[k]=q } } END { exit !f }')
+}
+
 push_verdict() { # pr verdict-file evidence-dir -> proposes the verdict on review/<pr>
   local pr=${1:-} v=${2:-} ev=${3:-} first hsha t gd tree why
   numeric "$pr" || die "push-verdict: the pull request '$pr' is not a number"
@@ -273,6 +279,7 @@ push_verdict() { # pr verdict-file evidence-dir -> proposes the verdict on revie
   [ -n "$ev" ] && [ -d "$ev" ] || die "push-verdict: no evidence directory (a verdict cites one; fix-review.md)"
   grep -rqF -- "$hsha" "$ev" \
     || die "push-verdict: no file under $ev names the head $hsha"
+  why=$(case_collision "$ev") && die "push-verdict: evidence names collide case-insensitively under $ev: $why; rename one"
   [ -z "$(find "$ev" -type f -size +50M 2>/dev/null)" ] \
     || die "push-verdict: a file under $ev is over 50 MB; cite it by path instead"
   # Verify the nonce against the dispatcher's record before proposing: a
@@ -362,7 +369,7 @@ kind_of() { # ref name -> "<kind> <name>"
 }
 
 unpack() { # family pr [want] -> sets c d first hsha in the caller; prints BUS refused, rc 1
-  local fam=$1 want=${3:-} why=""
+  local fam=$1 want=${3:-} why="" cc
   pr=$2
   numeric "$pr" || { printf 'BUS refused %s: %s/%s is not a pull-request number\n' "$pr" "$fam" "$pr"; return 1; }
   if ! git fetch -q "$REMOTE" "+refs/heads/$fam/$pr:refs/hpo-bus/$fam/$pr" 2>/dev/null; then
@@ -382,6 +389,7 @@ unpack() { # family pr [want] -> sets c d first hsha in the caller; prints BUS r
     elif ! grep -rqF -- "$hsha" "$d/evidence" 2>/dev/null; then why="no file under evidence/ names the head $hsha"
     fi
   fi
+  if [ -z "$why" ] && cc=$(case_collision "$d/evidence" 2>/dev/null); then why="evidence/ names collide case-insensitively: $cc"; fi
   [ -z "$why" ] || { printf 'BUS refused %s %s: %s\n' "$pr" "$c" "$why"; return 1; }
 }
 
@@ -1048,6 +1056,12 @@ P
   [ $rc != 0 ] && echo "$out" | grep -q "names the head $h1"; expect "push-verdict refuses evidence that names no head" $?
   out=$(seat push-verdict 7 "$W/merge0.md"); rc=$?
   [ $rc != 0 ] && echo "$out" | grep -q "no evidence directory"; expect "push-verdict refuses a verdict with no evidence directory" $?
+  mkdir -p "$W/evcc" "$W/evok" && echo "$h1" > "$W/evcc/HEAD.txt" && echo "$h1" > "$W/evcc/head.txt" \
+    && echo "$h1" > "$W/evok/HEAD.txt" && echo "$h1" > "$W/evok/other.txt"
+  out=$(seat push-verdict 7 "$W/merge0.md" "$W/evcc"); rc=$?
+  [ $rc != 0 ] && echo "$out" | grep -q "collide case-insensitively.*HEAD.txt and head.txt"; expect "push-verdict refuses evidence names that differ only by case, naming both" $?
+  out=$(seat push-verdict 7 "$W/merge0.md" "$W/evok"); rc=$?
+  ! echo "$out" | grep -q "collide case-insensitively"; expect "push-verdict lets distinct evidence names past the case check (null control)" $?
   out=$(seat push-verdict 7x "$W/merge0.md" "$W/ev1"); rc=$?
   [ $rc != 0 ] && echo "$out" | grep -q "not a number"; expect "push-verdict refuses a non-numeric pull request" $?
   git -C "$W/seat" ls-remote --exit-code origin 'refs/heads/review/*' >/dev/null 2>&1
@@ -1354,6 +1368,27 @@ B
   out=$(run watch --once --post)
   echo "$out" | grep -q "^BUS refused 10 $t: no file under evidence/ names the head" && [ "$(calls)" = 2 ]
   expect "watch refuses a raw proposal whose only naming file is VERDICT.md" $?
+  # The read side of the case check (unpack): a review/<pr> commit whose evidence/ holds HEAD.txt
+  # and head.txt is refused on read, not only on push-verdict; distinct names are the null control.
+  rawev() { # names... : VERDICT.md from stdin, evidence/<each name> naming $h1
+    local b e tr n ents=""
+    b=$(git -C "$W/seat" hash-object -w --stdin)
+    e=$(printf 'measured at %s\n' "$h1" | git -C "$W/seat" hash-object -w --stdin)
+    for n in "$@"; do ents="$ents$(printf '100644 blob %s\t%s\n' "$e" "$n")"$'\n'; done
+    e=$(printf '%s' "$ents" | git -C "$W/seat" mktree)
+    tr=$(printf '100644 blob %s\tVERDICT.md\n040000 tree %s\tevidence\n' "$b" "$e" | git -C "$W/seat" mktree)
+    git -C "$W/seat" commit-tree "$tr" -m x
+  }
+  t=$(printf 'Fix review: merge %s\n' "$h1" | rawev HEAD.txt head.txt)
+  git -C "$W/seat" push -q origin "$t:refs/heads/review/40"
+  out=$(run watch --once --post)
+  echo "$out" | grep -q "^BUS refused 40 $t: evidence/ names collide case-insensitively: .*HEAD.txt and head.txt"
+  expect "unpack refuses a proposal whose evidence names differ only by case, naming both (read side)" $?
+  t=$(printf 'Fix review: merge %s\n' "$h1" | rawev HEAD.txt other.txt)
+  git -C "$W/seat" push -q origin "$t:refs/heads/review/41"
+  out=$(run watch --once --post)
+  ! echo "$out" | grep -q "^BUS refused 41 .*collide case-insensitively" && echo "$out" | grep -q "^BUS undispatched 41 $t"
+  expect "unpack lets distinct evidence names past the case check (null control, read side)" $?
 
   N9=$(run dispatch 9 "$h1" cmsg_S | sed -n 's/^bus-nonce: //p')
   printf 'Fix review: merge %s\n\nbus-nonce: %s\n' "$h1" "$N9" > "$W/merge9.md"
diff --git a/tools/audit/seat/cloud_relay.sh b/tools/audit/seat/cloud_relay.sh
index 0df114bbd..a29ffba6f 100644
--- a/tools/audit/seat/cloud_relay.sh
+++ b/tools/audit/seat/cloud_relay.sh
@@ -99,7 +99,9 @@
 #     A handoff already contained in its PR, or with no body ref, does nothing;
 #     a topic whose update failed is noted in `<ledger>.handoff-failed` by
 #     `<topic> <code-sha>` and retried only when handoff/<topic> moves, owed
-#     meanwhile as `OWED <utc> handoff-update <ref> <sha>` in <log>.level. The
+#     meanwhile as `OWED <utc> handoff-update <ref> <sha> <why>` in <log>.level, <why>
+#     kept in `<ledger>.handoff-failed.why`; a body whose `Code:` trailer names
+#     another head is `handoff-body-stale` (retried). The
 #     `handoff-no-pr` lines there are `ledger.py level`'s fold of every
 #     handoff/* and handoff-body/* ref: owed unless its topic has an open PR,
 #     it is disposed at its sha, or main already carries the change (`ledger.py
@@ -128,8 +130,15 @@
 #     <log>.level; `<state>/cloud-handoff-release` (the hold grammar, the
 #     orchestrator's) releases a listed PR from the freeze, never from the
 #     hold. review_freeze below says why each case is what it is.
+#     HELD-BODY: `cloud_relay: HELD-BODY #<pr> <tip8>`: the handoff is ahead of a
+#     body that does not name its first 8 chars; retried next pass. Levels
+#     `handoff-body-unapplied` (BODY-ONLY line) and `handoff-hold-stale` (hold line
+#     whose PR is not open) are published before the serial loops.
 #   probe arm: the --watch pass above (probe/rev-* -> relay -> confirm; other
 #     probe refs OWED until disposed).
+#   relay() refuses (rc 2, naming both) ev/ names differing only in case, and
+#     pushes nothing when review/<pr> already carries the probe's tree (delivered
+#     guard: recorded). Each pass prints `state dir <dir>, ledger ..., log ...`.
 #   stuck and no-return arms: level lines only (THE STUCK ANDON, THE NO-RETURN LINE below).
 #   confirm arm (--confirm): the ledger is written before confirm runs, so a
 #     confirm that failed, a relay by a script without the confirm, or one by a
@@ -228,8 +237,27 @@ relay() {
   else die "the first line is not 'Fix review: merge $head' or 'Fix review: blocked $head <class>: <reason>': '$first'"; return; fi
   grep -qx "bus-nonce: $nonce" "$d/verdict.md" || { die "nonce mismatch: no 'bus-nonce: $nonce' line"; return; }
   [ -d "$d/ev" ] || { die "no ev/ directory in the ref"; return; }
+  # Names under ev/ that differ only in case: a case-insensitive filesystem (the orchestrator's
+  # macOS) unpacks one over the other, and push-verdict then refuses "no file names the head" --
+  # a cause that reads as a missing file (PR 3061). Refused here by name, on the first tick line.
+  # Every ancestor path is compared too, so a file ev/A and a directory ev/a collide as well.
+  local dup; dup=$(git -c core.quotepath=off ls-tree -r --name-only "$sha" -- ev | awk '{
+    n = split($0, p, "/"); q = ""
+    for (i = 1; i <= n; i++) { q = (i == 1 ? p[i] : q "/" p[i]); k = tolower(q)
+      if ((k in s) && s[k] != q) { print s[k] " and " q; exit } s[k] = q } }')
+  [ -z "$dup" ] || { die "ev/ holds names that differ only in case ($dup); a case-insensitive checkout keeps one, so rename them apart"; return; }
   local out sha2 wt tip tries=0
   wt=$(verdict_tree "$d/verdict.md" "$d/ev") || { echo "cloud_relay: could not build the verdict's tree" >&2; return 1; }
+  # DELIVERED GUARD (R10-RELAY-REPLAY): a ledger that is not the one that recorded this probe (a
+  # loop restarted without HPO_STATE_DIR read the stale default) made every probe look unseen, and
+  # 93 were replayed as 92 commits on 56 review refs. Whether review/<pr> already carries this
+  # verdict's tree is asked of the remote, so correctness does not depend on which ledger is read.
+  # The tree list goes to a file: a pipe into an early-exiting reader breaks under pipefail.
+  if tip=$(review_tip "$pr") && [ -n "$tip" ] && git log --format=%T "$tip" > "$d/rtrees" 2>/dev/null && grep -qxF "$wt" "$d/rtrees"; then
+    mkdir -p "$state" && echo "$ref $sha" >> "$led"
+    echo "cloud_relay: review/$pr already carries this verdict's tree (tip ${tip:0:12}); $ref $sha recorded as relayed, nothing pushed"
+    return 0
+  fi
   # A push refused non-fast-forward (review/<pr> moved since push-verdict read its tip) is
   # re-applied: push-verdict reads the fresh tip again and appends the same verdict there,
   # never forcing. A fresh tip that already carries this verdict's tree is not re-applied.
@@ -276,7 +304,9 @@ probe_arm() { # one pass over every probe/* ref: rev-* relays each unseen ref+sh
   led=$state/cloud-relayed; bus=${HPO_BUS_STATE:-$HOME/.zcode/bus}
   # a failed listing leaves the level as it was: unknown is not "nothing owed"
   git ls-remote origin 'refs/heads/probe/*' > "${TMPDIR:-/tmp}/cloud_relay_ls.$$" || { echo "cloud_relay: ls-remote failed; will retry" >&2; rm -f "${TMPDIR:-/tmp}/cloud_relay_ls.$$"; return 0; }
-  mkdir -p "$state"; : > "$state/cloud-level-probe.$$"; : > "$state/cloud-level-refused.$$"
+  mkdir -p "$state"; : > "$state/cloud-level-probe.$$"; : > "$state/cloud-level-refused.$$"; : > "$state/cloud-torelay.$$"
+  # The levels are published before the serial relay loop, which is slow (a fetch and a push per ref):
+  # written only at its end they were missing for a whole pass (2026-10-22, R10-RELAY-SWEEP carry 2).
   while read -r sha ref; do
     [ -n "$ref" ] || continue
     case $ref in refs/heads/probe/rev-*) ;;
@@ -288,6 +318,12 @@ probe_arm() { # one pass over every probe/* ref: rev-* relays each unseen ref+sh
       [ -z "$why" ] || disposed "$ref" "$sha" || level_line probe-refused "$ref" "$sha" "$why" >> "$state/cloud-level-refused.$$"
       continue
     fi
+    echo "$sha $ref" >> "$state/cloud-torelay.$$"
+  done < "${TMPDIR:-/tmp}/cloud_relay_ls.$$"
+  cp "$state/cloud-level-probe.$$" "$state/cloud-level-probe.$$.k"; cp "$state/cloud-level-refused.$$" "$state/cloud-level-refused.$$.k"
+  level_set probe-ref "$state/cloud-level-probe.$$.k"; level_set probe-refused "$state/cloud-level-refused.$$.k"
+  while read -r sha ref; do
+    [ -n "$ref" ] || continue
     k=${ref#refs/heads/probe/rev-}; pr=${k%%-*}; n8=${k#*-}
     rec=$(awk -v p="$pr" -v n="$n8" '$1 == p && index($4, n) == 1 { print $2, $4 }' "$bus/dispatched" 2>/dev/null | tail -n 1)
     if [ -z "$rec" ]; then echo "$(date -u +%FT%TZ) cloud_relay: $ref $sha has no dispatch record in $bus; leaving it" >&2; continue; fi
@@ -303,8 +339,8 @@ probe_arm() { # one pass over every probe/* ref: rev-* relays each unseen ref+sh
       echo "$ref $sha" >> "$led.refused"; echo "$ref $sha $why" >> "$led.refused-why"
       level_line probe-refused "$ref" "$sha" "$why" >> "$state/cloud-level-refused.$$"; echo "cloud_relay: REFUSED $ref $sha $why"
     else echo "cloud_relay: relay of $ref $sha failed (rc=$rc, try $n of $max); the next pass retries: $why" >&2; fi
-  done < "${TMPDIR:-/tmp}/cloud_relay_ls.$$"
-  rm -f "${TMPDIR:-/tmp}/cloud_relay_ls.$$" "$state/cloud-relay-err.$$"
+  done < "$state/cloud-torelay.$$"
+  rm -f "${TMPDIR:-/tmp}/cloud_relay_ls.$$" "$state/cloud-relay-err.$$" "$state/cloud-torelay.$$"
   level_set probe-ref "$state/cloud-level-probe.$$"; level_set probe-refused "$state/cloud-level-refused.$$"
 }
 
@@ -432,6 +468,30 @@ tools_level() { # <state>: prints the levelled tree's seat directory, or why not
     || { rm -rf "$tw.lock"; echo "the relay's tools tree $tw could not check out origin/main"; return 2; }  # mut:toolslevel
   echo "$tw/tools/audit/seat"
 }
+body_only_owed() { # <pr> <topic> <body sha> <head> <why>: a body-only handoff left unapplied is owed while its body tip is newer than the head's commit
+  local bt ht; git fetch -q origin "refs/heads/handoff-body/$2" 2>/dev/null
+  bt=$(git log -1 --format=%ct "$3" 2>/dev/null) && ht=$(git log -1 --format=%ct "$4" 2>/dev/null) && [ "$bt" -gt "$ht" ] || return 1
+  echo "cloud_relay: BODY-ONLY #$1 handoff-body/$2 ${3:0:12} is newer than head ${4:0:12} and not applied: $5"
+  level_line handoff-body-unapplied "refs/heads/handoff-body/$2" "$3" "#$1 $5" >> "$state/cloud-level-bodyonly.$$"
+}
+handoff_level() { # the handoff-no-pr and hold-stale levels, derived from this pass's listings (called before the serial update loop)
+  local state=${HPO_STATE_DIR:-$HOME/.local/state/hpo} repo=${HPO_RELAY_REPO:-tvofi/heatpump_optimizer} l
+  # a hold-file line whose PR is no longer open (merged or closed) is stale: it holds nothing and is never expired
+  : > "$state/cloud-level-holdstale.$$"
+  for l in $held_prs; do
+    grep -qxF "$l" <<< "$(cut -f1 "$state/cloud-prs.$$")" || level_line handoff-hold-stale "$(hold_file)" "#$l" "PR #$l is not open; remove the line" >> "$state/cloud-level-holdstale.$$"
+  done
+  level_set handoff-hold-stale "$state/cloud-level-holdstale.$$"
+  cut -f2 "$state/cloud-prs.$$" | sed -e 's,^fix/,,' -e 's,-pr$,,' > "$state/cloud-topics.$$"
+  { if [ -n "${HPO_RELAY_MERGED:-}" ]; then "$HPO_RELAY_MERGED"
+    else gh pr list -R "$repo" --state merged --limit 200 --json headRefName,mergedAt \
+      -q '.[] | [.headRefName, .mergedAt] | @tsv'; fi; } > "$state/cloud-merged.$$" \
+    || { echo "cloud_relay: could not list merged PRs; the handoff level stays as it was" >&2; return 0; }
+  awk -F'\t' 'NF == 2 { t = $1; sub(/^fix\//, "", t); sub(/-pr$/, "", t); print t " merged=" $2 }' "$state/cloud-merged.$$" >> "$state/cloud-topics.$$"
+  ledger level "$state/cloud-hrefs.$$" "$state/cloud-topics.$$" > "$state/cloud-level-handoff.$$"
+  case $? in 0|1) level_set handoff-no-pr "$state/cloud-level-handoff.$$";;
+    *) echo "cloud_relay: the ledger could not derive the handoff level; it stays as it was" >&2; rm -f "$state/cloud-level-handoff.$$";; esac
+}
 handoff_arm() { # one pass over open PRs; updates one whose handoff is ahead of its head
   local state=${HPO_STATE_DIR:-$HOME/.local/state/hpo} repo=${HPO_RELAY_REPO:-tvofi/heatpump_optimizer} f pr br head topic hs bs bd body iss nh nonce urc held_prs released upd why code
   local bf bonly key seed=""
@@ -454,7 +514,8 @@ handoff_arm() { # one pass over open PRs; updates one whose handoff is ahead of
   # one listing of the verdicts per pass, outside the loop: an unread listing would update a merge-verdicted head
   git ls-remote origin 'refs/heads/verdict/*' > "$state/cloud-vrefs.$$" \
     || { echo "cloud_relay: could not list verdict refs; will retry" >&2; rm -f "$state/cloud-prs.$$" "$state/cloud-hrefs.$$" "$state/cloud-vrefs.$$"; return 0; }
-  : > "$state/cloud-level-update.$$"; : > "$state/cloud-level-held.$$"; : > "$state/cloud-level-stale.$$"
+  : > "$state/cloud-level-update.$$"; : > "$state/cloud-level-held.$$"; : > "$state/cloud-level-stale.$$"; : > "$state/cloud-level-bodyonly.$$"
+  handoff_level
   while IFS=$'\t' read -r pr br head; do
     [ -n "$pr" ] || continue
     topic=${br#fix/}; topic=${topic%-pr}
@@ -469,7 +530,7 @@ handoff_arm() { # one pass over open PRs; updates one whose handoff is ahead of
       grep -qxF "$topic $bs" "$bf" && continue
       [ -z "$seed" ] || { echo "$topic $bs" >> "$bf"; continue; }
       bonly=1; fi
-    if grep -qxF "$pr" <<< "$held_prs"; then echo "cloud_relay: HELD #$pr $hs"; continue; fi
+    if grep -qxF "$pr" <<< "$held_prs"; then echo "cloud_relay: HELD #$pr $hs"; [ -z "$bonly" ] || body_only_owed "$pr" "$topic" "$bs" "$head" "held by the hold file" || :; continue; fi
     # a body-only move leaves the head under review where it is, so no review freezes it
     if [ -z "$bonly" ] && ! grep -qxF "$pr" <<< "$released" && why=$(review_freeze "$pr" "$head" "$state/cloud-vrefs.$$"); then
       echo "cloud_relay: HELD-${why%% *} #$pr $hs${why#"${why%% *}"} (head $head under review; merge it, or list #$pr in $(release_file) and re-dispatch)"
@@ -498,7 +559,16 @@ handoff_arm() { # one pass over open PRs; updates one whose handoff is ahead of
     fi
     # A body-only move is made with the body pushed for this head: one with no `Code:` line, which
     # predates the trailer, is recorded as applied and left alone, as before this arm existed.
-    if [ -n "$bonly" ] && [ -z "$code" ]; then echo "$topic $bs" >> "$bf"; rm -rf "$bd"; continue; fi
+    if [ -n "$bonly" ] && [ -z "$code" ]; then
+      # owed (and not recorded) while the body is newer than the head: its return must not be skipped in silence (P288)
+      body_only_owed "$pr" "$topic" "$bs" "$head" "its body carries no Code: trailer" || echo "$topic $bs" >> "$bf"
+      rm -rf "$bd"; continue; fi
+    # HELD-BODY: a code push precedes its body push, so a handoff ahead of its own body is partial work.
+    # The body must name the tip (its first 8 characters), else the update waits for the next pass.
+    if [ -z "$bonly" ] && ! grep -qF "${hs:0:8}" "$body"; then
+      echo "cloud_relay: HELD-BODY #$pr ${hs:0:8}"
+      level_line handoff-held "refs/heads/handoff/$topic" "$hs" "#$pr BODY" >> "$state/cloud-level-held.$$"; rm -rf "$bd"; continue
+    fi
     iss=$(grep -oiE '\b(close[sd]?|fix(e[sd])?|resolve[sd]?)[: ]+#[0-9]+' "$body" | grep -oE '[0-9]+' | sort -un | tr '\n' ' ')
     if [ -n "$bonly" ]; then echo "$(date -u +%FT%TZ) cloud_relay: handoff-body/$topic $bs is new for #$pr $head; body-only"
     else echo "$(date -u +%FT%TZ) cloud_relay: handoff/$topic $hs is ahead of #$pr $head; updating"; fi
@@ -548,19 +618,7 @@ handoff_arm() { # one pass over open PRs; updates one whose handoff is ahead of
   level_set handoff-update "$state/cloud-level-update.$$"
   level_set handoff-held "$state/cloud-level-held.$$"
   level_set handoff-body-stale "$state/cloud-level-stale.$$"
-  # a handoff or handoff-body ref whose topic has no open PR is OWED on every pass until disposed
-  cut -f2 "$state/cloud-prs.$$" | sed -e 's,^fix/,,' -e 's,-pr$,,' > "$state/cloud-topics.$$"
-  # and the merged ones, `<topic> merged=<utc>`: a merge closes a handoff committed by then (RCA section 5.1)
-  { if [ -n "${HPO_RELAY_MERGED:-}" ]; then "$HPO_RELAY_MERGED"
-    else gh pr list -R "$repo" --state merged --limit 200 --json headRefName,mergedAt \
-      -q '.[] | [.headRefName, .mergedAt] | @tsv'; fi; } > "$state/cloud-merged.$$" \
-    || { echo "cloud_relay: could not list merged PRs; the handoff level stays as it was" >&2
-         rm -f "$state/cloud-prs.$$" "$state/cloud-hrefs.$$" "$state/cloud-topics.$$" "$state/cloud-vrefs.$$" "$state/cloud-merged.$$"; return 0; }
-  awk -F'\t' 'NF == 2 { t = $1; sub(/^fix\//, "", t); sub(/-pr$/, "", t); print t " merged=" $2 }' "$state/cloud-merged.$$" >> "$state/cloud-topics.$$"
-  # The level is ledger.py's fold (rc 0 none owed, 1 owed, 2 unreadable: the level stays as it was).
-  ledger level "$state/cloud-hrefs.$$" "$state/cloud-topics.$$" > "$state/cloud-level-handoff.$$"
-  case $? in 0|1) level_set handoff-no-pr "$state/cloud-level-handoff.$$";;
-    *) echo "cloud_relay: the ledger could not derive the handoff level; it stays as it was" >&2; rm -f "$state/cloud-level-handoff.$$";; esac
+  level_set handoff-body-unapplied "$state/cloud-level-bodyonly.$$"
   rm -f "$state/cloud-prs.$$" "$state/cloud-hrefs.$$" "$state/cloud-topics.$$" "$state/cloud-vrefs.$$" "$state/cloud-merged.$$"
 }
 
@@ -650,7 +708,9 @@ pass() { # [--confirm] [--log FILE] [--loop [--interval N]]
     --confirm) CONFIRM=1; shift;; --log) LOG=${2:-}; shift 2;; --loop) loop=1; shift;; --interval) every=${2:-}; shift 2;;
     *) echo "cloud_relay: unknown pass option '$1'" >&2; return 2;; esac; done
   case $every in ''|*[!0-9]*|0) echo "cloud_relay: --interval must be a positive number of seconds" >&2; return 2;; esac
-  while :; do handoff_arm; probe_arm; [ -z "${CONFIRM:-}" ] || confirm_arm; stuck_arm; noreturn_arm; [ -z "$loop" ] && return 0; sleep "$every"; done
+  while :; do
+    echo "cloud_relay: state dir ${HPO_STATE_DIR:-$HOME/.local/state/hpo}, ledger ${HPO_STATE_DIR:-$HOME/.local/state/hpo}/cloud-relayed, log $(relay_log)"
+    handoff_arm; probe_arm; [ -z "${CONFIRM:-}" ] || confirm_arm; stuck_arm; noreturn_arm; [ -z "$loop" ] && return 0; sleep "$every"; done
 }
 
 self_test() {
@@ -797,6 +857,45 @@ EOF
   chk "without --confirm, relay logs nothing" 0 relay 7 $n $h
   chk "and the log stayed empty" 0 test ! -s "$LOG"
   chk "but the ledger owes its posting: a relayed verdict is owed until it is read back" 0 owes "verdict-unposted 7 $h "
+  # DELIVERED GUARD (carry 6) and case-colliding ev/ names (carry 8)
+  mkf() { # mkf <pr> <content> <ev file>...: a probe ref whose ev/ holds those files, all with that content
+    local f p=$1 body=$2; shift 2
+    rm -rf "$t/pr"; throwaway_git_init "$t/pr" -q
+    for f in "$@"; do mkdir -p "$t/pr/$(dirname "$f")"; echo "$body" > "$t/pr/$f"; done
+    printf 'Fix review: merge %s\n\nbus-nonce: %s\n' "$h" "$n" > "$t/pr/verdict.md"
+    git -C "$t/pr" add -A; git -C "$t/pr" commit -qm "verdict $p $h"
+    git -C "$t/o.git" fetch -qf "$t/pr" "HEAD:refs/heads/probe/rev-$p-${n:0:8}"; }
+  pushes() { [ -f "$t/pushed" ] && wc -l < "$t/pushed" | tr -d ' ' || echo 0; }
+  rm -f "$t/pushed" "$t/state/cloud-relayed"; HPO_RELAY_PUSH=$stub
+  mkf 31 first ev/e; out=$(relay 31 $n $h 2>&1); chk "a new tree is pushed (stub called)" 0 test "$(pushes)" = 1
+  : > "$t/state/cloud-relayed"; mkf 31 first ev/e; P31=$(git -C "$t/o.git" rev-parse refs/heads/probe/rev-31-${n:0:8})
+  out=$(relay 31 $n $h 2>&1); rc=$?
+  chk "a tree review/31 already carries relays rc 0 with an emptied ledger" 0 test "$rc" = 0
+  chk "and does not call the push stub again" 0 test "$(pushes)" = 1
+  chk "and records ref sha in the ledger" 0 grep -qxF "refs/heads/probe/rev-31-${n:0:8} $P31" "$t/state/cloud-relayed"
+  chk "and says 'already carries'" 0 grep -q "already carries" <<< "$out"
+  mkf 31 second ev/e; out=$(relay 31 $n $h 2>&1); rc=$?
+  chk "a different tree (different ev content) is pushed (null control)" 0 test "$rc $(pushes)" = "0 2"
+  chk "and does not say 'already carries'" 1 grep -q "already carries" <<< "$out"
+  for v in one two three four five; do mkf 32 $v ev/e; relay 32 $n $h >/dev/null 2>&1; done
+  : > "$t/state/cloud-relayed"; before=$(pushes); mkf 32 one ev/e; out=$(relay 32 $n $h 2>&1); rc=$?
+  chk "the oldest of many review commits is still found (pipefail-safe): skipped" 0 test "$rc $(pushes)" = "0 $before"
+  chk "and says so" 0 grep -q "already carries" <<< "$out"
+  : > "$t/state/cloud-relayed"; before=$(pushes); GIT_COMMITTER_DATE="@4000000000 +0000" mkf 32 three ev/e; out=$(relay 32 $n $h 2>&1)
+  chk "the guard does not depend on the review commit being newer than the probe" 0 test "$(pushes)" = "$before"
+  PS=$t/state/pass.log; out=$( (handoff_arm() { :; }; probe_arm() { :; }; stuck_arm() { :; }; noreturn_arm() { :; }; CONFIRM= LOG=$PS; pass) 2>&1 )
+  chk "a pass prints its state dir, ledger and log once" 0 test "$(grep -cxF "cloud_relay: state dir $t/state, ledger $t/state/cloud-relayed, log $PS" <<< "$out")" = 1
+  out=$( (handoff_arm() { :; }; probe_arm() { :; }; stuck_arm() { :; }; noreturn_arm() { :; }; CONFIRM= LOG=$PS; pass; pass) 2>&1 )
+  chk "and once per pass (two passes, two lines)" 0 test "$(grep -c '^cloud_relay: state dir ' <<< "$out")" = 2
+  # ev/ names differing only in case (carry 8): refused by name, nothing pushed
+  rm -f "$t/pushed"
+  mkf 41 x ev/HEAD.txt ev/head.txt; out=$(relay 41 $n $h 2>&1); rc=$?
+  chk "ev/HEAD.txt and ev/head.txt are refused rc 2" 0 test "$rc" = 2
+  chk "naming both files" 0 grep -Eq "HEAD.txt and ev/head.txt|head.txt and ev/HEAD.txt" <<< "$out"
+  chk "with nothing pushed" 0 test ! -s "$t/pushed"
+  mkf 41 x ev/A ev/a/x; out=$(relay 41 $n $h 2>&1); rc=$?
+  chk "a file ev/A and a directory ev/a/x are refused rc 2" 0 test "$rc $(pushes)" = "2 0"
+  mkf 41 x ev/head.txt ev/other.txt; chk "distinct names relay (null control)" 0 relay 41 $n $h
   # the watch pass
   HPO_RELAY_PUSH=$stub; rm -f "$t/pushed" "$t/state/cloud-relayed" "$t/state/cloud-relayed.refused"
   export HPO_BUS_STATE=$t/bus; mkdir -p "$t/bus"
@@ -874,7 +973,7 @@ EOF
   unset HPO_RELAY_PUSH; export HPO_RELAY_PUSH=$stub; LOG=$t/pass.log; : > "$LOG"; CONFIRM=
   prs=$t/prs.tsv; ustub=$t/ustub.sh; dstub=$t/dstub.sh; astub=$t/astub.sh; N40=aaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaa
   hc() { git -C "$t/pr" -c user.name=t -c user.email=t@t commit -q --allow-empty -m "$1"; }
-  mkref() { git -C "$t/o.git" fetch -qf "$t/pr" "HEAD:refs/heads/$1"; }
+  mkref() { git -C "$t/o.git" fetch -qf "$t/pr" "HEAD:refs/heads/$1"; [ "$1" = handoff/topic-a ] && [ -f "$t/b/BODY.md" ] && mkref2; return 0; }
   rm -rf "$t/m"; throwaway_git_init "$t/m" -q; git -C "$t/m" -c user.name=t -c user.email=t@t commit -q --allow-empty -m main
   git -C "$t/o.git" fetch -qf "$t/m" "HEAD:refs/heads/main"
   rm -rf "$t/pr"; throwaway_git_init "$t/pr" -q; hc base; mkref fix/topic-a-pr; PRH=$(git -C "$t/pr" rev-parse HEAD)
@@ -892,7 +991,10 @@ EOF
   chk "a handoff with no body ref does nothing" 0 test ! -e "$t/updated"
   # a handoff ahead of its PR fires the arm
   rm -rf "$t/b"; throwaway_git_init "$t/b" -q; printf 'Part of #201\n\nCloses #77 and fixes #78.\n' > "$t/b/BODY.md"
-  git -C "$t/b" add BODY.md; git -C "$t/b" -c user.name=t -c user.email=t@t commit -qm body; mkref2() { git -C "$t/o.git" fetch -qf "$t/b" "HEAD:refs/heads/handoff-body/topic-a"; }; mkref2
+  git -C "$t/b" add BODY.md; git -C "$t/b" -c user.name=t -c user.email=t@t commit -qm body; mkref2() { # the body names the handoff tip it is pushed against (HELD-BODY otherwise)
+    { grep -v '^Code head: ' "$t/b/BODY.md"; echo "Code head: $(git -C "$t/o.git" rev-parse refs/heads/handoff/topic-a)"; } > "$t/b/BODY.new"; mv "$t/b/BODY.new" "$t/b/BODY.md"
+    git -C "$t/b" diff --quiet || git -C "$t/b" -c user.name=t -c user.email=t@t commit -qa --amend --no-edit
+    git -C "$t/o.git" fetch -qf "$t/b" "HEAD:refs/heads/handoff-body/topic-a"; }; mkref2
   handoff_arm >/dev/null 2>&1
   chk "a handoff ahead of its PR runs update_pr with branch and code sha" 0 grep -q "^fix/topic-a-pr $HS " "$t/updated"
   chk "the issues come from the body's closing keywords" 0 grep -q " 77 78 *$" "$t/updated"
@@ -1150,7 +1252,7 @@ EOF
   chk "and runs no update and owes handoff-held" 0 test "$([ -e "$t/hupdated" ] && echo ran)-$(grep -c "handoff-held refs/heads/handoff/topic-a $HS3 #41 VERDICT\$" "$LOG.level")" = -1
   git -C "$t/o.git" update-ref refs/heads/handoff/topic-a "$HS2"; git -C "$t/o.git" update-ref -d refs/heads/verdict/41
   git -C "$t/pr" reset -q --hard "$PRH"; mv "$t/bus/dispatched.bo" "$t/bus/dispatched"; rm -f "$t/hupdated"
-  rm -f "$t/hupdated"; bodyc; handoff_arm >/dev/null 2>&1
+  rm -f "$t/hupdated"; GIT_COMMITTER_DATE="@1000000000 +0000" bodyc; handoff_arm >/dev/null 2>&1  # a body not newer than the head's commit
   chk "a contained body with no Code: line runs nothing, and is recorded applied" 0 test ! -e "$t/hupdated" -a "$(tail -n 1 "$BF")" = "topic-a $(bsha)"
   bodyc "$HS"; ho=$(handoff_arm 2>&1)
   chk "a contained body naming another code head runs nothing and is owed stale" 0 test ! -e "$t/hupdated" -a "$(grep -c "handoff-body-stale refs/heads/handoff/topic-a $HS2 body names ${HS:0:12}\$" "$LOG.level")" = 1
@@ -1208,6 +1310,71 @@ EOF
   mv "$t/dispositions.tsv" "$t/disp.bak"; mkdir "$t/dispositions.tsv"; handoff_arm >/dev/null 2>&1
   chk "an unreadable ledger leaves the handoff level as it was (rc 2 is not 'nothing owed')" 0 grep -q "handoff-no-pr refs/heads/handoff/topic-b $OB2 ct=" "$LV"
   rmdir "$t/dispositions.tsv"; mv "$t/disp.bak" "$t/dispositions.tsv"
+  # HELD-BODY, BODY-ONLY, a stale hold line, and the levels published before a slow update or relay.
+  # topic-h: head A (PR 51); handoff tip B ahead of it, then C (the head, holding B). Dates are fixed.
+  hx=$t/hx; hbd=$t/hbd; hprs=$t/hprs.sh; hslow=$t/hslow.sh; hid=(-c user.name=t -c user.email=t@t)
+  hxc() { GIT_COMMITTER_DATE="@$2 +0000" git -C "$hx" "${hid[@]}" commit -q --allow-empty -m "$1"; git -C "$hx" rev-parse HEAD; }  # never-empty: hid is assigned three words on line 1315
+  hbc() { GIT_COMMITTER_DATE="@$1 +0000" git -C "$hbd" "${hid[@]}" commit -q --allow-empty -m "body $1 ${2-}" ${2:+-m "Code: $2"}  # never-empty: hid is assigned three words on line 1315
+    git -C "$t/o.git" fetch -qf "$hbd" HEAD:refs/heads/handoff-body/topic-h; }
+  hlv() { grep -c "$1" "$LV"; }
+  rm -rf "$hx" "$hbd"; throwaway_git_init "$hx" -q; throwaway_git_init "$hbd" -q
+  HA=$(hxc a 1700000000); git -C "$t/o.git" fetch -qf "$hx" HEAD:refs/heads/fix/topic-h-pr
+  HB=$(hxc b 1700000100); git -C "$t/o.git" fetch -qf "$hx" HEAD:refs/heads/handoff/topic-h
+  printf '#!/bin/sh\nprintf "51\\tfix/topic-h-pr\\t%%s\\n" "$HX_HEAD"\n' > "$hprs"; chmod +x "$hprs"; export HX_HEAD=$HA
+  printf 'Code head: %s\n' "${HA:0:8}" > "$hbd/BODY.md"; git -C "$hbd" add BODY.md; hbc 1700000150 >/dev/null
+  rm -f "$t/hupdated" "$t/state/cloud-handoff-failed" "$t/state/cloud-handoff-failed.why" "$hf"; : > "$LOG"; rm -f "$LV"; HPO_RELAY_UPDATE=$hu
+  ho=$(HPO_RELAY_PRS=$hprs handoff_arm 2>&1)
+  chk "a handoff ahead of its PR whose body names the old tip prints HELD-BODY once per pass" 0 test "$(grep -c "^cloud_relay: HELD-BODY #51 ${HB:0:8}\$" <<< "$ho")" = 1
+  chk "and runs no update and owes one handoff-held line with why BODY" 0 test "$([ -e "$t/hupdated" ] && echo ran)-$(hlv "handoff-held refs/heads/handoff/topic-h $HB #51 BODY\$")" = -1
+  printf 'Code head: %s\n' "${HB:0:8}" > "$hbd/BODY.md"; git -C "$hbd" add BODY.md; hbc 1700000160 >/dev/null
+  ho=$(HPO_RELAY_PRS=$hprs handoff_arm 2>&1)
+  chk "once the body names the new tip the update runs (null control)" 0 grep -q "^fix/topic-h-pr $HB\$" "$t/hupdated"
+  chk "and prints no HELD-BODY and owes no handoff-held (null control)" 0 test "$(grep -c HELD-BODY <<< "$ho")-$(hlv handoff-held)" = 0-0
+  # carry 3: the head holds the handoff tip (C is B's child) and a body with no Code: line is newer than it
+  HC=$(hxc c 1700000200); git -C "$t/o.git" fetch -qf "$hx" HEAD:refs/heads/fix/topic-h-pr; export HX_HEAD=$HC
+  rm -f "$t/hupdated"; hbc 1700000300 >/dev/null
+  ho=$(HPO_RELAY_PRS=$hprs handoff_arm 2>&1); HPO_RELAY_PRS=$hprs handoff_arm >/dev/null 2>&1
+  chk "a body-only handoff with a body newer than the head prints BODY-ONLY once per pass" 0 test "$(grep -c "^cloud_relay: BODY-ONLY #51 " <<< "$ho")" = 1
+  chk "runs nothing and owes exactly one handoff-body-unapplied line after two passes" 0 test "$([ -e "$t/hupdated" ] && echo ran)-$(hlv "handoff-body-unapplied refs/heads/handoff-body/topic-h ")" = -1
+  hbc 1700000150 >/dev/null; ho=$(HPO_RELAY_PRS=$hprs handoff_arm 2>&1)
+  chk "null control: a body committed before the head's commit prints no BODY-ONLY" 1 grep -q BODY-ONLY <<< "$ho"
+  chk "and owes no handoff-body-unapplied" 0 test "$(hlv handoff-body-unapplied)" = 0
+  printf '51\n' > "$hf"; hbc 1700000310 >/dev/null; ho=$(HPO_RELAY_PRS=$hprs handoff_arm 2>&1)
+  chk "held by the hold file, a newer body-only body prints HELD and BODY-ONLY once each" 0 test "$(grep -c "^cloud_relay: HELD #51 " <<< "$ho")-$(grep -c "^cloud_relay: BODY-ONLY #51 .*held by the hold file" <<< "$ho")" = 1-1
+  chk "and owes one handoff-body-unapplied line" 0 test "$(hlv "handoff-body-unapplied .*#51 held by the hold file")" = 1
+  hbc 1700000150 >/dev/null; ho=$(HPO_RELAY_PRS=$hprs handoff_arm 2>&1)
+  chk "null control: held, with a body older than the head, prints no BODY-ONLY and owes nothing" 0 test "$(grep -c BODY-ONLY <<< "$ho")-$(hlv handoff-body-unapplied)" = 0-0
+  # a hold-file line for a PR that is not open is stale; one for an open PR is not
+  printf '51\n99\n' > "$hf"; HPO_RELAY_PRS=$hprs handoff_arm >/dev/null 2>&1
+  chk "a hold line for a PR not among the open PRs owes handoff-hold-stale" 0 test "$(hlv "handoff-hold-stale [^ ]* #99 ")" = 1
+  chk "a hold line for an open PR does not (null control)" 0 test "$(hlv "handoff-hold-stale [^ ]* #51 ")" = 0
+  rm -f "$hf"; HPO_RELAY_PRS=$hprs handoff_arm >/dev/null 2>&1
+  chk "and the stale line is gone with the hold line" 0 test "$(hlv handoff-hold-stale)" = 0
+  # carry 2: the levels are published before the slow serial loop. The update stub blocks until released.
+  git -C "$t/o.git" update-ref refs/heads/handoff/topic-h "$HB"; git -C "$t/o.git" update-ref refs/heads/handoff/topic-o "$HB"
+  export HX_HEAD=$HA; git -C "$t/o.git" update-ref refs/heads/fix/topic-h-pr "$HA"
+  printf 'Code head: %s\n' "${HB:0:8}" > "$hbd/BODY.md"; git -C "$hbd" add BODY.md; hbc 1700000320 >/dev/null
+  printf '#!/bin/sh\necho "$1" > "%s/slow.started"\nwhile [ ! -e "%s/slow.go" ]; do sleep 0.1; done\n' "$t" "$t" > "$hslow"; chmod +x "$hslow"
+  rm -f "$t/slow.started" "$t/slow.go" "$LV"; HPO_RELAY_UPDATE=$hslow HPO_RELAY_PRS=$hprs handoff_arm >/dev/null 2>&1 & hp=$!
+  for _ in $(seq 100); do [ -e "$t/slow.started" ] && break; sleep 0.1; done
+  chk "while the update runs, the handoff-no-pr line for an orphan handoff ref is already on the level" 0 grep -q "handoff-no-pr refs/heads/handoff/topic-o $HB " "$LV"
+  chk "and the run is in flight (the stub has started)" 0 test -e "$t/slow.started"
+  : > "$t/slow.go"; wait "$hp"; rm -f "$t/slow.go" "$t/slow.started"
+  git -C "$t/o.git" update-ref -d refs/heads/handoff/topic-o
+  # probe_arm: the probe-ref level (a non-rev probe ref) is published before a slow relay push
+  cp "$t/bus/dispatched" "$t/bus/dispatched.h"; rm -f "$t/state/cloud-relayed" "$t/state/cloud-relayed.refused" "$t/state/cloud-relayed.tries" "$LV"
+  mk 5 $h $h $n; printf '5 %s thread %s\n' "$h" "$n" >> "$t/bus/dispatched"
+  git -C "$t/o.git" update-ref refs/heads/probe/odd "$(git -C "$t/o.git" rev-parse refs/heads/probe/rev-5-${n:0:8})"
+  printf '#!/bin/sh\necho "$1" > "%s/slow.started"\nwhile [ ! -e "%s/slow.go" ]; do sleep 0.1; done\nexec "%s" "$@"\n' "$t" "$t" "$stub" > "$hslow"
+  HPO_RELAY_PUSH=$hslow probe_arm >/dev/null 2>&1 & hp=$!
+  for _ in $(seq 100); do [ -e "$t/slow.started" ] && break; sleep 0.1; done
+  chk "while the relay push runs, the probe-ref line is already on the level" 0 grep -q "probe-ref refs/heads/probe/odd " "$LV"
+  chk "and the push is in flight" 0 test -e "$t/slow.started"
+  : > "$t/slow.go"; wait "$hp"; rm -f "$t/slow.go" "$t/slow.started"
+  mv "$t/bus/dispatched.h" "$t/bus/dispatched"; rm -f "$t/state/cloud-relayed" "$t/state/cloud-relayed.refused" "$t/state/cloud-relayed.tries"
+  git -C "$t/o.git" update-ref -d refs/heads/probe/odd; git -C "$t/o.git" update-ref -d refs/heads/probe/rev-5-${n:0:8}
+  for r in fix/topic-h-pr handoff/topic-h handoff-body/topic-h; do git -C "$t/o.git" update-ref -d refs/heads/$r; done
+  unset HX_HEAD; HPO_RELAY_UPDATE=$hu; rm -f "$t/hupdated" "$hf"
   git -C "$t/o.git" update-ref -d refs/heads/handoff/topic-b; : > "$LOG"
   chk "pass --loop is the only loop (a bad interval is refused)" 2 pass --loop --interval 0
   HPO_RELAY_UPDATE=$ustub; rm -f "$t/updated" "$t/state/cloud-handoff-failed"; : > "$LOG"; printf '%s\t%s\t%s\n' 41 fix/topic-a-pr "$PRH" > "$prs"
@@ -1353,7 +1520,7 @@ open(sys.argv[1], "w").close(); time.sleep(60)' "$t/stuck.held" "$t/state/pr/upd
     done
     cp "$LOG.level" "$t/stuck.level"
     # one more pass with every lock released: a released lock is never reported
-    stuck_free=$(stuckrun)
+    stuck_free=$(stuckrun | grep -v "^cloud_relay: state dir ")
   }
   stuckpass
   chk "a held branch lock aged 901 s by its recorded start is STUCK, naming branch, run pid and age" \
diff --git a/tools/audit/seat/instruments/cloud_relay.sh.md b/tools/audit/seat/instruments/cloud_relay.sh.md
index f9b36d0bb..31318c704 100644
--- a/tools/audit/seat/instruments/cloud_relay.sh.md
+++ b/tools/audit/seat/instruments/cloud_relay.sh.md
@@ -133,11 +133,18 @@
   `<topic> <body-sha>` for every body applied, by an update or body-only; a pass
   that finds no such file records every contained topic's body and runs
   nothing (the seed), and a contained body with no `Code:` line is recorded
-  and left alone. A failed update is noted in `cloud-handoff-failed` by
+  and left alone. A handoff ahead of a body that does not name its first 8
+  characters is partial work: `cloud_relay: HELD-BODY #<pr> <tip8>`, owed as
+  `handoff-held ... BODY`, retried next pass. Levels `handoff-no-pr`,
+  `handoff-hold-stale` (a hold-file line whose PR is not open) and
+  `handoff-body-unapplied` (`cloud_relay: BODY-ONLY` line: a body-only handoff
+  left unapplied while its body tip is newer than the PR head's commit) are
+  published before the serial update loops, so a slow update cannot delay them.
+  A failed update is noted in `cloud-handoff-failed` by
   `<topic> <code-sha>` (a body-only one by `<topic> <code-sha> <body-sha>`, so
   a new body re-triggers it), its reason, the update's last `REFUSE` line else
   its last line, kept beside it in `cloud-handoff-failed.why` (tab-separated),
-  owed as `OWED <utc> handoff-update <ref> <sha> <why>` in `<log>.level` while
+  owed as `OWED <utc> handoff-update <ref> <sha> <why>` (the `<why>` is the line kept in `cloud-handoff-failed.why`) in `<log>.level` while
   that entry matches, and retried only when the handoff (or body) moves. The
   update's output is held in a file until it ends, then replayed to the
   relay's stderr. An update that
@@ -158,6 +165,13 @@
   each passed push-verdict, `reviewer-fire`, `approve-held-runs`, `dispatch`)
   is opened in the ledger, never appended to the log, which keeps only the
   `POSTED` journal.
+  Relay guards (R10-RELAY-REPLAY): each pass prints `cloud_relay: state dir
+  <dir>, ledger <path>, log <path>` once, so a loop restarted without
+  `HPO_STATE_DIR` shows the wrong ledger. `relay` pushes nothing when
+  `review/<pr>` already has a commit with the probe's tree (the delivered
+  guard): the probe is recorded as relayed. A probe whose `ev/` holds names
+  differing only in case (`ev/HEAD.txt` and `ev/head.txt`; a file `ev/a` and a
+  directory `ev/A/x` too) is refused rc 2, naming both, and nothing is pushed.
   No-return line (triage P-E): each pass, a `dispatch/fixer-<topic>` tip older
   than `HPO_RELAY_NORETURN_SECS` (default 7200) and younger than
   `HPO_RELAY_NORETURN_WINDOW_SECS` (default 172800), with no `handoff-wip/`,
diff --git a/tools/audit/seat/ledger.py b/tools/audit/seat/ledger.py
index 4d1d738d9..6c14625ac 100644
--- a/tools/audit/seat/ledger.py
+++ b/tools/audit/seat/ledger.py
@@ -104,7 +104,7 @@ from merge_train import is_sha  # noqa: E402
 ROOT = Path(__file__).resolve().parents[3]
 KINDS = {
     "handoff-no-pr": "derived", "handoff-update": "derived", "probe-ref": "derived",
-    "handoff-hold-malformed": "derived", "handoff-held": "derived", "handoff-body-stale": "derived",
+    "handoff-hold-malformed": "derived", "handoff-held": "derived", "handoff-body-stale": "derived", "handoff-body-unapplied": "derived", "handoff-hold-stale": "derived",
     "design-build": "derived", "review-owed": "derived", "record-owed": "derived",
     "probe-refused": "derived", "confirm-owed": "derived", "push-stuck": "derived",
     "seat-no-return": "derived",
diff --git a/tools/audit/seat/orchestrator_tick.py b/tools/audit/seat/orchestrator_tick.py
index 89d2deea3..ececf246d 100644
--- a/tools/audit/seat/orchestrator_tick.py
+++ b/tools/audit/seat/orchestrator_tick.py
@@ -1049,6 +1049,15 @@ class Tick:
                 level = [r.strip() for r in fh if r.startswith("OWED ")]
         except FileNotFoundError:
             level = []
+            try:
+                with open(self.relay_log, encoding="utf-8", errors="replace") as fh:
+                    n = sum(1 for r in fh if r.startswith("OWED ") and " handoff-no-pr " in r)
+            except OSError:
+                n = 0
+            if n > 0:
+                self.line(S, f"GAP: {self.relay_log} holds {n} handoff-no-pr OWED line(s) but "
+                             f"{self.relay_log}.level does not exist: the relay has not published its level",
+                          flag=True)
         except OSError as e:
             level = []
             self.unreadable(S, "cloud-relay level", str(e)[:100])
@@ -4640,6 +4649,21 @@ def self_test() -> int:
         ])
         total, failed = total + a, failed + f
 
+        gap_text = f"OWED 2026-10-21T07:35:00Z handoff-no-pr refs/heads/handoff/t0 {'c' * 40}\n"
+        gap_no_level, _ = owed_lines(gap_text)
+        gap_no_lines, _ = owed_lines(o1 + "\n")
+        gap_with_level, _ = owed_lines(gap_text, gap_text)
+        a, f = check("relay GAP", [
+            ("a relay log holding a handoff-no-pr OWED line and no .level file prints GAP, flagged, with the count",
+             any(l["text"].startswith("GAP: ") and "holds 1 handoff-no-pr OWED line(s)" in l["text"] and l["flag"]
+                 for l in gap_no_level)),
+            ("null control: no .level file and no handoff-no-pr line prints no GAP",
+             not any(l["text"].startswith("GAP:") for l in gap_no_lines)),
+            ("null control: the same log with its .level file published prints no GAP",
+             not any(l["text"].startswith("GAP:") for l in gap_with_level)),
+        ])
+        total, failed = total + a, failed + f
+
         # ---- REVIEW OWED (fold s4) ----
         (tmp / "bus-ro").mkdir()
         (tmp / "bus-ro" / "dispatched").write_text(f"{61} {h(61)} thread {'0' * 32}\n")
diff --git a/tools/audit/seat/tick_loop.sh b/tools/audit/seat/tick_loop.sh
index 926931ddd..a75d48bad 100644
--- a/tools/audit/seat/tick_loop.sh
+++ b/tools/audit/seat/tick_loop.sh
@@ -62,6 +62,7 @@ HERE=$(cd "$(dirname -- "$0")" && pwd)
 # <out>.relay.rc. Only this process holds the lock fd, so it frees on the holder's
 # exit however that comes. 76: a finished relay's rc is not yet reaped; start none.
 RELAY_HOLDER='import fcntl, os, subprocess, sys, time
+os.setpgid(0, 0)  # own process group: a group signal to the stopped loop leaves an in-flight relay to write its rc
 r = sys.argv[1]
 f = open(r + ".lock", "a")
 try: fcntl.flock(f, fcntl.LOCK_EX | fcntl.LOCK_NB)
@@ -219,6 +220,14 @@ done" ]
     && [ "$(printf '%s\n' "$out" | grep -c SLOW-LOG)" = 2 ] && printf '%s\n' "$out" | grep -q 'relay=ok tick=0' \
     && [ "$(grep -c start "$t/slow")" = 2 ] && [ ! -f "$t/b.txt.relay.rc" ]
   ck "null control: the late relay is reaped with its log next pass, and a fast relay reports ok" $?
+  # A group TERM to the loop (a stop of its process group) must leave an in-flight relay to write its rc.
+  rm -f "$t/g.txt" "$t/g.txt.relay.rc"
+  RELAY_SLEEP=4 HPO_TICK_RELAY_WAIT=1 HPO_TICK_RELAY=$t/slow.sh HPO_TICK_CMD="bash $t/tick.sh" \
+    python3 -I -c 'import os, sys; os.setpgid(0, 0); os.execvp("bash", ["bash"] + sys.argv[1:])' "$0" --once --out "$t/g.txt" > "$t/g.log" 2>&1 &
+  gp=$!; sleep 2.5; kill -TERM -- "-$gp" 2>/dev/null; wait "$gp" 2>/dev/null
+  k=0; while [ ! -f "$t/g.txt.relay.rc" ] && [ $k -lt 100 ]; do sleep 0.1; k=$((k + 1)); done
+  [ -f "$t/g.txt.relay.rc" ]
+  ck "a TERM to the loop's process group leaves the in-flight relay to write its rc" $?
   # Stubbed and --once, so a mutant that accepts the interval cannot loop on the real tick.
   HPO_TICK_RELAY=$t/absent.sh HPO_TICK_CMD="bash $t/tick.sh" bash "$0" --once --interval x --out "$t/b.txt" > "$t/e" 2>&1
   [ $? = 2 ] && grep -q 'interval' "$t/e"

## Before you return the verdict (P275)
Run `python3 -I tools/audit/carry_audit.py check --body <PR body file> --comments <file holding [{"id": 0, "body": <verdict.md text>}]>`. Give every reported item its own `Carry: <GROUP> | #<issue> | O<n> | dismissed: <reason>`;
an evidence line flagged by its wording takes `Carry: dismissed: evidence, not a finding`. Return the verdict only at rc 0.
