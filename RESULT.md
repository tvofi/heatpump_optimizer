# merge-3845 result (PR #3845, R11-SEAM-cycle-reporting)

- New head: `dcdb80d9745b855ebdbcfa518b56b2c811638bf9`, pushed to `refs/heads/handoff/r11-seam-cycle-reporting`
  (force-with-lease over `753065db`: same parents d13c3e84 + f52e700d as the branch's own merge, tree identical to b3c29891 by `git diff --stat b3c29891 753065db` printing nothing).
- Merged: `origin/main` at `6a58ba5cb30bf231dd7c6f60c42dc0d7583cb699` into `b3c29891ebc2987c574ee0fd7c6601eb5f092a03`; measured 2026-11-25T11:29Z.
- Reviewer's resolution delta: `b3c29891ebc2987c574ee0fd7c6601eb5f092a03..dcdb80d9745b855ebdbcfa518b56b2c811638bf9` (one merge commit; no further commits).

## Resolution per file

| file | how |
|---|---|
| tests/features.py | textual conflict: both sides appended a section at the tail before `sys.exit(R.close(...))` (branch: R11-SEAM-cycle-reporting checks; main: R11-OWNER-CARD-EXTERNAL-HEAT suffix contract). Union, branch section first, each R.check closed. `ast.parse` clean. |
| tests/structure_budgets.json | ledger driver (base + both deltas): class_excess_loc 17293, module_excess_loc 21762, max_class_loc 7833 from main. Re-measured by `tests/structure.py`: every budget key equal to its measured value; no raise. STRUCTURE RATCHET PASSED. |
| tests/closures.json | ledger driver union; then `tests/derive_closures.sh --scripts-from` (partial merge, Linux strace) re-recorded the three test scripts both sides changed (features.py, entities.py, doc_claims.py): file byte-identical after the re-record (`git diff` empty), i.e. the union already covered every measured read. entities.py: 3 committed files not re-read, kept by the partial merge. |
| duty_switch.py, optimizer.py, doc_claims.py, entities.py | auto-merged. |
| mutation_ledger killed_by | main-only additions, no conflict; both sides' pins kept. |
| dev/audit/rounds/round4/D6/claims.* | not touched by either side; no regeneration needed; gate left the tree clean. |

Read-back (orchestrator.md s6): for each of the 5 files both sides changed, every line each side added vs the merge base f52e700d is present in the merged file: 0 missing in all 10 (file, side) pairs. Null control: the same check of the branch's features.py lines against main's unmerged features.py reports 328 missing.

## Gate

`GATE_SCOPE=auto GOLDEN_MODE=drift GOLDEN_REF=$(git merge-base origin/main HEAD) ./tests/run.sh` at dcdb80d9:
- `MODE: SCOPED -- 29 script(s) run, 5 scoped out.` (layout.py ran as run_always)
- `31 TEST SCRIPT(S) PASSED; 4 SCOPED OUT AND NOT RUN`, rc=0. Not run: frontend.py, ha_contract.py, md_tables.mjs, open_meteo.py (no changed file in their measured closures).
- `python3 tests/structure.py`: STRUCTURE RATCHET PASSED.
- `node tools/policy/brief_lint.mjs`: exit 0.
- No red caused by the merge; no red to name on main.
