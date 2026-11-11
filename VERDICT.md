Fix review: blocked 808a8eebe68cf683f5de429f4fcf3977bcb68e19 mutation-vacuous: tests/harness.py sys.path anchor (both inserts reverted to cwd-relative) survives harness_headers.py, 113 of 113 pass

bus-nonce: c63deeb5e36d8a0093b65716fcd82b71
pending-ci: gate

Round: first review of PR 3431 (R10-SUITE-ENV-RESIDUE), head 808a8eebe68cf683f5de429f4fcf3977bcb68e19, merge base 40fe1cae2ed3efbcf4760b524e17a99ff2a7ec7f.

## Block

- The PR exists to repair item 6d58568e: a harness that imports `tests/harness.py` from a root other than the cwd measures the cwd's package. That repair is the two `sys.path` inserts anchored to `_ROOT`. Its one new check pins only the third changed line, the translations listing.
- Mutant M1 (`ev/mutant-M1-syspath-relative.diff`) puts back `sys.path.insert(0, "tests")` and `sys.path.insert(0, "custom_components")` and leaves the translations anchor in place. `PYTHONPATH=tests/hastub python3 tests/harness_headers.py` still prints ALL 113 HARNESS HEADER CHECKS PASSED (`ev/harness_headers-m1.txt`).
- M1 brings the defect back. I ran the `learner_inputs_swap.py` pattern from cwd = the base worktree, with T = the M1 tree (`sys.path[:0] = [T/tests/hastub, T/custom_components, T/tests]`, then `import harness, heatpump_optimizer`). The M1 harness resolved the package from the base tree; the head harness resolved it from its own tree (`ev/m1-capture.txt`).
- The body's mutation proof reverted the whole file (M3). That fails only through the translations read, which raises FileNotFoundError, so the proof does not show the `sys.path` lines are pinned.
- Owed, either way:
  - extend the foreign-cwd check so it also asserts that `heatpump_optimizer` resolves under the harness's own tree when the cwd is another tree that has `custom_components/` (for example, `cwd=` a temporary copy or the base checkout);
  - or show a check in the closure that fails under M1.

## Evidence

- RESULT head: `ALL 113 HARNESS HEADER CHECKS PASSED` (`ev/harness_headers-head.txt`). This matches the body's 113.
- RESULT M3 (`tests/harness.py` at the merge base, the body's mutant): `1 of 113 HARNESS HEADER CHECKS FAILED`, failing on "tests/harness.py imports from a cwd outside the tree and finds its catalogues". This matches the body.
- RESULT M1 (only the `sys.path` inserts reverted): `ALL 113 HARNESS HEADER CHECKS PASSED`. The mutant survived.
- Null control: at the base, a direct foreign-cwd import (`cd /`) raises FileNotFoundError on `custom_components/heatpump_optimizer/translations`. At the head it prints 3 catalogues. Both match the body.
- Class enumeration: I re-ran the body's rule at the head (the 29 files the import-and-sys.path grep lists, less the 13 the os.chdir grep lists) and got 24 files (`ev/enum.txt`).
  - I traced root handling in 15 of them with a read-only subagent; that trace is this reviewer's instrument, not the finder's. Only `learner_inputs_swap.py` takes a tree on argv and imports `harness` from it.
  - Before the fix, `harness.py`'s relative inserts landed ahead of that tree, which was the capture; the anchor closes it.
  - The others either take no tree and run from the cwd, or insert absolute root paths themselves (`r10_configflow_pages.py`, `r9_dbg2_selftest_price.py`, `r10_store_*`, and `r10_i1_sweep_guards.py`'s RUNNER).
  - The body's dismissal of per-harness relative inserts holds for the files traced. The class is not open beyond the block above.
- Finder's harness: none committed for 6d58568e. The packet says "Finder's harness: none named". The body's foreign-cwd check is the fixer's instrument.
- Merge with origin/main: `git merge-tree --write-tree origin/main 808a8eebe6` rc=0, no conflict (`ev/merge-tree.txt`).
- `VERSION`, manifest, `RELEASE_NOTES.md` and `tests/golden/` are untouched in the three-dot diff. No claim-file change.
- Roles contract: `git diff <merge-base>...origin/main -- dev/governance/roles/` is empty.
- Commits `aa631f7c5d..808a8eebe6` carry no Co-Authored-By or Claude trailer.
- Owed-reds set at this head is in `ev/owed-reds.txt`. CI state: `merge_train.py classify` polled every ~60 s for 03:02 to 03:36 UTC printed `WAIT 808a8eebe6... pending: gate red: none` every time (`ev/classify.log`). No red was reported, and none is answered here. This block does not rest on CI.
- Forward-carries 1, 2, 4, 5 and 6 are dismissed in the body with reasons; the packet's carry_audit routes all 5. I did not re-derive carry 6's prepr.sh hook output, which is a figure from the fixer's seat.

## Findings

none
