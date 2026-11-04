Fix review: blocked a01e980f0aa5290276a8d9951471863db33470af pr-closed: PR #3213 was closed at 2026-11-04T22:51:19Z and every run of this head was cancelled, so CI never concluded

bus-nonce: 6b8e80bc00d8a38153780c1d1fb60994

Round 1. Triage record PR #3213 (batch 123, P388), head a01e980f0aa5290276a8d9951471863db33470af. Adds only dev/programme/triage/s6-batch123.md and delivery/3213.md.

## Evidence
- RESULT: merge-tree of the head with origin/main is clean (exit 0, tree e178577981d2); no claim-file conflict. Output in ev/HEAD.txt.
- RESULT: the diff touches no VERSION, manifest, notes, budget, closure or claim file.
- RESULT: carry_audit at the head: 0 finding items, 0 unrouted (review packet).
- RESULT: verdict grammar OK: Verdict ACCEPT, Source, Instances, Cost, Binding present; the ACCEPT names its destination, R10-TRAIN-MERGE-LOOP, which exists on origin/handoff/audit-r10-roster (group 287 of 328) and carries the carry text the ruling widens (its 0-based carry 3: a body-repaired pre-flight park cannot rejoin at the same verdict, #3074). Its citation s6-batch32.md#P189 resolves on main.
- RESULT: code claims hold at origin/main: already_held holds a same-verdict skip unless its class is in READMIT_SAME_VERDICT (HOLDER, BRANCH_POLICY) (merge_train.py:770, 1021-1048); Train.preflight sets a class only for step recarry (cls = HOLDER if step == "recarry" else None); admit_add has a policy rule that passes under a mandate id and no findings rule.
- RESULT: the table's tally re-derives from its own rows: 6 of 9 (5 policy parks, 1 findings park); the Binding's instance list matches it.
- Could not re-derive: the train/current.log lines, the pid 38222 / 4 h 37 min figure and the queue line of 2026-11-04T21:09:35Z. The log is on the orchestrator's machine, not in the tree; the record cites them as read, and says the log has no timestamps. Not verified by me.
- Could not re-derive: "plan slot 24". The roster has no slot key (the group is at array index 287); the slot is the orchestrator's plan. Not verified by me.
- Could not re-derive: "the rolling batch after batch 122". origin/main holds batches up to 118 (P382); batches 119-122 and P383-P387 are not on main at this head, presumably in open PRs. P388 does not collide with anything on main.
- Review-packet figure_lint: 1 figure not verified (git diff --stat citing shas outside this PR), not a refusal.
- CI: classify exits 1 (RED, gate) but the cause is the closure: every gate job of the head's runs is conclusion cancelled at 22:50:53Z, one (instrument-self-tests) still in progress, and the PR reads state closed, closed_at 22:51:19Z, not merged. Not a defect in the diff. ev/classify.txt.

## Block

The head cannot be merged: the pull request is closed and its CI never concluded. On the content, the review found no defect (see Evidence); if the orchestrator reopens or re-files the same record, the same review applies, and the three un-derivable figures (train log, plan slot 24, batch 122 predecessor) stay unverified. Round 1.

## Findings
- Follow-up: the destination roster carry is not yet written; the orchestrator routes it through roster_edit.py citing triage: dev/programme/triage/s6-batch123.md#P388, after the merge. Carry: R10-TRAIN-MERGE-LOOP
