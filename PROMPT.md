CLOUD REVIEWER seat for PR #3547 of tvofi/heatpump_optimizer, at head b53bbf1604a3720aeb665a3b51219eb54df1fe6a. Bus nonce: 0e95d2f4c4f3b1c47cd67488e8b3a383. Never send push notifications. Write no Claude Code footer, no Co-Authored-By or Claude-Session trailer and no claude.ai session link in any commit, pull-request body or comment you produce; check your commits with `git log --format=%B` before pushing.
Setup: `git fetch --unshallow --tags origin`. The session-start `toolchain:` line says whether venv-ci's python3 is on PATH: on REFUSE, start each Bash call with `eval "$(bash .claude/hooks/session-start.sh --env-lines)"`. Then run `bash tools/audit/seat/cloud-setup.sh --check`, and on REFUSE stop: report its line as your result and start no work. Run anything heavy in the background with Monitor and no timeout. Never wait in one tool call longer than 240 s; poll again instead. Read your policy once, verbatim: `python3 -I tools/policy/role_pack.py render fix-review --out $HOME/role-pack.md`, then that file in place of your role contract and INSTRUMENTS.md; on REFUSE read those files as before.
Role: read dev/governance/roles/fix-review.md and its rules from main, and follow them exactly. Fetch the PR head with `git fetch origin b53bbf1604a3720aeb665a3b51219eb54df1fe6a`; the PR body is in the PR. Start from the review packet, which you render here rather than read from the dispatcher, whose copy is a path on its own machine: `python3 -I tools/audit/seat/review_packet.py render --pr 3547 --head b53bbf1604a3720aeb665a3b51219eb54df1fe6a --reviewed-head a81d7f15293fc2101f42e48ade37ef7022c35517 --out $HOME/review-packet.md`. A refusal names its signal and the packet is still written unless the signal is `host-path`; re-read the live checks either way. This is a later round over the reviewed head a81d7f15293fc2101f42e48ade37ef7022c35517: its scope is the packet's `## Review scope` line, the delta and the previous verdict's findings when it reads `delta`, widened only to the exact already-reviewed code a production (custom_components/) delta puts at non-obvious risk that CI would not detect, the verdict naming path and risk; an instrument, test, policy or body delta never widens it (fix-review.md step 12). Verify each claim adversarially: mutate the fix and check the tests fail, and check every figure in the body at this head. Check that it merges with origin/main (`git merge-tree --write-tree origin/main <head>`); block on main only when that reports a conflict, never on a head that is behind main but merges cleanly (the train re-proves it on the current main). Wait for CI on this head only by re-running `python3 tools/audit/seat/merge_train.py classify b53bbf1604a3720aeb665a3b51219eb54df1fe6a --pr 3547` in the background, at least 60 s between runs, until it exits 0 (GREEN), 1 (RED), 2 (unreadable: say so in the verdict) or 4 (APPROVAL-OWED: the only red is the budget raise's approval, which follows your verdict; judge the head as GREEN and quote the line); 3 is WAIT, so run it again. Never wait with `pgrep` or `pkill`, whose `-f` pattern matches the waiter's own command line, nor on a context the ruleset does not require, such as `prelude`. A review_packet `required-red` signal does not stop you while classify prints WAIT: classify decides. If your review is otherwise complete and classify still prints WAIT after about 30 minutes of polling, stop waiting: put the line `pending-ci: <the context names it printed>` straight after the `bus-nonce:` line and return the verdict as below; the relay posts it once CI is green at this head, refuses it over a red, and refuses it if the head moves. If the review is not complete then, push `Fix review: blocked b53bbf1604a3720aeb665a3b51219eb54df1fe6a ci-wait: <the last classify line>` as below.
Output: in a fresh directory of your own (`W=$(mktemp -d)`), write verdict.md, whose first line is exactly `Fix review: merge b53bbf1604a3720aeb665a3b51219eb54df1fe6a` or `Fix review: blocked b53bbf1604a3720aeb665a3b51219eb54df1fe6a <class>: <reason>` (no brackets; the class is lower-case letters and dashes), in the format the role file gives, then a blank line, then `bus-nonce: 0e95d2f4c4f3b1c47cd67488e8b3a383`, then the body in sections. A blocked verdict's block goes under `## Block`. Each finding this PR does not settle (a defect, a surviving mutant, a deferral, a follow-up, a task owed after the merge) is its own bullet under `## Findings` ending in its own `Carry: <GROUP> | #<issue> | O<n> | dismissed: <reason>` (finding-propagation.md). Everything else (RESULT lines, re-runs, CI state, figures you could not re-derive) goes under `## Evidence`: tools/audit/carry_audit.py reads an item there, and under any heading of a merge verdict but `## Findings`, `## Friction`, a block heading and a note heading (Residuals, Follow-ups, Notes ...), by its shape alone: a finding only when it opens with a lead word (Residual:, Follow-up:, Out of scope: ...) or carries a `Carry:`, so a defect you hand on goes under `## Findings`, and bus.sh refuses a verdict holding a finding with no valid `Carry:`. Put the evidence files in `ev/` beside it, under 25 MB in all (cite a large log by path and keep its tail: a ~30 MB ev/ once failed its push), and make at least one file under `ev/` contain the full 40-hex head `b53bbf1604a3720aeb665a3b51219eb54df1fe6a` (e.g. `ev/HEAD.txt` holding the head you reviewed, beside your command output): bus.sh refuses a verdict whose `ev/` names no head. Do NOT run bus.sh: its dispatch record lives on the orchestrator's machine, which publishes the verdict there (cloud_relay.sh). Return the verdict on a probe ref, and push nothing else; this builds one parentless commit with a private index and touches no branch of your checkout: `R=$(git rev-parse --show-toplevel); G=$(git rev-parse --absolute-git-dir); mkdir -p $W/pr && cp -r $W/verdict.md $W/ev $W/pr/ && cd $W/pr && T=$(GIT_DIR=$G GIT_INDEX_FILE=$W/idx GIT_WORK_TREE=$W/pr sh -c 'git add -A -f . && git write-tree') && C=$(GIT_DIR=$G git -c user.name=hpo-fixer -c user.email=70032254+tvofi@users.noreply.github.com commit-tree $T -m "verdict 3547 b53bbf1604a3720aeb665a3b51219eb54df1fe6a") && git -C $R push -q origin $C:refs/heads/probe/rev-3547-0e95d2f4`. That ref is the return signal. Do not post comments, approve or merge.
Every way your turn ends pushes a verdict to that ref: a setup or hook refusal that stops you pushes `Fix review: blocked b53bbf1604a3720aeb665a3b51219eb54df1fe6a seat-refused: <the refusing line>`; never end your turn while a background poll runs. After the push, read the ref back with `git ls-remote origin refs/heads/probe/rev-3547-0e95d2f4`, and push again if it does not print your commit.
A red is owed a `## Red checks` answer, and may block, only when its name is in the set `python3 tools/audit/seat/merge_train.py owed-reds` prints (defect-root-cause.md); any other red is neither answered nor a block.
Never write to any branch except your return refs. Never work around a hook or a refusal; report it in your result instead.
Discovery reads (search, list, read across files) go through Agent subagents, as the frugal routing guard requires: when it refuses inline work, dispatch a haiku or sonnet Agent subagent to do it rather than bypassing the guard; never set FRUGAL_ALLOW_INLINE and never edit .claude/settings.json.

Brief (snapshotted when this payload was rendered):
# Review packet #3547
head: b53bbf1604a3720aeb665a3b51219eb54df1fe6a
base: 7eadd75f3c420404aabc83d4b05f9691f3e49136

Start here (fix-review.md). Re-read the live check state before a verdict: the digest is as read at render.

## Gate digest: pending
arm id=132067628550 skipped
cancel-superseded id=132067657388 queued
prelude id=132067657029 queued
refresh id=132067657445 queued

## Refusals
none

## Advisories
none

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

## Review scope: full (first round: no --reviewed-head)

## Three-dot diff
diff --git a/dev/programme/delivery/3547.md b/dev/programme/delivery/3547.md
new file mode 100644
index 0000000000..b5e6556753
--- /dev/null
+++ b/dev/programme/delivery/3547.md
@@ -0,0 +1 @@
+- [#3547](https://github.com/tvofi/heatpump_optimizer/pull/3547) — **open**, R10-PREPR-RESIDUE (part 2): r10 prepr residue p2 (R10-PREPR-RESIDUE)
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
index 093cb52ba9..f793091d6b 100644
--- a/tools/pr/gate_priority.py
+++ b/tools/pr/gate_priority.py
@@ -3,6 +3,7 @@
 
     python3 tools/pr/gate_priority.py              # HEAD's branch, live roster
     python3 tools/pr/gate_priority.py --branch B    # an explicit branch
+    python3 tools/pr/gate_priority.py --hotfix      # prints 1 when the group is a hotfix, else 0
     python3 tools/pr/gate_priority.py --self-test   # hermetic fixtures
 
 The lease (``tests/gate_lock.py``) is generic: it orders waiters by an integer
@@ -42,6 +43,8 @@ absent or malformed file means no group is critical.
 from __future__ import annotations
 
 import argparse
+import contextlib
+import io
 import os
 import subprocess
 import sys
@@ -99,35 +102,50 @@ def _roster_ref(repo: str) -> str | None:
     return ref
 
 
-def derived_priority(branch: str, *, repo: str = ".", ref: str | None = None,
-                     fetch: bool = True) -> int:
-    """2 for a hotfix group, 1 for an outside group or one in the
-    critical-path set at the roster ref (a missing or malformed set drops only
-    the critical path's 1; an outside group still answers 1).
-
-    0 for every other answer, including every failure. ``ref`` overrides the
-    live roster ref (the self-test's fixture); ``fetch=False`` reads the local
-    ref without refreshing it.
-    """
+def _rank(branch: str, *, repo: str, ref: str | None, fetch: bool) -> int | None:
+    """The roster dispatch rank of the branch's group, None on any failure."""
     try:
         roster_ref = ref
         if roster_ref is None:
             roster_ref = _roster_ref(repo) if fetch else roster_lib.reader_ref(repo, None)
         if roster_ref is None:
-            return PRIORITY_NORMAL
-        group = roster_lib.group_for_branch(
-            roster_lib.show_roster(repo, roster_ref), branch)
-        if group is None:
-            return PRIORITY_NORMAL
+            return None
         roster = roster_lib.show_roster(repo, roster_ref)
+        group = roster_lib.group_for_branch(roster, branch)
+        if group is None:
+            return None
         critical = roster_lib.critical_path_groups(repo, roster_ref)
         if critical is None:
             critical = set()
-        rank = roster_lib.dispatch_rank(roster, group, critical)
-        return {roster_lib.RANK_HOTFIX: HOTFIX_PRIORITY,
-                roster_lib.RANK_TOP: TOP_PRIORITY}.get(rank, PRIORITY_NORMAL)
+        return roster_lib.dispatch_rank(roster, group, critical)
     except Exception:  # noqa: BLE001 -- a pre-pr helper must never crash a run
-        return PRIORITY_NORMAL
+        return None
+
+
+def derived_priority(branch: str, *, repo: str = ".", ref: str | None = None,
+                     fetch: bool = True) -> int:
+    """2 for a hotfix group, 1 for an outside group or one in the
+    critical-path set at the roster ref (a missing or malformed set drops only
+    the critical path's 1; an outside group still answers 1).
+
+    0 for every other answer, including every failure. ``ref`` overrides the
+    live roster ref (the self-test's fixture); ``fetch=False`` reads the local
+    ref without refreshing it.
+    """
+    rank = _rank(branch, repo=repo, ref=ref, fetch=fetch)
+    return {roster_lib.RANK_HOTFIX: HOTFIX_PRIORITY,
+            roster_lib.RANK_TOP: TOP_PRIORITY}.get(rank, PRIORITY_NORMAL)
+
+
+def is_hotfix(branch: str, *, repo: str = ".", ref: str | None = None,
+              fetch: bool = True) -> bool:
+    """True only when the roster classes the branch's group a hotfix.
+
+    The derived class alone: ``$HPO_GATE_PRIORITY`` and ``.gate-priority`` order
+    the lease and say nothing about the group. Every failure is False, so an
+    unreadable roster yields the full pre-PR run, never a skipped one.
+    """
+    return _rank(branch, repo=repo, ref=ref, fetch=fetch) == roster_lib.RANK_HOTFIX
 
 
 def _declared(raw: str | None) -> int | None:
@@ -243,6 +261,52 @@ def _self_test() -> int:
               [derived(b, at=plain_sha) for b in ("handoff/r10-crit", "handoff/r10-other", "fix/none")] == [1, 0, 0],
               [derived(b, at=plain_sha) for b in ("handoff/r10-crit", "handoff/r10-other", "fix/none")])
         (rosters / "wave-r10-groups.json").write_text(json.dumps(roster))
+        check("is_hotfix: true for the hotfix group only; an outside, a critical and an unmapped branch are not",
+              [is_hotfix(b, repo=str(repo), ref=live, fetch=False) for b in
+               ("handoff/r10-hot", "handoff/r10-out", "handoff/r10-crit", "handoff/r10-other", "fix/none")]
+              == [True, False, False, False, False])
+        check("is_hotfix ignores the lease override and fails closed (False) on a failed fetch",
+              not is_hotfix("handoff/r10-other", repo=str(repo), ref=live, fetch=False)
+              and not is_hotfix("handoff/r10-hot", repo=str(repo), fetch=True))
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
@@ -292,11 +356,16 @@ def main(argv: list[str] | None = None) -> int:
                         help="roster ref override, for fixtures (default: the live one)")
     parser.add_argument("--no-fetch", action="store_true",
                         help="read the local roster ref without refreshing it")
