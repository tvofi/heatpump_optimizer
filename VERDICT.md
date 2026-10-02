Fix review: blocked 1f5b0aa4a7a8828bcbfaa2dee362082b950a5d1c root-cause-unanswered: nightly-status went red, unanswered
bus-nonce: edb049c73a24e3c8be0b4d7f5e8cbac3

Round 1. Measured head 1f5b0aa4a7a8828bcbfaa2dee362082b950a5d1c (live head re-read before posting). Base 8fa06663cf64a32cf19a3a2f2742ce3225f06e3a. Contract fix-review.md current (no diff in tools/audit/briefs/ against origin/main).

The code is sound. The block is on the body only.

RESULT entities-base 8fa06663: 1 of 2071 FAILED; the failing check is "no job-level `if` leads with `always()`" [mutation-ledger, mutation-ledger-push], rc=1
RESULT entities-head 1f5b0aa4a7a8828bcbfaa2dee362082b950a5d1c: ALL 2071 ENTITY CHECKS PASSED, rc=0 (venv R9-F11.4, PYTHONPATH=tests/hastub). The only other check-line difference is a8:register_once inside a planted control, where the dup ordering is nondeterministic
RESULT mutant m1 (mutation-ledger back to always()): killed, CI-cancel check FAIL [mutation-ledger]
RESULT mutant m2 (push back to always()): killed, CI-cancel check FAIL [mutation-ledger-push]
RESULT mutant m3 (push drops github.ref == main): killed, reach check FAIL (schedule on fix/x pushes alone)
RESULT mutant m4 (revert the _gh_eval line): killed, reach check FAIL, NameError: cancelled. The evaluator line is needed
RESULT mutant m5 (push drops needs.mutation-ledger.result == 'success'): killed, 2 checks FAIL (write-grant split + reach: dispatch with recheck=true on main pushes without measuring)
RESULT mutant m6 (mask attempt, "!cancelled() || always() && ..."): killed, reach check FAIL (branch refs reach mutation-ledger). The _gh_eval change does not mask a widened guard; the leading-always regex is not the only gate
RESULT semantics: a status function in the if: replaces the implicit success(), so !cancelled() equals always() for a skipped or failed recheck-gate and differs only when the run is cancelled. The push keeps the main-only, schedule-or-dispatch guard, the mutation-ledger success requirement and environment: ledger (entities.py:27878 pins it). The reach matrix is green at the head
RESULT root-cause body: verified. 8fa06663's parents are 5f87e25a (#1854) and 9a096055. git merge-base --is-ancestor 5f87e25a 9a096055 returns rc=1. 9a096055 merges 948671af, which is an ancestor of #1854's first parent. mergewhen.sh waits for CLEAN and uses --match-head-commit, with no comparison to origin/main. The main-protect-checks ruleset (23698884) has strict_required_status_checks_policy=false. State (d) is plausible. The countermeasure is recorded, not built, and that is the orchestrator's to accept. Not re-derived: the "two this round" gate-file merge rate in the cost test
RESULT merge-tree origin/main(8fa06663) x head: rc=0, no conflict
RESULT VERSION/manifest/notes: untouched (diff is tests.yml, entities.py, docs/delivery/1859.md)
RESULT CI at head (check-runs API): success 22, skipped 11, cancelled 2 (superseded pr-contract and budget-raise-gate; budget-raise-gate re-ran green), failure 2: nightly-status and pr-contract

BLOCK. pr-contract run 110968638807 at the head failed with one body error: "check `nightly-status` is red and `## Red checks` does not name it ... this diff touches what it reads (.github/workflows/tests.yml)". fix-review.md step 11 voids the nightly-status exemption when the diff reaches what the reporter reads, and this diff edits the two lanes it watches. nightly-status (run 110955998517, script pinned at 8fa06663) printed "NIGHTLY ABSENT": mutation-ledger and mutation-ledger-push did not run in last night's scheduled run 36984959667 (head 492d840, which predates #1848 adding those lanes).

The repair is body-only. The code head can stand, and no re-measure is owed for the code. Under `## Red checks`, name nightly-status and answer it. The cause is main's: the lanes are new since #1848, and no scheduled run has happened since. This PR does not cause it. The proof the check asks for is a concluded `gh workflow run tests.yml --ref main` dispatch after this merges, or the next cron. Then pr-contract re-runs on the body edit.

Evidence: ~/hpo-seats/1859-review/evidence (entities runs at base, head and 6 mutants; mutant diffs; the pr-contract and nightly-status logs; waitci). Reviewer harness: the finder's own check (tests/entities.py) plus my own mutants m1-m6, disclosed as mine.
