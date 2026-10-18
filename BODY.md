# R10-CI-CONCURRENCY pre-study (step 0, no fix written)

Harness head: `07b615a37b815e382d4e983703e803c9e11b0716` on `handoff/r10-ci-concurrency`
(`dev/audit/harnesses/superseded_runs.py`, sha1 `909b7a8a8f8908ab2c3c47eb736465a4f9e7c331`
at the time of the first commit; the committed file is the one measured below).
Based on origin/main `f4955e15f` (main has since moved to `c09d61dc9`; nothing below reads the tree).
Data fetched 2026-10-18T08:3xZ, figures taken 2026-10-18T08:47Z. Every figure is a function of the
window and the cache, so it is stale the moment main's PR traffic moves: re-derive with the commands.

## Commands

    # fetch (read-only gh api, paced; 6 workflows, 3 s apart; rate limit 4438/5000 after)
    gh api -X GET repos/tvofi/heatpump_optimizer/actions/workflows/<w>.yml/runs \
       -f created='>=2026-10-14T20:00:00Z' -f per_page=100 --paginate --jq '<fields>'   # w in tests validate hassfest governance codeql pr-contract
    # jobs for the superseded runs only (116 cached job pages, 1 s apart)
    gh api repos/tvofi/heatpump_optimizer/actions/runs/<id>/attempts/<n>/jobs --paginate
    # measure
    python3 dev/audit/harnesses/superseded_runs.py --selftest
    python3 dev/audit/harnesses/superseded_runs.py --cache $CACHE --since 2026-10-14T22:55:00Z --until 2026-10-18T07:24:00Z --jobs

Rule (brief's, with two stated refinements): non-main run, completed, conclusion != cancelled, and a run of the
same workflow on the same head_branch with a different head_sha STARTED inside this run's [start, updated_at].
Start is `run_started_at` (a rerun keeps the first attempt's `created_at`; `--start created_at` reads 37 as well,
tests wall 2139 vs 2136 min). The window selects the OLD run; the newer run may fall after it.
WALL = updated_at - start of the superseded run. TAIL = updated_at - start of the newer run (what an immediate
cancel gives back). BILLED = sum over jobs of ceil(job seconds / 60), Linux-minute basis, labelled apart; TAIL_BILLED
counts job time after the newer run's start only.

## Figures (window created 2026-10-14T22:55Z..2026-10-18T07:24Z, window selects the OLD run)

    RESULT tests      nonmain_runs=391 completed_not_cancelled=284 superseded=37 wall_min=2081 tail_min=968 tail_ge_5min=25 billed_min=6057 tail_billed_min=2042
    RESULT codeql     nonmain_runs=391 completed_not_cancelled=277 superseded=19 wall_min=450  tail_min=203 tail_ge_5min=16 billed_min=496  tail_billed_min=212
    RESULT validate   superseded=0     RESULT hassfest superseded=0     RESULT governance superseded=0
    RESULT pr-contract superseded=60 wall_min=45 tail_min=34 tail_billed_min=60   (cancel false on purpose; seconds-long)

All five PR workflows: only `tests` and `codeql` carry cost; validate, hassfest and governance finish before a
newer head can arrive (null: they print 0 and their NULLCONTROL line is 0).
The brief's 36 / 388 / ~2020 differ from 37 / 391 / 2081 by fetch time (the cache ends 08:37Z, runs finishing after
07:24Z are now complete) and by 1 duplicate row the paginated listing returned twice (tests 1, validate 1,
pr-contract 3; the harness dedupes by id and prints `deduped_rows`). Wall-min is not billed-min: the superseded
tests runs billed 6057 job-minutes across 2081 wall-minutes (matrix shards run in parallel).

**Null controls (printed on every run, must be 0, and they were):**
`all_cancelled_superseded=0` (the same set with every superseded run forced to `cancelled`),
`same_sha_superseded=0` (every run of a branch relabelled onto one SHA),
`unique_sha_dup_heads=0` (every run given a unique SHA). The third caught a real defect while I wrote this:
before the dedupe it printed 1, from a run the paginated listing repeated. `--selftest` drives seven synthetic
cases (superseded 1, cancelled 0, same-SHA 0, sequential 0, main 0, other branch 0, bot-sent 1) and passes.

