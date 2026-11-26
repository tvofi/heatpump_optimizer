Fix review: merge 2b85f00206359887d28726af32d593baf120aae3

bus-nonce: 03dced486a569547eec42d14a256adde
pending-ci: gate

## Findings

none

## Evidence

- Scope: no verdict on `verdict/3883` names fe5ff1cc (its only verdict is the block at ef591eaa), so this review covers `git diff ef591eaa 2b85f002` net of main. That is the diff from `git merge-tree --write-tree origin/main ef591eaa` (tree 0ef14edeac) to the head. Production delta: `pump_arbiter.py` only. The conflict hunks are resolved as the union of both sides:
  - one `from . import` line carrying both `flow_anchor` and `flow_limit`;
  - main's `heat_c` under `_space_limit_c` kept, with the branch's settled `floor_c`.
  - The three-dot diff drops main's unused `quantise_setpoint_c` import. Nothing else in the head references it.
- The prior block is resolved. Mutant m3 (`_pass_record`: `_settle(held, inp)` -> `held.served`, `ev/mut_m3.diff`) is KILLED, from my own full run of `tests/features.py` at the head with the mutant applied:
  - result: `1 of 6235 FEATURE CHECKS FAILED`, rc=1;
  - the failing check: `STEP-KICK T6b: through _arbitrate, a system-identification step and a return target on the swap pass record the unsettled floor ...`, with `(swap, no swap) floors: {'flow': (34.0, 59.0), 'probe': (34.0, 59.0), 'return': (34.0, 59.0)}`;
  - the unmutated baseline: `ALL 6235 FEATURE CHECKS PASSED`, rc=0 (`ev/mut_m3.txt`, `ev/features_base_tail.txt`).
- The three hand resolutions are in merge 80d15ad8c0 (parents fe5ff1cc and 8f22a3b284). Each is a union, judged against the conflicted `git merge-tree fe5ff1cc 8f22a3b284`:
  - `tests/features.py`: the whole R11-OWNER-STEP-KICK block and the whole #3616 R11-OUTSIDE-ROOMS-3B block are kept, in that order. The only edits are the dropped markers and the block's closing `)`.
  - `tests/deployment_shape.py`: the count is now 124. The branch's `flow_anchor.py` clause (123) is added ahead of main's `comfort_floor.py` clause (122), and main's full history is kept. The branch's superseded "182 on main before the merge" clause is replaced by one recording 184 on main and the six pairs the merge joins. Nothing else from main is lost.
  - `dev/audit/rounds/round4/D6/claims.py`: 105, the branch's `flow_anchor.py` clause added on top of main's `comfort_floor.py` history.
  - The later merge 2b85f002 of main dbdc71fa is clean, and the head is now based on origin/main.
- Figures, re-derived at the head (`ev/pairs.txt`, `ev/claims_out.txt`, `ev/gates.log`):
  - 105 top-level package `.py` modules and 124 tracked package files (`git ls-tree`).
  - HA-free: 105 - 36 - 1 = 68.
  - Closure pairs: 190 of the 561 pairs reach the 0.80 Jaccard floor, by the `_d308_pairs` predicate in `tests/entities.py`, against 184 at origin/main. The six joined pairs are exactly the six the note names, and no pair leaves.
  - `claims.py` prints `arch_modules_on_disk=105`, `arch_map_listed=105` and `claims_false=0`, and running it leaves the tree clean.
  - `doc_claims.py`: ALL 443 checks PASSED. `deployment_shape.py`: ALL DEPLOYMENT SHAPE CHECKS PASSED.
  - `structure.py`: STRUCTURE RATCHET PASSED, rc 0, with nothing re-recorded.
- Budgets: `tests/structure_budgets.json` against origin/main moves `module_excess_loc` 21753 -> 21745 and `unloaded_package_imports` 5 -> 4. Both fall, so no budget rises. `tools/audit/archscore/score.py --diff origin/main` prints `Architecture score: dS +0.0000 NULL` (`ev/archscore.txt`).
- Pins: f57bc5a34e is authored and committed by github-actions[bot] (`ci: pin killed mutants`, 14 added files). The 14 files are byte-identical at the head (`git diff --quiet f57bc5a34e 2b85f002 -- <paths>`). The three-dot ledger delta is those 14 adds plus one deletion, `_space_target.RETURN_DEL.628d75e4`. That deletion is the branch's own earlier commit 497f9c1954, reviewed at ef591eaa: its pinned line moved to `settle=settle`, and the bot re-pinned that line as `4dd771a4` (`ev/pins.txt`).
- Merge: `git merge-tree --write-tree origin/main 2b85f002` exits 0 (tree 75e4da3f2e; origin/main dbdc71fa).
- Not re-run: the finder's harness `dev/audit/harnesses/r11_owner_step_kick.py`. This round's delta leaves `flow_anchor.py` unchanged.
- CI: after about 30 minutes of polling, `merge_train.py classify 2b85f002 --pr 3883` still prints `WAIT 2b85f00206359887d28726af32d593baf120aae3 pending: gate red: none` (`ev/classify-last.txt`). No context is concluded red. The owed-reds set is `tests / coverage-ratchet`, `tests / fast (3.14)`, `tests / mutation`, `tests / typing` and `validate / validate-hacs`. The verdict is returned as `pending-ci` for the relay.
