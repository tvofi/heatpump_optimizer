# Proposal triage, session s14, batch 160 (P572, P573)

This batch rules `s7/triage-queue-s7.txt` line 255. It also records the result of the P569
sampler, which batch 157 left owed. The bar and the denominators are batch 141's.

Sources:
- origin/main `dbd1ab5b07`. Every line number below is at that commit.
- Job log 130312858296 (pr-contract on PR 3424, run 42953123178), read once with
  `gh api .../actions/jobs/130312858296/logs`, and grepped.
- The open pull requests, read once with `gh api 'repos/.../pulls?state=open&per_page=100'`:
  number, `base.sha` and head for each.
- The P569 sampler's two logs, `s14/seat/triage/s14-5/rate2.log` and `s14-5/ghproc.log`, and the
  beat journal `r10s6/beatd/*.log`.

## P572: PR-CONTRACT-GRADER-SKEW

Verdict: ACCEPT, at a corrected cause that is wider than the proposal's. The fix goes to a new
hotfix group, R10-HOTFIX-RESTORE-BASE-SKEW. The proposed self-test detector is REJECTED.

Source: queue line 255 (2026-11-11T04:26:40Z, orchestrator s14, PR 3424 head f9c7952b).

Instances:
- **What was checked out.** pr-contract checked out the merge ref, not the head.
  - Job log line 8746: `git checkout --progress --force refs/remotes/pull/3424/merge`.
  - Line 8764: `HEAD is now at 427c4ca87 Merge f9c7952b... into c620ebba96...`. c620ebba96 is
    main after #3417 (`git merge-base --is-ancestor 8efacee48d c620ebba96` succeeds).
- **What was restored, and from where.** The restore took the event's stale base commit.
  - Job log line 8816: `PINNED: d08ed31049...`.
  - Line 8819: `check source restored from d08ed31049...: 3 file(s) differ`.
  - `pr-contract.yml` line 104 sets `PINNED` from `github.event.pull_request.base.sha`.
  - Line 118 lists `tools/audit/seat/roster_lib.py` among the files restored at line 135.
  - `carry_audit.py` is not on that list. Lines 449-454 say CODEOWNERS covers it instead.
