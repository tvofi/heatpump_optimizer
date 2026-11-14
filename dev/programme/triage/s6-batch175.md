# Proposal triage, session s14, batch 175 (P592)

This batch rules queue line 271 (the orchestrator's dispatch intake), 2026-11-11.

Sources:
- origin/main `45a8b828a4`. Every line number below is at that commit.
- `git ls-remote origin 'refs/heads/design-verdict/*'` and the `verdict.md` history of each ref.

## P592: DESIGN-REVIEW-ROUND-CONTEXT

Verdict: ACCEPT, narrowed, as a carry on R10-REVIEW-DISPATCH-RESIDUE (stage in-progress). That
group owns `tools/audit/seat/cloud_dispatch.py`. Parts p1, p3 and p4 are dispatched already, so
this carry rides the group's next part.

Source: the orchestrator's queue line 271, 2026-11-11 (R10-ADVISOR-STEADY-START round 3, with
the round context pasted into the fire message by hand).

Measured:
- `cloud_dispatch.py --group` refuses `--brief`, because "the roster gives the brief"
  (`GROUP_FLAGS`, `:1305`).
- The design-reviewer prompt (`:340-353`) names only the design tip from `design_tip`
  (`:524`). It carries no previous verdict and no round number. `reviewed_head` is a
  reviewer-only argument (`:388`).
- **How often a later round happens.** 27 `design-verdict/*` refs hold 51 verdicts. 25 of the 51
  are later rounds: a ref's second or later `verdict.md` commit. Each one needed the context
  pasted by hand, or the reviewer went without it.
  - Had later rounds been rare, the count would read near 0 of 51.
  - The maximum is 4 verdicts on one ref (r10-combi-tank, R10-ORCH-BEATD). That is the
    three-note limit in `design-review.md`. A reviewer who cannot see the previous verdicts
    cannot apply that limit.

The fix, narrowed to what the refs already hold:
- When `design-verdict/<group>` exists, the design-reviewer render states:
  - the round number (that ref's `verdict.md` commit count plus 1);
  - the last verdict's first line and its commit sha, which the reviewer reads with
    `git show <sha>:verdict.md`;
  - the range `git diff <previous design sha>..<design tip>`, where the previous design sha is
    the one the last verdict line names.
- A first round, with no ref, renders none of this. That is the null control the self-test pins.
- **The owner's non-acceptance is not rendered from the fire message, and no new flag is
  added.** Like any routed decision, it goes into the group's brief through the roster's
  existing `edit-brief` op. `group_brief` already renders the brief, and `GROUP_FLAGS` keeps its
  refusal of `--brief`.

What it costs and what it saves:
- **Cost:** about 25 lines in `cloud_dispatch.py`, using git reads it already makes for
  `design_approved`, plus two self-test checks.
- **Benefit:** 25 of 51 design reviews to date were later rounds. Each one is a hand-paste the
  orchestrator owes, or a review blind to the verdict it follows.
- It clears the 20% bar as a carry.
