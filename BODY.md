R11-HOTFIX-INSTRUMENT-SELFTESTS: commit the absorb bot's table for main's self-test drift red

Hotfix for a red main: push run 44913478338 at e698fc8ac3, job `governance / instrument-self-tests` (136874174276). The failing step is "Refuse a self-test read set the committed table misses": `selftest_scope check: 127 gated step(s), 7 refusal(s)`, every refusal `UNDER-SCOPED`. In that run every self-test passed, including prepr's `reds_arm refuses a body that leaves an ancestry red unanswered (P351)`. The local prepr self-test failure in the dispatch is therefore environmental (no token for the ancestry read), not CI's red.

Cause, from the drift output of each red push since the table was last written:
- **#3708 (6d7d52709f)** is red at its own merge commit, with 4 refusals (job 136559042272). The steps policy-lint-mutants, dependency-graph-census and prepr miss `dev/audit/rounds/round11/**` directories (present since #3723), and roster-library misses `dev/governance/dimensions`. The same 4 stand in jobs 136601192942 and 136822627720.
- **#3711 (b486fe58fd)** adds 3 more (job 136867174737). regret-oracle misses `room_history.py` and `room_record.py`. self-tests-outside-seat and temp-or-machine-path miss their `tests/mutation_ledger/{killed_by,survivor_triage}/room_*.py` directories.

The only file changed is `tools/ci/selftest_closures.json`. It is `python3 -I tools/ci/selftest_scope.py absorb --from <run 44913478338 selftest-closures artifact> --out ...` run at this branch's base. That output is byte-identical (`cmp`) to the run's own `selftest-absorbed` artifact, which the workflow leaves for a seat to commit (governance.yml, step "Absorb the drift step's measured reads into this head's table"). It adds 738 reads to 7 steps. Three roster-library probes, `dev/governance/dimensions/{D12,D3,D99}.md`, are folded by `compact_probes` into the directory entry the step now holds. No run_sha changes.

## Head

`c76347bdb50cb5f2dcf4d9edc8e69dc307aeeee5`, measured on origin/main `e698fc8ac374a1d72c230b55d938d75b03b7de67` (merge base) at 2026-11-21T16:04:57Z.

## Mutation proof

n/a: a data-file record from the instrument's own generator; neither the instrument nor its self-test is touched. Each read removed from the table brings back its own UNDER-SCOPED line in the null control below (that function is the one CI's step calls).

## Null control

`selftest_scope.drift(table, steps of the run's selftest-closures artifact, workflow_steps())`, run against the artifact:
- with origin/main's table it returns exactly the 7 UNDER-SCOPED refusals CI printed;
- with this branch's table it returns 0.

`python3 -I tools/ci/selftest_scope.py static` gives 127 gated steps and 0 problems. `python3 -I tools/ci/selftest_scope.py --self-test` gives 165 checks and 0 failed.

prepr: hotfix mode, `PREPR_SKIP_CODE=1 PREPR_SKIP_CLOSURES=1`. CI is the authority.

## Figures

none

## Red checks

governance / instrument-self-tests on main: step "Refuse a self-test read set the committed table misses" (7 UNDER-SCOPED at run 44913478338). No cheaper detector exists. dev/audit/rca/R11-RCA-SELFTEST-TABLE-DRIFT.md measured and rejected each PR-time detector:
- a static scan: 21% recall at about 22 false flags a merge;
- a precheck: at most 33% recall;
- a PR-time trace: about +35 minutes per FULL job.

The countermeasure it passed is the main-side absorb (C5). Its commit stays a seat's under the owner's 2026-11-18 ruling on D1/D2, option (b), and this PR is that commit. Carry: R11-RCA-SELFTEST-TABLE-DRIFT

## Forward-carry

none

## Friction

none
