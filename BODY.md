R10-COP-PARTLOAD: price the compressor's power in COP, off by default

`ThermalModel.compute_cop` priced efficiency from outdoor temperature, humidity and flow or tank temperature only; electrical power entered every heat conversion as a plain multiplier, `heat = cop * power`. `ThermalParameters.cop_partload_derate` (options flow `heat_pump_cop_partload_derate`, default 0) is the share of COP lost at maximum power against the floor, linear across the band, refused to 0 at or past `partload_derate_limit`. `thermal_model.delivered_heat_kw` and `heat_per_cop_kw` apply it at the priced forward conversions. At the default 0 they return `cop * power` unchanged, so no existing install's plan moves. Every save that can move the band or the derate judges the derate against the band it leaves (`config_flow._partload_errors`, and `_prefill_errors` on `base`).

Root-cause analysis: `dev/audit/rca/R10-RCA-COP-PARTLOAD.md`.

## Re-cut

This body replaces the round history and the earlier merge narratives. It describes the tree at the head below: the previous head `27bb23875cf0248028d243b4643523e6f4c7f04e` plus one merge of origin/main. Production code and tests are unchanged by this merge (see `## Head`), so the mutation proof, null control, band-writer census and harness readings recorded on the previous body at `3dbefe25f`/`9b24795b2`/`f4dc68a48` are carried by reference to that body's text at `27bb2387`, not restated here.

## Head

`7d9ac8b81d4caf13da90796c3d5d699750b7e721` is the head measured (2026-10-30T06:29Z). It is one merge, by the fixer seat, of origin/main `1148ee635e8278ebbb033b524d54001b2a89218c` (after #2917) into the PR's previous head `27bb23875cf0248028d243b4643523e6f4c7f04e`; it was owed because `git merge-tree --write-tree origin/main 27bb2387` conflicted.

Resolution delta:

- One conflict, `tests/golden/claimed_drift.txt`: both sides rewrote the bare claim list. Resolved to main's list verbatim plus this branch's own diff's one claim, `config_flow` (R10-COP-PARTLOAD). Main's lines are inert until `stamp.py` empties them (`claim-files.md`). The previous head's R10-HOUSE-GRADE and R10-BUFFER-STORE lines were inherited from the older merge base, not this branch's diff, and are dropped.
- The brief expected `coord_all_features`, `coord_dhw`, `coord_grid_fee`, `coord_minimal` and `coord_two_zone` to be claimed here. Re-verified at the merge base, they do not move: `env_drift.py --all` reads each `byte-identical to origin/main here`, and a claim of them would be stale. They are therefore not claimed. Main's own R10-COP-GATE lines for those five (written by #2917's diff) stay as main has them.
- Auto-merged: `tests/features.py`, `tests/structure_budgets.json`, `tests/closures.json`, and mutation-ledger files (ledger drivers); no production file conflicted.

Three-dot checks at the head: `git merge-tree --write-tree origin/main HEAD` exits 0; `git diff --stat $(git merge-base origin/main HEAD)...HEAD -- VERSION RELEASE_NOTES.md custom_components/heatpump_optimizer/manifest.json` prints nothing (0 lines).

## Mutation proof

Not re-run: the merge adds no production line and no conflict touched one. The proof recorded for the fix (`_partload_errors`, `_prefill_errors`, `partload_factor`, the resolved `thermal_model.py` line; M1 to M5 on the previous body) stands, and the pinned-mutant ledger files are carried unchanged. CI's required mutation check remains the arbiter.

## Null control

`GOLDEN_MODE=drift` against origin/main `1148ee635`, `PYTHONPATH=tests/hastub python3 tests/env_drift.py --all`, exits 0 and prints `CLAIMED config_flow: 2 leaves moved`, `NO UNCLAIMED DRIFT: 56 scenario(s) checked against origin/main` and `NO STALE FIXTURE: 56 committed fixture(s) still match what this tree computes`. Its own null: the same run lists `config_flow` as moved (two `present on one side only` leaves), so it can see a moved fixture, and the five coord fixtures read byte-identical beside it.

## Figures

All at `7d9ac8b81`, origin/main `1148ee635`, 2026-10-30T06:29Z.

- Scope: `python3 tests/closure.py select --diff $(git merge-base origin/main HEAD) --workdir "$D"` prints `MODE: SCOPED -- 30 script(s) run, 3 scoped out.`
- `GATE_SCOPE=auto GOLDEN_MODE=drift GOLDEN_REF=origin/main PYTHONPATH=tests/hastub bash tests/run.sh`: `MODE: SCOPED`, ends `32 TEST SCRIPT(S) PASSED; 2 SCOPED OUT AND NOT RUN`, exit 0 (scoped out: `tests/arch_score.py`, `tests/ha_contract.py`).
- `python3 tests/structure.py`: `STRUCTURE RATCHET PASSED`.
- `PYTHONPATH=tests/hastub python3 tools/pr/ci_predict.py --base origin/main`: `CI PREDICT: no closures, fast, wave-script or instrument red predicted against 1148ee635e82`.
- `python3 tools/audit/archscore/score.py --diff origin/main`: `Architecture score: dS +0.0000 NULL`.
- Class enumeration: no new class beyond the previous body's `## Band writers` census; this merge changes no band writer.
- Not run locally: `tools/pr/prepr.sh` in full; `body_push.sh` runs its static predictor.

