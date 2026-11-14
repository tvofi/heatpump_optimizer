Fix review: merge 4edd4f2d24108139bdedf2bce07841e31a4a7e63

bus-nonce: 6ad73d13a70854876c1f7da920602126

Round 1 (first-round handoff review of R10-SAV-VALUATION-RESIDUE part 3, Carry 10 only), measured at 4edd4f2d24108139bdedf2bce07841e31a4a7e63, which is still the tip of handoff/r10-sav-valuation-residue-p3 at posting.

## Evidence

- Head and range: the tip is a merge of origin/main fafd6a9ff5 into 8341359750. The three-dot diff origin/main...head names 8 files (README.md, climate.py, entity.py, sensor.py, dev/audit/harnesses/r10_combi_tank.py, docs/configuration.md, tests/doc_claims.py, tests/entities.py). VERSION, manifest.json, RELEASE_NOTES.md and tests/golden are untouched. `git diff merge-base...origin/main -- dev/governance/roles/` is empty, so the contract is current.
- Merge with main: `git merge-tree --write-tree origin/main <head>` exits 0 with no conflict (origin/main a6db2209bf). Evidence: ev/merge_tree.txt.
- Merge resolution: `git show --remerge-diff` shows the one hand resolution in tests/doc_claims.py. It deletes only the conflict markers, keeps main's R10-CONFIG-FLOW-TEXT-VERIFY block and check_combi_dhw_split whole, and adds `check_combi_dhw_split()` to main(). Evidence: ev/remerge_diff.txt.
- doc_claims at the head: `python3 tests/doc_claims.py` prints ALL 390 checks PASSED, including the four Carry 10 checks (ev/doc_claims.txt).
- The doc checks read the real text: my own perturbations each fail only their own check (ev/doc_mutants.txt, driver ev/doc_mut.py). The README cost row losing its note: KILLED. The space row gaining `dhw_split`: KILLED. configuration.md's combi option losing the sentence: KILLED. `entity.COMBI_DHW_SPLIT` reworded: KILLED. The null run SURVIVED.
- Main's pin was not hollowed out by the union. Changing strings.json's "sent again every 5 minutes" to 7 fails "every quoted figure in the flow help (19 pins)", 1 of 390 (ev/flowpin_mutant.txt).
- entities.py at the head: `PYTHONPATH=tests/hastub python3 tests/entities.py` prints ALL 2728 ENTITY CHECKS PASSED, with the three Carry 10 checks ok (ev/entities.txt).
- Mutation proof, re-run with my own mutant set. I patched each production line and ran tests/entities.py's header (lines 1-537) plus the Carry 10 block (lines 6036-6095); driver ev/block_driver.sh, mutants ev/mut.py, results ev/mutants.txt.
  - null: SURVIVED.
  - KILLED: guard_off, guard_on, const_text, cost_attr_none, cost_attr_empty, cost_unrec, acc_unrec, acc_guard_space, acc_guard_true, acc_call_del (re-run as `pass` after my first spelling was a syntax crash, both lines recorded), climate_call_del, climate_unrec.
  - SURVIVED: guard_enabled_only. It replaces `params.combi_tank_active` with `params.dhw_combi_tank_enabled`; see Findings. It is not a vacuous mutation: deleting each named line kills it.
- Finder's harness, both ends. `r10_combi_tank.py split_attrs` (the head's arm run over the merge base fafd6a9ff5) reads 0 for every row at the base. At the head, the four combi hot-water rows read 1 and every other row reads 0 (ev/split_attrs_base.txt, ev/split_attrs_head.txt). `r10_combi_tank.py exchange` prints identical rows at both ends apart from solve_s: exchange 3 rounds, 22.135 kWh, cost 46.357, tap draw 7.830, shortfall -1.455; null 0 rounds, 5.327 kWh, 7.304, 7.830, 28.767. These match the body's census table (ev/exchange_base.txt, ev/exchange_wt.txt).
- Null control, re-derived by my own script (ev/nullattrs_*.txt, ev/nullattrs_diff.txt). On the separate-tank store, the full `extra_state_attributes` of DHWHeatingCost, DHWEnergy, DHWCost, the climate entity, SpaceEnergy and SpaceCost are byte-identical at base and head. On the combi store, the four hot-water readers differ only by the `dhw_split` key, and the space readers are identical.
- Production reachability: the real coordinator exposes `thermal_params = _view("_thermal_params")` (coordinator.py:3513), so the `getattr(..., None)` fallback is not the path taken in production. In the DHWHeatingCostSensor MRO, only the class itself defines `extra_state_attributes`, so the new property drops no inherited attribute.
- Structure and architecture: `python3 tests/structure.py` prints STRUCTURE RATCHET PASSED. `score.py --diff fafd6a9ff5` prints `Architecture score: dS +0.0000 NULL` (ev/structure.txt, ev/archscore.txt). The body measured against a2ef25b4b2; I measured against the tip's merge base, with the same result.
- Forward-carry: the one-channel recount is on handoff/audit-r10-roster at a0eca1b526, in R11-INTAKE-R10-RESIDUE's carry list ("From r10-sav-valuation-residue-p3, body item 5a1ba9c2"). It states its precondition: the separate install and the combi null row stay bitwise, and savings do not move. It also gives its re-measure instruction (`r10_combi_tank.py exchange` at the merge base).
- CI and red checks: no pull request exists yet, so there is no review packet and no CI run to read. The red-check answer could not be checked against live runs. The body pre-answers the `tests / mutation` red that prepr.sh predicts; `tests / mutation` is in the owed-reds set (ev/owed_reds.txt). That answer, and the five unpinned sites, must be checked once CI runs on the opened PR.
- Figures I did not re-derive: the scoped-gate line ("23 script(s) run"), the fixer's `mutant_run.py --diff` count of 12 mutants, and the failing-first run at a2ef25b4b2. I did not re-run the gate (CI's heavy run; none exists yet). My failing-first evidence is the split_attrs base row instead.

## Findings

- Surviving mutant on entity.py:390. Replacing `params.combi_tank_active` with `params.dhw_combi_tank_enabled` passes every Carry 10 check. The test's null uses only flag-off, never flag-on with the predicate false. That state is distinct at function level: ThermalParameters(dhw_combi_tank_enabled=True, buffer 50 L) gives active False, and the real helper returns {} (ev/flag_on_inactive.txt). The config flow's building step refuses that combination (config_flow.py:3784), so it is reachable only through a path that skips that validator. The code is correct; the test does not pin the predicate's flag-on, inactive domain. Carry: R11-INTAKE-R10-RESIDUE

## Friction

none
