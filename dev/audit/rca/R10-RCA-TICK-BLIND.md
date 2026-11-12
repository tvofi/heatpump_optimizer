# R10-RCA-TICK-BLIND: the tick board was present and stalls happened anyway

Owner's question (tvofi, 2026-11-08): the tick board (`tools/audit/seat/orchestrator_tick.py`
via `tick_loop.sh`, written to the session's `tick.txt`) exists so that stalls cannot
happen, so why did these sit for hours? This file covers five cases, (a) to (e). The
orchestrator added (e) during the analysis.

Evidence base: the board written at `2026-11-08T19:11:13Z`, measured from origin/main
`996ded2a6dc5` (37 open PRs, 244 `->` lines). Also the relay, opener and tick logs in
the session state directory, the roster history on `handoff/audit-r10-roster`, git refs,
and live GitHub reads taken 19:40 to 20:45Z. Every figure below was read by a command
named beside it. Code citations are origin/main `17e621f08c`.

## 1. The five cases

### (a) Outside request #3225 (R10-COMBI-TANK) sat with no live seat

**Reproduction.** The newest COMBI-TANK seat ref before the fixer dispatch is
`handoff-body/r10-combi-tank` at 2026-11-07T10:18:37Z. The next one is
`dispatch/fixer-r10-combi-tank` at 2026-11-08T19:17:37Z, which makes **33.0 h**
(`git show -s --format=%cI` on each ref). PR 0 (#3268) merged at 2026-11-07T22:29:20Z
(`gh pr view 3268`), so for **20.8 h** after it nothing was in flight. Roster history
(`git log -S R10-COMBI-TANK` on the roster file, then `after` read per commit):

- `after: []` from append (2026-11-06T21:16Z) until `9b2b70355c`, 2026-11-08T01:53:41Z.
  That commit set `after: [R10-ADVISOR-WHATIF, R10-COP-GATE-E,
  R10-GENERIC-HEAT-CURVE-PERSISTENT]`.
- `62ecb13511`, 2026-11-08T19:25:55Z, set it back to `[]` (17.5 h blocked).

At 19:11Z the board printed `R10-COMBI-TANK: blocked by R10-ADVISOR-WHATIF,
R10-COP-GATE-E, R10-GENERIC-HEAT-CURVE-PERSISTENT (stage carries-open)` with no `->`
flag. Walking those edges, the newest seat ref per group before 19:11Z was:

| group | its PLAN line | newest seat ref | age at 19:11Z |
|---|---|---|---|
| R10-ADVISOR-WHATIF | `in progress (stage carries-open)` | handoff-body 2026-10-29T18:31Z | 240.7 h |
| R10-COP-GATE-E | `blocked by R10-HOTFIX-COP-UNMEASURED` | dispatch 2026-11-07T15:04Z | 28.1 h (`SEAT ENDED NO RETURN`) |
| R10-HOTFIX-COP-UNMEASURED | `in progress` | wip-sync 2026-11-08T10:47Z | 8.4 h; #3297 real red and DIRTY |
| R10-GENERIC-HEAT-CURVE-PERSISTENT | `blocked by R10-GENERIC-HEAT-CURVE` | none | not started |
| R10-GENERIC-HEAT-CURVE | `in progress` | handoff-wip 2026-11-08T17:38Z | 1.5 h (live) |

Two of the three blocking paths ended in a group nobody was working on. At 13:51:44Z a
comment on #3225 told the outside user that "The remaining parts are being worked on
now". No group on the chain had a live seat at that moment except
GENERIC-HEAT-CURVE's resolve.

**Cause.** `plan()` (orchestrator_tick.py, `def plan`) derives `in progress` and
`blocked by` from the roster stage and the `after` list alone. It never asks whether a
seat is on the group, or on the group's blockers. `outside_intake.py` closes the outside
obligation at `answered` ("on the roster, and a comment by OURS carrying ANSWER_MARK").
So after the answer, no line connects #3225 to a liveness check. The board has a
per-PR seat test (`_seat_on`, SEAT_WINDOW_MIN = 120), but none per group or per chain.

**State: (c).** The process ran and was obeyed: intake triaged and answered, and PLAN
printed each group. Its unit, the roster stage, cannot see a dead chain. The line said
`in progress` for a group whose last seat ref was ten days old.

### (b) 23 handoffs had no PR, and the opener's refusals never reached the board

**Reproduction.** At 19:11Z the board held 21 `handoff-no-pr` and 2 `handoff-update`
level lines (23), plus 20 `OWED handoff:` orphan lines (`orphans: 20 stranded`). The
cap `CAP_ORPHANS = 20` did not truncate on this pass: 20 of 20 printed. The opener that
ran was the session-local `s9/seat-opener/driver4.py` (pid 82190, started 2026-11-04
23:42:30). The tree's `open_driver.py` did not run. Its state directories
`$HPO_STATE_DIR/open-driver/` and the beat digest `$HPO_STATE_DIR/digest/` do not
exist (`ls`). `driver4.out` on 11-08:

- `NEEDS-TITLE/GROUP (no roster group for topic)` for every `-pN` topic, from 08:21Z on.
  driver4 maps a topic to its group by `t.upper()` only, so `r10-dispatch-at-handoff-p2`
  looks for a group `R10-DISPATCH-AT-HANDOFF-P2` that does not exist. The tree's
  `open_driver.py` `resolve()` has had P363 part-topic resolution since `20cfab74c6`
  (2026-11-02T04:52Z), and `roster_lib.group_for_branch` resolves the same pattern
  ("A phase branch `<group>-pN` ... answers for its group").
- `open_pr: REFUSE: merging origin/main into <sha> conflicts` for body-contract-p3
  (11:05, 12:02, 13:05Z), gate-busy-defer-p5 and codeql-headroom.
- `STUCK ... failed 3x; needs a repair seat`: dispatch-at-handoff-p2 13:48Z,
  fly-gh-read-retry-p3 15:41Z, codeql-headroom 17:24Z, gate-busy-defer-p5 17:28Z,
  rca-relay-handoff-starvation 18:36Z, rca-stamp-claim-conflict 19:11Z.
- driver4 silently `SKIP`s every `triage-*` topic under an owner ruling (2026-11-04).
  The board still printed all eight triage batches as `OWED handoff ... repair=opener`,
  aged 17.1 to 39.4 h, with a repair that will never run.

The board's handoff line names `open_pr.sh (opener)` as the repair, whether or not the
opener had already tried and been refused. `beat_jobs.py`'s `opener` row
(`OPENER = re.compile(r"^(?:OWED \S+ open-refused |NEEDS-TITLE |STARVED |STUCK )")`)
is the reader built to surface those refusals, but it reads `open_driver.py`'s output.
driver4 wrote its refusals to its own files.

**Cause.** A session-local opener with a weaker topic resolver ran in place of the tree
instrument that already fixed it. Its refusals went to a file no board section reads.

**State: (b).** The process existed and was not followed. `orchestrator.md` section 13
says "An instrument the programme runs is a tracked, self-tested file; a session-local
copy is a defect" and "When an instrument merges, re-check your briefs and running
seats for steps it replaces". `open_driver.py` merged on 11-02 and `beat_jobs.py` on
11-04 (`0a98a0173f`, 10:21Z), and driver4 was restarted 13 h after the latter. Because
(b) tempts "tell harder", the countermeasure below does not add an instruction. It
makes the board notice that its own opener is not running.

### (c) Verdicts for #3327 (critical path) and #3330 were refused by carry_audit false positives

**Reproduction.** The probe refs `probe/rev-3327-d37440ce` (13:23:44Z) and
`probe/rev-3330-e85597ef` (14:07:49Z) were refused finally by the relay at 13:32:37Z and
about 14:33Z (`cloud-relay.daemon.log`, `tick-loop.log`). The refusal was `bus: REFUSE:
push-verdict: 1 finding item(s) with no valid Carry: (carry_audit.py)`. They were still
OWED in `cloud-relay.log.level` at 20:43Z: **7.2 h and 6.2 h**, and growing. The 19:08Z
stamp in the brief is the level file's restamp, not the first refusal. I reproduced both
refusals with `bus.sh carry_gate`'s exact invocation (`carry_audit.py --roster-ref
origin/main check --body /dev/null --comments <verdict json>`, rc 1):

- #3327: `UNROUTED review push-verdict item 07f06569 (## Block) [non-blocking]`. The
  Block item does carry `Carry: built-here`, on an indented continuation line after a
  nested paragraph, and the parser does not attach it to the item.
- #3330: `UNROUTED ... item 8e3e097e (## Evidence) [carry]`. An Evidence line that
  *quotes* the phrase "states it as a Carry: marker" is read as a finding item.

**Class reach.** `cloud-relayed.refused-why` holds seven carry_audit refusals of review
verdicts this round: #3170, #3212 (BAD-DEST), #3274, #3278, #3310, #3327 and #3330. That
is an audit class by `defect-root-cause.md` (three or more instances in one round), so a
barrier is owed.

**Board side.** Both refusals printed every pass as one flat `-> OWED: ... probe-refused
...` line among 244 flagged lines, unranked. Nothing said that #3327 was the critical
path, that the refusal was a parser false positive, or that the repair is the reviewer's
re-push or a carry_audit fix rather than the fixer's.

**State.** The parser is (c): the check was followed and gave the wrong answer. The
board is also (c): the line printed, and its unit (an unclassed, unranked line) did not
produce action.

### (d) About 25 PRs read "NOT REVIEWABLE ... back to its fixer"; the real ones drowned

**Reproduction.** The board had 17 `NOT REVIEWABLE` lines and 20 `back to` lines in
all (the other 3 are DIRTY). Every red gate on those 17 heads was read from its job
log, the `FAIL` line, into `ev/notrev-classified.txt` in the seat's scratch:

| class | PRs | count |
|---|---|---|
| deferral-only: every red gate says `FAIL run(s) [...] at this head are still being judged; their gate decides`, and the deciding gate is green | #3245, #3291, #3317, #3337, #3343 | 5 |
| red at 19:11Z, all gates green after reruns at 19:09-19:25Z | #3325, #3330 | 2 |
| older suite's real red superseded by a newer green gate | #3326 | 1 |
| codeql cancelled (the board already prints a rerun line) | #3315, #3321, #3322 | 3 |
| real red (fork head, `tests / fast`, `pr-contract`, `budget-raise-gate`) | #3284, #3297, #3305, #3319, #3323, #3339 | 6 |

So 8 of 17 were settleable by a rerun and needed no fixer. Only 6 were the fixer's. The
board printed all 17 identically. The deferral-only reds had waited, from decider-green
to 19:11Z, 6.6 h (#3245), 0.3 h, 0.4 h, 1.7 h and 0.2 h: **9.2 h** in all.

**Cause.** `merge_train.latest_runs` keeps the worst latest gate per check suite ("an
older suite's red is never hidden behind a newer green (A5)"). That is sound only while
something re-runs a deferring gate once its decider finishes. `gate.py`'s DEFERRAL
docstring names that something: "gate-sweep.yml re-runs it when the deciding run
completes". The Gate sweep workflow is `disabled_manually`, with `updated_at`
2026-11-08T11:54:00Z and last run 12:22:30Z (`gh api .../actions/workflows`). After
that, every deferral stayed red for good. `one_pr()` prints `NOT REVIEWABLE` for any
required red, without reading why the gate failed.

**State: (d).** The process was sound, and its precondition (the sweep reruns
deferrals) was removed underneath it. The board did not notice that the workflow was
disabled.

### (e) "record beat owed" over-fires, and `postmerge.py --retry` posts duplicate #201 lines

**Reproduction.** The board line `record beat owed: state_docs.py --push + #201 comment
for cb5512741638, ... 4a9d2d54...` named ten merges, which is exactly `CAP_MERGES`.
`unrecorded()` asks `gh api --method GET search/issues -f "q=<sha40>
repo:tvofi/heatpump_optimizer type:comment"` and counts a merge unrecorded at
`total_count == 0`. Measured on two recorded merges:

| sha | `type:comment` | no qualifier | `in:comments` |
|---|---|---|---|
| cb5512741638... | 0 | 2 | 1 |
| 8a4cf2618c53... (#201 comment 6722538394) | 0 | 7 | 3 |

The qualifier makes the query return 0 for any sha, so the line fires on every pass
for the newest ten merges whatever #201 holds. It has done so since at least
2026-10-24T13:46Z: the coordinator's note in the session log reads "#201 comment
6384739224 posted for 9586fce; board ... still prints record beat owed". The 10-31
board also listed ten. The tick self-test stubs `search/issues` with a chosen count,
so the self-test passes no matter what GitHub returns. That is the "check that supplied
the value it asserted" shape `defect-root-cause.md` names.

Acting on it on 11-08 posted three duplicate #201 lines: 6726155237 (19:38:56Z, #3324),
6726174539 (19:40:41Z, #3308) and 6726198190 (19:42:50Z, #3335). #3312 already had two:
6720284987 (10:20:13Z) and 6720439444 (10:37:28Z). `postmerge.py` calls
`record_beat.record()` on every run, `--retry` included, and `record()` posts
unconditionally. Nothing checks for an existing #201 comment that carries the sha40.

**Class reach (one more line of the same shape).** `STATE` printed `HANDOVER
updated-for a7dd7f50d67e is 3883 commit(s) behind origin/main` and `run python3
tools/audit/seat/state_docs.py --push`. HANDOVER.md says "this file's `updated-for:`
line stays manual", and `state_docs.py`'s write set excludes `dev/programme/HANDOVER.md`
(its self-test, line 808). So the named repair cannot discharge the line. Together with
the eight triage handoffs in (b), that makes three board line kinds whose named repair
cannot remove them.

**State.** The search is (c): it ran every pass and is structurally unable to find a
hit. GitHub may have changed what `type:comment` means, which would make it (d), but I
could not measure past API behaviour, so I record (c). The retry is (a): no idempotence
check existed.

### The orchestrator acted on wake events, not the whole board

Measured on the 19:11Z board: of 244 `->` lines, at least 26 were false or could not
be discharged by the repair they named:

- 8 rerun-settleable NOT REVIEWABLE lines
- 15 triage-handoff lines (8 level, 7 orphan) the opener skips by ruling
- 3 STATE lines (record beat, HANDOVER, state_docs)

The real stalls, (a) to (c), were flat lines among them. This contributes to (a) to (d);
it is not a separate cause. The countermeasures below remove the false lines and rank
the true ones, which addresses it without a new instruction.

## 2. Class: a board line whose state or repair is wrong

Cases (a) to (e) share one shape: the board printed a line whose stated state (`in
progress`, `NOT REVIEWABLE: back to its fixer`, `record beat owed`) or named repair
(`open_pr.sh`, `state_docs.py --push`) did not match the world. At least seven instances
in R10: (a), (b) refusals, (b) triage, (c), (d), (e) record beat and (e) HANDOVER. That
is an audit class, so a barrier is owed. Barrier, for the owning group:

> every flagged line kind has a self-test arm in which running its named repair, in the
> fakes, removes the line, and an arm in which the repair cannot run (refused, skipped
> by ruling, precondition gone) changes the line to say so.

That turns "the repair named is the repair that works" into something the self-test
pins, and it would have caught (b) triage, (d) and both (e) lines.

## 3. Cost test

`cost(countermeasure, recurring) < cost(defect) x P(recurrence)`, in wall-clock per
occurrence. P(recurrence) is the measured class frequency: seven instances of the class
in R10 (section 2), and each of (a) to (e) recurred within the day it was found. The
NOT REVIEWABLE flood lasts as long as Gate sweep stays disabled, and the record beat
line fired on every pass for at least 15 days.

| case | cost of the defect, measured | countermeasure's standing cost | verdict |
|---|---|---|---|
| (a) | 20.8 h (33.0 h since last seat ref) on an outside user's request, plus one public status claim that was false | a walk over the roster already read each pass, plus the `_heads` refs already listed: no new API call, under 10 ms | build |
| (b) | 98.9 handoff-hours waiting on non-triage opener repairs (sum of board ages: 18.9, 21.3, 11.0, 10.7, 9.6, 8.5, 8.1, 7.5, 2.1, 1.2) | read `$HPO_STATE_DIR/open-driver/` files: local, under 5 ms | build |
| (c) | 13.4 h verdict delay (7.2 + 6.2), one on the critical path, and growing; seven in the round | classify `probe-refused` by its reason text and rank by critical path: string work, 0 API | build; the carry_audit fix is the class barrier |
| (d) | 9.2 h on five deferral-only heads; 8 of 17 lines sent to fixers who owed nothing | one job-log read per red gate, cached by job id (logs are immutable once complete): about 25 calls once, then 0 per pass | build |
| (e) | 5 duplicate #201 comments; one always-on false line for at least 15 days | the fixed query costs the same 10 calls or fewer (or one page of #201 comments); one search per postmerge | build |

Each standing cost is milliseconds or zero API calls per pass, against hours per
occurrence at a measured recurrence of one or more a day. Every row passes.

## 4. Countermeasures

None is landed here. The tick arms belong to `R10-TICK-LEVELS` (its seam is
`tools/audit/seat/orchestrator_tick.py`, stage carries-open). The parser fix belongs to
`R10-BODY-CONTRACT` (it owns `tools/audit/carry_audit.py`). Retiring the stand-in opener
belongs to `R10-FLY-STANDING-CONTRACTS` (its scope: "review the live usage of the sweep
... and fix any gaps"). `orchestrator_tick.py` is 4937 lines with structural budgets at
zero headroom, and five arms is not a small change, so each is routed as a carry. The
orchestrator asked for a new fly-in group. Measured: `carry_audit.py check` refuses
`Carry: R10-FLY-TICK-BLIND` as `BAD-DEST ... not a group of the roster`. The carries
therefore name the existing owning groups. If the roster seat appends
`R10-FLY-TICK-BLIND`, re-point the R10-TICK-LEVELS carries there.

Each check-shaped arm owes, in its own fixer's PR, a self-test arm failing on the exact
case named here and passing after, plus a null control and a mutation run
(`defect-root-cause.md`, "A detector must be shown to detect"). The fixtures are the
recorded cases: the check-run sets and FAIL lines in section 1(d), the five driver4
lines, the COMBI-TANK chain table, and the two verdict files on the probe refs.

1. **(d), state (d): NOT REVIEWABLE names its class.** Read each red gate's FAIL line
   (cached by job id). Print `NOT REVIEWABLE (deferral-only, decider <id> green):
   rerun the gate, not the fixer` for a deferral whose decider is green, and keep `back
   to its fixer` only for a real red. Add a level line `GATE SWEEP DISABLED since <utc>:
   deferrals are never rerun` when `gate-sweep.yml`'s workflow state is not `active`.
   Fails on: #3291 (two deferral reds and one green decider) and #3245. Passes: #3297
   (real `tests / fast`) still reads back to its fixer. Carry: R10-TICK-LEVELS
2. **(b), state (b): the board notices its own opener.** Each `OWED handoff` line
   carries the opener's last result from `$HPO_STATE_DIR/open-driver/`
   (`NEEDS-TITLE`, `REFUSE: merge conflicts`, `STUCK after 3`). When that directory is
   missing while handoffs are owed, print `OPENER ABSENT: open_driver.py has no state
   under $HPO_STATE_DIR -- a session-local opener is a defect (orchestrator.md 13)`. A
   topic the opener skips by ruling (`triage-*`) prints as `held by ruling`, not as
   `repair=opener`. Count every handoff line and never cap it silently. Fails on: the
   19:11Z state (no `open-driver/`, and r10-dispatch-at-handoff-p2 STUCK). Carry:
   R10-TICK-LEVELS
3. **(b): retire `driver4.py` and the other out-of-tree stand-ins for `open_driver.py`
   under `beatd.py`.** Check that no `-pN` topic reads NEEDS-TITLE. Carry:
   R10-FLY-STANDING-CONTRACTS
4. **(a), state (c): OUTSIDE-CHAIN-IDLE.** For every open group with `source: outside`,
   walk `after` edges transitively. For each blocking path whose deepest open group has
   no seat ref (handoff, handoff-wip, handoff-body, dispatch or fix) inside
   SEAT_WINDOW_MIN, print `OUTSIDE-CHAIN-IDLE <G> (#issue): <path> idle <h>` as a
   flagged line, first in its section. Fails on the 19:11Z chain (ADVISOR-WHATIF idle
   240.7 h; COP-GATE-E then HOTFIX-COP-UNMEASURED idle 8.4 h). Passes when every path
   ends in a live seat. Carry: R10-TICK-LEVELS
5. **(c), state (c): probe-refused routed by class.** Classify a `probe-refused` reason
   as `carry_audit` (the reviewer re-pushes, or the parser is fixed), `already relayed`
   or `no ev names the head`. Rank critical-path PRs first and name the owning seat.
   Fails on the #3327 and #3330 lines. Carry: R10-TICK-LEVELS
6. **(c) class barrier: carry_audit on review verdicts.** Attach an indented `Carry:`
   continuation to its item, and do not read a quoted `Carry:` phrase inside an
   Evidence line as a finding item. Pin with both verdicts (#3327 item 07f06569, #3330
   item 8e3e097e) and the other five refused verdicts. Carry: R10-BODY-CONTRACT
7. **(e), state (c): the unrecorded-merge query.** Replace `type:comment` with a read
   that can return a hit. Either read #201's comments since the oldest scanned merge
   and match sha40 locally, or use `in:comments` (measured to return hits). Replace the
   self-test's chosen count with a fixture that pins the query string. Fails on
   cb5512741638 and 8a4cf2618c53 (recorded, read as unrecorded). Also: `HANDOVER
   updated-for` behind must not name `state_docs.py --push`, which cannot write it.
   Carry: R10-TICK-LEVELS
8. **(e), state (a): `postmerge.py` / `record_beat.record()` idempotence.** Before
   posting, look for a #201 comment that carries the merge sha40, and post nothing when
   one exists, `--retry` included. Fails on #3312 (two lines) and the 19:38-19:42Z
   triple. Carry: R10-TICK-LEVELS
9. **Section 2 class barrier: a repair-discharges-line arm per flagged line kind** in
   the tick self-test. Carry: R10-TICK-LEVELS

Nothing here changes policy. Arm 2 cites `orchestrator.md` section 13 without amending it.

## 5. Not established

- The brief's "about 25 NOT REVIEWABLE" and "19:08Z" figures. The stored board shows 17
  (20 `back to` lines), and the relay refusals date from 13:32Z and 14:33Z. Earlier
  boards are not kept, so I could not count 25.
- Who disabled Gate sweep, and why. The API gives the time (11:54:00Z), not the actor.
- Whether `type:comment` ever returned hits.
