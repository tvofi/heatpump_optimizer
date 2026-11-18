# Proposal triage, session s14, batch 227

Source: the orchestrator's brief to triage seat s14-36 (2026-11-12), four proposals A-D, ruled as
P682-P685. Line numbers are at origin/main b737e88eee. Roster read at handoff/audit-r10-roster
fe123f912d.

## P682: HELD-REVIEW releases behind a disposed or refused verdict

Verdict: ACCEPT

Finding: twice on 2026-11-12 (#3461 dispatch edf76a05, #3479 dispatch 14c317ab) a repair handoff sat
HELD-REVIEW in `tools/audit/seat/cloud_relay.sh` (hold described at :127) behind a dispatch whose
verdict had been returned, refused by the relay over red CI and disposed; each waited for a hand
listing in cloud-handoff-release (about 15 and 12 minutes).
Ruling: the hold releases when the dispatch's probe ref exists and the relay ledger records it
disposed or refused; until that is built the level line names the state so the tick prints the cure.
Destination and severity: carry on R10-RELAY-NOBODY-STALL (M, medium, not-started), the live owner
of cloud_relay.sh hold residue.
Figure against 20%: 2 of 2 observed holds of this shape needed a hand release; the fix removes all
of them (100% > 20%). Basis: the two dispatch records above.

## P683: the train's post-merge record comment is refused by the shim's comment guard

Verdict: ACCEPT

Finding: `tools/audit/seat/shims/seat-gh` :123-126 admits a record-issue comment only from python
running the tree's own `tools/pr/gh_comment.py` by real path; the train's postmerge
(`tools/audit/seat/postmerge.py` :12) posts from another checkout, so the guard refused the record
comment on every merge tonight (#3478, #3468, #3404, #3469), each repaired by a hand
`postmerge.py --retry`.
Ruling: the guard admits the gh_comment.py of the caller's own git top level when that file is
tracked and byte-identical to the baked tree's, or postmerge invokes the baked tree's poster by its
real path; the fixer picks the sounder of the two and pins both arms (admitted poster passes, a raw
`gh issue comment` on a tracker still refused).
Destination and severity: carry on R10-GH-READ-RESIDUE-P3 (S, not-started, owns seat-gh and
merge_train.py); severity high, dispatched first among its carries.
Figure against 20%: exempt, severity high; 4 of 4 merges observed needed a hand retry (100%).

## P684: class barrier for Darwin-only prepr self-test reds

Verdict: ACCEPT

Finding: the third Darwin-only red in `tools/pr/prepr.sh --self-test` (R10-HOTFIX-PREPR-SELFTEST-DARWIN;
the wc padding at :2413; the wc-pad hotfix's own stub self-test) triggers the barrier named in
R10-HOTFIX-PREPR-WC-PAD's brief. No workflow under .github runs on macOS today.
Ruling: the barrier is a path-filtered CI job running `prepr.sh --self-test` on a macOS runner for a
pull request touching tools/pr/prepr.sh or its stubs. Cost: macOS minutes only on those few pull
requests; it catches all three instances, where the raw-wc lint (P676(b)) catches the wc subclass
only and a BSD-stub lane on Linux reproduces only the stubs it is given. The raw-wc lint is refused
as superseded. A root-cause record (dev/audit/rca, root-cause.md) is owed in its own seat at the third
instance; the barrier is its proposed countermeasure and the record must show the cost test.
Destination and severity: new group R10-PREPR-DARWIN-SELFTEST-LANE (S, medium, instrument), after
R10-HOTFIX-PREPR-WC-PAD; RCA seat dispatch is the orchestrator's.
Figure against 20%: 3 of 3 instances are Darwin-userland reds the lane would have caught before
merge (100%). Basis: the three instances above.

## P685: carry-fold misses an indented body_push refusal line

Verdict: ACCEPT

Finding: cloud_relay.sh :819 reads refusal kinds with `sed -n 's/^body_push: REFUSED ...'`, anchored at
column 0; the fixer's BLOCKED.md at handoff-wip 78b786f4 (#3481) quotes body_push output indented
(`    body_push: REFUSED CARRY-LANDED`, line 14), so the job printed "names no refusal line" and folded
nothing; the orchestrator folded by hand with carry_fold.py.
Ruling: widen the reader, not the writer's grammar: accept leading whitespace on the refusal line
(and only that), pinned by a self-test fixture with the indented quote; the kept-body check stays.
Destination and severity: carry on R10-RELAY-NOBODY-STALL (M, medium), beside P682 in the same file.
Figure against 20%: 1 of 1 fold of this shape missed (100%); the fix is one regex.
