The merge train treated a red `gate` as a final verdict even while the head's code run was still running. That made it skip pull requests that would have gone green. This is a hotfix-tier change because it blocks merges. It is CI-throughput lever 1, approved by the owner (tvofi, 2026-11-07, #201 comment 6707834331).

How it happens: an edit run's gate fails straight away, deferring to the code run (tools/ci/gate.py `deferral`: "run(s) [..] at this head are still being judged; their gate decides"). The code run publishes no `gate` check run until every one of its units has finished. So `latest_runs` sees only the edit gate, `classify` counts it red, `wait_ci` returns it, and `at_head` logs `ci red=['gate']` and SKIPs. The brief's s12 CI-throughput study (2026-11-05 13:26Z to 2026-11-07 13:26Z) counted 56 such SKIPs. In 32 of them the code run later concluded success, and in 10 it failed. This seat did not re-take those figures: they come from the brief.

The fix (tools/audit/seat/merge_train.py, tools/audit/seat/proof_watch.py):
- `classify(latest, required, busy=())`: a red GATE counts as pending while `busy` is non-empty. Every other context, and every caller that passes no `busy`, behaves exactly as before.
- `gate_busy(ci_runs, check_runs)`: calls tools/ci/gate.py's own `busy` (imported from its tree path, not copied), i.e. unfinished, not held, not judging. Each run's jobs are taken from the check runs of its own check suite, so no per-run jobs read is needed. `run_id` is set to infinity because the train is not a run: gate.py's tie-break against a later run with a started gate is between two gates and has no train side.
- `Train._gate_busy`: one `actions/workflows/ci.yml/runs?head_sha=` listing, made only when the gate reads red. If the listing cannot be read, no run counts as busy and this is logged, so the red stands exactly as it did before.
- `wait_ci(only=...)`: re-reads a red GATE against that listing and logs each change in the busy set. There is a gap between the code run finishing and gate-sweep.yml (which starts on that completion) re-running the deferred red. To cover it, a red GATE with a green GATE suite beside it gets one settle poll (`SWEEP_SETTLE_POLLS = 1`). If the sweep never re-runs it, the red is read again one poll later and SKIPs. A genuine code-run failure leaves no green suite, so it gets no settle.
- Round 2, the sibling readers the verdict named, through the same predicate:
  - `Train.classify_at(h, runs, required)`: `classify` with a red GATE re-read against `_gate_busy`. It is the reading of the one-read readers, and it takes no settle, because a single read cannot wait; the caller's next read sees the sweep.
  - The `classify` subcommand: its read moves to `classify_cmd(t, sha, pr, on_main)` (a pure move, its own commit) and goes through `classify_at`, so a deferring edit gate prints `WAIT` (rc 3), not `RED` (rc 1). Its deferral log goes to stderr, because stdout is the one verdict line dispatch and reviewers parse.
  - `proof_watch.required_state`: goes through `Train.classify_at` over its own runner (`ProofWatch.train()`), so a deferral red is pending and the watch keeps waiting under `--budget`, instead of aborting `REQUIRED RED`.
  - `ci-watch.sh`: when its per-suite read finds `gate` red, it asks `merge_train.py classify <sha>` (`gate_deferred`, overridable as `CI_WATCH_CLASSIFY` for the self-test). It drops `gate` from the alert only on `WAIT` (rc 3) with `gate` absent from that line's red list. Any other answer, a refusal included, keeps the red.
  - The `wait-ci` subcommand (`wait_ci` with no `only`): it returns only once every check run at the head is concluded. At that point gate.py's `busy` can name no run, but gate-sweep's re-run may not have started yet. So a red GATE beside a green GATE suite takes the same one-poll settle as the train.
- Merges are still decided only by gate success, `cross_check` against GitHub's required-check evaluation, and the ruleset. The train's wait is still bounded by `polls` and ends in TIMEOUT. proof_watch's wait is still bounded by `--budget`.

Alternatives considered:
- (a) Copying `busy`'s three conditions into the train: rejected, because that is a second reading of the rule.
- (b) Reading each run's jobs as gate.py does: rejected, because it costs one read per run per poll, where check runs grouped by suite give the same name -> (status, conclusion) map.
- (c) Parsing the deferral text from the gate's log: rejected, because it needs a log read per red and depends on wording.
- (d) Round 2: dispositioning the readers by `Carry:` instead of fixing them: rejected, because they share the seam (`classify` over one check-runs read), so the shared predicate closes them in about 20 production lines. `ci-watch.sh` is shell with no Python seam, so it calls the `classify` CLI, the same predicate, instead of carrying a second copy of the rule.
- (e) Carrying `ci-watch.sh` to R10-TRAIN-MERGE-LOOP-2: tried first. `body_push.sh` refused it, because the carry is not in that group's brief or carries and landing it needs a write to the roster branch, which this seat may not make. Fixing it took about 15 production lines, so it is fixed here.

