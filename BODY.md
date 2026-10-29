R10-RCA-PREPR-HEAD-GRADERS is the root-cause record for #2916's red `governance / policy-docs` and `governance / env-matrix`, and the countermeasure it calls for: `tools/pr/ci_predict.py`'s `graders` arm, keyed on the restore pathspecs of each `governance.yml` job that restores its check source from the base.

`f008c2b75` wrote a `named-docs` exclusion into `tools/policy/policy_lint.mjs`'s `CORPUS_EXCLUDED`. CI's restore step graded the PR with the base's copy of that file, so the exclusion was never read, while `prepr.sh` and `ci_predict.py` were green on the same head. Eight round-10 pull requests went red this way (base copy red, head copy green, on CI's merge tree); the class is I3, barriered, past the per-round threshold. **Process state: (c).**

The record is `dev/audit/rca/R10-RCA-PREPR-HEAD-GRADERS.md`; `dev/audit/config/bugclasses.json` cites it under `_rca` and I3; its drivers are in `dev/audit/rca/prepr-head-graders/`.

## Re-cut

Review round 5 blocked `2c62c682d` as `class-open`: `budget-raise-gate.yml`'s `budget-raise-gate` job restores and runs the base's `tools/policy/budget_raise_gate.py`, outside `restore_jobs` and undispositioned. This is round 6, past the three-round rule, so the re-cut is minimal and this body replaces the earlier one.

The re-cut narrows the claim and adds no predictor code. The arm's scope is `governance.yml`'s restoring jobs, which is what `restore_jobs` reads. The record now says so in its summary and in section 7. Section 7 also names every restoring job outside `governance.yml` as not covered by the arm:
- `briefs` (tests.yml);
- `pr-contract` (pr-contract.yml);
- `budget-raise-gate` (budget-raise-gate.yml).

The record does not claim these three. The rule that enumerates them is in `## Figures`. Widening `restore_jobs` to them was the other option, and it lost: `budget-raise-gate` reads live reviews, so a local run of it can only be partial (the round-5 verdict), and the brief for this round said not to widen the PR. They are not routed to a later stage from this body: their destination is a new group (the round-5 verdict's split), which only the orchestrator can create, so this seat filed no issue and wrote no roster or carry file; the handoff note asks the orchestrator for it. The diff against the previous head is `dev/audit/rca/R10-RCA-PREPR-HEAD-GRADERS.md` alone.

## Head

Code head `d379cfa4389f815b5065c2856256608a4a9f7905`, one commit on `2c62c682d180b6270a42d8c3a9a010fb6dd1ac4c`, measured against `origin/main` `b87019b86` (2026-10-29T12:27Z). `git merge-tree --write-tree origin/main HEAD` exits 0: no conflict. `VERSION`, the manifest, `RELEASE_NOTES.md` and both claim files are untouched in the three-dot diff.

## Mutation proof

This round adds no production line; its diff is the record alone. The arm's own proof, re-run at this head with `python3 -I dev/audit/rca/prepr-head-graders/mutants.py .` (each mutant applied to a copy of `tools/pr/`, then `graders_self_test` run against it):

- **M1** `restored_hit` returns `[]`: `bad 5`. FAIL `tools/policy/vendor/markdown-it.min.js keys every restoring job`, `tools/policy/budget_raise_gate.py keys every restoring job`, and the three red e2e cases (`#2916's shape`, `round 3's markdown-it.min.js`, `round 2's budget_raise_gate.py`).
- **M2** `restored_hit` ignores the base tip: `bad 1`. FAIL `a restored path the base tip lacks keys no job`.
- **M3** `grader_runs` drops no exemption: `bad 1`. FAIL `the arm makes every pinned run but the agreement arm's and the exempt`.
- **M4** `predict`'s `graders` entry removed: `bad 1`. FAIL `predict reaches the graders arm by name`.
- **M5** `ci_tree_run` restores nothing: `bad 3`. FAIL the three red e2e cases.

## Null control

- The unmutated tree: `python3 -I tools/pr/ci_predict.py --self-test` prints `ci_predict self-test: 0 failed`, rc 0, the same checks every mutant above turns red.
- The enumeration rule in `## Figures` run at `origin/main` returns the same six jobs as at this head, at shifted `governance.yml` lines, so the three-job left-open set does not depend on which tip is read.
- Before this commit, `grep -c budget-raise-gate dev/audit/rca/R10-RCA-PREPR-HEAD-GRADERS.md` at `2c62c682d` prints `0`. That is the round-5 block. At this head it prints `2`.

## Figures

- The class's jobs: `git grep -n -- "- name: Restore the check source from the base commit" HEAD -- .github/workflows/` returns six hits. Three are in `governance.yml` (`policy-docs`, `env-matrix`, `wave-script`), which `restore_jobs` keys and the arm covers. Three are outside it, and each is dispositioned as named in record section 7 and not covered by this arm: `budget-raise-gate.yml:66` (`budget-raise-gate`), `pr-contract.yml:93` (`pr-contract`), `tests.yml:603` (`briefs`). The same command at `origin/main` returns the same six jobs.
- `grep -c budget-raise-gate dev/audit/rca/R10-RCA-PREPR-HEAD-GRADERS.md`: `0` at `2c62c682d`, `2` at this head.
- `python3 -I tools/pr/ci_predict.py --self-test`: `ci_predict self-test: 0 failed`, rc 0, 129 s wall.
- `python3 tests/structure.py`: `STRUCTURE RATCHET PASSED`.
- Scope: `python3 tests/closure.py select --diff $(git merge-base origin/main HEAD)` prints `MODE: SCOPED -- 1 script(s) run, 32 scoped out`, naming `tests/entities.py`. `PYTHONPATH=tests/hastub python3.13 tests/entities.py` (a Python 3.13 venv with voluptuous, numpy, scipy, aiohttp and pyyaml): `ALL 2470 ENTITY CHECKS PASSED`, rc 0.
- CI at `2c62c682d`, read through the pull request's check runs: 68 runs, all completed. The one with conclusion `failure` is `tests / nightly-status`.

Not re-taken in this pass: the plant timings, `jobtime.py` and the `keycount.py` cost census. The record's section 5 states them with their own head and commands. This round's diff changes no code they measure.

## Red checks

- `tests / nightly-status`: red at `2c62c682d`. It grades `main`'s scheduled Nightly, not this branch, and this diff touches none of what it reads (its scripts, `ci.yml`, `tests.yml`, `nightly.yml`, the plan, `HANDOVER.md`). By `defect-root-cause.md` its red is the orchestrator's on `main` and owes no answer here.

## Forward-carry

- `review_packet.py render` refuses `host-path` on a cloud seat. `ref_privacy.Identity.of_host` adds passwd's home and matches it as a bare substring, so a body describing that defect is itself refused. It is an instrument defect in `tools/audit/seat/ref_privacy.py`, outside this class. The open group owning that file already carries it in `dev/programme/rosters/wave-r10-groups.json` (`brief` and `carry`). Carry: R10-RECORD-API-O1

## Friction

none
