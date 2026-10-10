MEASUREMENTS — fix review of PR #2113

HEAD MEASURED: 44b5c3e53295d5875c20d5582f9575398fd391d7
MERGE BASE:    7cd5a588cbbbef354c00148040da2d720b8a888c
REVIEWER:      hpo-approver seat, round 9 fix wave, group R9-RC-NIGHTLY-DEFER
WORKTREES:     /Users/timmalmstrom/hpo-seats/r9rev-2113/wt   (head, detached)
               /Users/timmalmstrom/hpo-seats/r9rev-2113/base (merge base, detached)
INTERPRETER:   /Users/timmalmstrom/.local/state/hpo/venv-ci/bin/python3 (3.14.7), PYTHONPATH=tests/hastub

Every line below is my own run, not the fixer's. The finder's/fixer's own logs
are at /Users/timmalmstrom/hpo-seats/nightly-defer/logs/ and were read, not trusted.

== RESULT: the two cited nights are real, and are the ones the body names ==

run 37108891698 (2026-10-03T08:11Z, schedule), job mutation-ledger -> failure
  line 747/749/773 of the job log:
    drivers in play: ... tests/harness_headers.py ... tests/stress.py ...
    null control: custom_components/heatpump_optimizer/__init__.py:42 NULL_COMMENT
    MUTATION TABLE REFUSED -- the null control ... was killed by
      tests/harness_headers.py (tools/audit/round4/D7/sysid_estimator_frontier.py
      exits 0  [rc=-24 stderr=]; ...)
  -> harness_headers.py SIGXCPU rc=-24, on the null control. CONFIRMED.

run 37189092011 (2026-10-04T08:29Z, schedule), job mutation-ledger -> failure
  line 862/864/889:
    null control: custom_components/heatpump_optimizer/accuracy.py:42 NULL_COMMENT
    MUTATION TABLE REFUSED -- ... killed by tests/stress.py (no scenario exceeds
      its own recorded cost by the budget factor  [summer/1z/dhw/fuse-cap at 8.0x
      its reference vs its own budget 7.9x (recorded 2.6x x 3)]; ...)
  -> stress.py's own cost budget, 8.0x against its own 7.9x. CONFIRMED.

Both nights the sibling lane `mutation-nightly` PASSED. So the arm is the
mutation-ledger lane, and the refusal is intermittent (machine load), not
deterministic.

== RESULT: the change itself, by my own harness over the tree's own functions ==
(harness-head.txt / harness-base.txt; python3 -I harness_2113.py <root>)

  scope_deferred("full")     head ('tests/harness_headers.py','tests/stress.py')
  scope_deferred("changed")  head ()
  files_losing_a_driver_OUTSIDE_the_drop   head []          base []
  files_losing_one_at_all                  head 75          base 0
  drivers unioned over the tree            head 26 -> 24    base 26 -> 26
  production files walked                  75 at both ends
  unpinned site(s)                         4617 at both ends (5983 candidates)
  ledger rows naming a deferred driver     4 at head, 5 at the merge base
  census_deferral_note("changed")          "" at head
  max_survivor_fraction                    {"changed":0.2,"full":0.3} at both ends
  last_measured full/changed               unchanged at both ends

  The four head rows, and who the fixer's RCA names:
    tests/stress.py           optimizer.py:HeatPumpOptimizer.get_current_action BOOLOP 519a7ed9
    tests/harness_headers.py  quiet_windows.py:overlap_problem RETURN_DEL da9e8e97
    tests/stress.py           thermal_model.py:ThermalModel.flow_lift_factor CLAMP_DROP bc44c8b4
    tests/stress.py           thermal_model.py:ThermalModel.simulate_trajectory_batch BOOLOP b5554584
  Identical sets. The census clause prints 4 and names both drivers.

