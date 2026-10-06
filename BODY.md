Block DHW and Block Space Heating are two-hour switches, the opposite of the boost pair. A block zeroes that duty on the copy of the plan action, the arbiter drops it (idle when nothing remains; the supply switch is not written), and the later press wins against a boost on the same channel. A safety floor releases the block and the switch publishes why. State stays in `boost.py`'s weak map. The four duty switches share one base. No coordinator attribute was added, and the structure ratchet did not move.

Closes #1926

Leaves #201 open

_Requested by **tvofi**_.

## Head

`3301d6197d15cfbf58543f4af82fc7980c012996`

Measured at origin/main `62f604eb062bf88d3dc4b0f4ec85ca17359af229` (`date -u`: 2026-10-06T15:27:10Z). This is not a stamp.

## Mutation proof

In `boost.py` `_zero_blocked`, the assignment `action["power"] = 0.0` was replaced with `action["power"] = action["power"]` (the predicate that zeroes the blocked duty, not a line after a return). The overlay predicate `tests/features.py` names `a space block zeroes space power and leaves the supply switch and DHW alone` then left `power` at 1.2. The line was restored. On the restored tree that same check printed `ok`.

`python3 tests/mutation_table.py --scope changed --base origin/main` was not driven. Its own rule refuses a mutant verdict when a selected baseline script is already red, and `tests/features.py` is red on this machine for the reason in Red checks. No `--pin-killed`. The two existing `restore` pins still name the comparison line; that line was put back at its original indent so the ledger still generates the site.

## Null control

With no block set, `boost.overlay` adds no key and changes no value (`tests/features.py`: `with no block set the overlay adds no key and changes no value`, printed `ok`). A boost-only store payload has no `block_dhw` or `block_space` key (printed `ok`). `tests/golden/claimed_drift.txt` and `tests/golden/card_claimed_drift.txt` are not in the diff. `tests/env_drift.py --all` against `62f604eb` printed `NO UNCLAIMED DRIFT`.

## Figures

- `python3 tests/closure.py select --diff origin/main` — `MODE: SCOPED -- 21 script(s) run, 10 scoped out`
- `PYTHONPATH=tests/hastub python3 tests/structure.py` — `STRUCTURE RATCHET PASSED`
- `PYTHONPATH=tests/hastub python3 tests/ha_floor.py check` — `RESULT checked=147 missing=0 unrecorded=0 undecidable=0`
- `PYTHONPATH=tests/hastub python3 tests/entities.py` — `ALL 2190 ENTITY CHECKS PASSED`
- `PYTHONPATH=tests/hastub python3 tests/features.py` — `1 of 3721 FEATURE CHECKS FAILED`, the one name in Red checks. The block checks printed `ok`, including `a space block zeroes space power and leaves the supply switch and DHW alone`, `a space block on a space step serves the idle row, not heating`, `a DHW block stays idle through the hot-water lease instead of handing space heat back`, `a space block keeps the lease expiry on hot water, not the baseline's both duties`, `a due cycle refuses the block press and the switch says why`, `a due anti-legionella cycle releases the block before the overlay zeroes it`
- `PYTHONPATH=tests/hastub python3 tests/env_drift.py --all 62f604eb062bf88d3dc4b0f4ec85ca17359af229` — `NO UNCLAIMED DRIFT: 56 scenario(s) checked` and `NO STALE FIXTURE`
- `PYTHONPATH=tests/hastub python3 tests/doc_claims.py` — `ALL 160 checks PASSED`
- `PYTHONPATH=tests/hastub python3 tests/harness_headers.py` — `ALL 105 HARNESS HEADER CHECKS PASSED`
- `PYTHONPATH=tests/hastub python3 tests/boost_drift_replay.py` — `ALL 43 BOOST DRIFT CHECKS PASSED`
- `PYTHONPATH=tests/hastub python3 tests/config_flow_steps.py` — `ALL 496 checks PASSED`
- `PYTHONPATH=tests/hastub python3 tests/deployment_shape.py` — `ALL DEPLOYMENT SHAPE CHECKS PASSED`
- `PYTHONPATH=tests/hastub python3 tests/finite_boundary.py` — `ALL 83 FINITE BOUNDARY CHECKS PASSED`
- `PYTHONPATH=tests/hastub python3 tests/guard_pins.py` — `ALL 9 GUARD PIN CHECKS PASSED`
- `PYTHONPATH=tests/hastub python3 tests/manual_plan.py` — `ALL 85 manual plan checks PASSED`
- `PYTHONPATH=tests/hastub python3 tests/solar_alignment.py` — `ALL SOLAR ALIGNMENT CHECKS PASSED`
- `PYTHONPATH=tests/hastub python3 tests/wood_advisor.py` — `ALL 7 wood-advisor checks PASSED`
- `PYTHONPATH=tests/hastub python3 tests/arch_score_head.py` — `ALL 14 ARCHITECTURE SCORE HEAD CHECKS PASSED`
- `PYTHONPATH=tests/hastub python3 tests/typing_ruler.py` — `ALL 11 typing-ruler source checks PASSED`
- `node tests/md_tables.mjs` — `RESULT doc_orphaned_table_rows=0 count` and `RESULT doc_misrendered_lines=0 count`
- `PYTHONPATH=tests/hastub GOLDEN_MODE=drift GOLDEN_REF=62f604eb062bf88d3dc4b0f4ec85ca17359af229 python3 tests/plan_view.py` — `plan reason codes, price provenance and slot energy OK`
- `node tests/card.mjs` — `ALL CARD CHECKS PASSED`
- `node tests/card_drift.mjs` — `card_drift: identical in all 40 states`
- `PYTHONPATH=tests/hastub python3 tools/audit/round4/D6/claims.py` — `RESULT claims_true=123 claims` and `RESULT claims_false=0 claims`

Seams of this feature, each a check above: overlay zero on the action copy, closed; arbiter idle row and lease not handing the blocked duty back, closed; later press wins, including the space-boost settling tail, closed; legionella due inside the horizon (the planner hard deadline, `due < horizon`), disinfection, tank floor, room floor at `ECONOMY_ABSOLUTE_FLOOR + SPACE_PUMP_FLOOR_MARGIN_C`, cold rail, sysid, stale plan, closed; persist omits block keys when unset and restore keeps a live block only, closed; switch count, object ids, names, DHW gate, closed. No separate frost-protection module is documented.

## Red checks

`tests/features.py` is red on this machine: `R9-F2.1 P3: the shipped storage plan is no worse on its own objective than the half-price floor's plan refined under it` — shipped 110.4366, seeded with the half-price plan 110.1297. `git diff --stat origin/main -- custom_components/heatpump_optimizer/optimizer.py custom_components/heatpump_optimizer/thermal_model.py` is empty. The same pair was printed by a solve that imported only `optimizer` and `thermal_model`. Cheaper detector: none. That check is the detector; it compares two solves in one process, and on this machine's BLAS the shipped plan is worse than the seeded one by more than the 0.1 tolerance. The diff does not touch the solver.

## Forward-carry

none

## Friction

none
