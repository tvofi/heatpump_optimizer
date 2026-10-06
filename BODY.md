Block DHW and Block Space Heating are two-hour switches, the opposite of the boost pair. A block zeroes that duty on the copy of the plan action, the arbiter drops it (idle when nothing remains; the supply switch is not written), and the later press wins against a boost on the same channel. A safety floor releases the block and the switch publishes why. State stays in `boost.py`'s weak map. The four duty switches share one base. No coordinator attribute was added, and the structure ratchet did not move.

Closes #1926

Leaves #201 open

_Requested by **tvofi**_.

The release conditions are enumerated by `PYTHONPATH=tests/hastub python3 tests/block_duty.py`. Each one has a failing direction in that script: a due or overdue anti-legionella cycle (`a due or overdue cycle inside the horizon releases DHW`), a disinfection hold, the tank at its minimum inside a demand window and not outside one (`00:00-01:00` at 12:00), the room floor, the cold-rail lease, system identification, and a stale plan.

## Head

`aa1a661584d66722c4167c00b995c7609c4cf7cf`

`3560b69668e171c91cac0fbcf1db35490795306e` merges origin/main `f07cd253` into `aedd50be`. The entity census keeps both additions: 78 entities, 60 sensors, 6 switches.

`b89154264a7eb6cca52d4605b902f4238d23240d`

`6132233c4a1a8dc1fda61aa142624d1a4f8af38c` adds one commit to the previous head, containing only this PR's own row, `docs/delivery/1997.md`. The authored code head is `3301d6197d15cfbf58543f4af82fc7980c012996`.

