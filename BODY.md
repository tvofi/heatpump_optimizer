# HOTFIX R10-HOTFIX-CI-CRITPATH-2: a measured tolerance band on critical_path_minutes only

Main is red on `tests / ci-ratchet` from 05c0d6d5d (the #3040 merge) through 0cae227c3: `GREW critical_path_minutes: 34.467 (budget 34.267)` (run 41201096004). 0d33c9348 is green. `git diff --stat 0d33c9348 05c0d6d5d` is seven `dev/programme/delivery/*.md` rows, which cannot move CI work.

The metric is not a function of the tree. It is the median of the newest 8 completed ci.yml push runs' work, read live from the Actions API (`tests/ci_ratchet.py --gather-runs`, `PUSH_WINDOW = 8`). Whether the gate passes depends on which 8 host draws the window holds when the job runs: state (b), runner variance.

Measured with `ci_ratchet.run_minutes` over the runs and jobs that `--gather-runs` writes:
- 59 completed ci.yml push runs, 2026-10-30..31: median 33.767, sigma 1.638. The first-20 median is 33.884 and the last-20 is 33.867, so the work is flat. Every sliding 8-run median falls between 32.916 and 34.575, and the largest |median8 - window median| is 0.851.
- 86 runs of 2026-10-25, the recording window: median 32.55, p90 34.267. That p90 is the budget, reproduced exactly. Sliding 8-run medians run 31.709..33.850, and the largest |dev| is 1.300.
- The red window's record-only merges ran 35.150 (05c0d6d5d), 33.917 (3759d49a5), 33.967 (4c3645406), 34.917 (2fc0e95b2) and 33.500 (0cae227c3). The live 8-run median at fetch is 34.467, the logged value.

Cause: the 8-run median's sampling spread (up to 1.3 min) is larger than the headroom left between the work's center and the budget (34.267 - 33.767 = 0.5), so the gate flaps on host variance. Caveat, stated plainly: the center did rise from 32.55 to 33.77 since the 2026-10-25 recording. `tests / fast (3.14)` median work went from 29.47 to 31.83 and `arch-instrument` from 31.43 to 31.92. That is real growth across many merges, and it spent the headroom. The center is still under the budget, and the band does not raise the budget.

Fix (owner ruling 2026-10-31, under mandate 6329234399):
- `tests/ci_budgets.json` gains `critical_path_minutes_band: 1.3`, the largest measured |8-run median - window median| over every sliding window of 145 runs, unpadded.
- `compare()` reports `critical_path_minutes` as GREW only past budget + band. Every other row, the integer counters included, stays at zero tolerance. `--record` carries the band over, through `record_table()`, a pure function `main()` calls and the self-test drives.
- `tools/policy/budget_raise_gate.py` types the band MAX0: absent means zero tolerance, so adding or widening the band is a raise and narrowing it is routine.
- `critical_path_minutes` stays at 34.267.

## Head

536da691c7c77d0275e72235bc0b95991ce7f722

## Mutation proof

- Before the code (test commit 765a0d19692ca5ed4b79b89192dcb1973bbac8b4), `python3 -I tests/ci_ratchet.py --self-test` failed 3 of its 44 checks: "the observed noise (34.467 on a 34.267 budget) passes inside the 1.3 band", "a median at budget + band exactly passes", and "a band row is a known, non-negative bound and not a graded metric". After the code (b8a027974): 44 checks, 0 failed. At this head, with the record-table pin: 45 checks, 0 failed.
- The checks that already pass on the unfixed code bound the fix from the other side: "a median one thousandth past budget + band is growth" (35.568), "the band never applies to a counter (54 -> 55 is growth with a band present)", and "no band row is zero tolerance".
- The `--record` carry-over (fix review round 1, surviving mutant M6). At b8a027974, deleting `**{k: budgets[k] for k in BAND_KEYS if k in budgets},` from `main()` left `ci-ratchet self-test: 44 checks, 0 failed`: no check pinned it. At this head that line is in `record_table()`, and the new check "--record carries the band over unchanged and re-records every derived metric" compares the whole table. Deleting the line now gives 45 checks, 1 failed.
- Every mutant, each applied to this head and restored, run with `env -u BASH_ENV python3 -I <script> --self-test` (summary lines):
  - Baseline: `ci-ratchet self-test: 45 checks, 0 failed`; `budget_raise_gate self-test: 240 checks, 0 failed`.
  - M1, band ignored in compare (`band = 0`): 45 checks, 2 failed.
  - M2, band applied to every row: 45 checks, 1 failed.
  - M3, gate row MAX instead of MAX0: 240 checks, 1 failed.
  - M3b, gate row deleted: 240 checks, 1 failed.
  - M4, band bounds check dropped: 45 checks, 1 failed.
  - M5, `>=` for `>`: 45 checks, 4 failed.
  - M6, record carry-over deleted: 45 checks, 1 failed. Killed.
  - M7, band key not excluded from the grading loop: 45 checks, 0 failed. This mutant is equivalent: the band key is never derived, so `compare()` prints `? not derived; not graded` for it and never grades it as growth.
- Deleting the `critical_path_minutes_band` MAX0 row from `budget_raise_gate.py` SCHEMA reds "ci: a critical-path band narrowed is routine" (240 checks, 1 failed). With the row: 240 checks, 0 failed.

## Null control

On the live window, `compare()` against the budget table without the band row reports `GREW critical_path_minutes: 34.467 (budget 34.267)`, which is main's red reproduced. With the band it reports `ok critical_path_minutes: 34.467 (budget 34.267, band 1.3)`. A copy of the window shifted by +1.31 min reads 35.777 and is GREW with the band. `script_runs_per_push` 55 on a budget of 54 is GREW with the band present.

## Figures

- `gh run view 41201096004 -R tvofi/heatpump_optimizer --log-failed`: GREW critical_path_minutes 34.467 (budget 34.267)
- `git diff --stat 0d33c9348 05c0d6d5d`: 7 files, all dev/programme/delivery/*.md
- `python3 -I tests/ci_ratchet.py --gather-runs FILE --window 60` (GITHUB_REPOSITORY=tvofi/heatpump_optimizer), then `ci_ratchet.critical_path_minutes` and `run_minutes` per run: the 59-run and 8-run figures above
- `gh api repos/tvofi/heatpump_optimizer/actions/workflows/ci.yml/runs?event=push&branch=main&created=2026-10-25..2026-10-26` plus each run's jobs, through `run_minutes`: the 86-run figures above
- `env -u BASH_ENV python3 -I tests/ci_ratchet.py --self-test`: 45 checks, 0 failed
- `env -u BASH_ENV python3 -I tools/policy/budget_raise_gate.py --self-test`: 240 checks, 0 failed
- `python3 tests/structure.py`: STRUCTURE RATCHET PASSED
- `python3 tools/audit/archscore/score.py --diff $(git merge-base origin/main HEAD) HEAD`, three-dot against the merge base 0cae227c329f24d859c10db94b9dbd8a6368d11c, at head 536da691c7c77d0275e72235bc0b95991ce7f722: `Architecture score: dS +0.0000 NULL`

## Architecture score

dS +0.0000 NULL, measured three-dot against the merge base 0cae227c3 (command in `## Figures`). The diff touches no coordinator code, so no architecture metric moves. Round 1's body quoted an improvement read two-dot against a newer origin/main. That movement was main's own drift, not this diff's, and the figure is withdrawn.

## Raise justification

The raise is `tests/ci_budgets.json: critical_path_minutes_band: new at 1.3` (absent counts as zero). Mandate 6329234399, and the owner's ruling of 2026-10-31 in chat: "I suspect the ci-critical path minutes is runner variance, increase the variance band in that case under the mandate".
Payments tried: (1) Re-recording critical_path_minutes by its documented rule (p90 of a 40-run window) would raise the budget itself, 34.267 -> 35.317. The owner's ruling rejects that, and it would hide the 1.2-min center growth inside the cap. Rejected. (2) Paying down the work: the critical path is `arch-instrument` (~31.9 min) and `fast (3.14)` (~31.8 min). The center sits 0.5 min under the budget already, and no reduction makes an 8-sample median of a sigma-1.64 distribution stay within 0.5 min of its center, so that payment cannot fix a variance red. (3) Grading on a wider window (median of 40) would cut the noise, but it changes how the instrument grades and was not the ruled fix. It is left to the orchestrator as a proposal for triage. No payment that improves the architecture removes the variance, so the band is the remaining path.
Architecture score: dS +0.0000 NULL

## Red checks

`tests / ci-ratchet` on main pushes 05c0d6d5d..0cae227c3: GREW critical_path_minutes 34.467 (budget 34.267). Root cause (defect-root-cause.md, red-check trigger): the graded statistic is an 8-sample median of live runner timings, and its noise exceeded the headroom. No cheaper detector exists. The metric reads only main's push-run history at the moment the job runs. A pull request's own run, prepr.sh and ci_predict.py cannot see it, because none of their inputs come from the tree. The countermeasure is this band, sized from measured spread and typed as a raise when widened.

`budget-raise-gate`: red by design until a decisive approval at this head. The diff adds `tests/ci_budgets.json: critical_path_minutes_band` at 1.3. The base's schema reads it as a pinned value, and the head's schema types it MAX0, so either way it is a raise. This is the deliberate, mandated raise justified under `## Raise justification` (mandate 6329234399, the owner's ruling of 2026-10-31), not a defect, so the root-cause rule owes nothing: no cheaper detector applies to a gate that exists to hold a raise for approval.

## Forward-carry

- The fix review's instrument finding: budget_raise_gate checks only the shape of the `Architecture score:` line, never its value against the arch-score job; that is how round 1's unearned improvement figure passed the gate. Destination: the group's brief in dev/programme/rosters/wave-r10-groups.json. Carry: R10-FLY-MANDATE-REVOKE-GUARD (the budget_raise_gate dS value check; queued by the orchestrator)
- The fix review's MAX0 finding: budget_raise_gate calls a removed band a raise. Carry: dismissed: a fail-closed false positive that opens no gate weakness, and only the owner can decide that removal should be routine
- The fix review's wording finding: the "86 runs of 2026-10-25" label spans 2026-10-25T00:42Z..2026-10-26T20:55Z. Carry: dismissed: only the label is loose, and every figure re-derives exactly

## Friction

none
