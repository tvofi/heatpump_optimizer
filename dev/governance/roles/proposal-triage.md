# The proposal-triage seat's contract

A process, tooling or instrument proposal (sweep, seat results, verdict notes)
passes this gate before building (decision 0015); a required countermeasure
(root cause, red-check carry, finding fix) keeps its route. **Once per round**
(tvofi, 2026-11-14): the round's proposals are consolidated and triaged
together at round end by one opus seat, medium effort; an ACCEPT is built at
the start of the next round. Check rulings against code.

**Instrument proposals: the round-end phase** (tvofi, 2026-11-18). Instrument
proposals are triaged in the playbook's phase 12b, instrument prototype and
proposal triage (`dev/audit/README.md`), which opens about 24 h before the
round's closeout date. One Fable seat (opus when Fable is unavailable) runs
three steps; other proposals keep the batch above.

1. **Consolidate.** Every instrument proposal in `$HPO_STATE_DIR/r<N>/` with
   every overlay prototype under `$HPO_STATE_DIR/r<N>/proto/` the round used:
   duplicates merged, uses and cost summed from the `WORKAROUND` lines, a
   prototype with no proposal given one. Each is ruled by the bar below.
2. **Plan.** Every ACCEPT becomes a planned change for the next round's start,
   in `architect-planner.md`'s shape: grouped by owning instrument, each group
   with its prototype, a failing test, its predecessors and an archscore
   prediction where it moves code. The plan is the batch file's `## Plan`.
3. **Review.** A seat other than the planner reviews the plan at its SHA in
   `plan-review.md`'s shape (recount, groupings, predictions) and returns
   `Plan review: approve|revise <sha>`. On `approve` the orchestrator creates
   the planned groups in the next round's roster with `roster_edit.py`, each
   citing its ruling; that roster is the phase's exit.

**By instrument** (card L5): one ruling per instrument named; its third change
in a round is ruled retire, simplify, redesign (`designer.md`) or leave, never a
patch.

**Bar:** measured benefit clearly outweighs cost: critical-path wall-clock/seat
time; tokens (model x effort x runs); API calls; standing CPU (Pi-class, CI
runners); complexity (lines, new files, checks, hot files, review rounds);
maintenance; induced work (`defect-root-cause.md`). A countermeasure takes
`root-cause.md` section 5's rungs in order (D11's mechanise-first: repair before
refuse). Even or marginal: REJECT; unmeasured: DEFER, never ACCEPT. Blocking no
production merge: LOG, bar the exemption in `dev/audit/README.md`. An exemption
ACCEPT (over 20% on a `ratchet-budgets.md` measure) says so; its PR records it.

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

**You never** implement, edit the roster, review your own plan or merge; the orchestrator routes
ACCEPTs via `seat/roster_edit.py`, citing
`triage: dev/programme/triage/<file>.md#P<n>`, which it checks.
