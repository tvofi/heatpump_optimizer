Hotfix. Main's push-only step "Refuse a self-test read set the committed table misses" of `governance / instrument-self-tests` is red (job 136902224642, run 44922703115 at a8efe1d1c2, #3830's merge): `selftest_scope check: 127 gated step(s), 7 refusal(s)`, all UNDER-SCOPED. This commits that run's own `selftest-absorbed` artifact to `tools/ci/selftest_closures.json`; only that file changes.

None of the five most recent merges (#3830, #3810, #3808, #3708, #3736) introduced a refusal: the same step was red on every concluded main push back to at least run 44501970677 (cb8edb65a5, 2026-11-19 10:02Z). The step went red when a read was added, and nobody committed the artifact. Each refusal by the merge that added the read (`git log origin/main --first-parent --diff-filter=A -- <path>`; the per-run drift lines from runs 44501970677, 44567897866, 44677469341, 44798542157, 44813755126, 44826216706, 44911122597, 44913478338, 44922703115):
- #3723 (8fa10e00ce), the `dev/audit/rounds/round11/D*/` evidence tree: policy-lint-mutants (probes), dependency-graph-census and prepr (dirs). These were red in the oldest run read.
- #3739 (e893cd3d1e, first red in run 44567897866), `dev/governance/dimensions`: roster-library (dirs).
- #3711 (b486fe58fd, first red in run 44911122597), `room_history.py` and `room_record.py`: regret-oracle (files). Their `tests/mutation_ledger/{killed_by,survivor_triage}/` directories: self-tests-outside-seat (dirs) and temp-or-machine-path (probes).
- The currency.py reads in run 44501970677 were committed by 912b87c035 and are absent in later runs.

## Head
`dd2f26e749d54d7295dc2873a601487ce59367a4` is this PR's head. It re-absorbs: main's push run 44957362163 at 4ebd430fbf refused 11 steps, not the 7 this table covered (the other 4, verdict-bus, review-packet, roster-sync-reconciler and ci-predictor, each miss `dev/programme/rosters/wave-r11-groups.json`). The table is now the `selftest-absorbed` artifact of that run, 802 reads over 11 steps, a superset of the earlier 738 (0 reads of the earlier table are absent). The commit over the reviewed head 35bb34b2a3 changes `tools/ci/selftest_closures.json` only (+64). Where the text below says 7 steps and 738 reads, it describes the reviewed head.

25238b470a1440782336d164789f09ddecf144d0 on origin/main a8efe1d1c2a8f1e0b44cdf1046a0ea4ca2155a3b (fetched 2026-11-21, unmoved at handoff).

## Mutation proof
n/a: a data-only change to a measured table, with no predicate edited. The refusing check is `selftest_scope.drift`, which is red on main for these 7 steps.

## Null control
Harness `drift_harness.py` (seat scratch) calls `selftest_scope.drift(table, measured, workflow_steps)`. Here `measured` is run 44922703115's `selftest-closures` artifact, which is the committed table unioned with that run's strace measurement, so its refusals are the run's refusals.
- Main's table: 7 refusals, line for line the 7 in the job log (rc 1). This is the failing test.
- This head's table: 0 refusals (rc 0). This is the passing test.
- Perturbation: this head's table with `dev/governance/dimensions` removed from roster-library's dirs gives 1 refusal, `UNDER-SCOPED step roster-library: dirs misses ['dev/governance/dimensions']` (rc 1).

## Figures
- `python3 -I tools/ci/selftest_scope.py absorb --from <selftest-closures artifact of run 44922703115>` at a8efe1d1c2 (python 3.14.7, a pure-Python path with no strace): `selftest_scope absorb: 738 read(s) added to 7 step(s)`. The output is byte-identical (`cmp`) to CI's `selftest-absorbed` artifact of the same run.
- `git diff --stat`: 738 insertions, 3 deletions. The 3 deleted lines are roster-library probes `dev/governance/dimensions/{D12,D3,D99}.md`, now answered by its new `dirs` entry for that directory. Duplicate list items: 0. run_sha: unchanged.
- `python3 -I tools/ci/selftest_scope.py static`: `127 gated step(s), 0 problem(s)`.
- Hotfix prepr (`PREPR_SKIP_CODE=1 PREPR_SKIP_CLOSURES=1 HPO_ALLOW_STALE_TOOLS=1`): `PRE-PR: 25238b470a14 rc=0`; structure ratchet passed (`tests/structure.py`, HEAD merged with origin/main); ci_predict reports no closures, fast, governance or instrument red against a8efe1d1c2a8; ref_privacy refused 0; claim files byte-identical to origin/main.

## Red checks
`governance / instrument-self-tests` drift step (push-only, main). It goes green on the first main push after merge. A read added by a later merge reddens it again until the next absorb lands. This is at least the fourth main-red hotfix of the selftest-drift family (#3487, #3718, 912b87c035, this one). The absorb step (R11-PRE-SHARED-FILES part 1) produced the right table on every red run, but no seat or beat committed it for about 2.5 days. The docstring's "the record beat hands it the newest selftest-closures artifact" is not happening.

`governance / instrument-self-tests` at `35bb34b2a3` (job 136929429316, run 44931573918): cancelled by the job's pull-request cap (30 minutes; 90 on a push, `governance.yml`'s `timeout-minutes`) at 30m13s, inside the `ci_predict.py --self-test` step, with no step red before it. All 127 gated steps ran (`selftests=all: 127 of 127 gated step(s) run`).
- It is not the drift this PR repairs. The drift step is push-only and did not run on this pull request. The table is not short either: the prototype absorb beat (`selftest_absorb_beat.py --max-runs 3`, run at origin/main a8efe1d1c2 over runs 44922703115, 44913478338 and 44912297572) produced a table that `cmp` finds byte-identical to this head's `tools/ci/selftest_closures.json`.
- It is not inherited from main either. Main's push runs of this job get a 90-minute cap, and their red is the drift step.
- It is environmental. Eight other pull-request runs of the same job today (15:16Z to 18:18Z) succeeded in 19 to 28 minutes. One other run, `fix/r11-carry-drawmap-pr` at 15:37Z, was cancelled at the same 30-minute cap. The job runs close to its cap on a loaded runner. The run's own `gate` (job 136942285244) passed with this job cancelled, so the head's gate is green and the job was not re-run: a re-run would re-gate an unchanged head.
- Cheaper detector: none for this PR. The class is a job-level cap set near the job's measured duration, the same class env-matrix's cap was re-derived for in 1ec3ebde08.

`gate` on the `edited` runs 44931575439 and 44932321089: `FAIL run(s) [44931573918] at this head are still being judged; their gate decides`. That run's own gate decides, so these two are not failures of this diff. Both were re-run after it concluded (attempt 2, jobs 136942619584 and 136942630943) and passed.

## Forward-carry

- Carry: dismissed: this hotfix has no roster group and R11-PRE-SHARED-FILES is carries-open and takes no carry, so the reviewer's table-only-diff timeout follow-up stays recorded in the instrument round-end triage (item d45f668f, supersedes R11-PRE-SHARED-FILES)
- Carry: dismissed: the automatic absorb job is unbuilt pending the owner's D1/D2 ruling, as the countermeasure text in dev/audit/config/bugclasses.json records, so no group can take it now (item 132fe653, supersedes R11-PRE-SHARED-FILES)

## Friction
none




