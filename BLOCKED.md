# BLOCKED: R10-HOTFIX-GATE-BUSY-DEFER-4 is already covered at origin/main (8aec35435)

Verdict: the defect does not reproduce at origin/main. Drop the group on this evidence.

## Covering change
fix/r10-hotfix-train-defer-wait, merged as 50f77d837 (2026-11-08 02:01 +0100). Commits
305b0d551 (failing test first) and eb1081cf0 (fix: `classify_at` waits out the gate-sweep
settle gap, a re-running gate is busy), both ancestors of origin/main. They were written
at 21:28-21:30Z on 2026-11-07, after the 21:06-21:20Z skips, and sit on top of #3287's
`_gate_busy` / `gate_busy` (gate.py `busy`) path, which already covered `wait_ci`.

## Test at the exact evidence shape (merge_train.py --self-test, run at origin/main, rc/ok lines)
    ok   #3293 race: the edit gate failed while code run 42414123291 runs -- `classify` reads WAIT (exit 3), never RED
Scene: edit run 42414123334 completed/failure (gate), code run 42414123291 in_progress with
`tests / closures` in progress, one head. Reads WAIT, not RED.
Train's own wait loop (`wait_ci`, the `ci red=[..]` path):
    ok   defer-wait #3248: the edit gate's red while code run ... runs is waited on, then it MERGES
    ok   defer-wait 13:01Z cycle: five of five deferring heads wait and merge, none SKIPs
Whole self-test: no FAIL line (337+ ok lines when this was written).

## Null controls (both in the same self-test, both pass)
    ok   #3293 null: the same edit gate failure with no code run in progress stays RED (exit 1)
    ok   #3293 null: once the code run ends in a content FAIL, no run in progress and no settle -- RED (exit 1)
    ok   defer-wait null: a genuine code-run failure still SKIPs once that run finishes
    ok   settle gap null: a content FAIL of the code gate leaves no green suite, no settle -- RED at once

## Why the 21:06-21:20Z skips happened
The evidence trains ran before 305b0d551/eb1081cf0 reached main; at the head (fefaa492) the
code run's `tests / coverage` ran to 21:42Z and its gate only listed at 22:20Z, so a train
without the settle/busy reads saw the edit gate's failure with nothing pending. No fresh
reproduction exists at 8aec35435.

## Side finding
`tools/audit/seat/train.sh` already documents and passes `add ... --front` (its header, line 10 and 20). Nothing to add.

No code change was made; VERSION, budgets and claim files untouched.
