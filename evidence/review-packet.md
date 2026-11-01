# Review packet #3073
head: 828b6e8ce5b5b646d0c291ee3998b8e284e26f4b
base: e4c9e2016a455d787d3a7604ef88c803c3ba5c70

Start here (fix-review.md). Re-read the live check state before a verdict: the digest is as read at render.

## Gate digest: pending
CodeQL id=124892541121 neutral
arch-score / arch-score id=124892383875 success
arm id=124892256434 skipped
budget-raise-gate / budget-raise-gate id=124892383915 success
cancel-superseded id=124892259131 success
codeql / Analyze (actions) id=124892383726 success
codeql / Analyze (javascript-typescript) id=124892383704 success
codeql / Analyze (python) id=124892383680 in_progress
governance / delivery-status id=124892383904 success
governance / delivery-status-publish id=124892384954 skipped
governance / env-matrix id=124892383909 in_progress
governance / instrument-self-tests id=124892383708 in_progress
governance / policy-docs id=124892383658 success
governance / record id=124892385140 skipped
governance / wave-script id=124892383692 success
hassfest / hassfest id=124892383733 success
kernel-points id=124892384700 skipped
prelude id=124892258852 in_progress
refresh id=124892259155 success
tests / arch-instrument id=124892483790 success
tests / briefs id=124892383693 success
tests / browser id=124892483792 in_progress
tests / closure-scope id=124892383787 success
tests / closures id=124892483765 in_progress
tests / coverage id=124892483728 in_progress
tests / fast (3.14) id=124892483808 in_progress
tests / mutation id=124892383770 success
tests / mutation-autofix id=124892588024 skipped
tests / mutation-pins id=124892587619 skipped
tests / nightly-ha id=124892485199 skipped
tests / nightly-status id=124892383758 success
tests / replay id=124892485226 skipped
tests / typing id=124892483828 success
validate / validate-hacs id=124892383683 success

## Refusals
none

## Advisories
hot-file: HPO_BUS_TRAIN_STATE is unset, so every merge verdict reads unboarded

## carry_audit at the head
CARRY-AUDIT: 0 finding item(s): 0 routed, 0 unrouted, 0 bad destination(s)

## figure_lint at the head
ok         python3 -I tools/audit/seat/review_packet.py --self-test
             `tools/audit/seat/review_packet.py` is in the tree at this head
  ok         python3 tools/audit/seat/merge_train.py --self-test
             `tools/audit/seat/merge_train.py` is in the tree at this head
  ok         python3 -I tools/audit/seat/orchestrator_tick.py --self-test
             `tools/audit/seat/orchestrator_tick.py` is in the tree at this head
  ok         bash tools/audit/seat/bus.sh --self-test
             `tools/audit/seat/bus.sh` is in the tree at this head
  ok         python3 dev/audit/harnesses/r10_fly_raise_reviewable_overfire.py <checkout>
             `dev/audit/harnesses/r10_fly_raise_reviewable_overfire.py` is in the tree at this head
  ok         python3 tests/closure.py select --diff $(git merge-base origin/main HEAD) --workdir "$D"
             `tests/closure.py` is in the tree at this head
  ok         tests/entities.py
             `tests/entities.py` is in the tree at this head
  ok         node tools/policy/policy_lint.mjs --budgets
             `tools/policy/policy_lint.mjs` is in the tree at this head
  unverified git grep -nE "approval_owed|classify .*--pr|merge_train.py.? classify" -- tools/audit/seat/*.py tools/audit/seat/*.sh
             `git grep` resolves; its flags are not checked -- git prints a man page rather than a flag list, and a list carried in this file would rot into false refusals
  ok         python3 tools/audit/archscore/score.py --diff 8fec54ee2afb HEAD
             `tools/audit/archscore/score.py` is in the tree at this head
  ok         python3 tools/audit/seat/orchestrator_tick.py --self-test
             `tools/audit/seat/orchestrator_tick.py` is in the tree at this head
  ok         python3 tools/audit/seat/cloud_dispatch.py --self-test
             `tools/audit/seat/cloud_dispatch.py` is in the tree at this head
  ok         python3 -I tools/audit/seat/review_carry.py --self-test
             `tools/audit/seat/review_carry.py` is in the tree at this head
  ok         tests/doc_claims.py
             `tests/doc_claims.py` is in the tree at this head
  unverified git grep -nE "review_carry(\.py)?|--carry\b" -- 'tools/**/*.py' 'tools/**/*.sh'
             `git grep` resolves; its flags are not checked -- git prints a man page rather than a flag list, and a list carried in this file would rot into false refusals
  ok         tools/pr/app_approve.sh --carry
             `tools/pr/app_approve.sh` is in the tree at this head
  ok         bash dev/audit/harnesses/r10_fly_raise_reviewable_carry.sh <checkout> <pr> <rh>
             `dev/audit/harnesses/r10_fly_raise_reviewable_carry.sh` is in the tree at this head
  ok         node tools/policy/policy_lint.mjs
             `tools/policy/policy_lint.mjs` is in the tree at this head
  ok         node tools/policy/rules_sync.mjs --check
             `tools/policy/rules_sync.mjs` is in the tree at this head
  ok         python3 tools/audit/archscore/score.py --diff 2b6bef7453a8 HEAD
             `tools/audit/archscore/score.py` is in the tree at this head
  ok         python3 tools/audit/seat/merge_train.py classify 9ef51b8215dd7216950f177386fb2f5a8f010a47 --repo tvofi/heatpump_optimizer
             `tools/audit/seat/merge_train.py` is in the tree at this head
  ok         python3 dev/audit/harnesses/r10_fly_raise_reviewable.py <checkout> classify <sha> --repo tvofi/heatpump_optimizer [--pr N]
             `dev/audit/harnesses/r10_fly_raise_reviewable.py` is in the tree at this head
  ok         tests/structure.py
             `tests/structure.py` is in the tree at this head
  unverified git grep -nE "classify\(|merge_train.py\"?\}? classify|merge_train.py classify|& set\(REQUIRED\)|req_red|req_bad" -- 'tools/audit/seat/*.py' 'tools/audit/seat/*.sh'
             `git grep` resolves; its flags are not checked -- git prints a man page rather than a flag list, and a list carried in this file would rot into false refusals

FIGURES: 21 resolved, 3 not verified, 0 refused

## Finder's harness: none named
### at the base
not run
### at the head
not run

## Mutation-ledger diff
none

