Fix review: merge 1dd030c424ec0b81274287d65ef2ba084e40702d

bus-nonce: eba217a04df73022ee59ecd42633ea3a

## Round

Round 4, a delta review over the reviewed head 10d8f0433b00382ac991373f3eb2feaeaec57500 (packet `## Review scope: delta`). Measured from a detached worktree at 1dd030c424ec0b81274287d65ef2ba084e40702d; origin/main and merge base e23124ff6e45bac1d48b4a775dad555a37965355. `git diff <merge-base>...origin/main -- dev/governance/roles/` is empty. The verdict is `merge`, so the re-cut `fix-review.md` makes owed from the fourth round does not arise.

Do the three earlier blocks share a cause that re-cutting the body or the approach would remove? Not one cause:
- The round-2 blocks were about substance: the class seams, the stepped grid and the rule's variants. They were answered in the code and are not repeated here.
- The `main-conflict` on `tests/deployment_shape.py` came from this branch's `tests/block_duty.py` check building a coordinator. That grew the script's closure, so the branch had to hand-edit the selection-cost note. `main` edits the same prose paragraph whenever a closure moves. The conflict came back in this round's main merge (efe1ae593c, resolved, below). This is my inference and I did not measure it: a re-cut that put that coordinator check in a script whose closure already reads the coordinator would not have moved the note.
- The `ci-red` on `tests / mutation` came from the old `while` loop, which only advanced through its own guard. This round's rewrite removes that cause. No body re-cut would have.

## Evidence

- The previous verdict's one block is resolved. `merge_train.py classify 1dd030c424ec0b81274287d65ef2ba084e40702d --pr 3531` exits 0 with `GREEN 1dd030c424ec0b81274287d65ef2ba084e40702d pending: none red: none` at 20:26:03 UTC, after 10 WAIT lines (ev/ci-poll.txt).
  - Check runs read from the commit's `check-runs` API (ev/check-runs.txt): `tests / mutation` success (job 132125817973), `gate` success (jobs 132147069862 and 132147695121), `pr-contract / pr-contract` success (job 132146473627, started 20:22:54, after the last red concluded).
  - The digest's earlier `gate` failure, job 132126626236, has no output title. classify read it as pending and it was superseded by the green `gate` runs.
- The previous verdict's finding (the stale `## Head` account of main) is resolved. The body's `## Head` names 1dd030c424ec0b81274287d65ef2ba084e40702d, its code head 667a8c8302 and merge base e23124ff6e, and its figures use that base.
- The red is answered. The body's `## Red checks` names `tests / mutation`, `tests / mutation-autofix` and `gate` at 10d8f0433b with the measured cause (the pin drive's mutant timed out). It names the cheaper detector, `prepr.sh`'s timed-out draw, and records that no check is built. `tests / mutation` is in the set `merge_train.py owed-reds` prints (`tests / mutation`, `tests / typing`, `validate / validate-hacs`), so this answer is owed and present. No red stands at this head.
- The production delta is `custom_components/heatpump_optimizer/dhw_planner.py`, where `drop_unstartable`'s `while` loop becomes `for i in np.flatnonzero(on[1:] & ~on[:-1]) + 1:`.
  - The PR's patch over `custom_components/` at e23124ff6e...1dd030c424 differs from the patch reviewed at 154dbb4c61...10d8f0433b only on those lines (ev/patch-delta-custom_components.txt).
  - Equivalence, with my own script (ev/equiv.py, seed 3531; the tank model depends on the mutated plan, so drop order matters): `RESULT plans=20000 old_vs_new_differ=0 old_vs_control_differ=10540`. The control is the variant that judges every on-step as a start. The body's own 0 of 20000 and 7592 come from its scratch probe, which is not in the tree, so I did not re-derive them. Mine is an independent equivalent result.
  - By reading: `on` is computed once and never updated, and the old loop jumped to `end`, the first off-step after a start. So the starts it visited are exactly the rising edges at index 1 or later, in the same ascending order. A run at step 0 is excluded in both versions, and sizes 0 and 1 give an empty loop.
