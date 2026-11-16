# BLOCKED: r11-pre-machinery-limiter, part 1 re-dispatched after it merged

Dispatch: PROMPT.md at 9eab0e7428 ("Part 1 of 3: build carries 0-4"), base 367c3b9cac.

Part 1 (card P2 and carries 0-4) is pull request #3627, merged to main as
4ce615b5e6 (2026-11-16T06:09Z), an ancestor of the dispatched base
(`git merge-base --is-ancestor 4ce615b5e6 367c3b9cac` exits 0). The roster on
handoff/audit-r10-roster (43d8d918e4, wave-r11-groups.json) records the group as
`carries-open`, commit 4ce615b5e6, pr 3627, but marks no carry delivered, so the
render re-issued part 1.

Re-checked at 367c3b9cac, each present:
- P2: `proposal-triage.md:22` (severity route: red required check on main or a
  blocked production pull request); `ratchet-budgets.md:108` ("One in, one out");
  `machinery_target_budgets.json` (anchor b3831ff64e, 48 per 290 merges).
- Carries 0-2: `orchestrator.md:108-118` (the instrument freeze: prototype path,
  WORKAROUND line, proposals file, round-end triage, exemptions, what a workaround
  may never do); `dev/audit/README.md` round start steps 4 and 5 (where proposals
  and prototypes are; owner/outside items fold in, deferral recorded, silence is
  not one).
- Carry 3: `python3 tools/audit/machinery_ratchet.py --measure --head origin/main`
  at 367c3b9cac reads nonproduction_merges 481 against cap 478 band 5, and
  churn_per_kilo_product_lines 14213 against 14797 band 3636: neither cap sits
  more than its band above the measurement, so nothing is owed to record down.
- Carry 4: `pr_cap.py` `PRODUCTION_SLOTS`, `class_line`; `orchestrator_tick.py`
  prints it every pass.

No code is built: a second build of part 1 would duplicate merged policy.

Question: is this dispatch stale, so that the seat owed is part 2 (carries 5-11
by the original split, plus carry 12 and carry 13 as the orchestrator assigns),
and should the roster mark carries 0-4 delivered by #3627 before the next render?
