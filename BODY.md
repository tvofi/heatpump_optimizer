This changes policy (decision 0017 and the allowlist it governs) and tooling. It adds the first entry to `dev/governance/config/outside_contributors.json` (Bankaifan, id 476059, type User, since 2026-11-22, decision 0017) and replaces 0017's "Before the first allowlist entry" section with the owner's ruling of 2026-11-22: the first entry no longer waits on live checks; the first adopted verdict is the live check of the adopt, confirm and approve path; and, quoted for what it decides, *"DO NOT MERGE ANYTHING ON ANOTHER USERS FORK"* (tvofi, 2026-11-22): no identity of ours merges into, pushes to or update-branches a contributor's fork, and the contributor brings their own branch up to date with main.

The code follows the ruling, so nothing in the tree can write to a fork. `tools/audit/seat/remerge_main.sh --head-repo` now refuses (`REMERGE FAILED <pr> at fork ...`, exit 1) before it fetches, mints a token, merges or pushes; its update-branch, token and read-back block is deleted. `Train.recarry` in `tools/audit/seat/merge_train.py` parks a fork head that does not contain main `[OUTSIDE]`, saying the contributor brings the branch up to date, before any pull-ref fetch, worktree or call to `remerge_main.sh`. `merge_pr.sh` and `queue_pre_flight.py` have no fork write arm and are unchanged. Owner-directed, so the tooling freeze does not hold it. Items 6 and 7 of 0017, `docs/CONTRIBUTING.md` and the instrument pages for `remerge_main.sh` and `merge_train.py` say the same. No tracked file is added.

## Head

ac2204c8cc47e682dd19aaf155a3f84c7bc5f22e

## Mutation proof

`python3 -I tools/audit/seat/remerge_main_selftest.py --mutant=remergeforkrefuse` (the refusal line deleted): 4 of 6 checks go red, the stale-head and conflicting-head refusals and their no-fetch/no-mint/no-curl/no-push checks. The train's self-test carries the matching checks (a fork head parks `[OUTSIDE]` with no pull-ref fetch, worktree, `remerge_main.sh` or push).

## Null control

The same self-tests on our own heads: remerge_main's attached-branch case still pushes and exits 0, and the train still recarries a head of ours from `origin/<branch>` on `-B` and treats a conflict on it as the fixer's. On origin/main the allowlist is empty and `outside.py check` returns rc 3 for this author.

## Figures

none

## Red checks

none

## Forward-carry

none

## Friction

none
