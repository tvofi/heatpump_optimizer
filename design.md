# R11-PRE-STANDING-SCRIPTS: the merge and dispatch seats as beat rows, one exception seat

Designer round 2, answering design-verdict c51f65059e (`Design review: revise d1a4ae6a74 architecture-unsound`, one point). **Base e0ad8b2bd32b60a67975039f8573dbba2207757f**; code read there (origin/main at dispatch). From round 1's base b3831ff64e only beatd.py and bus.sh move under tools/audit/seat/ (`git diff --name-only b3831ff64e e0ad8b2bd3`); every line cited below is re-pinned at e0ad8b2bd3. Predecessor R11-PRE-PARALLEL-PIPELINE still has no handoff head: its approved note (design/R11-PRE-PARALLEL-PIPELINE 22fdbabafb30, design-verdict 2d229ce672bb) is read instead. Roster: handoff/audit-r10-roster add5384763, size L, carries 0-17. Owner: card R1 2026-11-13 (scripts on the beat, one exception seat); card C8 2026-11-15 (L, design first). Evidence: process-convergence audit d5d7ff8187 section 2.2 and "What to REMOVE"; triage r10-round-end.md P752, P772, P773, P792 at 2e17928032.

**Round 2 answer (point 1, accepted in full).** Round 1 rewrote the shared setup line and tail to name handoff-wip/<topic>; both strings reach all five roles. The stop channel is now **per role, stated in each role's body**, and the shared lines name no ref: section 2 "Prompt text" and section 6 "Part 2" are rewritten, section 4's first bullet corrected. Round 1's shape would also have turned three base self-test nulls red (cloud_dispatch.py:1412, :1435, :1438); they bound the new shape. The verdict's three notes and routed decision are carried below.

**NO-READ.** Carry 16's prototype scripts live under the orchestrator's state directory and on no ref; a cloud seat cannot read them. Specified from the two standing contracts and the three written traps. **Precondition on the orchestrator, before the fixer of part 3 dispatches:** push them, paths scrubbed by ref_privacy.py, to an archive ref (decision 0013) and name it in that part's brief. Carry: R11-PRE-STANDING-SCRIPTS

## 1. Owning seams (fixer.md step 17; tests/seam_map.json names none of these files)

