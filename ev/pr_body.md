Triage batch 126 (R10-TRIAGE-S6) rules on the existing set under the owner's 5 % and 10 % rule: P391 DEFER on the non-production CI lanes, P392 DEFER on the triage seat. This is repair round 3 of the review block `owner-ruling-contradicted`.

**Round 2 block, answered.** P392 Binding item 1 ("a queue line with no measured figure gets a one-line DEFER... needs no decision") is removed from the Binding list. It changed the ruling form that `dev/governance/roles/proposal-triage.md` requires, which is policy. The record now holds it as a proposal for proposal-triage, adopted nowhere, with destination `dev/governance/roles/proposal-triage.md`. The remaining two bindings are renumbered 1 and 2; the first now refers to the proposed form. Nothing else in the file, the body or `dev/programme/delivery/3238.md` cited the removed item (grep).

**Follow-up, the `ci-fails` arm.** It now reads REST only: `gh api -X GET search/issues` for merged_at inside the window, and `pulls/<n>` for each head ref (the harness's `api()` now passes `-X GET`). The docstring and the ruling state the definition. Re-run at this head, cold cache, from this cloud seat: 423 failed pull-request runs, 55 failed push runs, 262 pull requests merged, 232 distinct head refs. Unchanged. The arm's definition is merged_at (262 by REST); the git arm's 263 first-parent merges by commit date differ at the window boundary. The 233 vs 232 distinct branches the reviewer counted came from that git count; the arm's own 232 is distinct head refs of the 262. `report` re-run on the ci-cost (221 runs, 309.7 runner h) and ci-fails outputs reproduces the per-lane table, for example arch-instrument 5.4 % / 779 s / 0 caught and instrument-self-tests 10.7 % / 1328 s / 9 caught. No ruling figure changed. Carry: dismissed: fixed in this PR, the arm in `dev/audit/harnesses/r10_triage_p391.py` is REST.

## Head

`21dbeb61c28f18aea98b45eebc290e30d991461a` is this PR's head, unchanged: its code was already in it and main merged cleanly, so the orchestrator's script set this body without a push.

`86d1220327a31155f78423bf19e17aa05cbc7d5e`

## Mutation proof

This file's only consumer is the triage gate in `tools/audit/seat/roster_edit.py`: `ruling_verdict` reads P391 and P392 DEFER and P393 None, and a carry citing either is refused as not an ACCEPT ruling. The harness change is evidence only; the arm was run, its output compared with the recorded figures.

## Null control

P393 reads None; with the file absent a carry citing it is refused as not on the roster branch or origin/main. For the REST switch the null control is the unchanged figures: 423, 55, 262, 232 against the recorded ones.

## Figures

- `git diff --stat $(git merge-base origin/main HEAD)...HEAD`: 4 files changed, 450 insertions(+) (harness, `tests/closures.json`, the ruling, the delivery row).
- origin/main was merged into the branch before the run; `tools/pr/prepr.sh` ran at `86d1220327a31155f78423bf19e17aa05cbc7d5e` and printed `rc=0`.
- The git, roster, ci-cost and nightly figures are untouched.

## Red checks

none concluded at this head yet; its checks run after the push.

## Forward-carry

- The proposal-triage proposal (a one-line DEFER for a queue line with no measured figure) is for the owner and proposal-triage, not this PR. Destination: `dev/governance/roles/proposal-triage.md`. Carry: dismissed: a policy change needs the owner's approval in its own policy pull request; the ruling records it as a proposal and no roster group follows R10-TRIAGE-S6.

## Friction

none

