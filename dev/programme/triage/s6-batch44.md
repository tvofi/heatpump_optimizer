# Proposal triage, session s7, batch 44 (P219-P222)

Four entries: V132, V133, V134 and V135, written by the orchestrator s7 on 2026-10-27 and quoted
from `proposals.md` as they stand. Facts read at origin/main `e8cb7e683` (v7.0.5); roster at
`origin/handoff/audit-r10-roster` `de410e4c9` (212 groups). From this batch on, a heading carries no
proposal id: the contract's form is `## P<n>: <title>`, and the `Source:` line is the one place an
id is written (P219).

The same pull request corrects the headings P219 measures in the merged batches 36-40: P204-P210
read `(orchestrator relay; no proposals.md id)` instead of `(V124)`-`(V130)`, and P211 reads
`(V124)`, its `Source:` id, instead of `(V131)`. Each entry's `Verdict:` reads the same through
`roster_edit.ruling_verdict` before and after (P204 DEFER, P205 DEFER, P206 ACCEPT, P207-P209
ACCEPT, P210 DEFER, P211 ACCEPT), so no roster carry citing them moves. The residual the batch-40
review left is applied: `s6-batch40.md` now says the first cut "reached `main` as PR #2886 (merge
`a0e7664ea`)"; `ee5816b1` was the file's blob.

## P219: triage headings cite a V-number seven above their source

Verdict: REJECT -- the instrument (a pre-commit step that resolves a heading's V-number against
`proposals.md`). The defect it targets is real and is removed here at no tooling cost: headings
carry no id (above), and batches 41-43 are corrected on their own branches.

Source: `proposals.md` V132 (orchestrator s7, 2026-10-27T21:00Z).

Instances: five batch files, one cause.
- `grep -n '^## P\|^Source:' dev/programme/triage/s6-batch3[6-9].md dev/programme/triage/s6-batch40.md`
  at `e8cb7e683`: P204-P210 headings read `(V124)`-`(V130)`, and their `Source:` lines name the
  orchestrator's relays, not `proposals.md` ("V124 assigned to this seat in the orchestrator's
  09:37Z relay", `s6-batch36.md:18`; "not yet in `proposals.md`", `s6-batch39.md:13`, `:56`, `:93`,
  `:135`). P211's heading reads `(V131)` beside `Source: proposals.md V124` (`s6-batch40.md`).
