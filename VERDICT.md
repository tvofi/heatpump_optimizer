Fix review: blocked b02ffd170d5049d8869689cbc889a5cf46097a1e metric-gamed: archscore: the body's dS +0.0012 IMPROVES is not this diff's, which scores dS +0.0000 NULL three-dot and in CI

bus-nonce: 83ea6356a16366c48fbb3ccd206a96e0

Round 1 of this fix review. Measured head: b02ffd170d5049d8869689cbc889a5cf46097a1e. At the post time it is still the PR head (`git fetch origin fix/r10-hotfix-ci-critpath-2` resolves to it), and origin/main is 7539d1675, the merge base.

## Block

The body states `Architecture score: dS +0.0012 IMPROVES (coord_footprint 2390 -> 2388)` three times: in `## Figures`, in `## Architecture score`, and as the `Architecture score:` line of `## Raise justification`. The owner's mandated approval quotes the same figure. The diff touches only tests/ci_ratchet.py, tests/ci_budgets.json, tools/policy/budget_raise_gate.py and a delivery row. None of those is coordinator code, so the diff cannot move coord_footprint.

- `score.py --diff origin/main HEAD` at this head, where origin/main is the merge base 7539d1675, prints `Architecture score: dS +0.0000 NULL` (ev/archscore-diff.txt).
- `score.py --diff 0cae227c3 b8a027974` scores the authored code head against its own merge base and also prints `dS +0.0000 NULL` (ev/archscore-codehead.txt).
- CI's own arch-score job 124591643014 on this head prints `Architecture score: dS +0.0000 NULL` and `PASS: dS +0.0000 NULL, no gate metric rose` (ev/ci-arch-score-log.txt).

So the +0.0012 movement survives with the mechanism removed. It is main's own drift, read two-dot against an origin/main that was not the branch's base, which CLAUDE.md rule 3 forbids for any branch-vs-main comparison. This is a misreport, not gaming of the instrument. The honest value, NULL, still meets rule 2's requirement that the score not read worse. But the brief makes an honest Raise justification a condition, and fix-review step 14 makes every figure the body quotes owed to the change. The repair is a body-only edit and does not move the head: replace the three occurrences with `dS +0.0000 NULL` measured three-dot, and drop the coord_footprint clause. All other checks below pass at this head, so a re-verdict should only need to re-read the body and the post-edit `budget-raise-gate` and `pr-contract` runs.

## Findings

- Surviving mutant M6: deleting the `--record` carry-over line `**{k: budgets[k] for k in BAND_KEYS if k in budgets},` in tests/ci_ratchet.py main() leaves `ci-ratchet self-test: 44 checks, 0 failed`. The body states "`--record` carries the band over" as part of the fix, and no check pins it. If the line is lost, the outcome fails closed: a re-record drops the band, and budget_raise_gate reads the removal as a raise (ev/gate-band-removal.txt). A one-check self-test pin on the record table is still owed. The fixer adds the pin with the body repair. Carry: R10-HOTFIX-CI-CRITPATH-2
- budget_raise_gate types the band MAX0, but MAX0 calls `critical_path_minutes_band` removed (1.3 -> absent) a raise, "a removed cap is no cap". Narrowing to 0 is routine, and adding it at 0 is routine. So removing the band, which tightens the gate to zero tolerance, would wrongly need owner approval. The PR's own docstring says "absent is a band of zero". This false positive fails closed, so it is not blocking. Carry: dismissed: a fail-closed false positive that opens no gate weakness, and only the owner can decide that removal should be routine
- Instrument finding: budget_raise_gate checks only the shape of the `Architecture score: dS <n> <verdict>` line (regex at tools/policy/budget_raise_gate.py:145). It never checks the value against the arch-score job, which is how an unearned IMPROVES got through the gate and into the owner's approval. The orchestrator propagates it to the budget-raise-gate brief by finding-propagation.md. Carry: R10-HOTFIX-CI-CRITPATH-2
- Wording: "86 runs of 2026-10-25" comes from the query `created=2026-10-25..2026-10-26`, whose runs span 2026-10-25T00:42Z..2026-10-26T20:55Z. The figures reproduce exactly, so only the label is loose. Carry: dismissed: only the label is loose, and every figure re-derives exactly

## Evidence

