# R10-RCA-OWED-UNACTIONED: tick owed lines that stood for hours with no action

This is a root-cause seat. It follows `root-cause.md` (under
`dev/governance/roles/`) and `dev/governance/rules/defect-root-cause.md`. It
ran at `origin/main` `beb570c8` on 2026-10-28, from 19:02Z. The trigger was
recurrence: the owner corrected this class on 2026-10-28 at 19:00Z ("no pr
should wait without reason, in particular not CP prs").

Evidence lives in `dev/audit/rca/owed-unactioned/`. The session inputs are
outside the tree, so each script takes them as arguments:

- `replay.py <orch-sweep.log> <checkout> [--acked]` replays the night's sweep
  boards. Its outputs are `replay_out.tsv` and `replay_acked_out.tsv`.
- `live.sh <checkout> <ack files>` runs the two live boards of today, which are
  saved in `boards/`. Its output is `live_out.txt`.
- `mutants.py <checkout>` plants ten mutants in the tool. Its output is
  `mutants_out.tsv`.

## 1. The defect, reproduced

The tick (`orchestrator_tick.py`) prints its owed lines on every pass. Its
`ledger.escalate` adds `DISPATCH:` lines at 4 h and `OWNER FLAG:` lines at
12 h. Both thresholds are the owner's ruling of 2026-10-21. The lines were
printed, and they still stood. Times below come from git, the obligations
ledger and the orchestrator's queue (`ORCH-QUEUE.md`).

| obligation | complete at | what was done | effective action | standing, host up |
|---|---|---|---|---|
| `triage-s7-batch49` (handoff + body) | 10:38:12Z | 10:55Z routed to the opener seat. The opener first ran at 17:36:08Z and refused `BAD-DEST`. At 17:39Z the queue recorded a wait on RCA-HEADMOVED, whose PR #2909 had merged at 16:41:53Z. | 19:09Z, after the owner's 19:00Z correction | 5.7 h |
| `r10-review-carry` (handoff + body) | 10:44:11Z | 11:00Z routed to the opener. It ran at 17:16:39Z and was refused (`app_approve.sh` conflict). At 17:39Z "re-cut owed" was recorded, and no fixer started. | 19:09Z | 5.6 h |
| `r10-orch-beatd`, `repair=review`, **critical-path #2916** | 17:17:21Z (`c991d64c`) | The relay printed `HELD-REVIEW #2916 ... list #2916 in cloud-handoff-release` on all 33 of its passes in the log. At 19:00Z the queue recorded "Relay updates #2916 -> then review", which was false: the relay was holding it. | 19:09Z | 1.9 h |

The host was down from 12:42Z to 15:32Z (power loss, `ORCH-QUEUE.md` 15:45Z).
That 2.83 h is taken out of the standing figures.

The same shape appears on the night of 2026-10-28, in the session board's own
log (`orch-sweep.log`, 31 sweeps, 00:27Z to 05:56Z). `triage-s6-batch40` stood
on all 31 sweeps, aging from 4.8 h to 10.2 h, and was disposed at 08:58Z.
`r10-learner-default` stood on 28 sweeps, aging from 4.6 h to 9.6 h, and got a
fixer at 08:38Z. `r10-cop-partload` `54437ac8` stood on 23 sweeps, aging from
0.8 h to 4.8 h.

## 2. The cause

**Nothing in the sweep carries owed state as a result, so the sweep can report
done while an owed line stands. It also checks a handled line no more than an
unhandled one.** Three mechanisms make this up, each measured:

1. **The board's exit code ignores owed lines.** `orch_sweep.sh`, the session
   copy of the sweep board, sets `rc=1` only for a dead loop, a dead seat, a
   stale tick or beat, or a red train. Its owed block comes last: on average
   it starts at line 56 of a 65-line board (`orch-sweep.log`, 32 blocks). It
   is `grep -E '^-> (OWED|REVIEW OWED)' | tail -8 | cut -c1-170`. On the
   19:04Z board that shows 8 of the 26 owed-family lines. It never shows a
   `DISPATCH:`, `OWNER FLAG:` or `DESIGN-BUILD:` line, so the tick's own age
   escalation never reaches it.
2. **The orchestrator's ad-hoc filters removed the block, and nothing
   signalled it.** The orchestrator read the board 19 times between 10:40Z and
   18:55Z (Bash `tool_use` records in the session transcript):
   - 11 reads were `orch_sweep.sh 2>&1 | grep -v '^ ok' | sed -n '1,/verdict refs/p' | head -40`.
     That pipeline stops before the owed block by construction.
   - 1 read was `sed -n '1,/-- pull requests/p'`.
   - 2 reads were `grep -E` patterns that have no `OWED` alternative.
   - 1 read was a bare `head -40`.
   - 4 reads could show the block: one `tail -60`, and three `grep ... OWED ... | head`.

   So 15 of 19 reads did not display the block. Since `rc` ignored it, the
   reads did not look any different.
3. **A recorded action is never re-checked.** Each of today's three lines had
   an action written against it: a routing at 10:55Z and 11:00Z, a named wait
   at 17:39Z, and a belief at 19:00Z. Each action then failed: the opener did
   not run for 6.3 h, the wait's precondition had already cleared, and the
   relay held the update. The line printed exactly as it had before the
   action. No instrument ages an action, so "handled once" and "handled" read
   the same.

**Contributing: standing noise from a split ledger home.** The standing relay
runs `cloud_relay.sh pass --log <r10s6>/cloud-relay.log`. `cloud_relay.sh
dispose` wrote the session's dispositions there:
- `roster-b24-wip` and `triage-s6-batch40` at 08:58Z;
- `r10-handoff-bodies` at 09:12Z.

`tick_loop.sh` was started without `HPO_STATE_DIR`. Its own relay pass and
the tick therefore use `~/.local/state/hpo`, whose `dispositions.tsv` (last
written 2026-10-27T11:28Z) holds none of them. `ledger.py level`, run against
the relay's home, prints `disposed=2` for `roster-b24-wip` and
`r10-handoff-bodies`. On the tick's board, those two still print `DISPATCH:`
and `OWNER FLAG:` at 31.2 h and 18.3 h. On the morning's board the
orchestrator wrote that the tick's lines for these refs were known. A board
that always carries known-stale `OWNER FLAG` lines teaches its reader to skip
them.

## 3. Process state: (c)

The process existed and was followed:
- the tick's level-triggered owed lines (after the 2026-10-18 edge-trigger
  miss);
