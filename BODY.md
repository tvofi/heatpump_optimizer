Main red, instrument (the main-red exception to the round-11 instrument freeze). Every ci.yml push run on main on 2026-11-15 ended `failure` or `cancelled` in `governance / instrument-self-tests`, for two causes, both repaired here.

**(1) The drift step's four refusals.** `tools/ci/selftest_closures.json` missed reads main measured: the `dirs` of `dependency-graph-census` and `prepr` and the `.gitattributes` probes of `policy-lint-mutants` under `dev/audit/yardstick`, `dev/audit/yardstick/round10` and `dev/audit/rounds/round10/objective` (directories #3611 added at 646352ff), and `selftest-scope-mutants`' probe `-c`. Re-recorded the way `selftest_scope.py`'s docstring states ("Commit that file, or re-record ... and union the same way"): run 43741911544's `selftest-closures` artifact 14174287444 (main 755b7f57; zip sha256 `21243679cf94a01cb833960c4284ab52db371963081a12c6ff6f690d4b0645da`, the digest that job's log prints) unioned over main's committed table by `selftest_scope.union_record`, so `finder-overlap` and `plant-recall`, gated after that run, keep their committed entries. The diff adds exactly the ten reads the four refusals name and nothing else.

**`selftest_scope`'s own self-test does not fail.** The `FAIL` lines and the `TypeError` in job 132896968023 are the output of `selftest_scope_mutants.sh`, which prints each mutant's failing checks; that step ended "SELFTEST-SCOPE MUTANTS: every mutant refused" and passed, and the unmutated self-test step printed `selftest_scope self-test: 118 checks, 0 failed`. The `TypeError` is the "prune goes on over an unreadable table" mutant: with the `table is None` guard deleted, `prune_entries(None, ...)` raises before its `ck` line, so the mutant is killed by rc 1, not by a named check. No code defect, so no failing test was owed; the union guard of #3551 is not implicated.

**(2) The 60-minute cap on a push.** Six of main's eleven push runs on 2026-11-15 were cancelled at 60.2-60.3 minutes, the other five finished in 34.5-52.9. The variance is the runner host, not the tree: the in-line steps ran about 2.3x slower on some hosts (job 132905064799, `northcentralus`) than on others (job 132896968023, `centralus`) at near-identical heads, while the mutant step (1.0-1.4 min) and the drift fold (4.3-6.0 min) stayed flat. Every cancelled run had reached the mutant step at 57.2-59.8 minutes, which projects to about 67 minutes uncensored.

Slowest steps (min-max over the eleven runs): self-tests-outside-seat 4.9-11.6, policy-lint-mutants 2.9-7.7, the drift fold 4.3-6.0, cloud-relay 2.3-5.1, verdict-bus 1.9-4.9, ci-predictor 1.7-3.9, beat-job-rows 1.4-2.9, merge-train 1.6-2.7.

Options and the wall each buys:
- **Timeout to 90 on a push (taken).** Buys about 23 minutes over the projected slow-host worst case of about 67, i.e. about 34% headroom; costs zero seconds on a run that finishes and lengthens only a hung run, by 30 minutes. A pull request keeps 30. It does not extend the CI run's wall in practice: `codeql / Analyze (python)` in the same run takes 52.9-75.1 minutes.
- **Two shards (matrix), not taken.** Buys about half the in-line wall (a slow-host shard about 30-35 minutes including its own drift fold). Needs `scope` to filter by shard, `check` to accept a step subset rather than refuse the other shard's steps as UNMEASURED, two `selftest-closures` artifacts unioned at re-record, and a job name every reader of `instrument-self-tests` keys on to change. That is a redesign of an instrument in a freeze, not a main-red hot-fix.
- **Moving self-tests-outside-seat into the detached set, not taken.** Buys at most its 4.9-11.6 minutes and only if the runner has a free core; the slow hosts are the ones already CPU-bound, and pr_args.sh's self-test is documented in the launch step as missing its window under that contention.

**CodeQL (recommendation only, no change here).** `codeql / Analyze (python)` on main's push runs on 2026-11-15: 52.9-75.1 minutes, one cancelled at its 75-minute cap (run 43733946364, e0ad8b2b). Main's push leg scans the full tree; the pull-request leg already ignores `tests/**` and `dev/**` (codeql.yml, r10-codeql-pr-paths). Python by top directory at this head: `dev/` 1151 files, 191421 lines (863 files under `dev/audit/rounds/`, round evidence and harnesses that no product or CI path imports); `tests/` 84 files, 216677 lines (`tests/features.py` alone 92325); `tools/` 288 files, 109906 lines; `custom_components/` 92 files, 74071 lines. Recommendation: exclude `dev/audit/rounds/**` (evidence data, never executed by CI or shipped) from main's python leg; keep `tests/**`, which CI executes. This removes about 32% of the python lines (all of `dev/`) or a little less for `dev/audit/rounds/**` alone; the duration it buys is not measured here, because extraction time is dominated by `tests/features.py`, which this would keep. Measure by one `workflow_dispatch` of the leg with the exclusion before deciding.

## Head

91164e63e9c7d07d13e8546275d6ee34b4d86b71, on main e75ad291ff5c58f7c8362b0a20fbe6b230adf717, measured 2026-11-15.

## Mutation proof

Each read the union added, deleted alone from the head table and driven through `selftest_scope.drift` against the artifact's measurement (the drift one-liner under Figures, with the mutated table as its second argument):
- drop `selftest-scope-mutants` probe `-c`: `UNDER-SCOPED step selftest-scope-mutants: probes misses ['-c']`, 1 refusal(s)
- drop `prepr` dir `dev/audit/yardstick`: `UNDER-SCOPED step prepr: dirs misses ['dev/audit/yardstick']`, 1 refusal(s)
- drop `policy-lint-mutants` probe `dev/audit/rounds/round10/objective/.gitattributes`: `UNDER-SCOPED step policy-lint-mutants: probes misses [...]`, 1 refusal(s)

The timeout is a cap, not a check; its evidence is the job-duration measurement under Figures.

## Null control

Main's table (`git show origin/main:tools/ci/selftest_closures.json`) through the same drift one-liner prints the four refusals job 132896968023's drift step printed, verbatim (policy-lint-mutants, dependency-graph-census, prepr, selftest-scope-mutants) and `4 refusal(s)`; the head table prints `0 refusal(s)`. The union one-liner run on main's table reproduces the committed head table byte-identically (`git diff --quiet HEAD -- tools/ci/selftest_closures.json` exits 0).

## Figures

<!-- figure-block: scope-line mb=e75ad291ff5c58f7c8362b0a20fbe6b230adf717 head=91164e63e9c7d07d13e8546275d6ee34b4d86b71 -->
~~~text
MODE: FULL -- every test script runs, nothing is scoped out.
~~~
<!-- /figure-block -->
- drift, base 4 / head 0 refusals: `python3 -I -c 'import json,sys;sys.path.insert(0,"tools/ci");import selftest_scope as s;from pathlib import Path as P;st=s.workflow_steps(P.cwd());g=set(s.gated_ids(st));t=json.load(open(sys.argv[2]));a=json.load(open(sys.argv[1]))["steps"];m={k:a.get(k,t["steps"][k]) for k in g};r=s.drift(t,m,st)[0];print(*r,sep="\n");print(len(r),"refusal(s)")' ARTIFACT TABLE`, ARTIFACT the `selftest_closures.json` inside artifact 14174287444, TABLE main's or the head's `tools/ci/selftest_closures.json`; a step gated after the artifact's run is measured as its committed entry.
- the re-record: `python3 -I -c 'import json,sys;sys.path.insert(0,"tools/ci");import selftest_scope as s;from pathlib import Path as P;r=P.cwd();a=json.load(open(sys.argv[1]))["steps"];s.write_table(r/s.TABLE,s.union_record(s.load_table(r/s.TABLE),a,set(s.gated_ids(s.workflow_steps(r)))),r)' ARTIFACT` on main's table.
- `python3 -I tools/ci/selftest_scope.py static`: 119 gated step(s), 0 problem(s); `python3 -I tools/ci/selftest_scope.py --self-test`: 128 checks, 0 failed; `sh tools/ci/selftest_scope_mutants.sh --self-test`: every mutant refused.
- job durations and per-step times: the `jobs` of ci.yml push runs on main on 2026-11-15 (runs 43691296618, 43695566176, 43705258717, 43716462808, 43725314631, 43726315630, 43730325600, 43730716444, 43733946364, 43741911544, 43744546894), `GET repos/tvofi/heatpump_optimizer/actions/runs/<id>/jobs?per_page=100`, duration = completed_at - started_at per job and per step; a job at 60.2 minutes or more counts as capped. The host region is the `Region:` line of each job log's header.
- python lines per directory: `git ls-files '<dir>/*.py' | xargs cat | wc -l` and `wc -l tests/features.py`.

## Red checks

none on this branch. The reds this fixes are main's (`governance / instrument-self-tests` on every push run listed above). Cheaper detector for (1): none on a pull request, by design: `selftest_scope.py` measures read sets only under strace on main's push and turns main red within one merge (CLAUDE.md rule 1's trade); #3611's new directories changed what four steps list, which only a traced run sees. For (2): the cap is a fixed number over a host-dependent wall, the shape `dev/audit/rca/R10-RCA-FAMILY-POLICY-DOCS-TIMEOUT.md` names for every fixed `timeout-minutes`; its root-cause seat is separate from this one.

## Forward-carry

none

## Friction

none
