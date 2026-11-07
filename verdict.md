Fix review: merge 16452e45300be5507d6f979e5033676052d0f4e8

bus-nonce: 309106c046dd5ce53e696b338872f2e6

## Verdict

PR #3287 (R10-HOTFIX-GATE-BUSY-DEFER, r10-gate-busy-defer-3) at head 16452e45300be5507d6f979e5033676052d0f4e8, merge base and origin/main 4b5d771bdf8feb1f83d7d9443e5117b771a0ab76. This is review round 2: an earlier verdict/3287 at 29ee7261 was `settle-unjudged`, and this head carries its repair. The review ran from a detached worktree at the head, by the three-dot diff. The finder's harnesses were run at both ends: `dev/audit/harnesses/r10_gate_busy_defer_3.py replay` and `dev/audit/harnesses/r10_gate_defer_race.py`, the latter also as main's unmodified copy. Every production line the PR adds or changes was mutated, with a null control. CI on this head is GREEN.

Answers to the brief's four focus questions:
1. The #3282 replay reproduces the defect at the base and passes at the head. Base: `RESULT replay wait_s=720 first=FAIL swept=yes final=PASS`. Head: `wait_s=0 first=FAIL swept=yes final=PASS`. `final` stays flat because the sweep did fire at the base too, as the body says. The metric the replay moves is `wait_s`, the runner hold. Mutant G1, which restores the wait, puts head back to `wait_s=720`. The null mutant leaves it at 0. CI showed the defect live at this head: edit gate 128458265063 ran on main's program (`programs restored from 4b5d771b`), held its runner 16:36:00–16:48:08Z, and then published `FAIL run(s) [42388999905] at this head are still being judged`.
2. `settle` leaves nothing unjudged and loops nowhere in the cases I checked. Mutual deferral, a red decider, a cancelled decider, a red lower or green lower in a lagging pair, and real reds all behave. My mutants S2–S7 each turn a named settle check red. Every re-run judges after every source and the peer gate concluded, so no `undecided()` arm fires again (S3 and S4 kill the no-loop nulls). One gap remains, and it is not a regression: a head with a completed `ci.yml` run that has no `gate` job (see Findings).
3. `gate.judge` has one bound left, `lag_bound(why)`, for the run's own listing lag. The deferral-specific `GATE_WAIT_MAX_S` branch is gone, and `deferral()` is the only producer of the text. There is no second copy of the busy/wait rule in `tools/ci`. Two stale descriptions and one copied text pattern live outside the diff; they are carried below.
4. A deferral red at a head that a later green code run covers is re-run by the green branch (unchanged) or by `settle`. Live at this head, both edit gates were re-run and green within about 30 s of code gate 128470411243 going green (17:11:32Z → 17:12:23Z and 17:12:34Z).

## Findings

- Follow-up: two new `settle` lines survive their deletion with every self-test and the replay green (ev/mutants.txt). S9 drops the poll on a gate that completed while its run is still open. S10 drops the `live()` head-moved stop inside settle's poll. Neither breaks liveness. Under S9, `judge()` leaves that run ("run still busy") and that run's own completion sweep settles it. Under S10, a sweep re-runs gates at a superseded head, which wastes runners but leaves no red at the live head. They are still untested branches on lines this PR adds, and the PR names neither in its mutation proof. Owed: a settle self-test that kills each one. Carry: R10-HOTFIX-GATE-BUSY-DEFER
- Follow-up: settle never ends when the head holds a `ci.yml` run that completed with no `gate` job listed, for example a `startup_failure`. `gates[i]` is `{}`, so `unconcluded` names that run and settle prints "their completion sweeps", but that run's completion has already happened. Probe ev/probe.py, ev/probe_nogate_run.txt: posts=[] at this head with that third run, posts=[jobs/10/rerun] without it. The base gives the same SKIP outcome, so this is not a regression. It is still a head where a deferral nothing re-runs stays red. Owed: settle keys `unconcluded` on gates whose run is not completed. Carry: R10-HOTFIX-GATE-BUSY-DEFER
- Follow-up: one consumer still describes the superseded wait. `tools/audit/seat/orchestrator_tick.py:1161` tells the orchestrator, for a gate red beside a running sibling, "rerun the failed jobs once siblings settle (the gate defers up to 720s, GATE_WAIT_MAX_S)". At this head a deferral is published at once and gate-sweep.yml re-runs it, so the line points a seat at the hand re-run that raced the sweep on #3282 (body, brief-cause). Its self-test pins the constant's name at :3811-3824. `tools/ci/sweep.py:8`'s "the higher-id code run's gate the one that waits" is the same stale wording. Owed: reword the tick line to "the sweep re-runs it once the decider completes", together with its pinned check. Carry: R10-HOTFIX-GATE-BUSY-DEFER
- Follow-up: the new harness holds its own copy of the deferral text. `dev/audit/harnesses/r10_gate_busy_defer_3.py:61` `DEFERRAL = re.compile(r"FAIL run\(s\) \[([0-9, ]+)\] at this head are still being judged")` matches the string `gate.deferral()` builds rather than deriving from it. A reworded deferral would make `census` print `deferral_fails=0` silently, which reads as the after-merge prediction `held_ge_600=0` passing. Owed: derive the pattern from `gate.deferral` (the harness already imports `gate`), or pin it with a self-check. Carry: R10-HOTFIX-GATE-BUSY-DEFER
- Follow-up: the roster carry on this group (orchestrator, 2026-11-06 ~23:27Z) binds "a deferral resolve itself to the code run's conclusion, with no red and no hand rerun". This design publishes the deferral red at once and relies on gate-sweep.yml to turn it green. That means a transient red, with no hand re-run. The 11-07 dispatch brief sanctions this ("publish its deferral at once"; focus 4 asks only that no red survive a later green code run). The body never answers the carry's "no red" clause by name, though. The orchestrator should record the supersession on the group. Carry: R10-HOTFIX-GATE-BUSY-DEFER