- **Which file came from which ref.** This answers the proposal's open question. Each count is
  `git show <ref>:<file> | grep -c`:

  | ref | `def carry_receivable` in roster_lib.py | `carry_receivable` in carry_audit.py |
  |---|---|---|
  | d08ed31049 (PINNED) | 0 | 0 |
  | c620ebba96 (the merge's base) | 1 | 3 |
  | 427c4ca874 (the checkout) | 1 | 3 |

  So `roster_lib.py` came from d08ed31049, through the restore. `carry_audit.py` came from the
  merge ref, so from c620ebba96. The call at job log line 9038 then raised the AttributeError at
  line 9040.
- **Cause.** The event's `base.sha` is not the commit the merge ref was built on.
  - The run checks out GitHub's merge commit, whose first parent is current main.
  - It restores from `pull_request.base.sha`, which stays put while main moves.
  - Files the restore takes and files it leaves are then two different mains. Any program the
    restore leaves, importing a module the restore takes, can break when one main commit changes
    both.
  - The "stale-tree arm" the proposal suspected does not pick the files. Its NOTE (line 9024)
    only chooses where the roster is read.
- **Does a head push refresh `base.sha`?** Measured: no.
  - For 15 of the 19 stale open PRs, the stale `base.sha` is an ancestor of their own head
    (`git merge-base --is-ancestor <base> <head>`). The exceptions are 3382, 3420, 3425 and 3429.
  - PR 3427's head was committed at 04:08Z, after #3417 merged at 02:38Z, and its base is still
    stale.
  - So `base.sha` tracks the last main the head took in, not the push. The proposal's workaround,
    merging main into the head, is the one that works.
- **Exposure.** 19 of 23 open PRs have a `base.sha` that lacks 8efacee48d: 3379 3381 3382 3386
  3387 3388 3390 3391 3398 3404 3419 3420 3423 3424 3425 3427 3428 3429 3355. Command: the pulls
  read above, then `git merge-base --is-ancestor 8efacee48d <base.sha>` for each.
  - Not measured: how many of them reach `carry_receivable`. Only that step's code path calls it.
- **The class is wider than this one pair.** The same event base drives every restore site.
  `git grep -c -E 'git checkout "?\$\{?PINNED' origin/main -- .github/workflows` gives:
  - budget-raise-gate.yml 1, ci.yml 5, codeql.yml 1, governance.yml 4, pr-contract.yml 1,
    tests.yml 6.
  - Each one carries the same skew whenever a restored file and a file the restore leaves change
    together on main.

Cost:
- **The fix: restore from the commit the checkout was built on.**
  - For a `pull_request` event, a restore takes its source from the merge commit's first parent
    (`HEAD^1` after the checkout), not from the payload's `base.sha`.
  - It first asserts that the payload's `base.sha` is an ancestor of that parent, and refuses if it
    is not.
  - `HEAD^1` of GitHub's merge commit is a base-branch commit. The pull request cannot choose it,
    so the security property the restore exists for (decision 0013) is kept.
  - `merge_group` (`base_sha`) and the `inputs.base` dispatch fallbacks keep their current
    meaning.
- **Do not change the diff bases.** The restore source and the diff base are two different
  meanings that currently share one value.
  - `BASE_SHA`, `SINCE`, `PR_BASE`, `MACHINERY_BASE`, `PAYLOAD_BASE` and `tests.yml`'s `BASE` key
    the pull request's own diff. For a diff, the merge base is the right base.
  - The fixer splits the two meanings and changes only the restore source.
  - Where one step uses `PINNED` as both, the fixer separates them in that step. It does not
    re-key the diff.
- **Size: M.**
  - One shared resolution of the restore commit: a single step's output, or a script under
    `tools/ci/` that every restore site calls. It is not 18 hand edits, so the next workflow
    inherits it.
  - Plus the 18 call sites.
  - None of the six workflows has a row in `tests/structure_budgets.json` (`git show
    origin/main:tests/structure_budgets.json | grep -c workflows/` gives 0).
  - The workflows are code-owned, so the PR needs tvofi's review or the mandate.
- **Mutation proof the fixer owes.** Replay PR 3424's merge ref 427c4ca874 with the old `PINNED`
  (d08ed31049) and with the new one (`HEAD^1` = c620ebba96). The `carry_audit.py check` step must
  go red under the old one and green under the new one.
  - Null control: a PR whose `base.sha` equals its merge parent (for example one of the four fresh
    PRs) gives the same result under both.

Binding:
- The cost of doing nothing is a red pr-contract on every exposed PR's next body edit. It is
  already red on 3424, which is on the critical path. Each one costs a remerge of main and a
  re-review of carries.
- It recurs whenever one main commit changes a restored module together with a program the
  restore leaves. #3417 was such a commit. Nothing on the list prevents the next.
- The fix makes the restore and the checkout one ref by construction. That removes the class, not
  this pair.
- **REJECTED: the proposal's detector**, a pr-contract self-test with a planted old `roster_lib.py`.
  - It pins one file pair. After the fix the skew cannot arise, so the self-test would guard a
    state that can no longer occur.
  - The fixer's replay above is the proof.
  - Whether a cheaper detector should have caught this belongs to the root-cause seat. This is a
    red check, so the red-check trigger of `defect-root-cause.md` applies. Triage does not
    pre-empt the cost test.

Routing:
- A new group, R10-HOTFIX-RESTORE-BASE-SKEW. Severity high (a red pr-contract on a critical-path
  PR, and 19 of 23 open PRs exposed). Kind instrument, lane IN.
  - Files: `.github/workflows/{pr-contract,ci,tests,governance,codeql,budget-raise-gate}.yml`,
    plus the one shared resolver.
  - Brief: this ruling's Cost section.
- It does not go to R10-BODY-CONTRACT, which also owns `pr-contract.yml`. That group is in
  progress with 45 carries, and P551's five-carry split applies. This fix spans five workflows it
  does not own.
- Until it lands, a red `carry_audit.py check` with `AttributeError` on a stale-base PR is this
  defect, and the workaround is merging main into the head.

## P573: P569 sampler result (batch 157's owed split)

Verdict: DEFER. Batch 157's DEFER of (a), the start-of-pass rate_limit guard in
`tick_loop.sh`/`beat_jobs.py`, stands. Its condition is met only marginally, and even or marginal
is not an ACCEPT.

Source: batch 157 (P569), owed item: the per-caller split from the s14-5 sampler (03:11:16Z to
04:31Z).

Instances:
- **The window.** 03:24:37Z-04:24:37Z (reset 1794371077): `awk '$3==1794371077' rate2.log`.
  - The first reading is 60 used at 03:25:21 and the last is 4001 at 04:23:42, so the spend is
    about 3941.
  - The peak is 80.02%. It crossed 4000 by one call, 55 s before the reset. It did not exhaust.
- **The split.** `ghproc.log` restricted to the same range: 1132 gh process-seconds, 911 distinct
  gh pids. Shares are by process-seconds, then calls seen:

  | bucket | process-seconds | share | pids | callers |
  |---|---|---|---|---|
  | tick | 320 | 28.3% | 306 | `orchestrator_tick.py` 315, `pr_cap`, `approve_held_runs` |
  | beat | 252 | 22.3% | 105 | `plan_page.py` (plan-beat) 151 s over 14 pids; `beat_jobs`; `cancel_superseded`; `outside_intake`; `pulse`; `worktree_gc` only inside the beat disk pass 03:34:45-03:37:32 (journal `PASS ... disk start=03:34:45Z dur=167`) |
  | relay | 3 | 0.3% | 3 | `cloud_relay.sh` |
  | train | 179 | 15.8% | 151 | `merge_train.py`, `postmerge.py` |
  | train, inferred | 134 | 11.8% | 110 | `worktree_gc.sh` 03:27:08-03:33:44, outside any beat disk pass and during the train's run; `roster_sync.py` |
  | seats | 184 | 16.3% | 178 | |
  | sweep-runner | 48 | 4.2% | 48 | `blind_spots.py`, `s9/sweep-runner`, every ~15 min |
  | unattributed | 12 | 1.1% | 12 | |

- **Scheduled (tick+beat+relay).** 575 s, 50.8% of process-seconds, but 414 of 911 pids, 45.4%
  of calls seen.
  - The measures disagree about the half because `plan_page.py`'s 14 calls are long.

Cost: nothing is built.

Binding:
- The window passes 80% by one call and the scheduled share sits on the half. The decision
  condition is therefore marginal on both arms.
- An 80% guard would have shed under one minute of scheduled passes in this window, saving tens of
  calls against a 5000 bucket that was not exhausted.
- **What would reopen it:** one exhausting or above-90% window with scheduled callers at least
  half by calls, measured through the gh shim once PR 3427 (R10-GH-READ-RESIDUE) merges.
  - Calls under 1 s are under-sampled here. Cloud seats spend the same token from other hosts and
    are invisible. This is a sample, not a count.
