Carries the two D0 residues of #2269 that #2631 did not land, both from #2612, into the D0 brief's Traps: a tighter stop is refused on money unless it shows realised closed-loop money off the flat price (#1293), and `_solve_space`'s DHW seeds are unguarded until DHW cells join `_CERT_CELLS`. The brief sits at its line and token caps, so the added prose is paid by cuts to other D0.md prose. Closes #2269.

Carry 1 (stop tolerance refused on money, #1293): landed as the second Traps bullet of `dev/governance/dimensions/D0.md`.
Carry 2 (DHW seeds unguarded, `_CERT_CELLS` space-only): landed as the third Traps bullet of `dev/governance/dimensions/D0.md`.

## Head

9da9caee2a8f08cc391839e5b8643a974e651cf7, on origin/main 7e8939d38cedb2976acc80a4ad7875cb545bd588. Main had not moved since the `tools/pr/prepr.sh` run, so there is no second run.

## Mutation proof

n/a: prose-only change to a policy brief; no production line or check is added.

## Null control

At the merge base D0.md is over neither cap and has no #1293 or `_CERT_CELLS` mention: `git grep -e '#1293' -e _CERT_CELLS origin/main -- dev/governance/dimensions/D0.md` prints nothing. At the head, the two Traps carry them and `node tools/policy/policy_lint.mjs --budgets` reads D0.md at or under both caps.

## Figures

- D0.md line and token count against its caps: `node tools/policy/policy_lint.mjs --budgets` (row for D0.md; line cap met, tokens under cap).
- Scope of the gate: `python3 tests/closure.py select --diff $(git merge-base origin/main HEAD)`, mode SCOPED, one changed file.

## Red checks

none

## Forward-carry

none

## Friction

none

## Approval

Pending: D0.md is policy, so the owner's approving review at this head is required before merge (CLAUDE.md, "Where the policy is"). No approval is claimed here.
