R9-UX-9: the Advisor tab recommends adding a pump power, energy, frequency or water-flow sensor on an install that has none of them, naming each class and the config key that would use it, and the flow-meter config key those recommendations can now name exists.

Closes #1956

Part of #2016 (items 1-3; item 4 is R9-UX-10). Items 1-3 here: the `flow_meter_entity` key, the unit conversion, and the options-step field. The "estimate follows the sensor" acceptance of #2016 is met by the published `measured_heat_output_kw`; feeding it into the learners or the COP model is not part of this PR.

- Detection is #1955's own install probe (`probe_install`) plus the energy and flow entities the probe does not hold, as a class table in `feedback_gaps` (one entry per class). A class whose config key `const` does not define is not offered, which is how flow waited for its key.
- The gap advisor sensor (on by default) publishes the list as `feedback_gaps`; the card draws one dismissable row (dismissal in the browser's localStorage) and the row's markup is byte-identical when the list is empty.
- `flow_meter.py`: thermal output = flow x 4.186 kJ/(kg K) x (supply - return), used only when no power or frequency signal exists, published as `measured_heat_output_kw` on the Recommended Power sensor. Units L/min, L/s, L/h, m3/h, m3/s, kg/s, kg/min, kg/h at 0.998 kg/L; unavailable, negative and unknown-unit readings are absent.
- Options step: an optional sensor field in the compressor group, now headed "Compressor frequency and flow" (en, sv).
- **Budget raise**, approved by tvofi 2026-10-07 (new feature: the flow-meter config key, #2016), reason in commit 02d9c0f3. Against the current base 8d7903e6 it is `max_class_loc` 9048 to 9049 (+1) and `seam_cut_total` 766 to 768 (+2), both from the one `measured_heat_output_kw` payload line in the coordinator. It is the smallest raise that passes: `python3 tests/structure.py` at this head measures `max_class_loc=9049` and `seam_cut_total=768`, so each raised cap equals its measurement and has no headroom. (The PR's earlier text gave 9104 to 9105; main has since lowered that cap to 9048, so the delta is still +1.) Alternatives considered and not taken: holding the value in a coordinator attribute would have cost +1 `coordinator_attrs`, +1 `coordinator_multiassigned_attrs` and +6 `max_class_loc`, so the value rides `FlowCurveBias` instead. The payload line cannot leave the coordinator class because `_measurement_view` is a coordinator method. Having the sensor read `_flow_bias` directly would skip the payload, and was rejected as a private-attribute read.

## Head

bb410745a1d87075654e266ed9142799130aea99

The code head merges origin/main 8d7903e6 into the handoff head 2581479b (commit 703af1e7) and adds two fix commits, f5810852 and bb410745.

Conflicts, all resolved so that both sides are kept:

- `dev/audit/rounds/round3/D5/option_doc_coverage.py`: main moved the D5 harness here (R9-RO-8) and #1939 took the counts from 198/231 to 199/232. This branch's field adds one more, so the counts are now 200/233 and the header records both moves. Running the harness at this head prints `option_fields_rendered=200` and `option_schema_keys_rendered=233`.
- `dev/audit/rounds/round4/D6/claims.py` and `claims.json`: main's moved path and main's DBG-1 history are kept, and R9-UX-9's `flow_meter.py` is added (72 to 73 modules). `claims.md` was deleted at the old `tools/audit/round4/D6/` path, which main had moved. `claims.py` regenerated the new-path `claims.md` and `claims.json`, and prints `arch_modules_on_disk=73` and `arch_map_listed=73`.
- `docs/architecture.md`: main's 27 module-level `homeassistant` importers (debugger) are kept, and the module count is now 73 (flow_meter does not import `homeassistant`).
- `tests/golden/claimed_drift.txt` (the `claimnotes` driver refused it, and I resolved it by hand): only this branch's six R9-UX-9 claims are kept. The five R9-DIAG-2S lines the branch had inherited from an earlier main are dropped; main had already dropped them. Main's #1939 `config_flow` line is also dropped, because #1939 is in this diff's baseline and the `config_flow` name is now claimed for this diff's keys. `claims-for: 6.7.16` equals `VERSION`.

## Mutation proof

Four production predicates were broken together, `tests/features.py` (the closure of the new checks) was run once, and the predicates were restored with `git checkout`:

- `feedback_gaps`: the "any offered class present" test replaced by `False and ...`
- `flow_meter.read_heat_output_kw`: the `cap.measured_power or cap.frequency` gate deleted
- `inputs.read_flow_kg_s`: `converted < 0.0` replaced by `converted < -1e18`
- `const.FLOW_UNIT_TO_KG_S`: the `m³/h` factor dropped its `* 1000.0`

These checks went red (besides R9-F2.1 P3, a known local failure):

- "any one of the signals silences the recommendation (null control: each alone)"
- "the gap advisor publishes the probe's list for the card to read"
- "L/min, L/s, m3/h and kg/s all convert to kg/s at 0.998 kg/L"
- "an unavailable or negative flow reading is absent"
- "a power or a frequency signal keeps the estimate off (the signal outranks the flow meter)"

That run was at head a5290021. The merges since then touch none of these predicates.

Card side:

- Replacing the dismissal test with `true` failed "dismissing removes the row and it stays gone on a fresh card".
- Hard-coding the attribute read failed "the row cites the config key each class would use", "a metered install (empty list) shows no recommendation" and "an older backend without the attribute shows no recommendation".

## Null control

The unmodified tree (origin/main) has no `feedback_gaps` attribute, no `flow_meter_entity` key and no `measured_heat_output_kw`. The new checks fail on it, because the symbols do not import.

In the tests:

- With the flow key unset, nothing is estimated.
- With the flow key deleted from `const`, the table emits no flow row.
- Doubling a planted flow doubles the estimate (the follow claim).
- A metered install, an empty list and a backend that publishes no list each show no row.
- With the dismissal cleared, the row returns.

For the closure repair: `tools/pr/ci_predict.py` (from origin/fix/r9-ro-11-pr, run from a scratch path), run at the merge commit 703af1e7 before the repair, printed rc 1 with `UNCLASSIFIED ... flow_meter.py` (fast) and `UNDER-SCOPED ... read by 18 script(s)` (closures). At this head it prints rc 0 and `no closures or fast red predicted`.

## Figures

All figures are at this head unless stated otherwise. The venv-ci Python 3.14 is first on PATH, with `PYTHONPATH=tests/hastub`. Heavy scripts are CI's.

- `python3 tests/closure.py select --diff 8d7903e69cfe --workdir <dir>` prints `MODE: SCOPED -- 30 script(s) run, 3 scoped out`. Of those, I ran locally only the cheap scripts below. The rest (`features.py`, `golden.py`, `env_drift.py`, `stress.py`, `optimality.py` and the other heavy lanes) are left to CI's check-runs at this head.
- `python3 tests/structure.py`: rc 0, `STRUCTURE RATCHET PASSED`. It prints `ok   max_class_loc 9049 <= 9049` and `ok   seam_cut_total 768 <= 768`.
- `python3 tests/entities.py`: rc 0, `ALL 2203 ENTITY CHECKS PASSED`. Before the deployment-shape note was recounted, the same script printed `1 of 2203 ENTITY CHECKS FAILED`, on "the lane's docstring records those measured numbers", with `missing markers -> ['all 91 files']`.
- `python3 tests/harness_headers.py`: rc 0, `ALL 109 HARNESS HEADER CHECKS PASSED`.
- `node tests/card.mjs`: rc 0, `ALL CARD CHECKS PASSED` (after `python3 tests/plan_view.py`, rc 0, which writes the payload it reads; run without it first, card.mjs printed `plan payload ... not found` and rc 1).
- `PYTHONPATH=tests/hastub python3 dev/audit/rounds/round3/D5/option_doc_coverage.py` prints `option_fields_rendered=200`, `option_fields_undocumented=0` and `option_schema_keys_rendered=233`.

## Unpinned sites

`mutation` at 7cab991c (job 112901417777) refused 11 sites this diff adds, and `tools/pr/ci_predict.py` at this head lists the same 11. Each one is pinned by mutation-autofix (awaiting R9-CI-1):

- `custom_components/heatpump_optimizer/flow_meter.py:31` GUARD_OFF: pinned by mutation-autofix (awaiting R9-CI-1)
- `custom_components/heatpump_optimizer/flow_meter.py:36` CMP_BOUND: pinned by mutation-autofix (awaiting R9-CI-1)
- `custom_components/heatpump_optimizer/inputs.py:278` GUARD_OFF: pinned by mutation-autofix (awaiting R9-CI-1)
- `custom_components/heatpump_optimizer/inputs.py:281` RETURN_DEL: pinned by mutation-autofix (awaiting R9-CI-1)
- `custom_components/heatpump_optimizer/inputs.py:821` GUARD_OFF: pinned by mutation-autofix (awaiting R9-CI-1)
- `custom_components/heatpump_optimizer/inputs.py:825` CMP_BOUND: pinned by mutation-autofix (awaiting R9-CI-1)
- `custom_components/heatpump_optimizer/inputs.py:825` GUARD_OFF: pinned by mutation-autofix (awaiting R9-CI-1)
- `custom_components/heatpump_optimizer/inputs.py:827` GUARD_OFF: pinned by mutation-autofix (awaiting R9-CI-1)
- `custom_components/heatpump_optimizer/inputs.py:831` RETURN_DEL: pinned by mutation-autofix (awaiting R9-CI-1)
- `custom_components/heatpump_optimizer/inputs.py:833` RETURN_DEL: pinned by mutation-autofix (awaiting R9-CI-1)
- `custom_components/heatpump_optimizer/thermal_model.py:1286` RETURN_DEL: pinned by mutation-autofix (awaiting R9-CI-1)

The two `flow_meter.py` sites could not be measured at 7cab991c (`recorded closure reaches ... flow_meter.py ... stays unpinned`), because no committed closure listed the module. This head lists it in 21 closures, so the drivers now reach those sites. If a site survives every driver after the bot commit, I owe it a killing check or a `survivor_triage` verdict.

## Red checks

These are read from the check-runs of PR head 7cab991c (run 37653143979 and its siblings), the last head CI ran on.

- `fast (3.14)` (job 112901417713): one script failed, `tests/entities.py`, on three checks that all come from `flow_meter.py` having no measured closure: "covers every python file", "the deployment-shape lane's closure is the whole tracked package" and "every tracked file is either measured or deliberately classified". This diff caused them. They are fixed at this head by the closure entries below, and the deployment-shape note now cites 91 files. Everything else under `FAIL` in that log is a self-test's planted negative (`a3:`, `a4:`, `a5:`, `a8:`, `a10:`), which `ok` lines follow.
- `closures` (job 112901558566): `UNDER-SCOPED` on 20 scripts (`arch_score_head`, `block_duty`, `boost_drift_replay`, `card.mjs`, `card_drift.mjs`, `config_flow_steps`, `deployment_shape`, `doc_claims`, `entities`, `env_drift`, `features`, `finite_boundary`, `golden`, `harness_headers`, `manual_plan`, `plan_view`, `solar_alignment`, `structure`, `typing_ruler`, `wood_advisor`). Each one reads `custom_components/heatpump_optimizer/flow_meter.py` alone. This diff caused it. Fixed at f5810852: that one path was copied from CI's log into those 20 lists, not recorded locally. Commit bb410745 adds it to `tests/debug_collect.py`'s list too. That script came from main (R9-DBG-1) after CI's recording, so only `ci_predict.py` could name it. No `inert_reads` entry was named.
- `closures-autofix` (job 112910283667): `skip-failed-recording`. `tests/stress.py` exited 1 under `strace`, on its timing-budget check `no scenario exceeds its own recorded cost by the budget factor` (typical_slab/winter at 11.5x against a budget of 11.3x). That is wall-clock under the recorder's load, in a lane this diff's code does not reach, and stress.py was not among the UNDER-SCOPED scripts. A red autofix means no bot commit was coming, so per `ci-autofix.md` I committed the repair from CI's own log instead. The cheaper detector is `tools/pr/ci_predict.py`, seconds and static, and it predicted this red (the null control above). The handoff did not run it because it was not yet in the tree.
- `Analyze (python)` (job 112901394357): the analysis ran to the end. The queries executed, and `Exported results to SARIF` is printed at 16:56:16. The job then failed in `Uploading code scanning results`, and the job log carries no alert line and no `##[error]` naming a rule. I could not read the code-scanning alerts for `refs/pull/2024/merge`, because the shared GitHub API quota was exhausted (`HTTP 403 API rate limit exceeded` at 20:23 UTC). So I have found no CodeQL finding to fix, and I am not claiming that none exists. The answer is owed at the new head: read `code-scanning/alerts?ref=refs/pull/2024/merge` once the quota resets. The cheaper detector is the alerts API, the same read. None runs locally, because CodeQL is not installed on the seat.
- `budget-raise-gate` (job 112901410974 failure, 112901395080 cancelled): red by construction. It printed `RAISE tests/structure_budgets.json: max_class_loc` and `seam_cut_total` and `REFUSED: no decisive review by tvofi`. The raise was owner-approved 2026-10-07 (the new flow-meter config key, #2016). It is named and minimal (+1, +2), as described above, and merges only on tvofi's approving review at the head (decision 0013). The cancelled twin carries no verdict and is to be rerun. No cheaper detector exists for "a human approved this raise".
- `mutation` (job 112901417777): `MUTATION TABLE REFUSED -- 4703 unpinned site(s) against 4693 ..., 11 of them added by this diff`. These are listed under `## Unpinned sites`. The PR leaves them to mutation-autofix (awaiting R9-CI-1). Nothing is pinned locally (`ci-autofix.md`). The cheaper detector is `tools/pr/ci_predict.py`'s ADDED UNPINNED arm, which listed the same 11 at this head.
- `mutation-autofix` (job 112903169103): red, and it did not repair, for the same cause, since no closure reached `flow_meter.py` at 7cab991c. That cause is gone at this head. The pins themselves await R9-CI-1's autofix repair.
- `pr-contract` (job 112918985908): `check \`Analyze (python)\` is red and \`## Red checks\` does not name it`. This was the body's own omission. This body names it, above.
- `delivery-status` (job 112901395650): `DELIVERY STATUS OVERDUE -- 54 rowed, 0 pending, 3 overdue` (#1917, #2003, #2001). The cause is main's: the check grades main's delivery table, and no commit of this branch edits `dev/programme/delivery/`. It is not a required context.
- `nightly-status` (job 112901409382): `NIGHTLY FAILED: mutation-ledger, mutation-nightly, record-autofix` (scheduled run 37595831734, head be0cb82). The cause is main's: the check grades main's last nightly and is not a required context on `main-protect`.

## Forward-carry

None. #2016 item 4 (consuming `measured_heat_output_kw` in the thermal model and learners) is roster group R9-UX-10. That is a deferral to a group, not a finding that changes how a later stage works.

## Friction

ci-autofix: cost: `closures-autofix` went red with `skip-failed-recording` on a `tests/stress.py` timing-budget breach recorded under `strace` load, in a script outside the UNDER-SCOPED set, so the one-path repair across 20 lists was hand-copied from CI's log instead of a bot commit.
