Fix review: blocked 5e4fbb0d3b14d963d746d5c416fe41c30e919d00 carry-missing: not carried to the stage owning tools/audit/seat/cloud_dispatch.py; the body's Forward-carry names R10-ORCH-MACHINERY, which is absorbed, and no roster brief holds it

bus-nonce: f1ae933eaad5e3dff636bd0289e2e300

Review round 2 of PR #2709 (R10-FLY-CLOUD-SETUP-TOOLCHAIN), measured at head 5e4fbb0d3b14d963d746d5c416fe41c30e919d00. Round 1 blocked as mutation-vacuous. That block is answered: every mutant named in the body dies at this head. One check is still open.

## Block

- fix-review.md step 10 and finding-propagation.md's Enforcement section. The body's `## Forward-carry` says `tools/audit/seat/cloud_dispatch.py`'s setup line should run `bash tools/audit/seat/cloud-setup.sh --check` and stop on `REFUSE`. The finding is real and has its control: both `--check` outcomes are reachable, see Evidence. But it reached no stage's brief:
  - The body names no file, stage brief or roster SHA for it. It has only the marker `Carry: R10-ORCH-MACHINERY`.
  - The roster at `handoff/audit-r10-roster` bae86879d (and 50c690758) has R10-ORCH-MACHINERY at `resume.stage: absorbed`: "Closed, superseded by the re-cut ... This group keeps only the no-build records and residuals as carries". Nothing dispatches it, so it is not a destination.
  - None of its carries, and no other group's, contains `cloud-setup.sh --check`. See `ev/forward_carry_roster_bae86879d.txt`, and a `grep` of the whole roster for `cloud-setup`: only R10-FLY-CLOUD-SETUP-TOOLCHAIN's own carries match.
  - The live stages that own `cloud_dispatch.py` are R10-FLY-POOL-INSTRUMENT and R10-FLOW-DESIGN-STAGES (both not-started).
  - Remedy: append the carry to one of those, stating its control as a precondition, with `roster_edit.py`. Then name that group and the roster SHA in the body. The same goes for the two `## Friction` lines routed to R10-ORCH-MACHINERY.

## Findings

- Surviving mutant, reviewer-planted. `check`'s `[ -x "${HPO_TYPING_PYTHON:-}" ]` weakened to `[ -n ... ]`: `13 checks, 0 failed`. The body's M3 deletes the whole conjunct and is killed only through the unset arm. So the body's "HPO_TYPING_PYTHON is executable" is unpinned for a set path that does not exist or is not executable. The head's behaviour is right (under `env -u BASH_ENV`, `HPO_TYPING_PYTHON=/nonexistent` gives `REFUSE`, rc 1). Under the mutant the same call gives `OK`, rc 0 (`ev/R3_behaviour.txt`). One arm with a non-executable `HPO_TYPING_PYTHON` kills it. Carry: R10-FLY-CLOUD-SETUP-TOOLCHAIN
- Surviving mutants, reviewer-planted. The refusal's "values it read" text is unpinned. Deleting `HPO_TYPING_PYTHON is ${HPO_TYPING_PYTHON:-unset}, ` (R8a) or ` OPENBLAS_CORETYPE is ${OPENBLAS_CORETYPE:-unset}` (R8b) leaves `13 checks, 0 failed`. Commit 2602f99db's subject claims "--check's refusal names each of the three values it read". Only the python3 value is in an arm's pattern. Carry: R10-FLY-CLOUD-SETUP-TOOLCHAIN
- Surviving mutant, reviewer-planted. The profile's `HPO_TYPING_PYTHON` pointed at `venv-ci/bin/python3` instead of `venv-ha/bin/python` (R9) passes 13 of 13. No arm checks which interpreter the profile names, only that it is executable. Carry: R10-FLY-CLOUD-SETUP-TOOLCHAIN
- Three roster carries on this group get no disposition in the body (roster 50c690758, carries [1], [3], [7]). This PR is the group's only delivery, and a done group is not a carry destination. They would be lost at merge:
  - [1] #2554's `gh auth status` failure (GH_TOKEN).
  - [3] #2629's `seat_venv.sh` with no `uv` download for cpython-3.14.7.
  - [7] #2585's "a seat replaying a governance job's steps sets RUNNER_TEMP first". This PR itself adds a governance step that `tee`s to `$RUNNER_TEMP`.

  Each needs a fix, a re-route or a dismissal in the body. Carry: R10-FLY-CLOUD-SETUP-TOOLCHAIN
- `tools/audit/seat/INSTRUMENTS.md`'s new `cloud-setup.sh` entry says "`OK` (exit 0) only when all three hold" but never names the three conditions. The body says the entry gives "`--check`'s three conditions". Carry: R10-FLY-CLOUD-SETUP-TOOLCHAIN

