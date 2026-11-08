R10-FLY-GH-READ-RETRY, the carries part (topic r10-fly-gh-read-retry-p3). It belongs to the class "one unretried GitHub read kills an instrument". This diff closes two seams (stamp.py's rule-2 reads, the harness's pages) and lands the runner a third needs, each under `tools/audit/seat/gh_read.py`'s one rule: 4 reads settling 5/15/45 s, retrying a transport error, a 5xx, a 429 or a secondary-limit 403, and refusing anything else after its one read.

- Carry 0, the runner and the classifier. The workflow's wiring waits, and the reason is measured (below).
  - New `tools/audit/seat/gh_read_run.py` runs one `gh` read under `gh_read.retry`/`gh_wait`. It refuses any argv that `gh_read.is_read` does not call a read, with exit 2 and the argv never run. It writes the answering read's stdout once, so a retried `--paginate` prints no page twice.
  - `gh_read.py` gains `NON_JSON`. With no status line, gh's `invalid character '<c>' looking for beginning of value` is transient. This is the exact line of #2579's failure (run 39681234360, job 119504172159, read from its log). A status line, when one is printed, still decides.
  - `governance.yml` `instrument-self-tests` gains the runner's self-test step.
  - `tools/policy/field_coverage.mjs` declares both files as pinned graders, each `pending` its pin.
  - Why the wiring is not in this diff. A first cut routed all 7 of pr-contract.yml's `gh api` reads through the runner and added both files to the job's base restore. `tools/pr/prepr.sh` then refused on `ci_predict.py`: `PREDICT governance / policy-docs GRADER field_coverage.mjs REFUSED by the base's copy ... pinned tools/audit/seat/gh_read.py is unregistered`. policy-docs grades with the base's `field_coverage.mjs`, and that copy cannot hold a registration this diff adds. ci_predict's named repair for a GRADER refusal is to land the grader change first (dev/audit/rca/R10-RCA-PREPR-HEAD-GRADERS.md).
  - So this diff lands the runner, the class and the two pending DECLARED entries. The pr-contract.yml wiring is a follow-up on a base that has all three (Forward-carry); that follow-up also drops `pending`.
  - `gh_read_run.py` is a new file rather than a `--read` mode of `gh_read.py`, for the same reason: pr-contract restores what it pins from the base, so the PR adding a mode to a pinned file is graded by a copy lacking it.
- Carry 5, `dev/audit/harnesses/r10_codescan_wait_race.py` `pages()`. It now pages by `PER_PAGE = 30` instead of 100. A retry cannot ride out this 502: the page size itself causes it (re-measured below). The page bound keeps the base's ceiling of 5000 items (`MAX_ITEMS = ghapi.MAX_PAGES * 100`). The first cut kept 50 pages, which caps at 1500 items, and this harness's own run over run 42454528717 (1760 jobs, every attempt listed) refused with `too many pages`. A self-test arm now pins the 1760 case.
- Carry 6, `tools/release/stamp.py`. Rule 2's two sources now read under gh_read's rule:
  - `get_rest` uses `urllib_wait`.
  - `get_gh` (the default source whenever gh is installed, and a single-shot read of the same class) uses `gh_wait`.
  - A refusal names the last failure and the attempt count, and `tests_gate` carries that into its verdict.

Alternatives considered, and why each lost:
- (a) An inline bash retry loop in each workflow step. Refused: it would be a third copy of the rule, beside `gh_read.py` and `app_approve.sh`'s twin.
- (b) A `--read` mode inside `gh_read.py`. Refused: the pinned base copy would lack it.
- (c) Wiring pr-contract.yml in this diff. Refused: governance / policy-docs is predicted red under the base's `field_coverage.mjs`, and that red reaches `gate`, the required check.
- (d) Retrying `pages()`. Refused: the 502 reproduces at per_page=100 on every read.
- (e) Retrying `get_rest` only, as the carry names it. Refused: `get_gh` is the source rule 2 actually uses on a seat with gh installed.

