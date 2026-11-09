# Review packet #3359
head: 40c79702c72359f00a0a932eabf727a942b1f9eb
base: fdc8d21adaa50a7feee534f08ee5edde9bda81ed

Start here (fix-review.md). Re-read the live check state before a verdict: the digest is as read at render.

## Gate digest: green
CodeQL id=128906818810 success
arch-score / arch-score id=128917487223 success
arm id=128905551687 skipped
budget-raise-gate / budget-raise-gate id=128917487250 success
cancel-superseded id=128914151547 success
codeql id=128917488768 skipped
codeql / Analyze (actions) id=128906670858 success
codeql / Analyze (javascript-typescript) id=128906670819 success
codeql / Analyze (python) id=128906670864 success
gate id=128920774162 success
governance id=128917488260 skipped
governance / delivery-status id=128906670903 success
governance / delivery-status-publish id=128906672023 skipped
governance / env-matrix id=128906670817 success
governance / instrument-self-tests id=128906670824 success
governance / policy-docs id=128906670919 success
governance / record id=128906672084 skipped
governance / wave-script id=128906670812 success
hassfest id=128917488309 skipped
hassfest / hassfest id=128906670845 success
kernel-points id=128917488392 skipped
pr-contract id=128920775376 skipped
pr-contract / pr-contract id=128917889353 success
prelude id=128914151484 success
refresh id=128914151258 success
tests id=128917488881 skipped
tests / arch-instrument id=128907061079 success
tests / briefs id=128906670815 success
tests / browser id=128907061106 success
tests / ci-ratchet id=128917890518 skipped
tests / claims-autofix id=128909622842 skipped
tests / closure-scope id=128906670888 success
tests / closures id=128907061083 success
tests / closures-autofix id=128917890555 skipped
tests / coverage id=128907061099 success
tests / coverage-ratchet id=128910536240 success
tests / fast (3.14) id=128907062502 success
tests / graders-head-copy id=128910536222 success
tests / lane-proofs id=128910536286 success
tests / mutation id=128906670798 success
tests / mutation-autofix id=128907093398 skipped
tests / mutation-pins id=128907093610 skipped
tests / nightly-ha id=128907061884 skipped
tests / nightly-status id=128906670803 success
tests / replay id=128907062463 skipped
tests / typing id=128907061045 success
validate id=128917488442 skipped
validate / validate-hacs id=128906670630 success

## Refusals
none

## Advisories
hot-file: HPO_BUS_TRAIN_STATE is unset, so every merge verdict reads unboarded

## carry_audit at the head
NOTE body item 2763967f: #201
NOTE body item 121a7318: dismissed:closed here, pinned by pr_args.sh's REMERGE FAILED arm and mut:remergeconflict
NOTE body item f254eb47: dismissed:bounded by the train's own cap and the owner's card 1 asks for exactly that bound
CARRY-AUDIT: 3 finding item(s): 3 routed, 0 unrouted, 0 bad destination(s)

## figure_lint at the head
ok         python3 tools/audit/seat/merge_train.py --self-test
             `tools/audit/seat/merge_train.py` is in the tree at this head
  ok         bash tools/audit/seat/pr_args.sh --self-test
             `tools/audit/seat/pr_args.sh` is in the tree at this head
  ok         python3 dev/audit/harnesses/r10_train_rejoin_no_recarry_mutants.py
             `dev/audit/harnesses/r10_train_rejoin_no_recarry_mutants.py` is in the tree at this head
  ok         python3 tests/structure.py
             `tests/structure.py` is in the tree at this head
  ok         python3 tools/audit/archscore/score.py --diff $(git merge-base origin/main HEAD)
             `tools/audit/archscore/score.py` is in the tree at this head
  ok         python3 tests/closure.py select --diff $(git merge-base origin/main HEAD) --workdir "$D"
             `tests/closure.py` is in the tree at this head
  ok         PYTHONPATH=tests/hastub python3 tests/entities.py
             `tests/entities.py` is in the tree at this head
  ok         tests/harness_headers.py
             `tests/harness_headers.py` is in the tree at this head
  ok         tests/closure.py selftest
             `tests/closure.py` is in the tree at this head
  ok         tests/layout.py
             `tests/layout.py` is in the tree at this head
  ok         tests/env_drift.py --claims-only
             `tests/env_drift.py` is in the tree at this head
  ok         python3 tools/pr/ci_predict.py --apply-inert
             `tools/pr/ci_predict.py` is in the tree at this head
  unverified git grep -n "self\.recarry(" -- tools/audit/seat/merge_train.py
             `git grep` resolves; its flags are not checked -- git prints a man page rather than a flag list, and a list carried in this file would rot into false refusals
  unverified git grep -n "self\.skip(" -- tools/audit/seat/merge_train.py
             `git grep` resolves; its flags are not checked -- git prints a man page rather than a flag list, and a list carried in this file would rot into false refusals
  unverified git grep -n "MERGE CONFLICT" -- tools/
             `git grep` resolves; its flags are not checked -- git prints a man page rather than a flag list, and a list carried in this file would rot into false refusals
  ok         bash tools/pr/prepr.sh
             `tools/pr/prepr.sh` is in the tree at this head
  ok         bash tools/pr/prepr.sh <body>
             `tools/pr/prepr.sh` is in the tree at this head
  ok         python3 -I tools/audit/seat/mutant_run.py --diff 17e621f08c4f...HEAD --cmd "python3 tools/audit/seat/merge_train.py --self-test" --max-mutants 40 --report-only
             `tools/audit/seat/mutant_run.py` is in the tree at this head

FIGURES: 15 resolved, 3 not verified, 0 refused

## Finder's harness: none named
### at the base
not run
### at the head
not run

## Mutation-ledger diff
none