- **Owed-event watch (new module, tools/audit/seat/, name the fixer's):** owns the fired-ledger read, the "a seat is on it" predicate and every owed-by-grace arm. orchestrator_tick.py's payloads (FIRE-OWED, :1087-1088) and _seat_on (:857) **move** into it; the tick imports them. Beat row cp-owed in beat_jobs.py and beatd.jobs.json calls it.
- **Dispatch drain (new module):** owns turning an orchestrator dispatch line into bus records and a published payload. It calls cloud_dispatch.py (sole owner of `_prompt`, :230), bus.sh dispatch / dispatch-handoff, approve_held_runs.sh and outside_intake.py answer. Row dispatch-drain.
- **Merge drain (new module):** owns turning an orchestrator merge line into a train entry and a post-merge report. It calls `merge_train.py add`, tools/pr/preflight.sh and postmerge.py. **merge_train.py is not edited** (L5: its redesign is P754's). Row merge-drain.
- **Queue grammar:** roster_queue.py's parse_line and mark_line (`#done` / `#refused`), imported, never copied.
- **Stop channels:** each role's stop sentence lives in that role's branch of `_prompt`; the grammar it writes is owned where it is read (fix verdict: fix-review.md and cloud_relay.sh; design verdict: bus.sh push_design_verdict, :2547-2560; design note: bus.sh push_design, :2540-2546).
- **Contracts:** standing-merge.md and standing-dispatch.md become retirement stubs like standing-tick.md; standing.md becomes the **exception seat's** contract. Callers in section 4. Policy: owner review.

No concern needs two owners.

## 2. Shape

**Lines in** (the orchestrator appends; it still chooses everything):
`merge <pr> <head40> closes=<n,...|-> mandate=<id|->`; `reviewer <pr> <head40>`; `reviewer-handoff <topic> <tip40>`; `fixer|designer|design-reviewer <group> [--part k] [--design-requested <blocked-ref>]`; `answer <issue>`.

**Lines out**, one digest per row under S/digest/jobs/: today's report grammar unchanged (`merged #<n> <sha> closed <issues>`, `parked #<n> <reason>`, `set-stage owed`, `fire-owed <ref>`), plus `EXCEPTION <row> <key> <class>: <refusal tail>`. Classes are fixed tokens: head-moved, autofix-hold, not-reviewable-real, not-reviewable-deferral, refused-<tool>, seat-stopped, unintended-close, owed-record, unreadable. A held line stays unmarked and is retried next pass; it becomes an EXCEPTION only past its grace.

```
orchestrator --line--> queue file --row pass--> drain
  dispatch-drain: re-read head == line head? -> approve_held_runs -> autofix hold
     -> classify (merge_train.py classify): RED real -> EXCEPTION; deferral-only -> hold
     -> bus.sh dispatch [--nonce relay's] [--reviewed-head only if a prior verdict]
     -> cloud_dispatch.py --publish -> read dispatch ref: prompt line 1 == rendered? -> fire-owed <ref>
  merge-drain: head == line head, verdict posted (merge_train.py posted-verdict) -> preflight over body
     -> merge_train.py add -> (on merge) postmerge.py -> closed set == closes= ? else EXCEPTION
cp-owed: roster_lib.is_outside(g) or g in critical_path_read(...) -> CP-OWED lines past grace
seat stop (any role) -> that role's own return ref -> its existing reader -> EXCEPTION ... seat-stopped
exception seat: reads EXCEPTION and fire-owed lines; fires (RemoteTrigger is a tool call); answers or routes
```

**Invariants.** K1: no script chooses what merges or dispatches. K2: one bus dispatch per (pr, head); a relay-minted nonce is passed with `--nonce`, never re-minted (trap 1). K3: `--reviewed-head` only when a verdict for the PR exists (trap 2). K4: nothing is fire-owed until the published prompt's line 1 equals the rendered one (trap 3). K5: a drain never retries past a refusal; it marks `#refused` and prints EXCEPTION. **K6: a role's stop is written only to a ref that role may already push, in a grammar that ref's reader already parses or refuses; no role's text names another role's ref.**

**cp-owed** (carry 4, verbatim arms and graces): PR arms merge-verdict-no-approval 10 min, approved-unmerged 45, blocked-no-fire 15, head-no-dispatch 25; group arms UNFIRED, DESIGN-REVIEW OWED 10, FIXER-OWED, SEAT-SILENT 90. SEAT-SILENT keys on the return ref's absence, never on a session's status (carry 17). It is also the backstop for a seat whose stop push itself refuses. DESIGN-REVIEW OWED counts a design-verdict of class seat-refused as no review. Ranked critical path, then outside, then hotfix (roster_lib.is_hotfix narrowed to the flag or the name: carry 11, :828-835).

**Prompt text** (cloud_dispatch.py `_prompt`; carries 8, 9, 10, 17). Shared lines, all roles: the setup REFUSE (:238) reads "stop by your role's stop channel, stated below"; the tail (:377-378) reads "never work around a hook or a refusal; stop by your role's stop channel". Neither names a ref. Per-role channel, in the role's body:

| role | stop channel (the role's own return ref) | reader today | change |
|---|---|---|---|
| fixer | BLOCKED.md on handoff-wip/<topic>, code or no code, holding the refusing command and its last lines (:332 widens from "a question" to every stop; :338 CARRY-LANDED stays) | cloud_relay.sh fold arm; the tick's handoff-wip read | text only |
| reviewer | `Fix review: blocked <head> seat-refused: <line>` on its probe ref (:316-320) | cloud_relay.sh | none |
| designer | a design.md whose first line is `Design blocked: <the refusing line>`, pushed by `bus.sh push-design` onto design/<topic> (push_design admits any non-empty note) | design_approved (:599-610) already refuses the fixer on an unapproved tip | the design-reviewer route (:672-675) refuses a tip whose line 1 is that form, so the dispatch drain marks `#refused` and prints EXCEPTION seat-stopped |
| design reviewer | `Design review: revise <design> seat-refused` by `bus.sh push-design-verdict` (grammar `[a-z-]+` admits it, :2553) | :677-683, round_context (:581) | a seat-refused verdict is **not a round**: the designer route refuses on it ("re-dispatch the design reviewer"), and the round count (:683, rev-list --count) excludes commits whose subject ends ` seat-refused` (the subject carries the first line, :2559) |
| probe | its result body by body_push.sh (:371): a stop is a result holding the refusing command and its last lines | the relay's handoff-body read | one sentence added |

The designer's line holds neither "BLOCKED.md" nor the step-ref namespace, so :1435 and :1438 hold unedited. :1412's null is re-keyed from the bare token seat-refused to the reviewer's sentence (`Fix review: blocked` with its probe ref), because the design reviewer now carries the token in its own grammar; the part says so in the check's label.
Rest of the text: fixer names in-seat repair of every body_push.sh refusal but CARRY-LANDED (exit 4), and PREPR_SKIP_CLOSURES with a Friction line; fixer and reviewer: wait in the foreground, bounded, never end a turn on a wait handed to a background task or subagent (heavy work may still run in the background; :239-240 reworded, not removed). WAIT_LINE's 240 s (:134) stays unless the fixer reproduces carry 17's exit 137 under it.
**CLI** (carry 14): `--part` with `--group` renders a This-part line on the flag path (PC-07; at the base the refusal is :1572); PC-08 weighs a light text carry at one fifth of PART_CARRIES (:520), the rule stated in fixer.md; PC-09: `--design-requested <ref>` admits a design role on size M when the ref holds a BLOCKED.md naming a design departure (the refusal at :670-671; roster_lib.needs_design unchanged).

## 3. Alternatives, and why they lost

1. **One Workflow script per group** (PC-1113-06, carry 15). Lost: it moves the coordination tokens rather than removing them, and keeps no state across beat restarts. Still DEFERred. Carry: R11-PRE-TOKEN-LEDGER
2. **New arms in orchestrator_tick.py.** Lost: L5; and the tick is read-only by contract, so drains could not live there.
3. **Drain subcommands in cloud_dispatch.py / merge_train.py.** Lost: other groups' hot files, merge_train.py L5-frozen; a renderer owning queue state couples two concerns.
4. **Keep a haiku dispatch seat with a shorter contract.** Lost: its tokens are the measured problem; every step is a fixed command sequence.
5. **One stop ref for every role** (round 1: handoff-wip/<topic>; or a new stop/<topic> family). Lost: for the design roles <topic> is the group's, so the first writes onto the fixer's step ref and contradicts "You may push only to that ref" (:349, :364); a new family needs a new push licence in four bodies, a new bus verb and a new reader, where each role's own ref already has all three.

## 4. Sibling sites (enumerated)

- `git grep -n "your result" -- tools/audit/seat/`: :238, :378 change; :371 keeps its meaning (the probe's result channel). **The probe render is not byte-unchanged**: it carries :238 and the tail.
- `git grep -n "seat-refused\|BLOCKED.md\|WIP_NS" -- tools/audit/seat/cloud_dispatch.py`: every self-test null over a stop token (:1403, :1412, :1435, :1438) is kept or re-keyed as section 2 says.
- `git grep -ln "standing-merge\|standing-dispatch" -- . ':!.cursor' ':!.claude/rules'`: live policy and instruments change (CLAUDE.md, orchestrator.md, standing.md, INSTRUMENTS.md, sweep_template.md, dev/audit/README.md, tests/entities.py, scorecard_selftest.py, policy_budgets.json, closures.json via derive); triage, rca, PLAN-TABLE and the r10 roster are records, out of scope.
- `git grep -n "FIRE_GRACE_MIN\|_seat_on\|_fired(" tools/audit/seat/`: every caller moves to the watch module in one change.

## 5. Parts, serial position, hot files

| part | carries | files | position |
|---|---|---|---|
| 1 | 4, 5, 11 | watch module, beat_jobs.py, beat_jobs_selftest.py, beatd.jobs.json, roster_lib.py, orchestrator_tick.py (move only) | first; touches no day-1 file of PARALLEL-PIPELINE; beatd.jobs.json serialises against R11-PRE-TOOLCHAIN-PIN |
| 2 M | 8, 9, 10, 14, 17 | cloud_dispatch.py | serial with R11-PRE-TOKEN-LEDGER (same `_prompt`) |
| 3 M | 13, 16, 0, 1 | dispatch drain, beat rows, standing-dispatch.md stub | after part 2 and the archive ref |
| 4 M | 3, 6, 12, 2, 7 | merge drain, record_beat.py, postmerge.py, standing-merge.md stub, standing.md, orchestrator.md, CLAUDE.md | after PARALLEL-PIPELINE TRAIN-ROUTING (it rewrites standing-merge.md's serial route) |

decision: orchestrator (routed by the verdict): part 1 is S or M. If cut, 1a is the watch module, the move and the cp-owed row; 1b is class_wait_s and is_hotfix.
Hot: orchestrator_tick.py also in R11-PRE-ACK-COMPLETION and R11-INTAKE-R10-RESIDUE (R11-PRE-SHARED-FILES cites its :4144 only); beat_jobs.py in TOOLCHAIN-PIN, ROUND-METRICS, PLAN-RENDER, TOKEN-LEDGER. New tracked files go on a measured closure or INERT (tests/entities.py).

**L5 decision for orchestrator_tick.py** (carries 0, 1, 2, 5, 7): no new arm, ever; it shrinks by extraction. Carries 0 and 1 are built as the dispatch drain's classes and cp-owed's rank. Carry 5 is built in part 1 (beatd.jobs.json line 3; the new rows take no class lock). Carry 2 is re-measured first in part 4 (the tick's unrecorded query, :2187, against record_beat's readback); a remaining defect carries to R11-PRE-ACK-COMPLETION. Carry 7 rides part 4's record PR.

## 6. Evidence, by part

- **Part 1.** Failing test: beat_jobs_selftest.py, a planted roster with one CP and one outside group fires each of the eight arms at grace 0 (fails on the base: no row); null: every step inside grace prints nothing; one mutant per arm. A design-verdict of class seat-refused keeps DESIGN-REVIEW OWED firing (null: class-open does not). class_wait_s table check: 60 with a 900 class row is refused; mutant back to 60 fails. is_hotfix: kind bug without flag or name is not a hotfix (fails on base). Agreement test: old and new FIRE-OWED on one fixture.
- **Part 2.** cloud_dispatch.py --self-test, over the five rendered roles (the `prompts` map the base arms already build):
  (a) no role's text holds "as your result" or "in your result" (fails on the base: :238 in all five, :378 in all five);
  (b) per role, the stop sentence names that role's return ref and no other role's: fixer handoff-wip/<topic>; reviewer its probe ref; designer design/<topic> with the `Design blocked:` line; design reviewer design-verdict/<topic> with the seat-refused class; probe handoff-body/<topic>. Each fails on the base except the reviewer's, which is the arm's positive control;
  (c) the shared setup and tail lines are byte-identical across the five roles apart from the identity pin and name no ref (regex over `refs/heads/`), which is the mutant target for round 1's shape: naming handoff-wip in the tail turns (c), :1435's and :1438's nulls red;
  (d) null control: the probe still returns by body_push.sh at handoff-body/<topic> (the :371 sentence present, unchanged); the check's label states that the probe render is not byte-equal to the base because the two shared lines changed under it (carry 10's "or the test says why");
  (e) consumers: a design tip whose line 1 is `Design blocked:` refuses the design-reviewer route; a seat-refused design verdict refuses the designer route and leaves the round number unchanged (throwaway origin, the pattern at :861-878); nulls: an ordinary note dispatches, a class-open revise counts a round;
  (f) fixer text names PREPR_SKIP_CLOSURES, in-seat body repair and CARRY-LANDED as the stop; fixer and reviewer carry the new foreground-wait sentence; each fails on the base. PC-07/08/09: a group over five carries renders with `--part`; a light-carry part of nine renders; size M with `--design-requested` renders, without it refuses.
  Mutants: one per channel row (drop the role's stop sentence), one for (c), one per consumer in (e).
- **Part 3.** Offline drain self-test against a throwaway origin: trap 1 (relay nonce present: no second bus dispatch), trap 2 (first round: no `--reviewed-head`), trap 3 (published line 1 altered: no fire-owed); held autofix stays unmarked; a refused design-reviewer line prints EXCEPTION seat-stopped. Null: an all-clear queue prints nothing. Mutant per trap.
- **Part 4.** record_beat.py self-test (carries 3, 6): a post exiting 1 while the thread (gh_comment.py fetch_thread, :205) holds the record prints recorded, and `--retry` posts nothing; null: exit 1 with no such comment stays OWED. Carry 12 is on main (merge_pr.sh:379, self-tested :304, :310): marked landed, no build. Merge drain: unintended close is an EXCEPTION; a moved head is not added. Re-measure after merge: local seat tokens per merge (R11-PRE-TOKEN-LEDGER), seven days before and after. No goldens move; no claim file is touched.

## Notes for the fixer

- Carry 16's traps are acceptance cases verbatim; the prototypes are a specification, never copied with their paths. Carry: R11-PRE-STANDING-SCRIPTS (item d-traps)
- Firing stays with a seat: RemoteTrigger is a tool call; the drain's output is fire-owed. Carry: R11-PRE-STANDING-SCRIPTS (item d-fire)
- Part 2: carry 9's premise "no match for foreground|background" is stale: :239-240 and the reviewer body (:317, pinned at :1403) already say "background". The arm keys on the new foreground-wait sentence, or the reviewer arm passes on the base. Carry: R11-PRE-STANDING-SCRIPTS (item dr1-wait-premise)
- Part 1: beatd.jobs.json is hot with R11-PRE-TOOLCHAIN-PIN's promote row; serialise. Carry: R11-PRE-STANDING-SCRIPTS (item dr1-beatd-jobs-hot)
- Parts 3, 4: each stub contract keeps citing `standing.md`, or tests/entities.py:42646-42650 is edited in the part that writes the stub. Carry: R11-PRE-STANDING-SCRIPTS (item dr1-stub-citation)
- Part 2: a designer or design reviewer whose bus.sh push itself refuses (append_commit runs ref_privacy.py under python3, bus.sh:492) has no second channel by design; SEAT-SILENT is the backstop, and the text must not invent a raw `git push` for those two roles. Carry: R11-PRE-STANDING-SCRIPTS (item dr2-push-refused)