This retires R10-TRAIN-MERGE-LOOP-2's carry for the same defect: its carry about the gate deferral being read as a final red moves here, so it is built once.

Process state (d): gate.py's at-once deferral (fa921fd59, 2026-11-05) post-dates the classifier (e23062763, 2026-10-21).

## Head

60257aaf0ae7dc334d8e2e6bbbc5690a19f463ac: round 2 on PR head 43a9d5842392426ea06806affa479461f6017645. Between the merges come the classify_cmd move, three failing-first test commits, three fix commits and the instrument docs. origin/main was merged in three times:
- 4b5d771bd (#3272, two record files).
- aaaec2128e5d2efc2e0ad8ffe4918eec6cbb7f98 (#3280, which reaches merge_train.py and stamp.py), after main moved during the handoff. Every figure below was then re-taken at d7b258a0 (2026-11-07T17:54Z): the self-tests, every mutant and null, the finder's replay, scope, structure, entities, the closure selftest and `tools/pr/prepr.sh` rc=0.
- 364353e670f666be6c97a5942ffa0bea9132b5ce (`ci: record nightly kills`, 32 mutation-ledger JSON files; no `.py` or shell under tools/ or tests/ moves, per `git diff --stat HEAD^1 HEAD -- tools/ tests/*.py`), which moved main again before the push. At this head, at 2026-11-07T18:29Z, the three self-tests (492/0, 44/0, 18/0), `tests/structure.py`, the scope, `tests/entities.py` and `tools/pr/prepr.sh` (`PRE-PR: 60257aaf... rc=0`) were re-run. The mutants and the replay were not re-run for this ledger-only delta, which reaches none of the files they mutate or read.

## Mutation proof

The failing cases came first. Each was committed before its fix and is run by `python3 tools/audit/seat/merge_train.py --self-test` or `python3 tools/audit/seat/proof_watch.py --self-test`:
- Commit ae367e5c (before the round-2 fix, at main 4b5d771bd). merge_train printed `482 checks, 2 failed`: `defer-wait CLI #3248: classify reads the deferring edit gate as WAIT (exit 3) while code run 42237558473 runs, never RED` and `defer-wait CLI: an unreadable runs listing leaves the red standing (exit 1), logged`. proof_watch printed `45 checks, 2 failed`: `(g3) a deferral red while the code run runs is waited on, not REQUIRED RED` (it got `aborted: REQUIRED RED at aaaaaaaaaaaa: gate; nothing merged`) and `(g3) the deferral waits one poll, then merges once the code run's gate lands`.
- The ci-watch test commit (before its fix, at main 4b5d771bd). `bash tools/audit/seat/ci-watch.sh --self-test` printed `ci-watch self-test: 18 checks, 1 failed`: `W13 an edit run's deferral red while its code run runs (classify WAIT, gate not red) is no RED alert`.
- The wait-ci test commit (before its fix, at main 4b5d771bd). merge_train printed `485 checks, 2 failed`: `defer-wait wait-ci: a red gate beside a green suite, every run concluded, waits one poll for gate-sweep's re-run and reads its green` and `defer-wait wait-ci bound: a sweep that never re-runs the red leaves it standing one poll later`.

Each mutant below was applied at d7b258a0 to the committed file by an exact one-occurrence string replacement, the self-test was run, and the file was restored. Afterwards the tree was clean (`git status --porcelain` empty):
- MA: `classify_at` without the predicate (`busy = self._gate_busy(h, runs) if GATE in state[2] else []` -> `busy = []`). merge_train: `492 checks, 2 failed`, the two CLI cases. proof_watch: `45 checks, 2 failed`, both (g3) cases.
- MB: proof_watch's reader reverted (`self.train().classify_at(self.sha, self.check_runs(), self.required_names())` -> `_train().classify(_train().latest_runs(self.check_runs()), self.required_names())`). proof_watch: `45 checks, 2 failed`, both (g3) cases.
- MC: the CLI's reader reverted (`t.classify_at(sha, runs, req)` -> `classify(latest_runs(runs), req)`). merge_train: `492 checks, 2 failed`, the two CLI cases.
- MD: wait-ci's settle off (`if not (GATE in red and settle < SWEEP_SETTLE_POLLS` -> `if not (False and GATE in red and settle < SWEEP_SETTLE_POLLS`). merge_train: `492 checks, 2 failed`, the two wait-ci cases.
- ME: ci-watch's predicate off (`  [ "$rc" = 3 ] || return 1` -> `  return 1` in `gate_deferred`). ci-watch: `18 checks, 1 failed`, W13.
- Round 1's M1 (`busy = self._gate_busy(h, runs)` -> `busy = []` in `wait_ci`), re-run at this head: `492 checks, 4 failed`, the #3248 scene, the 13:01Z cycle, the TIMEOUT bound and the unreadable-listing case. Its M2 and M3 are unchanged by this round, and the reviewer re-ran them at 43a9d584 (verdict/3290 evidence/mut-M2.txt, mut-M3.txt): 4 and 2 failed.

## Null control

- The mutation null: a comment-only edit in `classify_at` gives merge_train `492 checks, 0 failed`, a comment-only edit in `required_state` gives proof_watch `44 checks, 0 failed`, and a comment-only edit in `gate_deferred` gives ci-watch `18 checks, 0 failed`.
- ci-watch W14 (classify reads RED) and W15 (classify refuses) still alert `RED: gate`. W10 and W12 (an older red suite, a skipped gate) still alert, and there the real CLI runs against the fake gh, refuses, and keeps the red.
- `defer-wait CLI null: a red gate with no unfinished ci.yml run still reads RED (exit 1)` passed both before and after the fix.
- `defer-wait CLI: one read takes no settle -- a red beside a green suite with nothing busy is RED`.
- `defer-wait wait-ci null: a red gate with no green suite beside it is read on the first poll, no settle`.
- proof_watch's (g) and (g2) still abort `REQUIRED RED` (a red gate with no busy run, an older red suite, a RATE-LIMITED suite). The fixture's ci.yml listing is readable and empty, so these are nulls over a real read, not an unreadable one.
- The P345 and #3073 `classify --pr` cases (APPROVAL-OWED, rc 4, and their RED nulls) all still pass. Their fixture now answers the ci.yml listing with no runs.

## Figures

- merge_train self-test at the head: `python3 tools/audit/seat/merge_train.py --self-test` prints `merge_train self-test: 492 checks, 0 failed` (main's #3280 added cases of its own).
- ci-watch self-test at the head: `bash tools/audit/seat/ci-watch.sh --self-test` prints `ci-watch self-test: 18 checks, 0 failed`.
- proof_watch self-test at the head: `python3 tools/audit/seat/proof_watch.py --self-test` prints `proof_watch self-test: 44 checks, 0 failed`. On success the (g3) abort branch's check does not run, which is why the count is one lower than under a mutant.
- Mutants MA to MD, and the failing-first runs: the commands and results are in `## Mutation proof`.
- The finder's harness, at both ends. The reviewer's evidence is its live reads at 16:22Z (verdict/3290 evidence/check-runs.txt sha1 e1abc6242c27b5ef4fc24229ac6f4a6d2e8ed4c6, evidence/ci-runs.txt sha1 439f1fa8a9d4b3e04a8fc97f3ad08c9116859b33). A replay driver, `replay_cli.py` (sha1 f288f3c9ca28f0e97984784fa4ec7eef5bc03698, kept in seat scratch as a one-off probe), feeds those reads to `merge_train.main(["classify", "43a9d584..."])` with `Train._run` stubbed, so it exercises the CLI end to end.
  - At 43a9d584 (the base of this round): `rc=1 RED 43a9d584... pending: none red: gate`. This matches evidence/classify-log.txt's 16:22:14 line and the reviewer's `CLI-classify(no busy): ('red', [], ['gate'])`.
  - At the head: `rc=3 WAIT 43a9d584... pending: gate red: none`.
  - Null control (`--drop-busy`: the same reads with code run 42387525051 marked completed): `rc=1 RED ... red: gate` at both ends.
- Scoped gate: `python3 tests/closure.py select --diff $(git merge-base origin/main HEAD) --workdir "$D"` prints `MODE: SCOPED -- 1 script(s) run, 32 scoped out`, naming tests/entities.py. `PYTHONPATH=tests/hastub python3 tests/entities.py` prints `ALL 2645 ENTITY CHECKS PASSED` (rc 0). The run_always lines also pass: `python3 tests/env_drift.py --claims-only $(git merge-base origin/main HEAD)` printed `claims hygiene: 4b5d771bdf8feb1f83d7d9443e5117b771a0ab76 ok` before the second merge (prepr's `claims hygiene` step passes at this head), and `python3 tests/closure.py selftest` prints `ALL 118 closure shrink pins PASSED`.
- Structure: `python3 tests/structure.py` prints `STRUCTURE RATCHET PASSED`.
- The 56 / 32 / 10 SKIP counts, the 27 re-merged heads and the about 3,500 runner-minutes come from the brief's s12 CI-throughput study. They were not re-measured here, and that study's harness is not in the tree. Instead, the #3248 scene and the 13:01Z scene are each reproduced as a self-test case.
- Class enumeration, the rule: `git grep -n -E "classify\(|latest_runs\(|run_state\(|gate_suites\(" -- tools/audit/seat` (every reader of a gate check-run state through merge_train's reading). It was widened by `git grep -n -E "conclusion|check-runs|check_runs" -- 'tools/audit/seat/*.sh' 'tools/audit/seat/*.py' 'tools/audit/seat/*.mjs'` to catch readers that do not go through merge_train. Every returned seam and its disposition:
  - `wait_ci(only=...)`, the train and batch-proof waits, and `main_green`'s non-overlap path, which waits through it: closed in round 1.
  - The `classify` subcommand (`classify_cmd`): closed in this diff.
  - `proof_watch.required_state`: closed in this diff.
  - The `wait-ci` subcommand (`wait_ci`, no `only`): closed in this diff (the settle).
  - `approval_owed` (`classify` over `gating_names`) and `gate_raise_only`: already guarded. From the CLI they are asked only when `classify_at` reads RED, so a deferral-only red is WAIT before they are reached. A deferral red's log is not raise-only either, so `gate_raise_only` reads False.
  - `main_green`'s `--overlap` read (`classify`, logged only), `infra_rerun` and `unstale`: unchanged on purpose. The first is a log line at main's tip. `infra_rerun` acts on attempt-1 infrastructure reds. `unstale` reads pending runs only, not reds.
  - `orchestrator_tick` (`latest`, `judge`, `one_pr`'s RAISE APPROVAL OWED line, `main`'s REQUIRED-not-green line): unchanged on purpose. These are report lines with no merge, skip or abort.
  - `review_packet.py` (`gate_digest`), `record_row.py` (`failed_required`), `merge_pr.sh` (which exits on GitHub's mergeStateStatus, not on its red read), `failure_logs.sh`, `body_patch.sh` and `ci_predict_replay.sh`: reports or generic name lists, unchanged on purpose. They take no wait or skip decision on a gate red.
  - `autofix_statuses.sh`, `bus.sh`, `ci_critpath.py`, `codeql-triage-poll.sh`, `probe_bridge.py`, `replay_draws.py` and `run_twins.py`: they read no `gate` check-run conclusion (workflow, job or status reads).
  - `ci-watch.sh` (the `reds` awk, `gate` per suite red when completed and not success): closed in this diff, through the `classify` CLI (`gate_deferred`). Before, a deferring edit gate made it alert `RED: gate` as a new state while the code run ran, which is a false wake for a waiting seat.

## Red checks

Read at 2026-11-07T17:21Z, over `gh api --paginate "repos/tvofi/heatpump_optimizer/commits/43a9d5842392426ea06806affa479461f6017645/check-runs?filter=all&per_page=100"`, which returns 94 check runs, all on one page. This round's own head has no CI yet, because the handoff push starts it. Every concluded red at the PR head:
- `gate`, check run 128451133241 (edit run 42387524862) and check run 128453922283 (edit run 42387655386), both failure. Class: the gate deferral this PR exists for (verdict/3290 evidence/edit-gate-logs.txt: `FAIL run(s) [42387525051] at this head are still being judged; their gate decides`). Code run 42387525051's gate concluded success at 16:43Z, and gate-sweep re-ran both edit gates to success (16:50Z, check runs 128465019117 and 128465021586). Answer: the red is gate.py's designed at-once deferral, not a defect, so no cheaper detector applies. Its misreading by the train, the CLI and proof_watch is what this diff removes.
- `tests / nightly-status`, check run 128452078720, failure. Class: not this PR's. It reports main's nightly (`mutation-nightly cancelled`, run 42369836867), is unrequired, and its own log says so. The diff reaches nothing it reads. Answer: the nightly lane is the orchestrator's to re-dispatch. This seat dispatches no workflow (its return is refs only).
- `governance / instrument-self-tests`, check run 128452078743, cancelled. Class: job timeout. It ran 16:01:52Z to 16:32:02Z against `timeout-minutes: 30`. Every self-test step it reached passed, including `merge_train self-test: 478 checks, 0 failed` and `proof_watch self-test: 43 checks, 0 failed`, and it was cancelled after `ci_predict self-test: 0 failed`. It is unrequired. Answer: a runner-time bound, not a verdict on the diff. The cases this round adds are offline and sleep-free, and no cheaper detector than the job's own bound exists. Whether the job's budget needs re-pricing is R10-CI-SLIM's call, not this hotfix's.

## Forward-carry

- The reviewer's M5 (`action_required` jobs mapping) is an equivalent mutant: gate.py's `busy` filters that status before it reads `jobs`. Carry: dismissed: equivalent mutant, busy() filters that status first

## Friction

none
