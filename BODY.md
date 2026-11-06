The owner's ruling (tvofi 2026-11-06), verbatim: "The HTML plan seems to incorrectly place some instrument or CI fixes in the core model lane, fix that".

The lane is decided in one place, `roster_lane` in `tools/plan/replan.py` (`plan_page.py` only reads `pg["lane"]` from the plan JSON). It matched group-name prefixes and `kind`, and fell through to "Core model" for everything else, so a hotfix named `R10-HOTFIX-*` or `R10-PROCESS-SLIM` landed in the core lane whatever files it owned. It now reads the files a group owns first: when every owned file is an instrument, CI, test or record path, the group is Instruments (Docs for a `kind: doc` group or a user-docs group). A group owning no file, a bare filename, or any `custom_components/` file stays where it was. The fix is made once, at the source, not per group.

## Head

a6e3c0d76251c0d56c4296278161bdd7b37b0166 (origin/main merged at 28482eceeb6b9809e44b12d80fc994282cc21645, 2026-11-06; the merge was clean and `tools/pr/prepr.sh` was rerun on the merged head: rc=0).

## Mutation proof

Mutating the predicate (`return owned` replaced by `pass` in `roster_lane`) and running `python3 -I tools/plan/replan.py --self-test` makes these fail: `lane: a CI-only group is Instruments`, `lane: a tests-and-tools group is Instruments`, `lane: a docs-only doc group is Docs`, `lane: a user-docs group is Docs`, `lane null control: docs plus a tool is Instruments, not Docs`, and the unmutated-copy null control. The file was restored and the self-test then reports `self-test: 0 failed`. The tests were written first and failed on the unfixed tree (4 lane checks red).

## Null control

Core-model groups must stay in the core lane. The self-test asserts it for a group touching `custom_components/heatpump_optimizer/optimizer.py`, a mixed tools plus `custom_components` group, a group with no files, and a bare filename (`coordinator.py`); all stay "Core model" after the fix. In the live roster the 12 groups left in Core model include those owning `thermal_model.py`, `ledger.py`, `optimizer.py` and the other integration files.

## Figures

Before and after lane lists: open groups in the Core model lane, from `python3` calling `replan.roster_lane` over `roster_lib.load_roster_file(roster_lib.roster_path())` (dev/programme/rosters/wave-r10-groups.json at the base), skipping `replan.is_done` groups. Before the fix, 22 groups:
ARCH-SHAPES-CLASSIFIER, CARRY-RESIDUE-2, CATALOG-PR, CLONE-2238, COP-GATE-D, FLY-ARCHSCORE-STMT-PACKING, FRICTION-RECORDS, HOTFIX-CI-CRITPATH-4, HOTFIX-GATE-BUSY-DEFER, HOTFIX-GATE-STALE-JOBS, HOTFIX-RECORD-ATTRIB, HOTFIX-SAV-ESTIMATE, OVERBOOK-RESIDUAL, PARTLOAD-PRICING, PROCESS-SLIM, PROD-RESIDUE-PINS, RCA-SAV-ESTIMATE, ROUND-PLAYBOOK, SAV-METER-FLOOR, SAV-WOOD-MEASURED, USER-DOCS-VERIFY, WHY-NOW-WIDGET (all prefixed R10-).
After the fix, 12 groups: ARCH-SHAPES-CLASSIFIER, CARRY-RESIDUE-2, CATALOG-PR, CLONE-2238, COP-GATE-D, HOTFIX-SAV-ESTIMATE, OVERBOOK-RESIDUAL, PARTLOAD-PRICING, PROD-RESIDUE-PINS, SAV-METER-FLOOR, SAV-WOOD-MEASURED, WHY-NOW-WIDGET.
Moved to Instruments (8): FLY-ARCHSCORE-STMT-PACKING, FRICTION-RECORDS, HOTFIX-CI-CRITPATH-4, HOTFIX-GATE-BUSY-DEFER, HOTFIX-GATE-STALE-JOBS, HOTFIX-RECORD-ATTRIB, PROCESS-SLIM, RCA-SAV-ESTIMATE. Moved to Docs (2): ROUND-PLAYBOOK, USER-DOCS-VERIFY. (8 + 2 = 10 = 22 - 12.)
Not moved, by decision: CARRY-RESIDUE-2 and CATALOG-PR list no files in the roster (CARRY-RESIDUE-2 is a policy-line group), so the file rule has nothing to read; fixing their roster `files` is a roster edit this group does not make. HOTFIX-SAV-ESTIMATE owns `external_heat.py`, `ledger.py`, `optimizer.py`, so it is core-model work.
Instruments run: `python3 -I tools/plan/replan.py --self-test` (0 failed), `python3 tests/structure.py` (passed), `tests/entities.py` (2637 checks passed), `tools/pr/prepr.sh` (rc=0). The enumeration rule for the class is `roster_lane` itself over every roster group; no group's open/done state or schedule was changed.

## Red checks

none

## Forward-carry

none

## Friction

none
