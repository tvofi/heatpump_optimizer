Fix review: blocked e8cef66b5cde41501964773983b6ab39ed863bee mutation: 3 of the 13 rewritten sites have no check that fails on revert (pump_arbiter hold echo grace, pump_arbiter _write retry gate, coordinator _update_snow_memory heavy-snow hold)

Round 1. PR #1809, code head e8cef66b (transport tip e2e88ee0, live head unchanged at posting). Base 787fe137 = current main.

## Blocking

Per-site revert mutants at e8cef66b, each restoring the one line to main's wall-clock form, run against HASTUB_TZ=Europe/Stockholm tests/dst_checks.py:

- RESULT hold-echo  `utc_elapsed_seconds(now, at) < ECHO_GRACE_S` -> `(now - at).total_seconds() < ECHO_GRACE_S`: ALL 92 PASSED (survives)
- RESULT write-gate `utc_elapsed_seconds(now, held.retry[slot]) < 0` -> `now < held.retry[slot]`: ALL 92 PASSED (survives)
- RESULT heavy-snow `utc_elapsed_seconds(now, self._last_heavy_snow) < (` -> `(now - self._last_heavy_snow).total_seconds() < (`: ALL 92 PASSED (survives)
- RESULT expiry-future (control, a pinned site): 1 of 92 FAILED (killed)

The body lists all three as sites that "misfired and now read true elapsed time", and barrier_gap records them so. The null control's 11 failures at main map to the other 10 sites only; the two arbiter failures come from the _not_held stamp. The mutation-table pins on pump_arbiter.py:502 and :548 are GUARD_OFF/BOOLOP mutants, which delete the guard, so they say nothing about fold semantics.

Two of the three are real misfires, measured here:
- write gate: now 02:58 CEST, retry = utc_shift(now, 5 min) = 02:03 CET (fold 1). Wall `now < retry` is False, so the retry is not held. The instant gate holds it. Once _not_held is fixed, reverting the gate re-opens the retry at once, and no check sees it.
- echo grace: written 02:59 CEST, now 02:00 CET, true 60 s. The wall difference is -3540 s, so a mismatch is skipped as "still in grace" for a wall hour. True elapsed is 60 s, past the 20 s grace.
- heavy-snow hold: a one-hour error on a SNOW_ROOF_DAYS window. It is fixed in the same way but neither measured nor pinned.

Owed: a fold check per site that fails on that one-line revert. Alternatively, record a site as unmeasured in barrier_gap and the body instead of "misfired".

## Verified

- Null control re-run (git archive 787fe137 plus the head's dst_checks.py): 11 of 92 FAILED, the same 11 the body names. At the head: ALL 92 PASSED.
- Spring gap (the brief asks for it; the body measured only the fold). spring_probe.py, GuardState.throttled for a true 5 s pair 01:59:58 CET -> 03:00:03 CEST: main False (lets it through), head True. The fix covers spring; no check pins it. Not blocking.
- Measured-clean exclusions hold. _solar_forecast_view uses dt_util.utcnow (coordinator.py:6393). The _prepare_dhw_inputs:3077 and night_advice:212 `now + timedelta(days=1)` results feed only .date(). The census rg at the head returns only those 3 lines.
- Correction to the record: open_meteo._should_refresh has one production caller, coordinator.py:6385, which passes dt_util.utcnow(). It cannot misfire in production; only the check's zoned stamps reach it. The fix is harmless, but barrier_gap and the body should say "defensive" rather than "misfired".
- utc_elapsed_seconds and _instant both read a naive stamp as UTC, so a mixed naive/aware pair now compares instead of raising TypeError. In production HA every stamp is aware.
- Conflicts: git merge-tree against origin/main, #1806 and #1808 all rc 0. No textual conflict in coordinator.py.
- VERSION, manifest and notes untouched. There are no resume files in the code-head ancestry (787fe137..e8cef66b is 3 commits: code, barrier_gap, ledger).
- CI on e8cef66b at review time: typing, briefs, policy-docs, pr-contract, budget-raise-gate, closure-scope, env-matrix, browser, delivery-status and nightly-status green. fast, mutation, closures and coverage still running; cited, not re-run. Real-HA on the Mac (relayed): 61/61 contracts, 22/22 probes.
- No budget moved; no raise to judge.

## Out of scope (not blocking; for the coordinator to route, not to file)

The census rule `\bnow (\+ timedelta|- self\._)` is narrower than the P7 class. The same same-zone `(now - x).total_seconds()` or wall compare appears outside it, with nothing in barrier_gap recording them. Examples: legionella.py:206/222/300, drift.py:129, comfort_learning.py:102, external_heat.py:462, sysid.py:1299/1585, coordinator.py:4594/4703/4892 (learning dt_h), coordinator.py:8543/8554 (outage holds), boost.py:65-71, away.py:249/469. None are measured here. This PR's barrier_gap now reads "closed" for the census, so P7 shows no open item. A sentence noting that the census rule does not enumerate these would keep the register honest.