Part of #2731.

Carry status at merge base 73365699a:
- Carry 0: in part, this diff (above). The pr-contract.yml wiring waits on this diff's merge; see Forward-carry.
- Carry 1: covered by 80b06040a. `tools/pr/app_approve.sh` reads the JWT GET of `/installation` through `read_with inst curl_get`, and its self-test's `curlfail-installation` census drives it. Proven by `bash tools/pr/app_approve.sh --self-test`: 316 checks, 0 failed.
- Carry 2: PR 1's proof, applied to this diff's classifier and loops:
  - (a) Every spent-budget fixture queues one transient failure more than the budget, and asserts that each queued line is transient. This holds in `gh_read_run.py` (5 queued, refused after 4 calls), in `stamp.py` `get_rest` (5 queued, 4 reads) and in `get_gh` (5 queued, 4 reads).
  - (b) Census: every fixture line goes through the production `gh_transient`/`urllib_wait`.
  - (c) `NON_JSON` is derived as an alternative by `gh_read.ALTERNATIVES()` from the source. The self-test asserts the derived set, and that each key holds both classes. It adds 3 retry rows and 6 near-misses.
  - (d) The rule-generated sweep `dev/audit/harnesses/r10_gh_read_retry_mutants.py` derives mutants of the new pattern (anchors, quantifier, the `or` in `gh_transient`). See Figures for its result.
  - Covered by 80b06040a for PR 1/PR 2.
