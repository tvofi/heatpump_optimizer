R10-CI-LAYOUT PR 0: the inert `ci.yml` stub (DESIGN-P1 step 5b), plus the three ci-ratchet payments that the design review placed in PR 0 (`DESIGN-REVIEW.md` section 3, rows PR 0-R(a), R(b) and R(c)).

The stub lets `workflow_dispatch` dispatch the umbrella from `probe/ci-layout-*` refs. GitHub dispatches only a file that exists on the default branch, so without the stub on main the fan-out's live work cannot run.

The payments are meant to turn main's red `ci-ratchet` job green. On main's push runs it reports `GREW critical_path_minutes` and `GREW script_runs_per_push`, and it is red at this branch's first base, `4a3cbcf62` (push run 39310145738).

- **stub**: `.github/workflows/ci.yml`, `name: CI`, `on: workflow_dispatch` only. It takes the inputs `pr`, `base`, `recheck` and `no-skip`, each an optional string. It has `permissions: {}` at both levels and one job `stub` that runs `true`. `tests/entities.py` pins it inert, and `tests/closure.py` lists it in `GATE_FILES`.
- **R(a)**: `tests/arch_score.py` and `tests/arch_score_head.py` move from `lane_units` to `lane_golden` in `tests/run.sh`, with a placement pin.
  - **Round 3:** `tests/harness_headers.py` moves from `lane_units` into the alone-on-the-box phase, after `stress.py` (`lane_stress`). The move to `lane_golden` put arch_score.py beside it, and that turned `fast (3.14)` red (see Red checks). An entities pin holds the placement.
- **R(b)**: `tools/coverage/coverage_tree.sh`'s floor re-validation re-measures only the scripts it reused. Their `reused` rows leave `scripts.tsv` and `per/provenance.tsv`. `_coverage_revalidation` pins the executions, and the ledger check pins the two ledgers.
- **R(c)**: `tests/ci_ratchet.py` `script_runs()` stops counting a `reused` coverage row, which is a copy that executes nothing.
  - `script_runs_per_push` is re-recorded from 68 to 53, the count when every script is measured once. **This is a tightening, not a raise.**
  - `_CIR_REUSE` and its null pin the exclusion.
  - A planted extra run turns the ratchet red, and the budget is pinned equal to the derived count.

**Alternatives** (fixer step 17):
- **(a)** A separate job for the arch-score pair would add a check name and a runner for the same work.
- **(b)** Counting around the duplicate re-measure would keep the duplicate execution, which is the cost being removed.
- **(c)** The window maximum (about 34) would turn a legitimate floor-FAIL push red.
- **Round 3's harness_headers placement:**
  - **Raise the 480 s bound, or loosen the 50 % headroom.** Refused. That would fit the check to the contention instead of removing it (review: metric-gaming).
  - **Put it in `lane_golden` before arch_score.py.** It would then overlap lane_units' `features.py`/`entities.py` and lane_e2e. On the base layout it effectively ran with nothing beside it: it sat at the tail of the longest lane, after the other two had finished.
  - **Measure CPU so a co-runner does not move it.** No such rule exists: under SMT sharing, CPU seconds themselves inflate.
  - **Chosen:** run it alone. That is already the class `gate_lock.py needs-lease` assigns it: `run.sh`'s `leased()` names "the scripts that MEASURE the machine (stress.py, harness_headers.py)". The in-run layout now agrees with the lease's classification.

## Head

`dd3a44474543f52974667fb37861b346d607980d`. Its merge base is origin/main `d1db05dfcf2a541e720e32996aee4a22d8e63968`. It adds one authored commit to the round-2 PR head `c4a357e5e`: `dd3a44474`, the harness_headers placement, its pin, the lease test's stub, and mutant M8.

`c4a357e5e` was the orchestrator's merge of origin/main `d1db05dfc` over `0cc5cd864`, which itself merged the round-2 code head `b4d7bf9c7`. Every local figure below was taken at this head on this seat, CPython 3.14.7. The CI figures name their runs.

## Mutation proof

