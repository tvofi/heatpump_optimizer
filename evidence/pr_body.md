R10-TRAIN-MERGE-LOOP part 1, repair round 2 of the `Fix review: blocked 40019c52e` verdict (carry-unanswered). It builds the five things the owner ruled for this round. Carry 2: one Actions job-log reader for the tree. Carries 14 and 15: batch by default, and record PRs ride the stamp. Carry 18: the instrument page states the train.sh default. Carry 19: every arm. It also kills the `same_tree_posting` fetch mutant (R5). Carries 3, 6, 7, 8, 9, 16 and 17 go to part 2 (R10-TRAIN-MERGE-LOOP-2, on the roster now; `## Forward-carry`). Refs #2715 #3137; both stay open for part 2.

Carry status, 1-based (`git show origin/handoff/audit-r10-roster:dev/programme/rosters/wave-r10-groups.json`, group R10-TRAIN-MERGE-LOOP, 19 carries, Carry N is the Nth element of its `carry` array, element N-1 counting from 0). Every number in this body is 1-based. An earlier version of this body mixed in 0-based numbers ("Carries 0 and 1", "9-12" for the #3090 block); those are removed. The old body's dispositions were re-decided on the tree, and none was wrong. Its numbering was.
- Carry 1 (review settle bounded by time, P331): on main. `git merge-base --is-ancestor d69619360 origin/main` succeeds. `review_settle` and `policy_refusal` are at merge_train.py:2359 and :2279 at the head, with the carry's fixtures in the self-test. Nothing is built here.
- Carry 2 (one job-log reader): built here, `job_log` in merge_train.py; the failing-test-first proof and mutants merge_train-45, 46, 54 and 55 are below.
- Carry 3 (bot tip, run still action_required): forwarded to R10-TRAIN-MERGE-LOOP-2 (`## Forward-carry`).
- Carry 4 (a cured pre-flight park rejoins at the same verdict): built here, at 6e3a59b29 (`git merge-base --is-ancestor 6e3a59b29 origin/handoff/r10-train-merge-loop` succeeds). `Train.preflight_entry` is the shared pre-flight and `PREFLIGHT_PARK` is in `READMIT_SAME_VERDICT` (merge_train.py:816). The arm "carries 3/18: a cured pre-flight park rejoins at the same verdict (ADDED, spooled); the uncured one ..." is killed by merge_train-44 and merge_train-48. That commit's message labels this "Carries 3/18"; those are its 0-based numbers, and the roster's 1-based carry is 4.
- Carry 5 (same-tree commit after the posted verdict): built here, at 6e3a59b29, `same_tree_posting` (merge_train.py:2625) called from `posted_verdict` (:2644). Its fetch-failure arm is added here. Killed by merge_train-43 (drops the tree comparison) and merge_train-47 (fetch failure check). That commit's message labels it "Carry 4", which is 0-based.
- Carries 6, 7, 8 and 9 (the hand-written add scripts and the three stranded carries): forwarded to R10-TRAIN-MERGE-LOOP-2.
- Carry 10 (R10-FLOW-POSTMERGE brief, after-merge bookkeeping; moved from R10-TRAIN-POSTMERGE): implemented by #3090. Its merge commit 38dcb6c5d is an ancestor of origin/main and of this head (`git merge-base --is-ancestor 38dcb6c5d origin/main` and `... origin/handoff/r10-train-merge-loop` both succeed). The carry says it is discharged when #3090 merges and the fixer builds nothing twice. The `OWED` / `set-stage owed` bookkeeping is in merge_train.py at the head (:2274, :4711 with its self-test at :4717).
- Carry 11 (part 2 of the group, and P312's drain order): implemented by #3090, merge commit 38dcb6c5d. `Train.queue_take` honours priority then critical path then arrival; its self-test rows are at merge_train.py:7530-7590. Nothing is built here.
- Carry 12 (`set-stage owed <GROUP> <merge sha>`, group from the roster): implemented by #3090, merge commit 38dcb6c5d, using `roster_lib.group_for_branch` (roster_lib.py:531). Nothing is built here.
- Carry 13 (P312, `add --priority N` and the stable sort): implemented by #3090, merge commit 38dcb6c5d. `--priority` is at merge_train.py:7705 and :3215 and exercised at :7559. Nothing is built here. This head's mutant merge_train-42 re-anchors on the drain order carry 14 adds.
- Carries 14, 15, 18 and 19: built here (designs and mutants below: 14 is merge_train-49, 15 is 50-53, 18 is checked by the `git grep` pair under `## Null control`, 19 is 44 and 48 plus the new arms).
- Carries 16 and 17: forwarded to R10-TRAIN-MERGE-LOOP-2.
Tally: 1 on main; 10, 11, 12, 13 by #3090; 2, 4, 5, 14, 15, 18, 19 built here; 3, 6, 7, 8, 9, 16, 17 forwarded. That is 19. The group R10-TRAIN-MERGE-LOOP-2 is on the roster now (added with #3239, `resume.stage` not-started, `after` R10-TRAIN-MERGE-LOOP, files merge_train.py and train.sh, 7 carries, which are exactly 3, 6, 7, 8, 9, 16, 17 in order).

Carry 2 design. `job_log(run, repo, job_id)` passes `--allow-escape-sequences` first. When gh refuses that as `unknown flag` (gh 2.89, measured below), it reads the same log without the flag. Any other failure returns None, so no caller judges an unread log. Two alternatives lost. Flag-only fails on gh 2.89. No-flag-only fails on the gh the R9-RO-12 proof measured. Either one alone leaves one gh with a reader that reads nothing, and the review measured exactly that disagreement. `merge_train.py job-log <job id> <owner/repo>` is the same reader for shell callers. infra_rerun, gate_raise_only and culprit read through it. So do the seven outside sites the enumerator returns (`## Figures`, class seams). The `gh` helper in probe_bridge.py was used only for that read, so it is deleted.

Carry 14 design. When `train_add` starts a train, `Train.ready_batch` adds every other ready verdicted PR to its first batch. A sweep hands over its own queue. A bare add reads `build_queue`. An unreadable queue starts over the add's own entry and logs `BATCH-READ`, so a read failure never blocks a start. A sweep's second add for a PR now in the started train is `ALREADY` (pending). The two sweep checks that pinned the old one-PR start now pin the batch.

Carry 15 design. The record predicate is `record_pr`: stamp.py's `record_class_paths` classes, plus the programme's own record paths (triage batches, HANDOVER.md, rosters). Those three are the carry's "triage batches, record/HANDOVER PRs, roster landings". Every path must be a record, and there must be at least one. `merge_fastpath.file_class`, which the carry names, has no record class: it classifies refusal routes (workflow, claim, grader, budget). So the predicate reuses stamp.py's rather than adding a second copy there. `queue` and `sweep` read the files from the PR list's own `files` field, so they make no extra call. `add` reads them with one `gh pr view --json files`. An unreadable list is not held. That is the fail-open direction: a record merged singly costs one gate run, while a production PR held waits for a stamp. `--stamp` on `queue`, `add` and `sweep` admits the records. The stamp seat's `merge_train.py queue --stamp` then `train.sh --queue` merges them in one batch before the tag. tools/release/stamp.py is untouched: it dispatches no merges, and no in-tree stamp launcher calls the train (`git grep -n 'merge_train\|train.sh' -- '*stamp*'` prints nothing). The `--bot-prs` record/autofix guard is unchanged.

Carry 18. tools/audit/seat/instruments/merge_train.py.md now states that a `train.sh` launch runs `RECOMMENDED`, names `RECOMMENDED` in merge_train.py as the flags' one definition, and says a caller passes none of them by hand. The one hand-passed instruction under instruments/ (`train.sh --bot-prs --approval-carry --pre-flight`, the sweep's started train) now reads "a bare `train.sh` launch".

Carry 19. The new self-test arms: a cured `policy` park rejoins, and uncured it is refused with no spool line. A cured `policy` park and a cured `findings` park each reach batch 2 through `queue_take`. A park at a new verdict is admitted with no pre-flight re-read and is drained. The existing arms stay: a cured and an uncured `findings` park, and a `ci` skip at the same verdict staying ALREADY.

## Head

`e836876f3dadc368a414ccc2b19126e78507f7d0` is this PR's head, unchanged: its code was already in it and main merged cleanly, so the orchestrator's script set this body without a push.

`23d83cad918b2310245f9fd1902a4b482befbf78`. The merge base is dc0a170b671814be196a54b1c71e29449f54d6d7. origin/main has since moved to 7e8939d38 (#3239, a roster-only merge); `git diff --stat dc0a170b6 origin/main -- tools/audit/seat tests dev/audit/harnesses` prints nothing, so the code under review is unchanged and this body-only continuation does not merge it.

## Mutation proof

Every row is a production-line mutant in `dev/audit/harnesses/r10_seat_selftests_mutants.py`. It is run as `python3 dev/audit/harnesses/r10_seat_selftests_mutants.py merge_train-42 … merge_train-55` at the head. The harness first runs the same step on the unmutated file, which must pass (the null control). Then it plants the mutant and restores the file.

| mutant | what it breaks | at the mutant | null control (unmutated) |
|---|---|---|---|
| merge_train-42 | the started train's drain order (re-anchored on carry 14's start line) | KILLED, `464 checks, 2 failed` | 0 failed |
| merge_train-43 | same-tree posting drops the tree comparison | KILLED, `464 checks, 1 failed` | 0 failed |
| merge_train-44 | `train_add` drops the pre-flight re-read | KILLED, `464 checks, 2 failed` | 0 failed |
| merge_train-45 | infra_rerun reads job logs without job_log (the carry-2 defect) | KILLED, `464 checks, 1 failed` | 0 failed |
| merge_train-46 | job_log drops the unknown-flag fallback | KILLED, `464 checks, 3 failed` | 0 failed |
| merge_train-47 | same_tree_posting's `git fetch origin verdict/<n>` failure check becomes `if False:` (the review's R5) | KILLED, `464 checks, 1 failed` | 0 failed |
| merge_train-48 | PREFLIGHT_PARK dropped from READMIT_SAME_VERDICT (the drain refuses a cured park) | KILLED, `464 checks, 4 failed` | 0 failed |
| merge_train-49 | carry 14: a started train's `others = []` | KILLED, `464 checks, 5 failed` | 0 failed |
| merge_train-50 | carry 15: build_queue holds no record | KILLED, `464 checks, 1 failed` | 0 failed |
| merge_train-51 | carry 15: `held_for_stamp` never holds at `add` | KILLED, `464 checks, 1 failed` | 0 failed |
| merge_train-52 | carry 15: `record_pr` drops the programme record paths | KILLED, `464 checks, 3 failed` | 0 failed |
| merge_train-53 | carry 15: `--stamp` no longer admits a record | KILLED, `464 checks, 1 failed` | 0 failed |
| merge_train-54 | gate_raise_only reads without job_log | KILLED, `464 checks, 1 failed` | 0 failed |
| merge_train-55 | culprit reads without job_log | KILLED, `464 checks, 1 failed` | 0 failed |

