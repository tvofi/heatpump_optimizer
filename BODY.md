R10-FLY-GH-READ-RETRY, PR 1 of 2: `tools/pr/app_approve.sh`'s GitHub reads retry with a bounded backoff, and only on failures that a later read can ride out.

Train 8 stopped at 21:50:38Z on `app_approve: REFUSE: could not read pull request #2547`, after a 2667 s CI wait. That was one `gh api` call with no retry, and its stderr was not kept, so nothing recorded what kind of failure it was. The roster brief counts this as the third instance of the class "one unretried GitHub read kills an instrument".

What changes, in `tools/pr/app_approve.sh`:

- **`gh_read <var> <gh api args...>`** is the one entry for the four reads:
  - the pull request, read twice by `check_pr`: before the mint and again before the POST;
  - the comments (`--paginate`);
  - `.github/CODEOWNERS` at `ref=main`;
  - the changed files (`--paginate`).

  It sets `<var>` to the answer. On a refusal it returns 1 and leaves gh's stderr in `GH_ERR`. Every `die` at those four sites now names that error.
- **`gh_transient <stderr>`** classifies a failure from gh's own stderr format: `gh: <message> (HTTP NNN)`, or `gh: HTTP NNN` when the body has no message. These are retried:
  - 5xx;
  - 429;
  - a 403 whose message names the `secondary rate limit`;
  - a transport error, which carries no status: Go's `Get "https://...": <err>` (the shape merge_train's own stop logged), or gh's `error connecting to`.

  Everything else refuses after its one call, as it did before: 401, a permission 403, 404, 422, any other status, or a stderr that matches no rule.
- **The budget is `app_push.sh`'s read-back rule.** That is 4 reads, settling `READ_SLEEP * 3^(n-1)` between them, so 5/15/45 s. Each settle prints `app_approve: read n/4 of <path>: <error>; sleeping Ns` on stderr. A spent budget refuses with the last error and `(after 4 attempts)`.
- **A wrong answer is never retried.** A read that completes but answers wrong (head moved, closed, no verdict, an owned path) is judged by the callers after `gh_read` returns 0, so it never enters the loop.
- **Writes are never retried.** The token mint, the review POST and the revoke stay on single `curl` calls.
- **The python parse of the comments** keeps its own refusal, reworded to `could not parse the comments`. A parse failure is no longer reported as a read failure.
- **`tools/audit/seat/INSTRUMENTS.md`**: the `app_approve.sh` entry states the rule in one sentence.

Round 2 clears the review of `e4b3e01a` (blocked: `mutant-survives`, `root-cause-unanswered`):

- **The budget is pinned.** The spent-budget arm `rspent` used to queue `gh: Service Unavailable (HTTP 503) the-last-one` as its fourth line. That line is unclassified, not transient, so it refused in the budget's place, and the reviewer's R1 (budget 5) and R11 (`[ "$_try" -ge 999 ]`) both passed. The arm now queues five transient lines (500, transport, `gh: HTTP 502`, `gh: Service Unavailable (HTTP 503)`, `gh: Gateway Timeout (HTTP 504)`). It asserts all of these:
  - 4 calls;
  - the fifth line is still unread;
  - the refusal names the fourth line, anchored at `(after 4 attempts)$`;
  - the stderr file is gone.

  So only the budget can stop it, and a fifth read takes the 504 and then an answer and is approved.
- **The class rule, a census over every fixture line.** Each retry and refusal arm queues its stderr lines through `queue <case> <read> <class> <line>...`, which also records the class that arm needs. The census sends every recorded line through the production `gh_transient` and fails on any line whose class differs. It also asserts its own preconditions:
  - it covers every `fail-*` file an arm made;
  - it holds both classes.

  The review's shape, a retry arm stopped by a line it did not mean, is what it refuses.
