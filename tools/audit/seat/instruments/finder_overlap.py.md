# `finder_overlap.py`

- `finder_overlap.py` — the two-finder overlap estimate, decision 0018
  section 5's second held-out check (the owner's round-11 trial,
  R11-PRE-ROUND-METRICS). No seat is scored on it. Its rules and null control
  are the script's docstring; the commands are:
  - **Seat the pair, before `audit-find.js`'s Finders phase:**

        python3 -I tools/audit/seat/finder_overlap.py seat --scopes dev/audit/config/scopes.json \
          --seat <D<k>-s<n>> --model-a <seat A's model> --model-b <the twin's model> \
          --round <N> --out ../audit-r<N>-overlap.json

    Seat A is the scopes.json seat, run by `audit-find.js` as ever. The
    orchestrator dispatches the twin with seat A's brief, cells and export,
    its finding ids numbered from 71 and its report at the path the command
    prints; scopes.json is not edited, so it stays disjoint. The twin's
    report joins `audit-verify.js`'s input like any seat's.
  - **Estimate, after the judge:**

        python3 -I tools/audit/seat/finder_overlap.py estimate --scopes dev/audit/config/scopes.json \
          --pair ../audit-r<N>-overlap.json \
          --report-a dev/audit/rounds/round<N>/reports-<box>.json \
          --report-b dev/audit/rounds/round<N>/<dim>/<key>-twin/REPORT.json \
          --judge dev/audit/rounds/round<N>/JUDGE.json

    Prints n1, n2, m, the estimate (n1 + 1)(n2 + 1) / (m + 1) - 1 and the
    unseen count over judged-real bugs (a judge merge is the shared bug), and
    both models, with `biased low` when they are one. A missing pair, report
    or judge verdict prints `overlap unread (<why>)`.
  - **Owner-only dimensions are never twinned.** A dimension whose
    `dev/audit/config/scopes.json` entry carries `owner_only: true` publishes
    nothing, and a twin's report path is in the tree: `seat` refuses a seat
    of one, and `estimate` refuses a pair naming one before it opens a report
    or the judge record. Each prints `REFUSED`, the seat id and that its
    dimension is owner-only, never a path or a count. `--scopes` is required
    by both commands, and admission is scopes.json membership alone.
  `--self-test`: the seating refusals, the count rules, the null controls,
  the owner-only arms (a canary seat and a nonce drawn per run; null: the
  flag removed or false, and a D15 seat, are admitted with the twin path
  printed), and one mutant per predicate.
