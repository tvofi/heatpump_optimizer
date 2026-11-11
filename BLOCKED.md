# BLOCKED: r10-advisor-steady-start (fixer, second dispatch), at c966138ad, base ee64358be

Question: has the owner answered item brief-departure of design/R10-ADVISOR-STEADY-START 55f90c7c6 (a schedule ask's figure becomes a thermostat's day energy at the day's mean weather and mean price, not two plans solved from held starts as the group's brief requires)? Both the note ("the schedule branch is not started before it is answered") and its approving verdict aa148a9f9 ("The fixer does not start on the schedule branch before the owner answers item brief-departure") gate the schedule branch on that answer, and this seat found none.

## Where this seat looked for the answer (2026-11-11, after 12:43Z)

- The dispatch, PROMPT.md at 0f5a8f50f: names the approved note and says it binds; states no owner answer.
- The group's roster entry on handoff/audit-r10-roster ec5364c3f (`jq` on dev/programme/rosters/wave-r10-groups.json, group R10-ADVISOR-STEADY-START): one carry, the brief's; `owner_gate` null; no answer. origin/main ee64358be holds no entry for the group.
- #2257: one comment, the 2026-10-26 reopening.
- #3394: `updated_at` 2026-11-11T11:25:27Z, before the approval commit aa148a9f9 (12:41:07Z).
- `git grep brief-departure` over dev/programme at both refs: no line.

## Done meanwhile, none of it the schedule branch (measured head 936d92ccc, origin/main ee64358be merged in, no conflict)

- The appendix probe is landed as dev/audit/harnesses/r10_advisor_steady_carrier.py, classified as an inert read of tests/harness_headers.py in tests/closures.json (`tools/pr/ci_predict.py --apply-inert`), with one added line, `RESULT ... m2` (verdict item m2-row).
- Item main-drift, rerun on the merged tree: `AGE=<a> STEP=<s> PYTHONPATH=tests/hastub:tests:custom_components python3 dev/audit/harnesses/r10_advisor_steady_carrier.py`, the count being "schedule figures 96 against the ask" per key, in the order off / offm / at / atm (section 1's rows 1 to 4):

| AGE, STEP | off | offm | at | atm | no-schedule asks, energy difference exactly 0 of 36: off / at | m2 line |
|---|---|---|---|---|---|---|
| 0, 0 | 0 | 0 | 0 | 0 | 36 / 36 | +0.0..+0.0, off 0 on 0 of 12 |
| 0, 4 | 3 | 0 | 3 | 0 | 36 / 36 | +0.0..+0.0, off 0 on 0 of 12 |
| 1, 4 | 8 | 24 | 3 | 0 | 0 / 36 | -6.0..-1.3, off 0 on 12 of 12 |
| 2, 4 | 18 | 24 | 3 | 0 | 0 / 36 | -11.8..-2.6, off 0 on 12 of 12 |
| 2, 0 | 0 | 0 | 0 | 0 | 15 / 36 | -0.0..+0.0, off 0 on 7 of 12 |

  Every cell equals the note's section 1 at 273079db5; `ERRORS 0 horizon hours [24.0]` on all five. The STEP 0 rows are the null of the weather term (rows 1 and 3 read 0 there and 3 to 18 at STEP 4). Pair branch as built: cap figure +7.9..+26.4 at AGE 1 and +11.8..+30.0 at AGE 2 (STEP 4), solves 2; zero ask solves 3, built +0.0. Wall: one cell 91 s alone on this box.
- Not started: the optimizer reference method, the price_tiles schedule function, the `async_simulate` branch, checks (a), (a2), (a3), and everything the first BLOCKED.md (c966138ad) lists as owed; `ci_predict.py` at this head still predicts those reds (whatif.py unclassified and under-scoped, two stale pins on `async_simulate`, 15 unpinned sites, BLOCKED.md's layout).

Carry: R10-ADVISOR-STEADY-START (item brief-departure; the question above is this group's own, pending the owner's ruling)
