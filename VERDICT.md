Fix review: merge a54aed8b9e756aaa47ea18e9a13bf33a06878a0b

Round 3 (round 1 blocked a8a2778e mutation-vacuous; this is not the fourth round). Reviewed from a detached worktree at a54aed8b9e756aaa47ea18e9a13bf33a06878a0b; merge base and origin/main f2fb1b0e950ecd047b7f08b3adef93776a622540. Role contract current (`git diff merge-base...origin/main -- dev/governance/roles/` empty).

RESULT selftest_head: `cloud_relay self-test: 163 checks, 0 failed`, rc 0 (ev/selftest_head.txt)
RESULT harness_head: r10_seat_selftests_mutants.py, M0 `0 seat step(s) red`, 47 KILLED (S01..S34, S04U, W1..W3, cloud_relay-1..9), `RESULT survivors=0`, rc 0 (ev/harness_head.txt)
RESULT harness_main: same harness at f2fb1b0e9, 38 KILLED, `RESULT survivors=0`, rc 0 (ev/harness_main.txt)
RESULT R6: production line `while IFS= read -r l || [ -n "$l" ]; do` -> `while IFS= read -r l; do` reddens 3 checks (`a last line without a newline is read: it holds #41`, `and held says held for it`, `a one-line file without a newline holds #41`); null control `printf '99\n41\n'` still passes under it (ev/own_mutants.txt, harness row cloud_relay-5)
RESULT own mutants: HELD echo removed -> 6 failed; hold `continue` removed -> 3 failed; refusal rc 2 -> 0 -> 9 failed; held() argument guard loosened -> 1 failed; comment/blank allowance removed -> 2 failed; not-a-regular-file guard removed -> 0 failed (note 1)
RESULT S31..S34: byte-identical to main; every S row identical (ev/s_rows.txt)
RESULT merge-tree: `git merge-tree --write-tree origin/main a54aed8b9` exit 0, tree 3ca9474f4 (ev/merge_tree.txt); no claim-file conflict
RESULT scope: `MODE: SCOPED -- 0 script(s) run, 33 scoped out`; VERSION / manifest / RELEASE_NOTES / tests/golden untouched
RESULT class: automatic update_pr.sh drivers = cloud_relay.sh only (tick_loop.sh drives it via `cloud_relay.sh pass`; other hits are comments, self-tests or manual tools); readers of the hold file = cloud_relay.sh only. Class closed; R10-ORCH-MACHINERY's handoff job is a carry, as the body says.
RESULT CI (check-runs API, once, at the end, ev/check_runs.txt): all completed gate checks success, incl. instrument-self-tests, pr-contract, mutation, closure-scope, delivery-status. Pending: `coverage`, `Analyze (python)` — judged on the rest. Red: `nightly-status` only — grades main, the diff reaches nothing it reads; the body answers it under `## Red checks`.

Figures in the body re-derived at this head: 163 checks; 137 at 0ddbc0c21 not re-taken; per-mutant failure counts 27/42/2/3/9/2/1/1 match the harness rows; 47/38 KILLED rows match. Body head names a54aed8b9 = measured head; head still a54aed8b9 at posting.

Notes:
1. Mutant `[ -f "$f" ] && [ -r "$f" ] ||` -> `true ||` survives the self-test. It is near-equivalent: a directory still refuses rc 2 through the redirect's read error (verified `held 41` -> rc 2 both at head and mutated), only the message changes; a FIFO hold file would block instead of refusing. Not blocking; a later seat may pin a directory-as-hold-file check.
2. Roster registration pending (roster PR-B): verdict note only, per brief. Pack JSON at pin f89bfb4e matches the PR's files; the P6 carry (per-file ids) is honoured.
3. Forward-carry: R10-ORCH-MACHINERY carry is left to the orchestrator's roster_edit.py (the seat cannot write the roster branch); R10-FLOW-ROSTER-FREEZE dismissed as unregistered. Not checked on the roster branch by this review.

bus-nonce: 6ed39626378f4923fe2e58ee0552fedb
