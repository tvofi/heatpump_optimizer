Fix review: blocked 8be64a110fa4e741889920c4eff2b6b4cb99cf3a carry-missing: the four #2444 carries at roster ebf81fc1d state no control, and the merge_pr/push-lines carry to R10-CI-LAYOUT is half refuted: deleting open_pr.sh's and update_pr.sh's app_push line reddens their self-tests

bus-nonce: cfee72218fe11aa3fb06b4a66bb9b930

Round: 3. Round 1 was `Fix review: blocked b891dfa04 mutation-survivor`. Round 2 was `Fix review: blocked 8be64a110 carry-missing`. This head is the one round 2 measured, unchanged. From round 4, `fixer.md` owes a re-cut, not a repair. The finding here is in the roster and the body, not in code.
Measured head: 8be64a110fa4e741889920c4eff2b6b4cb99cf3a (ev/HEAD). I read it again from the API just before writing this, and it had not moved.
Contract: `git diff $(merge-base)...origin/main -- dev/governance/roles/` is empty, so the contract is current. origin/main is at 64b0ae690, three record commits past the merge base e59f0291a.
Environment: PYTHONUNBUFFERED=1, which is how this container is set up.

## Blocking (step 10)

All four carries exist at `handoff/audit-r10-roster` ebf81fc1d, which is the SHA the body cites and the branch's current tip (ev/roster_tip). Three are in R10-CI-LAYOUT's `carry` and one is in R10-BRIEFS-FOLD's. Both groups are at `resume.stage: not-started`. `git diff origin/main...ebf81fc1d -- dev/programme/rosters/` is non-empty, so the branch is live (ev/carries_2444.txt). So round 2's absence finding is fixed.

Step 10 also requires each carry to "state its control as a precondition". Under `finding-propagation.md`, that means carrying the control and not only the claim, and giving the figures a re-measurement instruction. Round 2's fix line asked for exactly this. None of the four does it. Each one is the body line copied word for word:

- **The merge_pr/push-lines carry (R10-CI-LAYOUT)** is wrong in part. It says the push lines of `handoff_push.sh`, `open_pr.sh` and `update_pr.sh`, and `merge_pr.sh`'s path after its gates, "are not exercised by those files' own self-tests". I measured this on a worktree at the head and restored it afterwards; `git status` was clean:
  - `open_pr.sh` line 44 (`bash "$_push" ...`, the first push) replaced by `true`: `--self-test` rc=1, `pr_args self-test: 46 checks, 4 failed`. The arms that fail include `open_pr: --over-cap opens at the cap` and the null control (ev/openpr_mut44.txt). The unmutated file gives rc=0 (ev/openpr_base.txt).
  - `update_pr.sh` line 58 (its push) replaced by `true`: rc=1, `46 checks, 2 failed` (ev/updatepr_mut.txt).
  - `handoff_push.sh` lines 75, 94 and 108 (its push lines), each replaced by `true`: rc=0 every time. The claim holds here (ev/handoff_mut_*.txt).
  - `merge_pr.sh` line 169 (`gh pr merge ...`) replaced by `exit 0`: rc=0, `12 checks, 0 failed`. The claim holds here (ev/mergepr_mut169.txt).

  So as carried, the line tells R10-CI-LAYOUT to build offline seams for two files whose push lines `pr_args.sh`'s copies already pin. That is the "read as established fact" failure CLAUDE.md warns about. The body shows no measurement behind the line, which `finding-propagation.md` ("an unverified observation is not carried") forbids.
- **The seven-unwired carry** names neither the seven files nor the rule that found them. It points at "(Figures, class seams)" of a PR body. R10-CI-LAYOUT's earlier carry ("Enumerate every `--self-test` under tools/ ... plant a failing case ... Null control") covers this in substance. To be sufficient, the #2444 line would have to cite that rule and the seven names. Alternatively it could say it adds nothing to that carry.
- **The census-cost carry** routes a cost question. It is a routing note rather than a measured finding, so the missing control is the least serious here. Still, it gives no figure and no re-measurement instruction.
- **The Friction carry (R10-BRIEFS-FOLD)** carries no control. For example: `git check-ignore -v tools/audit/seat/<new>` prints `.git/info/exclude:<n>:seat/`, and the null control is a clone without that line.

What a fix needs, with no code change: amend the three R10-CI-LAYOUT lines and the R10-BRIEFS-FOLD line in the roster with `roster_edit.py`. The push-lines line should be narrowed to `handoff_push.sh` and `merge_pr.sh`, with the mutants above as its control and the unmutated self-tests as its null control. Then correct the body's Forward-carry line to match and cite the new roster SHA.

## Not blocking, but no merge could be returned on it now (step 11)

These are from the check-runs API at 14:44Z with filter=all (ev/check-runs.tsv, 49 runs).
- The re-runs failed again on the same installation rate limit, before any check body ran:
  - `arch-score` 118124086255 (14:42Z): `gh: API rate limit exceeded for installation (HTTP 403)`.
  - `pr-contract` 118124086016 and 118124448660 (14:42Z and 14:43Z): the same 403 at the body read.
  - `validate-hacs` 118114888472: `GitHubRatelimitException`.
  - Logs: ev/log_*.txt.
- No `pr-contract` run has read the body at this head. `closures` 118120973522 and `Analyze (python)` were still `in_progress`.
- `nightly-status` is main's red, and the body answers it.
- Because the workflows have not all concluded and no `pr-contract` run has checked the body, I do not block on root-cause-unanswered. These reds are infrastructure, not this diff. Even without the carry finding, this head is not mergeable until those re-runs go green.

## Verified at this head

- Step 13: `git merge-tree --write-tree origin/main 8be64a110` exits 0 against origin/main 64b0ae690, printing tree ca4fcaab3, with no MERGE-CLAIM line (ev/merge_tree.txt). Main's three new commits touch only `dev/programme/delivery/`.
- Step 1, re-checking round 1's finding: `selftest_wiring.py --self-test` prints `15 checks, 0 failed`, and `--check` prints `37 self-testing, 37 wired, 0 unwired`. With S30 applied (`return 1 if unwired else 0` changed to `return 0`), the self-test prints `15 checks, 1 failed`, which the step's tally grep refuses. KILLED.
- Step 7: the body's `## Head` names 8be64a110, the head I measured. The body cites roster ebf81fc1d, and that commit exists and is the roster branch's tip.

## Not re-derived in this round

The rest of round 2's figures were taken at this same, unchanged head, and I did not re-take them:
- the harness's 34 KILLED and `RESULT survivors=0`
- the field-coverage `misread=0`/`8`
- the offline spy's `37 files, 0 refused`
- gate scope and the ratchets

The body's job-time figure, its seven-unwired census outside `tools/audit/seat/`, and the macOS sandbox path were not re-run.
