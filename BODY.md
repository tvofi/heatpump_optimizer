R10-FLY-GH-READ-RETRY, PR 2 of 2 (the brief's PR 2; PR 3, `pr-contract.yml`'s body read, is not this one): `merge_train.py`'s and `record_row.py`'s GitHub reads retry under one bounded rule, and so does `app_approve.sh`'s JWT read of the App's installation (the carry from #2589).

The brief's two transport stops: train 8's `ci: the head commit at <sha> could not be read: Get "https://api.github.com/...": net/http...` (merge_train.py's own `bot_tip` read), and P7's `HTTP Error 500` from `record_row.py` on main's push run. PR 1 put the rule into `app_approve.sh`'s four `gh api` reads. This PR puts the same rule behind every API read the two Python instruments make.

What changes:

- **`tools/audit/seat/gh_read.py`** (new) holds the read rule for the Python instruments: `app_push.sh`'s read-back rule, 4 reads settling `READ_SLEEP_S * 3^(n-1)` = 5/15/45 s, each settle printed. Retried: a transport error, HTTP 5xx, 429, or a 403 whose deciding status line names `secondary rate limit`; everything else refuses after its one call. A spent budget returns the last failure with `(after N attempts)`.
  - `gh_transient` is `app_approve.sh`'s `gh_transient` in Python. It has two Python-only alternatives, because `gh pr view` reads over GraphQL and fails in go-gh's shapes: `HTTP NNN: msg (url)`, and `Post "https://...": ` for transport. `app_approve.sh` never calls `gh pr view`.
  - `urllib_wait` classifies urllib failures: an `HTTPError` by its status, reason and body; `URLError`, `HTTPException`, `ConnectionError` and `TimeoutError` as transport.
  - Named waits: a `Retry-After` (seconds or an HTTP date) or a spent primary bucket's `x-ratelimit-reset` is waited out, never undercut. A named wait past 45 s (the schedule's longest settle) refuses at once and says so. A spent bucket (`x-ratelimit-remaining: 0`) is read again only after its reset and is never put on the schedule. This is the R10-RCA-INSTALL-RATELIMIT carry: "A retry must wait until the reset time the 403 names, and must never loop."
  - `is_read` decides what may be retried: `gh api` with no method but GET and no field or input (gh POSTs those, attached short forms like `-fbody=x` included), and `gh pr view`. Writes never reach the loop.
- **`merge_train.py`**: `Train.__init__` wraps its own `run` (`self.run = self._reads_retried(self.run)`). Every `gh` call the train or `queue_pre_flight.py` makes goes through that `run`, so all 25 of their `gh` reads are under the rule, and a write passes through untouched. One wrapper and no call site edited: a read added later is covered the day it lands.
- **`record_row.py`**: `_api`, its one `urlopen`, reads under the rule; a spent budget re-raises the last `HTTPError` with the count as a note.
- **`app_approve.sh`**: PR 1's loop becomes `read_with <var> <fetcher>` (`gh_read` is `read_with "$1" gh api ...`), and the installation read goes through it as `curl_get`. `curl -f` gives exit 22 for every status of 400 and over, so `curl_get` reads the status off `-w '%{http_code}'`. It prints the gh status line the failure would have produced (with the API's `message`), or gh's `error connecting to` for curl's transport exits 6, 7, 28, 35, 52, 55 and 56. The same `gh_transient` classifies both shapes, so one classifier serves both fetchers. The token mint and the review POST stay bare `curl`.
- **`.github/workflows/governance.yml`**: wave-script's restore list gains `tools/audit/seat/gh_read.py`. `agreement_py.py` loads `merge_train.py`, which now imports it, and the branch copy's restore precondition refused without it (`UNRESTORED tools/audit/seat/gh_read.py`). Left out, the first pull request graded against main after this merge would be refused.
- **`tests/closure.py` / `tests/closures.json`**: `gh_read.py` goes into `INERT_EXCEPT` and entities.py's closure, the `ref_privacy.py` route, because entities.py loads `record_row.py` and runs its self-test, which imports it.
- **`tools/audit/seat/INSTRUMENTS.md`**: the rule is stated once, under `gh_read.py`, and the `app_approve.sh`, `merge_train.py` and `record_row.py` entries point to it.
- **`dev/audit/harnesses/r10_gh_read_retry_mutants.py`**: the bash region now runs to `curl_get`'s closing `}`. A Python half sweeps `gh_read.py` rule by rule (P mutants: `num cmp bool not const if str re meth elt del`), and `--seams [DIR]` enumerates the class's call sites.

