Idle steps publish an exact sub-code when the solved plan shows why, and the Advisor hot-water row writes that recommended setpoint through `apply_schedule`, which stores it and the comfort target in the entry options. The card says Because for a published sub-code and keeps Likely because when the step is only idle. The what-if prices an active away setback. The payload's minimum temperature is the floor that solve used, and the configured floor is named beside it while they differ. The comfort-at-risk event carries the coldest step's published reason.

Part of #201. Leaves #201 open.

Closes #1795

_Requested by **tvofi**_.

## Head

a5379d67dd1f489c1083843b4fb0888df56812db

Merge base and origin/main e2a4f7c67b28622206016b4eb1032abe0fbe4621 (read 2026-10-08T00:30Z). a5379d67 is the previous PR head 5eaf0982 plus three merges of origin/main (8d7903e6, f6a962e2, e2a4f7c6) and one closures commit. 5eaf0982 contains the code head c75b7770, whose idle-classifier change (`idle_codes`, one pass per channel) was approved. None of this pull request's production, card, doc or ledger lines changed in those merges: see `## Delta`. The figures below that name c75b7770 or 97f89cda were taken there. The figures marked "at this head" were re-taken at a5379d67.

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

At this head: `git merge-base origin/main HEAD` is e2a4f7c67b28622206016b4eb1032abe0fbe4621. `python3 tests/closure.py select --diff e2a4f7c6... --workdir "$D"` printed `MODE: SCOPED -- 28 script(s) run, 5 scoped out`. `python3 tests/structure.py` printed `STRUCTURE RATCHET PASSED`. Under the CI venv's Python 3.14 with `PYTHONPATH=tests/hastub`, `tests/harness_headers.py` printed `ALL 109 HARNESS HEADER CHECKS PASSED` and `tests/entities.py` printed `ALL 2205 ENTITY CHECKS PASSED`. `PYTHONPATH=tests/hastub python3 tools/pr/ci_predict.py --base e2a4f7c6...` printed `no closures or fast red predicted` with 35 ADDED UNPINNED sites. Its null control is the tree before the closures commit, where it printed the INERT READS prediction CI's `closures` job failed on.

Taken at c75b7770 (merge base then 17f30f9cedf2a442592d3db01d1d2e708a55425b):

`python3 tests/closure.py select --diff $(git merge-base origin/main HEAD) --workdir "$D"` printed `MODE: SCOPED -- 26 script(s) run, 5 scoped out` at the first merge; scripts run locally at this head, `PYTHONPATH=tests/hastub`:

`python3 dev/audit/harnesses/ux5_idle_codes.py 97f89cdaf5fb7fbcc046b40d0d26f16164f3e88e HEAD $(git merge-base origin/main HEAD) 1 20000` -- `cases=216223`, `mismatches=0` (per-step `idle_reason` at 97f89cda against `idle_codes` here, step by step and through both classifiers); `base_calls=195`, `old_calls=2422`, `new_calls=249` optimizer.py calls for one 96-step `classify_space_steps` by `tests/stress.py`'s own `production_calls` meter, the old and new codes identical (`c2f1e8e08c44` both). Null control: the same run against a tree whose solar test read `>= 1e-6` printed `mismatches=509`.

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

Check-runs at the previous PR head 5eaf0982049135c33696f3e60f9fa86ebe460e00, read through the API (`commits/<sha>/check-runs`, 2026-10-07T20:05Z); this head has no run yet. Each red there, and each red the blocked review named at ace05371ed47a6a9d378883c9fefbad08315c343:

`closures` (job 112899052762) -- this pull request's own, repaired at this head. It printed `INERT READS UNDER-APPROXIMATED` for `tests/harness_headers.py` reading the ux5 harness this branch adds, which `inert_reads` did not list. Main has since moved the harness directory under `dev/audit/harnesses/`; the merge moves the harness with it, and this head adds `dev/audit/harnesses/ux5_idle_codes.py` to `inert_reads["tests/harness_headers.py"]` beside the eleven other harnesses there. The entry is copied, not recorded locally. Cheaper detector: `tools/pr/ci_predict.py`, which is now on main. At the tree before the closures commit it printed `PREDICT closures INERT READS tests/harness_headers.py: dev/audit/harnesses/ux5_idle_codes.py`. At this head it prints `no closures or fast red predicted`.

`closures-autofix` (job 112922379387) -- printed `skip-manual-repair-owed -- THE REPAIR DID NOT HAPPEN`. That is the status `ci-autofix.md` gives an INERT READS failure, so the repair was owed by hand. It is the `closures` entry above. Cheaper detector: the same predictor arm.

`mutation` (job 112898946065) -- `MUTATION TABLE REFUSED -- 4729 unpinned site(s) against 4693 ... 37 of them added by this diff`, with the diff's sites `not started: it would have overrun --budget-minutes`. Waiting on R9-CI-1. Each site the predictor names at this head is listed under `## Unpinned sites`. Cheaper detector: `tools/pr/ci_predict.py`'s ADDED UNPINNED arm names the sites in seconds. It cannot kill them, and on a Mac the `tests/features.py` baseline is red on R9-F2.1 P3, so `--pin-killed` refuses there.