## Three-dot diff
diff --git a/dev/audit/harnesses/r10_train_rejoin_no_recarry_mutants.py b/dev/audit/harnesses/r10_train_rejoin_no_recarry_mutants.py
new file mode 100755
index 000000000..97f264389
--- /dev/null
+++ b/dev/audit/harnesses/r10_train_rejoin_no_recarry_mutants.py
@@ -0,0 +1,129 @@
+#!/usr/bin/env python3
+"""R10-TRAIN-REJOIN-NO-RECARRY: one mutant per new arm of merge_train.py (card 1, the
+rejoin; card 5, no recarry) and remerge_main.sh's conflict diagnosis is pinned by
+pr_args.sh's own `mut:remergeconflict` arm, against merge_train.py's own self-test.
+
+    python3 dev/audit/harnesses/r10_train_rejoin_no_recarry_mutants.py            # all, 4 at a time
+    python3 dev/audit/harnesses/r10_train_rejoin_no_recarry_mutants.py --list     # enumerate only
+    python3 dev/audit/harnesses/r10_train_rejoin_no_recarry_mutants.py M0 M2      # named
+
+Run from the branch's worktree. Each mutant replaces exactly one source span of
+tools/audit/seat/merge_train.py (the span must occur exactly once, or the
+mutant is reported STALE, never silently skipped), writes the result beside the
+original as `_mutant_<id>.py` (so ROOT, gh_read and the tool table resolve as
+for the real file), runs its `--self-test`, and prints the FAIL lines. M0 is
+the unmutated file and must pass; every other mutant must fail at least one
+check, else it SURVIVED. The copies are removed whatever happens.
+"""
+
+from __future__ import annotations
+
+import concurrent.futures
+import subprocess
+import sys
+from pathlib import Path
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
+SRC = ROOT / "tools/audit/seat/merge_train.py"
+sys.path.insert(0, str(Path(__file__).resolve().parent))
+import mutant_guard  # noqa: E402 -- restores the mutated file on a kill (SIGTERM/SIGINT) and refuses a leftover mutant
+
+# (id, arm, the span, its replacement)
+MUTANTS = [
+    ("M0", "the unmutated head", "", ""),
+    # Card 1: the rejoin.
+    ("M1", "a rejoin fires on GREEN only, never on RED",
+     "                if state == \"green\":\n                    self.log(f\"REJOIN #{pr}: GREEN",
+     "                if state in (\"green\", \"red\"):\n                    self.log(f\"REJOIN #{pr}: GREEN"),
+    ("M2", "the batch runs the rejoin", "                self.rejoin(rejoin, head_req)\n", "                pass\n"),
+    ("M3", "only a red holding GATE is a rejoin candidate",
+     "        if isinstance(s, HeadRed) and GATE in s.red:", "        if isinstance(s, HeadRed):"),
+    ("M4", "the rejoin waits, bounded by the train's cap (cap 0)",
+     "        cap = self.wait_cap_s()\n        while waiting:", "        cap = 0\n        while waiting:"),
+    ("M5", "the rejoin's bound is the train's cap (cap x100)",
+     "        cap = self.wait_cap_s()\n        while waiting:", "        cap = 100 * self.wait_cap_s()\n        while waiting:"),
+    ("M6", "a head the branch moved off does not rejoin",
+     "                if self.head(pr) != h:\n                    self.log(f\"REJOIN #{pr}: the head moved off",
+     "                if False:\n                    self.log(f\"REJOIN #{pr}: the head moved off"),
+    ("M7", "a serial rejoin candidate is queued too", "                        self.rejoin_candidate(a, s, rejoin)\n", ""),
+    # Card 5: no recarry.
+    ("M8", "a clean merge tree merges with no recarry (a recarry on every main move)",
+     "        if not self.contains_main(h) and not self.merges_as_is(item, h):", "        if not self.contains_main(h):"),
+    ("M9", "a strict or unreadable policy recarries",
+     "        if item.get(\"grade_held\") or self.strict_update() is not False:", "        if item.get(\"grade_held\"):"),
+    ("M10", "a merge-tree conflict recarries", "        if got is None or got[1] or self.bot_tip(h):",
+     "        if got is None or self.bot_tip(h):"),
+    ("M11", "a bot head recarries", "        if got is None or got[1] or self.bot_tip(h):", "        if got is None or got[1]:"),
+    ("M12", "a held grade recarries",
+     "        if item.get(\"grade_held\") or self.strict_update() is not False:",
+     "        if self.strict_update() is not False:"),
+    ("M13", "the non-recarried head is graded against its merge base (serial)",
+     "        self.serial(item, h, item.get(\"nr_base\"))", "        self.serial(item, h, None)"),
+    ("M14", "the non-recarried head is graded against its merge base (--overlap)",
+     "                        a[\"rc_base\"] = a.get(\"nr_base\") or rb", "                        a[\"rc_base\"] = rb"),
+    ("M15", "strict_update reads the policy", "        return {\"true\": True, \"false\": False}.get(o.strip()) if ok else None",
+     "        return False"),
+    # prepr.sh step 6d's diff-mutant survivors at 5358f7b1, killed by tests added after them.
+    ("M16", "a REMERGE FAILED recarry stops as a git failure", "            if failed:  # carry f7d2bf7c",
+     "            if False:  # carry f7d2bf7c"),
+    ("M17", "a rejoin refused again is skipped again",
+     "                        self.skip(pr, \"post-merge\" if self.is_merged(pr) else s.step, f\"#{pr} {s.why}\", s.cls)\n",
+     "                        pass\n"),
+    ("M18", "the rejoin sleeps between reads", "            if waiting:\n                self.hold_refresh()  # the rejoin",
+     "            if False:\n                self.hold_refresh()  # the rejoin"),
+    ("M19", "the rejoin's sleep is the train's poll grain",
+     "                self.sleep(min(POLL_SECONDS, HEARTBEAT_SECONDS))\n\n    def skip_report", "                pass\n\n    def skip_report"),
+]
+
+def one(m: tuple[str, str, str, str]) -> tuple[str, str, list[str]]:
+    mid, _arm, old, new = m
+    text = SRC.read_text()
+    if old and text.count(old) != 1:
+        return mid, "STALE", [f"span occurs {text.count(old)} times"]
+    dst = SRC.parent / f"_mutant_{mid}.py"
+    try:
+        dst.write_text(text.replace(old, new) if old else text)
+        r = subprocess.run([sys.executable, str(dst), "--self-test"], cwd=ROOT, capture_output=True, text=True,
+                           timeout=1800)
+        fails = [ln.strip() for ln in r.stdout.splitlines() if ln.startswith("  FAIL")]
+        if mid == "M0":
+            return mid, "PASS" if r.returncode == 0 and not fails else "BROKEN", fails
+        return mid, "KILLED" if fails or r.returncode else "SURVIVED", fails or [f"rc {r.returncode}"]
+    finally:
+        dst.unlink(missing_ok=True)
+
+
+def main(argv: list[str]) -> int:
+    mutant_guard.arm([], scratch=[SRC.parent / f"_mutant_{m[0]}.py" for m in MUTANTS])
+    if argv[:1] == ["--list"]:
+        for mid, arm, _o, _n in MUTANTS:
+            print(f"{mid}\t{arm}")
+        return 0
+    todo = [m for m in MUTANTS if not argv or m[0] in argv]
+    bad = 0
+    with concurrent.futures.ThreadPoolExecutor(max_workers=4) as ex:
+        for mid, state, fails in ex.map(one, todo):
+            arm = next(a for i, a, _o, _n in MUTANTS if i == mid)
+            print(f"{mid} {state}: {arm}")
+            for f in fails[:4]:
+                print(f"    {f[:200]}")
+            bad += state not in ("PASS", "KILLED")
+    print(f"MUTANTS: {len(todo)} run, {bad} not as required")
+    return 1 if bad else 0
+
+
+if __name__ == "__main__":
+    sys.exit(main(sys.argv[1:]))
diff --git a/dev/programme/carries/carry-201.json b/dev/programme/carries/carry-201.json
index 74050c1da..597d7aee7 100644
--- a/dev/programme/carries/carry-201.json
+++ b/dev/programme/carries/carry-201.json
@@ -13,7 +13,7 @@
   "the in-tree brief of a stage with no live roster group."
  ],
  "issue": 201,
