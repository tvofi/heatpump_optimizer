Fix review: blocked 18ae7cb0a4e6acb942867980a50b4f862701a473 mutation-survivor: R7 (|| true), R8 (continue-on-error), R9 (empty token) leave the arm unable to go red with every check green
bus-nonce: bd250b1c89d6517c51a8b095356da0e1

Round 2. #1863 (R9-F11.7, Closes #1757). I measured the head 18ae7cb0a4e6acb942867980a50b4f862701a473, and it is still the live head at posting. Merge base 03ba7f70f007147bda32ac0fc5dd83b11499bbaf. `fix-review.md` is unchanged between the merge base and origin/main. Against the new merge base the three-dot diff is still tests.yml, docs/delivery/1863.md and tests/entities.py only. The v6.7.14 stamp files arrive through the main merge, not through this branch.

The orchestrator asked me to hold this verdict for the CI demonstration unless something else blocks. Something else does, so I am posting now. The demonstration is still owed and is not judged here.

## Correction to my round-1 verdict

The fixer is right about R6. `if true || git diff ...; then governance=false` always takes the `false` branch, so R6 never fires. That is the under-fire direction, not the over-fire I called it, and it was a blocking survivor I wrongly marked benign. At this head it is killed: "the arm's trigger fires on a restored path and only there" FAILs with `.claude/workflows/x.mjs -> 'false'`.

## Mutants (tests/entities.py in full, venv python, PYTHONPATH=tests/hastub, each restored from HEAD; mutants2.py)

- RESULT entities head rc=0 ALL 2086 ENTITY CHECKS PASSED
- RESULT M1 (tests.yml at the merge base) rc=1, 4 of 2086 failed
- RESULT M2 rc=1. The first check FAILs, and the pre-existing `_pin_unhashed_installs` crashes on the bool `run`, as in round 1.
- RESULT M3 rc=1, 1 failed. RESULT M4 rc=1, 2 failed.
- RESULT R1 rc=1, 1 failed. RESULT R2 rc=1, 1 failed. RESULT R3 rc=1, 2 failed. RESULT R4 rc=1, 1 failed. RESULT R5 rc=1, 1 failed. RESULT R6 rc=1, 1 failed.
- All ten round-1 mutants are killed, as the fixer reports.
- **RESULT R7: field_coverage arm `run: node .claude/workflows/field_coverage.mjs || true`. rc=0, ALL 2086 PASSED. SURVIVES.**
- **RESULT R8: `continue-on-error: true` on the policy_lint arm step. rc=0, ALL 2086 PASSED. SURVIVES.**
- **RESULT R9: field_coverage arm `GITHUB_TOKEN: ""`. rc=0, ALL 2086 PASSED. SURVIVES.** The key is present, so `_pt_armed` counts the step as armed, but `gh` runs with no credential.

R7 and R8 leave the arm's red invisible. R9 removes the Actions-token view the arm exists for: either `gh` refuses to run, or the ruleset read takes a different path. Each is the same class as R2 and R3: the arm looks wired and cannot report #1721. `_pt_armed` and `_PT_PROG` match the program name anywhere in the run line and accept any value under the env key.

Suggested pin:
- each armed step's `run` is exactly `node <prog>`;
- it has no `continue-on-error`;
- its `GITHUB_TOKEN` value equals `${{ secrets.GITHUB_TOKEN }}`.

The null control for that pin is R7, R8 and R9 above.

## Red checks

The body's answer does not describe the red at this head. It answers `NIGHTLY ABSENT` on check-run 111022420278 at the round-1 head, and that answer is verified:
- #1848 merged 2026-10-02T16:51:20Z and is not an ancestor of 492d84011;
- nightly-status is `failure` at a8f86edd6, 441adb4ae and eed5ac3fa.

At this head nightly-status (check-run 111054174313) is red for a different reason: `NIGHTLY FAILED: mutation-ledger-push, mutation-nightly failed in the last verification dispatch`. That is run 37050037132, a `workflow_dispatch` on main at aa7a81192, conclusion failure. It is main's red; this diff changes neither lane. The body owes it one line naming it, re-taken at the head it describes.

Every other latest check-run at this head is success, skipped or neutral; see `check_runs_<head>.tsv`. The body's `## Head` paragraph names 18ae7cb0a as both the authored code head and the merge result. The SHA is correct; the sentence is garbled.

## Unchanged from round 1 (not re-measured)

- the #1721 reproduction under the Actions-view emulation (main green, demo field_coverage REFUSED);
- the six-seam class enumeration;
- permissions parity.

The reworded exemption reasons for envmatrix and budget_raise_gate now match what I measured in round 1.

## Still owed

The CI demonstration on the throwaway draft: comment edit 3689657c green in both arm steps; #1721 perturbation 7c4a9fbd red in the field_coverage arm step. Both run links go in the body.

Evidence: `evidence/` (mutants2.py, mutants.out, mut_*.txt, ent_head.txt, nightly_status_job.log, check_runs_<head>.tsv).