## Three-dot diff
diff --git a/dev/audit/harnesses/r10_fly_raise_reviewable.py b/dev/audit/harnesses/r10_fly_raise_reviewable.py
new file mode 100644
index 000000000..95ccc75f0
--- /dev/null
+++ b/dev/audit/harnesses/r10_fly_raise_reviewable.py
@@ -0,0 +1,39 @@
+#!/usr/bin/env python3
+"""R10-FLY-RAISE-REVIEWABLE (P345): the real-head control for `classify --pr`.
+
+Runs <checkout>/tools/audit/seat/merge_train.py's `classify` CLI against live
+GitHub with one TRANSPORT shim and nothing else changed: a proxy that refuses
+`gh api --paginate`'s numeric-id follow-up links (a cloud seat's) is answered
+by reading `gh api --paginate --slurp P` as the single page `gh api P`, wrapped
+in a list; every read the classifier makes for one pull request is < 100 items.
+Without the shim such a seat's raise_hold Stops and approval_owed fails closed
+(RED, rc 1), which is the designed answer to an unread mandate thread.
+
+    python3 dev/audit/harnesses/r10_fly_raise_reviewable.py <checkout> classify <sha> --repo R [--pr N]
+
+Point <checkout> at a merge-base worktree (no `--pr` there) and at the head.
+Control: #3045 at 9ef51b82, RED rc 1 at the base, APPROVAL-OWED rc 4 at the head.
+Null: #3055 at 6a988a23, RED rc 1 at both ends.
+"""
+import importlib.util
+import json
+import sys
+
+root = sys.argv[1]
+spec = importlib.util.spec_from_file_location("mt", f"{root}/tools/audit/seat/merge_train.py")
+mt = importlib.util.module_from_spec(spec)
+spec.loader.exec_module(mt)
+orig = mt.Train._run
+
+
+def run(argv, cwd=mt.ROOT, stdin=None):
+    if argv[:4] == ["gh", "api", "--paginate", "--slurp"]:
+        code, o = orig(["gh", "api", *argv[4:]], cwd=cwd, stdin=stdin)
+        return (code, json.dumps([json.loads(o)])) if code == 0 else (code, o)
+    return orig(argv, cwd=cwd, stdin=stdin)
+
+
+mt.Train._run = staticmethod(run)
+rc = mt.main(sys.argv[2:])
+print(f"rc={rc}")
+sys.exit(0)
diff --git a/dev/audit/harnesses/r10_fly_raise_reviewable_carry.sh b/dev/audit/harnesses/r10_fly_raise_reviewable_carry.sh
new file mode 100755
index 000000000..d18d307c3
--- /dev/null
+++ b/dev/audit/harnesses/r10_fly_raise_reviewable_carry.sh
@@ -0,0 +1,31 @@
+#!/bin/bash
+# R10-FLY-RAISE-REVIEWABLE (P348): the real-ref control for `bus.sh dispatch`'s
+# review-carry refusal. Runs <checkout>/tools/audit/seat/bus.sh dispatch at
+# <head> with --reviewed-head <reviewed>, against the live verdict/<pr> ref on
+# origin, from the current checkout (which must have both shas). Only the
+# classifier and the packet renderer are stubbed (GREEN, a packet naming the
+# head); state, ledger and the past-three log go to a temporary directory, so a
+# minted nonce is never recorded anywhere a seat reads and nothing is posted.
+# --past-three is passed so a PR past three rounds reaches the carry test.
+#
+#   bash dev/audit/harnesses/r10_fly_raise_reviewable_carry.sh <checkout> <pr> <reviewed> [<head>]
+#
+# Prints `carry: MINTS rc=0` or `carry: REFUSED rc=N <reason>`.
+# Control: #3045, 9ef51b82 -> 9ef51b82 (latest verdict blocked): REFUSED (CARRY)
+# at the base, MINTS at the head. Null: #2962, 9ce0179f -> 9ce0179f (latest
+# verdict merge): REFUSED (CARRY) at both ends.
+set -u
+co=$1 pr=$2 rh=$3 h=${4:-$3}
+T=$(mktemp -d) || exit 2
+trap 'rm -rf "$T"' EXIT
+printf 'echo "GREEN $2 pending: none red: none"\n' > "$T/classifier"
+cat > "$T/packer" <<'P'
+while [ $# -gt 0 ]; do case $1 in --head) h=$2; shift 2 ;; --out) o=$2; shift 2 ;; *) shift ;; esac; done
+mkdir -p "$(dirname "$o")" && printf '# Review packet\nhead: %s\n' "$h" > "$o"
+P
+out=$(HPO_BUS_STATE=$T/state HPO_BUS_LEDGER=$T/ledger/cloud-relay.log HPO_BUS_CLASSIFY="bash $T/classifier" \
+      HPO_BUS_PACKER="bash $T/packer" bash "$co/tools/audit/seat/bus.sh" dispatch "$pr" "$h" harness-probe \
+      --reviewed-head "$rh" --past-three "harness probe, scratch state" 2>&1); rc=$?
+printf '%s\n' "$out" | grep -E '^bus: (review-carry|REFUSE)' | sed 's/^/  /'
+if [ $rc = 0 ]; then echo "carry: MINTS rc=0"
+else echo "carry: REFUSED rc=$rc $(printf '%s\n' "$out" | grep -o 'review_carry: CARRY\|cannot read[^,]*' | head -n 1)"; fi
diff --git a/dev/audit/harnesses/r10_fly_raise_reviewable_overfire.py b/dev/audit/harnesses/r10_fly_raise_reviewable_overfire.py
new file mode 100644
index 000000000..fd4eadb0a
--- /dev/null
+++ b/dev/audit/harnesses/r10_fly_raise_reviewable_overfire.py
@@ -0,0 +1,112 @@
+#!/usr/bin/env python3
+"""R10-FLY-RAISE-REVIEWABLE (#3073 round 1, class-open): approval_owed over-fire census.
+
+Drives <checkout>/tools/audit/seat/merge_train.py's `classify --pr 3045` CLI over
+#3045's shape (gate and budget-raise-gate failed, one unheld raise, the owner's
+approval on an older head) plus one extra unit per case, with every read stubbed
+the way the self-test's `owed_cli` stubs it. The fix reviewer's probe
+(verdict/3073 evidence/overfire.py) planted the same runs; this companion also
+answers the gate job's log with the reasons gate.py prints for that shape
+(tools/ci/gate.py `gate()`: a non-success unit, ABSENT, PENDING), so a checkout
+that reads why `gate` is red is measured on the same input as one that does not.
+
+    python3 dev/audit/harnesses/r10_fly_raise_reviewable_overfire.py <checkout>
+
+Prints one `RESULT <case>: rc=<n> <STATE>` line per case. Expected at a checkout
+that reads the gate's reasons: the control and the two designed owed shapes
+(an older approval; a red that is no gate unit) rc=4, every other case rc=1.
+"""
+import contextlib
+import datetime
+import io
+import json
+import sys
+
+sys.path.insert(0, sys.argv[1] + "/tools/audit/seat")
+import merge_train as mt  # noqa: E402
+
+_g, owner_rv, mandate_c, _rv = mt.policy_fixture_builders()
+OLD, BASE = "d" * 40, "e" * 40
+now = datetime.datetime.now(datetime.timezone.utc)
+G, R = mt.GATE, mt.RAISE_GATE
+OWN = f"{R}: failure (this run)"
+
+
+def cr(name, status="completed", conclusion="success"):
+    return {"name": name, "status": status, "started_at": "1", "id": 1, "details_url": "",
+            "conclusion": conclusion if status == "completed" else None}
+
+
+def glog(reasons):
+    ts = "2026-10-31T21:40:02.5110117Z "
+    lines = ['##[group]Run python3 -I tools/ci/gate.py --pr "$PR" --base "$BASE" --kind "$KIND"', "##[endgroup]",
+             *(("FAIL " if i == 0 else "") + r for i, r in enumerate(reasons)),
+             "##[error]Process completed with exit code 1."]
+    return "".join(ts + x + "\n" for x in lines)
+
+
+def run(runs, files, why, budgets=mt.RAISE_FIXTURE, reviews=None, body="## Summary\n", flags=("--pr", "3045")):
+    def fake_run(argv, cwd=mt.ROOT, stdin=None):
+        a = " ".join(argv)
+        if "/actions/jobs/" in a and a.endswith("/logs"):
+            return 0, glog(why)
+        if "check-runs" in a:
+            return 0, "\n".join(json.dumps(c) for c in runs)
+        if a.endswith("rulesets --jq " + argv[-1]):
+            return 0, "7"
+        if "rulesets/7" in a:
+            return 0, "gate\n"
+        if argv[:2] == ["git", "merge-base"]:
+            return 0, BASE + "\n"
+        if argv[:4] == ["git", "diff", "--no-renames", "--name-only"]:
+            return 0, "".join(f + "\n" for f in files)
+        got = mt.budget_fixture(budgets, argv, BASE)
+        if got is not None:
+            return got
+        if "/reviews" in a:
+            return 0, json.dumps([reviews if reviews is not None else [owner_rv(OLD, now)]])
+        if argv[:3] == ["gh", "pr", "view"]:
+            return 0, body
+        if "issues/comments/" in a:
+            return 0, json.dumps(mandate_c(now))
+        if "/comments" in a:
+            return 0, json.dumps([[]])
+        return 1, "unexpected " + a
+    saved, buf = mt.Train._run, io.StringIO()
+    mt.Train._run = staticmethod(fake_run)
+    try:
+        with contextlib.redirect_stdout(buf):
+            rc = mt.main(["classify", "a" * 40, *flags])
+    finally:
+        mt.Train._run = saved
+    return rc, (buf.getvalue().split() or ["?"])[0]
+
+
+base = [cr(G, conclusion="failure"), cr(R, conclusion="failure"), cr("tests / fast (3.14)"),
+        cr("pr-contract / pr-contract")]
+F = ["tests/structure_budgets.json", "tools/x.py"]
+cases = [
+    ("control #3045 shape", base, F, [OWN], {}),
+    ("null: red head not a raise (no budget file)", base, ["tools/x.py"], [OWN], {"budgets": None}),
+    ("null: raise + tests/fast red", base[:2] + [cr("tests / fast (3.14)", conclusion="failure")], F,
+     [OWN, "tests / fast (3.14): failure (this run)"], {}),
+    ("null: raise + tests/fast cancelled", base[:2] + [cr("tests / fast (3.14)", conclusion="cancelled")], F,
+     [OWN, "tests / fast (3.14): cancelled (this run)"], {}),
+    ("null: approval at the head (held)", base, F, [OWN], {"reviews": [owner_rv("a" * 40, now)], "body": mt.JUSTIFIED_BODY}),
+    ("designed owed: approval at an older head", base, F, [OWN], {}),
+    ("null: gate red, raise unit green", [base[0], cr(R), *base[2:]], F, ["pr-contract / pr-contract: failure (run 7)"], {}),
+    ("designed owed: a non-gate red (governance / instrument-self-tests) + raise",
+     base + [cr("governance / instrument-self-tests", conclusion="failure")], F, [OWN], {}),
+    ("hidden: gate red because tests / browser SKIPPED", base + [cr("tests / browser", conclusion="skipped")], F,
+     [OWN, "tests / browser: SKIPPED (this run)"], {}),
+    ("hidden: gate red because a unit is ABSENT", base, F, [OWN, "tests / arch-instrument: ABSENT (this run)"], {}),
+    ("hidden: gate red because a unit is still in_progress", base + [cr("tests / browser", "in_progress")], F,
+     [OWN, "tests / browser: PENDING (this run)"], {}),
+    ("hidden: gate red for a reason naming no unit (deferral)", base, F,
+     ["run(s) [99] at this head are still being judged past the bound"], {}),
+]
+for label, runs, files, why, kw in cases:
+    rc, state = run(runs, files, why, **kw)
+    print(f"RESULT {label}: rc={rc} {state}")
+rc, state = run(base, F, [OWN], flags=())
+print(f"RESULT no --pr: rc={rc} {state}")
diff --git a/dev/governance/roles/orchestrator.md b/dev/governance/roles/orchestrator.md
index 00cc225d6..2f17230b2 100644
--- a/dev/governance/roles/orchestrator.md
+++ b/dev/governance/roles/orchestrator.md
@@ -168,8 +168,8 @@ head SHA, invisible to a liveness check for its worktree or marker. A
 head moving under an in-flight review costs it; a code-carrying move re-issuing
 the verdict needs a fresh `bus.sh dispatch` before the reviewer publishes, since
 `push-verdict` refuses a nonce minted at another head.
-Dispatching a second reviewer over a range clean against the reviewed head
-(`--reviewed-head`) is the error, not diligence (tvofi, 2026-10-27);
+Dispatching a second reviewer over a range clean against a reviewed head whose
+verdict was merge (`--reviewed-head`) is the error, not diligence (tvofi, 2026-10-27);
 `review_carry.py`'s `CARRY` refuses it. **A conflict after the handoff is
 resolved by merge, never a re-cut**: merge `origin/main` in, or hand a
 semantic one to the fixer; the resolution delta goes to that reviewer.
diff --git a/dev/programme/delivery/3073.md b/dev/programme/delivery/3073.md
new file mode 100644
index 000000000..367a3f868
--- /dev/null
+++ b/dev/programme/delivery/3073.md
@@ -0,0 +1 @@
+- [#3073](https://github.com/tvofi/heatpump_optimizer/pull/3073) — **open**, R10-FLY-RAISE-REVIEWABLE: a budget-raise PR is reviewable before its approval; review-carry refuses only a merge verdict (R10-FLY-RAISE-REVIEWABLE)
diff --git a/tests/closures.json b/tests/closures.json
index 361b84499..1d96d3284 100644
--- a/tests/closures.json
+++ b/tests/closures.json
@@ -3942,6 +3942,9 @@
    "dev/audit/harnesses/r10_flow_dispatch_mutants.py",
    "dev/audit/harnesses/r10_fly_nightly_hb.py",
    "dev/audit/harnesses/r10_fly_orphans_landed.sh",
+   "dev/audit/harnesses/r10_fly_raise_reviewable.py",
+   "dev/audit/harnesses/r10_fly_raise_reviewable_carry.sh",
+   "dev/audit/harnesses/r10_fly_raise_reviewable_overfire.py",
    "dev/audit/harnesses/r10_ftol_cell_search.py",
    "dev/audit/harnesses/r10_gate_defer_race.py",
    "dev/audit/harnesses/r10_gate_priority_base.py",
diff --git a/tools/audit/seat/bus.sh b/tools/audit/seat/bus.sh
index 3338eaffb..75fe9de6b 100755
--- a/tools/audit/seat/bus.sh
+++ b/tools/audit/seat/bus.sh
@@ -38,8 +38,9 @@
 # that can keep the row from landing late. `dispatch` also REFUSES TO MINT a
 # nonce for a head whose `review_carry.py <reviewed-head> <head>` answers
 # CARRY -- no branch-authored commit since the head the caller names with
-# --reviewed-head (tvofi, 2026-10-27: "if there are no code changes, the
-# previous review can be carried"). The refusal is what makes the ruling
+# --reviewed-head and whose latest verdict at that head on verdict/<pr> is
+# merge (tvofi, 2026-10-27: "if there are no code changes, the previous review
+# can be carried"; a blocked one carries nothing, P348). The refusal is what makes the ruling
 # mechanical rather than a judgement a seat can talk itself out of; a
 # `--nonce` re-record mints nothing and is left alone.
 # `orphans` is the handoff family's level-triggered obligation, which `watch`
@@ -393,16 +394,27 @@ train_add() { # pr first-line -> one `BUS train-add <pr> rc=<rc> <add's last lin
   printf 'BUS train-add %s rc=%s %s\n' "$1" "$rc" "$(tail -n 1 "$log")"
 }
 
-blocked_rounds() { # pr -> the count of blocked verdict commits in verdict/<pr>'s history; rc 1 unreadable
-  local tip subj
+verdict_log() { # pr -> verdict/<pr>'s commit subjects, newest first (nothing when no ref); rc 1 unreadable
+  local tip
   tip=$(git ls-remote "$REMOTE" "refs/heads/verdict/$1") || return 1
   tip=${tip%%[[:space:]]*}
-  [ -n "$tip" ] || { echo 0; return 0; }
+  [ -n "$tip" ] || return 0
   git fetch -q "$REMOTE" "refs/heads/verdict/$1" 2>/dev/null && git cat-file -e "$tip^{commit}" 2>/dev/null || return 1
-  subj=$(git log --format=%s "$tip") || return 1
+  git log --format=%s "$tip"
+}
+
+blocked_rounds() { # pr -> the count of blocked verdict commits in verdict/<pr>'s history; rc 1 unreadable
+  local subj
+  subj=$(verdict_log "$1") || return 1
   printf '%s\n' "$subj" | grep -c "^verdict: #$1 Fix review: blocked " || :
 }
 
+verdict_at() { # pr sha -> the latest verdict word naming <sha> on verdict/<pr> (merge, blocked), or nothing; rc 1 unreadable
+  local subj
+  subj=$(verdict_log "$1") || return 1
+  printf '%s\n' "$subj" | sed -n "s/^verdict: #$1 Fix review: \([a-z]*\) $2\( .*\)\{0,1\}\$/\1/p" | head -n 1
+}
+
 # THE THREE-ROUND RULE (fixer.md, "Past three rounds"). Each round's verdict stays in
 # verdict/<pr>'s history, so its blocked commits are the rounds already reviewed. After three,
 # a dispatch needs the body's `## Re-cut` note (read only then, through $HPO_BUS_GH) or
@@ -431,7 +443,7 @@ three_rounds() { # pr past-three-reason -> 0 to dispatch; else why
 # names it only once `check` reads that head in it. --harness/--harness-file is the finder's.
 # HPO_BUS_PACKER replaces the renderer (the self-test's stub).
 dispatch() { # pr head reviewer [--reviewed-head <sha>] [--nonce N] [--model M] [--past-three <reason>] [--harness P|--harness-file F] -> records, closes, prints the packet and nonce lines
-  local pr=${1:-} h=${2:-} r=${3:-} n="" m=- p3="" row why rh="" carry rc hk="" hv="" pk prc=0 pmsg="" pkline="" cls
+  local pr=${1:-} h=${2:-} r=${3:-} n="" m=- p3="" row why rh="" carry v rc hk="" hv="" pk prc=0 pmsg="" pkline="" cls
   shift 3 2>/dev/null || shift $#
   while [ $# -gt 0 ]; do
     case $1 in
@@ -464,11 +476,14 @@ dispatch() { # pr head reviewer [--reviewed-head <sha>] [--nonce N] [--model M]
   # reviewable. merge_train.py's `classify`, the one owner of that state, answers
   # RED (rc 1) and the dispatch refuses, naming the contexts; GREEN (0) and WAIT
   # (3, a run still in flight) dispatch. Unreadable (2: the ruleset or the check
-  # runs) refuses too, never read as green. HPO_BUS_CLASSIFY replaces the
-  # command (the self-tests' stub).
-  cls=$(${HPO_BUS_CLASSIFY:-python3 "$ROOT/tools/audit/seat/merge_train.py"} classify "$h" --repo "$REPO" 2>&1); rc=$?
+  # runs) refuses too, never read as green. APPROVAL-OWED (4, with --pr: the red is
+  # only budget-raise-gate over a raise whose owner approval follows this review,
+  # merge_train.approval_owed; P345) dispatches and prints its line. HPO_BUS_CLASSIFY
+  # replaces the command (the self-tests' stub).
+  cls=$(${HPO_BUS_CLASSIFY:-python3 "$ROOT/tools/audit/seat/merge_train.py"} classify "$h" --repo "$REPO" --pr "$pr" 2>&1); rc=$?
   case $rc in
     0|3) ;;
+    4) printf 'bus: %s\n' "$(printf '%s\n' "$cls" | grep '^APPROVAL-OWED ' | tail -n 1)" >&2 ;;
     1) die "dispatch: #$pr's head $h is not reviewable: a required context's latest run there concluded failure ($(printf '%s\n' "$cls" | sed -n 's/^RED .* red: //p')) -- repair the head, then dispatch" ;;
     *) die "dispatch: cannot classify #$pr's head $h, so no reviewer is dispatched (an unread head is never green): $(printf '%s\n' "$cls" | grep -v '^[[:space:]]*$' | tail -n 1)" ;;
   esac
@@ -479,6 +494,10 @@ dispatch() { # pr head reviewer [--reviewed-head <sha>] [--nonce N] [--model M]
   # commit range and app_approve.sh --carry's predicate, so the seat cannot
   # judge; this refusal is a refusal, not a warning, because a warning is what
   # let the second reviewer start.
+  # Only a MERGE verdict carries (P348): a clean range refuses only when the
+  # latest verdict naming <rh> on verdict/<pr> (verdict_at) is merge. A blocked
+  # review, or none, leaves nothing to carry, so it mints and says so; an
+  # unreadable verdict ref refuses, never read as either.
   # --nonce mints nothing (a relay-minted nonce re-recorded for the seat
   # fired with it), so it is left alone.
   if [ -n "$rh" ] && [ -z "$n" ]; then
@@ -488,7 +507,12 @@ dispatch() { # pr head reviewer [--reviewed-head <sha>] [--nonce N] [--model M]
     if [ "$rc" = 2 ]; then
       die "dispatch: cannot read the range $rh..$h: ${carry#review_carry: CANNOT DECIDE: }"
     elif [ "$rc" = 0 ]; then
-      die "dispatch: #$pr's head $h carries no branch-authored commit since the reviewed head $rh (review_carry: CARRY) -- the prior review carries, so no second reviewer is dispatched (tvofi, 2026-10-27)"
+      v=$(verdict_at "$pr" "$rh") || die "dispatch: cannot read verdict/$pr to learn what the review at $rh decided, so the clean range $rh..$h is not carried blind"
+      case $v in
+        merge) die "dispatch: #$pr's head $h carries no branch-authored commit since the reviewed head $rh (review_carry: CARRY) -- the prior review carries, so no second reviewer is dispatched (tvofi, 2026-10-27)" ;;
+        "") printf 'bus: review-carry: %s has no verdict, so a fresh review is owed\n' "$rh" >&2 ;;
+        *) printf 'bus: review-carry: %s was %s, so a fresh review is owed\n' "$rh" "$v" >&2 ;;
+      esac
     fi
   fi
   why=$(three_rounds "$pr" "$p3") || die "dispatch: $why"
@@ -790,6 +814,7 @@ case ${BUS_CLASSIFY_RC:-0} in
   0) echo "GREEN $2 pending: none red: none" ;;
   1) echo "RED $2 pending: none red: tests / fast gate" ;;
   3) echo "WAIT $2 pending: gate red: none" ;;
