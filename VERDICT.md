Fix review: blocked 1aec0e574b424af409b8bed502e3424b336986a4 class-open: round 1's items 2-5 are unaddressed, policy_refusal reads three real reds as a deferral, and the merge broke the finder harness; all listed under Block

bus-nonce: 0ae1cd85550c7d4774833bf6def952d7

## Block

This is round 2, a delta review against the round-1 verdict at 940705766041a8316ba976d33a3b16b7ca281668 (probe/revt-r10-gate-defer-barrier-68948c61). The delta is merge b0762a639d (origin/main 14f227c5 merged in) plus record commit 1aec0e574b. Apart from the merge resolution in `gate_deferred_runs` and its four self-test stubs, the PR's own patch is the same as before (ev/pr_patch_delta.txt). The packet printed `Review scope: full` because no verdict on verdict/3499 names the reviewed head. I reviewed the delta and every round-1 item, as the dispatch asked.

Round-1 items checked at this head:

1. merge-conflict: RESOLVED. `git merge-tree --write-tree origin/main 1aec0e57` exits 0 against origin/main fc2a7edc (ev/merge_tree.txt). The resolution matches the merge message: main's `self.pages(..., "workflow_runs")` is joined to the branch's `(id, status, run_started_at)` tuples. Self-tests on the merged tree: merge_train 666 checks, 0 failed; orchestrator_tick 317, 0 failed; merge_pr 25, 0 failed. These match the body.
2. class-open, `merge_pr.sh` under-run: NOT ADDRESSED. `tools/audit/seat/merge_pr.sh` is byte-identical to the reviewed head (ev/unchanged_since_round1.txt is empty). After `HPO_MERGE_CLASSIFY_POLLS` (20) WAIT answers, it still prints `RED: <name>` and exits 1. This PR's own CI shows the shape: code run 43195308607 has sat `queued` since 09:52:29Z, so the 60-min check-run wait plus 20 classify polls would print RED on a deferral. The body still says it "waits out a classify WAIT before it prints RED".
3. class-open, census keyed on argument count: NOT ADDRESSED. Re-planted `classify(l, r, None)` in review_packet.py: merge_train self-test 666 checks, 0 failed (ev/mutant_M6.diff, ev/mutant_M6.log).
4. mutation-vacuous, M8: NOT ADDRESSED. M8 deletes `or self.gate_deferred(h, [GATE])` from `policy_refusal`. The merge_train self-test still reads 666 checks, 0 failed (ev/mutant_M8.diff, ev/mutant_M8.log). My JSON-lines copy of the finder harness reads it rc 0 with no DEFECT (ev/harness_jl_on_M8.txt). My plant (A, below) does kill it: under M8 the deferral alone reads `wait=False` (ev/plant_on_M8.txt). That instrument is mine and is not in the tree. Survivors my driver reports at this head: M6, M8.
5. body: NOT ADDRESSED. The Approval section still names "the generated `tools/audit/briefs/nudge.md`", which does not exist at this head (ev/nudge_path.txt: `fatal: path ... does not exist`).

New at this head:

