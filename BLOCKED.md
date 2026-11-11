# BLOCKED: r10-hotfix-combi-census-main-red

Question: `tools/pr/prepr.sh` refuses one step, `closures` ("failed while being recorded: tests/entities.py (exit 1)"), and the cause is the seat's environment: `/opt/hpo/venv-ci/bin/python3` has no `homeassistant`, so `tests/harness.py:25` raises `ModuleNotFoundError` -- identically on unmodified origin/main ee64358b. May this seat hand off on prepr.sh's other 30 steps (all ok, body check included) with CI proving `closures`, or must it wait for a seat whose venv imports homeassistant?

Done at the fix 39f34916 (unchanged first-fixer commit; ref had not moved):
- census block alone (`tools/audit/seat/features_block.py`, block `_CB_SLUGS = set(_cb_const.COMBI_TANK_PRESETS)` to `# R10-BUFFER-STORE review 1`): FAIL at origin/main (vendor: const.py:812, const.py:1595, heat_curve.py:72, pump_arbiter.py:256, pump_arbiter.py:1015, thermal_model.py:1870); `ALL 1 FEATURES BLOCK PASSED` at the fix.
- `tools/audit/seat/mutant_run.py --in-place`, six mutants putting the vendor back on each renamed line: SURVIVED NULL, all six KILLED.
- `git merge-tree --write-tree origin/main HEAD` at ee64358b: no conflict, main not merged.
- prepr.sh: `PRE-PR: 39f34916ab9929ee14c5c63fbdd64ab5298c04e7 0000000000000000000010000000000 rc=1`; the single 1 is `closures`.
