# Review packet #3325
head: 061a828e18df8ba29a95827fb0e11cd3b7f963b4
base: daf8b349fd30cc60786eeca333a426b693aa4c5f

Start here (fix-review.md). Re-read the live check state before a verdict: the digest is as read at render.

## Gate digest: red
CodeQL id=128875034720 success
arch-score / arch-score id=128874759867 success
arm id=128874357645 skipped
budget-raise-gate / budget-raise-gate id=128874759923 success
cancel-superseded id=128874360912 success
codeql id=128874761267 skipped
codeql / Analyze (actions) id=128874739369 success
codeql / Analyze (javascript-typescript) id=128874739375 success
codeql / Analyze (python) id=128874739469 success
gate id=128879330618 cancelled
governance id=128874761694 skipped
governance / delivery-status id=128874739526 success
governance / delivery-status-publish id=128874741239 skipped
governance / env-matrix id=128874739536 success
governance / instrument-self-tests id=128874739574 failure
governance / policy-docs id=128874739485 success
governance / record id=128874741127 skipped
governance / wave-script id=128874739499 success
hassfest id=128874761151 skipped
hassfest / hassfest id=128874739400 success
kernel-points id=128874761448 skipped
pr-contract id=128879329794 skipped
prelude id=128874360713 success
refresh id=128874360611 success
tests id=128874761558 skipped
tests / arch-instrument id=128875307016 success
tests / briefs id=128874739392 success
tests / browser id=128875307003 success
tests / ci-ratchet id=128879330832 cancelled
tests / claims-autofix id=128877937740 skipped
tests / closure-scope id=128874739493 success
tests / closures id=128875307045 cancelled
tests / closures-autofix id=128879329875 cancelled
tests / coverage id=128875307010 cancelled
tests / coverage-ratchet id=128879277746 cancelled
tests / fast (3.14) id=128875306957 success
tests / graders-head-copy id=128879277641 cancelled
tests / lane-proofs id=128879277788 cancelled
tests / mutation id=128874739432 success
tests / mutation-autofix id=128875340202 skipped
tests / mutation-pins id=128875339900 skipped
tests / nightly-ha id=128875308022 skipped
tests / nightly-status id=128874739515 success
tests / replay id=128875308419 skipped
tests / typing id=128875307025 success
validate id=128874760935 skipped
validate / validate-hacs id=128874739378 success

## Refusals
red-unanswered: concluded red check `tests / ci-ratchet` is not named in ## Red checks
red-unanswered: concluded red check `tests / coverage` is not named in ## Red checks
red-unanswered: concluded red check `tests / coverage-ratchet` is not named in ## Red checks
red-unanswered: concluded red check `tests / graders-head-copy` is not named in ## Red checks
red-unanswered: concluded red check `tests / lane-proofs` is not named in ## Red checks
required-red: required context `gate` concluded failure at 061a828e18df8ba29a95827fb0e11cd3b7f963b4

## Advisories
hot-file: HPO_BUS_TRAIN_STATE is unset, so every merge verdict reads unboarded

## carry_audit at the head
NOTE body item 67cfb27f: dismissed:already carries 5, 6, 7, 9, 10 and 11 of this group, no new finding
NOTE body item b3ad9aa1: dismissed:it is in this diff, nothing to carry
CARRY-AUDIT: 2 finding item(s): 2 routed, 0 unrouted, 0 bad destination(s)

## figure_lint at the head
ok         python3 tools/audit/carry_audit.py --self-test
             `tools/audit/carry_audit.py` is in the tree at this head
  ok         bash tools/audit/seat/body_push.sh --self-test
             `tools/audit/seat/body_push.sh` is in the tree at this head
  ok         bash tools/audit/seat/cloud_relay.sh --self-test
             `tools/audit/seat/cloud_relay.sh` is in the tree at this head
  ok         bash tools/audit/seat/bus.sh --self-test
             `tools/audit/seat/bus.sh` is in the tree at this head
  ok         python3 -I tools/audit/seat/cloud_dispatch.py --self-test
             `tools/audit/seat/cloud_dispatch.py` is in the tree at this head
  ok         python3 -I tools/audit/seat/ledger.py --self-test
             `tools/audit/seat/ledger.py` is in the tree at this head
  ok         python3 tests/structure.py
             `tests/structure.py` is in the tree at this head
  ok         python3 tests/closure.py select --diff daf8b349f
             `tests/closure.py` is in the tree at this head
  ok         tests/doc_claims.py
             `tests/doc_claims.py` is in the tree at this head
  ok         tests/entities.py
             `tests/entities.py` is in the tree at this head
  ok         PYTHONPATH=tests/hastub python3 tests/doc_claims.py
             `tests/doc_claims.py` is in the tree at this head
  ok         PYTHONPATH=tests/hastub python3 tests/entities.py
             `tests/entities.py` is in the tree at this head
  ok         PREPR_SKIP_CLOSURES=1 bash tools/pr/prepr.sh <body>
             `tools/pr/prepr.sh` is in the tree at this head

