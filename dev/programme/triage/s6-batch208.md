# Proposal triage, session s14, batch 208 (P639)

Sources:
- Triage queue line 316, 2026-11-11T15:59:50Z, and the disk survey `s14/seat/disk-1/DISK.md`.
- `tools/audit/worktree_gc.sh` at origin/main: header lines 21-79 (arms A-E and the keep rules) and
  the self-test case at :336.
- `git worktree list` on the shared object store and `du` over the triage seat scratch, read
  2026-11-11 about 16:20Z.

## P639: one reused (or removed) worktree per triage record batch

Verdict: ACCEPT alternative 1 (the record script removes its own worktree). REJECT alternative 2
(a `worktree_gc.sh` arm for the seat scratch).

Source: triage queue line 316, PROPOSAL (orchestrator s14). Each triage record batch leaves about
155 MB of worktree behind, and 32 of them put the disk under the 6 GiB floor at 15:50Z.

Instances:
- Per-batch cost: `du -sh wt141 s14-22/wt206` gives 156M and 156M.
- Rate: `git log origin/handoff/audit-r10-roster --grep='^triage: s14 batch'` shows batch 141 at
  01:33+01:00 and batch 207 at 16:54+01:00. That is 67 batches in 15.4 h, about 4.4 per hour, or
  about 0.67 GiB per hour of worktrees left behind if nothing removes them.
- Left after the 15:58Z removal: `ls -d wt1* s14-*/wt[0-9]*` lists 39 directories and
  `du -sch` totals 6.0G. All 39 are clean and their HEADs sit on the roster branch or on their
  own handoff/triage-s14-batchN ref, so nothing in them is unpushed.
- worktree_gc cannot collect them as it stands. Each is a BRANCH worktree (`triage/s14-batchN`)
  with no pull request, and the keep rule at header :72 ("a branch with no pull request at all
  (ambiguous, not proved merged)") keeps that shape, pinned by the self-test at :336. Its default
  seats root is also /tmp/hpo-orch, not s14/seat.
- One producer: the triage seat's `batch.sh`, which seats copy forward at each recycle (s14-20,
  s14-22 and s14-23 each hold a copy).

The rule, run per instance:
- Alternative 1. s14-23/batch.sh now ends by removing `wt$N` once the roster record's local head
  equals origin/handoff/audit-r10-roster and the tree is clean. Its own batch 207 worktree was
  removed by hand after read-back: `git worktree list | grep -c triage/s14-batch207` gives 0.
  Measure: GiB of triage batch worktrees per session falls from about 0.67 GiB per hour of seat
  time (10.1 GiB this session: 4.1 GiB removed plus 6.0 GiB left) to at most one live worktree,
  about 0.16 GiB. That is a reduction of more than 95%, well past the 20% bar.
- Alternative 2. A gc arm would have to relax the no-pull-request keep rule (or add a triage-branch
  exception to it) in a 1188-line deletion tool whose keep rules exist because evidence was lost
  once (#716). Alternative 1 already removes every instance at its single producer, so on this
  class the arm would add 0% on the same measure.

Cost:
- Alternative 1: three lines in a seat-local script. No tracked file, no CI, no API calls, no
  review round. Upkeep is the recycle handoff naming the script to copy.
- Alternative 2: a new arm and a self-test case in `tools/audit/worktree_gc.sh`, a keep rule
  loosened, and a review round, for a class that no longer arises.

Binding:
- Alternative 1 clears the bar on a measured gain, at no tracked cost.
- Alternative 2's binding cost is complexity and risk in a deletion tool, against a zero
  remaining gain.

Destination: not routed to the roster. The change is in the triage seat's own record script
(`s14-23/batch.sh`), and the s14-23 recycle handoff carries it forward with the line "copy
s14-23/batch.sh; never leave a batch worktree". The 39 predecessor worktrees were removed at
16:03Z on the orchestrator's instruction. Each went by `git worktree remove` after a clean,
on-remote and no-cwd check; none was skipped, and `df -h /` available went from 9.4Gi to 16Gi.

What would reopen alternative 2: a second producer of no-PR branch worktrees in seat scratch, or a
batch worktree found left behind by a seat running the s14-23 script.
