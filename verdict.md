Fix review: blocked d710f5ddf91ae498d6d8a8193fc62c04e4b01f24 mutation-vacuous: tests/harness.py sys.path.insert of _ROOT/tests reverted alone to cwd-relative "tests" survives harness_headers.py, 113 of 113 pass

bus-nonce: 677c1ae0f4a8b6644141be7b1103524f

Round: delta re-review, round 2, of PR 3431 (R10-SUITE-ENV-RESIDUE). Head d710f5ddf91ae498d6d8a8193fc62c04e4b01f24, previous reviewed head 808a8eebe68cf683f5de429f4fcf3977bcb68e19, merge base 40fe1cae2ed3efbcf4760b524e17a99ff2a7ec7f. Delta `git diff 808a8eebe6 d710f5ddf9`: only `tests/harness_headers.py` (+20/-10), via merge of 6ce0b46dda.

## Block

- The previous block is resolved. Its named mutants M1 and M3 are killed at this head; see Evidence.
- New survivor M1a (`ev/mutant-M1a-tests-relative.diff`) changes only `sys.path.insert(0, os.path.join(_ROOT, "tests"))` back to `sys.path.insert(0, "tests")`. It keeps the `custom_components` anchor and the translations anchor. Under M1a, `PYTHONPATH=tests/hastub python3 tests/harness_headers.py` prints `ALL 113 HARNESS HEADER CHECKS PASSED` (`ev/harness_headers-m1a.txt`).
- M1a brings the defect back in the finder's own harness. `dev/audit/harnesses/learner_inputs_swap.py` imports `from profiles import house` straight after `from harness import ...`. I ran that file's sys.path pattern with cwd = the base worktree (`ev/m1a-capture.txt`):
  - With T = the head tree, `profiles` resolves to `<head>/tests/profiles.py`.
  - With T = the M1a tree, `profiles` resolves to `<base>/tests/profiles.py`. That is the cwd's tree, which is exactly what item 6d58568e describes.
- Why the decoy check misses it: the decoy `tests/` directory is empty, and the check imports nothing from `tests/` after `harness`.
- Previous rounds did not name this mutant. I found it in this round. It is the second of the two inserts the body names as the production change. M1 reverted both inserts together, so the `custom_components` half alone was enough to kill it.
- Owed, either way:
  - give the decoy `tests/` a sibling module that `tests/` also has (for example an empty `profiles.py`), import it after `harness`, and assert its `__file__` lies under `ROOT/tests`;
  - or show a check in the closure that fails under M1a.

## Evidence

- RESULT head: `ALL 113 HARNESS HEADER CHECKS PASSED` (`ev/harness_headers-head.txt`). This matches the body.
- RESULT M1 (both inserts reverted to cwd-relative, translations anchor kept, `ev/mutant-M1-syspath-relative.diff`): `1 of 113 HARNESS HEADER CHECKS FAILED`, failing on "tests/harness.py from a foreign cwd finds its catalogues and its own tree's package" (`ev/harness_headers-m1.txt`). Killed. This matches the body.
- RESULT M1b (only the `custom_components` insert reverted, `ev/mutant-M1b-cc-relative.diff`): 1 of 113 FAILED on the same check. Killed.
- RESULT M1a (only the `tests` insert reverted): ALL 113 PASSED. **Survived**; see Block.
- RESULT M3 (`tests/harness.py` at the merge base, `ev/mutant-M3-harness-at-base.diff`): 1 of 113 FAILED on the same check (`ev/harness_headers-m3.txt`). Killed. This matches the body.
- Null control (`ev/null-control.txt`): a foreign-cwd (`cd /`) import of `harness`.
  - At the base it raises `FileNotFoundError` on `custom_components/heatpump_optimizer/translations`.
  - At the head it prints 3. This matches the body.
- Finder's harness: none is committed for 6d58568e (the packet says "none named"). The capture runs reuse the sys.path pattern of `learner_inputs_swap.py` lines 24-26. They are this reviewer's instrument, built on the finder's pattern.
- Merge with origin/main: `git merge-tree --write-tree origin/main d710f5ddf9` rc=0, no conflict (`ev/merge-tree.txt`).
- Untouched: `VERSION`, the manifest, `RELEASE_NOTES.md` and `tests/golden/` show no three-dot change (`ev/untouched.txt`).
- Delta commits 6ce0b46dda and d710f5ddf9 carry no Co-Authored-By, Claude-Session or claude.ai text (`ev/delta-commits.txt`).
- Roles contract: `git diff <merge-base>...origin/main -- dev/governance/roles/` is not empty. It changes fix-review.md steps 11 and 12 and fixer.md. I reviewed under main's text, which is what the role pack rendered.
- CI: `merge_train.py classify d710f5ddf9 --pr 3431` printed `WAIT ... pending: gate red: none` (`ev/classify.log`). This block does not rest on CI.
- Delta scope: the delta is tests only and does not widen the review. Body carries 1, 2, 4, 5, 6 and 7 are unchanged from round 1 and were not re-derived.
- Self-audit: `carry_audit.py check` rc=0, `CARRY-AUDIT: 6 finding item(s): 6 routed, 0 unrouted`. I ran it against the body's Forward-carry section, copied into a file in abridged form, with this verdict as the comment. The packet's own run over the full body agrees (6 routed).

## Findings

none
