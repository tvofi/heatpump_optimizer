Hotfix for two opener refusals that were not the body's fault (root cause R10-RCA-OPENER-REFUSALS, 2026-11-13). Group R10-HOTFIX-OPENER-REFUSALS; closes no issue.

1. `open_pr.sh`: two openers on one topic share the topic-keyed state dir and its `body.md`, but the lock is keyed on the branch, and the second run renamed itself `fix/<topic>-pr` whenever the first's `worktree add` had made a local `fix/<topic>`. It took another lock, rewrote `body.md` from handoff-body with no head note, and the first run's prepr then refused the body. Fix: a run that finds the topic's opener worktree registered (`git worktree list --porcelain`) adopts the branch that worktree holds, so it takes the first run's lock and exits BUSY (75) before writing. A detached leftover worktree holds no branch and keeps the old rename (the closed-open re-run case, whose existing check failed against a first version that skipped the rename on any registered worktree). Alternative rejected: keying the lock on the topic changes `update_pr.sh`'s shared lock names. Known gap: a first opener whose worktree is already detached at the end of its run, and renamed `-pr`, is not matched by a second.

   Round 2: git records and lists a worktree by its physical path, and the `mut:opreg` match compared it with `$WT` as `$HPO_STATE_DIR` spelled it, so a state dir reached through a symlink (or ending in `/`, or holding `/./`) left `OP_REG` empty and the defect live. `pr_state_root` (`pr_args.sh`) creates the state dir's `pr/` and resolves the root once, `cd -P && pwd -P` (no GNU realpath: macOS `/bin/bash` 3.2 and BSD tools run these scripts); `open_pr.sh` and `update_pr.sh` derive every state path from it. Alternative rejected: canonicalising each comparison site separately, which leaves the next site added to repeat the defect; one physical root makes every derived path (`$D`, `$WT`, `$P`, locks, `selftest-main`) one spelling.
2. `ci_predict.py`: `ci_tree_run`'s clone lacked the fetch `pr-contract`'s step 'Every finding the body records names its destination' does, so `origin/handoff/audit-r10-roster` in the clone was root's stale local branch and a carry to a newly appended group was predicted BAD-DEST. `fetch_round_rosters` gives the clone root's `refs/remotes/origin/handoff/audit-r*-roster`. `carry_audit.py` and the workflow are unchanged.

## Head

`4df50c054e4228f6f4e2b204a40d973e7f039fde` is the head everything below was measured at.

## Review scope

Delta from `cde73e8b72fc563d515fd5ab66a6a12eec85698e` (the blocked round-1 head): one commit, `4df50c054e4228f6f4e2b204a40d973e7f039fde`, touching `tools/audit/seat/pr_args.sh` (`pr_state_root`, the `spell` helper and the new self-test arms), `tools/audit/seat/open_pr.sh` (`D` from `$PR_STATE`) and `tools/audit/seat/update_pr.sh` (`P` from `$PR_STATE`). `ci_predict.py` and the behaviour round 1 found correct are unchanged.

## Class enumeration

Rule (run at the head): `git grep -nE 'worktree list|HPO_STATE_DIR|PR_STATE|HPO_WT_ROOT' HEAD -- tools/audit/seat/open_pr.sh tools/audit/seat/update_pr.sh tools/pr/ci_predict.py tools/audit/seat/pr_args.sh`, production lines (pr_args.sh above its self-test). Every site it returns, with its verdict:

- `open_pr.sh` `mut:opreg` (`awk -v w="worktree $WT"` over the porcelain list): canonicalised, `$WT` is built on `$PR_STATE`.
- `open_pr.sh` `op_clear_leftover` (`grep -qxF "worktree $WT"`): canonicalised, same `$WT`.
- `update_pr.sh` own-worktree scan (`grep "^$P/"` and `[ "$o" = "$WT" ]`): canonicalised, `$P` is `$PR_STATE/pr`.
- `update_pr.sh` `mut:elsewhere` (`grep -vqF "$WT "`): canonicalised, same `$WT`.
- `open_pr.sh` and `update_pr.sh` `export PATH=${HPO_STATE_DIR...}/venv-ci/bin`: safe, a filesystem lookup that resolves any spelling; compared with nothing.
- Lock files (`upd-<branch>.lock`, `$WT.lock`, `.push`): safe, `flock(2)` on the file the kernel resolves; both scripts now name the same physical path as well.
- `selftest-main` cache and `pr_step_sig`'s `git worktree add/remove`: safe, built on `$D` (now physical); git resolves the path it is given.
- Per-topic `body.md`, `p2.log`, `close.md`, `fig-*.log`: safe, file reads and writes, compared with nothing.
- `ci_predict.py`: returns no site (no worktree list, no state dir).