- Band measured, not padded. I fetched the 86 ci.yml push runs with the body's own query and scored them with `ci_ratchet.run_minutes` (ev/band.py, ev/band-1025.txt): `RESULT n=86 median=32.550 p90=34.267 sliding8 min=31.709 max=33.850 max|dev|=1.300`. That is the head's 1.3, unpadded, and the p90 equals the 34.267 budget exactly.
- I fetched the 59-run set again with `ci_ratchet.py --gather-runs ... --window 90` (ev/band-59-search.txt). The set ending at 0cae227c3 reproduces the body: median 33.767, sliding8 32.916..34.575, max|dev| 0.851, first20 33.883, last20 33.867. The body's sigma 1.638 is the population SD; the sample SD is 1.652. On the newest 59 runs at review time, max|dev| is 0.875..0.925, still under 1.3.
- The red log of job 124543698895 (run 41201096004) reads `GREW critical_path_minutes: 34.467 (budget 34.267)`. `git diff --stat 0d33c9348 05c0d6d5d` lists 7 files, all dev/programme/delivery/*.md (ev/red-run-log.txt).
- compare() applies the band to critical_path_minutes only. ev/null-control.txt holds `compare()` at the base budgets vs the head budgets:
  - 34.467 is GREW at the base and ok at the head, inside the band.
  - 35.777 is GREW at both.
  - The 35.567 edge is ok at the head.
  - script_runs_per_push 55 and archscore.unused_boundary_imports 1 are GREW at both, so the counters stay at zero tolerance.
  - budget_problems(head) is [].
- budget_raise_gate on the actual tables (ev/gate-band-removal.txt):
  - Null control: no raise.
  - Absent -> 1.3 (this PR): raise, "an absent entry here is a cap of zero", so a missing band reads as zero.
  - 1.3 -> 1.31: raise.
  - 1.3 -> 0: routine.
- Self-tests under `env -u BASH_ENV` at the head: `ci-ratchet self-test: 44 checks, 0 failed` and `budget_raise_gate self-test: 240 checks, 0 failed`.
- Mutants (ev/mutants.txt, summary lines):
  - M1, band ignored in compare: 44 checks, 2 failed.
  - M2, band applied to every row: 1 failed.
  - M3, gate row MAX instead of MAX0: 240 checks, 1 failed (band added is a raise).
  - M3b, gate row deleted: 1 failed.
  - M4, bounds check dropped: 1 failed.
  - M5, `>=` for `>`: 4 failed.
  - M6, record carry-over deleted: 0 failed. It survives (see Findings).
  - M7, band key not excluded from the grading loop: 0 failed. This one is equivalent: the band key is never derived, so it prints `? not derived; not graded` and never grows.
- The `gh: HTTP 500/502` lines in the mutant output are the self-test's own fixture noise. They show identically on unmutated runs.
- Merge: `git merge-tree --write-tree origin/main b02ffd170d5049d8869689cbc889a5cf46097a1e` gives tree 95e85e293 at exit 0 (ev/merge-tree.txt).
- Claims and versions: tests/golden/claimed_drift.txt and card_claimed_drift.txt are byte-identical to origin/main. VERSION, manifest.json and RELEASE_NOTES.md are untouched three-dot.
- Roles: `git diff $(merge-base)...origin/main -- dev/governance/roles/` is empty.
- CI: `merge_train.py classify b02ffd170d5049d8869689cbc889a5cf46097a1e` printed `GREEN b02ffd170d5049d8869689cbc889a5cf46097a1e pending: none red: none` at exit 0 (ev/classify-final.txt, ev/classify-log.txt). get_check_runs on the head shows no failure. budget-raise-gate succeeded on three runs, the last 124601791289 after tvofi's approval at this head. pr-contract 124601389482 succeeded.
- Red-check answers: the body answers the main-side `tests / ci-ratchet` red (no cheaper detector, because the input is live push-run history) and `budget-raise-gate` (red by design until approval). No check is red on this head.
- Head line: the body names b02ffd170d5049d8869689cbc889a5cf46097a1e as head, with code head b8a027974 and merge 9794b2228. That matches the measured head.
- Forward-carry: "none". O3 above is a carry this review hands on.
- Mandate: tvofi's approving review 5723761725 at commit_id b02ffd170d5049d8869689cbc889a5cf46097a1e is present. `## Raise justification` lists payments (1)-(3), and I found no architecture-improving payment it missed. Its `Architecture score:` line is the false figure blocked above.
- Harness: no committed finder harness is named, because this is a red-main hotfix whose evidence is the run history. The band statistic is my own script (ev/band.py) over `ci_ratchet.run_minutes`, disclosed as mine. It is not the fixer's.
