# Round 9, D3: verifier V1 (reproduce), leads unit (D3-s2-01, D3-s2-02)

## Environment
- Python 3.14.0rc2 (`/home/claude/venv314/bin/python`); numpy 2.4.6; scipy 1.17.1.
- Evidence tree: detached worktree of `origin/handoff/audit-r9-evidence` at `96b8916318513c3617254c3ce43b10570eb16307`. That is the tree every number below was run against.
- Machine: 4 vCPU cloud container (box G1-V1), shared with other sub-seats; `load1` 0.47–0.59 at measurement, `thread_factor` 1.000 on both witness runs.
- Baseline SHA the findings were measured against: `1936d5ca72a06556eeed4e8e5bf3dea520e517e1`.

Tally: 2 verify, 0 weaken, 0 refute, 0 unresolved.

## Scope of this vote (tvofi rule, 2026-09-26T11:37Z)
No mutation pre-screen (`prescreen.py`), mutant pool, or full-gate mutant confirmation was re-run. Quiet window not run (tvofi rule). Per finding:
1. Read the recorded evidence (`tools/audit/round9/D3/s2/REPORT.md`, `storeguards.json`, `pool.json`, `results_store.jsonl`).
2. Confirmed each named production line still reads exactly as the mutant record's `old` string (`sed -n` at `96b89163`).
3. Ran the seat's own committed `witness.py` (the in-memory mutant plus probe harness, not the pre-screen or the gate) and compared its `RESULT` lines with those recorded in `REPORT.md`.

## D3-s2-01 — store-parser non-finite guards (flow_lift.py:210 / tariff.py:402 / price_model.py:324 / price_model.py:349)

**Production-line confirmation.** All four lines read exactly as claimed:
- `flow_lift.py:210` — `if not np.isfinite(bias) or samples < 0:`
- `tariff.py:402` — `if not math.isfinite(tracker._window_factor):`
- `price_model.py:324` — `if not np.all(np.isfinite(parsed)):` (shapes)
- `price_model.py:349` — `if not np.all(np.isfinite(parsed)):` (quarter factors)

`mutload.pair()`'s own line-match assertion, which aborts if `old` no longer matches the live source, passed for all four.

**Executed number** (`PYTHONPATH=tests/hastub /home/claude/venv314/bin/python tools/audit/round9/D3/s2/witness.py M31 S05 S17 S18`, wall 0.654 s, `thread_factor=1.000`, `load1=0.47`):
```
M31_diverge_in_domain=0/60
M31_corrupt_payloads_restored_non_inert=6/6   (1/6 moves priced COP 2.0125->1.8619; 2/6 persist NaN bias; 1/6 raises ZeroDivisionError)
S05_diverge_in_domain=0/4
S05_corrupt_payloads_diverging=1/3            ("inf" window_factor: threshold_kw 3.0 -> 3.5)
S17_diverge_in_domain=0/10;  zero-priced guessed steps: orig 0/288, mutant 12/288
S18_diverge_in_domain=0/10;  zero-priced guessed steps: orig 0/288, mutant 3/288
```
An exact reproduction of every number in `REPORT.md`'s D3-s2-01 section and the finding's evidence and perturbation fields. In-domain divergence is 0 for all four; the corrupt-payload divergence is as claimed. No closure driver feeds these payloads, so nothing turns red.

**Metric.** Count of isfinite guards in the persisted-state parsers whose GUARD_OFF mutant survives every measured closure driver (`storeguards.py`'s census), cross-checked by `witness.py`'s in-domain versus corrupt-payload divergence. Same definition as the finder.

**Attacks:**
- *Contention:* count metric; `thread_factor=1.000`, `load1=0.47`.
- *Wrong gate mode:* the finder's method records `tests/env_drift.py --all <ref>` among the 17 closure drivers, green under all four mutants. Recorded, not re-run (tvofi rule).
- *Grid artefact:* not applicable; four independent point findings.
- *Null control:* recorded. A comment-only edit of `optimizer.py` lives under all 17 drivers in three separate runs (`baseline.json`).
- *Real-HA reach:* `from_dict` on these classes is the Store-restore path at coordinator startup (`async_setup_entry` → `Store.async_load` → `from_dict`), not a FakeHass-only path; reachable whenever the `.storage` JSON is corrupted.
- *Severity:* medium is earned. A corrupted store is needed, but the consequence is a crash on the next learning fold, hours priced at 0.0, or a peak billed at `inf`.

**Vote: verify, medium.**

## D3-s2-02 — `price_model.py:368` residual_var round trip discarded

**Production-line confirmation.** `price_model.py:368` reads `model.residual_var = [[max(0.0, float(v)) for v in s] for s in var]`, matching `storeguards.json`'s `S19.old`. `mutload`'s line-match assertion passed.

**Executed number** (`PYTHONPATH=tests/hastub /home/claude/venv314/bin/python tools/audit/round9/D3/s2/witness.py S19`, wall 0.344 s, `thread_factor=1.000`, `load1=0.59`):
```
S19_diverge_in_domain=10/10
S19_restart_round_trip_nonzero_sigma_steps_orig=96/96
S19_restart_round_trip_nonzero_sigma_steps_mutant=0/96
```
Exact match to `REPORT.md` and the finding ("96/96 -> 0/96"; in-domain divergence 10/10).

**Metric.** Guessed steps (of 96) with `sigma > 0` from `extend_price_series` after a learned `PriceShapeModel` is round-tripped through `as_dict`/`from_dict`. Same definition as the finder.

**Attacks:**
- *Contention:* clean (`thread_factor=1.000`, `load1=0.59`).
- *Wrong gate mode:* recorded as all 15 closure drivers green including `env_drift --all` (not re-run).
- *Grid artefact:* not applicable.
- *Null control:* the existing check (`tests/features.py:41446`) feeds only a corrupt `"x"` payload against a fresh all-zero model, which the mutant also satisfies. The 10/10 in-domain divergence and 96/96 → 0/96 round trip show the missing positive control directly.
- *Real-HA reach:* same Store-restore path, reached on every restart once a variance has been learned.
- *Severity:* low is earned. The affected term (`price_risk_lambda`) defaults to 0.0 (opt-in); the other effect is a diagnostic sigma silently resetting.

**Vote: verify, low.**
