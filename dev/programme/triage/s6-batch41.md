# Proposal triage, session s7, batch 41 (P212-P215)

Four proposals appended to `proposals.md` by the orchestrator s7 at 2026-10-27T20:20Z (file mtime
21:20 local): V125, V126, V127, V128. Each is ruled on cost and benefit first, as
`proposal-triage.md` requires; nothing is implemented here. Facts read at origin/main
`a0e7664ea`; roster at `origin/handoff/audit-r10-roster` `d61e2834c` (212 groups).

## P212: a verdict cannot be voided by a change to the content it ruled (V132)

Verdict: REJECT. The proposed mechanism cannot see the instance it was written for.

Source: `proposals.md` V125 (orchestrator s7, 2026-10-27T20:20Z).

Instances: one, and it is this seat's own. #2886 merged at 19:41Z with `Fix review: merge
0f779c2dc` carrying `dev/programme/triage/s6-batch40.md` as this seat first wrote it; the seat had
already withdrawn one claim and split P211's second arm in its own record, and the correction
needed #2888 and a second review. The proposal's cost figure -- two pull requests, two reviews,
one day of a roster carrying a rejection of a mechanism the tree shows firing -- is not disputed.

Why the candidate fails on that instance, which is the whole of its benefit: the ruled text was
**inside the head**. `bus.sh dispatch` would digest `dev/programme/triage/*.md` as it stands at
the dispatched head, and `confirm` would compare against the same head's bytes (`bus.sh`'s
`dispatched` record is `<pr> <head> <reviewer> <nonce> <date> <model>`, line 479, and
`dispatched_to` matches on `pr` and `head`, line 313). Nothing in the tree moved between dispatch
and merge, so the digests are equal and the verdict confirms. What changed was the author's
judgement, written to the seat's state and to a message, never to a file. A digest of files
records files.

The candidate's second half is worse than idle here. It digests `dev/programme/rosters/*`, and that
ref moved three times in 45 minutes on this box today -- `32b938f3e` (19:0xZ), `8f7e252fe`
(20:0xZ), `d61e2834c` (20:3xZ), all reads recorded in the session ledger -- so a verdict whose
packet cites any roster path would be refused at `confirm` several times an hour. That converts a
rare stale merge into routine dispatch churn, and the churn is paid by every reviewer, not by the
one class it was built for.

What would make it worth pricing: the first instance where a document cited by a packet but
**outside** the head (the roster ref, a ruling file already on `main`) changes under a live
verdict and the stale reading is what merges. Then a digest of exactly the out-of-head paths the
packet cites, and nothing else, is a bounded check. No such instance is recorded.

## P213: a complete pull request can be unmergeable because its `## Head` names another sha (V133)

Verdict: ACCEPT narrowed -> a carry of **R10-ORCH-REVIEW-PACKET** (`resume.stage` `done`, so the
roster op reopens it; it owns `tools/audit/seat/review_packet.py`, and its brief is the packet's
refusals). The carried half is the first: the refusal states the repair, not just the fault. The
in-place `head_note.py` rewrite is not carried; see Cost.

Source: `proposals.md` V126 (orchestrator s7, 2026-10-27T20:20Z).

Instances: #2883 and #2889, both refused within ten minutes after their work was pushed and green
with `REFUSE head-note: ## Head does not name the dispatched head <sha>` -- #2883's body naming the
head as it stood before its fix commit, #2889's naming its code head rather than the head that
carries its own delivery row. Each cost a barge-in, a re-body through a push lane and a fresh
dispatch. Neither was a code defect.

The refusal already exists and names no repair: `tools/audit/seat/review_packet.py:289` appends
`head-note: ## Head does not name the dispatched head {head}` and nothing else. The one command
that rewrites a body already exists -- `tools/audit/seat/update_pr.sh <branch> - <body>` ("bring
the PR branch to: its current head ... + origin/main, prefix ## Head with what happened, push as
hpo-author", usage block) -- so the carried change is a message, not a mechanism.

Cost: one string in `build()` at `review_packet.py:289`, plus whatever the refusal needs to name
the branch (the packet already holds the PR and head facts it reads from the gate; a branch is one
more field of the same read). No new process, no new dependency, no new rule. Benefit measured by
two refusals in ten minutes at the cost of a barge-in, a push-lane re-body and a dispatch each.

Not carried, and why: the second half asks `tools/pr/head_note.py` to rewrite the `## Head`
paragraph in place. That file today has only `head_offset()` and `prefix()` -- it prepends a note
under the heading and cannot replace the section's content -- and no roster group owns it or
`tools/pr/merge_main_bot.py` (`files` and `hot_files` across 212 groups), so the change would land
in an unowned file through a group whose brief is the packet. The measured cost of the slip is the
missing instruction: an operator told the command can run it in the same minute. No instance
distinguishes "did not know the command" from "knew it and wanted a one-liner", so the rewrite's
benefit is unmeasured and belongs in a later proposal with an owner.

Binding: the refusal keeps its name and its trigger (`head_note_ok(body, head)` unchanged, so the
same bodies refuse); it gains the required head, the branch as the packet read it, and the
`update_pr.sh` invocation as one line; the hint may not be a promise -- if the packet cannot read
a branch, it prints the refusal without the command rather than a guess; and the self-test arm at
`review_packet.py:411` ("a ## Head naming another head refuses") gains its twin asserting the
repair text is present only when the branch is known (null control: the refusal with no branch
prints no command).

## P214: the claimnotes refusal leaves a PR unrunnable without stating the decision (V134)

Verdict: ACCEPT -> a carry of **R10-996-RUNNER-CLAIMS** (`resume.stage` `carries-open`; it owns
`tests/env_drift.py` and `tests/golden/claimed_drift.txt`, and its note is the claimnotes arm).

Source: `proposals.md` V127 (orchestrator s7, 2026-10-27T20:20Z).

Instances: #2872 is DIRTY at `fe964895e` and the bot answered `skip-driver-refused
tests/golden/claimed_drift.txt`. Establishing why took a diff of both sides: `main` added
`negative_prices` and `summer_dhw_only` (R10-SAV-COMFORT) and keeps `config_flow`'s #1955 text,
while the branch deletes those two and rewrites `config_flow` for its own
`heat_pump_cop_partload_derate`. A DIRTY pull request runs no CI, so nothing on it can be verified
until the decision is made -- the cost is the owner's reconstruction, and the blocked queue behind
it.

The decision text already exists and is not reaching the operator. `tests/env_drift.py`'s
`conflicting_claims_message` (around 1845-1857) prints, verbatim, "CONFLICTING CLAIMS: both sides
rewrote the claim list -- this branch claims [...] and the merge brings in [...]. A claim excuses
one release's golden diff ... Resolve it by hand: keep the claims that describe THIS branch's diff
and delete the rest." That is the whole of what the proposal asks for. What the bot emits is
`"skip-driver-refused " + ",".join(driver_conflicts or text_conflicts)` at
`tools/pr/merge_main_bot.py:139` -- a filename list with the reason stripped.

Cost: carry the driver's own message into the bot's line (or its stderr) instead of the filename
list; no new analysis, no canonical-environment measurement, no change to either claim file. The
message the driver prints already names both sides and the decision rule, so the fix is one join
in the bot and one caller check. No canonical-environment run is owed by the fix; the *ruling* on
#2872 remains a separate, owner-side measurement and this ruling does not pre-empt it.

Binding: the bot's line carries `env_drift`'s own message, not a second summary of it (one reader,
the precedent P207 set for `carry_audit`); when the driver cannot be run, the bot prints today's
filename list rather than a guess -- that is the null control, and a merge with no claim conflict
prints exactly what it prints today; the fix touches no claim file (the mandate excludes them) and
does not decide any claim; and the driver's message stays the one source, so a wording change
lands in `env_drift.py` only.

## P215: a lane rule that only prose enforces (V135)

Verdict: ACCEPT narrowed -> a carry of **R10-ROSTER-OPS** (`resume.stage` `done`, so the roster
op reopens it; it owns `tools/audit/seat/roster_edit.py` and the mutant driver
`tools/audit/seat/r10_roster_ops_mutants.py` that re-runs its self-test). The narrowing: the guard
covers the **structural** ops, and leaves `set-stage`/`set-resume` callable directly.

Source: `proposals.md` V128 (orchestrator s7, 2026-10-27T20:20Z).

Instances: this sweep the orchestrator ran `roster_edit.py wire-issue` twice --
`R10-RCA-FRICTION-RESIDUE` `fixes` `2410` at `e331abfbf` and `2593` at `d61e2834c` -- before the
owner said roster operations belong to the standing roster seat. Both writes were correct; one
writer was wrong; nothing was red. Verified here at `d61e2834c`: the group's `fixes` is
`[2410, 2593]`, and `2597`, `2660`, `2784` are queued to `roster-queue-s7.txt` for the standing
seat.

Why narrowed: the sweep template instructs the orchestrator to run `roster_edit.py set-stage`
directly after each merge (`tools/audit/seat/sweep_template.md:63`, `nudge.md` steps 12 and 18), so
a guard on every op would refuse the tree's own written procedure -- the next slip, built by the
fix. The structural ops (`wire-issue`, `unwire-issue`, `append-group`, `edit-brief`,
`append-carry`, `set-after`, `drop-carry`; `roster_edit.py:703-705`) are the ones the lane assigns
to the roster seat, and the instance's op is among them.

Cost: one environment marker set where the queue runner builds its child environment
(`tools/audit/seat/roster_queue.py:94-102`, which already builds `env` and invokes
`roster_edit.py`), one guard at the top of `roster_edit.py`'s op dispatch -- before the JSON load,
so a refusal writes nothing -- and two self-test arms (a structural op with no marker refused; the
same op with the marker accepted), with the fixtures' own direct invocations carrying the marker.
The mutant driver already exists and re-runs the self-test per plant. Benefit measured: two
mis-caller writes landed in one sweep on correct content, and the class has no bound because no
instrument can tell its caller.

Binding: the marker is an environment variable the queue runner sets on its child, not a lock and
not a pid check, so the seat's own pass carries it and a seat calling `roster_edit.py` directly
from a shell does not; the refusal names the queue runner and the group and exits before the
roster file is read; `set-stage` and `set-resume` are unchanged and stay direct-callable, because
the sweep template and `nudge.md` require them; the null control is `roster_queue.py` running the
same ops, which passes with the marker; and a caller that sets the marker by hand is out of scope
-- the guard stops a caller that does not know the lane, which is what the instance was, not a
caller determined to break it.
