# Review packet #3249
head: 6bca687e48b8fe68ddb49ca0bac866add51e1078
base: 30638cf0c8a7114019682f87051a4a282d2981ff

Start here (fix-review.md). Re-read the live check state before a verdict: the digest is as read at render.

## Gate digest: green
CodeQL id=128008998089 success
arch-score / arch-score id=128025769976 success
arm id=128008513033 skipped
budget-raise-gate / budget-raise-gate id=128025769523 success
cancel-superseded id=128025767128 success
codeql id=128025769910 skipped
codeql / Analyze (actions) id=128008834427 success
codeql / Analyze (javascript-typescript) id=128008834410 success
codeql / Analyze (python) id=128008834581 success
gate id=128025768789 success
governance id=128025769510 skipped
governance / delivery-status id=128008834403 success
governance / delivery-status-publish id=128008837881 skipped
governance / env-matrix id=128008834361 success
governance / instrument-self-tests id=128008834423 success
governance / policy-docs id=128008834590 success
governance / record id=128008837549 skipped
governance / wave-script id=128008834720 success
hassfest id=128025768594 skipped
hassfest / hassfest id=128008834558 success
kernel-points id=128025770073 skipped
pr-contract id=128025771196 skipped
pr-contract / pr-contract id=128022460572 success
prelude id=128025768331 success
refresh id=128025825431 success
tests id=128025769212 skipped
tests / arch-instrument id=128009582214 success
tests / briefs id=128008834337 success
tests / browser id=128009582252 success
tests / ci-ratchet id=128021057313 skipped
tests / claims-autofix id=128012917780 skipped
tests / closure-scope id=128008834483 success
tests / closures id=128009582261 success
tests / closures-autofix id=128021056499 skipped
tests / coverage id=128009581940 success
tests / coverage-ratchet id=128010608185 success
tests / fast (3.14) id=128009582259 success
tests / graders-head-copy id=128010608152 success
tests / lane-proofs id=128012914422 success
tests / mutation id=128008834554 success
tests / mutation-autofix id=128009950911 skipped
tests / mutation-pins id=128009950405 skipped
tests / nightly-ha id=128009585080 skipped
tests / nightly-status id=128008834383 success
tests / replay id=128009585819 skipped
tests / typing id=128009581947 success
validate id=128025769973 skipped
validate / validate-hacs id=128008834294 success

## Refusals
none

## Advisories
hot-file: HPO_BUS_TRAIN_STATE is unset, so every merge verdict reads unboarded

## carry_audit at the head
NOTE stale tree: cb48d97e2cd0860435e5a2ad71d3534a93944e30 lacks origin/main 862affd07d2ce3430c200d4f09aa6e16934b5c4d; roster read at origin/main
NOTE body item e8623ad0: dismissed:built in this diff or already in the tree
CARRY-AUDIT: 1 finding item(s): 1 routed, 0 unrouted, 0 bad destination(s)

## figure_lint at the head
ok         bash tools/audit/seat/bus.sh --self-test
             `tools/audit/seat/bus.sh` is in the tree at this head
  ok         python3 dev/audit/harnesses/r10_seat_selftests_mutants.py
             `dev/audit/harnesses/r10_seat_selftests_mutants.py` is in the tree at this head

FIGURES: 2 resolved, 0 not verified, 0 refused

## Finder's harness: none named
### at the base
not run
### at the head
not run

## Mutation-ledger diff
none