`de8ccc657ccd9fe5acdcfc6b800d02d70c6ee9e5` merges origin/main `6b1ccb68` into the authored code head `3301d6197d15cfbf58543f4af82fc7980c012996` (an automatic merge by the orchestrator's script; any resolution inside the code head is described below).

`3301d6197d15cfbf58543f4af82fc7980c012996`

The window check was measured at `aa1a661584d66722c4167c00b995c7609c4cf7cf` (`date -u`: 2026-10-06T18:46:09Z). This is not a stamp. origin/main in that merge is `f07cd253c52f1012427d9869a808f1df39dafb93`. The unpinned count below was taken at `b8915426` against `6b1ccb685e51903e7e524995a84d831d3904da9f`, `62f604eb062bf88d3dc4b0f4ec85ca17359af229` and `0a60e06585640fd79ca321c65a9b8f13bc0030a4`.

## Mutation proof

`PYTHONPATH=tests/hastub python3 tests/mutation_table.py --scope changed --base origin/main --pin-killed --scripts tests/block_duty.py` drove the sites this diff added. `tests/block_duty.py` killed 68 of them (the last run's line was `PIN KILLED: 2 pinned, 10 left unpinned` after 66 were already recorded). The 10 that stayed green are equivalent, and each has a `survivor_triage` row: dropping `max` of two constants that are both 2, guards whose body cannot run, a comparison that writes the instant the slot already holds, and a trailing `return None` replaced by `pass`.

The overlay assignment `action["power"] = 0.0` replaced with `action["power"] = action["power"]` left power at 1.2 under the check `a space block zeroes space power and leaves the supply switch and DHW alone`. Restored, that check printed `ok`.

Deleting `and _window_open(snap, now)` from `_dhw_floor` made `PYTHONPATH=tests/hastub python3 tests/block_duty.py` exit 1: `FAIL the tank at its minimum outside a demand window does not release` (1 of 46). A 45 °C tank, minimum 45 °C, windows `00:00-01:00`, at 12:00. Restored, the same command printed `ALL 46 BLOCK DUTY CHECKS PASSED` and that check `ok`.

## Null control

With no block set, `boost.overlay` adds no key and changes no value (`tests/features.py`: `with no block set the overlay adds no key and changes no value`, printed `ok`). A boost-only store payload has no `block_dhw` or `block_space` key (printed `ok`). `tests/golden/claimed_drift.txt` and `tests/golden/card_claimed_drift.txt` are not in the diff. `tests/env_drift.py --all` against `62f604eb` printed `NO UNCLAIMED DRIFT`.

## Figures

- `PYTHONPATH=tests/hastub python3 tests/block_duty.py` — `ALL 46 BLOCK DUTY CHECKS PASSED` at `aa1a661584d66722c4167c00b995c7609c4cf7cf`. The same command with `and _window_open(snap, now)` deleted exited 1 on `the tank at its minimum outside a demand window does not release`.
- Unpinned ratchet, `tests/mutation_table.py`'s `unpinned_sites` / `added_unpinned` / `ratchet_refusal` against `6b1ccb685e51903e7e524995a84d831d3904da9f`, `62f604eb062bf88d3dc4b0f4ec85ca17359af229` and `0a60e06585640fd79ca321c65a9b8f13bc0030a4` — unpinned 4698, base 4699, added 0, refusal None
- `python3 tests/closure.py select --diff origin/main` — `MODE: SCOPED -- 21 script(s) run, 10 scoped out` at the code head before `tests/block_duty.py`
- `PYTHONPATH=tests/hastub python3 tests/structure.py` — `STRUCTURE RATCHET PASSED`
- `PYTHONPATH=tests/hastub python3 tests/ha_floor.py check` — `RESULT checked=147 missing=0 unrecorded=0 undecidable=0`
- `PYTHONPATH=tests/hastub python3 tests/entities.py` — `ALL 2190 ENTITY CHECKS PASSED` at `3301d619`, before this pin commit
- `PYTHONPATH=tests/hastub python3 tests/features.py` — `1 of 3721 FEATURE CHECKS FAILED` on this machine, the storage-plan check in Red checks. The block checks printed `ok`
- `PYTHONPATH=tests/hastub python3 tests/env_drift.py --all 62f604eb062bf88d3dc4b0f4ec85ca17359af229` — `NO UNCLAIMED DRIFT: 56 scenario(s) checked` and `NO STALE FIXTURE`
- `PYTHONPATH=tests/hastub python3 tests/doc_claims.py` — `ALL 160 checks PASSED`
- `PYTHONPATH=tests/hastub python3 tests/harness_headers.py` — `ALL 105 HARNESS HEADER CHECKS PASSED`
- `PYTHONPATH=tests/hastub python3 tests/boost_drift_replay.py` — `ALL 43 BOOST DRIFT CHECKS PASSED`
- `PYTHONPATH=tests/hastub GOLDEN_MODE=drift GOLDEN_REF=62f604eb062bf88d3dc4b0f4ec85ca17359af229 python3 tests/plan_view.py` — `plan reason codes, price provenance and slot energy OK`
- `node tests/card.mjs` — `ALL CARD CHECKS PASSED`
- `node tests/card_drift.mjs` — `card_drift: identical in all 40 states`
- `PYTHONPATH=tests/hastub python3 tools/audit/round4/D6/claims.py` — `RESULT claims_true=123 claims` and `RESULT claims_false=0 claims`

## Red checks

`mutation` went red at `6132233c4a1a8dc1fda61aa142624d1a4f8af38c`. First error line: `MUTATION TABLE REFUSED -- 4776 unpinned site(s) against 4699 at the ratchet base 6b1ccb685e51903e7e524995a84d831d3904da9f, 78 of them added by this diff.` The same job's pin step then printed `MUTATION TABLE REFUSED -- nothing was measured: 0 mutant(s) timed out, 78 not started for --budget-minutes`. Cheaper detector: `tests/mutation_table.py`'s source inventory, which prints that refusal before any driver and costs seconds. This commit records the 68 kills and the 10 equivalent rows. Against `6b1ccb68` the unpinned count is 4698 and added is 0.

`mutation-autofix` went red on the same head. First error line: `mutation-autofix: skip-no-measurement -- THE REPAIR DID NOT HAPPEN.` The pin step had measured nothing, so the job had no rows to apply. Cheaper detector: that summary line. The dispositions are in this commit, which is what the job would have pushed.

`nightly-status` and `delivery-status` grade `main` and were already red on that head. This commit does not change their scripts, `tests.yml`, `governance.yml`, the plan, or `docs/HANDOVER.md`. Cheaper detector: none. Each check is the detector.

On this machine `tests/features.py` fails `R9-F2.1 P3: the shipped storage plan is no worse on its own objective than the half-price floor's plan refined under it` (shipped 110.4366, seeded 110.1297). `optimizer.py` and `thermal_model.py` are not in the diff. CI's `fast (3.14)` was green at `6132233c`. Cheaper detector: none. That check is the detector.

## Forward-carry

none

## Friction

none
