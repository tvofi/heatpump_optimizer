Fix review: merge 9c92e927bf4b75d84420ce1d2ad4906be116d06b

bus-nonce: a3e04210b199d1707e65d0e19e673118

## Round

Delta review (owner ruling 2026-11-09) of 699491f2368ddcd96c0fb14cf6040155f66f5c44..9c92e927bf4b75d84420ce1d2ad4906be116d06b. A later round than the four before it; this verdict is `merge`, so no re-cut is owed. `review_carry.py 699491f23 9c92e927b` prints FRESH-REVIEW (a hand-resolved merge, ca57a8133), so I judged the delta.

## Evidence

- RESULT head=9c92e927bf4b75d84420ce1d2ad4906be116d06b (ev/HEAD.txt). Merge-base with origin/main is 01782a1e3.
- RESULT merge-tree: `git merge-tree --write-tree origin/main 9c92e927bf4b75d84420ce1d2ad4906be116d06b` rc=0, no conflict (ev/merge_tree.txt).
- RESULT previous findings (verdict at 699491f2): both were `Follow-up` items carried to #201, not blocks (the edit-run deferral `gate` red; the unpinned `cop_electric()` conjunct). Neither needed a code change here. The deferral red recurs on this head and is judged below; the conjunct is unchanged, since the delta touches no thermal_model.py line of this branch's.
- RESULT de.json: flattened keys of de.json and en.json each equal strings.json's, 1456 = 1456 = 1456, missing [] extra [] (my own script, not committed). The PR's three-dot patch to de.json is the 13 branch lines (heat_pump_power_source, heat_pump_thermal_power_source, heat_meter_sees_dhw, their descriptions, meter_source options), plus commit 2ea5b75e2's flow_heat_c, flow_min_lift_k and return-option strings, which came from main's keys and which de.json lacked.
- RESULT card de block: the PR patch to heatpump-optimizer-card.js adds the cop_reason_not_measurable, cop_reason_estimated_inputs, cop_reason_no_heat_reading and score.reason_cop_unmeasurable German lines and drops draw_follows_plan, matching the other two language blocks' edits.
- RESULT claim commits: claimed_drift.txt adds 6 lines (5 coord_* at 2 string leaves each, config_flow leaves added) and card_claimed_drift.txt adds score_open; both `claims-for: 7.1.9` = VERSION 7.1.9. `env_drift.py --all 01782a1e3` rc=0: NO UNCLAIMED DRIFT, NO STALE FIXTURE, 56 scenarios (ev/env_drift.txt). `card_drift.mjs` I could not run standalone: it needs the plan payload from tests/plan_view.py first (ev/card_drift.txt); the CI gate runs it and passed on the code run.
- RESULT version/budgets: the three-dot diff touches no VERSION, RELEASE_NOTES.md, manifest or *_budgets.json (ev/version_touch.txt is empty).
- RESULT production risk: the delta's custom_components changes are main's own merged-in code plus the translation and card strings above. I found no branch statement of this fix in coordinator.py, store.py or accuracy.py changed by the merge resolution, so no review was extended past the delta.
- RESULT CI at this head: `merge_train.py classify` exits 1, `RED pending: none red: gate` (ev/classify.txt). The red is the edit run 42733642788's `gate` job 129560680398, whose log is `FAIL run(s) [42733644271] at this head are still being judged; their gate decides` (gate.py deferral). The code run 42733644271's own `gate` job 129589164749 is success, as are `pr-contract / pr-contract` 129587965468, `tests / fast (3.14)`, `tests / mutation`, `tests / typing`, `tests / coverage-ratchet` and `validate / validate-hacs`, every context `owed-reds` lists. I judge the head GREEN: the only red is a deferral to a gate that is green. Same pattern as the previous verdict's finding.

## Findings

- Follow-up: the edit-run deferral `gate` red again holds `merge_train.py classify` at RED after the code run's gate concluded success (head 9c92e927bf4b75d84420ce1d2ad4906be116d06b, job 129560680398); the train needs that edit-run gate job re-run, with no code change. Carry: #201
- Follow-up: the unpinned `and self.cop_electric()` conjunct in `InstallCapability.cop_measured` is still unpinned at this head (carried from the previous verdict, not re-run: its code is unchanged by this delta). Carry: #201
