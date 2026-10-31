# `orchestrator_tick.py`

- `orchestrator_tick.py` — the heartbeat's dispatch list: one read-only command
  that measures the whole board — train liveness, stale queue entries, log/rc
  tail, prepr slots; per open PR the latest check-run per name, reds unanswered
  in `## Red checks`, missing delivery rows, moved verdicts with no carry,
  BLOCKED, DIRTY with the conflicted files `git merge-tree` names under
  GitHub's merge, no local driver run (the
  claimnotes repair only when all are claim files; a content conflict goes
  back to its fixer), NOT REVIEWABLE at a head whose required context
  concluded red, zero-run heads, absent required contexts, twin heads, claim
  stamps, staleness behind main; worker seats judged from the work they were
  dispatched for; roster groups newly unblocked or blocked; main's tip, its
  required contexts re-read live and judged by `merge_train.py`'s classifier,
  the mandate through `budget_raise_gate`'s
  own reader, action-pin drift. When: run BY a watcher seat on a ~4-minute
  loop — never inline in the orchestrator's turn, whose cron firings skip
  while a turn runs (measured: ticks skipped for hours during one diagnosis
  turn); the watcher seat notifies only on actionable events (TRAIN
  DONE/STOPPED with skip classes, Traceback, silent train death, a new merge
  → beats owed) and never diagnoses or fixes. Every failed lane at main's
  tip — required or not — becomes a fixer dispatch brief (context, job id +
  error line, suspected class, dispatch instruction; bot lanes lead with the
  ci-autofix rule): a main-side issue the orchestrator cannot resolve in one
  short turn is fixer work, and the orchestrator's duty is routing, not
  diagnosing. It replaces re-deriving the
  sweep from conversation memory. It does NOT act; the orchestrator acts on
  the list. Operating contract it assumes: orchestrator turns stay SHORT; any
  script with over a minute of wait or execution runs BACKGROUND (nohup, log
  file, completion notification); findings are DISPATCHED, not merely printed
  — a finding that only lands in tick output repeats the
  PR-comment-is-not-propagation defect. Refusal: a section whose read fails
  prints UNREADABLE, never a silent skip; a rule the tick cannot read from
  the tree or API it does not report. Every pass prints two level lines in
  PRS (tvofi, 2026-10-20): `WIP: N/6 (open PRs M)`, N the roster groups whose
  `resume.stage` is `in-progress` through `pr_cap.py`'s `wip_groups` and M its
  counted open pull requests, flagged at or over `HPO_WIP_CAP` — at the cap a
  new group is not dispatched, while opening and merging are always allowed;
  and `coordinator.py PRs: K/2`, the counted pull requests whose three-dot diff
  touches the coordinator, flagged over 2 or when a diff is unreadable. Also
  level lines every pass from the approver App's newest `Fix review:` on
  each open PR (the identity off `app_approve.sh`, the grammar `bus.sh`'s;
  the round-10 orchestrator, 2026-10-18): `MERGE-READY: #N <head8>` for a
  merge verdict at the current head on a CLEAN or UNSTABLE PR, and
  `BLOCKED-UNFIXED: #N <head8>` for a blocked verdict at the current head with
  no `handoff/<topic>` tip committed after it; `APPROVAL-OWED: #N <head8>` for a
  merge verdict at the head on a BLOCKED, REVIEW_REQUIRED PR (queue it for the
  train, which posts the approval); and `UNLEVELLED: #N <head8> <state>/<decision>`
  for a merge verdict at the head in any other state, except a draft, DIRTY,
  BEHIND, UNKNOWN, or a head with a pending, red or absent check (one_pr's
  gate lines own those). A verdict at a stale head prints none; comments it cannot read print UNREADABLE. One comments read per
  open PR per pass. A queue entry is unmerged only when its PR is in the open
  set (one `gh pr list --state open` per pass, TRAIN and REPLAN alike), never
  from a `pulls/<n>` `.state`, which reads `closed` for a merged PR: a queue
  whose entries are all merged prints no train-not-alive line (2026-10-18, t16).
  `OWED: <line>` prints every pass for each line of `cloud_relay.sh`'s level
  file (`<log>.level`, beside its default log `$HPO_STATE_DIR/cloud-relay.log`;
  a line of no ledger kind prints REFUSED) and for each event `ledger.py`'s
  fold holds open against this pass's open-PR heads and read-back verdicts;
  its stranded handoffs escalate to `DISPATCH:` and `OWNER FLAG:` lines
  (`ledger.escalate`); no store and no log yet prints no OWED. `REVIEW OWED:
  #N <head12>` prints for each open non-draft PR whose head no approver
  verdict names and no `bus.sh` dispatch record carries, and PLAN prints
  `DESIGN-BUILD:` for an approved `design/<g>` whose group has no build
  dispatched. `OWED handoff: <bus.sh ORPHAN line>`
  prints every pass for each complete handoff no PR head carries, read by
  `bus.sh orphans --min-age-h 0` (a pull request behind its own newer handoff
  included, #2411); a run with no summary line is UNCHECKED, never a clean
  zero. STATE's missing-row check, the closes check and the #201
  unrecorded-merge check enumerate merges through
  `tests/delivery_status.py`'s `parse_log` and `collect`, so a `<title> (#N)`
  merge counts as a merge (#2413, #2412, #2407). `--only CARRY`
  (opt-in, weekly and at closure; never in the default pass) runs
  `carry_audit.py sweep --last N --issues` over origin/main and the tick's
  roster ref: exit 1 prints one dispatch line and the unowned lines, and a
  run without its `CARRY-SWEEP:` summary is UNREADABLE. Its driver is
  `tick_loop.sh`.
