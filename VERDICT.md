Fix review: merge c12695cff70ec25c45085b1dae7a4044c0287087

bus-nonce: a2e2e4e4501925efb3028dc2c5cd0ec6

Round 3 of #3667. This is a delta review over the reviewed head 4fba42d0851101ef4f3994060e2cd092eac2bb2c, run from a detached worktree at the head c12695cff70ec25c45085b1dae7a4044c0287087.

## Evidence

- Scope: the packet's `## Review scope` reads `delta`. Since 4fba42d085 the PR has added two commits of its own: `7860872aea` (a two-ended clamp check for `_scaled`) and `dcedcd330c` (the ledger pin `_scaled.CLAMP_DROP.8c7e424f`). It has also merged main three times (`064b60f7b2`, `8fbbe09acf`, `c12695cff7`). The production change and the pin had already reached main through #3678, which was stacked on this branch. Against the merge base b6e52b0598, the PR's three-dot diff is two files: `tests/features.py` +12 (round 1's degF check) and `dev/programme/delivery/3667.md`. `git diff b6e52b0598...head -- custom_components/ VERSION RELEASE_NOTES.md` is empty (ev/own-diff.txt). The delta touches no production code, so the review is not widened.
- The previous block is resolved. The `inputs.py:287 _scaled` `CLAMP_DROP` site is now killed at this head:
  - M1 drops the upper bound (`min(max(scale, MIN), MAX)` becomes `max(scale, MIN)`, ev/m1-drop-max.diff). `PYTHONPATH=tests/hastub python3 tests/features.py` prints `1 of 5833 FEATURE CHECKS FAILED`, rc=1 (ev/features-m1.log).
  - M2 drops the lower bound (it becomes `min(scale, MAX)`, ev/m2-drop-min.diff). The same command prints `1 of 5833 FEATURE CHECKS FAILED`, rc=1 (ev/features-m2.log).
  - Under both mutants the failing check is main's `the staleness scale is clamped at both ends ...`. M1 reads `[180.0, 180.0, 3600.0, 360000000000.0]` and M2 reads `[0.0, 180.0, 3600.0, 3600.0]` (ev/killing-checks.txt). Each mutant moves only the arm on its own side. The in-range ends pass through unchanged under both, which is the null control.
  - Unmutated, the suite prints `ALL 5833 FEATURE CHECKS PASSED`, rc=0 (ev/features-head.log). The pin `tests/mutation_ledger/killed_by/inputs.py/_scaled.CLAMP_DROP.8c7e424f.json` is on main and agrees with this kill.
- The previous verdict's two dismissed follow-ups (the `rooms.ROOMS_MAX` writer and the joined ECL110 line) are not touched by this delta. They stay dismissed.
- Merge resolutions: `git show --remerge-diff 8fbbe09acf` resolves `tests/deployment_shape.py`, `tests/features.py` (it drops the branch's duplicate clamp check in favour of main's) and three ledger files: `rooms.py` `published.GUARD_OFF.cdba2f29` and `readings_of.RETURN_DEL.627b05e8` take main's side, and `sensor.py` `RoomSpreadSensor...RETURN_DEL.c783d968` is deleted. The other merges, `064b60f7b2`, `8fdb89b825` and `c12695cff7`, show no resolution. None of these touch `custom_components/` (ev/remerge-diff.txt). The body describes them the same way.
- Figures re-derived at this head:
  - `ALL 2731 ENTITY CHECKS PASSED` (ev/entities-head.log).
  - `STRUCTURE RATCHET PASSED` (ev/structure-head.log).
  - `python3 tests/closure.py select --diff $(git merge-base origin/main HEAD)` prints `MODE: SCOPED -- 2 script(s) run, 31 scoped out.` (ev/scope.log).
  - All three match the body. The features count does not, as the note below explains.
- Merge with main: `git merge-tree --write-tree origin/main c12695cff7` exits 0 against origin/main e3c75934c2 (ev/merge-tree.txt).
- CI: `merge_train.py classify c12695cff70ec25c45085b1dae7a4044c0287087 --pr 3667` exits 0 with `GREEN c12695cff70ec25c45085b1dae7a4044c0287087 pending: none red: none` on both reads (ev/classify.log).
- Role contract: `git diff $(git merge-base origin/main HEAD)...origin/main -- dev/governance/roles/` is empty.
- Note: stale-body: the body says `ALL 5828 FEATURE CHECKS PASSED` "at this head". That figure was measured at `8fbbe09acf`; this head merges main b6e52b0598 and prints 5833. The body's `## Head` section also repeats the `230141af81` paragraph and lists heads it has since superseded. Carry: dismissed: paperwork; the verdict states the figure at this head.

## Red checks

- None. classify reports `red: none` at this head, and no check in the `owed-reds` set (ev/owed-reds.txt) is red.