+  4) echo "APPROVAL-OWED $2 1 budget raise(s), first tests/structure_budgets.json: m: 3 -> 4: a raise is the owner's (0013): planted" ;;
   *) echo "REFUSE proof: could not read main-protect-checks's required contexts; no proof is judged against a guessed list" ;;
 esac
 exit "${BUS_CLASSIFY_RC:-0}"
@@ -927,6 +952,12 @@ bus-nonce: $N1b" ] && [ "$(grep -c " $N1b " "$W/state/dispatched")" = 2 ] \
   git -C "$W/seat" -c user.name=t -c user.email=t@t merge -q --no-ff \
     -m "Merge remote-tracking branch 'origin/main' into carry" "$mainadv"
   hm=$(git -C "$W/seat" rev-parse HEAD)
+  # P348: only a MERGE verdict carries. verdict/31's latest verdict naming the
+  # reviewed head decides; vc pushes one more verdict commit on top.
+  vc() { local t p; p=$(git -C "$W/seat" ls-remote origin refs/heads/verdict/31 | cut -f1)
+         t=$(git -C "$W/seat" commit-tree "$(git -C "$W/seat" rev-parse "$h1^{tree}")" ${p:+-p "$p"} \
+               -m "verdict: #31 Fix review: $1 $2${3:+ $3}") && git -C "$W/seat" push -q origin "$t:refs/heads/verdict/31"; }
+  vc merge "$h1"
   out=$(seat dispatch 31 "$hm" cmsg_C1 --reviewed-head "$h1"); rc=$?
   [ $rc != 0 ] && echo "$out" | grep -q "review_carry: CARRY" \
     && echo "$out" | grep -q "reviewed head $h1" \