+    parser.add_argument("--hotfix", action="store_true",
+                        help="print 1 when the roster classes the branch's group a hotfix, else 0")
     parser.add_argument("--self-test", action="store_true")
     args = parser.parse_args(argv)
     if args.self_test:
         return _self_test()
     branch = args.branch if args.branch is not None else _current_branch(args.repo)
+    if args.hotfix:
+        print(int(is_hotfix(branch, repo=args.repo, ref=args.ref, fetch=not args.no_fetch)))
+        return 0
     print(priority_for_branch(branch, repo=args.repo, ref=args.ref,
                               fetch=not args.no_fetch))
     return 0
diff --git a/tools/pr/prepr.sh b/tools/pr/prepr.sh
index e0ffdff44d..ba63727c3c 100755
--- a/tools/pr/prepr.sh
+++ b/tools/pr/prepr.sh
@@ -1759,6 +1759,33 @@ merged_steps() { # body, unpinned-site key file -> step lines
   esac
 }
 
+# A hotfix group's branch runs the scoped prepr by default (tvofi, 2026-11-09: "hotfixes should
+# have aggressively scoped or no prepr"; the main de.json hotfix spent about 40 min in a full
+# one while 7 PRs waited). The class is the roster's, through gate_priority.py's own
+# derivation of the group's dispatch rank -- the one the gate lease already trusts -- so a
+# branch name alone never decides it, and an unreadable roster answers 0, a full run. Only an
+# UNSET variable takes the default: a caller's value, set empty included, wins per variable.
+# The scope is code and closures; the merged-tree structure ratchet, ci predict and the body
+# and contract checks (`merged_steps`, steps 1a-1a3, 6, 7) stay, as under any PREPR_SKIP_CODE.
+# The defaults are not exported: only this shell reads them, and a child (the self-test step,
+# a merged-tree command) must not inherit a skip the roster chose for this run alone.
+hotfix_class() { # branch -> 1 when the roster classes its group a hotfix, else 0
+  python3 tools/pr/gate_priority.py --hotfix --branch "$1" 2>/dev/null
+}
+hotfix_scope() { # branch -> sets the unset skips (this shell's, never exported); prints one line when it scoped
+  if [ -n "${PREPR_SKIP_CODE+x}" ] && [ -n "${PREPR_SKIP_CLOSURES+x}" ]; then return 0; fi
+  [ "$(hotfix_class "$1")" = 1 ] || return 0
+  HOTFIX_SCOPED=1
+  [ -n "${PREPR_SKIP_CODE+x}" ] || PREPR_SKIP_CODE=hotfix
+  [ -n "${PREPR_SKIP_CLOSURES+x}" ] || PREPR_SKIP_CLOSURES=1
+  say ok "hotfix scope" "$1 is a hotfix group's branch: code and closure steps skipped; merged structure, ci predict, body and contract checks run (a caller's PREPR_SKIP_CODE / PREPR_SKIP_CLOSURES, set empty included, wins)"
+}
+
+code_steps_line() { # REUSE -> the main flow's code-steps line; HOTFIX_SCOPED names the roster's default
+  if [ -n "${HOTFIX_SCOPED:-}" ] && [ "$1" = hotfix ]; then say ok "code steps" "hotfix scope: no heavy slot, and the steps keyed to the code alone are dropped"
+  elif [ -n "$1" ]; then say ok "code steps" "reused from the receipt at ${1:0:12}: no heavy slot, and the steps keyed to the code alone are dropped"; fi
+}
+
 selftest_owed() { # changed-paths file -> 0 when a changed path is a self-test input
   awk 'NR==FNR { if ($0 ~ /\/$/) d[$0]=1; else f[$0]=1; next }
        ($0 in f) { hit=1; exit }
@@ -1915,6 +1942,10 @@ selftest_tmp_root() {
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
@@ -4120,6 +4151,50 @@ exit $rc'*) r=0 ;; *) r=1 ;; esac
   st "$(printf '%s\n' "$RA" | grep -cE '^  [a-zA-Z]+ +(heavy slot|policy_lint|self-test|agreement lane|gate priority) ')$(printf '%s\n' "$RA" | grep -c '^  ok  *code steps  ')" 01 "(a) a PREPR_SKIP_CODE run takes no heavy slot and drops the code-keyed steps"
   st "$(printf '%s\n' "$RA" | grep -cE '^  [a-zA-Z]+ +merged structure ')$(printf '%s\n' "$RA" | grep -cE '^  [a-zA-Z]+ +ci predict ')" 11 "(a) and runs tests/structure.py and ci predict on HEAD merged with main, once each"
   st "$([ -f "$(git -C "$RQ/wt" rev-parse --absolute-git-dir)/hpo-prepr-receipt" ] && echo left)" "" "(a) a run with a body removes an earlier receipt first, so one that writes none leaves none"
+  # Carry 21: a hotfix group's branch defaults to the scoped run, decided once from the
+  # roster's class (`hotfix_class`, gate_priority.py --hotfix), never from the branch name.
+  # hs: the main flow's own sequence (hotfix_scope, then REUSE and code_steps_line) under a
+  # stubbed classifier. Each say prints "<label>=<message up to its first colon>;"; then the
+  # two skips as this shell holds them, and as a child process sees them (never exported).
+  hs() { # classifier answer -> "<say lines>|<CODE>|<CLOSURES>|<child CODE>,<child CLOSURES>"
+    local cls=$1
+    ( hotfix_class() { printf '%s' "$cls"; }
+      say() { printf '%s=%s;' "$2" "${3%%:*}"; }
+      HOTFIX_SCOPED=""
+      hotfix_scope fix/any
+      code_steps_line "${PREPR_SKIP_CODE:-}"
+      printf '|%s|%s|%s' "${PREPR_SKIP_CODE-unset}" "${PREPR_SKIP_CLOSURES-unset}" \
+        "$(bash -c 'printf "%s,%s" "${PREPR_SKIP_CODE-unset}" "${PREPR_SKIP_CLOSURES-unset}"')" )
+  }
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
+  st "$(awk '/^hotfix_scope "\$\(git rev-parse --abbrev-ref HEAD/{a=NR} /^REUSE=/{b=NR} END{print (a>0 && b>a) ? "ok" : "late"}' "$PREPR_PATH")" ok "(hotfix) the main flow decides the scope once, before REUSE is read from PREPR_SKIP_CODE"
   rm -rf "$RQ"
 
   printf '\n%s passed, %s failed\n' "$st_pass" "$st_fail"
@@ -4192,8 +4267,10 @@ summary_start
 # at that code sha was found and the head is its clean merge with the live head
 # and main, so the steps keyed to the code alone are dropped and no heavy slot is
 # taken; the steps keyed to main, the body or the merge still run (`merged_steps`).
+HOTFIX_SCOPED=""
+hotfix_scope "$(git rev-parse --abbrev-ref HEAD 2>/dev/null)"
 REUSE=${PREPR_SKIP_CODE:-}
-[ -z "$REUSE" ] || say ok "code steps" "reused from the receipt at ${REUSE:0:12}: no heavy slot, and the steps keyed to the code alone are dropped"
+code_steps_line "$REUSE"
 
 # --- 1a. no transport file in any commit the branch adds (`transport_in_ancestry`).
 TRANSPORT=$(transport_in_ancestry "$BASE" HEAD)

## Before you return the verdict (P275)
Run `python3 -I tools/audit/carry_audit.py check --body <PR body file> --comments <file holding [{"id": 0, "body": <verdict.md text>}]>`. Give every reported item its own `Carry: <GROUP> | #<issue> | O<n> | dismissed: <reason>`;
an evidence line flagged by its wording takes `Carry: dismissed: evidence, not a finding`. Return the verdict only at rc 0.
