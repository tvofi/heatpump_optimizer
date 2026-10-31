# Proposal triage, session s9, batch 96 (P350)

The rolling batch after batch 95, which was pushed before this ruling and is left at its head.
Facts were read at origin/main `2b6bef745` and at the round's roster branch,
`origin/handoff/audit-r10-roster`.

## P350: land the sweep's handoff-orphan stand-in as an owed-handoff arm

Verdict: ACCEPT, narrowed, as one carry on R10-FLY-OPENPR-ATOMIC, amending P337's open driver: a
board topic the priority file omits never starves. The carry is at the end of this entry. The
proposal as stated, landing `handoff_orphans.sh` or an equivalent arm in `orchestrator_tick.py` or
`owed_unactioned.py`, is REJECTED.

Source: the orchestrator s9's message of 2026-10-31, an addendum to P349. It covers two more
instances, r10-fly-train-defaults-p2 (`17b38f7d9`, 13 files, "no PR ever, in nobody's queue") and
r10-cop-gate-r4-merge (2026-10-30). Both were found by a session-local stand-in, the sweep
runner's `handoff_orphans.sh`.

Instances, read from git and the opener's files at 22:34Z:
- **r10-fly-train-defaults-p2 is on the tick board.** `tick.txt` line 66 reads `OWED
  2026-10-31T21:53:36Z handoff-no-pr refs/heads/handoff/r10-fly-train-defaults-p2 17b38f7d9...
  body=39fe88960...`.
  - The handoff was committed at 19:45:17Z (`ct=1793475917`).
  - The driver's `cands()` reads exactly that line. The topic was absent from the opener's
    `prio.txt`, so it sorted last behind the listed topics at cap 6. It is now `prio.txt` line 1,
    added by hand.
  - It was in a queue, the board's, and was starved by the priority file, not missed by a
    detector.
- **r10-cop-gate-r4-merge is a false positive of the stand-in.**
  - `handoff/r10-cop-gate-r4-merge` is `9db842127`, "Merge origin/main into R10-COP-GATE r4",
    2026-10-30T06:49Z.
  - `git cherry origin/main 9db842127` shows 0 `+`, and `ledger.py landed` answers `merges-only`.
  - Its only content against the merge base is #2975's delivery row and a `tests/features.py`
    hunk, `_cg_aged`. PR #2975 merged (`dev/programme/delivery/2975.md` on main: "merged
    `507a9ec`"), and `_cg_aged` is on main (`git show origin/main:tests/features.py | grep -c
    _cg_aged`: 5).
  - The stand-in counts files from the merge base and never asks `ledger.py landed`, so it
    reports a merged PR's merge-forward as an orphan. The tick, which asks, correctly prints
    nothing.
- **P349's instances are the same shape.** All four are on the tick board. The three never
  started were absent from `prio.txt`, among them the critical-path r10-996-runner-claims
  (handoff since 18:41:52Z, `ct=1793472112`), still absent at 22:34Z.
- **The detector already exists in the tree.**
  - The tick's `handoff-no-pr` owed line comes from the handoff family (`bus.sh orphans`,
    `ledger.py landed`).
  - P337, batch 94, already carries the driver into the tree on R10-FLY-OPENPR-ATOMIC.
  - P337's text orders "Priority from `$HPO_STATE_DIR/open-priority.txt` ... default order
    `roster_lib.critical_path` > R10-HOTFIX-* > record topics > the rest". It does not say where
    a topic the file omits goes. The hand copy sorts it last, which is the starvation measured
    above.

Cost:
- As proposed: a second detector (about 25 lines of shell, or an arm in a tick file) that
  restates the tick's `handoff-no-pr` and lacks its `landed` test. One of the two instances is a
  false positive, and the other is already on the board.
- As narrowed: about 5 lines in P337's not-yet-written driver plus two fixture rows, inside a
  carry not yet built.
  - A topic the priority file omits sorts by P337's default order, never last.
  - A critical-path topic is never behind a non-critical one.
  - The driver prints `STARVED <topic> <sha8> <h>h` for a board topic that has stayed unstarted for
    more than 2 h.
- No capped file. The driver is a new file, and `owed_unactioned.py` is not touched.

Binding:
- The stand-in's benefit is zero: the board already names 5 of the 6 instances, and the sixth is
  a false positive.
- The priority file's omission is what held every real instance, the critical-path one
  included. It is fixed where the ordering is written, in the driver P337 already lands, at about
  5 lines.
- The orchestrator owes now: add r10-996-runner-claims to `s9/seat-opener/prio.txt` at the head,
  and retire the stand-in from the sweep runner, or teach it `ledger.py landed` while it runs.

The carry:
P350 amends P337's open driver (`s6-batch94.md#P337`). The priority file only orders topics it
lists; a board `handoff-no-pr` topic it omits sorts by the default order
(`roster_lib.critical_path` > R10-HOTFIX-* > record topics > the rest), never after every listed
topic. A critical-path topic is never placed behind a non-critical one, whatever the file says.
Each pass, a board topic that has stayed unstarted for more than 2 h prints `STARVED <topic> <sha8>
<hours>h`. Basis: r10-996-runner-claims (critical path, handoff 18:41:52Z) and
r10-fly-train-defaults-p2 (19:45:17Z) sat on the board unstarted for hours because the
session-local `prio.txt` omitted them. Rows: an omitted critical-path topic opens before a listed
instrument topic; null control: an omitted non-critical topic sorts after the listed ones of
higher default class; a STARVED line appears at 2 h 10 min unstarted, and not at 1 h 50 min. One
mutant sorts omitted topics last, and the critical-path row fails. triage:
dev/programme/triage/s6-batch96.md#P350