## Classes the harness returns (tests unless named; `old -> newer`, sender = run actor; `+rerun` = attempt > 1 by hpo-runs)

| # | class | n | wall | tail | tail_billed | example old -> newer |
|---|---|---|---|---|---|---|
| A | App PR -> dispatch (bot) | 15 | 748 | 209 | 477 | 39103673327 -> 39107309553 |
| B | bot PR `+rerun` -> App PR | 8 | 630 | 425 | 986 | 39090494028 -> 39091600343 |
| C | bot PR `+rerun` -> dispatch (bot) | 4 | 284 | 126 | 242 | 38835580132 -> 38836257484 |
| D | dispatch (bot) -> App PR | 6 | 246 | 125 | 203 | 39090491271 -> 39091600343 |
| E | dispatch (bot) -> dispatch (bot) | 3 | 119 | 83 | 133 | 38835575916 -> 38836257484 |
| F | tvofi PR -> dispatch | 1 | 55 | 0 | 1 | 39088333397 -> 39091575112 |

codeql has the same five classes (tail_billed 36 / 56 / 37 / 54 / 29). **No tests class has an App/human PR run on
both sides.** That row exists only where the cancel was never wanted (pr-contract: 47 App->App, 35 wall-min).
Control that the harness would print it: pr-contract's App->App row.

**Mechanism per class (every class has a bot-sent or dispatched run on at least one side, and the other suspect is not the cause):**