6. harness: finder-harness-stale. The merge moved `gate_deferred_runs` onto main's paged JSON read. The committed `dev/audit/harnesses/r10_gate_defer_barrier.py` still stubs `actions/runs?head_sha=` with the retired TSV, so its `under` arm no longer reaches the code under test. At this head it exits 1 with `DEFECT under` and `DEFECT under-null`, and `under_started=['gate'] under_queued_null=['gate']` (ev/harness_head.txt). At origin/main fc2a7edc it prints the same two DEFECTs, plus `DEFECT policy` (ev/harness_base.txt). So the `under` arm cannot tell the fix from the baseline, and its null arm fails at both ends. The body's Figures line "at this head: exit 0, no DEFECT line" is false at this head. The merge's re-run list updated the self-tests' `started` stub (a `_jl` JSON-lines helper) but not the harness. I made a copy with one stub line changed to JSON lines (ev/reviewer_harness_jl.diff, ev/reviewer_harness_jl.py; it is mine, not the finder's). It reads head rc 0, `under_started=[]`, `under_queued_null=['TIMEOUT']` (ev/harness_jl_head.txt), and base rc 1 with `DEFECT policy` and `DEFECT under` (ev/harness_jl_base.txt). So the fix holds, and only the committed harness is stale. Fix: update the harness stub the way the self-test helper was updated, then re-take the figure.
7. class-open: `policy_refusal` reads a real red as a deferral. This is the barrier the dispatch asked to attack. I planted the cases with my instrument ev/reviewer_plant_policy.py at both ends (ev/plant_readings.txt):
   - A, a deferral alone: gate FAILURE with the code run queued or in_progress. Head: `wait=True`. Base: `wait=False`, red. Correct, and it is the fix.
   - Null, gate FAILURE with no unfinished run: `wait=False`, red, at both ends. Correct.
   - B, a real red beside a deferral: a second, newer gate FAILURE (the code run's own), with only an unrelated workflow unfinished (`codeql`, in_progress). Head: `wait=True`, "is a deferral". Base: red. WRONG.
   - B', a real gate red alone, with an unrelated workflow unfinished. Head: `wait=True`. WRONG.
   - C, a final red of another required context (`tests / fast (3.14)` FAILURE) beside a deferral gate, with the code run in_progress. Head: `wait=True`, and the gate early-return never reaches `red`. Base names both. WRONG: the other context's red is hidden. `classify` reads C correctly (`('red', ['gate'], ['tests / fast (3.14)'])`).

   Cause: the arm reads `self.gate_deferred(h, [GATE])`, and that counts ANY unfinished workflow run at the head. It is not `classify_at`'s `_gate_busy`, which is gate.py's `busy` over ci.yml runs. The arm also returns before the other required contexts are read. The body says the alternative that lost was "copying gate.py's `busy` into each reader (`classify_at` is the one reading)", but `policy_refusal` uses a second, broader reading. The cost is a bounded retry with the wrong reason, not a wrong merge: GitHub still refuses. Fix: read the deferral through the `classify_at`/`_gate_busy` reading, and check the other required contexts before the gate arm returns. Pin B, B' and C as self-test nulls; that also kills M8 (item 4).

## Findings

none

## Evidence

- Head measured: 1aec0e574b424af409b8bed502e3424b336986a4 (ev/HEAD.txt). It is the PR head per `pull_request_read` at about 10:45Z and matches the body's `## Head` line. That section names both 1aec0e57 ("unchanged") and the merge b0762a639d under it. Both are on this head's history; it reads awkwardly but is not wrong.
- The live gate reading at this head (ev/gate_checkruns.txt, ev/gate_failures.txt, ev/workflow_runs.txt):
  - The 09:55:01Z failure (check run 131105882615, edit run 43195308518) logs `FAIL run(s) [43195308607] at this head are still being judged; their gate decides`. So did the 10:38:15Z failure (131126357137, edit run 43196595262).
  - Run 43195308607 is the `CI code` run. It has been `queued` since 09:52:29Z, and its gate check run 131129500777 is queued.
  - `merge_train.py classify ... --pr 3499` prints `WAIT 1aec0e57... pending: gate red: none` (rc 3) at three polls between 10:44Z and 10:49Z (ev/classify_polls.txt). That reading is right for this head: both failures are edit-run deferrals to a code run that has not finished, and nothing at this head has concluded the gate.
  - I did not wait the 30 minutes for CI, because this verdict is blocked on the tree, not on CI. No `pending-ci` line follows, since a blocked verdict needs no green.
- Red checks: `tests / nightly-status` is failure in the packet's digest. It is not in `merge_train.py owed-reds` (ev/owed_reds.txt), so it is neither answered nor a block. The deferral gate reds read WAIT, as above.
- Untouched: VERSION, the manifest, RELEASE_NOTES.md and both claim files are absent from the three-dot diff (ev/untouched.txt is empty).
- Not re-derived: `tools/pr/prepr.sh` rc 0, the live instances (#3479, #3454, #3442, #3465), and the body's figures measured at ba47446a8722. The body itself discloses them as not re-taken.