@@ -934,7 +965,28 @@ bus-nonce: $N1b" ] && [ "$(grep -c " $N1b " "$W/state/dispatched")" = 2 ] \
     && [ "$(grep -c "^31 " "$W/state/dispatched")" = 0 ] \
     && ! python3 -I "$ROOT/tools/audit/seat/ledger.py" --log "$W/ledger/cloud-relay.log" board 2>/dev/null \
          | grep -q "reviewer-fire 31 "
-  expect "dispatch refuses to mint a nonce over a clean range, naming the reviewed head, and records nothing" $?
+  expect "null control (P348): a merge verdict at the reviewed head over a clean range refuses to mint, naming the reviewed head, and records nothing" $?
+  vc blocked "$h1" "metric-gamed: planted"
+  out=$(seat dispatch 31 "$hm" cmsg_C3 --reviewed-head "$h1"); rc=$?
+  [ $rc = 0 ] && echo "$out" | grep -q '^bus-nonce: ' \
+    && echo "$out" | grep -qF "review-carry: $h1 was blocked, so a fresh review is owed" \
+    && [ "$(grep -c "^31 $hm cmsg_C3 " "$W/state/dispatched")" = 1 ]
+  expect "P348: a blocked verdict at the reviewed head over a clean range mints, says why, and records (#3045 r3)" $?
+  vc merge "$h1"; vc blocked "$h2" "harness: another head"; n=$(grep -c . "$W/state/dispatched")
+  out=$(seat dispatch 31 "$hm" cmsg_C4 --reviewed-head "$h1"); rc=$?
+  [ $rc != 0 ] && echo "$out" | grep -q "review_carry: CARRY" && [ "$(grep -c . "$W/state/dispatched")" = "$n" ]
+  expect "P348: the latest verdict naming the reviewed head decides -- blocked then merge refuses, a blocked verdict at another head aside (#2962)" $?
+  git -C "$W/seat" push -q origin :refs/heads/verdict/31
+  out=$(seat dispatch 31 "$hm" cmsg_C5 --reviewed-head "$h1"); rc=$?
+  [ $rc = 0 ] && echo "$out" | grep -qF "review-carry: $h1 has no verdict, so a fresh review is owed" \
+    && [ "$(grep -c "^31 $hm cmsg_C5 " "$W/state/dispatched")" = 1 ]
+  expect "P348: a reviewed head with no verdict at all carries nothing, so it mints" $?
+  n=$(grep -c . "$W/state/dispatched")
+  out=$(HPO_BUS_REMOTE=$W/missing.git seat dispatch 31 "$hm" cmsg_C6 --reviewed-head "$h1"); rc=$?
+  [ $rc != 0 ] && echo "$out" | grep -qF "cannot read verdict/31 to learn what the review at $h1 decided" \
+    && ! echo "$out" | grep -q '^bus-nonce: ' \
+    && [ "$(grep -c . "$W/state/dispatched")" = "$n" ]
+  expect "P348: an unreadable verdict/<pr> over a clean range refuses, and records nothing" $?
   out=$(seat dispatch 31 "$h2" cmsg_C2 --reviewed-head "$h1"); rc=$?
   [ $rc = 0 ] && echo "$out" | grep -q '^bus-nonce: ' \
     && [ "$(grep -c "^31 $h2 " "$W/state/dispatched")" = 1 ]
@@ -1441,7 +1493,7 @@ B
   n=$(grep -c . "$W/state/dispatched")
   out=$(BUS_CLASSIFY_RC=1 run dispatch 7 "$h1" cmsg_K); rc=$?
   [ $rc != 0 ] && echo "$out" | grep -q "is not reviewable: .*(tests / fast gate)" \
-    && [ "$(grep -c . "$W/state/dispatched")" = "$n" ] && tail -n 1 "$W/classifies" | grep -qx "classify|$h1|--repo|o/r|"
+    && [ "$(grep -c . "$W/state/dispatched")" = "$n" ] && tail -n 1 "$W/classifies" | grep -qx "classify|$h1|--repo|o/r|--pr|7|"
   expect "a head whose required context concluded failure (classify RED) is not dispatched, and nothing is recorded" $?
   out=$(BUS_CLASSIFY_RC=0 run dispatch 7 "$h1" cmsg_K); rc=$?
   [ $rc = 0 ] && echo "$out" | grep -q '^bus-nonce: ' && [ "$(grep -c . "$W/state/dispatched")" = "$((n + 1))" ]
@@ -1449,9 +1501,13 @@ B
   out=$(BUS_CLASSIFY_RC=3 run dispatch 7 "$h1" cmsg_K); rc=$?
   [ $rc = 0 ] && [ "$(grep -c . "$W/state/dispatched")" = "$((n + 2))" ]
   expect "a head still in flight (classify WAIT) is reviewable and dispatches" $?
+  out=$(BUS_CLASSIFY_RC=4 run dispatch 7 "$h1" cmsg_K 2>&1); rc=$?
+  [ $rc = 0 ] && echo "$out" | grep -q '^bus: APPROVAL-OWED '"$h1"' 1 budget raise' \
+    && echo "$out" | grep -q '^bus-nonce: ' && [ "$(grep -c . "$W/state/dispatched")" = "$((n + 3))" ]
+  expect "P345: a raise whose only red is its owed approval (classify --pr APPROVAL-OWED) dispatches, records, and prints the line" $?
   out=$(BUS_CLASSIFY_RC=2 run dispatch 7 "$h1" cmsg_K); rc=$?
   [ $rc != 0 ] && echo "$out" | grep -q "cannot classify .*never green): REFUSE proof" \
-    && [ "$(grep -c . "$W/state/dispatched")" = "$((n + 2))" ]
+    && [ "$(grep -c . "$W/state/dispatched")" = "$((n + 3))" ]
   expect "an unreadable classification refuses the dispatch, never green" $?
   out=$(run dispatch 7 "$h1" cmsg_P --harness a --harness-file b); rc=$?
   [ $rc != 0 ] && echo "$out" | grep -q "takes one path, once"; expect "dispatch takes one finder's harness, never two" $?
