Fix review: merge afbaaf73b3baf81809980926b737308761fd9a2d

bus-nonce: 700cbd8e34bdd6cc2bc757957810b598

Round 2. Measured head afbaaf73b3baf81809980926b737308761fd9a2d, which is also the live head at posting (pulls API). Merge base and origin/main are 0c25836e5a847d39f7a023e9f567ac2525741ebe. The authored code head is dda217b3.

## Round-1 blockers: all closed
- Harness root: the harness now carries the canonical `repo_root` walk inline. `harness_headers.depth_root_seams()` at the head returns `[]`; in round 1 it returned one seam. On this head, `fast (3.14)` (check-run 113197338336) is **success**.
- Red answered: the body's `## Red checks` names check-run 113185847660, says the diff caused it, names the cheaper detector (`python3 tests/harness_headers.py`, about 105 s) and says why the seat missed it (`scope.run` omits `run_always` scripts).
- RCA section 4: the `gc.auto=0` correction matches `run-command.c` `prepare_auto_maintenance` at v2.55.0.
- Trigger rate versus failure rate: RCA sections 3 and 6 now say 2/256 is the trigger rate and that the failure rate is not derived.
- Credit: the `realgit` and `realgit-forced` arms are credited to this reviewer's method and build, and the 0/300 natural result is quoted correctly as mine. The base 9/20 row is the seat's own run with my build; it is consistent with my 6/20 and 11/20.

## Main merges: nothing resolved by hand
`git merge-tree --write-tree <p1> <p2>` reproduces the actual tree of all three merge commits: afbaaf73 = ec2b0ff5, bef0efcc = 1d9fd307, 46baba99 = e289fe89. The head merges onto origin/main with rc=0. The three-dot diff touches only the PR's 4 files.

## Measurements at this head (real git 2.55.0 built from git/git v2.55.0, through the PR's own adopted harness)
    RESULT base 0c25836e arm=realgit-forced runs=20 directory_not_empty=11 nonzero_exit=11
    RESULT head afbaaf73 arm=realgit-forced runs=20 directory_not_empty=0 nonzero_exit=0
    RESULT head afbaaf73 arm=realgit        runs=20 directory_not_empty=0 nonzero_exit=0
    RESULT head afbaaf73 arm=shim runs=5 0/0; arm=plain runs=3 0/0; arm=realgit with no GIT_BIN -> exit 2 (refuses)
    RESULT mutant (the three GIT_CONFIG_* keys deleted): self-test FAIL on the readback check; realgit-forced directory_not_empty=13 nonzero_exit=20; restored tree is clean and the self-test passes

## Checks at this head (check-runs API)
24 success, 14 skipped, 1 failure, 1 cancelled.
- `delivery-status` failure: the job printed `DELIVERY STATUS UNCHECKED — 72 rowed, 0 pending, 0 overdue`. It is not a required context and none of its inputs is in this diff, so it is not this PR's.
- `budget-raise-gate` was cancelled, not failed, and the diff touches no budget file. Rerun the cancelled twin before merging.

## Not blocking: one sentence the RCA still owes
Section 4 now says `maintenance.auto=false` has "no such dependency" on inherited configuration. That is false. In git 2.55, `git_config_from_parameters` reads `GIT_CONFIG_COUNT` first and `GIT_CONFIG_PARAMETERS` after it. So an inherited `GIT_CONFIG_PARAMETERS` `maintenance.auto=true` overrides the fix: `git config --get maintenance.auto` printed `true` (evidence/r2-params-override.txt). The code is still sound, because the self-test's readback check fails loudly in exactly that case. The sentence should say that the readback check catches the override, not that the override cannot happen.

## Owner decision (unchanged from round 1)
A workflow-level env is a CI-only barrier for the other 34 sites. A shared throwaway-repo helper is the full closure, as the RCA now says.