- Carry 3: covered by 80b06040a. `gh_read.urllib_wait` returns only a spent bucket's named reset, and a wait past the 45 s cap refuses at once. Proven by the gh_read self-test arms `a spent hourly bucket resetting in 20 min refuses after 1 call, naming the wait` and `a spent bucket resetting in 20 s is read once more, after its reset`, run inside `python3 -I tools/audit/seat/record_row.py --self-test`.
- Carry 4: moved to R10-TRAIN-MERGE-LOOP, as the brief records. Not here.
- Carry 5: this diff. The brief's `[implemented: 166647f1b]` did not hold: at the merge base `pages()` still asked per_page=100, and the live read still fails (Null control).
- Carry 6: this diff.
- Carry 7 and carry 9 (the same item): covered by 4f478a78c. `tools/ci/codescan_wait.py` `source()`'s own-run path now polls `_jobs()` until `settled(jobs)`, and fails at the bound. Proven by `python3 -I tools/ci/codescan_wait.py --self-test` checks 18-20 (`18 own run: a lagging step row is polled ...`, `19 ... FAILs, never passes`, `20 null: a settled stand-down ...`): 20 checks, 0 failed.
- Carry 8 and carry 10 (the same item): the measurement the carry asks for, delivered by `dev/audit/harnesses/r10_red_list_lag.py` in this diff; its count is in `## Figures`, line "Lagging reds" (1 lagging red in 379 lists); the fix decision is forward-carried.
- Carry 11: waits. `git_transient` does not exist at the merge base: `git grep -n git_transient` is empty. The classifier the carry would reuse comes with R10-TRAIN-MERGE-LOOP-2 (#3288, in progress), so app_push.sh's push retry follows once #3288 lands.

## Head

2e9a022457f5c943776ccaa76f705b0de6e2eaf1, on merge base 73365699a135fb813a43380096b6776d57f8ff4c (origin/main's tip when this branch was cut, 2026-11-08T07:37Z). `tools/pr/prepr.sh` passed at this head with rc 0. origin/main has since moved to 2a3c05644d85b7ee5c2c314fde5aca950e4aba91, and `git merge-tree --write-tree origin/main HEAD` reports no conflict. Under the owner's 2026-11-07 ruling, main is not merged, so prepr.sh was not re-run.

## Mutation proof

- Rule-generated sweep of `gh_read.py`: `python3 dev/audit/harnesses/r10_gh_read_retry_mutants.py P0 P1 ... P360`, every P mutant `--list` names. It prints `RESULT mutants=360 killed=346 equivalent=14 survivors=0`. That includes P36/P37/P38 (the `NON_JSON` anchors and quantifier) and P93 (`or` to `and` in `gh_transient`).
- Diff mutants: `python3 -I tools/audit/seat/mutant_run.py --diff 73365699a...HEAD --cmd "$MUTANT_CMD" --max-mutants 0 --report-only`.
  - `MUTANT_CMD` runs `stamp.py --self-test` and `gh_read_run.py --self-test` (each grepped for its pass line, as the CI steps grep) and `gh_read.self_test()`.
  - 118 mutants, 26 survivors, all dispositioned under `## Unpinned sites`. No production predicate survives.
  - A first pass left 32 survivors. Its production survivors were:
    - `text=True` to `False` in both runners;
    - `gh_read_run.main`'s `return read(argv)`;
    - the `__main__` guard;
    - `read_rule`'s own path insert.
  - Each is now killed: the stubs assert `text`/`capture_output`/`cwd`, `main` is driven with a write argv, the CI-style pass-line grep catches a dead entry point, and a fresh `-I` interpreter calls `stamp.read_rule()`.
- Deleting the fix: with the merge base's `get_gh`/`get_rest` under this head's self-test arms, the spliced control prints `FAIL` on each of the 10 `carry 6` arms it reaches. The arms pass an `opener`/`run` the base functions do not take, so that control fails on a TypeError, not on a retry count. The count-level control is the diff-mutant run above, where `GUARD_OFF`/`RETURN_DEL` on the retry lines are killed.

## Null control

- `gh_read`: at the merge base, `printf '%s' "invalid character 'S' looking for beginning of value" | python3 -I <base gh_read.py> --classify` exits 1 (refused). At the head it exits 0 (transient).
- Carry 5, live: the merge base's `dev/audit/harnesses/r10_codescan_wait_race.py`, run as `--since 2026-10-24T14:15:00Z --until 2026-10-25T00:30:00Z`, dies with `ghapi.ApiError: repos/tvofi/heatpump_optimizer/actions/runs/40132661027/jobs: HTTP 502` after 3m01s. The head's run of the same window completes, printing `ci.yml pull_request runs created ...: 249`, `INVERTED 34, ORDERED 68` and `RED edit runs: 22 INVERTED, 0 ORDERED`.
- Carry 5, per page size: `gh api -i "repos/tvofi/heatpump_optimizer/actions/runs/40126133450/jobs?filter=all&per_page=N&page=P"` answers 502 for per_page=100 on pages 1 and 2. It answers 200 on all 11 pages at 30 and all 7 at 50; the run has 312 jobs (`total_count`).
- The harness self-test's new arm (a server refusing pages over 50 jobs) fails against the base `pages()`: `selftest: 11 checks, 1 failed ['pages over a server refusing pages over 50: got None in [100]']`. At the head: `11 checks, 0 failed`. The 1760-job arm fails against a 50-page bound (`pages over 1760 jobs: got None`) and passes at the head.
- Null controls inside the self-tests, each at the head:
  - a 404 refuses after exactly 1 call;
  - a 422 refuses after exactly 1 call;
  - a body that does not parse refuses after 1 read;
  - a write argv is never run;
  - each `NON_JSON` near-miss is refused (a prefix, a suffix, a different JSON error, an empty or overlong character, and a status line that decides first).

## Figures

- `python3 -I tools/audit/seat/gh_read_run.py --self-test`: `gh_read_run self-test: 13 checks, 0 failed`.
- `python3 -I tools/release/stamp.py --self-test`: `RESULT stamp_self_test=pass`, with 12 `carry 6` arms.
- `python3 -I tools/audit/seat/record_row.py --self-test`: `gh_read self-test: 131 checks, 0 failed` and `record_row self-test: all checks passed`.
- `bash tools/pr/app_approve.sh --self-test`: `app_approve self-test: 316 checks, 0 failed`. The bash twin is unchanged: `NON_JSON` is the Python twin's own, because app_approve.sh's reads pass no `--jq` to gh.
- `python3 -I dev/audit/harnesses/r10_codescan_wait_race.py --selftest`: `selftest: 11 checks, 0 failed`.
- `python3 -I dev/audit/harnesses/r10_red_list_lag.py --selftest`: `selftest: 5 checks, 0 failed`.
- `node tools/policy/field_coverage.mjs`: `FIELD COVERAGE ok`, `refused=0`, with both newly pinned files declared.
- `python3 tools/pr/ci_predict.py --apply-inert`: it wrote the two INERT READS entries (`gh_read_run.py`, `r10_red_list_lag.py`) and then printed `CI PREDICT: no closures, fast, governance or instrument red predicted`.
- `python3 dev/audit/harnesses/r10_gh_read_retry_mutants.py P0 ... P360`: `RESULT mutants=360 killed=346 equivalent=14 survivors=0`, wall time 7m57s.
- `python3 tools/pr/ci_predict.py` at the head: `CI PREDICT: no closures, fast, governance or instrument red predicted`.
- `python3 -I tools/audit/seat/mutant_run.py --diff 73365699a...HEAD --cmd "$MUTANT_CMD" --max-mutants 0 --report-only`: 118 mutants, 26 survivors, wall time 1m36s.
- `python3 tests/closure.py select --diff 73365699a135fb813a43380096b6776d57f8ff4c --workdir "$D"`: `MODE: SCOPED -- 3 script(s) run, 30 scoped out`. It names `tests/doc_claims.py` (`ALL 296 checks PASSED`), `tests/entities.py` (run by prepr.sh) and `tests/harness_headers.py` (`ALL 112 HARNESS HEADER CHECKS PASSED`).
- `python3 tests/structure.py`: `STRUCTURE RATCHET PASSED`.
- `python3 tools/audit/archscore/score.py --diff 73365699a135fb813a43380096b6776d57f8ff4c`: `Architecture score: dS +0.0000 NULL`.
- Class seams in workflows. The rule `git grep -n 'gh api' -- .github/workflows` returns 24 single-shot `gh api` reads in 9 files at the merge base: 7 in pr-contract.yml (the carry's own) and 17 in the other 8 workflows (arch-score, codeql, dependabot-automerge, dependency-graph, governance, nightly, pages, tests). All 24 are open in this diff and forward-carried below; the runner they need is the one this diff lands.
- Class seams over urllib. `git grep -nE "urlopen\(" -- tools` returns:
  - `record_row.py`'s read: already behind `gh_read.retry`.
  - Its self-test stand-in: no call.
  - `tools/ci/ghapi.py` `_open`: behind `ghapi.get`'s 2/6 s GET retry, carry 7 of #2995.
  - `stamp.py` `get_rest`: closed here.
  - `stamp.py` `dispatch_record_beat`: a POST, outside the read rule.
- Lagging reds (carry 8/10). `python3 -I dev/audit/harnesses/r10_red_list_lag.py --since 2026-11-07T18:00:00Z --rows` lists every `pr-contract / pr-contract` job of ci.yml pull_request runs created since 2026-11-07T18:00Z. For each job it counts the check runs at that head that started before the job's "List the red checks at this head" step completed and concluded `failure` after it. Result (2026-11-08, wall time 44m06s): 178 runs, 379 red lists read, 69 heads. LAGGING is 1: run 42420923725 attempt 2 at head 30e7024e listed its reds at 23:19:53Z, while `tests / fast (3.14)` at that head had started at 22:55:16Z and concluded `failure` at 23:29:35Z. The null control is the same lists with the timing comparison removed: REDS 13524, the failed check runs at those heads summed over every list. So the fail-open the carry describes is real but rare: 1 red in 379 lists. Whether a fix is owed, and which one (waiting for in-progress check runs, or listing them), is the orchestrator's call on this number. The window is not the RCA's three incident windows, which this seat could not name.

## Unpinned sites

All 26 diff-mutant survivors, by site:
- `tools/audit/seat/gh_read_run.py:28` and `tools/release/stamp.py` `read_rule`'s `sys.path.insert(1, ...)`. Equivalent: the insert position does not matter while no other `gh_read` is on the path (`-I` drops the script directory). Deleting the insert is killed by the fresh-interpreter arm.
- `gh_read_run.py:59`, `:61` (`passed`/`failed += 2`), `:118` (`return 2 if failed`, and `RETURN_DEL`). These are the self-test's own counters and return code. They differ only once a check fails, and the CI step greps `0 failed` on the summary line.
- `gh_read_run.py:70` (the stub's kwarg guard off): the guard is the self-test's own assertion, so taking it off weakens the oracle without changing production.
- `gh_read_run.py:79`, `:82`, `:90`, `:91`, `:101` and `stamp.py:1358`, `:1361`, `:1365` (fixture exit code 1 to 2). Equivalent: any non-zero exit is a failed read, and the code is kept (`a refusal keeps the last read's own exit code`).
- `gh_read_run.py:89`, `:100`, `:105`, `:107`, `:109`, `:116` (a `check(...)` deleted). Each deletes one assertion of the self-test, not a behaviour. Each is the oracle, pinned by review.
- `stamp.py:1320`, `:1329`, `:1330`, `:1337` (a fixture's 502 to 503, 503 to 504, errno 104 to 105). Equivalent: each is still a member of the transient class it stands for.
- `stamp.py:1348` (the `get_gh` stub's kwarg guard off): the self-test's own assertion, as above.

## Red checks

none

## Forward-carry

- Carry 0's wiring, once this diff is on main. Route each of pr-contract.yml's 7 `gh api` reads through `python3 -I tools/audit/seat/gh_read_run.py gh api ...`, add `'tools/audit/seat/gh_read.py'` and `'tools/audit/seat/gh_read_run.py'` to the step "Restore the check source from the base commit"'s pathspec list, and drop both `pending` keys in `tools/policy/field_coverage.mjs`'s DECLARED.
  - It is code-owned (`.github/workflows/`), under the mandated approval the brief names.
  - Measured on this branch's first cut, that wiring passes `codeowners_gap.py --check` (rc 0, `uncovered_files=0`, both files `PINNED`). It went red only on the base-copy registration this diff lands.
  - Carry: R10-FLY-GH-READ-RETRY
- The other 17 workflow `gh api` reads (`git grep -n 'gh api' -- .github/workflows`, less pr-contract.yml's) are the same class. Each can use the same runner where its job pins nothing, or with the same restore and DECLARED entries where it does. Re-run the enumerator at that group's merge base. Carry: R10-FLY-GH-READ-RETRY
- Carries 8/10, measured here: pr-contract's red list missed 1 still-running red in 379 lists (2026-11-07T18:00Z onward, `dev/audit/harnesses/r10_red_list_lag.py`). The fix decision, and a re-run over the RCA's three incident windows, rest with the orchestrator. Carry: R10-FLY-GH-READ-RETRY
- Carry 11 (app_push.sh's push on `git_transient`) waits on #3288 landing the classifier. Carry: R10-FLY-GH-READ-RETRY

## Friction

- pr-contract-base-restore: cost: a grader the base runs cannot learn a registration in the pull request that needs it, so a new pinned grader takes two merges. The runner landed first, with its wiring carried. Carry: dismissed: the restore is the #1515 barrier working as designed, and field_coverage's `pending` key is the mechanism for exactly this