## Red checks

Read from the check-runs of PR #2872 (`pull_request_read get_check_runs`, then `get_job_logs` for the one red; `failure_logs.sh` needs `gh` auth, which this seat lacks). At the live head `27bb2387` the newest run of every named check except `nightly-status` is `success` (`tests / fast (3.14)`, `tests / typing`, `tests / mutation`, `governance / delivery-status`, `budget-raise-gate / budget-raise-gate`) or `skipped` (`tests / mutation-autofix`, which runs only after a red `mutation`). The reds below were red on earlier heads of this branch or on the superseded `DIRTY` head; each is answered for the defect that turned it red.

- `tests / nightly-status`: red at `27bb2387`. Its log reads `NIGHTLY FAILED: slow failed in the last verification dispatch`, run 40948493872 at head `e5ddba1`, 2026-10-29T20:22Z. It grades main's last concluded nightly dispatch and says itself that it is not a required context. This diff touches neither `nightly.yml` nor the `slow` lane's inputs, so the red is main's and not this PR's. The cause is outside this change; the nightly's owner is the orchestrator seat, which owes the `gh workflow run nightly.yml --ref main` proof. Cheaper detector: none, the check is the cheap detector for a red nightly.
- `governance / delivery-status`: red earlier, green at the head. It grades main's delivery record and this diff touches none of what it reads except its own `dev/programme/delivery/2872.md`. Main-graded, not this PR's; no cheaper detector.
- `budget-raise-gate / budget-raise-gate`: red in this branch's ancestry at `fe964895e`, when `class_excess_loc` rose; paid in code by `2f082ee3b` and green since. At `7d9ac8b81` this diff raises no cap: `git diff $(git merge-base origin/main HEAD)...HEAD -- tests/structure_budgets.json` moves `class_excess_loc` 17724 to 17672, which is down, and `python3 -I tools/policy/budget_raise_gate.py --check-body BODY.md --base origin/main --head HEAD` prints `the diff raises no cap, and the body has no raise section to judge`. This body therefore carries no raise section: rule 2 requires one only for a raise, and none exists. Cheaper detector: `python3 tests/structure.py` names a growing row locally before the push for about 30 s; it is the standing detector and was run (`STRUCTURE RATCHET PASSED`).
- `tests / fast (3.14)`: red in the ancestry at `fe964895e` (`tests/finite_boundary.py`: `_partload_derate` read its option through a bare `float()`, repaired by `54437ac84`) and at three later heads; green at the live head. Cheaper detector: the scoped gate (`GATE_SCOPE=auto bash tests/run.sh`) locally, minutes against CI's half hour, run before the handoff and passing (`## Figures`).
- `tests / typing`: red in the ancestry at `fe964895e`, `bf1983846` and `d2e128d49` (`no-any-return` +1), repaired by `eeb7430a6`; green at the head. Cheaper detector: `tests/typing_ruler.py`, about 1 s locally.
- `tests / mutation` and `tests / mutation-autofix`: red in the ancestry while a push added unpinned killed sites; the bot's `ci: pin killed mutants` commits pinned them and `mutation` is green at the live head. The two merges since add no production site. Cheaper detector: `prepr.sh` step 6d, whose predictor `ci_predict.py` prints no red at this head (`## Unpinned sites`).

## Unpinned sites

none: the predictor above names none, and the merge adds no production site.

## Forward-carry

- Carry 1, the inverse conversions: they still close the loop with `heat / cop`: `dhw_planner._plan_dhw_min_cost`, `_clamp_dhw_to_capacity`, `optimizer._compute_baseline_power` and `coordinator._dhw_setpoint_sweep`. With a derate the forward relation is quadratic in power, so the closed form understates the electrical power needed for a given heat, by up to the derate. At the default 0 the current forms are exact.

  Carry: R10-COP-PARTLOAD
- Carry 2, D2's brief: D2's item 2 lists the inputs its COP step sweeps, and power is not among them. The countermeasure is one sentence in `dev/governance/dimensions/D2.md`: derive the priced formula's inputs from the device's own control surface. That is policy, which the owner approves; this seat did not edit it.

  Carry: R10-COP-PARTLOAD
- Carry 3, the live buffer store's 2.5x CPU cost and the 272 s owner-box outlier (R10-BUFFER-STORE's carry onto this group): not this PR's. The diff adds no planner search, bound or warm start. Carried forward unchanged.

  Carry: R10-COP-PARTLOAD
- Carry 4, the inline 35 L buffer fallback in the two-zone and batch steps: not touched here. Carried forward unchanged, to the group that next prices that family in `optimizer.py`.

  Carry: R10-COP-PARTLOAD

## Friction

none

## Architecture score

Architecture score: dS +0.0000 NULL (`python3 tools/audit/archscore/score.py --diff origin/main`, origin/main `1148ee635`, at `7d9ac8b81`).