FIGURES: 13 resolved, 0 not verified, 0 refused

## Finder's harness: none named
### at the base
not run
### at the head
not run

## Mutation-ledger diff
none

## Three-dot diff
diff --git a/dev/governance/roles/standing-tick.md b/dev/governance/roles/standing-tick.md
index a9774c61d..e3daa8ba5 100644
--- a/dev/governance/roles/standing-tick.md
+++ b/dev/governance/roles/standing-tick.md
@@ -1,23 +1,22 @@
 # The tick seat's contract (standing)
 
 One of the four standing seats the orchestrator keeps alive (`orchestrator.md`
-section 5); haiku, low effort. It runs in windows of about 70 min and is
-restarted on this contract by the sweep's standing-seat liveness step.
+section 5); haiku, low effort; windows of about 70 min, restarted on this
+contract by the sweep's liveness step.
 
 **Input:** the orchestrator's queue lines: the window, the standing filters
-(items already routed, held by the owner or waiting on CI, suppressed until
-their state changes) and the board's arguments.
+(routed, held by the owner or waiting on CI, suppressed until their state
+changes) and the board's arguments.
 
-**Instrument:** `tools/audit/seat/orchestrator_tick.py`, every few minutes; it
-only lists, and so do you.
+**Instrument:** `tools/audit/seat/orchestrator_tick.py`, every few minutes; it only lists, as do you.
 
 **Report** only owed or new items, one line each, naming the PR or group, the
 owed action and the board line that shows it. Before any `REVIEW OWED`, apply
 the ancestor-recarry test: a head that moved past its verdict only by merging
 `origin/main`, with `git diff --name-only <verdict> <head>` missing the
-branch's own diff, is a carry for the orchestrator (`orchestrator.md`
-section 11), never a review owed. Touch the session's liveness file every
-pass; end the window with `tick: <n> owed, <m> new, window ends <utc>`.
+branch's own diff, is a carry (`orchestrator.md` section 11), never a review
+owed; the board prints it as the unflagged `CARRY: #<pr> <sha>` line. Touch
+the liveness file every pass; end the window with `tick: <n> owed, <m> new, window ends <utc>`.
 
 **You never** act on the board: no push, merge, dispatch, comment or roster
 edit.