diff --git a/tools/audit/seat/cloud_dispatch.py b/tools/audit/seat/cloud_dispatch.py
index 5346afba2..944232896 100644
--- a/tools/audit/seat/cloud_dispatch.py
+++ b/tools/audit/seat/cloud_dispatch.py
@@ -204,9 +204,10 @@ def _prompt(role: str, repo: str, pr: str, head: str, topic: str, nonce: str, br
             "Verify each claim adversarially: mutate the fix and check the tests fail, and check "
             "every figure in the body at this head. Check that it merges with origin/main "
             "(`git merge-tree --write-tree`). Wait for CI on this head only by re-running "
-            f"`python3 tools/audit/seat/merge_train.py classify {head}` in the background, at least 60 s "
-            "between runs, until it exits 0 (GREEN), 1 (RED) or 2 (unreadable: say so in the verdict); "
-            "3 is WAIT, so run it again. Never wait with `pgrep` or `pkill`, whose `-f` pattern matches "
+            f"`python3 tools/audit/seat/merge_train.py classify {head} --pr {pr}` in the background, at least "
+            "60 s between runs, until it exits 0 (GREEN), 1 (RED), 2 (unreadable: say so in the verdict) "
+            "or 4 (APPROVAL-OWED: the only red is the budget raise's approval, which follows your verdict; "
+            "judge the head as GREEN and quote the line); 3 is WAIT, so run it again. Never wait with `pgrep` or `pkill`, whose `-f` pattern matches "
             "the waiter's own command line, nor on a context the ruleset does not require, such as "
             "`prelude`.\n"
             f"Output: in a fresh directory of your own (`W=$(mktemp -d)`), write verdict.md, whose first line is "
@@ -1029,9 +1030,11 @@ def self_test() -> int:
     check("every role's setup line runs the toolchain check and stops on its REFUSE (#2709)",
           all(f"`{SETUP_CHECK}`, and on REFUSE stop" in t.splitlines()[1] for t in prompts.values()))
     rv = prompts["reviewer"]
-    check("the reviewer waits for CI only by re-running merge_train.py classify, 60 s apart, until 0, 1 or 2",
-          f"`python3 tools/audit/seat/merge_train.py classify {head}` in the background, at least 60 s" in rv
-          and "exits 0 (GREEN), 1 (RED) or 2 (unreadable: say so in the verdict)" in rv and "3 is WAIT" in rv)
+    check("the reviewer waits for CI only by re-running merge_train.py classify --pr, 60 s apart, until 0, 1, 2 "
+          "or 4 (APPROVAL-OWED, P345)",
+          f"`python3 tools/audit/seat/merge_train.py classify {head} --pr 7` in the background, at least" in rv
+          and "or 4 (APPROVAL-OWED: " in rv
+          and "exits 0 (GREEN), 1 (RED), 2 (unreadable: say so in the verdict)" in rv and "3 is WAIT" in rv)
     check("the reviewer is forbidden a pgrep or pkill waiter and a context the ruleset does not require",
           "Never wait with `pgrep` or `pkill`" in rv and "such as\n`prelude`" not in rv and "such as `prelude`" in rv)
     check("no other role is told to wait on merge_train.py classify (null control)",
diff --git a/tools/audit/seat/instruments/bus.sh.md b/tools/audit/seat/instruments/bus.sh.md
index 4bf8d046f..77451c279 100644
--- a/tools/audit/seat/instruments/bus.sh.md
+++ b/tools/audit/seat/instruments/bus.sh.md
@@ -25,8 +25,14 @@
   and says why in `review-packet: unavailable -- <reason>`. A head is
   dispatched only when `merge_train.py classify` reads it reviewable: RED (a
   required context's latest run concluded failure) or an unreadable answer
-  refuses and records nothing; GREEN and WAIT dispatch (`$HPO_BUS_CLASSIFY`
-  replaces the command in self-tests).
+  refuses and records nothing; GREEN and WAIT dispatch, and so does
+  APPROVAL-OWED (`classify --pr`, rc 4: the red is only a budget raise's
+  approval, which follows the review; its line is printed) (`$HPO_BUS_CLASSIFY`
+  replaces the command in self-tests). With `--reviewed-head <rh>`, a range
+  `review_carry.py` answers CARRY refuses only when the latest verdict naming
+  `rh` on `verdict/<pr>` is merge; a blocked one, or none, dispatches and prints
+  `review-carry: <rh> was blocked|has no verdict, so a fresh review is owed`,
+  and an unreadable `verdict/<pr>` refuses (P348).
 
 The design steps (decision 0014) write the same append-only way:
 `bus.sh push-design <topic> <design.md>` adds `design.md` to `design/<topic>`;
diff --git a/tools/audit/seat/instruments/merge_train.py.md b/tools/audit/seat/instruments/merge_train.py.md
index d7f1cff8f..fe5b178c9 100644
--- a/tools/audit/seat/instruments/merge_train.py.md
+++ b/tools/audit/seat/instruments/merge_train.py.md
@@ -102,7 +102,17 @@
   `classify <sha>` prints GREEN (rc 0), RED (rc 1) or WAIT (rc 3) over a pull
   request's required contexts (`--main`: less the PR-only ones), rc 2 when
   unreadable — a head is reviewable unless RED, which `bus.sh dispatch`
-  enforces. A required context red at main's tip whose workflow run is at
+  enforces. `--pr N` asks `approval_owed(train, pr, head, runs, required)`, the one
+  owner of a budget raise's pre-approval red (P345): when the red set over
+  `gating_names` is `gate` and `budget-raise-gate / budget-raise-gate` alone,
+  every red gate suite's own log (`gate_raise_only`, through `gate_outcome`)
+  lists that unit's failure as its only reason (a SKIPPED, ABSENT or PENDING
+  unit, or a reason naming none, reddens `gate` outside the red set: #3073),
+  and `Train.raise_hold`, over the three-dot names from git, reads a raise not
+  held, it prints `APPROVAL-OWED <sha> <the gate's reason>` (rc 4): reviewable,
+  because the owner's approval follows the verdict. A raise_hold Stop, a gate suite still
+  running or a failed read (a log included) stays RED; `classify` itself, the train and the merge state are
+  unchanged, and without `--pr` the answer is as before. A required context red at main's tip whose workflow run is at
   attempt 1 and failed on infrastructure alone (every failed job but `gate`
   logs an API rate-limit or unreachable string, and `gate` printed
   RATE-LIMITED or only `<job>: failure (this run)` reasons naming those jobs)
diff --git a/tools/audit/seat/instruments/orchestrator_tick.py.md b/tools/audit/seat/instruments/orchestrator_tick.py.md
index 437a1eb0b..d87ab1cf0 100644
--- a/tools/audit/seat/instruments/orchestrator_tick.py.md
+++ b/tools/audit/seat/instruments/orchestrator_tick.py.md
@@ -8,7 +8,9 @@
   GitHub's merge, no local driver run (the
   claimnotes repair only when all are claim files; a content conflict goes
   back to its fixer), NOT REVIEWABLE at a head whose required context
-  concluded red, zero-run heads, absent required contexts, twin heads, claim
+  concluded red -- except RAISE APPROVAL OWED (review it, then approve under
+  the owner or the mandate, never its fixer) where `merge_train.approval_owed`
+  reads the red as a budget raise's owed approval alone (P345), zero-run heads, absent required contexts, twin heads, claim
   stamps, staleness behind main; worker seats judged from the work they were
   dispatched for; roster groups newly unblocked or blocked; main's tip, its
   required contexts re-read live and judged by `merge_train.py`'s classifier,
diff --git a/tools/audit/seat/instruments/review_carry.py.md b/tools/audit/seat/instruments/review_carry.py.md
index f2ac1bd7d..945b7d068 100644
--- a/tools/audit/seat/instruments/review_carry.py.md
+++ b/tools/audit/seat/instruments/review_carry.py.md
@@ -19,4 +19,6 @@
   a `ci:`/`claims:` commit are all `FRESH-REVIEW`, and so is a range
   `app_approve.sh --carry` refuses, with its reason.
   `--verdict-only` prints the token alone; `bus.sh dispatch --reviewed-head`
-  is its caller, and `--self-test` grades the ranges.
+  is its caller, refusing on CARRY only when the latest verdict naming the
+  reviewed head on `verdict/<pr>` is merge (a range never says what a review
+  decided: P348), and `--self-test` grades the ranges.
diff --git a/tools/audit/seat/instruments/review_packet.py.md b/tools/audit/seat/instruments/review_packet.py.md
index 9d4538d7d..f49cdd216 100644
--- a/tools/audit/seat/instruments/review_packet.py.md
+++ b/tools/audit/seat/instruments/review_packet.py.md
@@ -10,8 +10,9 @@
   cloud reviewer, whose dispatcher's copy is a path on another machine,
   renders its own from its dispatch prompt. Refusal: carry-audit, a `## Head`
   not naming the head, a `tests/structure.py` refusal at the head merged with
-  main, an unanswered concluded red, a required context concluded failure, a
-  host path, a hot file shared with an open pull request holding an
+  main, an unanswered concluded red, a required context concluded failure
+  (unless `merge_train.py classify --pr` answers APPROVAL-OWED, printed as the
+  `approval-owed` advisory instead; P345), a host path, a hot file shared with an open pull request holding an
   unboarded merge verdict, or a `fix/<t>` head lacking its `handoff/<t>` tip
   (`handoff-not-applied`), or a body line citing a carry as landed that the roster ref lacks at the cited sha (`carry-landed`); a pending check never refuses. A `head-note` refusal names the repair (`update_pr.sh`). The packet closes on the `carry_audit.py check` self-audit a reviewer runs before its verdict. `handoff`, run by
   `body_push.sh` before a PR body is pushed, refuses the structure and
diff --git a/tools/audit/seat/merge_train.py b/tools/audit/seat/merge_train.py
index f6e542967..88e5bdd8f 100644
--- a/tools/audit/seat/merge_train.py
+++ b/tools/audit/seat/merge_train.py
@@ -370,15 +370,20 @@ def latest_runs(runs) -> dict:
     GATE: the latest run of each check suite is kept and the worst stands
     (pending before red before green), so an older suite's red is never
     hidden behind a newer green (A5)."""
-    runs = sorted(runs, key=lambda c: c.get("started_at") or "")
-    out = {c["name"]: c for c in runs}
-    suites = {(c.get("check_suite") or {}).get("id") or ("run", c.get("id")): c
-              for c in runs if c["name"] == GATE}
+    out = {c["name"]: c for c in sorted(runs, key=lambda c: c.get("started_at") or "")}
+    suites = gate_suites(runs)
     if suites:
-        out[GATE] = min(suites.values(), key=lambda c: ("pending", "red", "green").index(run_state(c)))
+        out[GATE] = min(suites, key=lambda c: ("pending", "red", "green").index(run_state(c)))
     return out
 
 
+def gate_suites(runs) -> "list[dict]":
+    """The latest GATE run of each check suite (A5: one CI run, one suite, one gate)."""
+    runs = sorted(runs, key=lambda c: c.get("started_at") or "")
+    return list({(c.get("check_suite") or {}).get("id") or ("run", c.get("id")): c
+                 for c in runs if c["name"] == GATE}.values())
+
+
 def run_state(cr: dict) -> str:
     """'pending' while not completed (wait, never red); else 'green' for a
     GREEN conclusion (GATE_GREEN for GATE) and 'red' for any other, one
@@ -450,6 +455,65 @@ def classify(latest: dict, required) -> "tuple[str, list[str], list[str]]":
     return ("red" if red else "wait" if pending else "green"), pending, red
 
 
+#: The gate unit whose red, before the review, is every budget raise's state (K15 (d)).
+RAISE_GATE = "budget-raise-gate / budget-raise-gate"
+
+
+def approval_owed(train: "Train", pr: int, head: str, runs, required) -> "str | None":
+    """The ONE owner of K15 (d)'s raise exception (P345): the gate's reason
+    when <head> is red only because a budget raise's approval is owed, else
+    None. Owed exactly when (a) every red name over `gating_names(required)`
+    (the ruleset's `gate` alone never names the unit) is GATE or RAISE_GATE,
+    RAISE_GATE among them; (b) every reason each red gate suite printed is
+    RAISE_GATE's own failure (`gate_raise_only`: a SKIPPED, ABSENT or PENDING
+    unit, or a reason naming no unit, reddens `gate` while leaving the red set
+    alone -- #3073); and (c) `Train.raise_hold` -- and so budget_raise_gate's
+    own raises_between and approval -- reads at least one raise not held, over
+    the three-dot names from git. A read that fails or a raise_hold Stop is
+    None: fail closed, the head stays not reviewable. The merge state is
+    untouched: `classify` and the train judge as before."""
+    red = set(classify(latest_runs(runs), gating_names(required))[2])
+    if RAISE_GATE not in red or red - {GATE, RAISE_GATE}:
+        return None
+    if not gate_raise_only(train, runs):
+        return None
+    code, base = train.run(["git", "merge-base", "origin/main", head])
+    if code or not is_sha(base.strip()):
+        return None
+    code, names = train.run(["git", "diff", "--no-renames", "--name-only", base.strip(), head])
+    if code:
+        return None
+    try:
+        raises, held, why = train.raise_hold(pr, head, names.split())
+    except Stop:
+        return None
+    return why if raises and not held else None
+
+
+#: The one reason a gate red only through an owed raise prints (gate.py's judge,
+#: the unit read in this run or in an earlier one at the head).
+RAISE_REASON = re.compile(rf"^{re.escape(RAISE_GATE)}: failure \((?:this run|run \d+)\)$")
+
+
+def gate_raise_only(train: "Train", runs) -> bool:
+    """True when at least one gate suite is red, none is still running, and
+    every red one's log (`gate_outcome`, gate.py's own FAIL reasons) lists
+    RAISE_REASON alone. An unread log, a gate step that never ran or a
+    RATE-LIMITED gate is False. A check run's id is its Actions job's id; gh
+    refuses an Actions log unless told to pass its terminal escapes."""
+    suites = gate_suites(runs)
+    if not suites or any(run_state(c) == "pending" for c in suites):
+        return False
+    reds = [c for c in suites if run_state(c) == "red"]
+    for c in reds:
+        code, log = train.run(["gh", "api", "--allow-escape-sequences",
+                               f"repos/{train.repo}/actions/jobs/{c.get('id')}/logs"])
+        out = gate_outcome(log) if code == 0 else None
+        if not out or out[0] != "fail" or not out[1] or not all(RAISE_REASON.match(x) for x in out[1]):
+            return False
+    return bool(reds)
+
+
 def stale(cr: dict, run_status: str) -> bool:
     """K15 (b): a check-run still queued or in progress while its workflow run
     has completed is stale, not pending: nothing will conclude it (#2559's
@@ -5174,6 +5238,149 @@ def _state_self_test(check, go, merged, throwaway_git_init) -> None:
           and cli(red_pc, "fast\npr-contract\n", "--main")[0] == 1)
     check("K15 (d): a head still in flight is WAIT (rc 3) and reviewable; an unreadable ruleset refuses (rc 2)",
           cli([cr("fast", "in_progress"), cr("pr-contract")])[0] == 3 and cli(red_pc, "")[0] == 2)
+    # P345 (K15 (d)'s raise exception): every raise is red at budget-raise-gate
+    # until the owner's approval names its head, and that approval follows the
+    # review. With --pr, a RED whose gating red set is gate + RAISE_GATE alone,
+    # over a diff whose raise raise_hold reads as not held, is APPROVAL-OWED (rc 4).
+    _g, owner_rv, mandate_c, _rv = policy_fixture_builders()
+    OLD, BASE = "d" * 40, "e" * 40
+    now = datetime.datetime.now(datetime.timezone.utc)
+
+    def glog(*reasons, step=True) -> str:
+        """A gate job's log as the Actions logs API serves it: timestamped lines, gate.py's
+        step opened by its `##[group]Run` line, its stdout (`FAIL <reason>`, then one
+        reason a line) closed by the runner's `##[error]`."""
+        ts = "2026-10-31T21:39:58.5470993Z "
+        out = [ts + "##[group]Run set -euo pipefail", ts + "##[endgroup]"]
+        if step:
+            out += [ts + '##[group]Run python3 -I tools/ci/gate.py --pr "$PR" --base "$BASE" --kind "$KIND"',
+                    ts + "env:", ts + "##[endgroup]"]
+        out += [ts + ("FAIL " if i == 0 else "") + r for i, r in enumerate(reasons)]
+        return "\n".join(out + [ts + "##[error]Process completed with exit code 1.", ts + "Post job cleanup."]) + "\n"
+    RAISE_LOG = glog(f"{RAISE_GATE}: failure (this run)")
+
+    def owed_cli(runs, files, budgets=RAISE_FIXTURE, reviews=None, ls_fail=False, body="## Summary\n",
+                 *flags, logs=None, diff_fail=False) -> "tuple[int, str]":
+        def fake_run(argv, cwd=ROOT, stdin=None):
+            a = " ".join(argv)
+            if "/actions/jobs/" in a and a.endswith("/logs"):
+                text = (logs or {}).get(int(a.rsplit("/", 2)[-2]), RAISE_LOG)
+                return (0, text) if text is not None else (1, "HTTP 410: logs expired")
+            if "check-runs" in a:
+                return 0, "\n".join(json.dumps(c) for c in runs)
+            if a.endswith("rulesets --jq " + argv[-1]):
+                return 0, "7"
+            if "rulesets/7" in a:
+                return 0, "gate\n"
+            if argv[:2] == ["git", "merge-base"]:
+                return 0, BASE + "\n"
+            if argv[:4] == ["git", "diff", "--no-renames", "--name-only"]:
+                if diff_fail:
+                    return 128, "fatal: bad object tests/structure_budgets.json\n"
+                return 0, "".join(f + "\n" for f in files)
+            if ls_fail and argv[:2] == ["git", "ls-tree"]:
+                return 128, "fatal: not a tree object"
+            got = budget_fixture(budgets, argv, BASE)
+            if got is not None:
+                return got
+            if "/reviews" in a:
+                return 0, json.dumps([reviews if reviews is not None else [owner_rv(OLD, now)]])
+            if argv[:3] == ["gh", "pr", "view"]:
+                return 0, body
+            if "issues/comments/" in a:
+                return 0, json.dumps(mandate_c(now))
+            if "/comments" in a:
+                return 0, json.dumps([[]])
+            return 1, "unexpected " + a
+        saved, buf = Train._run, io.StringIO()
+        Train._run = staticmethod(fake_run)
+        try:
+            with contextlib.redirect_stdout(buf):
+                rc = main(["classify", "a" * 40, *flags])
+        finally:
+            Train._run = saved
+        return rc, buf.getvalue()
+
+    BUDGET_F = ["tests/structure_budgets.json", "tools/x.py"]
+    shape3045 = [cr(GATE, conclusion="failure"), cr(RAISE_GATE, conclusion="failure"), cr("tests / fast (3.14)"),
+                 cr("pr-contract / pr-contract")]
+    rc, out = owed_cli(shape3045, BUDGET_F, RAISE_FIXTURE, None, False, "## Summary\n", "--pr", "3045")
+    check("P345 row 1: #3045's shape (gate + budget-raise-gate red, one raise in the diff, the owner's "
+          "approval on an older head) is APPROVAL-OWED, rc 4, naming the raise and the gate's why",
+          rc == 4 and out.startswith(f"APPROVAL-OWED {'a' * 40} 1 budget raise(s), first ")
+          and "a raise is the owner's" in out)
+    rc, out = owed_cli([*shape3045[:2], cr("tests / fast (3.14)", conclusion="failure")], BUDGET_F,
+                       RAISE_FIXTURE, None, False, "## Summary\n", "--pr", "3045")
+    check("P345 row 2 (null): the same plus `tests / fast (3.14)` red stays RED, rc 1",
+          rc == 1 and out.startswith("RED "))
+    rc, out = owed_cli(shape3045, ["tools/x.py"], None, None, False, "## Summary\n", "--pr", "3045")
+    rc2, out2 = owed_cli(shape3045, ["tests/ci_budgets.json"], NEW_ROWS_FIXTURE, None, False,
+                         "## Summary\n", "--pr", "3045")
+    check("P345 row 3 (null): budget-raise-gate red with no raise in the diff -- no budget file, or one "
+          "that only gains rows (#2401) -- stays RED, rc 1", rc == 1 and rc2 == 1 and out.startswith("RED "))
+    rc, out = owed_cli(shape3045, BUDGET_F, RAISE_FIXTURE, None, True, "## Summary\n", "--pr", "3045")
+    check("P345 row 4 (null): a raise_hold Stop (an unlistable tree) is not approval owed: RED, rc 1",
+          rc == 1 and out.startswith("RED "))
+    rc, out = owed_cli(shape3045, BUDGET_F, RAISE_FIXTURE, None, False, "## Summary\n")
+    check("P345 row 5: without --pr the same head is RED, rc 1, exactly as old callers read it",
+          rc == 1 and out.startswith("RED "))
+    rc, out = owed_cli(shape3045, BUDGET_F, RAISE_FIXTURE, [owner_rv("a" * 40, now)], False, JUSTIFIED_BODY,
+                       "--pr", "3045")
+    check("P345 (null): a raise the owner's mandated approval already holds at the head owes nothing: RED, rc 1",
+          rc == 1 and out.startswith("RED "))
+    rc, out = owed_cli([cr(GATE, conclusion="failure"), cr("tests / fast (3.14)", conclusion="failure")],
+                       BUDGET_F, RAISE_FIXTURE, None, False, "## Summary\n", "--pr", "3045")
+    check("P345 (null): a red gate whose units do not include budget-raise-gate stays RED, rc 1",
+          rc == 1 and out.startswith("RED "))
+    # #3073 round 1 (class-open): the red SET never says why `gate` is red. gate.py fails a
+    # SKIPPED, ABSENT or PENDING unit, and for reasons naming no unit at all, none of which
+    # puts a unit into that set. Owed only when every reason in each red gate suite's own
+    # log names RAISE_GATE; every other answer, an unread log included, stays RED.
+    raise_r = f"{RAISE_GATE}: failure (this run)"
+    for label, extra, reasons in (
+            ("a SKIPPED unit", [cr("tests / browser", conclusion="skipped")],
+             (raise_r, "tests / browser: SKIPPED (this run)")),
+            ("an ABSENT unit (no check run)", [], (raise_r, "tests / arch-instrument: ABSENT (this run)")),
+            ("a PENDING unit under a concluded gate", [cr("tests / browser", "in_progress")],
+             (raise_r, "tests / browser: PENDING (run 9)")),
+            ("a reason naming no unit (the deferral bound)", [],
+             ("run(s) [99] at this head are still being judged past the bound",)),
+            ("a reason naming no unit (the prelude cross-check)", [],
+             ("prelude says kind=code pr='', the event says kind=code pr='3045'",)),
+            ("the raise unit itself SKIPPED or PENDING, not failed (no approval judged)", [],
+             (f"{RAISE_GATE}: SKIPPED (this run)", f"{RAISE_GATE}: PENDING (run 9)"))):
+        rc, out = owed_cli([*shape3045, *extra], BUDGET_F, RAISE_FIXTURE, None, False, "## Summary\n",
+                           "--pr", "3045", logs={1: glog(*reasons)})
+        check(f"#3073: a raise whose gate is also red for {label} stays RED, rc 1",
+              rc == 1 and out.startswith("RED "))
+    rc, out = owed_cli(shape3045, BUDGET_F, RAISE_FIXTURE, None, False, "## Summary\n", "--pr", "3045",
+                       logs={1: None})
+    rc2, out2 = owed_cli(shape3045, BUDGET_F, RAISE_FIXTURE, None, False, "## Summary\n", "--pr", "3045",
+                         logs={1: glog("base ref malformed", step=False)})
+    check("#3073: a gate log that cannot be read, or whose gate.py step never ran, stays RED, rc 1",
+          rc == 1 and out.startswith("RED ") and rc2 == 1 and out2.startswith("RED "))
+    suites = [{**cr(GATE, conclusion="failure", started="2", cid=11), "check_suite": {"id": 1}},
+              {**cr(GATE, conclusion="failure", started="3", cid=12), "check_suite": {"id": 2}}, *shape3045[1:]]
+    rc, out = owed_cli(suites, BUDGET_F, RAISE_FIXTURE, None, False, "## Summary\n", "--pr", "3045",
+                       logs={11: RAISE_LOG, 12: RAISE_LOG})
+    rc2, out2 = owed_cli(suites, BUDGET_F, RAISE_FIXTURE, None, False, "## Summary\n", "--pr", "3045",
+                         logs={11: RAISE_LOG, 12: glog("tests / fast (3.14): failure (run 5)")})
+    check("#3073: every red gate suite is read -- two raise-only suites (#3045 carried four) are owed, rc 4; "
+          "one suite red for another unit is RED, rc 1",
+          rc == 4 and out.startswith("APPROVAL-OWED ") and rc2 == 1 and out2.startswith("RED "))
+    running = [suites[0], {**cr(GATE, "in_progress", started="3", cid=12), "check_suite": {"id": 2}}, *shape3045[1:]]
+    # The CLI asks only once `classify` reads RED, so these two shapes (WAIT, GREEN there) are a
+    # direct caller's: gate_raise_only itself, over a train answering every log raise-only.
+    class lt:  # the two attributes gate_raise_only reads of a Train
+        repo, run = "o/r", staticmethod(lambda argv, **_k: (0, RAISE_LOG))
+    check("#3073: gate_raise_only is False for a gate suite still running beside a raise-only red one, and "
+          "for a green gate; True for the raise-only suites (the control)",
+          gate_raise_only(lt, running) is False and gate_raise_only(lt, [cr(GATE), *shape3045[1:]]) is False
+          and gate_raise_only(lt, suites) is True)
+    rc, out = owed_cli(shape3045, BUDGET_F, RAISE_FIXTURE, None, False, "## Summary\n", "--pr", "3045",
+                       diff_fail=True)
+    check("#3073 O2: a failed three-dot diff read is not approval owed: RED, rc 1",
+          rc == 1 and out.startswith("RED "))
     # (c) a DIRTY head, from git merge-tree against a throwaway repository:
     # once bare, once with the claimnotes driver installed as claim-files.md
     # tells every clone to, which resolves a notes-only claim conflict and
@@ -6892,9 +7099,11 @@ def _parser() -> argparse.ArgumentParser:
     u.add_argument("sha")
     c = sub.add_parser("classify", parents=[common],
                        help="GREEN (rc 0), RED (rc 1), WAIT (rc 3) over the required contexts; "
-                            "unreadable rc 2; a head is reviewable unless RED")
+                            "unreadable rc 2; with --pr, APPROVAL-OWED (rc 4) for a RED that is only a "
+                            "budget raise's owed approval (approval_owed); a head is reviewable unless RED")
     c.add_argument("sha")
     c.add_argument("--main", action="store_true", help="<sha> is main's tip: PR_ONLY contexts are not judged")
+    c.add_argument("--pr", type=int, help="the pull request <sha> heads: lets a RED read as APPROVAL-OWED (rc 4)")
     return p
 
 
@@ -6946,10 +7155,16 @@ def main(argv: list[str]) -> int:
             runs = t._check_runs(a.sha)
             if runs is None:
                 raise Stop("ci", f"the check runs at {a.sha[:12]} could not be read")
-            state, pending, red = classify(latest_runs(runs), t.required(pr_head=not a.main))
+            req = t.required(pr_head=not a.main)
+            state, pending, red = classify(latest_runs(runs), req)
+            why = (approval_owed(t, a.pr, a.sha, runs, req)
+                   if state == "red" and a.pr is not None else None)
         except Stop as s:
             print(f"REFUSE {s.step}: {s.why}")
             return 1 if a.cmd == "unstale" else 2
+        if why:
+            print(f"APPROVAL-OWED {a.sha} {why}")
+            return 4
         print(f"{state.upper()} {a.sha} pending: {' '.join(pending) or 'none'} red: {' '.join(red) or 'none'}")
         return {"green": 0, "red": 1, "wait": 3}[state]
     if a.cmd == "sweep":
diff --git a/tools/audit/seat/orchestrator_tick.py b/tools/audit/seat/orchestrator_tick.py
index 301ef7c53..3a9d43a0d 100644
--- a/tools/audit/seat/orchestrator_tick.py
+++ b/tools/audit/seat/orchestrator_tick.py
@@ -838,6 +838,25 @@ class Tick:
             self.line(S, "obligations ledger: closed this pass "
                       + " ".join(f"{k}={v}" for k, v in sorted(closed.items())))
 
+    def _approval_owed(self, n: int, head: str, runs: list, req: list) -> "str | None":
+        """merge_train.approval_owed over this head's check runs and required
+        list, its reads (the gate logs included, #3073) routed through this
+        tick's own gh and git (P345): the one owner
+        of K15 (d)'s raise exception, asked, never restated. A head that
+        cannot be fetched, or any failed read, is None: not reviewable."""
+        if self.git(["fetch", "-q", "origin", head])[0]:
+            return None
+
+        def run(argv, cwd=None, stdin=None):
+            if argv[:1] == ["gh"]:
+                return self.gh(argv[1:])
+            return self.git(argv[1:]) if argv[:1] == ["git"] else (1, "the tick runs gh and git only")
+        try:
+            t = mt.Train(self.repo, Path("."), None, "", (), 0, run=run, log=lambda _m: None)
+            return mt.approval_owed(t, n, head, runs, req)
+        except (mt.Stop, OSError, ValueError):  # fail closed: an unread raise is not reviewable
+            return None
+
     def one_pr(self, S: str, pr: dict, verdict: "str | None",
                required: "list[str] | None") -> None:
         n, head = pr["number"], pr.get("headRefOid") or ""
@@ -875,8 +894,14 @@ class Tick:
             for nm in run:
                 pend[(n, nm)] = (lat[nm].get("started_at"), head)
         if red and required is not None:
-            req_red = mt.classify(self.latest(runs or []), getattr(self, "_req_pr", None) or required)[2]
-            if req_red:
+            req = getattr(self, "_req_pr", None) or required
+            req_red = mt.classify(self.latest(runs or []), req)[2]
+            owed = self._approval_owed(n, head, runs or [], req) if req_red else None
+            if owed:
+                self.line(S, f"#{n}: RAISE APPROVAL OWED at {head[:8]}: review it, then approve "
+                             "under the owner or the mandate (0013) -- not its fixer (K15 (d)): "
+                             f"{owed}", flag=True)
+            elif req_red:
                 self.line(S, f"#{n}: NOT REVIEWABLE at {head[:8]}: required "
                              f"{', '.join(req_red)} concluded red -- back to its "
                              "fixer, never a reviewer (K15 (d))", flag=True)
@@ -3454,6 +3479,45 @@ def self_test() -> int:
                 (f"NOT REVIEWABLE {'names pr-contract' if want else 'absent'}",
                  (len(nr) == 1 and "pr-contract" in nr[0]) if want else not nr)])
             total, failed = total + a, failed + f
