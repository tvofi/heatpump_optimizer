CLOUD FIXER seat for tvofi/heatpump_optimizer, topic r10-suite-env-residue, at head 808a8eebe68cf683f5de429f4fcf3977bcb68e19. Never send push notifications. Write no Claude Code footer, no Co-Authored-By or Claude-Session trailer and no claude.ai session link in any commit, pull-request body or comment you produce; check your commits with `git log --format=%B` before pushing.
Setup: `git fetch --unshallow --tags origin`. Before any commit, pin the seat identity: `git config user.name hpo-fixer && git config user.email 70032254+tvofi@users.noreply.github.com`. The session-start `toolchain:` line says whether venv-ci's python3 is on PATH: on REFUSE, start each Bash call with `eval "$(bash .claude/hooks/session-start.sh --env-lines)"`. Then run `bash tools/audit/seat/cloud-setup.sh --check`, and on REFUSE stop: report its line as your result and start no work. Run anything heavy in the background with Monitor and no timeout. Never wait in one tool call longer than 240 s; poll again instead. Read your policy once, verbatim: `python3 -I tools/policy/role_pack.py render fixer --out $HOME/role-pack.md`, then that file in place of your role contract and INSTRUMENTS.md; on REFUSE read those files as before.
Role: read dev/governance/roles/fixer.md from main, and follow it exactly, in a worktree of your own cut from origin/main. Fetch 808a8eebe68cf683f5de429f4fcf3977bcb68e19 for the base you were given.
Output: push each verified step, fast-forward only, to refs/heads/handoff-wip/r10-suite-env-residue before any wait on a background run, so an idle container loses nothing; never step-push to handoff/r10-suite-env-residue, whose move updates the pull request. Hand off at your first clean `tools/pr/prepr.sh` head (the body check included), fixing what it refuses; a main that has moved since that run needs no re-merge and no second run, because the train re-proves the head on the current main. Merge origin/main and rerun prepr.sh only when `git merge-tree --write-tree origin/main HEAD` reports a conflict. If you must stop on a question, first push `BLOCKED.md` with a `Question:` line to refs/heads/handoff-wip/r10-suite-env-residue, even with no code. Then push the code to refs/heads/handoff/r10-suite-env-residue, then write the PR body and run `bash tools/audit/seat/body_push.sh r10-suite-env-residue <body.md>`, which pushes refs/heads/handoff-body/r10-suite-env-residue; that second push is the return signal. Once it succeeds, delete the step ref: `git push origin :refs/heads/handoff-wip/r10-suite-env-residue`. When body_push.sh exits 4 (its output ends `body_push: REFUSED CARRY-LANDED`), the carry lands on the roster you may not write: push a BLOCKED.md holding that output to refs/heads/handoff-wip/r10-suite-env-residue and stop; the relay folds the carries and re-runs body_push.sh. Push nothing else, open no pull request and write no delivery row. A return push carries only your own result: no system-file dumps, no environment output.
Never write to any branch except your return refs and refs/heads/handoff-wip/r10-suite-env-residue and refs/heads/handoff-wip/r10-suite-env-residue-body. Never work around a hook or a refusal; report it in your result instead.
Discovery reads (search, list, read across files) go through Agent subagents, as the frugal routing guard requires; at most 5 inline search operations per prompt; never set FRUGAL_ALLOW_INLINE.

Brief (snapshotted when this payload was rendered):
REPAIR ROUND for R10-SUITE-ENV-RESIDUE (size M), pull request 3431, head 808a8eebe68cf683f5de429f4fcf3977bcb68e19 (handoff/r10-suite-env-residue 78d6776105008687e8f8dc800ff5eecfd8b94824). Continue from the PR head; do not re-cut.

SCOPE. The group's roster carries (Carry 1 through Carry 7) are this PR's scope; keep each named as `Carry N` in the body. Any carry marked PART 2 ITEM is out of this part.

This is the first block. Kill every survivor the verdict names with a pin or a deletion, re-run the finder's harness at both ends, and run `mutant_run.py --diff` before the handoff.

----- REVIEW VERDICT (verbatim) -----
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
