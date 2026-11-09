Fix review: blocked 4818b1a254b8e34c15a08af342957e17026de04c ci-red: gate red at head, two deferred gates never re-judged after their deciding run 42572841641 went green

bus-nonce: e673276156c509b1737d382db3a619c9

## Block

`merge_train.py classify 4818b1a254b8e34c15a08af342957e17026de04c --pr 3329` printed `RED 4818b1a254b8e34c15a08af342957e17026de04c pending: none red: gate` (rc=1) at 06:33:33Z, 06:33:55Z and 06:37:03Z, and `gate` is in `merge_train.py owed-reds`. A red CI never carries, so this head cannot get `merge`.

The red is the `gate` job in two older ci.yml runs at this head: run 42554795796 (job 129014273190) and run 42554912554 (job 129014250944). Both were re-run at 06:25:40-44Z and both failed with the same line: `FAIL run(s) [42572841641] at this head are still being judged; their gate decides`. That run's gate (job 129014911894) concluded `success` at 06:28:29Z. At 06:37:03Z, nine minutes later, nothing had re-run the two deferred gates. Every other required check at this head is green. Carry: dismissed: evidence, not a finding

This is a CI-state block and not a defect in the authored content: every content check below passed. The orchestrator re-runs the two deferred gates (or the sweep does), then re-dispatches. The next review only needs CI on an unchanged head, by `review_carry.py`. Carry: dismissed: the block itself, settled by re-running the two gates

## Evidence

- Round: this is the fifth verdict on #3329. The earlier ones are `blocked 8db2e568 root-cause-detectable`, `merge 50a78a49`, `blocked 1310d182 ci-incomplete` and `blocked 1310d182 ci-red: gate`. The authored code last changed at `a0ee437f` and `95f3e79e`. Every block since the `merge` was CI state, so whether `fixer.md`'s fourth-round re-cut applies is the orchestrator's call.
- Head: `4818b1a254b8e34c15a08af342957e17026de04c` is both the PR body's `## Head` and `refs/pull/3329/head` at 06:37Z. `review_carry.py 1310d182 4818b1a2` prints `CARRY` (0 of 1 branch-only commit is non-merge). The role diff `git diff $(merge-base)...origin/main -- dev/governance/roles/` is empty.
- Merge with main: `git merge-tree --write-tree origin/main 4818b1a2` returns rc=0 and tree `428b9619`, with `LEDGER-MERGE: resolved tests/closures.json` and `LEDGER-MERGE: resolved dev/audit/config/bugclasses.json` (ev/merge_tree.txt).
- Mutation proof (a detector-only diff, no production line). I ran the harness `replay` against `git archive <sha> tools/ci` copies:
  - `4fe7d5934b` and `52f9fc5b34`: `RESULT replay reruns=86 max_attempt=44 sim_minutes=72 alarm=yes`
  - `52f9fc5b34^`: `reruns=0 max_attempt=1`
  - `--no-restamp` at `4fe7d5934b` and at origin/main: `reruns=1 max_attempt=2 alarm=no`
  - Candidate (arm 1 skips `conclusion == "skipped"`, ev/candidate.diff): `reruns=1 max_attempt=2 alarm=no`, and that copy's `sweep.py --self-test` prints `52 checks, 0 failed`

  Every figure matches the body and RCA section 1. The first replayed re-runs post at 10:22:25Z and 10:23:11Z, as stated.
- Harness mutants, mine, against `4fe7d5934b`'s sweep:
  - The open-loop mutant (a completed re-run no longer re-fires the sweep) gives `reruns=1 max_attempt=2`.
  - The mutant that drops the re-stamp from `post()` gives `reruns=1 max_attempt=2`.
  - Both kill detection, so the closed loop and the recorded transition are each load-bearing (ev/mutant_*.txt).
