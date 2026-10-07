Idle steps publish an exact sub-code when the solved plan shows why, and the Advisor hot-water row writes that recommended setpoint through `apply_schedule`, which stores it and the comfort target in the entry options. The card says Because for a published sub-code and keeps Likely because when the step is only idle. The what-if prices an active away setback. The payload's minimum temperature is the floor that solve used, and the configured floor is named beside it while they differ. The comfort-at-risk event carries the coldest step's published reason.

Part of #201. Leaves #201 open.

Closes #1795

_Requested by **tvofi**_.

## Head

c75b7770a88e0e9937bc03068014db0d672a4697

Merge base and origin/main 17f30f9cedf2a442592d3db01d1d2e708a55425b (read 2026-10-07T14:21:02Z). c75b7770 is 97f89cda plus one commit: the idle classifiers read a channel once (`idle_codes`) instead of once per idle step, the per-step `idle_reason` and its three helpers are gone, and `tools/audit/harnesses/ux5_idle_codes.py` lands. Since the blocked head ace05371ed47a6a9d378883c9fefbad08315c343 (verdict comment 6027912894): `_fold_away` is typed against the away state and returns a new `AwayFold` TypedDict in `payload.py`; `tests/features.py` gains value checks on the idle-reason helpers, the away fold and the comfort cause; one equivalent `RETURN_DEL` is triaged under `tests/mutation_ledger/survivor_triage/notifier.py/`; the advisor and plan-why pages are regenerated at the merged tree; origin/main is merged twice, and the delivery row now sits at `dev/programme/delivery/2010.md`. A spread of the local view inside `_fold_away` was tried and reverted (c0a3e641): `tests/entities.py` EG-B3 resolves a payload merge source by its call and reported `[['view']]` unresolved.

## Mutation proof

In `idle_codes`, the line `codes[_padded(caps, n) <= threshold] = REASON_IDLE_FUSE` was deleted. In `_fold_away`, the two lines `if floor == float(configured): return view` were deleted. A probe ran the inputs of the features checks "UX-5 an idle step whose fuse cap leaves no room says the fuse" and "UX-5 a setback equal to the floor does not name a second one" against a `git archive` of c75b7770, mutated and restored:

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

`python3 tools/audit/harnesses/ux5_idle_codes.py 97f89cdaf5fb7fbcc046b40d0d26f16164f3e88e HEAD $(git merge-base origin/main HEAD) 1 20000` -- `cases=216223`, `mismatches=0` (per-step `idle_reason` at 97f89cda against `idle_codes` here, step by step and through both classifiers); `base_calls=195`, `old_calls=2422`, `new_calls=249` optimizer.py calls for one 96-step `classify_space_steps` by `tests/stress.py`'s own `production_calls` meter, the old and new codes identical (`c2f1e8e08c44` both). Null control: the same run against a tree whose solar test read `>= 1e-6` printed `mismatches=509`.

`python3 tests/structure.py` -- `STRUCTURE RATCHET PASSED` (a first cut kept the per-step wrapper for the checks and failed `dead_top_level_symbols 2 > 1`; the checks now index `idle_codes`).

`PYTHONPATH=tests/hastub:custom_components:tests python3 tests/harness_headers.py` -- `ALL 109 HARNESS HEADER CHECKS PASSED`; `python3 -I tools/audit/seat/tmp_paths.py --check` -- `0 refused`.

`python3 tests/entities.py` -- `ALL 2200 ENTITY CHECKS PASSED`.

`node tests/card.mjs` -- `ALL CARD CHECKS PASSED` (after `tests/plan_view.py` printed `plan reason codes, price provenance and slot energy OK` at this head).

`node tests/card_drift.mjs origin/main` -- `2 state(s) moved and claimed, 38 identical`.

