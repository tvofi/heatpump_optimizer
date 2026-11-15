Fix review: blocked 680f34d3d275ec45143a7f30b8cf7953c73e6911 class-open: main push run 43675609284 at this PR's merge base 946eb6d255 prints 10 UNDER-SCOPED seat_gen misses the head's table still lacks

bus-nonce: 48215205c2481fb1a589704b3d8b4964

Round: first. Measured head 680f34d3d275ec45143a7f30b8cf7953c73e6911 (the PR's head.sha at review time, ev/pr-body.txt line 1). Merge base 946eb6d2551d9968de258bc47ee27efa10e7b3ea.

## Block

The PR's goal is to clear main's `governance / instrument-self-tests` step "Refuse a self-test read set the committed table misses". The enumeration rule is `selftest_scope.drift` against the newest Linux push run on main. That run now exists for this PR's own merge base: CI run 43675609284 at 946eb6d255, job 132695944383, failure, `selftest_scope check: 117 gated step(s), 14 refusal(s)`, artifact 14146974190. Replaying `drift(table, artifact["steps"], workflow_steps(root))` with that artifact (ev/drift-replay-946eb6d.txt): the merge-base table refuses 14 lines and the head's table refuses 10. The PR's 4 are gone. These 10 remain: `UNDER-SCOPED ... files misses tools/audit/seat/seat_gen.py[, seat_gen_selftest.py]` in field-coverage, selftest-wiring, roster-queue-runner, outside-contract, beat-job-rows, hooks-setup, merge-train, open-pr, pr-args and update-pr. #3491 introduced them (seat_gen), and run 43660322841 could not measure them. So merging this head leaves main red on the same step.

The body's sentence on newer merges names no measured miss; these 10 are measured now. The repair is cheap and has the same method: artifact 14146974190's table contains every entry of the head's table (ev/art-946-vs-head.txt: `head entries not in run-43675609284 artifact: []`). It carries seat-gen measured, identical to the carried-over block (`seat-gen head == run measurement: True`). It refuses nothing against its own measurement (`artifact vs its own measurement: []`). Re-cut: commit that artifact's table (Linux CI, not macOS traces), then re-run the null-control replay against it.

## Findings

- Body figure misstated: `python3 -I tools/ci/selftest_scope.py --self-test` prints `selftest_scope self-test: 120 checks, 0 failed` at the head and at the code head 2dbc55d42b. The body says `110 checks`. selftest_scope.py is byte-identical at both. The verdict does not depend on it (0 failed either way); correct it in the re-cut's body. Carry: dismissed: body figure corrected by the re-cut this block requires, not a later stage's

## Evidence

- Brief check (1): the three-dot diff touches only tools/ci/selftest_closures.json and dev/programme/delivery/3606.md. No expectation or code is touched.
- Brief check (2): the head table equals run 43660322841's selftest-closures artifact (id 14141587820, head 2a257fce0895, push, main) on every step but seat-gen. It also equals the set-union of the merge-base table and that artifact per list field; probe lists keep duplicates that the artifact also has. Nothing was removed, no run_sha changed, and the top-level keys are equal (ev/table-compare.txt). Added: 3 dirs each in dependency-graph-census and prepr, 1 probe in policy-lint-mutants, 2 probes in temp-or-machine-path. That matches the body's figure.
- Brief check (3), null control re-run (ev/drift-replay.txt): with run 43660322841's artifact, the merge-base table gives the 4 UNDER-SCOPED lines plus `UNMEASURED step seat-gen`. The head table gives only `UNMEASURED step seat-gen`. This matches the body.
- Targeted mutants (ev/mutants.txt): removing each of 6 added entries from the head table brings back its UNDER-SCOPED line. Result: 6/6 killed.
- Brief check (4): the seat-gen block at the head equals main's (ev/table-compare.txt `seat-gen head==mb: True`). It only moves to its sorted position. It also equals run 43675609284's own measurement of seat-gen.
- `selftest_scope static` at head: `117 gated step(s), 0 problem(s)`, matching the body (ev/selftest.txt).
- Merge: `git merge-tree --write-tree origin/main 680f34d3d275ec45143a7f30b8cf7953c73e6911` at origin/main 2d0b1c7594 gives rc=0 (ev/merge-tree.txt). Main's table is unchanged from 946eb6d255 to 2d0b1c7594.
- VERSION, manifest and notes heading: untouched (not in the diff).
- CI: `merge_train.py classify 680f34d3d275ec45143a7f30b8cf7953c73e6911 --pr 3606` printed `WAIT 680f34d3d275ec45143a7f30b8cf7953c73e6911 pending: gate red: none` twice (ev/classify-1.txt, ev/classify-2.txt). I did not wait further because the block does not depend on CI. Failed runs at the head are `gate` (in the owed set, but classify reads it pending with no red), `governance / delivery-status` and `tests / nightly-status`. The last two are outside `merge_train.py owed-reds` (ev/owed-reds.txt), so nothing is owed for them.
- No finder's harness is committed for this class. The drift replays here are my own script calling `selftest_scope.drift` (the builder's, not the finder's).
- Forward-carry: the body names R11-INTAKE-R10-RESIDUE on handoff/audit-r10-roster 89acffb1ab. The review packet's carry_audit routes it (1 routed, 0 unrouted). The block does not turn on it.
