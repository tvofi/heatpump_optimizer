R10-RCA-PREPR-HEAD-GRADERS is the root-cause record for #2916's red `governance / policy-docs` and `governance / env-matrix`, and the countermeasure it calls for: `tools/pr/ci_predict.py`'s `graders` arm, re-cut at review round 4 so its key is each job's restore pathspecs and not a grammar of what a grader loads.

`f008c2b75` wrote a `named-docs` exclusion into `tools/policy/policy_lint.mjs`'s `CORPUS_EXCLUDED`. CI's restore step graded the PR with the base's copy of that file, so the exclusion was never read, while `prepr.sh` and `ci_predict.py` were green on the same head. Eight round-10 pull requests went red this way (base copy red, head copy green, on CI's merge tree); the class is I3, barriered, past the per-round threshold. **Process state: (c).**

The record is `dev/audit/rca/R10-RCA-PREPR-HEAD-GRADERS.md`; `dev/audit/config/bugclasses.json` cites it under `_rca` and I3; its drivers are in `dev/audit/rca/prepr-head-graders/`.

## Re-cut

Review round 4 blocked `5a119e8af` as `class-open` on `tools/policy/vendor/markdown-it.min.js` and asked for a re-cut (`fixer.md`, past three rounds). This body replaces the earlier one; round history is deleted.

The re-cut takes the reviewer's construction. A governance.yml job holding the "Restore the check source from the base commit" step (`restore_jobs`) is keyed when the diff changes a path its own restore pathspecs cover and the base tip holds (`restored_hit`). The arm then runs every program that job runs (`pinned_runs`, less the `agreement` arm's two and `policy_lint.mjs --report`), on CI's merge tree with the base's copies restored (`ci_tree_run`), one tree per keyed job, side by side. Nothing models what a grader loads, so a `require()`d vendored parser and a spawned Python gate are keyed by the restore list that pins them.

Dropped from the branch: `named_loads`, `mjs_closure`, the `GRADERS` table, `grader_hit`, `grader_gaps`' load census and its `GRADER_NAMED_EXEMPT` table. `lane_files()` is deleted as well: the `agreement` arm is re-keyed onto `restored_hit`. `grader_gaps` stays as a population check only: it names a run line passing a runner token `RUN_TOKENS` does not map, and an exemption no run line still holds.

The cost test (record section 5) picked the arm's place. Where env-matrix is keyed it takes minutes, so it is opt-in under `--record-self-tests`. `prepr.sh` step 6d already passes that flag, and `body_push.sh` stays seconds.

The branch is not a new cut from `origin/main`. Its head descends from `5a119e8af`, so `handoff_push.sh` merges it into the PR branch. Its three-dot diff against `origin/main` is the re-cut and nothing else.

## Head

`7d1fbc055b6a672b718cac56eefa6de633124eca`, measured against `origin/main` `14fbf218d` (2026-10-29). `git merge-tree --write-tree origin/main 7d1fbc055` exits 0: no conflict. `VERSION`, the manifest, `RELEASE_NOTES.md` and both claim files are untouched.

Each round-4 point, answered (the first two in this PR, so they route no carry):
- **Class-open on `markdown-it.min.js`.** Closed by construction: `restored_hit` keys every path a restoring job's pathspecs cover, whatever loads it. The verdict's plant was re-run on this head (`## Figures`). Under round 4's predictor it ran no row, as the verdict found. Under this one all three jobs are keyed and every run is made.
- **Stale `## Head` note.** This body names its own head above. There is no `## Head note`; `handoff_push.sh` writes the merge note.
- **The review packet refusing `host-path` on a cloud seat.** Not this PR's defect, carried as before (`## Forward-carry`). This body cites no path that contains the root account's home as a substring.

## Mutation proof

Run with `python3 -I dev/audit/rca/prepr-head-graders/mutants.py .`. Each mutant is applied to a copy of `tools/pr/`, then `graders_self_test` runs against it. The unmutated tree prints `bad 0`.

- **M1** `restored_hit` returns `[]`: `bad 5`. FAIL `tools/policy/vendor/markdown-it.min.js keys every restoring job`, `tools/policy/budget_raise_gate.py keys every restoring job`, and the three red e2e cases (`#2916's shape`, `round 3's markdown-it.min.js`, `round 2's budget_raise_gate.py`).
- **M2** `restored_hit` ignores the base tip: `bad 1`. FAIL `a restored path the base tip lacks keys no job`.
- **M3** `grader_runs` drops no exemption: `bad 1`. FAIL `the arm makes every pinned run but the agreement arm's and the exempt`.
- **M4** `predict`'s `graders` entry removed: `bad 1`. FAIL `predict reaches the graders arm by name`.
- **M5** `ci_tree_run` restores nothing: `bad 3`. FAIL the three red e2e cases.