`python3 dev/audit/harnesses/r10_ci_layout_p0_mutants.py` at this head. Each mutant runs in its own detached worktree of HEAD and makes one text substitution that must apply exactly once, then a full `PYTHONPATH=tests/hastub python3 tests/entities.py`. A mutant is KILLED only if entities exits non-zero and an aimed check is among the FAIL lines.

```
M0 PASS rc=0 | ALL 2358 ENTITY CHECKS PASSED | aimed red: []
M1 KILLED rc=1 | 1 of 2358 ENTITY CHECKS FAILED | aimed red: ['the ci.yml umbrella stub is inert: dispatch only, one `true` job, no grant, no `uses:`, and a gate file']
M2 KILLED rc=1 | 1 of 2358 ENTITY CHECKS FAILED | aimed red: ['the ci.yml umbrella stub is inert: dispatch only, one `true` job, no grant, no `uses:`, and a gate file']
M3 KILLED rc=1 | 1 of 2358 ENTITY CHECKS FAILED | aimed red: ['the architecture-score pair runs in lane_golden and not in lane_units']
M4 KILLED rc=1 | 1 of 2358 ENTITY CHECKS FAILED | aimed red: ['the coverage floor re-validation re-measures only the scripts it reused']
M5 KILLED rc=1 | 2 of 2358 ENTITY CHECKS FAILED | aimed red: ['the CI ratchet counts no `reused` coverage row as a script run']
M6 KILLED rc=1 | 1 of 2358 ENTITY CHECKS FAILED | aimed red: ['one script run past the every-script-once budget turns the CI ratchet red, and the budget is that count']
M7 KILLED rc=1 | 1 of 2358 ENTITY CHECKS FAILED | aimed red: ['after a floor-FAIL re-validation each coverage ledger holds one row per script and no `reused` row']
M8 KILLED rc=1 | 1 of 2358 ENTITY CHECKS FAILED | aimed red: ['the CPU-bounded harness check runs alone: in lane_stress after stress.py, in no parallel lane']
RESULT survivors=0
```

- **M1 / M2 (stub).** M1 adds a `push:` trigger. M2 takes `ci.yml` out of `GATE_FILES`.
- **M3 (R(a)).** `arch_score_head.py` goes back into `lane_units`.
- **M4 (R(b)).** The re-measure-everything lines come back.
- **M5 (R(c)).** The `reused` exclusion is deleted.
- **M6.** The budget becomes 54.
- **M7 (round 1).** The reused-row ledger filter is deleted.
- **M8 (round 2).** `tests/harness_headers.py` is moved back to the end of `lane_units` and out of `lane_stress`. It is killed by `the CPU-bounded harness check runs alone: in lane_stress after stress.py, in no parallel lane`.
- **The reviewer's extra mutants X1-X5** (`probe/rev-2464-4c0a1675:ev/extra_mutants.py`) were all killed at `c4a357e5e`. This head changes none of the code they mutate.

## Null control

- **M0, the unmutated head.** The first line of the block above.
- **Nulls built into each new check:**
  - **Stub check:** three planted stubs, and each must report a defect.
  - **Placement pins:** the same reader finds `structure.py` in `lane_units` and `stress.py` in `lane_stress`.
  - **Revalidation and ledger checks:** the floor-met arm leaves the reused script unexecuted, with exactly one `reused` row per ledger.
  - **`_CIR_REUSE_NULL`:** reads 4.
  - **`_cir_planted(0)`:** grades `ok`.
- **Local checks.** `python3 tests/structure.py` printed `STRUCTURE RATCHET PASSED`. `PYTHONPATH=tests/hastub python3 tests/closure.py selftest` printed `ALL 124 closure shrink pins PASSED`. `PYTHONPATH=tests/hastub python3 tools/pr/ci_predict.py --base origin/main` printed `no closures or fast red predicted against d1db05dfcf2a`. `bash -n tests/run.sh` returned 0.

