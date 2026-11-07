The owner's ruling (tvofi 2026-11-06), verbatim: "The HTML plan seems to incorrectly place some instrument or CI fixes in the core model lane, fix that".

The lane is decided in one place, `roster_lane` in `tools/plan/replan.py` (`plan_page.py` only reads `pg["lane"]` from the plan JSON). It matched group-name prefixes and `kind`, and fell through to "Core model" for everything else, so a hotfix named `R10-HOTFIX-*` or `R10-PROCESS-SLIM` landed in the core lane whatever files it owned. Two rules now sit after the name and `kind` rules and before the core fallthrough:

1. Files owned. When every file a group owns (`files` plus `hot_files`) is an instrument, CI, test or record path, the group is Instruments; it is Docs for a `kind: doc` group or a user-docs group. A group owning no file, a bare filename, or any `custom_components/` file is not placed by this rule.
2. Unplaced tool-landing kind (91ed006b). A group neither the name rules nor its files place is drawn in Instruments when its `kind` is one of `INSTRUMENT_KINDS` (`instrument`, `policy`, `rca`, `tooling`) or its roster `class` is `instrument` (the signal `work_class` already prices); `work_class` now reads the same `INSTRUMENT_KINDS` tuple. Only a group none of these places is Core model.

User docs follow one rule: a group is Docs when it owns `README.md` or a `docs/` file and no file under `tools/`, `.github/` or `.claude/` (`_TOOLING_PREFIXES`); touching a tool makes it Instruments. The fix is made once, at the source, not per group.

## Head

91ed006bab25624a3c4640293a648a58a4071f19 (code head; merge base with origin/main 28482eceeb6b9809e44b12d80fc994282cc21645, branch history: bdae685fb, merge a6e3c0d76, 91ed006ba). origin/main has since moved to 80016a71f567d936450d8708abcbb79d9e8071d7; this body-only re-take changes no code, and the merge and gate result for the moved main is in Instruments run below.

## Mutation proof

Each rule was mutated at 91ed006b and `python3 -I tools/plan/replan.py --self-test` run; the file was restored after each (`git status` clean).
- Files rule (`return owned` replaced by `pass` in `roster_lane`): `self-test: 7 failed`: `lane: a CI-only group is Instruments`, `lane: a tests-and-tools group is Instruments`, `lane: a docs-only doc group is Docs`, `lane: a user-docs group is Docs`, `lane null control: docs plus a tool is Instruments, not Docs`, `lane: user docs with a dev harness are Docs`, and the unmutated-copy null control.
- Kind and class rule (the `INSTRUMENT_KINDS or class == "instrument"` branch replaced by `if False:`): fails `lane: an RCA group with no files is Instruments`, `lane: a tooling group with no files is Instruments`, `lane: a roster class instrument with no files is Instruments` and the unmutated-copy control.
- Single user-docs rule (the `not any(... _TOOLING_PREFIXES ...)` clause removed): fails `lane null control: docs plus a tool is Instruments, not Docs` and the unmutated-copy control.
The unfixed tree is not re-run in this re-take: that the tests were written first and failed there is not verified here.

## Null control

Core-model groups must stay in the core lane. The self-test asserts it for a group touching `custom_components/heatpump_optimizer/optimizer.py`, a mixed tools plus `custom_components` group, a group with no files, a bare filename (`coordinator.py`) and a `production` kind with class `production`; all stay "Core model". Name rules still win: a named UX group keeps Product UX over an `rca` kind and a learner keeps Learners over tool files. In the live roster, 10 of the 11 groups left in Core model own a `custom_components/` file; the eleventh is R10-CATALOG-PR (kind and class `owner-step`, no files).

## Figures

Before and after lane lists, derived by calling `roster_lane` (this head, and `tools/plan/replan.py` at merge base 28482ece for before) over `roster_lib.load_roster_file(roster_lib.roster_path())`, i.e. dev/programme/rosters/wave-r10-groups.json at 91ed006b, skipping `replan.is_done` groups; 68 open groups. Lane counts before: Instruments 40, Core model 22, Product UX 3, Replay 2, Docs 1. After: Instruments 49, Core model 11, Docs 3, Product UX 3, Replay 2.
Before the fix, 22 groups in Core model (all prefixed R10-): ARCH-SHAPES-CLASSIFIER, CARRY-RESIDUE-2, CATALOG-PR, CLONE-2238, COP-GATE-D, FLY-ARCHSCORE-STMT-PACKING, FRICTION-RECORDS, HOTFIX-CI-CRITPATH-4, HOTFIX-GATE-BUSY-DEFER, HOTFIX-GATE-STALE-JOBS, HOTFIX-RECORD-ATTRIB, HOTFIX-SAV-ESTIMATE, OVERBOOK-RESIDUAL, PARTLOAD-PRICING, PROCESS-SLIM, PROD-RESIDUE-PINS, RCA-SAV-ESTIMATE, ROUND-PLAYBOOK, SAV-METER-FLOOR, SAV-WOOD-MEASURED, USER-DOCS-VERIFY, WHY-NOW-WIDGET.
After the fix, 11 groups: ARCH-SHAPES-CLASSIFIER, CATALOG-PR, CLONE-2238, COP-GATE-D, HOTFIX-SAV-ESTIMATE, OVERBOOK-RESIDUAL, PARTLOAD-PRICING, PROD-RESIDUE-PINS, SAV-METER-FLOOR, SAV-WOOD-MEASURED, WHY-NOW-WIDGET.
Moved to Instruments (9): FLY-ARCHSCORE-STMT-PACKING, FRICTION-RECORDS, HOTFIX-CI-CRITPATH-4, HOTFIX-GATE-BUSY-DEFER, HOTFIX-GATE-STALE-JOBS, HOTFIX-RECORD-ATTRIB, PROCESS-SLIM, RCA-SAV-ESTIMATE, CARRY-RESIDUE-2. Moved to Docs (2): ROUND-PLAYBOOK, USER-DOCS-VERIFY. 9 + 2 = 11 = 22 - 11. No group left a non-core lane (0 moves from a lane other than Core model).
CARRY-RESIDUE-2 lists no files in the roster but carries roster `class: instrument`, so the kind and class rule places it in Instruments (the earlier head left it in Core model). CATALOG-PR lists no files and is an `owner-step` kind, so no rule places it and it stays Core model; fixing its roster `files` is a roster edit this group does not make. HOTFIX-SAV-ESTIMATE owns integration files, so it is core-model work.
Instruments run at 91ed006b: `python3 -I tools/plan/replan.py --self-test` (0 failed), `python3 tests/structure.py` (STRUCTURE RATCHET PASSED). `tests/entities.py` could not run in this seat (homeassistant missing from the interim toolchain), so its count is not verified here. prepr: `bash tools/pr/prepr.sh` at 91ed006bab25624a3c4640293a648a58a4071f19 (merged-structure check against origin/main 28482ece): rc=0. origin/main has since moved to 80016a71f567d936450d8708abcbb79d9e8071d7; this body-only re-take does not re-run prepr against it.

## Red checks

none

## Forward-carry

none

## Friction

none
