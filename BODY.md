Block DHW and Block Space Heating are two-hour switches. A block zeroes that duty on the copy of the plan action, and a safety floor releases it. The arbiter pass still drops a blocked duty, and it also holds the GCHV night-mode window. State stays in the boost store's weak map.

Closes #1926

Leaves #201 open.

_Requested by **tvofi**_.

## Head

`43cc1031b4ceefb43061fd982ae28955057bb2dd`

Measured `date -u` 2026-10-07T03:48:01Z against origin/main `421c77f950072f218d856dcf60f753e5f80ef10b`. `git merge-tree --write-tree origin/main HEAD` exited 0. The row is `dev/programme/delivery/1997.md`. `git cat-file -e HEAD:docs/delivery/1997.md` exits 128. `tests/closures.json` records `tests/block_duty.py` with `rc` 0 and lists `custom_components/heatpump_optimizer/quiet_windows.py` and `custom_components/heatpump_optimizer/modbus_prefill.py` among 82 files.

## Mutation proof

Replacing `action["power"] = 0.0` in `_zero_blocked` with `action["power"] = action["power"]` made `PYTHONPATH=tests/hastub python3 tests/block_duty.py` exit 1. It printed `FAIL a space block zeroes space power and not the supply switch` and `FAIL a space block does not invent power_normalized` (2 of 46). Restored, the same command exited 0.

Deleting `and _window_open(snap, now)` from `_dhw_floor` made that command exit 1. It printed `FAIL the tank at its minimum outside a demand window does not release` (1 of 46). Restored, the same command exited 0.

## Null control

With the tree restored, `PYTHONPATH=tests/hastub python3 tests/block_duty.py` exited 0 and printed `ok` for `no block leaves the action unchanged` and `ALL 46 BLOCK DUTY CHECKS PASSED`. `PYTHONPATH=tests/hastub python3 /tmp/hpo-r9-sw-5-rec/release_probe.py` calls `block_release_reason` and `overlay` and printed `PROBE 32 of 32`.

## Figures

```
PYTHONPATH=tests/hastub python3 tests/block_duty.py
```

```
git merge-tree --write-tree origin/main HEAD
```

```
git cat-file -e HEAD:dev/programme/delivery/1997.md
```

```
git cat-file -e HEAD:docs/delivery/1997.md
```

```
python3 -c 'import json; p=json.load(open("tests/closures.json")); r=p["recorded"]["tests/block_duty.py"]; files=p["closures"]["tests/block_duty.py"]; print(r["rc"], "custom_components/heatpump_optimizer/quiet_windows.py" in files, "custom_components/heatpump_optimizer/modbus_prefill.py" in files, len(files))'
```

```
PYTHONPATH=tests/hastub python3 /tmp/hpo-r9-sw-5-rec/release_probe.py
```

## Red checks

Failure conclusions across `git rev-list $(git merge-base origin/main HEAD)..HEAD`, `pr-contract` excluded: `closures`, `closures-autofix`, `delivery-status`, `fast (3.14)`, `mutation`, `mutation-autofix`, `nightly-status`. The two unpushed commits in that range answer 422 and have no runs.

`closures` — a `--record-only` recording of `tests/block_duty.py` after the absorb had `rc` 0 and read `custom_components/heatpump_optimizer/modbus_prefill.py`, and `tests/closure.py check --partial` printed `UNDER-SCOPED` until that file was committed. Cheaper detector: `closures_verdict` in `tools/pr/prepr.sh`, which reads the recording JSON `rc` and runs that check. Standing cost is one `./tests/derive_closures.sh --single` of the script the log names.

`closures-autofix` — the closures artifact's only recording with `rc` 1 is `tests/stress.py`. `tests/block_duty.py` in that artifact has `rc` 0. The job printed `AUTOFIX: skip-failed-recording` and `THE REPAIR DID NOT HAPPEN`. Cheaper detector: the same `closures_verdict`, which refuses a non-zero JSON `rc` as `failed while being recorded`. Standing cost is a read of the recordings the `closures` job already uploaded.

`delivery-status` grades `main`. Cheaper detector: none.

`nightly-status` grades `main`. Cheaper detector: none.

`fast (3.14)` — cheaper detector for an unwired script: the `UNWIRED TEST` line printed at the start of the job, which adds no standing cost of its own. For an entities failure in the same job: none. `tests/entities.py` is the detector.

`mutation` — cheaper detector: `tests/mutation_table.py`'s inventory, which prints `MUTATION TABLE REFUSED` for unpinned sites before it drives a mutant. Standing cost is that inventory.

`mutation-autofix` — the job printed `AUTOFIX: skip-no-measurement`. Cheaper detector: that summary line, which is this job reading the `mutation` job. Standing cost is the `mutation` job it already ran.

## Forward-carry

none

## Friction

none
