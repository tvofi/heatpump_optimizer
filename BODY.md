Lands two round-11 audit box results on main. Each box pushed one result commit with no history shared with main, so neither could be opened as a pull request:

- `handoff/audit-r11-sweep-SW7` (`902e4e66b5`): the class sweeps P1 (10 instances, not barriered), P10 (0) and P11 (3, not barriered), under `dev/audit/rounds/round11/sweep/P1`, `P10` and `P11`, and `reports-SW7.json`.
- `handoff/audit-r11-sweep-SW9` (`32a372faae`): the class sweeps P3 (1 instance, not barriered), P4 (1) and P5 (2), under `dev/audit/rounds/round11/sweep/P3`, `P4` and `P5`, and `reports-SW9.json`.

Every file of the two trees except each box's top-level `CHECK.txt` (it reads `ok` for each of the six sweeps) is copied: 78 files, none on main and none overwriting a main file. No production code changes. Every file sits under `dev/audit/`, which `tests/closure.py` lists as INERT by prefix. This PR does not fold, judge or register anything; the instances still go through the round's verify and judge steps.

Four landed harnesses walked a fixed parent count to the root (`HERE.parents[5]` in `P3` and `P4` `enumerate.py`, `parents[6]` in `P4` `probe_offstart_sites.py` and `P5` `enumerate.py`). At the landed path that names `dev/`, not the root, and `tests/harness_headers.py`'s depth-seam scan refuses it. Each now inlines `tools/audit/repo_root.py`'s `repo_root`. The reports are evidence as the boxes wrote them and name their enumerators at `dev/audit/rounds/round11/D14/sweep-P*/`, the path inside the box; the files land at `sweep/P*/D14/sweep-P*/`.

`python3 tools/pr/ci_predict.py --apply-inert` predicts no red against main `78d3b40221` and changes nothing. No home path appears in the landed files. `tools/audit/machinery_ratchet.py --check` reads `ok churn_per_kilo_product_lines 35281 <= 34898 + band 3636` and no budget is raised.

Issues: none drafted or closed.

## Head

`5680abbb85c5053520ff8c4019e0f3f4a6184763`: the authored head, on origin/main `78d3b40221`. It is one commit: the copy and the repo_root fix.

## Mutation proof

n/a: a record PR carries no fix to break.

## Null control

n/a: no behavioural claim.

## Figures

none

## Red checks

none

## Forward-carry

none

## Friction

none
