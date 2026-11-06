# Review packet #3249
head: 520550cebe311fad3d4f529c5267561ffe7e227c
base: b36679ceaa65a08a67a84f0d934c93aa15f7c7f3

Start here (fix-review.md). Re-read the live check state before a verdict: the digest is as read at render.

## Gate digest: green
CodeQL id=127915159850 success
arch-score / arch-score id=127939676231 success
arm id=127914852000 skipped
budget-raise-gate / budget-raise-gate id=127939676885 success
cancel-superseded id=127939720780 success
codeql id=127939675342 skipped
codeql / Analyze (actions) id=127915081560 success
codeql / Analyze (javascript-typescript) id=127915081696 success
codeql / Analyze (python) id=127915081614 success
gate id=127939676225 success
governance id=127939739904 skipped
governance / delivery-status id=127915081880 success
governance / delivery-status-publish id=127915084519 skipped
governance / env-matrix id=127915081790 success
governance / instrument-self-tests id=127915081781 success
governance / policy-docs id=127915081812 success
governance / record id=127915084742 skipped
governance / wave-script id=127915081669 success
hassfest id=127939721373 skipped
hassfest / hassfest id=127915081452 success
kernel-points id=127939740259 skipped
pr-contract id=127939676000 skipped
pr-contract / pr-contract id=127932730935 success
prelude id=127939675956 success
refresh id=127939675040 success
tests id=127939722132 skipped
tests / arch-instrument id=127915328971 success
tests / briefs id=127915081805 success
tests / browser id=127915328961 success
tests / ci-ratchet id=127930435915 skipped
tests / claims-autofix id=127917692714 skipped
tests / closure-scope id=127915081732 success
tests / closures id=127915329104 success
tests / closures-autofix id=127924710345 skipped
tests / coverage id=127915329141 success
tests / coverage-ratchet id=127930432924 success
tests / fast (3.14) id=127915328991 success
tests / graders-head-copy id=127930432966 success
tests / lane-proofs id=127930433009 success
tests / mutation id=127915081842 success
tests / mutation-autofix id=127915421585 skipped
tests / mutation-pins id=127915421015 skipped
tests / nightly-ha id=127915330821 skipped
tests / nightly-status id=127915081798 success
tests / replay id=127915330828 skipped
tests / typing id=127915329183 success
validate id=127939744297 skipped
validate / validate-hacs id=127915081631 success

## Refusals
none

## Advisories
hot-file: HPO_BUS_TRAIN_STATE is unset, so every merge verdict reads unboarded

## carry_audit at the head
NOTE stale tree: 520550cebe311fad3d4f529c5267561ffe7e227c lacks origin/main 33e60b5b71b67610bd02fdea238b882e9a97007b; roster read at origin/main
NOTE body item 33ac5015: dismissed:built in this diff or already in the tree
CARRY-AUDIT: 1 finding item(s): 1 routed, 0 unrouted, 0 bad destination(s)

## figure_lint at the head
ok         bash tools/audit/seat/bus.sh --self-test
             `tools/audit/seat/bus.sh` is in the tree at this head
  ok         python3 tools/audit/seat/review_packet.py --self-test
             `tools/audit/seat/review_packet.py` is in the tree at this head

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
index e63e3c1fd..8608414e5 100644
--- a/dev/audit/harnesses/r10_seat_selftests_mutants.py
+++ b/dev/audit/harnesses/r10_seat_selftests_mutants.py
@@ -229,6 +229,10 @@ MUTANTS = [
     ("bus-7", "bus.sh", '[ -n "$a" ] && [ -z "$(grep -vxF \'dependabot[bot]\' <<< "$a")" ]  # mut:botonly', '[ -n "$a" ]'),
     ("bus-8", "bus.sh", 'if [ -n "$holder" ] && kill -0 "$holder" 2>/dev/null; then  # mut:watchlock', 'if false; then'),
     ("bus-9", "bus.sh", '  rm -f "$b"; [ "$rc" != 1 ]  # mut:landed', '  rm -f "$b"; true'),
+    ("bus-10", "bus.sh", 'if [ "$(git rev-parse "$tip^{tree}" 2>/dev/null)" = "$tree" ]; then  # mut:sametree', 'if false; then'),
+    ("bus-11", "bus.sh", 'if [ -n "$holder" ] && kill -0 "$holder" 2>/dev/null; then  # mut:confirmlock', 'if false; then'),
+    ("bus-12", "bus.sh", '    [ "$v" != merge ] || die "dispatch: #$pr\'s head $h already holds a merge verdict, so no second reviewer is dispatched"  # mut:mergehead', '    true'),
+    ("bus-13", "bus.sh", 'if [ -n "$fixing" ]; then  # mut:autofixhold', 'if false; then'),
     # P43: the pre-flight reads each pull request's destinations with its head as the extra ref
     ("queue_pre_flight-1", "queue_pre_flight.py", "extra_ref=head or None)", "extra_ref=None)"),
     # carry_audit.py check reads no roster for a verdict with no finding item (bus.sh's step grades it:
@@ -319,6 +323,7 @@ MUTANTS = [
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
index bb14786a4..a6f08de7f 100755
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
@@ -505,6 +512,7 @@ three_rounds() { # pr past-three-reason -> 0 to dispatch; else why
 # names it only once `check` reads that head in it. --harness/--harness-file is the finder's.
 # HPO_BUS_PACKER replaces the renderer (the self-test's stub).
 dispatch() { # pr head reviewer [--reviewed-head <sha>] [--nonce N] [--model M] [--past-three <reason>] [--harness P|--harness-file F] -> records, closes, prints the packet and nonce lines
+  local force="" fixing=""
   local pr=${1:-} h=${2:-} r=${3:-} n="" m=- p3="" row why rh="" carry v rc hk="" hv="" pk prc=0 pmsg="" pkline="" cls
   shift 3 2>/dev/null || shift $#
   while [ $# -gt 0 ]; do
@@ -512,6 +520,7 @@ dispatch() { # pr head reviewer [--reviewed-head <sha>] [--nonce N] [--model M]
       --reviewed-head) [[ ${2:-} =~ ^[0-9a-f]{40}$ ]] || die "dispatch: --reviewed-head takes a 40-hex commit"; rh=$2; shift 2 ;;
       --nonce) [[ ${2:-} =~ ^[0-9a-f]{32}$ ]] || die "dispatch: --nonce takes a 32-hex nonce"; n=$2; shift 2 ;;
       --model) [[ ${2:-} =~ ^[A-Za-z0-9._-]+$ ]] || die "dispatch: --model takes one token"; m=$2; shift 2 ;;
+      --force) force=1; shift ;;
       --past-three) [ -n "${2:-}" ] && [ "${2#--}" = "$2" ] || die "dispatch: --past-three needs a reason"; p3=$2; shift 2 ;;
       --harness|--harness-file) [ -n "${2:-}" ] && [ -z "$hk" ] || die "dispatch: $1 takes one path, once"; hk=$1; hv=$2; shift 2 ;;
       *) die "dispatch: unknown argument '$1'" ;;
