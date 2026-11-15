# R11-PRE-STANDING-SCRIPTS: the merge and dispatch seats as beat rows, one exception seat

Designer round 1. **Base b3831ff64eca1936f0b618193ee86c3e337b51a9**; code read there (origin/main at dispatch). Predecessor R11-PRE-PARALLEL-PIPELINE has no handoff head: its approved note (design/R11-PRE-PARALLEL-PIPELINE 22fdbabafb30, design-verdict 2d229ce672bb) is read instead. Roster: handoff/audit-r10-roster 51e290c8ea, size L, carries 0-17. Owner: card R1 2026-11-13 (scripts on the beat, one exception seat); card C8 2026-11-15 (L, design first). Evidence: process-convergence audit d5d7ff8187 section 2.2 and "What to REMOVE" (standing seats 66 % of local seat tokens, 1.42 B in s14); triage r10-round-end.md P752, P772, P773, P792 at 2e17928032.

**NO-READ.** Carry 16's prototype scripts (the dispatch, loop, verify and publish helpers it names) live under the orchestrator's state directory and on no ref; a cloud seat cannot read them. This note specifies from the two standing contracts and the three written traps. **Precondition on the orchestrator, before the fixer of part 3 dispatches:** push them, paths scrubbed by ref_privacy.py, to an archive ref (decision 0013) and name it in that part's brief. Carry: R11-PRE-STANDING-SCRIPTS

## 1. Owning seams (fixer.md step 17, tests/seam_map.json names none of these files)

