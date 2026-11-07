R10-HOTFIX-SELFTEST-TIMEOUT. `governance / instrument-self-tests` ran its steps in line under `timeout-minutes: 30` and spent most of its wall time in five self-tests: prepr.sh's, beatd.py's, and pr_args.sh's alone and again through open_pr.sh and update_pr.sh, which each run it. Only prepr.sh's of the five keeps a core busy; the other four wait. They start detached in the job's first step, each to its own log and exit-status file. Five steps near the end of the job, under their old names, print each log, fail on its status and grep the same tally lines. The job lasts as long as the longer of its in-line steps and the detached work, instead of the sum of both. The timeout stays 30: no raise.

The three pr_args.sh callers run one after another in a single detached chain, and prepr.sh's self-test runs at `nice -n 10`. With all five at once, pr_args.sh's `mut:unlock` arm failed once in nine observations: it checks for a lock holder inside the 0.2 s poll the holder takes to notice that its parent has gone, and CPU contention shortens that window. Chained, they keep the order they had in line.

Alternatives, and why each lost:
- **Matrix shards** of the job would rename its check runs to `governance / instrument-self-tests (<shard>)`. That name is read in tools/pr/ci_predict.py's `JOB` table and by tools/audit/round4/D11/governance_cost.py's `bare()`, and each shard repeats checkout. Separate jobs fail tests/entities.py's census, which ties governance.yml job ids to governance_cost.py's `GOV`, until a file outside this group names them.
- **Dropping the standalone pr_args.sh step** would remove a step, and would leave pr_args.sh's tally to two callers outside this file.
- **Cutting prepr.sh's own cost** was not needed for the headroom: the detached run already takes it off the critical path.

Repair round 3 (review blocked a09ebaeb, mutation-vacuous, mutant W1). Deleting the waiter step `Show the pre-PR self-check refusing its own fixtures` survived every check: the launcher line still counted as wiring for selftest_wiring.py, and the harness read only the bg_* library. In CI, prepr.sh's self-test would have run detached with its exit status unread and the job green. The cure is the one the verdict names, in this group's own file:
- `bg_wait` writes a `<name>.read` marker when it reads a status.
- A new library function, `bg_unread`, lists every `<name>.pid` the launcher wrote with no `.read` beside it, prints `bg_unread: <started> started, <unread> unread`, and fails if any is unread.
- A new last step of the job, `Refuse a detached self-test whose status no step read`, runs `bg_unread` under `if: ${{ !cancelled() }}`.

