# Review packet #3547
head: b53bbf1604a3720aeb665a3b51219eb54df1fe6a
base: 7eadd75f3c420404aabc83d4b05f9691f3e49136

Start here (fix-review.md). Re-read the live check state before a verdict: the digest is as read at render.

## Gate digest: red
CodeQL id=132069479558 success
arch-score / arch-score id=132068832126 success
arm id=132067628550 skipped
budget-raise-gate / budget-raise-gate id=132068832149 success
cancel-superseded id=132067657388 success
codeql id=132068835070 skipped
codeql / Analyze (actions) id=132068679409 success
codeql / Analyze (javascript-typescript) id=132068679575 success
codeql / Analyze (python) id=132068679544 success
gate id=132069940694 failure
governance id=132068834356 skipped
governance / delivery-status id=132068679320 success
governance / delivery-status-publish id=132068682375 skipped
governance / env-matrix id=132068679547 success
governance / instrument-self-tests id=132068679739 success
governance / policy-docs id=132068679718 success
governance / record id=132068681798 skipped
governance / wave-script id=132068679157 success
hassfest id=132068833965 skipped
hassfest / hassfest id=132068678784 success
kernel-points id=132068834760 skipped
pr-contract id=132069942731 skipped
prelude id=132067657029 success
refresh id=132067657445 success
sweep-self id=132070633402 skipped
tests id=132068835381 skipped
tests / arch-instrument id=132069370462 success
tests / briefs id=132068678890 success
tests / browser id=132069370526 success
tests / claims-autofix id=132072897198 skipped
tests / closure-scope id=132068678916 success
tests / closures id=132069370620 in_progress
tests / coverage id=132069370460 in_progress
tests / fast (3.14) id=132069370370 success
tests / mutation id=132068679273 success
tests / mutation-autofix id=132070107467 skipped
tests / mutation-pins id=132070106641 skipped
tests / nightly-ha id=132069374247 skipped
tests / nightly-status id=132068679030 success
tests / replay id=132069373732 skipped
tests / typing id=132069370524 success
validate id=132068835076 skipped
validate / validate-hacs id=132068679714 success

## Refusals
none

## Advisories
required-wait: required context `gate` reads concluded failure at b53bbf1604a3720aeb665a3b51219eb54df1fe6a in the digest, but merge_train.py classify --pr reads WAIT (pending: gate red: none): classify decides, as bus.sh's dispatch does, and a pending check never refuses

## carry_audit at the head
CARRY-AUDIT: 0 finding item(s): 0 routed, 0 unrouted, 0 bad destination(s)

## figure_lint at the head
ok         python3 tools/pr/gate_priority.py --self-test
             `tools/pr/gate_priority.py` is in the tree at this head
  ok         bash tools/pr/prepr.sh --self-test
             `tools/pr/prepr.sh` is in the tree at this head
  ok         python3 tests/structure.py
             `tests/structure.py` is in the tree at this head
  ok         python3 tools/audit/seat/bare_array.py --check
             `tools/audit/seat/bare_array.py` is in the tree at this head
  ok         python3 tools/pr/ci_predict.py
             `tools/pr/ci_predict.py` is in the tree at this head
  unverified git merge-tree --write-tree origin/main HEAD
             `git merge-tree` resolves; its flags are not checked -- git prints a man page rather than a flag list, and a list carried in this file would rot into false refusals

FIGURES: 5 resolved, 1 not verified, 0 refused

## Finder's harness: none named
### at the base
not run
### at the head
not run

## Mutation-ledger diff
none

## Review scope: delta (later round over the reviewed head a81d7f15293fc2101f42e48ade37ef7022c35517)
Confirm each finding of the previous verdict is resolved, re-read the live required checks, and review the delta below. Widen only to exactly the already-reviewed code a delta touching production code (custom_components/) puts at risk of being affected in a non-obvious way CI would not detect, naming the path and the risk in the verdict; an instrument, test, policy or body delta never justifies a wider review (fix-review.md step 12).

## Previous verdict at a81d7f15293fc2101f42e48ade37ef7022c35517
Fix review: blocked a81d7f15293fc2101f42e48ade37ef7022c35517 mutation-vacuous: G5-cli-hotfix-inverted G5b-cli-hotfix-inverted-prepr P8-classifier-asks-priority G3-except-fails-open P7-HOTFIX_SCOPED-dropped P9-export-dropped

