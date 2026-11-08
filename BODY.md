R10-FLY-GH-READ-RETRY, the carries part (topic r10-fly-gh-read-retry-p3). It belongs to the class "one unretried GitHub read kills an instrument". This diff closes two seams (stamp.py's rule-2 reads, the harness's pages) and lands the runner a third needs, each under `tools/audit/seat/gh_read.py`'s one rule: 4 reads settling 5/15/45 s, retrying a transport error, a 5xx, a 429 or a secondary-limit 403, and refusing anything else after its one read.

- Carry 0, the runner and the classifier. The workflow's wiring waits, and the reason is measured (below).
  - New `tools/audit/seat/gh_read_run.py` runs one `gh` read under `gh_read.retry`/`gh_wait`. It refuses any argv that `gh_read.is_read` does not call a read, with exit 2 and the argv never run. It writes the answering read's stdout once, so a retried `--paginate` prints no page twice.
  - `gh_read.py` gains `NON_JSON`. With no status line, gh's `invalid character '<c>' looking for beginning of value` is transient. This is the exact line of #2579's failure (run 39681234360, job 119504172159, read from its log). A status line, when one is printed, still decides.
  - `governance.yml` `instrument-self-tests` gains the runner's self-test step.
  - `tools/policy/field_coverage.mjs` declares both files as pinned graders, each `pending` its pin.
  - Why the wiring is not in this diff. A first cut routed all 7 of pr-contract.yml's `gh api` reads through the runner and added both files to the job's base restore. `tools/pr/prepr.sh` then refused on `ci_predict.py`: `PREDICT governance / policy-docs GRADER field_coverage.mjs REFUSED by the base's copy ... pinned tools/audit/seat/gh_read.py is unregistered`. policy-docs grades with the base's `field_coverage.mjs`, and that copy cannot hold a registration this diff adds. ci_predict's named repair for a GRADER refusal is to land the grader change first (dev/audit/rca/R10-RCA-PREPR-HEAD-GRADERS.md).
  - So this diff lands the runner, the class and the two pending DECLARED entries. The pr-contract.yml wiring is a follow-up on a base that has all three (Forward-carry); that follow-up also drops `pending`.
  - `gh_read_run.py` is a new file rather than a `--read` mode of `gh_read.py`, for the same reason: pr-contract restores what it pins from the base, so the PR adding a mode to a pinned file is graded by a copy lacking it.
- Carry 5, `dev/audit/harnesses/r10_codescan_wait_race.py` `pages()`. The branch's first design paged at 30 a page always. origin/main (3220210742) meanwhile landed a second design of the same retry: per_page=100, and on a 5xx that outlasts `ghapi.get`'s own retries, the listing restarts at per_page=30. That design is kept, so there is one `pages()`, main's. Main's design had one defect, measured below: each size was bounded by `ghapi.MAX_PAGES` (50) pages, which is 1500 items at 30 a page. A 1760-job run (run 42454528717, every attempt listed) whose 100-a-page read 5xx's then refused with `too many pages` after 51 asks. The fix stays inside main's design: each size is bounded by items, `MAX_ITEMS = ghapi.MAX_PAGES * 100`, the same 50 pages at 100 a page and 167 at 30. The carry 5 self-test cases are re-expressed against the fallback: the 70-job server answering 502 for any page over 50 jobs, now asked `[100, 30, 30, 30]`, and the 1760-job run behind the same 502, asked `[100] + [30] * 59`. Main's two `pages()` calls in its fallback and clean checks now catch `ApiError` the way the carry cases do, so a raise is a failed check the summary counts, not a crash before the summary prints.
- Carry 6, `tools/release/stamp.py`. Rule 2's two sources now read under gh_read's rule:
  - `get_rest` uses `urllib_wait`.
  - `get_gh` (the default source whenever gh is installed, and a single-shot read of the same class) uses `gh_wait`.
  - A refusal names the last failure and the attempt count, and `tests_gate` carries that into its verdict.