+        # PRS (d), P345: a budget raise is red at budget-raise-gate until the
+        # owner's approval names its head, which follows the review. #3045's
+        # shape (gate + budget-raise-gate red, one raise, the owner's approval
+        # on an older head) is RAISE APPROVAL OWED, not NOT REVIEWABLE; null
+        # controls: a second gate unit red, and the same reds with no raise.
+        # #3073: owed only when the gate's own log names the raise alone; a gate also red
+        # for a SKIPPED unit (absent from the red set) is NOT REVIEWABLE.
+        RAISE = "budget-raise-gate / budget-raise-gate"
+        bud = "tests/structure_budgets.json"
+        glog = lambda *r: "".join(f"2026-10-31T21:40:02.5Z {x}\n" for x in (
+            '##[group]Run python3 -I tools/ci/gate.py --pr "$PR"', "##[endgroup]",
+            *(("FAIL " if i == 0 else "") + x for i, x in enumerate(r)), "##[error]Process completed with exit code 1."))
+        own = f"{RAISE}: failure (this run)"
+        for label, extra_red, files, want, why in (
+                ("#3045 shape", (), f"{bud}\ntools/x.py\n", True, (own,)),
+                ("null: tests / fast (3.14) red too", ("tests / fast (3.14)",), f"{bud}\n", False, (own,)),
+                ("null: no raise in the diff", (), "tools/x.py\n", False, (own,)),
+                ("null (#3073): the gate also failed a SKIPPED unit", (), f"{bud}\ntools/x.py\n", False,
+                 (own, "tests / browser: SKIPPED (this run)"))):
+            runs = [run_obj("gate", conclusion="failure"), run_obj(RAISE, conclusion="failure"),
+                    *(run_obj(x, conclusion="failure") for x in extra_red)]
+            t = tick(prs=[pr_obj(75, H1)], required_names=("gate",), runs_at={H1: runs},
+                     gh_extra=[(f"actions/jobs/{runs[0]['id']}/logs", 0, glog(*why))],
+                     bodies={75: "## Red checks\n\ngate: x\n"},
+                     reviews={75: [[{"user": owner, "state": "APPROVED", "commit_id": H2,
+                                     "submitted_at": iso(NOW), "body": "ok"}]]})
+            t._git.h[:0] = [(("diff", "--no-renames", "--name-only", V, H1), 0, files),
+                            (("ls-tree", "-r", "--name-only"), 0, f"{bud}\n"),
+                            (("show", f"{V}:{bud}"), 0, '{\n "m": 3\n}\n'),
+                            (("show", f"{H1}:{bud}"), 0, '{\n "m": 4\n}\n')]
+            t.one_pr("PRS", pr_obj(75, H1), None, t.required("PRS"))
+            txt = [x["text"] for x in t.findings]
+            owed = [x for x in txt if x.startswith(f"#75: RAISE APPROVAL OWED at {H1[:8]}: review it")]
+            nr = [x for x in txt if x.startswith("#75: NOT REVIEWABLE")]
+            a, f = check(f"P345 PRS {label}", [
+                ("RAISE APPROVAL OWED " + ("present, naming the raise" if want else "absent"),
+                 (len(owed) == 1 and f"{bud}: m: 3 -> 4" in owed[0]) if want else not owed),
+                ("NOT REVIEWABLE " + ("absent" if want else "present"), bool(nr) != want)])
+            total, failed = total + a, failed + f
         # PRS (c): DIRTY names the conflicted files from git merge-tree first;
         # the claimnotes repair only for claim files alone (#2569's shape).
         claim = CLAIM_FILES[0]
