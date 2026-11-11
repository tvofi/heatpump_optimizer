Fix review: merge 39f34916ab9929ee14c5c63fbdd64ab5298c04e7

bus-nonce: 585c7b1e430d5806ab836d254f82814a

## Evidence

- Round 1, handoff review at tip 39f34916ab9929ee14c5c63fbdd64ab5298c04e7 (body ref handoff-body/r10-hotfix-combi-census-main-red at 31a76f06, whose Code: line and ## Head name this tip). No pull request exists yet, so there is no review packet and no CI run to read; the check-run state is unread, not green.
- Role contract current: `git diff $(merge-base)...origin/main -- dev/governance/roles/` prints nothing.
- Merge: `git merge-tree --write-tree origin/main 39f34916ab9929ee14c5c63fbdd64ab5298c04e7` exit 0, tree 787478f3, no conflict (ev/merge_tree.txt). origin/main is ee64358b, as the body states; the merge base is cbd23f1c.
- Finder's harness (the `combi_type_branch` census in tests/features.py, run alone through tools/audit/seat/features_block.py from `_CB_SLUGS = set(` to the next block, with the block's imports and `_cb_pkg`/`_cb_trees` as preludes), my run (ev/census_three_ends.txt, ev/census_*.txt):
  - RESULT origin/main ee64358b: FAIL, vendor lines const.py:812, const.py:1595, heat_curve.py:72, pump_arbiter.py:256, pump_arbiter.py:1015, thermal_model.py:1870. These are the six lines the body names.
  - RESULT merge base cbd23f1c: FAIL, the same six lines.
  - RESULT head: `ALL 1 FEATURES BLOCK PASSED`.
- Mutation proof, re-run by me (ev/mutants.txt). A null run on the unmutated head gives rc 0. Six mutants each put the vendor name back on one renamed line: const.py x2, heat_curve.py, pump_arbiter.py x2 and thermal_model.py. All six were KILLED (rc 1) and the tree was restored clean. The diff changes only comments and docstrings, so CI's `mutation` lane will draw no production mutant from it (`changed_lines`). These targeted mutants are the proof.
- Step 14, base 4 -> 0: earned. Main at base 4 with the six lines present fails, which is the planted movement without the mechanism. At base 0 a single vendor line refuses, as every mutant shows.
- Class enumeration, the census rule (`_CB_VENDOR` over `_cb_pkg.glob("*.py")`): `git grep -niE` with the same regex over the package's `*.py` at the head returns nothing. The package has no Python subdirectory that the non-recursive glob would miss. Matches remain only in strings.json and translations/{de,en,sv}.json (ev/class_enum.txt). They are outside the census's stated domain ("the package's Python"), and the body excludes them explicitly. See Findings.
- No other pin on the base: tests/entities.py:4213 registers the check by name, and nothing else reads `_CB_VENDOR_BASE`.
- tests/structure.py at the head: `STRUCTURE RATCHET PASSED` (ev/structure_head.txt).
- VERSION, the manifest, RELEASE_NOTES, both claim files and every *_budgets.json are untouched. The diff touches 5 files: 4 package modules (comments only) and tests/features.py.
- Red checks: `merge_train.py owed-reds` includes `tests / fast (3.14)` (ev/owed_reds.txt). The body's ## Red checks names `tests / fast` and answers it with a cheaper detector (features_block.py, seconds) and a process state. That satisfies the trigger. No other red can be read until the PR's CI runs.
- Figures: the body quotes none beyond the six-line list, which I re-derived above. Forward-carry: none claimed, and none is owed.
- The fixer handed off under PREPR_SKIP_CLOSURES=1 by the orchestrator's ruling. That is not judged here. CI's `tests / closures` proves that step once the PR opens.

## Findings

- Out of scope: strings.json and translations/{de,en,sv}.json still name the vendor at keys space_setpoint_unit, space_setpoint_power_feedback, heat_curve_displace_entity, heat_curve_offset_band_k and heat_curve_persistent_band_k. The census by design reads only package Python, and this hotfix deliberately leaves translated strings alone, so the main-red fix is complete without them. Carry: dismissed: outside the census's stated domain (package Python) and outside this main-red hotfix; user-facing translated text is not the census's class
