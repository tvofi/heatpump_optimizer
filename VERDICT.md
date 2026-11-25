Fix review: merge 54a978b52ab8554954e627f0c35225e5215493e0

bus-nonce: b463ed1bbedf6f6d0fe1355fc087d81c
pending-ci: gate

## Scope

Delta round over the reviewed head 495f0c65527862aa8acefdc1b3802e36656f881a (my blocked verdict there: two mutation-vacuous published-flag reads, the diagnostics row's `block_ignored` and the override switch's `block_ignored` attribute). The PR's own commits since then are b4b8d88a8d (two checks, tests only) and 80412b13b2 (structure budget recorded down); 28fa42f78c, dc972220f3 and 54a978b52a merge main. No production (`custom_components/`) line changed in the PR's own delta, so the scope is not widened. The packet's `## Review scope` line reads `full` only because the earlier verdict returned on a probe ref, not on `verdict/3874`; the dispatch scopes this round as a delta.

## Evidence

- RESULT survivor diag-block-ignored: KILLED. Mutant `diagnostics.py:387` `"block_ignored": False` (ev/mutant_diag.diff): `tests/features.py` exits 1, `1 of 6192 FEATURE CHECKS FAILED`, the one failure the new check `diagnostics report the switch on and, with detection enabled, effective (#3862)  [{'switch_on': True, 'block_ignored': False}]` (ev/features_mut_diag.log.gz).
- RESULT survivor switch-attr: KILLED. Mutant `switch.py:253` `return {"block_ignored": False}` (ev/mutant_sw.diff): `tests/entities.py` exits 1, `1 of 2770 ENTITY CHECKS FAILED`, the new check `the external-heat override switch reports block_ignored true once the payload publishes it (#3862)  [{'block_ignored': False}]`. Against the head run, the only added FAIL line is that one; the other FAIL lines are negative-control self-test output and appear at head too (ev/entities_mut_sw.log.gz, ev/entities_head.log.gz).
- RESULT head: `tests/entities.py` `ALL 2770 ENTITY CHECKS PASSED`; in `tests/features.py`, all three #3862 diagnostics checks (null, switch-on with detection disabled, and the new effective case) print `ok`. My head features run hit its 900 s timeout (rc=124) while it ran alongside the other runs, after printing 0 FAIL lines. The 1200 s mutant run covers the whole file: it differs from head by one production line, and only the targeted check failed out of 6192.
- RESULT the two new checks are not vacuous: each one drives the true value through the production read it pins (the diagnostics row on a coordinator whose published `external_heat` view carries `block_ignored` true, and the switch built by `collect()` over a payload carrying `block_ignored: True`) and asserts equality to `True`.
- RESULT structure: `tests/structure.py` rc=0 at head, `ok class_excess_loc 17283 <= 17283` (ev/structure_head.txt). 80412b13 lowers a budget, which the ratchet allows, and its commit message gives the reason.
- RESULT merge: `git merge-tree --write-tree origin/main 54a978b5` writes tree 19d67db7b6 with no conflict (ev/merge_tree.txt).
- CI: `merge_train.py classify 54a978b52ab8554954e627f0c35225e5215493e0 --pr 3874` printed `WAIT 54a978b52ab8554954e627f0c35225e5215493e0 pending: gate red: none` (rc=3) on every run 16:26-16:54 UTC; returned with `pending-ci: gate` per the brief (ev/classify.txt).