**Root-cause control, owed by CI at this head.** The harness_headers line `sysid_estimator_frontier.py: cpu=<s>s of the 480s bound`, read from this head's FULL `fast (3.14)` job log, must fall back into the base layout's band.
- **Base band:** 142.5-164.0 s over the 8 regular base push runs, and 86.5 s on the fast-runner outlier.
- **Pass:** a reading in that band.
- **Fail:** a reading at or above the round-2 PR-layout readings (199.6, 231.0, 306.4 s) means co-running was not the cause, and this fix is wrong.

**FULL-run timing (review section 3, R(a) stage one).** Re-taken with the round-2 run included:

`python3 dev/audit/harnesses/r10_ci_layout_p0_fast_offsets.py --before <9 base push runs> --after 39333417268 39337586935 39337584363 39346553722`:

```
before 39310145738 push 4a3cbcf62 attempt=1 success queue=0.07 dur=57.73 offset=57.80
before 39309509899 push daca95c5d attempt=1 success queue=0.05 dur=57.97 offset=58.02
before 39309055147 push 28ebd0b07 attempt=1 success queue=0.08 dur=53.77 offset=53.85
before 39307877535 push d5d0b465b attempt=1 success queue=0.08 dur=54.80 offset=54.88
before 39302900612 push 8b14bcecc attempt=1 success queue=0.08 dur=58.43 offset=58.52
before 39301525639 push f118e2644 attempt=1 success queue=0.07 dur=57.77 offset=57.83
before 39299026662 push 91f011950 attempt=1 success queue=0.07 dur=58.73 offset=58.80
before 39298637824 push 76e96a406 attempt=1 success queue=0.07 dur=59.50 offset=59.57
before 39293926561 push 5b9c33d58 attempt=1 success queue=0.05 dur=34.37 offset=34.42
before: counted 9 of 9; median offset=57.83 median dur=57.77
after 39333417268 pull_request 4d1730bd1 attempt=1 success queue=1.28 dur=51.85 offset=53.13
after 39337586935 pull_request c5b5d06c3 attempt=2 success queue=1.22 dur=31.10 offset=32.32
after 39337584363 workflow_dispatch c5b5d06c3 attempt=1 success queue=1.00 dur=46.50 offset=47.50
after 39346553722 pull_request c4a357e5e attempt=1 failure queue=0.40 dur=52.45 offset=52.85
after: counted 4 of 4; median offset=50.17 median dur=49.17
RESULT saved_offset=7.66 bar=5.0 PASS
```

- **These four runs are the pre-round-3 layout.** In it, harness_headers ran inside the parallel phase. Round 3 runs it after `stress.py` instead. On the base layout's push runs it took 169-195 s of wall time (106 s on the outlier, `hh=` in the reviewer's `ev/sysid_cpu_by_run.txt`).
- **So this head's `fast` end is expected about 2-3 min later than these four, est.** From job 118380549631's timings: the parallel phase ends with arch_score.py at about 01:01:33 instead of lane_units at 01:02:22. Then stress.py runs, and then harness_headers.py alone, about 188 s. That leaves a median saving near 4.5 min (est.), under the 5-min stage-one bar. That projection is not a measurement.
- **The reviewer's permutation null** (0 of 84 three-run base subsets reach 5 min, U=25/27, p=0.018) speaks to the old after set, not to this layout.
- **The binding control stays push against push** (the window rule below). If this head's own FULL run, read with the same instrument, misses the bar, R(a)'s timing claim has not paid at this layout. The orchestrator then decides between the A3 Fallback for R(a) alone and keeping it on the window rule. R(b), R(c) and the stub do not depend on it.

**The window rule, the post-merge control (review B4), owed by CI.**
- **`script_runs_per_push`:** must be green on the first push run after the merge.
- **`critical_path_minutes`:** is the median wall time of the 8 newest completed push Tests runs, which is the mean of the 4th and 5th smallest. It goes green when that median is under 54.825 min. Five of the eight under the bar is enough, but not required.
- **Never re-run a push Tests run to check it.** A re-run moves `updated_at`.
- **If it is still red 6 push runs after the merge, stop and re-measure.** A raise is the last resort, under rule 2.

## Figures

