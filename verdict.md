Fix review: merge 0644c36d4831afd2593f39af61708647035b9972

Round 2 of R10-CI-LAYOUT-P1 (#2585), measured at head 0644c36d4831afd2593f39af61708647035b9972 (code head 2bd0e21b1 plus a main merge and the delivery-row commit), merge base 57f0c9c77cfd. dev/governance/roles/ is identical on main and at the merge base. Seat: Linux cloud, /opt/hpo/venv-ci. Evidence in ev/.

## Fix, failing check first, mutation proof

- Old head 31cf0426: `ref_privacy.py --check` prints `REFUSE .github/workflows/nightly.yml:381 ...`, `1 refused`, rc 1 (ev/ref_privacy_old.txt), the step that reddened instrument-self-tests there.
- This head: `20 file(s) with a push site, 9 guarded, 1002 line(s) added since 57f0c9c77cfd judged, 0 refused`, rc 0; self-test `66 checks, 0 failed` (ev/ref_privacy_head.txt).
- M7 re-run by me at this head: deleting nightly.yml's two-line PUSHERS entry (`1 file changed, 2 deletions(-)`) brings back the same nightly.yml:381 refusal, `1 refused`, rc 1 (ev/m7.txt). The test is not vacuous.
- CI at this head: `instrument-self-tests` concluded success (check-run 119435566558).
- Class: `ref_privacy.sites(grep("HEAD"))` returns 20 files; the two this PR moves sites between are tests.yml [2344, 2616, 2904] and nightly.yml [381, 746, 867], exactly the body's lines (ev/class_head.txt). The moved sites are main pushes and record/autofix pushes, which matches the new entry's reason. The wider `git grep -l workflows/tests.yml` class returns 19 files, as the body says.

## Figures re-measured at this head

RESULT entities ALL 2388 ENTITY CHECKS PASSED rc 0 (includes `one script run past the every-script-once budget turns the CI ratchet red, and the budget is that count`)
RESULT structure STRUCTURE RATCHET PASSED rc 0
RESULT archscore `score.py --diff 57f0c9c77 HEAD` Architecture score: dS +0.0000 NULL
RESULT closure selftest ALL 112 closure shrink pins PASSED
RESULT unitcheck head STATIC rows 225->232 lost 0 changed 29 misplaced 0 rc 0; plant lost 1 rc 1
RESULT jobs tests.yml 19, nightly.yml 6
RESULT self-tests merge_main_bot 40/0, orchestrator_tick 172/0, merge_train 198/0, ci_ratchet 15/0, selftest_wiring 38 wired 0 unwired, tmp_paths 0 refused
RESULT policy_lint TOTAL: 0 error(s) across 41 policy file(s); RULES-SYNC ok
RESULT c1_consumers HEAD lists 6 files, the same 6 the body disposes
RESULT merge-tree `git merge-tree --write-tree origin/main 0644c36d` rc 0, tree 1f19cca4c (clean, and no claim-file conflict)

- One figure differs: the body's `## Figures` gives `1001 line(s) added` for `ref_privacy --check` "at this head". That count is 1001 at the code head 2bd0e21b1 (ev/ref_privacy_code_head.txt), and 1002 at 0644c36d because the orchestrator's delivery-row commit (`dev/programme/delivery/2585.md`, +1 line) was added after the body was written. It is a counter of added lines, not a claim this PR makes; the verdict figure `0 refused` holds at both. Carry: dismissed: counter moved by the later delivery-row commit, not by the fix (item 417eb028)

## Red checks at this head (check-runs API)

- `nightly-status` (119435894694) is red at this head. Its log matches the body: `PINNED: 57f0c9c77`, `NIGHTLY FAILED: mutation-nightly, slow failed last night`, scheduled run 39563978649. It grades main. This PR's own run uses main's pinned grader, so moving the lanes changes nothing it reads here. After the merge, main's `DEFAULT_WORKFLOW` reads nightly.yml, and it reads RUNNING/ABSENT until a Nightly dispatch concludes. The body says this and carries the dispatch. Answered.
- `budget-raise-gate` (119435566980, 119435566119): `RAISE tests/ci_budgets.json: script_runs_per_push: 53 -> 54`, `REFUSED: no decisive review by tvofi`. It waits on the approving review at this head. Answered.
- `instrument-self-tests`: green here, so the old head's red is answered by the fix plus a cheaper detector (ref_privacy --check in prepr.sh, 0.67 s). Process state (a) is carried to R10-CI-LAYOUT.
- Heavy lanes `fast (3.14)`, `closures` and `coverage` of Tests run 39661552604, and CodeQL `Analyze (python)`, were still in_progress when I read them. They are cited, not re-run. If `closures` prints UNDER-SCOPED, the body already names it. Any other red there is unverified by this seat. Carry: R10-CI-LAYOUT-P2 (item e8bdafbd)

## Raise

- `tests/ci_budgets.json` `script_runs_per_push` 53 -> 54 is the only budget move. `## Raise justification` lists four payments and an `Architecture score: dS` line, which I re-ran: dS +0.0000 NULL.
- The row is pinned equal to the derived every-script-once count (34 closures plan + 20 fast), and entities passes it. So the raise is earned by W1 removing C1, not by the instrument.
- Payments 1-2 are the composition that owner ruling D-4 refuses, and payments 3-4 delete coverage. I found no further payment: any one-run saving must stop one of the 20 shared scripts from being executed twice, and that is C1's mechanism.

## Other

- VERSION, the manifest version and the RELEASE_NOTES heading are untouched in the diff. No claim file is touched.
- PR G #2529 orders before this one at merge only. selftest_wiring is owed again at that merge, as the body carries. Carry: R10-CI-LAYOUT-P2 (item f3c97a50)
- `ref_privacy.py --check` is not in prepr.sh (second instance, after #2447). The countermeasure belongs to a root-cause seat, not this fix. Carry: R10-CI-LAYOUT (item 4ee9730e)

bus-nonce: b3d22be827f314626bbccf241e7a127e
