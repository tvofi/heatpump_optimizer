Fix review: blocked 38422dd1525cbf2cf7ace3e6e04213ea04b0f4ff class-open: tools/policy/budget_raise_gate.py, a restored program the CORPUS run spawns, outside the graders key

bus-nonce: db52ed1308da3b18f3347dfa4d5f7966

## Round

Review round 2. The body's head note answers round 1's `class-open` block.

## Block

Step 6 (open the class). The record's class is the runs a pinned job restores from the base. The body's population rule (`pinned_runs` plus `grader_gaps`) finds a program only if it is named on a governance.yml run line, or if an unrestored head-copy program spawns a row's grader. It does not find a restored program that a row's grader spawns itself. `mjs_closure` follows only `.mjs` imports and `load`/`at` literals, so the arm's key misses those programs too.

One such seam, demonstrated at this head:
- `node tools/policy/policy_lint.mjs` (CORPUS, default mode, `policy-docs`) runs `tools/policy/budget_raise_gate.py` through `checkPrBody`/`raiseJustification` (policy_lint.mjs:6733) in its fixture acceptance (policy_lint.mjs:4007-4024). The probe: a `budget_raise_gate.py` that no longer imports turns the default lint run red with `FIXTURE VACUOUS` (ev/gate-spawn-probe-lint.txt).
- `tools/policy/*.py` is in `policy-docs`' restore pathspecs. CI therefore grades with the base's `budget_raise_gate.py`.
- The plant, a commit on top of this head (ev/plant.diff): `JUSTIFICATION_SCORE` accepts `Arch score: dS`, and `fixtures/policy-rot/prepr/raise/good.md` uses that spelling.
  - The head's copy of `policy_lint.mjs` exits 0 (ev/plant-head-copy-lint.txt).
  - With the base's `budget_raise_gate.py`, it exits 1: `FIXTURE VACUOUS: the raise-justification arm on prepr/raise/good.md drew 1 error(s)` (ev/plant-base-copy-lint.txt).
  - `ci_predict.py --base <head> --only graders` predicts no red, rc 0 (ev/plant-predict.txt).

This is the #2916 shape: every local path is green, and CI's base copy refuses. Neither the diff nor the body dispositions the seam. The repair is to widen the rule and the key to restored programs that a row's grader spawns, or to disposition each one with a reason. That means a `.py` `path.join(HERE, …)` spawn in `policy_lint.mjs` (and in the other rows' graders) keys and is enumerated, with a `grader_gaps` case that drops it.

## Findings

- Class-open: a restored program spawned by a row's grader (`budget_raise_gate.py` under CORPUS) is neither keyed nor enumerated by `grader_gaps`. A head edit to it, together with the fixture it grades, is predicted green and goes red on CI. Fix it in this PR (see the block). Carry: R10-RCA-PREPR-HEAD-GRADERS
- I did not verify that `ref_privacy._leaks`'s home-substring false positive has landed in R10-RECORD-API-O1's own brief. The body cites only record section 7 as its landing place, and `finding-propagation.md` asks for the stage's brief. The defect is real: `review_packet.py render` refused `host-path` at this head on `R10-RCA-PREPR-HEAD-GRADERS.md:4` and `:389` because `/root` occurs in `roles/root-cause.md`, so no packet was written. Confirm the carry when this PR is next reviewed. Carry: R10-RECORD-API-O1

## Evidence

- Head measured: 38422dd1525cbf2cf7ace3e6e04213ea04b0f4ff (ev/HEAD.txt). The PR's head was still this SHA when the verdict was written. The roles diff from the merge base to origin/main is empty, so this contract is current.
- Review packet: `review_packet.py render` refused on `host-path`, so no packet was written. I read the live checks directly.
- `grader_key_self_test` at the head: 11 ok, 0 FAIL (ev/grader_key_self_test.txt).
- My mutants, run in process:
  - M7 (`env-matrix` dropped from CORPUS's reds) fails the null-control gap row.
  - `grader_hit` keyed on the entry alone (closure dropped) fails `and by one to a module it imports (counts.mjs)`.
  - I did not re-run the full 420 s `--self-test` or the plant mutants M1-M3.
- `pinned_runs` at the head: 14 runs (ev/pinned_runs.txt). They match the run lines I read in governance.yml's `policy-docs`, `env-matrix` and `wave-script` jobs.
- `git merge-tree --write-tree origin/main HEAD` (origin/main b0b2d7697): rc 0, clean, empty stderr.
- `VERSION`, the manifest and `RELEASE_NOTES.md` are untouched (three-dot diff from the merge base).
- `fold_ledger.py check`: 127 rca entries, 0 violation(s). This matches the body's 127.
- I did not re-derive the body's round-10 population figures (543 merges, 8 instances, 40 red jobs, cost test) or its timings.
- CI at this head (ev/check-runs.json):
  - Concluded, with no red: `policy-docs`, `env-matrix`, `wave-script`, `mutation`, `briefs`, `closure-scope`, `arch-score`, `budget-raise-gate`.
  - CodeQL is neutral.
  - Still running or queued: `tests / fast`, `closures`, `coverage`, `typing`, `browser`, `arch-instrument`, `instrument-self-tests`, and CodeQL python.
  - The block does not depend on them.
