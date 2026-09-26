# D3 verify, lens V3 (reach and class), unit leads (D3-s2-01, D3-s2-02), box G1-V3

Evidence tree 96b89163 (baseline 1936d5ca). These votes use D3-s2's recorded evidence only. I did no mutation pre-screen, no pool and no full-gate rerun, and the quiet window was not run (tvofi rule).

## D3-s2-01: store-parser non-finite guards survive deletion
- **Recorded mutants:**
  - S05 (tariff.py:402), S17 (price_model.py:324) and S18 (price_model.py:349) are in `results_store.jsonl`.
  - M31 (flow_lift.py:210) is in `results.jsonl`.
  - All four are recorded SURVIVED.
- **Gate mode:** the drivers run include env_drift.py (checks 37, killed false) and features.py (checks 3420, killed false), so the full-gate driver misses them too.
- **Source check:** all four lines are the cited isfinite or negative-count guards in persisted-state parsers.
- **Step-4 line:** each guard is a single production line in the named file.
- **Severity:** medium.
- **Class:** I1.
- **Seam rule:** all. `storeguards.py` enumerates this guard class across the eight parser modules.
- **Vote:** verify.

## D3-s2-02: PriceShapeModel residual_var restore can zero every variance
- **Recorded mutant:** S19 (price_model.py:368, `max(0.0, float(v))`) is SURVIVED across 15 drivers.
- **Finder's witness.py:** 96/96 steps have non-zero sigma at baseline, against 0/96 on the mutant.
- **Source check:** price_model.py:364-371 is the only residual_var restore path. The corrupt-payload checks in tests/features.py compare against a fresh all-zero model, which the zeroing mutant also satisfies.
- **Severity:** low. The planner degrades gracefully to point estimates.
- **Class:** I1.
- **Seam rule:** all, by the same storeguards.py enumeration.
- **Vote:** verify.
