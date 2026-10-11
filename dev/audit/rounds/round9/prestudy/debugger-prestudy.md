<!-- Landed from handoff/r9-dbg-0 @ eae236d66; paths and file:line citations are as measured at its baseline origin/main ed0151ad2, before the R9-RO reorganisation moved tools/audit/round9/ under dev/audit/rounds/round9/. Body transcribed verbatim; this comment is the only added line. -->
# R9-DBG-0 pre-study: the debugger module and the repo-side debugger harness

Seat: R9-DBG-0 (STUDY, wave 1). Owner ask (tvofi, 2026-10-04): (A) an
integration-side debugger module that, when activated, collects relevant data
from a live install for up to a week or until stopped and makes it available
via a download-diagnostics surface, with optional non-intrusive self-tests
(<= 15 minutes total); (B) a repo-side harness an agent runs against the
downloaded bundle, supporting an agentic debugging seat. HARD CONSTRAINT:
existing code first, per-component reuse naming, anything duplicating an
existing surface is refused here, in the pre-study itself.

Baseline: `origin/main` at `ed0151ad2` ("ci: record nightly kills"), seat
worktree `/Users/timmalmstrom/hpo-seats/r9-dbg-0/wt`, branch
`handoff/r9-dbg-0`. Every figure below names its instrument; prototypes live
beside this doc (`dbg_bundle_gen.py`, `dbg_ingest_smoke.py`) and their runs
under `runs/`.

## 0. The one-paragraph answer

The feature is an extension of a pair that already exists, not a new
architecture. `tools/replay/export.py` already collects days from a live
install into a sanitised, allowlisted download (`hpo-replay/1`, state history
plus config entry); `tests/replay.py:run_fixture` already replays such a
document through the real coordinator tick cycle by cycle under a frozen
clock. The debugger **module** adds the missing half of collection — the
integration's own learned `.storage` documents, a slim per-cycle row, and a
daily payload snapshot, ring-bounded to a week — behind the existing options
toggle, button, service and HA-native "Download diagnostics" surfaces. The
**harness** is `run_fixture` plus a store-seeding stage and the monitor
loaders (`AccuracyTracker.from_dict`, `Cusum`, `SnapshotRing`), emitting the
replay lane's own invariant verdicts plus a leak gate
(`export.violations`). Both halves are prototyped below on a synthetic week;
neither adds a new transport, a new UI page, or a new persistence mechanism.

## 1. Existing-code inventory (the HARD CONSTRAINT, per component)

What exists, what the debugger reuses of it, what it adds. A new committer
can point at each piece:

