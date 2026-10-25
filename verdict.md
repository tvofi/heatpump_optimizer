Fix review: merge 627aea6dd97a1743b17a20efdff55d351f338f95

bus-nonce: 7a132fb254c601620fc3d482a63fe407

Delta review of #2775 (R10-LEARNER-ETA, branch `fix/r10-learner-eta-r3`) at its live head `627aea6dd97a1743b17a20efdff55d351f338f95`. Round: r5 delta. The full r5 review is verdict/2775 `afc2678c9`, a merge verdict at `af3b69b4d`. That verdict was never posted, so this one judges only (1) whether the posted r4 block (comment 6393460197, at `3b5ffde57`) is closed, (2) the delta `af3b69b4d..627aea6dd`, and (3) CI at the live head.

Roles check: my checkout is origin/main `b89fea13e`. `git diff $(git merge-base origin/main HEAD)...origin/main -- dev/governance/roles/` prints nothing, so the contract I followed is current. The head was re-read on the PR before this verdict was written: still `627aea6dd`.

## Findings

- The PR body's `## Red checks` still says `none`, and it covers only `3b5ffde57`. The intermediate head `af3b69b4d` was red on `tests / mutation` (`ADDED UNPINNED coordinator.py:1435 CMP_BOUND`, in the r5 verdict's evidence). The body names that site under `## Unpinned sites`, and `41f882a9a` pinned it, which is the answer ci-autofix.md accepts. `pr-contract` is green at the live head. However, the `## Red checks` line is stale: it should name that red and the pin. This repeats the r5 verdict's finding, which is not yet settled. Carry: R10-LEARNER-ETA
- `custom_components/heatpump_optimizer/sensor.py` is in R10-COP-GATE's roster `files`, and that group is unmerged. This PR adds `learner_progress` to `ModelStatusSensor.extra_state_attributes` (sensor.py:2043) and to `_unrecorded_attributes` (sensor.py:1996), next to the `cop` row COP-GATE edits. COP-GATE's fixer must keep both lines. The r5 verdict carried this, but the carry was never posted. The R10-COP-GATE entry in `dev/programme/rosters/wave-r10-groups.json` mentions `learner_progress` neither on origin/main `b89fea13e` nor at this head. Carry: R10-COP-GATE

## Evidence

- (1) The r4 block is closed at both `af3b69b4d` and the live head. I re-derived its named defects at the live head:
  - **The sensor exposes the field.** `ModelStatusSensor` publishes `"learner_progress": data.get("learner_progress")` (sensor.py:2043), and the key is in `_unrecorded_attributes` (sensor.py:1996) (`ev/sensor_head.txt`).
  - **Mutants MS and MU kill that wiring.** MS deletes the attribute line and MU drops the key from `_unrecorded_attributes`. Each takes `tests/features.py` to exit 1, `1 of 4387`, on `R10-LEARNER-ETA: the Health tab's source sensor publishes learner_progress as the view has it` (`ev/mut_MS.txt`, `ev/mut_MU.txt`).
  - **The dark-gate finding is closed.** coordinator.py:1424 has `darker = "darker" if is_sunlit_interval(...)`, :1431 has `house_wait = house_cold or darker`, and the lower learner has `or darker` at :1444 (`ev/darker_head.txt`). Mutant MD (`darker = None`) exits 1 on `in the sun the dark-gated learners wait for dark, and the aperture counts` (`ev/mut_MD.txt`).
  - **The carry-wording and census findings are closed.** Neither was touched by the delta (see (2)). The r5 verdict established both at `af3b69b4d`.
- (2) The delta `af3b69b4d..627aea6dd` has two first-parent commits:
  - `41f882a9a`, github-actions[bot] `ci: pin killed mutants`: one file, 6 added lines (`ev/bot_commit.txt`, `ev/pin.json`).
  - `627aea6dd`, a merge of origin/main `de794b537`.
  - The other commits in the range are main's own (`ev/delta.txt`).
