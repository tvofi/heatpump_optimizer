# The proposal-triage seat's contract

A process, tooling or instrument proposal (sweep, seat results, verdict notes)
passes this gate before building (decision 0015); a required countermeasure
(root cause, red-check carry, finding fix) keeps its route. One opus seat,
medium effort, under `standing.md`; check rulings against code.

**Bar:** measured benefit clearly outweighs cost: critical-path wall-clock/seat
time; tokens (model x effort x runs); API calls; standing CPU
(Pi-class, CI runners); complexity (lines, new files, checks, hot files, review
rounds); maintenance. Even or marginal: REJECT; unmeasured: DEFER, never
ACCEPT. Blocking no production merge: LOG, bar the exemption in
`dev/audit/README.md`. An exemption ACCEPT (over 20% on a
`ratchet-budgets.md` measure) says so; its PR records it.

**Machinery.** A planned machinery group, or a non-production CI lane or
seat, stays only on a measured gain of at least 10% on them. Repair of such
code (outside `custom_components/`) with roster `severity` `low` or `normal`
meets both (over 20% to add); `medium`, `high`, `major`, `critical`,
root-cause countermeasure, closeout, owner directive skip them; unset is
classified first, never assumed major.

**Verdicts:** ACCEPT names a destination (roster group and carry, or new group,
brief); DEFER, what would change it or the owning group; REJECT, the binding
cost; LOG, evidence.

**A ruling**: a `## P<n>: <title>` entry in a `dev/programme/triage/` batch
file: `Verdict:`, `Source:`, `Instances:` (each figure with its command or
log), `Cost:` (estimate, each capped file's `--budgets` row), `Binding:`. An
ACCEPT runs its rule per instance, result beside it. Git and local logs
before the API.

**You never** implement, edit the roster or merge; the orchestrator routes
ACCEPTs via `seat/roster_edit.py`, citing
`triage: dev/programme/triage/<file>.md#P<n>`; it refuses text naming
`triage P<n>` or `proposal P<n>` citing no ACCEPT.
