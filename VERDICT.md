Fix review: merge 29187b1ebc0f2c83bbb411af0a22ddb92b8068c3

bus-nonce: 01a1cfe59709beb38331d42588e0847b

Round 2 (delta review over the reviewed head 0b1994a331b7a3a46a49b0c8ed718cb338243860, per the packet's `## Review scope: delta`). The delta changes only test code, so the scope is not widened.

## Findings

- Note: stale-figure: the body's `## Figures` scope bullet still reads `roster_lib.py (124 checks)`, but at this head the self-test prints `125 checks, 0 failed`. The `## Mutation proof` section already states 125. This is paperwork and blocks nothing (C5). Carry: dismissed: body figure only, superseded by the body's own mutation-proof line at this head

## Evidence

- RESULT head: 29187b1ebc0f2c83bbb411af0a22ddb92b8068c3 is the PR head and the body's head (ev/HEAD.txt). The review ran from a detached worktree at that commit. `git diff <merge-base>...origin/main -- dev/governance/roles/` is empty, so the contract is current.
- RESULT delta: `git diff 0b1994a331 29187b1ebc` changes `tools/audit/seat/roster_lib.py` only, adding 4 lines inside `_self_test`. That is commit 1e81226fb9 plus a merge commit with no other content (ev/merge-delta.txt). No production (`custom_components/`) code changes, so the scope is not widened.
- RESULT prior finding resolved: the prior M7 mutant (`(rel, x) not in ROUND_RECORDS` changed to `x not in {k for _, k in ROUND_RECORDS}`) was applied at line 454 of this head. `roster_lib.py --self-test` then prints `125 checks, 1 failed`, `FAIL a ROUND_RECORDS key admits its constant in its own file and no other (got: [])`, rc 1. The mutant is killed (ev/mutants.txt).
- RESULT sibling mutant M7b (key checked on its file half only, `rel not in {f for f, _ in ROUND_RECORDS}`): it is killed by the existing arm `a ROUND_RECORDS key admits its own constant and no other`, 125/1. Both halves of the (file, constant) key are now pinned (ev/mutants.txt).
- RESULT restored: the unmutated head prints `125 checks, 0 failed`, and the worktree is clean afterwards.
- RESULT witness from the prior block: `round_literal_hits("tools/x/other.py", 'SEARCH = "dev/audit/rounds/round11/D11"\n')` returns `['tools/x/other.py:1: module constant: round11']`. `round_literal_defaults("HEAD")` returns `[]` (ev/witness.txt).
- RESULT null control: the body names the arm `a ROUND_RECORDS key admits its own constant and no other` as the in-file control. It passes at head, so the new arm refuses only because the file path differs.
- RESULT merge: `git merge-tree --write-tree origin/main 29187b1ebc` gives tree 88587044a5 with rc 0 and no conflict (ev/merge-delta.txt).
- RESULT CI: `merge_train.py classify 29187b1ebc0f2c83bbb411af0a22ddb92b8068c3 --pr 3880` exited 0 on its first poll, printing `GREEN 29187b1ebc0f2c83bbb411af0a22ddb92b8068c3 pending: none red: none` (ev/classify.log). No red is owed an answer.
- RESULT untouched: the delta does not touch VERSION, the manifest, RELEASE_NOTES.md, the claim files or tests/golden/.
- RESULT not re-derived this round: the archscore dS and structure.py figures. The CI lanes `arch-score` and `gate` are green at this head. Everything else in round 1's evidence is unaffected by a delta of 4 test lines.
