# Proposal triage, session s7, batch 43 (P217-P218)

Two proposals, written by the orchestrator s7 as alternatives on the same merge-train step: V130
(refuse a draft head at the merge step) and V131 (undraft a head the train has already proved
mergeable). They are ruled together, and the ruling says which one stands. Facts read at
origin/main `ea36188c3`; roster at `origin/handoff/audit-r10-roster` `9aed78e0e` (212 groups).

## P217: a draft head is admitted by the train and fails only at the merge call (V130)

Verdict: REJECT -- superseded by P218. The refusal is sound and costs little, but it spends the
resource the instance actually lost. Its one useful part, the add-time `draft: true` note, is
carried inside P218's carry, so nothing is lost with the stop.

Source: `proposals.md` V130 (orchestrator s7, 2026-10-27T20:55Z).

Instances: two today. #2878 was admitted as a draft and undrafted 23 s later (`updated_at`
2026-10-27T20:30:28Z); had its batch reached the merge step first, it would have stopped there.
#2854 -- green on every check, `gate` green on two runs, `policy_lint` and `structure.py` green
against main, approved by the app -- read `BLOCKED`/`REVIEW_REQUIRED` for the single reason that
`isDraft` was true, and it is the critical path for the v7.0.5 stamp. Admission reads `state`,
which says `open`; `mergeable_state: BLOCKED` cannot distinguish a draft from a missing approval.

Why the stop loses to the undraft on the same evidence: both proposals fix the same blindness, and
the measured cost is not "a merge was attempted on a draft" -- no merge was attempted -- it is
**time**. #2854 sat in the batch as the stamp's critical path, and a `Stop` phase converts that
into a batch slot spent plus a human round trip to perform a metadata write that changes no tree.
The refusal is the right behaviour for a head that is *deliberately* held; it is the wrong
behaviour for the heads in both instances, which were stale flags on heads every other check had
already cleared. P218 clears the stale flag only after the train has proved the head, which is the
stronger of the two answers to the same observation.

What is kept: the add-time line logging `draft: true` as a note rather than a refusal. Draft state
moves in both directions between `add` and the merge, and an admission-time refusal would have
thrown out #2878, which was clean 23 seconds later. P218 makes that note load-bearing rather than
a comment -- see its narrowing.

## P218: the train undrafts a head it has already proved mergeable, instead of stopping on it (V131)

Verdict: ACCEPT narrowed -> a carry of **R10-TRAIN-UPGRADE** (`resume.stage` `done`, so the roster
op reopens it; it owns `tools/audit/seat/merge_train.py` and its brief is exactly "upgrade
`merge_train.py` so that ...", with one carry open). The narrowing: undraft only a head the train
**recorded as a draft at admission**, which closes the one arm the settled shape leaves open.

Source: `proposals.md` V131 (orchestrator s7, 2026-10-27T21:00Z, owner-directed).

Instances: the two above, read once. #2854's hours as the stamp's critical path is the cost that
decides it; #2878's 23-second window is the demonstration that the flag is often stale.

The settled conditions, which this ruling does not weaken: undraft runs in the merge step where
V130 would stop, and only on a head the train has already admitted to that step -- a posted `merge`
verdict naming the current head or one that carries to it (`app_approve.sh --carry` decides
carrying), a clean merge tree against main, a delivery row at the head, no failing or pending
required context, and the approval the step posts. Undrafting writes no commit and moves no head,
so the verdict still names the tree being merged.

**The arm the settled shape leaves open, which the narrowing closes.** An author who holds a head
by flipping it to draft *after* admission, while a `merge` verdict is already posted at that head,
passes every one of the five conditions -- the verdict is current, the tree is clean, the row is
there, the contexts are green, the approval is the step's own -- and the train would publish a head
its author had just marked as held. The conditions cannot see intent; they can see history. The
admission-time `draft: true` note that V130 asked for makes one bit of that history available at
the merge step: undraft only when the head was **already a draft when it was admitted**, so a flag
set later -- the only flag an author sets to say "stop" -- is respected. The cost is one recorded
boolean at `add` and one comparison at the merge step, and the add-time note is no longer a
comment; it is the guard's input.

Cost: one `gh pr ready` call in the merge step, one recorded boolean at admission, one log line
(`UNDRAFT #<pr> <head>`), and a re-read of `isDraft` after the call before the merge proceeds.
Benefit measured: #2854's hours in the live batch as the v7.0.5 critical path, and #2878's near
miss. No new dependency, no new rule. The train reads no draft flag today (`grep -ci draft
tools/audit/seat/merge_train.py` = 0 at origin/main `e8cb7e683`); a seat reads `isDraft` by hand, so the
recorded boolean and the re-read are the train's first draft reads.

Binding: undraft only after all five settled conditions hold **and** the head was recorded a draft
at admission; the `UNDRAFT` line is written once, with the PR and the head, and the merge continues
in the same iteration only if the re-read shows `isDraft` false -- a re-draft between the call and
the merge stops the run rather than merging past it; a failed `gh pr ready` is a `Stop` with its own
phase, never a silent continue; the non-draft path is untouched and prints no line (null control);
a draft whose verdict names an older head, a draft with a pending required context, and a head
drafted after admission are each left exactly as they are today (the three null controls, the third
being this ruling's addition); and the write is the app's, as the approval already is, so a run
without the app's authority fails at `gh pr ready` and stops.