Sibling files outside this diff that read `git worktree list` beside a state path (`git grep -lE 'HPO_STATE_DIR|local/state/hpo' HEAD -- tools`, then those reading the list): `closeout.py` and `worktree_gc.sh` resolve both sides (`realpath`, `Path.resolve`, `realpath_of`) before comparing; `handoff_push.sh` and `merge_train.py` build state paths unresolved but compare none of them with the list in production (`merge_train.py`'s `"/state/wt/"` is a literal substring of git's own output). No open seam.

## Mutation proof

Each mutant deletes its marked line (`pr_args.sh` self-test mutant mechanism); the check names are the self-test's.
- `mut:opreg` (open_pr.sh): `mutant mut:opreg (its line deleted): the second opener takes the -pr lock, is not BUSY, and rewrites body.md (the defect)` passes, i.e. without the line rc is not 75 and `body.md` changes; the live case `a second opener on a topic whose opener worktree is registered is BUSY (75), body.md byte-identical, the first opens` passes with it.
- `mut:stateroot` (pr_args.sh, round 2): `mutant mut:stateroot (its line deleted): through a symlinked state dir the second opener is not BUSY and rewrites body.md (the defect)` and `mutant mut:stateroot (its line deleted): through a symlinked state dir the worktree stays on the branch and the run is BUSY (the defect)` both pass.
- `mut:headnote` (open_pr.sh): `mutant mut:headnote (its line deleted): the head note is missing, so the code push is refused for a ## Head that does not name HEAD` passes; the main-moved fixture's stub pusher now refuses a body whose `## Head` section does not name HEAD.
- `mut:roundrefs` (ci_predict.py): the self-test asserts `ci_tree_run` carries exactly one `fetch_round_rosters` line bearing the marker; with the helper made a no-op the self-test printed `FAIL fetch_round_rosters takes root's remote-tracking ref` and `ci_predict self-test: 1 failed`.
- Round 2, by `python3 tools/audit/seat/mutant_run.py --spec <spec> --in-place --cmd 'bash tools/audit/seat/pr_args.sh --self-test'`: `SURVIVED NULL`, `KILLED stateroot` (the resolve line deleted), `KILLED opener-logical` (`open_pr.sh`'s `D` back to `${HPO_STATE_DIR...}`), `KILLED updater-logical` (`update_pr.sh`'s `P` likewise), rc 0. `mutant_run.py --diff 3b9749dac55a85c200005352c661198c982e5799...HEAD --list` draws only `.py` lines: its mutants are all `ci_predict.py`, untouched in round 2, and the delta `cde73e8b...HEAD` draws none; the shell lines are covered by the spec run above.

## Null control

- Part 1 fail-before: the `mut:opreg` mutant is the unfixed tree (second run rc != 75, body.md differs); pass-after: rc 75, `cksum` of body.md equal before and after the second run. Null control: `null control: a lone opener beside a stale local fix/r and no registered worktree still takes fix/r-pr` passes.
- Round 2: the plain-path live case is unchanged and passes; each of `open_pr: the state dir spelled link|slash|dot: a second opener is BUSY (75), body.md byte-identical, the first opens` passes, and `update_pr: through a symlinked state dir, that worktree is detached as before and the run reaches its push` passes; with the resolution deleted (`mut:stateroot`) the symlink arms read the defect. The reviewer's driver (`perturb_symlink.diff`: the resolved state dir passed through `ln -sfn`) no longer applies as a hunk, because `dualrun` gained the spelling argument; `dualrun - link` is that perturbation, run at the head.
- Part 2 fail-before: the self-test reads the clone's `origin/handoff/audit-r10-roster` as the stale local commit before the fetch, and as root's newer remote-tracking commit after `fetch_round_rosters`. Null control: with the remote-tracking ref absent in the source, the clone's ref stays at the stale one and the helper does not raise. The self-test checks refs; it does not run `carry_audit`, so a group's BAD-DEST prediction is inferred from `carry_audit` reading exactly that ref (`roster_lib.round_ref`).

## Figures

- `bash tools/audit/seat/open_pr.sh --self-test` at `4df50c054e4228f6f4e2b204a40d973e7f039fde` ends `pr_args self-test: 253 checks, 0 failed`, rc 0 (round 1's 247 plus the six round-2 arms).
- `python3 tools/pr/ci_predict.py --self-test` ends `ci_predict self-test: 0 failed`.
- `bash -n` on the three shell files, `bare_array.py --check`, `tmp_paths.py --check` (`0 refused`), `selftest_wiring.py --check` (`0 unwired`, `0 index gap(s)`) and `node tools/policy/brief_lint.mjs`: clean at `4df50c054e4228f6f4e2b204a40d973e7f039fde`.

## Red checks

none

## Forward-carry

none

## Friction

none
