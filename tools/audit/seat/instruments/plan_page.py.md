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
  `dev/audit/harnesses/r10_plan_page_mutants.py`. A discharged group
  (replan.py's per-group `discharged`: merged, `carries-open`, every carry
  marked) renders merged, labelled with the record step it still owes (close
  or re-own its open issues, then `set-stage done`), and clears the edges on
  it. After the issue chart, the Flow section draws
  `merge_throughput.bottleneck_metrics` (imported, never copied): the
  critical-path lane as the plan's full set with each group's status,
  `bottleneck_check.judge`'s lines, the metrics table (a source it cannot read
  is UNAVAILABLE with its reason, never a zero, and never the UNAVAILABLE
  page), merge-wait per PR and skips per batch (latest 8). `--train-log PATH`
  names the live `train.log` (`state_docs.py --train-log`, which the beat's
  `plan-beat` row passes from the overlay's `train_log`); `--no-flow` draws no
  flow metrics. Its mutants are in
  `dev/audit/harnesses/r10_outside_intake_p2_mutants.py`.
- Round phases (R11-PRE-PLAN-RENDER): above the group lanes the page draws
  the round's phases file, `dev/programme/round<N>/phases.json` (`--phases
  FILE`, else the checkout's highest-numbered one), through
  `tools/audit/seat/plan_phases.py`: every playbook phase in the playbook's
  order on the file's own time axis, with status, started, finished, the
  planned window and its basis, entry and exit, and the open phases' items. A
  phase the file omits is drawn not started; a date the file does not carry
  is a dash. `plan_phases.py --check FILE` lints the file (unknown status or
  phase, out of order, waiting on nothing named, a non-ISO date, a date on a
  not-started phase, a finished date on a phase not done, a forecast with no
  basis: exit 1); an invalid file draws PHASES UNAVAILABLE and leaves the rest
  of the page standing. `plan_phases.py --phases FILE --html OUT` draws the
  section alone as a page, for a round with no plan yet. The file is named on
  the page by its checkout-relative path, never a host path. Its mutants are
  the `phases-*` entries of `dev/audit/harnesses/r10_plan_page_mutants.py`.