- **The class rule, a sweep over every one-line mutant of the retry region.** `dev/audit/harnesses/r10_gh_read_retry_mutants.py` covers the region from `READ_TRIES=` to `gh_read`'s closing `}`. It generates mutants by rule, not by hand:
  - `num`: each integer literal to n-1, n+1 and 999;
  - `rel`: each test operator to the other five;
  - `opnd`: each `"$var"` operand to 999 (R11 is this rule's);
  - `or`: `||` and `&&` swapped;
  - `not`: `if !` to `if`;
  - `ret`: a bare `return` to `return 0` or `return 1`;
  - `del`: each non-structural line deleted.

  It runs the self-test against each mutant. A survivor reads EQUIVALENT only under a listed reason, and a listed reason that no rule generates any more refuses the run. So a bound, budget or classification branch added to the region is swept the day it lands.
- **The branches the sweep found unpinned at `e4b3e01a`** each gained an arm:
  - `rempty`: an empty stderr refuses after 1 call, saying `gh failed with nothing on stderr`;
  - `rmktemp`: an uncreatable stderr file refuses with no `gh` call;
  - `r404`'s message is anchored, so a one-call refusal carries no attempt count;
  - `r404` and `rspent` assert the stderr file is removed.
- **`tests/closures.json`**: `ci_predict.py --apply-inert` added the harness to `tests/harness_headers.py`'s INERT READS. CI's Linux recording would otherwise merge that entry as a bot commit on the reviewed head.

Alternatives, and why each lost (fixer.md step 17):

- **Factor a shared helper with `app_push.sh`.** `app_push.sh`'s reads go through `curl -f`, which reports every HTTP status of 400 and over as exit 22. Its classifier works on a different signal, so it cannot classify a 404 apart from a 500. What could be shared is the six-line settle loop. Sharing it needs a new sourced file, which needs a `tests/closure.py` classification, and an edit to `app_push.sh`. Both are outside this PR's scope. PR 2's python callers could not source bash anyway.

  The rule is shared instead: the same budget and schedule, stated in both scripts and in `INSTRUMENTS.md`.
- **Retry on any non-zero exit.** That would retry a 404 and a 401, so a real refusal would read as slow success. The sweep's `?*) return 1` -> `return 0` mutant shows the self-test refuses it.
- **Honour `Retry-After`.** `gh api` puts response headers only on stdout, and only under `--include`, which mixes them into the paginated JSON this script parses. The house 65 s budget is used instead (see Forward-carry).
- **Kill the budget mutants with a fixed list of hand-picked mutants** (the round-1 mutation proof). Lost because a hand-picked list missed exactly the budget branch. The rule-generated sweep re-derives the list from the code.

Architecture score: `score.py --diff` prints `dS +0.0000 NULL`. No ratchet row moves and no budget is raised.

🤖 Generated with [Claude Code](https://claude.com/claude-code)

https://claude.ai/code/session_01Rm9bzxRPiA8mnUCoYC8Uog

## Head

`1063eb3a4ef69f924932b4159a67fd55dbb37c1a`. The branch's commits:

- `d42bda80f0477a72f41cc1588352b4f48e7ff046`: the retry.
- `e4b3e01abb48644841202e7d7b0ae93107258bd3`: the delivery row.
- `f84fa6b2e`: merge of `origin/main` at `93e6a63d2855651448a2b8f677b392feddc03c99`. `origin/main`'s tip and the merge base, measured 2026-10-22T02:16:49Z.
- `0f2fa660b07f9a4e039abb6e8cb38de06f53bdaf`: the budget pin, the census, the new arms and the sweep harness.
- `1063eb3a4ef69f924932b4159a67fd55dbb37c1a`: the INERT READS entry.

Every figure below was taken at `1063eb3a`. The two sweeps ran at tree `af8cb9ba` (`0f2fa660`'s tree, which `1063eb3a` changes only in `tests/closures.json`) and at `f84fa6b2e`.

## Mutation proof

**The sweep at both ends.** The command is `python3 dev/audit/harnesses/r10_gh_read_retry_mutants.py`, with the same harness and therefore the same 89 rule-generated mutants at each end:

| tree | self-test | killed | equivalent | survivors | rc |
|---|---|---|---|---|---|
| `f84fa6b2e` (round 1's tests, main merged) | 206 checks | 68 | 11 | 10 | 1 |
| `0f2fa660` (this round) | 218 checks | 78 | 11 | 0 | 0 |

The 10 survivors at `f84fa6b2e`, each killed at `0f2fa660`:

| mutant | line | rule | killed by, at `0f2fa660` |
|---|---|---|---|
| M54 (the review's R1) | `[ "$_try" -ge "$READ_TRIES" ]` | `rel -ge->-gt` | `after exactly 4 calls` |
| M60 (the review's R11) | `[ "$_try" -ge "$READ_TRIES" ]` | `opnd "$READ_TRIES"->999` | `REFUSE: four transient failures spend the budget` |
| M42 | mktemp's `return 1` | `num 1->0` | `rmktemp`: `naming that, not a parse of an empty answer` |
| M53 | `[ -n "$GH_ERR" ] \|\| GH_ERR="gh failed with nothing on stderr"` | `del` | `rempty`: `saying gh left no error` |
| M64 | the refusal's `rm -f "$_ef"` | `del` | `and the read's stderr file is gone` |
| M65, M66, M67 | `[ "$_try" -eq 1 ]` | `num 1->0/2/999` | `naming the error gh gave, with no attempt count after one call` |
| M71 | `[ "$_try" -eq 1 ]` | `rel -eq->-lt` | the same |
| M73 | `[ "$_try" -eq 1 ]` | `opnd "$_try"->999` | the same |

Each of the 11 equivalents carries its reason in the harness's `EQUIVALENT` table:

- six are `return 1` to `return 2` or `999`, which no caller can tell apart: every caller tests zero against non-zero only;
- `-ge` to `-eq` on the budget: `_try` steps by 1 from 1;
- `-eq 1` to `-le 1`: `_try` is never below 1;
- deleting `GH_ERR=""`, or `local code`: neither has another reader;
- deleting `?*) return 1`: a status line falls through to the transport grep, which it cannot match.

**The census's mutant** (null control for the census). In a scratch worktree of `0f2fa660`, I put the review's line `gh: Service Unavailable (HTTP 503) the-last-one` back as `rspent`'s fourth line. Result: `218 checks, 2 failed`, rc=1. The failures:

- `FAIL every queued stderr line classifies as its arm needs (production gh_transient)`, printing `census: rspent/fail-pulls line 'gh: Service Unavailable (HTTP 503) the-last-one' classifies refuse, its arm needs transient`;
- `FAIL naming the last error`.

**Round 1's named mutants** (the brief's three) are the sweep's rows:

- removing the retry: `not` and `or` on the `if ! gh_transient` line;
- retrying on 404: `?*) return 1` -> `return 0`;
- retrying a write: the POST arm `post502`, which asserts 1 POST and no settle.

Each is KILLED at `0f2fa660`.

## Null control

All runs are `bash tools/pr/app_approve.sh --self-test`:

| tree | result | rc |
|---|---|---|
| `f84fa6b2e` | `206 checks, 0 failed` | 0 |
| `1063eb3a` | `218 checks, 0 failed` | 0 |
| `0f2fa660` with the review's fourth line planted | `218 checks, 2 failed` | 1 |

**The finder's harness at both ends** is the group brief's null control (5): the self-test arms, read through the sweep.

- At `f84fa6b2e`, "a stub failing 4 times refuses after the budget, naming the last error" is vacuous: the budget mutants M54 and M60 survive.
- At `0f2fa660` both are killed.

The brief's controls at the head:

- **One transient failure, then an answer, approves.** The comments read makes exactly 2 calls. The pull-request read makes 3, because the pre-POST re-read is the third. The 429 and secondary-403 arms make 2.
- **No retry on a refusal.** A 404, a permission 403, a 401, a 422 or an empty stderr refuses `after exactly 1 call` with no `sleep`. A readable wrong head (`moved`) refuses after 1 read of the pull request, and a readable answer with no verdict (`none`) refuses after 1 comments read.
- **Four transient failures spend the budget** (`rspent`). Five transient lines are queued, and the read stops after exactly 4 calls with sleeps `sleep 5 sleep 15 sleep 45`. The fifth line is still queued. The refusal names the fourth line, `gh: Service Unavailable (HTTP 503) (after 4 attempts)`.
- **The budget's last read can still succeed** (`rlast`). Three transient failures and an answer on the fourth read approve.

The `sleep` the tool calls is a logging stub on the self-test's PATH, so the schedule is read off the log and costs no time.

## Figures

- **The self-test's check count** is the number of `st` assertions executed: `bash tools/pr/app_approve.sh --self-test`, at both ends (see Null control).
- **The sweep's counts** come from `python3 dev/audit/harnesses/r10_gh_read_retry_mutants.py`. The mutant total is the number of rule applications its header lists over the region. Its own null control is M0, the unmutated tree: `NULL-OK` at both ends.
- **The scoped gate** is `python3 tests/closure.py select --diff $(git merge-base origin/main HEAD) --workdir "$D"`. It prints `MODE: SCOPED -- 1 script(s) run, 32 scoped out`, and `scope.run` names `tests/entities.py`. The run comes from `tests/closures.json`'s new entry; the rest of the diff is in no measured closure.
- **`tests/entities.py`** and the `run_always` lines are run with `PYTHONPATH=tests/hastub` under `/opt/hpo/venv-ci`, each rc=0:
  - `python3 tests/entities.py`: `ALL 2382 ENTITY CHECKS PASSED`
  - `python3 tests/closure.py selftest`
  - `python3 tests/layout.py`
  - `python3 tests/harness_headers.py`: `ALL 109 HARNESS HEADER CHECKS PASSED`
  - `python3 tests/env_drift.py --claims-only <merge base>`
- **CI also runs the self-test**, in `governance.yml`'s `instrument-self-tests` job (`app_approve.sh --self-test`).
- `python3 tests/structure.py`: `STRUCTURE RATCHET PASSED`, rc=0.
- `node tools/policy/policy_lint.mjs --budgets`: rc=0.
- `python3 tools/audit/archscore/score.py --diff <merge base> HEAD`: `Architecture score: dS +0.0000 NULL`.
- `PYTHONPATH=tests/hastub python3 tools/pr/ci_predict.py --base origin/main`:
  - at `0f2fa660` it predicted 1 red, the INERT READS entry, which `--apply-inert` wrote;
  - at `1063eb3a` it prints `CI PREDICT: no closures or fast red predicted against 93e6a63d2855`.
- `python3 -I tools/audit/seat/tmp_paths.py --check`: `0 refused`.
- **The class's seams in this file.** Two rules enumerate them.
  - The GitHub calls outside the self-test:

    `awk '/^# --self-test: .gh./{exit} /(gh api|gh_read [a-z]|curl -|git fetch)/ && !/^ *#/' tools/pr/app_approve.sh`

    It returns 10 lines; each is dispositioned below.
  - The branches inside the retry path: the sweep above, whose survivors are 0 and whose 11 equivalents are each reasoned in the harness.

  | seam | what it is | disposition |
  |---|---|---|
  | `gh api` inside `gh_read` | the retry loop itself | this diff; every branch swept |
  | `gh_read js` in `check_pr` | the pull request, called twice | closed in this diff |
  | `gh_read comments` | the comments | closed in this diff |
  | `gh_read owners` | CODEOWNERS at `ref=main` | closed in this diff |
  | `gh_read files` | the changed files | closed in this diff |
  | `curl -X DELETE .../installation/token` | a write | never retried; it already only warns on failure |
  | `curl -X POST .../access_tokens` | the mint | a write, never retried |
  | `curl -X POST .../reviews` | the review | a write, never retried; `post502` pins it |
  | `curl .../repos/$repo/installation` | a JWT read | a distinct seam, carried below |
  | `git fetch ... refs/pull/$pr/head` | the carry path's git read | a distinct seam, carried below |

## Red checks

From the check-runs API, per commit:

- **`d42bda80`**: `nightly-status` failed and `pr-contract` failed. The rest of that run was cancelled by the push of `e4b3e01a`.
- **`e4b3e01a`**: `nightly-status` failed, and `pr-contract` failed in both of its runs (jobs 119527655690 and 119538432191). `ci-ratchet` was skipped.

The commits after `e4b3e01a` are on `handoff/r10-fly-gh-read-retry`, not on the pull request, so CI has not run on them.

- **`pr-contract`** fails with `BAD-DEST body item 0e5922c7: R10-FLY-GH-READ-RETRY: R10-FLY-GH-READ-RETRY is not a group of the roster`.
  - The cause: CI runs `carry_audit.py check` with no `--roster-ref`, so it reads `main`'s roster. This fly-in group is registered only on `handoff/audit-r10-roster`.
  - `python3 tools/audit/carry_audit.py --roster-ref origin/handoff/audit-r10-roster check --body <body>` routes this body with 0 bad destinations.
  - The cheaper detector is running that same command without `--roster-ref`. It costs about a second, and it reports the bad destination before a push. The round-1 body was checked only against the handoff roster.
  - The red is not this diff's. Routing the carry anywhere else would misroute it, so the check stays red on this body until the roster that registers the group merges to `main`.
  - Carry destinations that only the round's roster knows are R10-FLOW-ROSTER-FREEZE's part (b), which names #2529, #2547 and #2561 blocked the same way. Carry: R10-FLOW-ROSTER-FREEZE
- **`nightly-status`** grades `main`'s nightly lanes, not this branch. Its log names `mutation-nightly` and `slow` failing on `main`'s scheduled run 39563978649. This diff reaches neither lane. Carry: dismissed: grades main's nightly lanes, not this branch

## Forward-carry

- The JWT-authenticated `curl` GET of `/repos/$repo/installation`, and the carry path's `git fetch` of `refs/pull/$pr/head`, are GitHub reads of the same class. They are left single-shot here:
  - the brief scopes this PR to the four `gh` reads;
  - `curl -f` gives exit 22 for every HTTP status of 400 and over, so classifying it needs its own `-w '%{http_code}'` read.

  They go to PR 2 of this group, beside `merge_train.py`'s and `record_row.py`'s reads. Carry: R10-FLY-GH-READ-RETRY
- **PR 2 and PR 3 of this group owe the same proof.** That means:
  - a spent-budget fixture whose queued failures are all transient, with one more queued than the budget, so only the budget stops it;
  - a census sending every fixture line through the production classifier;
  - a rule-generated sweep of their retry loops.

  Without those, a hand-picked mutant list reads a vacuous budget pin as green, which is what this PR's round 1 did. Carry: R10-FLY-GH-READ-RETRY
- The roster brief asks for `Retry-After` to be honoured. `gh api` exposes response headers only on stdout, under `--include`, which mixes them into the paginated JSON this script parses. The fixed 5/15/45 s budget stands, as `app_push.sh`'s does. Carry: dismissed: gh exposes no Retry-After header without mixing headers into paginated stdout

## Friction

none
