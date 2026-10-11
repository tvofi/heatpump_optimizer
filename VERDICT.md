Fix review: merge e66bb607cbbfafbd2339ee1c242a5e5707f64084

Resolution-delta review (contract step 12) of the head after reviewed
`466b1be77`. Head measured: `e66bb607cbbfafbd2339ee1c242a5e5707f64084`;
remote head unchanged at publish time (evidence/ls-remote.txt).

RESULT diff-files: the range `466b1be77..e66bb607c` touches exactly four files:
`tests/closures.json` (+1 line), and the bot commit `fab19d92d`'s three pins
`tests/mutation_ledger/killed_by/early_cutoff.py/{_planned_room.CMP_BOUND.2cb216c6,_second_zone_cold.CMP_BOUND.cf19f108,on_room_event.GUARD_OFF.3e8518f7}.json`.
The only authored commit is `c90c52099` (fixer seat); no main-merge files and no
`dev/programme/delivery/`, `VERSION`, or notes file moved in this range.

RESULT closures-line: the added line is character-for-character
`dev/audit/rounds/round9/prestudy/boost_drift_refit.py` — exactly the path the
`closures` red named — inserted in `inert_reads["tests/harness_headers.py"]`
between `fixplan/gen.py` and `rca/1747/b8_replan_blocked.py`, i.e. correct sort
order; the file parses as JSON at the head.

RESULT production-untouched: `git diff 466b1be77..e66bb607c` over
`custom_components/`, `early_cutoff.py` and `coordinator.py` is empty.

RESULT ci-closures: CI's own `closures` check-runs at this head include two
completed **success** conclusions (ids 114446050666, concluded 2026-10-11T10:15:43Z;
114446026748, 10:16:07Z), with one later arm still in progress and none red —
that is the verification; no local re-derive attempted. `closures` at
`fab19d92d` indeed has a `failure` run (id 114316515916), as the body claims.

RESULT red-checks: no check at this head has concluded failure/timed_out/
cancelled/action_required, so the body's `## Red checks` names `closures`
truthfully and no other red at the head is unnamed.

Round: resolution delta only; substance unchanged from the review at `466b1be77`.
Evidence: hpo-seats/r9rev-2070c/evidence/ (diff-and-closures-line.txt,
check-runs-head.json, check-runs-fab19d92d.json, ls-remote.txt).

bus-nonce: b7954f6ed8e4fbc668c1fb6d5cc94639