- Origin/main `3231c071` and this head's own `tools/ci` replay to `reruns=1 max_attempt=2 alarm=no`, because the R10-HOTFIX-SWEEP-SETTLE-LOOP fix `34b98bbdb` is on main.
- Fixture facts I re-derived from `r10_rca_sweep_settle_loop.json` (ev/fixture_facts.txt):
  - 10 skipped jobs in the code run and 7 in the edit run.
  - Only the gate and skipped jobs change across attempts 2-6.
  - The latest non-skipped `completed_at` is 10:21:40Z (code) and 09:59:09Z (edit).
  - The skipped jobs' latest stamp falls 2-21 s before each gate start, including 10:23:18 against 10:23:22 and 10:25:17 against 10:25:20.
- Census: the arithmetic is verified on a synthetic TSV (ev/census_synthetic.txt). The quoted window figures are not verified, so I do not claim them: `runs=465/324`, `reattempts=428/1618`, `at_cap=0/17`, `max 17/45`, 32 runs at alarm 20, and the `gate-sweep.yml` 1000 runs / 904 run-minutes / 2.84 s probe. Their TSV is not in the tree, and the window was a live API read at 2026-11-08T11:52:46Z that attempts made later would change.
- Class enumeration: I re-ran the RCA's rule (`git grep -n completed_at -- tools/ .github/`, fixtures excluded) at `4fe7d5934b`. It returns 13 files, and section 3's table names 7 of them. I read every hit in the 6 unlisted ones (ev/class_enum_unlisted.txt). Each is a duration sum, a docstring, a self-test fixture literal, a log line or a raw listing (`nightly.yml`, `merge_throughput.py`, `governance_cost.py`, `probe_bridge.py`, `proof_watch.py`, `sweep_driver.py`, `replan.py`). None makes a decision on a non-gate job finishing after a time, so the class is not open.
- `VERSION`, the manifest and `RELEASE_NOTES.md` are untouched (ev/version_untouched.txt). The diff moves no budget. `tests/closures.json` gains one INERT READS entry, which the new tracked harness requires, and `bugclasses.json` gains one `_rca` entry. Nothing moves that the change did not earn.
- Local cheap checks at the head:
  - `closure.py select`: `MODE: SCOPED -- 1 script(s) run, 32 scoped out.`
  - `structure.py`: `STRUCTURE RATCHET PASSED`
  - `fold_ledger.py check`: `0 violation(s)`
  - `harness_headers.py` cannot run on this host (no `homeassistant`). CI `tests / fast (3.14)` is green at this head (jobs 129014272437 and 129014250697).
- Red-check answers: `pr-contract / pr-contract` job 129014574032 started at 06:26:42Z, after both red gates concluded, and is `success`. That run is the evidence that the body check passed. The non-required `governance / delivery-status` red (job 129014270552) blocks nothing.
- Forward-carry: Carries 1-3 name `#201`, and the packet's `carry_audit` routes all 3. Countermeasure A is recorded as `parts_missing` in the `_rca` entry. The fix on main replays recorded #3308 listings in one pass rather than a closed loop. That gap is raised under Findings.

## Findings

- Follow-up: countermeasure A (closed-loop convergence check over a recorded attempt-n/n+1 transition) has not landed, and its destination stage has already merged. `34b98bbdb` (R10-HOTFIX-SWEEP-SETTLE-LOOP) is on main, and its `sweep_selftest.py` replays the recorded #3308 listings and asserts zero posts in one pass. That kills this defect's arm 1, but it does not iterate sweep → re-run → completion to a fixed point. Control: `r10_rca_sweep_settle_loop.py replay --ci <tree>` gives `reruns=86` at `4fe7d5934b` and `reruns=1` at origin/main. Its open-loop mutant gives `reruns=1` on the defect too, so a one-pass check cannot stand in for it. Carry: #201
- Follow-up: deferred gates left red after their decider concluded green, observed at this head. Runs 42554795796 and 42554912554 deferred to run 42572841641 (`their gate decides`), whose gate went green at 06:28:29Z. At 06:37:03Z neither deferred gate had been re-run, so `classify` reads `gate` red. This may be the post-`34b98bbdb` settle rule (it leaves a bot-started gate with no new source), and it is the same block shape as the previous verdict at `1310d182`. I did not measure the sweep's runs for this head. Carry: #201