- the aging escalation (2026-10-21);
- `sweep_template.md` step (5), "act on the newest actionable lines";
- the standing instruction to act on every owed line in the turn. The
  orchestrator's memory recorded it on 2026-10-18, 10-22, 10-24 (twice) and
  10-28.

The sweep ran every 10 to 15 minutes, with 19 board reads in the window
above, and actions were recorded against all three lines. It did not produce
the result because its unit, the board read, cannot tell the three cases
apart: a standing line, a handled line and a line whose handling failed. The
board's exit code says nothing about any of them.

This is not (b). Three firmer instructions were written in eight days, and the
class recurred after each. That is the pattern `root-cause.md` section 2
warns of: an instruction that was obeyed, and wrong. It is not (a), because
the tick-side signal and its escalation exist. The countermeasure therefore
changes the unit, so that a sweep's result carries the owed state and a
handled line returns after a bounded time.

## 4. How far the class reaches

- **Hidden owed builds.** `DESIGN-BUILD: R10-CONFIGFLOW-PAGES` and
  `DESIGN-BUILD: R10-UX-HEALTH` are on the board: approved designs with no
  build dispatched. The session board's owed grep omits that prefix, so it
  has never shown them. Their age is not measured here.
- **Hidden reviews.** `REVIEW OWED: #2887` and `#2896` sit above the `tail -8`
  cut on the 19:04Z board.
- **Split ledger home.** See section 2. Session configuration: the tick
  restart line in `sweep_mech.sh` (`loop tick ... tick_loop.sh`) needs
  `HPO_STATE_DIR` set to the relay log's directory, or else the standing
  relay must drop `--log`. The orchestrator owes that line. It is not in the
  tree.
- **Open PRs with no owed line.** #2919, #2917 and #2906 stood with no
  handoff, so no owed line exists for them. That half is triage proposal
  **V179** (tick per-PR reconciliation) and is not duplicated here.
- **Same shape elsewhere in the tree.** `orchestrator_tick.py`'s docstring
  states "the list is a report, not a gate", and it always exits 0.
  `ledger.py board` exits 1 when obligations exist, but nothing in the sweep
  reads that code. `pulse.py` is the sweep's other liveness reader. It names
  waiting consumers, and step (5) already makes its `UNREADABLE` not clean.
  No other sweep instrument folds owed state into a result.

## 5. Cost test

    cost(countermeasure, recurring) < cost(defect) x P(recurrence)

Both sides are wall-clock per day.

- **cost(defect).** Today's three instances left 13.2 h of owed work idle
  while the host was up (5.7 + 5.6 + 1.9). The 1.9 h are on the critical
  path, so the round's closure moves by up to 1.9 h: #2916's review cannot
  start before its held update lands. The night's three instances are each
  at least 4 h in the log alone.
- **P(recurrence).** Measured, not estimated. Six instances stood past the
  owner's 4 h threshold in about 11.4 host-up hours of observed sweeps: the
  night log's 5.5 h, plus today's 10:38Z to 12:42Z and 15:32Z to 19:09Z. Six
  owner corrections of the class are recorded on four days between
  2026-10-18 and 2026-10-28. So P per day is 1.
