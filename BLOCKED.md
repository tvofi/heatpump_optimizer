# BLOCKED: r10-hotfix-combi-census-main-red

Question: `tools/pr/prepr.sh` refuses one step, `closures` ("failed while being recorded: tests/entities.py (exit 1)"), and the cause is the seat's environment: `/opt/hpo/venv-ci/bin/python3` has no `homeassistant`, so `tests/harness.py:25` raises `ModuleNotFoundError` -- identically on unmodified origin/main ee64358b. May this seat hand off on prepr.sh's other 30 steps (all ok, body check included) with CI proving `closures`, or must it wait for a seat whose venv imports homeassistant?

Done at the fix 39f34916 (unchanged first-fixer commit; ref had not moved):
- census block alone (`tools/audit/seat/features_block.py`, block `_CB_SLUGS = set(_cb_const.COMBI_TANK_PRESETS)` to `# R10-BUFFER-STORE review 1`): FAIL at origin/main (vendor: const.py:812, const.py:1595, heat_curve.py:72, pump_arbiter.py:256, pump_arbiter.py:1015, thermal_model.py:1870); `ALL 1 FEATURES BLOCK PASSED` at the fix.
- `tools/audit/seat/mutant_run.py --in-place`, six mutants putting the vendor back on each renamed line: SURVIVED NULL, all six KILLED.
- `git merge-tree --write-tree origin/main HEAD` at ee64358b: no conflict, main not merged.
- prepr.sh: `PRE-PR: 39f34916ab9929ee14c5c63fbdd64ab5298c04e7 0000000000000000000010000000000 rc=1`; the single 1 is `closures`.

## Second seat, same head 39f34916: a second cause, reproduced on main

In this container venv-ci imports homeassistant, and the `closures` refusal still fires. Here it comes from an environment leak. prepr.sh exports HPO_GATE_PRIORITY (its "gate priority" step printed 2), and two self-checks in tests/entities.py read it:
- `gate lease priority: priority: an urgent waiter takes before an older normal one, after its ticket rewrite`
- `gate lease priority: priority: the heavy-slot pool orders by the same rule`

Both report order=['normal', 'urgent']. Evidence:
- `HPO_GATE_PRIORITY=2 PYTHONPATH=tests/hastub python3 tests/entities.py` exits 1 with "2 of 2707 ENTITY CHECKS FAILED", both at cbd23f1c8 (unmodified main) and at 39f34916.
- Without the variable, `tests/derive_closures.sh --record-only` records tests/entities.py with rc 0, alone and in the 27-script lane run.
- prepr.sh's own recording, captured before it deleted its temporary files: entities.py.out ends "2 of 2707 ENTITY CHECKS FAILED", with these same two checks.

The second cause is a test-isolation defect in tests/entities.py or prepr.sh. It is not in this diff, and fixing it falls outside this hotfix's census lines. The same question stands.

Also at 39f34916: `GATE_SCOPE=auto GOLDEN_MODE=drift PYTHONPATH=tests/hastub bash tests/run.sh` exits 0, with 31 scripts passed and 3 scoped out.
