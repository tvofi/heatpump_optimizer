The merge train treated a red `gate` as a final verdict even while the head's code run was still running. That made it skip pull requests that would have gone green. This is a hotfix-tier change because it blocks merges. It is CI-throughput lever 1, approved by the owner (tvofi, 2026-11-07, #201 comment 6707834331).

How it happens: an edit run's gate fails straight away, deferring to the code run (tools/ci/gate.py `deferral`: "run(s) [..] at this head are still being judged; their gate decides"). The code run publishes no `gate` check run until every one of its units has finished. So `latest_runs` sees only the edit gate, `classify` counts it red, `wait_ci` returns it, and `at_head` logs `ci red=['gate']` and SKIPs. The brief's s12 CI-throughput study (2026-11-05 13:26Z to 2026-11-07 13:26Z) counted 56 such SKIPs. In 32 of them the code run later concluded success, and in 10 it failed. This seat did not re-take those figures: they come from the brief.

The fix (tools/audit/seat/merge_train.py):
- `classify(latest, required, busy=())`: a red GATE counts as pending while `busy` is non-empty. Every other context, and every caller that passes no `busy`, behaves exactly as before.
- `gate_busy(ci_runs, check_runs)`: calls tools/ci/gate.py's own `busy` (imported from its tree path, not copied), i.e. unfinished, not held, not judging. Each run's jobs are taken from the check runs of its own check suite, so no per-run jobs read is needed. `run_id` is set to infinity because the train is not a run: gate.py's tie-break against a later run with a started gate is between two gates and has no train side.
- `Train._gate_busy`: one `actions/workflows/ci.yml/runs?head_sha=` listing per poll, made only when the gate reads red. If the listing cannot be read, no run counts as busy and this is logged, so the red stands exactly as it did before.
- `wait_ci`: re-reads a red GATE against that listing and logs each change in the busy set. There is a gap between the code run finishing and gate-sweep.yml (which starts on that completion) re-running the deferred red. To cover it, a red GATE with a green GATE suite beside it gets one settle poll (`SWEEP_SETTLE_POLLS = 1`). If the sweep never re-runs it, the red is read again one poll later and SKIPs. A genuine code-run failure leaves no green suite, so it gets no settle.
- Merges are still decided only by gate success, `cross_check` against GitHub's required-check evaluation, and the ruleset. The wait is still bounded by `polls` and ends in TIMEOUT.

Alternatives considered:
- (a) Copying `busy`'s three conditions into the train: rejected, because that is a second reading of the rule.
- (b) Reading each run's jobs as gate.py does: rejected, because it costs one read per run per poll, where check runs grouped by suite give the same name -> (status, conclusion) map.
- (c) Parsing the deferral text from the gate's log: rejected, because it needs a log read per red and depends on wording.

This retires R10-TRAIN-MERGE-LOOP-2's carry for the same defect: its carry about the gate deferral being read as a final red moves here, so it is built once.

Process state (d): gate.py's at-once deferral (fa921fd59, 2026-11-05) post-dates the classifier (e23062763, 2026-10-21).

## Head

ac5cfc2a8f76c6ca56ab7dea8a762ae8adeee423: the fix (b8c58c8e, cut from origin/main a37c58e5) with origin/main b4ec2f332fe3ab8dcf169bd3066276d3bb8848ab merged in at 2026-11-07T14:52Z, after main moved during the first `prepr.sh` run. The self-test, mutants, scope, structure, entities and `prepr.sh` were all re-run at this head.

## Mutation proof

The failing test came first, in `_defer_wait_self_test`, which `python3 tools/audit/seat/merge_train.py --self-test` runs. Each mutant was applied with sed to the committed file, the self-test was run, and the file was restored:

- M1, dropping the unfinished-run test (`busy = self._gate_busy(h, runs)` -> `busy = []`) puts the base reading back. Result: 4 failed, including the named case `defer-wait 13:01Z cycle: five of five deferring heads wait and merge, none SKIPs (the mutant's named case)`, plus `defer-wait #3248: the edit gate's red while code run 42237558473 runs is waited on, then it MERGES (the failing-test-first scene)`, `defer-wait bound: a code run that never finishes ends in TIMEOUT within polls, never merges` and `defer-wait: an unreadable runs listing reads no run busy -- the red stands, logged, never a merge`.
- M2, classify ignoring `busy` (`deferred = {GATE} if busy else set()` -> `deferred = set()`). Result: 4 failed: `defer-wait: classify reads a red gate as pending while busy ...`, the #3248 scene, the 13:01Z cycle, and the TIMEOUT bound.
- M3, dropping the sweep settle (`if not busy and settle < SWEEP_SETTLE_POLLS and any(` -> `if False and any(`). Result: 2 failed: the #3248 scene and the 13:01Z cycle. This shows the settle poll is load-bearing for the measured scene.

## Null control

On the head, these checks are green (`--self-test`):
- `defer-wait null: a red gate with no unfinished ci.yml run at the head still SKIPs, on its first poll`
- `defer-wait null: a genuine code-run failure still SKIPs once that run finishes (no green suite: no settle)`
- `defer-wait bound: a sweep that never re-runs the red leaves it standing one poll later, a SKIP`
- the classify case `a red non-gate context stays red whatever is busy`
- the existing A5 cases: (i) and (ii) still read RED with no `busy`, and `head (i) at the train: an older red suite stops it before any cross-check` still stops

Table of cases pinning both readings: `gate_busy` over the train's two reads equals gate.py's `busy` over per-run jobs. It covers five rows, one of them judging's own null, where pr-contract is unfinished and the run reads busy.

## Figures

- merge_train self-test at the head: `python3 tools/audit/seat/merge_train.py --self-test` prints `merge_train self-test: 478 checks, 0 failed`.
- Mutants M1, M2 and M3: the same command after each sed in `## Mutation proof` prints `478 checks, 4 failed`, `4 failed` and `2 failed` respectively, naming the cases listed there.
- Scoped gate: `python3 tests/closure.py select --diff $(git merge-base origin/main HEAD) --workdir "$D"` prints `MODE: SCOPED -- 1 script(s) run, 32 scoped out`, naming tests/entities.py. `PYTHONPATH=tests/hastub python3 tests/entities.py` exits 0.
- Structure: `python3 tests/structure.py` prints `STRUCTURE RATCHET PASSED`.
- The 56 / 32 / 10 SKIP counts, the 27 re-merged heads and the about 3,500 runner-minutes come from the brief's s12 CI-throughput study (window 2026-11-05 13:26Z to 2026-11-07 13:26Z). They were not re-measured here, and that study's harness is not in the tree. Instead, the #3248 scene and the 13:01Z scene are each reproduced as a self-test case.
- Class enumeration: `git grep -n "classify(" -- tools/audit/seat` lists every classify reader. Dispositions:
  - `wait_ci`: closed in this diff.
  - `approval_owed`, `main_green`'s log-only read and `orchestrator_tick`: unchanged on purpose. These are reports, or the train's main-gate read; they read GATE without `busy`, and a deferral red there is reported as before.
  - The proof waits (`wait_ci(..., only=req)`) share `wait_ci`, so they are covered.

## Red checks

none

## Forward-carry

none

## Friction

none
