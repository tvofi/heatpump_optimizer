Fix review: merge 594ff9db20f0e6ea5a1c817cb6195ab6fee8536a

bus-nonce: f3d44a4d316ef81e4422601fb8785672

Round 1 of this review. Head measured: 594ff9db20f0e6ea5a1c817cb6195ab6fee8536a (worktree detached at it; still the PR head at 2026-10-24T14:5xZ). Merge base e97f5749b = origin/main.

## Findings

- Surviving mutant in `tools/ci/ruleset_cutover.py` `unordered()`: replacing `r["parameters"][RSC].sort(key=canon)` with `pass` leaves all 101 self-test checks passing; no fixture reorders the required-context list, so only rules and bypass-actor ordering are pinned. Its only reach is a 17-context rollback read-back, where an absent sort could cause only a false refusal (never a false pass). The ruleset now holds one context, and the window cannot reopen (the body's carries 15, 17 and 23). Carry: dismissed: the mutant can only produce a false refusal on a rollback path the live one-context ruleset cannot reach; a fixture would guard nothing reachable.

## Evidence

- Role contract current: `git diff $(merge-base)...origin/main -- dev/governance/roles/` empty.
- Merge: `git merge-tree --write-tree origin/main 594ff9db20f0e6ea5a1c817cb6195ab6fee8536a` rc 0, tree 65326bdd4 (ev/merge_tree.txt). No claim-file conflict.
- VERSION, manifest, RELEASE_NOTES.md, claimed_drift.txt and card_claimed_drift.txt are untouched (ev/structure_claims.txt). `env_drift.py --claims-only`: claims hygiene ok. `tests/structure.py`: STRUCTURE RATCHET PASSED.
- Self-tests at the head (ev/selftests.txt): codescan_wait 17/0 failed, ruleset_cutover 101/0, gate 27/0, merge_train 239/0; policy_lint `TOTAL: 0 error(s) across 50 policy file(s)`, no required-contexts line; field_coverage ok and its self-test ok; selftest_wiring 93/93/0. Each figure matches the body.
- Mutation proof re-run (ev/mutants_py.txt, ev/mutants_entities.txt), RESULT lines:
  - RESULT carry25 step1-raises: 2 failed (body: 14 and 17) — killed
  - RESULT carry25 wait-own-bound: 1 failed (17) — killed
  - RESULT carry25 ratelimit-stdout: 1 failed (15) — killed
  - RESULT carry25 fail-stdout: 1 failed (16) — killed
  - RESULT carry20 same-positional: 3 failed (apply, enable, rollback) — killed, matches the body
  - RESULT carry20 rules-unsorted: 4 failed (+staged-hash) — killed, matches the body
  - RESULT carry20 bypass-unsorted: 4 failed — killed, matches the body
  - RESULT own requires_only_gate positional: 0 failed — equivalent (NEW_CHECKS has one element, so order cannot differ)
  - RESULT own context-sort deleted: 0 failed — the surviving mutant under Findings
  - RESULT carry26 unmutated: defects=[] missed=[]
  - RESULT carry26 gate-exact arm deleted: missed ['gate does not need pr-contract', 'gate needs a unit beside pr-contract'] — matches the body
  - RESULT carry26 !cancelled arm deleted: missed ['pr-contract skippable before its needs end'] — matches the body
  - RESULT carry26 pr-contract needs arm deleted: missed ['pr-contract does not need a unit'] — matches the body
  Runner: `tests/entities.py` cut after `_CI_PLANT_MISSED` (line 19682) with a print appended, `BASH_ENV` unset, PYTHONPATH=tests/hastub. This is the same shape as the body's runner, built by me.
- Run-graph edge figures re-derived (ev/edges.txt): main 27/10/9, head 19/2/9; pr-contract's `if:` opens `${{ !cancelled() && `. These match the body.
- The semantic claim that a skipped pr-contract waits for its needs: the jobs of main push run 40092463804, read through the Actions API (ev/run_40092463804.txt), show pr-contract skipped at 12:36:18Z, which is when its last need `tests / arch-instrument` completed; gate started at 12:36:21Z. This matches the body. Since gate.py judges from the API and reads only `needs.prelude.outputs`, dropping the other eight needs leaves its verdict inputs unchanged; `gate.py`'s diff touches only the self-test.
- `ruleset_cutover.py`: every read-back and window comparison goes through `same()`/`requires_only_gate()`. Two comparisons stay positional, both correctly: `save_rollback`'s byte read-back of its own file, and `dry_run`'s `kept`, which compares a payload derived from the same live object.
- Not re-derived (this seat's gh token fails auth): the `r10_ci_gate_ready.py` RESULT `zero_delta` counts (10/10, 10/10, 10/10, 6/6) and its `--null prelude` arm; the live ruleset read at 12:41Z; the CodeQL python-leg durations 1397-1814 s; and the `ci_critpath.py` unmapped output. I report these as unverified rather than verified. The harness is the fixer's own, built because the owner-named `ci_critpath.py` cannot read the umbrella. The body discloses this and carries the instrument fix to R10-FLOW-TOOLKIT-MODEL with a stated control.
- Forward-carries: both `## Forward-carry` items name a group and a control (R10-CI-LAYOUT-P2 for CodeQL vs WAIT_MAX_S; R10-FLOW-TOOLKIT-MODEL for ci_critpath). I did not open the roster ref.
- CI on the head at about 14:53Z was in progress: the code run 40103681107 had no red among completed jobs (budget-raise-gate, closure-scope, nightly-status, briefs, mutation, wave-script, hassfest, codeql js, arch-score and validate-hacs passed; CodeQL neutral); codeql python, the tests jobs and the governance jobs were still running. In the edit run 40103681248, prelude was in progress. No check had concluded red, so no red-check trigger was owed yet. The body pre-answers the predicted `pr-contract` FAIL-closed on the edit run (carry 25's class, where the base's copy runs). The merge train's gate still governs. The heavy runs are CI's, per the contract; I did not re-run them.
