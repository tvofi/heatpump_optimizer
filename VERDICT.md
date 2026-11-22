Fix review: blocked 107e630c704fe329de1169e48c1e5afd399f99b9 introduced-red: governance / instrument-self-tests fails owner_only_channel.py P5b at this head, which still lists remerge_main.sh as a key-reading arm the diff removed

bus-nonce: 50f7e27c2c846c54ec90de80b4267e57

## Block

- `merge_train.py classify 107e630c704fe329de1169e48c1e5afd399f99b9 --pr 3867` ends `RED ... introduced: 1`, `INTRODUCED Show a planted owner-only canary reaching no public path of the audit pipeline` (ev/classify.log). The failing step is `governance / instrument-self-tests` (job 137314380969): `FAIL P5b: every file the sibling command returns is an arm here or named as no writer, and every arm is still returned -- owes an arm: []; no longer returned: ['tools/audit/seat/remerge_main.sh']` (ev/ci-instrument-self-tests-P5b.txt).
- Cause: this diff deletes remerge_main.sh's fork arm, and with it the script's only `tools/pr/app_mint.sh` source and token mint, so the sibling command that lists key-reading writers no longer returns remerge_main.sh. `dev/audit/harnesses/owner_only_channel.py` still carries it as an arm (`w_remerge`, line 436, and the no-writer table at line 85). The PR does not touch that harness.
- Reproduced on this seat: at the head, `python3 -I dev/audit/harnesses/owner_only_channel.py` prints the same P5b FAIL (ev/owner-only-channel-head.txt); at the merge base 8cc3fb3e35 the same P5b line is `ok` (ev/owner-only-channel-base.txt). It is introduced by this diff, not inherited.
- Owed: update owner_only_channel.py's arm tables to match remerge_main.sh's new surface (it no longer reads a key, so it leaves the arm map; keep or move its no-writer entry as the sibling command now answers), then re-run that harness and the instrument self-tests.

## Red checks

- `governance / instrument-self-tests`: answered above. root-cause-detectable: `python3 -I dev/audit/harnesses/owner_only_channel.py` (about a minute, local, no key) would have shown the red before the handoff. The diff deletes a key read from remerge_main.sh, and that harness lists key readers. prepr's scoped gate did not pick the harness for a change to remerge_main.sh.
- `gate` (job 137315599519): an earlier run's gate job, `FAIL run(s) [45056082768] at this head are still being judged; their gate decides` (ev/gate-job-137315599519.tail.txt). Classify reports `gate red: none`, so this red was superseded by that run's gate and is not a defect of the head.

## Evidence

- Round: first (no earlier verdict on this pull request). Reviewed from a detached worktree at 107e630c704fe329de1169e48c1e5afd399f99b9; role contracts unchanged between the merge base and origin/main.
- Merge with main: `git merge-tree --write-tree origin/main 107e630c704fe329de1169e48c1e5afd399f99b9` exits 0, tree 95853f99e74654d6c4da6e3537716e11c991c88e (ev/merge-tree.txt). Diff: 9 files, +140/-232 (ev/diffstat.txt).
- RESULT remerge_main self-test at head: 6 checks, 0 failed (ev/remerge-selftest-head.txt).
- RESULT mutant `remergeforkrefuse` (the refusal line deleted): 6 checks, 4 failed: the stale-head and conflicting-head refusals and their nothing-fetched/minted/curled/pushed checks, as the body states (ev/remerge-mutant-remergeforkrefuse.txt).
- RESULT merge_train self-test at head: 839 checks, 0 failed (ev/train-selftest-head.txt).
- RESULT reviewer's own mutant in `Train.recarry`: the four-line `if fork: raise Stop(... cls=OUTSIDE)` deleted; 839 checks, 3 failed: the fork-head park check and both "whatever remerge_main.sh would answer, it is never run" checks (ev/train-mutant-forkpark.txt). Restored.
- Null control re-run: in the same runs, our own heads still recarry (remerge_main attached-branch case pushes and exits 0; the train recarries a head of ours from origin/<branch> on -B, a conflict on it stays the fixer's, no [OUTSIDE]).
- RESULT outside.py self-test at head: 266 checks, 0 failed (ev/outside-selftest-head.txt).
- Both-ends check of the entry, with the contributor's open fork pull request #3848 (head repo Bankaifan/heatpump_optimizer): `outside.py check --ref origin/main` prints NOT OUTSIDE (author matches no allowlist entry, rc 3 as the body says); at this head the allowlist admits the author and the contract proceeds to its path classes (it refuses #3848 on two class R paths, a fact of #3848's diff, not of this PR) (ev/outside-check-3848.txt).
- The entry's login, numeric id and type re-derived from the API: every search result authored by Bankaifan in this repository reports user id 476059, type User (ev/user-lookup.txt; `users/<login>` is not reachable from this seat, so the search API was used).
- Class: the body names no enumeration rule; its claim is one seam per tool (remerge_main.sh's fork arm, the train's recarry). Reviewer's own enumeration, every site in tools/ and .github/workflows reading a pull request's head repository, calling update-branch or pushing to a non-origin URL (ev/class-enumeration.txt): no update-branch call remains in the tree; every workflow job that pushes or uses secrets carries the same-repository conjunct; bus.sh, ci_pause.py and cancel_superseded.py only read the head repository. The one generic pusher, tools/pr/app_push.sh, takes any owner/repo and is held below under Findings.
- No mutant name the deleted code carried (`remergeforkarg`, `remergeforkback`) is referenced by any harness or ledger outside the rosters' quoted carry text.
- VERSION, the manifest version and the RELEASE_NOTES.md heading are untouched; no claim file, golden fixture or *_budgets.json moves; no tracked file is added except this pull request's delivery row.
- Head: the body's head section names 107e630c704fe329de1169e48c1e5afd399f99b9 and its one row commit over the authored code head ac2204c8cc; the head did not move during the review.
- Figures: the body quotes one number (4 of 6 checks red under the mutant), re-derived above.
- Policy: this diff changes decision 0017 and the allowlist it governs, so it merges only on the owner's approving code-owner review; this verdict judges the code, tests and harness only.

## Findings

- tools/pr/app_push.sh takes any `<owner/repo>` that matches its shape and does not itself refuse a repository other than ours; what keeps it off a fork today is that no caller passes one (remerge_main.sh's fork arm is deleted here, the train passes our repository) and that its mint asks the App's installation for the named repository, which a contributor's fork does not have. The body's "nothing in the tree can write to a fork" therefore rests on callers and the App's installation scope, not on a refusal inside the pusher. Carry: dismissed: no caller passes a fork repository at this head and the App holds no installation on a fork, so no write path exists; a pusher-side refusal is a hardening the owner's ruling does not require
- The live check of the `bus.sh adopt`, `confirm` and `app_approve.sh` path, and which `commit_id` GitHub reports for a mandated class-O approval, are not run before the entry lands; decision 0017 as amended makes the first adopted verdict that check, recorded in its delivery row. Carry: dismissed: owner-ruled by decision 0017's amended section (the first adopted verdict is the live check), so it is owed on that pull request, not on this one

## Notes

Note: ruling-unrecorded: the two owner quotes of 2026-11-22 this diff relies on ("add him now", "DO NOT MERGE ANYTHING ON ANOTHER USERS FORK") are not in dev/programme/RULINGS.md at origin/main; the owner's approving code-owner review of this policy diff is what carries them. Carry: dismissed: paperwork, settled by the owner's review the policy diff already requires
