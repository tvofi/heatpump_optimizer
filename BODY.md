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

Alternatives, and why each lost (fixer.md step 17):

- **Factor a shared helper with `app_push.sh`.** `app_push.sh`'s reads go through `curl -f`, which reports every HTTP status of 400 and over as exit 22. Its classifier works on a different signal, so it cannot classify a 404 apart from a 500. What could be shared is the six-line settle loop. Sharing it needs a new sourced file, which needs a `tests/closure.py` classification, and an edit to `app_push.sh`. Both are outside this PR's scope. PR 2's python callers could not source bash anyway.

  The rule is shared instead: the same budget and schedule, stated in both scripts and in `INSTRUMENTS.md`.
- **Retry on any non-zero exit.** That would retry a 404 and a 401, so a real refusal would read as slow success. Mutant M2 below shows the self-test refuses it.
- **Honour `Retry-After`.** `gh api` puts response headers only on stdout, and only under `--include`, which mixes them into the paginated JSON this script parses. The house 65 s budget is used instead (see Forward-carry).

Architecture score: `score.py --diff` prints `dS +0.0000 NULL`. No ratchet row moves and no budget is raised.

🤖 Generated with [Claude Code](https://claude.com/claude-code)

https://claude.ai/code/session_016kyKyAkBA2MTwStBDQU4Xh

## Head

`d42bda80f0477a72f41cc1588352b4f48e7ff046`, cut from `origin/main` at `5a755f53efda8c099af7d6a98fb0b22828a0593c`. That is the merge base, and `origin/main`'s tip when measured on 2026-10-21.

## Mutation proof

How the mutants were run:

- Each mutant replaces one production line of `tools/pr/app_approve.sh` and runs `bash tools/pr/app_approve.sh --self-test`. The file is then restored, which `git diff --quiet` confirms.
- The runner is a one-off scratch script that string-replaces the line.
- Every mutant exits rc=1.

| mutant | the line changed | FAIL count | checks that went red (abridged) |
|---|---|---|---|
| M0 null | none | 0 | - |
| M1 remove the retry | `if ! gh_transient ... \|\|` -> `if true \|\|` | 15 | `train 8's shape: a 502 on the pull-request read, then an answer, is approved`; `a transport error on the comments read, then an answer, is approved`; `a 429 on the CODEOWNERS read ...`; `a secondary-rate-limit 403 on the files read ...`; `settling 5/15/45 s between them` |
| M2 retry on 404 (every other status) | `?*) return 1` -> `?*) return 0` | 9 | `REFUSE: a 404 on the pull-request read`; `after exactly 1 call: no retry masks a refusal`; `REFUSE: a 401 on the comments read`; `REFUSE: a 422 on the CODEOWNERS read` |
| M3 retry the review POST | the POST's `\|\| die` -> `\|\| { sleep 5; resp=$(curl ...POST...); } \|\| die` | 3 | `the refused POST was sent exactly once`; `after exactly 1 POST`; `and no settle` |
| M4 retry every 403 | the 403 arm -> `403) return 0` | 2 | `REFUSE: a permission 403 on the files read`; `after exactly 1 call` |
| M5 no transport class | the transport `grep -qE` -> `'^NEVER$'` | 5 | `a transport error on the comments read, then an answer, is approved`; `after exactly 4 calls` |
| M6 flat backoff | `_delay=$((_delay * 3))` -> `_delay=$_delay` | 1 | `settling 5/15/45 s between them` |
| M7 last error dropped | `check_pr`'s `die "...: $GH_ERR"` -> without it | 2 | `naming the error gh gave`; `naming the last error` |
| M8 budget off by one | `-ge "$READ_TRIES"` -> `-ge "$((READ_TRIES - 1))"` | 5 | `three transient failures and an answer on the fourth read, the budget's last, are approved` |

The brief names three mutants: removing the retry (M1), retrying on 404 (M2) and retrying a write (M3). Each turns a check red.

## Null control

All runs are `bash tools/pr/app_approve.sh --self-test`:

| tree | result | rc |
|---|---|---|
| unmodified tree at the merge base `5a755f53` | `171 checks, 0 failed` | 0 |
| new self-test arms on the base script, the failing test first | `206 checks, 16 failed` | 1 |
| head `d42bda80` | `206 checks, 0 failed` | 0 |

The 16 failures on the base script are every retry arm. They include `FAIL train 8's shape: a 502 on the pull-request read, then an answer, is approved (got '1', want '0')`.

The brief's three null controls are self-test cases at the head:

- **(a)** One transient failure, then an answer, approves.
  - Comments read: `with exactly 2 calls to that read`.
  - Pull-request read: 3 calls, because the pre-POST re-read is the third.
  - Same for the 429 and secondary-403 arms.
- **(b)** A 404, a permission 403, a 401 or a 422 refuses `after exactly 1 call` with no `sleep`. A readable wrong head (`moved`) refuses after 1 read of the pull request. A readable answer with no verdict (`none`) refuses after 1 comments read.
- **(c)** Four transient failures refuse:
  - `after exactly 4 calls`;
  - with the logged sleeps `sleep 5 sleep 15 sleep 45`;
  - naming the last error, `gh: Service Unavailable (HTTP 503) the-last-one (after 4 attempts)`.

  Before the budget's last read, a fourth read that answers approves. This is the off-by-one control M8 kills.

The `sleep` the tool calls is a logging stub on the self-test's PATH, so the schedule is read off the log and costs no time.

## Figures

- The self-test's check count and the arms that fail before the fix: `bash tools/pr/app_approve.sh --self-test`, run at both ends (see Null control). The count is the number of `st` assertions executed.
- The scoped gate: `python3 tests/closure.py select --diff $(git merge-base origin/main HEAD) --workdir "$D"` printed `MODE: SCOPED -- 0 script(s) run, 33 scoped out`. Neither changed file is in a measured closure.
  - The `run_always` lines run here and pass, each with rc=0: `python3 tests/closure.py selftest`, `python3 tests/layout.py`, `python3 tests/harness_headers.py` under the CI venv, and `python3 tests/env_drift.py --claims-only <merge base>`.
  - `governance.yml`'s `instrument-self-tests` job runs `app_approve.sh --self-test` in CI.
- `python3 tests/structure.py`: `STRUCTURE RATCHET PASSED`, rc=0.
- `node tools/policy/policy_lint.mjs --budgets`: rc=0.
- `python3 tools/audit/archscore/score.py --diff <merge base> HEAD`: `Architecture score: dS +0.0000 NULL`.
- `PYTHONPATH=tests/hastub python3 tools/pr/ci_predict.py --base origin/main`: `CI PREDICT: no closures or fast red predicted against 5a755f53efda`.
- **The class's seams in this file.** The rule is every GitHub call outside the self-test:

  `awk '/^# --self-test: .gh./{exit} /(gh api|gh_read [a-z]|curl -|git fetch)/ && !/^ *#/' tools/pr/app_approve.sh`

  It returns 10 lines; each is dispositioned below.

  | seam | what it is | disposition |
  |---|---|---|
  | `gh api` inside `gh_read` | the retry loop itself | this diff |
  | `gh_read js` in `check_pr` | the pull request, called twice | closed in this diff |
  | `gh_read comments` | the comments | closed in this diff |
  | `gh_read owners` | CODEOWNERS at `ref=main` | closed in this diff |
  | `gh_read files` | the changed files | closed in this diff |
  | `curl -X DELETE .../installation/token` | a write | never retried; it already only warns on failure |
  | `curl -X POST .../access_tokens` | the mint | a write, never retried |
  | `curl -X POST .../reviews` | the review | a write, never retried; M3 pins it |
  | `curl .../repos/$repo/installation` | a JWT read | a distinct seam, carried below |
  | `git fetch ... refs/pull/$pr/head` | the carry path's git read | a distinct seam, carried below |

## Red checks

- **`nightly-status`** grades `main`, not this branch. It reports `main`'s state at the time it ran, so it is no red this diff caused. Carry: dismissed: grades main, not this branch
- **`main`'s `ci-ratchet` red** is runner-speed variance on `main`, owned by R10-CI-LAYOUT. This diff touches no script that `ci-ratchet` times. Carry: R10-CI-LAYOUT

## Forward-carry

- The JWT-authenticated `curl` GET of `/repos/$repo/installation`, and the carry path's `git fetch` of `refs/pull/$pr/head`, are GitHub reads of the same class. They are left single-shot here:
  - the brief scopes this PR to the four `gh` reads;
  - `curl -f` gives exit 22 for every HTTP status of 400 and over, so classifying it needs its own `-w '%{http_code}'` read.

  They go to PR 2 of this group, beside `merge_train.py`'s and `record_row.py`'s reads. Carry: R10-FLY-GH-READ-RETRY
- The roster brief asks for `Retry-After` to be honoured. `gh api` exposes response headers only on stdout, under `--include`, which mixes them into the paginated JSON this script parses. The fixed 5/15/45 s budget stands, as `app_push.sh`'s does. Carry: dismissed: gh exposes no Retry-After header without mixing headers into paginated stdout

## Friction

none
