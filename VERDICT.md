Fix review: merge ca0e06eb3d4650ba8bfad61195620f429c09f2eb

bus-nonce: 76fd235eb55184647e6eec105cee83d3
pending-ci: gate

## Scope

First round on PR #3598 (R10-START-COUNTER-EDGES). Full review of the group's production change from merge base d7004eaa775dd7b42aa392df0eb53aeec198b2b0 plus the repair handoff 092746903fd5e1139abc542cb7718b4a3a88c2f3, measured at head ca0e06eb3d4650ba8bfad61195620f429c09f2eb in a detached worktree. Role contract current: `git diff <merge-base>...origin/main -- dev/governance/roles/` touches only evaluator.md and orchestrator.md, not fix-review.md.

## Evidence

- Mutation proof (step 1): `PYTHONPATH=tests/hastub python3 dev/audit/harnesses/start_counter_edges_mutants.py` at the head: `BASELINE [(0, False), (0, False)]`, 22 mutants, all KILLED, `RESULT survived=0` (ev/mutants-head.txt). This matches the body.
- The five survivors from the pin drive, re-planted by me with `tools/audit/seat/mutant_run.py --spec` over the build's features.py block: `SURVIVED NULL`, then KILLED for running_signal.py:164 GUARD_OFF, :166 GUARD_OFF and thermal_model.py:1971/1972/1973 `>`→`>=` (ev/survivor5-mutants.txt). This matches the body's `## Unpinned sites`.
- My own mutants, beyond the fixer's set (ev/own-mutants.txt): replaying the restore queue before the stored counts are assigned, the frequency source not preferred, wear booked at now instead of the edge time, and a stop edge leaving `running` true were each KILLED by the build's block. Arming the timer after detach (`pending = sig.tracker.pending` without the `unsub` guard) survived the build's block but was KILLED by part A's block (ev/own-timer-after-detach-partA.txt). A whole-script features.py run in a git-archive copy printed `KILLED NULL` (the unmutated script fails in that copy), so it measured nothing and I rely on the block runs (ev/own-timer-after-detach-wholescript.txt).
- Null control and failing-first (steps 2–3): no finder harness exists (an outside report); the build's harness is disclosed as the fixer's own. I ran `dev/audit/harnesses/start_counter_edges.py` against a git-archive export of the merge base and at the head. Base / head: control 3/3, perturbed 3/4, restored 7/8, s7_60s 0/5, s7_30s 0/5 (ev/nullcontrol-base.txt, ev/nullcontrol-head.txt). Every figure matches the body. The control is flat, and the perturbation moves by exactly one.
- Claims (step 4): neither `tests/golden/claimed_drift.txt` nor `card_claimed_drift.txt` is in the three-dot diff. I did not re-run the golden drift: the body's `NO UNCLAIMED DRIFT` figure is taken at 0845038530 and is the fixer's, not re-derived here.
- Version (step 5): `VERSION`, `manifest.json` and `RELEASE_NOTES.md` are absent from the three-dot diff.
- Structure (step 14): `python3 tests/structure.py` at the head prints `STRUCTURE RATCHET PASSED` (ev/structure-head.txt). Three budget rows go down and none goes up: `class_excess_loc` 17453→17446, `max_class_loc` 7894→7887 and `coordinator_multiassigned_attrs` 106→105. The drops come from deleting `_observe_compressor_start` and moving the immersion predicate into `thermal_model.immersion_over`. No `*_budgets.json` raise.
- Range (brief item 3): the 3aea425ace..ca0e06eb3d delta is `tests/features.py` (+46, the two new checks) and 44 new `tests/mutation_ledger/killed_by/` rows. No production line changes there. The other commits are the group's own, the merges of main and the delivery row `dev/programme/delivery/3598.md`. Nothing widens into unrelated code.
- Merge (step 13): `git merge-tree --write-tree origin/main ca0e06eb3d` exits 0, so there is no conflict (ev/merge-tree.txt).
- Code read: `running_signal.attach` runs in `__init__` after `_init_grid` subscribes the counter, so no edge is published before a subscriber exists. `_async_load_ledger`'s `finally` restores on every exit, including `stored is None`. `StartCounter.fold` queues while unrestored, and `restore` assigns the stored counts before replaying the queue. `detach` clears the subscribers and reader that close over the weak key.
- Forward-carry (step 10): both `## Forward-carry` items appear verbatim in `dev/programme/rosters/wave-r10-groups.json` on origin/main and on `handoff/audit-r10-roster`. The running_now item is under R11-OUTSIDE-HONEST-STARTS-RUNS, and the S7 item is under R10-START-COUNTER-EDGES as a pending owner ruling, which is the fixer.md own-group exception.
- Red checks (step 11): owed-reds set in ev/owed-reds.txt; red history per commit from the check-runs API in ev/red-history.txt. Owed reds in the range:
  - `tests / mutation` failed at 3aea425ace and 563650387b.
  - `governance / policy-docs` was cancelled at 3aea425ace.
  - `gate`, the roll-up, was red at both.
  The body's `## Red checks` names `tests / mutation` and `governance / policy-docs` and gives the cheaper detector or the no-detector finding for each. I checked that the trigger was answered, not the answer. At the head, `governance / delivery-status` and `tests / nightly-status` are red, but neither is in the owed set.
- CI at this head: `merge_train.py classify ca0e06eb3d4650ba8bfad61195620f429c09f2eb --pr 3598` polled about every 70 s from 05:32 to 06:01 UTC (ev/classify.log), each run printing `WAIT ca0e06eb3d4650ba8bfad61195620f429c09f2eb pending: gate red: none`; the one check still in progress at 05:53 was `tests / mutation`. Returned with `pending-ci: gate` per the brief.

## Findings

- Residual: S7, an element cut-in on an averaging meter. The edge path counts a false start at 5 of 6 offsets (harness rows s7_60s and s7_30s: 0 at the base, 5 at the head, re-measured here). It is disclosed in the body and waits on the owner's choice between the residual and a refresh-held start. Carry: R10-START-COUNTER-EDGES
