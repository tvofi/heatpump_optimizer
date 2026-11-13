# Proposal triage, session s14, batch 203 (P631-P633)

Sources:
- Roster `handoff/audit-r10-roster`, read at its tip at 2026-11-11T14:33Z. The groups owning
  `tools/ci/gate.py`, `tools/ci/sweep.py` and `merge_train.py` were read there.
- origin/main `ceb3070ccb`.
- The live merge-train log, `~/.local/state/hpo/merge_train/train.log`.
- `seat/unstick-3445/MECHANISM.md`, the orchestrator's 10-line mechanism note with file:line cites.

The queue's three tail lines number themselves 307-309, the same as two lines written beside
them. Here they are keyed by content and by their line in the queue file: 309, 310 and 311.

## P631: run every instrument self-test under a bound (orphaned roster_lib self-tests)

Verdict: DEFER. The cause is unmeasured, and the only instance has no launcher.

Source: triage queue line 309, 2026-11-11T14:21:08Z, orchestrator s14, PROPOSAL orphaned
self-tests.

Instances:
- One event, of two processes. Each was a `tools/audit/seat/roster_lib.py --self-test` under
  system python 3.11. They ran 3h52m and 3h59m as ppid-1 orphans at about 14% CPU each. The
  orchestrator killed them by PID at 14:2xZ.
- `hw.ncpu` is 8, and the load average was 84. So together they took about 0.28 of a core, or
  3.5% of the box, for 4 h.
- The only tracked caller is `.github/workflows/governance.yml:1145`, `python3 -I
  tools/audit/seat/roster_lib.py --self-test`. That runs on a CI runner.
  - Nothing under `tools/pr`, `tools/ci` or `tools/audit/seat` launches it locally: `git grep`
    at origin/main finds only the docstring and `r10_roster_ops_mutants.py`'s comment.
  - So the local launch was by hand, or from a seat reproducing that CI step verbatim. The
    command line matches it exactly, including `-I` under the ambient python.
  - The parent is gone, so the launcher cannot be named from this instance.
- `pr_bounded` (`pr_args.sh:342`) bounds only `pr_args`, `update_pr` and `cloud_relay`
  (`--self-test` arms at `pr_args.sh:1747`, `update_pr.sh:36`, `cloud_relay.sh:1862`). It was
  built after the 8.6 h `pr_args` spin.

Cost/benefit:
- Bounding every instrument self-test touches dozens of entry points, in python and in bash.
- The measured cost is 3.5% of the box for 4 h, once. That is under the bar on standing CPU.
- Not knowing why it ran 4 h matters more than the bound. A self-test that normally finishes
  in seconds and runs 4 h is hung (on a lock, a git call or a fixture), and a bound would hide
  that.

What would change it:
- A second instance, with `ps -o pid,ppid,lstart,etime,command` and the parent's command line
  captured before the kill, so that the launcher is named.
- Or `roster_lib.py --self-test`'s normal wall time measured on this box, so that a hang is told
  apart from load.
- Then the countermeasure goes where the launcher is: that seat's step, or `pr_bounded` widened
  to that one entry point. It does not go to every self-test.
- The orchestrator's PID kill already stands as the local action.

Binding: unmeasured. One instance, no launcher, and 3.5% of the box for 4 h.

## P632: a gate re-run's re-queued needs make the run busy() to every gate beside it

Verdict: ACCEPT, as a carry on R10-GATE-DEFER-BARRIER, with `tools/ci/gate.py` added to its files
and R10-HOTFIX-GATE-REDISPATCH-LOOP added to its `after`. No S fly-in group.

