# `plan_page.py`

- `plan_page.py` — renders the round's plan page (HTML) from
  `tools/plan/replan.py`'s plan.json, the roster through `roster_lib`, and
  GitHub's issue and pull-request state (`gh`, or `--github-snapshot`):
  swimlanes on the plan's time axis with the slot-occupancy strip,
  critical-path marks and planned stamps; the group ledger with status
  classes, PRs, struck closed issues and blockers; waves, stamps and the
  ETA method, every figure plan.json's. First section: open issues on
  not-done groups projected to close at the last carrying group's finish
  (closed ones dropped, unplanned ones flat), omitted with a note when `gh`
  is absent. When: after a replan at a wave
  edge, through `state_docs.py --plan`, which publishes it as `PLAN.html`
  beside the plan table. A group whose stage is a human disposition is
  `held`, never merged or ready. Refusal: a plan `replan.stale_reason` calls
  stale (its roster blob is not the roster's at its ref now; an `origin/` ref
  is fetched first), `replan.check_plan` refuses, or the plan records no
  duration model -- exit 1 and the UNAVAILABLE page (what could not be read,
  every figure a dash, no table), never a page of zeros. `--check` of
  replan.py applies the same freshness rule. `--self-test` carries the
  scratch generator's five defects as fixtures, each killed by its mutant in
  `dev/audit/harnesses/r10_plan_page_mutants.py`.
