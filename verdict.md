Fix review: blocked d554d42e9a645841ccf87da65d24fb1b6660f9a9 mutation-vacuous: thermal_model.py:1151 TWO_ZONE_FIELDS element delete (CONF_RADIATOR_POWER_FRACTION) survives features.py and entities.py

bus-nonce: 84457bb5c78921fbce948fd298354056

Round 1 (first review of #3925; full scope).

## Block

- Survivor: delete `const.CONF_RADIATOR_POWER_FRACTION,` from `TWO_ZONE_FIELDS` (`custom_components/heatpump_optimizer/thermal_model.py:1151`, a line this diff adds; patch `ev/mut_F.patch`). With that mutant, at the head: the PR's features block prints `ALL 16 FEATURES BLOCK PASSED` (`ev/mut_F.txt`), the full `tests/features.py` prints `ALL 6283 FEATURE CHECKS PASSED` rc=0 (`ev/mut_F_features_full.txt`), and `tests/entities.py` prints `ALL 2791 ENTITY CHECKS PASSED` rc=0 (`ev/mut_F_entities_full.txt`).
- What the mutant does: it brings back the accepted no-op this PR says it fixes. The body's companion probe is the only evidence that `radiator_power_fraction` belongs in the refused set ("why the refused set is the rule's four keys and not the brief's three"). Under the mutant, `set_thermal_parameters` on a mode-off one-zone install accepts `radiator_power_fraction` again, and an auto install holding only that key turns one-zone. Neither change fails a check.
- Why the tests miss it: both the census precondition and the refusal loop take their expected set from `two_zone_from_config`, and that function reads `TWO_ZONE_FIELDS`. So the census compares the constant with itself, and a key removed from the constant also disappears from the refusals the test drives. The block's comment says "a key the rule starts reading is driven the day it lands". That holds when a key is added. It does not hold when one is removed. The finder's harness (`probes_p2.py`) probes only the brief's three fields, so nothing independent pins the fourth key.
- What would kill it: pin the four keys literally, independent of the constant, or drive `radiator_power_fraction` specifically (refused on a mode-off entry, and turns an auto config two-zone). Then show this mutant failing.
- The PR's own `mutant_run.py` list drew 18 mutants and reported no survivor, but it has no tuple-element-delete operator. That explains why this mutant was never drawn. Not checked: whether the same deletion from the inline tuple survived at the base. A base survivor would make the gap older than this PR, but this PR now hangs the refusal on that line.

## Findings

- `_sim_coldest` (`coordinator.py:2643`) filters `plan.upper_temp_trajectory`/`lower_temp_trajectory` by truthiness and ignores the two-zone flag. The body's AST census does not return it, because it is a comprehension `if s` over a local, not a bare attribute. Its output does not depend on topology: on one zone both floor lists hold the room trajectory, so the minimum equals the room's. It is a reader that does not diverge, not a presence decision. Carry: dismissed: no divergence — on one zone the floor lists equal the room trajectory, so min() is unchanged

## Evidence

- RESULT head reviewed: d554d42e9a645841ccf87da65d24fb1b6660f9a9, the same as the PR head and the body's `## Head` (`ev/HEAD.txt`). `git diff $(merge-base)...origin/main -- dev/governance/roles/` is empty, so the roles are current.
- RESULT merge: `git merge-tree --write-tree origin/main d554d42e9a` exits 0 (tree 1768ceccdd), with no conflict.
- RESULT mutation proof re-run (features block, prelude from `features_block.py --emit-prelude`). Unmutated head: `ALL 17 FEATURES BLOCK PASSED` (`ev/block_head.txt`).
  - MUT-A (the refusal call deleted): 5 of 17 FAIL, the 4 refusals plus "wrote nothing" (`ev/mut_A.txt`). Matches the body.
  - MUT-B (`zone_trajectories(True)`): 1 FAIL, rows=96 zoned=96 (`ev/mut_B.txt`). Matches.
  - MUT-C (refusal judged on `effective_config` only): 1 FAIL, the auto null control (`ev/mut_C.txt`). Matches.
  - Reviewer mutants: D (upper/lower swapped) 1 FAIL, the column check (`ev/mut_D.txt`). E (one-zone rows fall back to the room trajectory, the old behaviour) 1 FAIL, the rows check (`ev/mut_E.txt`). F survives (see Block).
- RESULT finder's harness `probes_p2.py` (sha1 5058a46432166867f8e75a5d4846acea20d0b752, from 872510cd3e), run in `git archive` exports:
  - Base fd93aa3e9b: `probes_failed=6 of 10`, with all four zone seams FAIL and 96 of 96 rows zoned.
  - Head d554d42e9a: `probes_failed=2 of 10`; the two left are the DHW weekday seams outside this group.
  - `--perturb`: 0 of 10 at both ends.
  - All three match the body (`ev/finder_*.txt`).
- RESULT `python3 tests/structure.py` at the head: `module_excess_loc 21644 <= 21644`, STRUCTURE RATCHET PASSED. The -2 comes from folding the inline presence tuple into `TWO_ZONE_FIELDS` and sharing one comment, and is earned by the code.
- RESULT VERSION, manifest, RELEASE_NOTES.md and tests/golden: untouched in the three-dot diff. No golden fixture carries an `upper_temp`/`lower_temp` row key (git grep over tests/golden returns nothing), so no claim is owed. I did not re-run `env_drift.py --all`; CI's gate covers it.
- RESULT readers of the row keys: `git grep -E 'upper_temp([^_]|$)|lower_temp([^_]|$)'` over custom_components (www included) and tests finds only the writer (`coordinator.py`), `payload.py`'s annotations and the new features checks. That matches the body.
- RESULT CI: `merge_train.py classify d554d42e9a --pr 3925` printed `WAIT ... pending: gate red: none` from 00:43 to 01:15 UTC (`ev/classify.log`). No owed red was read at this head. The owed-reds set is in `ev/owed_reds.txt`. The body's predicted `tests / mutation` ADDED-UNPINNED red is answered in its `## Red checks`.
- RESULT figures I did not re-derive: the body's `closure.py select` count (28 scripts), the archscore `dS +0.0000`, and the AST census site counts for the head and base.
