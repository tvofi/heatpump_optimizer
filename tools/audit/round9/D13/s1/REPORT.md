# D13 round 9, seat s1: process yield and cost

Baseline `1936d5ca72a06556eeed4e8e5bf3dea520e517e1` (v6.7.1). Box B3: a 4-CPU container shared with other seats. Window `v6.6.0..1936d5ca`: 267 first-parent commits, 253 of them `Merge pull request #N` subjects and 14 stamps. Every count below is a GitHub-reported count or a git count, so none is a local timing. `load1` is quoted only because the harness contract asks for it.

## Method

- `fetch_window.py` (with `r9lib.py`) builds `window.json.gz`, a trimmed snapshot of every GET the harnesses need:
  - `/commits/<sha>/pulls` for every first-parent commit, keeping all rows;
  - `/pulls/<n>`, `/issues/<n>/comments` and `/pulls/<n>/reviews`, each paginated;
  - the check-runs listing at each merge commit and at each PR head, with pages decoded and joined.

  The fetcher uses `curl`, because CPython 3.14's strict X.509 mode rejects the proxy CA. It rewrites GitHub's `/repositories/<id>/` next-links to `/repos/owner/name/`, because this container's egress policy answers the id form with 403. That rewrite took 5 check-run listings with more than 100 runs from `api_failures=5` to 0. The final snapshot has `api_failures=0`.
- `yield_rounds.mjs` covers M1, M2 and M3. It imports `.claude/workflows/policy_lint.mjs` and drives `statsHistogram`, `waveVerdictRe`, `blockClasses` and the `stats*Line` functions over the snapshot. Beside them it computes the brief's own rule (`^Fix review:\s*(merge|blocked)`, both endpoints, ordered by time).
- `enum_gap.mjs` covers the M1 population. It runs the production CLI `policy_lint.mjs --stats --since v6.6.0` offline, through a stub `curl` that replays the snapshot. The replay reproduced the live run's lines exactly: `STATS: 201` and `STATS COVERAGE: 188 of 201`.
- `dora_by_job.py` covers M4. It imports `tools/audit/round4/D11/dora_keys.py` (`latest_by_name`, `cfr_keyings`, `cfr_by_name`, `load_exclusions`) and adds the brief's revert arm.
- `gov_cost.py` covers M5. It imports `tools/audit/round4/D11/governance_cost.py` (`GOV`, `dur`) and re-derives the governance set from the workflow files, using the rule stated in `GOV`'s own comment.
- `friction_keys.mjs` covers M6. It uses the brief's `--budgets` path rule, the production `frictionEntries` parser, and the production `statsHistogram` friction key for comparison.

## Findings

### D13-s1-01 (M1, medium): the API-mode enumerator silently drops 52 of the window's 253 merges

`enumerateMerges`, via `fetchPullsBySha`, skips any first-parent commit whose `/commits/<sha>/pulls` answers `[]`, on the grounds that such a commit is a stamp.

In this window, 52 merge commits for PRs #1098–#1165 answer `[]`. Their subjects all read `Merge pull request #N`. Their pull-request records return 404 today: `/issues/N` is 404 for 1097–1200 except 1104, 1127, 1128 and 1131.

As a result:
- `--stats` prints `STATS: 201 merged pull request(s)`, with no line naming the gap (`gap_marked=0`).
- `STATS COVERAGE` then reads 188 of 201. Counted over every merge, the coverage is 188 of 253.

Measured values:

| Run | `stats_window_merges` | `subject_merges` | `gap` |
|---|---|---|---|
| Baseline | 201 | 253 | 52 |
| `D13_PERTURB=drop:<8cca77bc>` | 200 | 253 | 53 (still unmarked) |
| `D13_PERTURB=restore` | 253 | 253 | 0 |

