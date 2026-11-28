Fix review: merge 19d895a6665f02afb1c94cab7a63d2a704882dfe

bus-nonce: e61caca423f70b632aeac38451a510fd

## Findings

none

## Evidence

- Round: this is a delta round over the reviewed head bcf46f6fb0544871f559837d38d10c2b4dfc194c, whose verdict was merge and had no findings, so no prior finding remains to resolve. `review_carry.py bcf46f6fb0 19d895a666` printed FRESH-REVIEW, because `tests/structure_budgets.json` is not main's merge of the reviewed head (`ev/review_carry.txt`).
- The delta has four branch-only commits: b4fe92313 (the bot's main merge), 2f97eb4273 (authored), 286f06b8b1 (a merge of that commit) and 19d895a666 (a merge of origin/main 265e061f65). To compare, I took the three-dot patch at the reviewed head (base e84856520d) and the one at this head (base 265e061f65), with index lines stripped (`ev/branch_diff_delta.txt`). Two things moved beyond hunk offsets:
  - `pump_arbiter.py`: the branch's removal of `quantise_setpoint_c` from the `.inputs` import left the patch. Main's f99ae8a4ef (#3931) made the same edit (`git diff e84856520d 265e061f65 -- pump_arbiter.py` is only that hunk). Main touched nothing else in `pump_arbiter.py` and nothing in `flow_anchor.py`. So the branch's production diff is byte-identical to the reviewed one.
  - `tests/structure_budgets.json`: the branch now changes only `module_excess_loc`, 21607 -> 21599, the same -8 as at the reviewed head. 2f97eb4273 restores `unloaded_package_imports` from -1 to 0, which is main's value, so the row leaves the patch. Nothing rises (`ev/budgets_branch_diff.txt`). `python3 tests/structure.py` at the head prints STRUCTURE RATCHET PASSED, with `ok module_excess_loc 21599 <= 21599` and `ok unloaded_package_imports 0 <= 0` (`ev/structure_head.txt`).
- Widening (step 12): none is owed. The production delta is empty; main's only overlapping production edit is the identical import line. At this head, `git grep` finds no reference to the moved symbols `FLOW_INLET_KEYS`, `RETURN_SKIPPED_RUNG` and `SPACE_SIDE_KEYS` other than through `flow_anchor` (in `pump_arbiter.py`, `tests/features.py` and the harness).
- Mutation proof, re-run at the head (`ev/mutant.txt`): I changed the last line of `flow_anchor.settled_inlet_c` to `return live_c`, which removes the fix.
  - Under the mutant, the R11-OWNER-STEP-KICK features block (`features_block.py`, prelude from `--emit-prelude`) read `6 of 55 FEATURES BLOCK FAILED`: T1, T4, T5, T8, end to end and T6b (`ev/block_mutant.txt`).
  - With the line restored it read `ALL 55 FEATURES BLOCK PASSED` (`ev/block_head.txt`).
  - `tests/guard_pins.py` stays rc 0 under this mutant: its ledger row pins only `anchor_c`'s BOOLOP. The features block is what kills this line (`ev/guard_pins_mutant.txt`).
- Harness `dev/audit/harnesses/r11_owner_step_kick.py` (`ev/harness_head.txt`, `ev/harness_mutant.txt`):
  - At the head, rc 0: `hot_inlet_after=0`, `i1_violations=0`, `i2_violations=0`, `leg_r_pass=True`, `perturb_raise_delta=5`, `perturb_lower_delta=-5`, `soak_null_pass=True`.
  - Under the mutant: `hot_inlet_after=40` and `leg_r_pass=False`. This matches the body's control (0 -> 40).
  - The harness is the design's harness. Its leg R on the owner's bundle stays carried as the body states (Carry 0, R11-OWNER-STEP-KICK).
- Merge: `git merge-tree --write-tree origin/main 19d895a666` exits 0 against origin/main cb2026c3b5 (`ev/merge_tree.txt`). LEDGER-MERGE resolved `tests/structure_budgets.json` (`module_excess_loc` 21607 + both deltas = 21592) and `tests/closures.json`. The PR's `mergeable_state: dirty` is GitHub's view, computed without the drivers (step 13).
- VERSION, `manifest.json`, `RELEASE_NOTES.md` and both claim files are absent from `git diff $(git merge-base origin/main HEAD)...HEAD`.
- carry_audit at the head (packet): `CARRY-AUDIT: 6 finding item(s): 6 routed, 0 unrouted, 0 bad destination(s)`.
- Live checks at the head (check-runs API, read 08:35 UTC):
  - Every context in `merge_train.py owed-reds` (`ev/owed_reds.txt`) is success in run 46113949137, including `gate` (job 140919540589).
  - The only red is `tests / nightly-status`, which is not an owed red, so no answer is owed.
  - `merge_train.py classify 19d895a666 --pr 3883` exited 0 at 08:41 UTC with `GREEN 19d895a6665f02afb1c94cab7a63d2a704882dfe pending: none red: none`, after the re-run `gate` job (run 46113949797) concluded (`ev/classify.log`).