`node tests/md_tables.mjs` -- `doc_misrendered_lines=0` (at 97f89cda; this head's commit touches no doc).

`python3 tests/doc_claims.py` -- `ALL 160 checks PASSED` (at 97f89cda; this head's commit touches no doc).

`.venv-typing/bin/python tests/typing_ruler.py --mypy` -- `ALL 9 typing-ruler checks PASSED`.

`python3 tests/env_drift.py --all origin/main` -- `NO UNCLAIMED DRIFT: 56 scenario(s) checked against origin/main` and `NO STALE FIXTURE: 56 committed fixture(s) still match what this tree computes`, at 97f89cda. Not re-run at this head (heavy); the classifier change is output-identical by the harness above, and CI's `fast` runs it.

`tests/features.py`'s UX-5 block, run statement by statement with a stub `R` (a scratch probe; statements needing names from earlier blocks skipped, 18 of them) -- `checks_run=43 failed=0` at this head and at 97f89cda; with the coasting margin 0.15 mutated to 0.10, `failed=1` ("UX-5 a step exactly 0.15 above the floor is not coasting"). The whole of `tests/features.py` is CI's.

`HPO_PAGES_OUT=<dir> node tests/card_browser.mjs` with `tests/pwlane`'s Playwright -- the advisor and plan-why pages written into `docs/img/card/`; the run's one failure, `P9 grid: no two text runs share ink` (`text "2" x text "3"`), fails identically on a `git archive` of origin/main 3910026e on this Mac. At the first merge the generator reproduced the committed advisor and plan-why PNGs byte for byte (`cmp`).

The heavy scope.run scripts (`tests/stress.py`, `tests/golden.py`, `tests/boost_drift_replay.py`, `tests/optimality.py`, `tests/backtest.py` and the rest) are left to CI on #2010 at this head, by tvofi's 2026-10-07 rule that heavy scripts run in CI; their results are CI's check-runs, not figures in this body. Before that rule, `tests/arch_score_head.py` and `tests/backtest.py` exited 0 locally at 13fc4a45.

## Red checks

Check-runs at the previous head ace05371ed47a6a9d378883c9fefbad08315c343, read through the API (`commits/<sha>/check-runs`); neither 97f89cda nor this head has a PR run yet.

`typing` (job 112558412302) -- this pull request's own, fixed at this head. `tests/typing_ruler.py --mypy` printed `FAIL errors did not grow [recorded 0, measured 5 (+5)]` at ace05371 and `ALL 9 typing-ruler checks PASSED` at 97f89cda. Cheaper detector: the same ruler under the pinned toolchain locally, about 90 s once its venv exists; no seat recipe in `tools/audit/seat/` builds that venv, so a fixer meets it only in CI.

`delivery-status` (job 112558000084) -- printed `DELIVERY STATUS UNCHECKED — 42 rowed, 2 pending, 0 overdue`. It grades main, but ace05371 carried this pull request's row at the retired path `docs/delivery/2010.md`, which it reads; this head moves the row to `dev/programme/delivery/2010.md`, the path main now uses. Whatever remains at this head is main's pending rows. Cheaper detector: none beyond the check itself, which already runs on the pull request.

`fast (3.14)` (job 112558412447) -- this pull request's own; fixed at c75b7770, pending CI's `tests/stress.py`. At ace05371 `tests/stress.py` printed `1 of 104 STRESS CHECKS FAILED`: "no scenario's production calls grew past what its work counts vouch for, on an unchanged plan (round 9)", optimizer.py adding about 11 700 to 23 200 production calls per scenario (summer/1z/space 1.259x against the 1.05x allowance). The cause was `idle_reason` running per idle step and recomputing channel-wide values (the dearest used price, a forward scan for the next run and next surplus). `idle_codes` reads the channel once; on one 96-step plan the meter reads 2422 calls before and 249 after against 195 at the merge base, outputs identical. Whether every stress scenario is back under 1.05x is CI's to confirm. Cheaper detector: `tools/audit/harnesses/ux5_idle_codes.py`'s call count, seconds, for this classifier only; for interpreter work in general none cheaper than `tests/stress.py` exists, because only that ratchet counts work outside the named seams.

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
