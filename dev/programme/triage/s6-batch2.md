# Proposal triage, session s6, batch 2 (P45-P51)

Seven proposals from the s6 orchestrator's out-of-tree `proposals.md`: items
I, J, K, L, M (the s5 orchestrator's, left unruled -- `s5-batch2.md` ruled
A-H as P34-P41, and no file under `dev/programme/triage/` names any of I-M)
and the s6 items Q and R. Ruled in the order the orchestrator listed them as
P45-P51 from `dev/governance/roles/proposal-triage.md`. Numbering continues
after `s6-batch1.md` (P42-P44, pull request #2688, unmerged at this base).

Base: origin/main `50af6174f`; roster origin/handoff/audit-r10-roster
`4c54758d7`, read with
`git show origin/handoff/audit-r10-roster:dev/programme/rosters/wave-r10-groups.json`.
Logs cited by file name are in the orchestrators' scratch directories
(`/Users/timmalmstrom/hpo-orch/r10s5/` and `.../r10s6/`, out of tree).
GitHub calls: 0.

A roster op citing an ACCEPT below resolves only once this file is on the
roster branch or origin/main (`roster_edit.py` reads the ruling from there).

**One destination, `R10-ORCH-BEATD`** (existing, not-started, in the in-tree
roster at origin/main), carries P45, P46 and P51. Its brief owns "the
supervised beat and its job table ... the journal the sweep's liveness rule
reads" (files `daemonize.py`, `tick_loop.sh`), the closest live scope to the
sweep template's liveness step (1b), `pulse.py`'s seat judgement and the
standing seats' waiting. A new group could not be the destination: `carry_audit`
reads the in-tree roster, which a later roster op does not yet change. The work
may later be split into its own group (`R10-FLY-STANDING-SEATS`: files
`tools/audit/seat/sweep_template.md`, `pulse.py`, `INSTRUMENTS.md`,
`dev/governance/roles/standing-*.md`) if the group's design pass finds it
too wide; the carry text is written to move whole. Each carry adds those files
to the group's scope. The carry text, shared by P45, P46 and P51:

> Standing-seat wiring (triage `s6-batch2.md#P45`, `#P46`, `#P51`). (1)
> `sweep_template.md` steps (2), (3), (4) and (6) tell the orchestrator to do
> inline what decision 0015 and the owner (2026-10-23T19:42Z) give to the
> standing seats; rewrite each to queue a line to its seat and read its
> report. (2) `pulse.py` judges a standing seat only by `--seat-queue FILE`
> with `<epoch> <text>` lines; add `--seat-alive SEAT=FILE[:MIN]` (mtime of
> `<seat>.alive`, STOPPED past MIN or the seat's STANDING cadence, UNREADABLE
> when absent) and make step (1b) use it. (3) each `standing-*.md` gets a Wait
> paragraph: a seat ends a turn only when nothing is owed; it waits with a
> `run_in_background` loop that touches its alive file and exits on a queue
> change or the window's end. Controls: the rendered sweep names no train launch
> for the orchestrator; a fresh `.alive` is ok and a stale one STOPPED, the old
> queue arm still reads its own format; a mutant for each arm. Policy files:
> the owner approves the merge.

## P45: sweep_template.md routes the orchestrator to work the standing seats own
Verdict: ACCEPT -> R10-ORCH-BEATD (carry above, item 1)
Source: s6 proposals.md item I (s5 measurement).
Instances: 2 sessions -- s5 wrote five "Sweep overrides" for steps (1b), (2),
(3), (4) and (6) into `r10s5/seat-ledger.md` ("Sweep overrides (owner,
2026-10-23)", lines 17-22), and the s6 render still carries the same text:
`r10s6/sweep.md` line 11 tells the orchestrator to launch
`tools/audit/seat/train.sh` itself, and
`rg -n 'train.sh' tools/audit/seat/sweep_template.md` prints it at origin/main
(line 61). The template was last edited by decision 0015's commit `b16084794`
(`git log -1 --format=%h -- tools/audit/seat/sweep_template.md`), which made
the four seats standing, so the contradiction with `orchestrator.md` section
5 ("Four standing seats do the routine work, never you inline", line 109)
was introduced there and is rendered into every session.
Cost: S -- one template, prose only; a `sweep_render.py` fixture row asserting
the rendered step (3) names `merge-queue` and not `train.sh --repo`, one mutant
(the old sentence returns); no new check, no hot file.
Binding: every new orchestrator session otherwise relearns the overrides from
the ledger of the last one or follows the template into a second live train
(`nudge.md`/`orchestrator.md` forbid it), against an owner ruling already made.
Decided: the template, not the overlay, because an overlay holds per-session
paths and `sweep_render.py` is the one rendering.

## P46: pulse.py cannot judge a standing seat whose queue is not `<epoch> <text>`
Verdict: ACCEPT NARROWED -> R10-ORCH-BEATD (carry above, item 2); the harness-neutral queue contract for all four seats is REJECTED
Source: s6 proposals.md item J (s5 measurement).
Instances: 2 sessions, 4 queue files -- s5's first pulse (19:39Z) read
`merge-queue.txt`'s leading PR number as an epoch ("57 years old"), so
seat-merge showed STOPPED, and queues with comment lines showed UNREADABLE
(`r10s5/seat-ledger.md` line 22; the workaround files were
`r10s5/pulse-*.txt`). In s6 the rendered step (1b), `r10s6/sweep.md` line 7,
passes `merge-queue.txt`, `roster-queue.txt` and `dispatch-queue.txt` to
`--seat-queue` again, so the same misreading is scheduled to repeat every
sweep. `pulse.py`'s own header (lines 49-53) defines the one accepted format,
and `rg -n 'alive' tools/audit/seat/pulse.py` finds no liveness-by-file arm.
Cost: S -- a `--seat-alive SEAT=FILE[:MIN]` arm of about 15 lines beside
`judge_queue`, using the `STANDING` cadences already in the file
(`STANDING = {"tick": 70, "merge": 120, ...}`), fixtures for fresh, stale and
absent, one mutant each; no API call, local `stat`.
Binding: a false STOPPED makes the sweep restart a live seat (a duplicate
merge seat is the worst case) and the workaround, a shadow `<epoch> <item>` line
appended and removed by hand per queued item, is a standing orchestrator
cost. The seat already writes `<seat>.alive` (tick, merge, roster, dispatch
all do), so judging that file needs no new format and no change to any seat's
queue. The proposal's full contract (every queued item carrying time and id,
completion recorded in a report) would edit four contracts, the roster
and merge instruments, and every orchestrator's queue habit to save what the
alive arm saves; REJECTED on that cost.

