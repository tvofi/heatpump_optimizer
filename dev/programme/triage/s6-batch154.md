# Proposal triage, session s14, batch 154 (P565)

This batch rules `s7/triage-queue-s7.txt` line 248, which arrived after batch 153. The bar and the
denominators are batch 141's.

Sources: origin/main `63bcdcaad8` (line numbers); the beat journal `S/beatd/journal.log` (8364
lines at 02:04Z, 11 `START` lines from 2026-11-09T07:52:35Z); the local job table
`s14/beatd.jobs.local.json`; `handoff/r10-tick-residue` (PR 3425).

## P565: S14-BEAT-CLASS-PHASE-LOCK

Verdict: ACCEPT narrowed (remedy (a), at the tracked table). It repairs an observed wrong
behaviour: three beat jobs of the `orch-checkout` class skip most of their passes as `busy`. Remedy
(b) is rejected.

Source: queue line 248 (2026-11-11T02:05:00Z, the orchestrator).

Instances:
- **The skip rate.** Counted over the whole journal with `grep -c "^PASS [^ ]* <job> "` and the
  same with `outcome=busy`:
  - gantt was busy on 57 of 84 passes, verdict-audit on 39 of 84, disk on 86 of 161 and plan-beat
    on 16 of 84. Roster-drain was busy on 34 of 986.
  - In the epoch that started at 01:26:21Z, gantt was busy 2 of 2, verdict-audit 2 of 2 and disk 3
    of 3, while plan-beat was ok 2 of 2.
  - The 08:50:32Z and 11:22:16Z epochs on 2026-11-10 had the same shape: gantt and verdict-audit
    were busy on every pass.
- **Who held the lock.** For each of the 232 busy passes, I listed the class jobs whose run overlapped
  the busy pass's wait window (start to end, from the PASS line's `start=` and `dur=`):
  - every busy pass had a holder: 232 of 232;
  - plan-beat overlapped 153 of them, a roster-drain `timeout` (a 900 s hold) 40, and the other
    class jobs the rest.
  - A false premise would have looked like busy passes with no class job running, which would mean a
    stale lock or a dead owner. There were none.
- **The mechanism, read in the code.**
  - `beatd.py` line 322 waits at most `class_wait_s` for the class lock, then records `busy`.
    `beatd.jobs.json` line 3 sets that wait to 60.
  - Plan-beat's run takes longer than that: a median of 96 s and a maximum of 281 s over its 67
    non-busy passes.
  - Every job loop starts at the daemon's start. `next_start` (line 282) keeps a periodic job on
    its grid, `max(prev, start) + interval_s`.
  - So the 1800 s jobs (plan-beat, gantt, verdict-audit) meet at every pass, and disk (900 s) at
    every other. The phase lock is real: it ends only with a restart, which re-races the same four.
- **The control, after the 02:04:44Z restart with `class_wait_s` 900.** The journal shows:
  - gantt ok at 02:04:49Z (dur 4), plan-beat ok at 02:06:21Z (dur 96), disk ok at 02:06:21Z and
    verdict-audit ok at 02:06:38Z (dur 113, including the wait);
  - the whole class finished in 114 s, inside one plan-beat pass;
  - roster-drain's next slot, 02:06:44Z, came after the class lock was released, so the drain was
    not delayed in this cycle.
- **What the drain would pay.** The worst serial wait at the shared start is the sum of the four
  maxima: 281 + 145 + 74 + 56 = 556 s, once per 30 min. The medians sum to about 147 s.
  - Today a drain pass that loses the race goes `busy` after 60 s and retries 120 s later, so it
    already waits about one plan-beat pass. The added delay is about 50 s median per 30 min.
  - That answers the source's open question: no material delay to roster-drain.
- **Remedy (b)'s alarm is already there.** `beatd.py status` (lines 467-471) reports a job whose
  last outcome is not ok as `JOB <name> busy` and counts it in the `N alarms` total, rc 1.
  - It is an alarm without the `ALERT` prefix, not a missing one. The status line the source quotes
    is that alarm.
  - A retry-at-release arm would add scheduler code to `beatd.py` to do what a table value already
    does.

Cost: one value in the tracked table, `tools/audit/seat/beatd.jobs.json` line 3, `class_wait_s` from
60 to 900. Make it at least the longest `timeout_s` of a class row, which is 900 today (roster-drain,
plan-beat, disk). `beatd.py` keeps its default.
- Self-test, in `beat_jobs.py`'s table checks (lines 133-136: its self-test already pins the table against the
  roster-drain timeout):
  - the shipped table's `class_wait_s` is at least the longest class-row `timeout_s`;
  - the null control: a table at 60 with a class row at 900 is refused by that check;
  - a mutant back to 60 fails it.
- `beatd.jobs.json` and `beat_jobs.py` have no row in `tests/structure_budgets.json`.
- After the merge, the local `s14/beatd.jobs.local.json` and its `--jobs` flag in
  `hook/launch/beatd.launch` retire at the next beat restart.

Binding:
- Remedy (b) is rejected. Its alarm half already exists as a counted alarm in `status`. Its
  retry-at-release half costs new scheduling code in `beatd.py` for the effect one table value
  gives.
- A start offset per job is not proposed and is not needed: the wait serialises the class.

The carry goes to R10-TICK-RESIDUE, which owns `beatd.jobs.json` and `beat_jobs.py`. Its fixer has
handed off (`handoff/r10-tick-residue` at `88a5ebe141`, PR 3425, still `class_wait_s` 60 there),
so the carry has the PART 2 prefix. Carry file: `b154-P565.txt`.