`mutation-autofix` (job 112902087980) -- `skip-no-measurement -- THE REPAIR DID NOT HAPPEN`, because `mutation` measured nothing. It is waiting on the same R9-CI-1 chain. Cheaper detector: none, because it only reports what `mutation` measured.

`pr-contract` (job 112922569719) -- the earlier body did not name `closures` or `closures-autofix`. This body names every red above and below. Its preflight step also printed `REFUSE 'Closes #1795' ... not in the intended list` because the update was run without an issue list. This update passes `1795`.

`budget-raise-gate` (job 112898937855) -- cancelled, not failed. No `*_budgets.json` file is in this diff (`git diff --name-only e2a4f7c6...HEAD`). A cancelled twin blocks the merge until it is re-run, and re-running it is the orchestrator's job.

`delivery-status` (job 112898936538) -- main's: `DELIVERY STATUS OVERDUE — 54 rowed, 0 pending, 3 overdue` for #1917, #2003 and #2001, none of them this pull request's row. Cheaper detector: not this pull request's to name.

`nightly-status` (job 112898939520) -- main's: `NIGHTLY FAILED: mutation-ledger, mutation-nightly, record-autofix failed last night`. This diff touches none of its inputs. Cheaper detector: not this pull request's to name.

`env-matrix` -- red on origin/main at the review's base (governance run 37531301054). It was not red at 5eaf0982. If it reddens at this head, it is main's. Cheaper detector: not this pull request's to name.

`typing` -- named by the blocked review at ace05371 (`FAIL errors did not grow [recorded 0, measured 5 (+5)]`). Fixed by `_fold_away`'s `AwayFold` return type, and not red at 5eaf0982. Cheaper detector: `tests/typing_ruler.py --mypy` under the pinned toolchain, about 90 s once its venv exists.

`fast (3.14)` -- named at ace05371 for `tests/stress.py`'s production-call ratchet. The fix is c75b7770's `idle_codes`, one pass per channel, already approved. Not red at 5eaf0982.

`R9-F2.1 P3` inside `tests/features.py` -- red on this Mac at this head and at origin/main. It comes from the Mac BLAS solve, not from this diff.

## Unpinned sites

Every site `tools/pr/ci_predict.py --base e2a4f7c6` names as ADDED UNPINNED at this head (35 lines; at the tree before the closures commit it named the same 35):

