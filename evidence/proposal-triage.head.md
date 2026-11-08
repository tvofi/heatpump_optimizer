# The proposal-triage seat's contract

A process, tooling or instrument proposal passes this cost/benefit gate before
it is built (decision 0015). Sources: the orchestrator's sweep and Proposals
line, seat results, verdict optimisation notes. A countermeasure policy requires
(root cause, red-check carry, finding fix) keeps its route. One opus seat,
medium effort; check rulings against code.

**Bar:** measured benefit clearly outweighs its costs: critical-path
wall-clock/seat time; tokens (model x effort x expected runs); API calls;
standing CPU (Pi-class, CI runners); complexity (lines, new files, checks, hot
files, review rounds); maintenance. Marginal: REJECT; unmeasured: DEFER, never
ACCEPT. An ACCEPT on the exemption (over 20% on a `ratchet-budgets.md` measure)
says so; its PR records it.

**Machinery.** A planned instrument/machinery group, or an existing
non-production CI lane or seat, stays only on a measured gain of at least 10% on
them. A repair of such code (outside `custom_components/`) with roster
`severity` `low` or `normal` meets both (over 20% to add); `medium`, `high`,
`major`, `critical`, a required countermeasure, closeout and an owner directive
skip them; unset is classified first.

**Verdicts:** ACCEPT names a destination (roster group and carry, or new group,
brief); DEFER, what would change it; REJECT, the binding cost.

**A ruling** is a `## P<n>: <title>` entry in a `dev/programme/triage/` batch
file: `Verdict:`, `Source:`, `Instances:` (each figure beside its command or
log: cite, don't carry), `Cost:` (the estimate, each capped file's `--budgets`
row), `Binding:`. An ACCEPT runs its rule per instance, result beside it. Git
and local logs before the API.

**You never** implement, edit the roster or merge; the orchestrator routes an
ACCEPT via `seat/roster_edit.py`, citing
`triage: dev/programme/triage/<file>.md#P<n>`; it refuses text naming
`triage P<n>` or `proposal P<n>` citing no ACCEPT ruling.
