# Sweep: N-silent-zero (round 11, D14 steps 3-4)

Class mechanism: a derivation's failure path returns the same empty value as its success
path, so a count over a set never enumerated reads as a clean zero. Ledger status:
`barriered`. The barrier is the census arm of `field_coverage.mjs`, which reaches only
registered count-printing instruments (structure.py `dead_*`). None of this round's six
findings is a registered instrument, so none is reached.
Findings: D10-s1-01, D10-s1-02, D15-s1-03, D15-s2-03, D15-s3-01, D17-s3-03.
Baseline: origin/handoff/audit-r11-register (28b864af6d).

## Enumerator

`python3 dev/audit/rounds/round11/D14/N-silent-zero/silent_zero_seams.py [--null] [--plant A|B|C1|C2|D1|D2]`

AST over `custom_components/heatpump_optimizer/` and `tools/replay/` (the debug-bundle
instruments D15 judged). It has one family per shape the findings took:

| family | rule | from |
|---|---|---|
| A absent == unparseable | a `parse`-named function that returns None from an emptiness guard and also returns a None-on-failure parse call | D10-s1-01 |
| B refusal acknowledged | an entity action handler that hands a coordinator action to `off_the_action` unawaited, or awaits one and discards a result the method can return non-None | D10-s1-02 |
| C1 sentinel zero | a measurement-named key published as literal 0 in the same dict as a not-run/failed status | D15-s3-01 |
| C2 no evidence passes | `if v is not None:` whose body rejects (`continue` / `return None|False`) with no else, so a missing value passes the filter | D17-s3-03 |
| D1 fixed denominator | `{N - len(x)}/N` with a literal N in a printed verdict | D15-s1-03 |
| D2 vacuous section | `<doc>.get(k) or {}|[]` in tools/: an absent section reads as an empty clean one | D15-s1-03 |
| D3 unloaded path | a silent `if not self._*_loaded: return`, and tools/replay builders without `enable_store_loads` | D15-s2-03 |

| run | result |
|---|---|
| baseline (positive control) | seams=42: A 1, B 2, C1 2, C2 18, D1 1, D2 17, D3 1. Every judged site is listed: away.py:622, button.py:156 and :217, coordinator.py:3220, snapshots.py:225, debug_ingest.py:297 and :97, coordinator.py:9653 |
| `--null` (clean fixture: distinct failure value, awaited and checked action, None sentinel, filtered evidence, derived denominator) | seams=0 |
| `--plant F`, one line of family F into the clean fixture | that family = 1, for each of A, B, C1, C2, D1, D2. D3's perturbation is the dynamic `replay_unloaded.py --perturb` below |

Outputs are under `D14/N-silent-zero/` in the report directory (`enumerate*.txt`).

## Probes written for this sweep

- `section_drop_probe.py BUNDLE`: drops one top-level section of a generated bundle (`dbg_bundle_gen.py --days 2`) at a time and reads `debug_ingest.py`'s own verdict. Null row (nothing dropped): pass 12/12. Still `pass 12/12` with `replay` (the judged D15-s1-03 site), `diagnostics`, `payload_snapshots` and `store_save_counts` dropped. Fails with `cycle_rows` (10/12), `manifest` (9/12), `schema` (11/12) and `stores` (10/12) dropped.
- `replay_unloaded.py FULL NOSTORES`: the real `debug_replay.main` on one bundle with and without `stores`. `SnapshotRing.observe_bias` calls go 96 -> 0, the 15 RESULT lines are identical, and no line names the unloaded state: `unloaded_replay_reads_clean=1`. `--perturb` (`enable_store_loads` forced on): 96 calls, 0.
- `legionella_unparseable.py`: `LegionellaGuard.async_load` on a fake store. A valid `last_cycle` is kept. An absent one becomes now (the fresh-install rule). Two unparseable strings also become now, are saved back, and log no WARNING: `unparseable_read_as_fresh=2`. `--perturb` (warn on a present but unparseable value): 0. The store boundary does not stop it: `_sanitize` passes "a non-numeric string the loader will refuse on its own" (store.py:111-117), and `_bound_instants` returns an unparseable instant unchanged (store.py:157-161).
- `defrost_unreadable_grid.py`: `DefrostDerate.from_dict` (v2) with the `factors` grid present but unreadable (wrong rows, wrong width, string, dict, scalar). All 5 load exactly like an absent grid (defaults, no WARNING, nothing recorded): `unreadable_read_as_absent=5`, and the valid round trip is kept. `--perturb`: 0. Whether the thermal-learning store boundary would admit such a document was not driven; the probe is at the loader.
- The finder's `D15/s1/ingest_checks.py` on the generated bundle with `--empty stores`: `stores-declared` and `stores-sanitize-idempotent` pass with 0 items, but `stores-present` fails, so the verdict reads fail.

## Seams (42) and dispositions

### Judged sites (beyond_finding false)

| seam | finding |
|---|---|
| A away.py:622 `_parse_return_time` | D10-s1-01: an unparseable `return_time` clears the stored return (probe `D10/s1/svc_set_away.py`) |
| B button.py:156 `SystemIdentificationButton.async_press` | D10-s1-02 (probe `D10/s1/btn_actions.py`) |
| B button.py:217 `DiagnoseIntervalButton.async_press` | D10-s1-02 |
| C1 coordinator.py:3220 `_apply_unsolved_payload` `"solve_time_ms": 0` | D15-s3-01: `debugger._solver_smoke` folds it as a 0 ms solve (probe `D15/s3/m7_rowscan.py`) |
| C2 snapshots.py:225 `SnapshotRing.best_restore` | D17-s3-03 (probe `D17/s3/f03_restore_unevidenced.py`) |
| D1 debug_ingest.py:297 `main` `/12` and D2 debug_ingest.py:97 `ingest` `bundle.get('replay') or {}` | D15-s1-03 (one judged site in two lines). `section_drop_probe.py`: drop replay -> pass 12/12 |
| D3 coordinator.py:9653 `_async_watch_learning_drift` | D15-s2-03: the load gate the null bundle never opens (probe `D15/s2/m6_null_ring.py`) |

