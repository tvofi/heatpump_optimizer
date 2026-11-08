Part 2 of R10-TRAIN-MERGE-LOOP (#3242), repair round 2 after `Fix review: blocked 35fc2646` (class-open: `tools/pr/app_approve.sh` carry-path `git fetch` unretried). The round adds two commits on top of the reviewed head 35fc2646, which is unchanged beneath them; the head is 022a55fd. No main merge: `git merge-tree --write-tree origin/main HEAD` exits 0 against origin/main 17e115792590 (2026-11-08T00:29Z), and the owner ruling of 2026-11-07 merges main only on a conflict.

Carry N is the 1-based position in this group's carry list on the roster (handoff/audit-r10-roster); the parent's numbers are noted.
- Carry 15 (the hotfix): `wait_ci` treats a red `gate` as pending while another workflow run at the same head is unfinished (read from actions/runs?head_sha, not check-run presence), then allows one poll for gate.py's rerun cascade. Bounded by the polls. A held (`action_required`) sibling run is not unfinished: this round pins that.
- Carry 1, Carry 8 and Carry 16 (parent carry 3): a bot tip whose pull_request runs are all approved is no longer refused; held, absent or unreadable runs keep the BOT_HEAD refusal.
- Carry 2 and Carry 10 (parent carry 6): `merge_train.py add --wait-post-approval [--poll] [--budget-hours]`, one module-level predicate (gate runs started at or after the approval, head pin, red refusal rc 2, budget rc 3). This round pins the verdict-comment half of its predicate.
- Carry 3, Carry 7, Carry 9, Carry 11 and Carry 17 (parent carries 7 and 17): one git-transient rule for every git fetch/push the train reaches. This round moves the rule (`GIT_TRANSIENT`, `GIT_REFUSED`, `git_transient`) and its bounded loop (`run_git_retry`, `GIT_TRIES`) from merge_train.py into `tools/audit/seat/gh_read.py`, the module that already owns the train's GitHub-transport retry rule, and exposes it as `--classify-git` and `--git-retry` for the shell callers. The 18 merge_train.py fetch/push sites reach it through `Train._reads_retried`. `tools/pr/app_approve.sh`'s carry fetch (the blocked seam) now retries through its own read loop (`retry_with`, generalised from `read_with`), classified by `gh_read.py --classify-git`. `tools/audit/seat/remerge_main.sh`'s recarry fetch, a further seam the class census returned, runs under `gh_read.py --git-retry`. Before this, one 502 there printed `MERGE CONFLICT` and stopped the train.
- Carry 4 and Carry 12 (parent carry 8): `pages()` in r10_codescan_wait_race.py falls back to per_page=30 after ghapi.get's own 5xx retries.
- Carry 5 and Carry 13 (parent carry 9): undraft only a head recorded `draft: true` at add; a failed ready or a re-draft is a Stop. This round keys each arm's test on its own Stop text.
- Carry 6 and Carry 14 (parent carry 16): remerge_main.sh prints FAIL and `full log:` lines and keeps the push log when nothing was pushed.

Alternatives for the shared rule: (a) copy the regexes into app_approve.sh: rejected, because it would be a second copy of the classifier. (b) A new module: rejected, because gh_read.py already holds the train's transport rule and app_approve.sh already shells to it (`--classify`), and a new file would need its own closure classification. (c) app_approve.sh calling `--git-retry`: rejected, because its self-test stubs `sleep` on PATH and runs each case under a 10 s deadline, and a Python `time.sleep` would sleep for real. So app_approve.sh shares the classifier and keeps its read loop's 4-try 5/15/45 s schedule. merge_train.py and remerge_main.sh share both the classifier and the 3-try 5/15 s loop.

## Head

022a55fd2fff20b3f66278464e03a9612b5dda8a

## Mutation proof

- Carry fetch (the block): the pre-fix tree (35fc2646, plain `git fetch`) with the new self-test arms gives `bash tools/pr/app_approve.sh --self-test` = `322 checks, 3 failed`: "a carry whose first fetch failed with git's 502 is fetched again and approved", "after one transient failure and one settle", "after 4 fetches, naming the count". The same 3 checks go red with the carry fetch classified by `gh_transient` instead of `git_transient`, and with `git_transient() { return 1; }`. With `git_transient() { return 0; }` 2 checks go red: "REFUSE: a carry fetch git rejected is not fetched again (null control)" and "at once, with no settle".
- remerge_main fetch: with `python3 "$SEAT/gh_read.py" --git-retry` reverted to plain `git fetch`, `bash tools/audit/seat/pr_args.sh --self-test` = `179 checks, 1 failed`: "remerge_main: a fetch failing once with git's 502 is fetched again, and the clean merge is kept".
- The three survivors the review named, each with `python3 tools/audit/seat/merge_train.py --self-test` (`521 checks, 1 failed` each at the first commit). `action_required` dropped from gate_deferred's exclusion: "a held sibling run (action_required) is not unfinished: the red gate returns on the first poll". `if not (at and said)` changed to `if not at`: "post-approval wait: an approval review with no `Fix review: merge <head>` comment beside it waits to the budget (rc 3), naming the missing verdict". undraft's `if code:` changed to `if False:`: "a failed gh pr ready is its own undraft Stop, naming the call and its output, no merge".
- The diff-mutant step's survivors at the first commit, pinned in the second. `said = False` changed to `said = True` in post_approval_wait's unparseable-listing arm: "post-approval wait: an unparseable comment listing is no verdict: it waits to the budget (rc 3)" red (`523 checks, 1 failed`). The `>=` on `started_at` changed to `>`: "post-approval wait: a gate run started at the approval's own second counts as the re-run (adds, rc 0)" red. The gh_read.py CLI, `_run_captured` and `run_git_retry`'s log survived because MUTANT_CMD ran only merge_train.py's self-test. gh_read's self-test now drives them (7 new checks), and the rerun with gh_read's self-test in MUTANT_CMD kills every one of them.
- gh_read census: with the `GIT_*` skip removed from `ALTERNATIVES()`, `gh_read.self_test()` = `122 checks, 2 failed` ("the table keys exactly the alternatives gh_read's source holds", "and every alternative but default holds both a transient input and a refused near-miss"): the gh twin census would read git's alternatives as gh's.
- Earlier rounds' proofs, unchanged code: hotfix deferral emptied, 4 red; runs_approved forced False, the approved-runs arm red; started_at filter dropped, red; git_transient forced False, the transient and retry arms red; admission condition dropped, red; `pages()` fallback removed, harness --selftest crashes with ApiError 502; mut:remergegrep, red.

## Null control

A rejected carry fetch (`couldn't find remote ref`) is one fetch, no settle, refused with git's text appended. A rejected recarry fetch is one fetch and still prints `MERGE CONFLICT 7`: a second fetch would have succeeded, so the arm shows it was not retried. A git rejection mixed with a 502 is not transient (merge_train's `_git_retry_self_test` table, now reading `gh_read.git_transient`). A red gate with no unfinished sibling run still returns red on the first poll. A review plus a `Fix review: merge <head>` comment with a green post-approval gate adds (rc 0). A re-drafted head stops as "is a draft again", not as a failed ready.

