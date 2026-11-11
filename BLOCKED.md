# r10-arbiter-off-restore (#3404) pin repair blocked

Mutation-autofix at d7347d0c reported `skip-measure-failed` (MUTATION_RESULT: failure): its measure step could not run, so it pinned nothing and pushed nothing. It is not a survivor and not skip-head-moved.

`python3 tests/mutation_table.py --pin-killed --base origin/main` (7 new sites, 2 files) ends MUTATION TABLE INCONCLUSIVE: the baseline is red in tests/features.py (rc=1, failed=2), the combi_type_branch vendor census, which origin/main already fails (vendor lines const.py:812, const.py:1595, heat_curve.py:72, pump_arbiter.py:268, pump_arbiter.py:1054, thermal_model.py:1870 against an allowance of 4). features.py is the driver that holds the checks killing this PR's mutants, so dropping it from --scripts would pin nothing honestly. No pin was written; no production code changed.

Question: may the pin run wait for PR #3466 (the census fix) to merge into origin/main, after which I merge origin/main (clean today) and re-run --pin-killed, or do you rule another route (e.g. a baseline waiver for the census in the pin run)?
