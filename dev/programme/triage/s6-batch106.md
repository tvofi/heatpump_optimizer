# Proposal triage, session s10, batch 106 (P363)

The rolling batch after batch 105. Facts were read at origin/main `c88d552c7`, at the round's
roster branch `origin/handoff/audit-r10-roster` (`41268f418`), in the session-local opener's log
and title-override file, and in the session's seat ledger.

## P363: the opener maps a part topic to no roster group

Verdict: ACCEPT, narrowed, as one carry amending rule (3) of P337's open driver. P337 and P350,
the two rulings that specify that driver, are re-routed verbatim with it to R10-OPENER-REUSE,
because their only copies sit on a group whose stage is `done`.

Source: the orchestrator s10's queue line of 2026-11-01T19:35:45Z ("PROPOSAL P363"): resolve a
topic to its group by stripping a trailing `-p<N>` / `-<N>` part suffix and checking the roster,
and take the title from the body's first line.

Instances:
- **The mechanism, read from the session-local opener (not in the tree).** Without a title
  override, the group is the uppercased topic; when that is not a roster group the opener logs
  `NEEDS-TITLE/GROUP (no roster group for topic)` and opens nothing. Every part topic misses.
- **Its log, 2026-10-31T17:36:42Z to 2026-11-01T19:27Z: 69 `RESULT` lines and 7 `NEEDS-TITLE`
  lines.** Three of the seven are part topics: `r10-fly-train-defaults-p2` (01:09Z),
  `r10-roster-ops-2-p1` (19:08Z) and `r10-sav-comfort-p2` (19:21Z). The other four
  (`r10-record-s9-owed`, `r10-rca-roster-sync-orphans`, `audit-r10-roster-land-s9`, and
  `r10-plan-real-durations` at 14:26Z) are not part topics and this rule leaves them as they are.
- **The title-override file holds 10 entries; one more is a part topic, `r10-ux-health-p3`.**
- **The critical-path cost.** `r10-sav-comfort-p2` is the critical-path head. It logged
  NEEDS-TITLE at 19:21Z and was opened by hand at 19:35Z, per the proposal line: 14 minutes.
- **One more is due.** The ledger line of 19:31:49Z dispatches the R10-PREPR-CAP part 2 fixer
  under the topic `r10-prepr-cap-2`; `R10-PREPR-CAP-2` is not a roster group, so its handoff will
  log NEEDS-TITLE under today's rule.
- **Suffix names that are real groups.** On roster `41268f418`, five group names end in such a
  suffix: R10-CI-LAYOUT-P1, R10-CI-LAYOUT-P2, R10-ROSTER-OPS-2, R10-STALE-PATHS-2 and
  R10-TICK-DRIVERS-2. So an exact match must come first, or `r10-roster-ops-2` would open against
  R10-ROSTER-OPS.
- **The body's first line as a title.** Of the three part bodies read, `r10-sav-comfort-p2`'s
  first line is a usable title ("R10-SAV-COMFORT part 2: ..."). `r10-roster-ops-2-p1`'s first line
  is a sentence of over 200 characters beginning "Adds the roster's two missing field-writing
  ops". So that half of the proposal is not taken.
- **Where the driver is specified.** P337 (`s6-batch94.md#P337`) and P350
  (`s6-batch96.md#P350`) are R10-FLY-OPENPR-ATOMIC carries 9 and 10. That group's stage is `done`
  (queue: `set-stage R10-FLY-OPENPR-ATOMIC done --at-sha 437f1ba9b`). The fold note under that op
  says carry 9 "is R10-FLY-STANDING-CONTRACTS carry 6" and carries 1-8 and 10 were answered by
  #2858 and #2989. On roster `41268f418` neither text is on any other group: a 100-character
  slice of each matches only R10-FLY-OPENPR-ATOMIC. R10-FLY-STANDING-CONTRACTS carry 6 is a
  different re-route (R10-ORCH-BEATD, P103). Its carry 20 names "the opener carry b94-P337" only
  by reference. And #2989 merged on 2026-10-30, before P350 was ruled on 2026-10-31. So neither
  driver ruling has a group that will build it.

Cost:
- **Size.** About 15 lines in the open driver P337 adds: an ordered lookup of three candidates
  plus a body check. Four rows, two nulls and one mutant in that driver's existing fixtures. No new
  file and no new check beyond P337's own.
- **Capped files.** `grep -ln 'open_pr\|opener' tests/*_budgets.json` prints nothing.
- **Hot files.** `tools/audit/seat/open_pr.sh` is not in `review_packet.py`'s `HOT_FILES`, and
  the driver P337 adds is a new file.
- **The re-route.** R10-OPENER-REUSE is `not-started`, has no `after`, and owns `open_pr.sh`, the
  script the driver launches. It already holds the opener's retry carry (carry 5) and, queued from
  batch 105, P362. Moving P337, P350 and P363 there adds a new script to a group sized M. The
  orchestrator may want to split it into parts; that is a dispatch choice, not this ruling's.

