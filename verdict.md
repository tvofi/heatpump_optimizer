Design review: revise 0e83751b1624081cdd7f7a429fcc551095ac4d28 exemption-gameable

Group R10-MACHINERY-RATCHETS (L). Design read from a detached worktree at 0e83751b1624081cdd7f7a429fcc551095ac4d28 (design/r10-machinery-ratchets tip at review start). Code read at 56630e7e6d229d960cf1b4db304d488ee20873e6 (origin/main). The note's base ddf4bfd73bc7 is an ancestor of it, one first-parent merge back (#3097, tools/plan only). Roster brief read at origin/handoff/audit-r10-roster 6b279e3b5.

## Revise points (one)

1. design.md:24, design.md:29 and design.md:79 (exemption). The match condition ties an entry to a PR number. It does not tie the entry to the merge that adds it. With `exemptions` as `superset`, which nobody has to approve, any later PR can append entries for machinery PRs that merged earlier and are still in the window. On push, those entries match "the merge subject's number". The window then drops those merges, so M1 and M2 fall and headroom appears with no improvement shipped.
   - Concrete game: a record-only PR appends 6 entries, each 11% with an existing evidence path, for 6 earlier machinery merges. M1 falls by 6, which is more than its whole band of 5. No arm refuses it.
   - PR mode is also left undefined. "The event's PR number" names only the candidate, so a push and a PR can grade the same window differently.
   - Fix wanted:
     - Honour an entry only when it is added by the merge it exempts: absent from the budgets file at P and present at M on a push, or absent at the merge base and present at the head for the candidate.
     - Apply the same rule to the base's W−1 merges in PR mode.
     - Add an arm to the self-test list at :79: "an entry appended later for an already-merged PR leaves M1 and M2 unchanged".
     - Add one row to the Gaming table at :40 for this move.
   - This must hold whichever way the owner decides at :31.

Everything else passes. On the next round, re-check only the exemption paragraph and the arm list.

## Routed decisions (not revise points)

- decision: owner (carried from :31): `superset` or `override` for `exemptions`.
- decision: owner, new: while main sits above cap+band, every record merge is refused, and delivery-status-tracking.md owes those records at each merge. The note does not say whether a capped main may hold owed records back until production merges bring M1 down, or whether record merges need a carve-out.
- decision: orchestrator (carried from :105): add files to the group. Also order the group against R10-FLY-STANDING-CONTRACTS. Its design (design/r10-fly-standing-contracts f21449444) also edits dev/governance/roles/proposal-triage.md and dev/governance/config/policy_budgets.json, and the note's hot-file list at :101-106 names only the overlap with R10-DEPS-ACTIONS-BUMP on governance.yml.

## Owner's checklist, item by item

- **Figures, re-run at 56630e7e.** Every enumerator reproduces exactly at ddf4bfd. At 56630e7e the following differ, and the fixer re-measures at its own merge base as :81 says:
  - M1 521 / window 580: same.
  - M2: 13624, not 13493.
  - Kind split: 213 machinery / 59 production / 308 record, not 212/59/309.
  - Bands: M1 5, same. M2 2436, not 2305. M2 range 11188..18162, same. M1 range 516..526 over 150 positions, or 516..527 over 151.
  - ACCEPT 218 in 87 files: same.
  - Open groups: 75 at the roster SHA (61 with no product file) and 50 on main. Reproduced, counting groups whose stage is not `done`.
- **Headroom at 56630e7e** with caps recorded at measurement: M1 has 5 (its band) and M2 has 2436. With the note's figures as caps: M1 5 and M2 13493+2305−13624 = 2174. Both pass today.
- **Source, counting rule and null control for each metric:** present at :11, :17-19 and :78. The rule classifies production, record and machinery from the merge commit's paths. I tried every gaming move in the table at :40 (not the exemption):
  - Splitting a machinery PR raises M1 by 1: survives.
  - Folding a record into a production PR is a real merge saved: survives.
  - Splitting a production PR, and a one-line product touch on a machinery PR, both lower M1. The note states both holes. M2 still charges the machinery lines, and the residual (product churn that changes no behaviour) is stated: survives as a pair.
  - Moving a file across the boundary: confirmed in a scratch repository. A rename-only move gives numstat `0 0` under -M, so it survives.
- **Rejected candidates:** (3) and (5) are rejected with reproduced data. (2), (4) and (6) are rejected by argument: redundancy, or no source exists. That is acceptable.
- **Budgets file beside policy_budgets.json, governed by budget_raise_gate 0013 through SCHEMA:** confirmed at budget_raise_gate.py:154-227.
- **Exemption recorded, with an unrecorded-raise control** (:79, "no entry refuses"): present. The defect is point 1.
- **Named in the note:**
  - fixer build order and failing test first (:74-86)
  - mutation targets (:88-95)
  - instrument doc (:84)
  - closures.json classification as a measured closure, not INERT (:85)
- **Scope:** about two pages, and no production code.
- **Steps 1, 3 and 6:**
  - Seam: one new owner. The only other merge classifier is `move_kind`, at merge_throughput.py:794.
  - Sibling readers: no other reader globs `*_budgets.json` except budget_raise_gate.py and its merge_train.py caller through `raises_between`.
  - Cost: about 10 files, which fits L.

## Notes for the fixer

- Name the file `machinery_budgets.json`. budget_raise_gate.py:154 discovers budget files by the suffix `_budgets.json`. A hyphenated "machinery-budgets" name, the note's wording at :7, is invisible to the gate. Carry: R10-MACHINERY-RATCHETS (item R1)
- budget-raise-gate.yml restores the gate from the base, so the landing PR is graded without the new SCHEMA entry. Every leaf of the new file reads `frozen` ("None -> value") and so counts as a raise. Plan for the owner's approving review at the head, or a mandate review with `## Raise justification` and an `Architecture score: dS` line. Carry: R10-MACHINERY-RATCHETS (item R2)
- `git diff -M --numstat` prints a cross-boundary rename with edits as `{tools => custom_components}/a.py`. Its lines then fall to nonproduct under a prefix test on the printed path; I checked this in a scratch repository: `1 0 {tools => custom_components}/a.py`. Read paths with `-z` and classify by destination. Add an arm for this case. Carry: R10-MACHINERY-RATCHETS (item R3)
- The kind-split enumerator in `## Figures` uses `--name-only` without -M. The rule at :11 uses numstat product lines under -M -w. The two agree on today's window (59) but differ on a pure move into product. The self-test must exercise the rule, not the enumerator. Carry: R10-MACHINERY-RATCHETS (item R4)

Seat token count: the harness reports none.
