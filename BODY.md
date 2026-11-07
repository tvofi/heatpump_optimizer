Outside work orders ahead of audit and owner work in the three orderers, after main and hotfix.

Owner ruling (tvofi 2026-11-07T19:40Z, triage batch 134 P420), verbatim: "all accepted outside issues or contributions should be prioritized higher than audit or owner submitted ones unless i call the owner one a hotfix."

Added `roster_lib.is_outside(group)` (true when `source` is the string `outside`; absent means internal, the contract) and `roster_lib.group_for_pr(roster, pr)` (`resume.pr`, for fork heads). R10-CI-PRIORITY-PAUSE's source enum is not built.

- `replan.dispatch_tier` (signature kept): tiers are now main, hotfix, outside, critical path, production, instrument. Hotfix was split from the critical path's tier because the ruling puts outside between them; hotfix therefore now precedes the critical path (previously critical path first within one shared tier). `plan_page.py` comment updated.
- `open_driver.default_class/order`: hotfix, outside, critical, record, rest; the fence covers the first three in that order whatever the priority file says. A critical-path group that is a hotfix by name is now class hotfix.
- `merge_train.Train.drain_order`: priority or front, then outside, then critical, then arrival; `Train._outside` maps an entry by branch, else `group_for_pr`. `outside` is injectable like `critical`.

No policy file states the order, so no policy sentence was written; docstrings cite the ruling.

## Head

da8a36ecc777aadd8c00566273d6463de4369b53

## Mutation proof

Each reader's outside term removed, its self-test arm fails:
- replan: `mut tier-outside` (new mutant in the self-test's own list): `self-test fails when tier-outside is deleted`.
- open_driver: `if group and roster_lib.norm_group(group) in outside:` -> `if False:` fails "the fence orders hotfix, outside, critical whatever the file lists", "an outside topic ranks ahead of a critical one and behind a hotfix one, by default", "an outside topic that is also critical is outside; a hotfix one is a hotfix" and the run_pass wiring arm; `outside = set() and {...}` in run_pass fails "run_pass: an outside group opens ahead of the critical path, cap 2".
- merge_train: `not self.outside(...)` -> `False` in drain_order (line tagged `mut:drain-outside`) fails "P420: an outside entry (#3) drains ahead of a critical-path one (#2) and behind a priority one (#4)" and "P420: outside entries keep arrival order among themselves, ahead of the critical path".

## Null control

A roster with no `source` field orders as the base in all three: replan "null control: any other source (or none) is internal"; open_driver "run_pass null: with no source field the critical path opens first, as before" and "null: no outside set orders byte-identically ..."; merge_train "P420 null: no outside entry orders ..." ([4, 2, 1, 3]) and "P420 _outside null: a roster with no source field has no outside entry".

## Figures

Self-tests at the head: `python3 tools/plan/replan.py --self-test`, `python3 tools/audit/seat/open_driver.py --self-test` (83 checks), `python3 tools/audit/seat/merge_train.py --self-test` (477 checks), `python3 tools/audit/seat/roster_lib.py --self-test` (69 checks), all 0 failed. `python3 tests/structure.py`: RATCHET PASSED.
Mutant run (prepr.sh diff-mutant step, MUTANT_CMD = the four self-tests chained, MUTANT_MAX=25, at the commit before the last test pin): the whole prepr.sh run took 23m41s (`real` line of its log; the mutant step is most of it); 25 survivors, all on lines in `merge_train.py`. Before the last test commit; the unreadable-roster arm was then pinned by a new check.
`python3 tests/entities.py` at the head and at base 8a1358e8: both `3 of 2655 ENTITY CHECKS FAILED`, exit 1, the same Pages-workflow probe failure; so prepr.sh's `closures` step REFUSEs on a failure this diff does not cause (the base run is the null control).

## Red checks

none

## Forward-carry

none

## Friction

none

## Unpinned sites

The 25 survivors (prepr log) are: ~17 CONST_SWAP/RETURN_DEL mutations of the added self-test lines themselves (literal PR numbers, fixture dicts, `pass`), which mutate the check and not the reader; the `outside=None` constructor default, the `opts.setdefault("outside", ...)` fixture defaults and the `except Exception: return False` arms of `_outside`. I re-ran two by hand against `merge_train.py --self-test` (`self.cp_read[0]` -> `[1]` in `_outside`: `P420 _outside` check fails; `not self.outside(...)` -> `False` in drain_order: both P420 drain checks fail), which the runner reported as survived, so the runner's survivor count over-reports here (its chained `&&` command in a copy is the suspect; not diagnosed). Disposition: value checks above, plus a new check pinning the unreadable-roster arm.
