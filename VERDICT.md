Fix review: merge 1f5b0aa4a7a8828bcbfaa2dee362082b950a5d1c
bus-nonce: f2d43c955e51be14c7bb04ee2bff83d7

Round 2 (re-verdict after a body-only edit; the head is unchanged at 1f5b0aa4a7a8828bcbfaa2dee362082b950a5d1c, re-read before posting). The round-1 block was root-cause-unanswered on nightly-status. It is cleared.

RESULT body: `## Red checks` now names nightly-status: NIGHTLY ABSENT for mutation-ledger and mutation-ledger-push, main's red. Scheduled run 36984959667 (head 492d840) predates #1848. The answer is "none" for a cheaper detector, and the proof is owed after the merge (a tests.yml dispatch on main, or the next cron). That matches the run log I read in round 1
RESULT pr-contract at head: run 110970305474 success (the round-1 failure 110968638807 was the body error, now answered)
RESULT nightly-status at head: run 110955998517 failure, answered in the body, not a required context on main-protect-checks. Not this PR's cause: the lanes this diff edits have never had a scheduled run
RESULT CI at head: no other failure (check-runs-round2.txt)

Carried unchanged from round 1 (same head, same tree; not re-taken):
RESULT entities-base 8fa06663: 1 of 2071 FAILED (the always() check, both ledger jobs); entities-head: ALL 2071 PASSED
RESULT mutants m1-m6 (mine): all killed. always() restored in either job, push loses its main guard, _gh_eval line reverted (NameError), push loses the success requirement, and a "!cancelled() || always()" widening, which the reach check catches
RESULT semantics: !cancelled() equals always() except on cancel. The push keeps main-only, schedule/dispatch, the mutation-ledger success requirement and environment: ledger. The reach matrix is green
RESULT root cause verified: 5f87e25a is not an ancestor of 9a096055. mergewhen.sh has no up-to-date check. Ruleset 23698884 has strict=false. The countermeasure is recorded, not built, and is the orchestrator's to accept. The "two this round" figure was not re-derived
RESULT merge-tree vs origin/main 8fa06663: clean. VERSION/manifest/notes untouched

Evidence: ~/hpo-seats/1859-review/evidence