How PR 1's carried proof obligations (a)-(d) are met, for the loop and the classifier alike:
- (a) A spent budget whose queue is all transient, with one more queued than the budget, in `gh_read.self_test()`, merge_train's `read retry` arms, record_row's `_api` arm and app_approve's `cispent`.
- (b) A census runs every queued `curl_get` answer through the production `curl_get` and `gh_transient` (precondition: every `curlfail` file an arm made is in it, with all three classes). The twin census runs every row of PR 1's alternatives table through both `gh_transient`s and compares them.
- (c) `ALTERNATIVES()` derives the Python classifier's keys from `gh_read.py`'s own source; app_approve's `CALTS` derives `curl_get`'s case labels. Each table must key exactly that set, with both classes per key (`default` aside).
- (d) The sweep below. A mutant killed only by one of those source-text preconditions reads SURVIVED.

The sweep's first run found one real bug, now fixed: `is_read` read `-fbody=x` as a read. In gh that is the attached short `-f`, which POSTs. Mutation M-D below pins it.

Alternatives, and why each lost (fixer.md step 17):
- **Edit each of merge_train's 25 call sites**: more code to change, and a read added later would bypass the rule. One wrapper on `Train.run` covers them all.
- **Put the Python rule in `record_row.py` and import it from merge_train**: record_row imports `tests/delivery_status.py` and the roster library, which merge_train does not need. One small module owning one concept is the sounder shape.
- **Replace app_approve's bash classifier with a call to `gh_read.py`**: CI can run a restored copy at `tools/audit/app_approve.sh`, where a sibling-relative import is fragile, and it would rewrite PR 1's reviewed code. The two twins are compared row for row instead.
- **A `--self-test` entry point on `gh_read.py`**: `selftest_wiring.py` would require a step in code-owned `governance.yml`. Instead `self_test()` runs inside record_row.py's self-test, which entities.py and governance already run.
- **Route record_row through `tools/ci/ghapi.py`**: main landed it during this PR (in `3cb111514`'s merge) as `tools/ci/`'s one REST client. It retries nothing by design: it returns non-2xx and raises `RateLimited`. Moving record_row onto it is a client migration that no brief asks for, and the retry rule would still have to sit around it.
- **Retry `git fetch`**: git's smart-HTTP failures are git's text, not the API's status lines, so a classifier for them would be a third one, written blind. Carried, not built (`## Forward-carry`).
- **Retry the post-merge GraphQL `closingIssuesReferences` query**: its answer is only logged and stops nothing, so a retry would delay the train up to 65 s for a log line.

## Head

`fac7b4d96037338644af8f49dee531b8e44bfb39`. In order: the change (`80b06040a`); a merge of main `de69745ff` (`dc73f5bd6`); the harness's bytecode fix (`f20882626`, below); two rows for the sweep's last two survivors (`3c67578bc`); a merge of main `3cb111514` (`0d3e88c6a`); and a merge of main `e45fc34fb` (`fac7b4d96`). All three merges were automatic and needed no resolution. The last one brings `tools/pr/prepr.sh`, `tools/policy/policy_lint.mjs` and `tools/audit/seat/body_push.sh` from #2625, so this body is linted by main's graders. `git merge-base origin/main HEAD` is `e45fc34fb1459e67f01ea50399b970f0e9aff2da`, `origin/main`'s tip at 2026-10-23T00:13Z. Every figure below was taken at this SHA, in a detached worktree of it; none depends on main's tip except where a row says so.

At the handoff (2026-10-23T00:45Z), `origin/main` is `d6308d77c5d02b2001e58a5436715d0c45a4fa9e`: 29 files past the merge base, mostly policy text and delivery rows, including `fixer.md` and `ci-autofix.md`. None of them is a grader of this body (`policy_lint.mjs`, `prepr.sh`, `body_push.sh`, `figure_lint`, `carry_audit.py`, `ci_predict.py`). `git merge-tree --write-tree --name-only HEAD origin/main` merges clean, with `LEDGER-MERGE: resolved tests/closures.json`. So the head is not merged again. The one obligation the new `fixer.md` text adds, repairing before the handoff any red `prepr.sh` step 6d predicts, is met: prepr's `ci predict` step reads `no closures or fast red predicted` at this head (`## Lint results`).

## Mutation proof

Each mutation was made in a detached worktree of the head, run, and restored (`git diff --quiet` after each):

| mutation | run | result | failed checks |
|---|---|---|---|
| M-A: delete `self.run = self._reads_retried(self.run)` (`merge_train.py`) | `merge_train.py --self-test` | `229 checks, 5 failed` | `read retry:` train 8's shape (2 calls, 5 s); the logged settle; the spent budget (4 calls, 5/15/45 s); the last error and count; `gh pr view` is a read |
| M-A | `queue_pre_flight.py --self-test` | `43 checks, 1 failed` | `its reads are the train's, under the read retry: ... passes after exactly 2 reads` |
| M-B: `_api` reads once (`gh_read.retry(...)` replaced by one `attempt()`) | `record_row.py --self-test` | `3 self-test check(s) failed` | `_api: a 500 twice, then 200, is read after exactly 3 calls`; `_api: and each settle is printed on stderr`; `_api: five 5xx queued ... after exactly 4 calls` |
| M-C: the installation read calls `curl_get` once, outside `read_with` | `app_approve.sh --self-test` | `254 checks, 9 failed` | `a 502 on the installation read, then an answer, is approved`; `a curl timeout (exit 28) ...`; `with exactly 2 calls` (x2); `after a printed settle of 5 s`; `naming the status and message the API gave`; `after exactly 4 calls`; `settling 5/15/45 s`; `naming the last error` |
| M-D: `is_read`'s field test back to a `startswith` over `flag=` (the pre-sweep form) | `gh_read.self_test()` | `112 checks, 2 failed` | `is_read(gh api repos/o/r/x -fbody=x) is False`; `is_read(... -Fn=1) is False` |

Failing first: before the wiring existed, merge_train's arms read `229 checks, 5 failed` (the same five) and record_row's `_api` arms failed, while the refusal arms (404, a write, a merge) already passed. Those are the arms that must not change.

**The sweep**: `python3 dev/audit/harnesses/r10_gh_read_retry_mutants.py --jobs 4` at the head prints `RESULT mutants=524 killed=494 equivalent=30 survivors=0`, rc=0, with no `TIMEOUT` line in its output (`grep -c TIMEOUT` prints 0). M0 and P0, the unmutated nulls, are `NULL-OK`. History, in order:
- The first full run printed `RESULT mutants=526 killed=468 equivalent=12 survivors=46`. The 46 were answered by:
  - the `is_read` fix above;
  - tests for untested branches: a 401 with the phrase; `-XGET`; `-X GET` last; a tuple argv; an unreadable and a non-UTF-8 body; a subcommand sorting below `api`; curl dropping after a 200;
  - removing code the sweep showed redundant: `^` beside `.match`, now `.search`; two `.strip()`s; the `max(0.0, ...)` clamps; the bounded `for` and its unreachable `raise`;
  - not mutating type annotations;
  - new equivalents (below).
- Two later runs disagreed about one mutant, P121: retry's default `note=lambda line: None` -> `0.0`, a value nothing reads. One run read it KILLED, by an unrelated check (`a non-transport exception (ValueError) refuses`), and the next read it SURVIVED. 60 unmutated self-test runs and 30 runs of P121 alone never failed. The cause was the harness: each worktree reused `tools/audit/seat/__pycache__`, which CPython validates by source mtime and size only. A mutant written within the second of the last one, at the same size, ran that one's stale bytecode. So those two runs' P verdicts are void, in either direction. `f20882626` runs the tiers under `PYTHONDONTWRITEBYTECODE=1` and `-B` and clears each worktree's caches.
- The first clean run, at `f20882626`, printed `RESULT mutants=524 killed=492 equivalent=30 survivors=2`. Stale bytecode had read both survivors KILLED: `GO_STATUS` without its `$`, and `wait > WAIT_CAP_S` -> `>=`. `3c67578bc` adds a row for each (text after the URL refuses; a 429 naming exactly 45 s is waited out).

**The equivalents**: 25 entries in the harness's `EQUIVALENT` table, keyed on line text and mutated text, each with its reason. Some match more than one mutant (the `return None` entry matches both functions' final line), so a run counts more equivalents than entries.
- PR 1's 12.
- `curl_get`'s 4: `local out rc code msg` deleted (it runs inside `read_with`'s `$(...)`, a subshell); `-eq 0` -> `-le 0` (an exit status is never negative); `return 1` -> `2` and `-> 999` (callers test zero against non-zero).
- `gh_read.py`'s 13:
  - 3 `SUBSUMED`: the `0.0` "names no wait" constants -> `1.0`, a wait below the 5 s first settle that `max(delay, wait)` outweighs;
  - `or ""` -> `or "x"` on Retry-After (both raise `ValueError` as a date) and on the reset (neither is a digit);
  - `body = ""` -> `"x"`;
  - `n == 1` -> `<=` and `n == READ_TRIES` -> `>=` (n starts at 1 and steps by 1);
  - `k + 1 < len` -> `!=` (k indexes argv);
  - a missing method `""` -> `"x"` (neither is GET);
  - `split("=", 1)` -> maxsplit 2 and 999 (same first field);
  - `return None` -> `pass` (falling off the end returns None);
  - retry's default `note` returning `0.0` (nothing reads it).