- Per-file three-dot comparison. For each file, I compared the PR's changed lines against its own merge base: `f40142d66...af3b69b4d` and `de794b537...627aea6dd`. I took the `+`/`-` lines of `git diff MB...HEAD -- <file>`, dropped the headers, and compared sha1s. The file sets are 49 and 50. The only difference is the added `tests/mutation_ledger/killed_by/coordinator.py/learner_progress_view.CMP_BOUND.fc8f0966.json`, and no other file's changed lines differ (`ev/delta.txt`). So the authored change at the live head is the reviewed change at `af3b69b4d` plus that pin.
- The pinned mutant is killed. I applied the pin's mutant (`irradiance < SOLAR_APERTURE_MIN_IRRADIANCE` → `<=` at coordinator.py:1435) in a fresh detached worktree at the live head. `tests/features.py` exited 1, `1 of 4387`, on `R10-LEARNER-ETA: the ΔT and irradiance edges admit a sample, and the gate count settles` (`ev/mut_PIN_fc8f0966.txt`). This matches the pin's `killed_by: tests/features.py`.
- The brief says "the six pinned mutants". The delta adds one pin file of six lines, which holds one mutant. I covered "six" two ways:
  - **CI's re-verification.** At the live head, `tests / mutation` printed `PIN RE-VERIFICATION: 6 reproduced, 0 not reproduced, 0 not re-verified`. It covers coordinator.py:1399 CLAMP_DROP, :1448 CMP_BOUND, :1458 RETURN_DEL, and learner_progress.py:87 GUARD_OFF, :127 CMP_BOUND and :127 BOOLOP, each killed by `tests/features.py`. It also printed `0 survivor(s) of 6 evaluated` and `MUTATION TABLE PASSED`. The baselines were `env_drift.py` rc=0 and `features.py` rc=0, and the null survived, so the green is a real pass, not INCONCLUSIVE (`ev/ci_mutation_627aea6dd.txt`).
  - **My own runs.** I ran every `learner_progress_view` pin in coordinator.py at the live head: fc8f0966, 42520d5a, 99aab500, 5494e5cb and 959b8308. All exit 1. Four exit with `1 of 4387 FEATURE CHECKS FAILED` on R10-LEARNER-ETA checks. 5494e5cb (`return` → `pass`) dies with `TypeError: 'NoneType' object is not subscriptable` inside the R10-LEARNER-ETA block, at features.py:21322 (`ev/mut_PIN_*.txt`, `ev/mut_PIN_5494e5cb_full.txt`).
  - **Controls.** Unmutated head: exit 0, `ALL 4387 FEATURE CHECKS PASSED` (`ev/mut_BASE.txt`). Null (a trailing comment on `MIN_RATE_WINDOW_DAYS = 1.0` in learner_progress.py): exit 0, `ALL 4387` (`ev/mut_NULL.txt`).
- The count is 4387 here, against the body's 4384. The difference is main's checks merged in since `af3b69b4d`. The body's figure was taken at `7774f7e2d`.
- (3) CI at the live head, read after every run had concluded:
  - All 55 check runs are `success` or `skipped`, and none is failure, cancelled or pending.
  - Green runs include `gate` (both runs), `pr-contract / pr-contract` (both runs, the last started 09:57:44Z after every other run had concluded), `tests / fast (3.14)`, `tests / closures`, `tests / mutation`, `tests / coverage`, `tests / typing`, `tests / browser`, `tests / replay`, `codeql / Analyze (python)`, `arch-score`, `budget-raise-gate`, `governance / delivery-status`, `tests / nightly-status`, `governance / instrument-self-tests`, `hassfest` and `validate-hacs`.
  - The live head introduced no red.
- Step 13: `git merge-tree --write-tree origin/main 627aea6dd` against the current origin/main `b89fea13e` exited 0, with no conflict and no MERGE-CLAIM line (`ev/merge_tree.txt`).
- Step 4: in a worktree at the live head, `tests/env_drift.py --all de794b537` exited 0, printing `NO UNCLAIMED DRIFT: 56 scenario(s)` and `NO STALE FIXTURE: 56`. Exactly the five `coord_*` fixtures read `CLAIMED ...: 2 leaves moved` (R10-LEARNER-ETA). `--claims-only` printed `claims hygiene: origin/main ok` (`ev/env_drift_all.txt`). Three-dot, the only claim file touched is `tests/golden/claimed_drift.txt`. `card_claimed_drift.txt` is untouched.
- Step 5: three-dot from `de794b537`, `VERSION`, `manifest.json` and `RELEASE_NOTES.md` show no diff. No `*budgets*.json` differs (`ev/static_checks.txt`).
- Structure at the live head: `python3 tests/structure.py` exited 0 with `STRUCTURE RATCHET PASSED` and `ok seam_cut_total 420 <= 420` (`ev/structure_head.txt`).
- Step 12 carry: `af3b69b4d`'s merge verdict had no reviewer turn and was not `head-moved`. The move since then is a bot ledger pin plus one automatic main merge. The PR's own changed lines are identical apart from the pin, so this delta is the resolution delta, and I judged it sound.
- Not re-derived, because they are carried from the r5 verdict at `af3b69b4d` and the delta touches no file they read: the finder's harness and companion figures, the census, and `Architecture score: dS +0.0006`. CI `arch-score` is green at the live head.

UNCERTAINTIES: none on the delta. The roster scan for the COP-GATE carry looked only for the string `learner_progress` in that group's entry.
