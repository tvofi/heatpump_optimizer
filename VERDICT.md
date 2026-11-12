Fix review: merge b4a663ebe57af9f9ab83cc9d70452f8a642026ab

bus-nonce: 30950f2dc2970733b7c3dbe3a3e94af4

## Summary
Round 1, handoff review before a pull request exists. Head b4a663ebe57af9f9ab83cc9d70452f8a642026ab on base 19baca76181cb019d9b1cfd93ee6bc0a08e20047, as BODY.md (handoff-body ref b07c80bed8ce505caba4cbc5615e49b7bf3b4ba9) states. The legacy-control list moves to tools/policy/legacy_control_files.json; the cap stays the literal `LEGACY_CONTROL_CAP = 14` in the pinned grader. The cap cannot be raised by editing the data file. The linter refuses exactly what it refused before. The new arm kills its named mutant, and the data read fails closed.

## Findings
- Out of scope: the cap bounds only the size of the set. It does not bound which carries are in it. With the list in unpinned data, a pull request that delists a repaired member can list a different carry with missing controls in the same edit, and CI passes. Mutant m6 shows this: carry-1067 is replaced by a new uncontrolled carry-99067 in dev/programme/carries, LEGACY-CONTROL says ok, and none of the new carry's control errors are reported. At this head the set sits at its cap (14/14), so the only way in is a one-for-one swap. Once part 2 delists carry-1412, there is a free slot of 1 that only the data file guards. The comment saying "the set may only shrink" now overstates what is enforced. Part 2 should lower LEGACY_CONTROL_CAP in the same pull request that delists, which is safe because the base's higher cap governs that pull request. It should also check that no listed name is absent from the base's list. Precondition for part 2's control: with a member delisted, adding any other carry to legacy_control_files.json must be refused. Carry: dismissed: the dispatch already names part 2 (repair carry-1412, delist, survey the listed files) as its own dispatch after this merges, and this belongs in that brief. The orchestrator must write it into part 2's brief before dispatching it (finding-propagation.md).

## Evidence
- RESULT null-control: `node tools/policy/brief_lint.mjs` at base worktree rc=0 and at head worktree rc=0. The diff of the two outputs is only the added `LEGACY-LISTED-CLEAN ok` line plus one blank line: 2 added lines, 0 removed (ev/lint-null-control.diff). Both show TOTAL: 0 error(s) across 46 file(s) and CARRY: 45. The body says "3 added lines". I measured 2. Both counts agree that nothing was removed.
- RESULT entries: the base literal and legacy_control_files.json hold the same 14 names. A script re-derived `entries equal: True 14 14`. The cap literal is 14 at base and at head.
- RESULT mutant m1 (staleLegacyMembers loops over `[]`, the body's named mutant): `LEGACY-LISTED-CLEAN VACUOUS`, rc=1, so the mutant is killed. The pre-existing LEGACY-CONTROL arm stays ok under m1, so the new arm is the only one that kills it (ev/mutant-m1.*).
- RESULT mutant m2 (LEGACY_CONTROL_FILES = empty set): TOTAL 27 errors, `CONTROL VACUOUS`, rc=1.
- RESULT m3 (data file malformed JSON): TOTAL 27 errors, rc=1. The read fails closed, as the code comment claims.
- RESULT m4 (cap-raise attempt: a 15th name added to the data file): `LEGACY_CONTROL_FILES holds 15 files, over its cap 14: the set only shrinks`, rc=1. The cap cannot be raised through the data file.
- RESULT m5 (delisting a member that still needs the exemption, carry-1067): TOTAL 2 errors, rc=1.
- RESULT m6 (swap, see Findings): rc=1 only because my sed rewrite left a dangling path citation (1 error). There were no control errors and LEGACY-CONTROL was ok.
- Pinning: tests.yml `briefs` restores `tools/policy/*.mjs` and `*.py` from the base. `*.json` is not restored, so the data file is the pull request's own and the cap is the base's. This matches the stated design.
- Classification: legacy_control_files.json falls under the INERT prefix `tools/policy/`. No gate script opens it: tests/entities.py does not run brief_lint.mjs, and the recording below has 0 occurrences.
- Closures refusal named in the body: in this image, with `env -u BASH_ENV`, `PYTHONPATH=tests/hastub python3 tests/entities.py` gives "ALL 2709 ENTITY CHECKS PASSED", rc=0 (ev/entities-head-full.tail.txt). `env -u BASH_ENV bash tests/derive_closures.sh --scripts-from <tests/entities.py> --record-only` gives "done tests/entities.py (exit 0)", rc=0 (ev/derive-closures-entities.txt, ev/entities.py.json). The refusal does not reproduce at this head, which supports the body's account. Its cause stays unconfirmed: a BASH_ENV profile or a leftover concurrent run are both plausible.
- Merge: `git merge-tree --write-tree origin/main b4a663eb` gives rc=0 and tree 55955d03ca348b3a48bd83cfc37f1ad8ec83c343 (origin/main 005eed2573da9e946fa4838de147401d0ff36cc1). It merges cleanly.
- `git diff merge-base...origin/main -- dev/governance/roles/` is empty, so the contract is current.
- VERSION, the manifest, RELEASE_NOTES.md, both claim files, every *_budgets.json, tests/closures.json and tests/closure.py are untouched (the three-dot diff touches 2 files: brief_lint.mjs and legacy_control_files.json). env_drift is not needed: no fixture or solver path changed.
- CI: no pull request exists yet, so there is no review packet, no check runs and no `pr-contract` run to read. The body's `## Red checks: none` cannot be checked against live runs. The train re-proves this on the pull request.
- Harness: this is a tooling hotfix with no finder's harness. The instrument is the fixer's own in-tree arm `assertLegacyListedClean`, re-run here. The checks the dispatch named (cap, null control) are my own runs.
- Not re-derived: the body's "failing test first: ReferenceError". The branch is a single commit, so the earlier state is not in history.
- Class: the body names no enumeration rule, and the dispatch states a single seam (one registration literal), so this is a one-seam class. I did not hunt for other literals in pinned graders.
- Forward carry: the body names part 2 as its own dispatch. No roster carry exists to open.
