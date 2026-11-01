# Review packet #3065
head: 1ac45d875522d5ab8040f8d89d1f05a7aeadda6d
base: b5df066e7a23e914ee81de83ef243097b3b397a3

Start here (fix-review.md). Re-read the live check state before a verdict: the digest is as read at render.

## Gate digest: red
CodeQL id=124792395542 success
arch-score / arch-score id=124885224358 success
arm id=124792166729 skipped
budget-raise-gate / budget-raise-gate id=124885227696 success
cancel-superseded id=124885213239 success
codeql id=124885189427 skipped
codeql / Analyze (actions) id=124885182497 success
codeql / Analyze (javascript-typescript) id=124885182676 success
codeql / Analyze (python) id=124885214578 success
gate id=124885190055 in_progress
governance id=124885231434 skipped
governance / delivery-status id=124885182822 success
governance / delivery-status-publish id=124885182428 skipped
governance / env-matrix id=124885183682 success
governance / instrument-self-tests id=124885182327 failure
governance / policy-docs id=124885222523 success
governance / record id=124885182615 skipped
governance / wave-script id=124885182776 success
hassfest id=124885229985 skipped
hassfest / hassfest id=124885182511 success
kernel-points id=124885223145 skipped
pr-contract / pr-contract id=124885190160 success
prelude id=124885215943 success
refresh id=124885216270 success
tests id=124885225332 skipped
tests / arch-instrument id=124885183649 success
tests / briefs id=124885221834 success
tests / browser id=124885183592 success
tests / ci-ratchet id=124885183603 skipped
tests / claims-autofix id=124885183772 skipped
tests / closure-scope id=124885227025 success
tests / closures id=124885183607 success
tests / closures-autofix id=124885184345 skipped
tests / coverage id=124885183550 success
tests / coverage-ratchet id=124885184466 success
tests / fast (3.14) id=124885183821 success
tests / graders-head-copy id=124885183824 success
tests / lane-proofs id=124885183861 success
tests / mutation id=124885182443 success
tests / mutation-autofix id=124885184075 skipped
tests / mutation-pins id=124885183368 skipped
tests / nightly-ha id=124885183643 skipped
tests / nightly-status id=124885211738 success
tests / replay id=124885183974 skipped
tests / typing id=124885183587 success
validate id=124885189470 skipped
validate / validate-hacs id=124885225959 success

## Refusals
none

## Advisories
hot-file: HPO_BUS_TRAIN_STATE is unset, so every merge verdict reads unboarded

## carry_audit at the head
NOTE body item 368c1fce: dismissed:evidence line recording verified behaviour (item f2b7b8d4)
NOTE body item 1b2f5911: dismissed:the harness already refuses a dirty file, and a seat that commits during its run is the defect
CARRY-AUDIT: 2 finding item(s): 2 routed, 0 unrouted, 0 bad destination(s)

## figure_lint at the head
ok         tests/structure.py
             `tests/structure.py` is in the tree at this head
  ok         bash tools/audit/seat/tick_loop.sh --self-test
             `tools/audit/seat/tick_loop.sh` is in the tree at this head
  ok         bash tools/audit/seat/cloud_relay.sh --self-test
             `tools/audit/seat/cloud_relay.sh` is in the tree at this head
  ok         bash tools/audit/seat/bus.sh --self-test
             `tools/audit/seat/bus.sh` is in the tree at this head
  ok         python3 tools/audit/carry_audit.py --self-test
             `tools/audit/carry_audit.py` is in the tree at this head
  ok         python3 tools/audit/seat/ref_privacy.py --self-test
             `tools/audit/seat/ref_privacy.py` is in the tree at this head
  ok         python3 tools/audit/seat/queue_pre_flight.py --self-test
             `tools/audit/seat/queue_pre_flight.py` is in the tree at this head
  ok         python3 tools/audit/seat/cloud_dispatch.py --self-test
             `tools/audit/seat/cloud_dispatch.py` is in the tree at this head
  ok         python3 tools/audit/seat/ledger.py --self-test
             `tools/audit/seat/ledger.py` is in the tree at this head
  ok         bash tools/pr/prepr.sh --self-test
             `tools/pr/prepr.sh` is in the tree at this head
  ok         bash tools/pr/prepr.sh <this body>
             `tools/pr/prepr.sh` is in the tree at this head
  ok         bash tools/pr/prepr.sh --body-check <this body>
             `tools/pr/prepr.sh` is in the tree at this head
  ok         python3 dev/audit/harnesses/r10_carry_field_figures.py c5ded0de1 2b6bef745
             `dev/audit/harnesses/r10_carry_field_figures.py` is in the tree at this head
  ok         python3 dev/audit/harnesses/r10_carry_field_figures.py 7539d1675 HEAD
             `dev/audit/harnesses/r10_carry_field_figures.py` is in the tree at this head
  ok         python3 dev/audit/harnesses/r10_carry_parser_mutants.py
             `dev/audit/harnesses/r10_carry_parser_mutants.py` is in the tree at this head
  ok         python3 dev/audit/harnesses/r10_seat_selftests_mutants.py <the ids above>
             `dev/audit/harnesses/r10_seat_selftests_mutants.py` is in the tree at this head
  ok         python3 tests/structure.py
             `tests/structure.py` is in the tree at this head
  ok         python3 tools/audit/archscore/score.py --diff origin/main
             `tools/audit/archscore/score.py` is in the tree at this head
  ok         PYTHONPATH=tests/hastub python3 tools/pr/ci_predict.py --base origin/main
             `tools/pr/ci_predict.py` is in the tree at this head
  ok         tests/closure.py select
             `tests/closure.py` is in the tree at this head
  ok         tests/doc_claims.py
             `tests/doc_claims.py` is in the tree at this head
  ok         tests/entities.py
             `tests/entities.py` is in the tree at this head

FIGURES: 22 resolved, 0 not verified, 0 refused

## Finder's harness: none named
### at the base
not run
### at the head
not run

## Mutation-ledger diff
none

## Three-dot diff
diff --git a/dev/audit/harnesses/r10_carry_field_figures.py b/dev/audit/harnesses/r10_carry_field_figures.py
new file mode 100644
index 000000000..9847294fe
--- /dev/null
+++ b/dev/audit/harnesses/r10_carry_field_figures.py
@@ -0,0 +1,60 @@
+#!/usr/bin/env python3
+"""R10-FLY-RELAY-REVIEW-FF: the field verdict items carry_audit.py flags, at any revision.
+
+    python3 dev/audit/harnesses/r10_carry_field_figures.py <rev> [<rev> ...]
+
+Loads tools/audit/carry_audit.py as <rev> holds it (git show) and runs its
+items() over dev/audit/harnesses/r10_carry_field_verdicts.json, as the working
+tree holds it: each field item alone under its own verdict word and heading,
+and #2645's round-1 blocked VERDICT.md whole. Prints one line per revision:
+
+  RESULT rev=<sha9> field_flagged=<n>/<total> v2645_flagged=<n>
+
+Each field item is no finding (P308, P314, P329, CARRY 3, CARRY 5), so a sound
+parser prints field_flagged=0; #2645's verdict holds one genuine NONBLOCK item.
+Null control: the merge base 7539d1675 prints 17/17 and 8.
+"""
+from __future__ import annotations
+
+import json
+import subprocess
+import sys
+import types
+
+
+def repo_root(start):
+    """The directory holding custom_components/heatpump_optimizer/manifest.json."""
+    from pathlib import Path
+    here = Path(start).resolve()
+    if here.is_file():
+        here = here.parent
+    marker = Path("custom_components") / "heatpump_optimizer" / "manifest.json"
+    for cand in (here, *here.parents):
+        if (cand / marker).is_file():
+            return cand
+    raise RuntimeError(f"no repository root above {start}")
+
+
+ROOT = repo_root(__file__)
+sys.path.insert(0, str(ROOT / "tools/audit/seat"))  # roster_lib, which carry_audit imports
+
+
+def flagged(rev: str) -> str:
+    src = subprocess.run(["git", "-C", str(ROOT), "show", f"{rev}:tools/audit/carry_audit.py"],
+                         capture_output=True, text=True, check=True).stdout
+    m = types.ModuleType("carry_audit_at_rev")
+    m.__file__ = str(ROOT / "tools/audit/carry_audit.py")
+    exec(compile(src, f"{rev}:tools/audit/carry_audit.py", "exec"), m.__dict__)
+    fx = json.loads((ROOT / "dev/audit/harnesses/r10_carry_field_verdicts.json").read_text())
+    n = sum(any(x["id"] == i and x["flagged"] for x in m.items(
+        f"Fix review: {v['verdict']} {'d' * 40}\n\n## {v['section']}\n\n{v['text']}\n", True))
+        for i, v in fx["items"].items())
+    w = sum(x["flagged"] for x in m.items(fx["verdict_2645"]["whole"], True))
+    sha = subprocess.run(["git", "-C", str(ROOT), "rev-parse", "--short=9", rev],
+                         capture_output=True, text=True, check=True).stdout.strip()
+    return f"RESULT rev={sha} field_flagged={n}/{len(fx['items'])} v2645_flagged={w}"
+
+
+if __name__ == "__main__":
+    for r in sys.argv[1:] or ["HEAD"]:
+        print(flagged(r))
diff --git a/dev/audit/harnesses/r10_carry_field_verdicts.json b/dev/audit/harnesses/r10_carry_field_verdicts.json
new file mode 100644
index 000000000..8357a8007
--- /dev/null
+++ b/dev/audit/harnesses/r10_carry_field_verdicts.json
@@ -0,0 +1,130 @@
+{
+ "_comment": "Verbatim verdict items the carry_audit.py self-test reads (R10-FLY-RELAY-REVIEW-FF: P308, P314, P329, P293, P306, CARRY 3 and 5). Each was flagged by the parser at origin/main 7539d1675 and is no finding; `whole` is #2645's round-1 blocked VERDICT.md (8 flagged there). Keyed by carry_audit item id.",
+ "items": {
+  "fccf8846": {
+   "pr": 3013,
+   "commit": "21aea29bc88d",
+   "verdict": "merge",
+   "section": "Summary",
+   "text": "`away.py` is code-owned, so `main-protect-checks` requires tvofi's approving review at merge. This verdict flags that and does not block on it."
+  },
+  "e963066e": {
+   "pr": 3005,
+   "commit": "55dfceb17297",
+   "verdict": "merge",
+   "section": "Round",
+   "text": "Round 2 of PR #3005 (R10-COP-GATE part 5). Reviewed head f91733b769b297847e7c143dbdc96d437a44c4b1 (code head eaa942dfd47f14b333c3b54f43d91419f1e1e029 plus an automatic merge of origin/main 5d4e0bcfb). Delta reviewed: 0e03b035..eaa942df, two commits touching tests only: fc03874db adds the fixtures and eaa942dfd adds the ledger entry. No production or golden file changed since round 1. coordinator.py is code-owned, so tvofi's approving review is still owed before the merge. This is flagged and does not block."
+  },
+  "af269651": {
+   "pr": 3002,
+   "commit": "56b16db30442",
+   "verdict": "merge",
+   "section": "Evidence",
+   "text": "- No finder's harness is named. This is tooling item G of a residual brief, and the self-test is the instrument. I built no harness of my own."
+  },
+  "c4431278": {
+   "pr": 3001,
+   "commit": "02508be7f774",
+   "verdict": "blocked",
+   "section": "Evidence",
+   "text": "- Disposition-stage count in the live roster: 11 at both the head and the base, under the body's own rule (DISPOSITION = deferred, refused, refuted, absorbed, carries-open). A fresh live plan rendered at the head shows 11 `pill held` rows."
+  },
+  "3de8ca1d": {
+   "pr": 3001,
+   "commit": "02508be7f774",
+   "verdict": "blocked",
+   "section": "Evidence",
+   "text": "- Forward-carry: every residual in the body routes to a group (carry_audit: 5 routed, 0 unrouted)."
+  },
+  "08d5f26d": {
+   "pr": 2987,
+   "commit": "ebee52e60ba2",
+   "verdict": "merge",
+   "section": "Evidence",
+   "text": "- Red checks: none red in the check-runs API at this read. Completed runs are green or skipped. `tests / fast (3.14)`, `tests / closures`, `tests / browser`, `governance / env-matrix`, `governance / instrument-self-tests` were still in_progress and no `pr-contract` run had started. These are heavy CI lanes cited, not re-run, per the contract. They are not a block for a docs-only diff, but the merge train reads them. The body's \"Red checks: none\" is correct as of now."
+  },
+  "19d896fa": {
+   "pr": 2937,
+   "commit": "3c0b929524fc",
+   "verdict": "merge",
+   "section": "Evidence",
+   "text": "- CI (step 11), live at return: all concluded gate checks green except governance / delivery-status. It is OVERDUE on other merged PRs' rows (#2921, #2910, #2873, #2909), not on this PR's row; its log says it is not a required context and a red there blocks no merge; by fix-review.md step 11 it is not this pull request's, so the packet's red-unanswered refusal on it does not block here. codeql / Analyze (python) and two prelude jobs were still in_progress at return; their conclusions are not re-read in this verdict."
+  },
+  "f76b3ac3": {
+   "pr": 2939,
+   "commit": "e24d5dad7809",
+   "verdict": "merge",
+   "section": "Evidence",
+   "text": "- Live CI on this head (check-runs API, re-read after the render):\n  - `gate` passed (123459287575, 123458371412, 123458354517).\n  - `pr-contract` passed (123458912125).\n  - Every other completed run passed or was skipped, except `tests / nightly-status` (123458368828).\n  - nightly-status is not a required check and does not block: `gate` concluded green. The body answers it under its second `## Red checks`. I did not re-derive main's Nightly state."
+  },
+  "158ad202": {
+   "pr": 2955,
+   "commit": "c8ff9d8a6975",
+   "verdict": "merge",
+   "section": "Evidence",
+   "text": "- CI at this head, all pages (55 runs, ev/check-runs.tsv): every workflow concluded, with 37 success, 17 skipped and 1 failure. The failure is `tests / nightly-status` (job 123739895869). It grades main's scheduled Nightly (run 40835853528, lane `slow`), it prints that it is NOT one of the required contexts on main-protect and does not block a merge, and this diff reaches nothing it reads, so it is not this PR's. `pr-contract` ran twice after the last red concluded (21:24:25Z), at 22:05:55Z and 22:08:12Z, and both succeeded, so the body's `## Red checks` (closures, closures-autofix, nightly-status) passed the contract. `tests / mutation` is green, but the diff writes no production code line, so no mutant is drawn; my targeted mutants above stand in for it."
+  },
+  "dde38e84": {
+   "pr": 2959,
+   "commit": "233c4f141c78",
+   "verdict": "merge",
+   "section": "Evidence",
+   "text": "- CI at the head (check-runs API, every run listed, ev/checks.txt): every run has concluded, and `gate` has three runs, all success. The only red is `tests / nightly-status`, which grades main's Nightly. The diff does not reach what it reads, and the body's `## Red checks` names it. It is not this pull request's and does not block."
+  },
+  "c21695db": {
+   "pr": 2969,
+   "commit": "742064c51211",
+   "verdict": "merge",
+   "section": "Evidence",
+   "text": "- CLI refusals at the head (VERSION 7.0.5, roster round 10), re-run with `--dry-run`. `--bump major`, `--round-close 7`, `--round-close 9` and `--round-close 10 --bump minor` each print `stamp refused (rule 3)` before any fetch. `--round-close 10` and `--bump minor` pass next_version and stop at rule 1, because HEAD is not origin/main. All of this matches the body."
+  },
+  "2471d3e6": {
+   "pr": 2955,
+   "commit": "0775846811b5",
+   "verdict": "merge",
+   "section": "Findings",
+   "text": "None. The merge resolution is a pure union; nothing is deferred or owed."
+  },
+  "57e267d2": {
+   "pr": 2683,
+   "commit": "e23093927fc4",
+   "verdict": "merge",
+   "section": "Body (steps 7, 10, non-blocking note 1)",
+   "text": "The live PR body is the same text as handoff-body ref `39cb37f13`. Both forward-carry items name their roster SHA (8d6527c07, 57bb4b33e). Lines 5 and 45–47 state that the countermeasure departs from the RCA's numeric quiet-interval form. `## Head` still names `07b83e9b2`."
+  },
+  "c571d890": {
+   "pr": 2683,
+   "commit": "e23093927fc4",
+   "verdict": "merge",
+   "section": "Body (steps 7, 10, non-blocking note 1)",
+   "text": "- `node tools/policy/policy_lint.mjs --pr-body … --head 07b83e9b2 --base d05a44c63 --paths-file … --existing-file …` printed `PR-BODY: 0 error(s)`, rc 0. Its red-history arm skipped because no token was set."
+  },
+  "14f2edf3": {
+   "pr": 2683,
+   "commit": "e23093927fc4",
+   "verdict": "merge",
+   "section": "Body (steps 7, 10, non-blocking note 1)",
+   "text": "- `node tools/policy/figure_lint.mjs` printed `FIGURES: 17 resolved, 13 not verified, 0 refused`, rc 0."
+  },
+  "7ca5af57": {
+   "pr": 2683,
+   "commit": "e23093927fc4",
+   "verdict": "merge",
+   "section": "Body (steps 7, 10, non-blocking note 1)",
+   "text": "(evidence/policy_lint-body.out)"
+  },
+  "a7dc6fe0": {
+   "pr": 2997,
+   "commit": "8051ad872982",
+   "verdict": "merge",
+   "section": "Evidence",
+   "text": "- tests/mutation_table.py is code-owned, so tvofi's approving review is what the code-owner rule enforces at merge. This review does not block on it."
+  }
+ },
+ "verdict_2645": {
+  "pr": 2645,
+  "commit": "cbac2180d",
+  "verdict": "blocked",
+  "whole": "Fix review: blocked ad62bf6346a131111ea482185caa2813e9851a19 mutation-vacuous: ci_critpath --event/--branch run-list filter dropped survives the self-test\n\nRound: 1 (first review of this head). Measured at ad62bf6346a131111ea482185caa2813e9851a19 from a detached worktree; re-read before writing: the PR head and refs/pull/2645/head are still that SHA. Merge base e30b24bbc4; origin/main 4200ea4c42. `git diff <mb>...origin/main -- dev/governance/roles/` is empty: the contract read is current.\n\n## The blocking finding\n\n`tools/audit/seat/ci_critpath.py` `Api.runs` builds the run-list query from `--event`/`--branch`:\n`q = \"\".join(f\"&{k}={v}\" for k, v in ((\"event\", event), (\"branch\", branch)) if v)`.\nNo client-side filter backs it: the rows returned are filtered only for cancelled/skipped. Mutant `c10-event-branch-q` (`q = \"\"`) leaves the self-test at `24 checks, 0 failed`: no check passes `--event` or `--branch`, and the stub `get` ignores the query string. With it, `--workflow tests.yml --last 8 --event push --branch main` silently mixes pull-request and branch runs into main's median.\n\nThe body leans on this exact filter twice:\n- `## Red checks`: the cheaper detector it names for `ci-ratchet` is `ci_critpath.py --event push --branch main --last 8`, which \"reads the same median before a push lands\".\n- `## Forward-carry` to R10-CI-LAYOUT-P2 (roster 5e70cc5ce): the next fixer is told to keep its window on one side of a job-graph change with \"`--event`, `--branch`, or `--run` lists\".\n\nSo a changed site that two claims rest on has no mutant and no check (brief item 3). The fix is small: one self-test check where the stub returns a different run list when `event=push&branch=main` is in the path (or asserts the path it was called with), plus a seat mutant like `c10` in `r10_seat_selftests_mutants.py`.\n\nTwo more survivors. Neither blocks, but the fixer should look at both:\n- `c9-git-first` (`p.stdout if False`: always read needs from the contents API): self-test stays green. The output is the same; only the API-read count changes, and the body quotes that count (\"11 API reads ... again reads 1\"). Low value; a check on `reads` for a head git holds would pin it.\n- `c7-cycle-guard` (cycle refusal removed): survives. GitHub refuses cyclic `needs:`, so this is a guard against input the API cannot produce. I judge it equivalent in practice.\n\n## RESULT lines\n\n```\nRESULT head=ad62bf6346a131111ea482185caa2813e9851a19 moved=no\nRESULT selftest ci_critpath=24/0 flow_metrics=16/0 review_strength=100/0 (python 3.11.17, -I)   # body: same\nRESULT selftest_wiring=89 self-testing, 89 wired, 0 unwired                                         # body: same\nRESULT seat_mutants M0=0 steps red (Linux; body's 3 pr_args reds were its Mac) ci_critpath-1 KILLED 3 failed, ci_critpath-2 KILLED 2, flow_metrics-1 KILLED 1, flow_metrics-2 KILLED 4, ruleset_cutover-1/2/3 KILLED 1 each, survivors=0\nRESULT own_mutants=18 killed=15 survived=3 (c7-cycle-guard, c9-git-first, c10-event-branch-q)\nRESULT mutants_file three-dot vs merge base: +6 lines only (this PR's block); head vs origin/main differs by exactly those 6 lines; main's ruleset_cutover-1..3 block byte-identical\nRESULT merge-tree origin/main head: rc=0 tree 91e0d774e8; LEDGER-MERGE: resolved tests/closures.json (inert_reads set merge); no MERGE-CLAIM lines (no claim file touched)\nRESULT structure.py=STRUCTURE RATCHET PASSED; archscore dS +0.0000 NULL; no *_budgets.json touched\nRESULT parity: PARITY 24/24, NULL 9/24, NEEDS 40 files 0 differ, mutant differs on 28   # body: same\nRESULT carry_audit pr 2645: 5 routed, 0 unrouted, 0 bad\nRESULT entities.py (venv-ci 3.14.7): head 2404/2404 pass; origin/main 4200ea4c 2406/2406 pass; merge(origin/main, head) 2406/2406 pass\nRESULT CI at head: red fast (3.14) [entities 1 of 2406], red nightly-status; closures, coverage, CodeQL python in progress\n```\n\n## Brief checklist\n\n1. **No round constant in code.** Grepping the three instruments for r10/R10/heatpump_optimizer/tvofi finds only `flow_metrics.py:6`, a usage example (`--prefix R10-`) in the docstring. In `ci_critpath.py`, `--repo` has no default. In `flow_metrics.py`, `--prefix` and `--roster` are required. Default values the body names: `--record-prefix record/` and `--tree origin/main`. No added review_strength line names the round or repository. Holds.\n2. **Self-tests and wiring** match the body. The named mutants all kill, and so do main's three. The mutants file merged cleanly, with main's block byte-identical (above).\n3. **Coverage of the changed sites without a full harness re-run.** The full re-run was skipped after the merge, and that is justified: the merges add only main's lines, which I ran. But the named set plus the body's targeted list leaves `--event`/`--branch` with no mutant and no check. That is the blocking finding. Every other site I planted was killed: queue held in replay, p90 rank, needs-field reset, jobs and runs paging, matrix mapping, expression name, cf path, first verdict, merge and roster windows, patch-id, unresolved, prev-merge kind, unjudged count.\n4. **structure.py** passes. **dS** +0.0000. Merges clean with origin/main. The entity failures the fixer saw on the Mac (heartbeat timing, `a8:register_once`) do not reproduce here on 3.14.7 at the head, at main or at the merge. The `FAIL` lines in those logs are the suite's indented null controls, the same set at main and at the head. pr_args: M0 here reports no red seat step. `instrument-self-tests` is green in CI at the head, and it runs the pr_args steps.\n5. **Carries.** carry_audit reads 5/0/0. The three roster carries are all on `origin/handoff/audit-r10-roster`:\n   - c137945d6 → R10-FLY-YIELD-GUARD. It owns the yield-probe guardrail (`yield-probe.md`), which reads review strength: the right owner.\n   - 5e70cc5ce → R10-CI-LAYOUT-P2. In progress; it owns `tests.yml`/`governance.yml`/`ci.yml` and states its next W figure with this instrument: the right owner. One note on its wording: `analyse` refuses a `--drop-edge` only when both jobs ran in that run and the edge is gone. If a graph change renames or removes either job, the drop is a silent no-op, not a refusal. So \"a window that straddles a job-graph change refuses\" holds only for a graph change that keeps both jobs. Not blocking; the carry should say so.\n   - 2ad8710e4 → R10-FLOW-JIDOKA. A stale `S36` pin in a seat mutant harness is a stop-the-line instrument-health item. Its roster files (prepr.sh, policy-rot) do not include the harness, so the fit is by role, not by file. Acceptable.\n   - R10-FLOW-TOOLKIT-MODEL (the FUTURE-STATE figures) and the dismissed `--record-prefix` carry are routed per carry_audit.\n6. **CI** (ev/check_runs.txt):\n   - `nightly-status`: red. Its diff does not reach what it reads, so it is not this PR's (`defect-root-cause.md`). The body names it.\n   - `fast (3.14)`: red, `tests/entities.py` \"1 of 2406 ENTITY CHECKS FAILED\". The body's `## Red checks` predates this run (\"No check has run on this head yet\"), so it is unanswered there. The check does not reproduce locally at the head, at main or at the merge on 3.14.7. Main's full push run at the merge base passed `fast (3.14)`. The retrieved log tail does not show which check failed. It looks like the timing-class checks (hb:*) the fixer reported; that is a judgement, not a measurement.\n   - Under rule 11 I post no root-cause class on it: closures and coverage are still running, and no `pr-contract` run has started since `fast` concluded red (last pr-contract 03:20:54Z, fast red 03:29:48Z). The fixer owes the answer in `## Red checks` once the workflows conclude.\n\n## Not re-derived\n\n- The `review_strength.py` one-node sweep (`mutants=2612 killed=2562 survived=50`): not re-run.\n- The live-API figures (655 verdicts, the 0.52/0.15 windows, the flow_metrics window counts, and \"11 API reads\"): this seat has no `gh` and did not fetch the bus tags.\n\nThose figures are the fixer's, not verified here.\n\nbus-nonce: da7eafe36d7cad6ecc675da0f5632b30\n"
+ }
+}
diff --git a/dev/audit/harnesses/r10_carry_parser_mutants.py b/dev/audit/harnesses/r10_carry_parser_mutants.py
index 562737e7b..2d1efe6e1 100644
--- a/dev/audit/harnesses/r10_carry_parser_mutants.py
+++ b/dev/audit/harnesses/r10_carry_parser_mutants.py
@@ -60,11 +60,11 @@ REL = "tools/audit/carry_audit.py"
 sys.path.insert(0, str(Path(__file__).resolve().parent))
 import mutant_guard  # noqa: E402 -- restores the mutated file on a kill (SIGTERM/SIGINT) and refuses a leftover mutant
 F = ROOT / REL