**Fix scope:**
- In API mode, a first-parent commit whose subject names `Merge pull request #N` and whose API rows are empty is still a merge. Count it as a merge whose data could not be fetched, and print it on the `unfetched` / `UNCHECKED` line.
- `fetchWindow` must then not abort the whole histogram on that PR's 404.

### D13-s1-02 (M1, high by the D13 severity rule): 22 re-verification rounds after a moved head caught nothing

The window has 22 parsable verdicts that each follow a `merge` verdict on a different head. The production `statsHistogram` counts these as `rounds.reverify`, 22. All 22 were `merge`, so `reverify_blocked=0`.

By `git log --first-parent prev..head`, the head moved for three reasons:

| What moved the head | Rounds |
|---|---|
| Merges (of `main`) only | 11 |
| `ci:` bot commits only | 1 |
| Branch content | 10 |

Re-verification is 22 of the 49 rounds after a PR's first verdict (the other 27 are 21 repairs and 6 repeats). It is the largest part of the process's rework, and over the window it detected 0 defects.

- Perturbation: `D13_PERTURB=block_one_reverify` moves `reverify_blocked` from 0 to 1.
- Null control: the repair rounds that follow a `blocked` verdict (21) are where every catch happened.

**Fix scope:** a mechanical equivalence check for a head moved only by merges of `main` or by `ci:` bot commits (the 12 rounds). For example, the branch's diff against the new merge base is byte-identical to the reviewed diff. The fix review then re-runs only when that check fails.

### D13-s1-03 (M3, high by the brief's own example): more blocked verdicts went on the body not answering a red check than on any engineering class

The window has 21 blocked verdicts. By the first class word:

| Class | Verdicts |
|---|---|
| `root-cause-unanswered` | 6 |
| `red-check` (untaught) | 2 |
| Any single engineering class | at most 1 |

That puts 8 body-answer blocks (`m3_body_answer_blocks=8`) against a largest engineering class of 1 (`m3_max_engineering_class=1`).

By bucket, each untaught word keeps its own row and is bucketed by the taught class it restates (see the harness header):

| Bucket | Blocked verdicts |
|---|---|
| Record-and-body | 12 |
| Engineering | 7 |
| Orchestration | 2 |

- Perturbation: `D13_PERTURB=rca_to_harness` moves the counts to 7 / 2 and the buckets to 11 / 8.
- Untaught words used: 10 of 21 blocked verdicts (`red-check`, `wrong-input`, `vacuous`, `mutation`, `readme-numbering`, `dirty`, `measurement`, `closures-unrepaired`, `carry-incomplete`), each on its own row.

**Fix scope:** the predicate `root-cause-unanswered` needs is "a check went red on a commit of this branch, and the body does not name it". It is mechanical from the check-runs listing and the body. `defect-root-cause.md`'s cheaper-detector rule applies to it: make it a check run before review, not a review round.

## Non-findings (measured)

