# LEADS-LC: audit round 9, leads catch-up batch (seat LC)

Baseline: `1936d5ca72a06556eeed4e8e5bf3dea520e517e1`. Set: `leads_catchup.json`
(6 leads). D3-s2 and D3-s3 have now reported (`origin/handoff/audit-r9-find-B2`,
`origin/handoff/audit-r9-find-B3`), so leads they own were measured live, not
closed as deferred. tvofi's 2026-09-26 D3 rule applied throughout: no mutation
pre-screen, no mutant pool, no full-gate mutant run against any D3-owned lead;
only in-memory guard on/off comparisons and timezone probes on production
code, never `tests/mutation_table.py`/`pool.json`/`prescreen.py`.

## Disposition (6/6)

| raised_by | file:symbol | owner | disposition |
|---|---|---|---|
| D3-s2 | tests/mutation_table.py: candidates (CLAMP_DROP) | D3-s2 (resolved via `check_scopes.py --seat`, keyed on price_model.py) | **closed** — owner already measured this exact site as finding **D3-s2-02** |
| D3-s2 | coordinator.py: flow-bias fold / FlowCurveBias.observe | D1-s2 | **converted → D1-s2-91** |
| D3-s3 | coordinator.py:586/588/6331/8112/8384 (tzinfo guards) | D3-s1 | **converted → D3-s1-91** |
| D3-s3 | optimizer.py:200, defrost.py:643 (tzinfo guards) | D3-s2 | **closed** — measured, does not fit the hypothesized UTC-blind pattern |
| D0-s1 (deferred) | tests/optimality.py: score_plan / pin_result | D3-s3 | **closed** — owner's now-live report does not mention this lead |
| D12-s3 (deferred) | tests/entities.py: _walk_flow_untouched | D3-s3 | **closed** — owner's now-live report does not mention this lead |

## Lead 1 — CLAMP_DROP (closed)

`check_scopes.py --seat D3-s2` owns `price_model.py`, the exact file the
lead's own text cites ("price_model.py:368 is one such site"). D3-s2's report
already measured that precise site as **D3-s2-02**: replacing
`max(0.0, float(v))` with `(0.0)` at price_model.py:368 zeroes every restored
`residual_var` (96/96 → 0/96 guessed steps with non-zero sigma after a
store round trip), surviving all 15 closure drivers. That is the CLAMP_DROP
defect the lead describes, on the cited site; not re-measured.

## D1-s2-91 (new finding) — flow-bias fold containment

`coord._flow_bias.samples = -1` (the state flow_lift.py:210's guard exists to
refuse) makes `FlowCurveBias.observe` divide by zero. Five real
`coord._record_accuracy()` calls, with `_fold_flow_lift`'s other four gates
satisfied, all raise `ZeroDivisionError` and none reach the lead-time
accuracy scoring later in the same method (0/5). A null control at
`samples=0` never raises (0/5) and always reaches scoring (5/5).
`_async_update_data`'s caller wraps `_command_frequency` and
`_async_drive_pumps` individually so a failure there "never breaks the
cycle", but calls `self._record_accuracy()` unwrapped; the method's own
blanket `except Exception` (coordinator.py:4698) then turns *any* raise from
inside it into `UpdateFailed` for the whole cycle. Severity **medium**: bounded
(recovers next successful cycle) but a real, silent loss of that cycle's peak
tracking, accuracy scoring and energy-totals persistence, plus one failed
`DataUpdateCoordinator` cycle. Harness:
`tools/audit/round9/D1/s2/leads/lc_flow_bias_containment.py`.

## D3-s1-91 (new finding) — coordinator.py's now.tzinfo guards, gate-blind via HASTUB_TZ

Of the 5 sites the lead named, two shapes:

- **:586/:588 (`_comparable_ts`) and, by identical code, :6331** hardcode
  `timezone.utc` via `.replace(...)` rather than `.astimezone(...)` on a naive
  value — TZ-independent by construction. Measured directly: GUARD_OFF
  diverges from GUARD_ON identically under `TZ=UTC` and
  `TZ=Europe/Stockholm` (`comparable_ts_586_utc_blind=0`,
  `comparable_ts_588_utc_blind=0`). Not the UTC-blind pattern; **non-finding**
  against that specific hypothesis, filed as such (:6331 not separately
  executed within budget — identical guard text by inspection).
- **:8112/:8384** key on `dt_util.now().tzinfo`, which under this harness's
  stub is naive unless `HASTUB_TZ` is set — a knob no driver in these files'
  closure ever sets. Measured on `_immersion_dhw_margin` (:8384's guard):
  under the gate's default (`HASTUB_TZ` unset, `now` naive), GUARD_ON and
  GUARD_OFF are byte-identical (`0.0` vs `0.0`) — the guard is dead. Only once
  `HASTUB_TZ=Europe/Stockholm` (`now` aware) does GUARD_OFF diverge, and not
  silently: it raises `TypeError: can't compare offset-naive and
  offset-aware datetimes`. Same family as D3-s3-01 (a guard the gate's
  default environment can never exercise), governed by `HASTUB_TZ` rather
  than OS `TZ`. `class_guess=I1` (instrument: a guard whose deletion leaves
  the gate green). Severity **medium**. Harness:
  `tools/audit/round9/D3/s1/leads/lc_tz_probe_coordinator.py`.

## Lead 4 — optimizer.py:200, defrost.py:643 (closed)

Same in-memory guard on/off technique, `tools/audit/round9/D3/s2/leads/lc_tz_probe_optimizer.py`.
Both sites diverge from their GUARD_OFF variant under **both** `TZ=UTC` and
`TZ=Europe/Stockholm` on the tested (non-DST-crossing) scenario — a real,
TZ-independent behaviour change (`_utc_step_starts` returns aware instead of
naive datetimes; `_elapsed` returns `900.0` instead of `None` on a mismatched
pair), not the UTC-only-gate-blind pattern the lead hypothesized. Closed as
measured; a genuine DST-crossing scenario (crossing Stockholm's autumn
fallback) would be needed to test the full hypothesis and was out of this
batch's budget.

## Leads 5–6 — deferred entries, now-open owner D3-s3

D3-s3 has reported. Its findings (`D3-s3-01`..`05`), non-findings and leads
were read in full (`origin/handoff/audit-r9-find-B3`); neither
`tests/optimality.py` (`score_plan`/`pin_result`) nor `tests/entities.py`
(`_walk_flow_untouched`, the DHW-pre-fill check) is mentioned anywhere in that
report. The owner did not measure either lead. Both concern D3-scoped gate
coverage (mutation-suite blind spots), so re-measuring them here would need
the pool/prescreen/full-gate machinery tvofi's rule bars; closed with that
routing, per the rule's own fallback text ("carry to the fixer as a test to
add").

## Harnesses

- `tools/audit/round9/D1/s2/leads/lc_flow_bias_containment.py`
- `tools/audit/round9/D3/s1/leads/lc_tz_probe_coordinator.py`
- `tools/audit/round9/D3/s2/leads/lc_tz_probe_optimizer.py`

No mutation pool, mutant pool file or full-gate run was executed by this
seat; every RESULT line above comes from one of these three harnesses.
