Fix review: blocked 495f0c65527862aa8acefdc1b3802e36656f881a mutation-vacuous: diag-block-ignored switch-attr (the published block_ignored replaced by constant False in diagnostics.py's external_heat_block_ignore row and in switch.py's ExternalHeatIgnoreBlockSwitch attribute; no test observes it True)

bus-nonce: 5effea7849ae5b4ecfc1531185d5d8be

## Evidence

All at 495f0c65527862aa8acefdc1b3802e36656f881a (ev/HEAD.txt), from a detached worktree, merge base 24e3f37620.

- Mutation proof (step 1), `tools/audit/seat/mutant_run.py --spec --in-place`, NULL first:
  - Spec A, 15 mutants on the PR's production lines, judged by the `#3862` block of tests/features.py through `features_block.py` (ev/mutants_A.log): NULL survives; 13 KILLED; SURVIVED switch-off-false and diag-block-ignored.
  - The two A survivors re-run against tests/entities.py by hand, apply / run / restore, judged on its `#3862` and `ExternalHeatIgnoreBlockSwitch` FAIL lines (ev/manual_B2.log; null: ev/entities_null2.log, the unmutated head, 0 such FAIL lines and 5 `#3862` ok lines): switch-off-false KILLED by "turning the external-heat override on and off moves boost's held flag (#3862)"; diag-block-ignored SURVIVED.
  - Spec B1 against tests/entities.py, `--in-place --timeout 3600` (ev/mutants_B1.log): NULL survives; binsensor-key-guard KILLED; switch-attr SURVIVED. switch-attr against the features.py block (ev/mutants_C_block.log): NULL survives; switch-attr SURVIVED.
- switch-attr: `custom_components/heatpump_optimizer/switch.py` `ExternalHeatIgnoreBlockSwitch.extra_state_attributes`, `return {"block_ignored": bool(published.get("block_ignored"))}` -> `return {"block_ignored": False}`. The only check reading the attribute (tests/entities.py:11810) expects `{"block_ignored": False}` on a fresh coordinator; tests/entities.py:13377 pins the key set only. The repair: read the attribute with the published payload's `block_ignored` True, expecting True.
- diag-block-ignored: `custom_components/heatpump_optimizer/diagnostics.py`, row `external_heat_block_ignore`, `"block_ignored": bool(((c.data or {}).get("external_heat") or {}).get("block_ignored"))` -> `"block_ignored": False`. The only test reading that row is tests/features.py:76250-76261, and both of its rows expect `block_ignored` False (`{"switch_on": False, "block_ignored": False}`, `{"switch_on": True, "block_ignored": False}`). No test drives the row with the override effective, so the published `True` is never observed. The repair: a row read with the switch on, detection enabled and the detector suppressing, expecting `"block_ignored": True`.
- Parity (base vs head on the block's unrelated rows): identical (ev/parity_base.txt, ev/parity_head.txt). Block at head: 20 passed (ev/block3862_head.log).
- `tests/env_drift.py --all` vs merge base: `NO STALE FIXTURE` (ev/env_drift.log), so no claim owed.
- `git merge-tree --write-tree origin/main 495f0c6552`: rc 0 (ev/merge_tree.txt).
- `merge_train.py classify` at 495f0c6552: GREEN, pending none, red none (ev/classify_last.txt).
- VERSION, manifest version and the notes heading: untouched by the diff (ev/prod_diff.patch).
- Step 12: the head moved to dc972220f313ed48b8accd80140ac1182b67b59b during the review, `ci: merge main` only (main through bb6377b4da and #3864). That merge does not touch the diagnostics row or the tests that read it, so the survivor stands at the new head. Every figure above was taken at 495f0c6552; none was re-taken at dc972220f3.

## Findings

- Blocking (tests): diag-block-ignored and switch-attr, above. One added check each repairs them; both are the same gap, the published `block_ignored` True never read through a reader.
- Note: test-host: tests/entities.py fails one unrelated timing self-test (a late-writing descendant) at the head unmutated on this host, so entities runs here are judged on the `#3862` and `ExternalHeatIgnoreBlockSwitch` lines only. The FAIL rows a3:* that print are the script's own negative self-test fixtures.
- Note: instrument: two `mutant_run.py` spec runs against tests/entities.py reported `KILLED NULL` (ev/mutants_B.log at the default 600 s timeout; ev/mutants_B2.log run concurrently with B1 in a second worktree). Rerun alone at --timeout 3600, the NULL survives (ev/mutants_B1.log, ev/ent_runs/). Hence the hand-run B2.
