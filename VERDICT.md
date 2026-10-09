Fix review: blocked b630c9e1e122e20374cc5951ad2e6a1c9f011668 architecture-unsound: tools/pr/merge_main_bot.py:242 (added by this PR, inside the bot's own --self-test) hand-rolls a throwaway repository -- os.makedirs plus g = lambda ... git(...) with an env carrying only the four identity variables, then g("init", "-q", "-b", "main") -- instead of tests/throwaway_git.py's throwaway_git_init, so the inherited local layer is not dropped and maintenance.auto/gc.auto are never written: a parallel mechanism beside the one main now owns, breaching fixer.md step 17 ("the existing mechanism, never a parallel one; no concept duplicated"). The same site is what turns instrument-self-tests red at this head (check run 113711202025, 07:07:17Z), and because ## Red checks does not name that check the required pr-contract refuses the body (check run 113730589928, 08:09:56Z).
bus-nonce: 6d80923094fbb96f2417ce0668f2ec10
seat: review-2059

Round 3 (delta). I measured head b630c9e1e122e20374cc5951ad2e6a1c9f011668, still the live head at
posting (`gh pr view --json headRefOid` at 2026-10-09T08:53Z). Worktree
/Users/timmalmstrom/hpo-seats/review-2059/wt-delta, detached at that SHA.
Evidence: /Users/timmalmstrom/hpo-seats/review-2059/evidence/delta (head.txt, checkruns-head.json,
prc_fail_113730589928.log, instrument_selftests_fail.log + ist.clean, nightly_status_fail.log,
run_*.json, required_contexts.txt, body_now.md, pr_files_now.tsv). The round-2 verdict that approved
afe9cfd87 is at ../VERDICT.md.

This head is `afe9cfd87` (the approved head) merged with origin/main `f84d891e1`, so by fix-review.md
step 12 I judge the resolution delta alone: the merge's own changes beyond the two parents, plus what
CI says about the resolved tree. I did not re-run the mutation proofs or the finder's harness -- those
belong to round 2 and the fix's contribution is unchanged (measured, point 4 below).

## RESULT lines (mine, this round)

RESULT throwaway_git --check at b630c9e1: rc=1, REFUSE tools/pr/merge_main_bot.py:242: g("init", "-q", "-b", "main"); 1 site refused, 0 stale allow entries
RESULT check-runs at b630c9e1: total=40 pending=0 red = pr-contract, instrument-self-tests, nightly-status (delivery-status GREEN here)
RESULT required contexts (ruleset 23698884 `main-protect-checks`, 17): pr-contract IS required; instrument-self-tests and nightly-status are NOT
RESULT fixer.md merged-tree vs origin/main f84d891e1: 315/315 lines; step 17 byte-identical to main's (both b581ef00f222ae60bb7fcb63076b0300); only the PR's step 5, handoff and step 7 hunks differ
RESULT branch diff unchanged by the merge: 16 files in, 16 out; per-file `git patch-id --stable` identical for 15 of 16 (only fixer.md differs, as above)
RESULT claim files == origin/main's: tests/golden/claimed_drift.txt 62bf9eaba, card_claimed_drift.txt c683379da (both parents equal)
RESULT VERSION, custom_components/heatpump_optimizer/manifest.json, RELEASE_NOTES.md: blob-equal to f84d891e1
RESULT policy_lint.mjs --budgets at the head: rc=0; rules_sync --check ok; brief_lint rc=0 (round-2 evidence)
RESULT merge-tree origin/main(c518447eb) b630c9e1: exit 0, clean, merged tree 7bd1c30de1c96e2f1b722edcba95e0d8dea7695a -- so the further recarry the orchestrator owes is conflict-free
RESULT closures at the head: check run 113711387623 SUCCESS (the draft's open item is closed); closures-autofix 113728007280 skipped

## 1. The blocker: the bot's self-test builds its own throwaway repo

`tests/throwaway_git.py` landed on main at 4e2a56ec7 (2026-10-08T08:11:53Z, "one shared helper at
every init and clone site (R9-GITTMP)"; widened by 70819a011 and 9ddea090b). It did not exist at this
branch's base `4647321d8` nor at the approved head `afe9cfd87`, which is why instrument-self-tests was
GREEN there (round 2, run 113343501538 at 13:44:51Z) and red here: the merge is what brought the
detector to the branch, and the detector's refusal names a line this PR added --
`tools/pr/merge_main_bot.py` is new in this PR (331 additions, 0 deletions) and is absent from
origin/main. This is the branch's own red, not main's.

The site (236-242):

    env = {"GIT_AUTHOR_NAME": "t", ... }          # identity only
    os.makedirs(r)
    g = lambda *a, **k: git(r, *a, env=env, **k)
    g("init", "-q", "-b", "main")

`git()` at :68 is `subprocess.run(["git", "-C", repo, ...], env={**os.environ, **(env or {})})`. So
the repo is initialized with the caller's whole environment: none of `LOCAL_ENV` is dropped, no
`GIT_CONFIG_GLOBAL=/dev/null`, no `GIT_CONFIG_NOSYSTEM`, and neither `maintenance.auto=false` nor
`gc.auto=0` is written -- which is exactly what `throwaway_git_init` (tests/throwaway_git.py:138) does,
and returns. The self-test whose subject is a merge driver then installs its own `merge.fake.driver`
into that repository's config: an inherited config pair from the surrounding checkout is in scope for
its assertions. That is the defect class R9-GITTMP was built to remove, duplicated rather than joined.

Remedy, either arm, the first preferred:
- call `tests/throwaway_git.throwaway_git_init(r, "-q", "-b", "main")` (it mkdirs, writes both CONFIG
  keys and returns the env to pass to the later `g(...)` calls), and pass the env it returns; or
- if the hand-rolled site is to stay, register it in `throwaway_git.ALLOW` with its reason -- weaker,
  it excuses without improving, and step 17 asks for the fix that yields the better code -- and in
  that case the body must name `instrument-self-tests` under `## Red checks` and answer the trigger
  (cheaper detector and its standing cost, or the finding that none exists).

Naming a class: the class is the code defect, because that is what routes a repair. Had the fix been
sound and only the answer missing, step 11's word would be `root-cause-unanswered`; that class routes
to the root-cause seat and NOT to a fixer round (`web-fix-wave.js` ROOT_CAUSE_CLASSES), and a repair is
needed here, so `fix-review.md` step 15 (`architecture-unsound`) is the honest word. Whichever word,
the fixer owes both: fix the site, and after the new head re-take `## Red checks` against that head's
red set in the S10 order (commit, body, push).

## 2. The two reds the draft left open, settled from the logs

**`instrument-self-tests`** -- check run 113711202025 (workflow run 37897219083, Governance, created
07:07:13Z, job started 07:07:17Z, job concluded 07:09:59Z), failure. Read from the run log, not the
body: every self-test block in the job passes (`policy_lint_mutants`, fragments_sync 20/0,
field_coverage ok, gh_comment TOTAL: 0 failed, sweep 21/0, prepr 210/0, push 77/0, app_approve 155/0,
merge_main_bot 24/0, app_comment 57/0, bus 45/0, budget_raise_gate 206/0, contract_rerun 24/0,
merge_fastpath 35/0, tmp_paths 43/0, figure_lint 22/0, figure_census 13/0, codeowners_gap 50 probes
9 nulls 0 wrong) and the single failing step is the last two lines of the throwaway_git block:
`REFUSE tools/pr/merge_main_bot.py:242` then exit 1. So the red is one site, and it is this PR's line.
Shape: NOT a stale-body artefact -- it is a genuine red on a commit in the branch, and the body does
not name it. It is not required (ruleset 23698884 lists 17 contexts; this is not one of them), so it
does not block a merge on its own -- it blocks through pr-contract and through step 11.

**`pr-contract`** -- two runs at the same head, and the LATER one is the red one, so this is not the
S10 shape where an `edited`/`synchronize` race strands a failure on the outgoing commit and a later
green run clears it. Both runs are against b630c9e1 and both name b630c9e1 in `## Head`:
- run 113710718912, workflow run 37897068166 created 07:05:37Z, job started 07:05:45Z, concluded
  07:06:03Z -- SUCCESS.
- run 113730589928, workflow run 37897219011 created 07:07:13Z, started 08:09:52Z (queued ~62 min),
  refused at 08:10:07Z, concluded 08:10:11Z -- FAILURE, one error:
  `ERROR [pr-body] check "instrument-self-tests" is red and "## Red checks" does not name it.`
The gap between the two conclusions is timing, not a race the body could have won: the 07:05:45 run
read the red set before instrument-self-tests concluded (07:09:59), the 08:09:52 run read it after.
The second run's own line `skip red-history ... no GITHUB_TOKEN ... every head before the one this
ran on is UNCHECKED this run` means its range claim is weak, but the refusal is about THIS head's
current red set, so it stands. Disposition: red, required, and unanswered in substance -- the body
does answer pr-contract, but for the round-1 refusal (run 37777939476, about delivery-status and
nightly-status); it never names the check this run refuses.

**`nightly-status`** -- run 113711202065 (Tests, job started 07:09:13Z), failure, and it is not
required (its own log says so). Arm: the diff DOES touch `.github/workflows/governance.yml` (+6), a
reporter input, which voids `defect-root-cause.md`'s main-state exemption, so the body owes a named
answer -- and it gives one (`## Red checks` names `nightly-status` and answers it: lanes this diff does
not touch, the nightly reports its own state). Trigger answered; per step 11 I check that, not the
answer. One staleness point for the repair, not a block: the body cites scheduled run 37595831734 with
`mutation-ledger, mutation-nightly, record-autofix`, while the run this check read at this head is
37753990323 at main head 816547e (2026-10-08T09:03:21Z) with `closures, mutation-nightly,
nightly-ha (2025.2.0), nightly-ha (stable)`, and it notes 37889206903 was still in flight. The lane
set is main's to fix (the nightly `closures` lane red on main predates and excludes this diff by
construction). `delivery-status` is GREEN at this head, so the body's answer for it is now history
rather than a red.

## 3. The rest of the delta, established (draft's items, re-verified by me)

- `tests/closures.json`. With the merged tree's `tools/merge/ledger_merge.py`, `merge_text(base
  4647321d8, main, PR)` is byte-identical to the committed file in both orders; an independent per-key
  check ("base, plus what either side added, less what either side removed") finds 0 mismatches. Two
  keys changed on both sides, both merged as sets: `tests/entities.py` (main +3, PR +1) and
  `tests/harness_headers.py` (+1/+1). Layout is closure.py's (`FORMATS[0]`). CI agrees: `closures`
  113711387623 SUCCESS and `closure-scope` SUCCESS at this head -- the draft's open item is closed.
  A local `git merge-tree` may print `LEDGER-MERGE: refused tests/closures.json` from a driver
  installed before the PR's own driver change; the merged tree's driver resolves the file. Not a
  defect in the PR.
- `dev/governance/roles/fixer.md` -- the only file whose patch-id the merge changed. main's step 17
  (#2064) is kept byte-identical; the only other hunks are this PR's own step 5, handoff and step 7
  edits, re-applied and trimmed to hold 315 lines / 5216 tokens (`policy_lint --budgets` rc=0 at the
  head). Judgement on the trims: step 5 "Derive it:" and "`structure.py` runs before every push"
  (drops "regardless"), step 7 "(a `--carry` head: no re-take; name bot reds)", and the run_always
  obligation kept in step 5 -- meaning unchanged in each.
- Wording note (NON-BLOCKING, carry it in the repair if the token cap allows): the handoff line now
  reads "only the orchestrator, the merge-main bot or `--carry` moves it". Read literally that is
  wrong -- `app_approve.sh --carry` is a predicate and moves nothing; the third mover is the class of
  commits `--carry` accepts (bot autofix commits). Restore the word "commit" ("a `--carry` commit")
  where the cap allows; nothing is widened and the rule is recoverable, so it is not a block.
- The other 14 files: blob-identical to `afe9cfd87` or patch-id-identical across the merge, so the
  branch's own contribution is unchanged by the resolution. File set in equals file set out (16).
  The auto-merged four (`governance.yml`, `fix-review.md`, `tests/entities.py`,
  `tools/pr/app_approve.sh`) keep the PR's own +/- lines.
- Step 13: `mergeStateStatus` is BLOCKED, not DIRTY, and a fresh `git merge-tree --write-tree
  origin/main(c518447eb) b630c9e1` exits 0 with tree 7bd1c30de -- no conflicting path at all. The
  PR is a draft; I left it as it is. main moved past the merge's second parent, so a further recarry
  is the orchestrator's and it is conflict-free.
- The PR is authored by `app/hpo-author`; `## Head` names the SHA I measured (step 7 satisfied).

## 4. What survives from round 2, and what to re-take after the repair

The fix's substance is unchanged by the merge (15/16 patch-ids identical, claim files equal main's,
VERSION/manifest/notes untouched), so round 2's conclusions on the carry predicate, the forged-author
and claim-subject arms, the `autofixMerge` ancestry check and the two mutants still stand. After the
next head, re-take for that head and re-measure: the 24/155 self-test counts, the three reds above
(all read from CI, not re-run here per step 11's cite-CI rule), and `## Red checks` against the red
set that exists at the new head in the S10 order.