- **Owed-event watch (new module, tools/audit/seat/, name the fixer's):** owns the fired-ledger read, the "a seat is on it" predicate and every owed-by-grace arm. orchestrator_tick.py's payloads (FIRE-OWED, :1087) and _seat_on (:857) **move** into it; the tick imports them. Beat row cp-owed in beat_jobs.py and beatd.jobs.json calls it.
- **Dispatch drain (new module):** owns turning an orchestrator dispatch line into bus records and a published payload. It calls cloud_dispatch.py (the one renderer, unchanged as owner of `_prompt`), bus.sh dispatch / dispatch-handoff, approve_held_runs.sh and outside_intake.py answer. Row dispatch-drain.
- **Merge drain (new module):** owns turning an orchestrator merge line into a train entry and a post-merge report. It calls `merge_train.py add`, tools/pr/preflight.sh and postmerge.py. **merge_train.py is not edited** (L5: its redesign is P754's, roster files list to drop it: `set-files` owed). Row merge-drain.
- **Queue grammar:** roster_queue.py's parse_line and mark_line (`#done` / `#refused`, atomic rewrite), imported, never copied.
- **Contracts:** standing-merge.md and standing-dispatch.md become retirement stubs like standing-tick.md; standing.md becomes the **exception seat's** contract (one seat, its Wait, Recycle and Alive files terms kept; Reads and Autofix hold move into the drains as code). Callers: orchestrator.md section 5, CLAUDE.md's role table, INSTRUMENTS.md, sweep_template.md, scorecard_selftest.py, tests/entities.py, dev/audit/README.md, policy_budgets.json (enumerated in section 4). Policy: owner review.

No concern needs two owners.

## 2. Shape

**Lines in** (orchestrator appends; it still chooses everything, as both contracts say):
`merge <pr> <head40> closes=<n,...|-> mandate=<id|->`; `reviewer <pr> <head40>`; `reviewer-handoff <topic> <tip40>`; `fixer|designer|design-reviewer <group> [--part k] [--design-requested <blocked-ref>]`; `answer <issue>`.

**Lines out**, one digest per row under S/digest/jobs/: today's report grammar unchanged (`merged #<n> <sha> closed <issues>`, `parked #<n> <reason>`, `set-stage owed`, `fire-owed <ref>`), plus `EXCEPTION <row> <key> <class>: <refusal tail>` for anything a script must not decide. Classes are fixed tokens: head-moved, autofix-hold, not-reviewable-real, not-reviewable-deferral, refused-<tool>, unintended-close, owed-record, unreadable. A held line (autofix hold, deferral-only NOT REVIEWABLE) stays unmarked and is retried next pass; it becomes an EXCEPTION only past its grace.

```
orchestrator --line--> queue file --row pass--> drain
  dispatch-drain: re-read head == line head? -> approve_held_runs -> autofix hold
     -> classify (merge_train.py classify): RED real -> EXCEPTION; deferral-only -> hold
     -> bus.sh dispatch [--nonce relay's] [--reviewed-head only if a prior verdict]
     -> cloud_dispatch.py --publish -> read dispatch ref: prompt line 1 == rendered? -> fire-owed <ref>
  merge-drain: head == line head, verdict posted (merge_train.py posted-verdict) -> preflight over body
     -> merge_train.py add -> (on merge) postmerge.py -> closed set == closes= ? else EXCEPTION
cp-owed: roster_lib.is_outside(g) or g in critical_path_read(...) -> CP-OWED lines past grace
exception seat: reads EXCEPTION and fire-owed lines; fires (a RemoteTrigger call is a tool, not a script); answers or routes to the orchestrator
```

**Invariants.** K1: no script chooses what merges or dispatches (the line does). K2: one bus dispatch per (pr, head); a nonce the relay minted is passed with `--nonce`, never re-minted (trap 1). K3: `--reviewed-head` only when a verdict for the PR exists; a first round has none (trap 2). K4: nothing is fire-owed until the published prompt's line 1 equals the rendered one (trap 3). K5: a drain never retries past a refusal; it marks `#refused` and prints EXCEPTION.

**cp-owed** (carry 4, verbatim arms and graces): PR arms merge-verdict-no-approval 10 min, approved-unmerged 45, blocked-no-fire 15, head-no-dispatch 25; group arms UNFIRED, DESIGN-REVIEW OWED 10, FIXER-OWED, SEAT-SILENT 90. SEAT-SILENT keys on the return ref's absence, never on a session's status: carry 17 measured last_event_at equal to created_at for live sessions. Ranked critical path first, then outside, then hotfix (roster_lib.is_hotfix, narrowed to the flag or the name: carry 11).

**Prompt text** (cloud_dispatch.py `_prompt`, carries 8, 9, 10, 17): every stop routes to a BLOCKED note (markdown, named BLOCKED) on handoff-wip/<topic> (the setup REFUSE at :238 and the tail at :377-378); fixer text names in-seat repair of every body_push.sh refusal but CARRY-LANDED (exit 4), and PREPR_SKIP_CLOSURES with a Friction line; fixer and reviewer text: wait in the foreground, bounded, never end a turn on a background task or subagent (heavy work may still run in the background; :240 is reworded, not removed). WAIT_LINE's 240 s stays unless the fixer reproduces carry 17's exit 137 under it.
**CLI** (carry 14): `--part` with `--group` renders a This-part line on the flag path (PC-07, re-measure: at the base only `--topic` with `--group` refuses, :1572); PC-08 weighs a light text carry at one fifth of a part's five (kind read from the carry's text class, the rule in fixer.md); PC-09: `--design-requested <ref>` admits a design role on size M when the ref holds a BLOCKED note naming a design departure (roster_lib.needs_design unchanged).

## 3. Alternatives, and why they lost

1. **One Workflow script per group** (PC-1113-06, carry 15). Lost: a workflow is an orchestrator turn plus agents, so it moves the coordination tokens rather than removing them, and it has no state across the beat's restarts that the queue file has. Its pricing is owed against R11-PRE-TOKEN-LEDGER's ledger; recorded as still DEFERred. Carry: R11-PRE-TOKEN-LEDGER
2. **New arms in orchestrator_tick.py** (where FIRE-OWED lives). Lost: L5, past the third-change threshold; and the tick is read-only by contract, so drains could not live there.
3. **Drain subcommands in cloud_dispatch.py / merge_train.py.** Lost: both files are other groups' hot files (TOKEN-LEDGER, PARALLEL-PIPELINE) and merge_train.py is L5-frozen; a renderer that also owns queue state couples two concerns.
4. **Keep a haiku dispatch seat with a shorter contract.** Lost: the seat's tokens are the problem measured (five recycles on 2026-11-13); every step it runs is a fixed command sequence.

## 4. Sibling sites (enumerated)

- `git grep -n "your result" -- tools/audit/seat/`: :238, :378 change; :371 is the probe's real result channel (null control, unchanged).
- `git grep -ln "standing-merge\|standing-dispatch" -- . ':!.cursor' ':!.claude/rules'`: live policy and instruments change (CLAUDE.md, orchestrator.md, standing.md, INSTRUMENTS.md, sweep_template.md, dev/audit/README.md, tests/entities.py, scorecard_selftest.py, policy_budgets.json, closures.json via derive); triage, rca, PLAN-TABLE and the r10 roster are records, out of scope.
- `git grep -n "FIRE_GRACE_MIN\|_seat_on\|_fired(" tools/audit/seat/`: every caller moves to the watch module in one change.

## 5. Parts, serial position, hot files

| part | carries | files | position |
|---|---|---|---|
| 1 S | 4, 5, 11 | watch module, beat_jobs.py, beat_jobs_selftest.py, beatd.jobs.json, roster_lib.py, orchestrator_tick.py (move only) | first; touches no day-1 file of PARALLEL-PIPELINE, so it may dispatch before that group merges (orchestrator's call; owner: "never let the critical path or outside PRs slip") |
| 2 M | 8, 9, 10, 14, 17 | cloud_dispatch.py | serial with R11-PRE-TOKEN-LEDGER (same `_prompt`) |
| 3 M | 13, 16, 0, 1 | dispatch drain, beat rows, standing-dispatch.md stub | after part 2 and the archive ref |
| 4 M | 3, 6, 12, 2, 7 | merge drain, record_beat.py, postmerge.py, standing-merge.md stub, standing.md, orchestrator.md, CLAUDE.md | after PARALLEL-PIPELINE TRAIN-ROUTING (it rewrites standing-merge.md's serial route) |

Hot: orchestrator_tick.py also in R11-PRE-ACK-COMPLETION and R11-INTAKE-R10-RESIDUE; beat_jobs.py in TOOLCHAIN-PIN, ROUND-METRICS, PLAN-RENDER, TOKEN-LEDGER. New tracked files go on a measured closure or INERT (tests/entities.py).

**L5 decision for orchestrator_tick.py** (carries 0, 1, 2, 5, 7): no new arm, ever; it shrinks by extraction. Part 1 moves the owed-by-grace readers out. Carry 0 (NOT REVIEWABLE deferral-only versus real) and carry 1 (refusals classed by reason, ranked by critical path) are built as the dispatch drain's classes and cp-owed's rank, not as tick arms. Carry 5 is built (part 1): beatd.jobs.json class_wait_s to at least the longest class-row timeout_s; the new rows take no class lock. Carry 2 is re-measured first in part 4 (the tick's unrecorded query, :2187, against record_beat's readback); a remaining defect carries to R11-PRE-ACK-COMPLETION. Carry 7 rides the record PR of part 4's merge, which changes the seat set the HANDOVER bullet names.

## 6. Evidence, by part

- **Part 1.** Failing test: beat_jobs_selftest.py, a planted roster with one CP and one outside group fires each of the eight arms at grace 0 (fails on the base: no row); null: every step inside grace prints nothing; one mutant per arm (drop its predicate). The class_wait_s table check: 60 with a 900 class row is refused; mutant back to 60 fails. is_hotfix: kind bug without flag or name is not a hotfix (fails on base, :835). Tick self-test stays green after the move (the agreement test: old and new FIRE-OWED on the same fixture).
- **Part 2.** cloud_dispatch.py --self-test arms: no cloud role's text routes a stop to "your result"; fixer text names PREPR_SKIP_CLOSURES, in-seat body repair and CARRY-LANDED as the stop; fixer and reviewer text carry the foreground-wait rule; each fails on the base render. Null: probe text unchanged at :371. PC-07/08/09: a group with more than five carries renders with `--part`; a light-carry part of nine renders; size M with `--design-requested` renders, without it refuses (:671).
- **Part 3.** Offline drain self-test against a throwaway origin (the `_group_checks` pattern): trap 1 (relay nonce present: no second bus dispatch), trap 2 (first round: no `--reviewed-head`), trap 3 (published line 1 altered: no fire-owed); held autofix stays unmarked. Null: an all-clear queue prints nothing. Mutant per trap.
- **Part 4.** record_beat.py self-test (carries 3, 6): a post exiting 1 while the thread (gh_comment.py fetch_thread, :205) holds the record prints recorded, and `--retry` posts nothing; null: exit 1 with no such comment stays OWED. Carry 12 is on main (95a12bf027; merge_pr.sh :378-379): marked landed, no build. Merge drain: unintended close is an EXCEPTION; a moved head is not added. Re-measure after merge: local seat tokens per merge (R11-PRE-TOKEN-LEDGER) for seven days before and after. No goldens move; no claim file is touched.

## Notes for the fixer

- Carry 16's traps are acceptance cases verbatim; the prototypes are a specification, never copied with their paths. Carry: R11-PRE-STANDING-SCRIPTS
- Firing stays with a seat: RemoteTrigger is a tool call; the drain's output is fire-owed. Carry: R11-PRE-STANDING-SCRIPTS
