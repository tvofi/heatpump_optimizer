Fix review: merge ca96324704b7fb88d18f7a474510a97ec6345433

bus-nonce: 6af10f90dc42f926ab9571bd7c399ebc
reviewer: review-2400
round: 2. This round reviews the delta since 3b4c0fabf against round 1's two blocks.
measured head: ca96324704b7fb88d18f7a474510a97ec6345433. I re-read it from GitHub before posting; it had not moved.
contract: dev/governance/roles/fix-review.md. `git diff <merge-base>...origin/main -- dev/governance/roles/` is empty, so the contract is current.
Evidence: ~/hpo-seats/r10s3/review-2400/evidence-r2/ (round 1's is ~/hpo-seats/r10s3/review-2400/evidence/)

## Delta

The authored delta is 9f3ae9fe3 (tvofi|tvofi). Since it, `git diff 9f3ae9fe3 HEAD -- tools/audit/seat` is empty. Both later merges (4505870d7, ca9632470) are clean: for each, the recomputed `merge-tree` of its parents equals the commit's tree (ae9cafa5, 7a8df24a). Everything else in 3b4c0fabf..HEAD is main's.

## RESULT lines

RESULT delivery_row-selftest head: 5 checks, 0 failed. handoff_push.sh --self-test prints the same line.
RESULT M7 (commit_row stages with `git add -A`), round 1 SURVIVED: now 5 checks, 2 failed. The round-1 block is closed; the fixture now plants an untracked file and an unstaged edit.
RESULT M9 (`git add -u` before the row's add, my new probe): 5 checks, 2 failed. Tracked edits are pinned too.
RESULT M8 (ensure_row rewrites the row before its guard), round 1 SURVIVED as a non-blocking note: now 5 checks, 1 failed. update_pr.sh no longer pre-guards, so ensure_row's own guard is the one production uses.
RESULT M3 (ensure_row's has_row guard deleted): 5 checks, 1 failed.
RESULT bus-selftest head: 68 checks, 0 failed, including "delivery_row.sh is the one seat script that defines write_row or commits a row".
RESULT G1 (a second `write_row()` planted in handoff_push.sh): bus self-test 68 checks, 1 failed, on the one-writer row. The round-1 class-open block is closed: handoff_push.sh now sources delivery_row.sh (commit_row on open, ensure_row on update), and INSTRUMENTS.md now reads "the one seat-script writer" and names record_row.py as the other row writer.
RESULT M2 (the '+' dropped): carried from round 1 (67 checks, 1 failed). bus.sh's orphans code and fixture are unchanged in this delta; the delta adds only the 5-line guard.
RESULT syntax: bash -n passes on handoff_push.sh, update_pr.sh, open_pr.sh and delivery_row.sh.
RESULT merge-tree origin/main vs head: rc 0. VERSION, manifest and notes are untouched.
RESULT CI at head (commit check-runs API, every run concluded): 30 success, 15 skipped, 0 red. instrument-self-tests 117697765167 success; closures 117698003491 success; pr-contract 117697763912 and 117697848066 success. I did not re-run the gate.

## Notes (not blocking)

- The one-writer guard is a grep over `tools/audit/seat/*.sh`. It does not see a Python writer or a writer that uses neither string. The INSTRUMENTS.md wording ("seat-script") matches that scope.
- handoff_push.sh's row commit now carries the Co-Authored-By trailer, which its old message lacked. The change is consistent with open_pr.sh and harmless.
- The empty-group row shape ("title", not "title ()") is now stated in the body and pinned by "no group writes no empty parentheses".
- NOT VERIFIED (carried from round 1): env_drift.py --all timed out under load. The diff touches no fixture or claim file.