The checks each mutant reddens, by name, from the same run:
- merge_train-42: `FAIL P312 start path: a stopped train's spool [#13 critical, #11] plus `add #14 --priority` starts the tr…`; `FAIL P112 start path: `add #14 --front` over a spool whose #11 is a HOTFIX keeps first place, then the HO…`
- merge_train-43: `FAIL queue: null controls -- a tip whose tree differs (#18's case), and a same-tree commit that does not…`
- merge_train-44: `FAIL carries 3/18: a cured pre-flight park rejoins at the same verdict (ADDED, spooled); the uncured one…`; `FAIL carry 19: a cured `policy` park rejoins at the same verdict (ADDED, spooled); uncured it is ADD REFU…`
- merge_train-45: `FAIL carry 2: infra_rerun reads its job logs through job_log, so a gh that needs --allow-escape-sequences…`
- merge_train-46: `FAIL carry 2: gate_raise_only reads the raise-only suites under a gh that needs the escape flag and under…`; `FAIL carry 2: infra_rerun reads its job logs through job_log, so a gh that lacks --allow-escape-sequences…`; `FAIL carry 2: job_log passes the flag first, reads without it only where gh does not know the flag, and r…`
- merge_train-47: `FAIL queue: null control -- the same same-tree descendant waits when `git fetch origin verdict/<n>` fails…`
- merge_train-48: `FAIL P189 HOLDER arm, pre-flight: a PARK at `recarry` (the worktree holder) is recorded skipped [HOLDER]…`; `FAIL carries 3/18: a cured pre-flight park rejoins at the same verdict (ADDED, spooled); the uncured one…`; `FAIL carry 19: a cured `policy` park rejoins at the same verdict (ADDED, spooled); uncured it is ADD REFU…`; `FAIL carry 19: a cured `policy` park and a cured `findings` park, once added, reach the next batch throug…`
- merge_train-49: `FAIL carry 14: three ready pull requests and no live train -> `add` starts ONE train whose first batch is…`; `FAIL carry 14: an unreadable queue at the start still starts the add's entry, logged BATCH-READ…`; `FAIL carry 14: with no queue handed in, the add reads build_queue itself (the fixture's #11 #12 #15)…`; `FAIL sweep, no train live: ONE train starts over BOTH missed heads in its first batch (carry 14: batch by…`; `FAIL sweep, a train live: the next pass adds nothing and starts nothing (exactly once)…`
- merge_train-50: `FAIL carry 15: outside a stamp, the record pull requests (#12, #15: every path a record) are HELD-FOR-STA…`
- merge_train-51: `FAIL carry 15 at add: a record pull request added between stamps is HELD-FOR-STAMP, rc 0, nothing started…`
- merge_train-52: `FAIL carry 15: outside a stamp, the record pull requests (#12, #15: every path a record) are HELD-FOR-STA…`; `FAIL carry 15 at add: a record pull request added between stamps is HELD-FOR-STAMP, rc 0, nothing started…`; `FAIL carry 15: record_pr is every path a record and at least one; an empty list is not a record…`
- merge_train-53: `FAIL carry 15 at add: a record pull request added between stamps is HELD-FOR-STAMP, rc 0, nothing started…`
- merge_train-54: `FAIL carry 2: gate_raise_only reads the raise-only suites under a gh that needs the escape flag and under…`
- merge_train-55: `FAIL a red fast job naming a script owned by one entry's files drops that entry, and the rest are re-prov…`