Alternatives considered, and why each lost:
- (a) An inline bash retry loop in each workflow step. Refused: it would be a third copy of the rule, beside `gh_read.py` and `app_approve.sh`'s twin.
- (b) A `--read` mode inside `gh_read.py`. Refused: the pinned base copy would lack it.
- (c) Wiring pr-contract.yml in this diff. Refused: governance / policy-docs is predicted red under the base's `field_coverage.mjs`, and that red reaches `gate`, the required check.
- (d) Retrying `pages()` at the same page size. Refused: the 502 reproduces at per_page=100 on every read.
- (f) Keeping the branch's always-30 design beside main's fallback, or replacing main's with it. Refused: two paging designs of one retry is the duplication the merge conflict exposed. Main's design asks one page more for a small run behind a 502 but asks 100 a page when the server allows it, and its only measured defect is the page bound, fixed here.
- (e) Retrying `get_rest` only, as the carry names it. Refused: `get_gh` is the source rule 2 actually uses on a seat with gh installed.

Part of #2731.

Carry status at merge base 73365699a:
Numbering: the carries are numbered 0 to 11, as in the brief. The review packet numbers them 1 to 12, so its Carry 12 is this list's Carry 11 (the app_push.sh push), and each other packet number is one above the number used here.
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
- Carry 11: not in this diff. At the merge base 17e621f08, `git grep -n git_transient -- tools/audit/seat/gh_read.py` returns the classifier R10-TRAIN-MERGE-LOOP-2 landed (0ccedc45d); at the branch's cut it was empty. app_push.sh's push retry can now reuse `gh_read.run_git_retry`, and is forward-carried. Carry: #2731

Each forward-carry item goes to #2731, the class's issue, which this group lists, because landing a carry on the roster branch is the orchestrator's write.

## Head

