# Review packet #3619
head: 419fd6d2c455601cebe473bd1b8ec77e0090daa0
base: 646352ff1364bcbc25875b949072f98e7a53b5fe

Start here (fix-review.md). Re-read the live check state before a verdict: the digest is as read at render.

## Gate digest: green
CodeQL id=132857461135 success
arch-score / arch-score id=132870454434 success
arm id=132857194205 skipped
budget-raise-gate / budget-raise-gate id=132870422958 success
cancel-superseded id=132870423417 success
codeql id=132870423753 skipped
codeql / Analyze (actions) id=132857403708 success
codeql / Analyze (javascript-typescript) id=132857403668 success
codeql / Analyze (python) id=132857403666 success
gate id=132870422826 success
governance id=132870455021 skipped
governance / env-matrix id=132857403720 success
governance / instrument-self-tests id=132857403770 success
governance / policy-docs id=132857403763 success
governance / record id=132857405269 skipped
governance / wave-script id=132857403755 success
hassfest id=132870423743 skipped
hassfest / hassfest id=132857403684 success
kernel-points id=132870453040 skipped
pr-contract id=132870451528 skipped
pr-contract / pr-contract id=132869769200 success
prelude id=132870466220 success
refresh id=132870451953 success
sweep-self id=132870653264 skipped
tests id=132870468388 skipped
tests / arch-instrument id=132857769020 success
tests / briefs id=132857403798 success
tests / browser id=132857769061 success
tests / ci-ratchet id=132869769656 skipped
tests / claims-autofix id=132867964272 skipped
tests / closure-scope id=132857403818 success
tests / closures id=132857769215 success
tests / closures-autofix id=132869769479 skipped
tests / coverage id=132857769047 success
tests / coverage-ratchet id=132866577749 success
tests / fast (3.14) id=132857769067 success
tests / graders-head-copy id=132866577753 success
tests / lane-proofs id=132867962438 success
tests / mutation id=132857403796 success
tests / mutation-autofix id=132857734860 skipped
tests / mutation-pins id=132857734590 skipped
tests / nightly-ha id=132857770792 skipped
tests / nightly-status id=132857403771 success
tests / replay id=132857770928 skipped
tests / typing id=132857769019 success
validate id=132870468569 skipped
validate / validate-hacs id=132857403581 success

## Refusals
none

## Advisories
none

## carry_audit at the head
NOTE body item 73b80ef1: R11-OUTSIDE-CONTRIBUTOR-CYCLE-P3: R11-OUTSIDE-CONTRIBUTOR-CYCLE-P3 resolved on origin/handoff/audit-r10-roster
NOTE body item e457b98a: R11-OUTSIDE-CONTRIBUTOR-CYCLE-P3: R11-OUTSIDE-CONTRIBUTOR-CYCLE-P3 resolved on origin/handoff/audit-r10-roster
CARRY-AUDIT: 2 finding item(s): 2 routed, 0 unrouted, 0 bad destination(s)

## figure_lint at the head
unverified MODE: FULL -- every test script runs, nothing is scoped out.
             no segment of this names a program this check knows
  ok         python3 -I tools/audit/seat/merge_train.py --self-test
             `tools/audit/seat/merge_train.py` is in the tree at this head
  ok         bash tools/audit/seat/merge_pr.sh --self-test
             `tools/audit/seat/merge_pr.sh` is in the tree at this head
  ok         python3 -I tools/pr/outside.py --self-test
             `tools/pr/outside.py` is in the tree at this head
  ok         python3 tools/audit/seat/queue_pre_flight.py --self-test
             `tools/audit/seat/queue_pre_flight.py` is in the tree at this head
  unverified git hash-object
             `git hash-object` resolves; its flags are not checked -- git prints a man page rather than a flag list, and a list carried in this file would rot into false refusals
  ok         python3 -I tools/audit/carry_audit.py --self-test
             `tools/audit/carry_audit.py` is in the tree at this head
  unverified git grep -n "outside\.py" -- '*.sh' '*.py' '*.mjs' '*.yml' '*.js'
             `git grep` resolves; its flags are not checked -- git prints a man page rather than a flag list, and a list carried in this file would rot into false refusals
  ok         python3 -I tools/ci/selftest_scope.py record --step merge-train --step pr-merger --step outside-contract --out <copy of the table>
             `tools/ci/selftest_scope.py` is in the tree at this head
  ok         tools/policy/policy_lint.mjs
             `tools/policy/policy_lint.mjs` is in the tree at this head
  ok         tools/pr/outside.py
             `tools/pr/outside.py` is in the tree at this head
  ok         python3 tests/structure.py
             `tests/structure.py` is in the tree at this head
  ok         python3 tools/audit/archscore/score.py --diff <merge base> HEAD
             `tools/audit/archscore/score.py` is in the tree at this head
  ok         python3 tests/closure.py select --diff $(git merge-base origin/main HEAD)
             `tests/closure.py` is in the tree at this head
  ok         tests/env_drift.py --claims-only <merge base>
             `tests/env_drift.py` is in the tree at this head
  ok         tests/closure.py selftest
             `tests/closure.py` is in the tree at this head

FIGURES: 13 resolved, 3 not verified, 0 refused

## Finder's harness: none named
### at the base
not run
### at the head
not run

## Mutation-ledger diff
none

## Review scope: full (first round: no --reviewed-head)

