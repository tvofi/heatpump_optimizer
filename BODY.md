R9-UX-9: the Advisor tab recommends adding a pump power, energy, frequency or water-flow sensor on an install that has none of them, naming each class and the config key that would use it, and the flow-meter config key those recommendations can now name exists.

Closes #1956

Part of #2016 (items 1-3; item 4 is R9-UX-10). Items 1-3 here: the `flow_meter_entity` key, the unit conversion, and the options-step field. The "estimate follows the sensor" acceptance of #2016 is met by the published `measured_heat_output_kw`; feeding it into the learners or the COP model is not part of this PR.

- Detection is #1955's own install probe (`probe_install`) plus the energy and flow entities the probe does not hold, as a class table in `feedback_gaps` (one entry per class). A class whose config key `const` does not define is not offered, which is how flow waited for its key.
- The gap advisor sensor (on by default) publishes the list as `feedback_gaps`; the card draws one dismissable row (dismissal in the browser's localStorage) and the row's markup is byte-identical when the list is empty.
- `flow_meter.py`: thermal output = flow x 4.186 kJ/(kg K) x (supply - return), used only when no power or frequency signal exists, published as `measured_heat_output_kw` on the Recommended Power sensor. Units L/min, L/s, L/h, m3/h, m3/s, kg/s, kg/min, kg/h at 0.998 kg/L; unavailable, negative and unknown-unit readings are absent.
- Options step: an optional sensor field in the compressor group, now headed "Compressor frequency and flow" (en, sv).
- Budget raise, approved by tvofi 2026-10-07 (new feature: flow-meter config key, #2016), reason in commit 02d9c0f3: `max_class_loc` 9104 to 9105 and `seam_cut_total` 766 to 768, from the one `measured_heat_output_kw` payload line in the coordinator. Payments considered: a coordinator attribute for the value (+1 `coordinator_attrs`, +1 `coordinator_multiassigned_attrs`, +6 `max_class_loc`) was not taken, the value rides `FlowCurveBias` instead; the payload line cannot move out of the coordinator class because `_measurement_view` is its method; a sensor reading `_flow_bias` directly would skip the payload and was rejected as a private-attribute read.

## Head

111521f31baff7debe1637827d14478ece766b39

## Mutation proof

Four production predicates broken together, one run of `tests/features.py` (the closure of the new checks), then restored by `git checkout`:

- `feedback_gaps`: the "any offered class present" test replaced by `False and ...`
- `flow_meter.read_heat_output_kw`: the `cap.measured_power or cap.frequency` gate deleted
- `inputs.read_flow_kg_s`: `converted < 0.0` replaced by `converted < -1e18`
- `const.FLOW_UNIT_TO_KG_S`: the `m³/h` factor dropped its `* 1000.0`

Checks that went red (besides the known local failure R9-F2.1 P3): "any one of the signals silences the recommendation (null control: each alone)", "the gap advisor publishes the probe's list for the card to read", "L/min, L/s, m3/h and kg/s all convert to kg/s at 0.998 kg/L", "an unavailable or negative flow reading is absent", "a power or a frequency signal keeps the estimate off (the signal outranks the flow meter)". Run at head a5290021 (before the clean main merge). Card side: replacing the dismissal test with `true` failed "dismissing removes the row and it stays gone on a fresh card"; hard-coding the attribute read failed "the row cites the config key each class would use", "a metered install (empty list) shows no recommendation" and "an older backend without the attribute shows no recommendation".

## Null control

The unmodified tree (origin/main) has no `feedback_gaps` attribute, no `flow_meter_entity` key and no `measured_heat_output_kw`: the new checks fail on it (the symbols do not import). In the tests: with the flow key unset nothing is estimated; with the flow key deleted from `const` the table emits no flow row; doubling a planted flow doubles the estimate (follow claim); a metered install, an empty list and a backend that publishes no list each show no row; with the dismissal cleared the row returns.

## Figures

- `python3 tests/features.py` at head a5290021 (before the main merge): 1 of 3820 checks failed, R9-F2.1 P3, the known local BLAS-drift failure (CI is authoritative); at the same head the new checks pass; with the four mutants above 6 of 3820 fail.
- `python3 tests/entities.py` at head a5290021: 3 of 2192 failed, all the closures classification of the new module `flow_meter.py` (`closures` UNDER-SCOPED, answered below).
- `node tests/card.mjs` and `GOLDEN_REF=$(git merge-base origin/main HEAD) node tests/card_drift.mjs` at head 02d9c0f3: pass; card_drift reports all 40 states identical.
- `python3 tests/structure.py` at head 111521f3: STRUCTURE RATCHET PASSED with the two raised rows.
- `python3 tests/closure.py select --diff a52900215c3dcf3a6e093c4d61e7f5b52558fd09 --workdir <dir>` over the merge of origin/main (17f30f9c): MODE: FULL, so the merge delta is not scopable and the full matrix is left to CI.
- `python3 tests/doc_claims.py`, `python3 tests/config_flow_steps.py`, `python3 tests/plan_view.py` at head 02d9c0f3: pass.

## Red checks

Read from the check runs of the PR head af479f7d (the orchestrator's merge of main into fix/r9-ux9; none of the six commits of this branch before it carry a failing run).

- `mutation` (job 112853420660): `MUTATION TABLE REFUSED -- 4703 unpinned site(s) against 4693 at the ratchet base, 11 of them added by this diff`. The 11 are all new flow code: `flow_meter.py:31` GUARD_OFF and `:36` CMP_BOUND, `inputs.py:278` GUARD_OFF and `:281` RETURN_DEL (`normalize_flow_kg_s`), `inputs.py:821`, `:825` (CMP_BOUND, GUARD_OFF), `:827`, `:831`, `:833` (`read_flow_kg_s`), and `thermal_model.py:1286` RETURN_DEL (`_configured`). Cause: new guards and returns in a new reader and module with no ledger disposition. Process state: I listed the survivors of my tests (mutants of the flow predicates) but never ran `python3 tests/mutation_table.py --scope changed` before the handoff, so the unpinned sites were not seen until CI; `fixer.md` step 2 asks for that list and I skipped it. Cheaper detector: that command, run once before the handoff (standing cost: one local mutation pass over the changed sites). Disposition: not pinned in this head; see `mutation-autofix`.
- `mutation-autofix` (job 112855239554): `AUTOFIX: skip-measure-failed -- THE REPAIR DID NOT HAPPEN`. The bot did not pin and will push nothing; its own instruction is to pin the sites by hand with `python3 tests/mutation_table.py --pin-killed --base origin/main` and commit `tests/mutation_ledger/`, and a site no driver kills needs a killing check or a `survivor_triage` verdict. That is a code-head change, so it is owed to the orchestrator's decision (it moves the reviewed head) and is not claimed done here. My mutation proof above shows the guard and bound sites on `feedback_gaps`, the power/frequency gate, the negative guard and the m3/h factor are killed by named checks; the remaining sites are not yet measured.
- `budget-raise-gate` (jobs 112853475616 failure, 112853420181 cancelled): red by construction, this branch raises `max_class_loc` 9104 to 9105 and `seam_cut_total` 766 to 768, merging only on tvofi's approving review at the head (0013); owner-approved 2026-10-07 (new feature: flow-meter config key, #2016). The cancelled twin is to be rerun, it carries no verdict. No cheaper detector exists for "a human approved this raise"; the review is the countermeasure.
- `delivery-status` (job 112853421054): `DELIVERY STATUS OVERDUE -- 53 rowed, 0 pending, 3 overdue (overdue at 12 commits)`; it grades main's delivery table, not a file of this branch, and no commit of this branch edits `dev/programme/delivery/`. Answered by naming it (`ci-autofix.md`); the delivery row for this PR is the orchestrator's.
- `nightly-status` (job 112853419302): `NIGHTLY FAILED: mutation-ledger, mutation-nightly, record-autofix failed last night` (scheduled run 37595831734, head be0cb82); it grades main's last nightly, is not a required context on `main-protect`, and its causes are outside this diff. Answered by naming it.
- `closures` UNDER-SCOPED is expected for a new module (`flow_meter.py`): `closures-autofix` repairs it (`ci-autofix.md`); I did not hand-derive recordings.
- `bash tools/pr/prepr.sh <body> 1956` (venv-ci first on PATH, `GIT_AUTHOR_NAME` unset) at head 111521f3 printed `closes #1956 -- intended` and `FIGURES: 9 resolved, 0 not verified, 0 refused`; I did not run `--self-test`.

## Forward-carry

none. #2016 item 4 (consuming `measured_heat_output_kw` in the thermal model and learners) is roster group R9-UX-10, which the orchestrator created on the roster branch `handoff/audit-r9-fixplan` (`.claude/workflows/wave-r9-groups.json` there, not yet in main's tree, so it cannot be cited as an in-tree carry destination). It is a deferral to a group, not a finding that changes how a later stage works.

## Friction

none
