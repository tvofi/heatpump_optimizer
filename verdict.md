Fix review: merge b4f8038e2e19e34c88008e0c768544b9442c3a82

bus-nonce: a77b1b03bcfec92a4fa11521f40520fa
pending-ci: gate

## Review

This is round 4, a delta review against the reviewed head 2a1a7de05b0c080029817dd4208864c5ef7e9f6a. The packet's scope reads `delta`. The delta, `git diff 2a1a7de0 b4f8038e`, changes `tools/pr/gate_priority.py` (+10/-2) and `tools/pr/prepr.sh` (+18), and both changes are self-test code only (`ev/delta-stat.txt`). It adds no `custom_components/` line, so the review is not widened. b4f8038e has two parents, 2a1a7de0 and e9ba58d3, and its tree is byte-identical to e9ba58d3, the authored head the body names under `## Head`.

Round 3 blocked on three surviving mutants: P12-codesteps-drops-scoped-test, P13-main-uses-inline-receipt-line and G6-cli-ignores-ref. All three are killed at this head by the arms the body describes:

- P12 is killed by the new `hs` row `PREPR_SKIP_CODE=hotfix PREPR_SKIP_CLOSURES=x`, 1 failed (`ev/mutants/P12-codesteps-drops-scoped-test.log`).
- P13 is killed by the `rhot 1` row, which runs prepr's main flow on a hotfix branch. Under the mutant it gets `ok code steps: reused from the receipt at hotfix` where it wants `hotfix scope` (`ev/mutants/P13-main-uses-inline-receipt-line.log`).
- G6 is killed by `--hotfix reads the roster at --ref, not the local roster ref`, giving `22 checks, 1 failed` (`ev/mutants/G6-cli-ignores-ref.log`).

The whole round-2 mutant set was re-run at this head with the same driver, and every mutant but the null is killed. No other survivor exists at this head in the reviewer's set. `rhot` writes a stub `tools/pr/gate_priority.py` into the throwaway clone `$RQ/wt`, where `tools/` is untracked, adds it to that clone's own `info/exclude`, and removes it afterwards. It never touches the real checkout.

## Evidence

- RESULT head: `git ls-remote origin refs/pull/3547/head` printed b4f8038e2e19e34c88008e0c768544b9442c3a82 at the start and again before the verdict (`ev/HEAD.txt`).
- RESULT mutation: `ev/driver.py`, run at this head (reviewer-built, not the finder's; no finder's harness is named). G1, G2, G3, G4, G5, G5b, P1 to P8, P9r, P10, P11, P12, P13 and G6: all KILLED. NULL-comment-only: SURVIVED, with `553 passed, 0 failed` (`ev/mutants-results.txt`, `ev/mutants/`).
- RESULT figures, re-derived at this head:
  - `prepr.sh --self-test` prints 553 passed, 0 failed (the null mutant's run).
  - `gate_priority.py --self-test` prints 22 checks, 0 failed.
  - `tests/structure.py` prints STRUCTURE RATCHET PASSED.
  - `tests/closure.py select --diff <merge-base>` prints `MODE: SCOPED -- 0 script(s) run, 33 scoped out.`
  - `gate_priority.py --hotfix --branch fix/r10-prepr-residue-p2` prints 0.
  - All five match the body.
- Not re-derived: the body's own `mutant_run.py --spec` and `--diff` tables. The table's P14 to P22 are its own spec, which I did not re-run, and its 16 `--diff` survivors with their equivalence answers were not re-checked. Both are pre-existing body content outside the delta scope; the reviewer's own set covers the same seam.
- RESULT merge: `git merge-tree --write-tree origin/main b4f8038e` exited 0 at origin/main 8af37bdf, with no conflict (`ev/merge-tree.txt`).
- VERSION, the manifest and RELEASE_NOTES.md are untouched in the three-dot diff.
- RESULT CI: `merge_train.py classify b4f8038e --pr 3547` printed `WAIT ... pending: gate red: none` (rc 3) on every poll from 01:37 to 02:15 UTC, more than 30 minutes (`ev/classify.log`, `ev/classify-final.txt`). No red has been read at this head, so no `## Red checks` answer is owed. Owed reds are listed in `ev/owed-reds.txt`.
- The forward-carry reads `none`, and carry_audit reports 25 body items, all routed (review packet).
- `date -u` at start: Sat Nov 14 01:34:44 UTC 2026.
