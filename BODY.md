The merge train treated a red `gate` as a final verdict while the head's code run was still running, and skipped pull requests that would have gone green. This is a hotfix-tier change because it blocks merges. It is CI-throughput lever 1, approved by the owner (tvofi, 2026-11-07, #201 comment 6707834331).

How it happens: an edit run's gate fails at once, deferring to the code run (tools/ci/gate.py `deferral`: "run(s) [..] at this head are still being judged; their gate decides"). The code run publishes no `gate` check run until every unit has finished. So `latest_runs` sees only the edit gate, and `classify` counts it red. Then `wait_ci` returns it, and `at_head` logs `ci red=['gate']` and SKIPs. The brief's s12 CI-throughput study (2026-11-05 13:26Z to 2026-11-07 13:26Z) counted 56 such SKIPs; in 32 the code run later concluded success. This seat did not re-take those figures; they come from the brief. #3293 at fefaa492 (2026-11-07 21:07:58Z, `SKIP #3293 ci: red at the head: gate` on main's tools at dee8b413) is a fresh instance, and this body replays it.

The fix (tools/audit/seat/merge_train.py, tools/audit/seat/proof_watch.py, tools/audit/seat/ci-watch.sh):
- `classify(latest, required, busy=())`: a red GATE is pending while `busy` is non-empty. Every other context, and every caller that passes no `busy`, behaves as before.
- `gate_busy(ci_runs, check_runs)`: tools/ci/gate.py's own `busy`, imported from its tree path and never copied. Each run's jobs come from its own check suite's check runs, so no read per run is needed.
- `Train._gate_busy`: one `actions/workflows/ci.yml/runs?head_sha=` listing, made only on a red gate. An unreadable listing reads no run busy, logged, so the red stands. **Round 3:** it also returns `gate_rerunning` over the same listing. That covers a ci.yml run that is unfinished although its suite's latest `gate` is completed. `gate` is ci.yml's last job, so such a run is a re-run attempt (gate-sweep's attempt 2) whose gate has not been listed again, and gate.py's `busy` reads it as judging.
- `wait_ci(only=...)` (the train): waits on a red GATE while `_gate_busy` names a run. A red beside a green GATE suite gets one settle poll (`SWEEP_SETTLE_POLLS = 1`). The `wait-ci` subcommand (`wait_ci`, no `only`) takes the same settle once every run has concluded.
- `Train.classify_at`, the reading of the one-read readers (the `classify` CLI and `proof_watch.required_state`). **Round 3**, the gate-sweep settle gap: a red GATE that `_gate_busy` does not hold reads WAIT under one condition. `sweep_settling` must find the newest green GATE suite completed at most `SWEEP_SETTLE_SECONDS` (`SWEEP_SETTLE_POLLS × HEARTBEAT_SECONDS`, 240 s) before the read, on the Train's `wall` clock. Past the bound, with an unstamped completion, or on a completion stamped ahead of the clock (unknowable, never age 0), the red stands. So a sweep that never comes still ends RED. `proof_watch.Watcher` takes a `wall` and hands it to the Train.
- `ci-watch.sh` `gate_deferred` asks the `classify` CLI, so it inherits the settle with no change of its own.
- Merges are still decided only by gate success, `cross_check` against GitHub's required-check evaluation, and the ruleset. The train stays bounded by `polls` (TIMEOUT), and proof_watch by `--budget`.
- Side finding (the brief's): `tools/audit/seat/train.sh add ... --front` now passes through to `merge_train.py add --front`. Before, a seat wanting the front of a live train had to call merge_train.py by hand, because a plain `train.sh add` with no train live starts a fresh train over everything ready. This is a one-flag pass-through mirroring `--priority`, pinned by train.sh's self-test step 11.

The round-3 design choice, between the verdict's two remedies:
- (b) alone, reading gate-sweep.yml's runs at the head: not possible. gate-sweep.yml runs on `workflow_run` at main's sha, so a listing by `head_sha=<PR head>` never names it. The edit run's re-run attempt is readable, and this diff reads it (`gate_rerunning`). But it appears only once the sweep requests the re-run, which at a38bd141 was 62 s after the code gate's green (20:02:31Z to 20:03:33Z). That leaves the first minute uncovered.
- (a) alone, a time bound: it covers the whole gap only if the bound outlasts the re-run's runner queue. At a38bd141 the re-run gates were listed 188 s after the green, against the 240 s bound, a 52 s margin on a latency the runner queue sets.
- Taken: both. The bound covers only the sweep's own start (measured 62 s against 240 s). The re-run read covers the queue after it, with no time bound, because the run is visibly unfinished; the caller's own `polls` or `--budget` still bound it. Neither alone closes the gap without a guess.
- Rejected: (c), a re-read on RED in each CLI caller. That makes three copies (bus.sh, cloud_dispatch's reviewer wait, ci-watch), as the a8c36900 verdict judged.

The a8c36900 verdict (probe/rev-3290-5a2baec6), answered. It blocked on the classify CLI exiting 1 RED in the gate-sweep settle gap, live at 18:16:12Z. Round 2's body answered it with "a single read cannot wait; the caller's next read sees the sweep". The a38bd141 verdict showed that answer false for every caller of the one-read path: bus.sh refuses the dispatch, proof_watch aborts `REQUIRED RED`, reviewer waits stop at exit 1, and ci-watch wakes `RED: gate`. This round withdraws that disposition and closes the gap in `classify_at` (above). The pinned case `defer-wait CLI: one read takes no settle ... is RED` is gone. In its place:
- `settle gap a38bd141 20:03:00Z ... reads WAIT (exit 3)`, within the bound;
- `settle gap null: past the bound (240 s) with no re-run, the red stands -- RED (exit 1)`;
- the unstamped null `defer-wait CLI null: a red beside a green suite whose completion is unstamped takes no settle -- RED`.
The a8c36900 follow-up (figures and mutants not re-taken) is answered by `## Figures` and `## Mutation proof`, re-taken at this head. M9 stays dismissed (`## Forward-carry`).

Process state (d): gate.py's at-once deferral (fa921fd59, 2026-11-05) post-dates the classifier (e23062763, 2026-10-21).

## Head

94da0b7f77a052d39a6aec116bfa18a6ebe808c1: repair round 3 on PR head a38bd141ec8b42fc8d2bcd17090be1814ca97d83. It adds four commits:
- 305b0d55: the failing tests, first;
- eb1081cf: the fix;
- 154500f8: train.sh `--front`;
- 94da0b7f: tests pinning the diff-mutant survivors that `prepr.sh` step 6d reported at 154500f8.

origin/main was not merged. It stood at dee8b413fd7da7b07f13e28a93d7d49b4a9e978a during the work and at 7c9c4c154cda514f938fd503cde2779716caf251 at 2026-11-07T23:16Z. `git merge-tree --write-tree origin/main HEAD` reports no conflict at either, so per the owner's ruling of 2026-11-07 the merge train recarries this head onto main and nothing was merged here. The self-tests, the replays and the class enumeration were taken at this head. The mutants MF1 to MF9 were taken at 154500f8 and S1 to S9 at 94da0b7f; 94da0b7f adds test lines only.

## Mutation proof

Failing first, at 305b0d55 (the tests, before eb1081cf):
- `python3 tools/audit/seat/merge_train.py --self-test` printed `merge_train self-test: 503 checks, 4 failed`:
  - `settle gap a38bd141 20:03:00Z: the code gate green 29 s ago, no sweep yet -- classify reads WAIT (exit 3)`
  - `settle gap a38bd141 20:04:00Z: gate-sweep's attempt 2 running, its gates not re-listed -- WAIT (exit 3)`
  - `settle gap: a re-run attempt whose gate is not re-listed is a wait past the bound too (the re-run read)`
  - `settle gap: at exactly the bound the settle still holds -- WAIT`
- `python3 -I tools/audit/seat/proof_watch.py --self-test` printed `proof_watch self-test: 48 checks, 2 failed`:
  - `(g4) the settle gap 30 s after the code gate's green is waited on, not REQUIRED RED` (got `aborted: REQUIRED RED at aaaaaaaaaaaa: gate; nothing merged`)
  - `(g4) the settle gap waits one poll, then merges on gate-sweep's swept green`

How the mutants were run: each was applied at 154500f8 (merge_train then at `503 checks`) to the committed file by one exact single-occurrence replacement. Then all four self-tests ran: merge_train, proof_watch, ci-watch and `bash tools/audit/seat/train.sh --self-test`. Then the file was restored. Afterwards `git status --porcelain` was empty. The driver is a one-off probe kept in seat scratch.
- MF1, `sweep_settling` off (`return 0 <= now - last <= SWEEP_SETTLE_SECONDS` -> `return False`):
  - merge_train `503 checks, 2 failed`: the 20:03:00Z case and the exact-bound case;
  - proof_watch `48 checks, 2 failed`: both (g4) cases.
- MF2, the re-run read dropped (`gate_busy(...) or gate_rerunning(...)` -> `gate_busy(...)`): merge_train `503 checks, 1 failed`, `a re-run attempt whose gate is not re-listed is a wait past the bound too`.
- MF3, the stamp-ahead guard dropped (`0 <= now - last <=` -> `now - last <=`): merge_train `1 failed`, `a completion stamped ahead of the reading clock is unknowable, no settle -- RED`.
- MF4, the bound made exclusive (`<=` -> `<`): merge_train `1 failed`, `at exactly the bound the settle still holds`.
- MF5, the settle unbounded (`return 0 <= now - last`):
  - merge_train `1 failed`, `settle gap null: past the bound (240 s) with no re-run, the red stands`;
  - proof_watch `1 failed`, `(g4) null: past the bound, REQUIRED RED`.
- MF6, `gate_rerunning` counts completed runs too (the status filter dropped):
  - merge_train `11 failed`, among them `defer-wait CLI null`, `#3293 null` (both) and `settle gap null: a content FAIL`;
  - proof_watch `1 failed`.
- MF7 (the suite filter dropped) survives. It is equivalent; see `## Unpinned sites`.
- MF8, proof_watch's wall not handed to the Train: proof_watch `48 checks, 2 failed`, both (g4) cases.
- MF9, train.sh's `${add_front:+"$add_front"}` dropped: train.sh rc 2, `REFUSE: self-test: add's argv shape wrong`.
- Every other suite stayed green under each mutant: ci-watch `18 checks, 0 failed` and train.sh `ok` throughout, except where named above.

The diff mutants step 6d reported at 154500f8 (`mutant_run.py --diff`, `MUTANT_CMD` = the four self-tests, `--max-mutants 40`) listed 9 survivors. S1 to S6 and S9 were then killed by tests in 94da0b7f. Each was re-applied at 94da0b7f the same way and run through merge_train's self-test, which printed `506 checks, 1 failed` for each:
- S1 `merge_train.py` `sweep_settling` CMP_BOUND (`0 <= now - last` -> `0 < now - last`) and S2, its CONST_SWAP (`1 <= now - last`): both fail `settle gap: a read in the code gate's completion second (age 0) is inside the settle -- WAIT`.
- S3, `classify_cmd`'s `if runs is None:` GUARD_OFF: fails `defer-wait CLI: unreadable check runs are a Stop (the caller's REFUSE), never a verdict`.
- S4 and S5, `classify_at`'s `if GATE not in state[2]: return state` (GUARD_OFF, and RETURN_DEL of the return): both fail `defer-wait CLI: a green gate is read with no ci.yml listing read (no unreadable-listing log) -- GREEN`.
- S6, `wait_ci`'s `settle < SWEEP_SETTLE_POLLS` -> `<=`, and S9, the fixture's listing counter `get("ci_list_reads", 0)` -> `1`: both fail `defer-wait bound: ... (two red polls, two ci.yml listing reads)`.
- S7 and S8 are equivalent: see `## Unpinned sites`.
- The round-1 and round-2 mutants (MA to ME, M1 to M3) were not re-run. Their lines are untouched except `_gate_busy`'s return, which MF2 covers.

## Null control

- The mutation null: a comment-only edit in `classify_at` (MF-NULL, at 154500f8) leaves merge_train `503 checks, 0 failed`, proof_watch `47 checks, 0 failed`, ci-watch `18 checks, 0 failed` and train.sh `ok`.
- Each new WAIT case has a RED null in the same self-test, passing both before and after the fix:
  - `settle gap null: past the bound (240 s) with no re-run, the red stands -- RED (exit 1)`;
  - `settle gap: a completion stamped ahead of the reading clock is unknowable, no settle -- RED`;
  - `settle gap null: a content FAIL of the code gate leaves no green suite, no settle -- RED at once`;
  - `defer-wait CLI null: a red beside a green suite whose completion is unstamped takes no settle -- RED`;
  - `#3293 null: the same edit gate failure with no code run in progress stays RED (exit 1)`;
  - `#3293 null: once the code run ends in a content FAIL, no run in progress and no settle -- RED (exit 1)`;
  - proof_watch `(g4) null: past the bound, REQUIRED RED` (and `no merge past the bound`).
- The earlier nulls still pass: proof_watch (g) and (g2), `defer-wait null` (three), `defer-wait wait-ci null`, and ci-watch W10, W12, W14 and W15.

## Figures

- merge_train self-test at the head: `python3 tools/audit/seat/merge_train.py --self-test` prints `merge_train self-test: 506 checks, 0 failed`.
- proof_watch self-test at the head: `python3 -I tools/audit/seat/proof_watch.py --self-test` prints `proof_watch self-test: 47 checks, 0 failed`. A passing (g4) runs one check, so the count is one lower than under a failing mutant.
- ci-watch self-test at the head: `bash tools/audit/seat/ci-watch.sh --self-test` prints `ci-watch self-test: 18 checks, 0 failed`.
- train.sh self-test at the head: `bash tools/audit/seat/train.sh --self-test` prints `train.sh self-test: ok (...)`, rc 0.
- The reviewer's own replay at both ends. The driver is verdict/3290 evidence/replay_gap.py (sha1 bab33cb9c230273b47aea6754fa5ae414cb9cbb6) over that verdict's evidence/check-runs-head.jsonl and evidence/ci-runs-head.jsonl. One line was added: `t.wall` is set to the cut time T, because the head's settle reads the wall clock (sha1 f9407e3a8e922b0cd39ba9b3c82cc50df5bc4b76, seat scratch).
  - At T = 20:03:00Z and 20:04:00Z: a38bd141 prints `1 RED ... red: gate` and this head prints `3 WAIT ... pending: gate`. At 20:06:31Z and 20:07:00Z both print `0 GREEN`. At 19:30:00Z both print `3 WAIT` (the round-2 case).
  - The rule over the whole gap: every 15 s from 20:02:31Z to 20:06:01Z, 15 reads. a38bd141 read 13 RED and 2 WAIT; the 2 WAITs are 20:05:46Z and 20:06:01Z, after the re-run gates started. This head read 15 WAIT and 0 RED.
  - The null past the bound is the self-test's `settle gap null` case, because the recorded data has no head whose sweep never came.
- #3293, live. The reads went through this head's `merge_train.py classify fefaa4926e36e9c571cc685e0b6aa2b391d14793 --pr 3293` at 21:21Z, with code run 42414123291 in progress and edit run 42414123334's gate failed:
  - this head printed `WAIT ... pending: gate red: none` (rc 3);
  - origin/main dee8b413's copy printed `RED ... pending: none red: gate` (rc 1), the train's SKIP.
- #3293, recorded. A one-off logger saved the head's check runs and ci.yml runs every ~33 s, 90 snapshots from 21:21:39Z to 22:10:25Z. A one-off replay driver fed each snapshot to `classify_cmd`, with `wall` set to the snapshot time:
  - a38bd141: 86 WAIT, 1 RED, 3 GREEN; this head: 87 WAIT, 0 RED, 3 GREEN.
  - The one RED is a live settle gap. At 21:49:05Z the code gate 128538924137 (suite 114906715780) was green, completed 21:48:51Z, 14 s earlier, and the edit gate 128528991330 was still red. a38bd141 read RED and this head read WAIT. Both read GREEN from 21:50:10Z, after the sweep.
- Diff mutants: `prepr.sh` step 6d, `mutant_run.py --diff 364353e6...HEAD --max-mutants 40`.
  - At 154500f8: 9 survivors. The whole prepr run took 49 min 42 s (22:23:57Z to 23:13:39Z), most of it the mutants.
  - At 94da0b7f, the head: 2 survivors, `merge_train.py:1714 CONST_SWAP` and `merge_train.py:1736 CONST_SWAP`, both answered under `## Unpinned sites`. The whole prepr run took 49 min 56 s (23:21:45Z to 00:11:41Z).
- Scoped gate: `python3 tests/closure.py select --diff $(git merge-base origin/main HEAD) --workdir "$D"` prints `MODE: SCOPED -- 1 script(s) run, 32 scoped out`, naming tests/entities.py.
  - `PYTHONPATH=tests/hastub python3 tests/entities.py` passes inside `prepr.sh`'s `closures` step (`ok closures: scoped recordings are covered`) with `BASH_ENV` unset; see `## Friction` for why.
  - With the container's `BASH_ENV` set, it prints `3 of 2645 ENTITY CHECKS FAILED`: the coverage marker, the release ZIP and the Pages probe. These are the same three the reviewer recorded at both ends.
- Structure: `python3 tests/structure.py` prints `STRUCTURE RATCHET PASSED`.
- prepr: `env -u BASH_ENV bash tools/pr/prepr.sh` prints `PRE-PR: 94da0b7f77a052d39a6aec116bfa18a6ebe808c1 ... rc=0` (its `closures` step passing only with `BASH_ENV` unset; see `## Friction`); `tools/pr/prepr.sh --body-check` and `python3 tools/audit/carry_audit.py check --body <body> --branch fix/r10-hotfix-train-defer-wait` pass on this body.
- Class enumeration, the rule: `git grep -n -E "classify_at\(|classify\(|_gate_busy\(|sweep_settling\(|gate_rerunning\(" -- tools/audit/seat`, plus every caller of the `classify` CLI (`git grep -n "merge_train.py classify" -- tools/audit/seat`). Every merge_train-reading seam it returns, and its disposition:
  - The `classify` CLI (`classify_cmd` -> `classify_at`), and through it: bus.sh dispatch, cloud_dispatch.py's reviewer wait, postmerge.py, review_packet.py and ci-watch.sh `gate_deferred`. Closed in this diff (the settle and the re-run read).
  - `proof_watch.required_state` -> `classify_at`: closed in this diff.
  - `wait_ci(only=...)`, the train: closed in round 1. Its `_gate_busy` now also carries the re-run read; the poll settle is unchanged.
  - The `wait-ci` subcommand: closed in round 2, by the poll settle.
  - `approval_owed` (`classify` over `gating_names`): already guarded. It is asked only when `classify_at` reads RED.
  - `main_green`'s `--overlap` read: unchanged on purpose. It is a log line at main's tip, where there are no edit runs.
  - orchestrator_tick.py's two `mt.classify` calls: unchanged on purpose. They are report lines with no merge, skip or abort.
  - The `classify` hits in ledger.py, prune_refs.py, record_row.py, review_carry.py, row_position.py, run_twins.py and tmp_paths.py are other functions of that name and read no gate.

## Unpinned sites

Answers to the survivors of `prepr.sh` step 6d's diff mutants, and to my own MF7. None is killable while the constant has its value; each is an equivalence, not a skipped test.
- `tools/audit/seat/merge_train.py:1714 CONST_SWAP` (`wait_ci` only-path `settle += 1` -> `+= 2`): equivalent while `SWEEP_SETTLE_POLLS == 1`. Any increment of at least 1 ends the settle after one poll, and the bound case pins one poll by its two listing reads. Carry: dismissed: equivalent mutant at SWEEP_SETTLE_POLLS = 1
- `tools/audit/seat/merge_train.py:1736 CONST_SWAP` (`wait_ci` all-runs-path `settle += 1` -> `+= 2`): equivalent for the same reason. `defer-wait wait-ci bound` pins `reads == 2`. Carry: dismissed: equivalent mutant at SWEEP_SETTLE_POLLS = 1
- `tools/audit/seat/merge_train.py` `gate_rerunning`'s `and r.get("check_suite_id") in done` dropped (MF7): equivalent. Take an unfinished, non-held run whose suite has no completed gate. Either its gate is listed in progress, and then `latest_runs` keeps that pending gate as the worst and `classify` never reads GATE red. Or its suite lists no gate, and then gate.py's `busy` already names it, because `judging` requires a listed `gate`. Kept for the reader: it names what a re-run attempt is. Carry: dismissed: equivalent mutant, an unfinished run with no completed gate is pending or busy already

## Red checks

Re-taken at 2026-11-07T21:34Z over `gh api --paginate "repos/tvofi/heatpump_optimizer/commits/a38bd141ec8b42fc8d2bcd17090be1814ca97d83/check-runs?filter=all&per_page=100"`, which returns 94 check runs. Every concluded non-success, non-skipped run, by literal name:
- `gate`, check run 128499580417 (edit run 42404527136 attempt 1, failed 19:19:15Z), and `gate`, check run 128507622651 (edit run 42406706258 attempt 1, failed 19:53:38Z).
  - Class: the gate deferral this pull request exists for. Both logs say `FAIL run(s) [42404526059] at this head are still being judged; their gate decides` (verdict/3290 evidence/head-gate-red-logs.txt).
  - Code run 42404526059's gate 128512781341 went green at 20:02:31Z, and gate-sweep re-ran both edit gates green: 128513382838 and 128513383466, 20:06:15Z/20:06:16Z.
  - Answer: the red is gate.py's designed at-once deferral, not a defect, so no cheaper detector applies. Its misreading by the train, the CLI, proof_watch and ci-watch, through the settle gap included, is what this diff removes.
- No other run at that head is red, and none is in progress. This head's own CI starts at the handoff push.

## Forward-carry

- M9 (the reviewer's: `classify`'s log routed to stderr -> `**({})`) survives. It is equivalent under every current stdout reader, re-checked by the a38bd141 verdict. Carry: dismissed: equivalent mutant under all current stdout readers (bus.sh, postmerge.py, review_packet.py)
- R5 (`_gate_busy`'s `except ValueError: ci_runs = None` -> `ci_runs = []`) survives. The verdict is the same; only the "unreadable" log line differs. Carry: dismissed: outcome-equivalent, only the diagnostic log line differs
- R6 (ci-watch `gate_deferred`'s `*" gate "*) return 1` -> `true`) survives. `classify` returns `wait` only on an empty red list. Carry: dismissed: equivalent mutant, classify's WAIT carries an empty red list by construction
- The reviewer's M5 (`action_required` jobs mapping) is equivalent: gate.py's `busy` filters that status first. Carry: dismissed: equivalent mutant, busy() filters that status first

## Friction

cloud-setup: stale: this container's `BASH_ENV` (the interim toolchain profile cloud-setup.sh writes) re-exports `RUNNER_TEMP` as its install prefix's `runner-temp`, which cloud-setup.sh exports but never creates, into every non-interactive bash. That overrides the `RUNNER_TEMP` that tests/entities.py hands its workflow-step replays. The coverage-marker, release-ZIP and Pages-probe checks then fail (`probe.err: No such file or directory`), and prepr's `closures` step refuses `tests/entities.py (exit 1)`. With `env -u BASH_ENV`, the same tree passes. These are the three failures the a38bd141 verdict recorded at both ends. Carry: dismissed: the container profile, not this diff; named for the orchestrator, whose dispatch carries the INTERIM TOOLCHAIN step
