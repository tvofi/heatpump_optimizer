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
  - **The producer** (the beat's `scorecard` row runs it once a day before
    `scorecard.py report`; `GH_TOKEN` passed):

        python3 -I tools/audit/seat/round_metrics.py produce --dir <state>/scorecard \
          --repo <checkout> --gh-repo <owner/name>

  `--self-test`: an empty input prints every read unread; a planted case per
  read in a throwaway repository and planted state dirs; one mutant per
  predicate.
