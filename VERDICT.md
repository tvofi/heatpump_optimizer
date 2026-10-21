Fix review: blocked 38ec7c60f5d536580a0deddf6c0342a1862f34e6 ci-red: the head fails its own widened wiring check -- tools/pr/gate_priority.py (from main 131f81957, merged in at 4f93c3a20) is a self-testing file under tools/ with no workflow step, so selftest_wiring --check reads 71 self-testing, 70 wired, 1 unwired and instrument-self-tests is red

Round: first review of this head (the fixer's round 3 body). Measured head 38ec7c60f5d536580a0deddf6c0342a1862f34e6; still the PR head and the ref tip when this verdict was written.

## The blocker

- `python3 -I tools/audit/seat/selftest_wiring.py --check` at 38ec7c60f5d536580a0deddf6c0342a1862f34e6 -> `UNWIRED tools/pr/gate_priority.py: no workflow run line names its self-test`, `selftest_wiring: 71 self-testing, 70 wired, 1 unwired`, rc=1 (ev/wiring.txt).
- At the authored code head 7dfec2f6b the same command reads `70 self-testing, 70 wired, 0 unwired` and gate_priority.py does not exist (ev/wiring_at_code_head.txt). The body's figure was true there. The orchestrator's merge of origin/main 6961f0663 (4f93c3a20) brought in `tools/pr/gate_priority.py` (added by 131f81957), which has a `--self-test` (line 6). The rule this PR widens to all of tools/ correctly names it.
- CI agrees: check run 119172833239 `instrument-self-tests` concluded **failure**, and its failed step is "Refuse a self-testing seat instrument that no step runs" (ev/ci_instrument_self_tests_annotations.txt). The finder's harness agrees too: `dev/audit/harnesses/r10_seat_selftests_mutants.py` M0 at the head reads `M0 rc=1 ... selftest_wiring: 71 self-testing, 70 wired, 1 unwired` (ev/mutants_harness_head.txt; I stopped the run after S02 once M0 was red, so it is partial).
- Merged with the current origin/main 9e2f6ed9d (merge-tree is clean), the result is the same: 71/70/1 (ev/wiring_merged_with_main_9e2f6ed.txt).
- The fix is small and in scope. Add `python3 -I tools/pr/gate_priority.py --self-test` to the "self-tests outside tools/audit/seat/" step after `offline_spy.py` clears it. At this head it is offline-clean on my side: `gate_priority self-test: 12 checks, 0 failed`, rc=0. Then re-take the 70/70/0 figure as 71/71/0.
- This is a semantic conflict with main, not a fault in the authored code. Every later main merge into this branch has the same exposure, so the fixer should re-run `--check` after each merge (fixer.md steps 2-8 re-execute after a merge).

## What I verified (all at 38ec7c60f5d536580a0deddf6c0342a1862f34e6 unless stated; Linux, bash 5.2.21, Python 3.11.17, node 22)

RESULT selftest_wiring_check unwired=1 (tools/pr/gate_priority.py) rc=1
RESULT agreement_py_selftest checks=7 failed=0 rc=0
RESULT agreement_py_restore closure=13 covered=13 missing=0 rc=0
RESULT handoff_push_selftest delivery_row=5/0 handoff_push=2/0 rc=0
RESULT merge_pr_selftest checks=14 failed=0 rc=0
RESULT row_files_replay_selftest rc=0
RESULT merge_tree origin/main=9e2f6ed9d rc=0 (no conflict)
RESULT structure STRUCTURE RATCHET PASSED

Mutation proofs (ev/mutations.txt). Each was planted in my worktree and restored, and `git status` was clean afterwards:
- M1: `if restore_check(root, reader):` -> `if False:` gives agreement_py --self-test `7 checks, 1 failed` (the --out arm). KILLED. Matches the body.
- M2: the `tests/delivery_status.py` pathspec at line 926 deleted gives `--out` rc=1, `UNRESTORED tests/delivery_status.py`, `13 ..., 12 covered, 1 missing`, and no JSON written. KILLED. Matches the body.
- M2b: the `tools/release/stamp.py` pathspec deleted gives `--restore` rc=1, `UNRESTORED tools/release/stamp.py`. KILLED.
- S31, S32 and S33 (handoff_push's three push lines -> `true`) each give `handoff_push self-test: 2 checks, 1 failed`, rc=1. S34 (merge line -> `exit 0`) gives `merge_pr self-test: 14 checks, 2 failed`, rc=1. All four KILLED. These match the body and #2444's carry: those mutants now give rc=1 where the carry's precondition was rc=0.
- The counter (which the body could not prove on bash 3.2): `i=0` reverted to a bare `i` under bash 5.2 gives `handoff_push.sh: line 55: i: unbound variable`, rc=1. Restored, rc=0. So the round-3 fix is proven on bash 5.
- D: in row_files_replay, `hist` replaced by the tip gives `FAIL: no commit on ...'s history still resolves at the old plan path`, rc=1. KILLED.

The restore derivation, checked against runtime. My own instrument is ev/runtime_loads.py, so this is not the finder's harness. It runs agreement_py --out in-process and lists every repository .py file loaded through sys.modules: delivery_status, layout, structure, d11lib, merge_train, budget_raise_gate, stamp (ev/runtime_loads.txt). Every one of these is in the static closure() (ev/closure.txt: 13 files). closure() is therefore a superset at this head. governance_cost.py is loaded through spec_from_file_location and is caught by the locate() arm.

The finder's carry loop (#2444's control rule, ev/carry_loop_{base,head}.txt) at the merge base 6961f0663 prints 24 wired and 9 unwired. The 9 are the carry's 7 plus tools/plan/replan.py and tools/pr/gate_priority.py, which main added since; the carry's re-measure clause applies. At the head it prints 33 wired and 1 unwired, gate_priority.py, the same file as the blocker. The PR wires replan.py (the body says so) but not gate_priority.py.

Carry check (step 10): all seven `Carry: R10-CI-LAYOUT` lines in the body (five forward-carry and two friction) are on the R10-CI-LAYOUT group's `carry` list at handoff/audit-r10-roster 05b3bd68f (ev/roster-groups-05b3bd68.json).

Not touched: VERSION, the manifest, RELEASE_NOTES.md, tests/golden and both claim files are outside the diff (step 5). Roles directory: `git diff $(merge-base)...origin/main -- dev/governance/roles/` is empty.

## CI on this head (check-runs API, ev/check_runs.tsv)

- `instrument-self-tests` **failure**: the blocker above. The body does not answer it because the red arose with the main merge, after the body was written.
- `nightly-status` failure: it grades main. The body names it and answers it (the slow lane's replay cap), and this diff does not touch tests.yml. It is not this PR's red.
- `fast (3.14)`, `coverage` and `Analyze (python)` were still running when I wrote this. The rest are green or skipped.

## Not verified / disclosed

- I did not re-run the gate (FULL by item E), the mutation table or entities.py (2033.6 s recorded). Those are CI's heavy runs.
- tests/closures.json's `tests/entities.py` seconds moved from 670.4 to 2033.6. That is a recording, not a budget, and I did not judge it.
- The entities closure also gains `tools/audit/seat/selftest_wiring.py`, which item E's prose (three modules) does not name. It over-selects only.
- The #2423 carry asks for "a planted divergence in one of [stamp.py, delivery_status.py] that turns the job red". The body proves the precondition with a missing pathspec (M2) instead. I accept that as the derived-list control. The base-side lane enforcement waits for the next PR, as carried.
- The finder harness run is partial (see above).

bus-nonce: 753fbd51dfffbae90431ade82369497b
