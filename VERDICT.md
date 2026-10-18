Fix review: merge ecdcc466d343421f091bcc9b5b159149bfaf36eb

bus-nonce: 5f1e74ced2ace2b625b4292f16747950

PR #2371, R10-LEAF-IMPORTS, review round 3, at the same head as round 2 (ecdcc466d343421f091bcc9b5b159149bfaf36eb). refs/pull/2371/head was re-read before posting. Round 2 (review/2371 e24291172) cleared items 1-4 and blocked only on the utc_shift forward-carry; every round-2 measurement stands unchanged at this head.

## The carry (fix-review step 10)

- The destination is opened and the carry is present. On handoff/audit-r10-roster at 8b12786d4 ("roster: carry accuracy.utc_shift to R10-LIVESTATE (#2371)"), R10-LIVESTATE's `carry` list holds: "From R10-LEAF-IMPORTS (#2371): accuracy.utc_shift is a second UTC owner beside the clock module; fold it into the one owner or state why it stays (#2371 r1/r2 review)." The full list is in evidence/livestate_carry_at_8b12786d4.json.
- It is stated as a precondition with a disposition: fold it, or record why it stays.
- Precondition for the merge: the carry is on the orchestrator's roster record ref, not yet on origin/main (0 occurrences at 9a1ce39c3), and no open pull request carries that ref. The roster record must land on main before or with this PR. That is the orchestrator's to sequence.
- R10-LIVESTATE's `brief` text does not yet name utc_shift. The roster's convention copies the carry list into the fixer prompt at dispatch, so the carry list is the binding source.

## State at this head

- Every CI check-run's latest run is success, skipped or neutral (evidence/checkruns_head.tsv).
- `git merge-tree --write-tree origin/main <head>` exits 0 at origin/main 9a1ce39c3.

## RESULT lines

RESULT carry R10-LIVESTATE utc_shift present at handoff/audit-r10-roster 8b12786d4 (1 entry); on origin/main 0 (pending roster record)
RESULT round2_results unchanged at same head: census 17->10, mutants M1-M6 and M8 killed, old-home REASON_ imports 0, archscore dS +0.4646 with layer_violations credited
RESULT ci all latest check-runs green/skipped/neutral
RESULT merge_tree rc=0 vs origin/main 9a1ce39c3