Source: triage queue line 310, 2026-11-11T14:26:32Z, orchestrator s14, RESIDUAL of
R10-HOTFIX-GATE-REDISPATCH-LOOP (#3473).

Instances, from MECHANISM.md item 2, with its cites checked at origin/main:
- Re-running a gate also re-runs its skipped `needs`. In run 43022147048 attempt 2,
  `pr-contract / pr-contract` was queued at 14:08:44Z and ran at 14:12:53Z.
- While those needs are unfinished, `judging()` is false (prelude.py:217-218), so the run is
  `busy()` (gate.py:124-126). Every gate re-run beside it then fails with "still being judged"
  (gate.py:185-187).
- At #3445 that hit 43013039961, 42980650874 and 42980702138 at 14:09-14:12Z.
- MECHANISM.md item 4 states the train-side effect: `latest_runs` keeps the WORST gate of every
  suite, so a leftover deferral red holds `classify` at WAIT.
- #3473 closes the re-dispatch arm (items 1 and 3). It leaves this producer.

Classification:
- This is a repair of CI code. The producer emits an at-once deferral red that is not a verdict
  on the head.
- It is the producer side of the class R10-GATE-DEFER-BARRIER exists to barrier. That group's
  brief reads: "every reader of the gate conclusion ... treats an at-once deferral red as
  provisional".
- That group is severity medium, so the machinery bar does not apply.
- It is not-started, so it can receive a carry.

Placement:
- R10-GATE-DEFER-BARRIER owns `sweep.py` and the gate-deferral readers. It lacks `gate.py`, so
  `gate.py` is added.
- #3473 (R10-HOTFIX-GATE-REDISPATCH-LOOP) edits gate.py and sweep.py, so it goes in the group's
  `after`.
- A separate S fly-in is not justified on one PR's instance. What would change that: a second
  PR held at WAIT by a deferral red from this producer before R10-GATE-DEFER-BARRIER dispatches.

The carry's acceptance:
- (i) A run whose only unfinished jobs are the re-queued `needs` of its own gate re-run is not
  `busy()` to another gate at the head. Either busy() discounts them, or judging() reads the
  run's pre-rerun sources. The fixer chooses, with a fixture.
- (ii) Null control: a run with a genuinely unfinished unit is still busy(), and the lower-id
  tie-break for two deferring runs (the #3241 case in busy()'s docstring) is unchanged.
- (iii) Mutation: reverting (i) turns its fixture red.

Binding: a merge-blocking false red from a class producer, carried to the class's owning group.

Bar re-check (2026-11-11, orchestrator's question; proposal-triage.md lines 9-19). A carry on an existing group is still added instrument work, so the same bar applies to it. No ratchet-budgets.md cap is touched: every change here is code under tools/ and moves no policy_budgets.json measure, so the 20% figure below is read on the proposal's own benefit measure.

Bar: severity medium (R10-GATE-DEFER-BARRIER's roster severity). Figure: none against 20%; the instance is one PR (#3445) held by three false gate reds at 14:09-14:12Z, with no denominator measured. Accepted as a severity-exempt defect repair (a merge-blocking false red from CI code), not as over-20%.


## P633: re-admit a skipped train entry whose head moved by a carry range

Verdict: DEFER. Re-ruled 2026-11-11 from ACCEPT; the original verdict was "ACCEPT, as a carry on
R10-TRAIN-REVIEW-PRESETTLE". See the bar re-check at the end of this entry.

Source: triage queue line 311, 2026-11-11T14:29:30Z, orchestrator s14, PROPOSAL train
re-admission at a carried head. The orchestrator later added #3454 to it, in its message to this seat.

Instances:
- `already_held()` (merge_train.py:1278) holds a `skipped` entry at the same verdict unless the
  skip's class is in `READMIT_SAME_VERDICT = (HOLDER, BRANCH_POLICY, PREFLIGHT_PARK)` (:973).
- A TIMEOUT or CI skip whose head then moves by a clean main merge keeps the same verdict sha.
  bus.sh rightly refuses a second reviewer for a carry range (tvofi, 2026-10-27).
- So such a PR has no route back onto the live train. Today that is:
  - #3445: verdict 7fb8680c, head 206a0ee1.
  - #3438: verdict 30b14392, head fb121b6b, class GREEN.
  - #3454: skipped at its verdict; it needs main merged in after #3466.
- train.log holds 26 `ALREADY ... skipped by this train` refusals in all, #3438 twice.
- The live train (pid 90809) started at 09:13:44Z. It takes new spool additions, so it does not
  end on its own schedule. These PRs wait for its end, which is unbounded.

Classification:
- An instrument defect: green, merge-verdicted PRs are held with no route back. Severity medium.
- The machinery bar does not apply.

The carry's acceptance:
- (i) A `skipped` record stores the head it was skipped at.
- (ii) `already_held` admits the same verdict when the head moved and `app_approve.sh --carry
  <verdict> <head>` says `CARRY: yes`.
- (iii) Null control: the same verdict at the SAME head stays held. A head moved by a non-carry
  range stays held, and needs a new verdict.
- (iv) Mutation: dropping the CARRY check admits a non-carry head, so (iii) goes red.

Until it lands, the operational route is to re-queue those PRs on the next train after the live
one ends. Starting a second train beside a live one is not this seat's to rule.

Binding: green, verdicted PRs with no route to merge, while a train lives.

Bar re-check (2026-11-11, orchestrator's question; proposal-triage.md lines 9-19). A carry on an existing group is still added instrument work, so the same bar applies to it. No ratchet-budgets.md cap is touched: every change here is code under tools/ and moves no policy_budgets.json measure, so the 20% figure below is read on the proposal's own benefit measure.

Bar: severity normal (R10-TRAIN-REVIEW-PRESETTLE's roster severity). The original ruling classified the defect itself as medium, but the contract classifies only an unset severity, so the group's normal stands and over 20% is required to add. Figure: none against 20%. The instances are 3 PRs and 26 `ALREADY ... skipped` lines, with no wall-clock and no denominator, and P638 (s6-batch207.md) later found train.log carries no timestamps and the CARRY class holds one instance this round (#3445). Re-ruled DEFER: a normal-severity addition, unmeasured against the bar. Reopens on P638's conditions (a) or (b), or a roster severity of medium or higher on the group. The landed carry is dismissed by `--match 'TRAIN-READMIT-CARRIED-HEAD'`.