## P47: roster_sync marks a multi-PR group done when any one of its PRs merges
Verdict: DEFER -> owned by R10-ORCH-ROSTER-SCHEMA (it owns the stage set and `roster_sync.py`); re-triage at a third instance
Source: s6 proposals.md item K (s5 measurement).
Instances: 2 -- `r10s5/state-beat.log` line 306, 2026-10-23T20:08Z:
`R10-CI-LAYOUT-P2: stage in-progress -> done at 5056615a28b8 (PR #2638
MERGED)`, line 308: `REFUSED Carry: R10-CI-LAYOUT-P2 from #2638: the
destination is done`; the group's second pull request merged later (line 585,
`done at b927f431abad (PR #2673 MERGED)`). The second is the proposal's
`R10-FLY-RELAY-REVIEW-FF` at #2664, which sits at stage `carries-open`
today. The mechanism is `roster_sync.chosen` (`rg -n 'def chosen' -A8
tools/audit/seat/roster_sync.py`): an open pull request wins, else the newest
merged one decides, so a group whose next pull request is not yet open reads
done.
Cost: M -- a rule needs either a group field declaring several pull requests
(schema change, a lint, a migration of 171 groups) or a ref scan for an
unmerged handoff ref per group (`git ls-remote`, run in the state beat on every
main move; a stale ref would hold a group open forever).
Binding: the damage so far is one false unblock (`R10-FLOW-MQ-PROBE`, noted
in the proposal) and one refused carry, both cured by a hand `set-stage`, and
a cheaper mechanism exists today: a stage outside `DERIVABLE_STAGES`
(`carries-open`) is never overwritten by the sync (`roster_sync.py` lines
84-92), so the orchestrator sets it when a group declares more than one pull
request. Two instances is below the third-instance trigger of `CLAUDE.md`'s
root-cause paragraph. What would change the answer: a third group read done
with its pull request unmerged, then the root-cause seat names the process
state; the schema choice belongs to the group that owns the stage set.

