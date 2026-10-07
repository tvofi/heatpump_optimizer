Block DHW and Block Space Heating are two-hour switches. A block zeroes that duty on the copy of the plan action, and a safety floor releases it. State stays in the boost store's weak map.

Closes #1926

Leaves #201 open.

_Requested by **tvofi**_.

## Head

`2a503e10424f37f60f38d626f09cb5625f623f8a`

Measured `date -u` 2026-10-07T03:39:19Z against origin/main `bcea74883bec1e3395377ff70d8640737c97fc3e`. `git merge-tree --write-tree origin/main HEAD` exited 0. The row is `dev/programme/delivery/1997.md`. `git cat-file -e HEAD:docs/delivery/1997.md` exits 128. `tests/closures.json` records `tests/block_duty.py` with `rc` 0 and lists `custom_components/heatpump_optimizer/quiet_windows.py` among 81 files.

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
python3 -c 'import json; p=json.load(open("tests/closures.json")); r=p["recorded"]["tests/block_duty.py"]; print(r["rc"], "custom_components/heatpump_optimizer/quiet_windows.py" in p["closures"]["tests/block_duty.py"], len(p["closures"]["tests/block_duty.py"]))'
```

```
PYTHONPATH=tests/hastub python3 /tmp/hpo-r9-sw-5-rec/release_probe.py
```

## Red checks

`closures` job 112482614284 printed `UNDER-SCOPED: tests/block_duty.py really reads 1 file(s) the committed closure does not list:` and named `custom_components/heatpump_optimizer/quiet_windows.py`. The record step printed `done tests/block_duty.py (exit 0)`. That script's recording JSON has `rc` 0. Cheaper detector: `closures_verdict` in `tools/pr/prepr.sh`, which reads that JSON `rc` and runs `tests/closure.py check --partial`. Standing cost is one `./tests/derive_closures.sh --single` of the script the log names.

`closures-autofix` job 112501591072 printed `AUTOFIX: skip-failed-recording` and `THE REPAIR DID NOT HAPPEN`. In that artifact `tests/stress.py` has `rc` 1 and `tests/block_duty.py` has `rc` 0. Cheaper detector: the same `closures_verdict`, which refuses a non-zero JSON `rc` as `failed while being recorded`. Standing cost is a read of the recordings the `closures` job already uploaded.

`delivery-status` job 112612505848 printed `DELIVERY STATUS UNCHECKED`. Cheaper detector: none. The check grades `main`.

`nightly-status` job 112612505878 failed in the step `Report the last scheduled run's conclusion`. Cheaper detector: none. The check grades `main`.

`fast (3.14)` job 112424333780 printed `UNWIRED TEST: tests/block_duty.py is not referenced by tests/run.sh`, `FAILED python3 tests/entities.py`, and `TEST NEVER RAN: tests/block_duty.py is wired into tests/run.sh but no lane executed it and no lane skipped it on purpose`. Cheaper detector for the unwired line: that line, printed at the start of the job, so it adds no standing cost of its own. For the entities failure: none. `tests/entities.py` is the detector.

`mutation` job 112361301163 printed `MUTATION TABLE REFUSED` for unpinned sites the diff added. Cheaper detector: `tests/mutation_table.py`'s inventory, which prints that refusal before it drives a mutant. Standing cost is that inventory.

`mutation-autofix` job 112363593627 printed `AUTOFIX: skip-no-measurement`. Cheaper detector: that summary line, which is this job reading the `mutation` job. Standing cost is the `mutation` job it already ran.

## Forward-carry

none

## Friction

none
