This changes policy (decision 0017 and the allowlist it governs) and tooling. It adds the first entry to `dev/governance/config/outside_contributors.json` (Bankaifan, id 476059, type User, since 2026-11-22, decision 0017) and replaces 0017's "Before the first allowlist entry" section with the owner's ruling of 2026-11-22: the first entry no longer waits on live checks; the first adopted verdict is the live check of the adopt, confirm and approve path; and, quoted for what it decides, *"DO NOT MERGE ANYTHING ON ANOTHER USERS FORK"* (tvofi, 2026-11-22): no identity of ours merges into, pushes to or update-branches a contributor's fork, and the contributor brings their own branch up to date with main.

The code follows the ruling, so nothing in the tree can write to a fork. `tools/audit/seat/remerge_main.sh --head-repo` now refuses (`REMERGE FAILED <pr> at fork ...`, exit 1) before it fetches, mints a token, merges or pushes; its update-branch, token and read-back block is deleted. `Train.recarry` in `tools/audit/seat/merge_train.py` parks a fork head that does not contain main `[OUTSIDE]`, saying the contributor brings the branch up to date, before any pull-ref fetch, worktree or call to `remerge_main.sh`. `merge_pr.sh` and `queue_pre_flight.py` have no fork write arm and are unchanged. Owner-directed, so the tooling freeze does not hold it. Items 6 and 7 of 0017, `docs/CONTRIBUTING.md` and the instrument pages for `remerge_main.sh` and `merge_train.py` say the same. No tracked file is added.

With its fork arm gone `remerge_main.sh` reads no key and no longer sources `tools/pr/app_mint.sh`, so `dev/audit/harnesses/owner_only_channel.py` drops it from `CREDENTIALED` and `WRITER_ARMS` and deletes `w_remerge`: P5b's sibling command no longer returns it, and its remaining push goes through `tools/pr/app_push.sh`, whose own fail-closed arm and null stay. `remerge_main_selftest.py` stays a named no-writer: its `mint_token` stub is the canary that records no mint is made.

## Head

e6f329f0ac7e96f9387745f279fab6ce926e4058

The authored code head over ac2204c8cc is the main merge 8373f8b7b0, the delivery row 107e630c70, and this harness fix. Measured against origin/main 1207ee13b0e439a4acefccabace691785af2ebad, 2026-11-22T19:46Z.

## Mutation proof

`python3 -I tools/audit/seat/remerge_main_selftest.py --mutant=remergeforkrefuse` (the refusal line deleted): 4 of 6 checks go red, the stale-head and conflicting-head refusals and their no-fetch/no-mint/no-curl/no-push checks. The train's self-test carries the matching checks (a fork head parks `[OUTSIDE]` with no pull-ref fetch, worktree, `remerge_main.sh` or push).

`dev/audit/harnesses/owner_only_channel.py --only P5b`, failing first: at 107e630c70 it prints `FAIL P5b ... no longer returned: ['tools/audit/seat/remerge_main.sh']`; at this head it holds. Mutant: `tools/audit/seat/remerge_main.sh` put back in `CREDENTIALED` prints the same `no longer returned` FAIL and `FAIL P5b: tools/audit/seat/remerge_main.sh: the arm ran to its end -- KeyError`. Reverse control: a `# mint_token` line appended to `remerge_main.sh` at this head prints `FAIL P5b ... owes an arm: ['tools/audit/seat/remerge_main.sh']`, so the comparison still sees a key reader the list lacks. Both restored.

## Null control

The whole `owner_only_channel.py` at this head prints `OWNER-ONLY CHANNEL HELD`; at merge base 8cc3fb3e35 its P5b line is `ok` with `remerge_main.sh` still a minting arm, so the list changed only with the surface. The same self-tests on our own heads: remerge_main's attached-branch case still pushes and exits 0, and the train still recarries a head of ours from `origin/<branch>` on `-B` and treats a conflict on it as the fixer's. On origin/main the allowlist is empty and `outside.py check` returns rc 3 for this author.

## Figures

- standing cost of the cheaper detector: `python3 -I dev/audit/harnesses/owner_only_channel.py --only P5b`, wall clock on this seat 1.4 s (date-stamped shell timer around the call).

## Red checks

- `governance / instrument-self-tests` (job 137314380969, at 107e630c70): `owner_only_channel.py` P5b still listed `remerge_main.sh` as a key-reading arm after the diff removed its key read. Fixed at this head (Mutation proof). Cheaper detector: `python3 -I dev/audit/harnesses/owner_only_channel.py --only P5b`, standing cost in `## Figures`, local, no key; it existed and was in no local path, because the scoped gate's closures do not select this harness for a change to `remerge_main.sh`. Countermeasure owed by the root-cause seat, not built in this fix (`defect-root-cause.md`, separate seat).
- `gate` (job 137315599519, run 45056081883, at 107e630c70): `FAIL run(s) [45056082768] at this head are still being judged`; superseded by run 45056082768's own gate, which concluded success. Not a defect of the head.
- `gate` (job 137324784530, run 45058628353, at 107e630c70): an edit-triggered run's gate, the same `FAIL run(s) [45056082768] at this head are still being judged; their gate decides`, superseded by that run's gate as above. Not a defect of the head.

## Forward-carry

none

## Friction

none