## Three-dot diff
diff --git a/tools/audit/seat/instruments/merge_pr.sh.md b/tools/audit/seat/instruments/merge_pr.sh.md
index 632fd21a2a..2a48f6df0d 100644
--- a/tools/audit/seat/instruments/merge_pr.sh.md
+++ b/tools/audit/seat/instruments/merge_pr.sh.md
@@ -5,7 +5,15 @@
   `--mandate <comment-id>` and reads that record-issue mandate live; `--ready` marks a
   draft ready. Refusal: a verdict or head mismatch stops the merge before the
   merge API call; a draft without `--ready`, or owner mode with no mandate in
-  force, refuses before anything posts. Before its CI wait it runs
+  force, refuses before anything posts. Both modes read whose head the pull
+  request is by `tools/pr/outside.py`'s `cross_repository` (unread refuses):
+  owner mode refuses a fork head, and app mode merges one only where
+  outside.py's `check` at origin/main admits that exact head, its refusal
+  printed `OUTSIDE CONTRACT REFUSES ...` before anything posts. outside.py
+  runs from origin/main's blob or not at all (the train's rule): it is
+  compared before whose head is read, and every file of the train's
+  `OUTSIDE_MAIN_COPIES` before the contract; a stale copy refuses `OUTSIDE
+  REFUSE: ... is not origin/main's copy`. Before its CI wait it runs
   `merge_train.py unstale` (below) at the head. `--self-test` also drives the whole
   script offline over a scratch clone and a fake `gh`, so the `gh pr merge …
   --match-head-commit` line is pinned: replaced by `exit 0` it records no
diff --git a/tools/audit/seat/instruments/merge_train.py.md b/tools/audit/seat/instruments/merge_train.py.md
index 459663e723..1b7612579d 100644
--- a/tools/audit/seat/instruments/merge_train.py.md
+++ b/tools/audit/seat/instruments/merge_train.py.md
@@ -112,6 +112,15 @@
   critical-path entries, then arrival order; an entry maps to its group by
   branch, else by its pull request (`roster_lib.group_for_pr`), so a fork head
   ranks as its group does.
