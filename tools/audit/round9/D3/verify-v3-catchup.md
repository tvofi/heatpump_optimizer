# D3 verify, lens V3 (reach and class), unit catchup (D3-s3-01..05), box G1-V3

Evidence tree c71187a2 (baseline 1936d5ca). The pre-screen, mutant pool and quiet-window gate were not re-run (tvofi rule). Votes rest on D3-s3's recorded evidence (`tools/audit/round9/D3/s3/`). The recorded run used `env_drift.py --all`: `prescreen.py` line 116 passes `["--all", BASELINE]`. Own harnesses are in `tools/audit/round9/D3/verify-v3-catchup/`. Every mutant is applied in memory.

## D3-s3-01: open_meteo naive-stamp UTC guard (M02)
- **Own measurement**: `D3-s3-01_prod.py` (box owner) compiles production `_parse_block` with the `if parsed.tzinfo is None:` guard and its body removed, in memory.
  - Metric: parsed timestamps, of 2, that differ from baseline.
  - TZ=UTC gives 0/2. TZ=Europe/Stockholm gives 2/2: the first stamp is 2026-01-15T00:00Z at baseline and 2026-01-14T23:00Z on the mutant. `--null` gives 0.
  - load1 0.27, thread_factor 1.000.
  - The sub-seat's `D3-s3-01_tz_reach.py` re-implements both arms and gives the same numbers, but it does not hook production. `_prod.py` is the one that carries the vote.
- **Reach in real HA**: `naive.astimezone()` reads the process TZ. HA 2026.2.3's `core_config`, `util.dt` and `core` never set `os.environ["TZ"]` and never call `time.tzset()`, so HA's configured zone neither masks the defect nor fixes it. A non-UTC host process reproduces it.
- **Severity**: medium, kept.
- **Seam rule**: all. The grep also returns about 15 further production sites with the same naive-datetime pattern.
- **Class**: I1.
- **Vote**: verify.

## D3-s3-02: DrawStats.from_dict open-occurrence zeroing (M19)
- **Own measurement**: `D3-s3-02_reach.py`.
  - Baseline gives open_kwh 1.5. M19 gives 0.0, a delta of 1.5 kWh. Null gives 0.
  - load1 0.18, thread_factor 0.999.
- **Reach**: `dhw_draws.py` imports no HA symbol, so the stub and real HA cannot diverge. The path is reached by a restart in the middle of a draw.
- **Severity**: medium, kept.
- **Seam rule**: demonstrated-only.
- **Class**: I1.
- **Vote**: verify.

## D3-s3-03: MonthlyLedger.add non-finite guard (M21)
- **Own measurement**: `D3-s3-03_reach.py`, one finite add then one NaN add, followed by an as_dict/from_dict round trip.
  - Baseline keeps 1 month. M21 keeps 0, a delta of 1. Null gives 0.
  - The real loader logged "Quarantined 1 malformed ledger month(s)".
  - load1 0.16.
- **Reach**: `ledger.py` imports no HA symbol.
- **Severity**: medium, kept.
- **Seam rule**: demonstrated-only. `observe_meta_mean` and the other finite guards are not enumerated.
- **Class**: I1.
- **Vote**: verify.

## D3-s3-04: async_fold_draw_stats positive fold unobserved (M24)
- **Own measurement**: `D3-s3-04_reach.py`, run on a real DhwProfileLearner.
  - With external heat on: baseline folds 0.0 kWh and M24 folds 1.0904.
  - With external heat off: baseline folds 1.0904 kWh and the no-fold mutant folds 0.0.
  - load1 0.066.
  - The finder's 0.4396 kWh differs because the fixture inputs differ; the direction matches.
- **Reach**: the fold arithmetic calls no HA symbol.
- **Severity**: medium, kept.
- **Seam rule**: demonstrated-only. It gives more drivers for one seam, not more seams.
- **Class**: I1.
- **Vote**: verify.

## D3-s3-05: disinfection write-failed notice memo (M20)
- **Own measurement**: `D3-s3-05_reach.py`, a real LegionellaGuard and DisinfectionSwitch over 5 healthy cycles.
  - Baseline makes 0 `async_delete_issue` calls. M20 makes 5. Null gives 0.
  - This is a count metric; thread_factor 0.69–0.87 comes from subprocess startup.
- **Reach**: in real HA 2026.2.3, `IssueRegistry.async_delete` pops the issue and returns before any event or save when the issue is already absent. The extra deletes are no-ops.
  - Harness trap: `PYTHONPATH=tests/hastub`, inherited into the real-HA subprocess, served the stub silently. The harness strips it.
- **Severity**: low, kept, and the real-HA no-op supports it.
- **Seam rule**: demonstrated-only.
- **Class**: I1.
- **Vote**: verify.
