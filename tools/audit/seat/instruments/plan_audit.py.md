# `plan_audit.py`

- `plan_audit.py` — P3's measuring half (R10-FLOW-AUDIT-PLAN, R11-ARCH-OBJECTIVE),
  beside the `audit-plan` workflow. `ledger` parses each merged PR's
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
- **The objective (decision 0018).** `PLAN.json`'s `objective` block holds
  only `OBJECTIVE_KEYS`: `baseline` (the previous round's record, `BASELINE`),
  `pin` (draft roster path and blob at the plan SHA, `--start`, the durations
  blob), `terms` (each of `objective.json`'s, `up`/`down`/`hold` with a basis,
  or `undecided` with a builder: the only value for a term NO-READ in the
  baseline), `groups` (per planned group a `rank` its keys must give: 1 for a
  verified `bug` finding or a `REGISTERED` id (an `in` row of the baseline's
  escapes ledger, an open card by `check_scopes.py --open-cards`, a bug class);
  else 2, with `examined_by`), `edges` (`from`, `to`, `adr`) and `dispositions`.
  `objective-check --ref <plan SHA>` reads every input at that SHA and runs
  that SHA's `replan.py` twice with the pin: A on the draft, B on A less every
  rank-2 group no rank-1 group reaches through `after`, written under the
  draft's basename. The floor cost is A less B; lead time is finish less the
  pinned start, 0018's roster-entry clock. `--write` puts the derived figures
  and the pin, never the plans or `VERSION`, in the projection record
  beside the plan (its basename PROJECTION.json); without it a record unequal to the re-run's bytes refuses. Refusals:
  no block, a key outside the grammar (a time-shaped one as authored time), a
  verified bug deferred with no card, an unknown or doubly closed finding, an
  unregistered escape, card or class, a baseline other than `BASELINE` of
  round N-1 and one blob at the plan SHA, its tree and main's merge base
  (`--main`), a rank its keys contradict, a rank-2 group with no
  `examined_by`, a rank-1 group waiting on a rank-2 group with no `edges` ADR
  among the moves, an open group A schedules with no rank, a ranked done
  group (B keeps every done group), a stale pin, a B not that reduction, and a MISSED line of
  `--previous` with no disposition. `settle` prints HELD, MISSED, UNDECIDED,
  NOT-DUE or UNPREDICTED per prediction; only a HELD keyed effect credits a
  term (`KEYED_TERMS`), cause, re-report and escape keys settle at the next
  round's close, and a record without `keyed.<kind>` rows settles those
  UNDECIDED. Not caught: whether an escape's seam is the group's, and a slot
  or hot-file turn `replan.py` does not model (plan review's).
