# R10-RCA-ROSTER-SYNC-ORPHANS: a done transition drops an open issue's only owner

Root-cause seat, `dev/governance/roles/root-cause.md`, run at base
`92588d581fde4ce287af3db5e8bb61461dc28015` against the live roster ref
`origin/handoff/audit-r10-roster` at `806d2db83aa0`.

## 1. Cause

An issue is owned when an open roster group lists it in `issues` or `fixes`, a
`dev/programme/carries/carry-<n>.json` names it, or an O-brief carries its
number (`carry_audit.Dests`; `finding-propagation.md`'s destinations). The
ownership is derived from the group's stage (`roster_lib.is_open`), so the
write that moves a group to a closed stage also removes it as the owner of
every issue it lists. Neither writer of that stage reads ownership:

- `roster_sync.py`'s `derive`, MERGED arm (`changes.append(Change(gid, "done",
  ...))`), writes `done` from the merge alone;
- `roster_edit.py`'s `op_set_stage` (and `op_set_resume --field stage`) writes
  any classified stage, closed ones included.

An issue that is still open after the merge, and that no other live owner holds,
therefore loses its owner silently. The one detector,
`carry_audit.py sweep --issues`, runs later and by hand, and with no
`--roster-ref` it reads the checkout's tree (main's roster), not the round's
live roster ref, which is where both writers write. A group done on the live
ref but still open in main's lagging copy keeps owning its issues in the
sweep's eyes.

Which side moved (`git log`): `carry_audit.py`'s ownership test and
`sweep --issues` landed with O11 (`8011549f1`, 2026-10-18); the round's
readers moved to the live roster ref the same day (O17, `a5de742c0`,
`roster_lib.reader_ref`), but `load_dests` adopted the round ref only for
group *destinations* (a group open there passes), not for `owned`;
`roster_sync.py` (`446dc318c`, 2026-10-20; first live write `89625c06b`,
2026-10-22) automated the done write. The class predates the reconciler: nine
hand-written roster commits orphaned issues before `roster_edit.py` and
`roster_sync.py` carried the writes (the last on 2026-10-19).

## 2. Process state: (c)

The process meant to guarantee every open issue an owner exists: the carry
sweep (`carry_audit.py sweep --issues`, `finding-propagation.md`'s
enforcement). It was followed: the 2026-11-01 sweep that found the eight
issues was run. It did not produce the intended result: its unit, main's copy
of the roster, did not reach the live record. 3 of the 8 were invisible to
it. It also runs after the fact, so even the 5 it caught had been orphaned for
tens of hours. The countermeasure changes the unit (the live ref) and moves
the same test to the transition itself.

Not (a): a check for unowned open issues existed. Not (b): it was run. Not
(d): main's roster lagged the live ref from the moment O17 made the branch the
record (2026-10-18), before the sweep's first run, so no precondition changed
under a process that had worked.

## 3. The eight issues, and how far the class reaches

At the sweep, main's roster and the live ref (`84571a150c06`, the live tip
before the issues were closed at 2026-11-01T09:10Z) answered, through
`carry_audit.load_dests(<ref>).owned`:

| issue | main's copy (what the sweep read) | live ref at the sweep | orphaned by |
|---|---|---|---|
| #2248 | UNOWNED: caught | UNOWNED | `roster_sync` R10-STORE-RACES done, 2026-10-29 20:35 |
| #2249 | UNOWNED: caught | UNOWNED | same transition |
| #2257 | UNOWNED: caught | UNOWNED | `roster_sync` R10-ADVISOR-WHATIF done, 2026-10-29 23:18 |
| #2942 | UNOWNED: caught | UNOWNED | `roster_sync` R10-FRICTION-MUTATION-SURVIVOR done, 2026-10-30 04:01 |
| #2998 | UNOWNED: caught | UNOWNED | none: no group listed it before 2026-11-01 (`e74e0870a`) |
| #2492 | owned by R10-SAV-ACTUATION, `in-progress` on main: **missed** | UNOWNED (done there since 2026-10-31) | `roster_sync` 2026-10-30 23:59, `set-stage` 2026-10-31 13:18 |
| #2731 | owned by R10-FLY-GH-READ-RETRY, `carries-open` on main: **missed** | UNOWNED (done there since 2026-10-30) | `roster_sync` R10-FLY-GH-READ-RETRY done, 2026-10-30 13:53 |
| #2674 | owned by `carry-2674.json`: **missed** | owned by `carry-2674.json` | none under the rule: a carry file is a destination |

So the sweep's 3 misses are two of the stale-copy shape (#2492, #2731), which
the live ref catches, and one that is not an orphan by the tree's own
ownership rule (#2674: its carry file stays a valid destination while no live
group lists the issue). Reading the live ref, the sweep would have caught 7 of
8; the done-transition test reaches 6 of 8 at write time (all but #2998, never
owned, and #2674).

Class search, the whole round: every first-parent version of the r10 roster on
the live ref (2382 versions), every open-to-closed stage transition (264),
each asked `carry_audit.orphaned` against the post-commit roster with the
issue's open/closed state at the commit's time (scratch replay, cited with its
sha1 in the PR body). 67 transitions orphaned at least one issue: 86
issue-orphan events over 63 distinct issues and 60 groups. By writer: 39
`roster_sync` passes, 19 `roster_edit set-stage` ops, 9 hand commits (all
before 2026-10-20). 94 transitions closed with every owned issue owned
elsewhere or closed, and 103 owned no issue. None was still orphaned at the
tip: 26 were repaired by re-staging the same group (`carries-open`, by hand),
33 by wiring the issue to another group, 27 by closing the issue. Window from
orphaning to owner or close: median 7.75 h, 70 of 86 over 1 h, 20 over 24 h,
1754.5 issue-hours in all.

The class meets `defect-root-cause.md`'s audit-class count (three or more
instances in one round), which owes a class-eliminating barrier; the cost test
below picks its form.

## 4. Cost test (wall-clock, round 10: 2026-10-17 to 2026-11-01)

Measured in this seat's container:

- one `gh api repos/<repo>/issues/<n>` read: 0.35-0.37 s (three runs);
- one `roster_edit.py` op up to its lint gate, no push: 10.3 s;
- one `roster_sync.py` dry-run pass: 9.27-9.73 s at the base, 9.55-10.40 s at
  the head with one hold read (three runs each); a pass deriving no done
  transition makes no read;
- `roster_lib.reader_ref`: 0.06-0.07 s; `carry_audit.py sweep --issues`:
  0.88-0.93 s.

Standing cost of the countermeasure over the round:

- issue-state reads: `orphaned` reads only an issue no other owner holds, 145
  of the 227 owned-issue references across the 264 transitions: 145 x 0.36 s =
  52 s;
- disposal ops: a held group needs one more op (`set-stage done`) once its
  issue is disposed, where today a person who wired the issue elsewhere or
  closed it wrote nothing more; a group a person re-staged `carries-open` by
  hand needs one op fewer. `roster_sync`: 21 such transitions disposed
  otherwise, 18 re-staged by hand: +3 ops. `set-stage`: 17 and 2: +15 ops. +18
  ops x 10.3 s = 185 s;
- the sweep's ref read: 0.06 s per sweep.

Total about 237 s per round, about 4.1 s per orphaning transition (58
tool-written).

Cost of the defect per occurrence: the seat time to find an orphan and trace it
to the group that dropped it, and the window in which a finding routed to it
is refused (`#n has no owner`) and nothing dispatches it. The disposal decision
itself is owed either way and cancels. The tracing time was not measured: the
sweep alone costs 0.9 s, and it missed 3 of the 8 it was run for, which then
cost this seat. P(recurrence) is measured: 58 of 264 transitions (22 %), 58
of 161 transitions owning an issue (36 %).

