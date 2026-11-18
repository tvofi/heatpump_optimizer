# Proposal triage, session s14, batch 220

Sources: triage queue line 350 (2026-11-11T22:43:06Z, carry-fold seat via orchestrator), ruled
as P673. Line numbers are at origin/main 61afd4f2db. Roster read at handoff/audit-r10-roster
7443303217. The accepted part is a carry on an existing group, so the open-PR cap does not bear
on it.

## P673: the carry-fold arm re-prints OWED for superseded wip refs; a gate_lock.py env leak

Verdict: ACCEPT (b) the gate_lock.py priority-env leak, as a carry on R10-PREPR-RESIDUE; REJECT (a) the carry-fold proposal as a duplicate of R10-RELAY-NOBODY-STALL carry idx 1 (P642).

Source: triage queue line 350. (a) 10 of 12 carry-fold level lines at 22:50Z were stale:
handoff-wip/<t> kept its BLOCKED.md after handoff-body/<t> named the handoff/<t> tip. Two
cleanup seats ran today (5 refs at about 21Z, 10 at about 22:50Z). Proposed: body_push.sh
deletes handoff-wip/<t> on success, or the arm skips a wip ref whose handoff-body names the
handoff tip. (b) A lead from the archived wip tag
archive/handoff-wip/r10-hotfix-restore-base-skew.69b3c17f3701: a local-only fix a27995c354 to
tests/gate_lock.py, never pushed.

Instances:
- (a) `jq '.groups[]|select(.group=="R10-RELAY-NOBODY-STALL")|.carry[1]'` on the roster at
  7443303217: CARRY-FOLD-SUPERSEDED (s6-batch211.md#P642). Its repair (a) drops the level line
  for a wip ref whose topic has a handoff-body/<topic> committed later than the wip commit, and
  repair (b) does the same when fix/<topic> merged. The group is `not-started`, severity medium.
  Line 350's 9 of 10 (body newer than wip) are exactly repair (a)'s case.
- (b) `git cat-file -t a27995c354`: not a valid object; the commit exists only as the diff in
  the archived tag's BLOCKED.md (`git show 69b3c17f3701:BLOCKED.md`, lines 7-53). On main,
  tests/gate_lock.py :1628 and :1738 start the `normal` waiter of the two ordering arms of
  `_priority_cases` with no `_Env(None)`, and tools/pr/prepr.sh :4159-4161 exports
  `HPO_GATE_PRIORITY`, so that waiter inherits the caller's priority.
- (b) measured: main's `tests/gate_lock.py` copied to scratch; `_priority_cases(g)` run under
  `python3 -I`:
  - `HPO_GATE_PRIORITY` unset (null control): `0 of 14 failed`.
  - `HPO_GATE_PRIORITY=1` (outside and critical-path branches): `0 of 14 failed`.
  - `HPO_GATE_PRIORITY=2` (a hotfix branch, gate_priority.py :104): `2 of 14 failed`. The two
    are "an urgent waiter takes before an older normal one" and "the heavy-slot pool orders by
    the same rule".
  So prepr.sh on any hotfix branch records these two failures, and the archived seat's
  `2 of 2707 ENTITY` red is this leak. #3463 merged R10-HOTFIX-RESTORE-BASE-SKEW part 1 without
  the fix (`git merge-base --is-ancestor 5ec2425619 origin/main` is true). That group is
  carries-open, so it cannot receive a carry.

Duplicate check: (a) is P642 / R10-RELAY-NOBODY-STALL idx 1. (b) No roster carry names
a27995c354, `_Env(None)` or `priority_first` (grep of the roster JSON at 7443303217).

Accepted change: (b) one carry on R10-PREPR-RESIDUE (in-progress, severity medium; it owns
tests/gate_lock.py and tools/pr/prepr.sh). In `_priority_cases`, the `normal` waiter of both
ordering arms enters under `_Env(None)`. Demonstration: the two arms fail with
`HPO_GATE_PRIORITY=2` exported on the base and pass on the fix. Null control: unset passes on
both.

Cost: (b) about 6 changed lines in one test file. tests/gate_lock.py has no row in
tests/structure_budgets.json. No new file, check or API call. (a) none: no new carry.

Binding:
- (b) The destination's severity is medium, which skips the 20% bar. On the bar alone it would
  still pass: a hotfix branch's prepr is red with no override, and hotfixes are the top
  dispatch rank.
- (a) The fix is already carried. The body_push.sh alternative adds a second mechanism in a
  second file for the same level line, and it would not clear refs that are already orphaned,
  which the arm-side repair does. Line 350's cost (two cleanup seats and near re-fires today)
  bears on when idx 1 is dispatched, which is the orchestrator's call. It does not justify a
  second carry. The stopgap (archive-tag, then delete) stays in use until then.
