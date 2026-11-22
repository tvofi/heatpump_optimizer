# Box D3-g34 partial notes (written as the work goes; provisional until results/<key>.json exists)
Probes (all on SystemIdentification.identify, in memory) run before the gates finished, while the null gate ran:
- separating (candidate if the gate SURVIVES): b8d5ec03 (rows<5 off: 2/2), 756f3beb (tm prior floor: 2/2), 84372c0e (k_hat clamp: 1/1),
  20f72103 (h_prev guard off: 3/3), 50daaa57 (h_prev tie 3600us: 3/3), 4eeb3661 (3 triples: 2/2), 44bb0ce0 (sigma2 tie: 1/1),
  10665a84 (rank<2 off: mutant completes on collinear columns, 2/2), d7421c10 (rank<=2: refuses rank-2 fallback 1/1), 07227ec9 (sign guard off: 1/1)
- equivalent-candidates: 3918ca4f, a9bc37e9 (rows>=5 guard precedes), b97b45a6, 6b6a8493 (sigma2==0 inert), 3e78e62a, 87c3101b (1e-6 tie never hit in 1602 inputs)
All null controls 0. identify() is harness-only at the baseline (sysid.py:1826-1835): severity low, hygiene.