Binding:
- **Why it clears the bar.** Every part handoff costs an orchestrator turn to write an override
  and holds its PR until that turn comes. Part PRs are now routine (four in 26 hours, a fifth
  dispatched). The rule costs a few lines inside a driver that is already accepted, and the
  exact-first order plus the body check keep it from opening against the wrong group.
- **Narrowed.** The bare `-<N>` strip is taken only behind the exact match and the body check.
  The title from the body's first line is rejected, as above.
- **The stand-in.** The session-local opener can take the same lookup today: it is session
  configuration, and editing it is the orchestrator's operational call. The `r10-prepr-cap-2`
  handoff otherwise needs a title-override entry.
- **Why the re-route.** An accepted ruling whose only copy is on a `done` group is never
  dispatched. R10-OPENER-REUSE over R10-FLY-STANDING-CONTRACTS: the latter waits on a designer, a
  design review and the owner's approval of policy files, and its files are role contracts. Its
  carry 20 keeps the judgement row for the opener loop, which still names the P337 build.

Carry (R10-OPENER-REUSE, `s7/carries/b106-P363.txt`):

> From triage P363 (orchestrator s10, 2026-11-01T19:35:45Z: the critical-path head
> r10-sav-comfort-p2 sat unopened 19:21Z to 19:35Z). P363 amends rule (3) of P337's open driver
> (`s6-batch94.md#P337`, re-routed to this group by the same batch). Rule (3) maps a topic to its
> group only as the uppercased topic, so every part topic logs NEEDS-TITLE and waits for a
> hand-written title override. In the session-local opener's log (2026-10-31T17:36Z to
> 2026-11-01T19:27Z, 69 RESULT lines) that happened to r10-fly-train-defaults-p2,
> r10-roster-ops-2-p1 and r10-sav-comfort-p2, and r10-ux-health-p3 needed an override;
> r10-prepr-cap-2 is dispatched under the same shape. Change: resolve a topic to a group in this
> order, each candidate checked against the round roster: (i) the uppercased topic itself; (ii)
> with one trailing `-p<N>` removed; (iii) with one trailing `-<N>` removed. Exact match always
> wins, because R10-ROSTER-OPS-2, R10-CI-LAYOUT-P1 and R10-CI-LAYOUT-P2 are groups whose names end
> in such a suffix. A stripped match (ii or iii) opens only when the first three lines of the
> handoff body name that group as a whole name (R10-ROSTER-OPS-3 does not name R10-ROSTER-OPS);
> otherwise it logs NEEDS-TITLE as today, so a topic for a group not yet on the roster never opens
> against its namesake prefix. The title stays generated (`<GROUP> (part <N>): <topic words>`);
> the body's first line is not used, since r10-roster-ops-2-p1's is a 200-character sentence.
> Rows: r10-sav-comfort-p2 resolves to R10-SAV-COMFORT; r10-roster-ops-2-p1 to R10-ROSTER-OPS-2;
> r10-prepr-cap-2 to R10-PREPR-CAP; r10-roster-ops-2 stays R10-ROSTER-OPS-2. Null controls:
> r10-record-s9-owed still logs NEEDS-TITLE; r10-foo-2 whose body does not name R10-FOO logs
> NEEDS-TITLE; r10-roster-ops-3 whose body names only R10-ROSTER-OPS-3 logs NEEDS-TITLE. One
> mutant that tries (iii) before (i) resolves r10-roster-ops-2 to R10-ROSTER-OPS and fails its
> row.
> triage: dev/programme/triage/s6-batch106.md#P363

Re-routed verbatim to R10-OPENER-REUSE, each ending in its own ruling's citation:
- `s7/carries/b106-P363r-P337.txt`: R10-FLY-OPENPR-ATOMIC carry 9, `s6-batch94.md#P337`.
- `s7/carries/b106-P363r-P350.txt`: R10-FLY-OPENPR-ATOMIC carry 10, `s6-batch96.md#P350`.

Roster ops (queued `#held` until this file is on origin/main), in order:
1. `append-carry R10-OPENER-REUSE @.../s7/carries/b106-P363r-P337.txt`
2. `append-carry R10-OPENER-REUSE @.../s7/carries/b106-P363r-P350.txt`
3. `append-carry R10-OPENER-REUSE @.../s7/carries/b106-P363.txt`

The two texts stay on R10-FLY-OPENPR-ATOMIC as its record. That group is `done` and is not
dispatched again.

Rule run on the instances: `r10-fly-train-defaults-p2`, `r10-sav-comfort-p2` and
`r10-ux-health-p3` miss at (i), resolve at (ii), and each body's first three lines name the group
(R10-FLY-TRAIN-DEFAULTS, R10-SAV-COMFORT, R10-UX-HEALTH): they open. `r10-roster-ops-2-p1`
resolves at (ii) to R10-ROSTER-OPS-2, which its first line names: it opens. `r10-roster-ops-2`
resolves at (i). `r10-record-s9-owed`, `r10-rca-roster-sync-orphans`, `audit-r10-roster-land-s9`:
no candidate is a group, so NEEDS-TITLE as today.