bus-nonce: c1dc4bad693bf2ac23244843f575ca13

## Block

Round 1 of this PR's review (a re-fire of the first session, which stopped with no verdict). Measured head: a81d7f15293fc2101f42e48ade37ef7022c35517, which is still the PR head (`pull_request_read get`).

The PR's own seven mutants are killed. The seam that carries the PR's whole behaviour is not covered by any test, though. That seam is prepr's `hotfix_class` calling `gate_priority.py --hotfix`, and the CLI printing `is_hotfix`. The prepr self-test stubs `hotfix_class`, and the gate_priority self-test calls `is_hotfix()` directly, never `main(["--hotfix", ...])`. Survivors at the head, from the reviewer's driver (`ev/driver.py`, `ev/mutants-results.txt`, one log per mutant in `ev/mutants/`):

- G5-cli-hotfix-inverted (`gate_priority.py` main prints `int(not is_hotfix(...))`), against the gate_priority self-test: SURVIVED. G5b is the same mutant against `prepr.sh --self-test`: SURVIVED. Failure scenario: every non-hotfix branch gets `PREPR_SKIP_CODE=hotfix PREPR_SKIP_CLOSURES=1`, so its code and closure steps are skipped, and every hotfix branch runs the full prepr. Every test still passes.
- P8-classifier-asks-priority (`hotfix_class` calls `gate_priority.py --branch` without `--hotfix`): SURVIVED. Failure scenario: `priority_for_branch` prints 1 for an outside or critical-path group and 2 for a hotfix. A critical-path branch would therefore be scoped and a hotfix branch would not, and every test still passes.
- G3-except-fails-open (`_rank`'s `except` returns `RANK_HOTFIX`): SURVIVED. `is_hotfix`'s docstring promises "Every failure is False", and the body says "a failed read gives a full prepr". The fail-closed self-test arm goes through `fetch=True` with no remote, which returns before the `try` body raises, so the exception path is never exercised. The same gap already existed in `derived_priority` at the base, but this PR newly relies on it as the safety property of a skip.
- P7-HOTFIX_SCOPED-dropped (`HOTFIX_SCOPED=1` deleted): SURVIVED. With it gone, a hotfix-scoped run prints "reused from the receipt at hotfix", a false receipt claim in the code-steps line. Nothing tests the main-flow message choice.
- P9-export-dropped (`export PREPR_SKIP_CODE PREPR_SKIP_CLOSURES` deleted): SURVIVED. Either the export is unneeded (then delete it), or a child depends on it (then pin it).

A fix that pins all of these: add one end-to-end arm per direction against a fixture roster, covering `hotfix_class` → `gate_priority.py --hotfix --ref <fixture> --no-fetch` for the hotfix branch (expects 1) and for an outside, a critical and an unmapped branch (expects 0). Add a gate_priority self-test arm that calls `main(["--hotfix", ...])` and checks stdout, and one that makes `show_roster` raise (for example a malformed roster file at the ref) and asserts `is_hotfix` is False. The null control (a comment-only edit) survived, as it should.

## Evidence

- RESULT prepr self-test head: `bash tools/pr/prepr.sh --self-test` printed 548 passed, 0 failed, exit 0 (`ev/selftest-head.log`). At the base 7eadd75f it printed 542 passed, 0 failed (`ev/selftest-base.log`). The difference is the 6 new arms, which matches the body's base figure of 544 passed + 4 failed with the arms present.
- RESULT gate_priority self-test head: 17 checks, 0 failed (`ev/gate_priority-head.log`), as the body states.
- RESULT structure: `python3 tests/structure.py` at the head printed STRUCTURE RATCHET PASSED, exit 0 (`ev/structure-head.log`). The diff touches no budget file.
- RESULT merge: `git merge-tree --write-tree origin/main a81d7f15` exited 0, with no conflict (`ev/merge-tree.txt`).
- RESULT CI: `merge_train.py classify a81d7f15 --pr 3547` printed `GREEN a81d7f15293fc2101f42e48ade37ef7022c35517 pending: none red: none`, rc 0 (`ev/classify.txt`). No red, so no `## Red checks` answer is owed.
- RESULT mutants: G1, G2, G4 (gate_priority) and P1–P6 (prepr) were killed. G3, G5, G5b, P7, P8 and P9 survived, and the NULL control survived. The body's M1–M7 correspond to P1, P2, P3, P4, G1, P5 and P6, and all were killed again here.
- VERSION, the manifest, RELEASE_NOTES.md and tests/golden are untouched (the three-dot diff is empty for those paths). No claim file is touched, and no fixture can move, because the diff is instruments-only.
- Live CLI at the head: `gate_priority.py --hotfix --branch fix/r10-prepr-residue-p2` prints 0. The roster has exactly one `"class": "hotfix"` group (R10-NIGHTLY-SLOW-ROLLING), per a scout grep of `dev/programme/rosters/`.
- Finder's harness: the packet reads "none named". This is an owner-instruction carry (Carry 21) with no audit harness, and the class is one seam (the hotfix default in prepr), so there is no enumeration rule to run.
- Not re-derived: the body's "28 s" wall clock for a scoped run at the merge base, and the carry's "about 40 minutes" figure (the body itself marks that one as not re-measured).
- tests/entities.py was not run: it needs `homeassistant`, which this cloud venv lacks. CI's green `tests / closure-scope` and `tests / fast (3.14)` stand for it at this head.
- The reviewer built the mutation driver (`ev/driver.py`); it is not the finder's.

## Delta diff: git diff a81d7f15293fc2101f42e48ade37ef7022c35517 b53bbf1604a3720aeb665a3b51219eb54df1fe6a
diff --git a/tests/closures.json b/tests/closures.json
index 6856968673..47873cb139 100644
--- a/tests/closures.json
+++ b/tests/closures.json
@@ -5167,7 +5167,7 @@
    "seconds": 0.2
   },
   "tests/harness_headers.py": {
-   "rc": 1,
+   "rc": 0,
    "seconds": 118.2
   },
   "tests/layout.py": {
diff --git a/tools/pr/gate_priority.py b/tools/pr/gate_priority.py
index 22160c837e..f793091d6b 100644
--- a/tools/pr/gate_priority.py
+++ b/tools/pr/gate_priority.py
@@ -43,6 +43,8 @@ absent or malformed file means no group is critical.
 from __future__ import annotations
 
 import argparse
+import contextlib
+import io
 import os
 import subprocess
 import sys
@@ -266,6 +268,45 @@ def _self_test() -> int:
         check("is_hotfix ignores the lease override and fails closed (False) on a failed fetch",
               not is_hotfix("handoff/r10-other", repo=str(repo), ref=live, fetch=False)
               and not is_hotfix("handoff/r10-hot", repo=str(repo), fetch=True))
+
+        def cli(branch: str) -> tuple[int, str]:
+            """``main(["--hotfix", ...])`` and its stdout: the line prepr's hotfix_class reads."""
+            buf = io.StringIO()
+            with contextlib.redirect_stdout(buf):
+                rc = main(["--hotfix", "--branch", branch, "--repo", str(repo),
+                           "--ref", live, "--no-fetch"])
+            return rc, buf.getvalue()
+
+        hot_out_crit_none = ("handoff/r10-hot", "handoff/r10-out", "handoff/r10-crit", "fix/none")
+        check("--hotfix prints 1 for the hotfix group's branch, 0 for an outside, a critical and an unmapped one",
+              [cli(b) for b in hot_out_crit_none] == [(0, "1\n"), (0, "0\n"), (0, "0\n"), (0, "0\n")],
+              [cli(b) for b in hot_out_crit_none])
+
+        # The except arm: a roster read that raises (not a failed fetch, which returns
+        # before the read) must fail closed -- not a hotfix, so a full prepr; priority 0.
+        def hot_answers() -> tuple[bool, int, tuple[int, str]]:
+            return (is_hotfix("handoff/r10-hot", repo=str(repo), ref=live, fetch=False),
+                    derived("handoff/r10-hot"), cli("handoff/r10-hot"))
+
+        real_show = roster_lib.show_roster
+
+        def unreadable(*_a, **_k):
+            raise ValueError("fixture: an unreadable roster")
+
+        roster_lib.show_roster = unreadable
+        try:
+            raised = hot_answers()
+        finally:
+            roster_lib.show_roster = real_show
+        check("a roster read that raises fails closed: not a hotfix, priority 0, --hotfix prints 0",
+              raised == (False, 0, (0, "0\n")), raised)
+        check("null control: the same read, restored, is (True, 2, '1')",
+              hot_answers() == (True, 2, (0, "1\n")), hot_answers())
+        check("the default is the fetched live read: with no origin to fetch, the hotfix branch fails closed",
+              not is_hotfix("handoff/r10-hot", repo=str(repo))
+              and derived_priority("handoff/r10-hot", repo=str(repo)) == 0
+              and is_hotfix("handoff/r10-hot", repo=str(repo), fetch=False),
+              (is_hotfix("handoff/r10-hot", repo=str(repo)), derived_priority("handoff/r10-hot", repo=str(repo))))
         check("a group that resolves but is not listed stays normal (null control)",
               derived("handoff/r10-other") == 0, derived("handoff/r10-other"))
         check("a branch that maps to no group stays normal",
diff --git a/tools/pr/prepr.sh b/tools/pr/prepr.sh
index 0425c71018..ba63727c3c 100755
--- a/tools/pr/prepr.sh
+++ b/tools/pr/prepr.sh
@@ -1767,19 +1767,25 @@ merged_steps() { # body, unpinned-site key file -> step lines
 # UNSET variable takes the default: a caller's value, set empty included, wins per variable.
 # The scope is code and closures; the merged-tree structure ratchet, ci predict and the body
 # and contract checks (`merged_steps`, steps 1a-1a3, 6, 7) stay, as under any PREPR_SKIP_CODE.
+# The defaults are not exported: only this shell reads them, and a child (the self-test step,
+# a merged-tree command) must not inherit a skip the roster chose for this run alone.
 hotfix_class() { # branch -> 1 when the roster classes its group a hotfix, else 0
   python3 tools/pr/gate_priority.py --hotfix --branch "$1" 2>/dev/null
 }
-hotfix_scope() { # branch -> exports the unset skips; prints one line when it scoped
+hotfix_scope() { # branch -> sets the unset skips (this shell's, never exported); prints one line when it scoped
   if [ -n "${PREPR_SKIP_CODE+x}" ] && [ -n "${PREPR_SKIP_CLOSURES+x}" ]; then return 0; fi
   [ "$(hotfix_class "$1")" = 1 ] || return 0
   HOTFIX_SCOPED=1
   [ -n "${PREPR_SKIP_CODE+x}" ] || PREPR_SKIP_CODE=hotfix
   [ -n "${PREPR_SKIP_CLOSURES+x}" ] || PREPR_SKIP_CLOSURES=1
-  export PREPR_SKIP_CODE PREPR_SKIP_CLOSURES
   say ok "hotfix scope" "$1 is a hotfix group's branch: code and closure steps skipped; merged structure, ci predict, body and contract checks run (a caller's PREPR_SKIP_CODE / PREPR_SKIP_CLOSURES, set empty included, wins)"
 }
 
+code_steps_line() { # REUSE -> the main flow's code-steps line; HOTFIX_SCOPED names the roster's default
+  if [ -n "${HOTFIX_SCOPED:-}" ] && [ "$1" = hotfix ]; then say ok "code steps" "hotfix scope: no heavy slot, and the steps keyed to the code alone are dropped"
+  elif [ -n "$1" ]; then say ok "code steps" "reused from the receipt at ${1:0:12}: no heavy slot, and the steps keyed to the code alone are dropped"; fi
+}
+
 selftest_owed() { # changed-paths file -> 0 when a changed path is a self-test input
   awk 'NR==FNR { if ($0 ~ /\/$/) d[$0]=1; else f[$0]=1; next }
        ($0 in f) { hit=1; exit }
@@ -1936,6 +1942,10 @@ selftest_tmp_root() {
 # (merge base, gate mode, version edit, claim files) are demonstrated by the
 # `pr-contract` job running this script on every pull request.
 if [ "${1:-}" = "--self-test" ]; then
+  # The rows set or leave unset these two themselves; a caller exporting one
+  # (update_pr.sh exports PREPR_SKIP_CLOSURES=1) must not reach a fixture child
+  # shell, where an assignment to an exported name keeps it exported.
+  unset PREPR_SKIP_CODE PREPR_SKIP_CLOSURES
   # Every throwaway repository below takes the shared helper: auto-maintenance
   # off and no inherited git config (R9-RCA-stamp-race). The cwd is the top level.
   . tests/throwaway_git.sh || exit 2
@@ -4143,18 +4153,47 @@ exit $rc'*) r=0 ;; *) r=1 ;; esac
   st "$([ -f "$(git -C "$RQ/wt" rev-parse --absolute-git-dir)/hpo-prepr-receipt" ] && echo left)" "" "(a) a run with a body removes an earlier receipt first, so one that writes none leaves none"
   # Carry 21: a hotfix group's branch defaults to the scoped run, decided once from the
   # roster's class (`hotfix_class`, gate_priority.py --hotfix), never from the branch name.
-  hs() { # classifier answer -> "<scope line>|<PREPR_SKIP_CODE>|<PREPR_SKIP_CLOSURES>", the caller's env as set
+  # hs: the main flow's own sequence (hotfix_scope, then REUSE and code_steps_line) under a
+  # stubbed classifier. Each say prints "<label>=<message up to its first colon>;"; then the
+  # two skips as this shell holds them, and as a child process sees them (never exported).
+  hs() { # classifier answer -> "<say lines>|<CODE>|<CLOSURES>|<child CODE>,<child CLOSURES>"
     local cls=$1
     ( hotfix_class() { printf '%s' "$cls"; }
-      say() { printf '%s' "$2"; }
+      say() { printf '%s=%s;' "$2" "${3%%:*}"; }
+      HOTFIX_SCOPED=""
       hotfix_scope fix/any
-      printf '|%s|%s' "${PREPR_SKIP_CODE-unset}" "${PREPR_SKIP_CLOSURES-unset}" )
+      code_steps_line "${PREPR_SKIP_CODE:-}"
+      printf '|%s|%s|%s' "${PREPR_SKIP_CODE-unset}" "${PREPR_SKIP_CLOSURES-unset}" \
+        "$(bash -c 'printf "%s,%s" "${PREPR_SKIP_CODE-unset}" "${PREPR_SKIP_CLOSURES-unset}"')" )
   }
-  st "$( (unset PREPR_SKIP_CODE PREPR_SKIP_CLOSURES; hs 1) )" "hotfix scope|hotfix|1" "(hotfix) a roster-classed hotfix branch prints the scope line and defaults both skips on"
-  st "$( (unset PREPR_SKIP_CODE PREPR_SKIP_CLOSURES; hs 0) )" "|unset|unset" "(hotfix) null control: a non-hotfix branch prints nothing and sets neither skip"
-  st "$( (unset PREPR_SKIP_CLOSURES; PREPR_SKIP_CODE=; hs 1) )" "hotfix scope||1" "(hotfix) an explicit empty PREPR_SKIP_CODE (a full code run) wins; the closures default stays"
-  st "$( (unset PREPR_SKIP_CODE; PREPR_SKIP_CLOSURES=; hs 1) )" "hotfix scope|hotfix|" "(hotfix) an explicit empty PREPR_SKIP_CLOSURES wins; the code default stays"
-  st "$( (PREPR_SKIP_CODE=abc; PREPR_SKIP_CLOSURES=x; hs 1) )" "|abc|x" "(hotfix) explicit values pass through unchanged and, both set, nothing is printed"
+  HSL="hotfix scope=fix/any is a hotfix group's branch;"
+  st "$( (unset PREPR_SKIP_CODE PREPR_SKIP_CLOSURES; hs 1) )" "${HSL}code steps=hotfix scope;|hotfix|1|unset,unset" "(hotfix) a roster-classed hotfix branch prints the scope line and the hotfix code-steps line (never a receipt claim), and defaults both skips on in this shell only"
+  st "$( (unset PREPR_SKIP_CODE PREPR_SKIP_CLOSURES; hs 0) )" "|unset|unset|unset,unset" "(hotfix) null control: a non-hotfix branch prints nothing and sets neither skip"
+  st "$( (unset PREPR_SKIP_CODE PREPR_SKIP_CLOSURES; PREPR_SKIP_CODE=; hs 1) )" "${HSL}||1|unset,unset" "(hotfix) an explicit empty PREPR_SKIP_CODE (a full code run) wins; the closures default stays"
+  st "$( (unset PREPR_SKIP_CODE PREPR_SKIP_CLOSURES; PREPR_SKIP_CLOSURES=; hs 1) )" "${HSL}code steps=hotfix scope;|hotfix||unset,unset" "(hotfix) an explicit empty PREPR_SKIP_CLOSURES wins; the code default stays"
+  st "$( (export PREPR_SKIP_CODE=abc PREPR_SKIP_CLOSURES=x; hs 1) )" "code steps=reused from the receipt at abc;|abc|x|abc,x" "(hotfix) explicit values pass through unchanged and, both set, no scope line; a caller's own value is still a receipt reuse"
+  # End to end, the seam the stub above skips: hotfix_class runs the real
+  # gate_priority.py --hotfix against a fixture roster published as a local origin, so
+  # the CLI's answer and the flag prepr passes are both under test. Only the hotfix
+  # group's branch answers 1; an outside, a critical-path, a plain and an unmapped
+  # branch answer 0 (gate priority would give the first two 1 and the hotfix 2).
+  HC=$(mktemp -d)
+  ( set -e; throwaway_git_env; cd "$HC"; throwaway_git_init . -q -b main
+    export GIT_AUTHOR_NAME=st GIT_AUTHOR_EMAIL=st@st GIT_COMMITTER_NAME=st GIT_COMMITTER_EMAIL=st@st
+    mkdir -p dev/programme/rosters
+    printf '%s\n' '{"groups": [{"group": "R10-HOT", "kind": "bug", "resume": {"branch": "handoff/r10-hot"}},
+      {"group": "R10-OUT", "source": "outside", "resume": {"branch": "handoff/r10-out"}},
+      {"group": "R10-CRIT", "resume": {"branch": "handoff/r10-crit"}},
+      {"group": "R10-OTHER", "resume": {"branch": "handoff/r10-other"}}]}' > dev/programme/rosters/wave-r10-groups.json
+    printf '%s\n' '{"at": "2026-10-20T00:00:00Z", "critical": ["R10-CRIT"]}' > dev/programme/rosters/critical-path.json
+    git add -A; git commit -q -m roster
+    git branch handoff/audit-r10-roster
+    git remote add origin "$HC"; git fetch -q origin ) >/dev/null 2>&1
+  ln -s "$PWD/tools" "$HC/tools"
+  hcl() { (cd "$HC" && for b in handoff/r10-hot handoff/r10-out handoff/r10-crit handoff/r10-other fix/none; do printf '%s ' "$(hotfix_class "$b")"; done); }
+  st "$(hcl)" "1 0 0 0 0 " "(hotfix) end to end: hotfix_class answers 1 for the roster's hotfix group only, through gate_priority.py --hotfix"
+  st "$(cd "$HC" && unset HPO_GATE_PRIORITY && python3 tools/pr/gate_priority.py --branch handoff/r10-hot; python3 tools/pr/gate_priority.py --branch handoff/r10-out)" "$(printf '2\n1')" "(hotfix) null control: the same fixture's lease priority is 2 and 1, so the 1 / 0 above is the class, not the priority"
+  rm -rf "$HC"
   st "$(awk '/^hotfix_scope "\$\(git rev-parse --abbrev-ref HEAD/{a=NR} /^REUSE=/{b=NR} END{print (a>0 && b>a) ? "ok" : "late"}' "$PREPR_PATH")" ok "(hotfix) the main flow decides the scope once, before REUSE is read from PREPR_SKIP_CODE"
   rm -rf "$RQ"
 
@@ -4231,8 +4270,7 @@ summary_start
 HOTFIX_SCOPED=""
 hotfix_scope "$(git rev-parse --abbrev-ref HEAD 2>/dev/null)"
 REUSE=${PREPR_SKIP_CODE:-}
-if [ -n "$HOTFIX_SCOPED" ] && [ "$REUSE" = hotfix ]; then say ok "code steps" "hotfix scope: no heavy slot, and the steps keyed to the code alone are dropped"
-elif [ -n "$REUSE" ]; then say ok "code steps" "reused from the receipt at ${REUSE:0:12}: no heavy slot, and the steps keyed to the code alone are dropped"; fi
+code_steps_line "$REUSE"
 
 # --- 1a. no transport file in any commit the branch adds (`transport_in_ancestry`).
 TRANSPORT=$(transport_in_ancestry "$BASE" HEAD)

## Before you return the verdict (P275)
Run `python3 -I tools/audit/carry_audit.py check --body <PR body file> --comments <file holding [{"id": 0, "body": <verdict.md text>}]>`. Give every reported item its own `Carry: <GROUP> | #<issue> | O<n> | dismissed: <reason>`;
an evidence line flagged by its wording takes `Carry: dismissed: evidence, not a finding`. Return the verdict only at rc 0.
