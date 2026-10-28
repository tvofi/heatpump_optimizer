Triage batch 48 rules the one proposal that had no ruling. V150 (after a host reboot, two orchestrator sessions resumed one round in parallel) is ruled as P236, ACCEPT narrowed, and carried to R10-ORCH-BEATD. That group already builds single-instance locks and owns duplicate standing-seat detection (carry 22). The orchestrator session is the one process neither covers. The ACCEPT is narrowed in three ways, each set by a measurement:
- liveness is read from the session's own pid, matched by command, never from stop lines (a reboot leaves none);
- the pid is never `$PPID`, because all four `sup=` values on session s10's launch lines are already dead;
- the check runs at resume, before the first dispatch.

The out-of-tree half (the orchestrator's own `seat-launch.sh` and `orch_sweep.sh`) is not a tree change. As P230 ruled for the same script, it is the orchestrator's to make now, with the same three narrowings, and it was sent to the orchestrator, not carried. No product behaviour changes: the diff is one markdown file under `dev/programme/triage/`.

## Head

`df0629384d64f692094ac983ea418f94a3c5933c`; the file is the whole diff against `6d86acc909f7fc465e5736771daf8fa45c1373a4`.

## Mutation proof

`tools/audit/seat/roster_edit.py`'s triage gate is this file's only consumer. Driven with the queued carry text, which begins "From triage P236" and ends `triage: dev/programme/triage/s6-batch48.md#P236`:

- committed file: `ruling_verdict` returns `ACCEPT` and `triage_refusal` returns `None`, so the carry lands.
- mutant 1 (`Verdict: ACCEPT narrowed` rewritten to `Verdict: DEFER` in a copy): refused, `... #P236 is not an ACCEPT ruling (DEFER)`.
- mutant 2 (heading `## P236:` renamed to `## P237:`): refused, `... #P236 is not an ACCEPT ruling (no such entry)`.

## Null control

- At the merge base the file does not exist, and the same call returns `the triage ruling dev/programme/triage/s6-batch48.md is not on the roster branch or origin/main`.
- The same carry with its cite removed is refused: `proposal-sourced text cites no triage ruling`.

## Figures

- One instance: the orchestrator's queue file, line 5002. Pid 10472 started at 08:16Z and dispatched s9 seats at about 08:38Z. Pid 21371 started at 08:19Z. 10472 was killed on the owner's instruction, and nine seats were relaunched at 08:44:41Z (launch ledger lines 53-61).
- No `orchestrator` launch line exists: `awk '$3=="orchestrator"' launch-ledger.txt | wc -l` prints 0.
- `ps -o etime= -p 21371` printed 57:48 at 09:17Z, and the command is `claude`. `ps -p` finds none of 10472, 67903, 69863, 88215 or 90379; the last four are the `sup=` values of s10's launch lines.
- Two host reboots this round: seat ledger line 1058 records about 13:38Z on 2026-10-26, and the queue file line 5002 records about 07:07Z on 2026-10-28.
- `seat-launch.sh` and `orch_sweep.sh` are not in the tree: `git ls-files | grep -c 'seat-launch\|orch_sweep'` prints 0.

## Red checks

`none`. A ref with no pull request has no checks.

## Forward-carry

- P236 ACCEPT narrowed (V150): the orchestrator session takes this group's single-instance lock at resume, before its first dispatch. Liveness is read from its own pid matched by command, never from stop lines or `$PPID`; a second live session refuses and stops. Lands in `dev/programme/rosters/wave-r10-groups.json`. Carry: R10-ORCH-BEATD

## Friction

none
