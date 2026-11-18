# Proposal triage, session s14, batch 236

Source: the orchestrator's request on R10-TRAIN-RESIDUE-P2 after its pull request #3470 merged to
main at be86e36a560fde88cc758cefcee322b9087a5deb (2026-11-12). Carry indices are 0-based on the
group at roster a15a842375; #3470's body numbers its carries from 1, so its "Carry 17" is index 16.
Ruling recorded by triage s14-44.

## P710: mark the carries #3470 built; leave the rest open

Verdict: ACCEPT
Evidence: #3470's body answers carries 1-18 (1-based): "Carry 17: built here
(TRAIN-POLICY-REASON-STALE-CONTEXT, `rollup_states`)" and "Carry 18: built here
(TRAIN-UNDRAFT-EVERY-ROUTE, `record_drafts` and the `land` draft arm)"; carries 1-16 read "left
for a later part; it stays on the roster". Carries 19-23 (indices 18-22) were appended after the
brief was rendered and the body does not name them. Checked on origin/main: merge_train.py
defines `rollup_states` and `Train.record_drafts`, and `_batch` calls `self.record_drafts(queue)`;
be86e36a56 is an ancestor of origin/main.
Ruling: mark index 16 and index 17 implemented at be86e36a56, each by --match on its key text.
Nothing is dismissed. Indices 0-15 and 18-22 (21 carries) stay open and buildable, so the stage
stays carries-open and no set-stage done is queued. The group is not idle: a next part owes them.
Destination and severity: roster ops only, normal. Figure against 20%: not applicable (record).

## P711: derive a merged part's carry marks from its body at the merge

Verdict: ACCEPT
Problem: marking the carries a merged part built is nobody's step. roster_sync.py at a merge
writes only the stage (carries-open while any carry is unmarked; its marks are read, never
written); no tool on main reads a body's "Carry N: built here" lines, and no policy file names
mark-carry as a step. R10-TICK-RESIDUE-P3 carry 25 (POSTMERGE-STAGE-VIA-DRAIN) queues the stage
op on a refused sync, not marks a body declares.
Cost seen: after #3470 merged, R10-TRAIN-RESIDUE-P2 read 23 of 23 carries unmarked, so the plan
could not tell its two built carries from its 21 owed ones, and a fixer dispatched on it would
have rebuilt `rollup_states` and `record_drafts`. 14 groups sit at carries-open on the roster
now; each merged part among them carries the same exposure. The body's 1-based numbering against
the roster's 0-based indices makes a by-number derivation wrong by one, so it must key on text.
Ruling: at a merge, postmerge derives one `mark-carry <GROUP> --match <key> implemented <merge>`
per body line "Carry N: built here (<KEY>, ...)" and a dismissed mark per "Carry N: dismissed
(<reason>)", keying --match on the key text the body quotes, checked to hit exactly one carry of
the group; a body line whose key hits zero or two carries is printed as OWED, never guessed by
index. The ops go to roster-drain.queue as the stage op does.
Destination: one carry on R10-TICK-RESIDUE-P3 (not-started; it owns postmerge.py and
roster_sync.py and carry 25, the neighbouring stage-op derivation). Severity: normal. Basis: one
observed instance with a measured near-miss dispatch; 20% bar not argued, the cost is a re-built
part per merged group with carries left. Size: S-M.