## Evidence

- Head: `5e4fbb0d3b14d963d746d5c416fe41c30e919d00` (`ev/HEAD.txt`). `git ls-remote` showed `fix/r10-fly-cloud-setup-toolchain` still at it when the verdict was written.
- Policy current: `git diff $(git merge-base origin/main HEAD)...origin/main -- dev/governance/roles/` is empty. Main is 73b69fe0a, and that is also the merge base.
- Merge: `git merge-tree --write-tree origin/main 5e4fbb0d3` gives tree 591ef7b72, rc 0, no conflict.
- VERSION, the manifest version and RELEASE_NOTES.md: `git diff origin/main...HEAD` over them is empty. pr-contract printed "no version edit".
- Blob sha1s match the body: cloud-setup.sh c634e178…, r10_cloud_setup_mutants.py b4b5ba0d…, r10_cloud_setup_toolchain.py e5d50e1f…. The base copy 145bfe197 is de099837…, the same as 73b69fe0a's blob.
- Self-test: `bash tools/audit/seat/cloud-setup.sh --self-test </dev/null` gave `13 checks, 0 failed` on 4 of 4 runs (`ev/selftest.txt`).
- `--check` in this seat: OK rc 0. Under `env -u BASH_ENV -u OPENBLAS_CORETYPE` it gives `REFUSE ... OPENBLAS_CORETYPE is unset`, rc 1. Under `env -i PATH=/usr/bin:/bin` it gives REFUSE, rc 1. An unknown flag gives usage, rc 2. These reproduce the body's null control.
- Body's mutation table, re-run with `python3 -I dev/audit/harnesses/r10_cloud_setup_mutants.py`: M0 PASS 3/3, M1 through M13 (with M12b) KILLED 3/3 with the arms the body lists, `RESULT survivors=0`, rc 0 (`ev/mutants_fixer.txt`).
- My own mutants, applied as one-occurrence replacements to the head copy (`ev/mutants_reviewer.txt`):
  - R0, the unmutated copy: 0 failed.
  - R2, the profile's `OPENBLAS_CORETYPE` value changed: KILLED.
  - R10, `--variables`' `HPO_TYPING_PYTHON` value changed: KILLED.
  - R3, R8a, R8b and R9: survived (Findings).
  - R11, `exit $?` to `exit 0` under `--check`: survived. This is the equivalent mutant the body discloses, since `set -e` exits first.
- Finder's control at both ends with `dev/audit/harnesses/r10_cloud_setup_toolchain.py` (`ev/toolchain_both_ends.txt`). It is the fixer's rebuild, disclosed under fixer.md step 18. No finder-committed harness exists. The carries' controls were prose.
  - Base: bare and remedy `/usr/local/bin/python3 numpy-missing`; remedy-nul numpy-ok; nested venv-ci; `verdict: no`.
  - Head: bare and remedy flat, which is the step-3 case; variables numpy-ok; check-ok rc 0; check-sys REFUSE rc 1; nested `<tmp>/stub/python3`; `verdict: yes`.
  - Every figure matches the body.
- Carry [6]'s re-measure instruction (#2452 / #2704), `PYTHONPATH=tests/hastub python3 tests/entities.py` at the head (`ev/entities_bash_env.txt`):
  - `BASH_ENV` set to the container's current, unguarded profile: `2 of 2425 ENTITY CHECKS FAILED`, rc 1.
  - `BASH_ENV` set to the profile this head's `write_profile` writes: `ALL 2425 ENTITY CHECKS PASSED`, rc 0.

  So the guarded profile settles #2452 once it is re-pasted.
- Class rule (step 6): the body's `git grep` gives exactly the seams it disposes of (`ev/class_rule.txt`). No class-open seam.
- Step 14: the `tests/closures.json` change only adds the two new harness files to the inert reads. It is earned by the new files. No budget, golden or claim file moved.
- CI on this head (`ev/check_runs.txt`, check-runs API) has all concluded:
  - The first `pr-contract` run, 15:29Z, failed in `codescan_wait.py`, before `codeql / Analyze (python)` concluded at 15:52Z.
  - A later `pr-contract` run, 16:09Z, succeeded. Both `gate` runs from 16:11Z succeeded.
  - `tests / closures`, `fast (3.14)` and the rest are green.

  The one red was a wait-timing red from the code-scanning wait, superseded at this head. The body's `## Red checks: none` is not challenged on that ground.
- Not re-run, by the rule against re-running CI's heavy runs: the full gate and the mutation table. CI's results are cited instead.