## Three-dot diff
diff --git a/dev/audit/harnesses/r10_seat_selftests_mutants.py b/dev/audit/harnesses/r10_seat_selftests_mutants.py
index e63e3c1fd..7daa40094 100644
--- a/dev/audit/harnesses/r10_seat_selftests_mutants.py
+++ b/dev/audit/harnesses/r10_seat_selftests_mutants.py
@@ -229,6 +229,13 @@ MUTANTS = [
     ("bus-7", "bus.sh", '[ -n "$a" ] && [ -z "$(grep -vxF \'dependabot[bot]\' <<< "$a")" ]  # mut:botonly', '[ -n "$a" ]'),
     ("bus-8", "bus.sh", 'if [ -n "$holder" ] && kill -0 "$holder" 2>/dev/null; then  # mut:watchlock', 'if false; then'),
     ("bus-9", "bus.sh", '  rm -f "$b"; [ "$rc" != 1 ]  # mut:landed', '  rm -f "$b"; true'),
+    ("bus-10", "bus.sh", 'if [ "$(git rev-parse "$tip^{tree}" 2>/dev/null)" = "$tree" ]; then  # mut:sametree', 'if false; then'),
+    ("bus-11", "bus.sh", 'if [ -n "$holder" ] && kill -0 "$holder" 2>/dev/null; then  # mut:confirmlock', 'if false; then'),
+    ("bus-12", "bus.sh", '    [ "$v" != merge ] || die "dispatch: #$pr\'s head $h already holds a merge verdict, so no second reviewer is dispatched"  # mut:mergehead', '    true'),
+    ("bus-13", "bus.sh", 'if [ -n "$fixing" ]; then  # mut:autofixhold', 'if false; then'),
+    ("bus-14", "bus.sh", """select(.status != "completed") | .name' 2>>"$err"); then  # mut:completedfilter""", """select(true) | .name' 2>>"$err"); then  # mut:completedfilter"""),
+    ("bus-15", "bus.sh", """sed 's/^/bus: check-runs read: /' "$err" >&2; rm -f "$err"; return 1""", """rm -f "$err"; return 0"""),
+    ("bus-16", "bus.sh", 'if [ -z "$holder" ] && [ "$blank" -lt "${HPO_BUS_PID_SETTLE:-10}" ]; then  # mut:pidsettle', 'if false; then'),
     # P43: the pre-flight reads each pull request's destinations with its head as the extra ref
     ("queue_pre_flight-1", "queue_pre_flight.py", "extra_ref=head or None)", "extra_ref=None)"),
     # carry_audit.py check reads no roster for a verdict with no finding item (bus.sh's step grades it:
@@ -319,6 +326,7 @@ MUTANTS = [
     # R10-ORCH-REVIEW-PACKET (P229, P256): the handoff-not-applied signal, the
     # handoff refusals and body_push's call of them; body_push-1/2 are graded by
     # prepr's self-test (STEP_OF), which drives body_push.
+    ("review_packet-own", "review_packet.py", "    this_pr, note = own_pr(open_prs, topic, is_ancestor)  # mut:ownpr", "    this_pr, note = 0, None"),
     ("review_packet-1", "review_packet.py",
      "return None if is_ancestor(tip, head) else", "return None if not is_ancestor(tip, head) else"),
     ("review_packet-2", "review_packet.py",
diff --git a/dev/programme/delivery/3249.md b/dev/programme/delivery/3249.md
new file mode 100644
index 000000000..8c5f51f9d
--- /dev/null
+++ b/dev/programme/delivery/3249.md
@@ -0,0 +1 @@
+- [#3249](https://github.com/tvofi/heatpump_optimizer/pull/3249) — **open**, R10-DISPATCH-AT-HANDOFF: dispatch at handoff (R10-DISPATCH-AT-HANDOFF)
diff --git a/tools/audit/seat/bus.sh b/tools/audit/seat/bus.sh
index bb14786a4..05471b85f 100755
--- a/tools/audit/seat/bus.sh
+++ b/tools/audit/seat/bus.sh
@@ -327,6 +327,13 @@ append_commit() { # family pr tree message -> pushes one commit on <family>/<pr>
     # from here on FETCH_HEAD belongs to whatever else is fetching.
     git fetch -q "$REMOTE" "refs/heads/$fam/$pr" \
       || { printf 'bus: REFUSE: could not fetch %s/%s\n' "$fam" "$pr" >&2; return 1; }
+    # A same-tree append can only repeat a verdict (post_verdict signs "<pr> <tree>"; each round's
+    # nonce makes its tree distinct), and it would leave the posted commit one behind the tip
+    # (P374, #3173): answer the existing tip, write and push nothing.
+    if [ "$(git rev-parse "$tip^{tree}" 2>/dev/null)" = "$tree" ]; then  # mut:sametree
+      printf '%s/%s %s\n' "$fam" "$pr" "$tip"
+      return 0
+    fi
     parent="-p $tip"
   fi
   # shellcheck disable=SC2086 # $parent is empty or exactly "-p <sha>"
@@ -494,6 +501,26 @@ three_rounds() { # pr past-three-reason -> 0 to dispatch; else why
   return 1
 }
 
+autofix_inflight() { # head -> prints the autofix bot jobs of the head that are not completed; rc 1 when the read failed
+  local raw err t=1 tries=${HPO_BUS_READ_TRIES:-4} out
+  err=$(mktemp "${TMPDIR:-/tmp}/bus-checks.XXXXXX") || return 1
+  while :; do
+    # --paginate: a head can carry more than one page of 100 check-runs. Every page is JSON the
+    # filter reads; the same classifier the Python instruments use (gh_read.py) decides whether a
+    # failure is worth another read, and a failure no later read can ride out refuses at once.
+    if raw=$(${HPO_BUS_CHECKS:-${HPO_BUS_GH:-gh} api --paginate "repos/$REPO/commits/$1/check-runs?per_page=100"} 2>"$err") \
+       && out=$(printf '%s' "$raw" | jq -r '.check_runs[] | select(.status != "completed") | .name' 2>>"$err"); then  # mut:completedfilter
+      rm -f "$err"
+      printf '%s\n' "$out" | grep -E '^(mutation|closures|claims)-autofix$' | sort -u | paste -sd, -
+      return 0
+    fi
+    if [ "$t" -ge "$tries" ] || ! python3 -I "$ROOT/tools/audit/seat/gh_read.py" --classify < "$err"; then
+      sed 's/^/bus: check-runs read: /' "$err" >&2; rm -f "$err"; return 1
+    fi
+    t=$((t + 1)); sleep "${HPO_BUS_READ_SLEEP:-5}"
+  done
+}
+
 # THE WORKER REGISTRY is $S/dispatched, one line per dispatch, `<pr> <head> <reviewer> <nonce>
 # <utc> <model|->` (lines before R10-ORCH-DISPATCH-REG stop at the nonce). Every reader keys on
 # the first four fields. `--nonce` re-records a nonce minted earlier at the same pr and head --
@@ -505,6 +532,7 @@ three_rounds() { # pr past-three-reason -> 0 to dispatch; else why
 # names it only once `check` reads that head in it. --harness/--harness-file is the finder's.
 # HPO_BUS_PACKER replaces the renderer (the self-test's stub).
 dispatch() { # pr head reviewer [--reviewed-head <sha>] [--nonce N] [--model M] [--past-three <reason>] [--harness P|--harness-file F] -> records, closes, prints the packet and nonce lines
+  local force="" fixing=""
   local pr=${1:-} h=${2:-} r=${3:-} n="" m=- p3="" row why rh="" carry v rc hk="" hv="" pk prc=0 pmsg="" pkline="" cls
   shift 3 2>/dev/null || shift $#
   while [ $# -gt 0 ]; do
@@ -512,6 +540,7 @@ dispatch() { # pr head reviewer [--reviewed-head <sha>] [--nonce N] [--model M]
       --reviewed-head) [[ ${2:-} =~ ^[0-9a-f]{40}$ ]] || die "dispatch: --reviewed-head takes a 40-hex commit"; rh=$2; shift 2 ;;
       --nonce) [[ ${2:-} =~ ^[0-9a-f]{32}$ ]] || die "dispatch: --nonce takes a 32-hex nonce"; n=$2; shift 2 ;;
       --model) [[ ${2:-} =~ ^[A-Za-z0-9._-]+$ ]] || die "dispatch: --model takes one token"; m=$2; shift 2 ;;
+      --force) force=1; shift ;;
       --past-three) [ -n "${2:-}" ] && [ "${2#--}" = "$2" ] || die "dispatch: --past-three needs a reason"; p3=$2; shift 2 ;;
       --harness|--harness-file) [ -n "${2:-}" ] && [ -z "$hk" ] || die "dispatch: $1 takes one path, once"; hk=$1; hv=$2; shift 2 ;;
       *) die "dispatch: unknown argument '$1'" ;;
@@ -590,6 +619,29 @@ dispatch() { # pr head reviewer [--reviewed-head <sha>] [--nonce N] [--model M]
       esac
     fi
   fi
+  # A SECOND REVIEWER AT A MERGE-VERDICT HEAD (card 3, 2026-11-01): a head that already holds a
+  # merge verdict has its review; --nonce re-records a mint and is no new dispatch.
+  if [ -z "$n" ]; then
+    v=$(verdict_at "$pr" "$h") || die "dispatch: cannot read verdict/$pr to learn whether $h already holds a verdict"
+    [ "$v" != merge ] || die "dispatch: #$pr's head $h already holds a merge verdict, so no second reviewer is dispatched"  # mut:mergehead
+  fi
+  # THE AUTOFIX HOLD (P344): a bot job that can still push a commit (mutation-autofix,
+  # closures-autofix, claims-autofix queued or in progress) moves the head under the reviewer, so
+  # the dispatch waits (rc 3). A completed job, red or green, is no commit coming. --force
+  # overrides with one ledger line. The check-runs are read once (autofix_inflight); HPO_BUS_CHECKS
+  # replaces the `gh api` call and prints the raw check-run JSON, so the status filter below runs.
+  if [ -z "$n" ]; then
+    fixing=$(autofix_inflight "$h") || printf 'bus: the check-runs of %s could not be read, so the autofix hold was NOT checked and this dispatch proceeds without it\n' "$h" >&2
+    if [ -n "$fixing" ]; then  # mut:autofixhold
+      if [ -n "$force" ]; then
+        printf '%s dispatch --force #%s %s over %s\n' "$(date -u +%FT%TZ)" "$pr" "$h" "$fixing" >> "$S/dispatch-force" 2>/dev/null || :
+        printf 'bus: --force: dispatching over the autofix job(s) %s\n' "$fixing" >&2
+      else
+        printf 'bus: HOLD: #%s head %s: autofix job(s) %s still queued or running and may move the head; dispatch again once they conclude (--force overrides)\n' "$pr" "$h" "$fixing" >&2
+        exit 3
+      fi
+    fi
+  fi
   why=$(three_rounds "$pr" "$p3") || die "dispatch: $why"
   pk=$S/packets/$pr-$h.md
   # THE PACKET IS AN AID, NEVER A GATE ON THE DISPATCH. Two failures are different:
@@ -633,6 +685,32 @@ dispatch() { # pr head reviewer [--reviewed-head <sha>] [--nonce N] [--model M]
 }
 
 confirm() { # pr review-commit -> signs the reviewer's proposal onto verdict/<pr>, then posts it
+  local lk holder rc blank=0
+  numeric "${1:-}" || die "confirm: the pull request '${1:-}' is not a number"
+  # One confirm per pull request at a time, across the replay pre-check, append_commit and
+  # post_verdict (P354): the lock holds the pid and a dead holder's is taken over (watch.lock).
+  mkdir -p "$S" || die "confirm: cannot create $S"
+  lk=$S/confirm.$1.lock
+  # A lock taken by mkdir has no pid for a moment: an EMPTY pid file is a holder still writing it,
+  # live for a bounded settle (HPO_BUS_PID_SETTLE polls of 0.2 s, 2 s by default), and only then
+  # a holder that died between its mkdir and its write.
+  until mkdir "$lk" 2>/dev/null; do
+    holder=$(cat "$lk/pid" 2>/dev/null)
+    if [ -z "$holder" ] && [ "$blank" -lt "${HPO_BUS_PID_SETTLE:-10}" ]; then  # mut:pidsettle
+      blank=$((blank + 1)); sleep 0.2
+    elif [ -n "$holder" ] && kill -0 "$holder" 2>/dev/null; then  # mut:confirmlock
+      blank=0; sleep 1
+    else
+      rm -rf "$lk"; blank=0
+    fi
+  done
+  printf '%s\n' "$$" > "$lk/pid"
+  confirm_locked "$@"; rc=$?
+  rm -rf "$lk"
+  return $rc
+}
+
+confirm_locked() { # pr review-commit -> confirm's body, run under its per-pull-request lock
   local pr c d first hsha thread key tree sig msg line v model
   numeric "${1:-}" || die "confirm: the pull request '${1:-}' is not a number"
   [[ ${2:-} =~ ^[0-9a-f]{40}$ ]] || die "confirm: '${2:-}' is not a 40-hex review commit"
@@ -861,7 +939,7 @@ self_test() {
   # 7, 9, 12, 21, 22 and 24 (21-24 are the FETCHHEAD/poster arms' pull
   # requests); h2 (a child) inherits them; norow is the base, with none.
   mkdir -p "$W/seat/$ROW_DIR"
-  for n in 7 9 12 21 22 24 31; do
+  for n in 7 9 12 21 22 24 30 31 32 33 34; do
     printf -- '- [#%s](https://github.com/o/r/pull/%s) — **open**\n' "$n" "$n" > "$W/seat/$ROW_DIR/$n.md"
   done
   git -C "$W/seat" -c user.name=t -c user.email=t@t add -A
@@ -1184,6 +1262,14 @@ bus-nonce: $N1b" ] && [ "$(grep -c " $N1b " "$W/state/dispatched")" = 2 ] \
   [ $rc != 0 ] && echo "$out" | grep -q "^BUS refused 7 $r1: this signed verdict was already posted on #7 (a replay)" \
     && [ "$(tip verdict/7)" = "$v1" ] && [ "$(calls)" = 1 ]
   expect "a second confirm of a posted tree is refused and verdict/<pr> stays at the first commit" $?
+  # P354: a confirm waits on a live holder of the pull request's lock; a dead holder's is taken over.
+  sleep 30 & cl=$!; mkdir -p "$W/state/confirm.7.lock"; echo "$cl" > "$W/state/confirm.7.lock/pid"
+  run confirm 7 "$r1" >/dev/null 2>&1 & cw=$!; sleep 3
+  kill -0 "$cw" 2>/dev/null && [ "$(tip verdict/7)" = "$v1" ]; expect "a confirm under a live holder's lock waits and moves nothing (P354)" $?
+  kill "$cw" "$cl" 2>/dev/null; wait "$cw" "$cl" 2>/dev/null
+  rm -rf "$W/state/confirm.7.lock"; mkdir -p "$W/state/confirm.7.lock"; echo 999999 > "$W/state/confirm.7.lock/pid"
+  out=$(run confirm 7 "$r1"); rc=$?
+  [ "$rc" = 1 ] && echo "$out" | grep -q "(a replay)" && [ ! -d "$W/state/confirm.7.lock" ]; expect "null control: a dead holder's lock is taken over and released (P354)" $?
 
   # A signed verdict copied to another pull request, or re-used over another tree.
   git -C "$W/seat" fetch -q origin verdict/7
@@ -1354,6 +1440,19 @@ B
     && [ "$(tip review/22^)" = "$g1" ]
   expect "an ordinary append with no intervening fetch is the same commit object as before" $?
 
+  # P374: a verdict pushed twice appends once. The same verdict and evidence build one tree, and a
+  # same-tree commit left the posted commit one behind the tip (#3173). Null control: the next
+  # round's verdict (new nonce, new tree) still appends.
+  g2=$(tip review/22)
+  out=$(seat push-verdict 22 "$W/ff2-22.md" "$W/ev2"); rc=$?
+  [ $rc = 0 ] && [ "$(tip review/22)" = "$g2" ] && [ "$out" = "review/22 $g2" ]
+  expect "a repeated push-verdict of one verdict appends nothing and prints the existing tip (P374)" $?
+  N3e=$(run dispatch 22 "$h2" cmsg_F | sed -n 's/^bus-nonce: //p')
+  printf 'Fix review: blocked %s harness: class-open x\n\nbus-nonce: %s\n' "$h2" "$N3e" > "$W/ff3-22.md"
+  seat push-verdict 22 "$W/ff3-22.md" "$W/ev2" >/dev/null
+  [ "$(tip review/22)" != "$g2" ] && [ "$(tip review/22^)" = "$g2" ]
+  expect "null control: a verdict with a new nonce, so a new tree, still appends (P374)" $?
+
   # A COPY OF THE SCRIPT OUTSIDE A CHECKOUT REFUSES BEFORE ANY PUSH (#2074).
   # ROOT is three levels above the file, so a copy parked in a throwaway
   # directory derives its poster from a path that cannot exist -- and `confirm`
@@ -1555,6 +1654,80 @@ B
   # #2310: a blocked verdict (the grammar that carries free text) whose first line names a host path is refused by
   # append_commit's guard, and review/7 does not move; the same verdict with a
   # clean tail is its null control and proposes.
+  # CARD 3: a head holding a merge verdict takes no second reviewer; a head with none does (null
+  # control), and the autofix hold (P344) is exercised on the same pull request.
+  N30=$(run dispatch 30 "$h1" cmsg_S | sed -n 's/^bus-nonce: //p')
+  printf 'Fix review: merge %s\n\nbus-nonce: %s\n' "$h1" "$N30" > "$W/m30.md"
+  seat push-verdict 30 "$W/m30.md" "$W/ev1" >/dev/null
+  HPO_BUS_TRAIN_STATE=$W/train HPO_BUS_TRAIN_CMD="bash $W/addstub" run confirm 30 "$(tip review/30)" >/dev/null
+  out=$(run dispatch 30 "$h1" cmsg_S2); rc=$?
+  [ $rc != 0 ] && echo "$out" | grep -q "already holds a merge verdict" && [ "$(grep -c '^30 ' "$W/state/dispatched")" = 1 ]
+  expect "a second reviewer at a head holding a merge verdict is refused, recording nothing" $?
+  out=$(run dispatch 30 "$h2" cmsg_S3); rc=$?
+  [ $rc = 0 ]; expect "null control: a head with no verdict dispatches (the first dispatch at a head is accepted)" $?
+  # The stub stands in for `gh api` and prints the API's own JSON, so bus.sh's status filter runs:
+  # $W/checks-in holds `name status` lines, rendered to {"check_runs":[{name,status}...]}.
+  chk() { # name-status pairs... -> a check-runs response on $W/checks-in's stub
+    printf '#!/bin/bash\nif [ -n "${BUS_TEST_CHECKS_FAIL:-}" ]; then echo "gh: Not Found (HTTP 404)" >&2; exit 1; fi\njq -Rn \x27{check_runs: [inputs | split(" ") | {name: .[0], status: .[1]}]}\x27 < "%s/checks-in"\n' "$W" > "$W/checks"
+  }
+  chk
+  nd=$(grep -c . "$W/state/dispatched")
+  printf 'mutation-autofix in_progress\nprelude completed\n' > "$W/checks-in"
+  out=$(HPO_BUS_CHECKS="bash $W/checks" run dispatch 31 "$h1" cmsg_A); rc=$?
+  [ $rc = 3 ] && echo "$out" | grep -q "HOLD.*mutation-autofix" && [ "$(grep -c . "$W/state/dispatched")" = "$nd" ]
+  expect "a dispatch is held (rc 3, naming the job) while mutation-autofix is in progress, recording nothing (P344)" $?
+  printf 'closures-autofix queued\n' > "$W/checks-in"
+  out=$(HPO_BUS_CHECKS="bash $W/checks" run dispatch 31 "$h1" cmsg_A); rc=$?
+  [ $rc = 3 ] && echo "$out" | grep -q "HOLD.*closures-autofix"; expect "a queued closures-autofix holds the dispatch too (P344)" $?
+  out=$(HPO_BUS_CHECKS="bash $W/checks" run dispatch 31 "$h1" cmsg_A --force); rc=$?
+  [ $rc = 0 ] && [ -s "$W/state/dispatch-force" ]; expect "--force dispatches over the hold and writes one ledger line (P344)" $?
+  printf 'mutation-autofix completed\nclosures-autofix completed\nclaims-autofix completed\nprelude completed\n' > "$W/checks-in"
+  out=$(HPO_BUS_CHECKS="bash $W/checks" run dispatch 32 "$h1" cmsg_A); rc=$?
+  [ $rc = 0 ]; expect "all autofix jobs completed dispatches (P344)" $?
+  printf 'claims-autofix completed\nprelude completed\n' > "$W/checks-in"
+  out=$(HPO_BUS_CHECKS="bash $W/checks" run dispatch 32 "$h2" cmsg_A); rc=$?
+  [ $rc = 0 ]; expect "a red completed autofix job is no commit coming: it dispatches (P344)" $?
+  printf 'prelude completed\n' > "$W/checks-in"
+  out=$(HPO_BUS_CHECKS="bash $W/checks" run dispatch 32 "$h1" cmsg_A2); rc=$?
+  [ $rc = 0 ]; expect "null control: no autofix job at all dispatches (P344)" $?
+  # A failed read says so: it neither holds nor passes in silence (a 404 is no read a retry rides out).
+  out=$(BUS_TEST_CHECKS_FAIL=1 HPO_BUS_CHECKS="bash $W/checks" run dispatch 32 "$h2" cmsg_A3); rc=$?
+  [ $rc = 0 ] && echo "$out" | grep -q "could not be read, so the autofix hold was NOT checked" && echo "$out" | grep -q "check-runs read: gh: Not Found"
+  expect "a failed check-runs read is reported on a line, not swallowed (P344)" $?
+  # P374 arm (b), #3173: a confirm whose poster refused leaves verdict/<pr> at its signed commit; a
+  # second review commit with the SAME tree, confirmed, appends nothing and posts at that commit.
+  N33=$(run dispatch 33 "$h1" cmsg_T | sed -n 's/^bus-nonce: //p')
+  printf 'Fix review: blocked %s harness: class-open x\n\nbus-nonce: %s\n' "$h1" "$N33" > "$W/t33.md"
+  seat push-verdict 33 "$W/t33.md" "$W/ev1" >/dev/null
+  rt1=$(tip review/33)
+  BUS_TEST_POSTER_FAIL=1 run confirm 33 "$rt1" >/dev/null
+  vt1=$(tip verdict/33)
+  rt2=$(git -C "$W/seat" commit-tree "$rt1^{tree}" -p "$rt1" -m "second review commit, same tree" | tee "$W/rt2" )
+  git -C "$W/seat" push -q origin "$rt2:refs/heads/review/33"
+  out=$(run confirm 33 "$rt2"); rc=$?
+  [ "$(tip verdict/33)" = "$vt1" ] && echo "$out" | grep -q "^BUS posted 33 $vt1 "
+  expect "a confirm on a second review commit of the same tree leaves verdict/<pr> at the first signed commit and posts there (P374)" $?
+  # P354: two concurrent confirms of one commit produce one verdict commit and one post.
+  N34=$(run dispatch 34 "$h1" cmsg_U | sed -n 's/^bus-nonce: //p')
+  printf 'Fix review: blocked %s harness: class-open x\n\nbus-nonce: %s\n' "$h1" "$N34" > "$W/t34.md"
+  seat push-verdict 34 "$W/t34.md" "$W/ev1" >/dev/null
+  rt=$(tip review/34); c0=$(calls)
+  run confirm 34 "$rt" > "$W/cc1" & cp1=$!
+  run confirm 34 "$rt" > "$W/cc2" & cp2=$!
+  wait "$cp1" "$cp2"
+  [ "$(git -C "$W/origin.git" rev-list --count "verdict/34")" = 1 ] && [ "$(( $(calls) - c0 ))" = 1 ] \
+    && [ "$(cat "$W/cc1" "$W/cc2" | grep -c '^BUS posted 34 ')" = 1 ]
+  expect "two concurrent confirms produce one verdict commit and one post (P354)" $?
+  # An empty pid file is a holder still writing it: it waits out the settle, then is taken over.
+  mkdir -p "$W/state/confirm.7.lock"; : > "$W/state/confirm.7.lock/pid"
+  run confirm 7 "$r1" >/dev/null 2>&1 & cw=$!; sleep 1
+  kill -0 "$cw" 2>/dev/null && [ -d "$W/state/confirm.7.lock" ]; expect "a lock whose pid is not yet written is a live holder inside the settle (P354)" $?
+  wait "$cw" 2>/dev/null
+  [ ! -d "$W/state/confirm.7.lock" ]; expect "null control: an empty pid left past the settle is a dead holder's, taken over (P354)" $?
+
+  # The block below re-dispatches at $h1 many times; its merge verdict is retired first (the
+  # refusal of a second reviewer at a merge-verdict head is exercised on pull request 30 below).
+  git -C "$W/seat" push -q origin :refs/heads/verdict/7
   r7=$(tip review/7)
   NL=$(run dispatch 7 "$h1" cmsg_L | sed -n 's/^bus-nonce: //p')
   printf 'Fix review: blocked %s harness: /%s/exampleuser/x\n\nbus-nonce: %s\n' "$h1" Users "$NL" > "$W/merge-leak.md"
diff --git a/tools/audit/seat/review_packet.py b/tools/audit/seat/review_packet.py
index ebc58358e..2a6e91d22 100644
--- a/tools/audit/seat/review_packet.py
+++ b/tools/audit/seat/review_packet.py
@@ -219,6 +219,26 @@ def hot_file_refusals(paths: set[str], open_prs: list[dict], boarded: set[int],
     return out
 
 
+def own_pr(open_prs: list[dict], topic: str, is_ancestor) -> tuple[int, str | None]:
+    """The open pull request a handoff updates (P368): by ancestry -- the one whose head is an
+    ancestor of the handoff's HEAD, since a re-cut is built on it -- and only when none is, by
+    head branch `fix/<topic>`. (0, None) when none qualifies; two qualifying are excluded
+    neither and named in the note, because a guess would hide a real collision."""
+    for found in ([p for p in open_prs if is_ancestor(p["head"])],
+                  [p for p in open_prs if p.get("branch") == f"fix/{topic}"]):
+        if len(found) == 1:
+            return found[0]["number"], None
+        if found:
+            return 0, "own-pr: ambiguous, " + " and ".join(f"#{p['number']}" for p in found) + " both qualify; neither is excluded from the hot-file rule"
+    return 0, None
+
+
+def handoff_hot(touched: set[str], open_prs: list[dict], boarded: set[int], topic: str, is_ancestor) -> list[str]:
+    """The handoff's hot-file refusals, the pull request it updates excluded (P368)."""
+    this_pr, note = own_pr(open_prs, topic, is_ancestor)  # mut:ownpr
+    return hot_file_refusals(touched, open_prs, boarded, this_pr) + ([note] if note else [])
+
+
 def handoff_topics(branch: str) -> list[str]:
     """The handoff topics a pull request's branch can carry: `fix/<t>` or
     `fix/<t>-pr`, `open_pr.sh`'s two spellings; none for any other shape."""
@@ -568,7 +588,7 @@ def hot_prs(touched: set[str]) -> tuple[list[dict], set[int]]:
         merge_head = None
         if tip and not git("fetch", "-q", "origin", f"refs/heads/verdict/{p['number']}", check=False):
             merge_head = verdict_merge_head(tip[0])
-        open_prs.append({"number": p["number"], "head": p["head"]["sha"], "files": files,
+        open_prs.append({"number": p["number"], "head": p["head"]["sha"], "branch": p["head"]["ref"], "files": files,
                          "merge_verdict_head": merge_head})
     return open_prs, train_boarded()
 
@@ -590,8 +610,10 @@ def handoff(a) -> int:
     gid = roster_lib.group_for_branch(roster, f"handoff/{a.topic}")
     carries = len(roster_lib.groups_of(roster)[gid].get("carry") or []) if gid else 0
     open_prs, boarded = hot_prs(touched)
+    anc = lambda sha: subprocess.run(  # noqa: E731
+        ["git", "merge-base", "--is-ancestor", sha, head], cwd=repo(), capture_output=True).returncode == 0
     refusals = handoff_refusals(structure_at_merge(a.main, head),
-                                hot_file_refusals(touched, open_prs, boarded, 0), unnamed_carries(body, carries),
+                                handoff_hot(touched, open_prs, boarded, a.topic, anc), unnamed_carries(body, carries),
                                 unlanded_carries(landed_cites(body), *reversed(roster_carry_reader([a.topic], ref))))
     for x in refusals:
         print(f"review_packet: REFUSE {x}", file=sys.stderr)
@@ -770,6 +792,22 @@ def _self_test() -> int:
     check("hot-file arm: an unboarded merge verdict sharing a hot file refuses",
           len(hot_file_refusals({HOT_FILES[0]}, prs, set(), 7)) == 1)
     check("hot-file null: the same verdict boarded passes", hot_file_refusals({HOT_FILES[0]}, prs, {9}, 7) == [])
+    # P368: the handoff's own pull request is not a collision with itself.
+    own = [{"number": 9, "head": H, "branch": "fix/t-2", "files": [HOT_FILES[0]], "merge_verdict_head": H}]
+    n, note = own_pr(own, "t", lambda sha: sha == H)
+    check("hot-file own-pr arm (a): the pull request whose head is an ancestor is not refused against itself",
+          n == 9 and note is None
+          and handoff_hot({HOT_FILES[0]}, own, set(), "t", lambda sha: sha == H) == [])
+    n2, _ = own_pr(own, "t-2", lambda sha: False)
+    check("own-pr: with no ancestor, the head branch fix/<topic> identifies it", n2 == 9)
+    other = [dict(own[0], number=11, head=B, branch="fix/other")]
+    n3, _ = own_pr(own + other, "t", lambda sha: sha == H)
+    check("hot-file own-pr arm (b) null: a different open pull request holding an unboarded merge verdict still refuses",
+          n3 == 9 and len(handoff_hot({HOT_FILES[0]}, own + [dict(other[0], merge_verdict_head=B)], set(), "t",
+                                      lambda sha: sha == H)) == 1)
+    n4, note4 = own_pr(own + other, "t", lambda sha: True)
+    check("hot-file own-pr arm (c): two ancestors are excluded neither and both are named",
+          n4 == 0 and note4 and "#9" in note4 and "#11" in note4)
     check("hot-file null: a verdict at a stale head is not a merge verdict at its head",
           hot_file_refusals({HOT_FILES[0]}, [dict(prs[0], merge_verdict_head=B)], set(), 7) == [])
     check("hot-file reader: the verdict's head is the first line of VERDICT.md through proof_watch.parse_verdict",

## Before you return the verdict (P275)
Run `python3 -I tools/audit/carry_audit.py check --body <PR body file> --comments <file holding [{"id": 0, "body": <verdict.md text>}]>`. Give every reported item its own `Carry: <GROUP> | #<issue> | O<n> | dismissed: <reason>`;
an evidence line flagged by its wording takes `Carry: dismissed: evidence, not a finding`. Return the verdict only at rc 0.
