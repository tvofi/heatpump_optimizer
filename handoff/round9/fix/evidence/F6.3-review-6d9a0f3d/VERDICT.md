block 6d9a0f3dbca18b7d180c6afda0069dda95f66498 mutation: slotHitExtents edge pass unpinned; harness: class-open grid scope misses the payload's measured closure

F6.3 (#1802), fix review round 1. Reviewer: opus, cloud session, detached worktrees at the head.
Measured head 6d9a0f3dbca18b7d180c6afda0069dda95f66498, merge base 6793659caed93f5a47bc7cc940f119b9e2abcbeb = origin/main at posting.
The transport commit 43f22cd4 is not in the head's ancestry. tools/audit/briefs is unchanged between the base and main.

Remedies:

1. Pin the non-overlap invariant the fix exists for. Mutant M2 (M2.diff: the final edge-split pass in slotHitExtents
   replaced by `continue`) passes the whole browser lane, rc 0, all 8 P9 grid checks ok (M2.log). The reviewer's probe
   (extents_probe.mjs, the head's own slotHitExtents extracted and called) shows what M2 lets back in:
   RESULT shared_steps_like max_overlap_px=12.00 under M2, 0.00 at the head; boxed_in 1.00 against 0.00.
   That is the defect the docstring names ("a pointer between them hit whichever was drawn last"). The grid's
   24 px / 2.5.8 rule cannot see it, because overlapping targets are each 24 px wide. Add a check that the slot-hit
   rects of one lane never overlap (a grid rule, a dialog witness, or a card.mjs unit on slotHitExtents), and show it
   failing under M2 and passing at the head. The fixer's slot_hit_ink perturbation disables both passes together,
   so it never separated them. M1 (push loop off, M1.diff) is killed: 3 failures, including the grid's target rule.

2. Scope the grid by the measured closure, not a hand list. The grid's slot runs come from the plan payload
   (tests/card_browser.mjs:140, `shared()` filters the payload's space_power), which tests/plan_view.py writes from
   production Python. GRID_SURFACE lists plan_view.py but none of its inputs. With HPO_BROWSER_SCOPE=auto
   (scope_probe.mjs, the head's gridScope extracted):
   solver-only diff (optimizer.py) -> SCOPED -- SKIPPED, NOT A PASS
   profiles-only diff (tests/profiles.py) -> SCOPED -- SKIPPED, NOT A PASS
   card diff (control) -> SCOPED -- RUN
   tests/closures.json already measures tests/plan_view.py's closure: 74 files, including optimizer.py and profiles.py.
   Build the surface from that closure plus the card files and the grid's own scripts, so a solver PR that moves
   slots cannot skip the P9 barrier (CLAUDE.md rule 1: scoped by measured closures). Show the solver-only probe
   printing RUN. This is latent until F11.7 sets the variable, but the carry hands F11.7 a scope that is wrong, so it is
   fixed here, not carried. tests/dom_stub.mjs is not on the grid's path (card_rig imports it only for makeCardContext,
   which the lane does not import), so leaving it off the surface is right.

3. Update the body: add M2 and its new pin to Mutation proof, the scope probe to Null control, and the head SHA.
   Answer any red check from #1802's CI there.

Checked and fine:
- The card fix: slotHitExtents keeps each target over its own ink, inside the plot, and locked or read-only runs keep
  their ink. The head gives 0 overlap and 24 px targets in the probe's three lanes.
- CODEOWNERS for tests/card_rig.mjs and tests/dom_stub.mjs: both are imported by the code-owned card_browser.mjs
  path or its rig, so owning them is consistent with codeowners_gap. carry-1757.json has the finding-propagation shape
  and a null control, but its brief must change with remedy 2. The bugclasses.json P9 entry (detector, barrier,
  status barriered) matches the lane, apart from remedy 2's scope text.
- No budget raise; no VERSION, manifest or notes heading touched.
- #1802 CI at review time: briefs, typing, mutation, closure-scope, policy-docs, pr-contract, budget-raise-gate,
  delivery-status and nightly-status green; browser, fast, coverage and closures still running. Not re-run here.

Not re-run (cited to CI): the gate, the mutation table, the head's own browser lane.