- **The scope.** `MODE: FULL`, reason `.github/workflows/ci.yml changes the gate itself`. Command: `D=$(mktemp -d); python3 tests/closure.py select --diff $(git merge-base origin/main HEAD) --workdir "$D"; cat "$D/scope.txt"`.
- **The red.** `fast (3.14)` check run 118380549631, conclusion `failure`, and `pr-contract` check run 118403223959, conclusion `failure`. Of 49 check runs at `c4a357e5e`, 32 succeeded, 15 were skipped and 2 failed. Command: `gh api 'repos/tvofi/heatpump_optimizer/commits/c4a357e5e3393d2f570e6061d283f680a317947f/check-runs?per_page=100' --jq '.check_runs[]|[.id,.name,.conclusion]|@tsv'`.
- **The failing line.** `FAIL dev/audit/rounds/round4/D7/sysid_estimator_frontier.py costs at most 50% of its CPU bound [cpu=306.4s against 240s (50% of its 480s bound)]`, with `1 of 109 HARNESS HEADER CHECKS FAILED`. Command: `gh api --allow-escape-sequences repos/tvofi/heatpump_optimizer/actions/jobs/118380549631/logs | grep -E 'sysid_estimator_frontier|HARNESS HEADER CHECKS'`.
- **The `sysid_estimator_frontier.py` CPU readings by run.**
  - Base layout: 160.2, 161.0, 159.8, 142.5, 161.0, 159.6, 163.0, 164.0, and 86.5 (the outlier).
  - PR layout: 199.6, 149.1, 231.0, 306.4.
  - arch_score.py wall: 1662-1851 s on the base layout, 1415-2476 s on the PR layout.
  - These are the reviewer's readings from each `fast (3.14)` job log (`git show origin/probe/rev-2464-4c0a1675:ev/sysid_cpu_by_run.txt`). This seat re-read only job 118380549631's line, above.
- **The lane timings in Red checks.** Command: `gh api --allow-escape-sequences repos/tvofi/heatpump_optimizer/actions/jobs/<id>/logs | grep -E '\] start|alone on the box'`, plus the per-script seconds table at the job's end, for jobs 118257300582 and 118380549631.
- **The class's seams.**
  - Rule: `git grep -ln 'RLIMIT_CPU\|process_time\|getrusage\|thread_time' -- 'tests/*.py' 'tests/*.sh'` returns 4 files.
  - `tests/harness_headers.py` is CPU-bounded. Fixed here: it now runs alone.
  - `tests/stress.py` already runs alone in `lane_stress`.
  - `tests/replay.py` is not in any lane. It is on `run.sh`'s not-a-test list, which skips it.
  - `tests/structure.py` only reports a `process_time/thread_time` factor and bounds nothing.
- **The count of 53, every script measured once.** 53 = 34 − 1 + 20:
  - 34: `PYTHONPATH=tests/hastub python3 tests/closure.py lane-plan --all-scripts --out-dir "$D"; wc -l < "$D/scripts.txt"`.
  - 1: `tests/composed_closures.json` `scripts`.
  - 20: coverage_tree.sh's `DERIVED` + `fast)` pipeline.
  - `_cir_once_count()` returns `(53, [])`. The reviewer re-derived it at `4a3cbcf62` and at `c4a357e5e`.
  - The old budget, 68: `git show 4a3cbcf62:tests/ci_budgets.json`.
- **The window cross-check** (unverified, read from out-of-tree artifacts). Push runs without reuse read 53 each. 39213675232 read 73 under the old rule.

## Red checks

