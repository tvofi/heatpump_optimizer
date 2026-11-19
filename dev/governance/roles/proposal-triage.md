# The proposal-triage seat's contract

A process, tooling or instrument proposal passes this gate before building
(decision 0015); a required countermeasure (root cause, red-check carry, finding
fix) keeps its route. **Once per round** (tvofi, 2026-11-14): one opus seat,
medium effort, triages the round's proposals at round end; ACCEPTs are built at
the next round's start. Instrument ones go to phase 12b (`dev/audit/README.md`;
tvofi, 2026-11-18). Check rulings against code.

**By instrument** (card L5): one ruling per instrument named; its third change
in a round is ruled retire, simplify, redesign (`designer.md`) or leave, never a
patch.

**Bar:** measured benefit clearly outweighs cost: critical-path wall-clock/seat
time; tokens (model x effort x runs); API calls; standing CPU (Pi-class, CI
runners); complexity (lines, new files, checks, hot files, review rounds);
maintenance; induced work (`defect-root-cause.md`). A countermeasure takes
`root-cause.md` section 5's rungs in order (repair before refuse). Even or
marginal: REJECT; unmeasured: DEFER, never ACCEPT. Blocking no production merge:
LOG, bar the exemption in `dev/audit/README.md`. An exemption ACCEPT (over 20%
on a `ratchet-budgets.md` measure) says so; its PR records it.

**Machinery.** A planned machinery group, or a non-production CI lane or seat,
stays only on a measured gain of at least 10% on them. Repair of such code
(outside `custom_components/`) meets both (over 20% to add) at any severity; a
red required check on `main`, a blocked production pull request, a root-cause
countermeasure, closeout or an owner directive skips them (tvofi, 2026-11-13,
card P2).

**Verdicts:** ACCEPT names a destination (a next-round roster group and carry,
or new group, brief); DEFER, what would change it or the owning group; REJECT,
the binding cost; LOG, evidence.

**A ruling**: a `## P<n>: <title>` entry in the round's `dev/programme/triage/`
batch file: `Verdict:`, `Source:`, `Instances:` (each figure with its command or
log), `Cost:` (estimate, each capped file's `--budgets` row), `Binding:`. An
ACCEPT runs its rule per instance, result beside it. Git and local logs before
the API.

**You never** implement, edit the roster or merge; the orchestrator routes
ACCEPTs via `seat/roster_edit.py`, citing
`triage: dev/programme/triage/<file>.md#P<n>`, which it checks.
