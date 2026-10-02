Fix review: merge 21f6299d77cca57b285dcef698526b23d53899ba

R9-F10.1e (PR #1816), round 1. Measured at code head 21f6299d (cut from main 661d56f4, no main merge in ancestry). PR head 7a392591 = 21f6299d + merge of main 90335cbd (#1811: claims tooling, prepr.sh, card/env_drift, entities.py); that delta touches no file this fix touches, so the verdict carries to it.

RESULT dst_checks head: ALL 127 DST / QUARTER-GRID CHECKS PASSED, rc=0 (dst_head.txt)
RESULT targeted mutants: 10/10 killed by dst_checks alone (mutants.txt)
  M1 drift._as_utc guard off -> naive-stamp check red
  M2 _as_utc returns value unconverted -> 8 checks red; M2b (pass) and M3 (wall subtraction) -> TypeError crash (weaker kill, still rc=1)
  M4 Cusum last_fed revert -> both drift checks red
  M5 boost clamp, M6 boost set, M7 sysid curvature, M8 wood_fuel duration, M9 legionella credited -> each its named check red
RESULT structure.py: STRUCTURE RATCHET PASSED; entities.py: ALL 2010 ENTITY CHECKS PASSED; closure selftest PASSED
RESULT closure: drift/boost/sysid/wood_fuel each select tests/features.py, which runs dst_checks
RESULT census rule (P7 barrier_gap): 35 hits on main, 11 at head. The 11: tariff.py:294 (exempt, wall-clock label), open_meteo 149/327-328 and coordinator 6395/9549 (dt_util.utcnow / UTC series, F10.1d measured clean), coordinator 3078 and wood_fuel 213 (calendar-day labels), away 250 (expire_override, measured clean), and snapshots.py:80 / curve_learning.py:114, which I read myself: both operands' "last" come from stored_instant(isoformat string) = fixed-offset tzinfo, so the subtraction against a ZoneInfo now converts to UTC; clean. Not in the body's disposition list by name; noted, not blocking.

Judgments:
- utc_elapsed_seconds/_as_utc moved to drift.py with accuracy re-export: architecturally sound. drift.py already owns the stored-instant rule (stored_instant), is the leaf both import, and the move removes a cycle-forced function-local import instead of raising local_imports. No ratchet raise.
- Three accuracy.py pins deleted: acceptable. The moved sites are killed by dst_checks (M1-M3), so mutation-autofix can pin them (ci-autofix.md); if mutation-autofix goes red, --pin-killed is owed by hand before merge.
- VERSION, manifest, RELEASE_NOTES, golden/claim files untouched. Body ## Head names 21f6299d = measured head. prepr's ## Head error is the transport-commit artefact; CI pr-contract passed.
- Unrun locally (named in body): stress.py, typing/mypy (3.14.2), --pin-killed. Real-HA ha_contract on the Mac at 7a392591: 61/61 PASSED, 22/22 probe comparisons PASSED (coordinator relay). At writing, CI on 7a392591 has fast, typing, mutation, coverage, closures still running; merge only on those green.
- Forward-carry: none; residual (same-zone compares in the repeated hour) is recorded in P7 barrier_gap.