- "stage": "any later seat that stamps a release (tools/release/stamp.py, the deploy-key tag push of dev/governance/decisions/0009-agent-identities-for-author-and-approver.md step 5); the D13 dimension of a later audit round (dev/governance/dimensions/D13.md is its method, dev/audit/rounds/round5/D13/seat-a/dora_cfr.py its harness); the D11 dimension of a later audit round, whose method dev/governance/dimensions/D11.md is and whose subject is .github/workflows/governance.yml; and the D0 dimension of a later audit round, whose method dev/governance/dimensions/D0.md is and whose capture harness is tests/optimality.py; and any later seat that repairs the nightly-ha positive control in tests/nightly_ha.py (the check is `check_hb_positive_control`, and the sites the RCA names are the py-spy call and the heartbeat pin); the next planning seat (the schedule model at tools/plan/replan.py and the page it feeds); and the roster owner's next re-record of the roster's wave field; the owner's decision on the off-host liveness barrier for audit class N-silent-stop (dev/audit/rca/R10-RCA-ORCH-CONTINUITY.md section 6, the seat that creates the schedule); and any later seat that maintains tools/audit/seat/failure_logs.sh or runs it from a cloud seat; the owner's decision whether to run the planted-defect audit that the review-strength guardrail names when it trips (tools/audit/seat/review_strength.py --guardrail, report-only under owner ruling R13); and the next seat that moves the typing ruler (tests/typing_ruler.py, its pair in tests/typing_budgets.json) off homeassistant-stubs; and the owner's next paste of tools/audit/seat/cloud-setup.sh into the environment's setup script",
+ "stage": "any later seat that stamps a release (tools/release/stamp.py, the deploy-key tag push of dev/governance/decisions/0009-agent-identities-for-author-and-approver.md step 5); the D13 dimension of a later audit round (dev/governance/dimensions/D13.md is its method, dev/audit/rounds/round5/D13/seat-a/dora_cfr.py its harness); the D11 dimension of a later audit round, whose method dev/governance/dimensions/D11.md is and whose subject is .github/workflows/governance.yml; and the D0 dimension of a later audit round, whose method dev/governance/dimensions/D0.md is and whose capture harness is tests/optimality.py; and any later seat that repairs the nightly-ha positive control in tests/nightly_ha.py (the check is `check_hb_positive_control`, and the sites the RCA names are the py-spy call and the heartbeat pin); the next planning seat (the schedule model at tools/plan/replan.py and the page it feeds); and the roster owner's next re-record of the roster's wave field; the owner's decision on the off-host liveness barrier for audit class N-silent-stop (dev/audit/rca/R10-RCA-ORCH-CONTINUITY.md section 6, the seat that creates the schedule); and any later seat that maintains tools/audit/seat/failure_logs.sh or runs it from a cloud seat; the owner's decision whether to run the planted-defect audit that the review-strength guardrail names when it trips (tools/audit/seat/review_strength.py --guardrail, report-only under owner ruling R13); and the next seat that moves the typing ruler (tests/typing_ruler.py, its pair in tests/typing_budgets.json) off homeassistant-stubs; and the owner's next paste of tools/audit/seat/cloud-setup.sh into the environment's setup script; and the orchestrator seat that holds the merge train's state-directory logs (train.sh's log and skipped.json under HPO_STATE_DIR), for the measure-first BOT_HEAD count R10-TRAIN-MERGE-LOOP-2 carried to R10-TRAIN-REJOIN-NO-RECARRY",
  "carries": [
   {
    "from": "the round-5 D11-02 finding (#1301), whose fix is rule \"rows\" in tools/release/stamp.py -- the stamp now re-applies `record`'s own predicate to the window it is about to close",
@@ -182,6 +182,13 @@
    "control": "The grade never sees its own run (status in_progress), so the push that merges this change grades the sixteen runs before it, none carrying a probe step: dev/audit/harnesses/r10_hotfix_ci_critpath_4/replay.py section 6 reads that window at 29.067 against 21.983 + 1.3. The first push after it grades its merge run probed; with each of #3201's two fully green probed CI runs (41862133797, 41862145105) standing in for the merge run, replay.py section 6 reads 25.644 and 25.993, still over 23.283, because `tests / closures` prices about 1400 reference-host seconds probed (its two fast-host runs, probes 22 s) where the budget's window priced it at its fastest draw, 1117 s. The control that the constant is load-bearing: the one-machine 17.50 / 18.92 reads the same windows at 22.252 and 22.633, green, which is why tools/audit/seat/probe_bridge.py --self-test now refuses any PROBE_REFERENCE_S the committed fleet record does not re-derive.",
    "remeasure": "On each push after the merge, read the `tests / ci-ratchet` step's critical_path_minutes line. Once eight or more probed push runs exist, run `python3 tools/audit/seat/probe_bridge.py --repo tvofi/heatpump_optimizer` and compare its implied PROBE_REFERENCE_S with the tree's (`python3 tools/audit/seat/probe_bridge.py` prints the committed record's). Re-run replay.py section 6 on a fleet.json holding those push runs.",
    "brief": "For the seat that merges R10-HOTFIX-CI-CRITPATH-4 and the owner: the merge commit's own `tests / ci-ratchet` reads GREW critical_path_minutes (29.067, no probed run in its window), and the pushes after it are predicted to keep reading GREW near 25.6-26.0 on the fleet-derived unit, not to clear: the budget 21.983 was recorded on each heavy job's fastest draw, below the fleet's fast-class host for `tests / closures`. No constant may be moved to clear it (probe_bridge.py --self-test refuses one the fleet record does not re-derive). The decision is the owner's under CLAUDE.md rule 2: re-record critical_path_minutes in the probed unit once a fully probed window exists (reason in the commit message), or pay it by cutting work on the closures / ci-ratchet path. Separately, a robustness follow-up from the #3201 review: window_work_minutes unions timing-inferred need edges across the window, so one run's coincidence (a job created as an unrelated job ended, within QUEUE_EPS) becomes an edge for the whole window; replay.py section 6's paths carry `budget-raise-gate` or `validate-hacs` (about 30 s) ahead of `tests / closures` that way. Keeping only edges to the workflow's declared `needs:` would close it; it is not built here."
+  },
+  {
+   "from": "#3288 (R10-TRAIN-MERGE-LOOP-2) body item 23779576, carried to R10-TRAIN-REJOIN-NO-RECARRY and passed on by its fixer: the count of BOT_HEAD stops in the train logs since 2026-10-20, and how many of those heads had their pull_request runs approved at refusal time",
+   "effect": "removes",
+   "control": "The fixer seat for R10-TRAIN-REJOIN-NO-RECARRY ran in a cloud container, where neither the tree nor the host holds a train log: `git ls-files | grep -cE '(^|/)train[^/]*\\.log$|queue\\.seen\\.json|skipped\\.json$'` printed 0 and `ls ~/.local/state/hpo` found no state directory, while the null control `git ls-files | grep -c merge_train` printed 2, so the grep reads the tree. The count cannot be taken from that seat; the option the carry assumed is not there.",
+   "remeasure": "On the orchestrator's host, over the train logs under HPO_STATE_DIR since 2026-10-20: `grep -h '\\[BOT-HEAD\\]' <logs> | grep -cE 'TRAIN STOPPED|SKIP #'` for the stops, then per stopped head `gh api 'repos/tvofi/heatpump_optimizer/actions/runs?head_sha=<sha>&event=pull_request' --jq '.workflow_runs[] | [.status, .conclusion] | @tsv'` read against the refusal's timestamp; null control: the same grep over a log with no BOT-HEAD line prints 0.",
+   "brief": "The measure-first count of BOT_HEAD stops (and how many had approved pull_request runs at refusal time) is owed by the seat holding the train logs, not by a cloud fixer. Since R10-TRAIN-REJOIN-NO-RECARRY a non-strict ruleset no longer recarries a clean head, but a GITHUB_TOKEN tip is still recarried (Train.merges_as_is refuses a bot tip), so the BOT_HEAD arm the count would size is unchanged by that group."
   }
  ]
