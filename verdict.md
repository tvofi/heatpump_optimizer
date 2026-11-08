Fix review: blocked f6d7be0cd4ef22a353d72532ca18aae38089e5cc architecture-unsound: settled() removes settle's bounded recovery of a mutually deferred bot-re-run gate pair, which the finder's replay shows the fix does not need

bus-nonce: d37440cec888a2b452596190cc201914

Round: first.

## Block

- Change (2), `settled()` in `tools/ci/sweep.py`, regresses a recovery path, and the finder's evidence does not call for it. It leaves any red gate whose latest attempt `github-actions[bot]` started, unless a source finished after that attempt started, "whichever arm reads it undecided". That includes the lagging-listing arm, which exists to recover two gates that deferred to each other (r10-gate-busy-defer-3, #3287). Settle's arm 1 re-runs both sibling gates in one pass when a real source finishes late, so the next pair it judges is a pair of overlapping bot attempts. If a lagging listing makes them defer to each other again, both stay red with no real red, and only a human re-run recovers them. Reviewer's own probe (`ev/liveness_probe.py`, not the finder's): at the base, step b re-runs the lower gate (`jobs/10/rerun`), then step c re-runs the higher (`jobs/20/rerun`), and the PR recovers with bounded re-runs. At the head, step b posts nothing: `RESULT liveness reruns_after_pair=0 stuck_red=yes`. The PR's own last self-test pins exactly this pair and calls it "is final". The body does not disclose that cost, and it does not name the alternative of change (1) alone, as `fixer.md` step 17 requires ("the body names the alternatives and why each lost").
  The finder's harness shows change (1) alone suffices. With `settled()` disabled (M2, below), the replay gives `reruns=1 max_attempt=2`, the same as the full head. With an injected bot `triggering_actor`, `settled()` still cannot stop the loop on its own (M1: `reruns=86`), because it reads the same `sources()`. Re-cut: drop `settled()` and its pin, or restrict it so that it never suppresses the lagging-pair and lower-green arms, and pin the probe's step b.
  Carry: built-here

## Evidence

- Finder's harness `dev/audit/harnesses/r10_rca_sweep_settle_loop.py` + `.json` taken from `handoff/r10-rca-sweep-settle-loop` ae2bceee, run against `git archive <sha> tools/ci`:
  - base 4a9d2d54: `RESULT replay reruns=86 max_attempt=44 sim_minutes=72 alarm=yes` (`ev/replay-base.txt`). The 86 reproduces, so the finding stands.
  - head f6d7be0c: `RESULT replay reruns=1 max_attempt=2 sim_minutes=1 alarm=no` (`ev/replay-head.txt`).
  - `--no-restamp` null: `reruns=1` at both ends.
- Perturbations at the head (`ev/mutations.txt`), each with the replay result and the self-test result:
  - M1, `sources()` keeps skipped jobs: replay `reruns=86`; `60 checks, 5 failed`.
  - M2, the `settled()` call disabled: replay `reruns=1`; `1 failed`, the overlapping-pair pin only.
  - M3, M1 and M2 together: replay `reruns=86`; `6 failed`.
  - M4, `settled()` drops `not source_after(...)`: `1 failed`, the codeql-python null.
  These match the body's M1–M4 counts.
- Replay with `triggering_actor` injected (bot on attempts past the first; reviewer's edit of a copy, `ev/replay-with-actor.txt`): head 1, M1 86, M2 1, M3 86.
- Self-tests at the head (`ev/head-selftests.txt`): `sweep self-test: 60 checks, 0 failed`; `gate self-test: 77 checks, 0 failed`. Base sweep.py beside the new self-test: `60 checks, 7 failed` (`ev/base-null.txt`), matching the body.
- Class rule: `git grep -n "completed_at\|started_at" -- 'tools/ci/*.py' ':!tools/ci/*selftest*'` outside sweep.py returns gate.py 662, 664, 682, 739 and 740, all inside `self_test()` (def at 360), as the body says. The class is one production seam, sweep.py.
- Merge: `git merge-tree --write-tree origin/main f6d7be0c`: clean.
- Three-dot diff: `dev/programme/delivery/3327.md` is present. VERSION, the manifest, RELEASE_NOTES.md, budgets, `tests/closures.json`, golden and claim files are untouched. No new file needs a closure entry besides the delivery row, and `tests / closures`, `closure-scope` and `fast` are green.
- CI: `merge_train.py classify` -> `RED f6d7be0c... pending: none red: gate`, rc=1 (`ev/classify.txt`, `ev/classify-poll.txt`).
  - The red is the two CI edit runs' gates, 42480467902 and 42480902071 (job 128732808932: `FAIL run(s) [42480466885] at this head are still being judged; their gate decides`), a deferral to the code run, whose gate 128740939651 is green.
  - No Gate sweep has run since 12:22:30Z, so nothing has re-run them yet.
  - Per the brief's GATE DEFERRAL rule this is not a reason to block, and this verdict does not rest on it.
- Body figures re-derived: the 60/0 and 60/7 self-test counts, the 77/0 gate self-test, M1–M4 and the class census. Not re-derived: the recorded attempts 39/25/24 (live API figures that move) and `tests/entities.py`; CI's Linux runner covers the latter.
- Body `## Head` names f6d7be0c, the head measured here.
