Fix review: merge f9a920e33f34e89608b6dbaf8e89896ac3d84af8

bus-nonce: 7bcb596d8783341d8336e08436ce62ce

Round 2 of the fix review, after the round-1 figures-unverified block at `a2cd2f659`. Measured head: `f9a920e33f34e89608b6dbaf8e89896ac3d84af8`, re-read by ls-remote just before writing (refs/pull/2799/head and fix/audit-r10-roster-pr both point at it). Main is `b89fea13e99f23cc75f01bb1604030cabea4ca66`, which is also the merge base. The head moved from round 1 by one merge of the roster tip `54d78f9bb`. I judged that delta and re-took every figure in the body at this head.

## Findings

- The PR's own delivery row, `dev/programme/delivery/2799.md`, still describes the PR as "roster ops on handoff/audit-r10-roster through 00ceb9aa4: IMMERSION-LATCH brief re-pin, CONFIG-NOTICES done, #2798 precondition carries ...". The title was corrected and the body now runs through `54d78f9bb`, but this row was not. `delivery-status-tracking.md` says the orchestrator writes this row and that nothing reconciles it, so the stale text lands on main unless whoever writes the merge row corrects it. Carry: #201

## Evidence

- RESULT round-1 block cleared. The body's figures now match the head. The groups are keyed by `group`, as the body states: 189 on main and 189 at the head, none removed, none new, 35 changed. Stage counts are done 115 then 117, in-progress 12 then 10, not-started 50 then 47, absorbed 1 then 4, queued 6 and carries-open 5. All 35 per-group lines match the body's pasted output line for line (`ev/fig_out.txt`). The 35 against round 1's 34 comes from the new R10-FLY-DEPGRAPH-STALE change (carry 1->3, issues +2777 +2806) that the delta adds. The title now reads "through 54d78f9bb".
- RESULT fig.py is not in the tree. I rebuilt it from the body's description (both rosters loaded as JSON, a group being an object holding both `group` and `resume`, keyed by `group`). This instrument is mine, `ev/fig.py`, not the body's script (step 8/9). Its output equals the body's byte for byte in content.
- RESULT parents: `git log -1 --format=%P` prints a2cd2f659883ce2e340f20b7c4aa5003ebc20fbf 54d78f9bbb7526767ac9f7b5df1c7e7173f96398, as the body says.
- RESULT diff stat: 2 files, 102 insertions and 69 deletions, as the body says (`ev/diffstat.txt`).
- RESULT null-control hashes: main ae5988d3415d399099e4dae250a8380da56e3c78 and head ce5e01b869142042371e63adfaae18017773af2d, as the body says.
- RESULT roster commits: 62 in `origin/main..head -- dev/programme/rosters/`, and 2 are not roster_edit (`5f94b943b`, `0574da74a`), as the body says. The oldest-first ops list matches the body's 62 lines in order (`ev/ops.txt`).
- RESULT merge: `git merge-tree --write-tree origin/main head` exits 0 (`ev/merge-tree.txt`). No claim file is touched.
- RESULT VERSION, manifest version and RELEASE_NOTES.md are untouched (no diff under them).
- RESULT brief_lint at the head: `TOTAL: 0 error(s) across 48 file(s)` (`ev/brief_lint.txt`). The head roster parses as JSON.
- Role drift: `git diff merge-base...origin/main -- dev/governance/roles/` is empty, so the contract is current.
- The mutation proof, finder's harness, null-control perturbation and class rule do not apply. This is roster state and a delivery row only, with no production or test code, so there is no mutant to draw. Step 14: the moved figures are the roster ops themselves, and each traces to a named roster_edit or roster_sync commit.
- CI at the head: 49 check-runs read, none failed. 31 succeeded, 13 were skipped and 5 were still in progress: env-matrix, instrument-self-tests and three preludes (`ev/checks.txt`). No pr-contract run was listed at read time. Step 11 has no red check to answer. The orchestrator should re-read once the in-progress runs conclude.
- Forward-carry: the body says none. The diff is itself the carry record.