- **M1 yield.** Brief rule: 172 of 188 merges carrying a verdict had `merge` as their first verdict (0.915). Rounds are 1.271 verdicts per merge on average, with a maximum of 4. The production one-round yield is 0.819 (154/188).
  - Endpoints: 237 issue-comment verdicts and 0 review verdicts.
  - 2 lines parse under the brief's rule but are refused by the wave's `VERDICT_RE` (#1551, #1287). Production reports both as unclassified, on their own rows.
  - `/commits/<sha>/pulls` returned more than one row for 0 commits, so `rows[0]` is never ambiguous in this window.
  - No PR had more than 5 comments, so the unpaginated `per_page=100` comment read loses nothing here.
- **M2 coverage.** 13 of 201 merges carry no parsable verdict, and every one of the 13 carries an APPROVED review from the owner account, tvofi. No tree file exempts any class. By class:

  | Class | Merges with no verdict |
  |---|---|
  | Fix/feature | 2 of 57 |
  | Record/chore | 6 of 36 |
  | Other lanes | 3 of 89 |
  | Bot cycles | 1 of 2 |
  | Untitled merge-subject titles | 1 of 17 |

  Perturbation `reshape_one` lowers coverage from 188 to 187.
- **M4 DORA by job.**

  | Key | Value |
  |---|---|
  | Deploys | 14 in 9.17 days (1.53 per day) |
  | Lead time | median 8.59 h, p90 21.22 h |
  | CFR at the merge commit, with exclusions | 0.174 |
  | CFR at the merge commit, without exclusions | 0.736 |
  | CFR at the PR head | 0.065, the same before and after the exclusion |
  | Merges reverted by a descendant, or by a merged `Revert "…"` PR | 0 (the window's one `This reverts commit` targets a branch-internal bot commit, not a merge) |

  - Per name at the merge commit: `record` 127, `instrument-self-tests` 18, `policy-docs` 10, `fast (3.14)` 8, `mutation` 4, `env-matrix` 3. None of these fails at any PR head.
  - Per name at the PR head: `delivery-status` 6, `nightly-status` 5.
  - All 35 non-excluded merge-commit failures are merge-surface-only. 14 of them follow another merge within 10 minutes; for all merges, 57 of 201 do.
  - Time to restore: `instrument-self-tests` was red for one 11.69 h episode across 18 merges.
  - Perturbation `D13_ADD_EXCLUDE=instrument-self-tests` takes the merge-keyed CFR from 0.174 to 0.109, a drop of 13/201, which is exactly its sole-failure count.
  - `dora_keys.py` has no revert arm; it is immaterial at 0 in this window.
- **M5 cost.** At the PR head, governance is 246.2 s per merge on average (median 227) and the gate is 4950.8 s (median 4095), so governance is 0.0474 of CI seconds.
  - The set re-derived from the workflow files adds `rerun-stale-verdict` (`budget-raise-gate-rerun.yml`), which the pinned `GOV` misses: 64 s over the window, at merge commits only. Share at the merge commit: 0.0409 with the pinned set, 0.0410 with the re-derived one.
  - Perturbation: dropping `pr-contract` takes the head share from 0.0474 to 0.039.
- **M6 friction keys.** 126 entries, all parsed. 78 name exactly one `--budgets` file (0.619), 0 are ambiguous and 48 are unresolved. The largest unresolved key is `decision-0013` ×6, a decision document with no `--budgets` path.
  - Spellings per file, for example: `fixer.md` 12, `tools/audit/briefs/fixer.md` 5, `fixer` 2, `fixer.md#…` 3; `gate-scoping` 7, `gate-scoping.md` 7, full path 1; `ratchet-budgets` 7, full path 2, `.md` 1.
  - The production `frictionKey` disagrees with the brief's rule on 5 entries: bare `fixer`/`orchestrator` are kept verbatim by design, and the `-s5`/`-step3` prefix walk resolves ids the brief's rule leaves unresolved.
  - Perturbations: re-spelling one entry as `README.md` moves it to the ambiguous row; `ratchet-budgets` written without backticks leaves the file's count at 10.

## Harnesses

`fetch_window.py`, `r9lib.py` (a library), `yield_rounds.mjs`, `enum_gap.mjs`, `dora_by_job.py`, `gov_cost.py` and `friction_keys.mjs`, with the snapshot `window.json.gz`. Each harness header carries its command.

## Unfinished

None.

## Exposure

- Read `main`'s git history and the GitHub REST API: commits→pulls, pulls, issue comments, reviews and check runs over the window, including the verdict and friction text, as population only.
- Read the headers of `tools/audit/round4/D11/{dora_keys,governance_cost,d11lib}.py` and `.claude/workflows/cfr_exclusions.json`, which the brief names as bases. Their comments cite earlier D13 finding ids; none is cited here as evidence.
- Listed directory names under `tools/audit/round5..8/D13` but read none of their files.
- Used the `mcp__github__pull_request_read` tool once, to confirm that #1165 is 404.