Deleting a waiter step, deleting its `bg_wait` line (the verdict's mutant A), or replacing a waiter with an echo of a fake tally (mutant D) now each leave a name unread, so the job itself goes red on main as well as at review. The harness gains the matching arms and mutants, and a shape check that the job's last step is that one.

## Head

Head 81ccb60da92ba016bd8f445ce43db368f2738d4c. It is the reviewed head a09ebaebd4f892729d96f24c7ec930ab6a12a37b, plus three commits:
- the cure commit 2a3a6998c1df6dd6692d7b54d956575c7c91624e;
- ec8c58a9446b68540d5fe2dc638f2461e5e8ce38, merging origin/main 1c1ae100b59e29564c7aec069b257dface6ef50f (fetched 2026-11-07 15:25:51 UTC). Main's commits there change nothing under tools/ or .github/ except tools/policy/agreement.mjs, which no figure below runs;
- 81ccb60da, merging origin/main 4b5d771bdf8feb1f83d7d9443e5117b771a0ab76 (fetched 2026-11-07 16:12:57 UTC), because main moved during the first prepr.sh run. That merge adds only dev/programme/delivery/3272.md and dev/programme/triage/s6-batch128.md.

Both merges were clean. The three-dot diff is unchanged by either: .github/workflows/governance.yml, dev/audit/harnesses/r10_selftest_timeout.py, dev/programme/delivery/3275.md and tests/closures.json. The harness, the replays, the gate and structure.py were taken at ec8c58a9. 81ccb60da differs from it only by those two record files, which none of them reads. prepr.sh and the body check were re-run at 81ccb60da.

## Mutation proof

`python3 dev/audit/harnesses/r10_selftest_timeout.py` reads the bg_* library out of the launcher step as committed, drives it over planted commands, and checks the job's last step. At the head:
- M0, the library as committed: all 14 lines PASS. That is the 10 arms from earlier rounds, plus `refuse unread`, `names unread`, `control all read` and `shape last step reads bg_unread`. The three new arms start the job's five names, wait on four, refuse and name the fifth (`UNREAD prepr:`), then wait on it and pass.
- W2, the job's last step deleted: KILLED by `shape last step reads bg_unread`.
- M1, `bg_wait` returning 0 in place of the recorded status: KILLED by `refuse slow bad`, `refuse chained bad` and `refuse bad`.
- M2, `bg_wait` returning 0 for a launcher gone with no status: KILLED by `refuse chain killed` and `refuse killed`.
- X8, `bg_wait` returning 0 after its first poll finds the command still running: KILLED by `refuse slow bad` and `control all read`.
- M3, `bg_wait`'s read marker `: > "$d/$1.read"; ` deleted: KILLED by `control all read`.
- M4, `bg_unread`'s verdict `test "$u" -eq 0` replaced by `true`: KILLED by `refuse unread`.
- `RESULT survivors=0`, rc 0.

Failing first: the same harness run from a detached checkout of a09ebaeb (the workflow before the cure) prints `M0 FAIL names unread`, `M0 FAIL control all read`, `M0 FAIL shape last step reads bg_unread`, `M3 NOT APPLIED`, `M4 NOT APPLIED`, `RESULT survivors=2`, rc 1.

W1 in the job itself: `python3 dev/audit/harnesses/r10_selftest_timeout.py replay <W1 workflow> bg`. The W1 workflow is governance.yml with the prepr waiter step removed by a `yaml.safe_load`/`safe_dump` filter on its name. At the head the last step fails, printing `bg_unread: 5 started, 1 unread` and `UNREAD prepr: no step read its status`, then `RESULT replay_seconds=610 failed=1`. At a09ebaeb the same mutant gives `RESULT replay_seconds=605 failed=0`. That is the verdict's W1, reproduced at the old head and killed at the new one.

## Null control

- Each refusal arm has its passing control in the same run: `control ok`, `control tally`, `control chained tally`, `control slow ok` and, for the new arms, `control all read`. A library that refused everything would fail them.
- The unmutated head replay (`... replay .github/workflows/governance.yml bg`) passes every step, the new last step included: `RESULT replay_seconds=616 failed=0`. So `bg_unread` does not refuse a job whose five statuses were all read. Its refusal under W1 is the other end.
- Every job step still runs and greps its `checks, 0 failed` line. The five waiter steps keep their names, and their grep lines are byte-identical to the base's.
- `python3 -I tools/audit/seat/selftest_wiring.py --check` prints `118 self-testing, 118 wired, 0 unwired` and `0 index gap(s)`, rc 0.

Seams of the class, a detached self-test whose status nothing reads. The enumerating rule is the started names against the waited names in governance.yml:
- `{ grep -oE '^ +bg_start [a-z-]+ ' .github/workflows/governance.yml | awk '{print $2}'; grep -E '^ +bg_pid "\$!" [a-z]' .github/workflows/governance.yml | sed -E 's/^ +bg_pid "\$!" //' | tr ' ' '\n'; } | sort` gives `beatd open-pr pr-args prepr update-pr`.
- `grep -oE '^ +bg_wait [a-z-]+' .github/workflows/governance.yml | awk '{print $2}' | sort` gives the same five.

All five are closed in this diff: each is read by its waiter step, and `bg_unread` refuses any that is not. The rule's null control is W1, where the started set keeps `prepr` and the waited set loses it, and `bg_unread` names it. In CI, `bg_unread` is the same rule at run time, over the `.pid` files the launcher actually wrote.

## Figures

- Harness at the head: `python3 dev/audit/harnesses/r10_selftest_timeout.py` gives 14 of 14 M0 PASS and `RESULT survivors=0` over W2, M1, M2, X8, M3 and M4, rc 0 (Mutation proof). The same file run from a09ebaeb gives `RESULT survivors=2`, rc 1. The harness sha1 at the head is `0196700d5c0e348f72671cc07f8ec82686103285` (`sha1sum`).
- Job replay, head: `python3 dev/audit/harnesses/r10_selftest_timeout.py replay .github/workflows/governance.yml bg` gives `RESULT replay_seconds=616 failed=0`. Per step: prepr waiter 365.3 s, PR opener 0.0, PR argument builder 45.0, supervised beat 0.0, PR updater 205.1, the new last step 0.0. The total is the replay's own `replay_seconds` line. Earlier rounds' figures stand as cited there: a base replay of 1870 s, and CI at d6482b704 of 631 s of 1800 s.
- Job replay, W1: 610 s with `failed=1` at the head, and 605 s with `failed=0` at a09ebaeb (Mutation proof).
- CI at a09ebaeb, the reviewed head with the same five-step layout: code run 42380487764, `governance / instrument-self-tests` job 128427022752 ran 14:12:54Z to 14:23:30Z, which is 636 s of the 1800 s timeout. That is completedAt minus startedAt from the PR's check runs. The cure adds one step that reads files and sleeps nothing, timed at 0.0 s in both replays.
- `mut:unlock` chained, under the rule "each pr_args.sh caller's waiter passed its `pr_args self-test: [1-9][0-9]* checks, 0 failed` grep". 13 of 13 before this round, by the verdict's count. This round's three local replays (head, W1 at the head, W1 at a09ebaeb) each passed all three pr_args waiter steps, for 9 of 9. The total is 22 of 22, which bounds the failure rate only to below about 1 in 7 (95%, rule of three: 3/22). It is not a measured rate, and it is carried below.
- Scoped gate: `GATE_SCOPE=auto GOLDEN_MODE=drift GOLDEN_REF=$(git merge-base origin/main HEAD) ./tests/run.sh` prints `MODE: SCOPED -- 2 script(s) run, 31 scoped out.` and `5 TEST SCRIPT(S) PASSED; 30 SCOPED OUT AND NOT RUN`, rc 0, with `ALL 2645 ENTITY CHECKS PASSED` and `ALL 112 HARNESS HEADER CHECKS PASSED`. `tests/closure.py select` names `tests/entities.py` and `tests/harness_headers.py`.
- `python3 tests/structure.py` prints `STRUCTURE RATCHET PASSED`.
- prepr: `bash tools/pr/prepr.sh` prints `PRE-PR: 81ccb60da92ba016bd8f445ce43db368f2738d4c ... rc=0` at the head. Its `ci predict` line reads `no closures, fast, governance or instrument red predicted against 4b5d771bdf8f`. origin/main had not moved past 4b5d771bd when it finished, so that run stands. The body passes `tools/pr/prepr.sh --body-check`, and `carry_audit.py check` reads 4 routed, 0 unrouted.

## Red checks

At the new head ec8c58a9 no CI run exists at handoff: the head is on the handoff ref only.

At the reviewed head a09ebaeb, the PR's check runs are 81, all on one page (`pull_request_read get_check_runs`, perPage 100, total_count 81). That tool takes no `filter` argument, so attempts were read per run with `actions_list list_workflow_jobs` and `filter: all`. Concluded reds:
- `gate`, edit run 42380487589, attempt 1, job 128427176656, failure at 14:25:41Z. Class: edit-run gate deferral. Its `Judge this head` step printed `FAIL run(s) [42380487764] at this head are still being judged; their gate decides` while the code run was in flight. Attempt 2, job 128437108588, concluded success at 15:02:27Z. Gate jobs 128431169741 and 128433055053, which the verdict names, are the same deferral in the later edit runs 42381808661 and 42382449320. Their latest attempts, 128437112022 and 128437116063, concluded success. Answer: a deferral to the code run, which concluded green. No code answer is owed.
- `tests / nightly-status`, job 128427022838, failure. Class: not this PR's (fix-review.md step 11). The three-dot diff touches none of the files nightly-status reads (the governance workflow's self-test job, the harness, this PR's delivery row and the closure ledger). Answer: no code answer is owed by this diff.

The previous body called this diff's change "the self-test shards" under nightly-status. That was wrong: the diff has no shards (see Alternatives). That sentence is gone from this body.

## Forward-carry

- pr_args.sh's `mut:unlock` arm passes only while its checker runs `kill -0` within the lock holder's 0.2 s parent poll, so CPU load can turn it red. Measured: 1 in 9 with all five self-tests at once, and 22 of 22 chained (Figures). That bounds the rate only to below about 1 in 7. The deterministic cure belongs to pr_args.sh, which this group does not own, and the reviewer concurred with this route. Carry text: make pr_args.sh's `mut:unlock` arm deterministic under CPU load (wait for the holder's exit with a bound, not one `kill -0` inside the holder's 0.2 s parent poll), null-controlled by the unmutated holder still read alive; measured 1 FAIL in 9 with five self-tests concurrent, 22 of 22 chained. Carry: R10-HANDOFF-PATH

- Carry 1 (roster, orchestrator evidence 2026-11-07: #3262 and #3265 each cancelled at the 30-minute job timeout; the fixer re-measures the self-test wall time at its own base): re-measured at this head. The job replay is 616 s with `failed=0`, and CI at a09ebaeb, the same layout without the 0.0 s last step, was 636 s of 1800 s. #3262's and #3265's timeouts ran the base's in-line layout, which this PR replaces. Carry: dismissed: re-measured here, 616 s replay and 636 s CI under the 1800 s timeout

## Friction

- fixer.md-step-3: unenforced: a CI-time claim owes before and after on a probe run, but a fixer seat has no probe path. ci_probe.py takes only `ci-probe/*` refs, and this seat writes no other branch. This head's first code run is the probe for the last step's cost. Carry: dismissed: the pull request's own first run is the probe
- seat-output-refs: stale: refs/heads/handoff-wip/r10-hotfix-selftest-timeout still held round 2's BLOCKED.md commit cfb1d69f3, which the orchestrator's body push 931e696ce had resolved. The step push is fast-forward only, so this round's step pushes are merge commits over cfb1d69f3 that carry this head's tree. Deleting the ref first was refused in this environment. Carry: dismissed: one stale step ref, deleted after this body's push
