R10-HOTFIX-SELFTEST-SCOPE-RERECORD (part 3): self-test scope re-record from main's run

Main is red on `governance / instrument-self-tests`, step "Refuse a self-test read set the committed table misses". Push run 43660322841 (head 2a257fce08, the newest completed CI run on main when this was cut; runs 43674107312, 43674063124 and 43674024407 were still in progress and carry no `selftest-closures` artifact) prints:

- UNDER-SCOPED step policy-lint-mutants: probes misses dev/programme/round10/state/.gitattributes
- UNDER-SCOPED step dependency-graph-census and prepr: dirs miss dev/programme/round10/state and the tests/mutation_ledger/{killed_by,survivor_triage}/whatif.py directories
- UNDER-SCOPED step temp-or-machine-path: probes miss the two whatif.py/.gitattributes paths
- `selftest_scope check: 116 gated step(s), 4 refusal(s)`

Cause: #3601 added dev/programme/round10/state and #3481 added the whatif.py mutation-ledger directories, which the committed table did not list. Third instance of this repair after #3589 and #3595; the method is #3595's: commit the table the drift step wrote (that run's `selftest-closures` artifact, the committed table unioned with the Linux run's measurement). Never macOS traces.

One addition beyond the artifact: the artifact lacks the `seat-gen` step (added by #3491 after 2a257fce08, so that run could not measure it), so main's `seat-gen` entry is carried over unchanged. Newer merges since 2a257fce08 may add further misses; the next push run to main shows it.

## Head

Code head 2dbc55d42b8c9834bad04b57f87d2fc8c4795c0d, one commit on origin/main 2c69fb3560.

## Mutation proof

n/a: no production line changes; the diff is the measured table alone. The table's role is shown both ways under Null control.

## Null control

Replaying `selftest_scope.drift(table, artifact["steps"], workflow_steps(root))` with run 43660322841's artifact as the measurement: against origin/main's table it refuses the same 4 lines CI printed (plus `UNMEASURED step seat-gen`, because the artifact predates that step); against the head's table the 4 are gone and only the `seat-gen` UNMEASURED line remains, an artifact limit and not a table gap. The artifact holds the table, not the raw traces, so `check --traces` cannot be run here.

## Figures

- Added paths: 3 dirs in each of dependency-graph-census and prepr, 1 probe in policy-lint-mutants, 2 probes in temp-or-machine-path; removed or changed: 0 (recursive list compare against origin/main's table; the `seat-gen` block only moves to sorted position).
- `python3 -I tools/ci/selftest_scope.py --self-test` at the head: `selftest_scope self-test: 110 checks, 0 failed`.
- `python3 -I tools/ci/selftest_scope.py static` at the head: `117 gated step(s), 0 problem(s)`.
- Scope: the table is a gate file, so CI runs FULL.

## Red checks

- `governance / instrument-self-tests`, step "Refuse a self-test read set the committed table misses" (main push run 43660322841, job 132648380279): 4 UNDER-SCOPED refusals; repaired by this diff. Root-cause answer: this is the third instance of the class. The cheaper detector is already ruled: loop-study card L9 (class barrier, built at round 11 start), whose predecessor is group R10-SELFTEST-SCOPE-UNION-GUARD / PR #3551. The countermeasure is recorded, not rebuilt here; its standing cost is the push-only trace, since `SELFTEST_TRACE` is set only on push and a PR that adds a read cannot see this red.

## Forward-carry

- The class barrier (L9) and the mechanical main-side union of the measured table, so a PR that adds an instrument read never leaves main red (lands in `tools/ci/selftest_scope.py`, routed by `dev/programme/rosters/wave-r10-groups.json`, stage R11-INTAKE-R10-RESIDUE, on origin/handoff/audit-r10-roster at 89acffb1abf6276cc58d18b36907aa81f0b8b20d). Carry: R11-INTAKE-R10-RESIDUE

## Friction

none
