R11-CARRY-ROOM-LIFT: the two room phase-2 lift rulings, re-measured at the merge base and built where they ask for a build.

- Carry 3 (roster carry 0, items 324a1354: the 1.0 K cap `rooms.ROOM_LIFT_CAP_C` and phase 2 as its own opt-in toggle, default off; owner ruling 2026-11-16T07:46:57Z, decision card, "1.0 K, opt-in off (Recommended)"): it still holds on main at 1723f9fdc9d8a6e6987190d2887686297a621dd4, so nothing is built for it. `rooms.ROOM_LIFT_CAP_C = 1.0` and `const.DEFAULT_ROOM_LIFT_ENABLED = False`, each already pinned by `tests/features.py` (the checks "one five kelvin shorter lifts the 1.0 K cap" and "with the flag off, or never stored, a room list changes nothing").
- Carry 4 (roster carry 1, items daa69071: the lifted floor raises the plan peak; ruled 2026-11-18 by the round-11 orchestrator under mandate 6893738184, option A: the rise is accepted, with no clip and no headroom under the target). The rise reproduces at the merge base (Figures). Built: a `tests/features.py` check, solving through the production optimizer, that fails on a clip or headroom; two null-control rows in `dev/audit/harnesses/room_lift_solve.py`; the ruling stated in `rooms.lifted`'s docstring; and the D6 correction. The sentence at `docs/configuration.md`'s "Let a cold room raise the planned minimum" row said the plan "never plans the house above it", which is false at the merge base (lift +0.450 K over target against none's +0.241 K). The row now states the ruling. The strings/translations `data_description` ("never above your comfort target") is about the minimum, which the margins still respect, so it stays.

Neither ruling is in `dev/programme/RULINGS.md` (`git grep -n -i -E "room|3616" origin/main -- dev/programme/RULINGS.md` prints nothing). This PR does not write that file, because recording rulings is the orchestrator's job (`orchestrator.md`).

The diff touches `docs/configuration.md` only in this group's own row, so it stays clear of #3711's adjacent row.

## Head

Code head 338aa528f9c50def49f173137a9588d7a7f39574, cut from origin/main 1723f9fdc9d8a6e6987190d2887686297a621dd4 (merge base), measured 2026-11-19T00:20Z.

prepr: passed rc=0 at 338aa528f9c50def49f173137a9588d7a7f39574 (PREPR_SKIP_CLOSURES=1). Local scoped gate, PYTHONPATH=tests/hastub, all rc 0: tests/doc_claims.py, tests/entities.py, tests/harness_headers.py, tests/structure.py, tests/typing_ruler.py, tests/arch_score_head.py, tests/guard_pins.py, tests/golden.py (GOLDEN_MODE=drift), tests/md_tables.mjs. The rest of scope.run, the full tests/features.py among them, is left to CI.

## Mutation proof

The block was run with `python3 tools/audit/seat/features_block.py --prelude "exec(open('<prelude>').read())" '# -- The plan peak under the lift'`, its prelude written by `--emit-prelude <prelude> '# -- The plan peak under the lift'`, with `PYTHONPATH=tests/hastub`. Each mutant edits one predicate line of `custom_components/heatpump_optimizer/rooms.py`'s `lifted` and is restored afterwards (`git diff --quiet` after restore: clean).
- Headroom under the target: `]) - margins` -> `]) - margins - 0.1`. Red: `the lifted floor reaches the comfort target, no headroom under it, at every step past the ramp (0.1 K at step 0, 0.25 K an hour, so from step 7)` and `the lift may raise the plan's peak over the unlifted plan's, and the lifted plan holds the target past the ramp; null control, an all-zero margin array plans the unlifted plan` (2 of 2 FEATURES BLOCK FAILED).
- Clip short of the target: `np.minimum(band, ramp)` -> `np.minimum(band * 0.5, ramp)`. Same two red (2 of 2 FEATURES BLOCK FAILED).
- Unmutated: ALL 2 FEATURES BLOCK PASSED.

## Null control

- In the solver: the features check's all-zero margin array plans the unlifted plan step for step (`np.array_equal` on the room trajectory), and the harness `zeros` row has `none`'s sha1 and `max_over_target_c`.
- For the peak (group brief): with `rooms.ROOM_LIFT_CAP_C` monkeypatched to infinity around `rooms.resolve` (row `lift_cap_removed`), the harness still moves the plan peak over `none`'s, so the rise comes from the floor and not from the cap. With the cap at zero (row `lift_cap_zero`), no lift is held (`rooms.lifted` returns None) and the plan is `none`'s by sha1. In this fixture the cap equals the night band (1.0 K), so removing it leaves the lift's margins unchanged.

## Figures

- `PYTHONPATH=tests/hastub:custom_components:tests OPENBLAS_NUM_THREADS=1 python3 dev/audit/harnesses/room_lift_solve.py`. At the merge base (harness sha1 4feec646b1e4acfecc52ac57cffdebc9ae3d6aad), `max_over_target_c` (highest planned room temperature less the 20.0 target): none +0.241, zeros +0.241, lift +0.450, and every gated row +0.241. At the head (harness sha1 8941f94eef28441e806fb316ee5f0c7abc326c85): the same rows unchanged, lift_cap_removed +0.450, lift_cap_zero +0.241 (sha1 eda725c0be09 = none's), and all 11 harness checks `ok`, rc 0.
- Features block (command above): ALL 2 FEATURES BLOCK PASSED at the head.
- `python3 tests/structure.py`: STRUCTURE RATCHET PASSED at the head.
- Class enumeration (fixer step 8), for sentences claiming the lift never raises the plan above the target: a scout grep of docs/, README.md, `custom_components/heatpump_optimizer/*.py`, strings.json and translations/*.json for "above it", "above the target", "never plans", "peak" and "never above" near room/lift. It returned `docs/configuration.md` (the room-lift row), corrected in this diff, and strings.json / en.json / de.json / sv.json `data_description.room_lift_enabled` ("never above your comfort target"), which describes the minimum and is true, so left alone.

<!-- figure-block: scope-line mb=1723f9fdc9d8a6e6987190d2887686297a621dd4 head=338aa528f9c50def49f173137a9588d7a7f39574 -->
~~~text
MODE: SCOPED -- 28 script(s) run, 5 scoped out.
~~~
<!-- /figure-block -->

## Red checks

none

## Forward-carry

none

## Friction

none