## Null control

- The unmutated self-tests at the head: `gh_read self-test: 112 checks, 0 failed`; `record_row self-test: all checks passed`; `merge_train self-test: 229 checks, 0 failed`; `queue_pre_flight self-test: 43 checks, 0 failed`; `app_approve self-test: 254 checks, 0 failed`. The sweep's M0 and P0, separate runs of the same self-tests, pass too. In each arm, a refusal (404, 401, a permission 403, 422, a wrong head, a write, a merge, curl exit 60, an installation answer with no `id`) makes exactly 1 call with no settle.
- The seam census at the merge base (`git archive e45fc34fb tools/audit/seat tools/pr`, then `--seams <that dir>`) prints `PRECONDITION Train.run wrapped=False _api retried=False` and `SEAMS unretried_reads=27`, rc=1. At the head it prints `wrapped=True _api retried=True` and `SEAMS unretried_reads=0`, rc=0. The 27 at the base are merge_train's 21 `gh` reads, queue_pre_flight's 4, record_row's `urlopen` and app_approve's installation `curl`.
- The agreement lane: the branch copy, and with wave-script's 35 base pathspecs restored from `e45fc34fb` (3 graded files differ from the branch: `merge_train.py`, `queue_pre_flight.py`, `app_approve.sh`), both print `RESULT divergent=0 unregistered=0 dead=0 refused=0` and `AGREEMENT ok`. The restore precondition reads 14 of 14 covered on the branch and 13 of 13 on the base copy. Before the `governance.yml` line, the branch read `14 closure file(s), 13 covered ... 1 missing`, rc=1.
- Agreement discovery does not read these files. At the head it prints `discovery: 407 governance code files, 1732 distinct grammars, 27 shared by two or more files`, and the same line again with `GH_STATUS`'s text made byte-identical to the bash sed. So the twin census in app_approve's self-test is the agreement mechanism for this pair, and the named group in the Python pattern dodges no registration.

