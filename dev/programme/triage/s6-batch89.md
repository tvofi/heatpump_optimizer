# Proposal triage, session s8, batch 89 (P326)

The rolling batch after batch 88 (handoff `triage-s8-batch88`). Facts were read at origin/main
`4822c8f9b` and at #3006's head `9033a5958`.

## P326: after a main merge, auto-record a structure budget that measures IMPROVED and not yet recorded

Verdict: REJECT. This covers both the filed auto-record and the driver fix it suggests on
inspection. No roster op.
- **The filed form is a policy change.** `dev/governance/rules/ci-autofix.md` lists what CI must
  not automate: "Do not automate survivor triage, golden drift, structure budgets, `no-copies`,
  orphan → `INERT`, or briefs lint." A job that commits `structure.py --record` on a merge is that
  automation. CLAUDE.md rule 2 also has a seat "re-record deliberately with the reason in the
  commit message". Accepting the job would mean an owner-approved edit to both. The trade below
  does not reach that question.
- **What actually happened, measured on #3006's merges.** Each row is `class_excess_loc`, read
  with `--first-parent` from the head:

  | Merge | Base | Ours | Theirs | Merged | Measured |
  |---|---|---|---|---|---|
  | `4665c0c91` (`ci: merge main`) | 17672 | 17671 | 17659 | 17658 | |
  | `958b4af8e` | 17671 | 17658 | 17670 | 17657 | |
  | `76d96ac77` (`ci: merge main`) | 17659 | 17657 | 17658 | 17656 | |
  | `9033a5958` (the train's recarry) | 17658 | 17656 | 17656 | 17656 | 17654 |

  - The first three merges follow `tools/merge/ledger_merge.py`'s count rule for
    `structure_budgets.json`: base plus both deltas.
  - The fourth hit the driver's earlier rule, "a key both sides changed to the same value takes
    it" (`merge3`, `if ours == theirs: return ours`). The two sides agreed on 17656 by
    coincidence, so both reductions were counted once.
- **The driver fix is REJECTED as unsound.** That fix would sum the deltas in a sum ledger even
  when the two sides agree.
  - The equal-value rule is what makes a merge correct when both sides carry the same reduction.
    `update_pr.sh` merges an authored handoff head into the PR branch, and a re-cut handoff
    re-records the same budgets on a fresh base. Summing there double-counts, so structure.py
    would read the merged tree as a raise.
  - A text merge cannot tell an independent reduction from a shared one. Only the measurement
    can.
- **Benefit, measured: one instance.** It is #3006's `9033a5958`, at about 30 minutes for a fixer
  round plus one train skip. `ledger_merge.py` resolved every other merge in #3006's chain
  correctly.
  - 41 first-parent merges since 2026-10-17 touched `tests/structure_budgets.json`.
  - A coincidental equal value on two independent reductions of the same key is rare.
  - The miss announces itself: `tests / fast` and prepr both refuse IMPROVED-not-recorded, and
    the repair is one deliberate `structure.py --record`.
- **Cost of the filed form.** A CI job that commits to PR heads, with a loop-guard subject and the
  `action_required` approvals `ci-autofix.md` describes for the existing three. The policy edits
  come on top.
- **The trade is marginal.** That cost is clearly more than one 30-minute round.
- **Re-open trigger.** Re-open, as the owner's policy question on `ci-autofix.md`'s list, if
  IMPROVED-not-recorded after an automatic merge recurs on three or more PRs in one round.

Source: the orchestrator s8's message of 2026-10-31 (#3006 round 3).

Instances: #3006, merge `9033a5958`, where structure.py measured 17654 against a recorded 17656.

Cost: as above. The filed form is a new autofix job plus edits to `ci-autofix.md` and CLAUDE.md
rule 2. The driver variant is XS but unsound.

Binding:
- One instance, self-announcing, repaired by one deliberate command.
- That does not pay for automating a budget write that the policy names as never automated, nor
  for a driver rule that would double-count every re-cut.
