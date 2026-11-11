CLOUD FIXER seat for tvofi/heatpump_optimizer, topic r10-suite-env-residue, at head a7628041dc02e298c5399003d4c0576391dd5c4e. Never send push notifications. Write no Claude Code footer, no Co-Authored-By or Claude-Session trailer and no claude.ai session link in any commit, pull-request body or comment you produce; check your commits with `git log --format=%B` before pushing.
Setup: `git fetch --unshallow --tags origin`. Before any commit, pin the seat identity: `git config user.name hpo-fixer && git config user.email 70032254+tvofi@users.noreply.github.com`. The session-start `toolchain:` line says whether venv-ci's python3 is on PATH: on REFUSE, start each Bash call with `eval "$(bash .claude/hooks/session-start.sh --env-lines)"`. Then run `bash tools/audit/seat/cloud-setup.sh --check`, and on REFUSE stop: report its line as your result and start no work. Run anything heavy in the background with Monitor and no timeout. Never wait in one tool call longer than 240 s; poll again instead. Read your policy once, verbatim: `python3 -I tools/policy/role_pack.py render fixer --out $HOME/role-pack.md`, then that file in place of your role contract and INSTRUMENTS.md; on REFUSE read those files as before.
Role: read dev/governance/roles/fixer.md from main, and follow it exactly, in a worktree of your own cut from origin/main. Fetch a7628041dc02e298c5399003d4c0576391dd5c4e for the base you were given.
Output: push each verified step, fast-forward only, to refs/heads/handoff-wip/r10-suite-env-residue before any wait on a background run, so an idle container loses nothing; never step-push to handoff/r10-suite-env-residue, whose move updates the pull request. Hand off at your first clean `tools/pr/prepr.sh` head (the body check included), fixing what it refuses; a main that has moved since that run needs no re-merge and no second run, because the train re-proves the head on the current main. Merge origin/main and rerun prepr.sh only when `git merge-tree --write-tree origin/main HEAD` reports a conflict. If you must stop on a question, first push `BLOCKED.md` with a `Question:` line to refs/heads/handoff-wip/r10-suite-env-residue, even with no code. Then push the code to refs/heads/handoff/r10-suite-env-residue, then write the PR body and run `bash tools/audit/seat/body_push.sh r10-suite-env-residue <body.md>`, which pushes refs/heads/handoff-body/r10-suite-env-residue; that second push is the return signal. Once it succeeds, delete the step ref: `git push origin :refs/heads/handoff-wip/r10-suite-env-residue`. When body_push.sh exits 4 (its output ends `body_push: REFUSED CARRY-LANDED`), the carry lands on the roster you may not write: push a BLOCKED.md holding that output to refs/heads/handoff-wip/r10-suite-env-residue and stop; the relay folds the carries and re-runs body_push.sh. Push nothing else, open no pull request and write no delivery row. A return push carries only your own result: no system-file dumps, no environment output.
Never write to any branch except your return refs and refs/heads/handoff-wip/r10-suite-env-residue and refs/heads/handoff-wip/r10-suite-env-residue-body. Never work around a hook or a refusal; report it in your result instead.
Discovery reads (search, list, read across files) go through Agent subagents, as the frugal routing guard requires; at most 5 inline search operations per prompt; never set FRUGAL_ALLOW_INLINE.

Brief (snapshotted when this payload was rendered):
REPAIR ROUND 2 for R10-SUITE-ENV-RESIDUE (size M, roster opus), pull request 3431, head d710f5ddf91ae498d6d8a8193fc62c04e4b01f24 (handoff/r10-suite-env-residue 6ce0b46dda03523c269cbc169bc2c80ea54bc5ee, merged into the PR head). Continue from the PR head; do not re-cut. THIS IS THE LAST REPAIR ROUND: the previous repair (a sonnet seat) left the reviewer's same sys.path mutant alive in two verdicts (M1 at 808a8eeb, then M1a at d710f5dd), so by the three-round rule a third block sends this group to a minimal re-cut. Read the surviving mutant below as the thing to kill, and kill it for the whole class, not for the one line.

SCOPE. The group's roster carries (Carry 1 through Carry 7) are this PR's scope; keep each named as `Carry N` in the body. Any carry marked PART 2 ITEM is out of this part.

THE SURVIVOR (M1a): `tests/harness.py` line `sys.path.insert(0, os.path.join(_ROOT, "tests"))` reverted ALONE to `sys.path.insert(0, "tests")` survives `PYTHONPATH=tests/hastub python3 tests/harness_headers.py` (113 of 113 pass). The existing foreign-cwd check passes because the suite runs from the repo root, where a cwd-relative "tests" is the same directory, and because its decoy `tests/` is empty and nothing is imported from `tests/` after `harness`. The defect it brings back: `dev/audit/harnesses/learner_inputs_swap.py` imports `from profiles import house` right after `from harness import ...`; with cwd = another tree, `profiles` resolves to the cwd's tree, not the harness's own.

REQUIRED:
1. A check in the closure of `tests/harness_headers.py` (or a test it runs) that FAILS when that one insert is reverted to the cwd-relative "tests". Either (a) drive the harness from a cwd that is NOT the repo root and has its own `tests/` directory with a sibling module the real `tests/` also has (for example an empty `profiles.py`), import that module after `harness`, and assert its `__file__` lies under `ROOT/tests` and not under the decoy; or (b) assert the inserted path is absolute and equals `os.path.join(_ROOT, "tests")`. Prefer (a), and add (b) if cheap. Make the `custom_components` insert pinned the same way, so neither half can be reverted alone.
2. The reviewer's exact mutant M1a re-created (`git show origin/probe/rev-3431-677c1ae0:ev/mutant-M1a-tests-relative.diff`, apply it to a git-archive copy of your handoff head) and shown KILLED, quoting the driver's output line (the `N of M HARNESS HEADER CHECKS FAILED` line and the failing check name), beside a NULL control (the unmutated head) that passes, quoted too.
3. Every other mutant the two verdicts named re-shown at the new head, each with its output line: M1 (both inserts reverted to cwd-relative), M1b (only the `custom_components` insert reverted: `ev/mutant-M1b-cc-relative.diff` in the same probe ref), M3 (tests/harness.py at the merge base: `ev/mutant-M3-harness-at-base.diff`). All must be KILLED with the null surviving. Say for each whether its status is unchanged from the verdict.
4. Mutate the production line, not the test: the pin must fail because of the revert, not because the check was weakened. Run the null and the mutants from the repo root AND say the check also fails from a different cwd.

Steps 2 to 8 of the fixer contract are re-executed at the new head: merge a fresh origin/main into the PR head (never rebase), re-measure the structure ratchet, finder's harness at both ends (`learner_inputs_swap.py` pattern from a foreign cwd, M1a tree vs head tree, as the verdict's ev/m1a-capture.txt), a null control for every quantified claim. A metric moved UP goes to the orchestrator with the measured number before the handoff. Hand off as before (handoff/r10-suite-env-residue, body updated in full, not a subset).

PIN EVIDENCE (triage P577, binding): for every mutation or pin claim, re-create the REVIEWER's own mutants exactly as the verdicts name them, show each KILLED at your handoff head and the NULL mutant surviving, and quote those lines in the body. mutant_run.py --diff is an optional extra and is NOT pin evidence (it skips tests/, YAML, shell and expression conjuncts).

----- BLOCKED VERDICT at d710f5dd (verbatim, probe/rev-3431-677c1ae0) -----
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
