Fix review: merge eab999bc6230b5f9668826b25dc64dcf657e46bf

bus-nonce: 44dc71c64400d0967431884d84426a55

## Round

Round 3 (delta review). The last review covered 5e7d8865; this one reviews the branch-only delta from there to eab999bc6230b5f9668826b25dc64dcf657e46bf, three-dot against origin/main (merge base 2d151411f80c3f868c4de5b3a878c673cb88df02 = origin/main at review time).

## Findings

none. The body's own forward-carries (the class proposal for carry 4, and A's unguarded `export X=$?` / `${?}` domain) are already routed to R10-ERREXIT-COUNTERMEASURES carry (4) in the body, and carry_audit at the head reports 3 routed, 0 unrouted. This round adds none.

## Evidence

- Head measured: eab999bc6230b5f9668826b25dc64dcf657e46bf, which is still the tip of fix/r10-errexit-countermeasures (git ls-remote) when this verdict was written. The body names this head, and 793658cd4 as the code head it merges.
- Delta: the only branch-only non-merge commit since 5e7d8865 is 6c123f469, a one-line change in tests/entities.py `_o1_window`: `["bash", "-c", script]` -> `[*_GHA_RUN, script]`. Diffing the three-dot diff at 5e7d8865 against the one at the head shows only that line (ev/delta-vs-5e7d8865.txt, closures.json lines aside). The `--remerge-diff` for merges 811de0cb7, 793658cd4 and eab999bc6 is empty: 811de0cb7 is the LEDGER-MERGE auto-resolution of tests/closures.json, and the other two are clean.
- Mutation proof, re-run by this reviewer: restoring `["bash", "-c", script]` in `_o1_window` (ev/mutant.diff) and running `env -u BASH_ENV PYTHONPATH=tests/hastub python3 tests/entities.py` prints `1 of 2482 ENTITY CHECKS FAILED`, rc=1. The failing check is countermeasure B, with `sites=12 without errexit=['tests/entities.py:_o1_window']` (ev/countermeasure-B-mutant.txt). The other FAIL lines in that log are self-test plant output, not failing checks.
- RESULT head: `ALL 2482 ENTITY CHECKS PASSED`, rc=0 (ev/entities-head.txt). Both figures match the body's.
- Class (step 6): at the head, B's check prints `ok` (ev/countermeasure-B-head.txt). Under the mutant, the same check prints `sites=12` with exactly one site lacking errexit, the reverted line. A grep of `["bash"|"sh", "-c"` across tests/ and tools/ at the head returns only the three `_SHELL_NOT_A_STEP` entries (throwaway_git.self_test, entities._cir_once_count, judge_batch.run), B's plant string literals, and one f-string argv at entities.py:36160 inside `_cir_once_count` (a listed function, def at line 36147). No seam is open.
- Null control: B's plants (bare, `sh -x -c`, `/bin/bash`, `/usr/bin/env bash`) pass unchanged inside the same run (`plants missed=[]`).
- Finder harness: dev/audit/harnesses/r10_errexit_capture.py is flat by design, as earlier rounds confirmed. This round touches no line it reads, so it was not re-run.
- Merge: `git merge-tree --write-tree origin/main eab999bc6230b5f9668826b25dc64dcf657e46bf` gives rc=0 and tree a9c21e7d9ebaf6a66146e1507c3666537d2561db, with no conflict and no MERGE-CLAIM line (ev/merge-tree.txt).
- VERSION, the manifest, RELEASE_NOTES.md and tests/golden are untouched in the three-dot diff.
- CI at eab999bc6230b5f9668826b25dc64dcf657e46bf, read from the check-runs API:
  - tests / fast (3.14) is success. It was red at 5e7d8865 and is now green: that was the red this round set out to fix.
  - Also success: tests / closures, instrument-self-tests, policy-docs, env-matrix, arch-score, mutation, budget-raise-gate, typing, browser, briefs, closure-scope, delivery-status, codeql (all three), hassfest and validate-hacs.
  - tests / nightly-status is failure. It grades main's scheduled Nightly, the diff does not reach what it reads, and it is not this PR's.
  - Still in progress when written: tests / coverage, tests / arch-instrument, and one prelude (run 41004554267). Their conclusions were not observed by this reviewer.
- Red checks (step 11): the body's `## Red checks` names tests / fast (3.14) and pr-contract at 5e7d8865, with a cheaper detector (re-running tests/entities.py after the main merge) and its standing cost. The trigger is answered. This reviewer checked that it was answered, not the answer itself.
- Figures not re-derived: the "about nine minutes" standing cost. The local entities.py run took several minutes on this box, which is consistent with it but was not timed.