diff --git a/tools/audit/seat/review_packet.py b/tools/audit/seat/review_packet.py
index 0f94e279a..ebc58358e 100644
--- a/tools/audit/seat/review_packet.py
+++ b/tools/audit/seat/review_packet.py
@@ -34,7 +34,10 @@ REFUSALS (rc 1, each named by its signal), all mechanical:
   structure        `tests/structure.py` refuses the head merged with main;
   red-unanswered   a CONCLUDED red check the body's `## Red checks` does not name
                    (`policy_lint.mjs --pr-body --red`);
-  required-red     a required context's latest run concluded failure;
+  required-red     a required context's latest run concluded failure -- unless
+                   `merge_train.py classify --pr` answers APPROVAL-OWED (P345: the
+                   red is only a budget raise's approval, which follows the
+                   review), printed as the `approval-owed` advisory instead;
   host-path        the body or an added line names this host (`ref_privacy.py`);
   hot-file         the diff shares a HOT_FILES path with an open pull request
                    whose merge verdict is at its head and not on the train;
@@ -181,6 +184,23 @@ def gate_digest(runs: list[dict]) -> tuple[str, list[str], list[str]]:
     return state, lines, reds
 
 
+def approval_owed_line(pr: int, head: str) -> str | None:
+    """The reason `merge_train.py classify --pr` prints after `APPROVAL-OWED <head>`
+    (rc 4), else None: the one owner of K15 (d)'s raise exception asked, never
+    restated (P345). Any other answer, or a classifier that cannot run, is None,
+    and the required red refuses as before. HPO_PACKET_CLASSIFY replaces the
+    command (the self-test's stub)."""
+    cmd = shlex.split(os.environ.get("HPO_PACKET_CLASSIFY", "")) or [
+        sys.executable, str(ROOT / "tools/audit/seat/merge_train.py")]
+    try:
+        r = subprocess.run([*cmd, "classify", head, "--repo", REPO, "--pr", str(pr)],
+                           capture_output=True, text=True)
+    except OSError:
+        return None
+    m = re.search(rf"^APPROVAL-OWED {re.escape(head)} (.+)$", r.stdout, re.M)
+    return m.group(1) if r.returncode == 4 and m else None
+
+
 def head_note_ok(body: str, head: str) -> bool:
     return head in section(body, "Head")
 
