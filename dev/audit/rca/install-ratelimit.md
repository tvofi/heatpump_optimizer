# R10-RCA-INSTALL-RATELIMIT: required checks red on "API rate limit exceeded for installation"

Root-cause seat for the round-10 recurrence of the rate-limit red. It ran beside
any fix, never as the fixer (`dev/governance/roles/root-cause.md`), and records
only: no workflow is changed here. Measured at origin/main `04c1dd779`.

**Defect.** Required checks fail on a read the check did not get to make:
`gh: API rate limit exceeded for installation ... (HTTP 403)` in arch-score's
first step (job `119753501292`, PR #2580, 09:44:27Z), `GitHubRatelimitException`
in validate-hacs (job `119753495288`), and the same in pr-contract and
env-matrix. Three times on 2026-10-22, about 06:27Z, 08:40Z and 09:44Z. Each
red turned a merge-ready head red and cost the merge train a re-run cycle of an
hour or more.

## 1. Cause

### 1.1 The bucket is `GITHUB_TOKEN`'s, not an App's

Every job that went red reads the API with the workflow's own token, and no
App token is minted in any of them:

| job | file | credential | calls per run (static) |
|---|---|---|---|
| arch-score | `arch-score.yml` | `secrets.GITHUB_TOKEN` | 1 (`pulls/N`); 2 on `merge_group` |
| pr-contract | `pr-contract.yml` | `secrets.GITHUB_TOKEN` | 2 `pulls/N` (body, author: the same object read twice) + 1..n `check-runs` + red-history 1 probe + 1 per branch commit (`policy_lint.mjs` `redHistoryForHead`) |
| env-matrix | `governance.yml` | `secrets.GITHUB_TOKEN` | the default lint's ruleset reads (`counts.mjs`: branch rules + each ruleset) per built shape |
| validate-hacs | `validate.yml` | `hacs/action`'s default, `github.token` | the action's own repository reads |
| rerun-stale-contract | `pr-contract-rerun.yml` | `github.token` | 1 per watched-workflow completion; on a red head `contract_rerun.py` adds 1 + up to 30 polls + 1 POST |

App installation tokens are minted only in `nightly.yml` (ledger-, record- and
approver-writer) and `merge-main.yml` (the run approver), and seats' own `gh`
calls carry the hpo-author App's token: separate buckets. `GITHUB_TOKEN` is an
installation token of the GitHub Actions App, so its exhaustion reads
"for installation" exactly as an App's does; its limit is **1,000 requests per
hour per repository**, shared by every job of every workflow (GitHub's
documented limit for `GITHUB_TOKEN`). The brief's 5,000/hr is the limit of a
different bucket, and so is HANDOVER item 44's "shared App quota".
Not measured here: the `x-ratelimit-limit` header itself. `gh api rate_limit`
is not counted against the limit; the countermeasure's first step prints it
(section 4, M0), which settles the number on the first run.

### 1.2 The consumer is Governance's `record` job, on every push to main

`governance.yml` `record` runs on `push` to main (its `if:` excludes only
`pull_request` and `merge_group`) and runs three `policy_lint.mjs` modes over
`<last v* tag>..origin/main`, each walking that window through `ghGet` (curl
with `GITHUB_TOKEN`), each from scratch:

- `--record`: `fetchPullsBySha`, one `/commits/<sha>/pulls` per first-parent commit (W);
- `--stats`: the same W, then `fetchWindow`, three reads per merged PR (P): `pulls/N`, `issues/N/comments`, `pulls/N/reviews`;
- `--sunset`: the same W + 3P again.

So one push costs `3W + 6P`. **Measured** with
`dev/audit/harnesses/record_api_calls.sh` (a logging stub `curl` on PATH, no
request leaves the host):

```
$ bash dev/audit/harnesses/record_api_calls.sh            # v7.0.2..origin/main
--record 94 call(s) over v7.0.2..origin/main
--stats 370 call(s) over v7.0.2..origin/main
--sunset 370 call(s) over v7.0.2..origin/main
TOTAL 834 call(s) per push to main, before policy-docs, env-matrix and the other jobs
$ bash dev/audit/harnesses/record_api_calls.sh origin/main  # null control: empty window
TOTAL 0 call(s) per push to main, ...
```

The live job agrees: run `39755501453` (push `c409c9b18`, 09:27Z), job
`119746351603`, printed `RECORD_ENUM: api` and `RECORD: 91 merged pull
request(s) in v7.0.2..origin/main` (W=93, so `3W+6P` = 825), and its step times
fit one sequential read every ~0.42 s: `--record` 44 s, `--stats` 153 s,
`--sunset` 155 s. **One push to main spends 83 % of the repository's hourly
`GITHUB_TOKEN` bucket**, and every later push in the same hour overdraws it.

### 1.3 The trigger: merge bursts against a window that only grows

The window resets only at a stamp, so the per-push cost rises with every merge
until the next tag. Pushes to main on 2026-10-22 (UTC, `git log --first-parent`),
with `3W+6P` at each from `git rev-list`:

| burst | pushes | per push | record-job demand | red |
|---|---|---|---|---|
| 06:07–06:11 | 5 (#2588, #2545, #2582, #2558, #2554) | 696–732 | ≈ 3,570 | ≈ 06:27Z |
| 08:03–08:09, 08:38 | 6 (#2577, #2591, #2585, #2596, #2598, #2578) | 744–789 | ≈ 4,600 | ≈ 08:40Z |
| 09:03–09:26 | 4 (#2600, #2599, #2601, #2602) | 798–825 | ≈ 3,250 | ≈ 09:44Z |

Each red follows a burst in the same hour, and each burst's record jobs alone
demand 3.2–4.6× the bucket (demand: once the bucket is dry the job's own reads
fail too, and Governance's push runs at `01cf1398a`, `8a4c438e7` and `04c1dd779`
concluded `failure`; their failing step was not read here). Everything else is small beside it: a PR head costs
pr-contract roughly 4 + its commit count, arch-score 1–2, the follower 1–2 per
watched-workflow completion (8 workflows per head), env-matrix a few per shape —
tens per head, against ~800 per main push. The candidates the brief named
(recarry re-runs, the follower's fan-out, pr-contract's reads, validate-hacs,
arch-score) are multipliers of the tens, not of the hundreds; they are where
the bucket was found empty, not what emptied it. The 20 cancelled follower runs
at `c409c9b18` are R10-FOLLOWER-DEBOUNCE's concurrency group working: each made
at most its one list read.

### 1.4 Which side moved

`git log` on the job: `31bcabac1` (#634, 2026-09-09) added the record job and
its three modes with a window of 38 first-parent commits (`v6.3.18..31bcabac1`)
and two reads per PR. `9eaa284c9` (2026-09-23, #1471) added the reviews
endpoint, the third per-PR read, in both `--stats` and `--sunset`. The tag
cadence then slowed from about daily (v6.7.9–v6.7.16, 2026-09-28 to 10-04) to
windows of 104 (`v6.7.17..v7.0.0`) and 188 (`v7.0.0..v7.0.1`) commits; at 188 a
single push is ≈ 1,680 calls by the measured formula, over the bucket on its
own. Main's merge rate reached 53 pushes on 2026-10-21. The job did not change;
its window, its per-PR read count and the merge rate did.

## 2. Process state: (c)

The class already had a process, and it ran. HANDOVER item 44 (`8556f7d0b`,
2026-10-14) recorded "App-quota 403s arrive disguised as red lanes" with a
recovery (recarry); R10-FOLLOWER-DEBOUNCE (tvofi, 2026-10-19; merged
`f210e78b5`) diagnosed the same reds — "drains the Actions installation API
quota (GitHubRatelimitException in validate-hacs, arch-score, env-matrix)" — and
debounced the follower. Both were followed and both were wrong in the direction
that mattered. **The unit was runs, not calls**: the follower was picked because
it was "435 of the first 1000 listed runs", and a run that makes one read
outnumbered a run that makes 834. The record job, 4 runs an hour, was invisible
to that count. The follower brief asked for "the call count per head measured
before and after" — per PR head, which is where the record job is not.

Not (a): a diagnosis and a countermeasure existed. Not (b): both were carried out
as written. Not (d) as the state of record: the record job's preconditions
(window, reads per PR, merge rate) did change underneath it (section 1.4), but
the process that owed the catch was this class's own diagnosis, and it ran over
those changed preconditions and named the wrong consumer. The countermeasure
therefore changes the unit (calls, per job, on the bucket that went dry), not
the instruction.

## 3. How far the class reaches

Searched for every `GITHUB_TOKEN` reader whose call count scales with something
other than one PR head:

- `governance.yml` `record` — O(window), section 1.2. The one large consumer.
- `tests.yml` `nightly-status` and `ci-ratchet` read fixed-size listings
  (`per_page=8`); `delivery-status-publish` reads one issue. Constant.
- `pr-contract`'s red-history walk is O(branch commits), one read per commit; a
  long-lived branch with many merge-from-main commits costs proportionally, and
  `body`/`author` read the same `pulls/N` twice (one read would serve both).
  Small, but the same shape at PR scale.
- `contract_rerun.py` polls up to 30 times on a red head. Bounded.
- The same three `policy_lint.mjs` modes run under seat tokens in local tools;
  a seat's own bucket, not CI's.

No other O(window) reader found.

## 4. Cost test

`cost(countermeasure, recurring) < cost(defect) x P(recurrence)`, per release
cycle, in wall-clock.

- **P(recurrence), measured.** 3 instances on 2026-10-22 (3 of the day's 3
  bursts); HANDOVER 44 and R10-FOLLOWER-DEBOUNCE record the same class on
  2026-10-14 and 2026-10-19. With one push at 834 calls the bucket is overdrawn
  by any hour holding two pushes to main, which today was 6 of the 10 hours from
  00Z to 10Z (01, 02, 04, 06, 08, 09). A red needs a second condition: a
  required check reading while the bucket is dry, so the quiet-PR hours (01Z to
  04Z) show none and the three busy ones show one each. P per busy hour with
  two or more pushes is therefore high, not 1; the measured rate, 3 a day, is
  the figure used. W grows until the next stamp, so the rate does not fall on
  its own.
- **cost(defect).** At least 1 h of merge-train wall-clock per instance (the
  brief), so ≥ 3 h on 2026-10-22, plus the seat time of diagnosing a red that is
  not the head's.
- **cost(countermeasure, recurring).** Below, per option; each is zero or
  negative standing cost.

### The countermeasure, in order of cost

- **M0 — measure the unit (addresses state (c)).** The record job prints
  `gh api rate_limit --jq .resources.core` before its first and after its last
  step: two reads that are not counted against the limit, < 1 s. It turns "a
  run" into "N calls of L" in the log, settles the limit (section 1.1), and lets
  the next diagnosis rank consumers by calls. A log line, not a gate, so the
  detector demonstration does not apply to it.
- **M1 — one window walk, not three (cuts per push 834 → 370).** `--record`,
  `--stats` and `--sunset` read the same `/commits/<sha>/pulls` and the same
  per-PR objects. Fetch once, in the first mode, into a file under
  `$RUNNER_TEMP`, and have the other two read it (a `--window-cache` argument to
  `policy_lint.mjs`). Standing cost negative: the job loses about 2.6 min of
  sequential reads per push. Demonstration: `record_api_calls.sh` reads 834 at
  this head and must read ≤ 370 with the fix (W + 3P = 94 + 276); its null
  control reads 0. Mutation: re-enable the per-mode fetch and the total returns
  to 834.
- **M2 — one record run per burst.** A job-level concurrency group on `record`
  for `push` (fixed group, `cancel-in-progress: false`): GitHub keeps one
  running and one pending, and drops the superseded pending runs. A burst of 5
  pushes runs it twice. Standing cost 0; a burst's report lands up to one job
  length (≈ 6 min) later. The job is not a required context, so nothing waits on
  it. Not alone sufficient: today's 08Z hour would still run it 3 times.
- **M3 — take the O(window) reader off the shared bucket.** Mint the record
  job's token from an App installation (`nightly.yml` already mints the
  record-writer's), so the required checks never share a bucket with a job whose
  cost scales with the release window. Standing cost one mint step (≈ 2 s). It
  changes which identity the job reads and files issues as (decision 0011), so
  it is the owner's decision; the record job's `issues: write` grant was the
  owner's (#201 comment 5670207248).

With M1 + M2, today's worst hour costs 3 × 370 ≈ 1,110 from the record job:
still over 1,000. **Recommended: M0 + M1 + M2, and M3** — M1 and M2 are the
cheap part and halve the load, M3 is the part that removes the coupling, and
without it the class returns as the window grows (M1's 370 is itself
O(window): `W + 3P` crosses 1,000 at about W = 250, one slow release). The
alternative to M3 that changes no identity — `--stats` and `--sunset` off the
push arm, onto the existing weekly schedule and dispatch — changes the friction
filer's cadence (#959 option B), which is also the owner's call.

**Verdict: the countermeasure pays for itself.** Its standing cost is ≤ 0 s per
run for M0–M2 and ≈ 2 s per push for M3, against ≥ 1 h of train wall-clock per
instance at a measured three instances a day.

**Retry with backoff is not the countermeasure.** R10-FLY-GH-READ-RETRY (#2589)
retries transient reads in `app_approve.sh`; a 403 on an exhausted hourly bucket
is not transient, and retrying it from every required check adds calls to the
bucket that is empty. Where a retry meets this class it should stop at the
reset time the 403 names, never loop.

## 5. Owner

No live group in `dev/programme/rosters/wave-r10-groups.json` owns
`governance.yml`'s record job: R10-FOLLOWER-DEBOUNCE is done and owns the
follower; R10-CI-LAYOUT-P2 is `tests.yml`; R10-FLY-GH-READ-RETRY is
`app_approve.sh`. **Proposed new group: `R10-RECORD-API-BUDGET`** (lane IN,
kind instrument, size S, priority high: it sits on every merge), carrying M0, M1
and M2 in one pull request (`.github/workflows/governance.yml`,
`tools/policy/policy_lint.mjs`), and M3 or the cadence alternative as a separate
owner decision before any code. Code-owned paths: the owner reviews.
Until the orchestrator registers it, the carry is held by R10-CI-LAYOUT-P2, the
only live group that already lists `governance.yml`; that group's brief should
also correct HANDOVER item 44's "shared App quota" to the `GITHUB_TOKEN` bucket.
