Fix review: merge 0632f89c89ad94f52bd7491fd4b7ea17a2d40968
bus-nonce: fe758bb22f3594db31439372e12cbdae
seat: review-2059
round: 5
Evidence: /Users/timmalmstrom/hpo-seats/review-2059/evidence/r5 (head.txt names the full sha I measured)

RESULT throwaway_git --check at 0632f89c8: rc=0, `0 raw git init or clone site(s) refused, 0 stale allow entries`
RESULT throwaway_git --check --ref b630c9e1: rc=1, `REFUSE tools/pr/merge_main_bot.py:247`-shaped site — the refusal was this branch's line
RESULT throwaway_git --check --ref origin/main: rc=0 (main is clean, so the red was never main's)
RESULT MY MUTANT A (hand-rolled `os.makedirs` + `g("init", "-q", "-b", "main")` restored, committed as bac965559): `REFUSE tools/pr/merge_main_bot.py:247: g("init", "-q", "-b", "main")`, rc=1 — the detector still bites
RESULT git diff origin/main...HEAD -- tests/throwaway_git.py: 0 lines — the branch weakened neither the detector nor its ALLOW list; no entry was added
RESULT merge_main_bot --self-test at head, clean env: `24 checks, 0 failed`, rc=0 (24 `ok` lines counted myself)
RESULT merge_main_bot --self-test at head, `env GIT_DIR=/nonexistent/.git GIT_INDEX_FILE=/nonexistent/index`: rc=0, `24 checks, 0 failed`
RESULT same hostile command at the blocked head b630c9e1: rc=1, `RuntimeError: git init -q -b main: rc=128 fatal: Cannot access work tree '/nonexistent'` — the fixer's both-ends pair, re-derived
RESULT MY MUTANT B (throwaway_git_init kept, `with throwaway_git_environ():` removed): clean env rc=0 `24 checks, 0 failed`; hostile env rc=1 `RuntimeError: git config merge.fake.driver …: rc=128 fatal: not in a git directory` — the wrapper is load-bearing, not decoration
RESULT MY MUTANTS on the head's decision (own edits to a `git archive` copy, one at a time): B5 (GitHub's view computed with the drivers) → `FAIL a ledger-only conflict the driver resolves is planned for a merge [skip-no-text-conflict]`, rc=1, run aborts before the tally; B1 (a conflict no driver owns allowed) → `24 checks, 2 failed` rc=1; B4 (a driver's `refused` ignored) → `24 checks, 1 failed` rc=1. Each reproduces the fixer's line and count, so the swap did not hollow out the subject
RESULT app_approve.sh --self-test at head: `153 checks, 0 failed`, rc=0
RESULT carry() byte-identity (my own extractor, brace-balanced from `carry() {`): 61 lines, sha1 `11e32b6dbf48` at `0ac45f641` (where P1–P7/F0/B2/B3/B6 were killed), `afe9cfd87`, `b630c9e1` and this head — the inherited mutation record does describe this tree for the carry arms
RESULT structure.py: `STRUCTURE RATCHET PASSED`; policy_lint.mjs: `TOTAL: 0 error(s)`; --budgets rc=0 with `fixer.md` 315/315 lines and 5215/5216 tokens; no `*budgets*` file in the three-dot diff — no cap raised, none re-recorded
RESULT policy_lint --pr-body <this body> --head 0632f89c8: `PR-BODY: 0 error(s)` and its own census `record red-history 15 commit(s) between origin/main and this head, every failure conclusion across them: CodeQL, delivery-status, instrument-self-tests, nightly-status` — `record`, not `skip`, so the earlier heads were read, and the body names all four plus `pr-contract`
RESULT check-runs API at the head, latest run per name (two polls, 12:1xZ and 12:3xZ): `instrument-self-tests` success, `pr-contract` success (its two runs both success, no red-then-green), `nightly-status`/`delivery-status`/`CodeQL` success, 16 of 17 required contexts success, `closures` **in_progress** — the one figure I could not get, and it is CI's lane, not mine to re-run. No name in the latest set concluded failure
RESULT nightly_status.py now (12:2xZ): rc=0 `NIGHTLY PASSED … dispatched run 37889206903, head 47b083b` — still the body's 09:58Z reading, and CI's own `nightly-status` is green at this head
RESULT delivery_status.py --check: rc=0 `DELIVERY STATUS OK — 7 rowed, 0 pending, 0 overdue (overdue at 12 commits)`; the branch adds exactly one row, `dev/programme/delivery/2059.md`, status `open`
RESULT blob equality HEAD vs origin/main: `tests/golden/claimed_drift.txt`, `tests/golden/card_claimed_drift.txt`, `VERSION`, `manifest.json`, `RELEASE_NOTES.md` all identical — claims nothing, moves no version
RESULT git merge-tree --write-tree origin/main HEAD: rc=0, tree `b3932f1d6a3b3517cd50584ed7c6d7da1cd2c8e7`, empty stderr — no `MERGE-CLAIM: refused` for any file, and the head is `mergeable: MERGEABLE`, not DIRTY
RESULT three-dot shortstat: `16 files changed, 734 insertions(+), 49 deletions(-)`; repair commit 47ba57929 alone: one file, +16/-7
RESULT archscore score.py --diff origin/main: `Architecture score: dS +0.0000 NULL`, rc=0, `real 29.11`
RESULT throwaway_git.py --self-test at head: `44 checks, 0 failed` — the helper itself untouched and passing
RESULT rules_sync.mjs --check: `RULES-SYNC ok` — the generated `.mdc` copies match their sources

## What round 4 blocked on, and whether the repair answers it

Round 4 blocked `architecture-unsound`: the bot's own `--self-test` hand-rolled a throwaway repository beside the mechanism main now owns. The repair takes main's mechanism: `throwaway_git_init` builds the repository, `throwaway_git_environ()` wraps the `--self-test` arm, and the hand-rolled `os.makedirs` + `g("init", …)` is gone. I confirmed the absence three ways, not one: the site is not in the file (only the helper call and a comment), `--check` is rc=0 at the head and rc=1 at `--ref b630c9e1`, and my own Mutant A, which restores the deleted shape and is refused again at once. A green detector proves nothing unless a planted defect still trips it; this one does.

The fixer's argument that the wrapper is load-bearing (`git()` at :70-72 merges `os.environ`; `plan_one`/`merge_tree`/`commit-tree` pass no `env=`) I did not take on its word. Mutant B keeps the helper and drops only the wrapper, and the hostile `GIT_DIR` run goes red at `git config merge.fake.driver` — a call the *production* wrapper makes, with no env of its own, exactly as argued. A repository-local config cannot rescue an inherited `GIT_DIR`, which is why `throwaway_git_environ` exists. So the two halves of the repair are each necessary, and I measured each separately.

## fixer.md step 17, judged on the added lines (+16/-7)

Sound. One owner per concern: both functions come from `tests/throwaway_git.py`, the module that owns the concept; nothing in `merge_main_bot.py` re-implements env scrubbing, identity or the two config keys. No parallel mechanism: the `sys.path.insert(0, str(ROOT / "tests"))` is the route main already takes for this helper (`dev/audit/harnesses/dual_path.py:91`, `ci-version-edit/pr_contract_shapes.py:22`), and the wrapper is the exact Python twin of what main's own sibling lane does in shell — `tools/pr/app_approve.sh:530` sources `tests/throwaway_git.sh` and calls `throwaway_git_env`, which unsets and exports into the ambient process for the whole self-test. The body's line "it is the same route main's own lane took through this file's sibling" is true, and it is the reason the wrapper is the existing mechanism rather than a new one.
The `ROOT` consolidation is sound: the expression `Path(__file__).resolve().parents[2]` existed once and the repair needed it twice (the `policy_lint.mjs` path and the new `tests` path), so it became one module-level constant beside the module that owns it. No concept duplicated, no new public surface, no production function changed — `self_test` and `main` only, which is what `## Null control` claims and what the diff shows.
Two non-blocking observations, mine, neither a breach: `throwaway_git_init`'s return value is now discarded (the env arrives through the wrapper instead of per call) — harmless, and the comment above it says why the call is still needed; and `self_test()`'s function-level import resolves only because `main()` inserted the path first, which its own inline comment records. A third seat could fold both by having `self_test()` take the path insertion, but nothing about that is unsound today.

## Step 14, and the numbers the repair moves

The only instrument the repair moves is `tests/throwaway_git.py --check`, from 1 refused to 0. The movement is earned, not a silencing: the diff adds no `ALLOW` entry (that file is byte-unchanged from main), does not leave the scanned scope (`tools/` is in `_SCOPE_DIRS`), and my planted defect still trips it. `structure.py`, `policy_lint --budgets`, the mutation ledger and `score.py` all read the same as main's own or better, and the archscore is NULL — a one-file, +16/-7 change with no metric payment and none owed.

## Step 11 — the range's reds

Each of the four the census returns is named in `## Red checks` and answered with a cheaper detector and its standing cost (`--check` at `real 0.26`–`0.49`; `delivery_status.py --check` in seconds), or with the finding that no cheaper one exists (`CodeQL`, `nightly-status`). Both `instrument-self-tests` and `pr-contract` — the two that actually refused this PR — are green at this head, and `pr-contract`'s refusal was a *consequence* of the `instrument-self-tests` red, so the repair closes the chain rather than muting the reporter.
`nightly-status`: the body states the rule and reports both readings with run ids, and its honesty check is that the instrument's rule is "the newest *concluded* `schedule` or default-branch `workflow_dispatch` run". I read `tests/nightly_status.py`:174-177 and :263-276 — a default-branch verification dispatch legitimately *is* the nightly there — and my own run now reproduces its 09:58Z output verbatim. Pinning one of those numbers in a body would have gone stale on the next dispatch; quoting the rule and both readings is the honest form.
`delivery-status` red inside the range, green at the head and green for me locally with the branch's one row present. `CodeQL` red at `9e44f73c1` closed inside the branch at `154c9139` (`0o700`), no failing run at any later head — and green at this one.
Not green yet: `closures`, the heavy gate lane, `in_progress` at both my polls. By step 11 that is not a red and owes no answer; by step 12 it is a number I did not get and the orchestrator's to read after the handoff settles. Everything else required is success.

## Step 12, and the one figure in my dispatch brief the tree contradicts

The head I measured is the live head: `gh pr view --json headRefOid` = `0632f89c89ad94f52bd7491fd4b7ea17a2d40968`, the same sha I re-read before posting this, and the sha the body's `## Head` names. The head is that sha plus one repair commit and two clean merges of main (each rc=0, no driver resolution), so per step 12 I judged the repair and the merged tree, and every RESULT line above is mine at this head.
This is round 5, and `fixer.md` owes a re-cut from the fourth: the body I read is one — 8 headings covering the template's 7, round history not restated, every figure re-taken at this head, the one inherited record (`0ac45f641`'s mutant ledger) disclosed as a record and then *proven* still applicable by `carry()` byte-identity, which I re-derived rather than accepted.
My dispatch brief said the three-dot diff should be "the five files the body claims". The tree answers 16 files, +734/-49, and that is exactly what the body claims; the five-file figure is not a description of this diff and I could not build one from it (the only five-set that resolves is the body's `## Approval` list of policy files). I am recording the disagreement rather than reporting a check I could not define: the diff is 16 files, the repair delta is 1 file, and both numbers match the body.
One trap for the next seat, mine and not the PR's: I ran `tests/closure.py select --diff <merge-base>` in this worktree with my own scratch file left untracked at its root, and it printed `MODE: FULL … reason: no recorded closure mentions .seat-claim-r5`. The body's `MODE: SCOPED -- 2 script(s) run, 31 scoped out` re-derived exactly in a clean tree. Key on the reason line before blaming a branch for a FULL you caused.

Merge. The blocked defect is gone at the head, the detector still bites my planted copy of it, the bot's real job is still driven and its mutants still kill, every number the body quotes that I could re-derive I did, and the one lane left is CI's `closures`.
