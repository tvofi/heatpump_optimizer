**R9-DIAG-1 delivered and folded** (doc + harnesses: `tools/audit/round9/prestudy/boost-drift-prestudy.md`, `boost_drift_replay.py`, `boost_drift_refit.py` on `handoff/r9-diag-1` @ `3c90f86a`).

**Diagnosis (measured, real-coordinator replay):** the "Learned model is drifting" warning tvofi saw is the accuracy_drift repairs notice (|bias| > 0.5 °C × 5 days). Boost handling is **defective**: the interval heat-loss learner replays from a plan-propagated plant state that never sees boost's extra heat — two boost days crash persisted `house_heat_loss_scale` 1.04 → 0.52 (the trust-region floor; 0.44 at five boost days), ~4-day recovery. The alarm itself needs an amplifier to fire (worst single-zone bias −0.094 °C): **two-zone is the named follow-up measurement**, folded into the fix group.

**Feasibility (your second question): feasible, bounded** — a batch Newton refit from three settled, boost-tagged days measured 1.138 vs truth 1.15 (the learner's own walk had reached 1.111), estimator band ±7–10%; recommend-only via a new advisor sensor → card inbox, accept applies through the existing restore path.

**Folded (roster 132 groups):** **R9-DIAG-1F** (boost/learner freeze + sample tagging + the two-zone measurement; after EG-B1 — coordinator.py) and **R9-DIAG-2S** (the restart-recommendation feature; after 1F). 1F dispatches the moment #1887 merges.