- **B, D (new run = App PR; old run = bot-sent PR or dispatch).** The old run's group is `Tests-<run_id>`
  (sender `github-actions[bot]` or event `workflow_dispatch` -> group falls to `github.run_id`), so it is not in the PR group
  the newer App run joins; the newer run's `cancel-in-progress` is true but has nothing in its group to cancel.
  Run id 39090494028 (#2371): attempt 1 `action_required` at 02:33:07, approved by `hpo-runs[bot]` as attempt 2 at 02:33:13,
  ran to 03:18:34; run 39091600343 (App push, same branch, new SHA) started 02:52:07 and did not cancel it: 26 min tail.
  Same head carries dispatch 39090491271, which ran to 03:11:12, also past 02:52.
- **A, C, E, F (new run = dispatch).** A dispatch has `cancel-in-progress: false` and its own group, so it cancels nothing,
  by design (below). A: the old run is a normal App PR run whose own `closures-autofix` pushed the new head and dispatched
  the newer run; in 10 of 15 the old run ends within 5 min of the dispatch (it is the run that pushed; not waste), in 5 it keeps going.
- **The second suspect, `approve_held_runs.sh` on non-live heads: refuted as stated.** The approval target is the SHA just pushed
  (`PUSH_SHA`) and the approval lands ~6 s after the push (above), so the approved head is live when approved. It also does not run
  from the workflow: tests.yml/merge-main.yml approve inline as the Actions-only App; `tools/pr/approve_held_runs.sh` is the manual tool.
- **A third mechanism the brief did not name: the approved run duplicates the dispatch.** Every bot-pushed head in the window has
  both a dispatched Tests and a held-then-approved `pull_request` Tests: 26 bot PR runs, 26 dispatches, 26 heads with both, 0 without
  (command in "Extra checks"). These are SAME-SHA overlaps, not supersessions (null: relabelled-unique SHA prints 0):
  `same_sha_dup_min` tests 1024 wall-min, codeql 556, validate 30, hassfest 22. It is the largest single block seen and
  is **not** the rule's, so it is out of the recommendation below and named as a follow-up finding.
- **Documentation conflict, flagged not fixed.** `ci-autofix.md`, `merge_train.py` (R9-RC-AUTOFIX-GOVERNANCE) and tests.yml's autofix
  comment say a GITHUB_TOKEN push creates *no* `pull_request` run (measured 2026-10-09). In this window all 26 bot-pushed heads have a held-then-approved
  `pull_request` Tests run (earliest 2026-10-15T10:23Z), and the one head I listed in full (3b76e0b0, `gh api actions/runs -f head_sha=3b76e0b0...`) has
  eight such runs (Tests, Validate, Hassfest, Governance, CodeQL, PR contract, Arch score, Budget raise gate), all approved by `hpo-runs[bot]`. One of the two is stale.

## Q3: why the bot exemption exists

`git log -S"github.event.sender.login != 'github-actions[bot]'" -- .github/workflows` returns five commits.
The first is `a98d5a05a` (2026-10-01, "R9-F10.9c: PR-only run cancellation", process review item 3). Its comment in tests.yml
states the protected property: an autofix push (GITHUB_TOKEN, `github-actions[bot]`) must not cancel "the run it would cancel is still
running the other autofix jobs, and the next run's `ci:` subject is their loop guard, so a repair cancelled there never comes".
Concretely: `claims-autofix` needs `fast` and `mutation-autofix` needs `mutation`+`mutation-pins`, both tens of minutes to hours after `closures-autofix`
pushes, and `closures-autofix` skips when the head subject is `ci: re-record closures`. The other four (`2fc3ab2d0`, `6ec6553e5`,
`e960a747d`, `397895df0`) carry the clause into pr-contract / budget-raise-gate / arch-score, where the property is a different one: same-SHA twins
(`synchronize` + `edited`) must not cancel each other (R9-RC-PRCONTRACT, R9-CI-2a). `tests/entities.py` (`_cc_problems`) encodes both:
a bot-sent PR pair must get distinct groups and `cancel-in-progress` false.
The `ci-autofix.md` property (a GITHUB_TOKEN push writes no `pull_request` contexts, so dispatch + approve) is about the dispatch
and approve steps, not this clause; neither option below touches them.

The clause conflates two senders: it is right that a **bot-sent newer run must not cancel** (property above), and it is wrong that a
**bot-sent older run cannot be cancelled** by a newer App push. The second half protects nothing: the newer App head's run re-detects
every repair the older head still owed, and its subject is not a loop guard.

## Q4: interactions

- `run_twins.py` (same-SHA cancelled twins): an option that cancels only a run whose head_sha differs from the live head never makes a twin.
  The SHA to compare is `github.event.pull_request.head.sha`; `github.sha` on a pull_request event is the merge commit and would compare
  unequal to every run.
- merge-main bot: its `ci: merge main` push is sender `github-actions[bot]`, so it keeps never cancelling; its approved run becomes cancellable
  by a later App push (class B), which is correct (the merge result is moot). 14 of the 26 bot-pushed heads in the window are `ci: merge main` (8 `ci: pin killed mutants`, 4 `ci: re-record closures`; `git log -1 --format=%s <sha>` per bot PR run).
- Three autofix loop guards: unchanged under Option 1 (a bot-sent newer run still cancels nothing).
- `merge_train` CI wait: reads check-runs at the *live head* (`_check_runs(h)`); a run cancelled at an older SHA is never read. Cancelling
  can leave a required context ABSENT at the live head only if the live head's own run is cancelled; Option 1 cancels only on behalf of
  the live head (verified by an API read before cancelling) and only older SHAs, so the live head's run is never a target.
  Residual: if a superseded head returns (force-push back to an old SHA), that SHA's run was cancelled and the push creates new runs: same as today.
- budget-raise-gate, pr-contract, arch-score: `cancel-in-progress: false` and per-run/serialised groups are deliberate (twins, queue-replace).
  Not touched. Their wall is 45 min total (pr-contract), so there is no saving to buy.
- A queue entry (`merge_group`) has its own branch name and event; the selector below filters on event `pull_request`/`workflow_dispatch` and the PR's own head_branch.

## Options

**1. Cancel older runs by API from the live App-sent run (recommended).** In tests.yml and codeql.yml only, add a job (tests.yml: beside
`recheck-gate`; `actions: write` on that job alone) that runs when `github.event_name == 'pull_request'` and
`github.event.sender.login != 'github-actions[bot]'`, reads `GET /pulls/N` and proceeds only if `.head.sha == github.event.pull_request.head.sha`
(live head), then cancels every run of this workflow on this head_branch with `head_sha != live`, status queued/in_progress/waiting, event in
(`pull_request`, `workflow_dispatch`). One script under `tools/` shared by both workflows, with a self-test driving a stub `gh`.
The concurrency expression is **unchanged**, so the existing `entities.py` bot-never-cancels model stays true and still pins property 1.
Saves (harness, tests / codeql tail_billed): B 986 + D 203 = 1189 of 2042 / 56+54 = 110 of 212; wall 550 / 107.
Keeps: bot-new never cancels (autofix siblings); same-SHA runs; main push, merge_group, schedule untouched (selector is the PR's own non-main branch);
dispatch+approve unchanged. Loses: a bot-pushed head's pending autofix siblings when an App push supersedes it; mitigated because the App
head re-runs all autofix with its own subject. Risk: fork PRs have a read-only token (job is fail-soft and skipped for forks), one more
quick job per run (seconds), and the cancel API is a write, so `.github/workflows/**` is owner-reviewed.
**2. Put bot-sent PR runs into the PR group (change the group expression, keep `cancel-in-progress` false for them).** Fixes B, D without an API.
Rejected: a run that joins a group with `cancel-in-progress: false` queues pending behind the running one, and the next pending replaces it
(`budget-raise-gate.yml` and `pr-contract.yml` comments: the same hazard); the bot head's run would wait out the hours-long run it should replace,
and `entities.py`'s model (`share = ... who != github-actions[bot]`) is the one that would have to be inverted.
**3. Stop duplicating: skip approving the held run when a dispatch of the same workflow is already running at that SHA (or drop the four dispatches).**
Saves the same-SHA block (tests 1024 wall-min, codeql 556), more than Option 1, but it is not the rule's finding and carries the original #1276 risk
(a held run left `action_required` shadows the dispatched green in the merge box). Needs its own pre-study; filed as a follow-up, not folded in.
**4. Do nothing for A, C, E, F.** The new run is a dispatch; the old run may still owe autofix. A + C + E = 852 tail_billed of 2042 stay. E (dispatch -> dispatch,
133) is safe to cancel (dispatch runs have no autofix jobs, `if: github.event_name == 'pull_request'`) and may be added to Option 1 as a second selector; I would not,
until B, D land.

## Recommendation (fixer.md step 17)

Option 1, `tests.yml` and `codeql.yml` only, selecting older runs of the PR's own head_branch at a different SHA, from the live App/human-sent run.
It removes the cause (a bot-sent *older* run is unreachable from a newer run's group) without touching the part of the clause that protects the
repair loop. Expected: about 58% of tests' tail billed minutes (1189 of 2042 in the window, ~57% of tail wall (550 of 968)) and ~52% of codeql's. The three short
workflows have nothing to save. Option 3 is the bigger lever and is a separate finding (same-SHA duplicate approval), named for the orchestrator.

## Extra checks (commands)

    # bot PR runs vs dispatches per head (tests, window): python3 over $CACHE/tests.jsonl, filter head_branch != main, created in window:
    #   26 bot PR runs / 26 distinct heads; 26 dispatch runs / 26 heads; 26 heads with both; 0 dispatch heads without a bot PR run
        # actor split of non-main tests runs: 345 pull_request/hpo-author[bot], 28 pull_request/github-actions[bot] (attempt>1, by hpo-runs[bot]),
    #   26 workflow_dispatch/github-actions[bot], 14 pull_request/tvofi, 1 workflow_dispatch/tvofi, 1 workflow_dispatch/github-actions[bot] rerun
    #   (counts taken before the dedupe and over the whole cache, so they differ from the window figures above)
    git log -S"github.event.sender.login != 'github-actions[bot]'" -- .github/workflows   # five commits, first a98d5a05a

## Not done

No fix, no test, no workflow edit, no PR, no GitHub write (reads only). The fix's failing check, mutation proof, and the same-SHA / push-to-main /
live-head-bot null controls are step 1 and wait for the go.