@@ -459,14 +479,20 @@ def build(facts: dict) -> tuple[list[str], list[str], str]:
     refusals += handoff_refusals(facts["structure"], facts["hot"], [])
     for n in facts["red_unanswered"]:
         refusals.append(f"red-unanswered: concluded red check `{n}` is not named in ## Red checks")
+    owed, owed_adv = facts.get("approval_owed"), []
     for n in sorted(set(reds) & set(REQUIRED)):
-        refusals.append(f"required-red: required context `{n}` concluded failure at {head}")
+        if owed:
+            owed_adv.append(
+                f"approval-owed: required context `{n}` concluded failure at {head} only on a budget "
+                f"raise's owed approval (merge_train.approval_owed): {owed}")
+        else:
+            refusals.append(f"required-red: required context `{n}` concluded failure at {head}")
     for w in facts["host"]:
         refusals.append(f"host-path: {w}")
     refusals += facts.get("unlanded", [])
     if facts.get("handoff"):
         refusals.append(f"handoff-not-applied: {facts['handoff']}")
-    advisories = [a for a in facts.get("advisories", [])]
+    advisories = [a for a in facts.get("advisories", [])] + owed_adv
     parts = [
         f"# Review packet #{facts['pr']}",
         f"head: {head}", f"base: {facts['base']}", "",
@@ -505,6 +531,7 @@ def gather(a) -> dict:
         unlanded = unlanded_carries(cites, carries_at, on_roster)
     runs = gh(f"repos/{REPO}/commits/{head}/check-runs?per_page=100").get("check_runs", [])
     gate = gate_digest(runs)
+    owed = approval_owed_line(a.pr, head) if set(gate[2]) & set(REQUIRED) else None
     crc, cout = tool([sys.executable, "-I", "tools/audit/carry_audit.py", "check", "--body", "{BODY}"], body)
     _, fout = tool(["node", "tools/policy/figure_lint.mjs", "--pr-body", "{BODY}", "--at", head], body)
     red_unanswered = unanswered_reds(body, head, base, gate[2], touched, existing)
@@ -513,7 +540,8 @@ def gather(a) -> dict:
     host += ref_privacy.content_refusals(ref_privacy.added_lines(base, head, repo()), ident)
     open_prs, boarded = hot_prs(touched)
     return {
-        "pr": a.pr, "head": head, "base": base, "body": body, "gate": gate, "branch": branch, "unlanded": unlanded,
+        "pr": a.pr, "head": head, "base": base, "body": body, "gate": gate, "approval_owed": owed,
+        "branch": branch, "unlanded": unlanded,
         "carry_rc": crc, "carry_out": cout, "figure_out": fout,
         "structure": None if a.no_structure else structure_at_merge(main, head),
         "red_unanswered": red_unanswered, "host": host, "handoff": handoff,
@@ -635,6 +663,36 @@ def _self_test() -> int:
                {"id": 2, "name": "gate", "status": "completed", "conclusion": "failure"}]
     check("required-red: the required context's latest run concluded failure refuses",
           refused("required-red", gate=gate_digest(redgate)))
+    r_o, adv_o, t_o = build({**clean, "gate": gate_digest(redgate), "approval_owed": "1 budget raise(s), planted"})
+    check("P345: a required red that is only a raise's owed approval renders: no refusal, an "
+          "`approval-owed` advisory naming the reason, in the packet",
+          r_o == [] and len(adv_o) == 1 and adv_o[0].startswith("approval-owed: required context `gate`")
+          and "1 budget raise(s), planted" in t_o)
+    with tempfile.TemporaryDirectory() as d:
+        stub = Path(d) / "classify.sh"
+        stub.write_text('echo "$*" > "$(dirname "$0")/argv"; echo "${PK_OUT:-}"; exit "${PK_RC:-1}"\n')
+        saved = os.environ.get("HPO_PACKET_CLASSIFY")
+        os.environ["HPO_PACKET_CLASSIFY"] = f"bash {stub}"
+        try:
+            os.environ.update(PK_OUT=f"APPROVAL-OWED {H} 1 budget raise(s): why", PK_RC="4")
+            got = approval_owed_line(7, H)
+            argv = (Path(d) / "argv").read_text().split()
+            os.environ.update(PK_OUT=f"RED {H} pending: none red: gate", PK_RC="1")
+            red_line = approval_owed_line(7, H)
+            os.environ.update(PK_OUT=f"APPROVAL-OWED {B} 1 budget raise(s): why", PK_RC="4")
+            other = approval_owed_line(7, H)
+            os.environ.update(PK_OUT=f"APPROVAL-OWED {H} 1 budget raise(s): why", PK_RC="1")
+            wrong_rc = approval_owed_line(7, H)
+        finally:
+            os.environ.pop("PK_OUT", None), os.environ.pop("PK_RC", None)
+            if saved is None:
+                os.environ.pop("HPO_PACKET_CLASSIFY", None)
+            else:
+                os.environ["HPO_PACKET_CLASSIFY"] = saved
+    check("P345: the reason is classify --pr's own APPROVAL-OWED line at rc 4, asked with the pull "
+          "request; RED (rc 1), a line naming another head, and the line at any rc but 4 are None (null controls)",
+          got == "1 budget raise(s): why" and argv[:2] == ["classify", H] and argv[-2:] == ["--pr", "7"]
+          and red_line is None and other is None and wrong_rc is None)
     check("required-red null: the same head with that run green renders",
           build({**clean, "gate": gate_digest(list(reversed([dict(r, id=3 - r["id"]) for r in redgate])))})[0] == [])
     running = [{"id": 1, "name": "gate", "status": "in_progress", "conclusion": None},

## Before you return the verdict (P275)
Run `python3 -I tools/audit/carry_audit.py check --body <PR body file> --comments <file holding [{"id": 0, "body": <verdict.md text>}]>`. Give every reported item its own `Carry: <GROUP> | #<issue> | O<n> | dismissed: <reason>`;
an evidence line flagged by its wording takes `Carry: dismissed: evidence, not a finding`. Return the verdict only at rc 0.
