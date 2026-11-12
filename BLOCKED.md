BLOCKED: r10-standing-contracts-p2 part 1 (carries 7, 9-12) at 2ced371c1af5. Wip started from main, not from the older stop note on this ref.

Carry 7: dismissed: implemented at 1b174e9b3 (orchestrator.md:109 "only from the plan page and the ledger's digest").
Carry 10: dismissed: implemented at 1b174e9b3 (standing-roster.md is the retired stub; roster-drain row in tools/audit/seat/beatd.jobs.json).
Carry 11: dismissed: implemented at 1b174e9b3 (same evidence as carry 10).
Carry 9: not buildable. standing-merge.md is still the live seat contract and beatd.jobs.json has no merge or train row (rows: tick-digest, owed-check, roster-drain, plan-beat, gantt, verdict-audit, pulse, cancel-sweep, disk, opener, head-watch, audit-dispatch, outside-intake, bottleneck). The carry requires the replacement job live and one real pitch merged by it before the seat stops (owner constraint "dont cause you to run things inline"). Retiring the contract text now would break that constraint.
Carry 12: not buildable. There is no dispatch row either; standing-dispatch.md:17 already says "a beat job takes over once a cycle's log agrees". It needs the job built and one full cycle run beside the seat.
Question: build the merge and dispatch beat rows in beatd.jobs.json and beat_jobs.py (new design, outside the approved P2 contract-edit design), or leave carries 9 and 12 to R10-ORCH-LEDGER?