| component | where it lives | what the debugger reuses | what it adds |
|---|---|---|---|
| HA-native diagnostics download | `custom_components/heatpump_optimizer/diagnostics.py:123` `async_get_config_entry_diagnostics`; quality_scale.yaml already `diagnostics: done` | the download surface itself, its redaction (`TO_REDACT` = Tibber token + name, `diagnostics.py:45`), coordinate coarsening (`_coarsen`, `diagnostics.py:42`), and the coordinator snapshot shape (`_coordinator_snapshot`, `diagnostics.py:81`) | include the finalized bundle (bounded, section 3) in the returned dict |
| live-install day export | `tools/replay/export.py` (`hpo-replay/1`): recorder SQLite read-only, `.storage` entry/registry/config, allowlist sanitiser, `violations()`/`check_file`, self-search for removed strings | the replay half of the bundle is an export document; `export.violations` is the harness's privacy gate; `synthesize.py` regenerates the committed fixture through it | the stores, slim rows and snapshots alongside the export document |
| replay lane | `tests/replay.py:718 run_fixture` — real `_async_update_data` per cycle, frozen clock, weather service + price overrides, entity sweep, invariants `finite/unit/no_default/agreement/cycle/not_frozen/cycle_cost`; nightly job | the harness's replay stage is `run_fixture` over the bundle's replay half; the judges come free | a store-seeding stage (write the bundle's store documents into the HA-stub `Store._DISK` before coordinator construction) |
| store machinery | `store.py:511 QuarantiningStore`, `DOMAINS` table (`store.py:275`), `.storage/heatpump_optimizer_<entry>_<suffix>` keys, `_sanitize` (`store.py:105`) | the debugger ring persists through the same `QuarantiningStore` with a `DOMAINS` declaration, so quarantine, version refusal and the `store_version` repair issue apply to it | one new store key (`..._debug`) + one `DOMAINS` entry |
| snapshot machinery | `snapshots.py` (`RING_SIZE=8`, weekly, every learner's `as_dict()`, `best_restore`) | collected in the bundle verbatim; harness re-runs `observe_bias`/`best_restore` offline | nothing |
| accuracy / drift monitors | `accuracy.py` (`AccuracyTracker`, 672-deque, `as_dict` persists 192, `summary`), `drift.py` (`Cusum`), `coordinator.py:9371` the `accuracy_drift` repair latch | bundle carries the accuracy store doc; harness re-derives bias/MAE/trust from it (prototyped, stage 4) | nothing — both are already Home-Assistant-free and JSON-serialisable |
| services pattern | `services.py:977 async_register_services`, `ServiceValidationError` + translation keys, `diagnose_interval` (`services.py:966`) as the report-shaped precedent | a `debug_collect` start/stop service pair follows the registration, schema and translation pattern exactly | two service handlers |
| button pattern | `button.py` `_OptimizerButtonBase` + `DiagnoseIntervalButton` (`button.py:171`), `off_the_action` (`entity.py:224`) for long work | a "finalize debug collection now" button | one button class (~30 lines) |
| options surface | `config_flow.py:1534 _OPTION_PAGES` (the `learning` page is literally "Self-learning and diagnostics"), `_OPTION_FIELDS` `_F(...)` rows, `_save` merge, `async_update_options` reload-on-change (`__init__.py:359`) | the activation toggle is one `_F("learning", CONF_DEBUG_COLLECT, False, bool)` row; it reaches the coordinator as `ctx._config` after the standard reload | one field + one const |
| background-task lifecycle | `entry.async_create_background_task`, coordinator `_spawn` (`coordinator.py:2449`) with `async_shutdown` reaping (`coordinator.py:5796`) | the collector task rides the same spawn/reap; unload cancels it for free | nothing |
| coordinator tick hook | `_async_update_data` (`coordinator.py:5106`) returns `_build_data_dict` (`coordinator.py:7611`) | the slim row is built from the tick's own return value — no recomputation (prototyped: the wrapper costs one dict read per cycle) | the row builder in the new module |
| payload contract | `payload.py` (`Payload` TypedDict, view slices; `tests/golden/coord_all_features.json` a full solved payload fixture) | the daily snapshot is `_build_data_dict`'s output verbatim | nothing |
| input health | `InputHealthBinarySensor` (`binary_sensor.py`): `problem_inputs`, `input_ages_minutes`, `learners_frozen` | the sensor-sanity self-test re-uses the input-health view over collected rows | nothing |
| self-test solver ruler | `tests/stress.py:639 reference_solve` (iteration-capped, fixed-cost); `coordinator.async_simulate` (`coordinator.py:11131`) solves without actuating | the solver smoke is `reference_solve` + one `async_simulate` over collected prices | nothing |
| harness canon | `tools/audit/README.md` "The harness contract" + `tools/audit/harnesses/README.md` (instruments are kept); the r9-diag-1 replay harness (`origin/handoff/r9-diag-1`, not on main) as the leanest driver pattern | the harness follows the header/BLAS-pin/RESULT/named-perturbation/null-control canon; both prototypes below follow it | nothing |
| code-path map | `tests/seam_map.json` (every coordinator method's seam, the round-9 integration pre-study's inventory) | the harness maps observed anomalies to seams by lookup | nothing |
| leak probes | `export.py` sanitiser self-search; `tests/replay.py` `LEAK_PROBES` (~20 private-data shapes, nightly + cheap half on PRs) | the bundle gate runs `export.violations` (prototyped, catches a planted credential) and the seat brief requires the nightly probes over the fixture half | nothing |

Refused duplicates (the constraint's teeth) are in section 6.

## 2. (a) The collection set — item, debugging question, size, privacy

Instrument for all week-size figures: `dbg_bundle_gen.py --days 7` on this
seat (venv-ci, numpy 2.4.6 / scipy 1.17.1); the run also records the replay
lane's own cost figures (`cpu_ratio 0.87`, `loop_cpu_ratio 0.28`, 24.8 s
wall for 336 cycles — a size/count measurement, contention-immune). The
synthetic week is the committed DHW-only fixture repeated day by day, so
store counts are a **floor**: a full-feature install runs up to 15 stores
(`store.py DOMAINS`) and the snapshot ring (several hundred KB steady state,
per the round-9 D1 store survey), not the 5 stores the synthetic week saved.

| item | debugging question it answers | week size (instrument above) | privacy |
|---|---|---|---|
| replay half: state history of every mapped input + published entity, config entry (`hpo-replay/1` via `export.py`) | what did the model actually see, cycle by cycle; when did an input go stale or jump | 627,795 B raw (synthetic; grows with input count) | `export.py` allowlist: credential keys dropped anywhere, coordinates cut to 2 dp, attribute-key allowlist, text-shape rules, self-search refuses to write if a removed string survives. Known residual (its own docstring): user-named entity ids and short text states can embed names — a person reads the file before it is shared; the bundle inherits exactly this contract |
| slim per-cycle row: `t, mode, action_mode, action_kw, heat_pump_on, solve_wall_ms, payload_solve_time_ms, solve_failures, prices_rows, weather_stale_h, indoor/outdoor/dhw temp, accuracy_sample` | did the solve run, how long, what did it command, what did it predict vs what happened | 155,771 B raw (463 B/row mean x 336 cycles) | numeric + enum fields only; no ids beyond those already in the replay half |
| daily payload snapshot (`_build_data_dict` output, one per day) | the full published contract at a moment: plan trajectories, learner views, grid view — anything not derivable from slim rows | 592,832 B raw (7 x ~84.7 KB; D9-s2 measured the live data dict at 75.8 KB/cycle on a full install) | rides `diagnostics.py` redaction before storage: `TO_REDACT` (token, name), `_coarsen` 1 dp coordinates |
| the integration's own `.storage` store documents (accuracy, dhw_accuracy, thermal_learning, price_model, ledger, snapshots, ...) | learner state, drift cusums, alarm streaks — can an offline seat reproduce the `accuracy_drift` latch and `best_restore`? | 54,544 B raw synthetic (floor); full installs larger (snapshot ring + ledger) | store documents are already domain-bounded by `QuarantiningStore`; entry options enter as **key names only** (the `diagnostics.py` precedent), never values |
| diagnostics snapshot (`_coordinator_snapshot`, reused verbatim) | the point-in-time view users already download today | 1,637 B | its own redaction, unchanged |
| manifest (schema, integration `VERSION`, HA floor, cycle count, replay verdict, generator) | which tree produced this bundle; does the week pass the replay lane's own invariants | < 1 KB | version strings only |

**Week total (synthetic floor): 1,435,346 B raw, 132,629 B gzipped
(gzip -6).** A full-feature install upper estimate is 2-4 MB raw / < 0.5 MB
gzipped (added stores and snapshot ring; the two largest sections stay
dominant). On the Pi-class target (D9's brief; CPU factor 4-6x assumed,
D9-s1's own extrapolation note), collection cost per cycle is one dict read
over data the tick already built, against D9-s2's measured 26.7 ms loop
CPU/cycle (`tools/audit/round9/D9/s2/loop_work.py`), and the ring persists
once per hour, not per cycle: measured existing write volume in the
synthetic week (`store_save_counts` in the manifest) is accuracy 336 +
energy 336 saves/week already; the debugger adds 168 hourly ring saves —
under a third of the install's existing store-write volume, no new write
mechanism.

Privacy pass, named: (1) no credential, token or auth value is ever read —
the collector reads coordinator state and mapped input states only;
(2) `CONF_TIBBER_TOKEN` and `CONF_NAME` redacted at capture
(`diagnostics.py:45 TO_REDACT`); (3) latitude/longitude coarsened — note the
**open discrepancy**: `diagnostics.py` coarsens to 1 decimal (~11 km),
`export.py` to 2; the bundle should ride the coarser rule for its extra
sections, and unifying the two is an owner decision recorded in section 8;
(4) entry options as key names only; (5) the leak gate runs at download time
and the harness runs it again at ingest (prototyped both arms).

## 3. (b) Activation, stop and download surface

- **Activate**: an options toggle on the existing `learning` page
  ("Self-learning and diagnostics", `config_flow.py:1534`), one `_F` row.
  Activation takes effect through the standard reload
  (`async_update_options` compares `effective_config` and reloads), so the
  collector starts on setup and, because the ring lives in the
  `..._debug` store rather than memory, a reload or restart mid-week does
  not lose collected days.
- **Auto-stop**: 7 days of rows (ring drops the oldest day beyond 7); the
  toggle stays on but the bundle is final until cleared.
- **Stop/finalize now**: one button (`button.py` pattern,
  `DiagnoseIntervalButton` precedent) running the self-tests
  (`off_the_action`, so the press returns immediately) and marking the
  bundle final; plus a `debug_collect` service pair (start/stop/status)
  following `services.py` registration + translation pattern, for
  automation. A `SupportsResponse.ONLY` status service answers "how many
  days, how many bytes" — the `simulate_plan` precedent.
- **Download**: HA's native "Download diagnostics" on the config entry
  (three-dot menu) — the card already routes users there
  (`www/heatpump-optimizer-card.js` `health.act_diagnostics` navigates to
  settings). `diagnostics.py` includes the finalized bundle in its returned
  dict, **capped**: if the bundle exceeds a stated byte cap (proposed 8 MB
  raw; no documented HA-side cap exists in-tree — section 8), diagnostics
  returns the summary plus a pointer to the store file instead. The bundle
  additionally persists as the `..._debug` store document under `.storage/`
  so it is manually retrievable even when oversized.

Nothing here creates a new page, a new HTTP route, or a new file-serving
surface.

## 4. (c) The self-test set (<= 15 minutes, non-intrusive)

Priced on this seat's venv (instruments named); Pi figures scale by D9's
assumed 4-6x factor. All tests read collected data and coordinator state;
none actuates the pump and none opens a network connection.

| self-test | data it adds | price (instrument) |
|---|---|---|
| store round-trip per store: `as_dict -> from_dict -> compare`, plus `QuarantiningStore` quarantine report | does restore work on *this* install; which leaf is off-domain (the corruption class `store.py` quarantines) | the synthetic week's whole store corpus is 54,544 B — sub-second; 15 stores well under 1 s here, seconds on a Pi |
| accuracy monitor re-derivation: bias/MAE/trust recomputed from the store's 192-sample window vs the live 672-deque summary | monitor disagreement — the prototyped window mismatch (0.054 vs 0.015, section 5) is exactly the kind of fact this test surfaces on a real install | instant (192 samples; `dbg_ingest_smoke.py` stage 4) |
| solver smoke: `tests/stress.py:reference_solve` once (fixed-cost ruler) + one `coordinator.async_simulate` over the collected final-day prices | does the solve converge on this install's own inputs, and where does `solve_time_ms` sit against the week's recorded distribution | `reference_solve` measured 20.2 ms wall/call here (3-call mean after warm-up, venv-ci); one replayed cycle averages 74 ms (24.8 s / 336 cycles, `dbg_bundle_gen.py`); < 1 s on a Pi |
| sensor sanity: the input-health view (`problem_inputs`, `input_ages_minutes`, `learners_frozen`) evaluated across the week's slim rows | which inputs went stale or implausible, and when — the D8 ordering questions answered from data | pure function over rows; sub-second |
| feed health summary: `prices_rows`, `weather_stale_h`, `_tibber_outage_cycles` trends over the week | was a bad plan caused by a starved feed | read from rows; instant |

Total measured cost: **seconds on this box; comfortably minutes on a Pi with
a maximal store corpus.** The 15-minute budget is a ceiling, not a target;
nothing in the set is priced anywhere near it, which is the point of pricing
them — the budget exists for the store round-trip on a very large ledger.

## 5. (d) The bundle format — prototyped

`hpo-debug/1`. Writer and synthetic-week generator:
`tools/audit/round9/prestudy/dbg_bundle_gen.py`; run and outputs under
`runs/`. Shape (all sections present in the committed run):

```
{ "schema": "hpo-debug/1",
  "manifest":  { generated_at, generator, integration_version, days, cycles,
                 replay_verdict <run_fixture's own verdict dict>, ... },
  "replay":    <a complete hpo-replay/1 document: entry, window, inputs, states>,
  "cycle_rows": [ one slim row per cycle, section 2 ],
  "payload_snapshots": [ {cycle, data} one per day ],
  "stores":    { "<full store key>": <document> },
  "store_save_counts": { ... write-cadence evidence ... },
  "diagnostics": <_coordinator_snapshot output, reused verbatim> }
```

Measured on the synthetic week (7 days, 336 cycles, 5 stores): raw
1,435,346 B, gzip -6 132,629 B; sections: replay 627,795 / snapshots
592,832 / rows 155,771 / stores 54,544 / diagnostics 1,637. Perturbation
arm (`--days 1`): 215,933 B raw, 24,042 B gz, 48 cycles, 1 snapshot —
scales as claimed.

Free corroboration the prototype produced: the reused replay judges ran over
the whole synthetic week and returned **one `agreement` offender**
(`2026-01-15T23:00+00:00 sensor.heatpump_optimizer_heat_pump_action:
power_kw 4.0 while the plan's current step...`) and empty `finite/unit/
no_default/cycle`. A debugging seat gets those verdicts for nothing because
the bundle rides `run_fixture`. The offender does not reproduce on the tail
day (`dbg_ingest_smoke.py` stage 5: `agreement=0`) — it is either an artifact
of the day-repetition in the synthetic fixture or a genuine finding; its
disposition belongs to the harness group (section 8).

## 6. (f) Scope refusals (what must NOT be built, and what refused it)

1. **A second download transport** (custom `HomeAssistantView`, websocket,
   or serving the bundle from `frontend.py`'s static path): duplicates HA's
   native diagnostics download, which the card already routes users to;
   `frontend.py`'s `StaticPathConfig` is read-at-register-time and cannot
   serve generated content. Adding one is a new attack surface for zero new
   capability.
2. **Live streaming / a real-time debugger dashboard**: the recorder and the
   card already visualise live state; debugging questions are answered by
   offline replay, and streaming costs Pi CPU the D9 brief spends elsewhere.
3. **Remote upload or telemetry of any kind**: the bundle contains home
   energy data; it stays on the box until the user downloads it. Also
   refused: any "send to developer" affordance.
4. **Recording the full 75.8 KB payload dict every cycle**: 25 MB/week raw
   for data derivable from the slim rows plus inputs — `diagnostics.py`'s
   own docstring already refuses "large, and derivable" content; daily
   snapshots bound it at ~0.6 MB.
5. **Reading the recorder SQLite from inside the integration**: `export.py`
   already does this repo-side behind a strict allowlist with a self-search;
   forking that sanitiser into the package would create two privacy gates
   that drift. The collector records at cycle boundaries and on listener
   updates it already receives; sub-cycle sensor behaviour is a stated,
   accepted limitation (the recorder half of the bundle covers it when the
   user runs `export.py`).
6. **Self-tests that actuate the pump or open sockets**: the non-intrusive
   bound in the ask. `async_simulate` is the solve-without-actuating path;
   feed health is read from collected staleness, not probed live.
7. **Collecting beyond this integration**: other integrations' entities
   enter only as the mapped inputs the optimizer already reads; HA-wide
   diagnostics is HA's own surface.
8. **A card UI page for debugger control** (F6 lane): the options toggle +
   button + existing card health row cover it; the card already navigates
   to the right settings page.
9. **An unbounded or > 7-day ring**: size math and privacy minimisation both
   bound it; the ring drops the oldest day.
10. **A new in-repo privacy gate**: `export.violations` + the nightly
    `LEAK_PROBES` are the gate; the harness calls them (prototyped), and a
    second, weaker gate would be the dangerous one.

## 7. (e) The harness interface and roster-ready group shapes

### Harness stages (each names its reuse)

1. **Ingest/validate** — schema + manifest; `export.violations` over the
   replay half with a planted-credential null control (prototyped, stage
   2/2b: a planted `sk-ant-...` string yields 2 violations);
   `store.DOMAINS` coverage; `_sanitize` idempotence (prototyped, stage 3).
2. **Store replay** — every store document through its real loader
   (`AccuracyTracker.from_dict` prototyped, 192 samples; the corruption arm
   `--corrupt accuracy` is refused by the loader's own barrier and the smoke
   fails visibly at 11/12 — prototyped). New capability owed here only:
   seeding the HA-stub `Store._DISK` from the bundle so the replay starts
   from *learned* state, which `run_fixture` today cannot do (the export
   deliberately carries no `.storage`; the D1 store survey names this gap).
3. **Timeline replay** — `run_fixture` over the bundle's replay half
   (prototyped, stage 5: final day, 48 cycles, invariants clean), with the
   lane's own judges (`finite/unit/no_default/agreement/cycle/not_frozen`)
   as the first bug-finding pass.
4. **Monitor re-run** — bias/MAE/trust recomputed from the accuracy store
   vs the live summary (prototyped, stage 4: store-window 0.054 vs
   live-deque 0.015 — the windows differ and the harness must state its
   window, a real property this prototype established); `Cusum` and
   `SnapshotRing.observe_bias` over the week's daily bias to reproduce the
   `accuracy_drift` latch offline.
5. **Code-path mapping** — anomaly to seam via `tests/seam_map.json`
   lookup plus the payload view that carried the field; emitted as a
   findings-ready JSON (id, claim, evidence command, harness, metric,
   perturbation — the COMMON.md report shape) plus `RESULT` lines per the
   harness canon.

**The agentic-seat interface**: the harness emits (i) the verdict dict per
stage, (ii) one re-runnable command per claim, (iii) the bundle itself
addressable as a fixture. A debugging seat brief then says: run the smoke,
read the offenders, drive targeted replays by trimming the fixture window
(the smoke's tail-day trick) or perturbing inputs — the r9-diag-1 study's
arm method on bundle data.

### Roster-ready groups (names for the orchestrator to fold verbatim)

Placement rule: each group lands **after the last roster group of every
fix-lane whose `OWNS` files it touches** (`tools/audit/round9/fixplan/
data.py` lanes; F1 runs to wave 14, F10 to 18, F5 to 5, F7 to 7, F8 to 6,
F3 to 3, F4 to 2). Relative to the live lanes (W2-W4 today): nothing here
can or should start before the fix waves free the coordinator — earliest
realistic start is the post-F1 waves, ~W15.

**R9-DBG-1 — "collector module + activation + bundle writer"** (wave 15,
after the last F1, F3, F4 and F5 groups; model opus — coordinator/store
surgery with ratchet payments; ~350-450 production lines). Files: new
`custom_components/heatpump_optimizer/debugger.py` (ring, row builder,
bundle assembly, self-test bodies); `store.py` (`DOMAINS` entry + store
construction, F1-owned: borrow declared); `const.py` (CONF + SERVICE
constants, F4); `config_flow.py` + `strings.json` + both translations (F5);
`services.py`, `button.py` (F1); `coordinator.py` (tick hook + `_spawn` of
the collector, F1 — the hook is the one-line call site, priced against the
seam map in the same diff per fixer.md step 12); `diagnostics.py`
(unowned); README/docs note (F8). Oracle: `dbg_bundle_gen.py`'s bundle shape
frozen as the spec.

**R9-DBG-2 — "self-tests + diagnostics bundle surface"** (wave 16, after
R9-DBG-1; model sonnet — specified work with an oracle: the priced
self-test table in section 4 and the synthetic bundle as fixtures;
~200 production lines). Files: `debugger.py` (self-test orchestration),
`diagnostics.py` (bundle inclusion + cap), `button.py` (finalize button if
not landed in DBG-1), translations.

**R9-DBG-3 — "repo-side debugger harness"** (wave 15, parallel to DBG-1 —
it touches no fix-lane file if confined to `tools/replay/**` (unowned) and
new files; model sonnet with the two prototypes as the oracle; ~400 tool
lines + a `tests/` smoke if wired into a gate). Files: new
`tools/replay/debug_ingest.py` (generalised `dbg_ingest_smoke.py`), new
`tools/replay/debug_replay.py` (store seeding + `run_fixture` driver),
`tools/replay/dbg_bundle_gen.py` promoted from the prototype (synthetic
week as a CI-visible artifact); **only if `tests/replay.py` itself must
change** (store-seed hook) does the F10 edge (wave 18) bind — prefer an
import-only integration to avoid it. Note: `tools/audit/**` is F11-owned,
which is why the harness homes under `tools/replay/`; if the orchestrator
prefers `tools/audit/harnesses/` (fixer.md step 18's home for reusable
harnesses), the group needs an F11 after-edge or ownership note — an
orchestrator decision recorded in section 8.

If the orchestrator wants fewer groups: DBG-2 folds into DBG-1 (same
reviewer surface) at ~550-650 lines — over the ~400-line fixer guidance, so
the split is the better shape.

## 8. Unknowns not closable from the tree

1. **HA's practical size ceiling for a diagnostics download**: no cap is
   documented anywhere in-tree; the module caps the inline bundle (proposed
   8 MB raw) and falls back to summary + store-file pointer. Verifying
   against a real HA instance is a `tests/nightly_ha.py`-lane check owed by
   DBG-2.
2. **Real-install bundle size**: the synthetic week is DHW-only, 5 stores —
   a floor. The first real bundle's measurement is owed by DBG-1's PR body
   (the section-2 upper estimate is an extrapolation, flagged as one).
3. **The coordinate-coarsening discrepancy**: `diagnostics.py` 1 dp vs
   `export.py` 2 dp. Which rule the bundle's extra sections ride is an
   owner decision; the pre-study proposes the coarser (1 dp).
4. **`tools/replay/` vs `tools/audit/harnesses/`** for the harness home
   (F10/F11 ownership edges) — orchestrator decision; the group shapes
   above assume `tools/replay/` with an import-only `tests/replay.py`
   integration.
5. **The synthetic week's single `agreement` offender** (section 5) —
   fixture artifact or genuine; DBG-3 dispositions it with a targeted
   replay rather than this seat guessing.
6. **Reload durability of an in-memory ring**: the design puts the ring in
   the `..._debug` store precisely so a reload cannot lose it; the
   reload-mid-week test is owed by DBG-1 (the options toggle itself
   triggers a reload, so the first activation must survive one by
   construction).

## Figures

Every figure above names its instrument inline. Headline commands:

    PYTHONPATH=tests/hastub:tests ~/.local/state/hpo/venv-ci/bin/python \
      tools/audit/round9/prestudy/dbg_bundle_gen.py --days 7 --out /tmp/r9-dbg-0/week
    gunzip -c tools/audit/round9/prestudy/runs/week/bundle.json.gz > /tmp/r9-dbg-0/bundle.json
    PYTHONPATH=tests/hastub:tests ~/.local/state/hpo/venv-ci/bin/python \
      tools/audit/round9/prestudy/dbg_ingest_smoke.py --bundle /tmp/r9-dbg-0/bundle.json
    # perturbation arms: --days 1; --corrupt accuracy

Run at baseline `ed0151ad2`, seat worktree, 2026-10-04. Committed under
`runs/`: the week bundle gzipped (132,629 B), the day-1 perturbation bundle
gzipped, the generator log, and both smoke logs (pass 12/12; corruption arm
fail 11/12). The raw bundle and the extended fixture are regenerable by the
committed generator and are not committed.
