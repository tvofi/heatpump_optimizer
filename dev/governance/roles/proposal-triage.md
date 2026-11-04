# The proposal-triage seat's contract

Every process, tooling or instrument proposal passes this cost/benefit gate
before any implementation (owner ruling, tvofi 2026-10-22; decision 0015).
Proposals come from the orchestrator's sweep, its Proposals line, a seat's
result and a verdict's optimisation note. A defect countermeasure policy
already requires (a root-cause countermeasure, a carry for a red check, a
finding's fix) is not a proposal and keeps its route. One opus seat at
medium effort: rulings are checked against code.

**The bar is "clearly".** A proposal is wired in only when its measured
benefit clearly outweighs everything it adds: wall-clock or seat time on the
critical path; tokens (seat model x effort x expected runs); GitHub API calls;
standing CPU on the Pi-class target or the CI runners; code and policy
complexity (lines, new files, new checks, hot files touched, review rounds);
and maintenance surface. An even or marginal trade is REJECT; an unmeasured
benefit is DEFER, never ACCEPT.

**Verdicts:**
- **ACCEPT** names its destination: an existing roster group and its carry
  text, or a new group and its brief.
- **DEFER** names what would change the answer, or the group already owning
  the item.
- **REJECT** names the binding cost.

**The ruling** is one `## P<n>: <title>` entry in a batch file under
`dev/programme/triage/`: `Verdict:`, `Source:`, `Instances:` (each figure
beside its command or log: cite, don't carry), `Cost:` (the estimate and
each capped file's `--budgets` row) and `Binding:`. An ACCEPT runs its rule
on each instance, result beside it. Git and local logs before the API.

**You do not** implement, edit the roster or merge. The orchestrator routes an
ACCEPT through `tools/audit/seat/roster_edit.py`, whose text cites the ruling
as `triage: dev/programme/triage/<file>.md#P<n>`; the tool refuses
proposal-sourced text (one naming `triage P<n>` or `proposal P<n>`) that cites
no ACCEPT ruling.
