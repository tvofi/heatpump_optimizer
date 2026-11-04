# Proposal triage, session s9, batch 96 (P350, P351)

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

## P351: an unanswered red check is refused at the end of a long prepr instead of first

Verdict: ACCEPT, narrowed, as one carry on R10-PREPR-CAP (`in-progress`, #3051), which owns
`tools/pr/prepr.sh`, its slot and what runs before it. The red arm moves ahead of the heavy slot
in `prepr.sh`, which every update and open runs. `body_push.sh` reuses the same function when the
PR branch exists. Neither copies the arm.

Source: the orchestrator s9's message of 2026-10-31 (recurring, four instances named: #3045,
#3047, #3050 and #3049's CodeQL alert 46 `py/overly-permissive-file`). It asks for an audit-class
barrier, not another refusal.

Instances:
- **Where the arm runs** (`tools/pr/prepr.sh` at `2b6bef745`):
  - The ancestry red-check arm, `reds_line` (lines 1329 onward), feeds every red a pushed commit
    of the PR branch carries, and every open code-scanning alert (`alert_reds`, line 1276), into
    the body check.
  - It runs at step 7c (line 3980), after step 1b has taken the heavy slot (line 3555) and after
    every heavy step.
  - It needs only the body, the changed-path list and the PR's remote head ref (`reds_head_sha`,
    line 1366). All three exist before the slot.
  - At the fixer's own prepr the arm skips: the fixer's branch is not the PR's head ref (`skip
    ancestry reds  no origin/fix/<topic> on the remote`, `pr/r10-ceiling-probe/p1.log`).
  - `body_push.sh` runs `prepr.sh --body-check`, which is "Offline: the red history is read at
    the open, never here" (line 1557).
  - So the first reader of these reds is the update or open, after its slot.
- **The count**, logs from the last 2 days holding `REFUSE   ancestry reds` (`find . -name '*.log'
  -mtime -2 | xargs grep -l`, under the session directory): 13 files. 9 are distinct update runs,
  besides the relay and tick logs that echo them:
  - `s8/upd-2989r5.log`;
  - `s8/r10-hotfix-away-live-upd-0032.log`;
  - `s8/r10-cop-partload-p2-upd-2317.log` and `-2334.log`;
  - `pr/upd-fix-r10-train-overlap-grade-p3.log`;
  - `pr/upd-fix-r10-fly-cancel-sweep.log`;
  - `pr/upd-fix-r10-fly-openpr-atomic-pr.log`;
  - `pr/upd-fix-r10-fly-gh-call-log.log`;
  - `s9/seat-dispatch/update-3049b.log`.
  The reds were `governance / instrument-self-tests` (7), `prelude` (3),
  `budget-raise-gate / budget-raise-gate` (2), `tests / fast (3.14)`, and CodeQL alert 46 (2).
- **What one refusal cost, measured on #3049** (`pr/upd-fix-r10-fly-gh-call-log.log`):
  - `taken slot=1 label=prepr-33638 expires_at=22:17:44Z` means the slot was taken at 21:47:44Z
    (`LEASE_SECONDS` 1800).
  - The run then ran `mutants` and `self-test  431 passed, 0 failed`, and was refused at 7c at
    22:44:59Z (log mtime).
  - That is 57 min of a heavy slot for a refusal readable in seconds.
  - The other refusals were on light diffs. Each paid the slot wait instead, median 11.4 min on
    batch 95's light-run sample (n = 8).
- **Rule run on the instances:**
  - With the arm before the slot, each of the 9 refuses at the same red in seconds, before
    `slot-take`.
  - Null control: a branch whose reds are all answered passes the early arm and continues
    exactly as today.

Cost: S, inside the existing group.
- `prepr.sh`: call `reds_line` before step 1b when a body is given and the PR's remote head ref
  exists. Exit on its rc 1 before the slot; keep rc 3 a skip line. Step 7c then reuses that
  result instead of a second read. About 15 lines.
- One self-test row pins the order: `reds_line` before `slot-take`, by the same awk shape as the
  existing line-3268 row.
- `--body-check`, called by `body_push.sh`, gains an optional `--pr-branch fix/<topic>`.
  `body_push.sh` passes it when origin has that ref, so a local fixer meets the red before the
  handoff. A seat without a token keeps today's skip line. About 6 lines.
- API: the same reads 7c makes today, moved earlier, so no new calls.
- `prepr.sh` and `body_push.sh` have no `policy_lint.mjs --budgets` row, and `tests/structure.py`
  measures `custom_components/` only.

Binding:
- 9 update refusals in two days, one of them 57 min of slot and the rest one slot wait each,
  become refusals in seconds.
- The arm already exists and is self-tested. This moves its call ahead of the slot and reuses it
  from `body_push.sh`, with no new check.
- It is the fourth instance of one class, so a barrier is owed (CLAUDE.md, "A recurring error is
  not a third issue"), and this is the cheapest one.
- The benefit clearly outweighs the cost.
- It sits beside the owner-ordered slot carry in the same group: both decide what runs before
  step 1b. One fixer should take both.

The carry:
P351: in `tools/pr/prepr.sh`, run the ancestry red-check arm (`reds_line`, step 7c at line 3980 of
`2b6bef745`) before step 1b's heavy-slot take (line 3555) whenever a body is given and the PR's
remote head ref exists. An unanswered red exits before the slot is taken; the skip answer (rc 3)
stays a skip line; step 7c reuses the early result instead of a second read. Give `--body-check`
an optional `--pr-branch fix/<topic>`, and have `tools/audit/seat/body_push.sh` pass it when origin
holds that ref, so a fixer meets the red at its handoff. Basis: 9 update runs refused at 7c in
two days; #3049's run held slot 1 for 57 min (taken 21:47:44Z, ran mutants and the 431-check
self-test) before the refusal at 22:44:59Z. Rows: a body that leaves a red unanswered is refused
with no `slot-take` call; null control: an answered body takes the slot and runs as today; the
order row, `reds_line` before `slot-take`; `--body-check --pr-branch` refuses the same red.
One mutant moves the call back after the slot, and the order row fails. triage:
dev/programme/triage/s6-batch96.md#P351