## P48: roster_edit.py has no op for `files` or `resume.pr`
Verdict: DEFER -> owned by R10-FLOW-TOOLKIT-MODEL (not-started; edits `roster_edit.py`); reopen when a widening names `coordinator.py`
Source: s6 proposals.md item L (s5 measurement).
Instances: 3 refused ops in 1 session, 2 of them `files` -- `r10s5/roster-report.txt`
line 16 (17:10Z, R10-LIVESTATE `files` += two files), line 44 (21:19Z, six
files) and line 43 (20:42Z, `set-resume R10-CI-LAYOUT-P2 pr=2673`: "invalid
choice: 'pr'").
Cost: S for `set-files add|remove` (about 25 lines, a fixture pair, a mutant, in
`roster_edit.py`); `resume.pr` stays derived.
Binding: a group's `files` has exactly one reader that decides anything,
`tools/plan/replan.py` line 205 (`hot_files` plus `files`, tested for a
path ending in `coordinator.py` to serialise coordinator groups); the six
files of the refused widening name none, and both widenings were recorded
without loss as a `note` and a carry (`roster-report.txt` line 50, read back
exact). So the measured cost is two refused queue lines and a note, in one
group. The `resume.pr` half is moot: `roster_sync.norm_head` already strips
`fix/` and `handoff/` prefixes, so the mapping the proposal asks for exists,
and the stale `pr` is a derived field the next sync rewrites. What would
change the answer: a widening that adds `coordinator.py` (the planner then
mis-serialises silently while the roster says otherwise), or a second reader
of `files` (the 08:00Z hot-file overlap ruling may add one).

## P49: record-autofix opens a new record pull request after every record merge
Verdict: ACCEPT (measure first) -> R10-FLOW-RECORD-PITCH (new carry; same workflow step)
Source: s6 proposals.md item M (s5 measurement).
Instances: 14 of 48 first-parent merges on main since 2026-10-23T00:00Z are
`tvofi/record/autofix` pull requests (`git log origin/main --first-parent
--since=2026-10-23T00:00Z --format=%s | grep '^Merge pull request' | grep -c
record/autofix` is 14; the others 34), and the chain is visible in
consecutive numbers: #2676, #2679, #2680, #2682, #2684, #2685, #2686 each add
exactly their own `dev/programme/delivery/<N>.md`
(`git diff --name-only --diff-filter=A <merge>^1 <merge> -- dev/programme/delivery/`).
#2685's own row reads "record: delivery rows for #2681, #2684", and #2684 is
itself a record pull request, so a record merge does owe a later row. What I
did not measure: whether `record_row.py` plans that row because the merged
record PR's own row still reads `open` (the self-row is written before the merge,
`nightly.yml` lines 492-515: "carries no merge SHA") or because the `record`
check demands it; that decides the fix and is the first step of the carry.
Cost: S to M, inside the step `R10-FLOW-RECORD-PITCH` already rewrites (that
group's brief: record pull requests are "about half of every merge to main",
and its pitch bound skips an automerge younger than 3600 s). The pitch bound
lowers the rate of the chain, it does not end it: a record merge begets
the next after one pitch, indefinitely.
Binding: each record merge moves main under every open head (that group's own
finding), so a chain with no terminal condition costs a main move per pitch
for rows that carry no information, and blocks any "queue drained" state
(`ruleset_cutover.py queue-drained`, per the proposal). Carry text for
`roster_edit.py append-carry` (cites this ruling): "Record chain: measure
first whether a record-only merge owes a further row (plan record_row.py at
main right after one: `delivery/<N>.md` of the merged record PR reading `open`,
or the `record` check demanding a row for `record/autofix` merges). If it does,
a record pull request's own merge must owe none: write its row final in the
same pull request, or let the status cell `open` satisfy `record` for a
`record/autofix` head, whichever the measurement shows is the cause. Controls:
after a record-only merge the beat's plan prints nothing owed (null control:
after a real rowless merge it prints that row); one mutant. HANDOVER trap 15 (one
record per merge) stays true for real merges."