-}
\ No newline at end of file
+}
diff --git a/dev/programme/delivery/3359.md b/dev/programme/delivery/3359.md
new file mode 100644
index 000000000..1dd8f3b6f
--- /dev/null
+++ b/dev/programme/delivery/3359.md
@@ -0,0 +1 @@
+- [#3359](https://github.com/tvofi/heatpump_optimizer/pull/3359) — **open**, R10-TRAIN-REJOIN-NO-RECARRY: train rejoin no recarry (R10-TRAIN-REJOIN-NO-RECARRY)
diff --git a/tests/closures.json b/tests/closures.json
index 49fc44084..08fcc071f 100644
--- a/tests/closures.json
+++ b/tests/closures.json
@@ -4174,6 +4174,7 @@
    "dev/audit/harnesses/r10_train_overlap_grade_p4_mutants.py",
    "dev/audit/harnesses/r10_train_raise_hold_mutants.sh",
    "dev/audit/harnesses/r10_train_raise_hold_replay.py",
+   "dev/audit/harnesses/r10_train_rejoin_no_recarry_mutants.py",
    "dev/audit/harnesses/r10_train_upgrade_mutants.py",
    "dev/audit/harnesses/r10_triage_gate_replay.py",
    "dev/audit/harnesses/r10_triage_p391.py",
diff --git a/tools/audit/seat/instruments/merge_train.py.md b/tools/audit/seat/instruments/merge_train.py.md
index c7f4806bc..2c5b4d0f5 100644
--- a/tools/audit/seat/instruments/merge_train.py.md
+++ b/tools/audit/seat/instruments/merge_train.py.md
@@ -77,6 +77,22 @@
   CI judges the new head, and a recarry that reproduces the same red tree
   stops instead of looping. A one-car batch (the #2595 repair car onto a red
   main) cannot move a base, so the grade never fires there.
+  Card 5 (tvofi 2026-11-07, `Train.merges_as_is`): a head that lacks
+  origin/main is recarried only when `main-protect-checks` requires an
+  up-to-date branch (`strict_update`, read live; unreadable counts as
+  required), when git's merge of origin/main and the head conflicts, when the
+  head is a GITHUB_TOKEN tip, or when a graded red holds it; otherwise it is
+  logged `#<pr> no recarry:` and merges at its proven head, its merge tree
+  graded against its merge base at the merge, as the overlap grade does.
+  Card 1 (`Train.rejoin`): under `--skip-bad`, an entry skipped on a head red
+  holding `gate` (`HeadRed`) rejoins the same train after the batch's own
+  merges, through the serial path, once its skipped head classifies GREEN
+  (`classify_at`), with no `add`; RED, a head still WAIT `wait_cap_s` (polls
+  x 305 s, 7320 s at the default) after its skip, or a head the branch moved
+  off stays skipped, each logged `REJOIN #<pr>: ...`; a rejoin that merges
+  is CURED. Residual: the rejoin's wait delays the next spooled batch, never
+  a merge of its own batch. `dev/audit/harnesses/r10_train_rejoin_no_recarry_mutants.py`
+  holds one mutant per arm of both cards.
   `batch` also takes several batches in one queue (a list of lists), run in
   order on one train, each with its own admission, proof and merges; between
   two it drains what `train.sh add` spooled into one more batch, never into a
diff --git a/tools/audit/seat/instruments/remerge_main.sh.md b/tools/audit/seat/instruments/remerge_main.sh.md
index 0b1dd0456..746e73adc 100644
--- a/tools/audit/seat/instruments/remerge_main.sh.md
+++ b/tools/audit/seat/instruments/remerge_main.sh.md
@@ -6,4 +6,7 @@
   on a clean 2-parent merge of the live head and main under the live body.
   When: main moved under an open PR. Refusal: a conflict is not
   auto-resolved — it stops loudly instead, the merge aborted, so the worktree
-  is left clean at origin/<branch> for the train to release.
+  is left clean at origin/<branch> for the train to release. `MERGE CONFLICT
+  <pr>` names only a merge that left unmerged paths; a fetch, reset or merge
+  that failed otherwise prints `REMERGE FAILED <pr> at <step> (rc=N)` under
+  git's own words, which the train stops on as a failure, never a conflict.
diff --git a/tools/audit/seat/merge_train.py b/tools/audit/seat/merge_train.py
index a156f1514..07c2271b3 100644
--- a/tools/audit/seat/merge_train.py
+++ b/tools/audit/seat/merge_train.py
@@ -964,6 +964,15 @@ class MainMoved(Stop):
         super().__init__(step, why, cls=MAIN_MOVED)
 
 
+class HeadRed(Stop):
+    """A head's required contexts concluded red (step "ci"): <red> the names, <head> the sha.
+    Under --skip-bad a skip whose red holds GATE is the rejoin's candidate (`Train.rejoin`)."""
+
+    def __init__(self, why: str, head: str, red: "list[str]") -> None:
+        super().__init__("ci", why)
+        self.head, self.red = head, red
+
+
 def classified(s: Stop) -> str:
     """<why>, prefixed `[<class>] ` when the stop is one of the known shapes."""
     return f"[{s.cls}] {s.why}" if s.cls else s.why
@@ -2331,7 +2340,8 @@ class Train:
         h = self.head(pr)
         if not is_sha(h):
             raise Stop("head", f"could not read the head: {h[:120]}")
-        if not self.contains_main(h):
+        item.pop("nr_base", None)
+        if not self.contains_main(h) and not self.merges_as_is(item, h):
             self.hold_refresh()  # a recarry is 5-15 min in app_push's prepr; --overlap's up-front loop is not a wait
             br = item.get("branch") or self.out("gh", "pr", "view", str(pr), "--repo", self.repo, "--json", "headRefName", "--jq", ".headRefName")
             wt = Path(item.get("worktree") or self.state / "wt" / str(pr))
@@ -2356,6 +2366,9 @@ class Train:
             code, o = self.run(["bash", tool("remerge_main"), str(pr), str(wt), br, str(body)])
             if "MERGE CONFLICT" in o:
                 raise Stop("recarry", "main does not merge without a resolution; that is a fixer's, and a re-review")
+            failed = next((ln.strip() for ln in o.splitlines() if ln.startswith("REMERGE FAILED")), None)
+            if failed:  # carry f7d2bf7c: git failed before any conflict, so nothing is owed a fixer
+                raise Stop("recarry", f"{failed}; run the train again once git answers")
             if "PUSHED" not in o:
                 # R9-RC-RECARRY-READBACK: app_push.sh --recarry confirms a race
                 # inside its own bounded read-back, so no PUSHED here is a real
@@ -2387,9 +2400,31 @@ class Train:
             raise self.bot_refusal(pr, h, bot)
         return h
 
+    def merges_as_is(self, item: dict, h: str) -> bool:
+        """Card 5 (tvofi, 2026-11-07): whether <h>, which lacks origin/main,
+        merges as it stands -- no recarry and no fresh CI run. True only when
+        RULESET requires no up-to-date branch (`strict_update` False: a strict
+        or unreadable policy recarries as before), no grade holds the car (a
+        held red is answered by a recarry and CI), git's merge of origin/main
+        and <h> is clean (a conflict is the one content reason to recarry), and
+        <h> is no GITHUB_TOKEN tip (whose cure is the recarry's App push). Then
+        item["nr_base"] is the merge base, the tree <h>'s CI read, and the
+        merge is graded against it at the merge (`grade_merge`)."""
+        pr = item["pr"]
+        if item.get("grade_held") or self.strict_update() is not False:
+            return False
+        got = self.merge_tree(self.git("rev-parse", "origin/main"), h)
+        if got is None or got[1] or self.bot_tip(h):
+            return False
+        item["nr_base"] = self.git("merge-base", "origin/main", h)
+        self.log(f"#{pr} no recarry: {h[:8]} merges with origin/main cleanly (merge tree {got[0][:8]}) and "
+                 f"{RULESET} requires no up-to-date branch; the proven head merges, graded at the merge")
+        return True
+
     def one(self, item: dict) -> None:
         self.hold_refresh()  # per item: a long item must not age the hold stale
-        self.serial(item, self.recarry(item), None)
+        h = self.recarry(item)
+        self.serial(item, h, item.get("nr_base"))
 
     def serial(self, item: dict, h: str, rb: "str | None") -> None:
         """`at_head`, recovering a MainMoved up to --main-moved-tries times: a
@@ -2413,7 +2448,8 @@ class Train:
                     raise
                 self.log(f"#{item['pr']} [MAIN-MOVED] {s.step}: {s.why}; recarry "
                          f"{n + 1}/{self.main_moved_tries} onto the new main, then CI again")
-                h, rb = self.recarry(item), None
+                h = self.recarry(item)
+                rb = item.get("nr_base")
             except Stop:
                 if item.pop("sweep_after", False):
                     self.sweep_bots()  # the entry stopped: the record PR waits no longer
@@ -2427,7 +2463,7 @@ class Train:
         caller lands entries one at a time, an earlier still-pending entry
         never jumped by a later eligible one."""
         h = item.get("rc_head") or self.recarry(item)
-        self.serial(item, h, item.get("rc_base"))
+        self.serial(item, h, item.get("rc_base") or item.get("nr_base"))
 
     def at_head(self, item: dict, h: str, rb: "str | None", req: "list[str] | None") -> None:
         """Steps 2-7 at a settled head: wait its CI, carry the verdict, land
@@ -2448,7 +2484,7 @@ class Train:
         red = [n for n in self.wait_ci(h, only=req) if n not in self.ignore]
         self.log(f"#{item['pr']} {h[:8]} ci red={red}")
         if red:
-            raise Stop("ci", "red at the head: " + ", ".join(red))
+            raise HeadRed("red at the head: " + ", ".join(red), h, red)
         if GATE in req:
             self.cross_check(item["pr"], h)
         self.run(["git", "fetch", "-q", "origin", h])
@@ -2689,7 +2725,7 @@ class Train:
             if not last_logged or waited - last_logged >= POLL_SECONDS:
                 last_logged = waited
                 self.log(f"#{pr} review run(s) {', '.join(open_)} at {h[:8]} still running; the merge waits "
-                         f"({int(waited)} s of {self.polls * (REVIEW_POLL_SECONDS + POLL_SECONDS)} s)")
+                         f"({int(waited)} s of {self.wait_cap_s()} s)")
 
     def release_worktrees(self) -> None:
         """Before the run's closing line (and again, a no-op, in `train`/`batch`'s
@@ -3003,16 +3039,27 @@ class Train:
     def tree(self, rev: str) -> str:
         return self.git("rev-parse", f"{rev}^{{tree}}")
 
-    def required(self, pr_head: bool = False) -> list[str]:
-        """The ruleset's required contexts, read live; less PR_ONLY unless
-        <pr_head> (a pull request's head carries those; main and a proof never)."""
+    def _checks_rule(self, field: str) -> "tuple[bool, str]":
+        """RULESET's required_status_checks rule's <field> (a jq path under
+        .parameters), read live: (read ok, the jq output)."""
         code, rid = self.run(["gh", "api", f"repos/{self.repo}/rulesets", "--jq",
                               f'.[] | select(.name == "{RULESET}") | .id'])
         code2, o = self.run(["gh", "api", f"repos/{self.repo}/rulesets/{rid.strip()}", "--jq",
-                             '.rules[] | select(.type == "required_status_checks")'
-                             ' | .parameters.required_status_checks[].context'])
+                             '.rules[] | select(.type == "required_status_checks") | .parameters' + field])
+        return not (code or code2 or not rid.strip().isdigit()), o
+
+    def strict_update(self) -> "bool | None":
+        """Whether RULESET requires a branch up to date before its merge
+        (`strict_required_status_checks_policy`), read live; None unreadable."""
+        ok, o = self._checks_rule(".strict_required_status_checks_policy")
+        return {"true": True, "false": False}.get(o.strip()) if ok else None
+
+    def required(self, pr_head: bool = False) -> list[str]:
+        """The ruleset's required contexts, read live; less PR_ONLY unless
+        <pr_head> (a pull request's head carries those; main and a proof never)."""
+        ok, o = self._checks_rule(".required_status_checks[].context")
         names = sorted({n.strip() for n in o.splitlines() if n.strip()} - set(() if pr_head else PR_ONLY))
