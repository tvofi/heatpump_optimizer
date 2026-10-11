Fix review: blocked 648f22d7ac57021b37da3556cf64677fc2141ece root-cause-unanswered: instrument-self-tests went red at two pushed heads (476dac6e0, f7d1bcf86) and stays red at this head; the body's Red checks names only budget-raise-gate and says "none further"
bus-nonce: 70ff01ee8a3f80419a909795d78e4d3a

Measured at detached worktree /Users/timmalmstrom/hpo-seats/r9rev-2132/wt, head
648f22d7ac57021b37da3556cf64677fc2141ece (branch fix/r9-ci-consolidation-ratchet,
merge-base e1501bf48, authored-code head 476dac6e0, row head f7d1bcf86).

## The block

- RESULT instrument-self-tests: RED, unanswered. `budget_raise_gate.py --self-test`
  fails exactly twice, on this PR's own new file:
  `FAIL tests/ci_budgets.json: has a schema: got False, want True` and
  `FAIL tests/ci_budgets.json: carries at least one cap the gate reads`. The
  gate's SCHEMA (tools/policy/budget_raise_gate.py:131-170) knows six
  *_budgets.json paths; a seventh tracked file was added without an entry.
  Reproduced by me locally at the head (211 checks, 2 failed) and read from
  check-runs at both earlier heads (jobs 114432813361, 114433418482).
- RESULT pr-contract: RED at f7d1bcf86 -- its own red-history step lists
  instrument-self-tests and the body does not name it (job 114433926227:
  "check 'instrument-self-tests' is red and '## Red checks' does not name it").
- The body's Red checks section is not merely silent, it asserts the opposite
  ("none further named as expected-red at the head"). Per defect-root-cause.md's
  second trigger the body owes the cheaper detector or the finding that none
  exists. Note the honest repair is not only a body sentence: registering the
  schema changes what budget-raise-gate reads (today the schema-less file is
  all-frozen, which is what made the disclosed 22 "raises"), so the fixer/root-cause
  seat should decide schema-vs-answer deliberately; that is the owner-adjacent
  judgement the class exists to dispatch.

## What survives (measured, so the repair round stays narrow)

- RESULT C2 fail-closed: all arms re-record. Other-tree manifest rc=1; corrupt
  recording rc=1; roster missing one selectable script rc=1; artifact absent
  rc=1 (workflow-side: lookup miss exits 0 with PROOF_CONSUMED=false -> full
  re-record); only a full-roster artifact on this run's own tree consumes
  (rc=0, 33 scripts). No arm proceeds on doubt.
- RESULT C1: local mechanism verified -- composed (COVERAGE_PROCESS_START) vs
  bare recording of tests/layout.py: files/inert_reads identical, rc 0 both,
  argv equal, 'how' marker distinguishes (my own instrument, macOS,
  non-authoritative). The Linux byte-identity proof is PROMISED, not run:
  composed-proof is 'cancelled' at 476dac6e0 and no completed run exists --
  it must run green before merge reliance, but it is the branch's own gate,
  not a defect.
- RESULT ratchet: not gamed by hand-transcription -- inputs are runner-emitted
  .tsv lines carrying event and run id; --record never passed by any job
  (pinned); one-way; a derived metric with no budget row is itself a growth;
  any value change in ci_budgets.json hits budget-raise-gate as a raise (the
  owner's, rule 2). Mutant 'if cur > budget: -> if False:' kills entities.py's
  named pin (1 of 2259); the two closure.py mutants each kill their named
  selftest pin. Null controls: selftest 74/74, structure PASSED, entities
  rc=0 ALL 2259 PASSED (body's 2258 predates the merge commit's main-side checks).
- RESULT initial values: all 17 archscore rows equal vector.measure exactly at
  this tree; 33 selectable + 20 coverage-fast (exact DERIVED pipeline) = 53;
  61.0 consistent with the p75-at-record rule (today's window 44.2/54.2/58.7/
  60.2 stays green). Body miscounts "16 archscore rows" (17) -- cosmetic.
- RESULT write set: 13 files; every new tracked file classified (entities
  green); no existing *_budgets.json touched or raised; custom_components
  untouched; VERSION/notes untouched; claim files byte-identical (absent from
  the diff). budget-raise-gate red at the head is disclosed and is the owner's.
- RESULT rule 1 end-to-end: no path found where a wrong closure survives
  beyond one merge. C2 keys on this run's own HEAD^{tree} by artifact name,
  refuses to re-record on every doubt, and the under-approximation check runs
  FULL (no --partial on push) on whatever recordings are consumed; C1 executes
  the script once per event and stores nothing across trees; a composed read
  set smaller than the committed table reddens the closures check.
- Forward-carry note (not the block): the 53->52 tightening's destination
  (wave-3l-groups.json resume) is named in the body but not edited, and the
  pre-study doc is on neither origin/main nor this branch (handoff 488aca6e1
  only) -- the orchestrator should carry it when the roster is next touched.