## P50: cloud seat pools -- claim-ref routines instead of one routine per seat
Verdict: REJECT
Source: s6 proposals.md item Q (s6 measurement, 07:46-07:56Z).
Instances: 1 session, 8 fixer runs fired from one pool routine
(`r10s6/seat-ledger.md` line 9, 07:52Z) and one reviewer pool (line 10). The
proposer's figure is ~5k orchestrator tokens per seat for create+run against
~2.5k per pooled fire; not re-measured here.
Cost: M -- `cloud_dispatch.py --pool` writing `POOL.txt` and the atomic
`claim/<session>/<topic>` push protocol, a `prune_refs.py` rule for `claim/*`
(`R10-FLY-PRUNE-REFS` is its owner and not yet landed), an INSTRUMENTS.md
entry, fixtures for a claim race; plus a standing change of rule.
Binding: (1) the saving, about 2.5k tokens per seat, is the same payload echo
that P-A (s4, 2026-10-22, accepted narrowed, carried verbatim in `R10-FLOW-DESIGN-STAGES`)
already removes by rendering a stub that names the pushed commit, and the pool
is not needed once that lands. (2) A pooled run is not persistent, but a blocked verdict goes back to the
original fixer session (the owner's standing rule, as the orchestrator applies it);
a pooled fixer has none, so the rule would need a new exception. (3) A pool routine fixes one model and effort: the
batch's own ledger line 15 records the reviewer pool running opus, "not the
rendered sonnet", which breaks the per-seat model routing (sonnet
where an oracle exists, opus for adversarial review). The pattern remains available to an orchestrator as
session scratch, which is where it is today. Reopen only if the P-A stub
lands and a per-seat fire still costs a measured, material share of a round.

## P51: standing seats end their turn after one pass
Verdict: ACCEPT NARROWED -> R10-ORCH-BEATD (carry above, item 3); a tracked `seat_loop.sh` is REJECTED
Source: s6 proposals.md item R (s6 measurement, 07:49Z-08:00Z).
Instances: 4 in the opening 11 minutes of one session -- the haiku tick and
dispatch seats and the sonnet merge and roster seats each ended their first
turn with a `nohup` or untracked watcher, so nothing woke them, and each
needed an orchestrator `SendMessage` (the proposal's count; the seats'
reports are in `r10s6/*-report.txt`). The four contracts each carry a
**Restart** line and nothing on how to wait: `rg -n -i 'wait|background'
dev/governance/roles/standing-*.md` prints one unrelated line (standing-tick.md:8), so a seat
chooses its own pattern.
Cost: S for the paragraph -- about 6 lines in each of four contracts, naming the
pattern this seat uses itself (a `run_in_background` shell loop that touches
`<seat>.alive` every 25 s and exits on a queue change or the window's end, so
its exit wakes the turn; a detached `nohup` wakes nothing). A tracked
`seat_loop.sh` would add a script, a self-test arm and an INSTRUMENTS entry
for a four-line loop.
Binding: the failure is the seat having no stated way to wait, and the
cheapest fix is the statement. The proposed helper is the same loop in a file
and costs a maintained script plus mutants; REJECTED as the surface, kept as
the paragraph. The paragraph is a policy change to four contracts, so the
owner approves its merge (CLAUDE.md, "Where the policy is").
