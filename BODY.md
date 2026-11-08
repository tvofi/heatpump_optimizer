R10-FRICTION-OTHER-FAMILY part 2. Folds `red-checks` into the `root-cause` friction family in `tools/policy/policy_lint.mjs`, which is the one countermeasure #3311's record (`R10-RCA-OTHER-UNTAUGHT.md` section 6, item 2) left owed. Adds the window record `dev/audit/rca/R10-RCA-FRICTION-OTHER-FAMILY-P2.md`.

Dispositions. #3283: the record and its countermeasure are now both in the tree. #3313 (`class-open`) and #3314 (`mutation-vacuous`) are not delivered by #3311 or by this part: each rests on an owner ruling already recorded in `R10-RCA-CLASS-OPEN.md` and `R10-RCA-MUTATION-VACUOUS.md` and still open, and the v7.1.5 window re-read adds no new cause. They are not closed. The honest limit: `other (untaught) (family)` still reads 6 PRs at v7.1.5, because the derived family does not subtract a declared family's members; the fold does not quiet #3283, it makes the obligation countable beside its siblings.

Closes #3283

## Head

7b272ef79cd53ccf9fa01eb9d29ac6ea1c13d6e0, on `origin/main` 51cd5ec8a42abde3c223f22e9f4a0d5f35f8844a (unmoved since the last `tools/pr/prepr.sh` run, which exited 0 at this head; no second run owed).

## Mutation proof

Delete the added member `'red-checks'` from `FRICTION_FAMILIES.root-cause` and run `node tools/policy/policy_lint.mjs --self-test`: it printed `FIXTURE VACUOUS: the derived ... root-cause family did not fold as pinned`, from the new `rcSpelled` pin. Restored, the same run prints no `FIXTURE VACUOUS` and ends `FIXTURE ok: 93 error(s) hold 269 pins`.

## Null control

The same pin folds `root-cause-detectable` + `root-cause-unrecorded` alone (no `red-checks`) to a family of 2, asserted by `rcNull`; the unmodified tree gives that 2 as well, so the pin reads the member and not the family's mere existence. `--stats --since v7.1.5` on the merge base prints no `root-cause (family)` row; at the head it prints `1 / 2`.

## Figures

- `node tools/policy/policy_lint.mjs --stats --since v7.1.5` at 51cd5ec8a42a, 2026-11-08 21:07Z: `class-open` 7 PRs / 10 entries, `mutation-vacuous` 6 / 11, `red-checks` 1 / 2, `other (untaught) (family)` 6 / 7. Window-dependent: re-derive, do not copy.
- `python3 -I dev/audit/rca/ci-red/entries.py W.json class-open` prints `ENTRIES 10 PRS 7`; the same for `mutation-vacuous` prints `ENTRIES 11 PRS 6`; for `red-checks` `ENTRIES 2 PRS 1`. (`W.json` is the `--window-cache` of the stats run above; a key with no entries prints `ENTRIES 0 PRS 0`.)
- `bash tools/pr/prepr.sh` at the head: exit 0, `STRUCTURE RATCHET PASSED`, `self-test 514 passed, 0 failed`.

## Unpinned sites

n/a: the diff adds no `custom_components/` or `tools/` production site; the one `tools/policy/policy_lint.mjs` change is a list entry pinned by the `rcSpelled` assertion above.

## Red checks

none

## Forward-carry

none

## Friction

none

## Approval

Approval owed under the mandate: `tools/policy/policy_lint.mjs` decides which friction issues the cron files, and the new record is development-record policy text. Merge waits on the owner's approving review.

## Not established

Per-key PR lists were read from the window cache, not re-read from each comment. Whether the derived family should subtract declared-family members is a separate keying-rule change, not made here.