## Figures

- **Self-tests**: `/opt/hpo/venv-ci/bin/python -c "import sys; sys.path.insert(0, 'tools/audit/seat'); import gh_read; sys.exit(gh_read.self_test())"`, `python3 tools/audit/seat/record_row.py --self-test`, `python3 tools/audit/seat/merge_train.py --self-test`, `python3 tools/audit/seat/queue_pre_flight.py --self-test`, `bash tools/pr/app_approve.sh --self-test`: the summaries under `## Null control`. Each Python one ran under `/opt/hpo/venv-ci/bin/python` (CPython 3.14.7, CI's pins) and again under CPython 3.11, with the same result.
- **Python alternatives**: `ALTERNATIVES()` in `gh_read.py` derives 12 (rule: each `|` alternative, at every level, of each module `re.compile` pattern, a pattern with none counting as one; each integer of `http_transient`; the `SECONDARY` phrase; `default`). The self-test asserts the table keys exactly that set.
- **curl alternatives**: `CALTS` (`sed -n '/^curl_get() {/,/^}/p' tools/pr/app_approve.sh | grep -v '^ *#' | grep -oE "^ +[^ ()]+\)"`, split on `|`, plus `default`) gives 9 keys: `0 6 7 28 35 52 55 56 default`. The self-test asserts the table keys exactly that set.
- **Sweep by rule**: `python3 dev/audit/harnesses/r10_gh_read_retry_mutants.py --list | awk -F'\t' '{split($3,a," "); print substr($1,1,1), a[1]}' | sort | uniq -c` gives 190 M mutants and 334 P mutants, plus the two nulls. M: `num` 84, `del` 32, `rel` 15, `alt` 11, `copy` 9, `flag` 6, `or` 6, `anch` 5, `quant` 5, `opnd` 4, `glob` 4, `word` 3, `pipe` 2, `ret` 2, `not` 1, `src` 1. P: `num` 67, `cmp` 65, `del` 54, `str` 38, `elt` 33, `re` 23, `if` 21, `const` 15, `bool` 9, `not` 6, `meth` 3.
- **The class's seams** (fixer.md step 8): `python3 dev/audit/harnesses/r10_gh_read_retry_mutants.py --seams` prints one row per seam with its route; `| cut -f3 | sort | uniq -c` gives the dispositions below. The rule enumerating the seams is in the harness docstring (THE SEAMS).

  | disposition | seams |
  |---|---|
  | read, retried through `Train.run` (`self.run` 13, `self.out` 8, `self.t.run` 4) | 25: closed in this diff |
  | read, `_api`'s `urlopen` under `gh_read.retry` | 1: closed in this diff |
  | read, `read_with` (`check_pr`'s pull request, `comments`, `owners`, `files`, the installation) | 5: PR 1's four, plus the installation closed in this diff |
  | the loop and its fetcher (`read_with`, `gh_read`, `curl_get`) | 3 |
  | write or local (`gh pr merge/review/ready`, `gh api --method POST/PATCH/DELETE`, `-X POST`, `gh workflow run`, `gh auth token`; curl `-X POST/DELETE`) | 15: never retried, already guarded |
  | `gh api graphql` `closingIssuesReferences`, a `self.log(` line | 1: log-only, not retried (alternatives above) |
  | git transport (`git fetch` x13 and `git push --delete` in merge_train.py; `git fetch refs/pull/$pr/head` in app_approve.sh's carry path) | 15: a distinct seam, carried |

- **Scope**: `python3 tests/closure.py select --diff $(git merge-base origin/main HEAD) --workdir "$D"` prints `MODE: FULL -- every test script runs, nothing is scoped out.` (reason: `tests/closure.py changes the gate itself`). As fixer.md step 5 says, that marks a diff the gate cannot scope. I ran the scripts that read what changed: `tests/entities.py` (`ALL 2399 ENTITY CHECKS PASSED`), `tests/closure.py selftest` (`ALL 112 closure shrink pins PASSED`), `tests/harness_headers.py` (`ALL 109 HARNESS HEADER CHECKS PASSED`), `tests/layout.py` (`layout self-test: ok`) and `tests/env_drift.py --claims-only e45fc34fb` (`claims hygiene: ... ok`), all with `PYTHONPATH=tests/hastub` under `/opt/hpo/venv-ci/bin/python`. The rest is CI's.
- `python3 tests/structure.py`: `STRUCTURE RATCHET PASSED`; `git diff --name-only $(git merge-base origin/main HEAD)...HEAD | grep -c '_budgets.json$'` prints 0.
- `python3 tools/audit/archscore/score.py --diff $(git merge-base origin/main HEAD) HEAD`: `Architecture score: dS +0.0000 NULL`.
- `python3 -I tools/audit/seat/selftest_wiring.py --check`: `87 self-testing, 87 wired, 0 unwired`. `python3 -I tools/audit/seat/tmp_paths.py --check`: `0 refused`.
- `git diff --quiet $(git merge-base origin/main HEAD)...HEAD -- VERSION 'custom_components/*/manifest.json' RELEASE_NOTES.md tests/golden/claimed_drift.txt tests/golden/card_claimed_drift.txt && echo NONE-TOUCHED` prints `NONE-TOUCHED`.
- **A fixture that moved**: `queue_pre_flight.py`'s fixture Train now takes `sleep=lambda s: None`. Its `gh: HTTP 500/502` "broken read" fixtures are transient now, so without it they would sleep out the 5/15/45 s schedule; the reads they pin are unchanged. No wall-clock figure is given: it moves with machine load.

## Red checks

none. No CI has run on this head: it is a handoff, and no pull request is open for it. `governance.yml` is in the diff, so `nightly-status` and `delivery-status` are owed an answer if they turn red on this branch.

## Forward-carry

- `git fetch`/`git push` are GitHub transport too (15 seams: 14 in `merge_train.py`, 1 in `app_approve.sh`'s carry path, which #2589's carry assigned to this PR). They are not API reads: git's smart-HTTP failures print git's own text (`fatal: unable to access '...'`, `error: RPC failed; HTTP 5xx`), not gh's status lines. Retrying them needs a classifier of its own, written against measured git stderr, not guessed. None has stopped a train in the brief's eleven. Carry: R10-FLY-GH-READ-RETRY
- For PR 3 (`pr-contract.yml`'s body read): `printf '%s' "$stderr" | python3 tools/audit/seat/gh_read.py --classify` already answers gh's classes (exit 0 transient) with the rule stated once. A workflow step can use it rather than a third classifier, and the non-JSON-body class that carry names would be added there, with a row in `ALTERNATIVES()`'s table. Carry: R10-FLY-GH-READ-RETRY
- `tools/ci/ghapi.py` (landed on main during this PR) is a second urllib GitHub client with no read retry. Its `get` returns a 5xx to the caller, and every `tools/ci/` hook judges it. When those hooks want a retry, `gh_read.retry` with `gh_read.urllib_wait` is the rule to wrap `ghapi.get` in, rather than a third. Carry: R10-CI-LAYOUT-P2

## Friction

- dispatch-prompt: stale: `dispatch/fixer-r10-fly-gh-read-retry`'s PROMPT.md still names PR 1's topic (`r10-fly-gh-read-retry`) and head `fd99148`, while the scheduled task names PR 2 and topic `r10-fly-gh-read-retry-2`. The task's words were taken, and the return refs use the `-2` topic. Carry: R10-FLY-GH-READ-RETRY

## Lint results

`PATH=/opt/hpo/venv-ci/bin:$PATH PREPR_SKIP_CLOSURES=1 bash tools/pr/prepr.sh <this body>` at the head prints `PRE-PR: fac7b4d96037338644af8f49dee531b8e44bfb39 0000000000000000000000000000`, rc=0, rc=0; every step is `ok` but `closures` (skipped, `PREPR_SKIP_CLOSURES`), `unpinned sites` (the diff adds none), and `push order` and `ancestry reds` (no remote branch until the handoff push).
`python3 tools/audit/carry_audit.py check --body <this body>` prints `CARRY-AUDIT: 4 finding item(s): 4 routed, 0 unrouted, 0 bad destination(s)`.

🤖 Generated with [Claude Code](https://claude.com/claude-code)

https://claude.ai/code/session_01QFcP6Ea7M3rDDN8Wvijpj3
