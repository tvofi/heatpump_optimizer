# Proposal triage, session s14, batch 143 (P548 to P549)

This batch rules `s7/triage-queue-s7.txt` lines 232 and 233. They arrived after batch 142. The bar
and the denominators are batch 141's.

Sources: the roster at `origin/handoff/audit-r10-roster` `39a92af760`, and origin/main
`d08ed31049`.

## P548: S14-ROSTER-SYNC-DUP-CARRIES

Verdict: ACCEPT, on the class-barrier route. The class repeats across ten groups.

Source: queue line 232 (2026-11-11T00:35:11Z, the s14 dispatch seat).

Instances:
- **The reported group.** R10-ARBITER-OFF-RESTORE holds 16 carries, and six repeat earlier ones
  (8=7, 11=9, 12=10, 13=3, 14=4, 15=5).
- **The shape of a repeat.** The first copy reads `From <topic>, body item <8-hex>: <text> Carry:
  <G> (items <8-hex>)`. That is the queue's append. The repeat is the same `<text> Carry: <G>` with
  no item id. That is `roster_sync.py`'s append of the same body item.
  - `roster_edit` refuses only an exact repeat, so the second copy lands.
- **The census.** Across the open groups at roster `39a92af760`, 39 of 312 open carries (12.5 %)
  repeat an earlier carry of the same group, once each copy is normalised (the "From ..., body
  item" prefix and the trailing "Carry:" clause stripped). They fall in ten groups:
  - R10-ROUND-PLAYBOOK-FINAL 13
  - R10-BODY-CONTRACT 10
  - R10-ARBITER-OFF-RESTORE 6
  - R10-FIXER-MD-SPELLING-CORPUS 2
  - R10-TRAIN-RESIDUE 2
  - R10-TICK-RESIDUE 2
  - R10-PREPR-RESIDUE, R10-USER-DOCS-VERIFY, R10-WATER-SETPOINT-FEEDBACK and
    R10-HOTFIX-MAIN-SELFTESTS, 1 each
- **The cost.** Every duplicate is an item a fixer must read and answer, and a carry
  `carry_audit` counts as open.

Cost: in `roster_sync.py`, before appending a body item, skip it when the destination group already
holds a carry naming the same 8-hex item id, or holding the same normalised text. Self-test:
- the queue-then-sync shape appends once;
- the null control, a distinct item to the same group, still appends;
- a mutant on the skip.

The 39 existing duplicates are roster data. Dismissing them by `mark-carry ... --match` is the
orchestrator's op, not this carry's.

Binding: one carry, R10-TICK-RESIDUE, which owns the roster-write seam (`roster_edit.py` and
`postmerge.py`, which runs `roster_sync --apply`). The orchestrator adds
`tools/audit/seat/roster_sync.py` to its files. Carry file: `b143-P548.txt`.

## P549: S14-CLOUD-CLASSIFY-PAGINATE

Verdict: ACCEPT. It repairs an observed wrong behaviour, and I classify it medium: the reviewer's
settled-CI read fails in its main environment.

Source: queue line 233 (2026-11-11T00:35:43Z, the PR 3405 reviewer's friction).

Instances:
- `merge_train.py` reads check-runs and workflow runs with `gh api --paginate`. At main these are
  lines 1847 (check-runs), 1866 and 1881 (workflow runs), and 1647.
- In a cloud seat, `--paginate` follows a `repositories/<id>` Link header, which the proxy answers
  403. So `classify` exits 2 (unreadable), and the reviewer has to read check-runs page by page.
- `cloud_dispatch.py` names `merge_train.py classify` 8 times, so every cloud reviewer's brief runs
  it.

Cost: the check-run and workflow-run reads page by explicit `page=` number through
`gh_read.py`'s read rule, and stop on a short page. Self-test:
- a stubbed three-page answer reads every run;
- the null control, a one-page answer, makes one read;
- a stub that 403s on a followed Link header still reads every page;
- a mutant on the stop.

Binding: one carry, R10-GH-READ-RESIDUE, the GitHub-read seam. The orchestrator adds
`tools/audit/seat/merge_train.py` to its files. Hot-file overlap with R10-TRAIN-RESIDUE is by seam.
Carry file: `b143-P549.txt`.
