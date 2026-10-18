Fix review: blocked 3b4c0fabfc12640e97f96fa581c0923dc4e27e2f vacuous-check: delivery_row self-test "adding only that row" survives `git add -A` (M7); class-open: handoff_push.sh keeps its own write_row and row commit, contradicting INSTRUMENTS.md "the one writer"

bus-nonce: c52eec7ea1e0ddc55b058b70614d55b8
reviewer: review-2400
round: 1 (no earlier review/2400 or verdict/2400 ref)
measured head: 3b4c0fabfc12640e97f96fa581c0923dc4e27e2f (re-read from GitHub before posting: unchanged)
contract: dev/governance/roles/fix-review.md; `git diff <merge-base>...origin/main -- dev/governance/roles/` empty, so it is current.

## RESULT lines (my runs, seat shims first on PATH, detached worktree at the head)

RESULT bus-selftest head: 67 checks, 0 failed, rc 0 (evidence/bus-selftest-head.log)
RESULT delivery_row-selftest head: 4 checks, 0 failed, rc 0; open_pr.sh and update_pr.sh --self-test print the same line
RESULT M2 (all four '+' dropped, the base's form): bus self-test 67 checks, 1 failed, "FAIL a handoff ref rewritten non-fast-forward after a run is still read, at its new tip"; the unreachable-remote null control stays ok (evidence/M2.diff, bus-selftest-M2-unforced.log). The forced-rewrite fixture reproduces the refusal without '+'. Fix 1 is confirmed.
RESULT M3 (ensure_row's has_row guard deleted): 4 checks, 1 failed, "FAIL null control: a head that carries its row gains no commit". Confirmed.
RESULT M7 (commit_row stages with `git add -A` instead of `git add "$p"`): 4 checks, 0 failed. SURVIVES (evidence/delivery-row-M7-add-all.log)
RESULT M7b (same mutant, plus one stray untracked file in the fixture, my own probe): 4 checks, 1 failed, the "adding only that row" check. The check can catch it only when the fixture has something else to stage, and it has nothing (evidence/delivery-row-M7b-add-all-stray.log)
RESULT M8 (ensure_row rewrites the row file before its has_row guard): 4 checks, 0 failed. Survives; not blocking, see below
RESULT open_pr row commit, base code vs commit_row, clean identity env: tree, author, committer and message identical (evidence/open_pr-row-equivalence.txt)
RESULT merge-tree origin/main vs head: rc 0, no conflict
RESULT VERSION / manifest / notes: untouched
RESULT CI at head (commit check-runs API, all concluded): 30 success, 15 skipped, 0 red; instrument-self-tests success (117672315727), mutation success (117672583919), pr-contract success x2 (evidence/checkruns-3b4c0fab.tsv). I did not re-run the gate.
NOT VERIFIED: `env_drift.py --all` timed out at 300 s under box load (evidence/env_drift.txt is empty). The diff touches no fixture or claim file, so I expect no drift, but I did not measure it.

## Blocking

1. vacuous-check. The new self-test row is named "a head without its row gains exactly one commit, adding only that row, as tvofi". Its "only that row" clause pins nothing: the fixture repo has nothing else to stage, so `git add -A` passes (M7). That clause is the orchestrator's null control, "touch no other path". Fix: plant an untracked file, a modified tracked file, or both, in `$t/r` before `ensure_row`. M7b shows this turns M7 red.
2. class-open, one writer. INSTRUMENTS.md now calls delivery_row.sh "the one writer of a PR's own delivery row". The brief's rule was one function, not a copy. But tools/audit/seat/handoff_push.sh:12-15 still defines its own ROW_DIR and write_row, and line 109 still makes its own row commit, with the same commit-after-the-first-push shape that #2390/#2391 hit. dev/governance/rules/delivery-status-tracking.md:33 still names handoff_push.sh as the row writer, and dev/programme/HANDOVER.md:33 still lists it. Fix one of two ways: make handoff_push.sh source delivery_row.sh (commit_row), or narrow the INSTRUMENTS.md wording and disposition handoff_push.sh in the body. The body names no enumeration rule for fix 2 (its class rule covers refspecs only), so this seam is undispositioned. (record_row.py --write-self-row also writes a row, but for the record beat's own PRs. It is a different writer class. Name it if the wording stays "the one writer".)

## Not blocking (for the fixer's judgement)

- M8: update_pr.sh guards with `if ! has_row` before it calls ensure_row, so ensure_row's own guard is unreachable from its only production caller. M3 kills the self-test, not production behaviour. Nothing pins that the working tree is untouched when the row exists.
- open_pr.sh with an empty group argument: the base wrote "title ()". row_line now writes "title" with no parentheses. Harmless, but it is a behaviour change the body does not state.
- watch was never affected: it reads `git ls-remote`, not the namespace. The body does not claim otherwise.
- Steps 10, 11: the forward-carry is "none", and that is plausible. There are no red checks, so no root-cause answer is owed.
