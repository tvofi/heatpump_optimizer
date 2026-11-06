Fix review: merge 89a82ddc602c719a76a583c9ed60c655e987af24

bus-nonce: 9991fd0b6b4b458ee2db34f4e288633c

CI-only re-check of record PR #3213 (triage, batch 123, P388) at its live head. The prior verdict (verdict/3213) blocked a01e980f on pr-closed only; no content defect was found there and none is re-reviewed here.

## Evidence
- RESULT: review_carry.py a01e980f -> 89a82ddc602c719a76a583c9ed60c655e987af24 prints CARRY (one branch-only commit, the merge of origin/main into the branch, no resolution). ev/carry.txt.
- RESULT: merge_train.py classify 89a82ddc602c719a76a583c9ed60c655e987af24 --pr 3213 prints "GREEN 89a82ddc602c719a76a583c9ed60c655e987af24 pending: none red: none", exit 0. ev/classify.txt.
- RESULT: all check-runs of the head listed across all pages (ev/check-runs.tsv): every run is completed; none is cancelled or pending. Both gate runs (01:09:26Z, 01:11:34Z), tests / fast (3.14), coverage, coverage-ratchet, closures, closure-scope, typing, mutation, browser, briefs, lane-proofs, graders-head-copy, governance / instrument-self-tests, policy-docs, wave-script, env-matrix, pr-contract (both runs), budget-raise-gate, arch-score, hassfest, validate-hacs and codeql are success; the rest are skipped. No run from 2026-11-04T22:5xZ appears on this head: the runs are all from 2026-11-06, the fresh run after the reopen.
- RESULT: two check-runs concluded failure, both read in their job logs and neither concerns the diff. tests / nightly-status (job 127644516490): "NIGHTLY FAILED: slow failed last night", scheduled run 41943946464 of 2026-11-05 at head 499162c, and the log says it is not a required context. governance / delivery-status (job 127644458541): lists other PRs pending or overdue in the delivery table and says "This check is NOT a required context and a red here blocks no merge". classify excludes both and reads GREEN.
- RESULT: PR state is open, not merged, head sha 89a82ddc602c719a76a583c9ed60c655e987af24. The body's `## Head` names 89a82ddc602c719a76a583c9ed60c655e987af24 ("merges main 7d95405 into the previous head ... The reviewed code is unchanged").
- RESULT: git merge-tree --write-tree origin/main 89a82ddc602c719a76a583c9ed60c655e987af24 exits 0 (clean). ev/merge-tree.txt.
- Not re-derived (carried from the prior verdict, unchanged code): the train/current.log figures, "plan slot 24" and the batch-122 predecessor.

## Findings
- Follow-up: the destination roster carry is not yet written; the orchestrator routes it through roster_edit.py citing triage: dev/programme/triage/s6-batch123.md#P388, after the merge. Carry: R10-TRAIN-MERGE-LOOP
- Residual: tests / nightly-status is red on main's nightly slow lane (run 41943946464), unrelated to this PR and not a required context. Carry: dismissed: not required, not caused by this diff; owed to the nightly lane's own fix