== RESULT: the mutation proof, through the FULL closure (entities.py) ==
(mutation-proof-full-closure.txt; the fixer's own arms were SIGTERM'd at rc=143
and its body discloses the four predicates were driven directly instead)

  control, unmutated, head:            ALL 2254 ENTITY CHECKS PASSED
  M1, the drop loop deleted from main(): 1 of 2254 FAILED -- exactly
     "the full scope drops the EXCLUSIVE pair out of its net, ... and main()
      takes the drop from that rule". The other three arms stayed green.
  M2, SCOPE_DEFERRED = {}:             4 of 2254 FAILED, and the net walk
     printed "files losing one at all=0" and "26 -> 26" -- the vacuity arm.
  restored: 0 diff lines after each; the worktree ended with 0 changed lines.

== RESULT: the rest of the contract's checks ==
  VERSION 6.7.17, manifest 6.7.17, RELEASE_NOTES heading v6.7.17: untouched
    (git diff <merge base>...HEAD over all three is empty)
  claim files: byte-identical to the merge base (nothing claimed, none moved)
  merge-tree --write-tree origin/main HEAD: exit 0, no conflicting path,
    no MERGE-CLAIM marker at all (the claim files do not conflict)
  budget_raise_gate at the head (job 114236486119): "RESULT budget_raises=0
    count / PASS: no budget raise; no owner review is owed"
  arch_score at the head (job 114236486206): "dS +0.0000 NULL, no gate
    metric rose"
  .github/workflows/: 0 files touched in the range
  entities.py at the merge base: ALL 2250 ENTITY CHECKS PASSED (this is the
    figure the body's "was 2243" should be -- see the verdict)

== RESULT: the head's own checks, and the range's ==
  head 44b5c3e53 check-runs: no failure. closures, fast (3.14), mutation,
    closure-scope, pr-contract, budget-raise-gate, case 3.14: success;
    coverage in progress at the time of measurement; the rest skipped.
  the range 2320fa4c4..HEAD: no push event ran CI at all before the head --
    the only non-success results on 14b891508 are `cancelled` (superseded by
    the head's push). The fixer's own prepr log agrees: "skip ancestry reds --
    no pushed commit carries any check run".

== RESULT: the class probe (is the pair the whole class?) ==
  RLIMIT_CPU / setrlimit on a child, across tests/*.py: only
    tests/harness_headers.py.
  a driver comparing a measured duration against its own budget, across the
    27 non-pair drivers in the net: only tests/stress.py.
  tests/structure.py mentions tests/stress_budgets.json in a docstring only
    ("the idea applied to counts instead of timings"); tests/features.py's
    budget-file hits are fixture paths and comments.
  Empirical: on 10-03 the sibling lane mutation-nightly drove the SAME 22
    drivers on the SAME null-control site and reported "null control ... survived
    every driver" -> PASSED. So no driver in the net besides the pair refused it.

== RESULT: the drop's cost, measured on real nightly draws ==
  10-03 mutation-nightly, 40 mutants: features.py 23, finite_boundary 5,
    entities 5, manual_plan 1, config_flow_steps 1, survivors 4 of 39 = 10.3%.
    Zero kills by tests/stress.py or tests/harness_headers.py.
  10-04 mutation-nightly, 32 evaluated: features.py 15, entities 5,
    finite_boundary 3, structure 1, config_flow_steps 1, survivors 7 of 32 =
    21.9% against the 30% cap. Zero kills by the pair.
  Ledger-wide: 1260 killed_by rows; tests/harness_headers.py 1, tests/stress.py 3.
  Reach of the drop: tests/harness_headers.py's recorded closure contains ALL
    75 production modules (so it was a candidate driver for every site) and
    tests/stress.py's contains 23. Of the 4617 unpinned sites, 4617 lie in
    harness_headers.py's closure and 1772 in stress.py's.
  Origin of the 4 stranded rows: 2 were recorded by the nightly's own
    `--drain` lane (the lane that loses stress.py), 1 by `--pin-killed`, 1 by
    `--pin-killed` via the EG-B1 hand route out of tree.
