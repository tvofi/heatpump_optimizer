Fix review: merge e0769b570ebe94ac3200fc420c86ed159c3f5a0c

bus-nonce: 3ceebd90470f80dfba3c033a18e8f5bb
pending-ci: gate

## Evidence

Round 1 (first round: full scope, no reviewed head). Head e0769b570ebe94ac3200fc420c86ed159c3f5a0c, merge base ae0ed64af898d8923ac35afe6e9c031ac1e6b111. The roles diff from the merge base to origin/main is empty, so the contract is current.

- Merge with main: `git merge-tree --write-tree origin/main e0769b57` exits 0 with origin/main at db597604. No conflict.
- Mutation proof (step 1), re-run at the head (`ev/mutants.txt`): mutant A (`if bindings:` -> `if False:`) and mutant B (`module_excess` -> `0 * sum`) each fail exactly the two self-checks the body names, with `2 COUNTING RULE(S) BROKEN`. Further mutants I added: C (drop `asname`) is killed by the aliased-binding check. F (limit +1) and H (`end_lineno` -> `lineno`) are killed by the module self-checks. D (drop the `a.name == "const"` filter) and E (drop the binding-name test) are killed only by the budget row (`const_modules_over_50 6 > 4`), not by a self-check. G (`len(list(...))`) is equivalent. I (drop `node.level == 1` on the binding import) is equivalent: an `ImportFrom` whose module is None must have level >= 1, and the package has no subpackages. J (drop the absolute `heatpump_optimizer.const` arm) survives, but that arm is unchanged from the old rule, and no module in the tree uses that spelling. Restored tree: `ok 80 counting rules hold`.
- Finder's harness (step 2): plan/r11 819aa2e354 `dev/audit/rounds/round11/D7/s1/m1_ratchet_census.py`, sha1 e2f94c69129a1e2840e5b4b83e67dab96b576f7b, matching the body. I ran it at both ends with perturbations none, const-respell and module-growth (`ev/harness-*.txt`). Every figure the body quotes reproduces:
  - Base: ratchet 3, any_spelling 4, const_unseen 1. Under const-respell the ratchet goes to 2. Under module-growth, unpriced goes 2986 -> 4409 with rows_off_budget 0.
  - Head: ratchet 4, const_unseen 0. Under const-respell it stays at 4. Under module-growth, module_excess_loc goes 21549 -> 22972, rows_off_budget 1.
  - `recount_mismatches=1` at the head is the harness's old from-import recount, as the body states.
- Figures (step 8), re-derived:
  - `tests/structure.py` at the head reads `const_modules_over_50=4` and `module_excess_loc=21549`, both at budget, rc 0 (`ev/structure-head.txt`).
  - The head's rule run over the base tree reads the same 4 and 21549 (`ev/structure-headrule-on-base.txt`), so recording at ae0ed64af8 is honest. The base's own rule reads 3.
  - An independent AST recount gives 21549 over 8 modules (`ev/indep-module-excess.txt`).
  - The four modules over the const limit, 424/135/120/100, match the body's list.
  - archscore `--diff <merge base> HEAD` reads `dS +0.0000 NULL` (`ev/archscore-mb.txt`). The body's two-dot `--diff origin/main HEAD` now reads +0.0012, an artifact of main's newer commits (`ev/archscore.txt`).
- Step 5: VERSION, the manifest and RELEASE_NOTES.md are untouched (`ev/version-untouched.txt`). No golden or claim file moved, so step 4 has nothing to compare.
- Step 14 (raise): the const row's move from 3 to 4 is earned. Removing `const_names_read`'s binding arm (mutant A) returns the tree to 3, and the move comes from entry_config.py's 120 binding reads. I found no payment the body missed: entry_config.py owns its configuration reads. `module_excess_loc` is a new row recorded at its measured value. Owner approval at the head is `budget-raise-gate`'s, which follows this verdict. The quoted ruling of 2026-11-18 is not in RULINGS.md on origin/main, but the gate's approving review is the binding record.
- Steps 10 and 16: the forward-carry is `none`, and there is no actuator path in the diff. Step 15: the added lines are test instruments only, with nothing under `custom_components/`.
- Step 7: the body names e0769b57 as the head, and the PR's head ref reads e0769b57. The body's measurements were taken at 045f358a. e0769b57 adds only `dev/programme/delivery/3735.md`, and I re-took the figures at e0769b57.
- CI: `merge_train.py classify` still printed `WAIT e0769b570ebe94ac3200fc420c86ed159c3f5a0c pending: gate red: none` after polling from 15:21 to 15:55 UTC (`ev/classify-last.txt`). No red at this head. The only owed red the body anticipates, `budget-raise-gate`, waits on the owner's approval.
- Note: harness: the finder's harness lives only on plan/r11 (819aa2e354), not in the tree at this head. It is cited by sha1, and I ran it from that commit.

## Findings

- Follow-up: `const_names_read` still misses absolute spellings of the package, such as `from custom_components.heatpump_optimizer import const` and `from custom_components.heatpump_optimizer.const import X`. Planted at the head, rewriting entry_config.py's `from . import const` to the absolute form drops the row 4 -> 3 with the coupling unchanged (`ev/plant-absolute-respell.txt`). That is the re-spelling class D7-s1-01 closes, through a neighbouring spelling. No module uses that spelling today, so this is an instrument finding, not a block of this change. Mutants D and E are killed only by the live budget and not by a self-check, so the counting rule's name filter is unpinned. Carry: dismissed: no live roster group owns structure instruments and the spelling is absent from the tree, so the orchestrator should route it to the plan seam R11-SEAM-instruments
