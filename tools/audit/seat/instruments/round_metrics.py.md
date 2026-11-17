# `round_metrics.py`

- `round_metrics.py` — decision 0018 section 2's flow reads per round and per
  week, and the producer of `scorecard.py`'s inputs (R11-PRE-ROUND-METRICS;
  the process convergence audit d5d7ff81, section 6 row a3). Its rules and
  null control are the script's docstring; the commands are:
  - **A round, or its weeks:**

        python3 -I tools/audit/seat/round_metrics.py report --dir <state>/scorecard \
          --repo <checkout> --round <N> [--weeks]

    `--since ISO [--until ISO]` reads any other window. A round whose
    opening tag `v<N-1>.0.0` does not exist prints `round <N> unread`.
    `closure_slip` and `unexamined` are a round's reads: under `--since` each
    prints `unread`. `closure_slip` reads the forecast closure of every
    `PLAN.html` page on the round's state ref `handoff/audit-r<N>-plan` after
    its register, as the producer cached it in `plans.json` (the ref is
    deleted at branch cleanup, the cache is not), against
    `closure_slip_ceiling` in `dev/audit/config/objective.json`. It reads one
    sample a day (each day's last page, days counted from the register) and
    prints the samples and pages beside it: summing the later moves of every
    page makes it a function of how often the page is committed (round 10's
    history reads 2.57 days per day over all 563 forecast pages and 1.27 over
    its 15 daily samples), and only a fixed cadence compares rounds. Its
    net move is over the same samples: the last sample's forecast less the
    first's, so the first day's earlier pages do not enter it;
    `unexamined` reads the round's finder baselines (`"baseline_sha"` under
    `dev/audit/rounds/round<N>/` on `origin/main`) and the roster group kinds
    in `groups.json`.
  - **The producer** (the beat's `scorecard` row runs it once a day before
    `scorecard.py report`; `GH_TOKEN` passed):

        python3 -I tools/audit/seat/round_metrics.py produce --dir <state>/scorecard \
          --repo <checkout> --gh-repo <owner/name>

  `--self-test`: an empty input prints every read unread; a planted case per
  read in a throwaway repository and planted state dirs; one mutant per
  predicate.
