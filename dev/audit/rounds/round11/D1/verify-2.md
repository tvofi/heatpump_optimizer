# Round 11, D1 verifier unit 2 (finder seat D1-s3)

Verifier contract: `dev/governance/roles/verifier.md`. Worktree `audit-r11-verify-D1-2` at
`handoff/audit-r11-register` (28b864af6d). All seven findings are scope D1-s3, a planted-tree
scope: every number below, finder harness and mine, was taken in the private export copy
`audit-r11-px-D1-2` (copied from `plant-export/audit-r11-baseline`; its round-11 D1/s3
evidence was already present and identical to the branch's), with `PYTHONPATH=tests/hastub`
and the venv-ci interpreter. The one exception is the real-Home-Assistant Store probe for
D1-s3-05, run in `venv-ha` (homeassistant 2026.9.3) outside any tree. My harnesses are under
`dev/audit/rounds/round11/D1/verify2/`. No number is a timing except where noted; load1 was
35-150 throughout (shared box, other seats running).

| id | V1 finder harness (perturbed; null) | V2 mine | V3 reach | class | seam_rule enumerates | vote |
|---|---|---|---|---|---|---|
| D1-s3-01 | 10 (0; null 0) | 12/12 non-finite tokens read as a flag, all True; strict=True also 12; finite tokens disagree 0/6 | yes, narrow | P1 | only the demonstrated seams | verify, medium |
| D1-s3-02 | 3 (0; null 2 numerics still accepted) | 9/9 bool payloads accepted (incl. bytes, nested command, effective_displace) | yes | P1 | only the demonstrated seams | verify, low |
| D1-s3-03 | 3 (0; null 0) | 3/6 extreme stamps raise OverflowError in mean_over (0001-01-01T00:00..00:59); null mean 100.0 | narrow: fixed first-party HTTPS URL | P1 | partly | weaken, low |
| D1-s3-04 | lock held 1 (perturb 0; null timeout arm 0) | 4/4 transport routes leave _PROCESS_LOCK held >3 s; null timeout route 0 | yes, conditional on a D-state child | P2 | yes (1918 and 2106) | verify, medium |
| D1-s3-05 | 10/10 (perturb 9; control 9/9 + 9/9) | 7/7 coordinator save methods silent above DEBUG on a payload-build fault | partly: real HA Store never raises a save failure | new | yes (17) | weaken, low |
| D1-s3-06 | 3 (perturb 0; null recovered=1) | 5/5 ERROR+traceback over 5 failures; null UpdateFailed 0 | yes | N-log-flood | yes | verify, low |
| D1-s3-07 | 7 of 11 (perturb 6; four helper-loggers 10/14/10/20) | static 30 silent broad handlers; all 7 named are in it | yes | new | yes (34) | verify, low |

## D1-s3-01 parse_bool non-finite flag

- V1: `parsers_fuzz.py --arm pump`: `pump_nonfinite_flag_true=10`, `pump_nonfinite_freeze_fault=5`;
  `--perturb parse_bool_finite` gives 0 and 0 (moves to zero as stated); null
  `pump_null_control_zero_flag_true=0`. load1 45.77, thread_factor 1.000. Exact match.
- V2 (`verify2/v2_parsers.py`): metric is the number of non-finite tokens for which `parse_bool`
  returns a flag while `const.finite_float` refuses the same token. Result 12/12 (nan, NaN, NAN,
  " nan ", inf, -inf, +inf, Infinity, -Infinity, 1e309, -1e309, 1e999), all True; `strict=True`
  also 12. Null: 0/6 disagreements on finite tokens.
- V3: real HA 2026.9.3 `SensorEntity` refuses a non-finite value only when the sensor is numeric
  (`sensor/__init__.py:747`); a raw code sensor with no unit or device class, a template or MQTT
  sensor, or a `states.async_set` writer still publishes "nan"/"inf". Reachable, narrowly.
  Consequence (fault=True, learning frozen) holds severity at medium. Class P1 confirmed. The
  seam rule greps `parse_bool|_parse_ecl110_state` out of the 31 `d1-parsers` lines, so it names
  only the demonstrated seams, not every flag or number reader.
- Attacks: contention (count, immune); stub reach (above); null present and zero. Vote verify.

## D1-s3-02 ECL110 bool displacement

- V1: `--arm ecl110`: `ecl110_bool_accepted=3`; `--perturb ecl110_refuse_bool`: 0, with
  `ecl110_numeric_null_control=2` in both runs. load1 35.46. Exact.
- V2: `_parse_ecl110_state(payload, (-10, 10))` over 9 boolean-carrying payloads (Python bools,
  'true', 'false', the dict forms, the nested `command` form, a bool `effective_displace`, bytes
  `b"true"`): 9/9 return a bool read as a number. Null: "3" and `{"displace": 3}` give 3.0.
- V3: the MQTT payload is whatever the configured topic publishes; reachable in real HA. 0 and 1
  sit inside every displacement window. Severity low (wrong published displacement, no control
  write shown). P1 confirmed. Seam rule names only the two demonstrated seams. Vote verify.

## D1-s3-03 Open-Meteo year-1 stamp

- V1: `--arm openmeteo`: `openmeteo_year1_solve_failures=3`, `failed_updates=0`; perturb 0;
  null `openmeteo_healthy_solve_failures=0`. load1 68-73. Exact.
- V2: `_parse_block` keeps every extreme stamp (73 of 73 samples). Then `mean_over` on a 15-minute
  window: 3/6 stamps raise OverflowError (0001-01-01T00:00, T00:30, T00:59). T01:00 and the two
  9999 stamps do not raise. Null series mean 100.0. The defect is real but narrower than "a
  year-1 stamp": only a stamp within one resolution of `datetime.min` overflows.
- V3: the URL is the fixed constant `OPEN_METEO_FORECAST_URL`/`SATELLITE_URL` over HTTPS. The
  trigger needs the provider itself to emit a year-1 stamp, which its time-windowed API does
  not do. The failure is booked and logged once (log_held), not silent. Consequence would be
  medium, but the trigger is close to unreachable, so I weaken to low. P1 confirmed. The seam rule
  covers the Open-Meteo parse seam; it does not enumerate the other external-instant parsers
  (Tibber `startsAt`, the weather forecast datetimes), so it covers part of the phenomenon.
- Vote weaken (low), with the executed 3/6.

## D1-s3-04 unbounded wait under _PROCESS_LOCK

- V1: `peer_wait.py`: `transport_returned_within_cap=0`, `transport_lock_held_after=1`; null arm
  `timeout_returned_within_cap=1`, `timeout_lock_held_after=0`; `--perturb`: transport 1/0. load1
  80.97, thread_factor 1.598 (perturb 2.053). The 8 s cap is a deadline, not a timing RESULT.
- V2 (`v2_peer.py`): a fake worker whose kill() is a no-op and whose untimed wait() blocks. Four
  transport routes (write BrokenPipeError, flush OSError, reply EOFError, reply
  ConnectionResetError) all leave a fresh `_PROCESS_LOCK` unacquirable after 3 s: 4/4. The null
  ProcessWorkerTimeout route gives 0.
- V3: real `subprocess.Popen.wait()` blocks until the child is reaped, and SIGKILL does not end a
  child in uninterruptible sleep (an SD-card I/O stall on a Pi). Reachable, but only when the
  transport fails while the child is still alive and stuck; a broken pipe usually means the
  child already died, and then wait() returns at once. Consequence (every later solve wedged,
  last_update_success never False) keeps it at medium. P2 confirmed: the timeout arm and the
  transport arm decide the same wait two ways. Seam rule (`silent_peer_waits.py --scan`) lists
  both untimed waits, coordinator.py:1918 and :2106. Vote verify.

## D1-s3-05 persist handlers log failures only at DEBUG

- V1: `persist_family.py`: `persist_silent_at_warning=10` of `persist_reached=10`; `--perturb`:
  9 of 10. Control `excepts_inject.py --reach`: `control_proc_phases_ok=9/9`,
  `control_inproc_phases_ok=9/9` (load1 117.83, thread_factor 27.238, provisional; counts are not
  timings). Leave-one-out: every handler has `added_warning=0` on its own, so dropping any one
  leaves 9/9.
- V2 (`v2_persist.py`): the 7 coordinator `_async_save_*` methods called on a self whose payload
  attributes are missing, which is the programming-error route. Result 7/7 neither raise nor log
  above DEBUG; each logs one DEBUG.
- V3, which corrects the claim: `v2_realstore.py` in venv-ha with real HA 2026.9.3 `Store` and a
  real `HomeAssistant`. A non-serialisable payload and an unwritable file both give
  `async_save` raised 0/2 and ERROR logged by HA 2/2 ("Error writing config for ..."); the
  healthy case logs 0 errors. Upstream catches `SerializationError` and `WriteError` itself
  (`helpers/storage.py:588`). `QuarantiningStore` does not override `async_save`. So "a failing
  save silently stops persisting" does not happen in real HA: HA logs it at ERROR. The hastub
  `Store.async_save` raises on a non-serialisable payload, which `tests/ha_contract.py` records as
  "matching the real Store"; that record is wrong for a save. What stands is a payload builder
  that raises (an AttributeError in an `as_dict`), swallowed at DEBUG on every cycle. Severity
  low. Class new, in the same family as D1-s3-07. The seam rule (`persist_seams.py`) lists all 17
  handlers.
- Vote weaken (low).

## D1-s3-06 ERROR+traceback every failed cycle

- V1: `log_flood.py`: `repeat_error_records=3`; `--perturb`: 0; null `recovered=1`. load1
  115-119. Exact.
- V2 (`v2_flood.py`): unbound `_async_update_data` with `_update_current_state` raising a
  persistent RuntimeError gives 5 ERROR records with exc_info over 5 calls (once per outage would
  be 1). Null: UpdateFailed gives 0.
- V3: the stub's DataUpdateCoordinator logs only on the transition
  (`tests/hastub/.../update_coordinator.py:201`), as upstream does, so the integration's own ERROR
  is the only per-cycle record. Reachable for any persisting unexpected exception. Severity low.
  The class N-log-flood fits its mechanism, but the record is ERROR rather than WARNING. Seam rule
  lists both broad arms (6148, 6195). Vote verify.

## D1-s3-07 broad handlers with no record

- V1: `silent_broad.py`: `silent_broad_no_record=7` of `silent_broad_reached=11`; `--perturb`: 6.
  The four separating handlers (6507, 7103, optimizer 1944, 1970) add 10, 14, 10 and 20 records.
  load1 87-97. Leave-one-out: each of the 7 has `added_records=0` on its own.
- V2 (`v2_silent.py`): my own AST definition counts broad handlers whose body has no raise and no
  call whose name contains log, warn, debug, error, exception, `_failed` or note. 30 in the
  package; all 7 named handlers are in it.
- V3: reachable; real HA does not change logging here. Three of the 7 (CoordinatorDiagnostics.of,
  diagnostics :339, :367) leave a visible marker in the diagnostics download, so 4 are truly
  invisible. Consequence only surfaces with a second defect behind it, so severity is low. Class
  new. Seam rule `--seams` lists all 34. Vote verify (low).
