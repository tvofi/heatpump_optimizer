# Round 9, extra unit "leads": verifier V2 (independent), D3

Box G1-V2, lens V2. Worktree `/home/claude/wt-g1v2-leads` (evidence tree 96b89163, baseline
`1936d5ca72a06556eeed4e8e5bf3dea520e517e1`), CPython 3.14.0rc2 venv, numpy 2.4.6, scipy 1.17.1,
BLAS threads pinned to 1, one worker process. Every number below is a count; `load1` and
`thread_factor` are quoted beside each. No mutation pre-screen, mutant pool, full-gate run or
full `./tests/run.sh` was run (tvofi's ruling of 2026-09-26T11:37Z).

Real Home Assistant, where a finding turns on it: `homeassistant==2026.2.3` pip-downloaded
(`--no-deps --ignore-requires-python`) into a temp root, extracted, its dependencies installed
with `pip install --target` into that root (never into the venv), imported in subprocesses by
`tools/audit/round9/D1/verify-v2/leads_realha.py` (which records the build commands and the one
compat shim: `typing.ByteString = bytes`, needed by mashumaro on CPython 3.14, on no measured
path). Harnesses taking it read the root from `LEADS_HA_ROOT`.

A first seat's draft of this unit was not used as evidence; every step-1 number below was re-run
here, and every step-2 number comes from a harness written here.

Votes: verify 1, weaken 1, refute 0, unresolved 0 (of 2).

Both D3 findings are voted on D3-s2's recorded evidence: `tools/audit/round9/D3/s2/REPORT.md`,
`results_store.jsonl` / `results.jsonl` (per-driver rows; every named mutant SURVIVED every
driver including `env_drift.py`, against ref 8cca77bc, which differs from the baseline only by
the release stamp), `storeguards.json` (the recorded mutant lines) and a re-run of `witness.py`.
Step 2 is a cheap executed differential over those recorded mutants, applied in memory through
D3-s2's own `mutload.pair`: an AST census of the payloads the suite feeds the three parsers, and
a reach grid fed directly versus through production `QuarantiningStore.async_load`.

Recorded single-line production mutations (step 4), all in production files:

| id | file:line | original | mutant |
|---|---|---|---|
| M31 = S34 | `custom_components/heatpump_optimizer/flow_lift.py:210` | `if not np.isfinite(bias) or samples < 0:` | `if False:` |
| S05 | `custom_components/heatpump_optimizer/tariff.py:402` | `if not math.isfinite(tracker._window_factor):` | `if False:` |
| S17 | `custom_components/heatpump_optimizer/price_model.py:324` | `if not np.all(np.isfinite(parsed)):` | `if False:` |
| S18 | `custom_components/heatpump_optimizer/price_model.py:349` | `if not np.all(np.isfinite(parsed)):` | `if False:` |
| S19 | `custom_components/heatpump_optimizer/price_model.py:368` | `[max(0.0, float(v)) for v in s] for s in var` | `[(0.0) for v in s] for s in var` |

Differential (`leads_store_guard_reach.py`, load1 0.21, thread_factor 1.000; `--null` gives 0 in every cell):

| mutant | suite payloads diverging | grid direct | grid through the store |
|---|---|---|---|
| S34 (M31) | 0 of 5 | 7 of 9 | 2 of 9 |
| S05 | 0 of 4 | 6 of 8 | 0 of 8 |
| S17 | 0 of 1 | 4 of 10 | 0 of 10 |
| S18 | 0 of 1 | 2 of 10 | 0 of 10 |
| S19 | 0 of 1 | 3 of 10 | 2 of 10 |
| S04 (recorded KILLED, positive control) | 1 of 4 | 0 of 8 | 0 of 8 |
| S08 (recorded KILLED, positive control) | 2 of 4 | 0 of 8 | 0 of 8 |

Census: 12 suite calls of the three parsers; 10 evaluate to a payload, 2 do not
(`features.py:11443`, a round trip of a live tracker; `:11553`, a helper's parameter).

## D3-s2-01: Store-parser non-finite guards in flow_lift, tariff, price_model survive deletion: no gate driver notices

- **Vote:** `weaken`; severity **low** (finder: medium).
- **Numbers:** step1 re-run (witness.py, recorded evidence): M31 6/6 corrupt payloads restore non-inert, S05 1/3, S17 12/288 and S18 3/288 guessed steps priced 0.0 under the mutant, in-domain 0 each (load1 0.90, thread_factor 1.000); recorded prescreen rows: S05/S17/S18 (results_store.jsonl) and M31 (results.jsonl) SURVIVED every driver incl. env_drift (0 killed of 17/15/15/17). Own differential: suite census 0 diverging suite payloads for all four (S04/S08 positive controls diverge 1/4 and 2/4; 10 literal suite payloads, 2 unresolved); through the production QuarantiningStore boundary the recorded mutants diverge S34(M31) 2/9, S05 0/8, S17 0/10, S18 0/10 (direct feed: 7/9, 6/8, 4/10, 2/10) (load1 0.21, thread_factor 1.000). Reachable-divergent sites: 1 of 4
- **Finder's metric:** Count of isfinite guards in the eight modules' persisted-state parsers (storeguards.py) whose GUARD_OFF mutant no closure driver kills (killed(): red and more failing checks than baseline).
- **My metric:** Per recorded mutant, payloads on which production and mutant parser restores differ (as_dict, NaN-aware): (A) every literal payload tests/features.py and tests/finite_boundary.py feed the parser; (B) my grid fed directly vs as QuarantiningStore.async_load returns it after a store round trip, the boundary every production store caller loads through.
- **Own harness:** `tools/audit/round9/D3/verify-v2/leads_store_guard_reach.py`
- **Method:** Voted on D3-s2's recorded evidence (no pre-screen, no pool, no gate run). Step 1: re-ran tools/audit/round9/D3/s2/witness.py M31 S05 S17 S18 and read results_store.jsonl/results.jsonl rows. Step 2: tools/audit/round9/D3/verify-v2/leads_store_guard_reach.py applies each recorded mutant in memory via D3-s2's mutload.pair and runs an AST census of the suite's payloads plus a store-boundary reach grid. Step 4 (recorded mutants): flow_lift.py:210 `if not np.isfinite(bias) or samples < 0:` -> `if False:` (M31=S34); tariff.py:402 `if not math.isfinite(tracker._window_factor):` -> `if False:` (S05); price_model.py:324 and :349 `if not np.all(np.isfinite(parsed)):` -> `if False:` (S17, S18); all production files, so the gap is not a test measuring itself.
- **Attacks (verifier.md step 3 order):** Contention: counts. Gate mode: the recorded survivals include env_drift.py --all, so not a default-mode artefact. Reach (step 3, real HA): every production caller of these parsers reads through a QuarantiningStore (coordinator.py _async_load_thermal_learning -> FlowCurveBias, _async_load_price_model -> PriceShapeModel, _async_load_accuracy -> PeakTracker), whose _sanitize turns non-finite floats and strings that float() makes non-finite into None; through that boundary S05, S17 and S18 diverge on 0 payloads, so by D3-s2's own M4 rule (no divergence over the reachable domain = equivalent) they are equivalent on the store path. Residual path: a snapshot rollback (coordinator.py restore via SnapshotRing.take's unsanitised json round trip) can hand PriceShapeModel/FlowCurveBias a non-finite value only if the live learner already holds one, a second defect; PeakTracker is not in snapshots. M31 stays a gap: a stored negative 'samples' is finite, passes the store, and restores a non-inert learner (2/9 through the store; the witness's samples=-1 fold raises ZeroDivisionError). Null control: --null (orig vs orig) 0 everywhere; positive controls S04/S08 diverge on suite payloads as their recorded kills require. Severity: one reachable site on a corruption-only input: low, not medium.

## D3-s2-02: PriceShapeModel residual_var restore can discard every stored variance with the gate green

- **Vote:** `verify`; severity **low** (finder: low).
- **Numbers:** step1 re-run (witness.py S19): restart round trip non-zero sigma steps 96/96 orig -> 0/96 mutant, in-domain divergence 10/10, non-finite sigma 0/576 both (load1 0.90, thread_factor 1.000); recorded prescreen row S19 SURVIVED all 15 drivers incl. env_drift. Own differential: suite census 0 of 1 suite residual_var payloads diverge under the mutant; through the production QuarantiningStore boundary 2/10 grid payloads diverge (direct 3/10), including an ordinary learned variance (load1 0.21, thread_factor 1.000)
- **Finder's metric:** Guessed steps (of 96) with sigma > 0 from extend_price_series after a learned PriceShapeModel is round-tripped through as_dict/from_dict.
- **My metric:** For recorded mutant S19 (price_model.py:368), payloads on which production and mutant PriceShapeModel.from_dict restores differ: (A) literal suite payloads in tests/features.py and tests/finite_boundary.py; (B) my grid fed directly and through QuarantiningStore.async_load after a store round trip.
- **Own harness:** `tools/audit/round9/D3/verify-v2/leads_store_guard_reach.py`
- **Method:** Voted on D3-s2's recorded evidence (no pre-screen, no pool, no gate run). Step 1: re-ran tools/audit/round9/D3/s2/witness.py S19 and read the results_store.jsonl row. Step 2: tools/audit/round9/D3/verify-v2/leads_store_guard_reach.py (same differential as D3-s2-01). Step 4 (recorded mutant): custom_components/heatpump_optimizer/price_model.py:368 `[max(0.0, float(v)) for v in s] for s in var` -> `[(0.0) for v in s] for s in var` (S19), a production file.
- **Attacks (verifier.md step 3 order):** Contention: counts. Gate mode: recorded survival includes env_drift.py --all. Reach: unlike D3-s2-01's three price/tariff guards, this divergence survives the store boundary on ordinary data (a learned positive variance, 0.03, restores as 0.0), so it is reached on every restart of a learned model, not only on corruption. Suite: the only suite residual_var payload (tests/features.py:41442, a corrupt 'x' row) restores identically under the mutant (0 of 1), which is the mechanism the finding names: no positive-control round trip. Null control: --null 0. Severity: sigma resets to zero after a restart until relearned, a bounded effect on risk-aware pricing, and the finding is a test gap: low earned.
