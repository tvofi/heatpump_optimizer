Hotfix for two opener refusals that were not the body's fault (root cause R10-RCA-OPENER-REFUSALS, 2026-11-13). Group R10-HOTFIX-OPENER-REFUSALS; closes no issue.

1. `open_pr.sh`: two openers on one topic share the topic-keyed state dir and its `body.md`, but the lock is keyed on the branch, and the second run renamed itself `fix/<topic>-pr` whenever the first's `worktree add` had made a local `fix/<topic>`. It took another lock, rewrote `body.md` from handoff-body with no head note, and the first run's prepr then refused the body. Fix: a run that finds the topic's opener worktree registered (`git worktree list --porcelain`) adopts the branch that worktree holds, so it takes the first run's lock and exits BUSY (75) before writing. A detached leftover worktree holds no branch and keeps the old rename (the closed-open re-run case, whose existing check failed against a first version that skipped the rename on any registered worktree). Alternative rejected: keying the lock on the topic changes `update_pr.sh`'s shared lock names. Known gap: a first opener whose worktree is already detached at the end of its run, and renamed `-pr`, is not matched by a second.
2. `ci_predict.py`: `ci_tree_run`'s clone lacked the fetch `pr-contract`'s step 'Every finding the body records names its destination' does, so `origin/handoff/audit-r10-roster` in the clone was root's stale local branch and a carry to a newly appended group was predicted BAD-DEST. `fetch_round_rosters` gives the clone root's `refs/remotes/origin/handoff/audit-r*-roster`. `carry_audit.py` and the workflow are unchanged.

## Head

`68e1704e2bdebe2003511684ee0a4c0d59197dc9` is the head everything below was measured at.

## Mutation proof

Each mutant deletes its marked line (`pr_args.sh` self-test mutant mechanism); the check names are the self-test's.
- `mut:opreg` (open_pr.sh): `mutant mut:opreg (its line deleted): the second opener takes the -pr lock, is not BUSY, and rewrites body.md (the defect)` passes, i.e. without the line rc is not 75 and `body.md` changes; the live case `a second opener on a topic whose opener worktree is registered is BUSY (75), body.md byte-identical, the first opens` passes with it.
- `mut:headnote` (open_pr.sh): `mutant mut:headnote (its line deleted): the head note is missing, so the code push is refused for a ## Head that does not name HEAD` passes; the main-moved fixture's stub pusher now refuses a body whose `## Head` section does not name HEAD.
- `mut:roundrefs` (ci_predict.py): the self-test asserts `ci_tree_run` carries exactly one `fetch_round_rosters` line bearing the marker; with the helper made a no-op the self-test printed `FAIL fetch_round_rosters takes root's remote-tracking ref` and `ci_predict self-test: 1 failed`.

## Null control

- Part 1 fail-before: the `mut:opreg` mutant is the unfixed tree (second run rc != 75, body.md differs); pass-after: rc 75, `cksum` of body.md equal before and after the second run. Null control: `null control: a lone opener beside a stale local fix/r and no registered worktree still takes fix/r-pr` passes.
- Part 2 fail-before: the self-test reads the clone's `origin/handoff/audit-r10-roster` as the stale local commit before the fetch, and as root's newer remote-tracking commit after `fetch_round_rosters`. Null control: with the remote-tracking ref absent in the source, the clone's ref stays at the stale one and the helper does not raise. The self-test checks refs; it does not run `carry_audit`, so a group's BAD-DEST prediction is inferred from `carry_audit` reading exactly that ref (`roster_lib.round_ref`).

## Figures

- `bash tools/audit/seat/open_pr.sh --self-test` ends `pr_args self-test: 247 checks, 0 failed`, rc 0.
- `python3 tools/pr/ci_predict.py --self-test` ends `ci_predict self-test: 0 failed`.

## Red checks

none

## Forward-carry

none

## Friction

none