- Batches 41-43 (PRs #2890, #2891, #2892): headings `(V132)`-`(V138)` beside `Source:` V125-V131.
- `proposals.md`'s own `## V124` to `## V131` are stamped 18:53Z to 21:00Z, after the relays
  batches 36-39 ruled: `git log --format=%cI --diff-filter=A -- dev/programme/triage/s6-batch3<n>.md`
  gives 09:47:20Z (36), 11:33:59Z (37), 12:41:42Z (38) and 17:18:24Z (39).
- Cost already paid: #2891's round-1 review blocked on V136 and #2890's round-2 review blocked on
  V132-V135 (hpo-approver, 2026-10-27T20:56:12Z and 21:05:00Z), plus one repair seat for the three
  branches.

Cause: not a counter that started seven ahead. Two writers allocated one id space. The relays
behind P204-P210 were seven proposals given ids V124-V130 outside `proposals.md`; the orchestrator
later wrote different proposals into `proposals.md` as V124 onward. The seat kept the relay
numbering, so every later heading ran exactly seven ahead -- the offset equals the number of
relayed rulings.

Cost: the candidate's check has one input, `proposals.md`, which lives in the orchestrator's state
directory and not in the tree. A pre-commit hook or CI step cannot read it on a runner, and naming
its path in the tree is a host path `ref_privacy.py` refuses. Moving the file into the tree is a
larger change than the defect (a new tracked, classified file rewritten on every relay).

Binding: the check's only input is out of the tree, and the defect needs no check once the
heading carries no id. The rule the owner already wrote holds it: `proposal-triage.md`'s entry is
`## P<n>: <title>`. The second writer is dispatch practice, not tooling: a relayed proposal is
ruled with `Source: orchestrator relay` and no V-number until `proposals.md` holds it (sent to the
orchestrator, not carried).

## P220: a fresh verdict is discarded for the life of a train, because a skipped entry counts as queued

Verdict: DEFER -- owned by **R10-TRAIN-OVERLAP-GRADE**: its carries 9 (P129,
`s6-batch26.md#P129`), 13 (P189, `s6-batch32.md#P189`) and 15 (the #2846 review applying P189)
already rule exactly this: one admission predicate for `add` and the drain, a PR this train skipped
and re-added at a new verdict head admitted into the next batch, and the same log word on both
sides. The group's `resume.stage` reads `done` with those carries unimplemented, so the route is a
reopen (the P196 route), queued for the roster seat. The filing's `REPLACED` line and its
replacement of a still-queued entry at a new head are not carried: P129's controls already fix the
words, and no instance of a queued (not skipped) entry at a moved head is recorded.

Source: `proposals.md` V133 (orchestrator s7, 2026-10-27T22:45Z).

Instances: three over two trains, two already counted.
- s7 merge train: `grep -n "in this train already" train.log` in the train's state directory
  (857 lines) returns one line, `ALREADY #2876: in this train already; not queued twice`; the merge seat's
  ledger entry at 21:40Z records the re-add at verdict head `9513b571` (comment `6452648096`).
- s40, 2026-10-25: #2745 and #2753, both counted by P129.
- At `e8cb7e683`, `batch` still seeds `seen` with every PR the train held
  (`tools/audit/seat/merge_train.py:2516`) and `queue_take` drops any PR in it (`:2567-2569`); the
  group's PR #2882 merged at `4db1d3e28` and
  `git diff 4db1d3e28^1 4db1d3e28 -- tools/audit/seat/merge_train.py | grep -c seen` is 0.

Cost: nothing new. P129's estimate (S, one predicate and self-test arms) and P189's (XS) stand.

Binding: the item is already ruled and carried twice; ruling it a third time adds a carry the
group would have to reconcile against two others. What is missing is not a ruling but a stage:
a `done` group with three unimplemented carries is invisible to dispatch.

## P221: `sweep` cannot merge a record PR, so the stamp's flush has no backstop as documented

Verdict: REJECT.

Source: `proposals.md` V134 (orchestrator s7, 2026-10-27T23:25Z, heading clock corrected in V135
to about 22:0xZ).

Instances: one, #2893 (`record/autofix`), the v7.0.5 stamp's flush.
- `sweep` left it with `LEFT #2893: the record pull request (record/autofix): --bot-prs merges it`
  (`merge_train.py:2038`). The line already names the flag.
- The merge seat's ledger, 22:19Z: "sweep_bots' --automerge-check guard exited 0, gh pr merge was
  refused by main-protect-checks (requires 1 approving review), #2893 had zero reviews"; "The beat
  approved 22:18:24Z and merged 22:18:33Z, 49 s after the train released the hold."
- The same ledger, 22:44Z: "a --bot-prs batch refreshes TRAIN HOLD, which suppresses the approver
  beat, and sweep_bots does not approve."
- `tools/audit/seat/INSTRUMENTS.md:516-519` names `sweep` the slow backstop for "each head `queue`
  admits", which excludes the record branch by `merge_train.py:2037-2038`; it does not name `sweep`
  for a record PR.

Cost: two strings (the `LEFT` line and `sweep`'s help) in `merge_train.py`, 5,831 lines and the
train's hot file.

Binding: the repair text the candidate would print -- "run a batch with --bot-prs" -- is the move
that failed in its own instance: a `--bot-prs` batch held the approver beat off the record PR and
`sweep_bots` cannot approve, so the PR merged only once the train let go. A message that sends the
next seat to that move is worse than the current one. The mechanism the ledger measured (a
`--bot-prs` batch suppresses the approval it waits on, and the train drops `gh pr merge`'s refusal
text, logging `(OPEN null)`) is a defect with its own route, not a proposal; it is sent to the
orchestrator for that route.

## P222: the worktree edit guard refuses edits on a worktree that does not exist

Verdict: REJECT.

Source: `proposals.md` V135 (orchestrator s7, 2026-10-27T22:18:45Z).

Instances: one, the `RELEASE_NOTES.md` edit during the v7.0.5 stamp, refused by a `PreToolUse` hook
naming a worktree `git worktree list` did not hold.
- `git grep -n "isolated git worktree\|base repo checkout"` at `e8cb7e683` matches only
  `dev/audit/rounds/round7/D3/REPORT.md:4`, which is prose.
- `.claude/settings.json`'s only `PreToolUse` hook is `.claude/hooks/pre-edit.sh`
  (Edit/Write/MultiEdit/NotebookEdit), and `grep -c worktree .claude/hooks/pre-edit.sh` is 0.

Cost: no repository cost can be stated, because no repository file produces the refusal.

Binding: no owner in the tree. The guard is the session host's own worktree-isolation check, and
no roster group can change it; a carry would sit on a group that cannot deliver it. The workaround
the filing used (a script, verified) is what the tree supports. The report belongs with the
owner, against the host.