@@ -590,6 +599,29 @@ dispatch() { # pr head reviewer [--reviewed-head <sha>] [--nonce N] [--model M]
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
+  # overrides with one ledger line. The check-runs are read once; HPO_BUS_CHECKS replaces the read.
+  if [ -z "$n" ]; then
+    fixing=$(${HPO_BUS_CHECKS:-${HPO_BUS_GH:-gh} api "repos/$REPO/commits/$h/check-runs?per_page=100" --jq '.check_runs[] | select(.status != "completed") | .name'} 2>/dev/null \
+             | grep -E '^(mutation|closures|claims)-autofix$' | sort -u | paste -sd, -) || fixing=""
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
@@ -633,6 +665,27 @@ dispatch() { # pr head reviewer [--reviewed-head <sha>] [--nonce N] [--model M]
 }
 
 confirm() { # pr review-commit -> signs the reviewer's proposal onto verdict/<pr>, then posts it
+  local lk holder rc
+  numeric "${1:-}" || die "confirm: the pull request '${1:-}' is not a number"
+  # One confirm per pull request at a time, across the replay pre-check, append_commit and
+  # post_verdict (P354): the lock holds the pid and a dead holder's is taken over (watch.lock).
+  mkdir -p "$S" || die "confirm: cannot create $S"
+  lk=$S/confirm.$1.lock
+  until mkdir "$lk" 2>/dev/null; do
+    holder=$(cat "$lk/pid" 2>/dev/null)
+    if [ -n "$holder" ] && kill -0 "$holder" 2>/dev/null; then  # mut:confirmlock
+      sleep 1
+    else
+      rm -rf "$lk"
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
@@ -861,7 +914,7 @@ self_test() {
   # 7, 9, 12, 21, 22 and 24 (21-24 are the FETCHHEAD/poster arms' pull
   # requests); h2 (a child) inherits them; norow is the base, with none.
   mkdir -p "$W/seat/$ROW_DIR"
-  for n in 7 9 12 21 22 24 31; do
+  for n in 7 9 12 21 22 24 30 31 32; do
     printf -- '- [#%s](https://github.com/o/r/pull/%s) — **open**\n' "$n" "$n" > "$W/seat/$ROW_DIR/$n.md"
   done
   git -C "$W/seat" -c user.name=t -c user.email=t@t add -A
@@ -1184,6 +1237,14 @@ bus-nonce: $N1b" ] && [ "$(grep -c " $N1b " "$W/state/dispatched")" = 2 ] \
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
@@ -1354,6 +1415,19 @@ B
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
@@ -1555,6 +1629,31 @@ B
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
+  printf 'mutation-autofix\nprelude\n' > "$W/checks-in"; printf '#!/bin/bash\ncat "%s/checks-in"\n' "$W" > "$W/checks"
+  nd=$(grep -c . "$W/state/dispatched")
+  out=$(HPO_BUS_CHECKS="bash $W/checks" run dispatch 31 "$h1" cmsg_A); rc=$?
+  [ $rc = 3 ] && echo "$out" | grep -q "HOLD.*mutation-autofix" && [ "$(grep -c . "$W/state/dispatched")" = "$nd" ]
+  expect "a dispatch is held (rc 3, naming the job) while mutation-autofix is queued or running, recording nothing (P344)" $?
+  out=$(HPO_BUS_CHECKS="bash $W/checks" run dispatch 31 "$h1" cmsg_A --force); rc=$?
+  [ $rc = 0 ] && [ -s "$W/state/dispatch-force" ]; expect "--force dispatches over the hold and writes one ledger line (P344)" $?
+  printf 'prelude\n' > "$W/checks-in"
+  out=$(HPO_BUS_CHECKS="bash $W/checks" run dispatch 32 "$h1" cmsg_A); rc=$?
+  [ $rc = 0 ]; expect "null control: no autofix job in flight dispatches (a completed one is never listed) (P344)" $?
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
