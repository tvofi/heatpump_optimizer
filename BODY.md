Block DHW and Block Space Heating are two-hour switches. A block zeroes that duty on the copy of the plan action, and a safety floor releases it: a due or running anti-legionella cycle, the tank at its minimum inside a demand window, the room at the economy floor, the cold-rail lease, a measurement experiment, or a stale plan. The arbiter drops a blocked duty before it commands the pump, and it still holds the GCHV night-mode window that R9-SW-4 added on the same pass. State stays in the boost store's weak map.

Closes #1926

Leaves #201 open.

_Requested by **tvofi**_.

## Head

`3018304403694c070c52ae9c3683dabbfd7cb702`

Measured `date -u` 2026-10-07T07:44Z against origin/main `be0cb82134bd3a008e59127da6f2b67fb1c77e98`, the tip this head merges. `git merge-tree --write-tree origin/main HEAD` exited 0. The `custom_components/heatpump_optimizer/pump_arbiter.py` conflict with R9-SW-4 (#2008) was resolved by keeping both sides in `_arbitrate`: the command takes `_without_block(coord, _share(...), now)`, and `_write_night_schedule(coord, inp, now)` follows it. The night-mode registers are a schedule, not a duty, so a block does not gate them. The row is `dev/programme/delivery/1997.md`.

## Mutation proof

Replacing `action["power"] = 0.0` in `_zero_blocked` with `action["power"] = action["power"]` made `PYTHONPATH=tests/hastub python3 tests/block_duty.py` exit 1 with `FAIL a space block zeroes space power and not the supply switch` and `FAIL a space block does not invent power_normalized` (2 of 46). Restored, it exited 0.

Deleting `and _window_open(snap, now)` from `_dhw_floor` made the same command exit 1 with `FAIL the tank at its minimum outside a demand window does not release` (1 of 46). Restored, it exited 0.

The merge-resolved line: replacing `desired(coord, inp, _without_block(coord, _share(coord, inp, duty, now), now), now)` with `desired(coord, inp, _share(coord, inp, duty, now), now)` in `_arbitrate` leaves `tests/block_duty.py` at exit 0, because that script drives `_arbitrate` in observe mode only. `PYTHONPATH=tests/hastub python3 tests/features.py` on that mutant, at this head and at `dc2e16f3416cafb371ad21187674c88f5026ccb2`, added `FAIL a space block keeps the lease expiry on hot water, not the baseline's both duties` to the failures of the unmutated run.

## Null control

With the tree restored, `PYTHONPATH=tests/hastub python3 tests/block_duty.py` exited 0, printed `ok` for `no block leaves the action unchanged`, and printed `ALL 46 BLOCK DUTY CHECKS PASSED`.

`tests/features.py` unmutated, run on this Mac seat at `dc2e16f3416cafb371ad21187674c88f5026ccb2` (this head's first parent, before #2009 merged), exited 1 with one failure, `R9-F2.1 P3: the shipped storage plan is no worse on its own objective than the half-price floor's plan refined under it`. That check compares solver objectives, which do not reproduce across BLAS builds (`CLAUDE.md` rule 3). It touches no file in this diff. CI's `fast` job is the authority for it.

## Figures

```
PYTHONPATH=tests/hastub python3 tests/block_duty.py
```

```
PYTHONPATH=tests/hastub python3 tests/features.py
```

```
git merge-tree --write-tree origin/main HEAD
```

```
python3 tests/structure.py
```

```
PYTHONPATH=tests/hastub python3 tests/entities.py
```

```
PYTHONPATH=tests/hastub python3 tools/audit/round4/D6/claims.py
```

```
PYTHONPATH=tests/hastub python3 tests/env_drift.py --claims-only $(git merge-base origin/main HEAD)
```

```
python3 -c 'import json; p=json.load(open("tests/closures.json")); r=p["recorded"]["tests/block_duty.py"]; files=p["closures"]["tests/block_duty.py"]; print(r["rc"], "custom_components/heatpump_optimizer/quiet_windows.py" in files, "custom_components/heatpump_optimizer/modbus_prefill.py" in files, len(files))'
```

The closures command printed `0 True True 82`. `tools/audit/round4/D6/claims.py` regenerated `claims.json` and `claims.md` with no diff against the head. `tests/structure.py` printed `STRUCTURE RATCHET PASSED`. `tests/closure.py select` printed `MODE: FULL`, because the diff changes `tests/derive_closures.sh`; the full suite is CI's.

## Red checks

Failure conclusions across `git rev-list $(git merge-base origin/main HEAD)..HEAD`, read from each commit's check runs, `pr-contract` excluded: `closures`, `closures-autofix`, `delivery-status`, `fast (3.14)`, `mutation`, `mutation-autofix`, `nightly-status`.

`closures` — a recording of `tests/block_duty.py` read `custom_components/heatpump_optimizer/quiet_windows.py`, and on a later merge `custom_components/heatpump_optimizer/modbus_prefill.py`, neither of which the committed closure listed. `tests/closure.py check --partial` printed `UNDER-SCOPED` until each was committed to `tests/closures.json`; the closures command in `## Figures` shows both listed now. Cheaper detector: `closures_verdict` in `tools/pr/prepr.sh`, which reads the recording's `rc` and runs that check. Standing cost is one `./tests/derive_closures.sh --single` of the script the log names.

`closures-autofix` — the artifact's only recording with `rc` 1 was `tests/stress.py`, so the job printed `AUTOFIX: skip-failed-recording`. Cheaper detector: the same `closures_verdict`, which refuses a non-zero recording `rc`. Standing cost is a read of the recordings the `closures` job already uploaded.

`delivery-status` grades `main`. Cheaper detector: none.

`nightly-status` grades `main`. Cheaper detector: none.

`fast (3.14)` — cheaper detector for an unwired script: the `UNWIRED TEST` line printed at the start of the job, which adds no standing cost of its own. For an entities failure in the same job: none. `tests/entities.py` is the detector.

`mutation` — cheaper detector: `tests/mutation_table.py`'s inventory, which prints `MUTATION TABLE REFUSED` for unpinned sites before it drives a mutant. Standing cost is that inventory.

`mutation-autofix` — the job printed `AUTOFIX: skip-no-measurement`. Cheaper detector: that summary line, which is this job reading the `mutation` job. Standing cost is the `mutation` job it already ran.

## Forward-carry

none

## Friction

none