## Evidence

- Self-tests at the head (ev/selftests_head.txt): `sweep self-test: 52 checks, 0 failed`, `gate self-test: 77 checks, 0 failed`. These match the body.
- #3282 replay (ev/replay.txt): base `RESULT replay wait_s=720 first=FAIL swept=yes final=PASS`; head `RESULT replay wait_s=0 first=FAIL swept=yes final=PASS`. These match the body.
- Race harness at both ends (ev/race_summary.txt). gate-wait, base → head: 2754 780→0, 2754-red 780→0, pair 120→0, cascade 120→0, editcode 600→0, single 0→0, prelude 480→0. RESIDUAL-RED is 0 at both ends, MASKED is 0 and DEADLOCK is `no`. This matches the body's table. The PR edits the finder's race harness (it adds job stamps). Main's unmodified copy, run against the head's tools/ci, gives the same gate-wait 0 and RESIDUAL-RED 0 in every scenario (ev/race_mainharness_at_head.txt), so the head's result does not depend on that edit.
- Mutants (ev/mutants.txt, driver /tmp/mut/drive.py, `-B`, restored after each):
  - Null, comment only: all green, `wait_s=0`.
  - G1 (deferral wait restored): gate self-test 14 failed, replay `wait_s=720`. This matches the body's M1.
  - G2: 1 failed.
  - S1 (settle → old SKIP): 20 failed.
  - S2: 3 failed. S3: 4 failed. S4: 3 failed. S5: 11 failed. S6: 1 failed. S7: 2 failed.
  - S8 (`conclusion != success` dropped): survives, but it is equivalent, because `Sweep.judge` returns on `success`.
  - S9 and S10: survive (see Findings).
- Hygiene (ev/hygiene.txt):
  - `VERSION`, the manifest, `RELEASE_NOTES.md`, both claim files and every `*_budgets.json` are untouched.
  - `STRUCTURE RATCHET PASSED`.
  - The new harness is classified in `tests/closures.json`.
  - `tests/closure.py select` reads `MODE: FULL` (the fixture changes the gate).
  - The delivery row `dev/programme/delivery/3287.md` is in the diff.
  - `tests/entities.py` could not run locally (no `homeassistant`). CI's full suite on this head is green.
- Merge: `git merge-tree --write-tree origin/main 16452e45` rc=0 (ev/merge_tree.txt), and origin/main is the merge base, 4b5d771b.
- Head: the PR body's `## Head` names 16452e45300be5507d6f979e5033676052d0f4e8, and `git ls-remote` at verdict time agrees.
- CI (ev/merge_train_classify.txt, ev/ci_log.txt, ev/check_runs.tsv, 68 latest check runs across all pages):
  - `merge_train.py classify` exit 0, `GREEN 16452e45300be5507d6f979e5033676052d0f4e8 pending: none red: none`.
  - First it read RED at 16:55Z on edit gate 128458265063. That job's log ends `FAIL run(s) [42388999905] at this head are still being judged; their gate decides`, which is the edit-run deferral. Per the brief I waited rather than blocked. Both edit gates (128470684096, 128470687553) were re-run and green at 17:12Z, after code gate 128470411243 went green at 17:11:32Z.
  - The only concluded red among the latest check runs is `tests / nightly-status` (128458115647). The body's `## Red checks` names it as inherited from main's nightly.
  - `pr-contract / pr-contract` 128470237986 is green at 17:10:13Z, after the last red concluded, and that run is the body-check evidence.
  - The superseded deferral attempts are the class this PR removes. The body does not name them, and by the GATE DEFERRAL rule they are not this PR's to answer.
- Not re-derived:
  - The live census figure (`deferral_fails=13 … held_runner_s=9391`). It reads a closed window of GitHub runs, and I did not re-take it. Carry: dismissed: evidence, not a finding
  - The fixer's own probe sha1 (refs/heads/verdict/3287) was not re-hashed. My S-series and the self-test census cover the same orderings.
- Per the PROMPT ("push nothing else"), no handoff-wip ref was pushed.
