Repairs the P387 ruling of triage batch 122 after the review block "figures-uncited": the earlier text read four commits that exist on no ref of origin. The ruling now cites pushed refs only (origin/main `750a6001a`, `d8eeae8f8`, the roster ref `7cfdd9cc1`), and every figure is re-taken with its command or struck. This body says what the ruling says: the `wood-full` ratio is 8.25, the ruling states no count of instances caught (the earlier "1 of 3" and "1 of 6" are struck), and the figures are re-taken at `750a6001a`. Two files change, `dev/programme/triage/s6-batch122.md` and `dev/programme/delivery/3212.md`. No production code, budget, claim or roster file. The roster carries (R10-HOTFIX-SAV-ESTIMATE, and the `triage:` pointer on the R10-SAV-METER-FLOOR brief) are routed by the dispatch seat through `roster_edit.py`; they are not on this branch and no roster commit is claimed here.

## Head

33a345901352189f67afe91df1db27970b25aa46

Three-dot diff, `git diff $(git merge-base origin/main HEAD)...HEAD --stat`: 2 files changed, 99 insertions (`dev/programme/delivery/3212.md` 1, `dev/programme/triage/s6-batch122.md` 98). origin/main had not moved since the last merge at this head (merge reads "Already up to date").

## Mutation proof

n/a: a triage record changes no production line; there is no fix to break.

## Null control

The earlier ruling cited commits that `git cat-file -t` reports as "Not a valid object name". The null for the re-taken arm table is the flat-price arm `valve-flat`, whose row is 0.47 %, so a saving has no source but volume and the ratio stays inside 0.5 to 2.0 (1.09). `grep -c '4fff42664\|39143c38f\|e1ee044cc\|77af298ef' dev/programme/triage/s6-batch122.md` prints 0.

## Figures

- Arm ratios R (booked reference 72.28 kWh over printed plan kWh: 1.07, 1.09, 1.08, 1.14, 1.73, 1.78, 1.78, 8.25): `PYTHONPATH=tests/hastub:tests:custom_components python3 dev/audit/harnesses/r10_sav_wood_reference.py --quick <arm>`, run on a `git archive` export of origin/main `750a6001ae4d09c84858b53f94c22f4e5ca0623a`, all eight arms. Only `wood-full` is above 2.0; none is below 0.5. The review seat re-ran all eight and reproduced the ratios.
- Wood floor: `git show 750a6001a:custom_components/heatpump_optimizer/ledger.py | sed -n 458,466p` shows `calibration = max(1.0, calibration)` under `if wood_configured and calibration is not None:`.
- Roster: `git grep -n '"group": "R10-SAV-METER-FLOOR"' origin/handoff/audit-r10-roster` reads `dev/programme/rosters/wave-r10-groups.json:17024` at `7cfdd9cc1`.
- RCA ratios 3.30 and 0.18 and cost 6.8 h: `dev/audit/rca/R10-RCA-SAV-ESTIMATE.md` at `d8eeae8f8`, lines 38, 162, 217, 273.
- Struck as unreproducible: the 2026-10 owner-export ratio, the instance counts, the 1.1 h per release benefit, the marker line counts, the 50.0 / 75 / 87.5 % calibration drive. The ACCEPT stands on the class-barrier duty and the owner's rulings.
- Lint: `node tools/policy/brief_lint.mjs` prints `0 error(s), 0 warning(s)` on every section of the ruling.

## Red checks

Read across all check-run pages for head 33a345901 (list read once, with the concluding jobs read from their logs):
- `tests / nightly-status` (job 127676643712) concluded failure: "NIGHTLY FAILED: slow failed 1 night ago", scheduled run 41943946464 at head 499162c. It is main's slow lane and reads no file of this diff, which touches markdown only. Not this diff's; no countermeasure owed here.
