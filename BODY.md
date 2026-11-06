Repairs the P387 ruling of triage batch 122 after the review block "figures-uncited": the ruling read four commits that exist on no ref of origin. The text is restated against pushed refs only (origin/main `750a6001a`, `d8eeae8f8`, the roster ref `7cfdd9cc1`); every figure is re-taken with its command or struck. Two files change: `dev/programme/triage/s6-batch122.md` and `dev/programme/delivery/3212.md` (unchanged text-wise). No production code, budget, claim or roster file.

## Head

c9ee4e291c483398bdca49bbfc1118ebd77f8adf

## Mutation proof

n/a: a triage record changes no production line; there is no fix to break.

## Null control

The earlier ruling cited four commits that `git cat-file -t` reports as "Not a valid object name". The null for the re-taken arm table is the flat-price arm `valve-flat`, whose row is 0.47 %, so a saving has no source but volume and the ratio stays inside 0.5 to 2.0 (1.09). `grep -n '4fff42664\|39143c38f\|e1ee044cc\|77af298ef' dev/programme/triage/s6-batch122.md` prints nothing.

## Figures

- Arm table (R = booked reference 72.28 kWh over the printed plan kWh; 1.07, 1.09, 1.08, 1.14, 1.73, 1.78, 1.78, 8.25): `PYTHONPATH=tests/hastub:tests:custom_components python3 dev/audit/harnesses/r10_sav_wood_reference.py --quick <arm>`, run on a `git archive` export of origin/main `750a6001ae4d09c84858b53f94c22f4e5ca0623a`, eight arms. Only `wood-full` is above 2.0; none is below 0.5.
- Wood floor: `git show origin/main:custom_components/heatpump_optimizer/ledger.py | sed -n 458,466p` shows `calibration = max(1.0, calibration)` under `if wood_configured and calibration is not None:`; coordinator passes it at `coordinator.py:7903`.
- Roster: `git grep -n '"group": "R10-SAV-METER-FLOOR"' origin/handoff/audit-r10-roster` reads `dev/programme/rosters/wave-r10-groups.json:17024` at `7cfdd9cc1`.
- RCA ratios 3.30 and 0.18 and cost 6.8 h: `dev/audit/rca/R10-RCA-SAV-ESTIMATE.md` at `d8eeae8f8`, lines 38, 162, 217, 273.
- Struck as unreproducible: the owner-export ratio for 2026-10, "1 of 3" and "1 of 6" instances, the 1.1 h per release benefit, the marker line counts, the 50.0 / 75 / 87.5 % calibration drive. The ACCEPT stands on the class-barrier duty and the owner's rulings.
- Lints: `node tools/policy/brief_lint.mjs` prints `0 error(s), 0 warning(s)` on every section; `bash tools/pr/prepr.sh` at this head with this body: rc=0.
- origin/main moved to `c679f4b69` after the first run; it is merged at this head and prepr re-run with this body.

## Red checks

Read from the job logs of PR #3212 at its previous head f02530f49 (the new head has no runs yet):
- `governance / delivery-status` (job 127616990319): "DELIVERY STATUS OVERDUE -- 10 rowed, 12 pending, 21 overdue"; the log says it is not a required context. Repo state (other PRs' delivery rows), not this diff.
- `tests / nightly-status` (job 127616990292): "NIGHTLY FAILED: slow failed last night", scheduled run 41943946464 at head 499162c; unrequired, a lane outside this diff. Repo state.
Not compared with main's head check-runs page by page; the cause read is from the logs above.

## Forward-carry

- The meter floor lands in the roster `dev/programme/rosters/wave-r10-groups.json`. Carry: R10-SAV-METER-FLOOR
- Part 2 of the countermeasure and the bugclasses text land in `dev/audit/rca/R10-RCA-SAV-ESTIMATE.md`. Carry: R10-RCA-SAV-ESTIMATE
- The unmeasured size of unforeseen wood heat is restated in `dev/programme/triage/s6-batch122.md`. Carry: R10-HOTFIX-SAV-ESTIMATE

## Friction

none