-        if code or code2 or not rid.strip().isdigit() or not names:
+        if not ok or not names:
             raise Stop("proof", f"could not read {RULESET}'s required contexts; no proof is judged against a guessed list")
         return names
 
@@ -3047,7 +3094,7 @@ class Train:
         # composed-proof) must never hold a batch whose required set is green.
         red = [n for n in self.wait_ci(h, only=head_req) if n not in self.ignore]
         if red:
-            raise Stop("ci", f"#{pr} red at its head: " + ", ".join(red))
+            raise HeadRed(f"#{pr} red at its head: " + ", ".join(red), h, red)
         if self.real:
             o = self.run(["bash", tool("app_approve"), "--carry", v, h])[1]
             if "CARRY: yes" not in o:
@@ -3461,6 +3508,60 @@ class Train:
             if read_pid(self.state / QUEUE_OPEN) == os.getpid():
                 queue_seen_write(self.state, self._seen)
 
+    def rejoin_candidate(self, item: dict, s: Stop, rejoin: list) -> None:
+        """Card 1: queue a skip for `rejoin` when its Stop is a head red holding
+        GATE -- the deferral-shaped red a later read can turn GREEN; any other
+        skip is final, as before. The entry is kept as queued: a recarry it
+        rejoins with is its own."""
+        if isinstance(s, HeadRed) and GATE in s.red:
+            keep = {k: v for k, v in item.items() if k not in ("rc_head", "rc_base", "nr_base")}
+            rejoin.append((keep, s.head, self.clock()))
+
+    def wait_cap_s(self) -> int:
+        """The train's one wait cap in seconds, `polls` x (REVIEW_POLL_SECONDS +
+        POLL_SECONDS): the review-run wait's ceiling and the rejoin's bound."""
+        return self.polls * (REVIEW_POLL_SECONDS + POLL_SECONDS)
+
+    def rejoin(self, waiting: "list[tuple[dict, str, float]]", req: "list[str]") -> None:
+        """Card 1 (tvofi, 2026-11-07): each entry this batch SKIPped on a red
+        GATE rejoins the train, through the serial path, once its skipped head
+        classifies GREEN (`classify_at`, the reading `classify` prints) -- no
+        add and no merge seat. RED stays skipped (a real red never rejoins), and
+        so does a head still WAIT `wait_cap_s` after its skip, or one the branch
+        moved off (a new head owes a new verdict). It runs after the batch's own
+        merges, so no wait here holds one; a rejoin refused again is skipped
+        again, its earlier row replaced."""
+        cap = self.wait_cap_s()
+        while waiting:
+            later = []
+            for item, h, since in waiting:
+                pr = int(item["pr"])
+                if self.head(pr) != h:
+                    self.log(f"REJOIN #{pr}: the head moved off {h[:8]}; stays skipped")
+                    continue
+                runs = self._check_runs(h)
+                state = "wait" if runs is None else self.classify_at(h, runs, req)[0]
+                if state == "green":
+                    self.log(f"REJOIN #{pr}: GREEN at {h[:8]}, {int(self.clock() - since)} s after its skip; "
+                             "it rejoins this train")
+                    try:
+                        self.one(item)
+                    except Stop as s:
+                        if s.step == "main":
+                            raise
+                        self.skipped = [r for r in self.skipped if r["pr"] != pr]
+                        self.skip(pr, "post-merge" if self.is_merged(pr) else s.step, f"#{pr} {s.why}", s.cls)
+                elif state == "red":
+                    self.log(f"REJOIN #{pr}: RED at {h[:8]}; stays skipped (a real red never rejoins)")
+                elif self.clock() - since >= cap:
+                    self.log(f"REJOIN #{pr}: still WAIT at {h[:8]} past the {cap} s cap; stays skipped")
+                else:
+                    later.append((item, h, since))
+            waiting = later
+            if waiting:
+                self.hold_refresh()  # the rejoin's wait is a train wait: the record beat stays held
+                self.sleep(min(POLL_SECONDS, HEARTBEAT_SECONDS))
+
     def skip_report(self, total: int) -> None:
         """`--skip-bad`'s closing report: the skipped list under the state dir
         and one line the orchestrator's tooling can grep. An entry this train
@@ -3692,6 +3793,7 @@ class Train:
         self.hold_refresh()  # before the sweep: the record beat waits for the batch
         self.branches: list[str] = []
         mine = len(self.skipped)  # this batch's skips start here: an earlier batch's never filter a re-added entry
+        rejoin: "list[tuple[dict, str, float]]" = []  # card 1: (entry, head, skipped at) per red-GATE skip
         try:
             mf = _fastpath()
             # P289: a batch holding a critical-path entry reads its base without
@@ -3725,6 +3827,7 @@ class Train:
                     if s.step == "main":
                         raise
                     self.skip(int(item["pr"]), s.step, s.why, s.cls)
+                    self.rejoin_candidate(item, s, rejoin)
             serial = [a for a in entries if a["route"]]
             # --overlap: re-carry every serial entry UP FRONT, before anything
             # merges, pushing each branch so all their pull_request runs fire
@@ -3743,7 +3846,8 @@ class Train:
                 for a in todo:
                     self.log(f"#{a['pr']} overlap: recarry start")
                     try:
-                        a["rc_head"], a["rc_base"] = self.recarry(a), rb
+                        a["rc_head"] = self.recarry(a)
+                        a["rc_base"] = a.get("nr_base") or rb
                     except Stop as s:
                         if s.step == "main" or not self.skip_bad:
                             raise
@@ -3830,6 +3934,9 @@ class Train:
                             raise Stop(s.step, f"#{a['pr']} {s.why}", cls=s.cls) from None
                         self.skip(a["pr"], "post-merge" if self.is_merged(a["pr"]) else s.step,
                                   f"#{a['pr']} {s.why}", s.cls)
+                        self.rejoin_candidate(a, s, rejoin)
+            if rejoin and self.real:
+                self.rejoin(rejoin, head_req)
         except Stop as s:
             self.release_worktrees()  # before the closing lines, which stay last
             self.hold_release()
@@ -4943,6 +5050,11 @@ def _self_test() -> int:
     check("a missing-evidence refusal is not overridden by a mandate", rc == 1 and "app_approve.sh refused: REFUSE: the verdict cites" in lines[-1] and not approved(calls))
     rc, lines, calls = go({"contains": [False], "heads": [H0, H1], "remerge": "MERGE CONFLICT 7"})
     check("a recarry conflict stops it, named as one", rc == 1 and "without a resolution" in lines[-1] and not merged(calls))
+    rc, lines, calls = go({"contains": [False], "heads": [H0, H1], "remerge": "REMERGE FAILED 7 at fetch (rc=128)"})
+    check("carry f7d2bf7c: a remerge that failed before any conflict stops as a git failure -- never a "
+          "conflict, never read as a push that landed",
+          rc == 1 and "REMERGE FAILED 7 at fetch" in lines[-1] and "without a resolution" not in lines[-1]
+          and not merged(calls))
     rc, lines, calls = go({"contains": [False], "heads": [H0], "remerge": "REFUSE: body"})
     check("a recarry that pushed nothing and left the head where it was stops it (the refusal is real)",
           rc == 1 and "pushed nothing" in lines[-1] and not merged(calls))
@@ -6967,6 +7079,12 @@ def _batch_self_test(check) -> None:
         runs = [{"name": n, "id": i, "status": "in_progress" if pend else "completed", "started_at": "1",
                  "conclusion": "failure" if over and n == w["ci_red"] else "success"}
                 for i, n in ((11, R0), (12, "policy-docs"))]
+        if w.get("gate_seq") is not None:  # the rejoin arms: GATE is required, its state per read
+            seq = w["gate_seq"].get(sha) or ["green"]
+            st = seq[min(w.get("cr_reads", {}).get(sha, 1), len(seq)) - 1]
+            runs.append({"name": GATE, "id": 17, "started_at": "1", "check_suite": {"id": 17},
+                         "status": "in_progress" if st == "wait" else "completed",
+                         "conclusion": None if st == "wait" else "failure" if st == "red" else "success"})
         if sha == w["base_sha"]:  # main's own push run writes every required context
             runs += [{"name": n, "id": 15, "status": "completed", "started_at": "1", "conclusion": "success"}
                      for n in w["required"].split() if n == "never-dispatched"]
@@ -7079,6 +7197,14 @@ def _batch_self_test(check) -> None:
                 return 0, "no script here"
             if argv[:2] == ["gh", "api"] and a.endswith("rulesets --jq " + argv[-1]):
                 return (0, "7") if w["required"] else (1, "HTTP 404")
+            if argv[:3] == ["gh", "api", "graphql"] and "statusCheckRollup" in a:  # A5's rollup: GitHub agrees
+                n = int(next(x for x in argv if x.startswith("pr="))[3:])
+                return 0, json.dumps({"data": {"repository": {"pullRequest": {"commits": {"nodes": [{"commit": {
+                    "oid": w["heads"][n], "statusCheckRollup": {"contexts": {"pageInfo": {"hasNextPage": False},
+                        "nodes": [{"__typename": "CheckRun", "name": GATE, "status": "COMPLETED",
+                                   "conclusion": "SUCCESS", "isRequired": True}]}}}}]}}}}})
+            if "rulesets/7" in a and "strict_required_status_checks_policy" in a:
+                return 0, w.get("strict", "true")  # today's world: an up-to-date branch is required
             if "rulesets/7" in a:
                 return 0, w["required"]
             if argv[:3] == ["gh", "workflow", "run"]:
@@ -7508,6 +7634,47 @@ def _batch_self_test(check) -> None:
           "happens only after the earlier entries merged (recarry one, wait, merge, next)",
           w["rc"] == 0 and list(w["merged"]) == [3, 1, 2]
           and merges and recarries and min(merges) < min(recarries))
+    # CARD 5, NO RECARRY (R10-TRAIN-REJOIN-NO-RECARRY; tvofi 2026-11-07): under a ruleset requiring
+    # no up-to-date branch, a head whose merge with origin/main is clean merges as it stands -- the
+    # proven head, graded at the merge -- and only a merge-tree conflict (or a strict or unreadable
+    # policy) recarries.
+    for ov in (True, False):
+        v = dict(ovl)
+        w = go(v, base="main", setup=lambda w: (main_moved(w), w.update(remerge=True, strict="false",
+                                                                         verdicts=dict(w["heads"]))),
+               overlap=ov)
+        check(f"NO RECARRY (c){' --overlap' if ov else ''}: a clean merge tree against origin/main and an "
+              "unchanged proven head merge with no recarry, at the verdicted heads, each graded at its merge",
+              w["rc"] == 0 and list(w["merged"]) == [3, 1, 2] and not w.get("recarries")
+              and not any("recarry: main merged" in ln for ln in w["lines"])
+              and w["heads"] == w["verdicts"]
+              and all(any(ln.startswith(f"#{p} no recarry:") for ln in w["lines"]) for p in (1, 2))
+              and all(any(ln.startswith(f"#{p} grade: merge tree") and ln.endswith("green") for ln in w["lines"])
+                      for p in (1, 2)))
+    w = go({1: {".github/workflows/t.yml": "x\n"}}, base="main", overlap=True,
+           setup=lambda w: (main_moved(w), w.update(strict="false")))
+    check("NO RECARRY grades the un-recarried car against its merge base even when the batch moved nothing: "
+          "the merge tree with the foreign main is read before it lands",
+          w["rc"] == 0 and list(w["merged"]) == [1] and not w.get("recarries")
+          and any(ln.startswith("#1 grade: merge tree") and ln.endswith("green") for ln in w["lines"]))
+    for strict, why in (("true", "a strict policy"), ("", "an unreadable policy")):
+        w = go(ovl, base="main", setup=lambda w, s=strict: (main_moved(w), w.update(remerge=True, strict=s)),
+               overlap=True)
+        check(f"NO RECARRY null control: under {why} every serial head that lacks main is recarried, as today",
+              w["rc"] == 0 and list(w["merged"]) == [3, 1, 2] and sorted(w.get("recarries", [])) == [1, 2]
+              and not any(" no recarry:" in ln for ln in w["lines"]))
+
+    def main_conflicts(w):
+        (w["R"] / ".github/workflows/t.yml").write_text("main\n")
+        g(w["R"], "commit", "-qam", "main moved t.yml")
+    w = go({1: {".github/workflows/t.yml": "x\n"}, 2: {".github/workflows/u.yml": "y\n"}}, base="main",
+           setup=lambda w: (main_conflicts(w), w.update(remerge=True, strict="false")), overlap=True, skip_bad=True)
+    check("NO RECARRY null control (d): a merge-tree conflict against origin/main still recarries (the "
+          "recarry names the conflict), while the clean head beside it does not",
+          any("remerge_main.sh 1 " in c for c in w["calls_flat"])
+          and any(ln.startswith("SKIP #1 recarry:") and "main does not merge" in ln for ln in w["lines"])
+          and any(ln.startswith("#2 no recarry:") for ln in w["lines"]) and 2 in w["merged"]
+          and w.get("recarries", []) == [])
     w = go(ovl, base="main", setup=lambda w: (main_moved(w), w.update(remerge=True, pending_prs={1})),
            overlap=True)
     m1 = next((i for i, ln in enumerate(w["lines"]) if ln.startswith("#1 MERGED")), None)
@@ -7538,6 +7705,13 @@ def _batch_self_test(check) -> None:
           "none is possible); it recarries at its turn, after the earlier merges, and lands",
           w["rc"] == 0 and list(w["merged"]) == [3, 1, 2] and w.get("recarries") == [2]
           and any(ln.startswith("OVERLAP: recarrying #1 up front") for ln in w["lines"]))
+    w = go({1: {".github/workflows/t.yml": "x\n"}, 2: {"b.txt": "B\n"}, 3: {"a.txt": "A\n"}}, base="main",
+           setup=lambda w: w.update(remerge=True, strict="false", bot_heads={w["heads"][2]: "ci: pin killed mutants"}),
+           overlap=True)
+    check("NO RECARRY keeps a bot head's cure: under a non-strict ruleset a GITHUB_TOKEN tip with a clean "
+          "merge tree is still recarried (the App push), and lands",
+          w["rc"] == 0 and list(w["merged"]) == [3, 1, 2] and w.get("recarries") == [2]
+          and not any(ln.startswith("#2 no recarry:") for ln in w["lines"]))
 
     # THE OVERLAP GRADE (R10-TRAIN-OVERLAP-GRADE): the third-instance barrier
     # (6077bf70e, 143e2d0ac, a2576fcb2 -- #2586 landed on a tree no CI had
@@ -7555,6 +7729,13 @@ def _batch_self_test(check) -> None:
           list(w["merged"]) == [1, 2] and w["rc"] == 1 and w.get("recarries") == [3]
           and any(ln.startswith("TRAIN STOPPED grade") for ln in w["lines"])
           and any("the recarry produced the same tree, so the car is held" in ln for ln in w["lines"]))
+    w2 = go({1: {"a.txt": "A\n"}, 2: {".github/workflows/t.yml": "w\n"},
+             3: {"tests/golden/claimed_drift.txt": "c\n", "red.txt": "x\n"}},
+            base="main", setup=lambda w: w.update(remerge=True, strict="false"), overlap=True, main_moved_tries=1)
+    check("NO RECARRY never skips the recarry a graded red holds: under a non-strict ruleset the held car is "
+          "still recarried for CI, then stopped on the same tree",
+          list(w2["merged"]) == [1, 2] and w2["rc"] == 1 and w2.get("recarries") == [3]
+          and any("the recarry produced the same tree, so the car is held" in ln for ln in w2["lines"]))
     check("THE OVERLAP GRADE: the red arm read the MERGE tree -- #3's own file was in the graded "
           "worktree, and the grade ran once per moved base (the recarry's identical tree is cached, "
           "not re-run)",
@@ -7676,6 +7857,74 @@ def _batch_self_test(check) -> None:
           "merges (the default did not change)",
           w["rc"] == 1 and not w["merged"] and not w["pushed"]
           and any(ln.startswith("TRAIN STOPPED ci:") and "#2" in ln for ln in w["lines"]))
+    # CARD 1, THE REJOIN (R10-TRAIN-REJOIN-NO-RECARRY; tvofi 2026-11-07): an entry SKIPped on a red
+    # GATE rejoins this train once its head classifies GREEN, within `wait_cap_s` of the skip, with
+    # no add; a head reading RED, or still WAIT at the cap, stays skipped and holds no merge.
+    def gated(seq):
+        def setup(w):
+            w.update(required=f"{R0}\npolicy-docs\n{GATE}\n", gate_seq={w["heads"][2]: seq},
+                     remerge=True, h2=w["heads"][2])
+        return setup
+
+    def ticking():
+        t = [0.0]
+
+        def clock() -> float:
+            t[0] += 60.0
+            return t[0]
+        return clock
+    two = {1: {"a.txt": "A\n"}, 2: {"b.txt": "B\n"}}
+    w = go(two, base="main", skip_bad=True, setup=gated(["red", "wait", "green"]), clock=ticking())
+    rj = [ln for ln in w["lines"] if ln.startswith("REJOIN #2")]
+    check("REJOIN (a): an entry SKIPped on a red gate whose head turns GREEN within the cap rejoins the "
+          "train and merges, with no add; the skip is CURED and the train exits 0",
+          w["rc"] == 0 and sorted(w["merged"]) == [1, 2] and any("GREEN" in ln for ln in rj)
+          and any(ln.startswith("SKIP #2 ci:") and "red at its head: gate" in ln for ln in w["lines"])
+          and any(ln.startswith("CURED #2") for ln in w["lines"]) and w["skip_json"] == []
+          and w["cr_reads"].get(w["h2"], 0) >= 3 and w["lines"][-1] == "TRAIN DONE")
+    w = go(two, base="main", skip_bad=True, setup=gated(["red"]), clock=ticking())
+    rj = [ln for ln in w["lines"] if ln.startswith("REJOIN #2")]
+    check("REJOIN null control (b): a head whose classify reads RED stays SKIPped -- never re-run, "
+          "never recarried, reported, rc 1",
+          w["rc"] == 1 and sorted(w["merged"]) == [1] and len(rj) == 1 and "RED" in rj[0]
+          and "stays skipped" in rj[0] and sum(ln.startswith("SKIP #2 ") for ln in w["lines"]) == 1
+          and not any(ln.startswith("#2 recarry") for ln in w["lines"])
+          and [s["pr"] for s in (w["skip_json"] or [])] == [2])
+    w = go(two, base="main", skip_bad=True, setup=gated(["red", "wait"]), clock=ticking())
+    rj = [i for i, ln in enumerate(w["lines"]) if ln.startswith("REJOIN #2")]
+    m1 = next((i for i, ln in enumerate(w["lines"]) if ln.startswith("#1 MERGED")), None)
+    check("REJOIN null control (b): a head that never leaves WAIT stops at the cap and does not hold the "
+          "batch -- #1 merged before the rejoin's first read, #2 stays skipped, the train ends",
+          w["rc"] == 1 and sorted(w["merged"]) == [1] and bool(rj) and m1 is not None and m1 < rj[0]
+          and "cap" in w["lines"][rj[-1]] and "stays skipped" in w["lines"][rj[-1]]
+          and w["cr_reads"].get(w["h2"], 0) <= 3 + 2 * (2 * (REVIEW_POLL_SECONDS + POLL_SECONDS)) // 60
+          and w["slept"].count(min(POLL_SECONDS, HEARTBEAT_SECONDS)) == w["cr_reads"].get(w["h2"], 0) - 2
+          and w["lines"][-1] == "TRAIN DONE" and [s["pr"] for s in (w["skip_json"] or [])] == [2])
+    w = go(two, base="main", skip_bad=True, setup=lambda w: (gated(["red", "green", "red"])(w), w.update(strict="false")),
+           clock=ticking())
+    check("REJOIN: a rejoin refused again (red at its own CI wait) is skipped again, its row replaced, "
+          "one row and one skip for #2",
+          w["rc"] == 1 and sorted(w["merged"]) == [1] and any(ln.startswith("REJOIN #2: GREEN") for ln in w["lines"])
+          and [s["pr"] for s in (w["skip_json"] or [])] == [2]
+          and "red at the head: gate" in (w["skip_json"] or [{}])[0].get("reason", "")
+          and any(ln == "SKIP REPORT: 1 skipped of 2" for ln in w["lines"]) and w["lines"][-1] == "TRAIN DONE")
+    w = go({1: {"a.txt": "A\n"}, 2: {".github/workflows/t.yml": "x\n"}}, base="main", skip_bad=True,
+           setup=lambda w: (gated(["red", "green"])(w), w.update(strict="false")), clock=ticking())
+    check("REJOIN (a), serial: a serial entry SKIPped on a red gate at its turn rejoins once GREEN and merges",
+          w["rc"] == 0 and sorted(w["merged"]) == [1, 2]
+          and any(ln.startswith("SKIP #2 ci: #2 red at the head: gate") for ln in w["lines"])
+          and any(ln.startswith("REJOIN #2: GREEN") for ln in w["lines"]))
+    w = go(two, base="main", skip_bad=True, clock=ticking(),
+           setup=lambda w: (gated(["red", "green"])(w), w.update(on_log=lambda ln: ln.startswith("SKIP #2")
+                                                                  and w["heads"].update({2: "f" * 40}))))
+    check("REJOIN: a skipped head the branch moved off does not rejoin -- a new head owes a new verdict",
+          w["rc"] == 1 and sorted(w["merged"]) == [1]
+          and any(ln.startswith("REJOIN #2: the head moved off") for ln in w["lines"])
+          and not any("GREEN" in ln for ln in w["lines"] if ln.startswith("REJOIN")))
+    w = go(two, base="main", skip_bad=True, setup=lambda w: (gated(["green"])(w), w["red"].add(w["h2"])),
+           clock=ticking())
+    check("REJOIN null control: a skip on a red that is not GATE is no rejoin candidate at all",
+          w["rc"] == 1 and sorted(w["merged"]) == [1] and not any(ln.startswith("REJOIN") for ln in w["lines"]))
     w = go({1: {"a.txt": "A\n"}, 2: {"b.txt": "B\n"}}, cap=1, setup=redmain, skip_bad=True)
     w2 = go({1: {"a.txt": "A\n"}, 2: {"b.txt": "B\n"}},
             setup=lambda w: w.update(on_sleep=lambda: w["red"].add(w["base_sha"])), skip_bad=True)
diff --git a/tools/audit/seat/pr_args.sh b/tools/audit/seat/pr_args.sh
index 7ad8cdf7a..d321cb3be 100644
--- a/tools/audit/seat/pr_args.sh
+++ b/tools/audit/seat/pr_args.sh
@@ -1573,8 +1573,12 @@ GH
     && [ "$(git -C "$t/rmw" rev-parse HEAD^2)" = "$(git -C "$t/rmm" rev-parse origin/main)" ]
   ck "remerge_main: a fetch failing once with git's 502 is fetched again, and the clean merge is kept" $?
   printf '%s\n' "fatal: couldn't find remote ref rc" > "$t/rmgitfail"
-  rmrun - rc; grep -qF "MERGE CONFLICT 7" "$t/out" && [ ! -s "$t/rmgitfail" ] && grep -qF "couldn't find remote ref" "$t/out"
-  ck "null control: a fetch git rejected is not fetched again (a second fetch would have succeeded)" $?
+  rmrun - rc; ! grep -qF "MERGE CONFLICT" "$t/out" && grep -qF "REMERGE FAILED 7 at fetch" "$t/out" && [ ! -s "$t/rmgitfail" ] \
+    && grep -qF "couldn't find remote ref" "$t/out"
+  ck "null control: a fetch git rejected is not fetched again (a second fetch would have succeeded), and is named REMERGE FAILED at fetch, never MERGE CONFLICT (carry f7d2bf7c)" $?
+  printf '%s\n' "fatal: couldn't find remote ref rc" > "$t/rmgitfail"
+  rmrun remergeconflict rc; grep -qF "MERGE CONFLICT 7" "$t/out"
+  ck "  mutant mut:remergeconflict (its line deleted): a rejected fetch is misreported as MERGE CONFLICT" $?
   : > "$t/rmgitfail"
   # The push's FAIL lines and prepr's `full log:` line reach the train's Stop message, and a push that
   # printed no PUSHED keeps its log (carry 16): the old grep kept only RECARRY|REFUSE|PUSHED and the trap
diff --git a/tools/audit/seat/remerge_main.sh b/tools/audit/seat/remerge_main.sh
index 138f304ab..8a1e90da4 100755
--- a/tools/audit/seat/remerge_main.sh
+++ b/tools/audit/seat/remerge_main.sh
@@ -10,7 +10,7 @@
 # example "GitHub reported a claim-file conflict it cannot resolve without the
 # claimnotes driver"); the default states none. merge_train.py calls this.
 # The worktree may be detached: it is reset to origin/<branch> before the merge, and left clean there
-# when the merge fails (MERGE CONFLICT).
+# when the merge fails (MERGE CONFLICT, or REMERGE FAILED <pr> at <step> when no conflict caused it).
 set -uo pipefail
 # A stopped run ends the whole tree it started (R10-PUSHER-REAP): pr_args.sh's EXIT
 # trap reaps it, and the push runs asynchronously so an INT does not wait behind it.
@@ -26,9 +26,18 @@ export GIT_AUTHOR_NAME=tvofi GIT_AUTHOR_EMAIL=70032254+tvofi@users.noreply.githu
 # origin/main, so the abort, or the reset when no merge is in progress, loses nothing.
 # The fetch rides git's own transient stderr out on gh_read.py's rule, the train's own
 # (R10-TRAIN-MERGE-LOOP-2): unretried, one 502 read as MERGE CONFLICT and stopped the train.
-if ! ( cd "$W" && python3 "$SEAT/gh_read.py" --git-retry git fetch -q origin main "$BR" && git reset -q --hard "origin/$BR" && git merge --no-edit -q origin/main ); then
+# MERGE CONFLICT is printed only for a merge that left unmerged paths (carry f7d2bf7c): a fetch that
+# spent its transient budget or git rejected, a refused reset, or a merge stopped for another reason
+# is REMERGE FAILED naming its step, with git's own words above it, and owes no fixer a resolution.
+step=fetch
+( cd "$W" && python3 "$SEAT/gh_read.py" --git-retry git fetch -q origin main "$BR" ) && step=reset \
+  && git -C "$W" reset -q --hard "origin/$BR" && step=merge && git -C "$W" merge --no-edit -q origin/main
+rc=$?
+if [ "$rc" -ne 0 ]; then
+  why="MERGE CONFLICT $PR"
+  { [ "$step" = merge ] && [ -n "$(git -C "$W" diff --name-only --diff-filter=U)" ]; } || why="REMERGE FAILED $PR at $step (rc=$rc)"  # mut:remergeconflict
   git -C "$W" merge --abort 2>/dev/null || git -C "$W" reset -q --hard "origin/$BR" 2>/dev/null || :  # mut:remergeabort
-  echo "MERGE CONFLICT $PR"; exit 1
+  echo "$why"; exit 1
 fi
 ( cd "$W" && python3 tests/env_drift.py --drop-inherited "$(git rev-parse origin/main)" >/dev/null 2>&1; git diff --quiet || git commit -qam "claims: drop the claims main already carries after the main merge" )
 ISS=$(grep -oiE '\b(fixes|closes|resolves) #[0-9]+' "$B" | grep -oE '[0-9]+' | sort -u | tr '\n' ' ')

## Before you return the verdict (P275)
Run `python3 -I tools/audit/carry_audit.py check --body <PR body file> --comments <file holding [{"id": 0, "body": <verdict.md text>}]>`. Give every reported item its own `Carry: <GROUP> | #<issue> | O<n> | dismissed: <reason>`;
an evidence line flagged by its wording takes `Carry: dismissed: evidence, not a finding`. Return the verdict only at rc 0.
