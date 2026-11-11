# `plan_audit.py`

- `plan_audit.py` — P3's measuring half (R10-FLOW-AUDIT-PLAN), beside the
  `audit-plan` workflow. `ledger` parses each merged PR's
  `## Architecture score` block with the parser `score.py`'s own report
  answers to, reconciles it metric by metric against `PLAN.json`'s moves, and
  demands the moves' sum account for `score.py --diff <fork> HEAD` within
  `--tolerance`; a merged metric no move names, a planned group with no body,
  an unexplained dS, an inadmissible reading or WORSENS fails, so a dS no
  planned move explains is `metric-gamed` rather than banked (`snapshot`
  likewise records the fork). `snapshot` records one ref's structure budgets,
  gate-only tripwires, behaviour inventory (entities, services, option steps,
  card tabs), mutation kill rate and 200-merge change coupling -- the fork's
  read by `--instrument`'s own scorer, so both sides are measured by the base
  -- and `compare` fails on any regression, with `--allow KIND:KEY` for a
  removal the plan's ADR approved. When: the architect measures the fork, and
  the stamp compares it. Refusal: `ARCHSCORE_ABLATE` set; a plan naming a
  different fork; two snapshots read by different instruments; `--self-test`
  (`governance.yml` greps its `checks, 0 failed` line).
