Fix reviewer for PR #2659, group R10-FLY-SUITE-ENV-FLAKES, head 5c091c198bb3d4663df171b918ecc80eb415428b. Read the group with jq from origin/handoff/audit-r10-roster:dev/programme/rosters/wave-r10-groups.json. Follow dev/governance/roles/fix-review.md exactly, from a detached worktree at the head. Use the finder harness the group brief names, never the fixer harness. A red nightly-status grades main and is not this PR unless its diff reaches what that check reads. Your ev/ MUST contain a file holding the full 40-hex head sha (ev/HEAD.txt), or the relay refuses the verdict.

The change: tests/harness_headers.py skips ONLY its CPU-headroom grade when HPO_CLOSURE_RECORDING=1 (closure.py sets it while recording a script under strace). It still runs every harness and checks its exit.

Verify:
(1) Red first (50423394a), then the fix (5576bcdba). Mutant: drop the flag check, and show the recorded-run pin goes red. Plant: inflate a harness cost past half its bound, giving rc 1 without the flag and rc 0 with it.
(2) NULL, the key claim: an unrecorded run past half its bound still FAILS. Confirm the fast lane (no strace) runs harness_headers WITHOUT HPO_CLOSURE_RECORDING on every PR, by reading the workflow and closure.py, so no grade is lost.
(3) The flag cannot leak: check that nothing except closure.py's recording path sets HPO_CLOSURE_RECORDING (git grep), and that a stray env in CI cannot disable the grade on the fast lane.
(4) The skip skips nothing else: harness exit codes and the other header checks still grade under the flag.
(5) The 50% rule and the 240 s bound are unchanged (diff).
(6) Scoped gate MODE line; CI read with one bulk check-runs read; no footers in commits; VERSION untouched.
