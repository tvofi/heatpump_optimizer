# D13-s1, round 11: first-pass yield, rounds per merge, verdict coverage

Seat D13-s1, baseline `92d38ecb640bd462f2e19c0814d0f0b7df1ee692`, box B8. Cells: D13.M1 and D13.M2,
any file (`check_scopes.py --seat D13-s1` prints `M1+M2 - (any file: no file axis)`).

## Window and method

- Window: `v7.1.10..92d38ecb` (250 first-parent commits). Merges come from `/commits/<sha>/pulls`
  through `policy_lint.mjs:resolvePrFromCommit` and `enumerateMerges` (API mode), with failures
  counted: **234 merged PRs, api_failures=0, 0 recovered from the subject**.
- For each PR the harness read `/pulls/<n>`, and every page of `/issues/<n>/comments` and
  `/pulls/<n>/reviews`. It then ran the production `policy_lint.mjs:statsHistogram` over the
  combined stream once for the whole window and once for each PR (for the max).
- The verdict bus is the population `review_strength.py` reads: origin's `review/<pr>`,
  `verdict/<pr>`, `archive/review/<pr>` and `archive/verdict/<pr>`. The harness read it for the same
  PRs and compared it with the comment population by (PR, word, head).
- Enumerator for both steps (one merged PR per line, 234 lines):
  `PYTHONPATH=tests/hastub node dev/audit/rounds/round11/D13/s1/yield_rounds.mjs --list`

## M1: first-pass yield and rounds per merge (comment and review population, as the brief defines it)

| metric | value |
|---|---|
| merges / verdict-carrying merges | 234 / 206 |
| verdicts (all 420 are issue comments, 0 are reviews; 0 fall outside the grammar) | 420 |
| first-verdict yield | 120/206 = **0.583** |
| one-round yield (merged on its single verdict) | 98/206 = 0.476 |
| rounds per merge, mean / max | **2.039** / 10 (#3355) |
| later rounds by kind: repaired after `blocked` / re-verified after `merge` at a moved head / repeated the same head | 150 / 55 (36 PRs) / 9 |

An independent Python reading of the brief's rule (`^Fix review:\s*(merge|blocked)`) produced the
same figures: 206 PRs, 120 first-merge, 420 verdicts.

## M2: verdict coverage by class (title type, author)

| class | no verdict / window | exempting rule |
|---|---|---|
| record, hpo-author[bot] | 23 / 24 | `.github/workflows/nightly.yml` record-autofix: "A record pull request the guard passes merges with no review seat" (tvofi, 2026-10-07). This sits in a workflow comment, not in a policy file. |
| build, dependabot[bot] | 4 / 4 | `.github/workflows/dependabot-automerge.yml` (tvofi, 2026-10-24). #3321 was approved by an agent comment, not by the workflow. |
| (untyped) lanes, hpo-author[bot] | 1 / 184 (#3618) | none. Its merge verdict is on the bus and was never posted (finding 01). |
| triage 12, hotfix 3, roster 3, closure 3, policy 1 | 0 | n/a |

That leaves 1 unexempt merge (#3618). Author does not separate classes in this window: every
non-Dependabot PR is `hpo-author[bot]`.

## Findings

- **D13-s1-01** (medium, I4): the verdict population of `policy_lint.mjs --stats` (comments and
  reviews) does not match the review rounds on the verdict bus.
  - 42 bus verdicts never reached the PR. 24 of them are `blocked`, they span 32 PRs, and 42 of 42
    heads are ancestors of the merged branch.
  - 9 comments relay one verdict a second time (same `bus-nonce`, 8 PRs).
  - Reading the bus once (`--perturb dedup,bus-union`) moves rounds/merge from 2.039 to 2.178,
    one-round yield from 0.476 to 0.452 and verdict PRs from 206 to 208.
  - #3618, a fix lane, then reads as carrying a verdict.
  - Dedup alone gives 411 verdicts and a mean of 1.995. Bus-union alone gives 462 and 2.221.
  - The brief's M2 perturbation (`--perturb reshape`) moves coverage from 206 to 205 and puts
    #3374 in triage's no-verdict row.

## Non-findings

- Enumeration: 0 API failures and 0 subject-gap recoveries over 250 first-parent commits.
- Both endpoints are read: 0 review-endpoint verdicts and 420 issue-comment verdicts. Nothing is
  hidden on `/pulls/<n>/reviews` in this window.
- Grammar: 0 `Fix review:` lines fall outside `VERDICT_RE`, and the brief's looser rule matches
  the same 420.
- `fetchWindow` reads one page of 100 per endpoint. The window's maximum is 10 comments and 7
  reviews on one PR, so the page limit is not reached.
- Re-verification cost was probed and left inconclusive (harness gap). I ran
  `tools/audit/seat/review_carry.py` on all 55 re-verify pairs, with main taken as of the later
  verdict. It printed FRESH-REVIEW 55 times, and 42 of those rounds returned `merge` again.
  However, most refusals read "no branch tip of origin". Those branches are deleted now, so a
  replay after the fact cannot reproduce the "ours" test, and this is not reported as a finding.

## Leads

- D5-s8: `tools/policy/policy_lint.mjs` `prClass`. The comment says
  `delivery-status-tracking.md` exempts `record` PRs from review. That file contains no exemption
  (`grep -i exempt` finds nothing). The predicate that does exempt them is a comment in
  `.github/workflows/nightly.yml`.

## Harnesses

- `dev/audit/rounds/round11/D13/s1/yield_rounds.mjs` (M1 and M2, with the perturbations
  `reshape`, `dedup`, `bus-union`, and `dedup,bus-union`). Outputs are saved beside it as
  `yield_rounds.*.out`.
- `dev/audit/rounds/round11/D13/s1/window_fetch.mjs` is the window reader the harness imports. It
  caches under `os.tmpdir()`.

## Exposure

These sources were read through the GitHub API on 2026-11-16, as the brief directs:

- `/commits/<sha>/pulls` for 250 commits.
- `/pulls/<n>`, `/issues/<n>/comments` and `/pulls/<n>/reviews` for 234 PRs: verdict first lines,
  and the full bodies of #3379, #3448, #3568, #3618, #3545 and #3321.
- `git ls-remote` and fetches of origin's verdict-bus refs and archive tags for those PRs. I read
  the bus history of #3461, #3517 and #3618.

Refs I created temporarily under `refs/d13s1/` in the shared repository were deleted again. None
remain.

## Unfinished

None. Both steps examined 234 of 234.
