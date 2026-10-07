Idle steps publish an exact sub-code when the solved plan shows why, and the Advisor hot-water row writes that recommended setpoint through `apply_schedule`, which stores it and the comfort target in the entry options. The card says Because for a published sub-code and keeps Likely because when the step is only idle. The what-if prices an active away setback. The payload's minimum temperature is the floor that solve used, and the configured floor is named beside it while they differ. The comfort-at-risk event carries the coldest step's published reason.

Part of #201. Leaves #201 open.

Closes #1795

_Requested by **tvofi**_.

## Head

97f89cdaf5fb7fbcc046b40d0d26f16164f3e88e

Measured against origin/main 17f30f9cedf2a442592d3db01d1d2e708a55425b at 2026-10-07T14:21:02Z. Since the blocked head ace05371ed47a6a9d378883c9fefbad08315c343 (verdict comment 6027912894): `_fold_away` is typed against the away state and returns a new `AwayFold` TypedDict in `payload.py`; `tests/features.py` gains value checks on the idle-reason helpers, the away fold and the comfort cause; one equivalent `RETURN_DEL` is triaged under `tests/mutation_ledger/survivor_triage/notifier.py/`; the advisor and plan-why pages are regenerated at the merged tree; origin/main is merged twice, and the delivery row now sits at `dev/programme/delivery/2010.md`. A spread of the local view inside `_fold_away` was tried and reverted (c0a3e641): `tests/entities.py` EG-B3 resolves a payload merge source by its call and reported `[['view']]` unresolved.

## Mutation proof

In `idle_reason`, `return REASON_IDLE_FUSE` was replaced with `return REASON_IDLE`. In `_fold_away`, the two lines `if floor == float(configured): return view` were deleted. A probe ran the inputs of the features checks "UX-5 an idle step whose fuse cap leaves no room says the fuse" and "UX-5 a setback equal to the floor does not name a second one" against a `git archive` of this head, mutated and restored:

    MUTANT RESULT fuse-check got=idle want=idle_fuse pass=False
    MUTANT RESULT fold-equal-floor second_floor=True pass=False
    RESTORED RESULT fuse-check got=idle_fuse want=idle_fuse pass=True
    RESTORED RESULT fold-equal-floor second_floor=False pass=True

The typing fix: `tests/typing_ruler.py --mypy` under the pinned toolchain printed, at ace05371, `FAIL errors did not grow [recorded 0, measured 5 (+5)]` with `by_code[arg-type]` +1, `by_code[no-any-return]` +3 and `by_code[typeddict-item]` +1; at this head `ALL 9 typing-ruler checks PASSED`.

Pinning is not done. `mutation_table.py --pin-killed --base origin/main` refuses on this Mac: driven by every closure driver, the `tests/env_drift.py` baseline timed out at 1200 s (host load average above 200); driven by `--scripts tests/features.py` alone, the baseline is red on R9-F2.1 P3 and the run printed `MUTATION TABLE INCONCLUSIVE`. The CI pin step at the previous head printed `47 not started for --budget-minutes`. The diff-added sites are therefore still unpinned at this head, and `mutation` will refuse them again unless the orchestrator routes a Linux pin drive.

## Null control

The same probe on the same inputs without a fuse cap returned `idle` (`RESULT null no-cap got=idle want=idle pass=True`), and an away state that is home published neither `min_temperature` nor `configured_min_temperature` (`RESULT null home keys_has_min=False pass=True`), mutated and restored alike. A setback below the floor publishes 16.0 with the configured 19.0 beside it in both arms. The pinned typing ruler at origin/main's tree is the recorded zero the head is compared with.

## Figures

`git merge-base origin/main HEAD` is 17f30f9cedf2a442592d3db01d1d2e708a55425b.

`python3 tests/closure.py select --diff $(git merge-base origin/main HEAD) --workdir "$D"` printed `MODE: SCOPED -- 26 script(s) run, 5 scoped out` at the first merge; scripts run locally at this head, `PYTHONPATH=tests/hastub`:

`python3 tests/structure.py` -- `STRUCTURE RATCHET PASSED`.

`python3 tests/entities.py` -- `ALL 2200 ENTITY CHECKS PASSED`.

`node tests/card.mjs` -- `ALL CARD CHECKS PASSED`.

`node tests/card_drift.mjs origin/main` -- `2 state(s) moved and claimed, 38 identical`.

`node tests/md_tables.mjs` -- `doc_misrendered_lines=0`.

`python3 tests/doc_claims.py` -- `ALL 160 checks PASSED`.

`.venv-typing/bin/python tests/typing_ruler.py --mypy` -- `ALL 9 typing-ruler checks PASSED`.

