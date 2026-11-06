Round 2 repair: carries the two D0 residues of #2269 that #2631 did not land, both from #2612, into the D0 brief's Traps. D0.md is restored to the merge base's owner text; the only changes are the two added Traps bullets and whole-text cuts that pay for them. Closes #2269.

Carry 1 (stop tolerance refused on money, #1293): Traps bullet 3 of `dev/governance/dimensions/D0.md`, now with the source's "Re-measure at your merge base".
Carry 2 (DHW seeds unguarded, `_CERT_CELLS` space-only): Traps bullet 4.

Every surviving sentence is verbatim from the merge base. Deletions, all whole text:
- Step 2: the challenger `tighter `ftol`;` (kept removed: the carry requires it, else step 2 contradicts the new Trap).
- Header: "This brief says what to measure and how; the contract there says what counts."
- What you are hunting: "You are not asked whether the objective is the right objective — that is D2 — but whether the solver minimises the one it has."
- Step 6: "Simulate the receding horizon over a day for the cells that matter (`tests/rolling.py:run_rolling` shape)."
- Reuse: the dead citation `evaluate` (cut).
- Traps: "Timing under the fan-out is provisional; function-evaluation counts and iteration counts are your evidence."
- Traps: the `_MULTI_START_SOLVES` bullet, cut whole (dead name, no live equivalent).
Result: 65 lines (cap 66), under the token cap. No budget raise.

## Head

4ac556526f9e199b96e5cc9790f8d4539be81577, on origin/main (unmoved since the prepr run).

## Mutation proof

n/a: prose-only change to a policy brief; no production line or check is added.

## Null control

`git grep -e '#1293' -e _CERT_CELLS origin/main -- dev/governance/dimensions/D0.md` prints nothing at main; at the head the Traps carry both.

## Figures

- D0.md line and token count against its caps: `node tools/policy/policy_lint.mjs --budgets` (row for D0.md).

## Red checks

gate: the earlier red was an early failure while run 42216207567 was still being judged, not a failed test; this head is re-run, and if gate is still red once every workflow has concluded, the cause is the in-flight run, with no cheaper detector needed.

## Forward-carry

none

## Friction

none

## Approval

Pending: D0.md is policy; the owner's approving review at this head is required before merge. No approval is claimed.
