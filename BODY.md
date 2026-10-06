Block DHW and Block Space Heating are two-hour switches, the opposite of the boost pair. A block zeroes that duty on the copy of the plan action, the arbiter drops it (idle when nothing remains; the supply switch is not written), and the later press wins against a boost on the same channel. A safety floor releases the block and the switch publishes why. State stays in `boost.py`'s weak map. The four duty switches share one base. No coordinator attribute was added, and the structure ratchet did not move.

Closes #1926

Leaves #201 open

_Requested by **tvofi**_.

The release conditions are enumerated by `PYTHONPATH=tests/hastub python3 tests/block_duty.py`. Each one has a failing direction in that script: a due or overdue anti-legionella cycle (`a due or overdue cycle inside the horizon releases DHW`), a disinfection hold, the tank at its minimum inside a demand window and not outside one (`00:00-01:00` at 12:00), the room floor, the cold-rail lease, system identification, and a stale plan.

## Head

`63aebe893e572c9ae558cae7049613b23a2c8f6b`

`63aebe893e572c9ae558cae7049613b23a2c8f6b` puts `tests/block_duty.py` on a `run` line in `tests/run.sh` and a `rec` line in `tests/derive_closures.sh`, and writes the selection-cost counts `tests/entities.py` derived from `tests/closures.json` into `tests/deployment_shape.py`. Parent `aa1a661584d66722c4167c00b995c7609c4cf7cf`. Measured `date -u`: 2026-10-06T19:02:19Z. This is not a stamp.

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

`closures` failed at `3560b69668e171c91cac0fbcf1db35490795306e`, job 112424468392. The job printed `closure: selectable script(s) with NO recording this run:` and `tests/block_duty.py`. `closures-autofix` on the same run, job 112436474265, printed `closures-autofix: skip-clean -- nothing owed to a human.` A script the derive lanes never run is not UNDER-SCOPED, so no bot commit comes. Cheaper detector: `tests/run.sh` prints `UNWIRED TEST: tests/block_duty.py is not referenced by tests/run.sh` before any lane. That scan is the start of `fast`; it adds no standing cost of its own. `63aebe89` adds the script to both lane files.

`fast (3.14)` failed at the same head, job 112424333780. The run printed `3 TEST SCRIPT(S) FAILED`. The three lines are `UNWIRED TEST: tests/block_duty.py is not referenced by tests/run.sh`, `FAILED python3 tests/entities.py` (`FAIL and the lane's docstring records those measured numbers as the selection-cost note (#1218)`, `missing markers -> ['103 of the 496', '378 pairs']`), and `TEST NEVER RAN: tests/block_duty.py is wired into tests/run.sh but no lane executed it and no lane skipped it on purpose.` Cheaper detector for the wiring: the unwired line, already the start of this job. For the note: none. `tests/entities.py` re-derives the pair counts and is the detector. `63aebe89` writes `103 of the 496` and `378 pairs` into the note (`all 88 files` was already there).

`mutation` went red at `6132233c4a1a8dc1fda61aa142624d1a4f8af38c`. First error line: `MUTATION TABLE REFUSED -- 4776 unpinned site(s) against 4699 at the ratchet base 6b1ccb685e51903e7e524995a84d831d3904da9f, 78 of them added by this diff.` The same job's pin step then printed `MUTATION TABLE REFUSED -- nothing was measured: 0 mutant(s) timed out, 78 not started for --budget-minutes`. Cheaper detector: `tests/mutation_table.py`'s source inventory, which prints that refusal before any driver and costs seconds. The 68 kills and the 10 equivalent rows are in `b8915426`. At `3560b696` the `mutation` job succeeded.

`mutation-autofix` went red at `6132233c4a1a8dc1fda61aa142624d1a4f8af38c`. First error line: `mutation-autofix: skip-no-measurement -- THE REPAIR DID NOT HAPPEN.` The pin step had measured nothing, so the job had no rows to apply. Cheaper detector: that summary line, which is this job reading the mutation job. The dispositions are in `b8915426`. At `3560b696` the job was skipped.

`nightly-status` grades `main`. At `3560b696`, job 112424333066, pinned `f07cd253c52f1012427d9869a808f1df39dafb93`, it printed `NIGHTLY FAILED: record-autofix failed last night.` and `scheduled run 37440269774, 2026-10-06T09:03:01+00:00, head cff39da, run conclusion 'failure'`. Cheaper detector: none. The check is the detector. This diff does not touch `tests/nightly_status.py`, `.github/workflows/tests.yml`, `.github/workflows/governance.yml`, `docs/plan-2026-09-open-issues.md`, or `docs/HANDOVER.md`.

`delivery-status` grades `main`. At `3560b696`, job 112424332787, pinned `f07cd253c52f1012427d9869a808f1df39dafb93`, it printed `DELIVERY STATUS UNCHECKED — 39 rowed, 1 pending, 0 overdue (overdue at 12 commits)` and `pending  #2001 1b1bbaa 0 commit(s) since — record: delivery rows for #2000 (autofix)`. Cheaper detector: none. The check is the detector. This diff does not touch `tests/delivery_status.py`.

## Forward-carry

none

## Friction

none
