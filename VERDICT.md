Fix review: merge cbd6e64df9e8ae00214ea162a5f587a2ba074339

bus-nonce: 9581c4b217eea29ed482175f2b2a6a60
pending-ci: gate

## Findings

none

## Evidence

- Scope: this is a delta review over the reviewed head 2b85f00206359887d28726af32d593baf120aae3. That verdict was `merge` with no findings, so there is no prior finding left to resolve. I compared the PR's three-dot diff at the old head (merge-base dbdc71fa) with the one at the new head (base 190ffb10, an ancestor of the head), file by file (`ev/delta.txt`).
- What changed in the branch's own diff:
  - `dev/audit/config/scopes.json`: commit 9740b9e336 re-cuts D5 seat s7 to `tests/fe*` and moves `tests/finite_boundary.py` and `tests/frontend.py` to s8. It is a cherry-pick of 7df39f349a, which is now on origin/main, and the two diffs are byte-identical (`ev/delta.txt`, `ev/scopes.diff`).
  - `docs/architecture.md`: only the `flow_anchor.py` map entry is left. The branch's literal module-count edits (104 -> 105, 67 -> 68) are gone, because main no longer carries those literals.
  - `tests/deployment_shape.py` and `dev/audit/rounds/round4/D6/claims.{py,json,md}`: these left the diff for the same reason. Main's newer text supersedes the branch's count clauses.
  - `tests/structure_budgets.json`: still only falls against the base. `module_excess_loc` goes 21646 -> 21638 and `unloaded_package_imports` 5 -> 4, so nothing rises.
  - `tests/closures.json`: merged as sets by the ledger driver.
- Production code is unchanged in the delta. `flow_anchor.py` and `pump_arbiter.py` carry the same branch diff as at the reviewed head, so no wider review is owed (step 12).
- Gates, run at the head in a detached worktree (`ev/gates.txt`, `ev/claims.txt`, `ev/selftest_merge.txt`):
  - `check_scopes.py --repo .`: rc 0.
  - `check_scopes.py --repo . --self-test`: SELF-TEST passed, rc 0.
  - `deployment_shape.py`: ALL DEPLOYMENT SHAPE CHECKS PASSED.
  - `doc_claims.py`: ALL 445 checks PASSED.
  - `structure.py`: STRUCTURE RATCHET PASSED, with nothing re-recorded.
  - `claims.py`: `claims_false=0`, `arch_modules_on_disk=107` = `arch_map_listed=107`, with no missing or phantom module. The tree is clean after the run.
- Merge: `git merge-tree --write-tree origin/main HEAD` exits 0 (origin/main ef797d79).
- CI:
  - The newest `gate` run (140368002719) is a success. Two earlier `gate` runs at this head failed and were superseded by it.
  - `tests / nightly-status` is red but not required.
  - `merge_train.py classify` prints `WAIT cbd6e64d... pending: gate red: none` (`ev/classify.txt`), so the verdict is returned as `pending-ci` for the relay.
- Not re-run: the finder's harness `dev/audit/harnesses/r11_owner_step_kick.py`, because the delta leaves production unchanged.