- Widening checked and not needed. Main's merge brings `_with_placement_ban` into `dhw_planner.py`, OR'd into `forced_off` at the planner's line 1208. The PR's `place_startable` repair receives that same `forced_off` (line 1308), so a re-bought charge cannot land in a banned step. Nothing in already-reviewed code is at a risk CI would miss, so the scope was not widened.
- Step 1, the mutation proof at this head. `python3 dev/audit/harnesses/r10_dhw_start_hysteresis_mutants.py <worktree at the head>` prints 43 KILLED lines and no ANCHOR line, including the three ported ones:
  - `M16 ... KILLED rc=1 3 failing`
  - `M19 ... KILLED rc=1 1 failing`
  - `M20 ... KILLED rc=1 1 failing`
  - The null: `NULL comment-only change: SURVIVED rc=0 0 failing`.
  - The worktree's HEAD read after the run is 1dd030c424ec0b81274287d65ef2ba084e40702d (ev/mutants-named.txt).
- Step 14, the ledger delta (commit 9ee6926234) removes only the pin of `drop_unstartable.CMP_BOUND.e34a7b90`. That pin's site, `while i < plan.size:`, no longer exists, so the removal follows from the change. CI's `tests / mutation` is green at this head and `mutation-pins` was skipped.
- The ratchet row: `class_excess_loc` is 17514 at origin/main and 17503 at this head (ev/budget-row.txt). `python3 tests/structure.py` prints `ok class_excess_loc 17503 <= 17503` and `STRUCTURE RATCHET PASSED` (ev/structure.txt). That is the same 11 earned in rounds 2 and 3, now resolved by the ledger-merge driver (`17522 + both deltas = 17503`).
- The note's counts, from my own script applying `tests/entities.py`'s `_d308_pairs` rule to `git show <ref>:tests/closures.json` (ev/pairs.py, ev/pairs.txt):
  - origin/main e23124ff6e: `at_floor=154 of 528 comparable=406 prod_files=110 block_duty=74`
  - this head: `at_floor=162 of 528 comparable=406 prod_files=110 block_duty=91`
  - Nine pairs joined, all with `tests/block_duty.py` and the nine scripts the body names. One pair left: `tests/block_duty.py` with `tests/card.mjs`.
  - Every figure equals the body's and the resolved note's `74 to 91`. The tracked judge agrees: `ALL 2711 ENTITY CHECKS PASSED` (ev/entities.txt).
- The main merge efe1ae593c, checked with `git show --remerge-diff`, differs from the automatic merge on `tests/deployment_shape.py`'s note only. The drivers print `LEDGER-MERGE: resolved` for `tests/structure_budgets.json` and `tests/closures.json`. 1dd030c424 is an automatic merge (its remerge-diff is empty). `tests/deployment_shape.py` prints `ALL DEPLOYMENT SHAPE CHECKS PASSED` (ev/deployment_shape.txt).
- Step 13: `git merge-tree --write-tree origin/main 1dd030c424ec0b81274287d65ef2ba084e40702d` exits 0 with tree 70849d141cd35bcccf6f829ecd14e15b5de02508 (ev/merge-tree.txt). The head's merge base is origin/main.
- Step 5: VERSION, RELEASE_NOTES.md and the manifest are untouched in e23124ff6e...1dd030c424 (`git diff --stat` of the three prints nothing).
- Steps 7 and 12: `git ls-remote` at the time of writing gives 1dd030c424ec0b81274287d65ef2ba084e40702d for the branch and for refs/pull/3531/head, and e23124ff6e for main (ev/ls-remote.txt).
- Step 10: the packet's `carry_audit at the head` reports 4 finding items: 4 routed, 0 unrouted, 0 bad destinations. All four are `dismissed:`, so there is no roster carry to open.
- Not re-derived:
  - the body's harness RESULT figures this round. They were re-taken in round 3, and the body re-took them at 9ee6926234. Its `--hysteresis 4` plan_sha1 is unchanged from round 3, which is consistent with the equivalence result above.
  - the body's `prepr.sh` draw.
  - the scoped-gate run, which is CI's and was green.
- Step 4, claims: `python3 tests/env_drift.py --all e23124ff6e45bac1d48b4a775dad555a37965355` prints `NO UNCLAIMED DRIFT: 56 scenario(s) checked` and `NO STALE FIXTURE: 56 committed fixture(s)`, rc 0 (ev/env_drift.txt).
- `python3 tools/audit/archscore/score.py --diff e23124ff6e45bac1d48b4a775dad555a37965355` prints `Architecture score: dS +0.0000 NULL` (ev/archscore.txt).
- `python3 tools/pr/ci_predict.py` prints `CI PREDICT: no closures, fast, governance or instrument red predicted against e23124ff6e45` (ev/ci_predict.txt).