- `custom_components/heatpump_optimizer/coordinator.py:1781 BOOLOP` -- pinned by mutation-autofix (awaiting R9-CI-1)
- `custom_components/heatpump_optimizer/coordinator.py:1781 RETURN_DEL` -- pinned by mutation-autofix (awaiting R9-CI-1)
- `custom_components/heatpump_optimizer/coordinator.py:1793 GUARD_OFF` -- pinned by mutation-autofix (awaiting R9-CI-1)
- `custom_components/heatpump_optimizer/coordinator.py:1797 GUARD_OFF` -- pinned by mutation-autofix (awaiting R9-CI-1)
- `custom_components/heatpump_optimizer/coordinator.py:1799 CLAMP_DROP` -- pinned by mutation-autofix (awaiting R9-CI-1)
- `custom_components/heatpump_optimizer/coordinator.py:1800 GUARD_OFF` -- pinned by mutation-autofix (awaiting R9-CI-1)
- `custom_components/heatpump_optimizer/notifier.py:94 GUARD_OFF` -- pinned by mutation-autofix (awaiting R9-CI-1)
- `custom_components/heatpump_optimizer/notifier.py:97 BOOLOP` -- pinned by mutation-autofix (awaiting R9-CI-1)
- `custom_components/heatpump_optimizer/notifier.py:97 GUARD_OFF` -- pinned by mutation-autofix (awaiting R9-CI-1)
- `custom_components/heatpump_optimizer/notifier.py:99 BOOLOP` -- pinned by mutation-autofix (awaiting R9-CI-1)
- `custom_components/heatpump_optimizer/notifier.py:99 RETURN_DEL` -- pinned by mutation-autofix (awaiting R9-CI-1)
- `custom_components/heatpump_optimizer/optimizer.py:1025 GUARD_OFF` -- pinned by mutation-autofix (awaiting R9-CI-1)
- `custom_components/heatpump_optimizer/optimizer.py:1026 CLAMP_DROP` -- pinned by mutation-autofix (awaiting R9-CI-1)
- `custom_components/heatpump_optimizer/optimizer.py:1053 CMP_BOUND` -- pinned by mutation-autofix (awaiting R9-CI-1)
- `custom_components/heatpump_optimizer/optimizer.py:1053 GUARD_OFF` -- pinned by mutation-autofix (awaiting R9-CI-1)
- `custom_components/heatpump_optimizer/optimizer.py:1061 GUARD_OFF` -- pinned by mutation-autofix (awaiting R9-CI-1)
- `custom_components/heatpump_optimizer/optimizer.py:1063 CLAMP_DROP` -- pinned by mutation-autofix (awaiting R9-CI-1)
- `custom_components/heatpump_optimizer/optimizer.py:1063 CMP_BOUND` -- pinned by mutation-autofix (awaiting R9-CI-1)
- `custom_components/heatpump_optimizer/optimizer.py:1065 BOOLOP` -- pinned by mutation-autofix (awaiting R9-CI-1)
- `custom_components/heatpump_optimizer/optimizer.py:1065 GUARD_OFF` -- pinned by mutation-autofix (awaiting R9-CI-1)
- `custom_components/heatpump_optimizer/optimizer.py:1066 CLAMP_DROP` -- pinned by mutation-autofix (awaiting R9-CI-1)
- `custom_components/heatpump_optimizer/optimizer.py:1067 CMP_BOUND` -- pinned by mutation-autofix (awaiting R9-CI-1)
- `custom_components/heatpump_optimizer/optimizer.py:1068 GUARD_OFF` -- pinned by mutation-autofix (awaiting R9-CI-1)
- `custom_components/heatpump_optimizer/optimizer.py:1069 CMP_BOUND` -- pinned by mutation-autofix (awaiting R9-CI-1)
- `custom_components/heatpump_optimizer/optimizer.py:1072 GUARD_OFF` -- pinned by mutation-autofix (awaiting R9-CI-1)
- `custom_components/heatpump_optimizer/optimizer.py:1074 CMP_BOUND` -- pinned by mutation-autofix (awaiting R9-CI-1)
- `custom_components/heatpump_optimizer/optimizer.py:1075 CLAMP_DROP` -- pinned by mutation-autofix (awaiting R9-CI-1)
- `custom_components/heatpump_optimizer/optimizer.py:1076 CMP_BOUND` -- pinned by mutation-autofix (awaiting R9-CI-1)
- `custom_components/heatpump_optimizer/optimizer.py:1079 CMP_BOUND` -- pinned by mutation-autofix (awaiting R9-CI-1)
- `custom_components/heatpump_optimizer/optimizer.py:1080 CMP_BOUND` -- pinned by mutation-autofix (awaiting R9-CI-1)
- `custom_components/heatpump_optimizer/optimizer.py:1081 CMP_BOUND` -- pinned by mutation-autofix (awaiting R9-CI-1)
- `custom_components/heatpump_optimizer/optimizer.py:1082 RETURN_DEL` -- pinned by mutation-autofix (awaiting R9-CI-1)
- `custom_components/heatpump_optimizer/optimizer.py:1299 GUARD_OFF` -- pinned by mutation-autofix (awaiting R9-CI-1)
- `custom_components/heatpump_optimizer/optimizer.py:4035 RETURN_DEL` -- pinned by mutation-autofix (awaiting R9-CI-1)
- `custom_components/heatpump_optimizer/services.py:1037 GUARD_OFF` -- pinned by mutation-autofix (awaiting R9-CI-1)

## Delta

Since the previous PR head 5eaf0982 and the approved code head c75b7770:

- Merges of origin/main 8d7903e6, f6a962e2 and e2a4f7c6. Conflicts came only at 8d7903e6:
  - `tests/features.py`: two blocks appended at the same place. Both are kept, UX-5 first, then R9-DBG-1.
  - `tests/golden/claimed_drift.txt`: main dropped the R9-DIAG-2S claims and their note. This branch's R9-UX-5 list is kept, and the R9-DIAG-2S note (stale once its claims were gone) is dropped.
  - `ux5_idle_codes.py`: this branch added it inside the harness directory that main renamed. Moved to `dev/audit/harnesses/`, with its usage line updated.
- One commit adds the `inert_reads` entry (see `## Red checks`, `closures`).

What did not change: `git diff <base> c75b7770` and `git diff e2a4f7c6 HEAD`, over `custom_components docs blueprints tests/card.mjs tests/entities.py tests/features.py tests/golden tests/mutation_ledger` (the base being `git merge-base e2a4f7c6 c75b7770`), restricted to their `+`/`-` lines, differ only in the claim-file resolution above and two blank separator lines. Left side 941 lines, right side 933. The comparison ran under bash with the path list word-split. The same comparison first ran under zsh, which passed the list as one pathspec, matched nothing, and printed an empty diff on both sides. The null control caught it: a path the head does change, `tests/closures.json`, came back identical too.

## Forward-carry

none

## Friction

fixer.md-step-2: unenforced: `mutation_table.py --pin-killed` cannot measure a diff whose sites only `tests/features.py` drives -- CI's 35-minute budget admits none, and a Mac's red baseline refuses the local run.