diff --git a/dev/programme/delivery/3325.md b/dev/programme/delivery/3325.md
new file mode 100644
index 000000000..3fcd68d89
--- /dev/null
+++ b/dev/programme/delivery/3325.md
@@ -0,0 +1 @@
+- [#3325](https://github.com/tvofi/heatpump_optimizer/pull/3325) — **open**, R10-CARRY-RESIDUE-2: carry residue 2 (R10-CARRY-RESIDUE-2)
diff --git a/tools/audit/carry_audit.py b/tools/audit/carry_audit.py
index 9d5440640..1327c3219 100644
--- a/tools/audit/carry_audit.py
+++ b/tools/audit/carry_audit.py
@@ -571,12 +571,13 @@ def audit(body: str, comments: list[dict], dests: Dests) -> dict:
 
 
 # ------------------------------------------------------------ the landing
-def group_text(dests: Dests, group: str) -> str:
-    """A group's brief and carries, on main's roster and on the round's branch."""
+def group_text(dests: Dests, group: str, brief: bool = True) -> str:
+    """A group's brief and carries, on main's roster and on the round's branch
+    (`brief=False`: its carries alone)."""
     out = []
     for g in (dests.groups.get(group), dests.round_groups.get(group)):
         if g:
-            out += [str(g.get("brief") or "")] + [str(c) for c in (g.get("carry") or [])]
+            out += ([str(g.get("brief") or "")] if brief else []) + [str(c) for c in (g.get("carry") or [])]
     return "\n".join(out)
 
 
@@ -603,8 +604,9 @@ def own_carry_status(dests: Dests, group: str, text: str) -> bool:
 
 def landed(body: str, dests: Dests, source: str = "", statuses: "list[dict] | None" = None) -> list[dict]:
     """Each (finding item, GROUP destination) of a body whose group's brief or
-    carries hold neither the item id nor the source (`#<pr>` or the handoff
-    topic: P310, an id re-minted by a reword still lands by its source), or
+    carries do not hold the item id and whose carries do not hold the source
+    (`#<pr>` or the handoff topic: P310, an id re-minted by a reword still lands
+    by its source; a brief naming the source lands nothing, #3234), or
     whose group is no valid destination. A `dismissed:` item, a `#N` and an
     O-brief need no landing. Each: {"group", "id", "text", "why"}.
 
@@ -627,9 +629,10 @@ def landed(body: str, dests: Dests, source: str = "", statuses: "list[dict] | No
                 if statuses is not None:
                     statuses.append({"group": tok, "id": r["id"], "text": r["text"]})
                 continue
-            words = set(re.split(r"[^\w#-]+", group_text(dests, tok)))  # whole tokens: #25581 is not #2558
-            keys = [r["id"]] + srcs
-            if not any(k in words for k in keys):  # mut:landed
+            split = lambda t: set(re.split(r"[^\w#-]+", t))  # whole tokens: #25581 is not #2558
+            # the source (`#<pr>`, the topic) lands only through a carry: a group's brief
+            # names the pull requests it was cut from (#3234: --pr hid 7 missing carries)
+            if r["id"] not in split(group_text(dests, tok)) and not any(k in split(group_text(dests, tok, False)) for k in srcs):  # mut:landed
                 out.append({"group": tok, "id": r["id"], "text": r["text"], "why": "not in its brief or carries"})
     return out
 
@@ -1909,6 +1912,12 @@ def _self_test() -> int:
           landed(lb, dl(["From #2558: the census."]), "#2558") == [])
     check("... and another pull request's number does not (null control)",
           len(landed(lb, dl(["From #2558: the census."]), "#25581")) == 1)
+    brief_src = json.loads(json.dumps(Dl_roster))
+    brief_src["groups"][0]["brief"] = "Cut from #2558 (r10-x): the census."
+    check("landed: the source named only in the group's brief does not land it (#3234, before)",
+          len(landed(lb, Dests(brief_src, {300}), "#2558 r10-x")) == 1)
+    check("... and the same source in its carries does (null control)",
+          landed(lb, dl(["From #2558 (r10-x): the census."]), "#2558 r10-x") == [])
     check("landed: a dismissed item and a #N with a carry file need no landing",
           landed(head + "## Forward-carry\n\n- x. Carry: dismissed: no seam remains\n- y. Carry: #300\n", dl()) == [])
     md = landed(head + "## Forward-carry\n\n- x. Carry: R10-DONE\n", dl())
diff --git a/tools/audit/seat/body_push.sh b/tools/audit/seat/body_push.sh
index 40099f3d2..1a2e54df9 100644
--- a/tools/audit/seat/body_push.sh
+++ b/tools/audit/seat/body_push.sh
@@ -42,7 +42,10 @@ if [ "${1:-}" = "--self-test" ]; then
   CODE=$(git -C "$W/repo" rev-parse HEAD)
   for arm in pred lint packet landed; do
     drop; : > "$W/flags/$arm"; run t; rc=$?
-    st "$rc" 1 "REFUSE $arm: exit code unchanged"
+    want=1; [ "$arm" != landed ] || want=4  # CARRY-LANDED alone is exit 4, so the relay can fold it
+    st "$rc" "$want" "REFUSE $arm: exit code ($want)"
+    tok=$(echo "$arm" | tr a-z A-Z); case $arm in pred) tok=PREDICTOR;; lint) tok=BODY-LINT;; packet) tok=REVIEW-PACKET;; landed) tok=CARRY-LANDED;; esac
+    st "$(grep -c "^body_push: REFUSED $tok\$" "$W/out")" 1 "... and the output names the refusal REFUSED $tok"
     k=$(keepsha)
     st "$(git -C "$W/o.git" show "$k:BODY.md" 2>/dev/null)" "the body" "... and the refused body is kept at handoff-wip/t-body"
     st "$(grep -c "^body_push: refused body kept at handoff-wip/t-body $k\$" "$W/out")" 1 "... and the keep line names the ref and sha"
@@ -122,6 +125,7 @@ ROOT=$(git rev-parse --show-toplevel)
 if ! PRED=$(cd "$ROOT" && PYTHONPATH=tests/hastub python3 tools/pr/ci_predict.py --base origin/main 2>&1); then
   printf '%s\n' "$PRED" >&2
   echo "body_push: the predictor refuses this head (above); repair it, push the code, then the body" >&2
+  echo "body_push: REFUSED PREDICTOR" >&2
   keep_refused # mut:keep
   exit 1
 fi
@@ -155,6 +159,7 @@ if [ -n "$HREF" ]; then
   if ! LINT=$(cd "$ROOT" && bash "$HERE/../../pr/prepr.sh" --body-check "$ABS" $PRB 2>&1); then
     printf '%s\n' "$LINT" >&2
     echo "body_push: the pr-body lint refuses this body (above), as open_pr.sh's prepr step 7 would; repair it and push again" >&2
+    echo "body_push: REFUSED BODY-LINT" >&2
     keep_refused # mut:keep
     exit 1
   fi
@@ -168,6 +173,7 @@ if [ -n "$HREF" ]; then
   printf '%s\n' "$PK"
   if [ "$prc" = 1 ]; then
     echo "body_push: the review packet refuses this head at the handoff (above); answer each, push the code, then the body" >&2
+    echo "body_push: REFUSED REVIEW-PACKET" >&2
     keep_refused # mut:keep
     exit 1
   elif [ "$prc" != 0 ]; then
@@ -183,8 +189,11 @@ if [ -n "$HREF" ]; then
   printf '%s\n' "$LD"
   if [ "$lrc" = 1 ]; then  # mut:landed
     echo "body_push: a carry above is not in its group's brief or carries; land it on the round's roster branch (carry_audit.py land-ops), then push the body" >&2
+    # exit 4, not 1: CARRY-LANDED alone, the one refusal a cloud fixer cannot repair (it may not
+    # write the roster). cloud_relay.sh's carry-fold arm keys on this line in the BLOCKED.md.
+    echo "body_push: REFUSED CARRY-LANDED" >&2
     keep_refused # mut:keep
-    exit 1
+    exit 4
   elif [ "$lrc" != 0 ]; then
     echo "body_push: the carry landing was not checked (rc $lrc, above); bus.sh dispatch checks it again" >&2
   fi
diff --git a/tools/audit/seat/bus.sh b/tools/audit/seat/bus.sh
index c6189967d..a5b3a0161 100755
--- a/tools/audit/seat/bus.sh
+++ b/tools/audit/seat/bus.sh
@@ -486,10 +486,10 @@ verdict_log() { # pr -> verdict/<pr>'s commit subjects, newest first (nothing wh
   git log --format=%s "$tip"
 }
 
-blocked_rounds() { # pr -> the count of blocked verdict commits in verdict/<pr>'s history; rc 1 unreadable
+blocked_rounds() { # pr -> the count of distinct heads with a blocked verdict in verdict/<pr>'s history (a re-post at one head is no round); rc 1 unreadable
   local subj
   subj=$(verdict_log "$1") || return 1
-  printf '%s\n' "$subj" | grep -c "^verdict: #$1 Fix review: blocked " || :
+  printf '%s\n' "$subj" | sed -n "s/^verdict: #$1 Fix review: blocked \([0-9a-f]\{7,40\}\)\([ ].*\)\{0,1\}\$/\1/p" | sort -u | grep -c . || :
 }
 
 verdict_at() { # pr sha -> the latest verdict word naming <sha> on verdict/<pr> (merge, blocked), or nothing; rc 1 unreadable
@@ -499,7 +499,8 @@ verdict_at() { # pr sha -> the latest verdict word naming <sha> on verdict/<pr>
 }
 
 # THE THREE-ROUND RULE (fixer.md, "Past three rounds"). Each round's verdict stays in
-# verdict/<pr>'s history, so its blocked commits are the rounds already reviewed. After three,
+# verdict/<pr>'s history, so its distinct blocked heads are the rounds already reviewed
+# (#3247: five re-posts at one head were one round). After three,
 # a dispatch needs the body's `## Re-cut` note (read only then, through $HPO_BUS_GH) or
 # `--past-three <reason>`, logged in $S/past-three; after a fourth -- a re-cut blocked again --
 # only `--past-three`: the split-or-close is the orchestrator's, never a silent re-dispatch.
@@ -969,7 +970,7 @@ self_test() {
   # 7, 9, 12, 21, 22 and 24 (21-24 are the FETCHHEAD/poster arms' pull
   # requests); h2 (a child) inherits them; norow is the base, with none.
   mkdir -p "$W/seat/$ROW_DIR"
-  for n in 7 9 12 21 22 24 30 31 32 33 34; do
+  for n in 7 9 12 21 22 24 30 31 32 33 34 35; do
     printf -- '- [#%s](https://github.com/o/r/pull/%s) — **open**\n' "$n" "$n" > "$W/seat/$ROW_DIR/$n.md"
   done
   git -C "$W/seat" -c user.name=t -c user.email=t@t add -A
@@ -1858,7 +1859,7 @@ B
   # THE THREE-ROUND RULE (fixer.md, "Past three rounds"): verdict/<pr>'s history keeps every
   # round, so the blocked commits on it are the rounds a dispatch would follow.
   blk() { git -C "$W/seat" commit-tree "$(git -C "$W/seat" rev-parse "$h1^{tree}")" ${2:+-p "$2"} \
-            -m "verdict: #31 Fix review: blocked $h1 harness: round $1"; }
+            -m "verdict: #${3:-31} Fix review: blocked ${4:-$(printf '%040d' "$1")} harness: round $1"; }
   printf '#!/bin/bash\nprintf "%%s|" "$@" >> "%s/gh-argv"; echo >> "%s/gh-argv"; cat "%s/body31"\n' "$W" "$W" "$W" > "$W/ghstub"
   printf '## Summary\nround four, repaired\n' > "$W/body31"
   f1=$(blk 1); f2=$(blk 2 "$f1"); git -C "$W/seat" push -q origin "$f2:refs/heads/verdict/31"
@@ -1885,6 +1886,16 @@ B
   expect "a re-cut body blocked again is refused for the orchestrator's split-or-close" $?
   out=$(run dispatch 31 "$h1" cmsg_T --past-three); rc=$?
   [ $rc != 0 ] && echo "$out" | grep -q "past-three needs a reason"; expect "--past-three without a reason is refused" $?
+  # #3247: five re-posts of one verdict at one head are one review round
+  rp=$(blk 1 "" 32 "$h1"); for i in 2 3 4 5; do rp=$(blk $i "$rp" 32 "$h1"); done
+  git -C "$W/seat" push -q origin "$rp:refs/heads/verdict/32"
+  out=$(run dispatch 32 "$h1" cmsg_T); rc=$?
+  [ $rc = 0 ] && echo "$out" | grep -q '^bus-nonce: '; expect "five re-posts at one head count as one round and dispatch (#3247)" $?
+  rp=$(blk 1 "" 35 "$(printf '%040d' 1)"); rp=$(blk 2 "$rp" 35 "$(printf '%040d' 2)")
+  rp=$(blk 3 "$rp" 35 "$(printf "%040d" 3)"); git -C "$W/seat" push -q origin "$rp:refs/heads/verdict/35"
+  printf "## Summary\nno note\n" > "$W/body31"
+  out=$(run dispatch 35 "$h1" cmsg_T); rc=$?
+  [ $rc != 0 ] && echo "$out" | grep -q "3 blocked round(s).*## Re-cut"; expect "null control: three distinct blocked heads are three rounds and refuse without a note" $?
 
   # THE REVIEW PACKET: dispatch names the packet rendered at its head and passes the
   # finder's harness through; a REFUSED head records nothing; a seat that cannot render
diff --git a/tools/audit/seat/cloud_dispatch.py b/tools/audit/seat/cloud_dispatch.py
index 6e8a6939d..ec2cc6b48 100644
--- a/tools/audit/seat/cloud_dispatch.py
+++ b/tools/audit/seat/cloud_dispatch.py
@@ -268,7 +268,10 @@ def _prompt(role: str, repo: str, pr: str, head: str, topic: str, nonce: str, br
             f"refs/heads/handoff/{topic}, then write the PR body and run "
             f"`bash tools/audit/seat/body_push.sh {topic} <body.md>`, which pushes "
             f"refs/heads/handoff-body/{topic}; that second push is the return signal. Once it succeeds, "
-            f"delete the step ref: `git push origin :refs/heads/{WIP_NS}/{topic}`. Push nothing "
+            f"delete the step ref: `git push origin :refs/heads/{WIP_NS}/{topic}`. When body_push.sh "
+            f"exits 4 (its output ends `body_push: REFUSED CARRY-LANDED`), the carry lands on the roster "
+            f"you may not write: push a BLOCKED.md holding that output to refs/heads/{WIP_NS}/{topic} and stop; "
+            "the relay folds the carries and re-runs body_push.sh. Push nothing "
             "else, open no pull request and write no delivery row. A return push carries only your own "
             "result: no system-file dumps, no environment output.")
     elif role == "designer":
@@ -841,7 +844,9 @@ def _group_checks(check) -> None:
         check("_publish itself refuses a ref that would publish the host, and pushes nothing",
               not published and "someone" not in git(work, "ls-remote", str(origin)))
         # A step push matches no glob the handoff machinery lists, read from its own source.
-        globs = (re.findall(r"'(refs/heads/handoff[^'*]*\*)'", (HERE / "cloud_relay.sh").read_text())
+        # (carry_fold_arm lists handoff-wip/* on purpose, to read a BLOCKED.md; it moves no PR, so it is not a handoff glob)
+        globs = ([g for g in re.findall(r"'(refs/heads/handoff[^'*]*\*)'", (HERE / "cloud_relay.sh").read_text())
+                  if not g.startswith(f"refs/heads/{WIP_NS}/")]
                  + re.findall(r'"\+(refs/heads/handoff[^:"*]*\*):', (HERE / "bus.sh").read_text()))
         git(work, "push", "-q", str(origin), f"{tip}:refs/heads/{WIP_NS}/r10-x", f"{tip}:refs/heads/handoff/r10-x")
         listed = git(work, "ls-remote", str(origin), *globs)
diff --git a/tools/audit/seat/cloud_relay.sh b/tools/audit/seat/cloud_relay.sh
index f55b4c35a..671c3b694 100644
--- a/tools/audit/seat/cloud_relay.sh
+++ b/tools/audit/seat/cloud_relay.sh
@@ -708,6 +708,53 @@ noreturn_arm() {
   rm -f "$state/cloud-nr.$$" "$state/cloud-nrr.$$"
 }
 
+carry_fold_arm() { # one pass over handoff-wip/<topic> refs whose BLOCKED.md names CARRY-LANDED alone: fold the kept body's carries, re-run body_push.sh
+  # A cloud fixer may not write the roster, so body_push.sh's CARRY-LANDED refusal (exit 4; each refusal prints
+  # `body_push: REFUSED <KIND>` into the BLOCKED.md the fixer pushes) stranded it until a seat landed the carries
+  # by hand (4 times on 2026-11-06, twice more on 11-07). The refusal is folded only when it is the ONLY kind the
+  # BLOCKED.md names and the refused body is kept on handoff-wip/<topic>-body; any other BLOCKED.md prints a tick
+  # line and folds nothing. carry_fold.py is the designated roster writer; HPO_RELAY_FOLD / HPO_RELAY_BODYPUSH replace the two steps.
+  local state=${HPO_STATE_DIR:-$HOME/.local/state/hpo} sha ref topic bw bsha kinds wt body why rc
+  git ls-remote origin 'refs/heads/handoff-wip/*' > "$state/cloud-wip.$$" \
+    || { echo "cloud_relay: could not list handoff-wip refs; the carry-fold level stays as it was" >&2; rm -f "$state/cloud-wip.$$"; return 0; }
+  mkdir -p "$state"; : > "$state/cloud-level-fold.$$"
+  while read -r sha ref; do
+    topic=${ref#refs/heads/handoff-wip/}
+    case $topic in ''|*/*|*-body|*-carries|*-body-*) continue;; esac
+    git fetch -q origin "$ref" 2>/dev/null && bw=$(git show "$sha:BLOCKED.md" 2>/dev/null) || continue
+    kinds=$(printf '%s\n' "$bw" | sed -n 's/^body_push: REFUSED \([A-Z-]*\)[[:space:]]*$/\1/p' | sort -u | tr '\n' ' ')
+    bsha=$(awk -v r="refs/heads/handoff-wip/$topic-body" '$2 == r { print $1; exit }' "$state/cloud-wip.$$")
+    if [ -f "$state/cloud-folded" ] && grep -qxF "$topic $bsha" "$state/cloud-folded"; then continue; fi
+    if [ "$kinds" != "CARRY-LANDED " ] || [ -z "$bsha" ]; then  # mut:foldonly
+      why="BLOCKED.md names ${kinds:-no refusal line}${bsha:+; }${bsha:-and no kept body}: not CARRY-LANDED alone, nothing folded"
+      echo "cloud_relay: OWED carry-fold $topic ${sha:0:12} $why"
+      level_line carry-fold "$ref" "$sha" "$why" >> "$state/cloud-level-fold.$$"; continue
+    fi
+    body=$state/cloud-fold-$topic.md
+    git fetch -q origin "refs/heads/handoff-wip/$topic-body" 2>/dev/null && git show "$bsha:BODY.md" > "$body" 2>/dev/null \
+      || { echo "cloud_relay: no BODY.md at handoff-wip/$topic-body; nothing folded" >&2; continue; }
+    rc=0; why=$(${HPO_RELAY_FOLD:-python3 -I "$HERE/carry_fold.py"} --body "$body" --topic "$topic" --worktree "$state/cloud-fold-wt" 2>&1) || rc=$?
+    if [ $rc != 0 ]; then
+      why=$(last_line "$why"); echo "cloud_relay: OWED carry-fold $topic ${sha:0:12} carry_fold rc=$rc: $why"
+      level_line carry-fold "$ref" "$sha" "carry_fold rc=$rc: $why" >> "$state/cloud-level-fold.$$"; continue
+    fi
+    if [ -n "${HPO_RELAY_BODYPUSH:-}" ]; then "$HPO_RELAY_BODYPUSH" "$topic" "$body" > "$state/cloud-fold.out" 2>&1; rc=$?
+    else
+      wt=$state/cloud-fold-code; rm -rf "$wt"; git worktree prune
+      git fetch -q origin "refs/heads/handoff/$topic" 2>/dev/null && git worktree add -q --detach "$wt" FETCH_HEAD 2>/dev/null \
+        || { echo "cloud_relay: OWED carry-fold $topic ${sha:0:12} no handoff/$topic to push the body from"; continue; }
+      (cd "$wt" && bash "$HERE/body_push.sh" "$topic" "$body") > "$state/cloud-fold.out" 2>&1; rc=$?
+      git worktree remove --force "$wt" 2>/dev/null
+    fi
+    if [ $rc = 0 ]; then echo "$topic $bsha" >> "$state/cloud-folded"; echo "cloud_relay: FOLDED $topic: carries landed, body_push.sh pushed handoff-body/$topic"
+    else
+      why=$(last_line "$(cat "$state/cloud-fold.out")"); echo "cloud_relay: OWED carry-fold $topic ${sha:0:12} body_push rc=$rc after the fold: $why"
+      level_line carry-fold "$ref" "$sha" "body_push rc=$rc: $why" >> "$state/cloud-level-fold.$$"
+    fi
+  done < "$state/cloud-wip.$$"
+  level_set carry-fold "$state/cloud-level-fold.$$"; rm -f "$state/cloud-wip.$$"
+}
+
 pass() { # [--confirm] [--log FILE] [--loop [--interval N]]
   local every=120 loop=""
   while [ $# -gt 0 ]; do case $1 in
@@ -716,7 +763,7 @@ pass() { # [--confirm] [--log FILE] [--loop [--interval N]]
   case $every in ''|*[!0-9]*|0) echo "cloud_relay: --interval must be a positive number of seconds" >&2; return 2;; esac
   while :; do
     echo "cloud_relay: state dir ${HPO_STATE_DIR:-$HOME/.local/state/hpo}, ledger ${HPO_STATE_DIR:-$HOME/.local/state/hpo}/cloud-relayed, log $(relay_log)"
-    handoff_arm; probe_arm; [ -z "${CONFIRM:-}" ] || confirm_arm; stuck_arm; noreturn_arm; [ -z "$loop" ] && return 0; sleep "$every"; done
+    handoff_arm; carry_fold_arm; probe_arm; [ -z "${CONFIRM:-}" ] || confirm_arm; stuck_arm; noreturn_arm; [ -z "$loop" ] && return 0; sleep "$every"; done
 }
 
 self_test() {
@@ -1594,6 +1641,37 @@ open(sys.argv[1], "w").close(); time.sleep(60)' "$t/stuck.held" "$t/state/pr/upd
   LOG=$t/nr2.log; : > "$LOG"; nrc dispatch/fixer-nr-p 10800
   nro=$(handoff_arm() { :; }; probe_arm() { :; }; CONFIRM= pass 2>&1)
   chk "a pass runs the no-return arm" 0 grep -q "SEAT ENDED NO RETURN nr-p " <<< "$nro"
+  # THE CARRY-FOLD ARM (R10-CARRY-RESIDUE-2 carry 14): a BLOCKED.md naming CARRY-LANDED alone, with its body kept on
+  # handoff-wip/<topic>-body, is folded (carry_fold.py) and re-pushed (body_push.sh); any other block prints a line and folds nothing.
+  throwaway_git_init "$t/cf.git" -q --bare; throwaway_git_init "$t/cfw" -q; cd "$t/cfw" || exit 1
+  git remote add origin "$t/cf.git"; LOG=$t/cf.log; : > "$LOG"; rm -rf "$t/state/cloud-folded"
+  cfref() { # cfref <ref> <file> <content>: a one-file orphan commit at <ref> on the origin
+    rm -rf "$t/cfx"; throwaway_git_init "$t/cfx" -q; printf '%s\n' "$3" > "$t/cfx/$2"; git -C "$t/cfx" add -A; git -C "$t/cfx" commit -qm x
+    git -C "$t/cf.git" fetch -qf "$t/cfx" "HEAD:refs/heads/$1"; }
+  printf '#!/bin/bash\necho "$@" >> %s/folds\n' "$t" > "$t/foldstub"; printf '#!/bin/bash\necho "$@" >> %s/bps\n' "$t" > "$t/bpstub"
+  chmod +x "$t/foldstub" "$t/bpstub"; export HPO_RELAY_FOLD=$t/foldstub HPO_RELAY_BODYPUSH=$t/bpstub
+  cfref handoff-wip/cf-a BLOCKED.md "$(printf 'the carries\nbody_push: REFUSED CARRY-LANDED')"; cfref handoff-wip/cf-a-body BODY.md "the body A"
+  cfo=$(carry_fold_arm 2>&1)
+  chk "a CARRY-LANDED-only block is folded by carry_fold.py on the kept body" 0 grep -q -- "--topic cf-a " "$t/folds"
+  chk "... and body_push.sh re-runs on the same body" 0 grep -q "^cf-a .*cloud-fold-cf-a.md" "$t/bps"
+  chk "... and the arm says FOLDED" 0 grep -q "FOLDED cf-a" <<< "$cfo"
+  rm -f "$t/folds" "$t/bps"; carry_fold_arm >/dev/null 2>&1
+  chk "a folded body is not folded twice (same topic and body sha)" 1 test -e "$t/folds"
+  cfref handoff-wip/cf-b BLOCKED.md "$(printf 'body_push: REFUSED CARRY-LANDED\nbody_push: REFUSED BODY-LINT')"; cfref handoff-wip/cf-b-body BODY.md "the body B"
+  rm -f "$t/folds" "$t/bps"; cfo=$(carry_fold_arm 2>&1)
+  chk "null control: CARRY-LANDED plus another refusal folds nothing" 1 test -e "$t/folds"
+  chk "... runs no body_push.sh" 1 test -e "$t/bps"
+  chk "... and prints its tick line naming both kinds" 0 grep -q "OWED carry-fold cf-b .*BODY-LINT CARRY-LANDED" <<< "$cfo"
+  chk "... which is on the level" 0 grep -q "carry-fold .*cf-b" "$LOG.level"
+  cfref handoff-wip/cf-c BLOCKED.md "the fixer is stuck on a design question"; cfref handoff-wip/cf-c-body BODY.md "the body C"
+  rm -f "$t/folds"; cfo=$(carry_fold_arm 2>&1)
+  chk "a block with no refusal line folds nothing and prints its line" 0 grep -q "OWED carry-fold cf-c .*no refusal line" <<< "$cfo"
+  chk "... and ran no fold" 1 test -e "$t/folds"
+  printf '#!/bin/bash\nexit 1\n' > "$t/foldstub"; cfref handoff-wip/cf-d BLOCKED.md "body_push: REFUSED CARRY-LANDED"; cfref handoff-wip/cf-d-body BODY.md "the body D"
+  rm -f "$t/bps"; cfo=$(carry_fold_arm 2>&1)
+  chk "a fold that fails (rc 1) re-runs no body_push.sh and stays owed" 0 grep -q "OWED carry-fold cf-d .*carry_fold rc=1" <<< "$cfo"
+  chk "... with no body_push" 1 test -e "$t/bps"
+  unset HPO_RELAY_FOLD HPO_RELAY_BODYPUSH; cd "$t/w" || exit 1
   cd / && rm -rf "$t"
   echo "cloud_relay self-test: $((ok+bad)) checks, $bad failed"; [ "$bad" = 0 ]
 }
diff --git a/tools/audit/seat/roster_edit.py b/tools/audit/seat/roster_edit.py
index df8cccd8e..dae345398 100644
--- a/tools/audit/seat/roster_edit.py
+++ b/tools/audit/seat/roster_edit.py
@@ -1516,8 +1516,11 @@ def _self_test() -> int:
         cannot tell this op's refusal from argparse refusing the op itself,
         or one refusal from another that happens to fire first."""
         err = io.StringIO()
-        with contextlib.redirect_stderr(err):
-            rc = sysrc(lambda: edit(*args, **kw))
+        try:
+            with contextlib.redirect_stderr(err):
+                rc = sysrc(lambda: edit(*args, **kw))
+        except Exception:  # a crash is no refusal: a FAIL line, not a traceback that ends the run (C6)
+            return False
         return rc not in (0, None) and why in err.getvalue()
 
     def refusal(*args, **kw):
@@ -1753,7 +1756,7 @@ def _self_test() -> int:
           and edit("drop-carry", "R9-B", None, match="no proposal") == 0
           and edit("drop-carry", "R9-B", None, match="lettered proposal") == 0
           and edit("drop-carry", "R9-B", None, match="P-value") == 0
-          and branch_roster()["groups"][1]["carry"] == [])
+          and branch_roster()["groups"][1].get("carry") == [])  # .get: a dropped key is a FAIL line, never a KeyError crash (C6)
 
     # set-resume: the resume free-text fields a session restarts from, through
     # the same load/modify/dump flow -- never a string splice.
