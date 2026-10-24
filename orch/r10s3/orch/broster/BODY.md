Roster for round 10: forward-carries from the #2411 and #2406 reviews, landed before those pull requests merge (finding-propagation.md). Part of #201.

## Head

`97344315a` — handoff/audit-r10-roster: seven `tools/audit/seat/roster_edit.py` commits on main. It appends group R10-SAV-COMFORT and its carry (from #2411's review). It adds carries to R10-ADVISOR (two), R10-SCORES, and R10-TICK-DRIVERS (two, from #2406). Every edit went through `roster_edit.py`'s lint gate.

## Mutation proof

n/a: roster state only; no production or test code.

## Null control

n/a: no measured claim. `git diff --stat origin/main...97344315a` touches only `dev/programme/rosters/wave-r10-groups.json`.

## Figures

none

## Red checks

none

## Forward-carry

dev/programme/rosters/wave-r10-groups.json (groups R10-SAV-COMFORT, R10-ADVISOR, R10-SCORES, R10-TICK-DRIVERS)

## Friction

none

🤖 Generated with [Claude Code](https://claude.com/claude-code)