## Null control

- In `graders_self_test`, three cases stay green with the arm in place: the repair in an unrestored data file (the grader keyed by a comment), a corpus-only diff (not keyed), and the plant staged but not committed.
- No real run line has an unmapped token. A planted `$ODD` token and a dropped exemption are each named as a gap.
- `corpus_excluded.json` keys no job, and a restored path the base tip lacks keys no job.
- The PR's own head: `ci_predict.py --base origin/main --only graders` keys all three jobs, runs every program, and is green (rc 0).
- The verdict plant under round 4's predictor is the control for the class: rc 0, no row run.
- `keycount.py`'s null pathspec keys 0 of 584 merges.

## Figures

- `python3 -I tools/pr/ci_predict.py --self-test`: `ci_predict self-test: 0 failed`, rc 0. This includes the 15 `graders_self_test` checks and every `plant_self_test` case, each now run with `--only` its own arm.
- `python3 tools/pr/ci_predict.py --base origin/main --only graders` on `5a119e8af`'s tree with this predictor: all three jobs keyed, rc 0, 477.0 s wall.
- `python3 -I dev/audit/rca/prepr-head-graders/jobtime.py 14fbf218d wave-script policy-docs`: wave-script 3.0 s. policy-docs 215.5 s, of which `field_coverage.mjs` 181.6 s and `policy_lint.mjs` 25.0 s. All runs rc 0.
- `python3 -I dev/audit/rca/prepr-head-graders/keycount.py 14fbf218d 2026-10-14`: 584 merges. 69 keyed all three jobs, 1 keyed policy-docs + wave-script, 71 keyed wave-script alone. Null pathspec: 0. Weighted per predictor run: (69 × 477 + 1 × 216 + 71 × 3) / 584 = 57 s. Expected defect cost per PR: 5 / 584 × 9,960 s = 85 s (record section 5).
- `bash dev/audit/rca/prepr-head-graders/plant.sh <head> mdit 5a119e8af <out>`: rc 0, no row run, 0.7 s. This is round 4's miss, reproduced.
- `bash dev/audit/rca/prepr-head-graders/plant.sh <head> mdit <head> <out>`: rc 0 with all three jobs keyed and run, 609 s.
- `bash dev/audit/rca/prepr-head-graders/plant.sh <head> gate <head> <out>`: **rc 1**, `PREDICT governance / policy-docs GRADER policy_lint.mjs REFUSED by the base's copy, over tools/policy/budget_raise_gate.py: FIXTURE VACUOUS: the raise-justification arm on prepr/raise/good.md drew 1 error(s)`, 608 s.
- The same plant under `5a119e8af`: rc 1, the same refusal, plus env-matrix by its row's model, 325 s. The new arm ran env-matrix's matrix program and it passed; no CI run of the plant exists to say which is right.
- The four plant runs shared the host, so their times are contended. `<head>` is the predictor commit `513b608a3`, whose arm code this head carries unchanged.
- `python3 tests/structure.py`: `STRUCTURE RATCHET PASSED`.
- Scope: `python3 tests/closure.py select --diff $(git merge-base origin/main HEAD)` prints `MODE: SCOPED -- 1 script(s) run`, naming `tests/entities.py`. `PYTHONPATH=tests/hastub python3.13 tests/entities.py`: `ALL 2470 ENTITY CHECKS PASSED`.

## Red checks

none. On `5a119e8af`, `governance / instrument-self-tests` concluded `cancelled` at 20 min, not failure. That was the job's 20-minute timeout, which `origin/main` has since raised to 30 for `beatd.py`'s self-test (`14fbf218d`'s governance.yml). It is not this diff's.

## Forward-carry

- `review_packet.py render` refuses `host-path` on a cloud seat. `ref_privacy.Identity.of_host` adds passwd's home and matches it as a bare substring, so a body describing that defect is itself refused. It is an instrument defect in `tools/audit/seat/ref_privacy.py`, outside this class. The open group owning that file already carries it in `dev/programme/rosters/wave-r10-groups.json` (`brief` and `carry`). Carry: R10-RECORD-API-O1

## Friction

none
