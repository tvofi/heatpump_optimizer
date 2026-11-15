Fix review: merge 7a587071be68a536ff3437df2b3bbc947f7013ad

bus-nonce: 5dbcad83176a90d2cf0013335af6694e

Round 1 (first round, full scope). Reviewed from a detached worktree at 7a587071be68a536ff3437df2b3bbc947f7013ad against merge base 98847b99d7bb3238686efd6869f805c89c6d1ff1.

## Evidence

- RESULT mutation glob-dropped: removing the criteria regex from POLICY_GLOBS makes `node tools/policy/policy_lint.mjs` exit 1 with `FIXTURE OVER-FIRES ... D10-criteria.md` (ev/mutant1-drop-glob.txt). Killed.
- RESULT mutation glob-widened: widening it to `criteria\/.+\.md` (a subtree) exits 1 with `FIXTURE VACUOUS ... criteria/sub/D10-criteria.md` (ev/mutant2-widen-glob.txt). Killed, so the deep-path arm is not vacuous.
- RESULT head lint: `TOTAL: 0 error(s) across 52 policy file(s)`, `FIXTURE ok: 93 error(s) hold 278 pins`, rc 0 (ev/lint-head.txt); origin/main reads 276 pins (ev/lint-main.txt). The +2 pins come from the two new arms, as both mutants show.
- RESULT null control, re-run by me at both ends: a tracked throwaway `criteria/X-criteria.md` at origin/main draws `[coverage] ... matches no POLICY_GLOBS pattern`, TOTAL 1 (ev/null-main.txt). At the head it draws no [coverage] error, only [index] and [budgets], TOTAL 2 (ev/null-head.txt). Matches the body.
- RESULT budgets: `policy_lint.mjs --budgets` output is byte-identical at origin/main and at the head (ev/budgets-diff.txt is empty).
- RESULT `rules_sync.mjs --check`: RULES-SYNC ok. `tests/structure.py`: STRUCTURE RATCHET PASSED.
- Every figure in the body re-derived at this head: 52 policy files, 93 errors, 278 pins (276 on main), budgets unchanged, rules-sync ok, structure passed.
- VERSION, the manifest version and RELEASE_NOTES.md are untouched (three-dot diff empty). No claim files and no golden fixtures are touched, so step 4 does not apply.
- `git merge-tree --write-tree origin/main 7a587071be68a536ff3437df2b3bbc947f7013ad`: rc 0, no conflict (ev/merge-tree.txt).
- CI: `merge_train.py classify 7a587071be68a536ff3437df2b3bbc947f7013ad --pr 3631` reports `GREEN 7a587071be68a536ff3437df2b3bbc947f7013ad pending: none red: none` (ev/classify.txt). The packet's `gate failure` digest line was superseded; classify decides. No owed red, so no Red checks answer is owed; the body's `none` stands.
- Harness: this is a bootstrap grader change, not an audit finding with a finder's harness. Its committed harness is the `checkCoverage` acceptance pair in `assertAcceptance`, which this review drove with both mutants above.
- Class (step 6): one seam. The lint's own coverage arm reports every uncovered file under dev/governance/; it reads 0 at the head, so no other directory is open.
- Step 14: the pin counter moves by 2 only through the two arms. No budget, closure, INERT or score figure moves.
- Step 15: one regex and its comment beside the sibling `dimensions/` glob, with fixtures in the existing acceptance block. Architecturally consistent.
- Body head equals the reviewed head. The live PR head was re-read before return (ev/live-head.txt).
- Dispatch: the scheduled prompt pinned PROMPT.md at 5f65ec27bf21, a main roster commit that holds no PROMPT.md. The brief was read from 838a8286f874 on dispatch/reviewer-rev-3631, the commit PAYLOAD.json names, with the same nonce and head. Its PROMPT.md is byte-identical to the branch tip 9764e50f.

## Findings

none