Verdict: the countermeasure pays if finding and tracing one orphan costs a seat
more than 4.1 s, and the class owes a barrier regardless. Among barrier forms,
the hold is the cheapest found:

- refusing the closed stage instead, at `roster_edit`: the refused call costs
  the same op the hold's later `set-stage done` does (refused, dispose,
  re-run), and costs one more for the two transitions whose owner wanted
  `carries-open`; at `roster_sync`, unattended, a refusal leaves the merged
  group at its pre-merge stage, the stale stage the reconciler exists to end;
- a printed warning: a firmer instruction for a step that was followed (state
  (b) treatment for a (c) cause), and `roster_sync`'s output reaches no owed
  list;
- a self-releasing hold (the sync writing `done` once the held issues are
  disposed): it would save the 36 extra ops (371 s) but needs a marker
  separating a sync-held `carries-open` from a person's, and a re-read of every
  held group on every beat pass. Not built; its standing cost scales with the
  beat cadence, which this seat did not measure.

## 5. Countermeasure

State (c): the unit changes, and the test moves earlier.

1. `carry_audit.py`: ownership is one method, `Dests.owns(n)`, used by
   `check`, `unowned_issues` (`sweep --issues`) and the new `orphaned(dests,
   group)`: the `--issues` test asked of one closing group on the roster the
   write will leave. An unreadable issue state counts as open. `carry_issues`
   is the one carry-file reader (lifted out of `load_dests`), and
   `issue_reader` the one issue-state source (`--issue-state FILE` offline).
2. `carry_audit.py sweep`, with no `--roster-ref`, reads
   `roster_lib.reader_ref`'s answer, the live ref (`sweep_ref`).
3. `roster_sync.py`: `hold_open` rewrites each derived `done` whose group
   would orphan an issue into `carries-open`, at the merge commit, printing
   `HELD: owns open #n ...`, on the dry run and on the write path's re-derive
   both. Groups closing in one pass are judged together, so two that share an
   issue are not each other's owner.
4. `roster_edit.py`: `set-stage` and `set-resume --field stage` writing a
   closed stage go through `hold_done`, the same test, writing `carries-open`
   and printing `HELD`.

A detector shown to detect: the head's `roster_sync.py` dry run, against the
live roster at the parent of each historical orphaning commit, with that
merge's pull-request row recorded:

- R10-FRICTION-MUTATION-SURVIVOR (PR #2961, parent `c47931afa`): base `stage
  in-progress -> done`; head `-> carries-open ... HELD: owns open #2942`; head
  with #2942 recorded closed: `-> done` (null control).
- R10-FLY-GH-READ-RETRY (PR #2639, parent `22622ddf6`), issue state read live
  from `gh`: base `-> done`; head `-> carries-open ... HELD: owns open #2731`.

And the sweep at origin/main `92588d58`, both online: the base reports four
ISSUE-UNOWNED (#2999, #2998, #2965, #2257) from main's copy; the head reports
none from the live ref, and with `--roster-ref origin/main` reports the same
four (null control: the difference is the ref).

Self-test and mutant counts, with the commands, are in the pull-request body.

## 6. Not reached

- An issue filed with no owner at all (#2998, and the two other auto-filed
  `[policy] recurring friction` issues the base sweep listed): no transition
  drops it, so a transition test cannot see it; `sweep --issues` stays its
  detector.
- A hand edit of the roster file, outside both writers: none since 2026-10-19.
- The carry-file shape of #2674: the carry file said no live group covered the
  issue while R10-STORE-RACES listed it (2026-10-26 to 2026-10-29); whether
  `brief_lint.mjs`'s refusal of that state ran on the live ref was not
  measured here.