diff --git a/tools/pr/prepr.sh b/tools/pr/prepr.sh
index 5c0c03930..7342eda56 100755
--- a/tools/pr/prepr.sh
+++ b/tools/pr/prepr.sh
@@ -3084,12 +3084,12 @@ https://claude.ai/code/session_011aqzm4YL9jLhU4jLvbkLYE'; got=$(lpush)
   grep -q 'were not run (rc 3' <<<"$got" && grep -q '^rc=0$' <<<"$got" \
     && [ "$(git --git-dir="$PDX/bodies.git" rev-parse refs/heads/handoff-body/zz-lint)" != "$was" ]
   st $? 0 "and pushes, saying so, when the handoff refusals cannot be run (rc 3 is never a refusal)"
-  # CARRY 11: body_push runs carry_audit.py landed after the packet; rc 1 pushes nothing, rc 3 pushes.
+  # CARRY 11: body_push runs carry_audit.py landed after the packet; rc 1 pushes nothing and body_push exits 4 (CARRY-LANDED alone, the relay folds it), rc 3 pushes.
   printf '#!/bin/bash\necho "CARRY-MISSING R10-X body item 0123abcd: not in its brief or carries"; exit %s\n' 1 > "$PDX/ld1"
   printf '#!/bin/bash\necho "carry_audit: UNREAD the roster"; exit %s\n' 3 > "$PDX/ld3"
   was=$(git --git-dir="$PDX/bodies.git" rev-parse refs/heads/handoff-body/zz-lint)
   got=$(HPO_HANDOFF_LANDED="bash $PDX/ld1" lpush)
-  grep -q '^CARRY-MISSING R10-X body item 0123abcd' <<<"$got" && grep -q '^rc=1$' <<<"$got" \
+  grep -q '^CARRY-MISSING R10-X body item 0123abcd' <<<"$got" && grep -q '^rc=4$' <<<"$got" \
     && [ "$(git --git-dir="$PDX/bodies.git" rev-parse refs/heads/handoff-body/zz-lint)" = "$was" ]
   st $? 0 "and refuses a body whose carry its group does not hold, naming it and pushing nothing (CARRY 11)"
   got=$(HPO_HANDOFF_LANDED="bash $PDX/ld3" lpush)

## Before you return the verdict (P275)
Run `python3 -I tools/audit/carry_audit.py check --body <PR body file> --comments <file holding [{"id": 0, "body": <verdict.md text>}]>`. Give every reported item its own `Carry: <GROUP> | #<issue> | O<n> | dismissed: <reason>`;
an evidence line flagged by its wording takes `Carry: dismissed: evidence, not a finding`. Return the verdict only at rc 0.
