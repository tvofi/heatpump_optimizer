R9-UX-9: the Advisor tab recommends adding a pump power, energy, frequency or water-flow sensor on an install that has none of them, naming each class and the config key that would use it, and the flow-meter config key those recommendations can now name exists.

Closes #1956

Part of #2016 (items 1-3; item 4 is R9-UX-10). Items 1-3 here: the `flow_meter_entity` key, the unit conversion, and the options-step field. The "estimate follows the sensor" acceptance of #2016 is met by the published `measured_heat_output_kw`; feeding it into the learners or the COP model is not part of this PR.

- Detection is #1955's own install probe (`probe_install`) plus the energy and flow entities the probe does not hold, as a class table in `feedback_gaps` (one entry per class). A class whose config key `const` does not define is not offered, which is how flow waited for its key.
- The gap advisor sensor (on by default) publishes the list as `feedback_gaps`; the card draws one dismissable row (dismissal in the browser's localStorage) and the row's markup is byte-identical when the list is empty.
- `flow_meter.py`: thermal output = flow x 4.186 kJ/(kg K) x (supply - return), used only when no power or frequency signal exists, published as `measured_heat_output_kw` on the Recommended Power sensor. Units L/min, L/s, L/h, m3/h, m3/s, kg/s, kg/min, kg/h at 0.998 kg/L; unavailable, negative and unknown-unit readings are absent.
- Options step: an optional sensor field in the compressor group, now headed "Compressor frequency and flow" (en, sv).
- Budget raise, approved by tvofi 2026-10-07 (new feature: flow-meter config key, #2016), reason in commit 02d9c0f3: `max_class_loc` 9104 to 9105 and `seam_cut_total` 766 to 768, from the one `measured_heat_output_kw` payload line in the coordinator. Payments considered: a coordinator attribute for the value (+1 `coordinator_attrs`, +1 `coordinator_multiassigned_attrs`, +6 `max_class_loc`) was not taken, the value rides `FlowCurveBias` instead; the payload line cannot move out of the coordinator class because `_measurement_view` is its method; a sensor reading `_flow_bias` directly would skip the payload and was rejected as a private-attribute read.

## Head

2581479bd3d2f3cf59773116965a5dd7d607e962

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

Read from the check runs of the PR head af479f7d (the orchestrator's merge of main into fix/r9-ux9); none of the branch's own commits before it carry a failing run. The head is now 2581479b (two fix commits and a merge of origin/main at e0f0b6fb); CI has not run on it yet.

- `fast (3.14)` (job 112853421380): three scripts failed.
  - `env_drift.py --all` (stale fixtures plus 6 unclaimed drifts): this diff's. The code now publishes `data.measured_heat_output_kw`, `current_power`'s attribute object, `sensor_gap_advisor.feedback_gaps` and the `flow_meter_entity` config field, so `config_flow` and the five `coord_*` captures were stale and moved vs the baseline. Fixed at head: the keys added to the committed files add-only (the 875ed11c method; no solver float re-recorded on a dev box), `config_flow` recorded (float-free), and the six scenarios claimed in `claimed_drift.txt` as keys added, no value moved. `python3 tests/env_drift.py --fixtures` now prints `no committed fixture is stale`.
  - `harness_headers.py`: this diff's. `option_doc_coverage.py` 198 to 199 and 231 to 232 (the new options field), `claims.py` module count 71 to 72, and the D6 outputs regenerated. Fixed at head: `harness_headers.py` prints `ALL 109 HARNESS HEADER CHECKS PASSED`.
  - `entities.py`: three checks about `flow_meter.py` having no recorded closure (covers every python file, deployment-shape closure, tracked file measured or classified), plus the architecture-doc counts fixed earlier at head. The closure three await `closures-autofix`, below.
  The cheaper detector for the first two is `python3 tests/env_drift.py --fixtures` and `python3 tests/harness_headers.py`, each seconds to minutes locally; I ran neither before the handoff, which is the process miss (fixer.md step 5 runs what `scope.run` names, and the merge delta had made the scope FULL).
- `closures` (job 112853584211): `INERT READS UNDER-APPROXIMATED ... tests/harness_headers.py: tools/audit/harnesses/eg_b7_seam_hubs.py`. Main's, not this diff's: #2017 added that harness and #2022 (`closures: record harness_headers.py's read of eg_b7_seam_hubs.py under inert_reads`, merged to main as e0f0b6fb) fixed it; main's own `closures` was red at 45142cc3 and green at e0f0b6fb, and this head contains #2022.
- `closures-autofix` (job 112871218157): `skip-manual-repair-owed`, because the `closures` failure above was not UNDER-SCOPED; it carried no repair for this diff. With #2022 merged, the remaining closure work is `flow_meter.py` (a new module no recording reaches): awaiting CI's chain, `closures-autofix` adds it with a bot commit. I committed no local recording (ci-autofix.md: Linux CI is the canonical recorder).
- `mutation` (job 112853420660): `MUTATION TABLE REFUSED -- 4703 unpinned site(s) against 4693 at the ratchet base, 11 of them added by this diff`: `flow_meter.py:31` GUARD_OFF and `:36` CMP_BOUND, `inputs.py:278`, `:281` (`normalize_flow_kg_s`), `:821`, `:825` (two), `:827`, `:831`, `:833` (`read_flow_kg_s`), `thermal_model.py:1286` (`_configured`). Cause: new guards and returns with no ledger disposition; the two in `flow_meter.py` could not be measured because no closure reaches that module. Process miss: I did not run `python3 tests/mutation_table.py --scope changed` before the handoff (the cheaper detector, one local pass over the changed sites). Awaiting CI's chain, not pinned locally: closures-autofix adds the closure, `mutation` measures, `mutation-autofix` pins the killed mutants. A site that survives every driver after the bot commit gets a killing check or a `survivor_triage` verdict from me then.
- `mutation-autofix` (job 112855239554): `AUTOFIX: skip-measure-failed -- THE REPAIR DID NOT HAPPEN`, for the same cause (no closure for `flow_meter.py`). Owner: CI's chain above; I committed no local pins.
- `budget-raise-gate` (jobs 112853475616 failure, 112853420181 cancelled): red by construction; this branch raises `max_class_loc` 9104 to 9105 and `seam_cut_total` 766 to 768, merging only on tvofi's approving review at the head (0013). Owner-approved 2026-10-07 (new feature: flow-meter config key, #2016). The cancelled twin is to be rerun, it carries no verdict. No cheaper detector exists for "a human approved this raise".
- `delivery-status` (job 112853421054): `DELIVERY STATUS OVERDUE -- 53 rowed, 0 pending, 3 overdue`; main's: it grades main's delivery table and no commit of this branch edits `dev/programme/delivery/` (the row for this PR is the orchestrator's).
- `nightly-status` (job 112853419302): `NIGHTLY FAILED: mutation-ledger, mutation-nightly, record-autofix failed last night` (scheduled run 37595831734, head be0cb82); main's: it grades main's last nightly, is not a required context on `main-protect`, and its causes are outside this diff.
- `bash tools/pr/prepr.sh <body> 1956` (venv-ci first on PATH, `GIT_AUTHOR_NAME` unset) at 111521f3 printed `closes #1956 -- intended` and `FIGURES: 9 resolved, 0 not verified, 0 refused`; I did not run `--self-test`.

## Forward-carry

none. #2016 item 4 (consuming `measured_heat_output_kw` in the thermal model and learners) is roster group R9-UX-10, which the orchestrator created on the roster branch `handoff/audit-r9-fixplan` (`.claude/workflows/wave-r9-groups.json` there, not yet in main's tree, so it cannot be cited as an in-tree carry destination). It is a deferral to a group, not a finding that changes how a later stage works.

## Friction

none