From the check-runs API at the round-2 head `c4a357e5e` (command in Figures): two failures.
- **`fast (3.14)`, check run 118380549631. Root cause: layout contention, which this head fixes.**
  - What failed: `tests/harness_headers.py` failed 1 of 109, the 50 % CPU headroom on `sysid_estimator_frontier.py` (306.4 against 240 CPU-s).
  - Why CPU seconds moved: the harness bills CPU-seconds against bounds sized from the serial cost. Its own `CPU_LIMIT_S` comment records that a CPU second is billed at least 2.48x inside a parallel pool.
  - What R(a) changed: it moved arch_score.py, the longest script, into `lane_golden`, which runs beside `lane_units`, where harness_headers.py ran. On the base layout, harness_headers sat at the tail of the longest lane, after the other lanes had finished.
  - The lane timings, from the two jobs' own logs, show the overlap directly:
    - **Base push job 118257300582:** harness_headers.py ran 20:09:01 + 188 s. By then lane_golden had ended (about 19:28:22, env_drift.py `--all` 443 s from 19:20:59) and lane_e2e had ended (19:32:43, card_drift.mjs 6 s from 19:32:37). It ran with no lane beside it.
    - **Round-2 job 118380549631:** harness_headers.py ran 00:54:49 + 411 s. arch_score.py ran in lane_golden from 00:20:17 for 2476 s, to about 01:01:33. So 404 of harness_headers' 411 s overlapped arch_score.py.
  - The readings: in 3 of the 4 PR-layout runs the figure sits above every base reading, and arch_score.py also slowed, which fits two-way contention. The 8-run base band (142.5-164.0) against the PR-layout trend rules out noise as the explanation.
  - The fix: harness_headers.py runs alone, after stress.py, with no bound moved.
  - Cheaper detector: the new entities placement pin, at the cost of one regex read per run. It refuses the layout before CI pays a FULL run to find the contention.
  - Outstanding: CI must confirm the sysid reading at this head (Null control).
- **`pr-contract`, check run 118403223959. Not a new defect.** It refused because the round-2 `## Red checks` did not name the red above (`check fast (3.14) is red and ## Red checks does not name it`). This section names it.
- **Possible at this head:** `closures` UNDER-SCOPED with one `closures-autofix` cycle, if the Linux recording of `tests/entities.py` sees reads the Darwin predictor does not. The predictor read clean.
- **After the merge:** `ci-ratchet` on `critical_path_minutes` until the window rule is met. It is red at the base as well.
- **The reviewer's container:** its one environmental entities red (`graders-head-copy`'s delivery_status step) fails identically at main there and is green in CI. It is not reproduced on this seat.

## Unpinned sites

n/a: prepr step 6d reports that the diff adds no unpinned mutation site.

## Forward-carry

- PR 1's W1 deletes the composed-closure path (`tests/composed_closures.json`, DESIGN-P1 step 5a). The every-script-once count then becomes 54. This PR's budget-equality check (`_cir_once_count()` against `script_runs_per_push`) refuses until PR 1 re-derives the count and re-records the budget, with its reason in that commit. R(b)'s `_coverage_revalidation` and the ledger check must stay green across W1. Carry: R10-CI-LAYOUT
- U9's re-keyed `ci_ratchet.py` reader (PR 2) keeps R(c)'s `reused` exclusion, `_CIR_REUSE` and the budget-equality pin unchanged. Any later lane edit, PR 1's W1 or the umbrella's split of `tests.yml`, keeps `tests/harness_headers.py` in the alone phase: the run-alone pin refuses otherwise. Carry: R10-CI-LAYOUT
- R10-STAMP: `stamp.py` rule 2 needs a green Tests push run at HEAD, and that includes `ci-ratchet`. The stamp can run once the median wall time of the 8 newest completed push Tests runs is under 54.825 min, which can be before PR 1 (review B7). Carry: R10-STAMP

## Friction

none

## Approval

`tests/run.sh` and `.github/workflows/` are code-owned by tvofi (`.github/CODEOWNERS`). This diff merges only on tvofi's approving review at its head, or under tvofi's mandate on #201, comment 6175172275, whose first line reads verbatim: "MANDATE: agents may approve as tvofi, scope all, from 2026-10-14T18:14Z until 2026-10-28T18:14Z". The PR 0 split and its contents are the design review's amended packaging (A3), approved under the R10 grant ("decisions = recommended"). The `script_runs_per_push` re-record is a tightening, 68 → 53, so it needs no `## Raise justification`. No bound or budget is raised in round 3.

🤖 Generated with [Claude Code](https://claude.com/claude-code)