### Instances beyond the findings: 3

| seam | probe |
|---|---|
| C2 legionella.py:224 `LegionellaGuard.async_load` | `legionella_unparseable.py`: unparseable_read_as_fresh=2 (`--perturb` 0). A corrupt stored disinfection time reads as "disinfected now", is saved over the evidence, and the next anti-legionella cycle is due a full interval later, silently |
| C2 defrost.py:577 `DefrostDerate.from_dict` | `defrost_unreadable_grid.py`: unreadable_read_as_absent=5 (`--perturb` 0). A learned derate grid that cannot be read loads as never learned, with no log and no counter (cell-level failures are counted in `reset`; a whole-grid failure is not) |
| D2/D3 tools/replay/debug_replay.py:200 `main` `bundle.get('stores') or {}` | `replay_unloaded.py`: observe_bias 96 -> 0 with identical RESULT lines (`--perturb` 96). A bundle downloaded without stores replays with every load-gated path dark and reads as the seeded run. This is D15-s2-03's mechanism in the replay tool rather than the generator |

### Guarded: 8

- C1 coordinator.py:3231 `"pv_self_consumed_kwh": 0.0`: nothing folds it as a measurement. The sole reader (sensor.py:2275) republishes it as an attribute beside the payload's `optimization_status: not_run`, and no spread, sum or count reads it.
- D2 debug_ingest.py:88 `manifest`: dropped -> fail 9/12 (manifest-cycles, manifest-version).
- D2 debug_ingest.py:92 `cycle_rows`: dropped -> fail 10/12 (rows-match, bias-rederived).
- D2 debug_ingest.py:112 `stores`: dropped -> fail 10/12. `stores-present` fails, though two sibling checks pass with 0 items.
- D2 debug_ingest.py:65 `unwrap_download` `doc.get('data') or {}`: an unwrapped empty bundle fails `schema` (dropping schema -> 11/12, fail).
- D2 debug_replay.py:199 `bundle.get('replay') or {}`: an absent replay half crashes `run_seeded` (traceback), loud, not clean.
- D2 debug_replay.py:110 `trim_replay` and :180 `gate_checks` `.get('states') or {}`: they read the replay the run itself needs, and with no replay the run fails as above.

### Not applicable: 24

- C2, a reason-returning predicate whose None is its "nothing to refuse" success by contract, not missing evidence: coordinator.py:973 `_fold_flow_lift`, :9246 `_track_curve_comfort`, :10987 `_record_quiet_comfort_period` (`_learning_frozen(..) is not None`), :11068 `_run_system_identification` (`why`), early_cutoff.py:305 and :313 `on_room_event` (`_exempt`, `reason`).
- C2, an optional parameter or handle, not evidence: coordinator.py:2816 `_hub` / `_hub.set` (ctx present; listed twice by the nested walk), :5415 `_fold_cop_evidence` (`read_scale` routes a held interval), optimizer.py:5219 `_safety_release_steps` (`space_pins` optional), pump_arbiter.py:2053 `note_supply` (unsubscribe handle), sysid.py:1476 `arm` (`plant` optional), grid_fee.py:164 `FeeRule.applies` (`hours` None means every hour, by configuration).
- C2 disinfection.py:178 `release`: None (unread) goes to its own explicit branch (the `_unreadable_since` timer), so it does not pass as clean.
- C2 sensor.py:2046 `_waiting_for`: returns None because a value exists; the inverse direction.
- D2 debug_ingest.py:164 `diagnostics.accuracy` (listed twice): `live_deque_bias` is printed as `None`, labelled, and judged by no check. `bias-rederived` compares store window against rows only, so dropping diagnostics changes no verdict by design.
- D2 debug_replay.py:212 `verdict.get('counts') or {}` and :216 `results`/`agreement` (listed twice): the tool reading its own verdict dict, which `run_seeded` always builds.
- D2 export.py:186 and :189 `untimed` (window, states): the export builder shaping a document, not a verdict or count.
- D2 dbg_bundle_gen.py:98 `recording_tick` `current_action or {}`: the synthetic generator's recorder, not a judgement.

Not seams (no rule reads them), but seen by the section probe: `debug_ingest.py` does not read
`payload_snapshots` or `store_save_counts` at all, so dropping either leaves pass 12/12. They
are unjudged sections, not silent zeros.

Totals: 42 = 9 judged-site lines (7 judged seams) + 3 instances + 8 guarded + 24 not applicable
(counting each listed line, the duplicates included). `instances` = 3.

## Barrier implication

The ledger's barrier (census arm, registered instruments only) reaches none of the seven
judged seams or the three new instances. Proposed:

1. A store-loader rule: a loader that reads a present but unparseable field (instant, grid) logs and records it rather than falling into the absent path. The legionella and defrost probes are its controls.
2. Register `debug_ingest.py` and `debug_replay.py` in `field_coverage.mjs`'s census with planted section drops. Every bundle section a verdict depends on must move the verdict when it is dropped, and the replay must name whether store loads ran.
3. Families B and C1 as tests/ lint rules: no unawaited coordinator action in an entity handler, and no 0 sentinel beside a not-run status.

AST cost is under a gate second. The section-drop census runs `debug_ingest` 9 times on a 2-day bundle (~10 s). Not built here.