Failing test first for carry 2. The two `carry 2: infra_rerun ...` arms were added before `job_log` existed, at 2bff1ae0c. Against that tree the self-test printed `449 checks, 1 failed`, and the failure was `FAIL carry 2: infra_rerun reads its job logs through job_log, so a gh that needs --allow-escape-sequences still re-runs the stamp's run once`. With `job_log` the same arms pass.

## Null control

- `python3 tools/audit/seat/merge_train.py --self-test` at the merge base dc0a170b6, from a detached worktree: `merge_train self-test: 443 checks, 0 failed`. At the head: `merge_train self-test: 464 checks, 0 failed`.
- carry 2 null: through the same reader, a gate red on a non-infra job is never re-run. This is a self-test arm and is green.
- carry 14 null: one ready PR (the add's own) gives a batch of one.
- carry 15 null: a production PR, meaning a record row beside code, is queued and starts its train, and is never HELD-FOR-STAMP.
- carry 19 null: a park at a new verdict behaves as today, and a `ci` skip at the same verdict stays ALREADY.
- R5 null: the same same-tree descendant is queued when the fetch succeeds. That is the existing arm, and it is green beside the new fetch-failure arm.
- carry 18: `git grep -c -- 'train.sh --bot-prs --approval-carry --pre-flight' <rev> -- tools/audit/seat/instruments` prints 1 at origin/main and nothing at the head. `git grep -c RECOMMENDED <rev> -- tools/audit/seat/instruments/merge_train.py.md` prints nothing at origin/main and 1 at the head.

## Figures

- gh flag behaviour, this seat: `gh --version` prints version 2.89.0. The same read with the escape flag added ahead of the path is refused client-side with "unknown flag: --allow-escape-sequences", which is the arm `job_log` falls back on (figure_lint refuses that command for exactly this reason). Without the flag, `gh api repos/tvofi/heatpump_optimizer/actions/jobs/127775984978/logs` gave rc 0 and 844474 bytes.
- job_log live, through the fallback: `python3 tools/audit/seat/merge_train.py job-log 127775984978 tvofi/heatpump_optimizer | wc -c` printed 844474. `python3 tools/audit/seat/merge_train.py job-log 1 tvofi/heatpump_optimizer` gave rc 1 (unread). probe_bridge's, ci_script_seconds', scan.py's and r10_replay_loopnorm's readers each returned the same log's 844472 characters. Characters, not bytes: the log holds multi-byte characters. r10_replay_loopnorm still tells a 404 apart (`HTTP 404` in the raised stderr).
- Class seams (fixer step 8), enumerator `git grep -n -E 'actions/jobs/[^ ]*/logs' HEAD -- '*.py' '*.sh'`. At origin/main it returns 11 lines. Each is dispositioned:
  - merge_train.py gate_raise_only, culprit, infra_rerun: closed in this diff (job_log).
  - tools/audit/seat/probe_bridge.py (the review's :256): closed in this diff.
  - dev/audit/harnesses/r10_ci_layout_p1/critpath_fetch.sh (:34): closed in this diff (`job-log`).
  - tools/audit/seat/failure_logs.sh, tools/audit/seat/autofix_statuses.sh (two sites), dev/audit/harnesses/r10_gate_stale_jobs/scan.py and dev/audit/harnesses/r10_replay_loopnorm.py: these pass the flag with no fallback, so they read nothing on gh 2.89. They are closed in this diff (`job-log` / job_log).
  - merge_train.py's self-test fixtures and tools/audit/seat/orchestrator_tick.py:3743: fixture strings, no read.
  At the head the enumerator returns job_log's own path, the fixtures, and the mutant harness's mutant strings.
  A second enumerator covers the other read form: `git grep -n -E 'run view[^|]*--log' HEAD -- '*.py' '*.sh'`. It returns only dev/audit/harnesses/k1725_blas_kernel_gap.py:45, a docstring that recounts a past measurement and reads nothing. The review's ci_script_seconds.py:65 (`gh run view --job N --log`) is closed in this diff.
- Self-tests of every script touched, at the head:
  - `python3 tools/audit/seat/merge_train.py --self-test`: `merge_train self-test: 464 checks, 0 failed`.
  - `python3 tools/audit/seat/probe_bridge.py --self-test`: `probe_bridge self-test: 8 checks, 0 failed`.
  - `python3 dev/audit/harnesses/ci_script_seconds.py --selftest`: `SELFTEST is_fast ... ok`.
  - `bash tools/audit/seat/failure_logs.sh --self-test`: `passed=7 failed=0`.
  - `bash tools/audit/seat/train.sh --self-test`: `train.sh self-test: ok`.
  - `python3 tools/audit/seat/r10_ledger_mutants.py --self-test`: `r10_ledger_mutants self-test: 135 checks, 0 failed`.
  - `bash -n` on autofix_statuses.sh and critpath_fetch.sh: rc 0.
- Instrument self-tests the closures reach, as CI runs them: `python3 dev/audit/harnesses/r10_seat_selftests_mutants.py M0`: every seat step in governance.yml's `instrument-self-tests` rc 0, `RESULT survivors=0`.
- Scoped gate: `python3 tests/closure.py select --diff $(git merge-base origin/main HEAD) --workdir D`. It prints `MODE: SCOPED -- 1 script(s) run, 32 scoped out`, and `scope.run` names `tests/entities.py`. `PYTHONPATH=tests/hastub python3 tests/entities.py`: `ALL 2632 ENTITY CHECKS PASSED`. run_always: `tests/env_drift.py --claims-only origin/main` printed `claims hygiene: origin/main ok`, and `tests/closure.py selftest` printed `ALL 118 closure shrink pins PASSED`.
- `python3 tests/structure.py`: `STRUCTURE RATCHET PASSED`. No budget file is touched.
- `tools/pr/prepr.sh` on this body at the head: its one refusal is `carry`, the seven BAD-DEST lines to R10-TRAIN-MERGE-LOOP-2 (not yet on the roster when that run was made; it is on the roster now, see Carry status), and `ci predict` predicts those same seven on pr-contract. Every other step is ok or skip.
- VERSION, the manifest and the RELEASE_NOTES heading are untouched, and both claim files are byte-identical to origin/main: `git diff origin/main...HEAD --stat -- tests/golden VERSION RELEASE_NOTES.md custom_components/heatpump_optimizer/manifest.json` prints nothing.

## Architecture score

`python3 tools/audit/archscore/score.py --diff $(git merge-base origin/main HEAD)`: `Architecture score: dS +0.0000 NULL`.

## Unpinned sites

none: `tools/pr/prepr.sh` step 6d prints "the diff adds no unpinned mutation site"; every production site this diff adds is pinned by an in-tree mutant (merge_train-45..55 above).

## Red checks

- `gate`, check run 127775984978, at the previous head 40019c52e: concluded failure. Its log says "FAIL run(s) [42182598391] at this head are still being judged; their gate decides". Class: the deferring aggregator's run, which concluded before the runs it aggregates. It was superseded: `merge_train.py classify 40019c52e… --pr 3242` read `GREEN … red: none` once CI concluded, as the review's ev/classify.log records. Root-cause answer: no cheaper detector exists. The aggregator defers by design and its later run is the detector.
- At this head (23d83cad918b2310245f9fd1902a4b482befbf78): re-read 2026-11-06 across all 55 check runs (`get_check_runs`, perPage 100, one page). Every run has concluded; none is a failure: 32 success, 23 skipped. Named: `gate` (two runs, 127786694602 and 127787006291) success, `pr-contract / pr-contract` success, `tests / fast (3.14)`, `tests / closures`, `tests / mutation`, `governance / instrument-self-tests`, `governance / policy-docs`, `arch-score / arch-score`, `budget-raise-gate / budget-raise-gate`, `hassfest / hassfest`, `validate / validate-hacs` and `CodeQL` with the three `codeql / Analyze` jobs all success. No concluded red exists at this head, so there is nothing to name.

## Forward-carry

- Carry 3, "From #2394 (R10-CI-AUTOFIX-INERT-ROUTE) body friction `merge-train-bot-tip`": split to part 2 by the owner side's ruling. The reasons are scope (part 1 is already carries 2, 14, 15, 18 and 19 across 12 files), keeping part 1 reviewable, and the three-round rule. The group is queued on the roster and is applied once #3239 merges. Carry: R10-TRAIN-MERGE-LOOP-2
- Carry 6, "Re-routed by triage P359 from R10-FLY-TRAIN-DEFAULTS … the merge seat hand-writes s9/seat-merge/add<N>.sh": split to part 2 for the same three reasons. It lands in the group's brief in `dev/programme/rosters/wave-r10-groups.json` (handoff/audit-r10-roster), where the group is queued, not yet written. Carry: R10-TRAIN-MERGE-LOOP-2
- Carry 7, "Re-routed by triage P359 … STRANDED CARRY 31": split to part 2 for the same three reasons. It lands in the group's brief in `dev/programme/rosters/wave-r10-groups.json` (handoff/audit-r10-roster), where the group is queued, not yet written. Carry: R10-TRAIN-MERGE-LOOP-2
- Carry 8, "Re-routed by triage P359 … STRANDED CARRY 32": split to part 2 for the same three reasons. It lands in the group's brief in `dev/programme/rosters/wave-r10-groups.json` (handoff/audit-r10-roster), where the group is queued, not yet written. Carry: R10-TRAIN-MERGE-LOOP-2
- Carry 9, "Re-routed by triage P359 … STRANDED CARRY 60": split to part 2 for the same three reasons. It lands in the group's brief in `dev/programme/rosters/wave-r10-groups.json` (handoff/audit-r10-roster), where the group is queued, not yet written. Carry: R10-TRAIN-MERGE-LOOP-2
- Carry 16, "From triage P353 (merge seat, #3052 recarry refused by prepr": split to part 2 for the same three reasons. It lands in the group's brief in `dev/programme/rosters/wave-r10-groups.json` (handoff/audit-r10-roster), where the group is queued, not yet written. Carry: R10-TRAIN-MERGE-LOOP-2
- Carry 17, "From #2639 (body, item bb2965c2), routed by routing audit 1": split to part 2 for the same three reasons. It lands in the group's brief in `dev/programme/rosters/wave-r10-groups.json` (handoff/audit-r10-roster), where the group is queued, not yet written. Carry: R10-TRAIN-MERGE-LOOP-2

## Friction

- frugal-inline-guard: cost: this seat's cost-routing hook refused direct reads past five a turn, mid-build. Reads were routed through cheap workers instead, and nothing was skipped. The hook is outside this repository, so a carry here has nothing to land on. Carry: dismissed: session plugin outside this repository
- seat-identity: contradiction: the dispatch's setup line pins the identity `seat` and its brief's last line names `hpo-fixer`. The commits use `seat`, as this branch's earlier fixer commits do, because the setup line is the one that gives the command. Carry: dismissed: orchestrator payload wording, not a tree rule

