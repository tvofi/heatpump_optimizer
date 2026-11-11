# `review_strength.py`

- `review_strength.py` — real-catch blocks per reviewed PR, incidence and
  first-pass share from the `review/*` bus and its `archive/review/*` tags,
  over git only (no REST), per window and per stratum: reviewer kind (a
  probe-ref return is cloud), class, the class the wave routes (`route`, the
  vocabulary read from web-fix-wave.js's VERDICT_CLASSES, never copied),
  re-review after a merge verdict, and with `--roster` the PR's origin, fixer
  model, size and product, taken `--as-of` the latest window's until (the
  verdicts, `--tree` and the roster ref cut there). `--guardrail` prints the
  review-strength guardrail's arms, report-only: incidence of the last 30
  PRs and of each seat family's last 20 against P0 = 0.28 with REAL widened
  by REAL_EXTRA, and the blocked words neither real nor taught. When: a flow guardrail
  or a D13 round reads review strength; `dev/audit/rounds/round10/D13/yield-probe.md`
  is its first use. Refusal: an out-of-grammar subject is its own row,
  never a verdict.
