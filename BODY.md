R10-RCA-PREPR-HEAD-GRADERS is the root-cause record for #2916's red `governance / policy-docs` and `governance / env-matrix`, and the countermeasure it calls for: `tools/pr/ci_predict.py`'s `graders` arm, keyed by each job's restore pathspecs and not by a grammar of what a grader loads.

`f008c2b75` wrote a `named-docs` exclusion into `tools/policy/policy_lint.mjs`'s `CORPUS_EXCLUDED`. CI's restore step graded the PR with the base's copy of that file, so the exclusion was never read, while `prepr.sh` and `ci_predict.py` were green on the same head. Eight round-10 pull requests went red this way (base copy red, head copy green, on CI's merge tree); the class is I3, barriered, past the per-round threshold. **Process state: (c).**

The record is `dev/audit/rca/R10-RCA-PREPR-HEAD-GRADERS.md`; `dev/audit/config/bugclasses.json` cites it under `_rca` and I3; its drivers are in `dev/audit/rca/prepr-head-graders/`.

## Delta since the last body

The last body described `34abdd2ea`; PR head `5a1d1e097` merged main after it. The arm code (`tools/pr/ci_predict.py`, `tools/policy/`, the drivers) is unchanged; `git diff 5a1d1e097 HEAD -- tools/pr/ci_predict.py tools/policy dev/audit/rca/prepr-head-graders` prints nothing. The delta since PR head `5a1d1e097`, the round-9 block, is one commit, `7e2346d0e`, in `dev/audit/rca/R10-RCA-PREPR-HEAD-GRADERS.md` only: the two lines that named the issue number now state the destination as the roster group R10-FLY-CIPREDICT-RESTORING, the carry having once pointed at an issue and now living in that group. No code changes.

## Head

`5682d74e56315ec90ef394191170147111e35382` merges the authored code head `7e2346d0e385aa9a72cd5ce4374801d0ef9f43c2` and then merges origin/main `2d151411f` (an automatic merge by the orchestrator's script; any resolution inside the code head is described below) into this PR's previous head.

`7e2346d0e385aa9a72cd5ce4374801d0ef9f43c2` (code tip of `handoff/r10-rca-prepr-head-graders`), measured against `origin/main` `c0a1d4635` (2026-10-30), merge-base `26c9d22a3`. `git merge-tree --write-tree origin/main HEAD` exits 0: no conflict. `VERSION`, the manifest, `RELEASE_NOTES.md` and both claim files are untouched.

## Mutation proof

Run with `python3 -I dev/audit/rca/prepr-head-graders/mutants.py .`. Each mutant is applied to a copy of `tools/pr/`, then `graders_self_test` runs against it. The unmutated tree prints `bad 0`. The arm code is unchanged since the last body, so its figures carry.
- **M1** `restored_hit` returns `[]`: `bad 5`. FAIL `tools/policy/vendor/markdown-it.min.js keys every restoring job`, `tools/policy/budget_raise_gate.py keys every restoring job`, and the three red e2e cases.
- **M2** `restored_hit` ignores the base tip: `bad 1`. FAIL `a restored path the base tip lacks keys no job`.
- **M3** `grader_runs` drops no exemption: `bad 1`. FAIL `the arm makes every pinned run but the agreement arm's and the exempt`.
- **M4** `predict`'s `graders` entry removed: `bad 1`. FAIL `predict reaches the graders arm by name`.
- **M5** `ci_tree_run` restores nothing: `bad 3`. FAIL the three red e2e cases.

## Null control

- In `graders_self_test`, three cases stay green with the arm in place: the repair in an unrestored data file, a corpus-only diff, and the plant staged but not committed.
- No real run line has an unmapped token. A planted `$ODD` token and a dropped exemption are each named as a gap.
- `corpus_excluded.json` keys no job, and a restored path the base tip lacks keys no job.
- `keycount.py`'s null pathspec keys 0 of 584 merges.
- `7e2346d0e` changes no code: `git diff 5a1d1e097 7e2346d0e --stat` names only the record.

## Figures

- `python3 -I tools/pr/ci_predict.py --self-test`: `ci_predict self-test: 0 failed`, rc 0, as measured on `7d1fbc055`'s identical arm code.
- `python3 -I dev/audit/rca/prepr-head-graders/keycount.py 14fbf218d 2026-10-14`: 584 merges; 69 keyed all three jobs, 1 keyed policy-docs + wave-script, 71 keyed wave-script alone; null pathspec 0. Weighted per predictor run 57 s; expected defect cost per PR 85 s (record section 5).
- `python3 -I dev/audit/rca/prepr-head-graders/jobtime.py 14fbf218d wave-script policy-docs`: wave-script 3.0 s, policy-docs 215.5 s.
- `bash dev/audit/rca/prepr-head-graders/plant.sh <head> gate <head> <out>`: rc 1, `GRADER policy_lint.mjs REFUSED by the base's copy, over tools/policy/budget_raise_gate.py`, as measured on the same arm code.
- `python3 tests/structure.py`: `STRUCTURE RATCHET PASSED`.
- Scope: `python3 tests/closure.py select --diff $(git merge-base origin/main HEAD)` names `tests/entities.py`. `PYTHONPATH=tests/hastub python3 tests/entities.py` under venv-ci's Python 3.14.7 (3.11 cannot parse it; the previous seat measured the same count under 3.13): `ALL 2471 ENTITY CHECKS PASSED`.

## Red checks

- `tests / nightly-status` and `governance / delivery-status` are red on `origin/main` too; neither reads a file this diff touches. Both are main's, not this PR's.

## Forward-carry

- `review_packet.py render` refuses `host-path` on a cloud seat: `ref_privacy.Identity.of_host` adds the account's home from passwd and matches it as a bare substring. An instrument defect in `tools/audit/seat/ref_privacy.py`, outside this class. Carry: dismissed: no live roster group owns tools/audit/seat/ref_privacy.py, and the defect bites only a cloud seat rendering a review packet
- The three restoring jobs outside governance.yml (`briefs`, `pr-contract`, `budget-raise-gate`) are not predicted by the graders arm; their instances are unmeasured. Carry: R10-FLY-CIPREDICT-RESTORING
- Review-verdict items routed here by id. The restoring jobs `budget-raise-gate`, `briefs` and `pr-contract` are what #2952 asks the graders arm to predict, and the roster group owns them. Carry: R10-FLY-CIPREDICT-RESTORING (item a3103224)
- The round-10 verdict's CI list records check states at one head; it states no defect. Carry: dismissed: a status snapshot at one head, with no finding to own (item 959730db)

## Friction

none
