Fix review: blocked c05c635f typing: _instant returns datetime|float, so channel_pins' three compares add 6 mypy operator errors in manual_plan.py and CI typing is red on #1804

Round 1. Measured head c05c635f4a03801e98a7aeea9a1f72a289ea2b98 (merge base main 6793659c). Transport tip 4855c809 is not in the code head's ancestry.

What holds (re-measured with the finder's harness, RCA-BULK-1 p7_mutants.py, sha1 62a78339 identical to the fixer's copy):
RESULT head NONE: rc=0, 0 FAIL (78 checks), 1m30s wall on a 4-core cloud box with three other runs in parallel.
RESULT R3-D2-02 head: red on arm [tariff 15 min] and arm [tariff 60 min] (tariff.py), plus #777's 2 pins. Base tests: only #777's 2 pins, tracer blind. The config arm reaches R3.
RESULT R5-D1-08 head: red on arm [straddle] (coordinator.py _plan_age_minutes), plus #1299's 3 pins. Base tests: only the 3 pins, tracer blind. The straddle arm reaches R5.
RESULT fix reverts: FIX-service-expiry red (20-hour pin, both tariff arms); FIX-build-cap red (20-hour pin, far-expiry pin, both tariff arms); FIX-step-end red (fold-step pin, both tariff arms); FIX-instants red (fold-step null control). All match the body's table.
RESULT census rg "\bnow (\+ timedelta|- self\._)": 12 hits at 6793659c, 10 at c05c635f; the two lost are services.py:878 and manual_plan.py:288. RCA's p7_raw_sites.txt had 13 (coordinator _fuse_advisor_at has since left main). Dispositions of the 10 are the fixer's reading, inferred, not measured by me.
utc_shift fix: correct on both transitions (autumn 21 h -> 20 h, spring 19 h -> 20 h, plain unchanged). It also makes the override agree with the store's lead bound (store.py:499 bound = as_utc(now) + lead, already true time), which the old wall sum overran in autumn.
dst_checks cost: 16.8 s -> 58.6 s (fixer) is acceptable; the body re-ran the RCA cost test (about 4.4 h/month against about 119 h/month of P7 span) and discloses that the RCA's 20 s estimate was low.
Ratchets: no budget moved; budget-raise-gate green. No raise to judge.

Blocking:
1. CI typing (job 110261990474) is red: typing_ruler --mypy measures 6 errors in manual_plan.py, all by_code[operator], against a recorded 0. Cause: _instant returns datetime | float, so `_instant(ref) >= expires`, `start < step_end` and `end > ref_at` compare unions mypy rejects. The body says "Red checks: none known" because the fixer could not install Python 3.14.

Non-blocking but owed in the same push:
2. barrier_gap does not record the 10 raw sites. The body says they "are the barrier_gap list", but the new text only says "re-derive ... (p7_raw_sites.txt)", a file that is not in the tree (it is on handoff/audit-r9-alt). F10.1d will start from this text, so it must name them.

Remedies:
1. Make _instant return float on both branches, keeping wall order for naive stamps: `return when.timestamp() if when.tzinfo is not None else when.replace(tzinfo=timezone.utc).timestamp()`, annotated `-> float`. Then re-run tests/typing_ruler.py --mypy (on the Mac, or by reading CI at the new head), dst_checks.py and the FIX-instants mutant, and re-pin the _instant RETURN_DEL ledger entry if its site hash moves.
2. In tools/audit/bugclasses.json P7 barrier_gap, list the 10 sites by file and function (coordinator _forecast_arrays, _solar_forecast_view, _update_snow_memory, _on_meter_reading, _write_frequency, simulate; open_meteo _should_refresh; power_guard throttled; pump_arbiter _not_held; wood_fuel night_advice), give the census command and its count (10 at the head), point the re-derivation at handoff/audit-r9-alt:handoff/round9/state/alt/rca/bulk1/p7_raw_sites.txt or drop that name, and say F10.1d owns them.
3. In the body's Red checks, name typing and answer it (the cheaper detector is typing_ruler --mypy, which the cloud seat could not run).

Also noted, not blocking: build_override's `expires_ref > cap` and `_slots[-1][0] > cap`, and ManualOverride.is_expired, still compare stamps sharing the zone as wall clock. For a naive input, or an apply made between 06:00 and 07:00 the day before the fold, the cap can land in the repeated hour. That is the "comparison is not traced" gap the new barrier text already names, so F10.1d can take it.

CI at the head when posted: typing failure; briefs, browser, closure-scope, pr-contract, policy-docs, env-matrix, instrument-self-tests, budget-raise-gate, delivery-status, nightly-status, hassfest, validate-hacs green; fast (3.14), mutation, coverage, closures, CodeQL python still running. nightly-ha was skipped on this PR, so the real-HA ha_contract run is still owed by the Mac.
