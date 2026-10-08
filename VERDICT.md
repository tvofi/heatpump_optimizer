Fix review: merge 4ff6152ea166d6e11db880ae9fa70727efcaa547

bus-nonce: 464a0a8b2ed57a6cef1725acc7662ce7
This is round 3, a delta review. I measured 4ff6152ea166d6e11db880ae9fa70727efcaa547 against the reviewed merge head 47d48472 and the merge base af79f2114 (that is also origin/main). Before posting I re-read the live head with git ls-remote, and it has not moved. Evidence: /Users/timmalmstrom/hpo-seats/review-2057/ev3

## What moved
- **03f7be4d** (main af79f2114 merged into 47d48472): its tree c6574a42 is identical to `git merge-tree --write-tree 47d48472 af79f2114`, run with the ledgermerge and claimnotes drivers configured. That run gave rc=0 and printed `LEDGER-MERGE: resolved tests/closures.json` (mergetree_stderr.txt). Nothing was resolved by hand.
- **88e04a5c** (the code head) changes one file: `tools/merge/ledger_merge.py`, +4/-4, all inside the `--resolve` self-test (delta_fix.diff). 4ff6152e has the same tree as 88e04a5c (4eb1b976).
- **Interdiff by file** (interdiff_byfile.txt): I compared the branch's own three-dot patch at the old head with the one at the new head. For the harness, the delivery row, closure.py and entities.py the patches are hash-identical. ledger_merge.py differs only by the delta above. closures.json differs only through main's re-record, which the driver merged as a set.
- **Untouched files:** VERSION, the manifest version and the notes heading are not in the diff. No budget or claim file is in it either.
- `git merge-tree origin/main HEAD` gives rc=0.

## The helper conversion
The new code is `sys.path.insert(0, os.path.join(ROOT, "tests"))`, then `from throwaway_git import throwaway_git_init`, then `env = throwaway_git_init(r, "-q", "-b", "main")`. This is the same shape #2054 used in this same `self_test` at line 611, and in `merge_train.py`'s self-test at line 612. The helper's environment carries the t/t@t identity that the deleted dict used to set. It also writes `maintenance.auto=false` and `gc.auto=0` into the repository's own config. Because of that, `resolve(..., repo=r)`, which runs git without this environment, also sees maintenance turned off.

## The check
`throwaway_git.py --check`:
- at 03f7be4d: rc=1, `REFUSE tools/merge/ledger_merge.py:569: g("init", "-q", "-b", "main")` (tg_check_03f7.txt)
- at the head: rc=0, `0 raw git init or clone site(s) refused` (tg_check_head.txt)
- **Mutant** (tg_check_mutant.txt): I restored the raw `g("init", "-q", "-b", "main")` and an `os.environ` env in a throwaway detached commit that was never pushed. The check went to rc=1 with `REFUSE tools/merge/ledger_merge.py:570`. After I reverted to the head it returned to rc=0.

## ledger_merge's behaviour
- `ledger_merge.py --self-test` at the head gives rc=0, `all passed`, 50 ok and 0 FAIL (ledger_selftest_head.txt). The 47d48472 tree also prints 50 ok.
- The test "closures: --resolve finishes a merge an older driver left conflicted" is still ok. Its assertion requires `merged != 0`, so the throwaway repository still conflicts without a driver.
- The production driver and resolve code are byte-unchanged by the branch delta. The only other ledger_merge.py lines that moved are main's #2054 conversion (9 lines, identical in 47d48472..03f7be4d and in 4647321d..af79f2114).
- The round-2 refusal probe, re-run at the head (refusal_probe_head.txt), gives the same five results: the canonical text rc=0 and every variant rc=1.
- I did not re-run replay.py (the 16/420 figure) or the transition replay. Neither the writer nor the driver code changed in this delta, so the round-2 figures carry over unchanged rather than being re-measured.

## CI at 4ff6152ea166d6e11db880ae9fa70727efcaa547
Source: check-runs with filter=all, read after the required runs settled (checkruns_4ff6152e.tsv). 38 runs: 22 success, 14 skipped, 1 failure, and `coverage` in progress (not required).
- Green: `instrument-self-tests` 113459942654, `pr-contract` (both runs), `closures` 113460095120, `closure-scope`, `mutation`, `fast (3.14)` 113459944184.
- The one red is `nightly-status` 113459943890. It grades main, the diff does not reach what it reads, and the body names and answers it. The body cites job 113428743210 from 03f7be4d; the cause is the same.

## The body re-take
- `## Red checks` names `instrument-self-tests` (job 113428743954, which I confirmed red at 03f7be4d in cr_03f7.json) with its cause, the #2054 check meeting the round-1 raw init through the merge-train merge. It gives a cheaper detector and its cost.
- It names `pr-contract` with its cause, the body not naming that red.
- It names `delivery-status` and `nightly-status`.
- The `## Head` lines are correct for 4ff6152e, 88e04a5c, 03f7be4d and 47d48472.

## Notes (not blocking)
- The body's first line still says "Round 2". The rest of the body says round 3.
- The body gives the delivery row as `docs/delivery/2057.md`. The file is `dev/programme/delivery/2057.md`.
- The pr-contract job the body cites (113429992729) is not among 03f7be4d's latest-filter runs. That listing shows 113455425919 red. Both point to the same cause.
- The `## Head` line says 4ff6152e "merges ... origin/main af79f2114". In fact main came in at 03f7be4d, and 4ff6152e is a merge whose second parent, 88e04a5c, sits directly on the first. The next paragraph states this correctly.