+  A head that is a fork's (`Train.fork_head`: `tools/pr/outside.py`'s
+  `pull_facts` and `cross_repository`, executed only once the checkout's copy
+  is byte-equal to origin/main's blob) is put to outside.py's whole `check` at
+  the landing head on every base, from origin/main's copies
+  (`Train.outside_contract`): on main before any approval, on a `batch/`
+  rehearsal before the merge, where the contract's base rule refuses it. A
+  refusal, an unread pull request or a stale copy parks the entry
+  `[OUTSIDE]`, naming the fork; its recarry worktree is detached at
+  `refs/remotes/pull/<pr>/head` and `remerge_main.sh --head-repo` moves it.
   `add` and that drain apply one admission rule (`already_held`, over the
   live train's `queue.seen.json`): a pull request still to run, spooled,
   merged or run by this train is `ALREADY` on both sides; one it skipped is
diff --git a/tools/audit/seat/instruments/outside.py.md b/tools/audit/seat/instruments/outside.py.md
index c707578eb6..f19aa7fff2 100644
--- a/tools/audit/seat/instruments/outside.py.md
+++ b/tools/audit/seat/instruments/outside.py.md
@@ -16,7 +16,8 @@
   posts the one mandated class-O approval, through the reviews API with
   `commit_id` the head read, and reads it back. When: `bus.sh adopt` runs
   main's copy as the gate; our class-O read seat returns through `approve`;
-  the merge train reads `check` again at the landing head (part 2). Refusal:
+  the merge train reads `check` again at the landing head on every base, and
+  `merge_pr.sh` app mode before it posts. Refusal:
   any unread fact (the allowlist, CODEOWNERS, the pull request, the review
   list, the mandate) refuses; `approve` refuses, posting nothing, without
   `--mandate`, under a mandate not in force now with scope all, on a head
diff --git a/tools/audit/seat/instruments/remerge_main.sh.md b/tools/audit/seat/instruments/remerge_main.sh.md
index 746e73adcc..f581d491db 100644
--- a/tools/audit/seat/instruments/remerge_main.sh.md
+++ b/tools/audit/seat/instruments/remerge_main.sh.md
@@ -10,3 +10,11 @@
   <pr>` names only a merge that left unmerged paths; a fetch, reset or merge
   that failed otherwise prints `REMERGE FAILED <pr> at <step> (rc=N)` under
   git's own words, which the train stops on as a failure, never a conflict.
+  `--head-repo <owner/repo>` is a head that is not a branch of ours (decision
+  0017; the train passes the head repository the pulls API names): nothing of
+  `origin/<branch>` is read, no claims commit is made, and the head moves only
+  by GitHub's own `update-branch` at the expected head, asked as the
+  hpo-author App, then read back as the automatic two-parent merge of that head
+  and main. A refusal there prints `REMERGE FAILED <pr> at push (fork ...)`,
+  which the train parks `[OUTSIDE]`. No tool of ours pushes a fork's head to a
+  branch of origin: the train fetches it to `refs/remotes/pull/<pr>/head` only.
diff --git a/tools/audit/seat/merge_pr.sh b/tools/audit/seat/merge_pr.sh
index c3f66d4c2f..e7352db86e 100755
--- a/tools/audit/seat/merge_pr.sh
+++ b/tools/audit/seat/merge_pr.sh
@@ -15,7 +15,8 @@
 # 0017): this approval is given after, and on the basis of, the verdict, which
 # on such a head the contributor's reviewer wrote. Whether a head is
 # cross-repository is tools/pr/outside.py's answer over the pulls API object,
-# asked before the mandate is read; unanswered is a refusal.
+# asked before the mandate is read; unanswered is a refusal. app mode on such a
+# head merges only where outside.py's whole contract (`check`) admits this head.
 set -uo pipefail
 R=tvofi/heatpump_optimizer
 # The self-test grades this script's own tree; a merge runs from the main checkout.
@@ -56,6 +57,53 @@ print("OURS")
 P
 }
 
+# outside.py runs from origin/main's blob or not at all, as the train's does
+# (`Train.outside_is_mains`): `outside_is_mains outside` compares outside.py alone,
+# before whose head is read; `outside_is_mains contract` every file of the train's
+# OUTSIDE_MAIN_COPIES, before the contract. Prints `REFUSE: <why>` and returns 1.
+outside_is_mains() { # <outside|contract>
+  local rel want have rels
+  if [ "$1" = outside ]; then rels=tools/pr/outside.py
+  else rels=$(python3 -I - "$PWD/tools/audit/seat/merge_train.py" <<'P'
+import importlib.util, sys
+s = importlib.util.spec_from_file_location("merge_train", sys.argv[1]); m = importlib.util.module_from_spec(s); s.loader.exec_module(m)
+print("\n".join(m.OUTSIDE_MAIN_COPIES))
+P
+) || { echo "REFUSE: the train's OUTSIDE_MAIN_COPIES could not be read"; return 1; }; fi
+  git fetch -q origin main 2>/dev/null || { echo "REFUSE: origin/main could not be fetched for the outside contract"; return 1; }
+  for rel in $rels; do
+    want=$(git rev-parse -q --verify "origin/main:$rel" 2>/dev/null); have=$(git hash-object -- "$rel" 2>/dev/null)
+    [[ "$want" =~ ^[0-9a-f]{40}$ ]] && [ "$want" = "$have" ] || {
+      echo "REFUSE: $rel in this checkout is not origin/main's copy (main ${want:0:12}, here ${have:0:12}): the outside contract is main's or it is not run; run from a checkout at main"; return 1; }
+  done
+}
+
+# outside.py's whole contract for the cross-repository <pr>, at origin/main:
+# prints `ADMITTED: <why>` (rc 0) only when it admits <pr> at <sha>, else
+# `CONTRACT REFUSES ...` or `REFUSE: <why>` (rc 1). No second contract here.
+outside_contract() { # <repo> <pr> <sha>
+  python3 -I - "$1" "$2" "$3" "$OUTSIDE" <<'P'
+import importlib.util, sys
+repo, pr, sha, path = sys.argv[1:5]
+try:
+    spec = importlib.util.spec_from_file_location("outside", path)
+    mod = importlib.util.module_from_spec(spec)
+    spec.loader.exec_module(mod)
+    rc, lines = mod.check(repo, int(pr), "origin/main")
+except Exception as e:  # fail closed: an unread contract admits nothing
+    print(f"REFUSE: {path}'s contract for #{pr} could not be read ({str(e).splitlines()[0][:160] if str(e) else type(e).__name__})")
+    sys.exit(1)
+why = "; ".join(str(ln) for ln in lines)
+if rc == 0 and any(str(ln).startswith("OUTSIDE: ") and f" at {sha}: " in str(ln) for ln in lines):
+    print("ADMITTED: " + why[:400])
+    sys.exit(0)
+if rc == 0:
+    why = f"it admitted a head other than {sha[:12]}: {why}"
+print(f"CONTRACT REFUSES #{pr} at {sha[:12]}: {why[:400]} (decision 0017)")
+sys.exit(1)
+P
+}
+
 # The mandate in force now, by the gate's own reading: prints `IN FORCE: <why>`
 # (rc 0) or `REFUSE: <why>` (rc 1). The gate file is the tree's own.
 mandate_in_force() { # <repo> <comment-id>
@@ -85,7 +133,7 @@ owner_body() { # <sha> <comment-id> <in-force why>
 
 # Every refusal that must come before a post: argv, draft, mandate. Prints the
 # refusal and returns 1, or returns 0; READY_OWED=1 when --ready must mark it.
-gates() { # <pr> <mode> <mandate-id> <ready 0|1>
+gates() { # <pr> <mode> <mandate-id> <ready 0|1> <sha>
   READY_OWED=0
   case "$2" in owner|app) ;; *) echo "USAGE: mode '$2' is neither owner nor app"; return 1 ;; esac
   d=$(gh pr view "$1" --repo $R --json isDraft --jq .isDraft) || { echo "REFUSE: #$1's draft state could not be read"; return 1; }
@@ -93,9 +141,17 @@ gates() { # <pr> <mode> <mandate-id> <ready 0|1>
     [ "$4" = 1 ] || { echo "DRAFT: #$1 is a draft; pass --ready to mark it ready, or ready it first"; return 1; }
     READY_OWED=1
   fi
+  if [ "$2" = owner ] && ! [[ "$3" =~ ^[0-9]{6,}$ ]]; then
+    echo "MANDATE REQUIRED: owner mode needs --mandate <comment-id> naming the mandate in force on a record issue (got '$3')"; return 1
+  fi
+  HEAD_WHY=$(outside_is_mains outside) || { echo "OUTSIDE $HEAD_WHY"; return 1; }
+  if ! HEAD_WHY=$(head_is_ours $R "$1"); then
+    # Only app mode merges a fork head, and only where the contract admits this head.
+    { [ "$2" = app ] && [[ "$HEAD_WHY" == CROSS-REPOSITORY:* ]]; } || { echo "OUTSIDE $HEAD_WHY"; return 1; }
+    CONTRACT_WHY=$(outside_is_mains contract) || { echo "OUTSIDE $CONTRACT_WHY"; return 1; }
+    CONTRACT_WHY=$(outside_contract $R "$1" "$5") || { echo "OUTSIDE $CONTRACT_WHY"; return 1; }
+  fi
   [ "$2" = owner ] || return 0
-  [[ "$3" =~ ^[0-9]{6,}$ ]] || { echo "MANDATE REQUIRED: owner mode needs --mandate <comment-id> naming the mandate in force on a record issue (got '$3')"; return 1; }
-  HEAD_WHY=$(head_is_ours $R "$1") || { echo "OUTSIDE $HEAD_WHY"; return 1; }
   MANDATE_WHY=$(mandate_in_force $R "$3") || { echo "MANDATE $MANDATE_WHY"; return 1; }
   MANDATE_WHY=${MANDATE_WHY#IN FORCE: }
 }
@@ -139,6 +195,19 @@ case "$*" in
 esac
 G
   chmod +x "$T/gh"
+  # A fake git answering the main-copy comparison alone: origin/main's blob of every path is f*40,
+  # and this checkout's copy of $FAKE_STALE is another; every other git call is the real git's.
+  export REAL_GIT; REAL_GIT=$(command -v git)
+  cat > "$T/git" <<'G'
+#!/bin/bash
+case "$*" in
+  "fetch -q origin main") echo "git $*" >> "${FAKE_LOG:-/dev/null}"; exit 0 ;;
+  "rev-parse -q --verify origin/main:"*) printf 'f%.0s' {1..40}; echo; exit 0 ;;
+  "hash-object -- "*) [ "$3" = "${FAKE_STALE:-}" ] && { printf '0%.0s' {1..40}; echo; } || { printf 'f%.0s' {1..40}; echo; }; exit 0 ;;
+esac
+exec "$REAL_GIT" "$@"
+G
+  chmod +x "$T/git"
   # outside.py is part 1's (decision 0017), and the real one is asked: its `pull_facts` reads the pulls object.
   printf '{"number": 7, "head": {"ref": "fix/x", "repo": {"full_name": "%s"}}}' "$R" > "$T/ours.json"
   printf '{"number": 7, "head": {"ref": "fix/x", "repo": {"full_name": "contributor/heatpump_optimizer"}}}' > "$T/theirs.json"
@@ -155,12 +224,12 @@ print(json.dumps({"id": 4100000001, "user": {"login": "tvofi", "id": 70032254, "
                   "body": f"MANDATE: agents may approve as tvofi, scope {sys.argv[3]}, from {c} until {iso(sys.argv[2])}"}))
 P
   }
-  mk -60 60 > "$T/live.json"; mk -120 -10 > "$T/expired.json"
+  mk -60 60 > "$T/live.json"; mk -120 -10 > "$T/expired.json"; S7=$(printf 'c%.0s' {1..40})
   mk -60 60 code-owned > "$T/code-owned.json"; mk -60 60 budget-raise > "$T/raise.json"
   ck() { # <name> <want rc> <want substring> <draft> <mandate file> -- gates args...
     local name=$1 want=$2 sub=$3 draft=$4 mf=$5 rc; shift 6
     : > "$T/log"
-    out=$(PATH="$T:$PATH" FAKE_LOG="$T/log" FAKE_DRAFT=$draft FAKE_MANDATE=$mf gates "$@" 2>&1); rc=$?
+    out=$(PATH="$T:$PATH" FAKE_LOG="$T/log" FAKE_DRAFT=$draft FAKE_MANDATE=$mf gates "$@" "$S7" 2>&1); rc=$?
     if [ "$rc" = "$want" ] && [[ "$out" == *"$sub"* ]]; then pass=$((pass + 1)); echo "  ok   $name"
     else fail=$((fail + 1)); echo "  FAIL $name (rc=$rc: $out)"; fi
   }
@@ -179,15 +248,64 @@ P
   FAKE_PULL=$T/other.json ck "owner mode refuses a pulls object of another pull request: the real outside.py's pull_facts reads it" 1 "is not #7" false "$T/live.json" -- 7 owner 4100000001 0
   FAKE_PULL= ck "owner mode on a pull request that cannot be read refuses: an unread head is never ours" 1 "OUTSIDE REFUSE: #7 could not be read" false "$T/live.json" -- 7 owner 4100000001 0
   OUTSIDE=$T/absent.py ck "owner mode with no outside.py to ask refuses, fail closed" 1 "OUTSIDE REFUSE: $T/absent.py could not say" false "$T/live.json" -- 7 owner 4100000001 0
-  FAKE_PULL=$T/theirs.json ck "null control: app mode on a cross-repository head passes the gates (the App's approval is app_approve.sh's)" 0 "" false "" -- 7 app "" 0
-  if ! grep -q 'pulls/7' "$T/log"; then pass=$((pass + 1)); echo "  ok   ... and app mode asks nothing about the head"
-  else fail=$((fail + 1)); echo "  FAIL ... and app mode asks nothing about the head"; fi
+  # App mode asks outside.py's whole contract on a cross-repository head (r11-outside-contributor-cycle-p3
+  # carry 7): a stub keeps the real pull_facts and cross_repository and answers `check` from FAKE_CHECK
+  # (a head it admits, or a REFUSE line), logging each call.
+  cat > "$T/outside_stub.py" <<'O'
+import importlib.util, os
+_s = importlib.util.spec_from_file_location("real_outside", os.environ["REAL_OUTSIDE"])
+_m = importlib.util.module_from_spec(_s); _s.loader.exec_module(_m)
+pull_facts, cross_repository = _m.pull_facts, _m.cross_repository
+def check(repo, pr, ref, **kw):
+    open(os.environ["FAKE_LOG"], "a").write(f"check {repo} {pr} {ref}\n")
+    at = os.environ.get("FAKE_CHECK", "")
+    if at.startswith("REFUSE"):
+        return 1, [at]
+    return 0, [f"OUTSIDE: #{pr} by contributor (id 1) at {at}: 1 class-F and 0 class-O path(s), none refused"]
+O
+  export REAL_OUTSIDE=$OUTSIDE
+  OUTSIDE=$T/outside_stub.py FAKE_PULL=$T/theirs.json FAKE_CHECK="REFUSE: class R: tools/x.py is a path an outside pull request does not change" \
+    ck "app mode on a cross-repository head the outside contract refuses refuses with outside.py's reason (decision 0017)" 1 "OUTSIDE CONTRACT REFUSES #7 at cccccccccccc: REFUSE: class R: tools/x.py" false "" -- 7 app "" 0
+  if grep -qx 'check tvofi/heatpump_optimizer 7 origin/main' "$T/log"; then pass=$((pass + 1)); echo "  ok   ... having asked the contract at origin/main"
+  else fail=$((fail + 1)); echo "  FAIL ... having asked the contract at origin/main ($(tr '\n' ';' < "$T/log"))"; fi
+  OUTSIDE=$T/outside_stub.py FAKE_PULL=$T/theirs.json FAKE_CHECK=$(printf 'b%.0s' {1..40}) \
+    ck "app mode on a cross-repository head the contract admits at ANOTHER head refuses, naming both" 1 "it admitted a head other than cccccccccccc" false "" -- 7 app "" 0
+  OUTSIDE=$T/outside_stub.py FAKE_PULL=$T/theirs.json FAKE_CHECK=$S7 \
+    ck "app mode on a cross-repository head the contract admits at this head passes the gates" 0 "" false "" -- 7 app "" 0
+  OUTSIDE=$T/outside_stub.py FAKE_PULL=$T/ours.json FAKE_CHECK="REFUSE: never asked" \
+    ck "null control: app mode on a head of ours passes and never asks the contract" 0 "" false "" -- 7 app "" 0
+  if grep -q 'pulls/7' "$T/log" && ! grep -q '^check ' "$T/log"; then pass=$((pass + 1)); echo "  ok   ... having read the pull request and asked no contract"
+  else fail=$((fail + 1)); echo "  FAIL ... having read the pull request and asked no contract ($(tr '\n' ';' < "$T/log"))"; fi
+  FAKE_PULL= ck "app mode on a pull request that cannot be read refuses: an unread head is never ours" 1 "OUTSIDE REFUSE: #7 could not be read" false "" -- 7 app "" 0
+  # outside.py runs from origin/main's blob or not at all, as the train's (`Train.outside_is_mains`,
+  # whose OUTSIDE_MAIN_COPIES this script reads): before whose-head is read, and the whole list
+  # before the contract.
+  for m in app owner; do
+    FAKE_STALE=tools/pr/outside.py ck "$m mode with a checkout whose outside.py is not origin/main's refuses before executing it, on a head of ours" 1 "OUTSIDE REFUSE: tools/pr/outside.py in this checkout is not origin/main's copy" false "$T/live.json" -- 7 $m 4100000001 0
+    if ! grep -q 'pulls/7' "$T/log"; then pass=$((pass + 1)); echo "  ok   ... having read no pull request"
+    else fail=$((fail + 1)); echo "  FAIL ... having read no pull request ($(tr '\n' ';' < "$T/log"))"; fi
+  done
+  OUTSIDE=$T/outside_stub.py FAKE_PULL=$T/theirs.json FAKE_CHECK=$S7 FAKE_STALE=tools/policy/policy_lint.mjs \
+    ck "app mode on a fork head refuses when a file the contract reads is not origin/main's, though the contract would admit" 1 "OUTSIDE REFUSE: tools/policy/policy_lint.mjs in this checkout is not origin/main's copy" false "" -- 7 app "" 0
+  if ! grep -q '^check ' "$T/log"; then pass=$((pass + 1)); echo "  ok   ... having asked no contract"
+  else fail=$((fail + 1)); echo "  FAIL ... having asked no contract ($(tr '\n' ';' < "$T/log"))"; fi
+  FAKE_STALE=tools/policy/policy_lint.mjs ck "null control: a head of ours is read whatever the contract's other files say (only outside.py is compared before the read)" 0 "" false "" -- 7 app "" 0
+  # The stub stands in for exactly the real module's calls: each name this script makes, bound with
+  # the arguments it passes, on the real outside.py (a renamed entry point fails here, not on a merge).
+  if python3 -I - "$REAL_OUTSIDE" <<'P'
+import importlib.util, inspect, sys
+s = importlib.util.spec_from_file_location("outside", sys.argv[1]); m = importlib.util.module_from_spec(s); s.loader.exec_module(m)
+inspect.signature(m.pull_facts).bind("o/r", 7, {}); inspect.signature(m.cross_repository).bind({}, "o/r")
+inspect.signature(m.check).bind("o/r", 7, "origin/main")
+P
+  then pass=$((pass + 1)); echo "  ok   the real outside.py takes every call head_is_ours and outside_contract make, as they make it"
+  else fail=$((fail + 1)); echo "  FAIL the real outside.py takes every call head_is_ours and outside_contract make, as they make it"; fi
   ck "a draft refuses without --ready, naming the flag" 1 "DRAFT: #7 is a draft; pass --ready" true "" -- 7 app "" 0
   ck "a draft with --ready passes the gates" 0 "" true "" -- 7 app "" 1
-  PATH="$T:$PATH" FAKE_LOG="$T/log" FAKE_DRAFT=true gates 7 app "" 1 >/dev/null
+  PATH="$T:$PATH" FAKE_LOG="$T/log" FAKE_DRAFT=true gates 7 app "" 1 "$S7" >/dev/null
   if [ "$READY_OWED" = 1 ]; then pass=$((pass + 1)); echo "  ok   ... and owes the ready mark"
   else fail=$((fail + 1)); echo "  FAIL ... and owes the ready mark"; fi
-  PATH="$T:$PATH" FAKE_LOG="$T/log" FAKE_DRAFT=false gates 7 app "" 1 >/dev/null
+  PATH="$T:$PATH" FAKE_LOG="$T/log" FAKE_DRAFT=false gates 7 app "" 1 "$S7" >/dev/null
   if [ "$READY_OWED" = 0 ]; then pass=$((pass + 1)); echo "  ok   a ready pull request with --ready owes no ready mark"
   else fail=$((fail + 1)); echo "  FAIL a ready pull request with --ready owes no ready mark"; fi
   stale='{"name":"budget-raise-gate","status":"in_progress","conclusion":null,"started_at":"1","id":7,"details_url":"https://github.com/o/r/actions/runs/119308796140/job/5"}'
@@ -238,6 +356,7 @@ P
   # app_comment.sh leaves a mark when it is asked to post; postmerge.py is a stub
   # recording its argv, printing OWED and failing when FAKE_PM_RC says so.
   mkdir -p "$mm/tools/pr"
+  cp "$T/outside_stub.py" "$mm/tools/pr/outside.py"  # the real pull_facts and cross_repository; `check` is FAKE_CHECK's
   # the approver identity posted_verdict reads (proof_watch.verdict_allowlist)
   printf 'VERDICT_AUTHORS="app[bot]"\nVERDICT_AUTHOR_ID=55\n' > "$mm/tools/pr/app_approve.sh"
   printf '#!/bin/bash\necho posted >> "$HPO_STATE_DIR/posted"\n' > "$mm/tools/pr/app_comment.sh"
@@ -251,12 +370,13 @@ sys.exit(rc)
 PM
   printf 'import sys\nprint(sys.argv[2] if len(sys.argv) > 2 else "")\n' \
     > "$mm/tools/audit/seat/ref_privacy.py"
-  printf '#!/bin/bash\nexit 0\n' > "$T/bin2/sleep"; chmod +x "$T/bin2/sleep"
+  printf '#!/bin/bash\nexit 0\n' > "$T/bin2/sleep"; chmod +x "$T/bin2/sleep"; cp "$T/git" "$T/bin2/git"
   cat > "$T/bin2/gh" <<'G'
 #!/bin/bash
 echo "$*" >> "$FAKE_LOG2"
 case "$*" in
   *issues/42/comments*) cat "$FAKE_COMMENTS" 2>/dev/null ;;
+  "api repos/tvofi/heatpump_optimizer/pulls/42") printf '{"number": 42, "head": {"ref": "fix/x", "repo": {"full_name": "%s"}}}' "${FAKE_HEAD_REPO:-tvofi/heatpump_optimizer}" ;;
   *headRefOid*) echo "$FAKE_SHA" ;;
   *isDraft*) echo false ;;
   *mergeStateStatus*) if [ -f "$FAKE_BLOCKED" ]; then rm -f "$FAKE_BLOCKED"; echo BLOCKED; else echo CLEAN; fi ;;
@@ -275,7 +395,7 @@ G
     if [ -n "${2:-}" ]; then printf '# Fix review: merge %s\n' "$2" > "$T/ev/VERDICT.md"
     else printf '# verdict\n' > "$T/ev/VERDICT.md"; fi
     HPO_STATE_DIR=$T/state2 PATH="$T/bin2:$PATH" FAKE_LOG2=$T/gh2.log FAKE_SHA=$msha \
-      FAKE_BLOCKED=$T/blocked FAKE_COMMENTS=$T/comments FAKE_MERGE_FAIL=$1 FAKE_PM_RC=${FAKE_PM_RC:-0} bash "$mm/tools/audit/seat/merge_pr.sh" 42 "$msha" "$T/ev" app \
+      FAKE_LOG=$T/check.log FAKE_BLOCKED=$T/blocked FAKE_COMMENTS=$T/comments FAKE_MERGE_FAIL=$1 FAKE_PM_RC=${FAKE_PM_RC:-0} bash "$mm/tools/audit/seat/merge_pr.sh" 42 "$msha" "$T/ev" app \
       > "$T/flow.out" 2>&1
     echo $? > "$T/flow.rc"
   }
@@ -284,6 +404,15 @@ G
     && grep -qxF "pr merge 42 --merge --match-head-commit $msha" "$T/gh2.log"
   if [ $? = 0 ]; then pass=$((pass + 1)); echo "  ok   null control: the merge records the reviewed head"
   else fail=$((fail + 1)); echo "  FAIL null control: the merge records the reviewed head ($(tail -1 "$T/flow.out"))"; fi
+  FAKE_HEAD_REPO=contributor/heatpump_optimizer FAKE_CHECK="REFUSE: the base is x:y, not tvofi/heatpump_optimizer:main" flow 0
+  [ "$(cat "$T/flow.rc")" != 0 ] && grep -q '^OUTSIDE CONTRACT REFUSES #42' "$T/flow.out" \
+    && [ ! -f "$T/state2/posted" ] && ! grep -q '^pr merge' "$T/gh2.log"
+  if [ $? = 0 ]; then pass=$((pass + 1)); echo "  ok   app mode end to end: a fork head the contract refuses posts nothing and merges nothing"
+  else fail=$((fail + 1)); echo "  FAIL app mode end to end: a fork head the contract refuses posts nothing and merges nothing ($(tail -1 "$T/flow.out"))"; fi
+  FAKE_HEAD_REPO=contributor/heatpump_optimizer FAKE_CHECK=$msha flow 0
+  [ "$(cat "$T/flow.rc")" = 0 ] && grep -qxF "pr merge 42 --merge --match-head-commit $msha" "$T/gh2.log"
+  if [ $? = 0 ]; then pass=$((pass + 1)); echo "  ok   null control: a fork head the contract admits at the head merges"
+  else fail=$((fail + 1)); echo "  FAIL null control: a fork head the contract admits at the head merges ($(tail -1 "$T/flow.out"))"; fi
   flow 1
   [ "$(cat "$T/flow.rc")" != 0 ]
   if [ $? = 0 ]; then pass=$((pass + 1)); echo "  ok   a refused merge fails the script (the line's own exit)"
@@ -368,7 +497,7 @@ done
 # For a queue of verdicted PRs, merge_train.py does the same with recarry and the carry check.
 D=${HPO_STATE_DIR:-$HOME/.local/state/hpo}/merge_pr; mkdir -p "$D/v"
 live=$(gh pr view $PR --json headRefOid --jq .headRefOid); [ "$live" = "$S" ] || { echo "HEAD MOVED: $live"; exit 1; }
-gates "$PR" "$MODE" "$MID" "$READY" || exit 1
+gates "$PR" "$MODE" "$MID" "$READY" "$S" || exit 1
 [ "$READY_OWED" = 1 ] && { gh pr ready $PR --repo $R >/dev/null || { echo "READY REFUSED for #$PR"; exit 1; }; }
 carried_head "$PR" "$S" "$E/VERDICT.md" || exit 1
 sed '1s/^# //' "$E/VERDICT.md" > $D/v/verdict-$PR.md; grep -q "$E" $D/v/verdict-$PR.md || printf '\nEvidence: %s/\n' "$(python3 -I tools/audit/seat/ref_privacy.py path "$E")" >> $D/v/verdict-$PR.md
diff --git a/tools/audit/seat/merge_train.py b/tools/audit/seat/merge_train.py
index 40d01a0013..3d26371855 100644
--- a/tools/audit/seat/merge_train.py
+++ b/tools/audit/seat/merge_train.py
@@ -2667,9 +2667,13 @@ class Train:
         cannot change its head repository. Both names are GitHub's, of the
         contributor's choosing: they travel as argv and log text only, never
         inside a shell string. A pull request, or a fork's name, that cannot be
-        read is a Stop: an unread head is never taken for ours."""
+        read is a Stop: an unread head is never taken for ours. The outside.py
+        executed is origin/main's blob or none (`outside_is_mains`, asked
+        before the read): a checkout's copy answering "ours" would otherwise
+        never reach the contract's own comparison."""
         if pr in self.forks:
             return self.forks[pr]
+        self.outside_is_mains((OUTSIDE_PATH,))  # main's copy is the one executed below, or none is
         code, o = self.run(["gh", "api", f"repos/{self.repo}/pulls/{pr}"])
         try:
             pull = json.loads(o) if code == 0 else None
@@ -2696,16 +2700,17 @@ class Train:
         self.forks[pr] = fork
         return fork
 
-    def outside_is_mains(self) -> None:
+    def outside_is_mains(self, rels: "tuple[str, ...]" = OUTSIDE_MAIN_COPIES) -> None:
         """The outside contract runs from origin/main's copies or not at all
-        (carry 23): origin/main is fetched HERE, and every file of
-        OUTSIDE_MAIN_COPIES in this checkout must be byte-equal to main's blob
-        of that path. Never the head's copy -- nothing of a fork head is
+        (carry 23): origin/main is fetched HERE, and every file of <rels>
+        (OUTSIDE_MAIN_COPIES for the contract, outside.py alone before
+        `fork_head` executes it) in this checkout must be byte-equal to main's
+        blob of that path. Never the head's copy -- nothing of a fork head is
         executed or imported on this machine -- and never a stale seat's."""
         code, o = self.run(["git", "fetch", "-q", "origin", "main"])
         if code:
             raise Stop("outside", "origin/main could not be fetched for the outside contract: " + o.strip()[-160:])
-        for rel in OUTSIDE_MAIN_COPIES:
+        for rel in rels:
             c1, want = self.run(["git", "rev-parse", f"origin/main:{rel}"])
             c2, have = self.run(["git", "hash-object", "--", rel])
             if c1 or c2 or not is_sha(want.strip()) or want.strip() != have.strip():
@@ -3358,6 +3363,11 @@ class Train:
         each attempt when the base is not where the merge expects it; the merge sha."""
         if self.head(pr) != h:
             raise Stop("approve", "head moved")
+        fork = self.fork_head(pr)
+        if fork is not None and not self.real:
+            # A rehearsal merges the head into a branch of ours too: a fork head is put to the
+            # contract on every base (on main, by `approve` below), and its base rule refuses it here.
+            self.outside_contract(pr, h, fork)
         if self.real:
             self.policy_approve(pr, h, item, files)
             under = self.policy_gate(pr, h, files)  # step 5, re-read at the merge itself
@@ -6346,6 +6356,36 @@ def _self_test() -> int:
         check(f"fork head: a pulls object {name} is a Stop saying so -- an unread head is never taken for ours -- "
               "and nothing is approved", isinstance(got, Stop) and got.step == "outside" and said in got.why
               and not asked_app(calls) and not approved(calls))
+    # Carry 8 (r11-outside-contributor-cycle-p3): the checkout's outside.py is compared with
+    # origin/main's blob BEFORE `fork_head` executes it. The decisive case is a head of ours: a
+    # copy that answers "ours" never reaches `outside_contract`'s comparison, so a reader that
+    # ran it first let any checkout's copy say whose head it is.
+    for name, pull in (("of ours", OURS), ("a fork's", THEIRS)):
+        w = {"pull": pull, "gate": OutsideStub(), "stale": OUTSIDE_PATH}
+        got, calls, _ = seat(w, step6)
+        check(f"fork head: a checkout whose {OUTSIDE_PATH} is not origin/main's blob stops before that copy is "
+              f"executed, on a head {name} too, and nothing is approved",
+              parked(got, OUTSIDE_PATH, "not origin/main's copy") and w["gate"].crossed == 0
+              and w["gate"].asked == [] and not asked_app(calls) and not approved(calls))
+    w = {"pull": OURS, "gate": OutsideStub(), "stale": "tools/pr/app_approve.sh"}
+    got, calls, _ = seat(w, lambda t: t.fork_head(7))
+    check("fork head null control: a head of ours read from main's outside.py is ours, whatever another of the "
+          "contract's copies says (only the executed file is compared before the read)",
+          got is None and w["gate"].crossed == 1 and ["git", "fetch", "-q", "origin", "main"] in calls
+          and calls.index(["git", "fetch", "-q", "origin", "main"]) < calls.index(["gh", "api", "repos/o/r/pulls/7"]))
+    # Carry 9: a batch/ rehearsal merges the head into a branch of ours too, so a fork head is put to
+    # the contract on that base as well -- which refuses it, the contract's base being main.
+    land = lambda t: t.land(7, H0, dict(item), FILES, lambda: None)
+    w = {"pull": THEIRS, "gate": OutsideStub((False, "the base is o/r:batch/x, not o/r:main"))}
+    got, calls, _ = seat(w, land, base="batch/x")
+    check("fork head on a batch/ base: the outside contract is asked before the pinned merge, and its refusal "
+          "parks the entry [OUTSIDE] naming the fork, nothing merged",
+          parked(got, "the base is o/r:batch/x", f"{FORK}:{FREF}") and w["gate"].asked == [("o/r", 7, "origin/main")]
+          and not merged(calls) and not asked_app(calls))
+    w = {"pull": OURS, "gate": OutsideStub((False, "never asked"))}
+    got, calls, _ = seat(w, land, base="batch/x")
+    check("null control: a head of ours on a batch/ base is never put to the outside contract and is merged",
+          not isinstance(got, Stop) and w["gate"].asked == [] and merged(calls))
     # THE REAL tools/pr/outside.py (decision 0017, part 1): its own `pull_facts` and `check`, over this
     # tree's policy_lint.mjs, tests/closure.py and mandate gate; only its edges are answered here (the API,
     # git, and `git show` at the ref). A renamed entry point or a changed answer fails HERE, not on the train.
diff --git a/tools/audit/seat/queue_pre_flight.py b/tools/audit/seat/queue_pre_flight.py
index 6d0d4c454d..c92234067d 100644
--- a/tools/audit/seat/queue_pre_flight.py
+++ b/tools/audit/seat/queue_pre_flight.py
@@ -338,6 +338,8 @@ def _self_test() -> int:
                 return 0, world.get("row_text", f"- [#7](https://example.test/7) — **open**, t")
             if "status" in argv and "--porcelain" in argv:  # Train.freeable's reads
                 return 0, world.get("holder_status", "")
+            if argv[:2] == ["git", "hash-object"] or (argv[:2] == ["git", "rev-parse"] and argv[2].startswith("origin/main:")):
+                return 0, "b" * 40  # `Train.outside_is_mains`: this checkout's copy is main's blob
             if argv[:3] == ["git", "-C", "/somewhere/wt"] and "rev-parse" in argv:
                 return 0, "1" * 40
             if argv[:2] == ["git", "rev-parse"]:
diff --git a/tools/ci/selftest_closures.json b/tools/ci/selftest_closures.json
index df8e917843..0c9eb7d07e 100644
--- a/tools/ci/selftest_closures.json
+++ b/tools/ci/selftest_closures.json
@@ -5032,7 +5032,9 @@
     "tools/ci/prelude.py",
     "tools/policy/budget_raise_gate.py",
     "tools/policy/fixtures/required-contexts.json",
+    "tools/policy/policy_lint.mjs",
     "tools/pr/app_approve.sh",
+    "tools/pr/outside.py",
     "tools/release/stamp.py"
    ],
    "probes": [],

## Before you return the verdict (P275)
Run `python3 -I tools/audit/carry_audit.py check --body <PR body file> --comments <file holding [{"id": 0, "body": <verdict.md text>}]>`. Give every reported item its own `Carry: <GROUP> | #<issue> | O<n> | dismissed: <reason>`;
an evidence line flagged by its wording takes `Carry: dismissed: evidence, not a finding`. Return the verdict only at rc 0.