65581d2929ca645265262b4d73278be9b4426d62, on merge base 51cd5ec8a42abde3c223f22e9f4a0d5f35f8844a (origin/main's tip, fetched before 2026-11-08T20:37Z). It is two merges onto 2e9a022457f5c943776ccaa76f705b0de6e2eaf1. 07ce17b1d9487b76b44b9d6457747ba6191f72ed merged origin/main 17e621f08 and resolved the conflict in `dev/audit/harnesses/r10_codescan_wait_race.py`. 65581d292 merged origin/main 51cd5ec8a, which had moved after `tools/pr/prepr.sh` passed at 07ce17b1d, with no conflict. Main's 17e621f08..51cd5ec8a delta is 9 files; the only one this diff also changes is `tests/closures.json` (`comm -12` of the two `git diff --name-only` lists), merged by LEDGER-MERGE (`inert_reads.tests/harness_headers.py: merged as a set (974 entries)`). The gate figures (closure select, its three scripts, the run_always lines, structure, archscore, ci_predict, the harness self-test) were re-taken at 65581d292 against 51cd5ec8a. The other self-test and mutant figures were taken at 07ce17b1d against 17e621f08; the second merge changed none of the files they read. `PREPR_SKIP_CLOSURES=1 bash tools/pr/prepr.sh <this body>` was re-run at 65581d292, the cloud's allowance; its PRE-PR line reads rc=0. The skipped step is the closures re-derivation. Its null control: `python3 tools/pr/ci_predict.py`, which reads the recorded closures, prints `CI PREDICT: no closures, fast, governance or instrument red predicted` at this head against 51cd5ec8a42a, and the same line in a worktree of origin/main 17e621f08.

## Mutation proof

- Carry 5, the fallback deleted: the two lines `if st >= 500 and size != 30: break` are removed from `pages()`, so it raises on the first 5xx. The harness self-test then prints `selftest: 14 checks, 3 failed pages['fallback', 'over50', 'many1760']` with rc 1: main's fallback check and both carry 5 cases fail, and `clean` passes.
- Rule-generated sweep of `gh_read.py`: not re-run at this head. `python3 dev/audit/harnesses/r10_gh_read_retry_mutants.py --list` lists 0 mutants and prints `EQUIVALENT entries no rule generates: [('    if ! gh_transient "$(cat "$_ef")" || [ "$_try" -ge "$READ_TRIES" ]; then', ...)]`, at this head and in a worktree of origin/main 17e621f08 alike. Main's 0ccedc45d renamed that `tools/pr/app_approve.sh` line's call to `"$_cls"`, so the harness's EQUIVALENT entry no longer matches. That is a pre-existing break on main, outside this repair's conflict region, and is forward-carried. The figure taken at 2e9a02245 (the base 73365699a) was `RESULT mutants=360 killed=346 equivalent=14 survivors=0`, including P36/P37/P38 (the `NON_JSON` anchors and quantifier) and P93 (`or` to `and` in `gh_transient`). The diff mutants below re-take the NON_JSON and retry lines at this head.
- Diff mutants: `python3 -I tools/audit/seat/mutant_run.py --diff 17e621f08...HEAD --cmd "$MUTANT_CMD" --max-mutants 0 --report-only`. The diff mode reads only files outside `dev/` and `tests/`, so the harness's mutation is the carry 5 line above.
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
- Carry 5, the bound. A probe drives origin/main's own `pages()` (`git show origin/main:dev/audit/harnesses/r10_codescan_wait_race.py`) with a server serving 1760 jobs that answers 502 for any page over 50 jobs. It raises `ApiError(x: HTTP 200 too many pages)` after 51 asks (1 at 100, 50 at 30). That is the defect the bound fix answers.
- Carry 5, the self-test at origin/main's bound. This head's file with only the loop bound reverted to main's `range(1, ghapi.MAX_PAGES + 1)` prints `selftest: 14 checks, 1 failed pages['many1760']` with rc 1. The 1760 case fails there because main's bound is the measured defect. The 70-job case passes there, because main's fallback handles 70 jobs; it fails only when the fallback is deleted (Mutation proof). `clean` passes under both. At this head: `selftest: 14 checks, 0 failed`, rc 0. origin/main's own file, unchanged, prints its own `selftest: 12 checks, 0 failed`.
- Null controls inside the self-tests, each at the head:
  - a 404 refuses after exactly 1 call;
  - a 422 refuses after exactly 1 call;
  - a body that does not parse refuses after 1 read;
  - a write argv is never run;
  - each `NON_JSON` near-miss is refused (a prefix, a suffix, a different JSON error, an empty or overlong character, and a status line that decides first).

## Figures

- `python3 -I tools/audit/seat/gh_read_run.py --self-test`: `gh_read_run self-test: 13 checks, 0 failed`.
- `python3 -I tools/release/stamp.py --self-test`: `RESULT stamp_self_test=pass`, with 12 `carry 6` arms.
- `python3 -I tools/audit/seat/record_row.py --self-test`: `gh_read self-test: 138 checks, 0 failed` and `record_row self-test: all checks passed`.
- `bash tools/pr/app_approve.sh --self-test`: `app_approve self-test: 322 checks, 0 failed`. The bash twin is unchanged: `NON_JSON` is the Python twin's own, because app_approve.sh's reads pass no `--jq` to gh.
- `python3 -I dev/audit/harnesses/r10_codescan_wait_race.py --selftest`: `selftest: 14 checks, 0 failed`. The 14 are measure()'s 8 counts, the rows check and the 5 `pages()` checks (fallback, clean, 4xx, over50, many1760).
- `python3 -I dev/audit/harnesses/r10_red_list_lag.py --selftest`: `selftest: 5 checks, 0 failed`.
- `node tools/policy/field_coverage.mjs`: `FIELD COVERAGE ok`, `refused=0`, with both newly pinned files declared.
- `python3 tools/pr/ci_predict.py --apply-inert`: it wrote the two INERT READS entries (`gh_read_run.py`, `r10_red_list_lag.py`) and then printed `CI PREDICT: no closures, fast, governance or instrument red predicted`.
- `python3 dev/audit/harnesses/r10_gh_read_retry_mutants.py --list`: refuses at this head and at origin/main 17e621f08 (`EQUIVALENT entries no rule generates`). Its figure at 2e9a02245 was `RESULT mutants=360 killed=346 equivalent=14 survivors=0`, wall time 7m57s; see Mutation proof.
- `python3 tools/pr/ci_predict.py` at the head: `CI PREDICT: no closures, fast, governance or instrument red predicted against 51cd5ec8a42a (a data-file read is not seen)`.
- `python3 -I tools/audit/seat/mutant_run.py --diff 17e621f08c4feec724478573741fbd8b596ceaba...HEAD --cmd "$MUTANT_CMD" --max-mutants 0 --report-only`: rc 0, 26 `SURVIVED` lines (`grep -c '^SURVIVED'`), the same 26 sites as at 2e9a02245, wall time 89 s. `MUTANT_CMD` is `bash -c` over `stamp.py --self-test | grep -q "RESULT stamp_self_test=pass"`, `gh_read_run.py --self-test | grep -q ", 0 failed"` and `sys.exit(gh_read.self_test())`.
- `python3 tests/closure.py select --diff 51cd5ec8a42abde3c223f22e9f4a0d5f35f8844a --workdir "$D"`: `MODE: SCOPED -- 3 script(s) run, 30 scoped out`, over 11 changed files. It names `tests/doc_claims.py` (`ALL 296 checks PASSED`), `tests/entities.py` (`ALL 2668 ENTITY CHECKS PASSED`, rc 0, 397 s) and `tests/harness_headers.py` (`ALL 112 HARNESS HEADER CHECKS PASSED`). The run_always lines: `tests/env_drift.py --claims-only 51cd5ec8a42a...` (`claims hygiene: ... ok`), `tests/closure.py selftest` (`ALL 118 closure shrink pins PASSED`), `tests/layout.py` (`layout self-test: ok`). `tests/closures.json` merged through LEDGER-MERGE (`inert_reads.tests/entities.py: merged as a set (68 entries)`, `inert_reads.tests/harness_headers.py: merged as a set (973 entries)`); its gate is the three scripts above plus prepr.sh's step, all re-run at this head.
- `python3 tests/structure.py`: `STRUCTURE RATCHET PASSED`.
- `python3 tools/audit/archscore/score.py --diff 51cd5ec8a42abde3c223f22e9f4a0d5f35f8844a`: `Architecture score: dS +0.0000 NULL`.
- Class seams in workflows. The rule `git grep -n 'gh api' -- .github/workflows` returns 24 single-shot `gh api` reads in 9 files at the merge base 17e621f08 (`git grep -n 'gh api' 17e621f08 -- .github/workflows | wc -l`): 7 in pr-contract.yml (the carry's own) and 17 in the other 8 workflows (arch-score, codeql, dependabot-automerge, dependency-graph, governance, nightly, pages, tests). All 24 are open in this diff and forward-carried below; the runner they need is the one this diff lands.
- Class seams over urllib. `git grep -nE "urlopen\(" HEAD -- tools` returns 5 lines:
  - `record_row.py:894`, its read: already behind `gh_read.retry`.
  - `record_row.py:1689`, its self-test stand-in: no call.
  - `tools/ci/ghapi.py:65` `_open`: behind `ghapi.get`'s 2/6 s GET retry, carry 7 of #2995.
  - `stamp.py:2583` `dispatch_record_beat`: a POST, outside the read rule.
  - `tools/audit/seat/outside_intake.py:104` `plan_live`: new on main since this branch's cut (absent at 73365699a). It is a single HEAD read of the Pages plan URL whose failure is reported as "not live" with its reason. It is not a GitHub API read and is not closed here; forward-carried.
  - `stamp.py` `get_rest` no longer matches: it reads through `gh_read.urllib_wait`, closed in this diff.
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
  - Carry: #2731
- The other 17 workflow `gh api` reads (`git grep -n 'gh api' -- .github/workflows`, less pr-contract.yml's) are the same class. Each can use the same runner where its job pins nothing, or with the same restore and DECLARED entries where it does. Re-run the enumerator at that group's merge base. Carry: #2731
- `dev/audit/harnesses/r10_gh_read_retry_mutants.py` refuses `--list` on origin/main 17e621f08: main's 0ccedc45d renamed `tools/pr/app_approve.sh`'s `gh_transient` call in the read loop to `"$_cls"`, and the harness's EQUIVALENT entry still names the old line. Re-key the entry (or derive it), then re-run the full sweep. Carry: #2731
- Carry 11, app_push.sh's push retry: `gh_read.run_git_retry` is now on main (0ccedc45d), so it can reuse that. Carry: #2731
- `tools/audit/seat/outside_intake.py` `plan_live`, a single-shot Pages read that main added after this branch's cut. Whether it belongs under the read rule is that file's owner's call. Carry: #2731
- Carries 8/10, measured here: pr-contract's red list missed 1 still-running red in 379 lists (2026-11-07T18:00Z onward, `dev/audit/harnesses/r10_red_list_lag.py`). The fix decision, and a re-run over the RCA's three incident windows, rest with the orchestrator. Carry: #2731

## Friction

- pr-contract-base-restore: cost: a grader the base runs cannot learn a registration in the pull request that needs it, so a new pinned grader takes two merges. The runner landed first, with its wiring carried. Carry: dismissed: the restore is the #1515 barrier working as designed, and field_coverage's `pending` key is the mechanism for exactly this
