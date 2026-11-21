Part of #3616 (the room lift made visible; R11-OUTSIDE-ROOMS-3B)

Built to the approved design `design/R11-OUTSIDE-ROOMS-3B` at `09049ddb` (`Design review: approve`, design-verdict `5554b972`), on `origin/main` `e698fc8ac374a1d72c230b55d938d75b03b7de67`. The why-now comfort-floor row and the daily narrative published the room lift as "holding the minimum temperature": the lift reached the solve folded into `min_temp_margins`, and nothing on the solve's result said which part of the floor was the rooms'. The plan is not changed: no variable, constraint or objective term moves, and `temp_min_bounds` is the same array (invariant iii, measured under `## Null control`).

## What it does

- **`rooms.floor_limits`** returns both `SolveLimits` floor keywords from one computation, as a `FloorLimits` mapping: `min_temp_margins` (the base plus the lift, what `rooms.lifted` returned) and `room_lifts` (the lift alone, None where no step is lifted). Both coordinator builds splat it in place of their `min_temp_margins=` argument; the what-if passes the baseline's held lift as before (P2 carry r4). `rooms.lifted` is removed; its callers in `tests/` and `dev/audit/harnesses/room_lift_solve.py` read `floor_limits(...)["min_temp_margins"]`.
- **`SolveLimits.room_lifts`** (attribution only) and **`_Horizon.room_lifts`**: `_build_comfort_bounds` runs the T5 bound arithmetic, now the module function `_raised_floor`, a second time on the margins less the lift, and records the held floor less that floor, clipped at 0. It is 0 where the mold floor or the ceiling clip covers the lift and None without input.
- **`room_floor`** (`payload.REASON_ROOM_FLOOR`): `_mark_room_floor` relabels a `comfort_floor` step whose next temperature is above the floor less the lift plus 0.15 K. Not idle, not in `_MANUAL_KEEP_REASONS`. Registered in `narrative.TEMPLATES` (en, sv, de), `strings.json`, the three translations, `icons.json` and the card's `REASON_LABELS` and reason strings.
- **`room_lift`** (`slot_drivers.DRIVER_CODES`, after `comfort_floor`): `slot_drivers.space_pushes` reads the comfort push against the floor less the lift and a room-lift push of the lift over the unchanged half band, clipped to [0, 1]; the row is present only where `h.room_lifts` is not None. `space_drivers` normalises those pushes as before. The card has the label and explanation in three languages; `docs/dashboard-card.md` and `docs/configuration.md` name both.

Departure from the note, raised here: **interface 4 is a post-pass, not a keyword on `classify_space_steps`.** The keyword form took `classify_space_steps` to 11 parameters, which `tools/audit/archscore/score.py --diff e698fc8ac3` refused (`params_over_10 6 -> 7`, `dS -0.1926 WORSENS (inadmissible)`). `_mark_room_floor` runs on the classifier's output before `_mark_manual_reasons` and `_mark_blocked_reasons`, the existing relabel passes, with the same 0.15 K test against the same arrays, so every label and rank is the keyword form's. At the head the score reads `dS +0.0000 NULL`.

Proposed wording, for the owner's decision the note routes (card and narrative text in en, sv, de):

| where | en | sv | de |
|---|---|---|---|
| narrative | lifting the floor for a room below its target took {kwh} kWh ({cost} {currency}) | att lyfta golvet för ett rum under sin måltemperatur tog … | das Anheben der Untergrenze für einen Raum unter seiner Zieltemperatur kostete … |
| reason / `plan_narrative` state | Lifting the floor for a room below its target | Lyfter golvet för ett rum under sin måltemperatur | Untergrenze für einen Raum unter seiner Zieltemperatur angehoben (state), … anheben (card) |
| why-now driver | Room lift | Rumslyft | Raumanhebung |