## Figures

- `python3 tools/audit/seat/merge_train.py --self-test` prints `523 checks, 0 failed` at this head (35fc2646: 519; +4 arms, and 2 undraft arms re-keyed).
- `bash tools/pr/app_approve.sh --self-test` prints `322 checks, 0 failed` at this head (3 new carry-fetch arms carry 6 checks).
- `bash tools/audit/seat/pr_args.sh --self-test` prints `179 checks, 0 failed` at this head (35fc2646: 177; +2 remerge fetch arms).
- `python3 -c "import sys; sys.path.insert(0,'tools/audit/seat'); import gh_read; sys.exit(gh_read.self_test())"` prints `gh_read self-test: 129 checks, 0 failed` (35fc2646: 122; +7 git-rule checks).
- `python3 tests/structure.py` prints STRUCTURE RATCHET PASSED; no budget file is in the diff.
- `python3 tools/audit/archscore/score.py --diff 35fc2646348b9c4d69a3b56b6452ff4075289807 HEAD` prints `Architecture score: dS +0.0000 NULL`.
- Class census (fixer step 8), rule: `git grep -nE '"git", *"(fetch|push)"|git (-C [^ ]+ )?(fetch|push)\b' -- tools/pr/app_approve.sh tools/audit/seat/merge_train.py tools/audit/seat/train.sh tools/audit/seat/remerge_main.sh`, outside each file's self-test. It returns 18 `self.run`/`self.ok` git fetch/push sites in merge_train.py above `_self_test` (17 fetches, 1 push; counted by piping the merge_train.py hits through `awk` on line < `_self_test`'s line and `grep -c 'self.run\|self.ok'`), which are closed through `Train._reads_retried` → `gh_read.run_git_retry`. It returns app_approve.sh's carry fetch, closed in this diff. It returns remerge_main.sh's recarry fetch, closed in this diff. train.sh returns none. The census also reaches app_push.sh's pushes, which the train runs through remerge_main.sh. They are outside this group's files, and app_push.sh's read-back rule already confirms a push. A distinct finding is carried under Forward-carry.
- Diff mutants: `tools/pr/prepr.sh` with `MUTANT_CMD="bash -c 'python3 tools/audit/seat/merge_train.py --self-test && python3 -c \"import sys; sys.path.insert(0, \\\"tools/audit/seat\\\"); import gh_read; sys.exit(gh_read.self_test())\"'"` (mutant_run.py --diff over the diff's added lines, its default cap of 40 mutants) prints `WARN diff mutants 4 survivor(s)`. The whole prepr run took 2087 s of wall time. The same prepr whose mutant baseline failed at once (record_row.py's self-test fails inside mutant_run's git-archive copy on a Node body check) took 683 s, so the mutant step is about 1400 s of that. The first run, with merge_train's self-test alone, printed 13 survivors: 11 in gh_read.py, which that command never runs, and 2 in post_approval_wait. Each is pinned under Mutation proof.
- prepr: `PYTHONPATH=tests/hastub PREPR_SKIP_CLOSURES=1 bash tools/pr/prepr.sh` prints `PRE-PR: 022a55fd2fff20b3f66278464e03a9612b5dda8a ... rc=0` at this head. Its only WARN is the diff-mutant line, and its scope line is `MODE: SCOPED`. origin/main moved after the run, and per the owner ruling it is not merged (merge-tree clean).
- Not measured, carried: the carry 1 measure-first count (BOT_HEAD stops since 2026-10-20, and how many had their runs approved at refusal) needs the train logs on the orchestrator's machine. This container has none.

## Unpinned sites

Each of the 4 survivors of the final diff-mutant run is on a self-test line in gh_read.py, not a production line. Each disposition below is a test-scaffolding equivalent: a mutant of a test's own assertion is caught by nothing but a test of the test.
- `tools/audit/seat/gh_read.py` `self_test`, the `run_git_retry` fixture `(1, "error: RPC failed; HTTP 502")`, CONST_SWAP 1 to 2: equivalent. Any non-zero exit is a failure to the loop.
- `tools/audit/seat/gh_read.py` `self_test`, the `_run_captured` check, CALL_DEL: the check call deleted. Vacuous, test scaffolding.
- `tools/audit/seat/gh_read.py` `self_test`, the `--classify-git` check, CALL_DEL: as above.
- `tools/audit/seat/gh_read.py` `self_test`, the `--git-retry` non-git argv check, CALL_DEL: as above.

## Red checks

Read from `pulls/3288` check-runs (filter latest, 94 runs, one page) at 35fc2646 on 2026-11-07, read after 22:30Z: every latest check-run is success or skipped. The concluded reds at 35fc2646 (filter all) are listed below by literal check-run name. Each was re-run green at that head, and none is caused by this diff:
- tests / coverage (128454571205): class runner stall ("The hosted runner lost communication with the server"). Re-run 128492818833 succeeded. Cheaper detector: none exists; this is GitHub infrastructure.
- tests / coverage-ratchet (128473127824): class consequence of the coverage stall (artifact `coverage-json` missing). Re-run 128495969221 succeeded. Cheaper detector: none; it is downstream of the stall.
- tests / nightly-status (128447471717, 128454570948): class main-graded reporter (a cancelled main verification dispatch). Re-run 128492818270 succeeded. It is not in the required set. Cheaper detector: none for a main-side cancel.
- pr-contract / pr-contract (128474383637): class body gap (the body did not name the two coverage reds). Later runs 128497175481, 128497835304 and 128498295968 succeeded. Cheaper detector: `tools/pr/prepr.sh --body-check`, one run per body push.
- gate (128474546962, 128451186144, 128448800913): class aggregate of the above. Later gates 128497380614, 128498034328, 128498498368, 128498735667 and 128498740508 succeeded.
At this head (022a55fd) no CI has run: it is pushed to the handoff ref only.

## Forward-carry

- The measure-first count parent carry 3 requires (BOT_HEAD stops in the train logs since 2026-10-20, and how many had their pull_request runs approved at refusal time) needs the orchestrator's train logs, the same raw train timelines that R10-TRAIN-REJOIN-NO-RECARRY's waste-study measurement reads. That group is not started, and its files are merge_train.py and train.sh, this seam. Carry: R10-TRAIN-REJOIN-NO-RECARRY
- The gate-race hotfix (Carry 15) has no committed finder harness. Its only pin is `_gate_race_self_test`, and the reviewer's own gate-race harness is review evidence, not tree. R10-HOTFIX-TRAIN-DEFER-WAIT (#3290) owns the same false-red-gate defect with a measured finder census (56 `ci red=['gate']` SKIPs over 2026-11-05..07), and its harness is the finder's. Carry: R10-HOTFIX-TRAIN-DEFER-WAIT
- remerge_main.sh prints `MERGE CONFLICT` for any failure of its fetch/reset/merge chain, so a spent transient budget or a rejected fetch is still misreported as a conflict, and the train's Stop says "main does not merge without a resolution". This is a separate diagnosis defect on the recarry seam (the transient case is closed here). Carry: R10-TRAIN-REJOIN-NO-RECARRY
- app_push.sh's `git push` on the recarry route is outside this group's files; its read-back rule confirms a landed push, but a transient push failure is not retried on git_transient. Carry: R10-FLY-GH-READ-RETRY
- Out of scope, from the review: post_approval_wait does not check the verdict nonce. Carry: dismissed: the approver-login filter, the exact-head match and the head pin bind the verdict to this head, and a nonce authenticates a dispatch, not a head.

## Friction

none
