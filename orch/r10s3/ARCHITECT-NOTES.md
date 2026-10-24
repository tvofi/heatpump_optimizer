# Round-10 replan architect notes (orchestrator decision 2026-10-17, #201) — binds every concurrent fixer (fixer.md step 17, orchestrator.md section 5)

Line numbers are at origin/main 6e5753a4a; re-anchor at your merge base.

1. coordinator.py — one shared seam map; each group's hunks stay inside its own seam:
   - VENT-DETECTOR: the `_vent_cusum` feed and `_learning_frozen`.
   - LOOP-CPU: only the two `_replay_interval(` call lines + `away.estimate_recovery_hours`; do NOT reflow the learner bodies (NIGHT-FOLDS / TRUST-RELATIVE own them). Offload, no new state.
   - RATIO-ANCHOR: the options-save write of the prior.
   - INPUT-STALENESS: the freshness check and `HUMIDITY_MAX_AGE_MINUTES`.
   - CURRENCY: `_narrative_view`.
   - STORE: store wiring calls only.
   - LEAF-IMPORTS: import lines and moved-symbol references, re-exporting nothing. Merges FIRST among coordinator groups.
   - FREQ-DEFROST: `_observe_frequency`.
   - SAV-BASELINE: `_contract_comparison` and `_baseline_house_load`.
   - CONFIG-NOTICES: the config-notice fields.
2. narrative.py (CURRENCY, SAV-BASELINE): currency.py owns currency resolution (CURRENCY deletes the local precedence); ledger.py owns the month figures and the one cost source (SAV-BASELINE touches only narrative's month summary). Whichever merges second re-runs the other's harness (p8_replay_currency 14/0; flat-price savings ~0).
3. store.py (STORE, RATIO-ANCHOR): STORE owns the load prelude (`load_mapping`), save digest and report rules; RATIO-ANCHOR only the thermal-learning domain's stored ratio. Neither changes the other's signatures.
4. accuracy.py: LEAF-IMPORTS import lines only; NIGHT-FOLDS owns `heat_loss_refit`'s body.
5. inputs.py / freq_control.py: ARCH-SHAPES (later) owns the power-kW reader and the finite-float helper; INPUT-STALENESS the max-age rule; FREQ-DEFROST the defrost predicate.
6. payload.py / legionella.py: LEAF-IMPORTS adds the reason vocabulary and nothing else.
7. .github/workflows/tests.yml (code-owned): TICK-ORCH edits only the ROSTER_REF comment; TRAIN-HOLD only the record beat's automerge step and merge_train.py.
8. check-wave-script.mjs: D15-GRADER owns the pin keys and D15.md; TICK-DRIVERS owns audit-find.js; second to merge re-runs the wave-script check.
9. Shared census files (tests/entities.py, tests/closure.py, tests/ci_budgets.json, the claim files) merge one at a time; a later group re-takes its rows after merging main.

GOLDEN RULE: groups that may move coord_*.json goldens (SAV-BASELINE, CURRENCY, INPUT-STALENESS, SENSOR-PAYLOAD) must show the goldens byte-identical at their fork (`GOLDEN_MODE=drift` vs merge base). If drift appears: STOP and report — do not claim in parallel with another claimant. Certain movers stay serial: ADVISOR -> SCORES -> LEARNER-ETA -> HEAT-METER -> COP-GATE; SAV-REASONS -> SOLVER; HEAT-METER -> CONFIGFLOW-PAGES.
LEARNER RULE: VENT-DETECTOR -> NIGHT-FOLDS -> TRUST-RELATIVE -> HEAT-METER stay serial (owner's-bundle re-baselines). RATIO-ANCHOR's D12-s2-71 harness is re-taken at its merge base after NIGHT-FOLDS lands.
After every main merge into your branch: re-execute fixer.md steps 2-8.

## Tightening (orchestrator, 2026-10-17 ~21:20Z)
10. RATIO-ANCHOR may hand off and be reviewed concurrently, but it MERGES only after R10-NIGHT-FOLDS has merged and its D12-s2-71 harness was re-taken on a tree containing NIGHT-FOLDS (a re-take on a pre-NIGHT-FOLDS tree does not count).
11. Merge order on the train: LEAF-IMPORTS first, then coordinator diffs smallest-first (by `git diff --stat` lines in coordinator.py).
12. Churn cap: a coordinator branch needing a THIRD main-merge catch-up before it lands pauses all new coordinator.py dispatches until it lands (orchestrator's rule; report your catch-up count in every handoff).
