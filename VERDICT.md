Fix review: merge c75b52e2d651ea8d20c4b8ce3993d25b0297a122

bus-nonce: 84b7789e5b1e16ab9a99d232c50d623e

Round 1 (no earlier `Fix review:` comment on #2393). Measured head c75b52e2d651ea8d20c4b8ce3993d25b0297a122, re-read as `refs/pull/2393/head` before writing this. Roles diff merge-base...origin/main is empty, so the contract I applied is current.

Diff (three-dot against merge base 5a41a5669): `README.md` (+40, new `## Minimal working setup`) and `dev/programme/delivery/2393.md` (+1). VERSION, manifest version, RELEASE_NOTES heading, golden and claim files: not touched (step 4/5: no fixture moved, no claim present; CI `env_drift.py --claims-only 5a41a566` ran in `fast`).

RESULT mutation_label_heat_pump_switch: doc_claims `1 of 169 checks FAILED` (I5 options-field arm) -- reproduced, ev/mut1-label.txt
RESULT mutation_anchor_quick_start: doc_claims `1 of 169 checks FAILED` (anchor not a heading) -- reproduced, ev/mut2-anchor.txt
RESULT mutation_anchor_supported_controls (mine, not in body): `1 of 169 checks FAILED` -- ev/mut3-anchor2.txt
RESULT mutation_screen_name (mine): `*Optional sensors*` -> `*Extra sensors*` stays `ALL 169 checks PASSED` -- that screen name is unpinned; the body does not claim it is pinned, and I confirmed it by hand: strings.json config.step.user_sensors.title = "Optional sensors", data.heat_pump_switch_entity = "Heat pump on/off switch".
RESULT null_control: `grep -c '^## Minimal working setup'` at 64b1f82a = 0 -- reproduced
RESULT doc_claims_head: ALL 169 checks PASSED -- reproduced
RESULT md_tables_head: doc_orphaned_table_rows=0, doc_misrendered_lines=0, exit 0 -- reproduced
RESULT structure_head: STRUCTURE RATCHET PASSED -- reproduced
RESULT closure_select: `MODE: SCOPED -- 4 script(s) run, 29 scoped out.` (doc_claims, entities, harness_headers, md_tables) -- reproduced
RESULT harness_headers / entities: NOT re-derived here -- this container has no `homeassistant` module, so both die on import (also with BASH_ENV/ENV unset). Cited from CI instead: `fast (3.14)` job 117726556759 on this head prints `ALL 109 HARNESS HEADER CHECKS PASSED` and `7 TEST SCRIPT(S) PASSED` including entities.py; the body's `2346` entity count is not verified by me.

Code claims (step 8), re-read at head, all hold: weather is the only `vol.Required` entity picker in `_user_credentials_fields` (config_flow.py:1287), price enforced via `price_entity_required`/`tibber_token_required` and Tibber validation (`invalid_tibber_token`/`cannot_connect`); `raw_today`/`raw_tomorrow` (price_model.py:792-802); "skipping optimization" (coordinator.py:6695); hourly forecast (6521); "marked stale" (6580); `switch_supply` gated on switch (7378); `room_temperature: float = 21.0` (thermal_model.py:1550) written only under `if indoor.ok` (coordinator.py:6038) -- and nowhere else on `_current_state` (grep); `forecast_outdoor_now` fallback (6047); early_cutoff releases unless both indoor and switch set (early_cutoff.py:171); IndoorTempSensor unavailable without a reading (sensor.py).

Step 6/9: README-only, owner-requested; the finding's harness is the committed `tests/doc_claims.py`; no multi-seam class stated, so no enumeration rule is owed.
Step 10 (forward-carry): the body's no-indoor learner observation is not in D1.md. Not blocking: `finding-propagation.md` carries only a finding "established by measurement with its null control", and the body says it was traced by reading only; the README makes no claim depending on it. I also only read it (coordinator.py:4992-5045: `observed = ctx._current_state.room_temperature`, `_learning_frozen(CONF_INDOOR_TEMP_ENTITY, ...)`), did not execute it, and do not confirm it. Orchestrator: it needs measuring before it can be carried or filed.
Step 11 (CI on head, check-runs API, 45 runs): every run success or skipped; no red. Reds on earlier heads (arch-score, validate-hacs, nightly-status, pr-contract) are named and answered in `## Red checks`; `pr-contract` on this head (jobs 117726458758, 117726582691) passed the body.
Step 13: `git merge-tree --write-tree origin/main c75b52e2` (origin/main c8cc75ea9, one merge past the base) exits 0, tree 192827ca; no claim-driver line (no claim file conflicts). ev/merge-tree.txt
Step 14: no budget, closure, INERT, golden or score number moves.
Step 7: body's `## Head` names c75b52e2 correctly. Nit, not blocking: it calls 9ef452f5 "the authored code head" in one paragraph and 38743da4 in another; 38743da4 is the authored commit, 9ef452f5 a main merge.