- **cost(countermeasure, recurring).**
  - Runtime: 0.08 s per sweep, measured five times on the 19:04Z board with
    the session's 750 KB of queue and ledger as acknowledgement files.
  - Acknowledgement load: the night replay holds a mean of 5.6 unactioned
    keys per sweep (`replay_out.tsv`). At one 1 h acknowledgement per
    standing key and about 30 s per line, that is at most 2.8 min/h, or
    67 min/day, if nothing is ever discharged. That time is the re-check the
    defect lacked; it is not overhead on top of it. A parked line can carry
    `ttl=12`.
- **Verdict.** 67 min/day at most, against at least 1.9 h/day on the critical
  path alone and 13.2 h/day of idle owed work. **Build.**

## 6. The countermeasure: `tools/audit/seat/owed_unactioned.py`

The state it addresses is (c): it changes the unit from a board read to a
result.

- It reads the tick's **whole** owed family: `-> OWED…`, `REVIEW OWED:`,
  `DISPATCH:`, `OWNER FLAG:` and `DESIGN-BUILD:`. It keys each line on its
  topic or `#<pr>`, so the four lines `r10-review-carry` prints are one
  obligation.
- A state file counts the sweeps each key has stood on. A sweep is a distinct
  board, by provenance time, so re-reading the same board adds nothing.
- At 2 sweeps, a key is **UNACTIONED** unless an acknowledgement covers it. An
  acknowledgement is a live `OWED-ACK <UTC> <key> <id> [ttl=<h>] <reason>`
  line whose id prefixes a sha the key carries now. A new tip therefore needs
  a new acknowledgement.
- An acknowledgement lapses after its ttl: 1 h by default, 12 h at most. The
  most recent handling of a line is therefore always re-checked within 12 h.
  Free text in a queue covers nothing; that is exactly the 10:55Z and 17:39Z
  routing lines.
- Exit 1 prints the block, oldest first, each entry with a ready ack line.
- Exit 2 means it cannot say: no provenance line, a board older than 20 min,
  an owed line it cannot key, or an unreadable state file. It never exits 0
  in that case.

`sweep_template.md` step (5) now runs it on every sweep, and the sweep is not
done while it exits 1. Its `INSTRUMENTS.md` entry is beside the others.

### Demonstration

- **It fires on today's case.** `live_out.txt` reads the 19:04Z and 19:12Z
  boards against one fresh state, with the session's real `ORCH-QUEUE.md` and
  `seat-ledger.md` as acknowledgement files. Both hold 0 `OWED-ACK` lines.
  The first board exits 0, because all 12 keys are new. The second exits 1
  with all 12 UNACTIONED, including:
  - `r10-orch-beatd` (its `handoff-held #2916 REVIEW` line and its
    `repair=review` line, as one entry);
  - `triage-s7-batch49` and `r10-review-carry`, with their `DISPATCH:` lines;
  - both `DESIGN-BUILD` lines.
- **It fires on the night's case.** `replay_out.tsv` replays the 31 night
  boards. The first exits 0, and the other 30 exit 1. `triage-s6-batch40`
  and `r10-learner-default` are each UNACTIONED from their own second sweep,
  11 minutes after first sight. On the session board they stood for 5 h, and
  the board's `rc` never moved for them.
- **Null controls.**
  - `replay_acked_out.tsv` re-takes an acknowledgement for every key on every
    sweep: 31 of 31 boards exit 0.
  - In `live_out.txt`, acknowledging all 12 keys at 19:13Z makes the 19:12Z
    board exit 0.
  - The self-test's all-clear board exits 0 with 0 keys.
- **It is not green by skipping.** These self-test arms each exit 2: a board
  with no provenance line, a 45-minute-old board, an owed line it cannot key,
  and a corrupt state file. A future, over-long or malformed acknowledgement
  is refused and covers nothing.
- **Mutation proof.** `mutants_out.tsv` plants 10 mutants, one per predicate
  above, and the self-test kills all 10. The self-test runs 21 checks
  offline.

## 7. Owed by others; not built here

- **The session board, `orch_sweep.sh`.** It is not in the tree; the
  orchestrator applies this. Print the tool's output first, directly under
  the `== SWEEP` line, so that any `head` filter keeps it. Fold the tool's
  exit code into `rc`. Delete the `-- owed (tick)` grep, which is the
  `tail -8` view. The pull-request body carries the exact lines.
- **The split ledger home** (section 4). This is session configuration, owned
  by the orchestrator.
- **V179.** Open pull requests with no owed line are triage's.
- **Not proposed: a fourth memory instruction.** Section 3 explains why.
- **Policy.** None of it changes. `sweep_template.md` is a usage guide by its
  own header, and `INSTRUMENTS.md` adds no obligation.
