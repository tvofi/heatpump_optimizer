R10-HOTFIX-MAIN-SELFTEST-SCOPE: union main's traced self-test read sets into tools/ci/selftest_closures.json

Main is red on `governance / instrument-self-tests`, step "Refuse a self-test read set the committed table misses", on every push since f7e7a0244a (#3573). The last green run of that step is 43553916206 at 0f37833e21 (#3547). At origin/main 9fdba3b854 (run 43611495159, job 132497640978) it prints `selftest_scope check: 114 gated step(s), 11 refusal(s)`, every one an UNDER-SCOPED line. Five merges added the reads. The first run that refuses each one names the merge:

- #3573 (f7e7a0244a): pr-merger misses `tools/audit/seat/proof_watch.py`; ci-prelude and gate-predicate miss `tools/ci/fixtures/gate_requeued_needs_runs.json`.
- #3544 (a77d71fb75): verdict-bus misses `dev/governance/roles/fixer.md`.
- #3584 (1791869fdb): gate-sweep misses `tools/ci/gate.py`, `tools/ci/ghapi.py`, `tools/ci/prelude.py`, and the probe `tools`.
- #3567 (5e3274a19f), which adds the tracked directory `dev/audit/rounds/round10/user-text`: policy-lint-mutants (probe `.gitattributes` there), dependency-graph-census and prepr (dirs).
- #3565 (6b61e47cc2): beat-job-rows misses 371 files and 46 dirs.

The repair is the one `tools/ci/selftest_scope.py` states: commit the table the drift step itself writes. Two traced push runs each uploaded a `selftest-closures` artifact. Each artifact is the committed table unioned with that run's measurement: 43607468927 at 6b61e47cc2, and 43611495159 at origin/main 9fdba3b854. Both are folded into the table with the instrument's own `union_entries` and written by its `write_table`. Nothing is edited by hand, and the check is not touched. The fold is `union.py`: it loads the committed table, unions each artifact's `steps` over it with `selftest_scope.union_entries`, and writes the result with `selftest_scope.write_table`. No entry loses a read. A per-step comparison of the old table against the new one, using `selftest_scope.covers`, finds two items gone. Both are beat-job-rows probes, `tools/audit` and `tools/audit/seat`. `write_table`'s `compact_probes` folds them into directories the step now lists (`tools`, `tools/audit`, `tools/audit/seat`). `drift` excuses a probe under a listed directory, so the fold does not change what main refuses.

What a PR run proves here, and what it does not: `SELFTEST_TRACE` is set only on `push` (governance.yml, the job's `env`). So a pull-request run never traces and never runs the drift step, and no PR run can show this repair green. This change touches a `GATE_FILES` member (the table), so the PR's instrument-self-tests run is FULL. It proves every step still passes, that `static` finds the table consistent and not stale against the workflow, and that the scope self-test passes. Only the first push to main after the merge proves the drift step green. Until then, the proof below replays the traced step's own comparison (`selftest_scope.drift`) with each run's CI-measured artifact as the measurement. The function documents that the compacted artifact and the live fold refuse the same lines. On origin/main's table, the replay reproduces the CI step's 11 refusals line for line.

## Head

2b8893814da8e6cf0a5fd8b33c05d849f2717d45, measured against origin/main 9fdba3b854 at 2026-11-14T16:41Z (`date -u`).

## Mutation proof

n/a: no production line changes. The diff is the measured table alone. The table's role in the check is shown both ways under Null control: the origin/main table refuses 11 lines and the head's table refuses none, over the same measurement.

## Null control

The unmodified tree, origin/main 9fdba3b854. Replaying `selftest_scope.drift` with run 43607468927's artifact as the measurement prints `replay: 114 gated step(s), 11 refusal(s)`. These are the same 11 UNDER-SCOPED lines that CI job 132485295279 printed. The CI step at the same tree (run 43611495159, job 132497640978) prints `selftest_scope check: 114 gated step(s), 11 refusal(s)`. At the head, the same replay with either run's artifact prints `replay: 114 gated step(s), 0 refusal(s), 0 note(s)`.

## Figures

<!-- figure-block: scope-line mb=9fdba3b8547f9762438dc19b98b310a63d34dcb1 head=2b8893814da8e6cf0a5fd8b33c05d849f2717d45 -->
~~~text
MODE: FULL -- every test script runs, nothing is scoped out.
~~~
<!-- /figure-block -->
- Drift refusals, origin/main table: 11, from `python3 -I replay.py <origin/main checkout> art-43607468927/selftest_closures.json`. `replay.py` loads the checkout's table and calls `selftest_scope.drift(table, artifact["steps"], workflow_steps(root))`. The CI step at the same tree printed 11 (job 132497640978).
- Drift refusals, head table: 0 for each artifact, from the same command at the head, run once with `art-43607468927` and once with `art-43611495159`.
- `python3 -I tools/ci/selftest_scope.py static` at the head: `114 gated step(s), 0 problem(s)`.
- `python3 -I tools/ci/selftest_scope.py --self-test` at the head: `110 checks, 0 failed`.
- `python3 tests/structure.py` at the head: `STRUCTURE RATCHET PASSED`.
- Gate scope: `python3 tests/closure.py select --diff $(git merge-base origin/main HEAD)` prints `MODE: FULL` (the table is a gate file). CI runs it.
- Items removed by the re-record: 2 probes, both beat-job-rows probes folded by `compact_probes` into dirs the step lists. Source: a per-step comparison of `git show HEAD~1:tools/ci/selftest_closures.json` against the head's table under `selftest_scope.covers`. The null control is that same comparison counting the 371 files and 46 dirs the head adds as additions, not drops.

## Red checks

- `governance / instrument-self-tests` (main push runs 43603039666, 43607468927, 43611495159, and every main push run since 43556918153), step "Refuse a self-test read set the committed table misses". It fails with 11 UNDER-SCOPED refusals and is repaired by this diff. Root-cause answer: the cheaper detector is to trace each pull request's selected self-test steps and run `check` over the steps that ran. The PR job already runs those steps through `tools/ci/selftest_step.sh`, but `SELFTEST_TRACE` is push-only. Its standing cost is strace overhead on every PR's selected steps, up to one traced 60-minute run per PR that selects many steps, as R10-RCA-MAIN-SELFTESTS-RED section 2d priced it. Its alternative, countermeasure A of that RCA (main commits the measured table mechanically), is ruled to round 11. Section 2d recorded "the record stands until a second instance". This red is at least the fourth instance (R10-HOTFIX-MAIN-SELFTESTS, R10-HOTFIX-MAIN-IST-READSET-2, R10-HOTFIX-SELFTEST-SCOPE-RERECORD, this one). The analysis belongs to the root-cause seat beside this fix, not to this PR.
- `tests / ci-ratchet` (main push runs 43603039666 through 43607708534) is not this diff's red, and this diff does not repair it. On a push it is report-only by design: the owner's 2026-11-11 ruling was built by #3500 (merge cbe8d93bd8) as `PUSH_REPORT_ONLY` in `tools/ci/gate.py`. Main's `gate` job succeeds in the same runs where ci-ratchet fails, as the ruling specifies. This red prints `ci-ratchet: CI push run 43602217369 has no completed `tests / *` job (fail closed)`. Run 43602217369 (97a3a921e0, #3570) was cancelled at `prelude` with every `tests / *` job skipped. `tests/ci_ratchet.py` `_walk` returns None for a run with a cancelled `tests / *` job, but refuses a completed run whose `tests / *` jobs never ran. It is not a budget overrun. That walk belongs to the live group R10-HOTFIX-CI-RATCHET-SKIPPED-RUN. Carry: R10-HOTFIX-CI-RATCHET-SKIPPED-RUN

## Forward-carry

- beat-job-rows now records 371 files and 46 dirs, nearly the whole `tools/` and `.github/workflows/` tree. The cause is #3565's self-test check "the wired set is the real tree's seat self-tests". It calls `beat_jobs.darwin_instruments(<repo root>)`, so `selftest_wiring.self_testing` walks all of `tools/`. This re-record records that read set as-is, because the measurement is the authority, and does not bless it. The step will now run on nearly every pull request that touches `tools/` or a workflow. A hermetic fixture tree would let the step scope again. No live roster group owns `tools/audit/seat/beat_jobs*.py` (R10-BEAT-JOB-TABLE and R10-HOTFIX-MACOS-SELFTEST-LANE are done), so it is reported to the orchestrator for routing. Carry: R10-HOTFIX-MACOS-SELFTEST-LANE | dismissed: deliberate real-tree wiring check recorded as measured, the routing of a hermetic fixture is the orchestrator's
- Open PR #3551 (R10-SELFTEST-SCOPE-UNION-GUARD) also edits `tools/ci/selftest_closures.json`. Whichever lands second re-unions with `union_entries` over the other's table. #3551's shrink guard should treat a `compact_probes` fold, a probe dropped because a listed ancestor directory answers it, as no drop: this re-record contains two such folds. Carry: R10-SELFTEST-SCOPE-UNION-GUARD

## Friction

none