-PARSER = ("items", "carry_segments", "carry_refs", "carry_dests", "seg_dests", "finding_rows", "audit",
+PARSER = ("freed", "items", "carry_segments", "carry_refs", "carry_dests", "seg_dests", "finding_rows", "audit",
           "ledger_unrouted")
 PATTERNS = ("HEADING", "BULLET", "TABLE_SEP", "FRICTION_ENTRY", "VERDICT", "CARRY_SECTIONS", "NONE_ITEM",
-            "TRAILER", "EVIDENCE_HEADING", "NOT_REQUIRED", "DEFERRED", "NONBLOCK", "LEAD", "NOTE_HEADING", "BLOCK_HEADING", "CARRY", "ITEM_REF", "CODE_SPAN",
-            "GROUP_TOK", "ISSUE_TOK", "BRIEF_TOK", "LEDGER_FINDING")
+            "TRAILER", "EVIDENCE_HEADING", "FINDINGS_HEADING", "APPROVAL", "APPROVAL_BARE", "NOTHING", "NONBLOCK", "LEAD", "NOTE_HEADING", "BLOCK_HEADING", "CARRY", "ITEM_REF", "CODE_SPAN",
+            "GROUP_TOK", "ISSUE_TOK", "BRIEF_TOK", "LEDGER_FINDING", "SUPERSEDES")
 
 # load_dests' stale-tree test: the lines the B2 mutants perturb
 B2_SHALLOW = '        shallow = git(["rev-parse", "--is-shallow-repository"])[1].strip() == "true"'