The room is named as a cause, not by entity (the note's routed decision): its entity stays on `rooms.lift.entity`.

## Head

`ddfc28e0993ed0bb7822eed43ecfe9b353947d9a`

## Mutation proof

Failing test first: the 3B block of `tests/features.py` over the base's production code stopped at its first check, `TypeError: classify_space_steps() got an unexpected keyword argument 'room_lifts'` (the keyword form, before the post-pass rework), and `tests/edge.py`'s `room lift named` check needs `rooms.floor_limits`, absent at the base.

Targeted mutants, each applied alone to a copy of the head and the 3B block run with `PYTHONPATH=tests/hastub python3 tools/audit/seat/features_block.py --prelude 'exec(open("P").read())' 'R.section("#3616 R11-OUTSIDE-ROOMS-3B'`, P written by `features_block.py --emit-prelude P` with the same marker. Unmutated: `ALL 7 FEATURES BLOCK PASSED` (8 at the head, with the boundary check below). Each mutant made it exit 1:

- M1 `_mark_room_floor` `0.15` -> `0.5`: `FAIL R11-OUTSIDE-ROOMS-3B: a heating step within 0.15 K of the lifted floor but above the floor less the lift is room_floor ...`
- M2 `_mark_room_floor` drops `- room_lifts[i]` from its comparison: the same check.
- M3 the unlifted-bounds build without `- _padded_nonneg(room_lifts, n_steps)`: `FAIL R11-OUTSIDE-ROOMS-3B: the solve's room lifts are the held floor less the floor without the lift ...`
- M4 `space_pushes` gives a zero `room_lift` row with no lift: `FAIL R11-OUTSIDE-ROOMS-3B null control: room_lifts None gives the five pre-3B codes ...`
- M5 the `room_lift` push unclipped: `FAIL R11-OUTSIDE-ROOMS-3B: a 3 K lift under a 0.5 K half band reads a room_lift push of 1 (clipped) ...`
- M6 the comfort push against the lifted floor: `FAIL R11-OUTSIDE-ROOMS-3B: with a lift the drivers carry a room_lift row after comfort_floor ...`
- M7 `floor_limits` hands back the all-zero lift array for a lift every step's band clips to zero: the null-control check above. M7 survived the first cut of the block (its only zero-lift case returned before the clip); commit `3886cc11d7` added the clipped case.

The diff's draw, `python3 -I tools/audit/seat/mutant_run.py --diff "$(git merge-base origin/main HEAD)...HEAD" --cmd CMD --max-mutants 40 --report-only` (`prepr.sh` step 2's draw: the first 40 mutants of added `.py` lines outside `tests/` and `dev/`, in a git-archive copy), with three detectors:

- CMD the 3B block (`bash mutcmd.sh`, the `features_block.py` call above): 8 survivors, every one a production-solve site the block does not drive (`coordinator.py:6285` and `:11296` STMT_DEL, the `SolveRecord` and what-if returns; `optimizer.py` STMT_DEL of the two `room_lifts` field declarations, the `OptimizationResult` return, the `_build_comfort_bounds` call and the `_Horizon` build; `room_lifts=floors[2]` -> `floors[3]`).
- CMD `PYTHONPATH=tests/hastub python3 tests/edge.py`, a production solve: kills each of those but the two `coordinator.py` statements. Its own 16 survivors are each killed by the block (the reverse direction: the classification, push and bound arithmetic the edge check reads only through the `room_floor` count).
- The two `coordinator.py` statements, by `--path custom_components/heatpump_optimizer/coordinator.py --cmd "PYTHONPATH=tests/hastub python3 tests/features.py" --in-place --timeout 1600` (a git-archive copy fails `features.py`'s checkout-reading checks on the unedited tree, rc 3): rc 0, no `SURVIVED` line; the unedited baseline passed, or the driver exits 3.

So no drawn mutant survives all three. The block's first full draw (at `2f3c14dc6f`) left four more that `ddfc28e099` answers: `_raised_floor`'s None/None early return (a 22.8 floor under a 23.0 ceiling stays unclipped), its ceiling-clip constant, `_mark_room_floor`'s `last` index and its strict `>` (now checked on the last step and exactly at the boundary), and the mold padding's `max(0, ...)`, which was equivalent (the extra element was cut by `[:n_steps]`) and is gone with the padding rewritten as a fill.

## Null control

- **The plan does not move.** `tests/edge.py` `room lift named`: on the cold day (`weather("winter_cold")` from 00:00, a held 0.5 K lift through `rooms.floor_limits`) the power schedule with `room_lifts` passed equals the schedule with the same margins and no `room_lifts`; 37 steps read `room_floor` and 13 `comfort_floor`, which sum to the 50 `comfort_floor` steps of the run without `room_lifts` (invariant iv); the run without `room_lifts` and the unlifted run have no `room_floor` step and no `room_lift` row.
- `dev/audit/harnesses/room_lift_solve.py` (P2's instrument; `PYTHONPATH=tests/hastub:custom_components:tests OPENBLAS_NUM_THREADS=1`) prints byte-identical output at the base (a `git archive` of `e698fc8ac3`, harness sha1 `8941f94eef28`) and at the head (harness sha1 `09c0d5b0ab1b`, the `rooms.lifted` call renamed): every row's sha1, the lifted plan's `edde566a7f8d` included. Its own control: the `lift` row's sha1 differs from `none`'s `eda725c0be09`.
- **The readers without a lift are today's.** `room_lifts` None gives the five pre-3B driver codes; the R10-WHY-NOW-WIDGET block's pinned weights pass unchanged on a horizon carrying `room_lifts=None`; a zero lift array gives the same five weights byte-equal and a 0.0 `room_lift` row; `floor_limits` with no held lift, a zero one or one the band clips to zero returns the base object and None (`tests/features.py`, the 3B null-control check).
- **Goldens.** No fixture has a room list: the scoped gate's `tests/env_drift.py --all e698fc8ac3` (drift mode against the merge base) passed, and `git diff --quiet e698fc8ac3 HEAD -- tests/golden && echo IDENTICAL` prints `IDENTICAL`.

## Figures

- Gate scope: `python3 tests/closure.py select --diff $(git merge-base origin/main HEAD) --workdir "$D"`.
<!-- figure-block: scope-line mb=e698fc8ac374a1d72c230b55d938d75b03b7de67 head=ddfc28e0993ed0bb7822eed43ecfe9b353947d9a -->
~~~text
MODE: SCOPED -- 28 script(s) run, 5 scoped out.
~~~
<!-- /figure-block -->
- The scoped gate at the head, `GATE_SCOPE=auto GOLDEN_MODE=drift GOLDEN_REF=$(git merge-base origin/main HEAD) ./tests/run.sh`, on a tree left untouched for the run: `MODE: SCOPED -- 28 script(s) run, 5 scoped out.`, `30 TEST SCRIPT(S) PASSED; 4 SCOPED OUT AND NOT RUN`, rc 0; among them `tests/features.py`, `tests/edge.py`, `tests/entities.py`, `tests/env_drift.py --all`, `tests/golden.py`, `tests/card.mjs`, `tests/doc_claims.py`, `tests/stress.py` (`ALL 122 STRESS CHECKS PASSED`, `tests/stress_budgets.json` unchanged) and `tests/harness_headers.py`. An earlier run of the same command at `13f8317e7c` failed `tests/features.py` (the R10-WHY-NOW-WIDGET key-set check read all of `DRIVER_CODES`; its stand-in horizon lacked `room_lifts`; two unpacks read two floor arrays) and `tests/doc_claims.py` (one comment sentence over 40 words), each fixed by a later commit of this branch.
- `python3 tests/structure.py`: `STRUCTURE RATCHET PASSED`; `class_excess_loc` recorded `17322 -> 17306`: the T5 arithmetic left `HeatPumpOptimizer` for `_raised_floor`, which the attribution calls a second time, and the result-build call site is one line shorter. No other row moved.
- `python3 tools/audit/archscore/score.py --diff e698fc8ac374a1d72c230b55d938d75b03b7de67`: `Architecture score: dS +0.0000 NULL`.
- `tests/card_browser.mjs` was not run: no scope selects it, and the card change is two strings tables, one map entry and no layout.

## Red checks

- `tests / mutation`: predicted red at the head by the unpinned sites below, which `mutation-autofix` pins once the pull request exists (`ci-autofix.md`: never duplicated by the fixer). Cheaper detector: `prepr.sh`'s step 6d, which ran before the handoff and named every site, at no standing cost beyond the prepr run; the red is the lane's own pinning step, so none cheaper exists.

## Unpinned sites

The 24 sites `python3 tools/pr/ci_predict.py --base origin/main` lists as `ADDED UNPINNED` at the head, each under `custom_components/`. `2f3c14dc6f` drops ten `killed_by` pins whose pinned lines this diff moved (`ci_predict.py` read each as `STALE PIN` on the ledger); the sites they pinned are now in `rooms.floor_limits`, `_raised_floor`, `_build_comfort_bounds`' return and `slot_drivers.space_pushes`.

- custom_components/heatpump_optimizer/optimizer.py:731 BOOLOP: pinned by mutation-autofix (its lane mutates `custom_components/`)
- custom_components/heatpump_optimizer/optimizer.py:731 GUARD_OFF: pinned by mutation-autofix (its lane mutates `custom_components/`)
- custom_components/heatpump_optimizer/optimizer.py:733 GUARD_OFF: pinned by mutation-autofix (its lane mutates `custom_components/`)
- custom_components/heatpump_optimizer/optimizer.py:735 GUARD_OFF: pinned by mutation-autofix (its lane mutates `custom_components/`)
- custom_components/heatpump_optimizer/optimizer.py:739 CLAMP_DROP: pinned by mutation-autofix (its lane mutates `custom_components/`)
- custom_components/heatpump_optimizer/optimizer.py:743 CLAMP_DROP: pinned by mutation-autofix (its lane mutates `custom_components/`)
- custom_components/heatpump_optimizer/optimizer.py:743 RETURN_DEL: pinned by mutation-autofix (its lane mutates `custom_components/`)
- custom_components/heatpump_optimizer/optimizer.py:2532 GUARD_OFF: pinned by mutation-autofix (its lane mutates `custom_components/`)
- custom_components/heatpump_optimizer/optimizer.py:2537 CLAMP_DROP: pinned by mutation-autofix (its lane mutates `custom_components/`)
- custom_components/heatpump_optimizer/optimizer.py:2537 CMP_BOUND: pinned by mutation-autofix (its lane mutates `custom_components/`)
- custom_components/heatpump_optimizer/optimizer.py:4933 GUARD_OFF: pinned by mutation-autofix (its lane mutates `custom_components/`)
- custom_components/heatpump_optimizer/optimizer.py:4937 CLAMP_DROP: pinned by mutation-autofix (its lane mutates `custom_components/`)
- custom_components/heatpump_optimizer/optimizer.py:4938 RETURN_DEL: pinned by mutation-autofix (its lane mutates `custom_components/`)
- custom_components/heatpump_optimizer/rooms.py:310 GUARD_OFF: pinned by mutation-autofix (its lane mutates `custom_components/`)
- custom_components/heatpump_optimizer/rooms.py:319 CLAMP_DROP: pinned by mutation-autofix (its lane mutates `custom_components/`)
- custom_components/heatpump_optimizer/rooms.py:321 CLAMP_DROP*3: pinned by mutation-autofix (its lane mutates `custom_components/`)
- custom_components/heatpump_optimizer/rooms.py:322 GUARD_OFF: pinned by mutation-autofix (its lane mutates `custom_components/`)
- custom_components/heatpump_optimizer/rooms.py:324 RETURN_DEL: pinned by mutation-autofix (its lane mutates `custom_components/`)
- custom_components/heatpump_optimizer/slot_drivers.py:116 CLAMP_DROP: pinned by mutation-autofix (its lane mutates `custom_components/`)
- custom_components/heatpump_optimizer/slot_drivers.py:125 CLAMP_DROP: pinned by mutation-autofix (its lane mutates `custom_components/`)
- custom_components/heatpump_optimizer/slot_drivers.py:126 CLAMP_DROP: pinned by mutation-autofix (its lane mutates `custom_components/`)
- custom_components/heatpump_optimizer/slot_drivers.py:127 CLAMP_DROP: pinned by mutation-autofix (its lane mutates `custom_components/`)
- custom_components/heatpump_optimizer/slot_drivers.py:128 CLAMP_DROP: pinned by mutation-autofix (its lane mutates `custom_components/`)
- custom_components/heatpump_optimizer/slot_drivers.py:131 RETURN_DEL: pinned by mutation-autofix (its lane mutates `custom_components/`)

The 8 sites `prepr.sh` step 2 reports `SURVIVED` under the 3B block, each a production-solve site the block does not drive, killed by the detector named under `## Mutation proof`:

- custom_components/heatpump_optimizer/optimizer.py:3112 STMT_DEL: killed by `tests/edge.py` (a value check: the `room_lifts` field of `_Horizon`)
- custom_components/heatpump_optimizer/optimizer.py:3179 STMT_DEL: killed by `tests/edge.py` (the `room_lifts` field of `SolveLimits`)
- custom_components/heatpump_optimizer/optimizer.py:4021 STMT_DEL: killed by `tests/edge.py` (the `OptimizationResult` return)
- custom_components/heatpump_optimizer/optimizer.py:4582 STMT_DEL: killed by `tests/edge.py` (the `_build_comfort_bounds` call)
- custom_components/heatpump_optimizer/optimizer.py:4629 STMT_DEL: killed by `tests/edge.py` (the `_Horizon` build)
- custom_components/heatpump_optimizer/optimizer.py:4663 CONST_SWAP: killed by `tests/edge.py` (`floors[3]` raises)
- custom_components/heatpump_optimizer/coordinator.py:6285 STMT_DEL: killed by `tests/features.py`, run in place (the `SolveRecord` return)
- custom_components/heatpump_optimizer/coordinator.py:11296 STMT_DEL: killed by `tests/features.py`, run in place (the what-if's return)

## Forward-carry

none

## Friction

design-review.md: unenforced: the approved note's interface 4 put an 11th parameter on `classify_space_steps`, which `tools/audit/archscore/score.py --diff` refuses (`params_over_10 6 -> 7`); the review did not price the interface with the instrument the fix is graded by. Built as a post-pass with identical labels. Carry: dismissed: one instance, resolved in this pull request.
