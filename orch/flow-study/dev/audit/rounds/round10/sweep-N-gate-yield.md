# Class sweep: N-gate-yield (round 10, phase D)

Finding in the class: D13-s2-01 (weakened, medium). `root-cause-unanswered`
blocked 37 of 124 fix-review verdicts in v6.7.16..17f1c55fad1b; the largest
engineering class, `harness`, blocked 23. The class is absent from
`dev/audit/config/bugclasses.json`, so it has no recorded status (open by default).

## Property and seam definition

A seam is every non-engineering block class (record/body, orchestration, and
untaught words that do not name a defect in the fixed code) that blocked at least
one verdict in the window. A seam is an **instance** when its count exceeds the
largest engineering class count: at that point the gate's cost outweighs every
engineering defect class in review yield.

Enumerator: `node dev/audit/rounds/round10/D14/sweep-N-gate-yield/enumerate.mjs <window.json>`
(window.json is D13-s2's `fetch_window.py` payload; parsing uses
`policy_lint.mjs` `waveVerdictRe` and `blockClasses`, as the D13 harness does).

## Controls (window at 17f1c55fad1b)

| control | command suffix | result |
|---|---|---|
| positive | (none) | `seams=13 instances=1`; re-finds root-cause-unanswered 37 > 23 |
| null | `--fixture=clean` (every blocked verdict stripped) | `seams=0 instances=0` |
| perturbation | `--fixture=reintro` (clean plus one re-inserted verdict line) | `seams=1 instances=1` |

## Dispositions (13 seams)

| seam | count | disposition |
|---|---|---|
| root-cause-unanswered | 37 | **instance**, the D13-s2-01 site (beyond_finding false). Partly guarded since #1951: `tools/pr/prepr.sh` predicts the head reds (budget-raise gate) and step 7c sweeps branch check-runs at push. The window still shows the class above the engineering maximum. Probe: the enumerator's INSTANCE line |
| other | 15 | not applicable: below the engineering maximum of 23 |
| conflict | 9 | not applicable: below the maximum |
| head-moved | 4 | not applicable: below the maximum |
| carry-missing | 4 | not applicable: below the maximum |
| claims | 3 | not applicable: below the maximum |
| untaught:body-stale, re-cut, body-false, body-figures, conflict-resolution, record-stale, instruments-stale | 1-2 each | not applicable: below the maximum |

Instances beyond the finding: **0**. Barriered: no. Because the class has a single
judged site and no further instances, `defect-root-cause.md` sets no case for a
new check. The countermeasure already in place is prepr.sh's push-time red
detection. The next round can re-run this enumerator on a post-#1951 window to
measure whether that countermeasure worked.