@@ -112,35 +112,62 @@ MUTANTS = [
     ("I-first", '        first = re.sub(r"^[\\s>*_`-]*(?:\\d+[.)]\\s*)?[*_`]*", "", t)', '        first = t'),
     ("I-first-num", '(?:\\d+[.)]\\s*)?[*_`]*", "", t)', '[*_`]*", "", t)'),
     ("I-first-emph", '(?:\\d+[.)]\\s*)?[*_`]*", "", t)', '(?:\\d+[.)]\\s*)?", "", t)'),
-    ("I-lead-reset", '        if it["kind"] != "bullet":\n            lead_flag = False', '        if False:\n            lead_flag = False'),
+    ("I-lead-reset", '        if it["kind"] != "bullet" or sec != lead_sec:\n            lead_flag = False', '        if False:\n            lead_flag = False'),
     ("I-inh-flag", "        inherited = lead_flag  #", "        inherited = False  #"),
     ("I-trailer", "        if TRAILER.match(first) or VERDICT.match(first):", "        if VERDICT.match(first):"),
     ("I-verdict-line", "        if TRAILER.match(first) or VERDICT.match(first):", "        if TRAILER.match(first):"),
     ("I-verdict", "        elif verdict:\n", "        elif False:\n"),
-    # items(): evidence (r10-verdict-item-barrier)
-    ("I-ev-verdict", "        elif verdict and EVIDENCE_HEADING.match(sec):", "        elif EVIDENCE_HEADING.match(sec):"),
-    ("I-ev-heading", "        elif verdict and EVIDENCE_HEADING.match(sec):", "        elif False:"),
+    # items(): the structural branch (P308 Evidence, P314 a merge verdict's other sections)
+    ("I-ev-verdict", "        elif verdict and (EVIDENCE_HEADING.match(sec)", "        elif (EVIDENCE_HEADING.match(sec)"),
+    ("I-ev-heading", "        elif verdict and (EVIDENCE_HEADING.match(sec)\n", "        elif verdict and (False\n"),
     ("I-ev-match", "EVIDENCE_HEADING.match(sec)", "EVIDENCE_HEADING.search(sec)"),
-    ("I-ev-lead", 'why = ("lead" if LEAD.match(first) else "evidence"', 'why = ("lead" if False else "evidence"'),
-    ("I-ev-deferred", 'else "evidence" if DEFERRED.search(t) or', 'else "evidence" if False or'),
-    ("I-ev-nonblock", " or NONBLOCK.search(claims)\n", "\n"),
-    ("I-ev-claims", "NONBLOCK.search(claims)", "NONBLOCK.search(t)"),
-    ("I-ev-carve", 'claims = NOT_REQUIRED.sub(" ", t)', "claims = t"),
-    # the open form (round 1): the carve-out freed its whole sentence
-    ("I-ev-sentence", 'claims = NOT_REQUIRED.sub(" ", t)',
-     'claims = " ".join(x for x in re.split(r"(?<=[.;!?])\\s+", t) if not NOT_REQUIRED.search(x))'),
-    ("P-notreq-a", 'r"not (?:a )?required', 'r"not required'),
-    ("P-notreq-clause", '(?:context|check)(?:,?', '(?:context|check)(?:QQ,?'),
-    ("P-notreq-comma", '(?:context|check)(?:,?\\s+', '(?:context|check)(?:\\s+'),
-    ("P-notreq-and", '(?:and\\s+)?(?:it', '(?:it'),
-    ("P-notreq-it", '(?:it\\s+)?"', '"'),
-    ("P-notreq-colon", '(?!\\s*:))?", re.I)', ')?", re.I)'),
-    ("I-ev-inh", 'else "under lead" if inherited else "")\n        elif verdict:', 'else "under lead" if False else "")\n        elif verdict:'),
-    ("I-bsec-block", "            block_sec = BLOCK_HEADING.search(sec) and not", "            block_sec = True and not"),
+    ("P314-merge-only", "or not (blocked_verdict or block_sec or FINDINGS_HEADING.match(sec))):", "or False):"),
+    ("P314-blocked", "or not (blocked_verdict or block_sec or", "or not (False or block_sec or"),
+    ("P314-block-sec", "or not (blocked_verdict or block_sec or", "or not (blocked_verdict or"),
+    ("P314-findings", "or block_sec or FINDINGS_HEADING.match(sec))):", "or block_sec)):"),
+    ("I-ev-lead", 'why = ("lead" if LEAD.match(first) else "under lead" if inherited\n                   else "carry"',
+     'why = ("lead" if False else "under lead" if inherited\n                   else "carry"'),
+    ("I-ev-inh", 'else "under lead" if inherited\n                   else "carry"', 'else "under lead" if False\n                   else "carry"'),
+    # P308's own mutant: the word clause restored in the structural branch
+    ("P308-restore", 'why = ("lead" if LEAD.match(first) else "under lead" if inherited\n                   else "carry"',
+     'why = ("lead" if LEAD.match(first) else "evidence" if NONBLOCK.search(t) else "under lead" if inherited\n                   else "carry"'),
+    # P296: drop the old-must-be-invalid test; drop the item-id scoping
+    # CARRY 0 / P310: landed and land-ops
+    ("L-landed", "            if not any(k in words for k in keys):", "            if False:"),
+    ("L-words", 'words = set(re.split(r"[^\\w#-]+", group_text(dests, tok)))', 'words = set(group_text(dests, tok).split())'),
+    ("L-source", "            keys = [r[\"id\"]] + srcs", "            keys = [r[\"id\"]]"),
+    ("L-bad", "            if not ok:\n                out.append(", "            if False:\n                out.append("),
+    ("L-group", "            if not GROUP_TOK.match(tok):\n                continue", "            if False:\n                continue"),
+    ("L-ops-bad", 'if m["why"].startswith("bad destination") or', 'if'),
+    ("L-ops-seen", "or (m[\"group\"], m[\"id\"]) in seen:", ":"),
+    ("P296-pattern", r'),\s*supersedes\s+(', r'),supersedes\s+('),
+    ("P296-findall", "SUPERSEDES.findall(seg)", 'SUPERSEDES.findall("")'),
+    ("P296-strip", 'old.strip("`*_.:")', "old"),
+    ("P296-filter", '[t for t in r["dests"] if t != old]', '[t for t in r["dests"] if True]'),
+    ("P296-valid", "            if dests.check(old)[0]:", "            if False:"),
+    ("P296-scope", '        for old, new in sups.get(r["id"], []):', '        for old, new in [x for v in sups.values() for x in v]:'),
+    ("P296-retire", '            elif old in r["dests"]:', '            elif False:'),
+    ("P296-ref", "            refs.setdefault(ref, []).extend(ds)\n            sups.setdefault", "            sups.setdefault"),
+    ("P296-merge", "                sups.setdefault(ref, []).extend(olds)", "                pass"),
+    ("P308-carry", 'else "carry" if carry_segments(t) else "")', 'else "")'),
+    # P329's strip and the negated deferral
+    ("P329-strip", "NONBLOCK.search(freed(t))", "NONBLOCK.search(t)"),
+    ("P329-approval", "        if APPROVAL.search(part):", "        if False:"),
+    ("P329-bare", "        if after and APPROVAL_BARE.match(part):", "        if after:"),
+    ("P329-bare-after", "        if after and APPROVAL_BARE.match(part):", "        if APPROVAL_BARE.match(part):"),
+    ("P329-cont-approval", "            after = True\n            continue", "            after = True\n            pass"),
+    ("P329-cont-bare", "            after = False\n            continue", "            after = False\n            pass"),
+    ("P329-once", "        after = False\n        out.append(part)", "        out.append(part)"),
+    ("P329-split", 're.split(r"(?<=[.;])", t)', '[t]'),
+    ("P329-nothing", 'return NOTHING.sub(" ", "".join(out))', 'return "".join(out)'),
+    # CARRY 3: a lead's bullets end at its section's end
+    ("C3-section", 'if it["kind"] != "bullet" or sec != lead_sec:', 'if it["kind"] != "bullet":'),
+    ("C3-record", 'lead_flag, lead_sec, it["lead"] = True, sec, True', 'lead_flag, it["lead"] = True, True'),
+    ("I-bsec-block", "        block_sec = BLOCK_HEADING.search(sec) and not", "        block_sec = True and not"),
     ("I-bsec-nonblock", " and not NONBLOCK.search(sec)\n", "\n"),
     ("I-nsec", "NONBLOCK.search(sec) if blocked_verdict else NOTE_HEADING.search(sec)", "NOTE_HEADING.search(sec)"),
     ("I-nsec-b", "NONBLOCK.search(sec) if blocked_verdict else NOTE_HEADING.search(sec)", "NONBLOCK.search(sec)"),
-    ("I-why-nb", 'why = ("non-blocking" if NONBLOCK.search(t) else', 'why = ("non-blocking" if False else'),
+    ("I-why-nb", 'why = ("non-blocking" if NONBLOCK.search(freed(t)) else', 'why = ("non-blocking" if False else'),
     ("I-why-block", '"" if block_sec\n', '"" if False\n'),
     ("I-why-note", '"section" if note_sec else "lead" if LEAD.match(first)\n                   else "under', '"section" if False else "lead" if LEAD.match(first)\n                   else "under'),
     ("I-why-vlead", 'else "lead" if LEAD.match(first)\n                   else "under lead" if inherited else "")\n        elif', 'else "lead" if False\n                   else "under lead" if inherited else "")\n        elif'),
@@ -171,7 +198,7 @@ MUTANTS = [
     # carry_refs / carry_dests: the segment scope (M15), the destinations kept
     ("M15", "        for ref in ITEM_REF.findall(seg):", "        for ref in ITEM_REF.findall(text):"),
     ("R-found", "        found += ds\n", "        found += []\n"),
-    ("R-extend", "            refs.setdefault(ref, []).extend(ds)", "            refs.setdefault(ref, ds)"),
+    ("R-extend", "ITEM_REF.findall(seg):\n            refs.setdefault(ref, []).extend(ds)", "ITEM_REF.findall(seg):\n            refs.setdefault(ref, ds)"),
     ("R-seg", "        ds = seg_dests(seg)", "        ds = seg_dests(seg.split(\"(\", 1)[0])"),
     ("R-dests", "    return carry_refs(text)[0]", "    return carry_refs(text)[1]"),
     # seg_dests: the rest, dismissed, the split, each token predicate
@@ -209,8 +236,8 @@ MUTANTS = [
     ("A-union-off", '        r["dests"] = r["dests"] + refs.get(r["id"], [])', "        pass"),
     ("A-bad", "            (notes if ok else bad).append(", "            notes.append("),
     ("A-note", '(f"{tok}: {note}" if note else tok)', "(tok)"),
-    ("A-status-u", 'r["status"] = "unrouted" if not r["dests"] else', 'r["status"] = "unrouted" if False else'),
-    ("A-status-b", '("bad" if bad else "routed")', '("routed")'),
+    ("A-status-u", '"unrouted" if not r["dests"] else "routed"', '"unrouted" if False else "routed"'),
+    ("A-status-b", 'r["status"] = "bad" if bad else', 'r["status"] = "bad" if False else'),
     # ledger_unrouted: the key and the marker
     ("L-key", "            if LEDGER_FINDING.search(ln) and not carry_dests(ln)]", "            if not carry_dests(ln)]"),
     ("L-carry", "            if LEDGER_FINDING.search(ln) and not carry_dests(ln)]", "            if LEDGER_FINDING.search(ln)]"),
@@ -249,6 +276,10 @@ MUTANTS = [
     # ... and a shallow clone, whose rc 1 may be its graft, keeps it too
     ("B2-shallow", B2_SHALLOW, "        shallow = False"),
     ("B2-shallow-always", B2_SHALLOW, "        shallow = True"),
+    # load_dests: P319, the round ref is read on the explicit-ref path too
+    # load_dests: P43, a pull request's own carry files join at the pre-flight
+    ("P43-extra", "for n in r.stdout.split() if n.endswith(\".json\")]  # mut:extra", "for n in []]  # mut:extra"),
+    ("P319-ref-path", "    if rref and rref != ref and not git(", "    if rref and not ref and not git("),
 ]
 
 
diff --git a/dev/audit/harnesses/r10_seat_selftests_mutants.py b/dev/audit/harnesses/r10_seat_selftests_mutants.py
index 266210393..244b8237b 100644
--- a/dev/audit/harnesses/r10_seat_selftests_mutants.py
+++ b/dev/audit/harnesses/r10_seat_selftests_mutants.py
@@ -216,6 +216,19 @@ MUTANTS = [
     ("bus-1", "bus.sh", "    0|3) ;;\n", "    0|1|3) ;;\n"),
     ("bus-2", "bus.sh", "    0|3) ;;\n", "    0) ;;\n"),
     ("bus-3", "bus.sh", '    *) die "dispatch: cannot classify', '    *) : "dispatch: cannot classify'),
+    # R10-FLY-RELAY-REVIEW-FF: push-verdict's refusals before review/<pr> moves, and the push buffer.
+    ("bus-4", "bus.sh", '  why=$(carry_gate "$v") || die "push-verdict: $why"\n', ''),
+    ("bus-5", "bus.sh", '  why=$(python3 -I "$ROOT/tools/audit/seat/ref_privacy.py" body-lines "$v") \\\n', '  why=$(true) \\\n'),
+    ("bus-6", "bus.sh", 'git -c http.postBuffer=524288000 push -q "$REMOTE"', 'git push -q "$REMOTE"'),
+    ("bus-7", "bus.sh", '[ -n "$a" ] && [ -z "$(grep -vxF \'dependabot[bot]\' <<< "$a")" ]  # mut:botonly', '[ -n "$a" ]'),
+    ("bus-8", "bus.sh", 'if [ -n "$holder" ] && kill -0 "$holder" 2>/dev/null; then  # mut:watchlock', 'if false; then'),
+    ("bus-9", "bus.sh", '  rm -f "$b"; [ "$rc" != 1 ]  # mut:landed', '  rm -f "$b"; true'),
+    # P43: the pre-flight reads each pull request's destinations with its head as the extra ref
+    ("queue_pre_flight-1", "queue_pre_flight.py", "extra_ref=head or None)", "extra_ref=None)"),
+    # carry_audit.py check reads no roster for a verdict with no finding item (bus.sh's step grades it:
+    # its scratch origin holds no roster until the carry rows plant one).
+    ("carry_audit-1", "tools/audit/carry_audit.py",
+     '            if not finding_rows(body, comments)[0]:\n                return report({"rows": []})', '            if False:\n                pass'),
     # Round 2: GitHub's merge under a local driver, and the reviewer's R1-R4.
     ("merge_train-12", "merge_train.py",
      '    drivers = text_merge(run)\n    if drivers is None:\n        return None\n',
@@ -302,6 +315,7 @@ MUTANTS = [
      '  if [ "$prc" != 0 ]; then\n    echo "body_push: the review packet refuses'),
     # R10-FLOW-BODY-ONLY carry 13 (V147): a PR body names its code head; graded by prepr's self-test
     ("body_push-3", "tools/audit/seat/body_push.sh", '[ -z "$HREF" ] || MSG=', '[ -n "$HREF" ] || MSG='),
+    ("body_push-4", "tools/audit/seat/body_push.sh", '  if [ "$lrc" = 1 ]; then  # mut:landed', '  if false; then'),
     # #2853's review: the class the copy enumeration missed is a link to an
     # in-tree file it does not name. prepr-11 renames a LISTED entry (the
     # pathspec arm); prepr-13 stops the copy taking the generator's own link
@@ -431,13 +445,39 @@ MUTANTS = [
      '    run, start = int(w[0]), int(os.fstat(f.fileno()).st_mtime)\n'),
     ("cloud_relay-31", "cloud_relay.sh", '  if now - start <= lim: continue\n', ''),
     ("cloud_relay-32", "cloud_relay.sh", '  if not held(f): continue\n', ''),
-    ("cloud_relay-33", "cloud_relay.sh", 'confirm_arm; stuck_arm; [ -z "$loop" ]', 'confirm_arm; [ -z "$loop" ]'),
+    ("cloud_relay-33", "cloud_relay.sh", 'confirm_arm; stuck_arm; noreturn_arm; [ -z "$loop" ]', 'confirm_arm; noreturn_arm; [ -z "$loop" ]'),
+    # R10-FLY-RELAY-REVIEW-FF P288: the worktree arm restored holds the #2953 shape again;
+    # the evidence dropped from the HELD line fails its row.
+    ("cloud_relay-39", "cloud_relay.sh", '  [ -n "$v" ] || return 1\n  echo "REVIEW dispatch=',
+     '  [ -n "$v" ] || git worktree list --porcelain | awk -v h="$2" \'$1 == "HEAD" { at = ($2 == h) } $1 == "detached" && at { f = 1 } END { exit !f }\' || return 1\n  echo "REVIEW dispatch='),
+    ("cloud_relay-40", "cloud_relay.sh", '#$pr $hs${why#"${why%% *}"} (head', '#$pr $hs (head'),
+    # P283: the relay's own checkout's update_pr.sh again; no dirty test; no busy test; no levelling.
+    # P-E: the no-return line: its age window, its moved test, its wiring into the pass
+    ("cloud_relay-45", "cloud_relay.sh", '[ "$age" -gt "$lim" ] && [ "$age" -le "$win" ] || continue  # mut:noreturnage', '[ "$age" -le "$win" ] || continue'),
+    ("cloud_relay-46", "cloud_relay.sh", '-gt "$t" ] && { moved=1; break; }  # mut:noreturnmoved', '-gt "$t" ] && { break; }'),
+    ("cloud_relay-47", "cloud_relay.sh", 'stuck_arm; noreturn_arm; [ -z "$loop" ]', 'stuck_arm; [ -z "$loop" ]'),
+    ("cloud_relay-48", "cloud_relay.sh", '[ "$age" -gt "$lim" ] && [ "$age" -le "$win" ] || continue  # mut:noreturnage', '[ "$age" -gt "$lim" ] || continue'),
+    # P332: the confirm arm's skip of a review on a PR that is not open
+    ("cloud_relay-49", "cloud_relay.sh", 'if [ -n "$open" ] && ! grep -qxF "$pr" <<< "$open"; then  # mut:closedskip', 'if false; then'),
+    ("cloud_relay-41", "cloud_relay.sh", 'upd=(bash "$why/update_pr.sh")  # mut:toolsseat', 'upd=(bash "$HERE/update_pr.sh")'),
+    ("cloud_relay-42", "cloud_relay.sh", 'if [ -n "$(git -C "$tw" status --porcelain --untracked-files=no 2>/dev/null)" ]; then', 'if false; then'),
+    ("cloud_relay-43", "cloud_relay.sh", 'if [ -n "$o" ] && kill -0 "$o" 2>/dev/null; then echo', 'if false; then echo'),
+    ("cloud_relay-44", "cloud_relay.sh", '  git -C "$tw" checkout -q --detach origin/main 2>/dev/null \\\n', '  true \\\n'),
     ("ledger-1", "ledger.py", '"confirm-owed": "derived", "push-stuck": "derived",', '"confirm-owed": "derived",'),
     ("pr_args-1", "pr_args.sh", 'p = os.getppid(); start = int(time.time())', 'p = os.getppid(); start = 0'),
     ("tick_loop-3", "tick_loop.sh", 'pass --confirm </dev/null', 'pass </dev/null'),
     # r10-flow-andon: ids are per file (tick_loop-N, heartbeat-N), never a new S number.
     ("tick_loop-1", "tick_loop.sh", '  timeout 60 bash "${HPO_TICK_HEARTBEAT:-$HERE/heartbeat.sh}" --once --message "TICK-PASS $now relay=$rrc tick=$trc"  # mut:heartbeat\n', ""),
     ("tick_loop-2", "tick_loop.sh", '[ $? = 0 ] || echo "HEARTBEAT NOT PUSHED: heartbeat.sh did not finish cleanly"', "true"),
+    # R10-FLY-RELAY-REVIEW-FF P14: the freshness check, one mutant per self-test row.
+    ("tick_loop-4", "tick_loop.sh", 'behind_count "$top" "${CODE_PATHS[@]}")', 'behind_count "$top" .)'),
+    ("tick_loop-5", "tick_loop.sh", '[ "$behind" -gt "$bound" ] || [ "$self" -gt 0 ] || return 0  # mut:bound', 'true'),
+    ("tick_loop-6", "tick_loop.sh", 'elif ! python3 -I -c "$LOCK_FREE" "$1.relay.lock"; then', 'elif false; then'),
+    ("tick_loop-7", "tick_loop.sh", 'elif [ -n "$(git -C "$top" status --porcelain --untracked-files=no)" ]; then', 'elif false; then'),
+    ("tick_loop-8", "tick_loop.sh", 'git -C "$top" show origin/main:tools/audit/seat/tick_loop.sh | bash -n 2>/dev/null', 'true'),
+    ("tick_loop-9", "tick_loop.sh", '    HPO_TICK_RESTARTED=1 exec bash "$top/tools/audit/seat/tick_loop.sh" "${ARGV[@]}"  # mut:exec\n', ''),
+    ("tick_loop-10", "tick_loop.sh", '  if [ -n "$stale" ]; then\n    rrc=stale', '  if false; then\n    rrc=stale'),
+    ("tick_loop-11", "tick_loop.sh", 'if [ -n "${HPO_TICK_RESTARTED:-}" ]; then why=', 'if false; then why='),
     ("heartbeat-1", "heartbeat.sh", 'git -C "$HERE" push -q --no-verify -f "$remote"', 'git -C "$HERE" push -q --no-verify "$remote"'),
     ("heartbeat-2", "heartbeat.sh", '  if [ "$age" -gt "$max" ]; then', '  if [ "$age" -gt $((max * 100)) ]; then'),
     ("heartbeat-3", "heartbeat.sh", '|| { echo "HEARTBEAT NOT PUSHED: $(printf', '|| { echo "$(printf'),
@@ -494,7 +534,8 @@ ENV_MUTANTS = [("S04U", "S04", {"PYTHONUNBUFFERED": "1"})]
 # A mutant planted in a file whose self-test is another instrument's step.
 STEP_OF = {"prepr-9": "tools/pr/prepr.sh", "prepr-10": "tools/pr/prepr.sh",
            "prepr-12": "tools/pr/prepr.sh", "body_push-1": "tools/pr/prepr.sh",
-           "body_push-2": "tools/pr/prepr.sh", "body_push-3": "tools/pr/prepr.sh"}
+           "body_push-2": "tools/pr/prepr.sh", "body_push-3": "tools/pr/prepr.sh", "body_push-4": "tools/pr/prepr.sh",
+           "carry_audit-1": "tools/audit/seat/bus.sh"}
 
 # The wrappers' own line is the dispatch to the self-tests they delegate.
 # S08's wrapper now runs both tallies (delivery_row.sh's and its own pushes):
diff --git a/dev/governance/roles/standing-dispatch.md b/dev/governance/roles/standing-dispatch.md
index bf5b3b69f..e39c90e31 100644
--- a/dev/governance/roles/standing-dispatch.md
+++ b/dev/governance/roles/standing-dispatch.md
@@ -11,8 +11,9 @@ head and nonce, and the `dispatch/reviewer-rev-<pr>` publish. Report
 `fire-owed <ref>`: a subagent cannot call RemoteTrigger, so the orchestrator
 fires.
 
-**Relay:** run `tools/audit/seat/cloud_relay.sh --confirm`; on a merge verdict
-at the live head, `bus.sh confirm`. Report each `handoff-body/<topic>` return.
+**Relay:** run `tools/audit/seat/cloud_relay.sh pass --confirm`; report each
+`handoff-body/<topic>` return. A beat job takes it over once one cycle's log
+agrees with you; never inline.
 
 ## Read the ref, not the record
 
@@ -35,5 +36,4 @@ pull request that diverged go back to the orchestrator. `bus.sh orphans`
 answers it for every ref at once.
 
 **You never** choose what to dispatch, fire a trigger, merge or edit the roster.
-**Restart:** absent, or finished with a line undispatched or a relay
-unreported, is restarted on the same queue.
+**Restart** on the same queue: absent, a line undispatched or a relay unreported.
diff --git a/dev/programme/delivery/3065.md b/dev/programme/delivery/3065.md
new file mode 100644
index 000000000..c5f0343f7
--- /dev/null
+++ b/dev/programme/delivery/3065.md
@@ -0,0 +1 @@
+- [#3065](https://github.com/tvofi/heatpump_optimizer/pull/3065) — **open**, relay, tick loop, bus and carry_audit carries after #2664 (R10-FLY-RELAY-REVIEW-FF) (R10-FLY-RELAY-REVIEW-FF)
diff --git a/tests/closures.json b/tests/closures.json
index e52d9f6cf..7ef9e183a 100644
--- a/tests/closures.json
+++ b/tests/closures.json
@@ -3891,6 +3891,7 @@
    "dev/audit/harnesses/r10_buffer_store.py",
    "dev/audit/harnesses/r10_card_harmony.mjs",
    "dev/audit/harnesses/r10_card_voice_states.mjs",
+   "dev/audit/harnesses/r10_carry_field_figures.py",
    "dev/audit/harnesses/r10_carry_parser_mutants.py",
    "dev/audit/harnesses/r10_carry_sweep_rows.py",
    "dev/audit/harnesses/r10_channel_line_reach.py",
diff --git a/tools/audit/carry_audit.py b/tools/audit/carry_audit.py
index d004c6b1f..ec891da45 100644
--- a/tools/audit/carry_audit.py
+++ b/tools/audit/carry_audit.py
@@ -24,15 +24,17 @@ starts an item without a bullet. A FINDING item:
   body     anything under `## Forward-carry` or `## Friction` but `none` or
            `n/a: <reason>`; elsewhere, an item whose heading or first words
            match LEAD (out of scope, residual, distinct finding, follow-up ...);
-  verdict  a comment whose first line is `Fix review: <word> <sha>`: an item
-           saying NONBLOCK (non-blocking, not a block, minor, deferred ...)
-           anywhere; else, outside a section holding the block (a heading
-           naming a block, or any heading of a `blocked` verdict), one under a
-           NOTE_HEADING (residual, owed, instrument findings ...) or led by LEAD.
-  evidence a verdict's `## Evidence` section: an item led by LEAD, under a
-           lead, saying DEFERRED (for a later, follow-up, residual ...), or
-           saying NONBLOCK outside the clause that calls its check not a
-           required one ("not a required context and does not block").
+  verdict  a comment whose first line is `Fix review: <word> <sha>`. In a
+           FINDINGS SECTION (a heading opening with FINDINGS_HEADING's words:
+           Findings, Friction, Block, Residuals, Follow-ups ...), and in every
+           section of a `blocked` verdict but `## Evidence`: an item saying
+           NONBLOCK (non-blocking, not a block, minor, deferred ...) outside an
+           owner-approval merge condition and a negated deferral ("nothing is
+           deferred"); else, outside a section holding the block, one under a
+           NOTE_HEADING (residual, owed ...) or led by LEAD.
+  structural  `## Evidence` of any verdict, and every other section of a merge
+           verdict (P308, P314): only an item led by LEAD, under a lead, or
+           carrying a `Carry:` marker; no word inside it is read.
   both     a paragraph that is finding-shaped and ends in `:` is a lead: its
            bullets are the items, it is not one. The bus trailer, `RESULT`
            lines and the attribution line never are.
@@ -101,18 +103,28 @@ CARRY_SECTIONS = ("forward-carry", "friction")
 NONE_ITEM = re.compile(r"^\W*(?:none|n/a)\W*$|^\W*n/a\s*:", re.I)
 # Not a finding wherever it sits: attribution, the bus trailer, raw RESULT lines.
 TRAILER = re.compile(r"^\W*(?:\U0001f916|Co-Authored-By|bus:|Evidence:|RESULT\b)", re.I)
-# A verdict's `## Evidence` section. NONBLOCK is read there too (a nit or a
-# defect left in place says "not blocking" under any heading), except in the
-# clause saying its check is not a required one and, joined by `,` or `and`
-# alone, does not block: a check's state, not a note. Only that clause is
-# freed; a NONBLOCK word anywhere else in its sentence, or one leading a `:`,
-# is read. An item opening with LEAD, under a lead, or saying DEFERRED is a finding.
+# A verdict's `## Evidence` section, and every section of a merge verdict but a
+# findings section, is read by its structure alone (P308, P314): a check's
+# state or a measurement there says "not blocking" or "deferred" as often as a
+# finding does, and the word tuning that freed one shape at a time (P293, P306)
+# parked the train on the next. An item there is a finding only when it opens
+# with LEAD, sits under a lead, or carries a `Carry:` marker.
 EVIDENCE_HEADING = re.compile(r"evidence\b", re.I)
-NOT_REQUIRED = re.compile(r"not (?:a )?required (?:context|check)(?:,?\s+(?:and\s+)?(?:it\s+)?"
-                          r"(?:does not block|is not blocking|not blocking|non-?blocking)(?!\s*:))?", re.I)
-DEFERRED = re.compile(r"follow-?up|(?:for|to|in|until) (?:a |the )?later\b|out of scope|not fixed here"
-                      r"|known[- ]open|distinct finding|residual|caveat|observation|still (?:has|have|needs?) to",
-                      re.I)  # NONBLOCK's own words (deferred, minor, advisory ...) are read beside it
+# A findings section: its heading OPENS with one of these words (a declared
+# grammar, CARRY 5: `## Body (steps 7, 10, non-blocking note 1)` holds check
+# results, not findings, though a NONBLOCK word sits in it). A block heading
+# (BLOCK_HEADING, not NONBLOCK) is one too.
+FINDINGS_HEADING = re.compile(r"^\W*(?:findings?\b|friction\b|residuals?\b|non-?blocking|not blocking"
+                              r"|follow-?ups?\b|out of scope|deferred\b|owed\b|notes?\b|caveats?\b"
+                              r"|observations?\b|instrument findings|carry\b)", re.I)
+# An owner-approval merge condition (P329): the sentence naming an approving
+# review at (or before) the merge, and the one bare sentence after it saying it
+# does not block on that, are a merge condition, not a non-blocking note.
+APPROVAL = re.compile(r"\bapproving review\b.*\b(?:at|before) (?:the )?merge\b", re.I)
+APPROVAL_BARE = re.compile(r"\s*(?:this (?:review|verdict) |this is |it )?(?:flag(?:s|ged)(?: that)?,? (?:and )?)?"
+                           r"(?:does not block(?: on it)?|not a block)\s*[.;]?\s*$", re.I)
+# A negated deferral, "nothing is deferred or owed", defers nothing (#2955 2471d3e6).
+NOTHING = re.compile(r"\bnothing (?:is|was|remains)\b[^.;]*", re.I)
 # The words a seat uses for "this is not done here". LEAD keys an item's first
 # words (or, in a body, its section heading); NONBLOCK flags a verdict item
 # wherever it says so, and is what a blocking section still lets through.
@@ -128,6 +140,8 @@ BLOCK_HEADING = re.compile(r"\bblock", re.I)
 
 CARRY = re.compile(r"(?<![\w-])Carry:")
 ITEM_REF = re.compile(r"\(item\s+([0-9a-f]{8})\)")
+# `Carry: <dest> (item <id>, supersedes <old>)` (P296): retires <old> for that item alone.
+SUPERSEDES = re.compile(r"\(item\s+([0-9a-f]{8}),\s*supersedes\s+([^\s),]+)\)")
 # a code span as CommonMark closes one: a backtick run closes only on a run of
 # exactly its own length, on its line or a later one of the same item
 CODE_SPAN = re.compile(r"(?<!`)(`+)(?!`)[\s\S]*?(?<!`)\1(?!`)")
@@ -137,6 +151,23 @@ BRIEF_TOK = re.compile(r"\AO(\d+)(?:-[a-z0-9][a-z0-9-]*)?\Z")
 
 
 # ------------------------------------------------------------------ parsing
+def freed(t: str) -> str:
+    """<t> less what reads NONBLOCK without being a note: each APPROVAL sentence
+    (split on `.` and `;`) with the APPROVAL_BARE sentence right after it, and
+    each NOTHING clause."""
+    out, after = [], False
+    for part in re.split(r"(?<=[.;])", t):
+        if APPROVAL.search(part):
+            after = True
+            continue
+        if after and APPROVAL_BARE.match(part):  # only the one sentence after it
+            after = False
+            continue
+        after = False
+        out.append(part)
+    return NOTHING.sub(" ", "".join(out))
+
+
 def items(text: str, verdict: bool) -> list[dict]:
     """The finding-shaped items of one markdown text, in order:
     {"id", "section", "text", "flagged"} (every item; `flagged` marks the
@@ -190,29 +221,30 @@ def items(text: str, verdict: bool) -> list[dict]:
             cur.append(ln)
     flush()
 
-    lead_flag = False
+    lead_flag, lead_sec = False, None
     blocked_verdict = text.split(None, 3)[2:3] == ["blocked"]  # read only for a verdict
     for it in out:
         sec = it["section"]
         t = it["text"]
         first = re.sub(r"^[\s>*_`-]*(?:\d+[.)]\s*)?[*_`]*", "", t)
-        if it["kind"] != "bullet":
+        # a lead's bullets end at a non-bullet, and at its section's end (CARRY 3, #2645)
+        if it["kind"] != "bullet" or sec != lead_sec:
             lead_flag = False
         inherited = lead_flag  # a non-bullet has just reset it
         why = ""
+        # The block is owed in this pull request, so a section that holds it
+        # -- a block heading, or any heading of a `blocked` verdict -- makes
+        # nothing a note unless it says it is not the block.
+        block_sec = BLOCK_HEADING.search(sec) and not NONBLOCK.search(sec)
         if TRAILER.match(first) or VERDICT.match(first):
             pass
-        elif verdict and EVIDENCE_HEADING.match(sec):
-            claims = NOT_REQUIRED.sub(" ", t)
-            why = ("lead" if LEAD.match(first) else "evidence" if DEFERRED.search(t) or NONBLOCK.search(claims)
-                   else "under lead" if inherited else "")
+        elif verdict and (EVIDENCE_HEADING.match(sec)
+                          or not (blocked_verdict or block_sec or FINDINGS_HEADING.match(sec))):
+            why = ("lead" if LEAD.match(first) else "under lead" if inherited
+                   else "carry" if carry_segments(t) else "")
         elif verdict:
-            # The block is owed in this pull request, so a section that holds it
-            # -- a block heading, or any heading of a `blocked` verdict -- makes
-            # nothing a note unless it says it is not the block.
-            block_sec = BLOCK_HEADING.search(sec) and not NONBLOCK.search(sec)
             note_sec = NONBLOCK.search(sec) if blocked_verdict else NOTE_HEADING.search(sec)
-            why = ("non-blocking" if NONBLOCK.search(t) else "" if block_sec
+            why = ("non-blocking" if NONBLOCK.search(freed(t)) else "" if block_sec
                    else "section" if note_sec else "lead" if LEAD.match(first)
                    else "under lead" if inherited else "")
         elif sec.lower() in CARRY_SECTIONS:
@@ -224,7 +256,7 @@ def items(text: str, verdict: bool) -> list[dict]:
         it["why"] = why
         it["lead"] = False
         if it["kind"] == "para" and t.endswith(":") and flagged:
-            lead_flag, it["lead"] = True, True  # a lead: its bullets carry
+            lead_flag, lead_sec, it["lead"] = True, sec, True  # a lead: its bullets carry
             flagged = False
         it["flagged"] = flagged
         it["id"] = hashlib.sha1(re.sub(r"\s+", " ", t).encode()).hexdigest()[:8]
@@ -246,17 +278,21 @@ def carry_segments(text: str) -> list[str]:
     return segs
 
 
-def carry_refs(text: str) -> "tuple[list[str], dict[str, list[str]]]":
-    """The destinations of <text>'s markers, and each item id a marker names
-    with every destination the markers naming it name: an id counts only as
-    `(item <id>)` inside a marker's own segment."""
-    found, refs = [], {}
+def carry_refs(text: str) -> "tuple[list[str], dict[str, list[str]], dict[str, list]]":
+    """The destinations of <text>'s markers; each item id a marker names, with
+    every destination the markers naming it name (an id counts only as
+    `(item <id>)` or `(item <id>, supersedes <old>)` inside a marker's own
+    segment); and each superseded token, `(old, its marker's destinations)`."""
+    found, refs, sups = [], {}, {}
     for seg in carry_segments(text):
         ds = seg_dests(seg)
         found += ds
         for ref in ITEM_REF.findall(seg):
             refs.setdefault(ref, []).extend(ds)
-    return found, refs
+        for ref, old in SUPERSEDES.findall(seg):
+            refs.setdefault(ref, []).extend(ds)
+            sups.setdefault(ref, []).append((old.strip("`*_.:"), ds))
+    return found, refs, sups
 
 
 def carry_dests(text: str) -> list[str]:
@@ -340,10 +376,11 @@ class Dests:
 
 
 def load_dests(repo: Path = ROOT, ref: str | None = None, briefs_dir: str | None = None,
-               issue_state=None) -> Dests:
+               issue_state=None, extra_ref: str | None = None) -> Dests:
     # A carry file's destination issue is its own `issue` field (brief_lint.mjs
     # owns the file-name grammar and refuses a name that disagrees with it).
     round_roster = None
+    git = roster_lib.git_in(str(repo))
     if ref:
         roster = roster_lib.show_roster(str(repo), ref)
         r = subprocess.run(["git", "-C", str(repo), "ls-tree", "--name-only", ref, CARRIES_DIR + "/"],
@@ -351,7 +388,6 @@ def load_dests(repo: Path = ROOT, ref: str | None = None, briefs_dir: str | None
         texts = [subprocess.run(["git", "-C", str(repo), "show", f"{ref}:{n}"], capture_output=True,
                                 text=True).stdout for n in r.stdout.split() if n.endswith(".json")]
     else:
-        git = roster_lib.git_in(str(repo))
         # A checkout behind origin/main reads main's roster, not its own stale
         # one (P98: a detached checkout 387 commits behind refused groups open
         # on main). One containing it keeps its tree, so a pull request's own
@@ -367,11 +403,21 @@ def load_dests(repo: Path = ROOT, ref: str | None = None, briefs_dir: str | None
         else:
             roster = roster_lib.load_roster_file(str(repo / roster_lib.roster_path(str(repo))))
         texts = [p.read_text() for p in sorted((repo / CARRIES_DIR).glob("*.json"))]
-        # The tree's roster lags the round's branch (finding-propagation.md);
-        # a branch this clone lacks is skipped, which only narrows what passes.
-        rref = roster_lib.round_ref(git)
-        if rref and not git(["rev-parse", "--verify", "--quiet", rref + "^{commit}"])[0]:
-            round_roster = (rref, roster_lib.show_roster(str(repo), rref))
+    # The roster at main, or at an explicit ref, lags the round's branch
+    # (finding-propagation.md counts a carry landed there), on either path
+    # (P319: the pre-flight's explicit origin/main parked two carries the round
+    # branch held); a branch this clone lacks is skipped, which only narrows
+    # what passes, and a ref that is the round's own is not read twice.
+    rref = roster_lib.round_ref(git)
+    if rref and rref != ref and not git(["rev-parse", "--verify", "--quiet", rref + "^{commit}"])[0]:
+        round_roster = (rref, roster_lib.show_roster(str(repo), rref))
+    # A pull request that adds its own carry file routes to it (P43): the issues of <extra_ref>'s
+    # carry files join the set, read with one local ls-tree; an unreadable ref adds nothing.
+    if extra_ref:
+        r = subprocess.run(["git", "-C", str(repo), "ls-tree", "--name-only", extra_ref, CARRIES_DIR + "/"],
+                           capture_output=True, text=True)
+        texts += [subprocess.run(["git", "-C", str(repo), "show", f"{extra_ref}:{n}"], capture_output=True,
+                                 text=True).stdout for n in r.stdout.split() if n.endswith(".json")]  # mut:extra
     carry = set()
     for t in texts:
         try:
@@ -392,32 +438,90 @@ def finding_rows(body: str, comments: list[dict]) -> "tuple[list[dict], dict]":
         b = c.get("body") or ""
         if VERDICT.match(b.lstrip()):
             texts.append((f"review {c.get('id')}", b, True))
-    rows, refs = [], {}
+    rows, refs, sups = [], {}, {}
     for where, text, verdict in texts:
         for it in items(text, verdict):
-            ds, named = carry_refs(it["text"])
+            ds, named, sup = carry_refs(it["text"])
             for ref, rds in named.items():
                 refs.setdefault(ref, []).extend(rds)
+            for ref, olds in sup.items():
+                sups.setdefault(ref, []).extend(olds)
             if it["flagged"]:
                 rows.append({"where": where, **it, "dests": ds})
-    return rows, refs
+    return rows, refs, sups
 
 
 def audit(body: str, comments: list[dict], dests: Dests) -> dict:
     """Every finding item of a body and its verdict comments, each with its
     disposition: routed (with its destinations), unrouted, or bad."""
-    rows, refs = finding_rows(body, comments)
+    rows, refs, sups = finding_rows(body, comments)
     for r in rows:
         r["dests"] = r["dests"] + refs.get(r["id"], [])
         bad, notes = [], []
+        # A supersede retires a bad token of this item only, printed, never dropped silently; one
+        # naming a valid destination is refused, so a live routing cannot be undone by it (P296).
+        for old, new in sups.get(r["id"], []):
+            if dests.check(old)[0]:
+                bad.append(f"{old}: a supersede names a valid destination (item {r['id']}); only a bad one retires")
+            elif old in r["dests"]:
+                r["dests"] = [t for t in r["dests"] if t != old]
+                notes.append(f"{old} superseded by {', '.join(new) or '-'} (item {r['id']})")
         for tok in r["dests"]:
             ok, note = dests.check(tok)
             (notes if ok else bad).append(f"{tok}: {note}" if note else tok)
         r["bad"], r["notes"] = bad, notes
-        r["status"] = "unrouted" if not r["dests"] else ("bad" if bad else "routed")
+        r["status"] = "bad" if bad else "unrouted" if not r["dests"] else "routed"
     return {"rows": rows}
 
 
+# ------------------------------------------------------------ the landing
+def group_text(dests: Dests, group: str) -> str:
+    """A group's brief and carries, on main's roster and on the round's branch."""
+    out = []
+    for g in (dests.groups.get(group), dests.round_groups.get(group)):
+        if g:
+            out += [str(g.get("brief") or "")] + [str(c) for c in (g.get("carry") or [])]
+    return "\n".join(out)
+
+
+def landed(body: str, dests: Dests, source: str = "") -> list[dict]:
+    """Each (finding item, GROUP destination) of a body whose group's brief or
+    carries hold neither the item id nor the source (`#<pr>` or the handoff
+    topic: P310, an id re-minted by a reword still lands by its source), or
+    whose group is no valid destination. A `dismissed:` item, a `#N` and an
+    O-brief need no landing. Each: {"group", "id", "text", "why"}."""
+    out = []
+    srcs = [x for x in re.split(r"[\s,]+", source) if x]
+    for r in audit(body, [], dests)["rows"]:
+        for tok in r["dests"]:
+            if not GROUP_TOK.match(tok):
+                continue
+            ok, note = dests.check(tok)
+            if not ok:
+                out.append({"group": tok, "id": r["id"], "text": r["text"], "why": f"bad destination: {note}"})
+                continue
+            words = set(re.split(r"[^\w#-]+", group_text(dests, tok)))  # whole tokens: #25581 is not #2558
+            keys = [r["id"]] + srcs
+            if not any(k in words for k in keys):  # mut:landed
+                out.append({"group": tok, "id": r["id"], "text": r["text"], "why": "not in its brief or carries"})
+    return out
+
+
+def land_ops(missing: list[dict], pr: str = "", topic: str = "") -> list[str]:
+    """roster_edit.py's append-carry op for each missing landing a carry can
+    make (never a bad destination), tagged `(items <id>)`, one per tag."""
+    ops, seen = [], set()
+    src = f"From {pr} ({topic})" if pr and topic else f"From {pr or topic or 'this pull request'}"
+    for m in missing:
+        if m["why"].startswith("bad destination") or (m["group"], m["id"]) in seen:
+            continue
+        seen.add((m["group"], m["id"]))
+        one = re.sub(r"^[-*+]\s+", "", re.sub(r"\s+", " ", m["text"]).strip())
+        text = f"{src}, body item {m['id']}: {one} (items {m['id']})"
+        ops.append("append-carry " + m["group"] + " '" + text.replace("'", "'\\''") + "'")
+    return ops
+
+
 def report(res: dict, label: str = "") -> int:
     rows = res["rows"]
     for r in rows:
@@ -539,10 +643,16 @@ def main(argv: list[str]) -> int:
     p.add_argument("--repo", default=REPO)
     p.add_argument("--briefs-dir")
     p.add_argument("--roster-ref", action="append", default=[])
+    p.add_argument("--git-dir", default=str(ROOT), help="the checkout whose refs the roster is read at")
     sub = p.add_subparsers(dest="cmd", required=True)
     c = sub.add_parser("check")
     c.add_argument("--body", required=True)
     c.add_argument("--comments")
+    for name in ("landed", "land-ops"):
+        x = sub.add_parser(name)
+        x.add_argument("--body", required=True)
+        x.add_argument("--pr", default="", help="the source pull request, #<N>")
+        x.add_argument("--topic", default="", help="the source handoff topic")
     r = sub.add_parser("pr")
     r.add_argument("n", type=int)
     s = sub.add_parser("sweep")
@@ -558,9 +668,29 @@ def main(argv: list[str]) -> int:
     ref = a.roster_ref[0] if a.roster_ref else None
     try:
         if a.cmd == "check":
-            dests = load_dests(ROOT, ref, a.briefs_dir)
+            body = Path(a.body).read_text()
             comments = json.loads(Path(a.comments).read_text()) if a.comments else []
-            return report(audit(Path(a.body).read_text(), comments, dests))
+            if not finding_rows(body, comments)[0]:
+                return report({"rows": []})  # nothing to route: the roster is not read
+            dests = load_dests(Path(a.git_dir), ref, a.briefs_dir)
+            return report(audit(body, comments, dests))
+        if a.cmd in ("landed", "land-ops"):
+            # rc 0 every carry landed, 1 one is missing (CARRY-MISSING lines), 3 the roster unreadable
+            try:
+                dests = load_dests(Path(a.git_dir), ref, a.briefs_dir)
+            except (roster_lib.RosterNotFound, ValueError, OSError) as e:
+                print(f"carry_audit: UNREAD the roster: {e}")
+                return 3
+            missing = landed(Path(a.body).read_text(), dests, f"{a.pr} {a.topic}")
+            if a.cmd == "land-ops":
+                for op in land_ops(missing, a.pr, a.topic):
+                    print(op)
+                return 1 if missing else 0
+            for m in missing:
+                one = re.sub(r"\s+", " ", m["text"])[:100]
+                print(f"CARRY-MISSING {m['group']} body item {m['id']}: {m['why']}: {one!r}")
+            print(f"CARRY-LANDED: {len(missing)} missing")
+            return 1 if missing else 0
         if a.cmd == "pr":
             dests = load_dests(ROOT, ref, a.briefs_dir, gh_issue_state(a.repo))
             body, comments = read_pr(a.n, a.repo, None)
@@ -711,6 +841,26 @@ def _self_test() -> int:
     r = run(plant.rstrip() + " Carry: R10-BRANCH\n", d=load_dests(Path(gtmp.name)))
     check("load_dests reads the round ref: a group only there passes, the note naming it",
           r["b"] == 0 and any(rnd[0] in n for x in r["rows"] for n in x["notes"]))
+    # P43: a pull request's own new carry file routes its `#N` at the pre-flight (extra_ref, its head).
+    git("checkout", "-q", "-b", "pr-carry")
+    Path(gtmp.name, CARRIES_DIR).mkdir(parents=True, exist_ok=True)
+    Path(gtmp.name, CARRIES_DIR, "carry-777.json").write_text('{"issue": 777}')
+    git("add", "-A")
+    git("commit", "-qm", "the pull request adds carry-777.json")
+    git("checkout", "-q", "-")
+    r = run(plant.rstrip() + " Carry: #777\n", d=load_dests(Path(gtmp.name), "origin/main"))
+    check("P43: a #N whose carry file only the pull request's head adds is bad at origin/main (before)", r["b"] == 1)
+    r = run(plant.rstrip() + " Carry: #777\n", d=load_dests(Path(gtmp.name), "origin/main", extra_ref="pr-carry"))
+    check("P43: ... and routes once the head is the extra ref (after)", r["b"] == 0)
+    r = run(plant.rstrip() + " Carry: #778\n", d=load_dests(Path(gtmp.name), "origin/main", extra_ref="pr-carry"))
+    check("P43: a #N with a carry file in neither main nor the head still refuses (null control)", r["b"] == 1)
+    # P319: an explicit ref (the pre-flight's origin/main) reads the round ref too.
+    r = run(plant.rstrip() + " Carry: R10-BRANCH\n", d=load_dests(Path(gtmp.name), "origin/main"))
+    check("load_dests at an explicit origin/main routes a group only on the round ref (P319)", r["b"] == 0)
+    r = run(plant.rstrip() + " Carry: R10-NEITHER\n", d=load_dests(Path(gtmp.name), "origin/main"))
+    check("... a group on neither is still BAD-DEST at an explicit ref (null control)", r["b"] == 1)
+    r = run(plant.rstrip() + " Carry: R10-BRDONE\n", d=load_dests(Path(gtmp.name), "origin/main"))
+    check("... and a group done on the round ref is still refused at an explicit ref", r["b"] == 1)
     git("update-ref", "-d", "refs/remotes/" + rnd[0])
     r = run(plant.rstrip() + " Carry: R10-BRANCH\n", d=load_dests(Path(gtmp.name)))
     check("... and a clone without that ref refuses it (null control)", r["b"] == 1)
@@ -982,8 +1132,8 @@ def _self_test() -> int:
                                "Non-blocking:", "Not blocking:", "Caveat:", "Observation:", "Deferred:",
                                "Advisory:", "Minor:", "A follow-up:", "An observation:", "One caveat:",
                                "Two follow-ups:", "Three caveats:")]
-    item_grammar += [(f"NONBLOCK reads {w!r} mid-sentence", head,
-                      verdict_of("merge", f"## Verified\n\n- the check is {w} here.\n"), [("non-blocking", U)])
+    item_grammar += [(f"NONBLOCK reads {w!r} mid-sentence in a findings section", head,
+                      verdict_of("merge", f"## Findings\n\n- the check is {w} here.\n"), [("non-blocking", U)])
                      for w in ("not blocking", "not a block", "neither blocks", "does not block", "not owed here",
                                "owed to the record", "minor", "advisory", "a secondary note", "deferred")]
     item_grammar += [(f"NOTE_HEADING reads {w!r}", head, verdict_of("merge", f"## {w}\n\n- a re-booking.\n"),
@@ -999,7 +1149,7 @@ def _self_test() -> int:
         ("under Friction a `word:` line without the kind's colon continues the item",
          head + "## Friction\n\n- a: unclear: x\nNote: this continues it. Carry: R10-LIVE\n", (), [("section", R_)]),
         ("a verdict naming a short SHA is read", head,
-         [{"id": 50, "body": "Fix review: merge abc1234\n\n## Verified\n\n- a minor note.\n"}], [("non-blocking", U)]),
+         [{"id": 50, "body": "Fix review: merge abc1234\n\n## Findings\n\n- a minor note.\n"}], [("non-blocking", U)]),
     ]
     item_grammar += [("a numbered list item is a bullet",
                       head + "## Friction\n\n1. a: unclear: x.\n2. b: cost: y. Carry: R10-LIVE\n", (),
@@ -1012,31 +1162,38 @@ def _self_test() -> int:
                           "and does not block the PR (tests.yml:2775).\n"), []),
         ("... `not required check` reads too", head,
          verdict_of("merge", "## Evidence\n\n- composed-proof is not required check and does not block.\n"), []),
-        ("under the Evidence heading a check that does not block, not said to be unrequired, is a note", head,
-         verdict_of("merge", "## Evidence\n\n- composed-proof is queued and does not block the PR.\n"),
-         [("evidence", U)]),
-        ("the carve-out is its clause's: a nit after it is a finding (#2441's shape)", head,
+        ("P308: under the Evidence heading a check that does not block is no finding, unrequired or not", head,
+         verdict_of("merge", "## Evidence\n\n- composed-proof is queued and does not block the PR.\n"), []),
+        # #2441's and #2465's rows flip (P308): a defect handed on belongs under `## Findings`, or opens
+        # with a lead, where it is read; under Evidence only the structure is.
+        ("P308: #2441's shape under the Evidence heading passes (a nit belongs under ## Findings)", head,
          verdict_of("merge", "## Evidence\n\n- composed-proof is not a required check and does not block. One nit, "
-                    "not blocking: the usage string still lists the arm names by hand.\n"), [("evidence", U)]),
-        ("a defect left in place, not blocking, under the Evidence heading is a finding (#2465's shape)", head,
+                    "not blocking: the usage string still lists the arm names by hand.\n"), []),
+        ("P308: #2465's shape under the Evidence heading passes (a defect handed on opens with a lead)", head,
          verdict_of("merge", "## Evidence\n\n- A hand-set fractional floor is written 0.27 K low and the check "
+                    "re-raises the issue; the selector cannot produce it, so it is not blocking.\n"), []),
+        ("... the same #2465 sentence under ## Findings is a finding (null control)", head,
+         verdict_of("merge", "## Findings\n\n- A hand-set fractional floor is written 0.27 K low and the check "
                     "re-raises the issue; the selector cannot produce it, so it is not blocking.\n"),
-         [("evidence", U)]),
+         [("non-blocking", U)]),
         ("the Evidence heading reads in any case and with words after it", head,
          verdict_of("merge", "## EVIDENCE (not findings)\n\n- nightly-status: not a required check, not blocking.\n"),
          []),
         ("a heading that only mentions evidence is not the Evidence heading", head,
          verdict_of("merge", "## Notes on evidence\n\n- nightly-status: not a required check, not blocking.\n"),
          [("non-blocking", U)]),
-        ("a heading whose first word only starts `evidence` is not the Evidence heading", head,
-         verdict_of("merge", "## Evidenced claims\n\n- nightly-status: not a required check, not blocking.\n"),
+        ("a heading whose first word only starts `evidence` is not the Evidence heading (a blocked verdict reads it)",
+         head, verdict_of("blocked", "## Evidenced claims\n\n- nightly-status: not a required check, not blocking.\n"),
          [("non-blocking", U)]),
-        ("a deferral under the Evidence heading is a finding", head,
-         verdict_of("merge", "## Evidence\n\n- M4 survives, not blocking, noted for a later tightening.\n"),
-         [("evidence", U)]),
-        ("... and routed by its own Carry: it passes (null control)", head,
-         verdict_of("merge", "## Evidence\n\n- M4 survives, noted for a later tightening. "
-                    "Carry: dismissed: fail-closed survivor\n"), [("evidence", R_)]),
+        ("P308: a deferral word under the Evidence heading is not read", head,
+         verdict_of("merge", "## Evidence\n\n- M4 survives, not blocking, noted for a later tightening.\n"), []),
+        ("P308: an Evidence item carrying Carry: <live group> routes", head,
+         verdict_of("merge", "## Evidence\n\n- M4 survives, noted for a later tightening. Carry: R10-LIVE\n"),
+         [("carry", R_)]),
+        ("P308: an Evidence item carrying Carry: <done group> is a bad destination", head,
+         verdict_of("merge", "## Evidence\n\n- M4 survives. Carry: R10-OVER\n"), [("carry", "bad")]),
+        ("P308: an Evidence item opening `Follow-up:` is a finding (null control)", head,
+         verdict_of("merge", "## Evidence\n\n- Follow-up: the census misses one.\n"), [("lead", U)]),
         ("a LEAD opening under the Evidence heading is a finding", head,
          verdict_of("merge", "## Evidence\n\n- Residual: the census misses one.\n"), [("lead", U)]),
         ("a lead's bullets under the Evidence heading are findings", head,
@@ -1048,20 +1205,20 @@ def _self_test() -> int:
         ("a time `later` under the Evidence heading is no deferral", head,
          verdict_of("merge", "## Evidence\n\n- a run 2.5 s later takes the lock.\n"), []),
     ]
-    item_grammar += [(f"DEFERRED reads {w!r} under the Evidence heading", head,
-                      verdict_of("merge", f"## Evidence\n\n- the check is {w} here.\n"), [("evidence", U)])
+    item_grammar += [(f"P308: {w!r} under the Evidence heading is not read", head,
+                      verdict_of("merge", f"## Evidence\n\n- the check is {w} here.\n"), [])
                      for w in ("a follow-up", "out of scope", "not fixed here", "known-open",
                                "a distinct finding", "residual", "for later", "moved to a later round",
                                "fixed in the later pass", "left until later", "a caveat", "an observation",
                                "still has to", "still have to", "still needs to", "deferred", "advisory",
                                "minor", "a secondary note", "owed to the record", "not owed here")]
-    item_grammar += [("a `;` ends a sentence: a nit after a not-required check's clause is a finding", head,
-                      verdict_of("merge", "## Evidence\n\n- composed-proof is not a required check; "
-                                 "one nit, not blocking: x.\n"), [("evidence", U)])]
+    item_grammar += [("under ## Findings a nit after a not-required check is a finding", head,
+                      verdict_of("merge", "## Findings\n\n- composed-proof is not a required check; "
+                                 "one nit, not blocking: x.\n"), [("non-blocking", U)])]
     # The carve-out frees the check's own clause, never its sentence: each
     # nit or defect sharing a sentence with it is a finding (round 2's attack).
-    item_grammar += [(f"a {k} beside a not-required check's clause is a finding", head,
-                      verdict_of("merge", f"## Evidence\n\n- {v}\n"), [("evidence", U)]) for k, v in (
+    item_grammar += [(f"under ## Findings a {k} beside a not-required check is a finding", head,
+                      verdict_of("merge", f"## Findings\n\n- {v}\n"), [("non-blocking", U)]) for k, v in (
         ("nit", "nightly-status is not a required check, and one nit is not blocking: the usage string."),
         ("minor defect", "composed-proof is not a required check and a minor defect stays, not blocking."),
         ("defect", "The guard misses a deleted ref, which is not a required check to fix, so not blocking."),
@@ -1075,6 +1232,141 @@ def _self_test() -> int:
                       [])]
     item_grammar += [("a later-stage compound is no deferral", head,
                       verdict_of("merge", "## Evidence\n\n- I found no later-stage finding.\n"), [])]
+    # The field items (dev/audit/harnesses/r10_carry_field_verdicts.json, verbatim): each was flagged at
+    # origin/main 7539d1675 and is no finding -- P308's four, P293's class A and C, P329's #3005 and
+    # #3013, CARRY 5's #2683 `## Body (steps 7, 10, non-blocking note 1)` four, #2955's "None."
+    fx = json.loads((ROOT / "dev/audit/harnesses/r10_carry_field_verdicts.json").read_text())
+    item_grammar += [(f"field item {i} (#{x['pr']} {x['verdict']}, ## {x['section']}) is no finding", head,
+                      verdict_of(x["verdict"], f"## {x['section']}\n\n{x['text']}\n"), [])
+                     for i, x in sorted(fx["items"].items())]
+    ap = fx["items"]["fccf8846"]["text"]
+    item_grammar += [
+        # P314: a merge verdict's every section but a findings section is read by its structure.
+        ("P314: #3013's code-owner note under a merge verdict's ## Findings is still read", head,
+         verdict_of("merge", "## Findings\n\n- `away.py` is code-owned, and a defect in it does not block.\n"),
+         [("non-blocking", U)]),
+        ("P314: a merge verdict's Summary item with a NONBLOCK word is no finding", head,
+         verdict_of("merge", "## Summary\n\n- the docs-only diff does not block on the nightly lane.\n"), []),
+        ("P314: a Summary line opening `Follow-up:` is a finding (null control)", head,
+         verdict_of("merge", "## Summary\n\nFollow-up: the census misses one.\n"), [("lead", U)]),
+        ("P314: a blocked verdict's Summary item keeps today's reading (null control)", head,
+         verdict_of("blocked", "## Summary\n\n- a minor defect stays.\n"), [("non-blocking", U)]),
+        ("CARRY 5: a heading that only holds a non-blocking word is no findings section (#2683)", head,
+         verdict_of("merge", "## Body (steps 7, 10, non-blocking note 1)\n\n- `figure_lint` printed 0 refused.\n"), []),
+        ("CARRY 5: a heading opening with a findings word is one (null control)", head,
+         verdict_of("merge", "## Non-blocking notes (steps 7, 10)\n\n- `figure_lint` printed 0 refused.\n"),
+         [("section", U)]),
+        # P329: an owner-approval merge condition, and its one bare sentence, read no NONBLOCK.
+        ("a blocked verdict's own first line is not a finding, whatever it says", head,
+         [{"id": 48, "body": f"Fix review: blocked {'d' * 40} harness: a minor note\n\n## Block\n\n- x.\n"}], []),
+        ("P314: a block heading in a merge verdict still reads NONBLOCK", head,
+         verdict_of("merge", "## Block\n\n- a minor nit stays.\n"), [("non-blocking", U)]),
+        ("P329: a bare `does not block` sentence with no approval before it is read (null control)", head,
+         verdict_of("merge", "## Findings\n\n- A defect in x stays. It does not block.\n"), [("non-blocking", U)]),
+        ("P329: only the one sentence right after the approval is freed", head,
+         verdict_of("merge", "## Findings\n\n- x.py needs tvofi's approving review at merge. A defect in y stays. "
+                    "It does not block.\n"), [("non-blocking", U)]),
+        ("P329: #3013's approval note under ## Findings clears", head,
+         verdict_of("merge", f"## Findings\n\n{ap}\n"), []),
+        ("P329: the approval note in a blocked verdict clears", head,
+         verdict_of("blocked", "## Notes\n\n- x.py is code-owned, so tvofi's approving review is required at merge. "
+                    "This review does not block on it.\n"), []),
+        ("P329: the approval sentence then a defect left in place stays a finding (null control)", head,
+         verdict_of("blocked", "## Notes\n\n- x.py is code-owned, so tvofi's approving review is required at merge. "
+                    "A defect in y is left in place, not blocking.\n"), [("non-blocking", U)]),
+        ("P329: code-owned with a defect that does not block stays a finding (null control)", head,
+         verdict_of("blocked", "## Notes\n\n- x.py is code-owned and a defect in it does not block.\n"),
+         [("non-blocking", U)]),
+        ("P329: #2281's line under a residual heading stays a finding (null control)", head,
+         verdict_of("merge", "## Residuals (not blocking)\n\n- tests.yml line 3908 comment names the removed "
+                    "roster_lib.ROSTER_PATH. It is code-owned and routed to TICK-ORCH.\n"), [("section", U)]),
+        ("a negated deferral, `nothing is deferred or owed`, is no finding (#2955 2471d3e6)", head,
+         verdict_of("merge", "## Findings\n\n- None. Nothing is deferred.\n"), []),
+        ("... a deferral is still one (null control)", head,
+         verdict_of("merge", "## Findings\n\n- A defect in x is deferred.\n"), [("non-blocking", U)]),
+        # CARRY 3: a lead's bullets end at its section's end.
+        ("CARRY 3: a lead's bullets in a later section do not inherit it (#2645)", head,
+         verdict_of("blocked", "## Notes\n\nTwo more survivors. Neither blocks, but:\n\n- s1.\n\n"
+                    "## Brief checklist\n\n- the brief names the file.\n"), [("under lead", U)]),
+        ("CARRY 3: a LEAD bullet under a checklist heading still counts (null control)", head,
+         verdict_of("blocked", "## Notes\n\nTwo more survivors. Neither blocks, but:\n\n- s1.\n\n"
+                    "## Brief checklist\n\n- Residual: the census misses one.\n"), [("under lead", U), ("lead", U)]),
+    ]
+    item_grammar += [(f"FINDINGS_HEADING reads {w!r}: its NONBLOCK item is a finding", head,
+                      verdict_of("merge", f"## {w}\n\n- a minor nit stays.\n"), [("non-blocking", U)])
+                     for w in ("Findings", "Friction", "Block", "Residuals", "Non-blocking", "Not blocking (x)",
+                               "Follow-ups", "Out of scope", "Deferred", "Owed", "Notes", "Caveats", "Observations",
+                               "Instrument findings", "Carry forward", "What blocks the merge")]
+    item_grammar += [(f"P329: the bare {w!r} after an approval sentence is freed", head,
+                      verdict_of("blocked", f"## Notes\n\n- x.py needs tvofi's approving review {m} merge. {w}\n"), [])
+                     for m, w in (("at", "This is not a block."), ("before the", "It does not block on it."),
+                                  ("at the", "This verdict flagged that and does not block."))]
+    item_grammar += [(f"a negated deferral reads {w!r}", head,
+                      verdict_of("merge", f"## Findings\n\n- None. Nothing {w} deferred.\n"), [])
+                     for w in ("is", "was", "remains")]
+    # P296: `Carry: <dest> (item <id>, supersedes <old>)` retires a bad <old> for that item alone.
+    def sup_rows(old_dest: str, marker: str, other: str = "") -> dict:
+        vc = verdict_of("merge", f"## Findings\n\n- a minor nit stays. Carry: {old_dest}\n{other}")
+        iid = ([x["id"] for x in items(vc[0]["body"], True) if x["flagged"]] + [""])[0]
+        res = run(head + "## Forward-carry\n\n- " + marker.replace("<id>", iid) + "\n", vc)
+        # a mutant that reads no row fails these checks, never crashes them
+        return {r["id"]: r for r in res["rows"] if r["where"].startswith("review")}.get(
+            iid, {"id": iid, "status": None, "notes": [], "bad": []})
+    r = sup_rows("R10-OVER", "Carry: R10-LIVE (item <id>, supersedes R10-OVER)")
+    check("P296: a bad destination superseded for its item routes (the #2925 and #2962 shape)", r["status"] == "routed")
+    check("... and the retired token prints as a NOTE, never dropped silently",
+          "R10-OVER superseded by R10-LIVE (item " + r["id"] + ")" in r["notes"])
+    r = sup_rows("R10-OVER", "Carry: R10-LIVE (item <id>, supersedes `R10-OVER`)")
+    check("P296: a backticked superseded token reads as the bare token", r["status"] == "routed")
+    r = sup_rows("R10-OVER", "Carry: R10-LIVE (item <id>)")
+    check("P296 null control: without `supersedes` the item stays bad", r["status"] == "bad")
+    r = sup_rows("R10-LIVE", "Carry: R10-LIVE (item <id>, supersedes R10-LIVE)")
+    check("P296: a supersede of a valid destination is refused, naming the item",
+          r["status"] == "bad" and any("a supersede names a valid destination (item " + r["id"] in b for b in r["bad"]))
+    r = sup_rows("R10-OVER", "Carry: R10-INVENTED (item <id>, supersedes R10-OVER)")
+    check("P296: a supersede whose new destination is bad stays bad", r["status"] == "bad")
+    r = sup_rows("R10-OVER", "Carry: R10-LIVE (item 0badc0de, supersedes R10-OVER)")
+    check("P296: a supersede naming another item's id leaves this item bad", r["status"] == "bad")
+    # CARRY 0 / P310: `landed` -- each body item's GROUP carry holds the item id or its source.
+    Dl_roster = {"groups": [
+        {"group": "R10-A", "resume": {"stage": "not-started"}, "brief": "Build the A arm.", "carry": []},
+        {"group": "R10-B", "resume": {"stage": "not-started"}, "brief": "Build the B arm.", "carry": []},
+        {"group": "R10-DONE", "resume": {"stage": "done"}, "brief": "", "carry": []}]}
+
+    def dl(a_carry=(), b_carry=()) -> Dests:
+        r_ = json.loads(json.dumps(Dl_roster))
+        r_["groups"][0]["carry"], r_["groups"][1]["carry"] = list(a_carry), list(b_carry)
+        return Dests(r_, {300})
+    lb = head + "## Forward-carry\n\n- The census misses the store seam. Carry: R10-A\n"
+    lid = ([x["id"] for x in items(lb, False) if x["flagged"]] + [""])[0]  # a mutant flagging none fails, never crashes
+    miss = landed(lb, dl())
+    check("landed: a carry not in its group's brief or carries is missing (the #2558 pair, before)",
+          [(m["group"], m["id"]) for m in miss] == [("R10-A", lid)])
+    ops = land_ops(miss, "#2558", "r10-x")
+    check("land-ops: one append-carry op, tagged with the item id",
+          ops == ["append-carry R10-A 'From #2558 (r10-x), body item " + lid
+                  + ": The census misses the store seam. Carry: R10-A (items " + lid + ")'"])
+    landed_text = ops[0].split(" ", 2)[2][1:-1] if ops else ""
+    check("landed: once the op's text is in the group's carries, nothing is missing (the #2558 pair, after)",
+          bool(landed_text) and landed(lb, dl([landed_text])) == [])
+    check("land-ops: a group named twice by one item yields one op (deduped on its tag)",
+          len(land_ops(landed(lb.replace("Carry: R10-A", "Carry: R10-A, R10-A"), dl()))) == 1)
+    check("land-ops: an already landed body yields no op (null control)", land_ops(landed(lb, dl([landed_text]))) == [])
+    check("landed: a carry reworded but naming the item id lands (the #2545 paraphrase)",
+          landed(lb, dl(["From #2545: the store seam is missed by the census (items " + lid + ")"])) == [])
+    check("landed: the id in another group's carries does not land it (the wrong group)",
+          len(landed(lb, dl(b_carry=["(items " + lid + ")"]))) == 1)
+    check("landed: a carry naming the source pull request lands its items (P310)",
+          landed(lb, dl(["From #2558: the census."]), "#2558") == [])
+    check("... and another pull request's number does not (null control)",
+          len(landed(lb, dl(["From #2558: the census."]), "#25581")) == 1)
+    check("landed: a dismissed item and a #N with a carry file need no landing",
+          landed(head + "## Forward-carry\n\n- x. Carry: dismissed: no seam remains\n- y. Carry: #300\n", dl()) == [])
+    md = landed(head + "## Forward-carry\n\n- x. Carry: R10-DONE\n", dl())
+    check("landed: a done destination is missing as a bad destination, and never gets an op",
+          len(md) == 1 and md[0]["why"].startswith("bad destination") and land_ops(md) == [])
+    flagged_2645 = [x["id"] for x in items(fx["verdict_2645"]["whole"], True) if x["flagged"]]
+    check("CARRY 3: #2645's round-1 blocked verdict flags at most one item (8 at 7539d1675)", len(flagged_2645) <= 1)
     for name, text, comments, want in item_grammar:
         got = sorted((x["why"], x["status"]) for x in run(text, comments)["rows"])
         check(f"items: {name}", got == sorted(want))
diff --git a/tools/audit/seat/body_push.sh b/tools/audit/seat/body_push.sh
index 75ba79029..3c308cec5 100644
--- a/tools/audit/seat/body_push.sh
+++ b/tools/audit/seat/body_push.sh
@@ -61,6 +61,20 @@ if [ -n "$HREF" ]; then
   elif [ "$prc" != 0 ]; then
     echo "body_push: the review packet's handoff refusals were not run (rc $prc, above); dispatch still runs structure and hot-file" >&2
   fi
+  # The carry landing (CARRY 11, P287): a body carry its group does not yet hold, on main's
+  # roster or the round's branch, is refused here, so it lands before the open rather than after
+  # a review round (2 of 15 blocked verdicts on 2026-10-29). bus.sh dispatch runs the same check.
+  # rc 3 (the roster unreadable) is said, never a refusal. HPO_HANDOFF_LANDED replaces the check.
+  lrc=0
+  LD=$(cd "$ROOT" && ${HPO_HANDOFF_LANDED:-python3 -I "$ROOT/tools/audit/carry_audit.py" --roster-ref origin/main} \
+    landed --body "$ABS" --topic "$TOPIC" 2>&1) || lrc=$?
+  printf '%s\n' "$LD"
+  if [ "$lrc" = 1 ]; then  # mut:landed
+    echo "body_push: a carry above is not in its group's brief or carries; land it on the round's roster branch (carry_audit.py land-ops), then push the body" >&2
+    exit 1
+  elif [ "$lrc" != 0 ]; then
+    echo "body_push: the carry landing was not checked (rc $lrc, above); bus.sh dispatch checks it again" >&2
+  fi
 else
   echo "body_push: no handoff/$TOPIC on origin, so a result body: the pr-body lint does not apply"
 fi
diff --git a/tools/audit/seat/bus.sh b/tools/audit/seat/bus.sh
index 3338eaffb..91e25d21c 100755
--- a/tools/audit/seat/bus.sh
+++ b/tools/audit/seat/bus.sh
@@ -73,6 +73,12 @@
 # idle; `confirm` keeps the same check as the signed gate. VERDICT.md alone
 # does not count: it names the sha by construction, and `app_approve.sh`'s
 # evidence gate exists to make a forged verdict forge artifacts too.
+# It also refuses, before review/<pr> moves, a verdict with a line its post
+# would refuse (ref_privacy.py body-lines, naming the line: P76), and one whose
+# finding items name no valid `Carry:` (carry_audit.py, the train pre-flight's
+# parser, over the verdict as its one comment, at origin/main and the round's
+# roster branch as last fetched: P40, P207). The push runs with a 500 MB
+# http.postBuffer: a ~30 MB evidence/ once failed HTTP 400 at git's 1 MB (#2563).
 #
 # NONCE VISIBILITY. The record lives in `$S` — `$HPO_BUS_STATE` else
 # `$HOME/.zcode/bus`, a per-machine path. `dispatch`, `push-verdict` and
@@ -193,6 +199,12 @@ dispatch_binding() { # verdict-file pr head -> 0 when the nonce binds to (pr, he
   [ "$rh" = "$3" ] || { printf 'nonce %s was dispatched at head %s, not the head %s this verdict names; mint a fresh dispatch at this head with bus.sh dispatch %s %s <reviewer>' "$n" "$rh" "$3" "$2" "$3"; return 1; }
   return 0
 }
+bot_only() { # head -> rc 0 when the commits in <remote>/main..head are all, and at least one, dependabot[bot]'s
+  local a
+  git fetch -q "$REMOTE" main 2>/dev/null
+  a=$(git log --format=%an "$REMOTE/main..$1" 2>/dev/null) || return 1
+  [ -n "$a" ] && [ -z "$(grep -vxF 'dependabot[bot]' <<< "$a")" ]  # mut:botonly
+}
 numeric() { case $1 in ''|*[!0-9]*) return 1 ;; esac; return 0; }
 approver_key() { # -> the hpo-approver App's private key on this machine, or a non-zero exit
   local k=${HPO_IDENTITY_DIR:-$HOME/.zcode}/identity-approver.pem
@@ -211,6 +223,45 @@ signed_by_approver() { # pr commit -> rc 0 when the commit's bus-signature is th
   rc=$?; rm -rf "$t"; return $rc
 }
 
+carry_landed() { # pr -> rc 1 when a body carry is not in its group (lines and roster ops on stderr); else 0
+  # An unread body or roster is said and the dispatch goes on: the gate cannot judge it.
+  local b out rc
+  b=$(mktemp) || return 0
+  if ! ${HPO_BUS_GH:-gh} api "repos/$REPO/pulls/$1" --jq '.body // ""' > "$b" 2>/dev/null; then
+    echo "BUS carry-landing UNREAD #$1: the body could not be read; the dispatch goes on" >&2; rm -f "$b"; return 0
+  fi
+  out=$(python3 -I "$ROOT/tools/audit/carry_audit.py" --git-dir "$(git rev-parse --show-toplevel)" --roster-ref origin/main \
+    landed --body "$b" --pr "#$1" 2>&1); rc=$?
+  case $rc in
+    0) ;;
+    1) printf '%s\n' "$out" >&2
+       python3 -I "$ROOT/tools/audit/carry_audit.py" --git-dir "$(git rev-parse --show-toplevel)" --roster-ref origin/main \
+         land-ops --body "$b" --pr "#$1" 2>/dev/null | sed 's,^,  roster op: python3 tools/audit/seat/roster_edit.py ,' >&2 ;;
+    *) printf 'BUS carry-landing UNREAD #%s: %s; the dispatch goes on\n' "$1" "$(tail -n 1 <<< "$out")" >&2 ;;
+  esac
+  rm -f "$b"; [ "$rc" != 1 ]  # mut:landed
+}
+carry_gate() { # verdict-file -> rc 0 when each finding item routes, else why, naming the count and the first
+  # carry_audit.py judges, the parser the train's pre-flight runs (decision 0012): the verdict is
+  # its one verdict comment, the roster read at origin/main and the round's branch (P319) as this
+  # checkout last fetched them (as the pre-flight reads them: no fetch here), and a verdict with
+  # no finding item reads no roster.
+  local cj out rc
+  cj=$(mktemp) || { echo "no temporary file for the carry check"; return 1; }
+  python3 -I -c 'import json, sys; json.dump([{"id": "push-verdict", "body": open(sys.argv[1], encoding="utf-8").read()}], open(sys.argv[2], "w"))' \
+    "$1" "$cj" || { rm -f "$cj"; echo "the verdict could not be read for the carry check"; return 1; }
+  out=$(python3 -I "$ROOT/tools/audit/carry_audit.py" --git-dir "$(git rev-parse --show-toplevel)" --roster-ref origin/main \
+    check --body /dev/null --comments "$cj" 2>&1); rc=$?
+  rm -f "$cj"
+  case $rc in
+    0) return 0 ;;
+    1) printf '%s finding item(s) with no valid Carry: (carry_audit.py); first: %s' \
+         "$(grep -cE '^(UNROUTED|BAD-DEST) ' <<< "$out")" "$(grep -m 1 -E '^(UNROUTED|BAD-DEST) ' <<< "$out")" ;;
+    *) printf 'the carry check could not read the roster: %s' "$(tail -n 1 <<< "$out")" ;;
+  esac
+  return 1
+}
+
 push_verdict() { # pr verdict-file evidence-dir -> proposes the verdict on review/<pr>
   local pr=${1:-} v=${2:-} ev=${3:-} first hsha t gd tree why
   numeric "$pr" || die "push-verdict: the pull request '$pr' is not a number"
@@ -229,6 +280,12 @@ push_verdict() { # pr verdict-file evidence-dir -> proposes the verdict on revie
   # proposal confirm would refuse must be refused here, while the reviewer is
   # still working, not after its seat has gone idle.
   why=$(dispatch_binding "$v" "$pr" "$hsha") || die "push-verdict: $why"
+  # Refused here, while the reviewer is still in its seat, and before review/<pr> moves: a
+  # line the post would refuse (P76: #2735, #2741, each a full re-review), and a finding item
+  # with no valid `Carry:` (P40, P207: #2670, #2876, #2881 parked in the train).
+  why=$(python3 -I "$ROOT/tools/audit/seat/ref_privacy.py" body-lines "$v") \
+    || die "push-verdict: its post would refuse $v at $why; write the path as ~/... or drop it"
+  why=$(carry_gate "$v") || die "push-verdict: $why"
   t=$(mktemp -d) || die "push-verdict: no temporary directory"
   mkdir -p "$t/w/evidence" && cp "$v" "$t/w/VERDICT.md" && cp -R "$ev"/. "$t/w/evidence/" \
     || { rm -rf "$t"; die "push-verdict: could not stage the verdict and its evidence"; }
@@ -277,7 +334,9 @@ append_commit() { # family pr tree message -> pushes one commit on <family>/<pr>
   c=$(git commit-tree "$tree" $parent -m "$msg") || { printf 'bus: REFUSE: commit-tree failed\n' >&2; return 1; }
   python3 -I "$ROOT/tools/audit/seat/ref_privacy.py" guard --ref "$fam/$pr" --message "$msg" \
     || { printf 'bus: REFUSE: %s/%s would publish this host (#2310)\n' "$fam" "$pr" >&2; return 1; }
-  git push -q "$REMOTE" "$c:refs/heads/$fam/$pr" || { printf 'bus: REFUSE: the push of %s/%s was refused\n' "$fam" "$pr" >&2; return 1; }
+  # A large evidence/ (73 files, ~30 MB: #2563) overran git's default 1 MB http.postBuffer and
+  # the chunked POST failed HTTP 400; the buffer holds a pack that size in one request.
+  git -c http.postBuffer=524288000 push -q "$REMOTE" "$c:refs/heads/$fam/$pr" || { printf 'bus: REFUSE: the push of %s/%s was refused\n' "$fam" "$pr" >&2; return 1; }
   printf '%s/%s %s\n' "$fam" "$pr" "$c"
 }
 
@@ -457,8 +516,21 @@ dispatch() { # pr head reviewer [--reviewed-head <sha>] [--nonce N] [--model M]
   git cat-file -e "$h^{commit}" 2>/dev/null || git fetch -q "$REMOTE" "$h" 2>/dev/null
   git cat-file -e "$h^{commit}" 2>/dev/null \
     || die "dispatch: the head $h is not readable in this checkout; fetch it, then dispatch"
-  git cat-file -e "$h:$row" 2>/dev/null \
-    || die "dispatch: #$pr's head $h carries no $row; the row lands before the review (delivery-status-tracking.md) -- write it and re-push, then dispatch"
+  # A head whose every commit over main is dependabot[bot]'s (P100) takes no row commit: one moves
+  # it off the bot's head and reddens pr-contract against dependabot_contract.mjs (#2773, #2678).
+  # Its row is the orchestrator's on main, so it is read at origin/main; any other head reads its own.
+  if bot_only "$h"; then
+    git cat-file -e "$REMOTE/main:$row" 2>/dev/null \
+      || die "dispatch: #$pr's head $h is dependabot[bot]'s alone and $REMOTE/main carries no $row; land the row on main (a commit on the bot's head reddens pr-contract), then dispatch"
+  else
+    git cat-file -e "$h:$row" 2>/dev/null \
+      || die "dispatch: #$pr's head $h carries no $row; the row lands before the review (delivery-status-tracking.md) -- write it and re-push, then dispatch"
+  fi
+  # THE CARRY LANDING (CARRY 0, P310): a body item routed `Carry: <GROUP>` whose group's brief
+  # and carries hold neither its id nor this pull request is refused here, before a reviewer
+  # blocks on it (14 of 21 carry-missing blocks after #2838), with the roster ops that land it.
+  # A --nonce re-record of a relay-minted nonce is no new dispatch: its mint was judged.
+  [ -n "$n" ] || carry_landed "$pr" || die "dispatch: #$pr's body routes a carry its group does not hold (CARRY-MISSING above); land the roster ops above, then dispatch"
   # THE REVIEWABLE HEAD (K15 (d); the #2577 carry, built by R10-FLOW-MAIN-GATE).
   # A head where a required context's latest run concluded failure is not
   # reviewable. merge_train.py's `classify`, the one owner of that state, answers
@@ -602,6 +674,19 @@ watch() {
     esac
     shift
   done
+  # One watcher per state directory (P102): two re-baseline over each other and one misses a
+  # tip (#2780 r4, 0.6 h). The lock is a directory holding the holder's pid; a dead pid's is
+  # taken over; the exit trap releases it.
+  local lk=$S/watch.lock holder
+  mkdir -p "$S" || die "watch: no state directory $S"
+  if ! mkdir "$lk" 2>/dev/null; then
+    holder=$(cat "$lk/pid" 2>/dev/null)
+    if [ -n "$holder" ] && kill -0 "$holder" 2>/dev/null; then  # mut:watchlock
+      die "watch: another watcher (pid $holder) holds $lk; stop it or let it run"
+    fi
+  fi
+  echo "$$" > "$lk/pid"
+  trap 'rm -rf "$S/watch.lock"' EXIT
   while :; do
     watch_once "$post"; rc=$?
     [ $rc = 3 ] || return $rc
@@ -910,6 +995,26 @@ bus-nonce: $N1b" ] && [ "$(grep -c " $N1b " "$W/state/dispatched")" = 2 ] \
   out=$(run dispatch 7 "$h1" cmsg_Z2); rc=$?
   [ $rc = 0 ] && echo "$out" | grep -q '^bus-nonce: '
   expect "dispatch accepts the same pull request once its row is on the head (null control)" $?
+  # P100: a dependabot-only head reads its row on origin/main; any other head reads its own.
+  mb0=$(git -C "$W/seat" ls-remote origin refs/heads/main | cut -f1); git -C "$W/seat" fetch -q origin main
+  bot() { GIT_AUTHOR_NAME=${3:-dependabot[bot]} git -C "$W/seat" \
+            commit-tree "$(git -C "$W/seat" rev-parse "$1^{tree}")" -p "$1" -m "$2"; }
+  hb=$(bot "$mb0" "bump x")
+  out=$(run dispatch 41 "$hb" cmsg_B0); rc=$?
+  [ $rc != 0 ] && echo "$out" | grep -q "dependabot\[bot\]'s alone and origin/main carries no $ROW_DIR/41.md"
+  expect "null control: a dependabot-only head with its row nowhere is refused (P100)" $?
+  rb41=$(printf -- '- [#41](https://github.com/o/r/pull/41) — **open**\n' | git -C "$W/seat" hash-object -w --stdin)
+  rt41=$(git -C "$W/seat" ls-tree "$mb0" | grep -v "	dev$"; printf '040000 tree %s\tdev\n' "$(printf '040000 tree %s\tprogramme\n' "$(printf '040000 tree %s\tdelivery\n' "$(printf '100644 blob %s\t41.md\n' "$rb41" | git -C "$W/seat" mktree)" | git -C "$W/seat" mktree)" | git -C "$W/seat" mktree)")
+  m41=$(printf '%s\n' "$rt41" | git -C "$W/seat" mktree); m41=$(git -C "$W/seat" -c user.name=t -c user.email=t@t commit-tree "$m41" -p "$mb0" -m "row 41")
+  git -C "$W/seat" push -q origin "$m41:refs/heads/main"; hb=$(bot "$m41" "bump y")
+  out=$(run dispatch 41 "$hb" cmsg_B1); rc=$?
+  [ $rc = 0 ] && echo "$out" | grep -q '^bus-nonce: '
+  expect "a dependabot-only head with its row on origin/main is dispatched (P100)" $?
+  hb=$(bot "$(bot "$mb0" "a hand fix" t)" "bump z")  # cut before the row landed on main
+  out=$(run dispatch 41 "$hb" cmsg_B2); rc=$?
+  [ $rc != 0 ] && echo "$out" | grep -q "carries no $ROW_DIR/41.md"
+  expect "a head with one non-bot commit and its row only on origin/main is refused (P100)" $?
+  git -C "$W/seat" push -q -f origin "$mb0:refs/heads/main"; git -C "$W/seat" fetch -q origin main
   # THE REVIEW CARRY (R10-REVIEW-CARRY; tvofi, 2026-10-27). A fresh nonce over a
   # head whose range against the named reviewed head is clean starts a second
   # reviewer for a proof that did not move. `hm` is a merge-only move (main
@@ -1386,6 +1491,39 @@ B
   [ $rc = 0 ] && [ "$(tip review/7)" != "$r7" ]
   expect "and proposes the same verdict with a clean first line (the null control)" $?
 
+  # P76, P40/P207: a verdict refused before review/7 moves -- a line its post would refuse, a
+  # finding item with no valid Carry: -- each beside the same verdict that proposes (null control).
+  r7=$(tip review/7)
+  rmk() { git -C "$W/seat" mktree; }
+  rb=$(printf '{"groups": [{"group": "R10-LIVE", "resume": {"stage": "not-started"}}]}\n' | git -C "$W/seat" hash-object -w --stdin)
+  rt=$(printf '100644 blob %s\twave-r10-groups.json\n' "$rb" | rmk); rt=$(printf '040000 tree %s\trosters\n' "$rt" | rmk)
+  rt=$(printf '040000 tree %s\tprogramme\n' "$rt" | rmk); rt=$(printf '040000 tree %s\tdev\n' "$rt" | rmk)
+  m0=$(git -C "$W/seat" ls-remote origin refs/heads/main | cut -f1)
+  git -C "$W/seat" push -q origin "$(git -C "$W/seat" -c user.name=t -c user.email=t@t commit-tree "$rt" -p "$m0" -m roster):refs/heads/main"
+  git -C "$W/seat" fetch -q origin main
+  NG=$(run dispatch 7 "$h1" cmsg_G | sed -n 's/^bus-nonce: //p')
+  vg() { printf 'Fix review: merge %s\n\nbus-nonce: %s\n\n## Findings\n\n- %s\n' "$h1" "$NG" "$1" > "$W/vg.md"; seat push-verdict 7 "$W/vg.md" "$W/ev1" 2>&1; }
+  out=$(vg "A defect in x is left in place, not blocking."); rc=$?
+  [ $rc != 0 ] && [ "$(tip review/7)" = "$r7" ] && echo "$out" | grep -q "1 finding item(s) with no valid Carry: (carry_audit.py); first: UNROUTED review push-verdict item [0-9a-f]\{8\} (## Findings)"
+  expect "push-verdict refuses an unrouted finding item, naming it, and review/7 does not move (P40, P207)" $?
+  out=$(vg "A defect in x is left in place, not blocking. Carry: R10-GONE"); rc=$?
+  [ $rc != 0 ] && [ "$(tip review/7)" = "$r7" ] && echo "$out" | grep -q "first: BAD-DEST .*R10-GONE"
+  expect "push-verdict refuses a finding routed to no live group (BAD-DEST)" $?
+  out=$(vg "A defect in x is left in place, not blocking. Carry: R10-LIVE"); rc=$?
+  [ $rc = 0 ] && [ "$(tip review/7)" != "$r7" ]
+  expect "and proposes the same verdict once its finding names a live group (the null control)" $?
+  r7=$(tip review/7)
+  out=$(vg "A defect, its log at $W/hpo/x.log. Carry: R10-LIVE"); rc=$?  # $W is the HOME run() sets
+  [ $rc != 0 ] && [ "$(tip review/7)" = "$r7" ] && echo "$out" | grep -q "its post would refuse .* at line 7: home-directory"
+  expect "push-verdict refuses a home path at line 7, naming the line, and review/7 does not move (P76)" $?
+  out=$(vg "A defect, its log at ~/hpo/x.log. Carry: R10-LIVE"); rc=$?
+  [ $rc = 0 ] && [ "$(tip review/7)" != "$r7" ]
+  expect "and proposes it with the path written ~/... (the null control)" $?
+  GIT_TRACE2_EVENT=$W/tr2 GIT_TRACE2_CONFIG_PARAMS=http.postBuffer seat push-verdict 7 "$W/merge-clean.md" "$W/ev1" >/dev/null 2>&1
+  grep -q '"param":"http.postbuffer","value":"524288000"' "$W/tr2"
+  expect "the verdict push runs with a 500 MB http.postBuffer (#2563's HTTP 400)" $?
+  git -C "$W/seat" push -q -f origin "$m0:refs/heads/main"
+
   # THE THREE-ROUND RULE (fixer.md, "Past three rounds"): verdict/<pr>'s history keeps every
   # round, so the blocked commits on it are the rounds a dispatch would follow.
   blk() { git -C "$W/seat" commit-tree "$(git -C "$W/seat" rev-parse "$h1^{tree}")" ${2:+-p "$2"} \
@@ -1394,8 +1532,9 @@ B
   printf '## Summary\nround four, repaired\n' > "$W/body31"
   f1=$(blk 1); f2=$(blk 2 "$f1"); git -C "$W/seat" push -q origin "$f2:refs/heads/verdict/31"
   out=$(run dispatch 31 "$h1" cmsg_T); rc=$?
-  [ $rc = 0 ] && echo "$out" | grep -q '^bus-nonce: ' && [ ! -s "$W/gh-argv" ]
-  expect "null control: two blocked rounds dispatch, reading no pull-request body" $?
+  # the carry landing reads the body on every dispatch (`.body // ""`); the re-cut rule's own read is `.body`
+  [ $rc = 0 ] && echo "$out" | grep -q '^bus-nonce: ' && ! grep -qx "api|repos/o/r/pulls/31|--jq|.body|" "$W/gh-argv"
+  expect "null control: two blocked rounds dispatch, the re-cut rule reading no pull-request body" $?
   f1=$(blk 3 "$f2"); git -C "$W/seat" push -q origin "$f1:refs/heads/verdict/31"; n=$(grep -c . "$W/state/dispatched")
   out=$(run dispatch 31 "$h1" cmsg_T); rc=$?
   [ $rc != 0 ] && echo "$out" | grep -q "3 blocked round(s).*## Re-cut" && [ "$(grep -c . "$W/state/dispatched")" = "$n" ] \
@@ -1483,6 +1622,40 @@ B
   out=$(cd "$W/seat" && run push-design-verdict R10-G9 "$W/dverd.md"); rc=$?
   [ $rc != 0 ] && echo "$out" | grep -q "no design/R10-G9"; expect "a verdict for a topic with no design ref is refused" $?
 
+  # CARRY 0 / P310: dispatch refuses a body carry its group does not hold, printing the roster op;
+  # the same body passes once the group's carries name this pull request (null control).
+  m0=$(git -C "$W/seat" ls-remote origin refs/heads/main | cut -f1)
+  lroster() { # <carry json list>: origin/main's roster with R10-LIVE holding those carries
+    local rb rt
+    rb=$(printf '{"groups": [{"group": "R10-LIVE", "resume": {"stage": "not-started"}, "brief": "b", "carry": %s}]}\n' "$1" \
+      | git -C "$W/seat" hash-object -w --stdin)
+    rt=$(printf '100644 blob %s\twave-r10-groups.json\n' "$rb" | git -C "$W/seat" mktree); rt=$(printf '040000 tree %s\trosters\n' "$rt" | git -C "$W/seat" mktree)
+    rt=$(printf '040000 tree %s\tprogramme\n' "$rt" | git -C "$W/seat" mktree); rt=$(printf '040000 tree %s\tdev\n' "$rt" | git -C "$W/seat" mktree)
+    git -C "$W/seat" push -q -f origin "$(git -C "$W/seat" -c user.name=t -c user.email=t@t commit-tree "$rt" -p "$m0" -m roster):refs/heads/main"
+    git -C "$W/seat" fetch -q origin main; }
+  lroster '[]'; printf '## Forward-carry\n\n- The census misses the store seam. Carry: R10-LIVE\n' > "$W/body31"
+  nd=$(grep -c . "$W/state/dispatched")
+  out=$(run dispatch 7 "$h1" cmsg_L1); rc=$?
+  [ $rc != 0 ] && echo "$out" | grep -q "^CARRY-MISSING R10-LIVE body item [0-9a-f]\{8\}: not in its brief or carries" \
+    && echo "$out" | grep -q "^  roster op: python3 tools/audit/seat/roster_edit.py append-carry R10-LIVE 'From #7, body item " \
+    && [ "$(grep -c . "$W/state/dispatched")" = "$nd" ]
+  expect "dispatch refuses a body carry its group does not hold, printing the roster op, recording nothing (CARRY 0)" $?
+  lroster '["From #7: the store seam."]'
+  out=$(run dispatch 7 "$h1" cmsg_L2); rc=$?
+  [ $rc = 0 ] && echo "$out" | grep -q '^bus-nonce: '
+  expect "and dispatches once the group's carries name the pull request (P310, the null control)" $?
+  printf '## Summary\nround four, repaired\n' > "$W/body31"
+  git -C "$W/seat" push -q -f origin "$m0:refs/heads/main"; git -C "$W/seat" fetch -q origin main
+  # P102: a second watcher over the same state directory refuses, naming the holder; a dead
+  # holder's lock is taken over; the lock is gone once a watcher exits.
+  sleep 30 & wl=$!; mkdir -p "$W/state/watch.lock"; echo "$wl" > "$W/state/watch.lock/pid"
+  out=$(run watch --once 2>&1); rc=$?
+  [ $rc != 0 ] && echo "$out" | grep -q "another watcher (pid $wl) holds"
+  expect "watch --once under a live watcher's lock refuses and names its pid (P102)" $?
+  kill "$wl"; wait "$wl" 2>/dev/null
+  out=$(run watch --once 2>&1); rc=$?
+  [ $rc = 0 ] && [ ! -e "$W/state/watch.lock" ]
+  expect "null control: a dead watcher's lock is taken over, the pass runs, and its exit releases the lock" $?
   [ -n "${BUS_KEEP:-}" ] && echo "kept $W" || rm -rf "$W"
   printf 'bus self-test: %s checks, %s failed\n' "$((pass + fail))" "$fail"
   [ "$fail" = 0 ]
diff --git a/tools/audit/seat/cloud_dispatch.py b/tools/audit/seat/cloud_dispatch.py
index 5346afba2..2e28e22d2 100644
--- a/tools/audit/seat/cloud_dispatch.py
+++ b/tools/audit/seat/cloud_dispatch.py
@@ -217,12 +217,13 @@ def _prompt(role: str, repo: str, pr: str, head: str, topic: str, nonce: str, br
             f"mutant, a deferral, a follow-up, a task owed after the merge) is its own bullet under "
             f"`## Findings` ending in its own `Carry: <GROUP> | #<issue> | O<n> | dismissed: <reason>` "
             f"(finding-propagation.md). Everything else (RESULT lines, re-runs, CI state, figures you "
-            f"could not re-derive) goes under `## Evidence`: tools/audit/carry_audit.py reads no item there "
-            f"as a finding unless it hands something on (deferred, for a later, follow-up, minor, advisory, "
-            f"residual, still has to, not blocking ...; a check that does not block is evidence only in "
-            f"the clause saying it is not a required check and does not block, never in the rest of its "
-            f"sentence: a nit or defect beside it is a finding), and the merge train parks a verdict holding a "
-            f"finding with no `Carry:`. Put the evidence files in `ev/` beside it, and make at least one file under `ev/` contain the full 40-hex head "
+            f"could not re-derive) goes under `## Evidence`: tools/audit/carry_audit.py reads an item there, "
+            f"and under any heading of a merge verdict but `## Findings`, `## Friction`, a block heading and a "
+            f"note heading (Residuals, Follow-ups, Notes ...), by its shape alone: a finding only when it opens "
+            f"with a lead word (Residual:, Follow-up:, Out of scope: ...) or carries a `Carry:`, so a defect "
+            f"you hand on goes under `## Findings`, and bus.sh refuses a verdict holding a finding with no "
+            f"valid `Carry:`. Put the evidence files in `ev/` beside it, under 25 MB in all (cite a large log "
+            f"by path and keep its tail: a ~30 MB ev/ once failed its push), and make at least one file under `ev/` contain the full 40-hex head "
             f"`{head}` (e.g. `ev/HEAD.txt` holding the head you reviewed, beside your command output): "
             f"bus.sh refuses a verdict whose `ev/` names no head. Do NOT run "
             f"bus.sh: its dispatch record lives on the orchestrator's machine, which publishes the verdict "
@@ -999,10 +1000,11 @@ def self_test() -> int:
           "file under `ev/` contain the full 40-hex head `" + head + "`" in msg and "ev/HEAD.txt" in msg)
     check("the reviewer is told to separate findings, each with its own Carry:, from evidence",
           "`## Findings` ending in its own `Carry: " in msg and "goes under `## Evidence`" in msg
-          and "`## Block`" in msg and "not a required check" in msg)
-    check("the reviewer is told the not-required carve-out is the check's clause, never its sentence",
-          "the clause saying it is not a required check and does not block, never in the rest of its sentence"
-          in msg)
+          and "`## Block`" in msg)
+    check("the reviewer is told carry_audit reads Evidence and a merge verdict's other sections by shape (P308, P314)",
+          "by its shape alone: a finding only when it opens with a lead word" in msg
+          and "a defect you hand on goes under `## Findings`" in msg)
+    check("the reviewer is told to keep ev/ under 25 MB in all (#2563's HTTP 400)", "under 25 MB in all" in msg)
     check("the reviewer is given the unbracketed first-line grammar",
           "blocked " + head + " <class>: <reason>" in msg and "[class: reason]" not in msg)
     check("the prompt builds no repository (throwaway_git.py --check refuses a raw init)",
diff --git a/tools/audit/seat/cloud_relay.sh b/tools/audit/seat/cloud_relay.sh
index 12dd735b8..0974eb172 100644
--- a/tools/audit/seat/cloud_relay.sh
+++ b/tools/audit/seat/cloud_relay.sh
@@ -87,7 +87,9 @@
 #     `fix/` and a trailing `-pr`. If handoff-body/<topic> and handoff/<topic>
 #     exist and handoff/<topic> is NOT an ancestor of the PR head, it runs
 #     update_pr.sh <branch> <code-sha> <body> <issues> (issues = the body's
-#     closing keywords), then approve_held_runs.sh on the branch, then
+#     closing keywords) from its own tools tree levelled to origin/main, never
+#     from this checkout (tools_level below; dirty or busy is refused by name and
+#     retried next pass), then approve_held_runs.sh on the branch, then
 #     `bus.sh dispatch <pr> <new head> cloud`, and opens `reviewer-fire <pr>
 #     <head40> nonce=<nonce>` in the ledger (a failed approve or dispatch opens
 #     `approve-held-runs` or `dispatch` instead): firing the cloud reviewer stays
@@ -118,15 +120,17 @@
 #     FREEZE. A PR whose live head is under review is not updated either: a
 #     merge verdict at that head on verdict/<pr> (HELD-VERDICT), or a review of
 #     that head in flight with no verdict at it yet (HELD-REVIEW: bus.sh's
-#     dispatch record, or a detached review worktree at the head). A blocked
-#     verdict, or one naming an older head, freezes nothing. Each prints
-#       cloud_relay: HELD-<why> #<pr> <handoff tip> (...)
+#     dispatch record of the PR at that head, the worker registry, and only it;
+#     its nonce prefix and time are the evidence). A blocked verdict, or one
+#     naming an older head, freezes nothing. Each prints
+#       cloud_relay: HELD-<why> #<pr> <handoff tip>[ dispatch=<nonce8> at=<utc>] (...)
 #     once per pass and is `OWED <utc> handoff-held <ref> <tip> #<pr> <why>` in
 #     <log>.level; `<state>/cloud-handoff-release` (the hold grammar, the
 #     orchestrator's) releases a listed PR from the freeze, never from the
 #     hold. review_freeze below says why each case is what it is.
 #   probe arm: the --watch pass above (probe/rev-* -> relay -> confirm; other
 #     probe refs OWED until disposed).
+#   stuck and no-return arms: level lines only (THE STUCK ANDON, THE NO-RETURN LINE below).
 #   confirm arm (--confirm): the ledger is written before confirm runs, so a
 #     confirm that failed, a relay by a script without the confirm, or one by a
 #     call without --confirm was never confirmed later ('already relayed';
@@ -140,7 +144,10 @@
 #     record shows it posted or `dispose` takes it. A tip with no dispatch for its
 #     PR, head and nonce is owed `undispatched` and never confirmed. A tip the
 #     relay did not push waits for the orchestrator's own read (bus.sh). Settled
-#     tips are noted in `<ledger>.confirm-done`, so a pass fetches only new ones.
+#     tips are noted in `<ledger>.confirm-done`, so a pass fetches only new ones. A tip whose PR
+#     is not open (this pass's open-PR listing; a verdict posts only on an open PR) prints
+#     `cloud_relay: confirm skip #<pr>: not open` once and is settled, owed nothing (P332); a failed
+#     listing skips nothing.
 #     It makes no gh call; bus.sh confirm posts.
 # `--loop` repeats a pass every --interval seconds (default 120); without it a
 # pass runs once. HPO_RELAY_PRS, HPO_RELAY_UPDATE, HPO_RELAY_APPROVE and
@@ -306,11 +313,23 @@ confirm_arm() { # one pass over review/* tips the relay delivered: confirm each
   led=$state/cloud-relayed; bus=${HPO_BUS_STATE:-$HOME/.zcode/bus}; lv=$(relay_log).level
   git ls-remote origin 'refs/heads/review/*' > "$state/cloud-reviews.$$" || { echo "cloud_relay: ls-remote of review/* failed; will retry" >&2; rm -f "$state/cloud-reviews.$$"; return 0; }
   : > "$state/cloud-level-confirm.$$"
+  # P332: a verdict posts only on an open PR (app_comment.sh), so one on a closed or merged PR is
+  # skipped, not owed. The open PRs are this pass's handoff-arm listing, else one listing here; a
+  # failed listing skips nothing (every tip stays owed as before).
+  local open=""
+  if [ -f "$state/cloud-prs-open.$$" ]; then open=$(cut -f1 "$state/cloud-prs-open.$$"); open=${open:-none}
+  else open=$( { if [ -n "${HPO_RELAY_PRS:-}" ]; then "$HPO_RELAY_PRS"
+    else gh pr list -R "${HPO_RELAY_REPO:-tvofi/heatpump_optimizer}" --state open --limit 100 --json number,headRefName,headRefOid \
+      -q '.[] | [.number, .headRefName, .headRefOid] | @tsv'; fi; } | cut -f1) && open=${open:-none} || open=""; fi
+  rm -f "$state/cloud-prs-open.$$"
   while read -r sha ref; do
     pr=${ref#refs/heads/review/}; case $pr in ''|*[!0-9]*) continue;; esac
     # only what this relay delivered: a reviewer of the orchestrator's own waits for its thread read
     grep -q "^refs/heads/probe/rev-$pr-" "$led" 2>/dev/null || continue
     grep -qxF "$pr $sha" "$led.confirm-done" 2>/dev/null && continue
+    if [ -n "$open" ] && ! grep -qxF "$pr" <<< "$open"; then  # mut:closedskip
+      echo "cloud_relay: confirm skip #$pr: not open"; echo "$pr $sha" >> "$led.confirm-done"; continue
+    fi
     git cat-file -e "$sha^{commit}" 2>/dev/null || git fetch -q origin "+$ref:refs/hpo-relay/review/$pr" 2>/dev/null
     if ! git cat-file -e "$sha^{commit}" 2>/dev/null; then  # unknown is not "nothing owed": keep its line
       [ -f "$lv" ] && awk -v r="$ref" -v s="$sha" '$3 == "confirm-owed" && $4 == r && $5 == s' "$lv" >> "$state/cloud-level-confirm.$$"; continue
@@ -382,11 +401,36 @@ review_freeze() { # <pr> <head> <verdict refs file>: prints VERDICT, REVIEW or U
     v=$(git log -1 --format=%s "$vs" | sed -nE "s/^verdict: #$1 Fix review: (merge|blocked) ([0-9a-f]{40})( .*)?\$/\1 \2/p")
     case $v in "merge $2") echo VERDICT; return 0;; "blocked $2") return 1;; esac
   fi
-  if awk -v p="$1" -v h="$2" '$1 == p && $2 == h { f = 1 } END { exit !f }' "$bus/dispatched" 2>/dev/null \
-     || git worktree list --porcelain | awk -v h="$2" '$1 == "HEAD" { at = ($2 == h) } $1 == "detached" && at { f = 1 } END { exit !f }'; then
-    echo REVIEW; return 0
+  # Only the worker registry holds a review (P288): a detached worktree at the head is the
+  # opener's or updater's own as often as a reviewer's (#2953 held 44 passes on one).
+  v=$(awk -v p="$1" -v h="$2" '$1 == p && $2 == h { n = $4; at = $5 } END { if (n != "") print substr(n, 1, 8), (at == "" ? "-" : at) }' \
+    "$bus/dispatched" 2>/dev/null)
+  [ -n "$v" ] || return 1
+  echo "REVIEW dispatch=${v% *} at=${v#* }"
+}
+# THE TOOLS TREE (P283). update_pr.sh refuses a checkout behind origin/main under the tools
+# (pr_args.sh's pr_tools_fresh), and the relay's own checkout is stale whenever main moves them;
+# the relay never moves that checkout, because bash reads a running script from its file as it
+# goes. So it runs update_pr.sh from a worktree it owns, <state>/relay-tools, added once detached
+# and checked out at origin/main before each update when clean. One that is dirty, or held by
+# another relay (the mkdir lock <state>/relay-tools.lock naming a live pid; a dead pid's is taken
+# over), is refused by name and left untouched; the update waits for the next pass.
+tools_level() { # <state>: prints the levelled tree's seat directory, or why not: rc 75 busy, 2 refused
+  local tw=$1/relay-tools o
+  if ! mkdir "$tw.lock" 2>/dev/null; then
+    o=$(cat "$tw.lock/pid" 2>/dev/null)
+    if [ -n "$o" ] && kill -0 "$o" 2>/dev/null; then echo "the relay's tools tree $tw is busy (pid $o)"; return 75; fi  # mut:toolsbusy
+  fi
+  echo "$$" > "$tw.lock/pid"
+  git fetch -q origin main 2>/dev/null || { rm -rf "$tw.lock"; echo "origin/main could not be fetched for the relay's tools tree"; return 2; }
+  [ -e "$tw/.git" ] || git worktree add -q --detach "$tw" origin/main 2>/dev/null \
+    || { rm -rf "$tw.lock"; echo "the relay's tools tree $tw could not be added"; return 2; }
+  if [ -n "$(git -C "$tw" status --porcelain --untracked-files=no 2>/dev/null)" ]; then  # mut:toolsdirty
+    rm -rf "$tw.lock"; echo "the relay's tools tree $tw is dirty; it is left as it is"; return 2
   fi
-  return 1
+  git -C "$tw" checkout -q --detach origin/main 2>/dev/null \
+    || { rm -rf "$tw.lock"; echo "the relay's tools tree $tw could not check out origin/main"; return 2; }  # mut:toolslevel
+  echo "$tw/tools/audit/seat"
 }
 handoff_arm() { # one pass over open PRs; updates one whose handoff is ahead of its head
   local state=${HPO_STATE_DIR:-$HOME/.local/state/hpo} repo=${HPO_RELAY_REPO:-tvofi/heatpump_optimizer} f pr br head topic hs bs bd body iss nh nonce urc held_prs released upd why code
@@ -399,6 +443,7 @@ handoff_arm() { # one pass over open PRs; updates one whose handoff is ahead of
     else gh pr list -R "$repo" --state open --limit 100 --json number,headRefName,headRefOid \
       -q '.[] | [.number, .headRefName, .headRefOid] | @tsv'; fi; } > "$state/cloud-prs.$$" \
     || { echo "cloud_relay: could not list open PRs; will retry" >&2; rm -f "$state/cloud-prs.$$"; return 0; }
+  [ -z "${CONFIRM:-}" ] || cp -f "$state/cloud-prs.$$" "$state/cloud-prs-open.$$"  # this pass's open PRs, for confirm_arm (P332)
   git ls-remote origin 'refs/heads/handoff/*' 'refs/heads/handoff-body/*' > "$state/cloud-hrefs.$$" \
     || { echo "cloud_relay: could not list handoff refs; will retry" >&2; rm -f "$state/cloud-prs.$$" "$state/cloud-hrefs.$$"; return 0; }
   # one listing of the verdicts per pass, outside the loop: an unread listing would update a merge-verdicted head
@@ -416,7 +461,7 @@ handoff_arm() { # one pass over open PRs; updates one whose handoff is ahead of
     git merge-base --is-ancestor "$hs" "$head" && continue
     if grep -qxF "$pr" <<< "$held_prs"; then echo "cloud_relay: HELD #$pr $hs"; continue; fi
     if ! grep -qxF "$pr" <<< "$released" && why=$(review_freeze "$pr" "$head" "$state/cloud-vrefs.$$"); then
-      echo "cloud_relay: HELD-$why #$pr $hs (head $head under review; merge it, or list #$pr in $(release_file) and re-dispatch)"
+      echo "cloud_relay: HELD-${why%% *} #$pr $hs${why#"${why%% *}"} (head $head under review; merge it, or list #$pr in $(release_file) and re-dispatch)"
       level_line handoff-held "refs/heads/handoff/$topic" "$hs" "#$pr $why" >> "$state/cloud-level-held.$$"; continue
     fi
     if [ -f "$f" ] && grep -qxF "$topic $hs" "$f"; then
@@ -445,11 +490,22 @@ handoff_arm() { # one pass over open PRs; updates one whose handoff is ahead of
     # It runs in a process group of its own (pr_own_group), so a signal to the loop's whole group
     # (`timeout`, a daemonizer ending the pgid, a closed terminal's HUP) reaches it only through
     # that reap, and a KILL to the group leaves it to finish under its own lock (#2549).
-    # One launch for both routes, so the self-test's stub runs the production launch line.
-    urc=0; upd=(bash "$HERE/update_pr.sh"); [ -z "${HPO_RELAY_UPDATE:-}" ] || upd=("$HPO_RELAY_UPDATE")
+    # One launch for both routes, so the self-test's stub runs the production launch line. The
+    # script is the levelled tools tree's (tools_level), never this checkout's; a stub skips the tree.
+    urc=0; upd=("${HPO_RELAY_UPDATE:-}")
+    if [ -z "${HPO_RELAY_UPDATE:-}" ]; then
+      why=$(tools_level "$state"); urc=$?
+      if [ "$urc" != 0 ]; then
+        echo "cloud_relay: REFUSED the update of #$pr: $why; the next pass retries" >&2
+        [ "$urc" = 75 ] || level_line handoff-update "refs/heads/handoff/$topic" "$hs" "$why" >> "$state/cloud-level-update.$$"
+        rm -rf "$bd"; continue
+      fi
+      upd=(bash "$why/update_pr.sh")  # mut:toolsseat
+    fi
     # Its output is kept until it ends, so a failure records its reason: the last REFUSE line, else the last line.
     pr_own_group "${upd[@]}" "$br" "$hs" "$body" $iss > "$bd/update.out" 2>&1 &
     PR_REAP_LEAD=$!; wait "$PR_REAP_LEAD" || urc=$?
+    [ -n "${HPO_RELAY_UPDATE:-}" ] || rm -rf "$state/relay-tools.lock"
     cat "$bd/update.out" >&2
     # 75 is update_pr.sh's BUSY: another run (the orchestrator's) holds this branch's worktree. Not
     # a failure, so it is not recorded and the next pass retries once that run has ended.
@@ -525,13 +581,57 @@ stuck_arm() { # one pass over the branch locks: each held past HPO_PUSH_STUCK_SE
   rm -f "$state/cloud-stuck.$$"; level_set push-stuck "$state/cloud-level-stuck.$$"
 }
 
+# THE NO-RETURN LINE (triage P-E, narrowed to git). A cloud fixer dispatched on
+# dispatch/fixer-<topic> returns on handoff-wip/, handoff/ or handoff-body/<topic>, or moves its
+# pull request's fix/<topic>-pr or fix/<topic> head. One whose dispatch tip is older than
+# HPO_RELAY_NORETURN_SECS (default 7200) with none of those moved since is
+#   OWED <utc> seat-no-return refs/heads/dispatch/fixer-<topic> <sha> SEAT ENDED NO RETURN <topic> <age>h
+# on the level (the #2620 seat sat 6 h silent). The record is the dispatch ref itself: no
+# cloud-sessions file is written anywhere in the tree, so the session id is not named; the
+# dispatch tip and its age are. Past HPO_RELAY_NORETURN_WINDOW_SECS (default 172800) a dispatch
+# falls off: its refs may be gone with a merged branch. Deleting the dispatch ref disposes it.
+# A listing or fetch that fails leaves the level as it was. Reviewer and designer seats are out
+# of scope: a reviewer's missing verdict is reviewer-fire's, in the ledger.
+noreturn_arm() {
+  local state=${HPO_STATE_DIR:-$HOME/.local/state/hpo} lim=${HPO_RELAY_NORETURN_SECS:-7200} win=${HPO_RELAY_NORETURN_WINDOW_SECS:-172800}
+  local now sha ref topic t age r rs moved
+  case $lim$win in *[!0-9]*) echo "cloud_relay: HPO_RELAY_NORETURN_SECS/WINDOW must be seconds; the level stays" >&2; return 0;; esac
+  mkdir -p "$state" || return 0
+  # Only the dispatch refs are listed by glob; each candidate's return refs are asked by name, so no
+  # glob here lists a handoff-wip step ref (cloud_dispatch.py pins that no handoff arm sees one).
+  git ls-remote origin 'refs/heads/dispatch/fixer-*' > "$state/cloud-nr.$$" \
+    && git fetch -q origin '+refs/heads/dispatch/fixer-*:refs/hpo-relay/dispatch/fixer-*' 2>/dev/null \
+    || { echo "cloud_relay: the dispatch refs could not be read; the no-return level stays" >&2; rm -f "$state/cloud-nr.$$"; return 0; }
+  now=$(date +%s); : > "$state/cloud-level-nr.$$"
+  while read -r sha ref; do
+    case $ref in refs/heads/dispatch/fixer-?*) topic=${ref#refs/heads/dispatch/fixer-} ;; *) continue ;; esac
+    t=$(git log -1 --format=%ct "$sha" 2>/dev/null) || continue
+    age=$((now - t))
+    [ "$age" -gt "$lim" ] && [ "$age" -le "$win" ] || continue  # mut:noreturnage
+    moved=
+    git ls-remote origin "refs/heads/handoff/$topic" "refs/heads/handoff-wip/$topic" "refs/heads/handoff-body/$topic" \
+      "refs/heads/fix/$topic-pr" "refs/heads/fix/$topic" > "$state/cloud-nrr.$$" || { moved=unread; }
+    for r in handoff/$topic handoff-wip/$topic handoff-body/$topic fix/$topic-pr fix/$topic; do
+      rs=$(awk -v r="refs/heads/$r" '$2 == r { print $1; exit }' "$state/cloud-nrr.$$")
+      [ -n "$rs" ] || continue
+      git cat-file -e "$rs^{commit}" 2>/dev/null || git fetch -q origin "refs/heads/$r" 2>/dev/null
+      [ "$(git log -1 --format=%ct "$rs" 2>/dev/null || echo 0)" -gt "$t" ] && { moved=1; break; }  # mut:noreturnmoved
+    done
+    [ -n "$moved" ] && continue
+    echo "cloud_relay: SEAT ENDED NO RETURN $topic (dispatch ${sha:0:12}, $((age / 3600))h, no return ref or PR head moved since)"
+    level_line seat-no-return "$ref" "$sha" "SEAT ENDED NO RETURN $topic $((age / 3600))h" >> "$state/cloud-level-nr.$$"
+  done < "$state/cloud-nr.$$"
+  level_set seat-no-return "$state/cloud-level-nr.$$"
+  rm -f "$state/cloud-nr.$$" "$state/cloud-nrr.$$"
+}
+
 pass() { # [--confirm] [--log FILE] [--loop [--interval N]]
   local every=120 loop=""
   while [ $# -gt 0 ]; do case $1 in
     --confirm) CONFIRM=1; shift;; --log) LOG=${2:-}; shift 2;; --loop) loop=1; shift;; --interval) every=${2:-}; shift 2;;
     *) echo "cloud_relay: unknown pass option '$1'" >&2; return 2;; esac; done
   case $every in ''|*[!0-9]*|0) echo "cloud_relay: --interval must be a positive number of seconds" >&2; return 2;; esac
-  while :; do handoff_arm; probe_arm; [ -z "${CONFIRM:-}" ] || confirm_arm; stuck_arm; [ -z "$loop" ] && return 0; sleep "$every"; done
+  while :; do handoff_arm; probe_arm; [ -z "${CONFIRM:-}" ] || confirm_arm; stuck_arm; noreturn_arm; [ -z "$loop" ] && return 0; sleep "$every"; done
 }
 
 self_test() {
@@ -888,10 +988,12 @@ EOF
   chk "the same ref listed at its own sha, a verdict at an older head, freezes nothing (null control)" 1 review_freeze 41 "$PRH" "$t/vl"
   git -C "$t/o.git" update-ref -d refs/heads/verdict/41
   # a review in flight: a dispatch of #41 at its head, until a verdict at that head posts
-  printf '41 %s cloud %s\n' "$PRH" "$n" >> "$t/bus/dispatched"; frz
+  printf '41 %s cloud %s 2026-10-29T17:07:00Z -\n' "$PRH" "$n" >> "$t/bus/dispatched"; frz
   chk "a dispatch at the head with no verdict holds the handoff: no update_pr call" 0 test ! -e "$t/hupdated"
-  chk "and prints HELD-REVIEW" 0 grep -q "^cloud_relay: HELD-REVIEW #41 $HS2 " <<< "$ho"
-  chk "and owes handoff-held REVIEW in the level" 0 grep -q "^OWED .* handoff-held refs/heads/handoff/topic-a $HS2 #41 REVIEW\$" "$LOG.level"
+  chk "and prints HELD-REVIEW naming the dispatch's nonce prefix and time (P288)" 0 \
+    grep -q "^cloud_relay: HELD-REVIEW #41 $HS2 dispatch=${n:0:8} at=2026-10-29T17:07:00Z (" <<< "$ho"
+  chk "and owes handoff-held REVIEW with that evidence in the level" 0 \
+    grep -q "^OWED .* handoff-held refs/heads/handoff/topic-a $HS2 #41 REVIEW dispatch=${n:0:8} at=2026-10-29T17:07:00Z\$" "$LOG.level"
   mkv "verdict: #41 Fix review: merge $h"; frz
   chk "a verdict at an older head does not dispose the review: still HELD-REVIEW" 0 grep -q "HELD-REVIEW #41 " <<< "$ho"
   mkv "verdict: #41 Fix review: blocked $PRH carry-missing: x"; frz
@@ -905,12 +1007,15 @@ EOF
   printf '42 %s cloud %s\n' "$PRH" "$n" >> "$t/bus/dispatched"; frz
   chk "a dispatch of another PR at the same head holds nothing (null control)" 0 test -e "$t/hupdated"
   cp "$t/bus/dispatched.keep" "$t/bus/dispatched"
-  # the review worktree heuristic: a detached worktree of this checkout at the head
+  # P288: a detached worktree at the head is no review (the opener's and updater's sit there);
+  # only the dispatch record holds. The #2953 shape: handoff ahead, no verdict, no dispatch record.
   git worktree add -q --detach "$t/rw" "$PRH" 2>/dev/null; frz
-  chk "a detached review worktree at the head holds the handoff" 0 test ! -e "$t/hupdated"
-  chk "and prints HELD-REVIEW" 0 grep -q "HELD-REVIEW #41 " <<< "$ho"
-  git -C "$t/rw" checkout -q --detach "$HS2"; frz
-  chk "a detached worktree at another commit holds nothing (null control)" 0 test -e "$t/hupdated"
+  chk "a detached worktree at the head with no dispatch record updates (the #2953 shape)" 0 test -e "$t/hupdated"
+  chk "and prints no HELD-REVIEW" 1 grep -q "HELD-REVIEW #41 " <<< "$ho"
+  printf '41 %s cloud %s\n' "$PRH" "$n" >> "$t/bus/dispatched"; frz
+  chk "the same with a dispatch record at the head holds (a record without a time says at=-)" 0 \
+    grep -q "HELD-REVIEW #41 $HS2 dispatch=${n:0:8} at=- (" <<< "$ho"
+  cp "$t/bus/dispatched.keep" "$t/bus/dispatched"
   git worktree remove --force "$t/rw"
   # the release: the orchestrator passes the freeze over a listed PR; the hold file outranks it
   mkv "verdict: #41 Fix review: merge $PRH"; printf '41\n' > "$rf"; frz
@@ -925,6 +1030,41 @@ EOF
   chk "and updates nothing" 0 test ! -e "$t/hupdated"
   chk "and owes handoff-hold-malformed naming the release file" 0 grep -q "^OWED .* handoff-hold-malformed $rf -\$" "$LOG.level"
   rm -f "$rf"; git -C "$t/o.git" update-ref -d refs/heads/verdict/41; rm -f "$t/hupdated" "$t/bus/dispatched.keep"; HPO_RELAY_UPDATE=$ustub; : > "$LOG"
+  # P283: the update runs from the relay's own tools tree, levelled to origin/main, never from
+  # this checkout. The scratch main carries a stand-in update_pr.sh holding pr_tools_fresh's test.
+  rm -rf "$t/tm"; throwaway_git_init "$t/tm" -q; mkdir -p "$t/tm/tools/audit/seat"
+  printf '#!/bin/bash\nd=$(cd "$(dirname "$0")" && pwd)\nn=$(git -C "$d" rev-list --count HEAD..origin/main -- :/tools)\n[ "$n" = 0 ] || { echo "REFUSE STALE CHECKOUT behind by $n"; exit 1; }\necho "$(git -C "$d" rev-parse HEAD) $1 $2" >> "%s/tupdated"\n' "$t" > "$t/tm/tools/audit/seat/update_pr.sh"
+  tmc() { git -C "$t/tm" add -A && git -C "$t/tm" -c user.name=t -c user.email=t@t commit -qm "$1"; }
+  tmc tools-a; TA=$(git -C "$t/tm" rev-parse HEAD); echo b > "$t/tm/tools/audit/seat/x"; tmc tools-b; TB=$(git -C "$t/tm" rev-parse HEAD)
+  git -C "$t/o.git" fetch -qf "$t/tm" "HEAD:refs/heads/main"; git fetch -q origin main
+  TW=$t/state/relay-tools; git worktree add -q --detach "$TW" "$TA"
+  # The relay's own checkout, stale: a copy of the seat whose update_pr.sh refuses as the guard would.
+  rm -rf "$t/seat"; cp -R "$HERE" "$t/seat"; printf '#!/bin/bash\necho "REFUSE STALE CHECKOUT (the relay checkout)"; exit 1\n' > "$t/seat/update_pr.sh"
+  keep_here=$HERE; HERE=$t/seat; rm -f "$t/tupdated"
+  ho=$(HPO_RELAY_UPDATE= handoff_arm 2>&1)
+  chk "a relayed update runs from the levelled tools tree, at origin/main, and passes the guard (P283)" 0 \
+    test "$(cat "$t/tupdated" 2>/dev/null)" = "$TB fix/topic-a-pr $HS2"
+  chk "the tools tree was moved from the commit behind to origin/main" 0 test "$(git -C "$TW" rev-parse HEAD)" = "$TB"
+  chk "and its lock is released after the update" 0 test ! -e "$TW.lock"
+  chk "the relay's own checkout is never moved or run" 1 grep -q "the relay checkout" <<< "$ho"
+  git -C "$TW" checkout -q --detach "$TA"; echo dirty >> "$TW/tools/audit/seat/update_pr.sh"; rm -f "$t/tupdated" "$t/state/cloud-handoff-failed"
+  ho=$(HPO_RELAY_UPDATE= handoff_arm 2>&1)
+  chk "null control: a dirty tools tree is refused by name, no update runs" 0 \
+    grep -q "REFUSED the update of #41: the relay's tools tree $TW is dirty" <<< "$ho"
+  chk "and the tree is left untouched (its commit and its edit)" 0 \
+    test "$(git -C "$TW" rev-parse HEAD) $(tail -n 1 "$TW/tools/audit/seat/update_pr.sh")" = "$TA dirty"
+  chk "and the refusal is owed on the level, unrecorded, so the next pass retries" 0 \
+    test "$(grep -c "handoff-update refs/heads/handoff/topic-a $HS2 the relay's tools tree .* is dirty" "$LOG.level")" = 1 -a ! -e "$t/tupdated"
+  chk "and not noted as a failed update" 0 test -z "$(grep -s "topic-a $HS2" "$t/state/cloud-handoff-failed")"
+  git -C "$TW" checkout -q -- .; sleep 30 & lp=$!; mkdir "$TW.lock"; echo "$lp" > "$TW.lock/pid"
+  ho=$(HPO_RELAY_UPDATE= handoff_arm 2>&1)
+  chk "a tools tree held by a live relay is busy: no update, no level line" 0 \
+    test -n "$(grep "is busy (pid $lp)" <<< "$ho")" -a ! -e "$t/tupdated"
+  kill "$lp"; wait "$lp" 2>/dev/null
+  ho=$(HPO_RELAY_UPDATE= handoff_arm 2>&1)
+  chk "a lock whose pid is dead is taken over and the update runs" 0 test "$(cat "$t/tupdated" 2>/dev/null)" = "$TB fix/topic-a-pr $HS2"
+  HERE=$keep_here; git worktree remove --force "$TW"; rm -rf "$TW.lock" "$t/tupdated" "$t/seat"
+  git -C "$t/o.git" fetch -qf "$t/m" "HEAD:refs/heads/main"; git fetch -q origin main 2>/dev/null; : > "$LOG"; rm -f "$LOG.level" "$t/state/cloud-handoff-failed"
   # a failing update is noted once and not retried
   rm -f "$t/updated"; git -C "$t/pr" reset -q --hard "$PRH"; mkref fix/topic-a-pr
   printf '%s\t%s\t%s\n' 41 fix/topic-a-pr "$PRH" > "$prs"; : > "$LOG"
@@ -1013,7 +1153,10 @@ EOF
   # the confirm arm (P-O): the ledger is written before confirm runs, so a failed confirm was never
   # retried ('already relayed'). pass --confirm confirms each review/<pr> tip the relay pushed and
   # bus.sh has not posted; posting is what the confirm stub records, as bus.sh does in posted-signed.
-  printf '#!/bin/sh\n' > "$t/none.sh"; chmod +x "$t/none.sh"; HPO_RELAY_PRS=$t/none.sh; HPO_RELAY_PUSH=$stub
+  printf '#!/bin/sh\n' > "$t/none.sh"; chmod +x "$t/none.sh"; HPO_RELAY_PUSH=$stub
+  # P332: these PRs are open (their branches carry no handoff, so the handoff arm passes them by)
+  printf '#!/bin/sh\nfor p in 61 62 63 64 66; do printf "%%s\\tfix/cf-%%s\\t%s\\n" $p $p; done\n' "$N40" > "$t/open.sh"
+  chmod +x "$t/open.sh"; HPO_RELAY_PRS=$t/open.sh
   git -C "$t/o.git" for-each-ref --format='%(refname)' refs/heads/review/ | while read -r r; do git -C "$t/o.git" update-ref -d "$r"; done
   cat > "$t/cf.sh" <<'EOF'
 #!/bin/sh
@@ -1055,6 +1198,17 @@ EOF
   chk "then stays owed once on the level with its last reason" 0 test "$(grep -c "^OWED .* confirm-owed refs/heads/review/63 $(rtip 63) tries=3/3, not retried; .*: bus: REFUSE: the push of verdict/63 was refused: HTTP 502$" "$LV")" = 1
   echo "63 $(git rev-parse "$(rtip 63)^{tree}")" >> "$t/bus/posted-signed"; pass --confirm --log "$LOG" >/dev/null 2>&1
   chk "a review posted by hand after that leaves the level" 1 grep -q "review/63 " "$LV"
+  # P332: a relayed review whose PR is not open is skipped once, owed nothing; a failed listing skips nothing.
+  CF_FAILS=99; export HPO_RELAY_CONFIRM=$t/cf.sh; mk 67 $h $h $n; printf '67 %s cloud %s\n' "$h" "$n" >> "$t/bus/dispatched"
+  cfo=$(pass --confirm --log "$LOG" 2>&1); cfo2=$(pass --confirm --log "$LOG" 2>&1)
+  # one call is the relay's own, at the relay; the confirm arm adds none over two passes
+  chk "a relayed review on a closed PR is skipped by the confirm arm with one line, confirmed no further (P332)" 0 \
+    test "$(grep -c '^cloud_relay: confirm skip #67: not open$' <<< "$cfo
+$cfo2") $(calls 67)" = "1 1"
+  chk "and owes no confirm-owed" 1 grep -q "review/67 " "$LV"
+  mk 68 $h $h $n; printf '68 %s cloud %s\n' "$h" "$n" >> "$t/bus/dispatched"
+  HPO_RELAY_PRS=$failprs pass --confirm --log "$LOG" >/dev/null 2>&1
+  chk "null control: with the open-PR listing failed, the same shape on #68 stays owed" 0 grep -q "confirm-owed refs/heads/review/68 " "$LV"
   CONFIRM=; CF_FAILS=0; unset HPO_RELAY_CONFIRM; HPO_RELAY_PRS=$t/lister.sh; LOG=$t/pass.log
   # R10-PUSHER-REAP: a relay TERMed mid-update ends the update's whole tree. The
   # update stub records itself and a two-level sleep tree by pid, then blocks.
@@ -1081,10 +1235,14 @@ EOF
   HPO_RELAY_UPDATE=$t/lead.sh stoprelay "$HERE/cloud_relay.sh" 2
   chk "a relay TERMed mid-update TERMs the update alone first, so it ends its own child before anything else does" \
     0 test "$tn $live $(tr '\n' ' ' < "$t/marks")" = "2 0 G "
-  # The production route, no HPO_RELAY_UPDATE: a copy of the relay and the real pr_args.sh beside
-  # an update_pr.sh that is the lead stub, so the relay's own `bash "$HERE/update_pr.sh"` runs it.
+  # The production route, no HPO_RELAY_UPDATE: the scratch main's update_pr.sh is the lead stub,
+  # so the relay's own launch runs it from its levelled tools tree (tools_level, P283). The relay
+  # is a copy, so no route (a mutant's included) reaches the real update_pr.sh.
+  cp "$t/lead.sh" "$t/tm/tools/audit/seat/update_pr.sh"; tmc lead; git -C "$t/o.git" fetch -qf "$t/tm" "HEAD:refs/heads/main"
   mkdir -p "$t/seat" && cp "$HERE/cloud_relay.sh" "$HERE/pr_args.sh" "$t/seat/" && cp "$t/lead.sh" "$t/seat/update_pr.sh"
   HPO_RELAY_UPDATE= stoprelay "$t/seat/cloud_relay.sh" 2
+  git worktree remove --force "$t/state/relay-tools"; rm -rf "$t/state/relay-tools.lock"
+  git -C "$t/o.git" fetch -qf "$t/m" "HEAD:refs/heads/main"; git fetch -q origin main 2>/dev/null
   chk "with no stub, the relay runs update_pr.sh beside it as the lead, asynchronously: a TERM ends it in that order" \
     0 test "$tn $live $(tr '\n' ' ' < "$t/marks")" = "2 0 G "
   # #2549: a signal to the loop's whole process group reaches the update only through the loop's
@@ -1143,7 +1301,33 @@ open(sys.argv[1], "w").close(); time.sleep(60)' "$t/stuck.held" "$t/state/pr/upd
   chk "a released lock aged 5000 s is not reported, whatever its text" 1 grep -qF 'fix-gone' <<< "$out"
   chk "once every lock is released nothing is reported, and the level holds no push-stuck line" \
     0 test "$(printf '%s' "$stuck_free")$(grep -c push-stuck "$LOG.level")" = 0
-  rm -rf "$t"
+  # P-E: SEAT ENDED NO RETURN, keyed on the dispatch ref's own age (git only).
+  LOG=$t/nr.log; : > "$LOG"; rm -f "$LOG.level"
+  rm -rf "$t/nr" "$t/nrw" "$t/nro.git"; throwaway_git_init "$t/nr" -q; throwaway_git_init "$t/nrw" -q
+  throwaway_git_init "$t/nro.git" -q --bare; cd "$t/nrw" && git remote add origin "$t/nro.git"
+  nrc() { # <ref> <age seconds>: one commit on the scratch origin's <ref>, committed <age> ago
+    GIT_COMMITTER_DATE="@$(( $(date +%s) - $2 )) +0000" git -C "$t/nr" -c user.name=t -c user.email=t@t commit -q --allow-empty -m "$1"
+    git -C "$t/nro.git" fetch -qf "$t/nr" "HEAD:refs/heads/$1"; }
+  nrc dispatch/fixer-nr-a 10800; nrc dispatch/fixer-nr-b 10800; nrc handoff-wip/nr-b 3600
+  nrc dispatch/fixer-nr-c 10800; nrc fix/nr-c-pr 1800; nrc dispatch/fixer-nr-young 1800
+  nrc dispatch/fixer-nr-old 300000; nrc handoff/nr-e 14400; nrc dispatch/fixer-nr-e 10800
+  nro=$(noreturn_arm 2>&1)
+  chk "a fixer dispatched 3 h ago with no return ref is SEAT ENDED NO RETURN (P-E)" 0 \
+    grep -q "^cloud_relay: SEAT ENDED NO RETURN nr-a (dispatch [0-9a-f]\{12\}, 3h" <<< "$nro"
+  chk "and owed seat-no-return on the level" 0 \
+    grep -qE "^OWED [^ ]+ seat-no-return refs/heads/dispatch/fixer-nr-a [0-9a-f]{40} SEAT ENDED NO RETURN nr-a 3h$" "$LOG.level"
+  chk "a seat whose handoff-wip moved after its dispatch is not reported (null control: it returned)" 1 grep -q " nr-b " <<< "$nro"
+  chk "a seat whose pull request's head moved after its dispatch is not reported" 1 grep -q " nr-c " <<< "$nro"
+  chk "a dispatch younger than the bound is not reported" 1 grep -q " nr-young " <<< "$nro"
+  chk "a dispatch past the window is not reported (its refs may be gone with a merged branch)" 1 grep -q " nr-old " <<< "$nro"
+  chk "a return ref older than the dispatch (an earlier round's) does not count as a return" 0 grep -q " nr-e " <<< "$nro"
+  git -C "$t/nro.git" update-ref -d refs/heads/dispatch/fixer-nr-a; git -C "$t/nro.git" update-ref -d refs/heads/dispatch/fixer-nr-e
+  noreturn_arm >/dev/null 2>&1
+  chk "deleting the dispatch ref takes its line off the level (the disposal)" 1 grep -q "fixer-nr-a\|fixer-nr-e" "$LOG.level"
+  LOG=$t/nr2.log; : > "$LOG"; nrc dispatch/fixer-nr-p 10800
+  nro=$(handoff_arm() { :; }; probe_arm() { :; }; CONFIRM= pass 2>&1)
+  chk "a pass runs the no-return arm" 0 grep -q "SEAT ENDED NO RETURN nr-p " <<< "$nro"
+  cd / && rm -rf "$t"
   echo "cloud_relay self-test: $((ok+bad)) checks, $bad failed"; [ "$bad" = 0 ]
 }
 
diff --git a/tools/audit/seat/instruments/bus.sh.md b/tools/audit/seat/instruments/bus.sh.md
index 4bf8d046f..3b7f23e72 100644
--- a/tools/audit/seat/instruments/bus.sh.md
+++ b/tools/audit/seat/instruments/bus.sh.md
@@ -35,3 +35,13 @@ The design steps (decision 0014) write the same append-only way:
 line is `Design review: approve <sha>` or `Design review: revise <sha> <class>`,
 and `<sha>` must be the current tip of `design/<topic>`: a design that moved
 under the review is refused, and so is a topic with no design ref.
+  `push-verdict` refuses, before `review/<pr>` moves, a verdict with a line
+  its post would refuse (`ref_privacy.py body-lines`, naming the line) and
+  one whose finding items name no valid `Carry:` (`carry_audit.py check` at
+  origin/main and the round's roster branch, as the train's pre-flight reads
+  them); its push carries a 500 MB `http.postBuffer` (#2563's HTTP 400).
+  `dispatch` reads a head's own delivery row, except a head whose every
+  commit over origin/main is `dependabot[bot]`'s: its row is read on
+  origin/main (a row commit on the bot's head reddens `pr-contract`).
+  `watch` holds `<state>/watch.lock` (a directory naming its pid): a second
+  watcher refuses naming the holder; a dead pid's lock is taken over.
diff --git a/tools/audit/seat/instruments/cloud_relay.sh.md b/tools/audit/seat/instruments/cloud_relay.sh.md
index e8a39a7a5..260584614 100644
--- a/tools/audit/seat/instruments/cloud_relay.sh.md
+++ b/tools/audit/seat/instruments/cloud_relay.sh.md
@@ -100,15 +100,23 @@
   pass (rc 2, `OWED handoff-hold-malformed` in `<log>.level`), never hold-all or hold-none.
   `cloud_relay.sh held <pr>` answers from the same file (rc 0 held, 1 not, 2
   malformed) for a driver that updates PRs itself.
+  Tools tree (P283): the update runs `update_pr.sh` from `<state>/relay-tools`,
+  a worktree the relay adds once detached and checks out at origin/main before
+  each update when clean, so `pr_tools_fresh` passes however stale the relay's
+  own checkout is (never moved: bash reads a running script as it goes). A
+  dirty tree is refused by name, left untouched and owed as `handoff-update`;
+  one held by a live relay (`relay-tools.lock`, a dead pid's taken over) is
+  busy and retried next pass.
   Freeze (R10-FLOW-ROSTER-FREEZE): a PR whose live head is under review is not
   updated either, so roster edits accumulate on the handoff ref and land between
   reviews: a `Fix review: merge <head>` tip on `verdict/<pr>` at that head
   (`HELD-VERDICT`), or a review of that head in flight with no verdict at it
-  (`HELD-REVIEW`: a `bus.sh dispatch` record of the PR at the head, or a
-  detached worktree at it). A verdict ref the listing names but the fetch
+  (`HELD-REVIEW`: a `bus.sh dispatch` record of the PR at the head, the worker
+  registry and only it, P288; its nonce prefix and time are printed as
+  `dispatch=<nonce8> at=<utc>`). A verdict ref the listing names but the fetch
   cannot read freezes too (`HELD-UNREAD`): it may be a merge at the head. A
   blocked verdict, or one at an older head, freezes nothing. Each prints
-  `HELD-<why> #<pr> <handoff tip>` once per pass and is
+  `HELD-<why> #<pr> <handoff tip>[ dispatch=<nonce8> at=<utc>]` once per pass and is
   `OWED <utc> handoff-held <ref> <tip> #<pr> <why>` in `<log>.level`;
   `cloud-handoff-release` (the hold file's grammar) releases a listed PR from the
   freeze, never from the hold, for new work that voids a merge verdict.
@@ -133,3 +141,13 @@
   each passed push-verdict, `reviewer-fire`, `approve-held-runs`, `dispatch`)
   is opened in the ledger, never appended to the log, which keeps only the
   `POSTED` journal.
+  No-return line (triage P-E): each pass, a `dispatch/fixer-<topic>` tip older
+  than `HPO_RELAY_NORETURN_SECS` (default 7200) and younger than
+  `HPO_RELAY_NORETURN_WINDOW_SECS` (default 172800), with no `handoff-wip/`,
+  `handoff/`, `handoff-body/<topic>`, `fix/<topic>-pr` or `fix/<topic>`
+  commit newer than it, prints `SEAT ENDED NO RETURN <topic>` and is
+  `OWED <utc> seat-no-return <ref> <sha> SEAT ENDED NO RETURN <topic> <age>h`
+  in `<log>.level`. Git only; deleting the dispatch ref disposes it.
+  Confirm arm (P332): a relayed `review/<pr>` whose PR is not in the pass's
+  open-PR listing prints `confirm skip #<pr>: not open` once and is settled,
+  owed nothing; a failed listing skips nothing.
diff --git a/tools/audit/seat/instruments/tick_loop.sh.md b/tools/audit/seat/instruments/tick_loop.sh.md
index 2245bbf97..08bcb04cf 100644
--- a/tools/audit/seat/instruments/tick_loop.sh.md
+++ b/tools/audit/seat/instruments/tick_loop.sh.md
@@ -5,8 +5,8 @@
   hand step) when the tree carries it (#2419; skipped
   and said so before), then `orchestrator_tick.py` with the given args,
   writing the board whole to `--out` (default `$HPO_STATE_DIR/tick.txt`) and
-  one `TICK-PASS <utc> relay=<ok|rc=N|running|absent> tick=<rc>` line to
-  stdout. The relay runs detached under the flock `<out>.relay.lock`, waited
+  one `TICK-PASS <utc> relay=<ok|rc=N|running|absent|stale> tick=<rc>
+  code=<sha7> behind=<n>` line to stdout. The relay runs detached under the flock `<out>.relay.lock`, waited
   for at most `HPO_TICK_RELAY_WAIT` s (default 30): one still in flight is
   left running, never killed, reported `relay=running`, and no second starts
   while it holds the lock, so a long `update_pr.sh` push never holds the
@@ -17,3 +17,13 @@
   is reported and the loop goes on. `--self-test` drives it over stubs.
   Each pass then calls `heartbeat.sh --once` (the andon, below), bounded at
   60 s; `HPO_TICK_HEARTBEAT` replaces it.
+  Before the relay, the freshness check (P14): `git fetch -q origin main`
+  and `behind`, the commits in `HEAD..origin/main` touching `tools/audit/seat`,
+  `tools/pr` or `tools/audit/carry_audit.py`. Past `HPO_TICK_STALE_BOUND`
+  (default 25) or on a commit touching `tick_loop.sh` or `cloud_relay.sh`, it
+  restarts between passes, at most once a pass: lock free, tree clean and
+  detached, `bash -n` passing on origin/main's copy, then a detached checkout
+  of origin/main and an exec with the same args (`TICK-RESTART`). Otherwise
+  a `TICK-STALE` line names why, the relay and sweep arms are skipped
+  (`relay=stale`) and the board is still written. Never a fast-forward in
+  place. `HPO_TICK_CODE_DIR` replaces the checkout.
diff --git a/tools/audit/seat/ledger.py b/tools/audit/seat/ledger.py
index dd631ef9d..13064feb3 100644
--- a/tools/audit/seat/ledger.py
+++ b/tools/audit/seat/ledger.py
@@ -103,6 +103,7 @@ KINDS = {
     "handoff-hold-malformed": "derived", "handoff-held": "derived", "handoff-body-stale": "derived",
     "design-build": "derived", "review-owed": "derived",
     "probe-refused": "derived", "confirm-owed": "derived", "push-stuck": "derived",
+    "seat-no-return": "derived",
     "reviewer-fire": "event", "verdict-unposted": "event", "approve-held-runs": "event",
     "dispatch": "event", "train-stop": "event", "postmerge-owed": "event",
 }
diff --git a/tools/audit/seat/queue_pre_flight.py b/tools/audit/seat/queue_pre_flight.py
index aa04f2a8e..d31a835b3 100644
--- a/tools/audit/seat/queue_pre_flight.py
+++ b/tools/audit/seat/queue_pre_flight.py
@@ -98,7 +98,7 @@ class PreFlight:
                  checkout: Path = ROOT, bot_cured: bool = False,
                  free_holders: bool = False, dests: "ca.Dests | None" = None) -> None:
         self.repo = repo
-        self.dests = dests  # carry_audit's destinations; read from origin/main on first use
+        self.dests = dests  # carry_audit's destinations as given (a fixture's); else read per pull request
         self.checkout = checkout
         # The train's own pre-flight (`merge_train.py --pre-flight`) passes
         # what it now cures itself: a bot tip (batch routes it serial, whose
@@ -170,11 +170,11 @@ class PreFlight:
             return "PARK", s.step, s.why
         if not held:
             return "PARK", "approve", why
-        if why := self.findings_gate(pr):
+        if why := self.findings_gate(pr, h):
             return "PARK", "findings", why
         return "PASS", "", ""
 
-    def findings_gate(self, pr: int) -> str:
+    def findings_gate(self, pr: int, head: str = "") -> str:
         """'' when every finding item of the body and its `Fix review:`
         verdicts is routed to a valid destination (carry_audit.audit), else
         the refusal naming the count and the first item. Fail-closed: a body,
@@ -193,11 +193,13 @@ class PreFlight:
         if not ca.finding_rows(body, comments)[0]:
             return ""  # nothing to route: the roster is not read
         try:
-            if self.dests is None:
-                self.dests = ca.load_dests(self.checkout, "origin/main", issue_state=self.issue_state)
+            # Read per pull request, never one set for the train: a head's own new carry file routes
+            # its `#N` (P43, #2675); an injected set (the self-test's) is used as given.
+            dests = self.dests or ca.load_dests(self.checkout, "origin/main", issue_state=self.issue_state,
+                                                extra_ref=head or None)
         except (ca.roster_lib.RosterNotFound, ValueError) as e:
             return f"the roster could not be read: {str(e)[:160]}"
-        bad = [r for r in ca.audit(body, comments, self.dests)["rows"] if r["status"] != "routed"]
+        bad = [r for r in ca.audit(body, comments, dests)["rows"] if r["status"] != "routed"]
         if not bad:
             return ""
         r = bad[0]
@@ -496,6 +498,17 @@ def _self_test() -> int:
           go({"comments": NOTE})[:2] == ("PARK", "findings") and "review 9" in go({"comments": NOTE})[2])
     check("comments that cannot be read PARK, fail-closed",
           go({"comments_fail": True})[:2] == ("PARK", "findings"))
+    # P43: with no injected set, each pull request's destinations are read with its head as the
+    # extra ref (its own new carry file), never one set cached for the train.
+    seen, real = [], ca.load_dests
+    ca.load_dests = lambda *a, **k: seen.append(k.get("extra_ref")) or ca.Dests(
+        {"groups": [{"group": "R10-LIVE", "issues": [], "fixes": [], "resume": {"stage": "planned"}}]}, set())
+    try:
+        go({"body": FR + " Carry: R10-LIVE"}, dests=None)
+        go({"body": FR + " Carry: R10-LIVE", "pr_head": H1}, dests=None)
+    finally:
+        ca.load_dests = real
+    check("P43: the destinations are read per pull request, with its head as the extra ref", seen == [H0, H1])
     check("a merge base that cannot be read PARKS, named as the failure",
           go({"no_base": True})[:2] == ("PARK", "files"))
     check("a diff that cannot be read PARKS, named as the failure",
diff --git a/tools/audit/seat/ref_privacy.py b/tools/audit/seat/ref_privacy.py
index a3f68e58c..8e9785358 100644
--- a/tools/audit/seat/ref_privacy.py
+++ b/tools/audit/seat/ref_privacy.py
@@ -3,6 +3,7 @@
 
     python3 -I tools/audit/seat/ref_privacy.py slug <path> [--root NAME=DIR]...
     python3 -I tools/audit/seat/ref_privacy.py path <path>      (~/-relative for a posted text)
+    python3 -I tools/audit/seat/ref_privacy.py body-lines <file> (rc 1: the lines a post would refuse)
     python3 -I tools/audit/seat/ref_privacy.py guard --ref <ref> [--message <text>]...
                                                      [--commits <rev> [--over <base>] [-C <dir>]]
     python3 -I tools/audit/seat/ref_privacy.py scrub [--write] <file>...  (this host's spans, in place)
@@ -304,6 +305,18 @@ def body_refusal(text: str, ident: Identity | None = None) -> str | None:
     return f"{', '.join(why)} in the body" if why else None
 
 
+def body_lines(text: str, ident: Identity | None = None) -> list[str]:
+    """`line <n>: <why>` for each line body_refusal refuses, or the whole body's
+    refusal when no one line carries it; [] when the body would post (P76: a
+    verdict refused at post for its line 15 cost a full re-review)."""
+    ident = ident or Identity.of_host()
+    whole = body_refusal(text, ident)
+    if whole is None:
+        return []
+    bad = [f"line {i}: {w}" for i, ln in enumerate(text.split("\n"), 1) if (w := body_refusal(ln, ident))]
+    return bad or [whole]
+
+
 def home_relative(path: str, home: str | None = None) -> str:
     """A local path as a posted text names it: `~/<rest>` under the home
     directory (as written or resolved), else unchanged. A reader resolves `~`
@@ -1074,6 +1087,14 @@ def self_test() -> int:
     ok("scrub rewrites the cloud home only as a whole path",
        scrub(cite + " " + under("root", "x"), rid) == cite + " ~/x", scrub(cite + " " + under("root", "x"), rid))
 
+    # body_lines (P76): a verdict body is judged line by line, as its post would judge it.
+    vbody = "Fix review: merge x\n\nbus-nonce: n\n" + "\n" * 12 + "- see " + fake_home + "/ev/log\n"
+    ok("body_lines names the line of a host path below the first line (P76)",
+       body_lines(vbody, fid) == ["line 16: home-directory, account-name in the body"], repr(body_lines(vbody, fid)))
+    ok("body_lines passes the same body with the path written ~/... (null control)",
+       body_lines(vbody.replace(fake_home, "~"), fid) == [])
+    ok("body_lines still names a host path on the first line",
+       body_lines("Fix review: blocked x h: " + fake_home + "/x\n", fid) == ["line 1: home-directory, account-name in the body"])
     print(f"ref_privacy self-test: {passed + failed} checks, {failed} failed")
     return 1 if failed else 0
 
@@ -1096,6 +1117,10 @@ def main(argv: list[str]) -> int:
                     Path(f).write_text(new, encoding="utf-8", errors="surrogateescape")
         print(f"ref_privacy scrub: {changed} of {len(paths)} file(s) {'rewritten' if write else 'would change'}")
         return 0
+    if argv[:1] == ["body-lines"] and len(argv) == 2:
+        bad = body_lines(Path(argv[1]).read_text(encoding="utf-8", errors="surrogateescape"))
+        print("; ".join(bad)) if bad else None
+        return 1 if bad else 0
     if argv[:1] == ["path"] and len(argv) == 2:
         print(home_relative(argv[1]))
         return 0
diff --git a/tools/audit/seat/tick_loop.sh b/tools/audit/seat/tick_loop.sh
index dfb263c9e..454015779 100644
--- a/tools/audit/seat/tick_loop.sh
+++ b/tools/audit/seat/tick_loop.sh
@@ -16,8 +16,20 @@
 #   2. orchestrator_tick.py with the given args. The board goes to --out (default
 #      $HPO_STATE_DIR/tick.txt, written whole then renamed, so a reader never sees
 #      half a board).
+#   0. Before both, the freshness check (P14, s5-batch1): `git fetch -q origin main` in
+#      the checkout this script runs from, and behind = the commits in HEAD..origin/main
+#      touching tools/audit/seat, tools/pr or tools/audit/carry_audit.py (the code the loop
+#      runs). Past HPO_TICK_STALE_BOUND (default 25), or on any commit touching tick_loop.sh
+#      or cloud_relay.sh, the loop restarts: with the relay lock free and the tree clean and
+#      detached, it checks out origin/main detached, runs `bash -n` on the new tick_loop.sh
+#      and execs it with the same arguments -- between passes, at most once per pass, never
+#      a fast-forward in place (bash reads a running script as it goes). When it cannot, one
+#        TICK-STALE <utc> code=<sha7> behind=<n>: <why>; the relay and sweep arms are skipped
+#      line precedes the banner, the arms that act are skipped (relay=stale) and the board
+#      is still written: never exit, never act from stale code. A failed fetch is
+#      behind=unknown and the pass runs as before. HPO_TICK_CODE_DIR replaces the checkout.
 # One banner line per pass on stdout:
-#   TICK-PASS <utc> relay=<ok|rc=N|running|absent> tick=<rc> out=<file>
+#   TICK-PASS <utc> relay=<ok|rc=N|running|absent|stale> tick=<rc> code=<sha7|none> behind=<n|unknown> out=<file>
 # The relay's output is printed when it is reaped; one that finished after its
 # pass's wait is reaped by the next pass, with its own line before that banner:
 #   TICK-RELAY <utc> relay=<ok|rc=N> started=<utc>
@@ -61,6 +73,47 @@ with open(r + ".log", "w") as log:
 with open(r + ".rc.part", "w") as o: o.write("%d %s\n" % (rc, t))
 os.replace(r + ".rc.part", r + ".rc")'
 
+# The relay lock is free: rc 0 (the holder's flock, tried and released at once).
+LOCK_FREE='import fcntl, sys
+f = open(sys.argv[1], "a")
+try: fcntl.flock(f, fcntl.LOCK_EX | fcntl.LOCK_NB)
+except BlockingIOError: sys.exit(1)'
+CODE_PATHS=(tools/audit/seat tools/pr tools/audit/carry_audit.py)
+SELF_PATHS=(tools/audit/seat/tick_loop.sh tools/audit/seat/cloud_relay.sh)
+
+behind_count() { # <checkout> <paths...>: the commits in HEAD..origin/main touching the paths
+  local d=$1; shift
+  git -C "$d" rev-list --count HEAD..origin/main -- "$@" 2>/dev/null
+}
+
+fresh_check() { # <out>: sets code, behind and stale (the acting arms are skipped); may exec the new loop
+  local top self why bound=${HPO_TICK_STALE_BOUND:-25}
+  case $bound in ''|*[!0-9]*) bound=25 ;; esac
+  code=none behind=unknown stale=
+  top=$(git -C "${HPO_TICK_CODE_DIR:-$HERE}" rev-parse --show-toplevel 2>/dev/null) || return 0
+  code=$(git -C "$top" rev-parse --short=7 HEAD 2>/dev/null) || code=none
+  git -C "$top" fetch -q origin main 2>/dev/null || return 0
+  behind=$(behind_count "$top" "${CODE_PATHS[@]}") || { behind=unknown; return 0; }  # mut:paths
+  [ "$behind" -gt 0 ] || return 0
+  self=$(behind_count "$top" "${SELF_PATHS[@]}") || self=1
+  [ "$behind" -gt "$bound" ] || [ "$self" -gt 0 ] || return 0  # mut:bound
+  stale=1
+  if [ -n "${HPO_TICK_RESTARTED:-}" ]; then why="restarted once this pass"
+  elif ! python3 -I -c "$LOCK_FREE" "$1.relay.lock"; then why="a relay is in flight (the lock is held)"  # mut:lock
+  elif git -C "$top" symbolic-ref -q HEAD >/dev/null; then why="a branch is checked out, not a detached head"
+  elif [ -n "$(git -C "$top" status --porcelain --untracked-files=no)" ]; then why="the tree is dirty"  # mut:dirty
+  elif ! git -C "$top" show origin/main:tools/audit/seat/tick_loop.sh | bash -n 2>/dev/null; then  # mut:syntax
+    why="bash -n refuses origin/main's tick_loop.sh"
+  elif ! git -C "$top" checkout -q --detach origin/main; then why="the checkout failed"
+  else
+    printf 'TICK-RESTART %s code=%s behind=%s -> %s\n' "$(date -u +%FT%TZ)" "$code" "$behind" \
+      "$(git -C "$top" rev-parse --short=7 HEAD)"
+    HPO_TICK_RESTARTED=1 exec bash "$top/tools/audit/seat/tick_loop.sh" "${ARGV[@]}"  # mut:exec
+  fi
+  printf 'TICK-STALE %s code=%s behind=%s: %s; the relay and sweep arms are skipped\n' \
+    "$(date -u +%FT%TZ)" "$code" "$behind" "$why"
+}
+
 relay_reap() { # <r> [late]: print a finished relay's output; sets rrc. 1: nothing to reap
   local r=$1 st
   [ -f "$r.rc" ] || return 1
@@ -96,10 +149,13 @@ sweep_pass() { # <out>: one merge-train sweep when one is due; prints its TICK-S
 }
 
 tick_pass() { # <out> [tick args...]: one pass; prints the banner
-  local out=$1 relay rrc trc tmp now; shift
+  local out=$1 relay rrc trc tmp now code behind stale; shift
   relay=${HPO_TICK_RELAY:-$HERE/cloud_relay.sh}
   mkdir -p "$(dirname -- "$out")"
-  if [ -f "$relay" ]; then
+  fresh_check "$out"
+  if [ -n "$stale" ]; then
+    rrc=stale  # mut:skip
+  elif [ -f "$relay" ]; then
     relay_start "$out.relay" "$relay"
     # 76: an earlier pass's relay finished after its wait; reap it, then start this pass's.
     [ "$rrc" = rc=holder-76 ] && { relay_reap "$out.relay" late; relay_start "$out.relay" "$relay"; }  # mut:reap
@@ -111,10 +167,10 @@ tick_pass() { # <out> [tick args...]: one pass; prints the banner
   else python3 "$HERE/orchestrator_tick.py" "$@" > "$tmp" 2>&1; trc=$?; fi
   mv -f "$tmp" "$out"
   now=$(date -u +%FT%TZ)
-  printf 'TICK-PASS %s relay=%s tick=%s out=%s\n' "$now" "$rrc" "$trc" "$out"
-  [ -z "$sweep" ] || sweep_pass "$out"  # mut:sweep
+  printf 'TICK-PASS %s relay=%s tick=%s code=%s behind=%s out=%s\n' "$now" "$rrc" "$trc" "$code" "$behind" "$out"
+  [ -z "$sweep" ] || [ -n "$stale" ] || sweep_pass "$out"  # mut:sweep
   # The andon: one heartbeat push per pass, bounded, its failure printed and never fatal.
-  timeout 60 bash "${HPO_TICK_HEARTBEAT:-$HERE/heartbeat.sh}" --once --message "TICK-PASS $now relay=$rrc tick=$trc"  # mut:heartbeat
+  timeout 60 bash "${HPO_TICK_HEARTBEAT:-$HERE/heartbeat.sh}" --once --message "TICK-PASS $now relay=$rrc tick=$trc code=$code behind=$behind"  # mut:heartbeat
   [ $? = 0 ] || echo "HEARTBEAT NOT PUSHED: heartbeat.sh did not finish cleanly"
 }
 
@@ -127,10 +183,13 @@ tick_loop_self_test() (
   chmod +x "$t/tick.sh"
   printf '#!/bin/bash\necho "hb $*" >> "%s/hb"; exit "${HB_RC:-0}"\n' "$t" > "$t/hb.sh"
   export HPO_TICK_HEARTBEAT=$t/hb.sh
+  # The rows before the freshness rows run from no checkout: never the real one, whose
+  # fetch and checkout a restart would move.
+  mkdir "$t/nogit"; export HPO_TICK_CODE_DIR=$t/nogit GIT_CEILING_DIRECTORIES=$t
   out=$(HPO_TICK_RELAY=$t/relay.sh HPO_TICK_CMD="bash $t/tick.sh" bash "$0" --once --out "$t/b.txt" -- --only PRS)
   [ "$(cat "$t/order")" = "relay pass --confirm
 tick --only PRS" ] && [ "$(cat "$t/b.txt")" = BOARD ] \
-    && printf '%s\n' "$out" | grep -Eq '^TICK-PASS [0-9T:-]+Z relay=ok tick=0 out=' && [ "$(printf '%s\n' "$out" | wc -l | tr -d ' ')" = 1 ]
+    && printf '%s\n' "$out" | grep -Eq '^TICK-PASS [0-9T:-]+Z relay=ok tick=0 code=none behind=unknown out=' && [ "$(printf '%s\n' "$out" | wc -l | tr -d ' ')" = 1 ]
   ck "--once: one pass, cloud_relay.sh pass --confirm first, then the tick with its args; one banner" $?
   rm -f "$t/order"
   out=$(HPO_TICK_RELAY=$t/absent.sh HPO_TICK_CMD="bash $t/tick.sh" bash "$0" --once --out "$t/b.txt")
@@ -166,7 +225,7 @@ done" ]
   rm -f "$t/hb"
   out=$(HPO_TICK_RELAY=$t/absent.sh HPO_TICK_CMD="bash $t/tick.sh" bash "$0" --once --out "$t/b.txt")
   [ "$(wc -l < "$t/hb" | tr -d ' ')" = 1 ] \
-    && grep -Eq '^hb --once --message TICK-PASS [0-9T:-]+Z relay=absent tick=0$' "$t/hb"
+    && grep -Eq '^hb --once --message TICK-PASS [0-9T:-]+Z relay=absent tick=0 code=none behind=unknown$' "$t/hb"
   ck "each pass calls the heartbeat once, with the pass line (no --out path)" $?
   out=$(HB_RC=1 HPO_TICK_RELAY=$t/absent.sh HPO_TICK_CMD="bash $t/tick.sh" bash "$0" --once --out "$t/b.txt"); rc=$?
   [ $rc = 0 ] && printf '%s\n' "$out" | grep -q '^HEARTBEAT NOT PUSHED' && printf '%s\n' "$out" | grep -q 'tick=0'
@@ -201,18 +260,74 @@ sweep" ] && printf '%s\n' "$out" | grep -q '^TICK-SWEEP '
   git -C "$t/w" remote add origin "$t/remote.git"; mkdir -p "$t/w/seat"
   cp "$HERE/heartbeat.sh" "$HERE/ref_privacy.py" "$t/w/seat/"
   out=$(HPO_TICK_HEARTBEAT=$t/w/seat/heartbeat.sh HPO_TICK_RELAY=$t/absent.sh HPO_TICK_CMD="bash $t/tick.sh" bash "$0" --once --out "$t/b.txt")
-  git -C "$t/remote.git" log -1 --format=%s heartbeat/orchestrator | grep -Eq '^TICK-PASS [0-9T:-]+Z relay=absent tick=0$' \
+  git -C "$t/remote.git" log -1 --format=%s heartbeat/orchestrator | grep -Eq '^TICK-PASS [0-9T:-]+Z relay=absent tick=0 code=none behind=unknown$' \
     && ! printf '%s\n' "$out" | grep -q 'NOT PUSHED'
   ck "a real pass moves heartbeat/orchestrator on the remote" $?
   git -C "$t/w" remote set-url origin "$t/nowhere.git"
   out=$(HPO_TICK_HEARTBEAT=$t/w/seat/heartbeat.sh HPO_TICK_RELAY=$t/absent.sh HPO_TICK_CMD="bash $t/tick.sh" bash "$0" --once --out "$t/b.txt")
   printf '%s\n' "$out" | grep -q '^HEARTBEAT NOT PUSHED: ' && printf '%s\n' "$out" | grep -q 'tick=0'
   ck "null control: a refused push is printed with its reason and the pass still completes" $?
+  # The freshness check (P14): a clone of a scratch origin, detached, holding this script.
+  unset HPO_TICK_HEARTBEAT; export HPO_TICK_HEARTBEAT=$t/hb.sh
+  throwaway_git_init "$t/o.git" -q --bare -b main && throwaway_git_init "$t/s" -q -b main
+  mkdir -p "$t/s/tools/audit/seat" "$t/s/tools/pr"
+  cp "$0" "$t/s/tools/audit/seat/tick_loop.sh"; echo 1 > "$t/s/tools/pr/x"; echo r > "$t/s/README"
+  # the scratch origin fetches each commit rather than taking a push: a push site here would need a
+  # PUSHERS entry (ref_privacy.py) keyed on the file, which would pass an unguarded loop push too
+  git -C "$t/s" add -A && git -C "$t/s" commit -qm base && git -C "$t/o.git" fetch -q "$t/s" main:main
+  throwaway_git_clone -q "$t/o.git" "$t/c" && git -C "$t/c" checkout -q --detach
+  land() { # <path> <content>: one commit on the scratch origin's main
+    printf '%s\n' "$2" > "$t/s/$1"; git -C "$t/s" commit -qam "$1" && git -C "$t/o.git" fetch -q "$t/s" main:main; }
+  fr() { rm -f "$t/order"; HPO_TICK_CODE_DIR=$t/c HPO_TICK_RELAY=$t/relay.sh HPO_TICK_CMD="bash $t/tick.sh" \
+    bash "$0" --once --out "$t/f.txt" "$@" 2>&1; }
+  at0=$(git -C "$t/c" rev-parse --short=7 HEAD)
+  out=$(fr); rm -f "$t/hb"
+  printf '%s\n' "$out" | grep -q "relay=ok tick=0 code=$at0 behind=0 out=" && [ "$(printf '%s\n' "$out" | wc -l | tr -d ' ')" = 1 ] \
+    && [ "$(git -C "$t/c" rev-parse --short=7 HEAD)" = "$at0" ]
+  ck "freshness null control: behind 0 is silent (code=<sha7> behind=0 on the banner) and does not exec" $?
+  land README r2; out=$(fr)
+  printf '%s\n' "$out" | grep -q "code=$at0 behind=0 " && ! printf '%s\n' "$out" | grep -q 'TICK-STALE\|TICK-RESTART'
+  ck "freshness: a commit outside the loop's code paths is not counted (the path filter)" $?
+  land tools/pr/x 2; out=$(fr); fr >/dev/null; cat "$t/hb" > "$t/hb1" 2>/dev/null
+  printf '%s\n' "$out" | grep -q "relay=ok tick=0 code=$at0 behind=1 " && ! printf '%s\n' "$out" | grep -q 'TICK-RESTART\|TICK-STALE' \
+    && grep -q "^relay pass --confirm" "$t/order" && [ "$(git -C "$t/c" rev-parse --short=7 HEAD)" = "$at0" ] \
+    && grep -q "code=$at0 behind=1$" "$t/hb1"
+  ck "freshness: behind within the bound and no change to the loop's own files relays, restarts nothing; the heartbeat says behind=1" $?
+  printf '#!/bin/bash\necho "NEW-LOOP $*"\n' > "$t/new.sh"
+  land tools/audit/seat/tick_loop.sh "$(cat "$t/new.sh")"
+  python3 -I -c 'import fcntl, sys, time
+f = open(sys.argv[1], "a"); fcntl.flock(f, fcntl.LOCK_EX); open(sys.argv[1] + ".up", "w").close(); time.sleep(30)' "$t/f.txt.relay.lock" & lp=$!
+  k=0; while [ ! -f "$t/f.txt.relay.lock.up" ] && [ $k -lt 100 ]; do sleep 0.1; k=$((k + 1)); done
+  out=$(fr)
+  kill "$lp" 2>/dev/null; wait "$lp" 2>/dev/null
+  printf '%s\n' "$out" | grep -q '^TICK-STALE .* behind=2: a relay is in flight' && printf '%s\n' "$out" | grep -q 'relay=stale tick=0' \
+    && [ "$(cat "$t/order")" = "tick " ] && [ "$(git -C "$t/c" rev-parse --short=7 HEAD)" = "$at0" ] && [ "$(cat "$t/f.txt")" = BOARD ]
+  ck "freshness: a held relay lock does not restart, skips the relay and still writes the board under TICK-STALE" $?
+  echo dirty >> "$t/c/tools/pr/x"; out=$(fr); git -C "$t/c" checkout -q -- tools/pr/x
+  printf '%s\n' "$out" | grep -q '^TICK-STALE .*: the tree is dirty' && printf '%s\n' "$out" | grep -q 'relay=stale' \
+    && [ "$(cat "$t/order")" = "tick " ] && [ "$(git -C "$t/c" rev-parse --short=7 HEAD)" = "$at0" ]
+  ck "freshness: a dirty tree prints the banner, skips the relay and is never moved" $?
+  git -C "$t/c" checkout -q -b local; out=$(fr); git -C "$t/c" checkout -q --detach; git -C "$t/c" branch -qD local
+  printf '%s\n' "$out" | grep -q '^TICK-STALE .*: a branch is checked out' && [ "$(git -C "$t/c" rev-parse --short=7 HEAD)" = "$at0" ]
+  ck "freshness: a checked-out branch is never moved (restart needs a detached head)" $?
+  out=$(HPO_TICK_RESTARTED=1 fr)
+  printf '%s\n' "$out" | grep -q '^TICK-STALE .*: restarted once this pass' && [ "$(git -C "$t/c" rev-parse --short=7 HEAD)" = "$at0" ]
+  ck "freshness: a pass already restarted does not exec again (at most once per pass)" $?
+  land tools/audit/seat/tick_loop.sh 'if then ('; out=$(fr)
+  printf '%s\n' "$out" | grep -q "^TICK-STALE .*: bash -n refuses" && printf '%s\n' "$out" | grep -q 'relay=stale tick=0' \
+    && [ "$(git -C "$t/c" rev-parse --short=7 HEAD)" = "$at0" ]
+  ck "freshness: origin/main's tick_loop.sh failing bash -n is never checked out or exec'd" $?
+  land tools/audit/seat/tick_loop.sh "$(cat "$t/new.sh")"; out=$(fr --sweep)
+  printf '%s\n' "$out" | grep -q "^TICK-RESTART .* code=$at0 behind=4 -> " \
+    && printf '%s\n' "$out" | grep -qx "NEW-LOOP --once --out $t/f.txt --sweep" \
+    && [ "$(git -C "$t/c" rev-parse HEAD)" = "$(git -C "$t/c" rev-parse origin/main)" ] && [ ! -f "$t/order" ]
+  ck "freshness: a loop-file change with a free lock and a clean detached tree checks out origin/main and execs it with the same args" $?
   rm -rf "$t"
   echo "tick_loop self-test: $n checks, $f failed"
   [ "$f" = 0 ]
 )
 
+ARGV=("$@")  # a restart execs the new loop with these
 once=; sweep=; every=300; out=${HPO_STATE_DIR:-$HOME/.local/state/hpo}/tick.txt
 while [ $# -gt 0 ]; do
   case $1 in
@@ -229,6 +344,7 @@ case $every in ''|*[!0-9]*) echo "tick_loop: --interval needs whole seconds, got
 [ -n "$out" ] || { echo "tick_loop: --out needs a file" >&2; exit 2; }
 while :; do
   tick_pass "$out" "$@"
+  unset HPO_TICK_RESTARTED  # once per pass: the next pass may restart again
   [ -n "$once" ] && exit 0
   sleep "$every"
 done
diff --git a/tools/pr/prepr.sh b/tools/pr/prepr.sh
index acca5adc0..b3910f927 100755
--- a/tools/pr/prepr.sh
+++ b/tools/pr/prepr.sh
@@ -2805,6 +2805,18 @@ https://claude.ai/code/session_011aqzm4YL9jLhU4jLvbkLYE'; got=$(lpush)
   grep -q 'were not run (rc 3' <<<"$got" && grep -q '^rc=0$' <<<"$got" \
     && [ "$(git --git-dir="$PDX/bodies.git" rev-parse refs/heads/handoff-body/zz-lint)" != "$was" ]
   st $? 0 "and pushes, saying so, when the handoff refusals cannot be run (rc 3 is never a refusal)"
+  # CARRY 11: body_push runs carry_audit.py landed after the packet; rc 1 pushes nothing, rc 3 pushes.
+  printf '#!/bin/bash\necho "CARRY-MISSING R10-X body item 0123abcd: not in its brief or carries"; exit %s\n' 1 > "$PDX/ld1"
+  printf '#!/bin/bash\necho "carry_audit: UNREAD the roster"; exit %s\n' 3 > "$PDX/ld3"
+  was=$(git --git-dir="$PDX/bodies.git" rev-parse refs/heads/handoff-body/zz-lint)
+  got=$(HPO_HANDOFF_LANDED="bash $PDX/ld1" lpush)
+  grep -q '^CARRY-MISSING R10-X body item 0123abcd' <<<"$got" && grep -q '^rc=1$' <<<"$got" \
+    && [ "$(git --git-dir="$PDX/bodies.git" rev-parse refs/heads/handoff-body/zz-lint)" = "$was" ]
+  st $? 0 "and refuses a body whose carry its group does not hold, naming it and pushing nothing (CARRY 11)"
+  got=$(HPO_HANDOFF_LANDED="bash $PDX/ld3" lpush)
+  grep -q 'carry landing was not checked (rc 3' <<<"$got" && grep -q '^rc=0$' <<<"$got" \
+    && [ "$(git --git-dir="$PDX/bodies.git" rev-parse refs/heads/handoff-body/zz-lint)" != "$was" ]
+  st $? 0 "and pushes, saying so, when the roster cannot be read (rc 3 is never a refusal)"
   (cd "$PDX/r" && git push -q -f origin pinert:refs/heads/handoff/zz-lint); got=$(lpush)
   grep -q 'push the code, then the body' <<<"$got" && grep -q '^rc=1$' <<<"$got"
   st $? 0 "and refuses a body pushed from a checkout that is not the head at handoff/<topic>"

## Before you return the verdict (P275)
Run `python3 -I tools/audit/carry_audit.py check --body <PR body file> --comments <file holding [{"id": 0, "body": <verdict.md text>}]>`. Give every reported item its own `Carry: <GROUP> | #<issue> | O<n> | dismissed: <reason>`;
an evidence line flagged by its wording takes `Carry: dismissed: evidence, not a finding`. Return the verdict only at rc 0.