`python3 tests/env_drift.py --all origin/main` -- `NO UNCLAIMED DRIFT: 56 scenario(s) checked against origin/main` and `NO STALE FIXTURE: 56 committed fixture(s) still match what this tree computes`.

`python3 tests/features.py` at the first merge (13fc4a45, whose test file this head keeps) -- `1 of 3833 FEATURE CHECKS FAILED`, the one being R9-F2.1 P3; 41 UX-5 checks passed.

`HPO_PAGES_OUT=<dir> node tests/card_browser.mjs` with `tests/pwlane`'s Playwright -- the advisor and plan-why pages written into `docs/img/card/`; the run's one failure, `P9 grid: no two text runs share ink` (`text "2" x text "3"`), fails identically on a `git archive` of origin/main 3910026e on this Mac. At the first merge the generator reproduced the committed advisor and plan-why PNGs byte for byte (`cmp`).

The heavy scope.run scripts (`tests/stress.py`, `tests/golden.py`, `tests/boost_drift_replay.py`, `tests/optimality.py`, `tests/backtest.py` and the rest) are left to CI on #2010 at this head, by tvofi's 2026-10-07 rule that heavy scripts run in CI; their results are CI's check-runs, not figures in this body. Before that rule, `tests/arch_score_head.py` and `tests/backtest.py` exited 0 locally at 13fc4a45.

## Red checks

Check-runs at the previous head ace05371ed47a6a9d378883c9fefbad08315c343, read through the API (`commits/<sha>/check-runs`); 97f89cda has no PR run yet.

`typing` (job 112558412302) -- this pull request's own, fixed at this head. `tests/typing_ruler.py --mypy` printed `FAIL errors did not grow [recorded 0, measured 5 (+5)]` at ace05371 and `ALL 9 typing-ruler checks PASSED` at 97f89cda. Cheaper detector: the same ruler under the pinned toolchain locally, about 90 s once its venv exists; no seat recipe in `tools/audit/seat/` builds that venv, so a fixer meets it only in CI.

`delivery-status` (job 112558000084) -- printed `DELIVERY STATUS UNCHECKED — 42 rowed, 2 pending, 0 overdue`. It grades main, but ace05371 carried this pull request's row at the retired path `docs/delivery/2010.md`, which it reads; this head moves the row to `dev/programme/delivery/2010.md`, the path main now uses. Whatever remains at this head is main's pending rows. Cheaper detector: none beyond the check itself, which already runs on the pull request.

`fast (3.14)` (job 112558412447) -- this pull request's own, NOT fixed at this head. `tests/stress.py` printed `1 of 104 STRESS CHECKS FAILED`: "no scenario's production calls grew past what its work counts vouch for, on an unchanged plan (round 9)", with optimizer.py adding about 11 700 to 23 200 production calls per scenario (summer/1z/space 1.259x against the 1.05x allowance). The cause is the new idle classifiers in `optimizer.py`: `idle_reason` and its helpers run per idle step and recompute channel-wide aggregates (`_dearer_than_used` takes the maximum price over every step that ran, once per idle step). It is not the closures or mutation chain. Cheaper detector: `tests/stress.py` itself is the detector and is heavy; none cheaper exists, because only this ratchet counts interpreter work outside the named seams.

`mutation` (job 112558411932) -- refused 47 unpinned sites at ace05371 and measured none (`47 not started for --budget-minutes`). It awaits CI's measurement and the `mutation-autofix` chain at this head; the sites are unchanged in kind. Cheaper detector: none on a Mac, where the `tests/features.py` baseline is red on R9-F2.1 P3 and `--pin-killed` refuses.

`mutation-autofix` (job 112560320989) -- printed `skip-no-measurement -- THE REPAIR DID NOT HAPPEN`, a consequence of `mutation` measuring nothing. It awaits the same chain. Cheaper detector: none; it only reports what `mutation` measured.

`nightly-status` (job 112558411995) -- main's: `NIGHTLY FAILED: record-autofix failed last night` (scheduled run 37440269774). This diff touches none of its inputs. Cheaper detector: not this pull request's to name.

`env-matrix` (job 112557999944) -- main's: red on origin/main at 6001b09a in governance run 37531301054. This diff does not touch it. Cheaper detector: not this pull request's to name.

`pr-contract` (jobs 112558118698, 112575120196) -- red because the earlier body did not name `env-matrix`; this body names each red above. `budget-raise-gate` (job 112557999142) was cancelled, not failed; no `*_budgets.json` is in this diff.

`R9-F2.1 P3` inside `tests/features.py` -- red on this Mac at this head and at origin/main; the Mac BLAS solve, not this diff.

## Forward-carry

none

## Friction

fixer.md-step-2: unenforced: `mutation_table.py --pin-killed` cannot measure a diff whose sites only `tests/features.py` drives -- CI's 35-minute budget admits none, and a Mac's red baseline refuses the local run.
